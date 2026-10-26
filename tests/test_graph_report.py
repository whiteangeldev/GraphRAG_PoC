"""The build report repeats the database counts and an empty derived sample."""

from pathlib import Path

import pytest

from graphrag_poc.graph.build import Edge, GraphData
from graphrag_poc.graph.client import make_driver
from graphrag_poc.graph.load import OIL_COOLER_STEP
from graphrag_poc.graph.report import (
    BuildSurvey,
    DerivedEdge,
    Orphan,
    counts_in_report,
    orphan_nodes,
    render_report,
    survey_database,
    write_report,
)


def _survey() -> BuildSurvey:
    return BuildSurvey(
        counts={"Document": 1, "Passage": 2, "NEXT": 1},
        orphans=[],
        missing_provenance=0,
        doubled_provenance=0,
        derived_total=0,
        derived_sample=[],
    )


def test_report_lists_counts_and_an_empty_derived_sample(tmp_path: Path) -> None:
    text = write_report(_survey(), tmp_path / "report.md")
    parsed = counts_in_report(text)
    assert parsed["Document"] == 1
    assert parsed["Passage"] == 2
    assert parsed["NEXT"] == 1
    assert parsed["MENTIONS"] == 0
    assert "This build has no orphan nodes." in text
    assert "0 edges have no document page and no case id." in text
    assert "The sample of 100 derived edges is empty." in text


def test_report_lists_orphans_and_a_derived_sample() -> None:
    survey = BuildSurvey(
        counts={"Passage": 1, "MENTIONS": 1},
        orphans=[Orphan("Passage", "tm280_10:orphan")],
        missing_provenance=2,
        doubled_provenance=1,
        derived_total=1,
        derived_sample=[DerivedEdge("MENTIONS", "tm280_10:1", "M998", "model token in prose", 0.4)],
    )
    text = render_report(survey)
    assert "| Passage | tm280_10:orphan |" in text
    assert "2 edges have no document page and no case id." in text
    assert "| MENTIONS | tm280_10:1 | M998 | model token in prose | 0.4 |" in text
    assert "The sample of 100 derived edges is empty." not in text


def test_orphan_nodes_are_the_nodes_no_edge_touches() -> None:
    graph = GraphData(
        documents=[
            {
                "id": "doc:tm",
                "doc_key": "tm",
                "title": "T",
                "lang": "en",
                "doc_type": "operation",
                "edition": "c2",
            }
        ],
        passages=[
            {
                "id": "passage:kept",
                "node_id": "kept",
                "text": "kept",
                "type": "step",
                "page_start": 1,
                "page_end": 1,
                "lang": "en",
                "doc_key": "tm",
                "breadcrumb": ["T"],
            },
            {
                "id": "passage:alone",
                "node_id": "alone",
                "text": "alone",
                "type": "step",
                "page_start": 1,
                "page_end": 1,
                "lang": "en",
                "doc_key": "tm",
                "breadcrumb": ["T"],
            },
        ],
        edges=[Edge("IN_DOCUMENT", "passage:kept", "doc:tm", "doc_key", "tm", 1)],
    )
    assert orphan_nodes(graph) == [("Passage", "alone")]


def _graph_loaded() -> bool:
    driver = make_driver()
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            count = session.run(
                "MATCH (p:Passage {node_id: $step}) RETURN count(p) AS n",
                step=OIL_COOLER_STEP,
            ).single()
    except Exception:
        return False
    finally:
        driver.close()
    return count is not None and count["n"] == 1


@pytest.mark.skipif(not _graph_loaded(), reason="rule graph is not imported")
def test_loaded_report_matches_the_database() -> None:
    survey = survey_database()
    text = render_report(survey)
    parsed = counts_in_report(text)
    for label, count in survey.counts.items():
        assert parsed[label] == count
    assert parsed["MENTIONS"] == survey.counts.get("MENTIONS", 0)
    assert survey.missing_provenance == 0
    assert survey.doubled_provenance == 0
    assert survey.orphans == []
    assert survey.derived_total == survey.counts.get("MENTIONS", 0)
    assert all(edge.type == "MENTIONS" and edge.weight < 1 for edge in survey.derived_sample)
    if survey.derived_total == 0:
        assert "The sample of 100 derived edges is empty." in text
    else:
        assert "The sample lists" in text
