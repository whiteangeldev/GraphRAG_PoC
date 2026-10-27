"""Bounded gold proposals are source-backed, reproducible, and remain unapproved."""

import hashlib
import json
from pathlib import Path

import pytest

from graphrag_poc.eval.check import load_questions, validate
from graphrag_poc.eval.gold import acceptance_errors, load_nodes, questions_digest
from graphrag_poc.eval.review_package import (
    AUDIT_PATH,
    CANDIDATES_PATH,
    QUESTIONS_PATH,
    REVIEW_PATH,
    ReviewCandidate,
    audit,
    check_pdf_spans,
    evaluation_records,
    load_candidates,
    render_candidates,
    validate_candidates,
)
from graphrag_poc.models import Node


@pytest.fixture(scope="module")
def nodes() -> dict[str, Node]:
    return load_nodes()


def test_candidate_pack_is_valid_and_has_distinct_evidence_cases(nodes: dict[str, Node]) -> None:
    candidates = load_candidates()
    assert len(candidates) == 50
    assert validate_candidates(candidates, nodes) == []
    assert sum(c.scope == "operator_reference_and_instruction" for c in candidates) == 23
    assert sum(c.scope == "maintenance_catalogue_identity" for c in candidates) == 12
    assert sum(c.scope == "maintenance_reference_and_instruction" for c in candidates) == 15
    assert sum(c.review_status == "client_accepted" for c in candidates) == 25
    assert all(
        c.review_status == "source_checked_pending_client" for c in candidates if c.batch == 2
    )
    for candidate in candidates:
        for relation in candidate.relations:
            if relation.kind == "explicit_part_number":
                assert relation.reference not in candidate.question


@pytest.mark.parametrize("field", ["m3_target_eligible", "complete_fault_to_part_chain"])
def test_drafts_cannot_be_promoted_by_a_flag(field: str) -> None:
    payload = load_candidates()[0].model_dump()
    payload[field] = True
    with pytest.raises(ValueError):
        ReviewCandidate.model_validate(payload)


def test_duplicate_evidence_is_not_counted_as_a_new_question(nodes: dict[str, Node]) -> None:
    candidate = load_candidates()[0]
    reworded = candidate.model_copy(update={"id": "review-reworded", "question": "A new wording"})
    errors = validate_candidates([candidate, reworded], nodes)
    assert any("duplicate evidence case" in error for error in errors)


@pytest.mark.parametrize("change", ["hash", "quote", "procedure", "scope"])
def test_stale_or_wrong_procedure_details_are_rejected(nodes: dict[str, Node], change: str) -> None:
    candidate = load_candidates()[0]
    detail = candidate.details[0]
    changes: dict[str, object] = {}
    if change == "hash":
        changes["details"] = [detail.model_copy(update={"text_sha256": "stale"})]
    elif change == "quote":
        changes["details"] = [detail.model_copy(update={"quote": "An invented instruction"})]
    elif change == "procedure":
        wrong = nodes[detail.node_id].model_copy(update={"parent": "tm280_10:3-28"})
        nodes = {**nodes, detail.node_id: wrong}
    else:
        changes["scope"] = "maintenance_catalogue_identity"
    assert validate_candidates([candidate.model_copy(update=changes)], nodes)


def test_saved_pack_and_audit_match_nodes_and_physical_pdf_pages(nodes: dict[str, Node]) -> None:
    candidates = load_candidates()
    assert REVIEW_PATH.read_text(encoding="utf-8") == render_candidates(candidates, nodes)
    expected = audit(candidates, nodes)
    expected.update(check_pdf_spans(candidates))
    saved = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    assert saved == expected
    assert len(saved["span_checks"]) > 65
    assert all(row["normalised_exact_match"] for row in saved["span_checks"])
    assert saved["candidates_sha256"] == hashlib.sha256(CANDIDATES_PATH.read_bytes()).hexdigest()
    assert saved["full_repair_chains_required"] is False
    assert saved["prepared_question_shortfall"] == 0
    assert saved["accepted_question_shortfall"] == 25
    assert saved["benchmark_frozen"] is False
    assert saved["accepted_candidate_questions"] == saved["pending_candidate_questions"] == 25


def test_current_benchmark_and_pending_contract_stay_separate() -> None:
    records = load_questions()
    assert len(records) == 155
    assert not any(str(record["id"]).startswith("review-") for record in records)
    contract_path = Path(__file__).resolve().parents[1] / "data/eval/target_set.json"
    contract = json.loads(contract_path.read_text())
    assert contract["status"] == "pending_client_agreement"
    assert contract["question_ids"] == []
    assert contract["questions_sha256"] == questions_digest(records)
    errors = acceptance_errors([candidate.model_dump() for candidate in load_candidates()])
    assert any("pending client agreement" in error for error in errors)
    assert any("at least 50" in error for error in errors)


def test_hvac_mismatch_is_flagged_and_not_used_as_gold(nodes: dict[str, Node]) -> None:
    candidates = load_candidates()
    saved = json.loads(AUDIT_PATH.read_text())
    conflict = saved["quarantined_references"][0]
    assert conflict["source_quote"] in nodes[conflict["source"]].text
    assert conflict["target_quote"] == nodes[conflict["target"]].text
    assert all(
        (relation.source.node_id, relation.reference) != (conflict["source"], "3-28")
        for candidate in candidates
        for relation in candidate.relations
    )


def test_normal_records_are_source_backed_but_full_acceptance_stays_blocked(
    nodes: dict[str, Node],
) -> None:
    rows = evaluation_records(load_candidates())
    assert rows == load_questions(QUESTIONS_PATH)
    assert validate(rows, {k: n.text for k, n in nodes.items()}, profile="bounded_targets") == []
    errors = acceptance_errors(rows)
    assert any("pending client agreement" in error for error in errors)
    assert sum("exploratory/unreviewed" in error for error in errors) == 25
    assert len({r["id"] for r in rows}) == 50


def test_catalogue_evidence_cannot_be_optional(nodes: dict[str, Node]) -> None:
    candidate = next(c for c in load_candidates() if c.id == "review-water-pump-65")
    assert "NSN" in candidate.question
    source_only = [
        f
        for f in candidate.required_facts
        if f.source_node_id == candidate.relations[0].source.node_id
    ]
    errors = validate_candidates(
        [candidate.model_copy(update={"required_facts": source_only})], nodes
    )
    assert any("exclusive NSN/description" in error for error in errors)


def test_maintenance_reference_rejects_toc_and_wrong_procedure(nodes: dict[str, Node]) -> None:
    from graphrag_poc.eval.gold import Evidence, validate_relations

    candidate = next(
        c for c in load_candidates() if c.scope == "maintenance_reference_and_instruction"
    )
    relation = candidate.relations[0]
    toc = nodes[f"{relation.source.doc_key}:{relation.reference}"]
    assert toc.type != "procedure"
    bad = Evidence(
        node_id=toc.node_id,
        doc_key=toc.doc_key,
        page=toc.page_start,
        quote=toc.text,
        text_sha256=hashlib.sha256(toc.text.encode()).hexdigest(),
    )
    errors = validate_relations([relation.model_copy(update={"target": bad})], nodes)
    assert any("actual procedure" in error for error in errors)
    wrong = relation.model_copy(update={"reference": "99-999"})
    assert any("another paragraph/document" in e for e in validate_relations([wrong], nodes))
