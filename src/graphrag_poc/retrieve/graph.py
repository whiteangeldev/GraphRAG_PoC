"""Router, graph traversal, fusion, and the relation frame."""

from dataclasses import dataclass

from neo4j import Driver
from qdrant_client import QdrantClient

from graphrag_poc.graph.client import make_driver
from graphrag_poc.graph.config import GRAPH_WEIGHT, HOP_DEPTH, REFERENCE_HOP_DEPTH
from graphrag_poc.graph.link import Link, TermTable, link_text, load_term_table
from graphrag_poc.graph.traverse import Seeds, traverse
from graphrag_poc.index.embed import Embedder
from graphrag_poc.index.store import Hit, search_passages, search_passages_dense
from graphrag_poc.retrieve.fusion import RRF_K, FusedHit, fuse

_GRAPH_TYPES = frozenset({"relational", "multi_hop", "troubleshooting", "applicability"})
_ADD_PASSAGES = frozenset({"relational", "multi_hop"})
_FRAME_TYPES = frozenset({"lookup", "troubleshooting"})
_TABLE: TermTable | None = None
_DRIVER: Driver | None = None
_DRIVER_CHECKED = False


@dataclass(frozen=True)
class Decision:
    """Whether this question uses the graph channel."""

    use_graph: bool
    reason: str
    edge_types: tuple[str, ...]
    hops: int


@dataclass(frozen=True)
class RelationFrame:
    """Code, cause, remedy, part, and cases for the generator."""

    code: str = ""
    cause: str = ""
    remedy: str = ""
    part: str = ""
    part_number: str = ""
    part_node_id: str = ""
    cases: tuple[str, ...] = ()

    def text(self) -> str:
        rows: list[str] = []
        if self.code:
            rows.append(f"code: {self.code}")
        if self.cause:
            rows.append(f"cause: {self.cause}")
        if self.remedy:
            rows.append(f"remedy: {self.remedy}")
        if self.part:
            rows.append(f"part: {self.part}")
        if self.cases:
            rows.append("cases: " + ", ".join(self.cases))
        return "\n".join(rows)


def route(question_type: str, links: list[Link]) -> Decision:
    """Turn the graph on for relational, multi-hop, troubleshooting, and applicability.

    A lookup stays off unless an entity links to a malfunction, part, or case.
    """

    linked = any(link.has_table_or_case for link in links)
    if question_type in _GRAPH_TYPES:
        use_graph = True
        reason = question_type
    elif linked:
        use_graph = True
        reason = "linked entity has table or case edges"
    else:
        use_graph = False
        reason = "simple lookup"
    depth = REFERENCE_HOP_DEPTH if question_type in _ADD_PASSAGES else HOP_DEPTH
    return Decision(use_graph, reason, edge_types_for(question_type), depth)


def infer_question_type(question: str, links: list[Link]) -> str:
    """A type for a question that did not come from the evaluation set."""

    lowered = question.lower()
    if any(
        term in lowered for term in ("catalogue", "catalog", "parts list", "part number", "nsn")
    ):
        return "relational"
    if any(term in lowered for term in ("paragraph", "referenced", "follow-on")):
        return "multi_hop"
    has_fault = any(link.label == "Malfunction" for link in links)
    if has_fault and "part" in lowered:
        return "relational"
    if "step" in lowered or "warning" in lowered or "disconnect" in lowered:
        return "procedure"
    if "model" in lowered and any(link.label == "Model" for link in links):
        return "applicability"
    return "lookup"


def retrieve_question(
    client: QdrantClient,
    embedder: Embedder,
    question: str,
    *,
    question_type: str | None = None,
    driver: Driver | None = None,
    table: TermTable | None = None,
    limit: int = 12,
    k: int = RRF_K,
    graph_weight: float = GRAPH_WEIGHT,
) -> tuple[list[FusedHit], Decision, RelationFrame]:
    """Fuse dense and sparse retrieval with the graph channel when the router allows it."""

    dense = search_passages_dense(client, embedder, question, limit=limit)
    sparse = search_passages(client, question, limit=limit)
    baseline = fuse({"dense": dense, "sparse": sparse}, k=k)
    graph = driver if driver is not None else _cached_driver()
    active_table = table if table is not None else (_cached_table(graph) if graph else None)
    if graph is None or active_table is None:
        decision = Decision(False, "simple lookup", (), HOP_DEPTH)
        return baseline, decision, RelationFrame()
    # Source passages seed bounded references directly; no dense entity guessing is
    # needed for these questions, and no reviewed gold IDs enter retrieval.
    bounded = question_type in _ADD_PASSAGES or infer_question_type(question, []) in _ADD_PASSAGES
    links = link_text(question, active_table, embedder=None if bounded else embedder)
    kind = question_type or infer_question_type(question, links)
    decision = route(kind, links)
    fault = next((link for link in links if link.label == "Malfunction"), None)
    frame = _frame(graph, fault, question, "corpus") if kind in _FRAME_TYPES else RelationFrame()
    if not decision.use_graph:
        return baseline, decision, frame
    passage_ids = tuple(
        hit.node_id
        for hit in baseline
        if kind in _ADD_PASSAGES or (kind == "procedure" and hit.type == "step")
    )
    seeds = Seeds(
        passages=passage_ids[: 10 if kind in _ADD_PASSAGES else 5],
        malfunctions=tuple(link.node_id for link in links if link.label == "Malfunction"),
        parts=tuple(link.key for link in links if link.label == "Part"),
        models=tuple(link.key for link in links if link.label == "Model"),
    )
    walked = traverse(
        graph, seeds, decision.edge_types, hops=decision.hops, question=question, build="corpus"
    )
    if kind not in _ADD_PASSAGES:
        order = {hit.node_id: index for index, hit in enumerate(baseline)}
        walked = [hit for hit in walked if hit.node_id in order]
        walked.sort(key=lambda hit: order[hit.node_id])
    if not walked:
        return baseline, decision, frame
    graph_hits = [
        Hit(
            hit.node_id,
            hit.text,
            hit.lang,
            hit.score,
            hit.page_start,
            hit.page_end,
            hit.doc_key,
            hit.type,
        )
        for hit in walked
    ]
    fused = fuse(
        {"dense": dense, "sparse": sparse, "graph": graph_hits},
        k=k,
        weights={"dense": 1.0, "sparse": 1.0, "graph": graph_weight},
    )
    return fused, decision, frame


