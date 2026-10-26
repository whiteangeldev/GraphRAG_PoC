"""Rule edges stay deterministic, and each edge cites a page or a case."""

import csv
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from graphrag_poc.graph.build import Edge, GraphData, build_from_disk, build_graph
from graphrag_poc.graph.client import make_driver
from graphrag_poc.graph.load import OIL_COOLER_CAUTIONS, OIL_COOLER_NEXT, OIL_COOLER_STEP
from graphrag_poc.models.graph import Provenance

_PROVENANCE = TypeAdapter(Provenance)

STEP = "s1"
DOCS = [
    {
        "id": "doc:tm280_10",
        "doc_key": "tm280_10",
        "title": "Operator",
        "lang": "en",
        "doc_type": "operation",
        "edition": "c2",
    },
    {
        "id": "doc:tm280_24p_1",
        "doc_key": "tm280_24p_1",
        "title": "Parts",
        "lang": "en",
        "doc_type": "parts",
        "edition": "c2",
    },
    {
        "id": "doc:tm280_20_2",
        "doc_key": "tm280_20_2",
        "title": "Maintenance",
        "lang": "en",
        "doc_type": "maintenance",
        "edition": "c2",
    },
]


def _step(node_id: str, text: str, siblings: list[str]) -> dict[str, object]:
    return {
        "node_id": node_id,
        "doc_key": "tm280_20_2",
        "retrievable": True,
        "type": "step",
        "text": text,
        "page_start": 32,
        "page_end": 32,
        "lang": "en",
        "breadcrumb": ["3-8"],
        "parent": "task",
        "siblings": siblings,
        "bound_cautions": [],
        "references": [],
        "applies_to": {"models": [], "series": ["M998"]},
    }


def _fixture() -> list[dict[str, object]]:
    caution = {
        "node_id": "caution",
        "doc_key": "tm280_20_2",
        "retrievable": True,
        "type": "caution",
        "text": "Do not drain oil when engine is hot",
        "page_start": 32,
        "page_end": 32,
        "lang": "en",
        "breadcrumb": [],
        "parent": STEP,
        "siblings": [],
        "bound_cautions": [],
        "references": [],
        "applies_to": {"models": [], "series": []},
    }
    first = _step(STEP, "1. Disconnect the oil cooler.", ["s2"])
    first["bound_cautions"] = ["caution"]
    return [
        first,
        _step("s2", "2. Loosen the clamps.", ["s1", "s3"]),
        _step("s3", "3. Remove the cooler.", ["s2", "i1"]),
        _step("i1", "1. Install the cooler.", ["s3", "i2"]),
        _step("i2", "2. Connect the lines.", ["i1"]),
        caution,
        {
            "node_id": "tm280_10:table:3-1:r1",
            "doc_key": "tm280_10",
            "retrievable": True,
            "type": "table_row",
            "text": "1. ENGINE FAILS TO CRANK Step 1. Check starter. Step 2. Check battery.",
            "page_start": 281,
            "page_end": 281,
            "lang": "en",
            "breadcrumb": [],
            "parent": "",
            "siblings": [],
            "bound_cautions": [],
            "references": [],
            "applies_to": {"models": ["M998"], "series": ["M998"]},
            "table": {"headers": ["MALFUNCTION"], "cells": ["1. ENGINE FAILS TO CRANK"]},
        },
        {
            "node_id": "tm280_10:note",
            "doc_key": "tm280_10",
            "retrievable": True,
            "type": "paragraph",
            "text": "Ignore token M12345.",
            "page_start": 1,
            "page_end": 1,
            "lang": "en",
            "breadcrumb": [],
            "parent": "",
            "siblings": [],
            "bound_cautions": [],
            "references": [],
            "applies_to": {"models": [], "series": []},
        },
        {
            "node_id": "tm280_24p_1:parts:r2",
            "doc_key": "tm280_24p_1",
            "retrievable": True,
            "type": "table_row",
            "text": "later row",
            "page_start": 11,
            "page_end": 11,
            "lang": "en",
            "breadcrumb": [],
            "table": {
                "headers": ["ITEM NO", "SMR", "NSN", "CAGE", "PART NUMBER", "DESCRIPTION"],
                "cells": ["2", "", "999", "19207", "5705628", "OTHER STARTER"],
            },
        },
        {
            "node_id": "tm280_24p_1:parts:r1",
            "doc_key": "tm280_24p_1",
            "retrievable": True,
            "type": "table_row",
            "text": "first row",
            "page_start": 10,
            "page_end": 10,
            "lang": "en",
            "breadcrumb": [],
            "table": {
                "headers": ["ITEM NO", "SMR", "NSN", "CAGE", "PART NUMBER", "DESCRIPTION"],
                "cells": ["1", "", "111", "19207", "5705628", "STARTER MOTOR"],
            },
        },
        {
            "node_id": "tm280_24p_1:parts:r3",
            "doc_key": "tm280_24p_1",
            "retrievable": True,
            "type": "table_row",
            "text": "injector",
            "page_start": 12,
            "page_end": 12,
            "lang": "en",
            "breadcrumb": [],
            "table": {
                "headers": ["ITEM NO", "SMR", "NSN", "CAGE", "PART NUMBER", "DESCRIPTION"],
                "cells": ["3", "", "222", "19207", "9999999", "INJECTOR PUMP"],
            },
        },
    ]


