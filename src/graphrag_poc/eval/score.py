"""Score the evaluation set with the Step 6 baseline and write the report."""

import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from graphrag_poc.eval.check import load_questions, validate
from graphrag_poc.eval.judge import (
    Judge,
    Judgment,
    build_judge,
    judgment_from_payload,
)
from graphrag_poc.eval.metrics import (
    Ratio,
    SliceMetrics,
    evidence_hits,
    first_gold_rank,
    format_mrr,
    format_percent,
)
from graphrag_poc.generate.__main__ import compose_answer
from graphrag_poc.generate.answer import _requested_label
from graphrag_poc.retrieve.fusion import RRF_K, FusedHit

ROOT = Path(__file__).resolve().parents[3]
REPORT_PATH = ROOT / "docs" / "baseline_report.md"
METRICS_PATH = ROOT / "data" / "eval" / "metrics.json"
RESULTS_PATH = ROOT / "data" / "eval" / "results.jsonl"
JUDGMENTS_DIR = ROOT / "data" / "eval" / "judgments"
EVIDENCE_LIMIT = 10
TYPE_ORDER = (
    "lookup",
    "procedure",
    "applicability",
    "relational",
    "multi_hop",
    "troubleshooting",
    "follow_up",
    "unanswerable",
)


@dataclass(frozen=True)
class Attempt:
    """One question after retrieval and generation, before judging."""

    id: str
    question_type: str
    language: str
    expected_action: str
    gold_ids: tuple[str, ...]
    ranked_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    answer_text: str
    refused: bool
    citation_ids: tuple[str, ...]
    cited_texts: tuple[str, ...]
    required_facts: tuple[str, ...]
    temperature: float
    seed: int
    looks_like_title: bool = False
    label_overshoot: bool = False


@dataclass(frozen=True)
class Judged:
    attempt: Attempt
    judgment: Judgment

    @property
    def question_type(self) -> str:
        return self.attempt.question_type


@dataclass(frozen=True)
class RunInfo:
    embedding_model: str
    generation_model: str
    judge: str
    temperature: float
    seed: int
    rrf_k: int = RRF_K
    evidence_limit: int = EVIDENCE_LIMIT


def retrieval_query(record: dict[str, object]) -> str:
    """The string the retriever sees. Follow-up questions include the earlier turn."""

    turns = record.get("turns")
    if isinstance(turns, list):
        parts: list[str] = []
        for turn in turns:
            if isinstance(turn, dict) and str(turn.get("role", "")) == "user":
                text = str(turn.get("text") or "").strip()
                if text:
                    parts.append(text)
        if parts:
            return "\n".join(parts)
    return str(record.get("question") or "")


def label_overshoots(question: str, evidence_texts: tuple[str, ...]) -> bool:
    """True when the title read from the question includes text that follows the title."""

    label = _requested_label(question)
    if not label or _in_any(label, evidence_texts):
        return False
    trimmed = _title_without_tail(label)
    if trimmed == label:
        return False
    return _in_any(trimmed, evidence_texts)


def looks_like_title(question: str) -> bool:
    return _requested_label(question) is not None


def _title_without_tail(label: str) -> str:
    """Drop the comma or the next capital that the title reader consumes."""

    trimmed = label.strip()
    if trimmed.endswith(","):
        trimmed = trimmed[:-1].rstrip()
    if (
        len(trimmed) >= 4
        and trimmed[-3] == "."
        and trimmed[-2] == " "
        and trimmed[-1].isascii()
        and trimmed[-1].isupper()
    ):
        trimmed = trimmed[:-3].rstrip()
    return trimmed


def _in_any(needle: str, texts: tuple[str, ...]) -> bool:
    folded = needle.lower()
    return any(folded in text.lower() for text in texts)


def attempt_from_hits(
    record: dict[str, object],
    hits: list[FusedHit],
    *,
    question: str,
) -> Attempt:
    """Give the generator the first ten fused passages and keep the full ranking."""

    evidence = hits[:EVIDENCE_LIMIT]
    answer = compose_answer(question, evidence)
    cited = {hit.node_id: hit.text for hit in evidence}
    citation_ids = tuple(citation.node_id for citation in answer.citations)
    return Attempt(
        id=str(record.get("id", "")),
        question_type=_question_type(record),
        language=_language(record),
        expected_action=str(record.get("expected_action", "")),
        gold_ids=_gold_ids(record),
        ranked_ids=tuple(hit.node_id for hit in hits),
        evidence_ids=tuple(hit.node_id for hit in evidence),
        answer_text=answer.text,
        refused=answer.refused,
        citation_ids=citation_ids,
        cited_texts=tuple(cited[node_id] for node_id in citation_ids if node_id in cited),
        required_facts=_fact_texts(record),
        temperature=answer.temperature,
        seed=answer.seed,
        looks_like_title=looks_like_title(question),
        label_overshoot=label_overshoots(question, tuple(hit.text for hit in evidence)),
    )


