"""Assign every evaluation question to one M2 failure class, or to success."""

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RESULTS_PATH = ROOT / "data" / "eval" / "results.jsonl"
ASSIGNMENTS_PATH = ROOT / "data" / "eval" / "failure_assignments.jsonl"
M1_RESULTS_PATH = ROOT / "data" / "eval" / "m1_baseline" / "results.jsonl"

# First match wins. Success is the fall-through.
CLASS_ORDER = (
    "keyword_mismatch",
    "unanswerable_answered",
    "follow_up_unresolved",
    "applicability_unresolved",
    "code_part_relation",
    "procedure_incomplete",
    "wrong_section",
    "ranked_too_low",
    "answer_omitted_fact",
)


@dataclass(frozen=True)
class Assignment:
    id: str
    question_type: str
    failure_class: str


def classify_row(row: dict[str, object]) -> str:
    """One class for a results.jsonl row. `success` means the question did not fail."""

    refused = bool(row.get("refused"))
    expected = str(row.get("expected_action", ""))
    question_type = str(row.get("question_type", ""))
    rank = _int(row.get("first_gold_rank"))
    missing = _strings(row.get("missing_gold"))
    facts_present = _int(row.get("facts_present"))
    facts_required = _int(row.get("facts_required"))
    in_ten = 1 <= rank <= 10
    parts_missing = [node_id for node_id in missing if node_id.startswith("tm280_24p_1")]
    if refused and in_ten and expected != "refuse":
        return "keyword_mismatch"
    if expected == "refuse" and not refused:
        return "unanswerable_answered"
    if question_type == "follow_up" and (missing or facts_present < facts_required):
        return "follow_up_unresolved"
    if question_type == "applicability" and missing:
        return "applicability_unresolved"
    if question_type in {"relational", "multi_hop"} and parts_missing and in_ten:
        return "code_part_relation"
    if question_type == "procedure" and missing and in_ten:
        return "procedure_incomplete"
    if missing and rank == 0:
        return "wrong_section"
    if missing and rank > 10:
        return "ranked_too_low"
    if facts_present < facts_required or (refused and expected != "refuse"):
        return "answer_omitted_fact"
    return "success"


def assign_all(rows: list[dict[str, object]]) -> list[Assignment]:
    """Classify every row. Raises if a question id is repeated."""

    seen: set[str] = set()
    assigned: list[Assignment] = []
    for row in rows:
        qid = str(row.get("id", ""))
        if not qid or qid in seen:
            raise ValueError(f"duplicate or empty result id {qid!r}")
        seen.add(qid)
        assigned.append(
            Assignment(qid, str(row.get("question_type", "")), classify_row(row))
        )
    return assigned


def counts(assigned: list[Assignment]) -> dict[str, int]:
    totals = {name: 0 for name in ("success", *CLASS_ORDER)}
    for item in assigned:
        totals[item.failure_class] = totals.get(item.failure_class, 0) + 1
    return totals


def load_results(path: Path | None = None) -> list[dict[str, object]]:
    source = path or RESULTS_PATH
    rows: list[dict[str, object]] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        if isinstance(row, dict):
            rows.append(row)
    return rows


def write_assignments(
    assigned: list[Assignment], path: Path | None = None
) -> Path:
    destination = path or ASSIGNMENTS_PATH
    lines = [
        json.dumps(
            {
                "id": item.id,
                "question_type": item.question_type,
                "failure_class": item.failure_class,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        for item in assigned
    ]
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination


def failing(assigned: list[Assignment]) -> list[Assignment]:
    return [item for item in assigned if item.failure_class != "success"]


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return value


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]
