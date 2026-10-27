"""Appendix A.4 library. The demonstration app is not imported here."""

import os
from pathlib import Path

from neo4j import Driver

from graphrag_poc.cases.rules import load_rules
from graphrag_poc.graph.build import GraphData
from graphrag_poc.graph.build import build_graph as build_rule_graph
from graphrag_poc.graph.client import make_driver
from graphrag_poc.graph.config import HOP_DEPTH, NODE_CAP, REFERENCE_HOP_DEPTH
from graphrag_poc.graph.export import write_csv
from graphrag_poc.graph.link import link_text, load_term_table
from graphrag_poc.graph.mentions import derive_mentions
from graphrag_poc.graph.report import orphan_nodes
from graphrag_poc.graph.traverse import Seeds as WalkSeeds
from graphrag_poc.graph.traverse import traverse as walk
from graphrag_poc.index.store import Hit
from graphrag_poc.library.models import (
    BuildReport,
    Candidate,
    Entity,
    GraphPath,
    RelationFrame,
    RouterDecision,
    Seed,
    TraversalResult,
)
from graphrag_poc.library.store import write_graph
from graphrag_poc.retrieve.fusion import fuse as fuse_hits
from graphrag_poc.retrieve.graph import edge_types_for, frame_for

CORPUS_BUILD = "corpus"


def build_graph(
    node_files: list[Path],
    case_file: Path | None,
    rules: Path,
    out: str | Path,
    build: str,
) -> BuildReport:
    """Build a graph from node files. `out` is a Bolt URI or a CSV folder."""

    graph = _assemble(node_files, case_file, rules)
    destination = str(out)
    if _is_bolt(out):
        driver = make_driver(uri=str(out))
        try:
            write_graph(driver, graph, build)
        finally:
            driver.close()
    else:
        folder = Path(out)
        write_csv(graph, folder)
        destination = str(folder)
    counts = graph.counts()
    return BuildReport(
        build=build,
        output=destination,
        counts=counts,
        orphans=len(orphan_nodes(graph)),
        derived=counts.get("MENTIONS", 0),
    )


def link_entities(
    entities: list[Entity],
    build: str,
    *,
    driver: Driver | None = None,
) -> list[Seed]:
    """Match entity text to graph nodes. `build` selects which graph to read."""

    active = driver
    owns = driver is None
    if active is None:
        active = make_driver()
    try:
        table = load_term_table(active, build=build)
        seeds: list[Seed] = []
        seen: set[str] = set()
        for entity in entities:
            for link in link_text(entity.text, table):
                if entity.type and link.label.lower() != _entity_label(entity.type):
                    continue
                if link.node_id in seen:
                    continue
                seen.add(link.node_id)
                seeds.append(
                    Seed(
                        node_id=link.node_id,
                        confidence=link.score,
                        matched_form=link.key,
                        label=link.label,
                    )
                )
        return seeds
    finally:
        if owns:
            active.close()


def traverse(
    seeds: list[Seed],
    question_type: str,
    hops: int,
    cap: int = NODE_CAP,
    build: str = CORPUS_BUILD,
    *,
    driver: Driver | None = None,
    question: str = "",
) -> TraversalResult:
    """Walk the allowed edges and return passage ids, scores, and paths."""

    active = driver
    owns = driver is None
    if active is None:
        active = make_driver()
    try:
        classified = _classify(active, seeds, build)
        hits = walk(
            active,
            classified,
            edge_types_for(question_type),
            hops=hops,
            cap=cap,
            question=question or " ".join(seed.matched_form for seed in seeds),
            build=build,
        )
        candidates = [
            Candidate(
                passage_node_id=hit.node_id,
                score=hit.score,
                channels=["graph"],
                via=list(hit.path),
            )
            for hit in hits
        ]
        paths = [
            GraphPath(
                passage_node_id=hit.node_id,
                via=list(hit.path),
                score=hit.score,
                provenance=list(hit.provenance),
            )
            for hit in hits
        ]
        frame = (
            None
            if question_type in {"relational", "multi_hop"}
            else _frame(active, seeds, question, build)
        )
        return TraversalResult(candidates=candidates, paths=paths, frame=frame)
    finally:
        if owns:
            active.close()


