"""Bounded live model checks using supplied passages, without retrieval or acceptance scoring."""

import argparse
import hashlib
import json
import platform
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from graphrag_poc.eval.config import (
    configure_evaluation,
    evaluation_fingerprint,
    validate_evaluation_models,
)
from graphrag_poc.eval.gold import load_nodes
from graphrag_poc.eval.judge import LanguageModelJudge
from graphrag_poc.generate.answer import clip_for_model
from graphrag_poc.generate.config import ModelSettings, fingerprint, model_settings
from graphrag_poc.generate.model import model_answer
from graphrag_poc.models import Node
from graphrag_poc.retrieve.fusion import FusedHit

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = ROOT / "data/eval/model_smoke"
SMOKE_PROTOCOL = "supplied-evidence-smoke-v1"
OIL_FACT = "Engine oil level is checked with engine off."
BULB_FACT = (
    "When changing light bulbs, ensure the system in which the bulb is being replaced "
    "is turned off."
)
UNSUPPORTED_FACT = "The manual specifies purple oil."


@dataclass(frozen=True)
class SmokeCase:
    id: str
    question: str
    node_ids: tuple[str, ...]
    required_facts: tuple[str, ...]
    expected_refusal: bool = False


CASES = (
    SmokeCase(
        "oil-level",
        "Should I check the engine oil level with the engine running or stopped?",
        ("tm280_10:3-17:step-a:2:note",),
        (OIL_FACT,),
    ),
    SmokeCase(
        "bulb-warning",
        "One ceiling light in the ambulance has failed. If inspection shows it needs a bulb, "
        "what must be turned off before changing it?",
        ("tm280_10:table:3-1:6:r28", "tm280_10:3-28:step-a:2:caution"),
        (BULB_FACT,),
    ),
    SmokeCase(
        "insufficient-evidence",
        "What is the tightening torque for part ZZ-NO-SUCH-PART?",
        ("tm280_10:3-17:step-a:2:note",),
        (),
        expected_refusal=True,
    ),
)


def _hits(case: SmokeCase, nodes: dict[str, Node]) -> list[FusedHit]:
    hits = []
    for rank, node_id in enumerate(case.node_ids, 1):
        if node_id not in nodes:
            raise RuntimeError(f"Smoke source missing: {node_id}")
        node = nodes[node_id]
        hits.append(
            FusedHit(
                node.node_id,
                node.text,
                node.lang,
                node.page_start,
                node.page_end,
                node.doc_key,
                node.type,
                ("supplied_smoke_evidence",),
                rank,
                0.0,
            )
        )
    if any(
        not any(fact in clip_for_model(hit.text) for hit in hits) for fact in case.required_facts
    ):
        raise RuntimeError(f"{case.id}: required fact missing from supplied model context")
    return hits


def safe_endpoint(url: str) -> str:
    """Display a connection destination without user-info, query parameters or fragments."""

    parsed = urlsplit(url)
    host = parsed.hostname or ""
    if ":" in host:
        host = f"[{host}]"
    port = f":{parsed.port}" if parsed.port is not None else ""
    return f"{parsed.scheme}://{host}{port}{parsed.path.rstrip('/')}"


def hardware() -> dict[str, object]:
    result: dict[str, object] = {"os": platform.system(), "architecture": platform.machine()}
    if platform.system() == "Darwin":
        for name, key in (("hw.memsize", "memory_bytes"), ("machdep.cpu.brand_string", "cpu")):
            value = subprocess.run(
                ["sysctl", "-n", name],
                capture_output=True,
                text=True,
                check=False,
            )
            if value.returncode == 0:
                text = value.stdout.strip()
                result[key] = int(text) if key == "memory_bytes" else text
    return result


def _error(exc: Exception) -> str:
    """SDK error bodies can echo credentials or URLs; report only class/status."""

    if isinstance(exc, RuntimeError):
        return str(exc)
    status = getattr(exc, "status_code", None)
    return f"{type(exc).__name__}" + (f" (HTTP {status})" if isinstance(status, int) else "")


def _list_models(settings: ModelSettings, timeout: float) -> list[str]:
    from openai import OpenAI

    with OpenAI(
        base_url=settings.base_url,
        api_key=settings.api_key or "not-needed",
        timeout=timeout,
        max_retries=0,
    ) as client:
        return [model.id for model in client.models.list().data]


def probe_models(timeout: float = 5.0) -> list[dict[str, object]]:
    """GET /models only. Finish all probes before permitting any chat request."""

    results: list[dict[str, object]] = []
    # One model-list request when both roles share an endpoint and credential.
    listings: dict[tuple[str, str], list[str] | Exception] = {}
    roles: tuple[Literal["GENERATION", "JUDGE"], ...] = ("GENERATION", "JUDGE")
    for role in roles:
        settings = model_settings(role)
        key = (settings.base_url.rstrip("/"), settings.api_key)
        if key not in listings:
            try:
                listings[key] = _list_models(settings, timeout)
            except Exception as exc:
                listings[key] = exc
        listing = listings[key]
        row: dict[str, object] = {
            "role": role.lower(),
            "model": settings.model,
            "endpoint": safe_endpoint(settings.base_url),
        }
        if isinstance(listing, Exception):
            row.update(status="unavailable", error=_error(listing))
        else:
            row.update(
                status="ready" if settings.model in listing else "model_not_listed",
                available_model_ids=listing,
            )
        results.append(row)
    return results


