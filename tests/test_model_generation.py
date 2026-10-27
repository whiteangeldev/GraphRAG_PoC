"""Exercise model-owned decisions and cost controls with a fake SDK, never inference."""

import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from graphrag_poc.eval.config import configure_evaluation, validate_evaluation_models
from graphrag_poc.eval.judge import LanguageModelJudge, QuoteJudge, verify_model_judgment
from graphrag_poc.eval.score import score_attempts
from graphrag_poc.generate.__main__ import compose_answer
from graphrag_poc.generate.config import model_settings
from graphrag_poc.generate.model import parse_model_answer
from graphrag_poc.retrieve.fusion import FusedHit
from graphrag_poc.retrieve.graph import RelationFrame
from test_eval_score import _attempt


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import os

    for name in os.environ:
        if name.startswith(("GENERATION_", "JUDGE_", "OPENAI_", "EMBEDDING_")):
            monkeypatch.delenv(name)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GENERATION_MODEL", "Qwen3-8B")
    monkeypatch.setenv("JUDGE_MODEL", "Qwen3-14B")


def _hit(node_id: str = "doc:source", text: str = "Check the cable.") -> FusedHit:
    return FusedHit(node_id, text, "en", 7, 7, "doc", "paragraph", ("sparse",), 1, 1 / 61)


def _payload(*, citations: list[dict[str, object]] | None = None, refused: bool = False) -> str:
    return json.dumps(
        {"answer": "Check the cable.", "refused": refused, "citations": citations or []}
    )


def _fake_sdk(
    monkeypatch: pytest.MonkeyPatch, raw: str, *, finish_reason: str = "stop"
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    requests: list[dict[str, object]] = []
    connections: list[dict[str, object]] = []

    def create(**kwargs: object) -> SimpleNamespace:
        requests.append(kwargs)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content=raw), finish_reason=finish_reason)
            ]
        )

    def client(**kwargs: object) -> SimpleNamespace:
        connections.append(kwargs)
        return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

    monkeypatch.setattr("openai.OpenAI", client)
    return requests, connections


@pytest.mark.parametrize("question", ["99. INVENTED FAILURE?", "My truck won't start."])
def test_title_mismatch_and_natural_wording_both_reach_model(
    monkeypatch: pytest.MonkeyPatch, question: str
) -> None:
    requests, _ = _fake_sdk(monkeypatch, _payload(citations=[{"node_id": "doc:source", "page": 7}]))
    answer = compose_answer(question, [_hit()])
    assert len(requests) == 1
    assert answer.text == "Check the cable."
    assert not answer.refused
    assert [citation.node_id for citation in answer.citations] == ["doc:source"]


def test_empty_retrieval_still_leaves_refusal_to_model(monkeypatch: pytest.MonkeyPatch) -> None:
    requests, _ = _fake_sdk(monkeypatch, _payload(refused=True))
    answer = compose_answer("What should I do?", [])
    assert len(requests) == 1
    assert answer.refused
    assert answer.citations == ()


