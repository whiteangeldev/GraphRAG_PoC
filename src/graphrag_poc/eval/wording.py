"""Keep curated draft wording separate from generated, provisional gold."""

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

WORDING_PATH = Path(__file__).resolve().parents[3] / "data/eval/question_wording.jsonl"
_TARGET_TYPES = {"relational", "multi_hop"}


class QuestionWording(BaseModel):
    """Pin a draft prompt to its question ID and source malfunction."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1)
    source_node_id: str = Field(min_length=1)
    question: str = Field(min_length=20)


def apply_wording(
    records: list[dict[str, object]], path: Path = WORDING_PATH
) -> list[dict[str, object]]:
    """Apply all curated prompts, refusing stale mappings instead of using templates."""

    entries = [
        QuestionWording.model_validate(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    wording = {entry.id: entry for entry in entries}
    if len(wording) != len(entries):
        raise ValueError("duplicate IDs in question wording")
    targets = [
        record
        for record in records
        if isinstance(slice_ := record.get("slice"), dict)
        and slice_.get("question_type") in _TARGET_TYPES
    ]
    target_ids = [str(record["id"]) for record in targets]
    if len(set(target_ids)) != len(target_ids) or set(wording) != set(target_ids):
        raise ValueError("question wording IDs do not match the generated target questions")
    # Check the complete mapping before modifying any records.
    for record in targets:
        entry = wording[str(record["id"])]
        gold = record.get("gold")
        if not isinstance(gold, dict) or gold.get("node_ids", [])[:1] != [entry.source_node_id]:
            raise ValueError(f"{entry.id}: question wording source changed; review it first")
    for record in targets:
        entry = wording[str(record["id"])]
        record["question"] = entry.question
        slice_ = record["slice"]
        assert isinstance(slice_, dict)
        slice_["vocabulary"] = "user"
        record["wording_review"] = {
            "status": "repository_revision_pending_client",
            "date": "2026-10-26",
            "source": "data/eval/question_wording.jsonl",
        }
        record["notes"] = (
            f"{record.get('notes', '')}; wording revised with AI assistance, "
            "26 October 2026; client review pending"
        )
    return records
