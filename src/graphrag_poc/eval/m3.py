"""Score baseline-plus-graph against the improved baseline and record the gates."""

import json
import math
import os
import sys
import time
from pathlib import Path

from graphrag_poc.eval.check import load_questions, validate
from graphrag_poc.eval.metrics import Ratio, SliceMetrics, evidence_hits, format_mrr, format_percent
from graphrag_poc.eval.score import (
    EVIDENCE_LIMIT,
    TYPE_ORDER,
    Judged,
    RunInfo,
    attempt_from_hits,
    metrics_by_type,
    retrieval_query,
    score_attempts,
    slice_metrics,
)
from graphrag_poc.graph.client import make_driver
from graphrag_poc.graph.config import GRAPH_WEIGHT, HOP_DEPTH, NODE_CAP
from graphrag_poc.retrieve.graph import retrieve_question
from graphrag_poc.retrieve.search import retrieve

ROOT = Path(__file__).resolve().parents[3]
BASELINE_METRICS = ROOT / "data" / "eval" / "metrics.json"
REPORT_PATH = ROOT / "docs" / "m3_report.md"
METRICS_PATH = ROOT / "data" / "eval" / "m3" / "metrics.json"
RESULTS_PATH = ROOT / "data" / "eval" / "m3" / "results.jsonl"
JUDGMENTS_PATH = ROOT / "data" / "eval" / "m3" / "judgments"
_TARGETS = ("relational", "multi_hop")


def main(argv: list[str] | None = None) -> int:
    from graphrag_poc.eval.score import _load_env_file

    _load_env_file()
    args = list(sys.argv[1:] if argv is None else argv)
    reproduce = args == ["--reproduce"]
    saved = None
    saved_metrics = None
    if reproduce and REPORT_PATH.exists():
        saved = REPORT_PATH.read_text(encoding="utf-8")
    if reproduce and METRICS_PATH.exists():
        saved_metrics = METRICS_PATH.read_text(encoding="utf-8")
    try:
        report, metrics = run_graph()
    except RuntimeError as exc:
        print(str(exc))
        return 1
    REPORT_PATH.write_text(report, encoding="utf-8")
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(metrics, encoding="utf-8")
    print(f"graph report written to {REPORT_PATH}")
    if reproduce and saved_metrics and not _same_metrics(saved_metrics, metrics):
        if saved is not None:
            REPORT_PATH.write_text(saved, encoding="utf-8")
        METRICS_PATH.write_text(saved_metrics, encoding="utf-8")
        print("graph metrics drifted from the saved report")
        return 1
    if reproduce and saved_metrics:
        print("reproduction check passed")
    return 0 if _gates_passed(report) else 1


