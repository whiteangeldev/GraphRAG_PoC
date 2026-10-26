"""Walk one or two hops from linked seeds and return passage ids."""

from dataclasses import dataclass
from typing import Any, cast

from neo4j import Driver, Session

from graphrag_poc.graph.config import HOP_DEPTH, NODE_CAP
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
) -> list[TraversalHit]:
    """Return at most `cap` passages. Shorter paths and the canonical part come first."""

    allowed = _checked(edge_types)
    depth = 1 if hops < 2 else 2
    found: dict[str, TraversalHit] = {}
    with driver.session() as session:
        if seeds.passages and allowed & _PASSAGE_OUT:
            _walk_passages(session, seeds.passages, allowed & _PASSAGE_OUT, depth, found)
        if seeds.malfunctions and {"CANDIDATE_PART", "LISTS"} <= allowed and depth >= 2:
            _walk_parts(session, seeds.malfunctions, question, found)
        if seeds.malfunctions and "STATES" in allowed:
            _walk_states(session, seeds.malfunctions, found)
        if seeds.models and "APPLIES_TO" in allowed:
            _walk_models(session, seeds.models, found)
        if seeds.cases and allowed & {"ABOUT", "INSTALLED"}:
            _walk_cases(session, seeds.cases, allowed, found)
        _load_passages(session, found)
    ordered = sorted(found.values(), key=_rank)
    return ordered[:cap]


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
    found: dict[str, TraversalHit],
) -> None:
    pattern = _pattern(types)
    rows = _run(
        session,
        f"MATCH (s:Passage)-[r:{pattern}]->(n:Passage) "
        "WHERE s.node_id IN $ids "
        "RETURN n.node_id AS node_id, type(r) AS rel, r.rule AS rule, "
        "r.doc_key AS doc_key, r.page_start AS page_start, r.case_id AS case_id",
        {"ids": list(seeds)},
    )
    for row in rows:
        _put(found, str(row["node_id"]), (str(row["rel"]),), _prov(row), 1)
    if hops < 2:
        return
    rows = _run(
        session,
        f"MATCH (s:Passage)-[r1:{pattern}]->(:Passage)-[r2:{pattern}]->(n:Passage) "
        "WHERE s.node_id IN $ids "
        "RETURN n.node_id AS node_id, type(r1) AS first, type(r2) AS rel, "
        "r2.rule AS rule, r2.doc_key AS doc_key, r2.page_start AS page_start, "
        "r2.case_id AS case_id",
        {"ids": list(seeds)},
    )
    for row in rows:
        _put(found, str(row["node_id"]), (str(row["first"]), str(row["rel"])), _prov(row), 2)


def _walk_parts(
    session: Session,
    seeds: tuple[str, ...],
    question: str,
    found: dict[str, TraversalHit],
) -> None:
    rows = _run(
        session,
        "MATCH (m:Malfunction)-[c:CANDIDATE_PART]->(p:Part)-[l:LISTS]->(n:Passage) "
        "WHERE m.node_id IN $ids AND n.node_id = p.node_id "
        "RETURN n.node_id AS node_id, c.keyword AS keyword, l.rule AS rule, "
        "l.doc_key AS doc_key, l.page_start AS page_start, l.case_id AS case_id "
        "ORDER BY n.node_id",
        {"ids": list(seeds)},
    )
    folded = question.lower()
    matched = [row for row in rows if str(row["keyword"]).lower() in folded]
    chosen = matched or rows
    if not chosen:
        return
    row = chosen[0]
    _put(found, str(row["node_id"]), ("CANDIDATE_PART", "LISTS"), _prov(row), 2)


def _walk_states(session: Session, seeds: tuple[str, ...], found: dict[str, TraversalHit]) -> None:
    rows = _run(
        session,
        "MATCH (m:Malfunction)-[r:STATES]->(n:Passage) "
        "WHERE m.node_id IN $ids "
        "RETURN n.node_id AS node_id, r.rule AS rule, r.doc_key AS doc_key, "
        "r.page_start AS page_start, r.case_id AS case_id",
        {"ids": list(seeds)},
    )
    for row in rows:
        _put(found, str(row["node_id"]), ("STATES",), _prov(row), 1)


