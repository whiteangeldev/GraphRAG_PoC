"""Walk bounded source relationships from linked seeds and return passage ids."""

import re
from dataclasses import dataclass
from typing import Any, cast

from neo4j import Driver, Session

from graphrag_poc.graph.config import HOP_DEPTH, NODE_CAP, REFERENCE_HOP_DEPTH
from graphrag_poc.models.graph import EdgeType

_TYPES = frozenset(item.value for item in EdgeType)
_PASSAGE_OUT = frozenset({"NEXT", "BOUND_CAUTION", "PARENT", "REFERS_TO"})


@dataclass(frozen=True)
class Seeds:
    """Node keys the walk starts from. Each list is that label's business key."""

    passages: tuple[str, ...] = ()
    malfunctions: tuple[str, ...] = ()
    parts: tuple[str, ...] = ()
    models: tuple[str, ...] = ()
    cases: tuple[str, ...] = ()


@dataclass(frozen=True)
class TraversalHit:
    """One passage reached by the walk."""

    node_id: str
    text: str
    lang: str
    page_start: int
    page_end: int
    doc_key: str
    type: str
    hops: int
    path: tuple[str, ...]
    provenance: tuple[dict[str, str | int | float | bool | None], ...]
    score: float


def traverse(
    driver: Driver,
    seeds: Seeds,
    edge_types: tuple[str, ...],
    *,
    hops: int = HOP_DEPTH,
    cap: int = NODE_CAP,
    question: str = "",
    build: str | None = None,
) -> list[TraversalHit]:
    """Return at most `cap` passages with explicit paths and source provenance."""

    allowed = _checked(edge_types)
    depth = max(1, min(hops, REFERENCE_HOP_DEPTH))
    if cap < 1:
        return []
    terms = _question_terms(question)
    found: dict[str, TraversalHit] = {}
    with driver.session() as session:
        source_ids = tuple(dict.fromkeys((*seeds.passages, *seeds.malfunctions)))
        if source_ids and "REFERS_TO" in allowed:
            reference_depth = depth if "PARENT" in allowed else 1
            _walk_references(session, source_ids, reference_depth, cap, build, terms, found)
        if source_ids and {"MENTIONS", "LISTS"} <= allowed and depth >= 2:
            _walk_mentions(session, source_ids, cap, build, found)
        if seeds.parts and "LISTS" in allowed:
            _walk_part_seeds(session, seeds.parts, cap, build, found)
        passage_types = allowed & _PASSAGE_OUT
        if "REFERS_TO" in allowed:
            passage_types -= {"REFERS_TO", "PARENT"}
        if seeds.passages and passage_types:
            _walk_passages(session, seeds.passages, passage_types, depth, cap, build, found)
        if seeds.malfunctions and {"CANDIDATE_PART", "LISTS"} <= allowed and depth >= 2:
            _walk_parts(session, seeds.malfunctions, question, cap, build, found)
        if seeds.malfunctions and "STATES" in allowed:
            _walk_states(session, seeds.malfunctions, cap, build, found)
        if seeds.models and "APPLIES_TO" in allowed:
            _walk_models(session, seeds.models, cap, build, found)
        if seeds.cases and allowed & {"ABOUT", "INSTALLED"}:
            _walk_cases(session, seeds.cases, allowed, depth, cap, build, found)
        _load_passages(session, found, build)
    ordered = sorted(found.values(), key=lambda hit: _rank(hit, terms))
    return ordered[:cap]


def _question_terms(question: str) -> set[str]:
    return set(re.findall(r"\w{3,}", question.lower())) - {
        "the",
        "and",
        "for",
        "which",
        "what",
        "that",
        "this",
        "does",
        "with",
        "from",
        "should",
        "before",
        "after",
        "how",
        "its",
        "are",
        "can",
        "must",
    }


_PATH_SCOPE = (
    "($build IS NULL OR ("
    "all(v IN nodes(path) WHERE coalesce(v.build, 'corpus') = $build) AND "
    "all(e IN relationships(path) WHERE coalesce(e.build, 'corpus') = $build))) "
)
_PATH_SELECTION = (
    "WITH n, path ORDER BY length(path), "
    "[v IN nodes(path) | coalesce(v.node_id, v.part_number, v.case_id, v.name, v.doc_key)] "
    "WITH n, head(collect(path)) AS path "
)
_PATH_TRACE = (
    "[e IN relationships(path) | {rel: type(e), rule: e.rule, doc_key: e.doc_key, "
    "page_start: e.page_start, case_id: e.case_id, derived: e.derived, weight: e.weight}] "
    "AS trace "
)
_PATH_RESULT = (
    _PATH_SELECTION
    + "RETURN n.node_id AS node_id, "
    + _PATH_TRACE
    + "ORDER BY length(path), n.node_id LIMIT $cap"
)
_REFERENCE_RESULT = (
    _PATH_SELECTION
    + "WITH n, path, size([pattern IN $patterns WHERE toLower(coalesce(n.text, '')) =~ pattern]) "
    "AS overlap RETURN n.node_id AS node_id, "
    + _PATH_TRACE
    + "ORDER BY overlap DESC, length(path), n.node_id LIMIT $cap"
)


