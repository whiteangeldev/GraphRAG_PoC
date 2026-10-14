"""Round-trip the Appendix A node and case contracts."""

import json

import pytest
from pydantic import ValidationError

from graphrag_poc.models import CaseRecord, Node

STEP_NODE = {
    "node_id": "docA:3-2:step4",
    "doc_key": "docA",
    "lang": "en",
    "edition": {"version": "2024-05", "twin_doc_key": None},
    "doc_type": "maintenance",
    "type": "step",
    "breadcrumb": ["Maintenance", "3 Hydraulics", "3-2 Filter replacement", "step 4"],
    "page_start": 88,
    "page_end": 88,
    "elements": [
        {
            "page": 88,
            "bbox": [72, 310, 540, 390],
            "text": "Wait at least 10 seconds before opening the housing.",
        }
    ],
    "text": "Wait at least 10 seconds before opening the housing.",
    "parent": "docA:3-2",
    "siblings": ["docA:3-2:step3", "docA:3-2:step5"],
    "bound_cautions": ["docA:3-2:step4:caution"],
    "references": ["docA:5-1"],
    "applies_to": {"models": ["M10", "M12"], "series": ["M"], "variants": []},
    "retrievable": True,
}

CASE_RECORD = {
    "case_id": "C-000123",
    "date": "2024-03-11",
    "model": "M12",
    "symptom": "Hydraulic pressure drops after startup.",
    "cause": "Filter restriction.",
    "action": "Replace the hydraulic filter.",
    "parts": ["1234567"],
    "error_codes": ["E0220"],
    "frequency": 3,
    "search_text": "M12 E0220 hydraulic pressure drops filter 1234567",
}


def test_node_and_case_round_trip() -> None:
    node = Node.model_validate(STEP_NODE)
    case = CaseRecord.model_validate(CASE_RECORD)

    node_line = node.model_dump_json()
    case_line = case.model_dump_json()
    assert "\n" not in node_line
    assert "\n" not in case_line

    restored_node = Node.model_validate_json(node_line)
    restored_case = CaseRecord.model_validate_json(case_line)
    assert restored_node == node
    assert restored_case == case

    node_json = json.loads(node_line)
    case_json = json.loads(case_line)
    assert node_json["node_id"] == "docA:3-2:step4"
    assert node_json["doc_type"] == "maintenance"
    assert node_json["type"] == "step"
    assert node_json["table"] is None
    assert node_json["edition"] == {"version": "2024-05", "twin_doc_key": None}
    assert node_json["elements"][0]["bbox"] == [72.0, 310.0, 540.0, 390.0]
    assert case_json["case_id"] == "C-000123"
    assert case_json["date"] == "2024-03-11"
    assert case_json["parts"] == ["1234567"]
    assert case_json["error_codes"] == ["E0220"]
    assert case_json["frequency"] == 3


def test_extra_fields_survive_round_trip() -> None:
    node = Node.model_validate({**STEP_NODE, "source_span": "p4"})
    case = CaseRecord.model_validate({**CASE_RECORD, "site": "field"})

    restored_node = Node.model_validate_json(node.model_dump_json())
    restored_case = CaseRecord.model_validate_json(case.model_dump_json())
    assert restored_node.model_extra == {"source_span": "p4"}
    assert restored_case.model_extra == {"site": "field"}


def test_table_row_round_trip() -> None:
    payload = {
        **STEP_NODE,
        "node_id": "docA:7-3:r12",
        "type": "table_row",
        "text": "E0220 Overpressure Clogged filter Replace the filter",
        "table": {
            "headers": ["Code", "Meaning", "Cause", "Remedy"],
            "cells": ["E0220", "Overpressure", "Clogged filter", "Replace the filter"],
        },
    }
    row = Node.model_validate(payload)
    restored = Node.model_validate_json(row.model_dump_json())
    assert restored == row
    assert restored.table is not None
    assert restored.table.cells[0] == "E0220"


def test_table_is_rejected_unless_node_is_a_table_row() -> None:
    with pytest.raises(ValidationError):
        Node.model_validate(
            {
                **STEP_NODE,
                "table": {
                    "headers": ["Code", "Meaning"],
                    "cells": ["E0220", "Overpressure"],
                },
            }
        )


def test_table_row_requires_table() -> None:
    with pytest.raises(ValidationError):
        Node.model_validate({**STEP_NODE, "type": "table_row"})


def test_page_range_must_cover_elements() -> None:
    with pytest.raises(ValidationError):
        Node.model_validate({**STEP_NODE, "page_end": 87})
