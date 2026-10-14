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


def format_mrr(denominators: tuple[int, ...]) -> str:
    """Mean reciprocal rank. A zero denominator means the gold passage was absent."""

    if not denominators:
        return "—"
    total = sum((1.0 / rank) if rank else 0.0 for rank in denominators)
    return f"{total / len(denominators):.3f}"
