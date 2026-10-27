"""Validate and render a review-only gold proposal without changing the benchmark."""

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from graphrag_poc.eval.check import AUTHOR, validate
from graphrag_poc.eval.gold import (
    Evidence,
    SourceRelation,
    load_nodes,
    questions_digest,
    validate_relations,
)
from graphrag_poc.models import Node

ROOT = Path(__file__).resolve().parents[3]
CANDIDATES_PATH = ROOT / "data/eval/review_candidates.jsonl"
AUDIT_PATH = ROOT / "data/eval/review_audit.json"
REVIEW_PATH = ROOT / "docs/client_review/gold_candidates.md"
BATCH_2_PATH = ROOT / "docs/client_review/additional_25_candidates.md"
CORRECTIONS_PATH = ROOT / "docs/client_review/catalogue_corrections.md"
QUESTIONS_PATH = ROOT / "data/eval/bounded_questions.jsonl"
FEEDBACK_PATH = "docs/client_review/client_feedback_2026_10_27.md"
PDF_FILES = {
    "tm280_10": "TM-9-2320-280-10.pdf",
    "tm280_20_1": "TM-9-2320-280-20-1.pdf",
    "tm280_20_2": "TM-9-2320-280-20-2.pdf",
    "tm280_24p_1": "TM-9-2320-280-24P-1.pdf",
}


class RequiredFact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["step", "caution", "value", "reference"]
    text: str = Field(min_length=1)
    source_node_id: str


