"""Write one in-memory graph to Neo4j through Bolt."""

from collections.abc import Mapping, Sequence
from typing import Any

from neo4j import Driver, Session

from graphrag_poc.graph.build import Edge, GraphData

_LABELS = {
    "passage": ("Passage", "node_id"),
    "malfunction": ("Malfunction", "node_id"),
    "part": ("Part", "part_number"),
    "model": ("Model", "name"),
    "case": ("Case", "case_id"),
    "doc": ("Document", "doc_key"),
}


def write_graph(driver: Driver, graph: GraphData, build: str) -> None:
    """Replace the nodes of `build` and write this graph. Other builds stay."""

    clear_build(driver, build)
    with driver.session() as session:
        _write_documents(session, graph, build)
        _write_passages(session, graph, build)
        _write_malfunctions(session, graph, build)
        _write_parts(session, graph, build)
        _write_models(session, graph, build)
        _write_cases(session, graph, build)
        for edge_type in sorted({edge.type for edge in graph.edges}):
            rows = [_edge_row(edge) for edge in graph.edges if edge.type == edge_type]
            _write_edges(session, edge_type, rows, build)
    apply_constraints(driver)


def clear_build(driver: Driver, build: str) -> None:
    """Delete every node written for `build`."""

    with driver.session() as session:
        session.run("MATCH (n) WHERE n.build = $build DETACH DELETE n", build=build).consume()


def apply_constraints(driver: Driver) -> None:
    """Create the uniqueness constraints and indexes used by the corpus load."""

    from graphrag_poc.graph.load import _CONSTRAINTS

    with driver.session() as session:
        for statement in _CONSTRAINTS:
            session.run(statement).consume()


def _write_documents(session: Session, graph: GraphData, build: str) -> None:
    rows = [
        {
            "key": row["doc_key"],
            "title": row["title"],
            "lang": row["lang"],
            "doc_type": row["doc_type"],
            "edition": row["edition"],
        }
        for row in graph.documents
    ]
    _run(
        session,
        "UNWIND $rows AS row MERGE (n:Document {doc_key: row.key}) "
        "SET n.title = row.title, n.lang = row.lang, n.doc_type = row.doc_type, "
        "n.edition = row.edition, n.build = $build",
        rows,
        build,
    )


def _write_passages(session: Session, graph: GraphData, build: str) -> None:
    rows = [
        {
            "key": str(row["node_id"]),
            "text": str(row["text"]),
            "type": str(row["type"]),
            "page_start": _as_int(row["page_start"]),
            "page_end": _as_int(row["page_end"]),
            "lang": str(row["lang"]),
            "doc_key": str(row["doc_key"]),
            "breadcrumb": list(row["breadcrumb"]) if isinstance(row["breadcrumb"], list) else [],
        }
        for row in graph.passages
    ]
    _run(
        session,
        "UNWIND $rows AS row MERGE (n:Passage {node_id: row.key}) "
        "SET n.text = row.text, n.type = row.type, n.page_start = row.page_start, "
        "n.page_end = row.page_end, n.lang = row.lang, n.doc_key = row.doc_key, "
        "n.breadcrumb = row.breadcrumb, n.build = $build",
        rows,
        build,
    )


def _write_malfunctions(session: Session, graph: GraphData, build: str) -> None:
    rows = [
        {
            "key": str(row["node_id"]),
            "code": str(row["code"]),
            "page_start": _as_int(row["page_start"]),
            "doc_key": str(row["doc_key"]),
        }
        for row in graph.malfunctions
    ]
    _run(
        session,
        "UNWIND $rows AS row MERGE (n:Malfunction {node_id: row.key}) "
        "SET n.code = row.code, n.page_start = row.page_start, n.doc_key = row.doc_key, "
        "n.build = $build",
        rows,
        build,
    )


def _write_parts(session: Session, graph: GraphData, build: str) -> None:
    rows = [
        {
            "key": row["part_number"],
            "description": row["description"],
            "nsn": row["nsn"],
            "node_id": row["node_id"],
            "doc_key": row["doc_key"],
            "page_start": _as_int(row["page_start"]),
        }
        for row in graph.parts
    ]
    _run(
        session,
        "UNWIND $rows AS row MERGE (n:Part {part_number: row.key}) "
        "SET n.description = row.description, n.nsn = row.nsn, n.node_id = row.node_id, "
        "n.doc_key = row.doc_key, n.page_start = row.page_start, n.build = $build",
        rows,
        build,
    )