def run_graph() -> tuple[str, str]:
    """Retrieve with the graph, judge, and render the before/after report."""

    from graphrag_poc.eval.judge import build_judge
    from graphrag_poc.index.client import make_client
    from graphrag_poc.index.embed import build_embedder

    records = load_questions()
    errors = validate(records)
    if errors:
        raise RuntimeError(errors[0])
    if not BASELINE_METRICS.exists():
        raise RuntimeError("the improved baseline metrics are missing")
    baseline = json.loads(BASELINE_METRICS.read_text(encoding="utf-8"))
    embedder = build_embedder()
    client = make_client(api_key=os.environ.get("QDRANT_API_KEY") or None)
    driver = make_driver()
    lookup_base: list[float] = []
    lookup_graph: list[float] = []
    attempts = []
    demo = ""
    try:
        for index, record in enumerate(records, start=1):
            question = retrieval_query(record)
            slice_ = record.get("slice")
            question_type = str(slice_.get("question_type", "")) if isinstance(slice_, dict) else ""
            started = time.perf_counter()
            retrieve(client, embedder, question)
            base_ms = (time.perf_counter() - started) * 1000
            started = time.perf_counter()
            hits, _decision, frame = retrieve_question(
                client,
                embedder,
                question,
                question_type=question_type,
                driver=driver,
            )
            graph_ms = (time.perf_counter() - started) * 1000
            if question_type == "lookup":
                lookup_base.append(base_ms)
                lookup_graph.append(graph_ms)
            attempt = attempt_from_hits(record, hits, question=question, frame=frame)
            attempts.append(attempt)
            if record.get("id") == "relational-0001":
                used = any("graph" in hit.channels for hit in hits[:EVIDENCE_LIMIT])
                demo = (
                    "relational-0001 asks which alternator part is listed for the charging fault.\n"
                    f"The graph channel is in the top {EVIDENCE_LIMIT}: {used}.\n"
                    f"Relation frame:\n{frame.text() or 'empty'}"
                )
            if index % 10 == 0 or index == len(records):
                print(f"retrieved {index} of {len(records)}", flush=True)
    finally:
        driver.close()
    judge = build_judge()
    rows, reused = score_attempts(attempts, judge, JUDGMENTS_PATH)
    print(f"judgments reused {reused} of {len(rows)}")
    info = RunInfo(
        embedding_model=os.environ.get("EMBEDDING_MODEL", ""),
        generation_model=os.environ.get("GENERATION_MODEL", "").strip(),
        judge=judge.name,
        temperature=attempts[0].temperature if attempts else 0.0,
        seed=attempts[0].seed if attempts else 0,
    )
    _write_results(rows)
    report = _render(info, rows, baseline, lookup_base, lookup_graph, demo)
    payload = {
        "embedding_model": info.embedding_model,
        "generation_model": info.generation_model,
        "judge": info.judge,
        "graph_weight": GRAPH_WEIGHT,
        "hop_depth": HOP_DEPTH,
        "node_cap": NODE_CAP,
        "lookup_p95_baseline_ms": _p95(lookup_base),
        "lookup_p95_graph_ms": _p95(lookup_graph),
        "by_type": {
            name: _metric_payload(metrics) for name, metrics in metrics_by_type(rows).items()
        },
    }
    return report, json.dumps(payload, indent=2) + "\n"


def _render(
    info: RunInfo,
    rows: list[Judged],
    baseline: dict[str, object],
    lookup_base: list[float],
    lookup_graph: list[float],
    demo: str,
) -> str:
    by_type = metrics_by_type(rows)
    overall = slice_metrics(rows)
    base_types = baseline.get("by_type")
    if not isinstance(base_types, dict):
        raise RuntimeError("baseline metrics have no by_type")
    evidence_before = _pooled(base_types, "evidence_recall")
    evidence_after = _pooled_rows(rows, "evidence")
    facts_before = _pooled(base_types, "required_fact_recall")
    facts_after = _pooled_rows(rows, "facts")
    lookup_delta = _p95(lookup_graph) - _p95(lookup_base)
    gates = [
        _gate(
            "relational and multi-hop evidence recall",
            _points(*evidence_after) - _points(*evidence_before),
            15,
        ),
        _gate(
            "relational and multi-hop required-fact recall",
            _points(*facts_after) - _points(*facts_before),
            10,
        ),
        _gate("lookup p95 latency", lookup_delta, 100, higher_is_better=False),
    ]
    for name in TYPE_ORDER:
        current = by_type.get(name)
        previous = base_types.get(name)
        if current is None or not isinstance(previous, dict):
            continue
        gates.append(_type_gate(name, "hit@10", current.hit_at_10, previous.get("hit_at_10")))
        gates.append(
            _type_gate(
                name,
                "required-fact recall",
                current.facts,
                previous.get("required_fact_recall"),
            )
        )
    lines = [
        "# Graph comparison",
        "",
        "The same 157 questions were scored with the improved baseline and with the graph.",
        f"Graph weight is {GRAPH_WEIGHT}. Hop depth is {HOP_DEPTH}. "
        f"The traversal cap is {NODE_CAP}.",
        "The reranker is off. Hit@10 still uses the first 10 fused passages.",
        "",
        "| Setting | Value |",
        "|---|---|",
        f"| Embedding model | {info.embedding_model} |",
        f"| Generation | {info.generation_model or 'passage text'} |",
        f"| Judge | {info.judge} |",
        f"| Graph weight | {GRAPH_WEIGHT} |",
        f"| Hop depth | {HOP_DEPTH} |",
        "",
        "## Scores with the graph",
        "",
        "| Question type | Questions | hit@10 | MRR | Evidence recall | Required-fact recall |",
        "|---|---:|---:|---:|---:|---:|",
        (
            f"| Overall | {overall.questions} | {format_percent(overall.hit_at_10)} | "
            f"{format_mrr(overall.mrr_denominators)} | {format_percent(overall.evidence)} | "
            f"{format_percent(overall.facts)} |"
        ),
    ]
    for name, metrics in by_type.items():
        lines.append(
            f"| {name} | {metrics.questions} | {format_percent(metrics.hit_at_10)} | "
            f"{format_mrr(metrics.mrr_denominators)} | {format_percent(metrics.evidence)} | "
            f"{format_percent(metrics.facts)} |"
        )
    lines.extend(
        [
            "",
            "## Gates",
            "",
            "| Gate | Change | Required | Result |",
            "|---|---:|---:|---|",
        ]
    )
    lines.extend(
        f"| {name} | {change:.1f} | {required:g} | {'pass' if passed else 'fail'} |"
        for name, change, required, passed in gates
    )
    lines.extend(["", "## Demonstration", "", demo, ""])
    return "\n".join(lines)


