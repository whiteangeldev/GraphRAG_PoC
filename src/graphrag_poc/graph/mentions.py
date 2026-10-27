"""Derived MENTIONS edges. A surface form in the passage text is the evidence."""

import re

from graphrag_poc.graph.build import Edge, GraphData
from graphrag_poc.graph.config import MENTION_WEIGHT
from graphrag_poc.graph.part_match import PartMatcher

_MODEL = re.compile(r"\bM\d{3,4}(?:A\d)?\b")
_RULE = "surface form in the passage text"


def derive_mentions(graph: GraphData) -> list[Edge]:
    """Link a passage to a model or part whose name is written in the passage.

    The weight stays below 1. Two calls on the same graph return the same edges.
    """

    models = {row["name"] for row in graph.models}
    parts = PartMatcher(row["part_number"] for row in graph.parts)
    edges: dict[tuple[str, str, str], Edge] = {}
    for passage in graph.passages:
        text = str(passage["text"])
        start = str(passage["id"])
        doc_key = str(passage["doc_key"])
        page = _page(passage.get("page_start"))
        for name in _MODEL.findall(text):
            if name not in models:
                continue
            _add(edges, start, f"model:{name}", doc_key, page, name)
        for number in parts.find(text):
            _add(edges, start, f"part:{number}", doc_key, page, number)
    return sorted(edges.values(), key=lambda edge: (edge.start_id, edge.end_id, edge.keyword))


def _add(
    edges: dict[tuple[str, str, str], Edge],
    start: str,
    end: str,
    doc_key: str,
    page: int,
    surface: str,
) -> None:
    edges.setdefault(
        (start, end, surface),
        Edge(
            "MENTIONS",
            start,
            end,
            _RULE,
            doc_key,
            page,
            keyword=surface,
            derived=True,
            weight=MENTION_WEIGHT,
        ),
    )


def _page(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 1:
        return value
    raise ValueError("a mention needs the passage page")