def _walk_references(
    session: Session,
    seeds: tuple[str, ...],
    depth: int,
    cap: int,
    build: str | None,
    terms: set[str],
    found: dict[str, TraversalHit],
) -> None:
    # PARENT is stored child -> parent; walking it backwards stays inside the
    # referenced procedure. Every structural edge counts toward the actual hop bound.
    rows = _run(
        session,
        "MATCH path=(s:Passage)-[:REFERS_TO]->(root:Passage)"
        f"<-[:PARENT*0..{depth - 1}]-(n:Passage) "
        "WHERE s.node_id IN $ids AND " + _PATH_SCOPE + _REFERENCE_RESULT,
        {
            "ids": list(seeds),
            "cap": cap,
            "build": build,
            # Python word tokens use Unicode letters/numbers and underscore.
            # Explicit Java classes preserve those boundaries across newlines.
            "patterns": [
                rf"(?s).*(?<![\p{{L}}\p{{N}}_]){re.escape(term)}(?![\p{{L}}\p{{N}}_]).*"
                for term in sorted(terms)
            ],
        },
    )
    _put_paths(found, rows)


def _walk_mentions(
    session: Session,
    seeds: tuple[str, ...],
    cap: int,
    build: str | None,
    found: dict[str, TraversalHit],
) -> None:
    rows = _run(
        session,
        "MATCH path=(s:Passage)-[:MENTIONS]->(:Part)-[:LISTS]->(n:Passage) "
        "WHERE s.node_id IN $ids AND " + _PATH_SCOPE + _PATH_RESULT,
        {"ids": list(seeds), "cap": cap, "build": build},
    )
    _put_paths(found, rows)


def _walk_part_seeds(
    session: Session,
    seeds: tuple[str, ...],
    cap: int,
    build: str | None,
    found: dict[str, TraversalHit],
) -> None:
    rows = _run(
        session,
        "MATCH path=(p:Part)-[:LISTS]->(n:Passage) "
        "WHERE (p.part_number IN $ids OR p.node_id IN $ids) AND " + _PATH_SCOPE + _PATH_RESULT,
        {"ids": list(seeds), "cap": cap, "build": build},
    )
    _put_paths(found, rows)


def _put_paths(found: dict[str, TraversalHit], rows: list[Any]) -> None:
    for row in rows:
        trace = row["trace"]
        path = tuple(str(item["rel"]) for item in trace)
        if not path:
            continue
        provenance = tuple(_prov(item) for item in trace)
        score = min(float(item["weight"] or 1.0) for item in provenance) / len(path)
        node_id = str(row["node_id"])
        previous = found.get(node_id)
        if previous is None or score > previous.score:
            found[node_id] = TraversalHit(
                node_id, "", "", 1, 1, "", "", len(path), path, provenance, score
            )


def _checked(edge_types: tuple[str, ...]) -> set[str]:
    unknown = set(edge_types) - _TYPES
    if unknown:
        raise ValueError(f"unknown edge type {sorted(unknown)}")
    return set(edge_types)


def _walk_passages(
    session: Session,
    seeds: tuple[str, ...],
    types: set[str],
    hops: int,
    cap: int,
    build: str | None,
    found: dict[str, TraversalHit],
) -> None:
    pattern = _pattern(types)
    rows = _run(
        session,
        f"MATCH path=(s:Passage)-[:{pattern}*1..{min(hops, 2)}]->(n:Passage) "
        "WHERE s.node_id IN $ids AND " + _PATH_SCOPE + _PATH_RESULT,
        {"ids": list(seeds), "cap": cap, "build": build},
    )
    _put_paths(found, rows)


def _walk_parts(
    session: Session,
    seeds: tuple[str, ...],
    question: str,
    cap: int,
    build: str | None,
    found: dict[str, TraversalHit],
) -> None:
    rows = _run(
        session,
        "MATCH path=(m:Malfunction)-[c:CANDIDATE_PART]->(p:Part)-[:LISTS]->(n:Passage) "
        "WHERE m.node_id IN $ids AND n.node_id = p.node_id AND "
        + _PATH_SCOPE
        + "RETURN n.node_id AS node_id, c.keyword AS keyword, "
        + _PATH_TRACE
        + "ORDER BY CASE WHEN $question CONTAINS toLower(c.keyword) THEN 0 ELSE 1 END, "
        "n.node_id LIMIT $cap",
        {"ids": list(seeds), "cap": min(cap, 1), "build": build, "question": question.lower()},
    )
    _put_paths(found, rows)


