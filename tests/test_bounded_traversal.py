"""Explicit reference/part traversal is bounded and independent of evaluation gold."""

import json
from pathlib import Path
from typing import Any

import pytest

from graphrag_poc.graph.client import make_driver
from graphrag_poc.graph.config import REFERENCE_HOP_DEPTH
from graphrag_poc.graph.link import Term, TermTable
from graphrag_poc.graph.traverse import TraversalHit, _rank
from graphrag_poc.index.store import Hit
from graphrag_poc.library import Seed, build_graph, clear_build
from graphrag_poc.library import traverse as library_traverse
from graphrag_poc.retrieve import graph as retrieval


def test_natural_reference_questions_seed_retrieved_passages_without_dense_entity_guessing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = Hit(
        "manual:source", "See para. 6-12. Fit part AB-12345.", "en", 1, 3, 3, "manual", "step"
    )
    monkeypatch.setattr(retrieval, "search_passages_dense", lambda *a, **k: [source])
    monkeypatch.setattr(retrieval, "search_passages", lambda *a, **k: [source])
    captured: dict[str, Any] = {}

    def walk(*args: Any, **kwargs: Any) -> list[TraversalHit]:
        captured.update(seeds=args[1], types=args[2], **kwargs)
        return [
            TraversalHit(
                "parts:row",
                "AB-12345 NSN 999",
                "en",
                8,
                8,
                "parts",
                "table_row",
                2,
                ("MENTIONS", "LISTS"),
                (),
                0.2,
            )
        ]

    monkeypatch.setattr(retrieval, "traverse", walk)
    monkeypatch.setattr(
        retrieval, "_frame", lambda *a: pytest.fail("bounded route must not use keyword frame")
    )
    table = TermTable((Term("Part", "AB-12345", "AB-12345", "parts:row"),))
    result, decision, frame = retrieval.retrieve_question(
        object(),
        object(),
        "Which catalogue NSN is listed for AB-12345?",  # type: ignore[arg-type]
        driver=object(),
        table=table,  # type: ignore[arg-type]
    )
    assert captured["seeds"].passages == (source.node_id,)
    assert captured["seeds"].parts == ("AB-12345",)
    assert captured["hops"] == REFERENCE_HOP_DEPTH
    assert "CANDIDATE_PART" not in captured["types"]
    assert frame.text() == ""
    assert any("graph" in hit.channels for hit in result)
    assert decision.use_graph


def _node(node_id: str, text: str, kind: str = "paragraph", **extra: object) -> dict[str, object]:
    return {
        "node_id": node_id,
        "doc_key": "boundedfix",
        "lang": "en",
        "type": kind,
        "text": text,
        "page_start": 1,
        "page_end": 1,
        "retrievable": True,
        "breadcrumb": ["Fixture", text],
        "parent": "",
        "siblings": [],
        "references": [],
        "bound_cautions": [],
        **extra,
    }


