"""Synthetic cases stay seeded, and every code and part is taken from the node files."""

from graphrag_poc.cases.generate import (
    consistent_with_source,
    generate_cases,
    missing_references,
    render_cases,
)
from graphrag_poc.cases.rules import CASES_PATH, load_rules
from graphrag_poc.cases.sources import load_faults, load_parts, parse_steps


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
        number = case.error_codes[0].split(".", 1)[0]
        description = catalog[case.parts[0]]
        assert any(word in description for word in rules.part_keywords[number])


def test_saved_case_file_matches_the_generator() -> None:
    assert CASES_PATH.exists(), "run make generate-cases first"
    assert CASES_PATH.read_text(encoding="utf-8") == render_cases(generate_cases())