def _walk_models(session: Session, seeds: tuple[str, ...], found: dict[str, TraversalHit]) -> None:
    rows = _run(
        session,
        "MATCH (n:Passage)-[r:APPLIES_TO]->(m:Model) "
        "WHERE m.name IN $ids "
        "RETURN n.node_id AS node_id, r.rule AS rule, r.doc_key AS doc_key, "
        "r.page_start AS page_start, r.case_id AS case_id "
        "ORDER BY n.node_id LIMIT $cap",
        {"ids": list(seeds), "cap": NODE_CAP},
    )
    for row in rows:
        _put(found, str(row["node_id"]), ("APPLIES_TO",), _prov(row), 1)


def _walk_cases(
    session: Session,
    seeds: tuple[str, ...],
    types: set[str],
    found: dict[str, TraversalHit],
) -> None:
    if "ABOUT" in types:
        rows = _run(
            session,
            "MATCH (c:Case)-[:ABOUT]->(m:Malfunction)-[r:STATES]->(n:Passage) "
            "WHERE c.case_id IN $ids "
            "RETURN n.node_id AS node_id, r.rule AS rule, r.doc_key AS doc_key, "
            "r.page_start AS page_start, r.case_id AS case_id",
            {"ids": list(seeds)},
        )
        for row in rows:
            _put(found, str(row["node_id"]), ("ABOUT", "STATES"), _prov(row), 2)
    if "INSTALLED" in types:
        rows = _run(
            session,
            "MATCH (c:Case)-[:INSTALLED]->(p:Part)-[r:LISTS]->(n:Passage) "
            "WHERE c.case_id IN $ids AND n.node_id = p.node_id "
            "RETURN n.node_id AS node_id, r.rule AS rule, r.doc_key AS doc_key, "
            "r.page_start AS page_start, r.case_id AS case_id "
            "ORDER BY n.node_id LIMIT 1",
            {"ids": list(seeds)},
        )
        for row in rows:
            _put(found, str(row["node_id"]), ("INSTALLED", "LISTS"), _prov(row), 2)


def _load_passages(session: Session, found: dict[str, TraversalHit]) -> None:
    if not found:
        return
    rows = _run(
        session,
        "MATCH (p:Passage) WHERE p.node_id IN $ids "
        "RETURN p.node_id AS node_id, p.text AS text, p.lang AS lang, "
        "p.page_start AS page_start, p.page_end AS page_end, "
        "p.doc_key AS doc_key, p.type AS type",
        {"ids": list(found)},
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


def _put(
    found: dict[str, TraversalHit],
    node_id: str,
    path: tuple[str, ...],
    provenance: dict[str, str | int | float | bool | None],
    hops: int,
) -> None:
    score = 1.0 / hops
    current = found.get(node_id)
    if current is not None and (current.hops < hops or current.score >= score):
        return
    found[node_id] = TraversalHit(node_id, "", "", 1, 1, "", "", hops, path, (provenance,), score)


def _prov(row: object) -> dict[str, str | int | float | bool | None]:
    page = _field(row, "page_start")
    case_id = str(_field(row, "case_id") or "")
    doc_key = str(_field(row, "doc_key") or "")
    return {
        "rule": str(_field(row, "rule") or ""),
        "doc_key": doc_key or None,
        "page_start": page if isinstance(page, int) and not isinstance(page, bool) else None,
        "case_id": case_id or None,
        "derived": False,
        "weight": 1.0,
    }


def _field(row: object, name: str) -> Any:
    return cast(Any, row)[name]


def _rank(hit: TraversalHit) -> tuple[int, int, str]:
    if hit.path == ("STATES",):
        group = 0
    elif "LISTS" in hit.path:
        group = 1
    else:
        group = 2
    return (group, hit.hops, hit.node_id)


def _pattern(types: set[str]) -> str:
    return "|".join(sorted(types))


def _run(session: Session, query: str, values: dict[str, object]) -> list[Any]:
    return list(session.run(query, values))


def _int(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return 1