def test_explicit_reference_instruction_precedes_inferred_catalogue_mentions() -> None:
    instruction = TraversalHit(
        "manual:instruction",
        "Disconnect the power.",
        "en",
        1,
        1,
        "manual",
        "step",
        3,
        ("REFERS_TO", "PARENT", "PARENT"),
        ({"weight": 1.0},),
        1 / 3,
    )
    catalogue = TraversalHit(
        "parts:row",
        "Power part NSN 111",
        "en",
        1,
        1,
        "parts",
        "table_row",
        2,
        ("MENTIONS", "LISTS"),
        ({"weight": 0.4}, {"weight": 1.0}),
        0.2,
    )
    assert sorted([catalogue, instruction], key=lambda h: _rank(h, {"power"}))[0] == instruction


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    nodes = [
        _node("boundedfix:source", "Follow para. 6-12.", "step", references=["boundedfix:6-12"]),
        _node("boundedfix:source-two", "See para. 6-12.", "step", references=["boundedfix:6-12"]),
        _node("boundedfix:6-12", "6-12. Filter Replacement 6-24"),
        _node("boundedfix:6-12:2", "6-12. FILTER REPLACEMENT", "procedure"),
        _node("boundedfix:phase", "a. Installation", "step", parent="boundedfix:6-12:2"),
        _node(
            "boundedfix:instruction",
            "Disconnect power before fitting AB-12345.",
            "caution",
            parent="boundedfix:phase",
        ),
        _node("boundedfix:6-12:3", "6-12. FILTER REPLACEMENT (Cont'd)", "procedure"),
        _node("boundedfix:continued", "Check the connector.", "step", parent="boundedfix:6-12:3"),
        _node(
            "boundedfix:part-a",
            "AB-12345 NSN 111",
            "table_row",
            table={
                "headers": ["ITEM NO", "SMR", "NSN", "CAGE", "PART NUMBER", "DESCRIPTION"],
                "cells": ["1", "", "111", "00000", "AB-12345", "FILTER A"],
            },
        ),
        _node(
            "boundedfix:part-b",
            "AB-12345 NSN 222",
            "table_row",
            table={
                "headers": ["ITEM NO", "SMR", "NSN", "CAGE", "PART NUMBER", "DESCRIPTION"],
                "cells": ["2", "", "222", "00000", "AB-12345", "FILTER B"],
            },
        ),
    ]
    path = tmp_path / "nodes.jsonl"
    path.write_text("".join(json.dumps(n) + "\n" for n in nodes))
    rules = json.loads((Path(__file__).parent / "fixtures/m4/rules.json").read_text())
    rules.update(fault_doc_key="boundedfix", parts_doc_key="boundedfix", part_keywords={})
    config = tmp_path / "rules.json"
    config.write_text(json.dumps(rules))
    return path, config


def _ready() -> bool:
    driver = make_driver()
    try:
        driver.verify_connectivity()
        return True
    except Exception:
        return False
    finally:
        driver.close()


@pytest.mark.skipif(not _ready(), reason="Neo4j is unavailable")
def test_real_reference_and_part_paths_respect_depth_provenance_and_build(tmp_path: Path) -> None:
    from graphrag_poc.graph.traverse import Seeds, traverse

    node_file, rules = _fixture(tmp_path)
    driver = make_driver()
    build = "bounded-traversal-fixture"
    try:
        build_graph([node_file], None, rules, "bolt://localhost:7687", build)
        source = [
            Seed(node_id="boundedfix:source", confidence=1, matched_form="task", label="Passage")
        ]
        result = library_traverse(
            source,
            "multi_hop",
            3,
            build=build,
            driver=driver,
            question="What should I disconnect before fitting the replacement?",
        )
        by_id = {c.passage_node_id: c for c in result.candidates}
        assert result.candidates[0].passage_node_id == "boundedfix:instruction"
        assert "boundedfix:6-12" not in by_id
        assert by_id["boundedfix:instruction"].via == ["REFERS_TO", "PARENT", "PARENT"]
        assert all(len(path.provenance) == len(path.via) for path in result.paths)
        assert "boundedfix:continued" in by_id
        unique = traverse(
            driver,
            Seeds(passages=("boundedfix:source", "boundedfix:source-two")),
            ("REFERS_TO", "PARENT"),
            hops=3,
            cap=3,
            build=build,
        )
        assert len({hit.node_id for hit in unique}) == 3
        shallow = library_traverse(source, "multi_hop", 1, build=build, driver=driver)
        assert {c.passage_node_id for c in shallow.candidates} == {
            "boundedfix:6-12:2",
            "boundedfix:6-12:3",
        }
        assert (
            library_traverse(
                source, "multi_hop", 3, build="another-build", driver=driver
            ).candidates
            == []
        )
        mention = traverse(
            driver, Seeds(passages=("boundedfix:instruction",)), ("MENTIONS", "LISTS"), build=build
        )
        assert {h.node_id for h in mention} == {"boundedfix:part-a", "boundedfix:part-b"}
        assert all(h.hops == 2 and h.path == ("MENTIONS", "LISTS") for h in mention)
        assert all(
            h.provenance[0]["derived"] is True and h.provenance[0]["weight"] == 0.4 for h in mention
        )
        assert all(len(h.provenance) == 2 and h.provenance[1]["derived"] is False for h in mention)
        public_mention = library_traverse(
            [
                Seed(
                    node_id="boundedfix:instruction", confidence=1, matched_form="", label="Passage"
                )
            ],
            "relational",
            2,
            build=build,
            driver=driver,
        )
        assert public_mention.paths[0].provenance[0]["derived"] is True
        assert public_mention.paths[0].provenance[0]["weight"] == 0.4
        parts = traverse(driver, Seeds(parts=("AB-12345",)), ("LISTS",), build=build)
        assert {h.node_id for h in parts} == {"boundedfix:part-a", "boundedfix:part-b"}
        assert (
            len(traverse(driver, Seeds(parts=("AB-12345",)), ("LISTS",), cap=1, build=build)) == 1
        )
    finally:
        clear_build(driver, build)
        driver.close()


