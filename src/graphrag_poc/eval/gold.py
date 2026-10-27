"""Source-checked relation candidates, independent of graph keyword rules."""

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from graphrag_poc.ingest.catalog import NODES
from graphrag_poc.models import Node

RELATIONS_PATH = NODES.parent / "eval" / "source_relations.jsonl"
TARGET_SET_PATH = RELATIONS_PATH.with_name("target_set.json")


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    doc_key: str
    page: int
    quote: str
    text_sha256: str


class SourceRelation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    kind: Literal["explicit_part_number", "explicit_paragraph_reference"]
    source: Evidence
    target: Evidence
    reference: str
    claim: str
    limitations: list[str]
    review_status: Literal["source_checked_pending_client"]
    # These records prove individual links, not a complete fault-to-repair chain.
    m3_target_eligible: Literal[False] = False


def load_relations(path: Path = RELATIONS_PATH) -> list[SourceRelation]:
    return [
        SourceRelation.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_nodes(nodes_dir: Path = NODES) -> dict[str, Node]:
    nodes: dict[str, Node] = {}
    for path in sorted(nodes_dir.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                node = Node.model_validate_json(line)
                nodes[node.node_id] = node
    return nodes


def validate_relations(relations: list[SourceRelation], nodes: dict[str, Node]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for relation in relations:
        if relation.id in seen:
            errors.append(f"duplicate relation {relation.id}")
        seen.add(relation.id)
        for evidence in (relation.source, relation.target):
            node = nodes.get(evidence.node_id)
            if node is None:
                errors.append(f"{relation.id}: missing node {evidence.node_id}")
                continue
            if not evidence.quote.strip() or evidence.quote not in node.text:
                errors.append(f"{relation.id}: quote is not an exact source span")
            if hashlib.sha256(node.text.encode()).hexdigest() != evidence.text_sha256:
                errors.append(f"{relation.id}: source text changed")
            if (
                evidence.doc_key != node.doc_key
                or not node.page_start <= evidence.page <= node.page_end
            ):
                errors.append(f"{relation.id}: incorrect document/page")
        target = nodes.get(relation.target.node_id)
        if relation.kind == "explicit_part_number":
            pattern = rf"(?<![A-Za-z0-9/-]){re.escape(relation.reference)}(?![A-Za-z0-9/-])"
            if not re.search(pattern, relation.source.quote):
                errors.append(f"{relation.id}: source does not state the complete part number")
            table = target.table if target else None
            if table is None or "PART NUMBER" not in table.headers:
                errors.append(f"{relation.id}: target is not a parts row")
            elif table.cells[table.headers.index("PART NUMBER")] != relation.reference:
                errors.append(f"{relation.id}: target PART NUMBER does not match")
        else:
            pattern = rf"\bpara\.\s*{re.escape(relation.reference)}(?![\d.-])"
            if not re.search(pattern, relation.source.quote, re.IGNORECASE):
                errors.append(f"{relation.id}: source does not state the paragraph reference")
            root = f"{relation.source.doc_key}:{relation.reference}"
            if not re.fullmatch(re.escape(root) + r"(?::[1-9]\d*)?", relation.target.node_id):
                errors.append(f"{relation.id}: reference resolves to another paragraph/document")
            elif (
                target is None
                or target.type != "procedure"
                or not re.match(re.escape(relation.reference) + r"\.\s", target.text)
            ):
                errors.append(
                    f"{relation.id}: reference must resolve to an actual procedure, not a TOC entry"
                )
    return errors


def acceptance_errors(records: list[dict[str, object]], path: Path = TARGET_SET_PATH) -> list[str]:
    """Require a frozen, explicitly reviewed target set before model calls or gates."""

    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ["M3 acceptance target-set contract is missing or invalid."]
    if not isinstance(contract, dict):
        return ["M3 acceptance target-set contract must be an object."]
    errors: list[str] = []
    if (
        contract.get("status") != "approved"
        or not contract.get("approved_by")
        or not contract.get("approved_at")
        or not contract.get("approved_scope")
    ):
        errors.append(
            "M3 acceptance is pending client agreement on all targets and benchmark freeze."
        )
    for field, expected in (
        ("minimum_target_questions", 50),
        ("evidence_gain_points", 15),
        ("required_fact_gain_points", 10),
    ):
        if type(contract.get(field)) is not int or contract.get(field) != expected:
            errors.append(f"M3 agreement {field} must remain {expected}.")
    targets: list[dict[str, object]] = []
    for record in records:
        slice_ = record.get("slice")
        if isinstance(slice_, dict) and slice_.get("question_type") in {"relational", "multi_hop"}:
            targets.append(record)
            metadata = record.get("evaluation")
            if (
                not isinstance(metadata, dict)
                or metadata.get("m3_target_eligible") is not True
                or metadata.get("evidence_basis") != "manual_supported"
                or not metadata.get("source_chain_review")
                or metadata.get("client_review_status") != "client_accepted"
            ):
                errors.append(
                    f"{record.get('id')}: exploratory/unreviewed gold cannot count toward M3."
                )
    ids = [str(record.get("id", "")) for record in targets]
    if len(set(ids)) != len(ids) or not all(ids):
        errors.append("M3 target IDs must be nonempty and unique.")
    if len(ids) < 50:
        errors.append(
            f"M3 needs at least 50 reviewed target questions; found {len(ids)} candidates."
        )
    if contract.get("question_ids") != ids:
        errors.append("M3 target IDs differ from the frozen agreement.")
    if contract.get("questions_sha256") != questions_digest(records):
        errors.append("M3 questions differ from the frozen agreement.")
    if "accepted_candidate_ids" in contract and contract["accepted_candidate_ids"] != ids:
        errors.append("M3 accepted candidate IDs differ from the frozen targets.")
    if contract.get("pending_candidate_ids"):
        errors.append("M3 candidate review is still pending.")
    return errors


def questions_digest(records: list[dict[str, object]]) -> str:
    body = json.dumps(records, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate independently sourced gold candidates.")
    parser.add_argument(
        "--acceptance",
        action="store_true",
        help="Also require the frozen M3 target set to be approved.",
    )
    args = parser.parse_args()
    relations = load_relations()
    errors = validate_relations(relations, load_nodes())
    if args.acceptance:
        from graphrag_poc.eval.check import load_questions

        errors.extend(acceptance_errors(load_questions()))
    if errors:
        print("\n".join(errors[:5]))
        if len(errors) > 5:
            print(f"{len(errors)} readiness errors in total; no model calls were made.")
        return 1
    contract = json.loads(TARGET_SET_PATH.read_text(encoding="utf-8"))
    accepted = contract.get("accepted_candidate_ids", [])
    print(
        f"{len(relations)} source-backed partial links validated; "
        f"{len(accepted)} Choice B candidates accepted. "
        "Full target review and benchmark freeze pending; no M3 scoring."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
