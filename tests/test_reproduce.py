"""The cached report is reproduced when every metric stays within 0.02."""

import json

from graphrag_poc.eval.metrics import metric_drifts
from graphrag_poc.eval.score import METRICS_PATH


def _block(
    *,
    hit: tuple[int, int] = (98, 141),
    mrr: tuple[int, ...] = (1, 2),
    evidence: tuple[int, int] = (10, 20),
    facts: tuple[int, int] = (1, 4),
    claims: tuple[int, int] = (3, 4),
    actions: tuple[int, int] = (9, 10),
) -> dict[str, object]:
    return {
        "hit_at_10": {"numerator": hit[0], "denominator": hit[1]},
        "mrr_denominators": list(mrr),
        "evidence_recall": {"numerator": evidence[0], "denominator": evidence[1]},
        "required_fact_recall": {"numerator": facts[0], "denominator": facts[1]},
        "claim_precision": {"numerator": claims[0], "denominator": claims[1]},
        "action_accuracy": {"numerator": actions[0], "denominator": actions[1]},
    }


def _report(block: dict[str, object], *, model: str = "embed-test") -> dict[str, object]:
    return {
        "embedding_model": model,
        "generation_model": "",
        "judge": "quote",
        "overall": block,
        "by_type": {"lookup": block, "unanswerable": _block(hit=(0, 0), mrr=(), evidence=(0, 0))},
    }


def test_identical_metrics_have_no_drift() -> None:
    payload = _report(_block())
    assert metric_drifts(payload, payload) == []


def test_two_percentage_points_is_the_limit() -> None:
    before = _report(_block(hit=(100, 141)))
    inside = _report(_block(hit=(100 - 2, 141)))
    outside = _report(_block(hit=(100 - 3, 141)))
    assert metric_drifts(before, inside) == []
    assert metric_drifts(before, outside)


def test_a_blank_metric_must_stay_blank() -> None:
    before = _report(_block())
    after = _report(_block())
    overall = after["overall"]
    assert isinstance(overall, dict)
    overall["hit_at_10"] = {"numerator": 0, "denominator": 0}
    drifts = metric_drifts(before, after)
    assert any("overall hit_at_10" in drift for drift in drifts)


def test_cached_metrics_match_themselves() -> None:
    payload = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    assert metric_drifts(payload, payload) == []
