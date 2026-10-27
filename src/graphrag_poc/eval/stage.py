"""Plan a bounded benchmark replacement without activating it or calling models."""

import argparse
import json
from collections import Counter
from pathlib import Path

from graphrag_poc.eval.check import QUESTIONS_PATH, load_node_text, load_questions, validate
from graphrag_poc.eval.config import (
    configure_evaluation,
    evaluation_fingerprint,
    validate_evaluation_models,
)
from graphrag_poc.eval.gold import TARGET_SET_PATH, acceptance_errors, questions_digest
from graphrag_poc.ingest.catalog import NODES

BOUNDED_PATH = QUESTIONS_PATH.with_name("bounded_questions.jsonl")
BASELINE_PATH = QUESTIONS_PATH.with_name("metrics.json")
PLAN_PATH = QUESTIONS_PATH.parent / "staging" / "plan.json"
PLAN_KIND = "bounded-evaluation-stage-plan-v1"
TARGET_TYPES = {"relational", "multi_hop"}


def _question_type(record: dict[str, object]) -> str:
    slice_ = record.get("slice")
    return str(slice_.get("question_type", "")) if isinstance(slice_, dict) else ""


def _target(record: dict[str, object]) -> bool:
    return _question_type(record) in TARGET_TYPES


def proposed_questions(
    bounded: list[dict[str, object]], active: list[dict[str, object]]
) -> list[dict[str, object]]:
    """Put bounded targets first, retaining the active controls in their existing order."""

    return [*bounded, *(record for record in active if not _target(record))]