def _write_models(session: Session, graph: GraphData, build: str) -> None:
    rows = [{"key": row["name"], "series": row["series"]} for row in graph.models]
    _run(
        session,
        "UNWIND $rows AS row MERGE (n:Model {name: row.key}) "
        "SET n.series = row.series, n.build = $build",
        rows,
        build,
    )


def _write_cases(session: Session, graph: GraphData, build: str) -> None:
    rows = [
        {
            "key": str(row["case_id"]),
            "date": str(row["date"]),
            "model": str(row["model"]),
            "symptom": str(row["symptom"]),
            "cause": str(row["cause"]),
            "action": str(row["action"]),
            "frequency": _as_int(row["frequency"]),
        }
        for row in graph.cases
    ]
    _run(
        session,
        "UNWIND $rows AS row MERGE (n:Case {case_id: row.key}) "
        "SET n.date = row.date, n.model = row.model, n.symptom = row.symptom, "
        "n.cause = row.cause, n.action = row.action, n.frequency = row.frequency, "
        "n.build = $build",
        rows,
        build,
    )


def _write_edges(
    session: Session,
    edge_type: str,
    rows: list[dict[str, object]],
    build: str,
) -> None:
    if edge_type not in {
        "IN_DOCUMENT",
        "PARENT",
        "NEXT",
        "BOUND_CAUTION",
        "REFERS_TO",
        "STATES",
        "HAS_STEP",
        "APPLIES_TO",
        "LISTS",
        "CANDIDATE_PART",
        "ABOUT",
        "INSTALLED",
        "ON_MODEL",
        "MENTIONS",
    }:
        raise ValueError(f"unknown edge type {edge_type}")
    grouped: dict[tuple[str, str, str, str], list[dict[str, object]]] = {}
    for row in rows:
        key = (
            str(row["start_label"]),
            str(row["start_prop"]),
            str(row["end_label"]),
            str(row["end_prop"]),
        )
        grouped.setdefault(key, []).append(row)
    for (start_label, start_prop, end_label, end_prop), group in grouped.items():
        _run(
            session,
            "UNWIND $rows AS row "
            f"MATCH (a:{start_label} {{{start_prop}: row.start_key}}) "
            f"MATCH (b:{end_label} {{{end_prop}: row.end_key}}) "
            "MERGE (a)-[r:"
            f"{edge_type} {{build: $build, rule: row.rule, "
            "step_number: row.step_number, keyword: row.keyword}]->(b) "
            "SET r.doc_key = row.doc_key, r.page_start = row.page_start, "
            "r.case_id = row.case_id, r.keyword = row.keyword, "
            "r.step_text = row.step_text, r.description = row.description, "
            "r.derived = row.derived, r.weight = row.weight",
            group,
            build,
        )


def _edge_row(edge: Edge) -> dict[str, object]:
    start_label, start_prop, start_key = _endpoint(edge.start_id)
    end_label, end_prop, end_key = _endpoint(edge.end_id)
    return {
        "start_label": start_label,
        "start_prop": start_prop,
        "start_key": start_key,
        "end_label": end_label,
        "end_prop": end_prop,
        "end_key": end_key,
        "rule": edge.rule,
        "doc_key": edge.doc_key or None,
        "page_start": edge.page_start or None,
        "case_id": edge.case_id or None,
        "keyword": edge.keyword,
        "step_number": edge.step_number,
        "step_text": edge.step_text,
        "description": edge.description,
        "derived": edge.derived,
        "weight": edge.weight,
    }


def _endpoint(graph_id: str) -> tuple[str, str, str]:
    prefix, value = graph_id.split(":", 1)
    if prefix not in _LABELS:
        raise ValueError(f"unknown graph id {graph_id}")
    label, prop = _LABELS[prefix]
    return label, prop, value


def _as_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int | str):
        raise ValueError(f"expected an integer, got {value!r}")
    return int(value)


def _run(session: Session, query: str, rows: Sequence[Mapping[str, Any]], build: str) -> None:
    if not rows:
        return
    session.run(query, rows=rows, build=build).consume()