def _walk_states(
    session: Session,
    seeds: tuple[str, ...],
    cap: int,
    build: str | None,
    found: dict[str, TraversalHit],
) -> None:
    rows = _run(
        session,
        "MATCH path=(m:Malfunction)-[:STATES]->(n:Passage) "
        "WHERE m.node_id IN $ids AND " + _PATH_SCOPE + _PATH_RESULT,
        {"ids": list(seeds), "cap": cap, "build": build},
    )
    _put_paths(found, rows)


def _walk_models(
    session: Session,
    seeds: tuple[str, ...],
    cap: int,
    build: str | None,
    found: dict[str, TraversalHit],
) -> None:
    rows = _run(
        session,
        "MATCH path=(n:Passage)-[:APPLIES_TO]->(m:Model) "
        "WHERE m.name IN $ids AND " + _PATH_SCOPE + _PATH_RESULT,
        {"ids": list(seeds), "cap": cap, "build": build},
    )
    _put_paths(found, rows)


def _walk_cases(
    session: Session,
    seeds: tuple[str, ...],
    types: set[str],
    depth: int,
    cap: int,
    build: str | None,
    found: dict[str, TraversalHit],
) -> None:
    if depth < 2:
        return
    if {"ABOUT", "STATES"} <= types:
        rows = _run(
            session,
            "MATCH path=(c:Case)-[:ABOUT]->(:Malfunction)-[:STATES]->(n:Passage) "
            "WHERE c.case_id IN $ids AND " + _PATH_SCOPE + _PATH_RESULT,
            {"ids": list(seeds), "cap": cap, "build": build},
        )
        _put_paths(found, rows)
    if {"INSTALLED", "LISTS"} <= types:
        rows = _run(
            session,
            "MATCH path=(c:Case)-[:INSTALLED]->(p:Part)-[:LISTS]->(n:Passage) "
            "WHERE c.case_id IN $ids AND n.node_id = p.node_id AND " + _PATH_SCOPE + _PATH_RESULT,
            {"ids": list(seeds), "cap": 1, "build": build},
        )
        _put_paths(found, rows)


def _load_passages(
    session: Session, found: dict[str, TraversalHit], build: str | None = None
) -> None:
    if not found:
        return
    rows = _run(
        session,
        "MATCH (p:Passage) WHERE p.node_id IN $ids "
        "AND ($build IS NULL OR coalesce(p.build, 'corpus') = $build) "
        "RETURN p.node_id AS node_id, p.text AS text, p.lang AS lang, "
        "p.page_start AS page_start, p.page_end AS page_end, "
        "p.doc_key AS doc_key, p.type AS type",
        {"ids": list(found), "build": build},
    )
    loaded = {str(row["node_id"]): row for row in rows}
    for node_id, hit in list(found.items()):
        row = loaded.get(node_id)
        if row is None:
            del found[node_id]
            continue
        found[node_id] = TraversalHit(
            node_id=node_id,
            text=str(row["text"] or ""),
            lang=str(row["lang"] or ""),
            page_start=_int(row["page_start"]),
            page_end=_int(row["page_end"]),
            doc_key=str(row["doc_key"] or ""),
            type=str(row["type"] or ""),
            hops=hit.hops,
            path=hit.path,
            provenance=hit.provenance,
            score=hit.score,
        )


def _prov(row: object) -> dict[str, str | int | float | bool | None]:
    page = _field(row, "page_start")
    case_id = str(_field(row, "case_id") or "")
    doc_key = str(_field(row, "doc_key") or "")
    return {
        "rule": str(_field(row, "rule") or ""),
        "doc_key": doc_key or None,
        "page_start": page if isinstance(page, int) and not isinstance(page, bool) else None,
        "case_id": case_id or None,
        "derived": bool(cast(Any, row).get("derived", False)),
        "weight": cast(Any, row).get("weight", 1.0),
    }


def _field(row: object, name: str) -> Any:
    return cast(Any, row)[name]


def _rank(hit: TraversalHit, terms: set[str]) -> tuple[int, float, int, float, str]:
    if hit.path == ("STATES",):
        group = 0
    elif "LISTS" in hit.path and "MENTIONS" not in hit.path:
        group = 1
    else:
        group = 2
    # Order referenced content by question terms before structural distance, so
    # multiple continuation headings cannot crowd instructions out of the ten
    # passages supplied to the model. This never selects an answer or drops a hit.
    overlap = (
        len(terms & set(re.findall(r"\w{3,}", hit.text.lower()))) if "REFERS_TO" in hit.path else 0
    )
    confidence = min(float(item.get("weight") or 1.0) for item in hit.provenance or ({},))
    return (group, -confidence, -overlap, -hit.score, hit.node_id)


def _pattern(types: set[str]) -> str:
    return "|".join(sorted(types))


def _run(session: Session, query: str, values: dict[str, object]) -> list[Any]:
    return list(session.run(query, values))


def _int(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return 1
