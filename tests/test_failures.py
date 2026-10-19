"""Every evaluation row receives exactly one M2 class."""

from graphrag_poc.eval.failures import assign_all, classify_row, counts, load_results


def _row(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "q",
        "question_type": "lookup",
        "expected_action": "answer",
        "refused": False,
        "first_gold_rank": 1,
        "missing_gold": [],
        "facts_present": 1,
        "facts_required": 1,
    }
    base.update(overrides)
    return base


def test_priority_picks_one_class() -> None:
    refused = _row(id="a", refused=True, first_gold_rank=2, facts_present=0)
    assert classify_row(refused) == "keyword_mismatch"
    quoted = _row(id="b", expected_action="refuse", refused=False, first_gold_rank=0)
    assert classify_row(quoted) == "unanswerable_answered"
    part = _row(
        id="c",
        question_type="relational",
        first_gold_rank=2,
        missing_gold=["tm280_24p_1:parts:r1"],
        facts_present=1,
        facts_required=2,
    )
    assert classify_row(part) == "code_part_relation"
    assert classify_row(_row(id="d")) == "success"


def test_saved_results_are_fully_assigned() -> None:
    rows = load_results()
    assigned = assign_all(rows)
    assert len(assigned) == len(rows)
    assert sum(counts(assigned).values()) == len(rows)
    assert {item.id for item in assigned} == {str(row["id"]) for row in rows}