def route(question_type: str, seeds: list[Seed]) -> RouterDecision:
    """Enable the graph for relational, multi-hop, troubleshooting, and applicability.

    A lookup stays off unless a seed is a malfunction, a part, or a case.
    """

    linked = [seed for seed in seeds if seed.label in {"Malfunction", "Part", "Case", ""}]
    model_only = bool(seeds) and all(seed.label == "Model" for seed in seeds)
    if question_type in {"relational", "multi_hop", "troubleshooting", "applicability"}:
        depth = REFERENCE_HOP_DEPTH if question_type in {"relational", "multi_hop"} else HOP_DEPTH
        return RouterDecision(enabled=True, hops=depth, reason=question_type)
    if linked and not model_only:
        return RouterDecision(
            enabled=True,
            hops=HOP_DEPTH,
            reason="linked entity has table or case edges",
        )
    return RouterDecision(enabled=False, hops=HOP_DEPTH, reason="simple lookup")


def fuse(
    lists: dict[str, list[Candidate]],
    weights: dict[str, float],
    k: int = 60,
) -> list[Candidate]:
    """Reciprocal rank fusion. A duplicate keeps its best rank and every channel."""

    via: dict[str, list[str]] = {}
    channels: dict[str, list[Hit]] = {}
    for name, candidates in lists.items():
        hits: list[Hit] = []
        for candidate in candidates:
            hits.append(
                Hit(
                    node_id=candidate.passage_node_id,
                    text="",
                    lang="",
                    score=candidate.score,
                )
            )
            current = via.setdefault(candidate.passage_node_id, [])
            for edge_type in candidate.via:
                if edge_type not in current:
                    current.append(edge_type)
        channels[name] = hits
    fused = fuse_hits(channels, k=k, weights=weights)
    return [
        Candidate(
            passage_node_id=hit.node_id,
            score=hit.rrf_score,
            channels=list(hit.channels),
            via=via.get(hit.node_id, []),
        )
        for hit in fused
    ]


def graph_stats(build: str = CORPUS_BUILD, *, driver: Driver | None = None) -> dict[str, object]:
    """Counts, orphan nodes, and the share of derived edges for one build."""

    active = driver
    owns = driver is None
    if active is None:
        active = make_driver()
    try:
        with active.session() as session:
            counts: dict[str, int] = {}
            for record in session.run(
                "MATCH (n) WHERE coalesce(n.build, $corpus) = $build "
                "UNWIND labels(n) AS label RETURN label, count(n) AS c",
                build=build,
                corpus=CORPUS_BUILD,
            ):
                counts[str(record["label"])] = int(record["c"])
            for record in session.run(
                "MATCH ()-[r]->() WHERE coalesce(r.build, $corpus) = $build "
                "RETURN type(r) AS label, count(r) AS c",
                build=build,
                corpus=CORPUS_BUILD,
            ):
                counts[str(record["label"])] = int(record["c"])
            orphans = session.run(
                "MATCH (n) WHERE coalesce(n.build, $corpus) = $build AND NOT (n)--() "
                "RETURN count(n) AS n",
                build=build,
                corpus=CORPUS_BUILD,
            ).single()
            derived = session.run(
                "MATCH ()-[r]->() WHERE coalesce(r.build, $corpus) = $build "
                "RETURN count(r) AS edges, "
                "count(CASE WHEN r.derived = true THEN 1 END) AS derived",
                build=build,
                corpus=CORPUS_BUILD,
            ).single()
    finally:
        if owns:
            active.close()
    edge_total = int(derived["edges"]) if derived is not None else 0
    derived_total = int(derived["derived"]) if derived is not None else 0
    share = derived_total / edge_total if edge_total else 0.0
    return {
        "build": build,
        "counts": counts,
        "orphans": int(orphans["n"]) if orphans is not None else 0,
        "derived": derived_total,
        "derived_share": share,
    }


def _entity_label(kind: str) -> str:
    names = {
        "code": "malfunction",
        "malfunction": "malfunction",
        "part": "part",
        "model": "model",
        "case": "case",
        "passage": "passage",
    }
    return names.get(kind.lower(), kind.lower())


def _assemble(node_files: list[Path], case_file: Path | None, rules_path: Path) -> GraphData:
    rules = load_rules(rules_path)
    nodes = _load_jsonl(node_files)
    cases = _load_jsonl([case_file]) if case_file is not None else []
    graph = build_rule_graph(
        nodes,
        cases,
        documents=_documents(nodes),
        part_keywords=rules.part_keywords,
        min_part_length=rules.min_part_length,
        known_models=set(rules.family_models),
        fault_doc_key=rules.fault_doc_key,
        fault_header=rules.fault_header,
        parts_doc_key=rules.parts_doc_key,
    )
    mentions = derive_mentions(graph)
    graph.edges = sorted(
        [*graph.edges, *mentions],
        key=lambda edge: (
            edge.type,
            edge.start_id,
            edge.end_id,
            edge.keyword,
            edge.step_number,
            edge.step_text,
        ),
    )
    return graph