@pytest.mark.skipif(not _ready(), reason="Neo4j is unavailable")
def test_reference_relevance_is_applied_before_the_unique_passage_cap(tmp_path: Path) -> None:
    from graphrag_poc.graph.traverse import Seeds, traverse

    node_file, rules = _fixture(tmp_path)
    nodes = [json.loads(line) for line in node_file.read_text().splitlines()]
    instruction = next(node for node in nodes if node["node_id"] == "boundedfix:instruction")
    instruction["text"] += "\nCafé voltage inspection."
    nodes.extend(
        _node(
            f"boundedfix:irrelevant-{i:03d}",
            "Caféteria disconnected powerlessness.",
            "step",
            parent="boundedfix:6-12:2",
        )
        for i in range(220)
    )
    node_file.write_text("".join(json.dumps(node) + "\n" for node in nodes))
    driver = make_driver()
    build = "bounded-traversal-cap-fixture"
    try:
        build_graph([node_file], None, rules, "bolt://localhost:7687", build)
        hits = traverse(
            driver,
            Seeds(passages=("boundedfix:source", "boundedfix:source-two")),
            ("REFERS_TO", "PARENT"),
            hops=3,
            cap=200,
            build=build,
            question="Disconnect POWER before fitting the replacement. Café voltage?",
        )
        assert len(hits) == len({hit.node_id for hit in hits}) == 200
        assert hits[0].node_id == "boundedfix:instruction"
        assert hits[0].hops == len(hits[0].provenance) == 3
    finally:
        clear_build(driver, build)
        driver.close()


