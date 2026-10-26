"""The Appendix A.4 library answers five questions from a fixture graph."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from graphrag_poc.generate.answer import answer_from_passages
from graphrag_poc.graph.client import make_driver
from graphrag_poc.library import (
    Entity,
    Seed,
    build_graph,
    clear_build,
    fuse,
    link_entities,
    route,
    traverse,
)
from graphrag_poc.library.models import Candidate
from graphrag_poc.retrieve.fusion import FusedHit

ROOT = Path(__file__).resolve().parent / "fixtures" / "m4"
NODES = ROOT / "nodes.jsonl"
CASES = ROOT / "cases.jsonl"
RULES = ROOT / "rules.json"
CODE = "1. M4 FIXTURE FAILS TO CRANK"
BUILD = "m4-fixture"
BOLT = os.environ.get("NEO4J_URI", "bolt://localhost:7687")


def test_build_writes_csv_and_counts_mentions(tmp_path: Path) -> None:
    report = build_graph([NODES], CASES, RULES, tmp_path, "m4-csv")
    assert report.counts["Malfunction"] == 1
    assert report.counts["Part"] == 1
    assert report.derived >= 1
    assert report.orphans == 0
    assert (tmp_path / "page_edges.csv").exists()


def test_route_and_fuse_follow_the_contract() -> None:
    assert route("lookup", []).enabled is False
    assert route("relational", []).enabled is True
    seed = Seed(
        node_id="m4fix:fault",
        confidence=1,
        matched_form=CODE,
        label="Malfunction",
    )
    assert route("lookup", [seed]).enabled
    fused = fuse(
        {
            "dense": [
                Candidate(passage_node_id="m4fix:fault", score=1, channels=["dense"], via=[])
            ],
            "graph": [
                Candidate(
                    passage_node_id="m4fix:fault",
                    score=1,
                    channels=["graph"],
                    via=["STATES"],
                )
            ],
        },
        {"dense": 1, "graph": 1},
    )
    assert fused[0].passage_node_id == "m4fix:fault"
    assert fused[0].channels == ["dense", "graph"]
    assert "STATES" in fused[0].via


def _neo4j() -> bool:
    driver = make_driver()
    try:
        driver.verify_connectivity()
        return True
    except Exception:
        return False
    finally:
        driver.close()


@pytest.mark.skipif(not _neo4j(), reason="Neo4j is not running")
def test_fixture_answers_five_questions() -> None:
    driver = make_driver()
    try:
        build_graph([NODES], CASES, RULES, BOLT, BUILD)
        linked = link_entities([Entity(text=CODE, type="code")], BUILD, driver=driver)
        assert linked and linked[0].node_id == "m4fix:fault"
        assert link_entities([Entity(text="99. M4 NOT A CODE")], BUILD, driver=driver) == []
        walked = traverse(
            linked,
            "relational",
            2,
            build=BUILD,
            driver=driver,
            question="Which starter part is listed?",
        )
        assert any(item.passage_node_id == "m4fix:part" for item in walked.candidates)
        assert walked.frame is not None
        assert "M4FIXPART" in walked.frame.part
        procedure = traverse(
            [
                Seed(
                    node_id="m4fix:step-1",
                    confidence=1,
                    matched_form="1. Disconnect",
                    label="Passage",
                )
            ],
            "procedure",
            2,
            build=BUILD,
            driver=driver,
        )
        found = {item.passage_node_id for item in procedure.candidates}
        assert "m4fix:step-2" in found
        assert "m4fix:caution" in found
        hits = [
            FusedHit(
                node_id="m4fix:fault",
                text="1. M4 FIXTURE FAILS TO CRANK Step 1. Check the starter.",
                lang="en",
                page_start=2,
                page_end=2,
                doc_key="m4fix",
                type="table_row",
                channels=("graph",),
                best_rank=1,
                rrf_score=1,
            )
        ]
        answer = answer_from_passages(
            "What is the corrective action for 1. M4 FIXTURE FAILS TO CRANK?",
            hits,
        )
        assert "Check the starter" in answer.text
    finally:
        clear_build(driver, BUILD)
        driver.close()


@pytest.mark.skipif(not _neo4j(), reason="Neo4j is not running")
def test_service_health_build_and_traverse() -> None:
    from graphrag_poc.service.app import app

    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"
        built = client.post(
            "/graph/build",
            json={
                "node_files": [str(NODES)],
                "case_file": str(CASES),
                "rules": str(RULES),
                "build": BUILD,
                "out": BOLT,
            },
        )
        assert built.status_code == 200
        assert built.json()["counts"]["Passage"] >= 5
        linked = client.post(
            "/graph/link",
            json={"entities": [{"text": CODE, "type": "code"}], "build": BUILD},
        )
        assert linked.status_code == 200
        assert linked.json()["seeds"][0]["node_id"] == "m4fix:fault"
        walked = client.post(
            "/graph/traverse",
            json={
                "seeds": linked.json()["seeds"],
                "question_type": "relational",
                "hops": 2,
                "build": BUILD,
                "question": "Which starter part is listed?",
            },
        )
        assert walked.status_code == 200
        ids = [item["passage_node_id"] for item in walked.json()["candidates"]]
        assert "m4fix:part" in ids
        counts = client.get("/graph/stats", params={"build": BUILD})
        assert counts.status_code == 200
        assert counts.json()["orphans"] == 0
    driver = make_driver()
    try:
        clear_build(driver, BUILD)
    finally:
        driver.close()
