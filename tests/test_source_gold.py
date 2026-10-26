"""A keyword coincidence cannot silently become M3 acceptance evidence."""

import json
from pathlib import Path

import pytest

from graphrag_poc.eval.check import load_questions
from graphrag_poc.eval.gold import (
    SourceRelation,
    acceptance_errors,
    load_nodes,
    load_relations,
    questions_digest,
    validate_relations,
)
from graphrag_poc.models import Node


@pytest.fixture(scope="module")
def nodes() -> dict[str, Node]:
    return load_nodes()


def test_selected_links_match_source_spans_and_typed_fields(nodes: dict[str, Node]) -> None:
    relations = load_relations()
    assert len(relations) == 10
    assert validate_relations(relations, nodes) == []
    assert all(not row.m3_target_eligible for row in relations)
    assert all(row.review_status == "source_checked_pending_client" for row in relations)
    assert any("conflicts" in note for row in relations for note in row.limitations)


@pytest.mark.parametrize("field", ["quote", "text_sha256", "page", "doc_key"])
def test_changed_or_incorrect_evidence_is_rejected(nodes: dict[str, Node], field: str) -> None:
    relation = load_relations()[0]
    values: dict[str, object] = {
        "quote": "An invented repair instruction",
        "text_sha256": "wrong-hash",
        "page": 9999,
        "doc_key": "another_manual",
    }
    changed = relation.source.model_copy(update={field: values[field]})
    assert validate_relations([relation.model_copy(update={"source": changed})], nodes)


def test_matching_cage_or_partial_number_is_not_a_part_link(nodes: dict[str, Node]) -> None:
    relation = load_relations()[0]
    for reference in ("61928", "251-59"):
        changed = relation.model_copy(update={"reference": reference})
        errors = validate_relations([changed], nodes)
        assert any("complete part number" in error for error in errors)
        assert any("PART NUMBER does not match" in error for error in errors)


def test_paragraph_reference_cannot_jump_to_another_manual(nodes: dict[str, Node]) -> None:
    relation = next(row for row in load_relations() if row.kind == "explicit_paragraph_reference")
    changed = relation.target.model_copy(update={"node_id": "tm280_20_2:3-28"})
    errors = validate_relations([relation.model_copy(update={"target": changed})], nodes)
    assert any("another paragraph/document" in error for error in errors)


def test_all_legacy_target_questions_are_explicitly_exploratory() -> None:
    targets = [
        row
        for row in load_questions()
        if row["slice"]["question_type"] in {"relational", "multi_hop"}
    ]
    assert len(targets) == 50
    assert all(row["evaluation"]["m3_target_eligible"] is False for row in targets)
    assert all(row["evaluation"]["benchmark_slice"] == "keyword_exploratory" for row in targets)


def test_scope_approval_does_not_approve_keyword_gold(tmp_path: Path) -> None:
    records = load_questions()
    ids = [
        row["id"] for row in records if row["slice"]["question_type"] in {"relational", "multi_hop"}
    ]
    path = tmp_path / "agreement.json"
    path.write_text(
        json.dumps(
            {
                "status": "approved",
                "approved_by": "test reviewer",
                "approved_at": "2026-10-26",
                "approved_scope": "test scope",
                "question_ids": ids,
                "questions_sha256": questions_digest(records),
            }
        )
    )
    errors = acceptance_errors(records, path)
    assert any("exploratory/unreviewed" in error for error in errors)
    records[0]["question"] = "A changed question"
    assert any("frozen agreement" in error for error in acceptance_errors(records, path))


def test_m3_stops_before_model_calls_for_pending_gold() -> None:
    from graphrag_poc.eval.m3 import run_graph

    with pytest.raises(RuntimeError, match="pending client agreement"):
        run_graph()


def test_partial_links_cannot_be_marked_eligible_by_a_flag() -> None:
    payload = load_relations()[0].model_dump()
    payload["m3_target_eligible"] = True
    with pytest.raises(ValueError):
        SourceRelation.model_validate(payload)
