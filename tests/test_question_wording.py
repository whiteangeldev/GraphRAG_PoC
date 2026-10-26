"""Client-requested wording survives regeneration without legitimising keyword gold."""

import copy
import json
import re
from pathlib import Path

import pytest

from graphrag_poc.eval.build import build_questions
from graphrag_poc.eval.check import load_node_text, load_questions
from graphrag_poc.eval.gold import questions_digest
from graphrag_poc.eval.wording import WORDING_PATH, apply_wording

ROOT = Path(__file__).resolve().parents[1]


def test_all_fifty_prompts_change_without_changing_provisional_gold() -> None:
    snapshot = [
        json.loads(line)
        for line in (ROOT / "data/eval/keyword_exploratory.jsonl").read_text().splitlines()
    ]
    current = {row["id"]: row for row in load_questions()}
    texts = load_node_text()
    assert len(snapshot) == 50
    for old in snapshot:
        row = current[old["id"]]
        assert row["question"] != old["question"]
        for field in ("gold", "required_facts", "expected_action", "evaluation"):
            assert row[field] == old[field]
        assert row["slice"]["vocabulary"] == "user"
        assert row["wording_review"]["status"] == "repository_revision_pending_client"
        # Do not paste malfunction titles, numbered faults, or the answer's part number.
        title = texts[row["gold"]["node_ids"][0]].split(" Step 1.", 1)[0]
        title = re.sub(r"^\d+\.\s*", "", title)
        assert title.casefold() not in row["question"].casefold()
        assert "malfunction " not in row["question"].lower()
        assert old["required_facts"][-1]["text"].lower() not in row["question"].lower()
        assert not any(
            hint in row["question"].lower()
            for hint in ("nozzle", "radiator", "oil pump", "alternator", "starter")
        )
    assert len({current[row["id"]]["question"] for row in snapshot}) == 50


def test_front_matter_is_excluded_without_renumbering_survivors() -> None:
    records = build_questions()
    procedures = [row for row in records if row["slice"]["question_type"] == "procedure"]
    assert len(records) == 155
    assert {row["id"] for row in procedures} == {
        f"procedure-{index:04d}" for index in range(1, 23) if index not in (1, 3)
    }
    for row in procedures:
        assert all(
            not node_id.startswith(("tm280_10:step-", "tm280_20_2:step-"))
            for node_id in row["gold"]["node_ids"]
        )


@pytest.mark.parametrize("change", ["missing", "extra", "duplicate", "source"])
def test_stale_wording_fails_before_changing_records(tmp_path: Path, change: str) -> None:
    entries = [json.loads(line) for line in WORDING_PATH.read_text().splitlines()]
    if change == "missing":
        entries.pop()
    elif change == "extra":
        entries.append({**entries[-1], "id": "multi-9999"})
    elif change == "duplicate":
        entries.append(entries[-1])
    else:
        entries[-1]["source_node_id"] = "tm280_10:table:3-1:r1"
    path = tmp_path / "wording.jsonl"
    path.write_text("\n".join(json.dumps(row) for row in entries))
    records = load_questions()
    before = copy.deepcopy(records)
    with pytest.raises(ValueError):
        apply_wording(records, path)
    assert records == before


def test_pending_target_manifest_fingerprints_current_questions() -> None:
    agreement = json.loads((ROOT / "data/eval/target_set.json").read_text())
    assert agreement["status"] == "pending_client_agreement"
    assert agreement["question_ids"] == []
    assert agreement["questions_sha256"] == questions_digest(load_questions())