def _read_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def build_plan(
    bounded: list[dict[str, object]],
    active: list[dict[str, object]],
    nodes: dict[str, str],
    contract_path: Path,
    *,
    config_sha256: str,
    model_errors: list[str] | None = None,
    baseline: dict[str, object] | None = None,
) -> dict[str, object]:
    """Validate a prospective 50-target/105-control set; never alter inputs or approval."""

    combined = proposed_questions(bounded, active)
    controls = [record for record in active if not _target(record)]
    target_ids = [str(record.get("id", "")) for record in bounded]
    accepted_ids: list[str] = []
    pending_ids: list[str] = []
    for record, qid in zip(bounded, target_ids, strict=True):
        metadata = record.get("evaluation")
        accepted = (
            isinstance(metadata, dict)
            and metadata.get("client_review_status") == "client_accepted"
            and metadata.get("m3_target_eligible") is True
            and metadata.get("evidence_basis") == "manual_supported"
            and bool(metadata.get("source_chain_review"))
        )
        (accepted_ids if accepted else pending_ids).append(qid)

    bounded_errors = validate(bounded, nodes, profile="bounded_targets")
    full_errors = validate(combined, nodes, profile="full")
    contract_errors = acceptance_errors(combined, contract_path)
    readiness_errors = list(model_errors or [])
    if len(bounded) != 50 or not all(_target(record) for record in bounded):
        readiness_errors.append("Expected exactly 50 bounded relational/multi-hop targets.")
    if len(controls) != 105:
        readiness_errors.append(
            f"Expected 105 retained non-target controls; found {len(controls)}."
        )
    if pending_ids:
        readiness_errors.append(f"{len(pending_ids)} bounded targets still lack client acceptance.")
    if not config_sha256:
        readiness_errors.append("The evaluation model/protocol fingerprint is missing.")

    try:
        contract = _read_object(contract_path)
    except (OSError, ValueError):
        contract = {}
    if contract:
        for key, expected in (
            ("minimum_target_questions", 50),
            ("evidence_gain_points", 15),
            ("required_fact_gain_points", 10),
        ):
            if contract.get(key) != expected:
                readiness_errors.append(f"Contract {key} must remain {expected}.")
        for key, expected_ids in (
            ("accepted_candidate_ids", accepted_ids),
            ("pending_candidate_ids", pending_ids),
        ):
            if contract.get(key) != expected_ids:
                readiness_errors.append(f"Contract {key} differs from the bounded review metadata.")
        if contract.get("prepared_questions_sha256") != questions_digest(bounded):
            readiness_errors.append(
                "Prepared bounded questions differ from the contract fingerprint."
            )
    readiness_errors.extend(bounded_errors)
    readiness_errors.extend(full_errors)
    readiness_errors.extend(contract_errors)

    proposed_sha256 = questions_digest(combined)
    baseline_errors = []
    if baseline is None:
        baseline_errors.append("No baseline metrics were supplied; a new baseline is required.")
    else:
        if baseline.get("questions_sha256") != proposed_sha256:
            baseline_errors.append(
                "Baseline questions do not match the proposed combined benchmark."
            )
        if baseline.get("evaluation_config_sha256") != config_sha256:
            baseline_errors.append("Baseline model/protocol fingerprint does not match.")

    return {
        "kind": PLAN_KIND,
        "plan_only": True,
        "activation_performed": False,
        "model_calls_made": False,
        "runtime_readiness_checked": False,
        "readiness_scope": "benchmark approval, schema and configuration only",
        "ready": not readiness_errors,
        "ready_for_m3": not readiness_errors and not baseline_errors,
        "counts": {
            "bounded_targets": len(bounded),
            "accepted_targets": len(accepted_ids),
            "pending_targets": len(pending_ids),
            "retained_controls": len(controls),
            "proposed_total": len(combined),
            "by_type": dict(Counter(_question_type(record) for record in combined)),
        },
        "target_ids": target_ids,
        "accepted_target_ids": accepted_ids,
        "pending_target_ids": pending_ids,
        "retained_control_ids": [str(record.get("id", "")) for record in controls],
        "excluded_legacy_target_ids": [
            str(record.get("id", "")) for record in active if _target(record)
        ],
        "fingerprints": {
            "active_questions_sha256": questions_digest(active),
            "bounded_questions_sha256": questions_digest(bounded),
            "retained_controls_sha256": questions_digest(controls),
            "proposed_questions_sha256": proposed_sha256,
            "evaluation_config_sha256": config_sha256,
            "contract_questions_sha256": contract.get("questions_sha256"),
            "baseline_questions_sha256": (baseline or {}).get("questions_sha256"),
            "baseline_evaluation_config_sha256": (baseline or {}).get("evaluation_config_sha256"),
        },
        "bounded_validation_errors": bounded_errors,
        "full_validation_errors": full_errors,
        "acceptance_errors": contract_errors,
        "readiness_errors": readiness_errors,
        "baseline_reuse_errors": baseline_errors,
        "next_step": (
            "Obtain explicit acceptance for every target and a freeze of the combined benchmark. "
            "target_set.question_ids must list the 50 targets, while target_set.questions_sha256 "
            "must cover all 155 ordered records, including the 105 controls. "
            "Any activation and model evaluation remain separate authorized actions. "
            "Baseline and graph must use this same combined digest and model/protocol fingerprint."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan", action="store_true", required=True, help="Plan only; never activate."
    )
    parser.add_argument("--bounded", type=Path, default=BOUNDED_PATH)
    parser.add_argument("--active", type=Path, default=QUESTIONS_PATH)
    parser.add_argument("--contract", type=Path, default=TARGET_SET_PATH)
    parser.add_argument("--nodes", type=Path, default=NODES)
    parser.add_argument("--baseline-metrics", type=Path, default=BASELINE_PATH)
    parser.add_argument(
        "--output", type=Path, default=PLAN_PATH, help="Write a staging-plan JSON report."
    )
    args = parser.parse_args(argv)
    protected = {QUESTIONS_PATH, BOUNDED_PATH, TARGET_SET_PATH, BASELINE_PATH}
    protected.update({args.active, args.bounded, args.contract, args.baseline_metrics})
    try:
        if args.output.resolve() in {path.resolve() for path in protected} or (
            args.output.exists() and _read_object(args.output).get("kind") != PLAN_KIND
        ):
            raise ValueError("the output may overwrite only a staging-plan report")
    except (OSError, ValueError) as exc:
        print(f"Refusing to overwrite {args.output}: {exc}")
        return 1
    configure_evaluation()
    model_errors = []
    config_sha256 = ""
    try:
        validate_evaluation_models()
        config_sha256 = evaluation_fingerprint()
    except RuntimeError as exc:
        model_errors.append(str(exc))
    try:
        baseline = _read_object(args.baseline_metrics) if args.baseline_metrics.exists() else None
        plan = build_plan(
            load_questions(args.bounded),
            load_questions(args.active),
            load_node_text(args.nodes),
            args.contract,
            config_sha256=config_sha256,
            model_errors=model_errors,
            baseline=baseline,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as destination:
            destination.write(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    except (OSError, ValueError) as exc:
        print(f"Cannot write staging plan: {exc}")
        return 1
    print(f"Plan written to {args.output}; ready={plan['ready']}. No activation or model calls.")
    return 0  # A successful plan does not activate data or grant review readiness.


if __name__ == "__main__":
    raise SystemExit(main())