def _same_metrics(previous_text: str, current_text: str) -> bool:
    previous = json.loads(previous_text)
    current = json.loads(current_text)
    if not isinstance(previous, dict) or not isinstance(current, dict):
        return False
    return previous.get("by_type") == current.get("by_type")


def _type_gate(
    name: str,
    label: str,
    current: object,
    previous: object,
) -> tuple[str, float, float, bool]:
    if not isinstance(current, Ratio) or not isinstance(previous, dict):
        return (f"{name} {label}", 0.0, -1, True)
    numerator = previous.get("numerator")
    denominator = previous.get("denominator")
    if isinstance(numerator, bool) or isinstance(denominator, bool):
        return (f"{name} {label}", 0.0, -1, True)
    if not isinstance(numerator, int) or not isinstance(denominator, int):
        return (f"{name} {label}", 0.0, -1, True)
    before = _points(numerator, denominator)
    after = _points(current.numerator, current.denominator)
    change = after - before
    return (f"{name} {label}", change, -1, change >= -1)


def _gate(
    name: str,
    change: float,
    required: float,
    *,
    higher_is_better: bool = True,
) -> tuple[str, float, float, bool]:
    if higher_is_better:
        return (name, change, required, change >= required)
    return (name, change, required, change <= required)


def _pooled(by_type: dict[str, object], key: str) -> tuple[int, int]:
    numerator = denominator = 0
    for name in _TARGETS:
        metrics = by_type.get(name)
        if not isinstance(metrics, dict):
            continue
        ratio = metrics.get(key)
        if not isinstance(ratio, dict):
            continue
        numerator += int(ratio["numerator"])
        denominator += int(ratio["denominator"])
    return numerator, denominator


def _pooled_rows(rows: list[Judged], field: str) -> tuple[int, int]:
    numerator = denominator = 0
    for row in rows:
        if row.question_type not in _TARGETS:
            continue
        if field == "evidence":
            denominator += len(row.attempt.gold_ids)
            numerator += evidence_hits(row.attempt.gold_ids, row.attempt.evidence_ids)
        else:
            denominator += len(row.attempt.required_facts)
            numerator += sum(1 for fact in row.judgment.facts if fact.present)
    return numerator, denominator


def _metric_payload(metrics: SliceMetrics) -> dict[str, dict[str, int]]:
    return {
        "hit_at_10": _ratio(metrics.hit_at_10),
        "evidence_recall": _ratio(metrics.evidence),
        "required_fact_recall": _ratio(metrics.facts),
    }


def _ratio(ratio: Ratio) -> dict[str, int]:
    return {"numerator": ratio.numerator, "denominator": ratio.denominator}


def _points(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return 100.0 * numerator / denominator


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)]


def _gates_passed(report: str) -> bool:
    return all("| fail |" not in line for line in report.splitlines() if line.startswith("| "))


def _write_results(rows: list[Judged]) -> None:
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for row in rows:
        lines.append(
            json.dumps(
                {
                    "id": row.attempt.id,
                    "question_type": row.question_type,
                    "evidence_ids": list(row.attempt.evidence_ids),
                    "missing_gold": [
                        node_id
                        for node_id in row.attempt.gold_ids
                        if node_id not in row.attempt.evidence_ids
                    ],
                },
                ensure_ascii=False,
            )
        )
    RESULTS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
