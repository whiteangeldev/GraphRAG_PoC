"""Auditable counts and input hashes for the current synthetic case revision."""

import hashlib
import json
from pathlib import Path

from graphrag_poc.cases.rules import CASES_PATH, RULES_PATH, Rules
from graphrag_poc.cases.sources import load_faults, usable_step
from graphrag_poc.ingest.catalog import NODES
from graphrag_poc.models import CaseRecord


def write_quality_report(cases: list[CaseRecord], rules: Rules) -> Path:
    faults = load_faults(rules)
    excluded = [
        {
            "code": fault.code,
            "source_node_id": fault.node_id,
            "reason": "no informative actionable pair",
        }
        for fault in faults
        if not any(usable_step(*step) for step in fault.steps)
    ]
    paths = [NODES / f"{key}.jsonl" for key in (rules.fault_doc_key, rules.parts_doc_key)]
    paths.extend([RULES_PATH, CASES_PATH])
    payload = {
        "revision": "m1-feedback-data-v2",
        "cases": len(cases),
        "eligible_faults": len(faults) - len(excluded),
        "excluded_faults": excluded,
        "numeric_causes": sum(case.cause.strip().isdigit() for case in cases),
        "generic_causes": sum(
            case.cause.strip(" .").lower() in {"all causes", "other causes"} for case in cases
        ),
        "invalid_pairs": sum(not usable_step(case.cause, case.action) for case in cases),
        "part_7X677": sum("7X677" in case.parts for case in cases),
        "case_kind": "synthetic_diagnostic_instruction",
        "diagnosis_confirmed": False,
        "part_relation": "keyword_candidate_unverified",
        "sha256": {
            str(path.relative_to(NODES.parents[1])): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths
        },
        "evaluation_status": "Historical scores; corrected data needs reindexing, "
        "independent gold review, realistic questions, and fresh evaluation.",
    }
    destination = CASES_PATH.with_name("quality_report.json")
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return destination
