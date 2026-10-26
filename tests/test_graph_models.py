"""Round-trip a passage node and a NEXT edge through Neo4j."""

import uuid

import pytest
from pydantic import ValidationError

from graphrag_poc.graph.client import make_driver
from graphrag_poc.models.graph import (
    EdgeType,
    GraphEdge,
    PassageNode,
    Provenance,
)

PASSAGE = {
    "node_id": "tm280_20_2:3-8:step-1",
    "text": "1. Disconnect two engine oil cooler supply and return lines.",
    "type": "step",
    "page_start": 32,
    "page_end": 32,
    "lang": "en",
    "breadcrumb": ["Unit maintenance", "3-8 Oil cooler", "step 1"],
}

NEXT_PASSAGE = {
    **PASSAGE,
    "node_id": "tm280_20_2:3-8:step-3",
    "text": "3. Connect two engine oil cooler supply and return lines.",
    "breadcrumb": ["Unit maintenance", "3-8 Oil cooler", "step 3"],
}


def test_passage_and_next_edge_round_trip_as_json() -> None:
    start = PassageNode.model_validate(PASSAGE)
    end = PassageNode.model_validate(NEXT_PASSAGE)
    edge = GraphEdge.model_validate(
        {
            "type": "NEXT",
            "start_id": start.node_id,
            "end_id": end.node_id,
            "provenance": {
                "rule": "numbered steps that share a task prefix",
                "doc_key": "tm280_20_2",
                "page_start": 32,
            },
        }
    )
    restored_start = PassageNode.model_validate_json(start.model_dump_json())
    restored_edge = GraphEdge.model_validate_json(edge.model_dump_json())
    assert restored_start == start
    assert restored_edge == edge
    assert restored_edge.type is EdgeType.NEXT
    assert restored_edge.provenance.derived is False
    assert end.node_id == restored_edge.end_id


def test_provenance_needs_a_page_or_a_case() -> None:
    with pytest.raises(ValidationError):
        Provenance.model_validate({"rule": "parent"})
    with pytest.raises(ValidationError):
        Provenance.model_validate(
            {"rule": "both", "doc_key": "tm280_10", "page_start": 1, "case_id": "C-000001"}
        )


def test_mentions_must_be_derived_with_a_lower_weight() -> None:
    with pytest.raises(ValidationError):
        GraphEdge.model_validate(
            {
                "type": "MENTIONS",
                "start_id": "tm280_10:1-12",
                "end_id": "M998",
                "provenance": {
                    "rule": "model token in prose",
                    "doc_key": "tm280_10",
                    "page_start": 12,
                },
            }
        )
    edge = GraphEdge.model_validate(
        {
            "type": "MENTIONS",
            "start_id": "tm280_10:1-12",
            "end_id": "M998",
            "provenance": {
                "rule": "model token in prose",
                "derived": True,
                "weight": 0.4,
                "doc_key": "tm280_10",
                "page_start": 12,
            },
        }
    )
    assert edge.provenance.derived is True
    assert edge.provenance.weight == 0.4


def _neo4j_ready() -> bool:
    driver = None
    try:
        driver = make_driver()
        driver.verify_connectivity()
        return True
    except Exception:
        return False
    finally:
        if driver is not None:
            driver.close()


@pytest.mark.skipif(not _neo4j_ready(), reason="Neo4j is not running on localhost:7687")
def test_passage_and_next_edge_round_trip_in_neo4j() -> None:
    prefix = f"m3step1-{uuid.uuid4().hex[:8]}"
    start = PassageNode.model_validate({**PASSAGE, "node_id": f"{prefix}:step-1"})
    end = PassageNode.model_validate({**NEXT_PASSAGE, "node_id": f"{prefix}:step-3"})
    edge = GraphEdge(
        type=EdgeType.NEXT,
        start_id=start.node_id,
        end_id=end.node_id,
        provenance=Provenance(
            rule="numbered steps that share a task prefix",
            doc_key="tm280_20_2",
            page_start=32,
        ),
    )
    driver = make_driver()
    try:
        with driver.session() as session:
            session.run(
                """
                MERGE (a:Passage {node_id: $start_id})
                SET a.text = $start_text, a.type = $start_type,
                    a.page_start = $page, a.page_end = $page, a.lang = $lang,
                    a.breadcrumb = $start_breadcrumb
                MERGE (b:Passage {node_id: $end_id})
                SET b.text = $end_text, b.type = $end_type,
                    b.page_start = $page, b.page_end = $page, b.lang = $lang,
                    b.breadcrumb = $end_breadcrumb
                MERGE (a)-[r:NEXT {rule: $rule}]->(b)
                SET r.doc_key = $doc_key, r.page_start = $page, r.derived = $derived,
                    r.weight = $weight, r.case_id = $case_id
                """,
                start_id=start.node_id,
                start_text=start.text,
                start_type=start.type,
                start_breadcrumb=start.breadcrumb,
                end_id=end.node_id,
                end_text=end.text,
                end_type=end.type,
                end_breadcrumb=end.breadcrumb,
                page=start.page_start,
                lang=start.lang,
                rule=edge.provenance.rule,
                doc_key=edge.provenance.doc_key,
                derived=edge.provenance.derived,
                weight=edge.provenance.weight,
                case_id=edge.provenance.case_id,
            ).consume()
            record = session.run(
                """
                MATCH (a:Passage {node_id: $start_id})-[r:NEXT]->(b:Passage {node_id: $end_id})
                RETURN a.node_id AS start_id, a.text AS start_text, a.page_start AS page,
                       a.breadcrumb AS start_breadcrumb,
                       b.node_id AS end_id, b.text AS end_text,
                       r.rule AS rule, r.doc_key AS doc_key, r.page_start AS edge_page,
                       r.derived AS derived
                """,
                start_id=start.node_id,
                end_id=end.node_id,
            ).single()
        assert record is not None
        restored_start = PassageNode.model_validate(
            {
                "node_id": record["start_id"],
                "text": record["start_text"],
                "type": "step",
                "page_start": record["page"],
                "page_end": record["page"],
                "lang": "en",
                "breadcrumb": record["start_breadcrumb"],
            }
        )
        restored_edge = GraphEdge.model_validate(
            {
                "type": "NEXT",
                "start_id": record["start_id"],
                "end_id": record["end_id"],
                "provenance": {
                    "rule": record["rule"],
                    "doc_key": record["doc_key"],
                    "page_start": record["edge_page"],
                    "derived": record["derived"],
                },
            }
        )
        assert restored_start.text == start.text
        assert restored_edge.end_id == end.node_id
        assert record["end_text"] == end.text
        assert restored_edge.provenance.doc_key == "tm280_20_2"
        assert restored_edge.provenance.page_start == 32
    finally:
        with driver.session() as session:
            session.run(
                "MATCH (n:Passage) WHERE n.node_id STARTS WITH $prefix DETACH DELETE n",
                prefix=prefix,
            ).consume()
        driver.close()
