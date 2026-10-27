"""Check the evaluation set against Appendix C and the node files."""

import json
from pathlib import Path
from typing import Literal

from graphrag_poc.ingest.catalog import NODES

QUESTIONS_PATH = Path(__file__).resolve().parents[3] / "data" / "eval" / "questions.jsonl"

MINIMUMS = {
    "relational_or_multi_hop": 50,
    "lookup": 30,
    "procedure": 20,
    "applicability": 20,
    "unanswerable": 15,
}
ACTIONS = {"answer", "refuse", "clarify", "related"}
AUTHOR = "incredible9120"


def load_questions(path: Path | None = None) -> list[dict[str, object]]:
    source = path or QUESTIONS_PATH
    questions: list[dict[str, object]] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if line:
            record = json.loads(line)
            if isinstance(record, dict):
                questions.append(record)
    return questions


def load_node_text(nodes_dir: Path | None = None) -> dict[str, str]:
    texts: dict[str, str] = {}
    root = nodes_dir or NODES
    for path in sorted(root.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            node = json.loads(line)
            texts[str(node["node_id"])] = str(node.get("text") or "")
    return texts


def validate(
    questions: list[dict[str, object]] | None = None,
    nodes: dict[str, str] | None = None,
    *,
    profile: Literal["full", "bounded_targets"] = "full",
) -> list[str]:
    """Return errors. An empty list means the Appendix C exit check passes."""

    records = questions if questions is not None else load_questions()
    texts = nodes if nodes is not None else load_node_text()
    errors: list[str] = []
    if profile == "full" and len(records) < 150:
        errors.append(f"expected at least 150 questions, found {len(records)}")

    counts: dict[str, int] = {}
    everyday = 0
    japanese = 0
    seen_ids: set[str] = set()
    for record in records:
        qid = str(record.get("id", ""))
        if not qid or qid in seen_ids:
            errors.append(f"duplicate or empty id {qid!r}")
        seen_ids.add(qid)
        slice_ = record.get("slice")
        if not isinstance(slice_, dict):
            errors.append(f"{qid}: slice is missing")
            continue
        qtype = str(slice_.get("question_type", ""))
        counts[qtype] = counts.get(qtype, 0) + 1
        if slice_.get("vocabulary") == "user":
            everyday += 1
        if slice_.get("language") == "ja":
            japanese += 1
        action = str(record.get("expected_action", ""))
        if action not in ACTIONS:
            errors.append(f"{qid}: unexpected action {action}")
        notes = str(record.get("notes", ""))
        if AUTHOR not in notes:
            errors.append(f"{qid}: notes do not name the author")
        gold = record.get("gold")
        if not isinstance(gold, dict):
            errors.append(f"{qid}: gold is missing")
            continue
        node_ids = gold.get("node_ids")
        if not isinstance(node_ids, list):
            errors.append(f"{qid}: gold.node_ids is missing")
            continue
        if qtype in {"relational", "multi_hop"} and len(node_ids) < 2:
            errors.append(f"{qid}: {qtype} question cites fewer than two passages")
        for node_id in node_ids:
            if str(node_id) not in texts:
                errors.append(f"{qid}: gold node {node_id} does not exist")
        facts = record.get("required_facts")
        if not isinstance(facts, list):
            errors.append(f"{qid}: required_facts is missing")
            continue
        if action == "answer" and not facts:
            errors.append(f"{qid}: an answer needs at least one required fact")
        for fact in facts:
            if not isinstance(fact, dict):
                errors.append(f"{qid}: a required fact is not an object")
                continue
            text = str(fact.get("text", ""))
            if not text:
                errors.append(f"{qid}: a required fact has empty text")
                continue
            if not any(text in texts.get(str(node_id), "") for node_id in node_ids):
                errors.append(f"{qid}: required fact {text!r} is not in a gold passage")

    relational = counts.get("relational", 0) + counts.get("multi_hop", 0)
    if relational < MINIMUMS["relational_or_multi_hop"]:
        errors.append(f"relational or multi-hop {relational} is below 50")
    if profile == "full":
        for name in ("lookup", "procedure", "applicability", "unanswerable"):
            if counts.get(name, 0) < MINIMUMS[name]:
                errors.append(f"{name} {counts.get(name, 0)} is below {MINIMUMS[name]}")
    if everyday * 2 < len(records):
        errors.append(f"everyday wording {everyday} is below half of {len(records)}")
    if profile == "full" and japanese < 8:
        errors.append(f"Japanese subset has {japanese} questions")
    if profile == "full" and (
        counts.get("troubleshooting", 0) < 1 or counts.get("follow_up", 0) < 1
    ):
        errors.append("troubleshooting and follow-up questions are missing")
    return errors
