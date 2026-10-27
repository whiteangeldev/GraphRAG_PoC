"""Every scoring entry point blocks pending gold before runtime work."""

import json
import sys
from pathlib import Path

import pytest

from graphrag_poc.eval import __main__ as evaluation_cli
from graphrag_poc.eval import m3, reproduce, score
from graphrag_poc.eval.check import load_questions
from graphrag_poc.eval.gold import questions_digest


@pytest.fixture(autouse=True)
def no_runtime_work(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Pending acceptance must stop before node/index/model/endpoint work")

    monkeypatch.setattr("socket.create_connection", forbidden)
    for module in (score, reproduce, m3):
        monkeypatch.setattr(module, "configure_evaluation", lambda: None)
        monkeypatch.setattr(module, "validate_evaluation_models", forbidden)
    monkeypatch.setattr(score, "validate", forbidden)
    monkeypatch.setattr(score, "build_judge", forbidden)
    monkeypatch.setattr(score, "_retrieve_all", forbidden)
    monkeypatch.setattr(m3, "validate", forbidden)
    monkeypatch.setattr(m3, "make_driver", forbidden)
    monkeypatch.setattr(reproduce, "ensure_index", forbidden)
    monkeypatch.setattr(reproduce, "japanese_sample_indexed", forbidden)
    monkeypatch.setenv("EMBEDDING_MODEL", "offline-test")


@pytest.mark.parametrize("explicit_questions", [False, True])
def test_baseline_api_requires_acceptance_even_with_explicit_records(
    explicit_questions: bool,
) -> None:
    arguments = {"questions": load_questions()} if explicit_questions else {}
    with pytest.raises(RuntimeError, match="pending client agreement"):
        score.run_baseline(**arguments)


@pytest.mark.parametrize("cached_metrics", [False, True])
def test_direct_reproduce_requires_acceptance_before_index_or_model_checks(
    cached_metrics: bool,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    metrics = tmp_path / "metrics.json"
    if cached_metrics:
        metrics.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(reproduce, "METRICS_PATH", metrics)
    assert reproduce.main() == 1
    assert "pending client agreement" in capsys.readouterr().err


@pytest.mark.parametrize("option", ["--score", "--reproduce"])
def test_evaluation_cli_dispatch_cannot_bypass_pending_acceptance(
    option: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["graphrag_poc.eval", option])
    assert evaluation_cli.main() == 1
    assert "pending client agreement" in capsys.readouterr().err


def test_graph_api_and_cli_check_acceptance_before_nodes_or_models(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(RuntimeError, match="pending client agreement"):
        m3.run_graph()
    assert m3.main([]) == 1
    assert "pending client agreement" in capsys.readouterr().out


@pytest.mark.parametrize("module", [score, reproduce, m3], ids=["baseline", "reproduce", "graph"])
def test_accepted_preflight_continues_to_normal_validation(
    module: object, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(module, "acceptance_errors", lambda _records: [])

    def offline_stop(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("offline validation reached")

    if module is reproduce:
        monkeypatch.setattr(reproduce, "validate_evaluation_models", offline_stop)
        assert reproduce.main() == 1
        assert "offline validation reached" in capsys.readouterr().err
    else:
        monkeypatch.setattr(module, "validate", offline_stop)
        entrypoint = score.run_baseline if module is score else m3.run_graph
        with pytest.raises(RuntimeError, match="offline validation reached"):
            entrypoint()


def test_accepted_reproduction_still_rejects_stale_protocol_before_indexing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(reproduce, "acceptance_errors", lambda _records: [])
    monkeypatch.setattr(reproduce, "validate_evaluation_models", lambda: None)
    monkeypatch.setattr(reproduce, "evaluation_fingerprint", lambda: "current-protocol")
    metrics = tmp_path / "metrics.json"
    metrics.write_text(
        json.dumps(
            {
                "questions_sha256": questions_digest(load_questions()),
                "evaluation_config_sha256": "old-protocol",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(reproduce, "METRICS_PATH", metrics)
    assert reproduce.main() == 1
    assert "Saved benchmark/model protocol is different" in capsys.readouterr().err


@pytest.mark.parametrize("changed", ["questions", "models"])
def test_accepted_graph_still_requires_matching_baseline_before_runtime_work(
    changed: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(m3, "acceptance_errors", lambda _records: [])
    monkeypatch.setattr(m3, "validate", lambda _records: [])
    monkeypatch.setattr(m3, "validate_evaluation_models", lambda: None)
    monkeypatch.setattr(m3, "evaluation_fingerprint", lambda: "current-models")
    metrics = tmp_path / "metrics.json"
    metrics.write_text(
        json.dumps(
            {
                "questions_sha256": "old-questions"
                if changed == "questions"
                else questions_digest(load_questions()),
                "evaluation_config_sha256": "old-models"
                if changed == "models"
                else "current-models",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(m3, "BASELINE_METRICS", metrics)
    expected = "different/unversioned benchmark" if changed == "questions" else "model/protocol"
    with pytest.raises(RuntimeError, match=expected):
        m3.run_graph()