class ReviewCandidate(BaseModel):
    """A bounded question for client review, never an approved repair diagnosis."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^review-[a-z0-9-]+$")
    scope: Literal[
        "operator_reference_and_instruction",
        "maintenance_catalogue_identity",
        "maintenance_reference_and_instruction",
    ]
    question_type: Literal["relational", "multi_hop"]
    question: str = Field(min_length=20)
    expected_answer: str = Field(min_length=20)
    relations: list[SourceRelation] = Field(min_length=1)
    details: list[Evidence] = Field(default_factory=list)
    limitations: list[str] = Field(min_length=1)
    required_facts: list[RequiredFact] = Field(default_factory=list)
    review_status: Literal["source_checked_pending_client", "client_accepted"]
    batch: Literal[1, 2] = 1
    m3_target_eligible: Literal[False] = False
    complete_fault_to_part_chain: Literal[False] = False


def load_candidates(path: Path = CANDIDATES_PATH) -> list[ReviewCandidate]:
    return [
        ReviewCandidate.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def evidence_spans(candidate: ReviewCandidate) -> list[Evidence]:
    return [
        evidence
        for relation in candidate.relations
        for evidence in (relation.source, relation.target)
    ] + candidate.details


def _within(node: Node, ancestor: str, nodes: dict[str, Node]) -> bool:
    seen: set[str] = set()
    while node.node_id not in seen:
        if node.node_id == ancestor:
            return True
        seen.add(node.node_id)
        if node.parent is None or node.parent not in nodes:
            return False
        node = nodes[node.parent]
    return False


def validate_candidates(candidates: list[ReviewCandidate], nodes: dict[str, Node]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    signatures: set[tuple[tuple[str, str, str], ...]] = set()
    for candidate in candidates:
        if candidate.id in ids:
            errors.append(f"duplicate candidate {candidate.id}")
        ids.add(candidate.id)
        signature = tuple(
            sorted((r.source.node_id, r.target.node_id, r.reference) for r in candidate.relations)
        )
        if signature in signatures:
            errors.append(f"{candidate.id}: duplicate evidence case, not an independent question")
        signatures.add(signature)
        errors.extend(validate_relations(candidate.relations, nodes))
        reference = candidate.scope != "maintenance_catalogue_identity"
        expected_kind = "explicit_paragraph_reference" if reference else "explicit_part_number"
        if any(relation.kind != expected_kind for relation in candidate.relations):
            errors.append(f"{candidate.id}: relation kind does not match proposed scope")
        if reference and (candidate.question_type != "multi_hop" or not candidate.details):
            errors.append(f"{candidate.id}: reference candidate needs a referenced instruction")
        if not reference and candidate.question_type != "relational":
            errors.append(f"{candidate.id}: parts identity is not a complete multi-hop repair")
        for evidence in candidate.details:
            node = nodes.get(evidence.node_id)
            if node is None:
                errors.append(f"{candidate.id}: missing detail node {evidence.node_id}")
                continue
            if (
                not evidence.quote.strip()
                or evidence.quote not in node.text
                or hashlib.sha256(node.text.encode()).hexdigest() != evidence.text_sha256
                or node.doc_key != evidence.doc_key
                or not node.page_start <= evidence.page <= node.page_end
            ):
                errors.append(f"{candidate.id}: detail span/document/page/hash changed")
            if reference and not any(
                _within(node, relation.target.node_id, nodes) for relation in candidate.relations
            ):
                errors.append(f"{candidate.id}: detail is outside the referenced procedure")
            if not reference and node.node_id not in {
                relation.target.node_id for relation in candidate.relations
            }:
                errors.append(f"{candidate.id}: catalogue detail must belong to its selected row")
        if not candidate.required_facts:
            errors.append(f"{candidate.id}: scored required facts are missing")
        for fact in candidate.required_facts:
            if not any(
                fact.source_node_id == evidence.node_id and fact.text in evidence.quote
                for evidence in evidence_spans(candidate)
            ):
                errors.append(f"{candidate.id}: required fact lacks selected source evidence")
        if not reference:
            for relation in candidate.relations:
                source = nodes.get(relation.source.node_id)
                target = nodes.get(relation.target.node_id)
                table = target.table if target else None
                if source is None or table is None:
                    continue
                values = {
                    cell
                    for header, cell in zip(table.headers, table.cells, strict=True)
                    if header in {"NSN", "DESCRIPTION"} and cell
                }
                if not any(
                    f.source_node_id == relation.target.node_id
                    and f.text not in source.text
                    and any(f.text in value for value in values)
                    for f in candidate.required_facts
                ):
                    errors.append(
                        f"{candidate.id}: catalogue row needs an exclusive NSN/description fact"
                    )
        if any(
            r.source.node_id == "tm280_10:table:3-1:7:r30" and r.reference == "3-28"
            for r in candidate.relations
        ):
            errors.append(f"{candidate.id}: excluded HVAC reference cannot count as gold")
    return errors


def evaluation_records(candidates: list[ReviewCandidate]) -> list[dict[str, object]]:
    """Convert reviewed/proposed cases without replacing the active legacy benchmark."""

    records: list[dict[str, object]] = []
    for candidate in candidates:
        evidence = {e.node_id: e for e in evidence_spans(candidate)}
        accepted = candidate.review_status == "client_accepted"
        records.append(
            {
                "id": candidate.id,
                "slice": {
                    "question_type": candidate.question_type,
                    "vocabulary": "user",
                    "language": "en",
                    "model": None,
                },
                "question": candidate.question,
                "expected_action": "answer",
                "gold": {
                    "node_ids": list(evidence),
                    "doc_keys": [e.doc_key for e in evidence.values()],
                    "pages": [e.page for e in evidence.values()],
                },
                "required_facts": [f.model_dump() for f in candidate.required_facts],
                "forbidden_facts": [],
                "turns": None,
                "notes": (
                    f"written by {AUTHOR}, 27 October 2026; "
                    f"AI-assisted wording; batch {candidate.batch}"
                ),
                "evaluation": {
                    "evidence_basis": "manual_supported",
                    "benchmark_slice": candidate.scope,
                    "m3_target_eligible": accepted,
                    "client_review_status": candidate.review_status,
                    "source_chain_review": FEEDBACK_PATH if accepted else None,
                    "batch": candidate.batch,
                    "complete_fault_to_part_chain": False,
                    "limitations": candidate.limitations,
                },
            }
        )
    return records


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def check_pdf_spans(candidates: list[ReviewCandidate], root: Path = ROOT) -> dict[str, object]:
    """Check every selected quote on its physical PDF page; no OCR or fuzzy matching."""

    import pdfplumber

    spans = {
        (evidence.doc_key, evidence.page, evidence.node_id, evidence.quote)
        for candidate in candidates
        for evidence in evidence_spans(candidate)
    }
    checked: list[dict[str, object]] = []
    hashes: dict[str, str] = {}
    for doc_key in sorted({span[0] for span in spans}):
        path = root / "data/corpus/source" / PDF_FILES[doc_key]
        hashes[doc_key] = hashlib.sha256(path.read_bytes()).hexdigest()
        with pdfplumber.open(path) as pdf:
            page_texts = {
                page: _normalise(pdf.pages[page - 1].extract_text() or "")
                for page in sorted({span[1] for span in spans if span[0] == doc_key})
            }
            for _, page, node_id, quote in sorted(span for span in spans if span[0] == doc_key):
                checked.append(
                    {
                        "node_id": node_id,
                        "doc_key": doc_key,
                        "pdf_page": page,
                        "quote": quote,
                        "normalised_exact_match": _normalise(quote) in page_texts[page],
                    }
                )
    return {"pdf_sha256": hashes, "span_checks": checked}


def audit(candidates: list[ReviewCandidate], nodes: dict[str, Node]) -> dict[str, object]:
    """Bounded text audit, explicitly not proof that the complete PDFs contain no chain."""

    faults = [
        node
        for node in nodes.values()
        if node.doc_key == "tm280_10" and node.table and node.table.headers[0] == "MALFUNCTION"
    ]
    refs = {
        (node.node_id, match)
        for node in faults
        for match in re.findall(r"para\.\s*(\d+-\d+(?:\.\d+)?)", node.text)
    }
    part_numbers = {
        node.table.cells[node.table.headers.index("PART NUMBER")]
        for node in nodes.values()
        if node.doc_key == "tm280_24p_1" and node.table and "PART NUMBER" in node.table.headers
    }
    mentions = [
        (node.node_id, match.group(1))
        for node in nodes.values()
        if node.doc_key in {"tm280_20_2", "tm2815_34"}
        for match in re.finditer(
            r"\b(?:P/N|part number)\s*[:#]?\s*([A-Za-z0-9][A-Za-z0-9/-]*)", node.text, re.I
        )
        if match.group(1) in part_numbers
    ]
    return {
        "status": "choice_b_additional_review_pending",
        "candidate_questions": len(candidates),
        "by_scope": dict(Counter(candidate.scope for candidate in candidates)),
        "by_question_type": dict(Counter(candidate.question_type for candidate in candidates)),
        "distinct_operator_fault_rows": len(
            {
                r.source.node_id
                for c in candidates
                if c.scope == "operator_reference_and_instruction"
                for r in c.relations
            }
        ),
        "distinct_operator_paragraphs": len(
            {
                r.target.node_id
                for c in candidates
                if c.scope == "operator_reference_and_instruction"
                for r in c.relations
            }
        ),
        "distinct_maintenance_instruction_nodes": len(
            {
                r.source.node_id
                for c in candidates
                if c.scope == "maintenance_catalogue_identity"
                for r in c.relations
            }
        ),
        "complete_fault_to_part_chains_in_package": 0,
        "accepted_candidate_questions": sum(
            c.review_status == "client_accepted" for c in candidates
        ),
        "pending_candidate_questions": sum(
            c.review_status != "client_accepted" for c in candidates
        ),
        "benchmark_frozen": False,
        "required_target_questions": 50,
        "full_repair_chains_required": False,
        "prepared_question_shortfall": max(0, 50 - len(candidates)),
        "accepted_question_shortfall": max(
            0, 50 - sum(c.review_status == "client_accepted" for c in candidates)
        ),
        "prepared_questions_sha256": questions_digest(evaluation_records(candidates)),
        "node_inventory_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((ROOT / "data/nodes").glob("*.jsonl"))
        },
        "candidates_sha256": hashlib.sha256(CANDIDATES_PATH.read_bytes()).hexdigest(),
        "text_audit": {
            "operator_fault_rows": len(faults),
            "distinct_fault_paragraph_references": len(refs),
            "references_resolving_in_operator_nodes": sum(
                f"tm280_10:{ref}" in nodes for _, ref in refs
            ),
            "labelled_part_number_mentions_matching_catalogue": len(mentions),
            "distinct_labelled_part_numbers_matching_catalogue": len({pn for _, pn in mentions}),
            "method": (
                "Exact para. references and labelled P/N or part number tokens; no keyword map."
            ),
            "limits": (
                "Not an exhaustive chain census: unlabelled numbers, graphics, OCR, and "
                "cross-manual reasoning are outside this scan. No complete repair-chain "
                "absence is claimed. Candidate identities and meaning require human review."
            ),
        },
        "quarantined_references": [
            {
                "source": "tm280_10:table:3-1:7:r30",
                "reference": "3-28",
                "target": "tm280_10:3-28",
                "reason": (
                    "HVAC filter service points to interior light bulb replacement; "
                    "semantic mismatch."
                ),
                "action": (
                    "Excluded; client/source-owner clarification required, not silently corrected."
                ),
                "source_page": nodes["tm280_10:table:3-1:7:r30"].page_start,
                "source_quote": "Service HVAC filters (para. 3-28).",
                "target_page": nodes["tm280_10:3-28"].page_start,
                "target_quote": nodes["tm280_10:3-28"].text,
            }
        ],
    }


def render_candidates(candidates: list[ReviewCandidate], nodes: dict[str, Node]) -> str:
    lines = [
        "# Additional 25 Choice B candidates for review"
        if candidates and all(c.batch == 2 for c in candidates)
        else "# Choice B questions and source evidence",
        "",
        "Choice B: bounded manual relationships. Full repair chains are not required.",
        "Client acceptance is shown per case. The full benchmark is not frozen or approved.",
        "Batch 2 must be reviewed before M3. Wording was prepared with AI assistance.",
        "Expected answers are review notes, not complete service procedures.",
        f"This file contains {len(candidates)} cases: "
        f"{sum(c.review_status == 'client_accepted' for c in candidates)} accepted and "
        f"{sum(c.review_status != 'client_accepted' for c in candidates)} pending review.",
        "PDF pages below are one-based physical file pages, not printed manual page labels.",
        "",
        "| ID | Scope | Type | Batch | Client review |",
        "|---|---|---|---|---|",
    ]
    lines.extend(
        f"| {c.id} | {c.scope} | {c.question_type} | {c.batch} | {c.review_status} |"
        for c in candidates
    )
    for candidate in candidates:
        lines.extend(
            [
                "",
                f"## {candidate.id}",
                "",
                candidate.question,
                "",
                "Expected answer for review: " + candidate.expected_answer,
                "",
                "Required facts for scoring:",
                "",
                *[f"- `{f.source_node_id}`: {f.text}" for f in candidate.required_facts],
                "",
                "Evidence:",
                "",
            ]
        )
        seen: set[tuple[str, str]] = set()
        for evidence in evidence_spans(candidate):
            if (evidence.node_id, evidence.quote) in seen:
                continue
            seen.add((evidence.node_id, evidence.quote))
            lines.extend(
                [
                    f"- `{evidence.node_id}`, PDF page {evidence.page}: {evidence.quote}",
                ]
            )
        for relation in candidate.relations:
            if relation.kind != "explicit_part_number":
                continue
            node = nodes[relation.target.node_id]
            assert node.table is not None
            fields = dict(zip(node.table.headers, node.table.cells, strict=True))
            lines.extend(
                [
                    "",
                    f"Parsed catalogue fields for `{relation.target.node_id}` "
                    "(check effectivity and fit against the PDF):",
                    "",
                ]
            )
            lines.extend(f"- {key}: {value}" for key, value in fields.items())
        lines.extend(["", "Limits:", ""])
        lines.extend(f"- {note}" for note in candidate.limitations)
        lines.extend(
            ["", f"Client disposition: {candidate.review_status}. Full benchmark freeze: pending."]
        )
    return "\n".join(lines) + "\n"


def render_corrections(candidates: list[ReviewCandidate]) -> str:
    lines = [
        "# Catalogue corrections to the accepted first batch",
        "",
        "The five flagged cases explicitly ask for catalogue NSNs. All first-batch catalogue",
        "cases now require a catalogue-only fact, so maintenance text alone cannot pass.",
        "Questions and required facts below are reflected in bounded_questions.jsonl.",
        "Applicability limits, including the water-pump conflict, are retained in the full pack.",
    ]
    for candidate in candidates:
        if candidate.batch != 1 or candidate.scope != "maintenance_catalogue_identity":
            continue
        targets = {r.target.node_id for r in candidate.relations}
        lines.extend(["", f"## {candidate.id}", "", candidate.question, ""])
        lines.extend(
            f"- Required catalogue fact from `{f.source_node_id}`: {f.text}"
            for f in candidate.required_facts
            if f.source_node_id in targets
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Refresh local review artifacts.")
    args = parser.parse_args()
    candidates = load_candidates()
    nodes = load_nodes()
    errors = validate_candidates(candidates, nodes)
    records = evaluation_records(candidates)
    errors.extend(
        validate(records, {k: n.text for k, n in nodes.items()}, profile="bounded_targets")
    )
    result = audit(candidates, nodes)
    result.update(check_pdf_spans(candidates))
    checks = result["span_checks"]
    assert isinstance(checks, list)
    errors.extend(
        f"{row['node_id']}: quote not found on physical PDF page {row['pdf_page']}"
        for row in checks
        if not row["normalised_exact_match"]
    )
    if errors:
        print("\n".join(errors))
        return 1
    markdown = render_candidates(candidates, nodes)
    audit_json = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    questions_json = "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in records
    )
    batch_2_markdown = render_candidates([c for c in candidates if c.batch == 2], nodes)
    corrections_markdown = render_corrections(candidates)
    if args.write:
        REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
        REVIEW_PATH.write_text(markdown, encoding="utf-8")
        AUDIT_PATH.write_text(audit_json, encoding="utf-8")
        QUESTIONS_PATH.write_text(questions_json, encoding="utf-8")
        BATCH_2_PATH.write_text(batch_2_markdown, encoding="utf-8")
        CORRECTIONS_PATH.write_text(corrections_markdown, encoding="utf-8")
    elif (
        REVIEW_PATH.read_text(encoding="utf-8") != markdown
        or AUDIT_PATH.read_text(encoding="utf-8") != audit_json
        or QUESTIONS_PATH.read_text(encoding="utf-8") != questions_json
        or BATCH_2_PATH.read_text(encoding="utf-8") != batch_2_markdown
        or CORRECTIONS_PATH.read_text(encoding="utf-8") != corrections_markdown
    ):
        print("Review artifacts changed; regenerate with --write and review the diff.")
        return 1
    print(
        f"{len(candidates)} Choice B cases validated against nodes and PDFs; "
        f"{result['accepted_candidate_questions']} accepted, "
        f"{result['pending_candidate_questions']} pending. "
        "M3 remains blocked until final review and freeze."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