def plan(cases: tuple[SmokeCase, ...], nodes: dict[str, Node]) -> dict[str, object]:
    case_rows = []
    for case in cases:
        hits = _hits(case, nodes)
        case_rows.append(
            {
                **asdict(case),
                "passages": [
                    {
                        "node_id": h.node_id,
                        "page": h.page_start,
                        "text_sha256": hashlib.sha256(h.text.encode()).hexdigest(),
                        "shown_text": clip_for_model(h.text),
                    }
                    for h in hits
                ],
            }
        )
    return {
        "protocol": SMOKE_PROTOCOL,
        "purpose": "model smoke test only; not M3 acceptance",
        "evaluation_config_sha256": evaluation_fingerprint(),
        "max_generation_requests": len(cases),
        "max_judge_requests": 1 + sum(not case.expected_refusal for case in cases),
        "cache_policy": "live run bypasses generator and judge caches",
        "failure_policy": "stop on first failure; no SDK automatic retries",
        "cases": case_rows,
        "smoke_inputs_sha256": fingerprint(case_rows),
    }


def run_suite(cases: tuple[SmokeCase, ...], nodes: dict[str, Node]) -> dict[str, object]:
    """At most six chat requests for the default suite, stopping at the first failure."""

    # Validate every source before the first paid request, including direct Python callers.
    prepared = [_hits(case, nodes) for case in cases]
    judge = LanguageModelJudge()
    probe = judge.judge(
        answer="Check the oil level with the engine stopped. " + UNSUPPORTED_FACT,
        facts=(OIL_FACT, UNSUPPORTED_FACT),
        cited_texts=(OIL_FACT,),
    )
    calibration_ok = tuple(f.present for f in probe.facts) == (True, False) and tuple(
        c.supported for c in probe.claims
    ) == (True, False)
    report: dict[str, object] = {
        "status": "failed",
        "judge_calibration": asdict(probe),
        "judge_calibration_passed": calibration_ok,
        "cases": [],
    }
    if not calibration_ok:
        report["reason"] = (
            "Judge must accept the supported paraphrase and reject the invented claim."
        )
        return report
    case_rows: list[dict[str, object]] = []
    report["cases"] = case_rows
    for case, hits in zip(cases, prepared, strict=True):
        row: dict[str, object] = {"id": case.id, "passed": False}
        case_rows.append(row)
        try:
            answer = model_answer(case.question, hits, use_cache=False)
        except Exception as exc:
            row["error"] = _error(exc)
            return report
        row["answer"] = asdict(answer)
        if answer.refused != case.expected_refusal:
            row["reason"] = "Answer/refusal decision differs from the supplied-evidence case."
            return report
        if case.expected_refusal:
            row["passed"] = not answer.citations
        elif not answer.citations:
            row["reason"] = "Model supplied no valid citations; no fallback is allowed."
            return report
        else:
            cited = {citation.node_id for citation in answer.citations}
            try:
                judgment = judge.judge(
                    answer=answer.text,
                    facts=case.required_facts,
                    cited_texts=tuple(hit.text for hit in hits if hit.node_id in cited),
                )
            except Exception as exc:
                row["error"] = _error(exc)
                return report
            row["judgment"] = asdict(judgment)
            row["passed"] = (
                bool(judgment.facts)
                and all(f.present for f in judgment.facts)
                and bool(judgment.claims)
                and all(c.supported for c in judgment.claims)
            )
            if not row["passed"]:
                row["reason"] = "Required facts or answer claims are unsupported by the cited text."
        if not row["passed"]:
            return report
    report["status"] = "passed"
    return report


def _write_report(report: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true", help="Validate inputs; no endpoint calls.")
    mode.add_argument("--probe", action="store_true", help="List served models; no inference.")
    mode.add_argument("--run", action="store_true", help="Run bounded LIVE model inference.")
    parser.add_argument("--limit", type=int, choices=(1, 2, 3), default=3)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args(argv)
    configure_evaluation()
    report: dict[str, object] = {
        "observed_at": datetime.now(UTC).isoformat(),
        "purpose": "model smoke test only; not M3 acceptance",
        "hardware": hardware(),
    }
    filename = "plan.json" if args.plan else "readiness.json" if args.probe else "results.json"
    path = args.output_dir / filename
    try:
        validate_evaluation_models()
        cases = CASES[: args.limit]
        if args.plan or args.run:
            nodes = load_nodes()
            report["plan"] = plan(cases, nodes)
        if args.plan:
            report["status"] = "planned_no_endpoint_calls"
        else:
            endpoints = probe_models()
            report["endpoints"] = endpoints
            if any(row["status"] != "ready" for row in endpoints):
                report.update(status="blocked", reason="Configured models are not both available.")
            elif args.probe:
                report["status"] = "endpoints_ready_inference_not_tested"
            else:
                report.update(run_suite(cases, nodes))
    except Exception as exc:
        report.update(status="failed", error=_error(exc))
    _write_report(report, path)
    print(f"Model smoke status: {report['status']}. Report: {path}")
    if report["status"] == "failed":
        if report.get("error") or report.get("reason"):
            print(f"Failure: {report.get('error') or report.get('reason')}")
        rows = report.get("cases", [])
        if isinstance(rows, list):
            for row in rows:
                if not row.get("passed"):
                    detail = row.get("error") or row.get("reason") or "Check failed."
                    print(f"{row['id']}: {detail}")
                    break
    if args.plan:
        print("No endpoint calls made. Default suite: at most 3 generator + 3 judge requests.")
    else:
        shown_endpoints = report.get("endpoints", [])
        if isinstance(shown_endpoints, list):
            for row in shown_endpoints:
                print(f"{row['role']}: {row['model']} at {row['endpoint']}: {row['status']}")
        if args.probe or report["status"] == "blocked":
            print("No inference calls made.")
    return (
        0
        if report["status"]
        in {"passed", "planned_no_endpoint_calls", "endpoints_ready_inference_not_tested"}
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