def _classify(driver: Driver, seeds: list[Seed], build: str | None = None) -> WalkSeeds:
    passages: list[str] = []
    malfunctions: list[str] = []
    parts: list[str] = []
    models: list[str] = []
    cases: list[str] = []
    with driver.session() as session:
        for seed in seeds:
            label = seed.label or _label_of(session, seed.node_id, build)
            if label == "Passage":
                passages.append(seed.node_id)
            elif label == "Malfunction":
                malfunctions.append(seed.node_id)
            elif label == "Part":
                parts.append(seed.node_id)
            elif label == "Model":
                models.append(seed.node_id)
            elif label == "Case":
                cases.append(seed.node_id)
    return WalkSeeds(
        passages=tuple(passages),
        malfunctions=tuple(malfunctions),
        parts=tuple(parts),
        models=tuple(models),
        cases=tuple(cases),
    )


def _label_of(session: object, node_id: str, build: str | None = None) -> str:
    record = session.run(  # type: ignore[attr-defined]
        "OPTIONAL MATCH (p:Passage {node_id: $id}) "
        "WHERE $build IS NULL OR coalesce(p.build, 'corpus') = $build "
        "OPTIONAL MATCH (m:Malfunction {node_id: $id}) "
        "WHERE $build IS NULL OR coalesce(m.build, 'corpus') = $build "
        "OPTIONAL MATCH (part:Part {part_number: $id}) "
        "WHERE $build IS NULL OR coalesce(part.build, 'corpus') = $build "
        "OPTIONAL MATCH (part_row:Part {node_id: $id}) "
        "WHERE $build IS NULL OR coalesce(part_row.build, 'corpus') = $build "
        "OPTIONAL MATCH (model:Model {name: $id}) "
        "WHERE $build IS NULL OR coalesce(model.build, 'corpus') = $build "
        "OPTIONAL MATCH (c:Case {case_id: $id}) "
        "WHERE $build IS NULL OR coalesce(c.build, 'corpus') = $build "
        "RETURN p IS NOT NULL AS passage, m IS NOT NULL AS malfunction, "
        "part IS NOT NULL OR part_row IS NOT NULL AS part, "
        "model IS NOT NULL AS model, c IS NOT NULL AS case_node",
        id=node_id,
        build=build,
    ).single()
    if record is None:
        return ""
    if record["malfunction"]:
        return "Malfunction"
    if record["part"]:
        return "Part"
    if record["model"]:
        return "Model"
    if record["case_node"]:
        return "Case"
    if record["passage"]:
        return "Passage"
    return ""


def _frame(
    driver: Driver, seeds: list[Seed], question: str, build: str | None = None
) -> RelationFrame | None:
    for seed in seeds:
        if seed.label not in {"", "Malfunction"}:
            continue
        with driver.session() as session:
            record = session.run(
                "MATCH (m:Malfunction {node_id: $id}) "
                "WHERE $build IS NULL OR coalesce(m.build, 'corpus') = $build "
                "RETURN m.code AS code",
                id=seed.node_id,
                build=build,
            ).single()
        if record is None:
            continue
        raw = frame_for(driver, seed.node_id, str(record["code"]), question, build=build)
        return RelationFrame(
            code=raw.code,
            cause=raw.cause,
            remedy=raw.remedy,
            part=raw.part,
            cases=list(raw.cases),
        )
    return None


def _documents(nodes: list[dict[str, object]]) -> list[dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for node in nodes:
        doc_key = str(node.get("doc_key") or "unknown")
        if doc_key in found:
            continue
        found[doc_key] = {
            "id": f"doc:{doc_key}",
            "doc_key": doc_key,
            "title": doc_key,
            "lang": str(node.get("lang") or "en"),
            "doc_type": str(node.get("doc_type") or "other"),
            "edition": "unspecified",
        }
    return [found[key] for key in sorted(found)]


def _load_jsonl(paths: list[Path]) -> list[dict[str, object]]:
    import json

    rows: list[dict[str, object]] = []
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                rows.append(loaded)
    return rows


def _is_bolt(out: str | Path) -> bool:
    text = os.fspath(out)
    return text.startswith("bolt://") or text.startswith("neo4j://")
