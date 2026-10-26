"""Reciprocal rank fusion of the dense list and the sparse list."""

from dataclasses import dataclass

from graphrag_poc.index.store import Hit

RRF_K = 60


@dataclass(frozen=True)
class FusedHit:
    """One passage after fusion. Channels are the lists that returned it."""

    node_id: str
    text: str
    lang: str
    page_start: int
    page_end: int
    doc_key: str
    type: str
    channels: tuple[str, ...]
    best_rank: int
    rrf_score: float


def fuse(
    channels: dict[str, list[Hit]],
    *,
    k: int = RRF_K,
    weights: dict[str, float] | None = None,
) -> list[FusedHit]:
    """Merge ranked lists. A duplicate keeps its best rank and the union of channels.

    The score is reciprocal rank fusion: each list contributes weight / (k + rank).
    The default weight is 1. Rank is 1-based. A repeated node inside one list
    keeps its first, best rank.
    """

    scores: dict[str, float] = {}
    best_rank: dict[str, int] = {}
    seen_channels: dict[str, set[str]] = {}
    exemplars: dict[str, Hit] = {}
    for name, hits in channels.items():
        seen: set[str] = set()
        for rank, hit in enumerate(hits, start=1):
            if hit.node_id in seen:
                continue
            seen.add(hit.node_id)
            weight = 1.0 if weights is None else weights.get(name, 1.0)
            scores[hit.node_id] = scores.get(hit.node_id, 0.0) + weight / (k + rank)
            previous = best_rank.get(hit.node_id)
            best_rank[hit.node_id] = rank if previous is None else min(previous, rank)
            seen_channels.setdefault(hit.node_id, set()).add(name)
            exemplars.setdefault(hit.node_id, hit)
    ordered = sorted(scores, key=lambda node_id: (-scores[node_id], best_rank[node_id], node_id))
    fused: list[FusedHit] = []
    for node_id in ordered:
        hit = exemplars[node_id]
        fused.append(
            FusedHit(
                node_id=node_id,
                text=hit.text,
                lang=hit.lang,
                page_start=hit.page_start,
                page_end=hit.page_end,
                doc_key=hit.doc_key,
                type=hit.type,
                channels=tuple(sorted(seen_channels[node_id])),
                best_rank=best_rank[node_id],
                rrf_score=scores[node_id],
            )
        )
    return fused
