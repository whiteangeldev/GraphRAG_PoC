"""Staging is offline, preserves controls, and cannot confer client acceptance."""

import copy
import json
from pathlib import Path

import pytest

from graphrag_poc.eval import stage
from graphrag_poc.eval.gold import questions_digest


def _record(qid: str, qtype: str, *, accepted: bool = False) -> dict:
    return {
        "id": qid,
        "slice": {"question_type": qtype, "vocabulary": "user", "language": "ja"},
        "question": "Which instruction applies to this documented situation?",
        "expected_action": "answer",
        "gold": {"node_ids": ["source", "target"]},
        "required_facts": [{"type": "step", "text": "Documented instruction."}],
        "notes": "written by incredible9120",
        "evaluation": {
            "client_review_status": "client_accepted"
            if accepted
            else "source_checked_pending_client",
            "m3_target_eligible": accepted,
            "evidence_basis": "manual_supported",
            "source_chain_review": "test-review.md" if accepted else None,
        },
    }


@pytest.fixture
def benchmark(tmp_path: Path) -> tuple[list[dict], list[dict], dict[str, str], Path]:
    bounded = [_record(f"bounded-{index}", "multi_hop", accepted=index < 25) for index in range(50)]
    types = {
        "lookup": 35,
        "procedure": 20,
        "applicability": 22,
        "unanswerable": 16,
        "troubleshooting": 9,
        "follow_up": 3,
    }
    controls = [
        _record(f"{kind}-{index}", kind) for kind, size in types.items() for index in range(size)
    ]
    active = [_record(f"legacy-{index}", "relational") for index in range(50)] + controls
    nodes = {"source": "Documented instruction.", "target": "A referenced procedure."}
    contract_path = tmp_path / "target_set.json"
    _write_contract(contract_path, bounded, active, approved=False)
    return bounded, active, nodes, contract_path


def _write_contract(path: Path, bounded: list[dict], active: list[dict], *, approved: bool) -> None:
    accepted = [
        row["id"]
        for row in bounded
        if row["evaluation"]["client_review_status"] == "client_accepted"
    ]
    pending = [row["id"] for row in bounded if row["id"] not in accepted]
    path.write_text(
        json.dumps(
            {
                "status": "approved" if approved else "pending_client_agreement",
                "approved_by": "test reviewer" if approved else None,
                "approved_at": "2026-10-27" if approved else None,
                "approved_scope": "Choice B",
                "question_ids": [row["id"] for row in bounded] if approved else [],
                "questions_sha256": questions_digest(stage.proposed_questions(bounded, active))
                if approved
                else questions_digest(active),
                "prepared_questions_sha256": questions_digest(bounded),
                "minimum_target_questions": 50,
                "evidence_gain_points": 15,
                "required_fact_gain_points": 10,
                "accepted_candidate_ids": accepted,
                "pending_candidate_ids": pending,
            }
        ),
        encoding="utf-8",
    )


def _approve(bounded: list[dict]) -> None:
    for row in bounded:
        row["evaluation"].update(
            client_review_status="client_accepted",
            m3_target_eligible=True,
            source_chain_review="test-review.md",
        )


def test_pending_plan_preserves_inputs_and_retains_all_controls(benchmark: tuple) -> None:
    bounded, active, nodes, contract_path = benchmark
    before = copy.deepcopy((bounded, active))
    contract_before = contract_path.read_bytes()
    plan = stage.build_plan(bounded, active, nodes, contract_path, config_sha256="test-models")
    assert plan["ready"] is plan["ready_for_m3"] is False
    assert plan["counts"] == {
        "bounded_targets": 50,
        "accepted_targets": 25,
        "pending_targets": 25,
        "retained_controls": 105,
        "proposed_total": 155,
        "by_type": {
            "multi_hop": 50,
            "lookup": 35,
            "procedure": 20,
            "applicability": 22,
            "unanswerable": 16,
            "troubleshooting": 9,
            "follow_up": 3,
        },
    }
    assert plan["bounded_validation_errors"] == plan["full_validation_errors"] == []
    assert len(plan["accepted_target_ids"]) == len(plan["pending_target_ids"]) == 25
    assert any("pending client agreement" in error for error in plan["acceptance_errors"])
    assert sum("exploratory/unreviewed" in error for error in plan["acceptance_errors"]) == 25
    combined = stage.proposed_questions(bounded, active)
    assert combined[:50] == bounded
    assert combined[50:] == active[50:]
    assert len(plan["excluded_legacy_target_ids"]) == 50
    assert plan["fingerprints"]["proposed_questions_sha256"] == questions_digest(combined)
    assert plan["fingerprints"]["bounded_questions_sha256"] == questions_digest(bounded)
    assert (bounded, active) == before
    assert contract_path.read_bytes() == contract_before