@pytest.mark.skipif(not _ready(), reason="Neo4j is unavailable")
def test_legacy_paths_and_frames_reject_cross_build_sources_edges_and_intermediates() -> None:
    from graphrag_poc.graph.traverse import Seeds, traverse
    from graphrag_poc.retrieve.graph import frame_for

    driver = make_driver()
    build = "legacy-scope-fixture"
    foreign = "legacy-scope-foreign-fixture"
    try:
        with driver.session() as session:
            session.run(
                "CREATE (n:Passage {node_id:'scopefix:target',build:$build,text:'Target',"
                "lang:'en',type:'paragraph',doc_key:'scopefix',page_start:1,page_end:1}), "
                "(s:Passage {node_id:'scopefix:source',build:$build}), "
                "(f:Passage {node_id:'scopefix:foreign-source',build:$foreign}), "
                "(m:Malfunction {node_id:'scopefix:fault',code:'1. SCOPE FAULT',build:$build}), "
                "(mf:Malfunction {node_id:'scopefix:foreign-fault',build:$foreign}), "
                "(p:Part {part_number:'SCOPE-ONLY',node_id:'scopefix:target',build:$foreign}), "
                "(model:Model {name:'SCOPEFIX',build:$foreign}), "
                "(c:Case {case_id:'scopefix-case',build:$build}), "
                "(cf:Case {case_id:'scopefix-foreign-case',build:$foreign}), "
                "(cv:Case {case_id:'scopefix-valid-case',build:$build}), "
                "(mv:Malfunction {node_id:'scopefix:valid-fault',build:$build}), "
                "(pv:Part {part_number:'SCOPE-VALID',node_id:'scopefix:target',build:$build}) "
                "CREATE (s)-[:NEXT {build:$foreign}]->(n), "
                "(s)-[:NEXT {build:$build}]->(f), (f)-[:NEXT {build:$build}]->(n), "
                "(mf)-[:STATES {build:$build}]->(n), "
                "(m)-[:STATES {build:$foreign}]->(n), "
                "(n)-[:APPLIES_TO {build:$build}]->(model), "
                "(m)-[:CANDIDATE_PART {build:$build,keyword:'STARTER'}]->(p), "
                "(p)-[:LISTS {build:$build}]->(n), "
                "(c)-[:ABOUT {build:$build}]->(mf), "
                "(cf)-[:ABOUT {build:$build}]->(m), "
                "(c)-[:INSTALLED {build:$build}]->(p), "
                "(m)-[:HAS_STEP {build:$foreign,step_number:1,step_text:'Foreign remedy'}]->(n), "
                "(cv)-[:ABOUT {build:$build,case_id:'scopefix-valid-case',weight:1.0}]->(mv), "
                "(mv)-[:STATES {build:$build,doc_key:'scopefix',page_start:1,weight:1.0}]->(n), "
                "(cv)-[:INSTALLED {build:$build,case_id:'scopefix-valid-case',weight:1.0}]->(pv), "
                "(pv)-[:LISTS {build:$build,doc_key:'scopefix',page_start:1,weight:1.0}]->(n)",
                build=build,
                foreign=foreign,
            ).consume()
        checks = [
            (Seeds(passages=("scopefix:source", "scopefix:foreign-source")), ("NEXT",)),
            (Seeds(malfunctions=("scopefix:fault", "scopefix:foreign-fault")), ("STATES",)),
            (Seeds(malfunctions=("scopefix:fault",)), ("CANDIDATE_PART", "LISTS")),
            (Seeds(models=("SCOPEFIX",)), ("APPLIES_TO",)),
            (
                Seeds(cases=("scopefix-case", "scopefix-foreign-case")),
                ("ABOUT", "STATES", "INSTALLED", "LISTS"),
            ),
        ]
        for seeds, types in checks:
            assert traverse(driver, seeds, types, build=build) == []
        for types in [("ABOUT", "STATES"), ("INSTALLED", "LISTS")]:
            seeds = Seeds(cases=("scopefix-valid-case",))
            hits = traverse(driver, seeds, types, hops=2, build=build)
            assert len(hits) == 1 and hits[0].path == types
            assert len(hits[0].provenance) == 2
            assert hits[0].provenance[0]["case_id"] == "scopefix-valid-case"
            assert hits[0].provenance[1]["doc_key"] == "scopefix"
            assert traverse(driver, seeds, types, hops=1, build=build) == []
            assert traverse(driver, seeds, types[:1], hops=2, build=build) == []
        frame = frame_for(driver, "scopefix:fault", "1. SCOPE FAULT", build=build)
        assert frame.code == "1. SCOPE FAULT"
        assert not frame.cause and not frame.part and not frame.cases
        assert frame_for(driver, "scopefix:foreign-fault", "Foreign code", build=build).text() == ""
        public = library_traverse(
            [
                Seed(
                    node_id="scopefix:foreign-fault",
                    confidence=1,
                    matched_form="",
                    label="Malfunction",
                )
            ],
            "troubleshooting",
            2,
            build=build,
            driver=driver,
        )
        assert not public.candidates and public.frame is None
    finally:
        clear_build(driver, foreign)
        clear_build(driver, build)
        driver.close()
