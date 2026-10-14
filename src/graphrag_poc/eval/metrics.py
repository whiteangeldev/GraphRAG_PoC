"""Retrieval and answer metrics from the requirements definition, section 9."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Ratio:
    numerator: int
    denominator: int


@dataclass(frozen=True)
class SliceMetrics:
    """Counts for one question type, or for the whole set."""

    questions: int
    hit_at_10: Ratio
    mrr_denominators: tuple[int, ...]
    evidence: Ratio
    facts: Ratio
    claims: Ratio
    actions: Ratio


def first_gold_rank(gold_ids: tuple[str, ...], ranked_ids: tuple[str, ...]) -> int:
    """1-based rank of the first gold passage. Zero means it was not retrieved."""

    gold = set(gold_ids)
    for rank, node_id in enumerate(ranked_ids, start=1):
        if node_id in gold:
            return rank
    return 0


def evidence_hits(gold_ids: tuple[str, ...], evidence_ids: tuple[str, ...]) -> int:
    evidence = set(evidence_ids)
    return sum(1 for node_id in gold_ids if node_id in evidence)


def format_percent(ratio: Ratio) -> str:
    if ratio.denominator == 0:
        return "—"
    return f"{100.0 * ratio.numerator / ratio.denominator:.1f}"


SHARE_KEYS = (
    "hit_at_10",
    "evidence_recall",
    "required_fact_recall",
    "claim_precision",
    "action_accuracy",
)
REPRODUCTION_TOLERANCE = 0.02


def metric_drifts(
    previous: dict[str, object],
    current: dict[str, object],
    *,
    tolerance: float = REPRODUCTION_TOLERANCE,
) -> list[str]:
    """Differences larger than `tolerance` on the fraction from 0 to 1.

    A share metric moves by 0.02 when it changes by 2 percentage points.
    MRR uses the same absolute tolerance.
    """

    errors: list[str] = []
    for field in ("embedding_model", "generation_model", "judge"):
        if previous.get(field) != current.get(field):
            errors.append(f"{field} changed from {previous.get(field)!r} to {current.get(field)!r}")
    errors.extend(
        _slice_drifts("overall", previous.get("overall"), current.get("overall"), tolerance)
    )
    prev_types = previous.get("by_type")
    curr_types = current.get("by_type")
    if not isinstance(prev_types, dict) or not isinstance(curr_types, dict):
        errors.append("metrics are missing by_type")
        return errors
    names = sorted(set(prev_types) | set(curr_types))
    for name in names:
        if name not in prev_types or name not in curr_types:
            errors.append(f"{name} is in only one report")
            continue
        errors.extend(_slice_drifts(str(name), prev_types[name], curr_types[name], tolerance))
    return errors


def _slice_drifts(name: str, previous: object, current: object, tolerance: float) -> list[str]:
    if not isinstance(previous, dict) or not isinstance(current, dict):
        return [f"{name} metrics are not objects"]
    errors: list[str] = []
    keys = (*SHARE_KEYS, "mrr")
    for key in keys:
        before = _fraction(previous, key)
        after = _fraction(current, key)
        if before is None and after is None:
            continue
        if before is None or after is None or abs(before - after) > tolerance:
            errors.append(f"{name} {key} moved from {_show(before)} to {_show(after)}")
    return errors


def _fraction(block: dict[str, object], key: str) -> float | None:
    if key == "mrr":
        raw = block.get("mrr_denominators")
        if not isinstance(raw, list) or not raw:
            return None
        total = 0.0
        for rank in raw:
            if not isinstance(rank, int):
                return None
            if rank > 0:
                total += 1.0 / rank
        return total / len(raw)
    raw = block.get(key)
    if not isinstance(raw, dict):
        return None
    numerator = raw.get("numerator")
    denominator = raw.get("denominator")
    if not isinstance(numerator, int) or not isinstance(denominator, int) or denominator == 0:
        return None
    return numerator / denominator


def _show(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:.4f}"


def format_mrr(denominators: tuple[int, ...]) -> str:
    """Mean reciprocal rank. A zero denominator means the gold passage was absent."""

    if not denominators:
        return "—"
    total = sum((1.0 / rank) if rank else 0.0 for rank in denominators)
    return f"{total / len(denominators):.3f}"
