"""Incomplete baselines cannot waive comparison gates or start model work."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from graphrag_poc.eval import m3
from graphrag_poc.eval.gold import questions_digest
from graphrag_poc.eval.metrics import Ratio
from graphrag_poc.retrieve.fusion import FusedHit
from graphrag_poc.retrieve.graph import RelationFrame


@pytest.fixture
def comparison() -> tuple[list[dict], dict]:
    records = [
        {
            "id": qid,
            "slice": {"question_type": kind},
            "question": f"Question for {qid}?",
            "gold": {"node_ids": [] if kind == "unanswerable" else ["source", "target"]},
            "required_facts": [] if kind == "unanswerable" else [{"text": "A source fact."}],
        }
        for qid, kind in (
            ("control-lookup", "lookup"),
            ("review-first-target", "multi_hop"),
            ("review-next-target", "relational"),
            ("control-refusal", "unanswerable"),
        )
    ]

    def block(rows: list[dict]) -> dict:
        gold_counts = [len(row["gold"]["node_ids"]) for row in rows]
        return {
            "questions": len(rows),
            "hit_at_10": {"numerator": 0, "denominator": sum(size > 0 for size in gold_counts)},
            "evidence_recall": {"numerator": 0, "denominator": sum(gold_counts)},
            "required_fact_recall": {
                "numerator": 0,
                "denominator": sum(len(row["required_facts"]) for row in rows),
            },
            "claim_precision": {"numerator": 0, "denominator": 0},
            "action_accuracy": {"numerator": 0, "denominator": len(rows)},
            "mrr_denominators": [0] * sum(size > 0 for size in gold_counts),
        }

    baseline = {
        "questions_sha256": questions_digest(records),
        "evaluation_config_sha256": "test-config",
        "overall": block(records),
        "by_type": {row["slice"]["question_type"]: block([row]) for row in records},
    }
    return records, baseline


def test_complete_baseline_matches_frozen_counts_and_allows_blank_refusal_ratios(
    comparison: tuple,
) -> None:
    records, baseline = comparison
    assert m3._baseline_errors(baseline, records) == []


@pytest.mark.parametrize(
    "damage",
    [
        "missing_type",
        "extra_type",
        "missing_overall",
        "invalid_block",
        "count",
        "denominator",
        "ranks",
    ],
)
def test_missing_or_incomparable_metrics_are_rejected(comparison: tuple, damage: str) -> None:
    records, baseline = comparison
    if damage == "missing_type":
        del baseline["by_type"]["lookup"]
    elif damage == "extra_type":
        baseline["by_type"]["invented"] = baseline["by_type"]["lookup"]
    elif damage == "missing_overall":
        del baseline["overall"]
    elif damage == "invalid_block":
        baseline["by_type"]["lookup"] = []
    elif damage == "count":
        baseline["by_type"]["lookup"]["questions"] = 2
    elif damage == "denominator":
        baseline["by_type"]["lookup"]["evidence_recall"]["denominator"] = 1
    else:
        baseline["by_type"]["lookup"]["mrr_denominators"] = [True]
    assert m3._baseline_errors(baseline, records)


@pytest.mark.parametrize("value", [True, False, float("nan"), float("inf"), -1, "1", 1.0])
def test_ratio_counts_must_be_valid_integers(comparison: tuple, value: object) -> None:
    records, baseline = comparison
    baseline["by_type"]["lookup"]["hit_at_10"]["numerator"] = value
    errors = m3._baseline_errors(baseline, records)
    assert any("lookup hit_at_10 must contain valid integer" in error for error in errors)


@pytest.mark.parametrize("value", [True, float("nan"), 1.0])
def test_question_counts_cannot_be_boolean_or_noninteger(comparison: tuple, value: object) -> None:
    records, baseline = comparison
    baseline["by_type"]["lookup"]["questions"] = value
    assert any(
        "question count differs" in error for error in m3._baseline_errors(baseline, records)
    )


def _offline_setup(
    comparison: tuple, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> tuple[list[dict], dict]:
    records, baseline = comparison
    metrics = tmp_path / "baseline.json"
    metrics.write_text(json.dumps(baseline), encoding="utf-8")
    monkeypatch.setattr(m3, "BASELINE_METRICS", metrics)
    monkeypatch.setattr(m3, "load_questions", lambda: records)
    monkeypatch.setattr(m3, "acceptance_errors", lambda _records: [])
    monkeypatch.setattr(m3, "validate", lambda _records: [])
    monkeypatch.setattr(m3, "validate_evaluation_models", lambda: None)
    monkeypatch.setattr(m3, "evaluation_fingerprint", lambda: "test-config")
    return records, baseline


def test_invalid_matching_fingerprint_baseline_stops_before_clients_or_models(
    comparison: tuple, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    comparison[1]["by_type"]["lookup"]["hit_at_10"]["numerator"] = True
    _offline_setup(comparison, monkeypatch, tmp_path)

    def forbidden(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Invalid baseline reached model/client construction")

    monkeypatch.setattr("graphrag_poc.eval.judge.build_judge", forbidden)
    monkeypatch.setattr("graphrag_poc.index.embed.build_embedder", forbidden)
    monkeypatch.setattr("graphrag_poc.index.client.make_client", forbidden)
    monkeypatch.setattr(m3, "make_driver", forbidden)
    with pytest.raises(RuntimeError, match="valid integer ratio counts"):
        m3.run_graph()


@pytest.mark.parametrize(
    "previous", [{}, {"numerator": True, "denominator": 1}, {"numerator": 0, "denominator": 2}]
)
def test_type_gates_fail_closed_on_invalid_or_changed_denominators(previous: object) -> None:
    with pytest.raises(RuntimeError, match="ratio counts"):
        m3._type_gate("lookup", "hit@10", Ratio(1, 1), previous)


def test_missing_target_metric_cannot_reduce_the_baseline_to_zero(comparison: tuple) -> None:
    _, baseline = comparison
    del baseline["by_type"]["multi_hop"]["evidence_recall"]
    with pytest.raises(RuntimeError, match="missing or invalid"):
        m3._pooled(baseline["by_type"], "evidence_recall")


@pytest.mark.parametrize("values", [[], [float("nan")], [float("inf")], [True], [-1.0]])
def test_lookup_latency_requires_real_finite_samples(values: list[float]) -> None:
    with pytest.raises(RuntimeError, match="latency samples"):
        m3._p95(values)


def test_graph_run_demonstrates_first_actual_target_without_model_calls(
    comparison: tuple, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    records, _ = _offline_setup(comparison, monkeypatch, tmp_path)
    closed = []
    monkeypatch.setattr(
        "graphrag_poc.eval.judge.build_judge", lambda: SimpleNamespace(name="test-judge")
    )
    monkeypatch.setattr("graphrag_poc.index.embed.build_embedder", lambda: object())
    monkeypatch.setattr("graphrag_poc.index.client.make_client", lambda **_kwargs: object())
    monkeypatch.setattr(
        m3, "make_driver", lambda: SimpleNamespace(close=lambda: closed.append(True))
    )
    monkeypatch.setattr(m3, "retrieve", lambda *_args: [])
    hits = [
        FusedHit(
            "actual-graph-passage", "Source text.", "en", 1, 1, "doc", "step", ("graph",), 1, 1
        )
    ]
    monkeypatch.setattr(
        m3, "retrieve_question", lambda *_args, **_kwargs: (hits, None, RelationFrame())
    )
    monkeypatch.setattr(
        m3, "attempt_from_hits", lambda *_args, **_kwargs: SimpleNamespace(temperature=0, seed=0)
    )
    monkeypatch.setattr(m3, "score_attempts", lambda *_args: ([], 0))
    monkeypatch.setattr(m3, "_write_results", lambda _rows: None)
    monkeypatch.setattr(m3, "_render", lambda *_args: _args[-1])
    report, _ = m3.run_graph()
    assert records[1]["id"] in report
    assert records[0]["id"] not in report
    assert records[2]["id"] not in report
    assert "actual-graph-passage" in report
    assert closed == [True]


def test_demonstration_reports_no_graph_evidence_without_inventing_a_passage(
    comparison: tuple,
) -> None:
    records, _ = comparison
    assert m3._demonstration(records[1], []).endswith("10: none.")
