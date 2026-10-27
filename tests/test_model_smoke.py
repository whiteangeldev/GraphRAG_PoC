"""Real SDK/protocol integration through a mock HTTP transport; no model inference."""

import json
import os
from pathlib import Path
from typing import Any

import httpx
import pytest
from openai import OpenAI

from graphrag_poc.eval import smoke
from graphrag_poc.eval.gold import load_nodes
from graphrag_poc.generate.model import model_answer
from graphrag_poc.models import Node


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for name in os.environ:
        if name.startswith(("GENERATION_", "JUDGE_", "OPENAI_", "EMBEDDING_")):
            monkeypatch.delenv(name)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GENERATION_MODEL", "Qwen/Qwen3-8B")
    monkeypatch.setenv("JUDGE_MODEL", "Qwen/Qwen3-14B")
    monkeypatch.setenv("GENERATION_CACHE_DIR", str(tmp_path / "answers"))


@pytest.fixture(scope="module")
def nodes() -> dict[str, Node]:
    return load_nodes()


class FakeServer:
    """Serve only the model-list and chat endpoints over httpx.MockTransport."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.requests: list[httpx.Request] = []
        self.connections: list[dict[str, object]] = []
        self.listing = ["Qwen/Qwen3-8B", "Qwen/Qwen3-14B"]
        self.fail_listing = False
        self.rubber_stamp = False
        self.missing_citation = False
        self.truncated = False
        self.reject_bulb = False
        self.generator_calls = 0
        self.judge_calls = 0
        transport = httpx.MockTransport(self.handle)

        def make_client(**kwargs: Any) -> OpenAI:
            self.connections.append(kwargs)
            return OpenAI(**kwargs, http_client=httpx.Client(transport=transport))

        monkeypatch.setattr("openai.OpenAI", make_client)

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if request.method == "GET":
            assert request.url.path == "/v1/models"
            if self.fail_listing:
                return httpx.Response(401, json={"error": {"message": "secret-in-server-body"}})
            return httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        {"id": model, "object": "model", "created": 0, "owned_by": "test"}
                        for model in self.listing
                    ],
                },
            )
        assert request.url.path == "/v1/chat/completions"
        body = json.loads(request.content)
        if body["model"] == "Qwen/Qwen3-8B":
            self.generator_calls += 1
            payload = self.generate(body)
        else:
            self.judge_calls += 1
            payload = self.judge(body)
        return httpx.Response(
            200,
            json={
                "id": "smoke-test",
                "object": "chat.completion",
                "created": 0,
                "model": body["model"],
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "length" if self.truncated else "stop",
                        "message": {"role": "assistant", "content": json.dumps(payload)},
                    }
                ],
            },
        )

    def generate(self, body: dict[str, Any]) -> dict[str, object]:
        user = json.loads(body["messages"][-1]["content"])
        question = user["question"]
        if "ZZ-NO-SUCH-PART" in question or (self.reject_bulb and "ceiling" in question):
            return {"answer": "Insufficient supplied evidence.", "refused": True, "citations": []}
        bulb = "ceiling" in question
        return {
            "answer": smoke.BULB_FACT if bulb else "Check the oil level with the engine off.",
            "refused": False,
            "citations": []
            if self.missing_citation
            else [
                {
                    "node_id": "tm280_10:3-28:step-a:2:caution"
                    if bulb
                    else smoke.CASES[0].node_ids[0],
                    "page": 318 if bulb else 300,
                }
            ],
        }

    def judge(self, body: dict[str, Any]) -> dict[str, object]:
        user = body["messages"][-1]["content"]
        facts = json.loads(user.split("Required facts:\n")[1].split("\n\nAnswer sentences:")[0])
        claims = json.loads(user.split("Answer sentences:\n")[1].split("\n\nAnswer:")[0])
        quote = smoke.BULB_FACT if smoke.BULB_FACT in facts else smoke.OIL_FACT

        def supported(text: str) -> bool:
            return self.rubber_stamp or "purple" not in text

        return {
            "facts": [
                {
                    "text": text,
                    "present": supported(text),
                    "quote": quote if supported(text) else "",
                }
                for text in facts
            ],
            "claims": [
                {
                    "sentence": text,
                    "supported": supported(text),
                    "quote": quote if supported(text) else "",
                }
                for text in claims
            ],
        }


def test_plan_validates_sources_without_contacting_models(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(smoke, "probe_models", lambda: pytest.fail("plan must not call endpoints"))
    assert smoke.main(["--plan", "--output-dir", str(tmp_path)]) == 0
    result = json.loads((tmp_path / "plan.json").read_text())
    assert result["status"] == "planned_no_endpoint_calls"
    assert result["plan"]["max_generation_requests"] == 3
    assert result["plan"]["max_judge_requests"] == 3
    assert "not M3 acceptance" in result["purpose"]


def test_successful_live_protocol_uses_six_chat_calls_and_no_cache(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    server = FakeServer(monkeypatch)
    for index in range(2):
        output = tmp_path / str(index)
        assert smoke.main(["--run", "--output-dir", str(output)]) == 0
        report = json.loads((output / "results.json").read_text())
        assert report["status"] == "passed"
        assert len(report["cases"]) == 3
        assert report["judge_calibration_passed"]
    # A second run must exercise the endpoints again, never reuse an answer cache.
    assert server.generator_calls == 6
    assert server.judge_calls == 6
    assert sum(request.method == "GET" for request in server.requests) == 2
    assert all(connection["max_retries"] == 0 for connection in server.connections)
    assert not (tmp_path / "answers").exists()


def test_missing_model_blocks_all_chat_calls(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    server = FakeServer(monkeypatch)
    server.listing = ["Qwen/Qwen3-8B"]
    assert smoke.main(["--run", "--output-dir", str(tmp_path)]) == 1
    result = json.loads((tmp_path / "results.json").read_text())
    assert result["status"] == "blocked"
    assert server.generator_calls == server.judge_calls == 0


def test_probe_only_lists_models_and_separates_role_credentials(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    server = FakeServer(monkeypatch)
    monkeypatch.setenv("GENERATION_API_KEY", "generator-secret")
    monkeypatch.setenv("JUDGE_API_KEY", "judge-secret")
    assert smoke.main(["--probe", "--output-dir", str(tmp_path)]) == 0
    assert len(server.requests) == 2
    assert server.generator_calls == server.judge_calls == 0
    text = (tmp_path / "readiness.json").read_text()
    assert "generator-secret" not in text and "judge-secret" not in text


def test_authentication_error_does_not_leak_provider_body_or_url_credentials(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    server = FakeServer(monkeypatch)
    server.fail_listing = True
    monkeypatch.setenv("OPENAI_BASE_URL", "http://user:password@host.test/v1?api_key=query-secret")
    # Keep the SDK query path conventional; the display helper separately strips secrets.
    assert (
        smoke.safe_endpoint("http://user:password@host.test/v1?api_key=query-secret")
        == "http://host.test/v1"
    )
    monkeypatch.setenv("OPENAI_BASE_URL", "http://user:password@host.test/v1")
    assert smoke.main(["--probe", "--output-dir", str(tmp_path)]) == 1
    text = (tmp_path / "readiness.json").read_text() + capsys.readouterr().out
    assert "AuthenticationError" in text
    assert not any(
        secret in text for secret in ("password", "query-secret", "secret-in-server-body")
    )


def test_rubber_stamping_judge_stops_before_generation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    server = FakeServer(monkeypatch)
    server.rubber_stamp = True
    assert smoke.main(["--run", "--output-dir", str(tmp_path)]) == 1
    result = json.loads((tmp_path / "results.json").read_text())
    assert not result["judge_calibration_passed"]
    assert server.judge_calls == 1 and server.generator_calls == 0


def test_uncited_answer_fails_without_judging_or_continuing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    server = FakeServer(monkeypatch)
    server.missing_citation = True
    assert smoke.main(["--run", "--output-dir", str(tmp_path)]) == 1
    assert server.generator_calls == 1 and server.judge_calls == 1
    report = json.loads((tmp_path / "results.json").read_text())
    assert "no valid citations" in report["cases"][0]["reason"]
    assert "oil-level: Model supplied no valid citations" in capsys.readouterr().out


def test_partial_answers_remain_in_report_when_a_later_case_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    server = FakeServer(monkeypatch)
    server.reject_bulb = True
    assert smoke.main(["--run", "--output-dir", str(tmp_path)]) == 1
    report = json.loads((tmp_path / "results.json").read_text())
    assert report["cases"][0]["passed"]
    assert not report["cases"][1]["passed"]
    assert server.generator_calls == 2 and server.judge_calls == 2


def test_stale_sources_stop_before_network_calls(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    nodes: dict[str, Node],
) -> None:
    server = FakeServer(monkeypatch)
    node_id = smoke.CASES[0].node_ids[0]
    modified = {**nodes, node_id: nodes[node_id].model_copy(update={"text": "Changed evidence"})}
    monkeypatch.setattr(smoke, "load_nodes", lambda: modified)
    assert smoke.main(["--run", "--output-dir", str(tmp_path)]) == 1
    assert not server.requests


def test_generator_cache_can_be_bypassed_explicitly(
    monkeypatch: pytest.MonkeyPatch,
    nodes: dict[str, Node],
) -> None:
    server = FakeServer(monkeypatch)
    hits = smoke._hits(smoke.CASES[0], nodes)
    model_answer(smoke.CASES[0].question, hits)
    model_answer(smoke.CASES[0].question, hits)
    assert server.generator_calls == 1
    model_answer(smoke.CASES[0].question, hits, use_cache=False)
    assert server.generator_calls == 2