def _graph() -> GraphData:
    cases = [
        {
            "case_id": "C-000001",
            "date": "2020-01-01",
            "model": "M998",
            "symptom": "no crank",
            "cause": "starter",
            "action": "replace",
            "frequency": 2,
            "error_codes": ["1. ENGINE FAILS TO CRANK"],
            "parts": ["5705628"],
        }
    ]
    return build_graph(
        _fixture(),
        cases,
        documents=DOCS,
        part_keywords={"1": ["STARTER", "INJECT"]},
        min_part_length=5,
        known_models={"M998"},
        fault_doc_key="tm280_10",
        fault_header="MALFUNCTION",
        parts_doc_key="tm280_24p_1",
    )


def test_restarted_step_numbers_follow_the_sibling_list() -> None:
    graph = _graph()
    again = _graph()
    assert graph.fingerprint() == again.fingerprint()
    pairs = {(edge.start_id, edge.end_id) for edge in graph.edges if edge.type == "NEXT"}
    assert pairs == {
        ("passage:s1", "passage:s2"),
        ("passage:s2", "passage:s3"),
        ("passage:s3", "passage:i1"),
        ("passage:i1", "passage:i2"),
    }
    cautions = [edge.end_id for edge in graph.edges if edge.type == "BOUND_CAUTION"]
    assert cautions == ["passage:caution"]
    steps = [edge.step_number for edge in graph.edges if edge.type == "HAS_STEP"]
    assert steps == [1, 2]
    keywords = {edge.keyword for edge in graph.edges if edge.type == "CANDIDATE_PART"}
    assert keywords == {"STARTER"}
    assert graph.parts[0]["description"] == "STARTER MOTOR"
    assert [edge.end_id for edge in graph.edges if edge.type == "LISTS"] == [
        "passage:tm280_24p_1:parts:r1",
        "passage:tm280_24p_1:parts:r2",
        "passage:tm280_24p_1:parts:r3",
    ]
    assert [row["name"] for row in graph.models] == ["M998"]
    assert "MENTIONS" not in graph.counts()


def test_every_fixture_edge_has_a_page_or_a_case() -> None:
    for edge in _graph().edges:
        _check_provenance(edge)


def test_corpus_graph_is_deterministic_and_links_the_oil_cooler() -> None:
    first = build_from_disk()
    second = build_from_disk()
    assert first.fingerprint() == second.fingerprint()
    assert first.counts() == second.counts()
    assert "MENTIONS" not in first.counts()
    for edge in first.edges:
        _check_provenance(edge)
    start = f"passage:{OIL_COOLER_STEP}"
    nxt = [edge.end_id for edge in first.edges if edge.type == "NEXT" and edge.start_id == start]
    cautions = [
        edge.end_id
        for edge in first.edges
        if edge.type == "BOUND_CAUTION" and edge.start_id == start
    ]
    assert nxt == [f"passage:{OIL_COOLER_NEXT}"]
    assert cautions == [f"passage:{item}" for item in OIL_COOLER_CAUTIONS]
    charging = next(row["id"] for row in first.malfunctions if str(row["code"]).startswith("4. "))
    candidates = [
        edge for edge in first.edges if edge.type == "CANDIDATE_PART" and edge.start_id == charging
    ]
    assert candidates
    assert {edge.keyword for edge in candidates} <= {"ALTERNATOR", "GENERATOR"}
    assert all(edge.keyword.upper() in edge.description.upper() for edge in candidates)


def test_relationship_files_keep_integer_columns_filled(tmp_path: Path) -> None:
    from graphrag_poc.graph.export import write_csv

    write_csv(_graph(), tmp_path)
    page = _rows(tmp_path / "page_edges.csv")
    case = _rows(tmp_path / "case_edges.csv")
    assert "page_start:int" in page[0]
    assert "page_start" not in case[0]
    assert "step_number:int" not in page[0]
    page_index = page[0].index("page_start:int")
    assert all(row[page_index].isdigit() and int(row[page_index]) >= 1 for row in page[1:])
    case_index = case[0].index("case_id")
    assert all(row[case_index] for row in case[1:])
    assert not (tmp_path / "relationships.csv").exists()


def _rows(path: Path) -> list[list[str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.reader(handle))


def _check_provenance(edge: Edge) -> None:
    _PROVENANCE.validate_python(
        {
            "rule": edge.rule,
            "doc_key": edge.doc_key or None,
            "page_start": edge.page_start or None,
            "case_id": edge.case_id or None,
            "derived": False,
            "weight": 1.0,
        }
    )


def _oil_cooler_loaded() -> bool:
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


@pytest.mark.skipif(not _oil_cooler_loaded(), reason="rule graph is not imported")
def test_imported_oil_cooler_and_candidate_part() -> None:
    from graphrag_poc.graph.load import spot_check

    found = spot_check()
    assert OIL_COOLER_NEXT in found["next"]
    assert found["cautions"] == list(OIL_COOLER_CAUTIONS)
    assert found["candidate_part"]
    assert str(found["candidate_code"]).startswith("4.")
    assert found["candidate_keyword"] in {"ALTERNATOR", "GENERATOR"}
    assert found["edges_without_provenance"] == 0