def test_no_citations_means_no_rule_fallback_or_frame_append(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _fake_sdk(monkeypatch, _payload())
    frame = RelationFrame(
        cause="Inspect the fluid.", part="UNVERIFIEDPART", part_number="UNVERIFIEDPART"
    )
    answer = compose_answer(
        "Which part should I get?", [_hit(text="Inspect the fluid. UNVERIFIEDPART")], frame
    )
    assert answer.text == "Check the cable."
    assert "UNVERIFIEDPART" not in answer.text
    assert answer.citations == ()
    judgment = QuoteJudge().judge(answer=answer.text, facts=("cable",), cited_texts=())
    assert not judgment.facts[0].present
    assert not any(claim.supported for claim in judgment.claims)


def test_any_supplied_passage_can_be_cited_but_wrong_ids_or_pages_cannot() -> None:
    raw = _payload(
        citations=[
            {"node_id": "doc:second", "page": 7},
            {"node_id": "doc:second", "page": 7},
            {"node_id": "doc:source", "page": 999},
            {"node_id": "invented", "page": 7},
        ]
    )
    answer = parse_model_answer(
        raw, question="Help", hits=[_hit(), _hit("doc:second")], temperature=0, seed=0
    )
    assert [(row.node_id, row.page) for row in answer.citations] == [("doc:second", 7)]


@pytest.mark.parametrize("raw", ["not JSON", '{"answer":"Hi","refused":"false","citations":[]}'])
def test_malformed_output_does_not_become_a_rule_answer(
    monkeypatch: pytest.MonkeyPatch, raw: str
) -> None:
    _fake_sdk(monkeypatch, raw)
    with pytest.raises(RuntimeError, match="invalid answer JSON"):
        compose_answer("Help", [_hit()])


def test_truncated_output_aborts_instead_of_scoring_a_partial_answer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _fake_sdk(monkeypatch, _payload(), finish_reason="length")
    with pytest.raises(RuntimeError, match="did not complete"):
        compose_answer("Help", [_hit()])


def test_generation_cache_reuses_only_identical_prompt_and_model_settings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("GENERATION_CACHE_DIR", str(tmp_path / "answers"))
    requests, connections = _fake_sdk(monkeypatch, _payload())
    compose_answer("Help", [_hit()])
    compose_answer("Help", [_hit()])
    assert len(requests) == 1
    compose_answer("Different question", [_hit()])
    compose_answer("Help", [_hit(text="Changed source text.")])
    compose_answer("Help", [_hit()], RelationFrame(cause="Unverified hint"))
    monkeypatch.setenv("GENERATION_MODEL", "another-model")
    compose_answer("Help", [_hit()])
    assert len(requests) == 5
    assert all(connection["max_retries"] == 0 for connection in connections)
    assert requests[0]["max_tokens"] == 1536
    assert requests[-1]["extra_body"] == {}


@pytest.mark.parametrize(
    ("generator", "judge"),
    [
        ("", "judge"),
        ("generator", ""),
        ("Qwen3-8B", "Qwen/Qwen3-8B"),
        ("Qwen3-0.6B", "judge"),
        ("qwen3:0.6b", "qwen3:14b"),
        ("qwen3:8b", "Qwen/Qwen3-8B"),
        ("qwen3:8b-q4_K_M", "Qwen/Qwen3-8B"),
    ],
)
def test_invalid_model_roles_fail_preflight(
    monkeypatch: pytest.MonkeyPatch, generator: str, judge: str
) -> None:
    monkeypatch.setenv("GENERATION_MODEL", generator)
    monkeypatch.setenv("JUDGE_MODEL", judge)
    with pytest.raises(RuntimeError):
        validate_evaluation_models()


def test_env_file_overrides_defaults_and_is_consistent_between_cli_processes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("GENERATION_MODEL")
    monkeypatch.delenv("JUDGE_MODEL")
    (tmp_path / ".env").write_text("GENERATION_MODEL=custom-generator\nJUDGE_MODEL=custom-judge\n")
    configure_evaluation()
    validate_evaluation_models()
    assert model_settings("GENERATION").model == "custom-generator"
    assert model_settings("JUDGE").model == "custom-judge"


def test_judge_uses_separate_endpoint_key_and_only_exact_aligned_quotes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_BASE_URL", "http://generator.test/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "generator-secret")
    monkeypatch.setenv("JUDGE_BASE_URL", "http://judge.test/v1")
    monkeypatch.setenv("JUDGE_API_KEY", "judge-secret")
    raw = json.dumps(
        {
            "facts": [{"text": "cable", "present": True, "quote": "Check the cable."}],
            "claims": [
                {"sentence": "Check the cable.", "supported": True, "quote": "Check the cable."}
            ],
        }
    )
    requests, connections = _fake_sdk(monkeypatch, raw)
    judge = LanguageModelJudge()
    judgment = judge.judge(
        answer="Check the cable.", facts=("cable",), cited_texts=("Check the cable.",)
    )
    assert connections[0]["base_url"] == "http://judge.test/v1"
    assert connections[0]["api_key"] == "judge-secret"
    assert requests[0]["model"] == "Qwen3-14B"
    assert judgment.facts[0].present
    assert judgment.claims[0].supported
    judge.judge(answer="An unsupported answer.", facts=("cable",), cited_texts=())
    assert len(requests) == 1


@pytest.mark.parametrize(
    ("flag", "text"), [("false", "cable"), ("true", "cable"), (True, "another fact")]
)
def test_judge_rejects_string_booleans_and_misaligned_rows(flag: object, text: str) -> None:
    judgment = verify_model_judgment(
        json.dumps({"facts": [{"text": text, "present": flag, "quote": "cable"}]}),
        facts=("cable",),
        shown=[],
        cited_texts=("cable",),
        judge="test",
    )
    assert not judgment.facts[0].present


def test_judge_keeps_source_punctuation_verbatim(monkeypatch: pytest.MonkeyPatch) -> None:
    source = "If oil level checks above 'FULL,\" it may be due to oil cooler drain back."
    corrected = "If oil level checks above 'FULL,' it may be due to oil cooler drain back."
    answer = "An above-full reading may be caused by oil cooler drain back."
    payload = {
        "facts": [],
        "claims": [{"sentence": answer, "supported": True, "quote": source}],
    }
    requests, _ = _fake_sdk(monkeypatch, json.dumps(payload))
    judgment = LanguageModelJudge().judge(answer=answer, facts=(), cited_texts=(source,))
    assert judgment.claims[0].supported
    assert judgment.claims[0].quote == source
    assert "character-for-character" in requests[0]["messages"][0]["content"]
    payload["claims"][0]["quote"] = corrected
    rejected = verify_model_judgment(
        json.dumps(payload), facts=(), shown=[answer], cited_texts=(source,), judge="test"
    )
    assert not rejected.claims[0].supported
    assert rejected.claims[0].quote == ""


@pytest.mark.parametrize("change", ["facts", "source", "judge"])
def test_judgment_cache_invalidates_changed_facts_sources_and_judge_settings(
    tmp_path: Path,
    change: str,
) -> None:
    attempt = _attempt()
    judge = QuoteJudge()
    assert score_attempts([attempt], judge, tmp_path)[1] == 0
    assert score_attempts([attempt], judge, tmp_path)[1] == 1

    class ChangedJudge(QuoteJudge):
        cache_key = "changed-endpoint-or-settings"

    changed = attempt
    if change == "facts":
        changed = replace(attempt, required_facts=("different fact",))
    elif change == "source":
        changed = replace(attempt, cited_texts=("different text",))
    else:
        judge = ChangedJudge()
    assert score_attempts([changed], judge, tmp_path)[1] == 0


def test_reproduce_rejects_historical_protocol_before_indexing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from graphrag_poc.eval import reproduce

    metrics = tmp_path / "metrics.json"
    metrics.write_text("{}")
    monkeypatch.setattr(reproduce, "METRICS_PATH", metrics)
    monkeypatch.setattr(reproduce, "ensure_index", lambda: pytest.fail("must stop before indexing"))
    assert reproduce.main() == 1