def judge_attempt(attempt: Attempt, judge: Judge, cache_dir: Path) -> tuple[Judgment, bool]:
    """Return the judgment and whether it was read from the cache."""

    digest = _digest(attempt)
    path = cache_dir / f"{_safe_id(attempt.id)}.json"
    cached = _read_cache(path, digest=digest, judge_name=judge.name)
    if cached is not None:
        return cached, True
    judgment = judge.judge(
        answer=attempt.answer_text,
        facts=attempt.required_facts,
        cited_texts=attempt.cited_texts,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = judgment.to_dict(question_id=attempt.id, answer_sha256=digest)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return judgment, False


def slice_metrics(rows: list[Judged]) -> SliceMetrics:
    """Pool the section 9 definitions. Blank ratios have a zero denominator."""

    hit_num = hit_den = 0
    evidence_num = evidence_den = 0
    fact_num = fact_den = 0
    claim_num = claim_den = 0
    action_num = 0
    denominators: list[int] = []
    for row in rows:
        attempt = row.attempt
        if attempt.gold_ids:
            hit_den += 1
            evidence_den += len(attempt.gold_ids)
            found = evidence_hits(attempt.gold_ids, attempt.evidence_ids)
            evidence_num += found
            if found:
                hit_num += 1
            denominators.append(first_gold_rank(attempt.gold_ids, attempt.ranked_ids))
        if attempt.required_facts:
            fact_den += len(attempt.required_facts)
            fact_num += sum(1 for fact in row.judgment.facts if fact.present)
        if attempt.expected_action == "answer":
            claim_den += len(row.judgment.claims)
            claim_num += sum(1 for claim in row.judgment.claims if claim.supported)
        predicted = "refuse" if attempt.refused else "answer"
        if predicted == attempt.expected_action:
            action_num += 1
    return SliceMetrics(
        questions=len(rows),
        hit_at_10=Ratio(hit_num, hit_den),
        mrr_denominators=tuple(denominators),
        evidence=Ratio(evidence_num, evidence_den),
        facts=Ratio(fact_num, fact_den),
        claims=Ratio(claim_num, claim_den),
        actions=Ratio(action_num, len(rows)),
    )


def metrics_by_type(rows: list[Judged]) -> dict[str, SliceMetrics]:
    present = {row.question_type for row in rows}
    ordered = [name for name in TYPE_ORDER if name in present]
    ordered.extend(sorted(present.difference(TYPE_ORDER)))
    return {
        name: slice_metrics([row for row in rows if row.question_type == name]) for name in ordered
    }


def render_report(info: RunInfo, rows: list[Judged]) -> str:
    """Baseline report: models, fusion, per-type scores, and the relational misses."""

    by_type = metrics_by_type(rows)
    overall = slice_metrics(rows)
    lines = [
        "# Baseline report",
        "",
        "The Step 6 retriever scored every question in `data/eval/questions.jsonl`.",
        "Dense and sparse lists are merged with reciprocal rank fusion.",
        f"The generator receives the first {info.evidence_limit} fused passages.",
        "The reranker is off.",
        "The malfunction title is read without the following word. This is the improved baseline.",
        "",
        "| Setting | Value |",
        "|---|---|",
        f"| Embedding model | {info.embedding_model} |",
        f"| Generation | {_generation_label(info)} |",
        f"| Judge | {_judge_label(info)} |",
        f"| Fusion | RRF k={info.rrf_k}, dense + sparse |",
        f"| Evidence size | {info.evidence_limit} |",
        f"| Temperature | {info.temperature:g} |",
        f"| Seed | {info.seed} |",
        "",
        "## Scores",
        "",
        _table_header(),
        _table_row("Overall", overall),
    ]
    for name, metrics in by_type.items():
        lines.append(_table_row(name, metrics))
    lines.extend(["", _coverage_note(overall, by_type), ""])
    lines.extend(["## Relational questions the baseline misses", ""])
    lines.append(relational_note(rows))
    lines.append("")
    for note in (applicability_note(rows), refusal_note(rows)):
        if note:
            lines.extend([note, ""])
    lines.extend([_japanese_note(rows), ""])
    return "\n".join(lines)


def relational_note(rows: list[Judged]) -> str:
    """Say which relational gold passages the top 10 missed, and which answers dropped a fact."""

    relational = [row for row in rows if row.question_type == "relational"]
    if not relational:
        return "This set has no relational questions."
    part_only: list[Judged] = []
    other_miss: list[Judged] = []
    dropped: list[Judged] = []
    for row in relational:
        missing = _missing_gold(row)
        parts = [node_id for node_id in missing if node_id.startswith("tm280_24p_1")]
        if missing and parts and len(parts) == len(missing):
            part_only.append(row)
        elif missing:
            other_miss.append(row)
        elif any(not fact.present for fact in row.judgment.facts):
            dropped.append(row)
    retrieved = len(relational) - len(part_only) - len(other_miss)
    sentences = [
        (
            f"Of {len(relational)} relational questions, "
            f"{len(part_only) + len(other_miss)} did not place every gold passage "
            f"in the {EVIDENCE_LIMIT} passages given to the generator."
        )
    ]
    if part_only:
        sentences.append(
            f"{len(part_only)} of those kept the malfunction row and missed the parts-list row."
        )
    if other_miss:
        sentences.append(f"{len(other_miss)} missed some other gold passage.")
    if dropped:
        sentences.append(
            f"{len(dropped)} placed every gold passage in that set, "
            "but the answer left out a required fact. "
            "The answer is taken from the passages it cites, "
            "and those citations did not include every gold passage."
        )
    complete = retrieved - len(dropped)
    sentences.append(
        f"{complete} relational questions had every gold passage in the evidence set "
        "and every required fact in the answer."
    )
    examples = _examples(part_only or other_miss or dropped)
    if examples:
        sentences.append("Examples: " + "; ".join(examples) + ".")
    overshoot = _overshoot_sentence(rows)
    if overshoot:
        sentences.append(overshoot)
    return " ".join(sentences)


def applicability_note(rows: list[Judged]) -> str:
    """Model tokens can be quoted from a passage that is not the gold passage."""

    credited = [
        row
        for row in rows
        if row.question_type == "applicability"
        and _missing_gold(row)
        and any(fact.present for fact in row.judgment.facts)
    ]
    if not credited:
        return ""
    return (
        f"On {len(credited)} applicability questions the required fact is a model token "
        "found in a cited passage other than the gold passage. "
        "Required-fact recall for that type is therefore higher than hit@10."
    )


def refusal_note(rows: list[Judged]) -> str:
    """Unanswerable questions are refused when they read as a missing malfunction title."""

    unanswerable = [row for row in rows if row.question_type == "unanswerable"]
    if not unanswerable:
        return ""
    refused = [row for row in unanswerable if row.attempt.refused]
    titled = [row for row in refused if row.attempt.looks_like_title]
    quoted = len(unanswerable) - len(refused)
    sentence = f"{len(refused)} of {len(unanswerable)} unanswerable questions were refused."
    if titled:
        sentence += (
            f" {len(titled)} of those read as a malfunction title that is not in the "
            "retrieved passages."
        )
    if quoted:
        sentence += (
            f" The other {quoted} do not read as a title, so the answerer quotes a "
            "retrieved passage."
        )
    return sentence


def _overshoot_sentence(rows: list[Judged]) -> str:
    counted: list[str] = []
    for name in ("relational", "lookup", "multi_hop"):
        total = sum(1 for row in rows if row.question_type == name and row.attempt.label_overshoot)
        if total:
            counted.append(f"{total} {name.replace('_', '-')} questions")
    if not counted:
        return ""
    listed = counted[0] if len(counted) == 1 else ", ".join(counted[:-1]) + ", and " + counted[-1]
    return (
        "The answerer refused questions whose retrieved passages contain the malfunction "
        f"title: {listed}. The title string it read from the question also included "
        "the comma or the next word, and that longer string is not in the passage."
    )


def write_outputs(
    info: RunInfo,
    rows: list[Judged],
    *,
    report_path: Path,
    metrics_path: Path,
    results_path: Path,
) -> str:
    report = render_report(info, rows)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(_metrics_json(info, rows), encoding="utf-8")
    lines = [_result_line(row) for row in rows]
    results_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def score_attempts(
    attempts: list[Attempt],
    judge: Judge,
    cache_dir: Path,
) -> tuple[list[Judged], int]:
    """Judge each attempt. The returned count is the number of cache hits."""

    rows: list[Judged] = []
    reused = 0
    for attempt in attempts:
        judgment, from_cache = judge_attempt(attempt, judge, cache_dir)
        reused += int(from_cache)
        rows.append(Judged(attempt, judgment))
    return rows, reused


def run_baseline(
    *,
    questions: list[dict[str, object]] | None = None,
    judge: Judge | None = None,
    cache_dir: Path | None = None,
    report_path: Path | None = None,
    metrics_path: Path | None = None,
    results_path: Path | None = None,
    embedding_model: str | None = None,
) -> str:
    """Retrieve, answer, judge, and write the baseline report."""

    records = questions if questions is not None else load_questions()
    errors = validate(records)
    if errors:
        raise RuntimeError(errors[0])
    active_judge = judge if judge is not None else build_judge()
    attempts = _retrieve_all(records)
    rows, reused = score_attempts(attempts, active_judge, cache_dir or JUDGMENTS_DIR)
    info = RunInfo(
        embedding_model=embedding_model or os.environ.get("EMBEDDING_MODEL", ""),
        generation_model=os.environ.get("GENERATION_MODEL", "").strip(),
        judge=active_judge.name,
        temperature=attempts[0].temperature if attempts else 0.0,
        seed=attempts[0].seed if attempts else 0,
    )
    report = write_outputs(
        info,
        rows,
        report_path=report_path or REPORT_PATH,
        metrics_path=metrics_path or METRICS_PATH,
        results_path=results_path or RESULTS_PATH,
    )
    print(f"judgments reused {reused} of {len(rows)}")
    print(f"baseline report written to {report_path or REPORT_PATH}")
    return report


def _retrieve_all(records: list[dict[str, object]]) -> list[Attempt]:
    from graphrag_poc.index.client import make_client
    from graphrag_poc.index.embed import build_embedder
    from graphrag_poc.retrieve.search import retrieve

    embedder = build_embedder()
    client = make_client(api_key=os.environ.get("QDRANT_API_KEY") or None)
    attempts: list[Attempt] = []
    for index, record in enumerate(records, start=1):
        question = retrieval_query(record)
        hits = retrieve(client, embedder, question)
        attempts.append(attempt_from_hits(record, hits, question=question))
        if index % 10 == 0 or index == len(records):
            print(f"scored {index} of {len(records)}", file=sys.stderr)
    return attempts


def _metrics_json(info: RunInfo, rows: list[Judged]) -> str:
    by_type = metrics_by_type(rows)
    payload = {
        "embedding_model": info.embedding_model,
        "generation_model": info.generation_model,
        "judge": info.judge,
        "rrf_k": info.rrf_k,
        "evidence_limit": info.evidence_limit,
        "rerank": False,
        "temperature": info.temperature,
        "seed": info.seed,
        "overall": _slice_payload(slice_metrics(rows)),
        "by_type": {name: _slice_payload(metrics) for name, metrics in by_type.items()},
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _slice_payload(metrics: SliceMetrics) -> dict[str, object]:
    return {
        "questions": metrics.questions,
        "hit_at_10": _ratio_payload(metrics.hit_at_10),
        "mrr_denominators": list(metrics.mrr_denominators),
        "evidence_recall": _ratio_payload(metrics.evidence),
        "required_fact_recall": _ratio_payload(metrics.facts),
        "claim_precision": _ratio_payload(metrics.claims),
        "action_accuracy": _ratio_payload(metrics.actions),
    }


def _ratio_payload(ratio: Ratio) -> dict[str, int]:
    return {"numerator": ratio.numerator, "denominator": ratio.denominator}


def _result_line(row: Judged) -> str:
    attempt = row.attempt
    payload = {
        "id": attempt.id,
        "question_type": attempt.question_type,
        "language": attempt.language,
        "expected_action": attempt.expected_action,
        "refused": attempt.refused,
        "first_gold_rank": first_gold_rank(attempt.gold_ids, attempt.ranked_ids),
        "missing_gold": _missing_gold(row),
        "facts_present": sum(1 for fact in row.judgment.facts if fact.present),
        "facts_required": len(attempt.required_facts),
        "claims_supported": sum(1 for claim in row.judgment.claims if claim.supported),
        "claims_shown": len(row.judgment.claims),
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _missing_gold(row: Judged) -> list[str]:
    evidence = set(row.attempt.evidence_ids)
    return [node_id for node_id in row.attempt.gold_ids if node_id not in evidence]


def _examples(rows: list[Judged]) -> list[str]:
    shown: list[str] = []
    for row in rows[:3]:
        missing = _missing_gold(row)
        absent = [fact.text for fact in row.judgment.facts if not fact.present]
        if missing:
            shown.append(f"{row.attempt.id} missed {missing[0]}")
        elif absent:
            shown.append(f"{row.attempt.id} omitted {absent[0]}")
    return shown


def _table_header() -> str:
    return (
        "| Question type | Questions | hit@10 | MRR | Evidence recall | "
        "Required-fact recall | Claim precision | Action accuracy |"
        "\n|---|---:|---:|---:|---:|---:|---:|---:|"
    )


def _table_row(name: str, metrics: SliceMetrics) -> str:
    return (
        f"| {name} | {metrics.questions} | {format_percent(metrics.hit_at_10)} | "
        f"{format_mrr(metrics.mrr_denominators)} | {format_percent(metrics.evidence)} | "
        f"{format_percent(metrics.facts)} | {format_percent(metrics.claims)} | "
        f"{format_percent(metrics.actions)} |"
    )


def _coverage_note(overall: SliceMetrics, by_type: dict[str, SliceMetrics]) -> str:
    gold_questions = overall.hit_at_10.denominator
    unanswerable = by_type.get("unanswerable")
    refused = unanswerable.questions if unanswerable is not None else 0
    return (
        "hit@10, MRR, and evidence recall cover the "
        f"{gold_questions} questions that have a gold passage. "
        f"The {refused} unanswerable questions have none, so those three cells are blank. "
        "Required-fact recall divides facts judged present, each with a quote from a cited "
        "passage, by the facts required. Claim precision divides supported sentences by the "
        "sentences shown. Both cover answerable questions. "
        "Action accuracy covers every question: a refusal for an unanswerable question, "
        "and an answer for every other expected action. "
        "Shares are percentages. MRR is the mean of 1/rank."
    )


def _japanese_note(rows: list[Judged]) -> str:
    japanese = [row for row in rows if row.attempt.language == "ja"]
    if not japanese:
        return "This run has no Japanese questions."
    with_gold = [row for row in japanese if row.attempt.gold_ids]
    documents = sorted(
        {node_id.split(":", 1)[0] for row in with_gold for node_id in row.attempt.gold_ids}
    )
    listed = ", ".join(documents) if documents else "no gold document"
    return (
        f"{len(japanese)} questions are Japanese. "
        f"{len(with_gold)} of them have gold passages in {listed}."
    )


def _generation_label(info: RunInfo) -> str:
    if info.generation_model:
        return info.generation_model
    return "none; the answer is the text of the cited passages"


def _judge_label(info: RunInfo) -> str:
    if info.judge == "quote":
        return (
            "quote check, because JUDGE_MODEL is empty. "
            "A fact or sentence counts only when its quote is an exact span of a cited passage. "
            "Set JUDGE_MODEL to use the language-model judge; the same quote rule still applies."
        )
    return (
        f"language model {info.judge}. "
        "A positive judgment counts only when its quote is an exact span of a cited passage."
    )


def _digest(attempt: Attempt) -> str:
    body = attempt.answer_text + "\n" + "\n".join(attempt.citation_ids)
    return hashlib.sha256(body.encode()).hexdigest()


def _safe_id(question_id: str) -> str:
    if not question_id or "/" in question_id or "\\" in question_id or question_id.startswith("."):
        raise ValueError(f"unsafe question id {question_id!r}")
    return question_id


def _read_cache(path: Path, *, digest: str, judge_name: str) -> Judgment | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("answer_sha256") != digest or payload.get("judge") != judge_name:
        return None
    return judgment_from_payload(payload, judge=judge_name)


def _question_type(record: dict[str, object]) -> str:
    slice_ = record.get("slice")
    if isinstance(slice_, dict):
        return str(slice_.get("question_type", ""))
    return ""


def _language(record: dict[str, object]) -> str:
    slice_ = record.get("slice")
    if isinstance(slice_, dict):
        return str(slice_.get("language", ""))
    return ""


def _gold_ids(record: dict[str, object]) -> tuple[str, ...]:
    gold = record.get("gold")
    if not isinstance(gold, dict):
        return ()
    node_ids = gold.get("node_ids")
    if not isinstance(node_ids, list):
        return ()
    return tuple(str(node_id) for node_id in node_ids)


def _fact_texts(record: dict[str, object]) -> tuple[str, ...]:
    facts = record.get("required_facts")
    if not isinstance(facts, list):
        return ()
    texts: list[str] = []
    for fact in facts:
        if isinstance(fact, dict):
            texts.append(str(fact.get("text", "")))
    return tuple(texts)


def _load_env_file() -> None:
    path = Path(".env")
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    _load_env_file()
    try:
        run_baseline()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0
