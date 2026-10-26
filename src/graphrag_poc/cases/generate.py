"""Build cases.jsonl from the rules file and the node files."""

import json
import random
from datetime import date, timedelta
from pathlib import Path

from graphrag_poc.cases.rules import CASES_PATH, Rules, load_rules
from graphrag_poc.cases.sources import (
    CatalogPart,
    Fault,
    load_faults,
    load_parts,
    load_stated_models,
    usable_step,
)
from graphrag_poc.models import CaseRecord


def generate_cases(
    rules: Rules | None = None,
    *,
    nodes_dir: Path | None = None,
) -> list[CaseRecord]:
    """Return the case list. The same rules and node files always return the same list."""

    active = rules or load_rules()
    if active.count < 1:
        raise ValueError("count must be at least 1")
    faults = load_faults(active, nodes_dir)
    eligible = [fault for fault in faults if any(usable_step(*step) for step in fault.steps)]
    if not eligible:
        raise ValueError("no faults contain an informative cause/action pair")
    parts = load_parts(active, nodes_dir)
    stated = load_stated_models(active.fault_doc_key, nodes_dir)
    family = tuple(model for model in active.family_models if model in stated)
    if not family:
        raise ValueError("none of the family models are stated in the fault document")

    start = date.fromisoformat(active.date_start)
    end = date.fromisoformat(active.date_end)
    span = (end - start).days
    if span < 0:
        raise ValueError("date_end is before date_start")
    if active.frequency_max < active.frequency_min:
        raise ValueError("frequency_max is below frequency_min")

    rng = random.Random(active.seed)
    cases: list[CaseRecord] = []
    for index in range(active.count):
        fault = eligible[index % len(eligible)]
        models = fault.models or family
        model = models[rng.randrange(len(models))]
        part = _related_part(fault, parts, active, rng)
        steps = [step for step in fault.steps if usable_step(*step)]
        cause, action = steps[rng.randrange(len(steps))]
        occurred = start + timedelta(days=rng.randrange(span + 1))
        frequency = rng.randint(active.frequency_min, active.frequency_max)
        fields = {
            "model": model,
            "error_code": fault.code,
            "symptom": fault.symptom,
            "cause": cause,
            "action": action,
            "part": part,
        }
        search = " ".join(fields[name] for name in active.search_text_fields)
        cases.append(
            CaseRecord.model_validate(
                {
                    "case_id": f"C-{index + 1:06d}",
                    "date": occurred.isoformat(),
                    "model": model,
                    "symptom": fault.symptom,
                    "cause": cause,
                    "action": action,
                    "parts": [part],
                    "error_codes": [fault.code],
                    "frequency": frequency,
                    "search_text": search,
                    "source_node_id": fault.node_id,
                    "case_kind": "synthetic_diagnostic_instruction",
                    "diagnosis_confirmed": False,
                    "part_relation": "keyword_candidate_unverified",
                }
            )
        )
    return cases


def render_cases(cases: list[CaseRecord]) -> str:
    lines = [
        json.dumps(case.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":"))
        for case in cases
    ]
    return "\n".join(lines) + "\n"


def write_cases(cases: list[CaseRecord], path: Path | None = None) -> Path:
    destination = path or CASES_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_cases(cases), encoding="utf-8")
    return destination


def _related_part(
    fault: Fault,
    parts: list[CatalogPart],
    rules: Rules,
    rng: random.Random,
) -> str:
    """Pick a part whose description names something in this malfunction."""

    number = fault.code.split(".", 1)[0]
    keywords = tuple(word.upper() for word in rules.part_keywords.get(number, []))
    if not keywords:
        raise ValueError(f"no part keywords for malfunction {number}")
    matched = [
        part for part in parts if any(keyword in part.description.upper() for keyword in keywords)
    ]
    if not matched:
        raise ValueError(f"no parts match {keywords} for malfunction {number}")
    return matched[rng.randrange(len(matched))].number


def missing_references(
    cases: list[CaseRecord],
    *,
    nodes_dir: Path | None = None,
) -> list[str]:
    """Check typed fault labels and PART NUMBER cells, rather than arbitrary cells."""

    rules = load_rules()
    codes = {fault.code for fault in load_faults(rules, nodes_dir)}
    parts = {part.number for part in load_parts(rules, nodes_dir)}
    missing: list[str] = []
    for case in cases:
        for code in case.error_codes:
            if code not in codes:
                missing.append(f"{case.case_id}: error code {code!r} is not in the node files")
        for part in case.parts:
            if part not in parts:
                missing.append(f"{case.case_id}: part number {part!r} is not in the node files")
    return missing


def consistent_with_source(cases: list[CaseRecord], faults: list[Fault]) -> list[str]:
    """Cause and action must be taken from the fault row named on the case."""

    by_id = {fault.node_id: fault for fault in faults}
    errors: list[str] = []
    for case in cases:
        source = case.model_extra.get("source_node_id") if case.model_extra else None
        fault = by_id.get(str(source))
        if fault is None:
            errors.append(f"{case.case_id}: source node is missing")
            continue
        if case.error_codes != [fault.code]:
            errors.append(f"{case.case_id}: error code does not match {fault.node_id}")
        pair = (case.cause, case.action)
        if pair not in fault.steps:
            errors.append(f"{case.case_id}: cause and action are not a step of {fault.node_id}")
        if not usable_step(*pair):
            errors.append(
                f"{case.case_id}: cause/action is generic, incomplete, or escalation-only"
            )
        allowed = fault.models
        if allowed and case.model not in allowed:
            errors.append(f"{case.case_id}: model {case.model} is not stated on {fault.node_id}")
    return errors
