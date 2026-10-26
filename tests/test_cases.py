"""Synthetic cases stay seeded, and every code and part is taken from the node files."""

import hashlib
import json

import pytest

from graphrag_poc.cases.generate import (
    consistent_with_source,
    generate_cases,
    missing_references,
    render_cases,
)
from graphrag_poc.cases.rules import CASES_PATH, load_rules
from graphrag_poc.cases.sources import load_faults, load_parts, parse_steps, usable_step


def test_step_text_is_taken_from_the_malfunction_row() -> None:
    body = (
        "Step 1. Check to see if transmission shift lever is in neutral. "
        "If not, place lever in neutral. "
        "Step 2. Other causes. Notify unit maintenance."
    )
    steps = parse_steps(body)
    assert steps[0] == (
        "Check to see if transmission shift lever is in neutral",
        "place lever in neutral",
    )
    assert steps[1] == ("Other causes", "Notify unit maintenance")
    assert all(cause in body and action in body for cause, action in steps)


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (
            "Step 1. Check for low oil level (para. 3-17). Add oil (Appendix G).",
            ("Check for low oil level (para. 3-17)", "Add oil (Appendix G)"),
        ),
        (
            "Clean and adjust parking brake (para. 3-13) "
            "If parking brake still fails to hold vehicle, notify unit maintenance.",
            (
                "Clean and adjust parking brake (para. 3-13)",
                "parking brake still fails to hold vehicle, notify unit maintenance",
            ),
        ),
        ("All causes. Notify unit maintenance.", ("All causes", "Notify unit maintenance")),
    ],
)
def test_references_remain_intact_in_cause_action_pairs(
    body: str, expected: tuple[str, str]
) -> None:
    assert parse_steps(body) == [expected]


@pytest.mark.parametrize(
    ("cause", "action"),
    [
        ("11", "ROUGH SHIFTING All causes. Notify unit maintenance"),
        ("Other causes", "Notify unit maintenance"),
        ("All causes", "Notify unit maintenance"),
        ("Check battery cables", "Notify unit maintenance of any damage to cables"),
        ("Check the lamp", "Notify unit maintenance if the wait-to-start lamp fails"),
        ("Check the oil", "Check the oil"),
        ("", "Add oil"),
    ],
)
def test_uninformative_pairs_are_not_eligible(cause: str, action: str) -> None:
    assert not usable_step(cause, action)


def test_two_runs_match_and_reference_real_rows() -> None:
    rules = load_rules()
    first = generate_cases(rules)
    second = generate_cases(rules)
    assert render_cases(first) == render_cases(second)
    assert len(first) >= 2000
    assert first[0].case_id == "C-000001"
    assert first[-1].case_id == "C-002000"
    assert missing_references(first) == []
    assert consistent_with_source(first, load_faults(rules)) == []
    crank = next(case for case in first if "ENGINE FAILS TO CRANK" in case.error_codes[0])
    assert crank.model in rules.family_models
    assert crank.search_text.startswith(f"{crank.model} ")
    assert crank.error_codes[0] in crank.search_text
    assert crank.parts[0] in crank.search_text
    smoke = next(case for case in first if case.error_codes[0].startswith("5. "))
    assert "TEMPERATURE" in smoke.error_codes[0]
    weapon = [case for case in first if case.error_codes[0].startswith("24. ")]
    ambulances = {"M996", "M996A1", "M997", "M997A1", "M997A2", "M1035", "M1035A1", "M1035A2"}
    assert weapon
    assert all(case.model not in ambulances for case in weapon)
    lights = [case for case in first if case.error_codes[0].startswith("26. ")]
    assert lights
    assert all(case.model in ambulances for case in lights)
    assert "ILLUMINATE" in lights[0].error_codes[0]
    catalog = {part.number: part.description.upper() for part in load_parts(rules)}
    for case in first:
        assert usable_step(case.cause, case.action)
        assert case.model_extra is not None
        assert case.model_extra["diagnosis_confirmed"] is False
        assert case.model_extra["part_relation"] == "keyword_candidate_unverified"
        number = case.error_codes[0].split(".", 1)[0]
        description = catalog[case.parts[0]]
        assert any(word in description for word in rules.part_keywords[number])

    invalid = first[0].model_copy(update={"parts": ["7X677"]})
    assert any("7X677" in error for error in missing_references([invalid]))


def test_saved_case_file_matches_the_generator() -> None:
    assert CASES_PATH.exists(), "run make generate-cases first"
    assert CASES_PATH.read_text(encoding="utf-8") == render_cases(generate_cases())


def test_quality_report_matches_current_inputs() -> None:
    report = json.loads(CASES_PATH.with_name("quality_report.json").read_text())
    root = CASES_PATH.parents[2]
    for name, digest in report["sha256"].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
    assert report["numeric_causes"] == report["generic_causes"] == 0
    assert report["invalid_pairs"] == report["part_7X677"] == 0