def test_acceptance_and_full_combined_freeze_are_both_required(benchmark: tuple) -> None:
    bounded, active, nodes, contract_path = benchmark
    _approve(bounded)
    _write_contract(contract_path, bounded, active, approved=False)
    plan = stage.build_plan(bounded, active, nodes, contract_path, config_sha256="test-models")
    assert plan["ready"] is False
    _write_contract(contract_path, bounded, active, approved=True)
    plan = stage.build_plan(bounded, active, nodes, contract_path, config_sha256="test-models")
    assert plan["ready"] is True
    assert plan["ready_for_m3"] is False  # An approved set still needs its own baseline.
    contract = json.loads(contract_path.read_text())
    contract["questions_sha256"] = questions_digest(bounded)
    contract_path.write_text(json.dumps(contract))
    plan = stage.build_plan(bounded, active, nodes, contract_path, config_sha256="test-models")
    assert plan["ready"] is False
    assert any("questions differ from the frozen" in error for error in plan["acceptance_errors"])


@pytest.mark.parametrize("question_hash,config_hash", [("old", "test-models"), ("current", "old")])
def test_stale_baseline_cannot_enable_m3(
    benchmark: tuple, question_hash: str, config_hash: str
) -> None:
    bounded, active, nodes, contract_path = benchmark
    _approve(bounded)
    _write_contract(contract_path, bounded, active, approved=True)
    digest = questions_digest(stage.proposed_questions(bounded, active))
    baseline = {
        "questions_sha256": digest if question_hash == "current" else question_hash,
        "evaluation_config_sha256": config_hash,
    }
    plan = stage.build_plan(
        bounded, active, nodes, contract_path, config_sha256="test-models", baseline=baseline
    )
    assert plan["ready"] is True
    assert plan["ready_for_m3"] is False
    assert len(plan["baseline_reuse_errors"]) == 1
    baseline.update(questions_sha256=digest, evaluation_config_sha256="test-models")
    assert (
        stage.build_plan(
            bounded, active, nodes, contract_path, config_sha256="test-models", baseline=baseline
        )["ready_for_m3"]
        is True
    )


def test_absent_lookup_controls_and_duplicate_ids_are_rejected(benchmark: tuple) -> None:
    bounded, active, nodes, contract_path = benchmark
    for row in active[50:]:
        if row["slice"]["question_type"] == "lookup":
            row["slice"]["question_type"] = "procedure"
    active[-1]["id"] = bounded[0]["id"]
    plan = stage.build_plan(bounded, active, nodes, contract_path, config_sha256="test-models")
    assert plan["ready"] is False
    assert any("lookup 0" in error for error in plan["full_validation_errors"])
    assert any("duplicate" in error for error in plan["full_validation_errors"])


@pytest.mark.parametrize(
    "key,value", [("prepared_questions_sha256", "stale"), ("evidence_gain_points", 10)]
)
def test_prepared_fingerprint_and_thresholds_cannot_drift(
    benchmark: tuple, key: str, value: object
) -> None:
    bounded, active, nodes, contract_path = benchmark
    _approve(bounded)
    _write_contract(contract_path, bounded, active, approved=True)
    contract = json.loads(contract_path.read_text())
    contract[key] = value
    contract_path.write_text(json.dumps(contract))
    plan = stage.build_plan(bounded, active, nodes, contract_path, config_sha256="test-models")
    assert plan["ready"] is False
    assert plan["readiness_errors"]


def test_plan_cli_is_offline_rerunnable_and_preserves_all_source_files(
    benchmark: tuple, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bounded, active, nodes, contract_path = benchmark
    paths = {}
    for name, rows in (("bounded", bounded), ("active", active)):
        paths[name] = tmp_path / f"{name}.jsonl"
        paths[name].write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    nodes_dir = tmp_path / "nodes"
    nodes_dir.mkdir()
    node_file = nodes_dir / "nodes.jsonl"
    node_file.write_text(
        "\n".join(json.dumps({"node_id": key, "text": text}) for key, text in nodes.items())
    )
    protected = [*paths.values(), contract_path, node_file]
    snapshots = {path: path.read_bytes() for path in protected}
    output = tmp_path / "staging" / "plan.json"
    monkeypatch.setattr(stage, "configure_evaluation", lambda: None)
    monkeypatch.setattr(stage, "validate_evaluation_models", lambda: None)
    monkeypatch.setattr(stage, "evaluation_fingerprint", lambda: "test-models")

    def no_network(*_args: object, **_kwargs: object) -> None:
        pytest.fail("The staging command must not open a network connection")

    monkeypatch.setattr("socket.create_connection", no_network)
    args = [
        "--plan",
        "--bounded",
        str(paths["bounded"]),
        "--active",
        str(paths["active"]),
        "--contract",
        str(contract_path),
        "--nodes",
        str(nodes_dir),
        "--baseline-metrics",
        str(tmp_path / "missing-baseline.json"),
        "--output",
        str(output),
    ]
    assert stage.main(args) == 0  # Planning succeeds while readiness stays false.
    first_report = output.read_bytes()
    assert stage.main(args) == 0
    assert output.read_bytes() == first_report
    assert all(path.read_bytes() == content for path, content in snapshots.items())
    for path in protected:
        assert stage.main([*args[:-1], str(path)]) == 1
    assert all(path.read_bytes() == content for path, content in snapshots.items())
    report = json.loads(output.read_text())
    assert report["plan_only"] is True
    assert report["model_calls_made"] is report["activation_performed"] is False