def edge_types_for(question_type: str) -> tuple[str, ...]:
    """Edge types the router walks for one question type."""

    return _edge_types(question_type)


def frame_for(
    driver: Driver, node_id: str, code: str, question: str = "", *, build: str | None = None
) -> RelationFrame:
    """Relation frame for one malfunction node."""

    return _frame(driver, Link("Malfunction", code, node_id, "exact", 1.0), question, build)


def _edge_types(question_type: str) -> tuple[str, ...]:
    if question_type == "procedure":
        return ("NEXT", "BOUND_CAUTION")
    if question_type in {"relational", "multi_hop"}:
        return ("REFERS_TO", "PARENT", "MENTIONS", "LISTS", "STATES")
    if question_type in {"applicability", "follow_up"}:
        return ("APPLIES_TO",)
    if question_type in {"lookup", "troubleshooting"}:
        return ("ABOUT", "INSTALLED", "CANDIDATE_PART", "LISTS", "STATES")
    return ()


def _frame(
    driver: Driver, fault: Link | None, question: str, build: str | None = None
) -> RelationFrame:
    if fault is None:
        return RelationFrame()
    scope = (
        "WHERE ($build IS NULL OR ("
        "all(v IN nodes(path) WHERE coalesce(v.build, 'corpus') = $build) AND "
        "all(e IN relationships(path) WHERE coalesce(e.build, 'corpus') = $build))) "
    )
    with driver.session() as session:
        source = session.run(
            "MATCH (m:Malfunction {node_id: $id}) "
            "WHERE $build IS NULL OR coalesce(m.build, 'corpus') = $build "
            "RETURN m.node_id AS node_id",
            id=fault.node_id,
            build=build,
        ).single()
        if source is None:
            return RelationFrame()
        steps = session.run(
            "MATCH path=(m:Malfunction {node_id: $id})-[h:HAS_STEP]->() "
            + scope
            + "RETURN h.step_number AS number, h.step_text AS text",
            id=fault.node_id,
            build=build,
        ).data()
        parts = session.run(
            "MATCH path=(m:Malfunction {node_id: $id})-[r:CANDIDATE_PART]->(p:Part) "
            + scope
            + "RETURN p.part_number AS number, p.description AS description, "
            "p.node_id AS node_id, r.keyword AS keyword ORDER BY p.node_id",
            id=fault.node_id,
            build=build,
        ).data()
        cases = session.run(
            "MATCH path=(c:Case)-[:ABOUT]->(m:Malfunction {node_id: $id}) "
            + scope
            + "RETURN c.case_id AS case_id ORDER BY case_id LIMIT 5",
            id=fault.node_id,
            build=build,
        ).data()
    folded = question.lower()
    matched = [row for row in parts if str(row["keyword"]).lower() in folded]
    chosen = (matched or parts)[:1]
    part = chosen[0] if chosen else None
    ordered = sorted(steps, key=lambda row: _step_number(row.get("number")))
    cause = str(ordered[0]["text"]) if ordered else ""
    remedy = str(ordered[1]["text"]) if len(ordered) > 1 else cause
    part_text = ""
    part_number = ""
    part_node = ""
    if part is not None:
        part_number = str(part["number"])
        part_node = str(part["node_id"])
        part_text = f"{part_number} {part['description']}".strip()
    return RelationFrame(
        code=fault.key,
        cause=cause,
        remedy=remedy,
        part=part_text,
        part_number=part_number,
        part_node_id=part_node,
        cases=tuple(str(row["case_id"]) for row in cases),
    )


def _step_number(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return 999


def _cached_driver() -> Driver | None:
    global _DRIVER, _DRIVER_CHECKED
    if _DRIVER_CHECKED:
        return _DRIVER
    _DRIVER_CHECKED = True
    try:
        driver = make_driver()
        driver.verify_connectivity()
    except Exception:
        return None
    _DRIVER = driver
    return driver


def _cached_table(driver: Driver) -> TermTable:
    global _TABLE
    if _TABLE is None:
        _TABLE = load_term_table(driver, build="corpus")
    return _TABLE
