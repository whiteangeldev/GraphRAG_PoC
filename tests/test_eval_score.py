"""Baseline metrics, the quote judge, and cache reuse."""

import json
from pathlib import Path

from pytest import MonkeyPatch

from graphrag_poc.eval.judge import QuoteJudge, sentences, verify_model_judgment
from graphrag_poc.eval.metrics import format_mrr, format_percent
from graphrag_poc.eval.score import (
    Attempt,
    Judged,
    RunInfo,
    attempt_from_hits,
    label_overshoots,
    render_report,
    retrieval_query,
    score_attempts,
    slice_metrics,
    write_outputs,
)
from graphrag_poc.retrieve.fusion import FusedHit


def _attempt(
    *,
    qid: str = "lookup-0001",
    question_type: str = "lookup",
    language: str = "en",
    expected: str = "answer",
    gold: tuple[str, ...] = ("doc:gold",),
    ranked: tuple[str, ...] = ("doc:gold",),
    evidence: tuple[str, ...] | None = None,
    answer: str = "Step 1. Check the cable.",
    refused: bool = False,
    citations: tuple[str, ...] = ("doc:gold",),
    cited: tuple[str, ...] = ("Step 1. Check the cable.",),
    facts: tuple[str, ...] = ("Check the cable",),
) -> Attempt:
    return Attempt(
        id=qid,
        question_type=question_type,
        language=language,
        expected_action=expected,
        gold_ids=gold,
        ranked_ids=ranked,
        evidence_ids=ranked[:10] if evidence is None else evidence,
        answer_text=answer,
        refused=refused,
        citation_ids=citations,
        cited_texts=cited,
        required_facts=facts,
        temperature=0.0,
        seed=0,
    )


def _fused(node_id: str, text: str) -> FusedHit:
    return FusedHit(
        node_id=node_id,
        text=text,
        lang="en",
        page_start=1,
        page_end=1,
        doc_key=node_id.split(":", 1)[0],
        type="step",
        channels=("sparse",),
        best_rank=1,
        rrf_score=1 / 61,
    )


def test_sentences_keep_step_numbers_intact() -> None:
    text = "Step 1. Check battery cable connections for looseness."
    assert sentences(text) == [
        "Step 1.",
        "Check battery cable connections for looseness.",
    ]
    assert sentences("これは試験です。次です。") == ["これは試験です。", "次です。"]


def test_quote_judge_requires_the_fact_in_the_answer_and_the_citation() -> None:
    judge = QuoteJudge()
    passage = "Step 1. Check battery cable connections for looseness."
    present = judge.judge(answer=passage, facts=("Check battery cable",), cited_texts=(passage,))
    assert present.facts[0].present is True
    assert present.facts[0].quote == "Check battery cable"
    assert all(claim.supported for claim in present.claims)

    missing = judge.judge(
        answer="Check battery cable",
        facts=("Check battery cable",),
        cited_texts=("a different passage",),
    )
    assert missing.facts[0].present is False
    assert missing.facts[0].quote == ""

    invented = judge.judge(answer="Invented sentence.", facts=(), cited_texts=(passage,))
    assert invented.claims[0].supported is False


def test_model_quote_outside_the_passage_does_not_count() -> None:
    passage = "Check battery cable connections."
    raw = json.dumps(
        {
            "facts": [{"text": "cable", "present": True, "quote": "not in the passage"}],
            "claims": [
                {
                    "sentence": "Check battery cable connections.",
                    "supported": True,
                    "quote": passage,
                }
            ],
        }
    )
    judgment = verify_model_judgment(
        raw,
        facts=("cable",),
        shown=["Check battery cable connections."],
        cited_texts=(passage,),
        judge="test-model",
    )
    assert judgment.facts[0].present is False
    assert judgment.claims[0].supported is True
    assert judgment.claims[0].quote == passage


def test_hit_at_10_uses_the_evidence_set_and_skips_empty_gold() -> None:
    ranked = tuple(f"doc:{index}" for index in range(11))
    missed = _attempt(
        qid="late", gold=("doc:10",), ranked=ranked, evidence=ranked[:10], refused=True
    )
    hit = _attempt(qid="early", gold=("doc:9",), ranked=ranked, evidence=ranked[:10])
    blank = _attempt(
        qid="unanswerable-0001",
        question_type="unanswerable",
        expected="refuse",
        gold=(),
        ranked=ranked,
        evidence=ranked[:10],
        answer="No retrieved passage contains the requested material. Searched: missing",
        refused=True,
        citations=(),
        cited=(),
        facts=(),
    )
    judge = QuoteJudge()
    metrics = slice_metrics(
        [
            Judged(
                missed,
                judge.judge(
                    answer=missed.answer_text,
                    facts=missed.required_facts,
                    cited_texts=missed.cited_texts,
                ),
            ),
            Judged(
                hit,
                judge.judge(
                    answer=hit.answer_text,
                    facts=hit.required_facts,
                    cited_texts=hit.cited_texts,
                ),
            ),
            Judged(blank, judge.judge(answer=blank.answer_text, facts=(), cited_texts=())),
        ]
    )
    assert metrics.hit_at_10.numerator == 1
    assert metrics.hit_at_10.denominator == 2
    assert metrics.mrr_denominators == (11, 10)
    assert format_mrr(metrics.mrr_denominators) == "0.095"
    assert format_percent(metrics.evidence) == "50.0"
    assert metrics.actions.numerator == 2
    assert metrics.actions.denominator == 3


def test_evidence_recall_is_the_share_of_gold_passages() -> None:
    attempt = _attempt(gold=("doc:a", "doc:b"), evidence=("doc:a",), ranked=("doc:a", "doc:c"))
    judgment = QuoteJudge().judge(
        answer=attempt.answer_text, facts=attempt.required_facts, cited_texts=attempt.cited_texts
    )
    metrics = slice_metrics([Judged(attempt, judgment)])
    assert metrics.evidence.numerator == 1
    assert metrics.evidence.denominator == 2
    assert metrics.mrr_denominators == (1,)


def test_title_reader_stops_at_the_malfunction_title() -> None:
    from graphrag_poc.generate.answer import _requested_label, answer_from_passages

    question = (
        "The vehicle has this problem: 10. NO RESPONSE TO SHIFT LEVER MOVEMENT. "
        "Which transmission part number is listed?"
    )
    passage = "10. NO RESPONSE TO SHIFT LEVER MOVEMENT Step 1. Check the lever."
    assert _requested_label(question) == "10. NO RESPONSE TO SHIFT LEVER MOVEMENT"
    assert label_overshoots(question, (passage,)) is False
    answer = answer_from_passages(question, [_fused("doc:row", passage)])
    assert answer.refused is False
    assert "Check the lever" in answer.text
    mixed = "4. vehicle not charging according to voltmeter \u2014 where do I start?"
    assert _requested_label(mixed) == "4. vehicle not charging according to voltmeter"


def test_follow_up_query_includes_the_earlier_turn() -> None:
    record = {
        "question": "And on the M998?",
        "turns": [
            {"role": "user", "text": "Does this instruction mention the M1123?"},
            {"role": "user", "text": "And on the M998?"},
        ],
    }
    assert retrieval_query(record) == ("Does this instruction mention the M1123?\nAnd on the M998?")


def test_generator_receives_only_the_first_ten_passages(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("GENERATION_MODEL", raising=False)
    hits = [_fused(f"doc:{index}", f"passage {index}") for index in range(12)]
    record = {
        "id": "lookup-0001",
        "slice": {"question_type": "lookup", "language": "en"},
        "expected_action": "answer",
        "gold": {"node_ids": ["doc:11"]},
        "required_facts": [{"text": "passage 0"}],
    }
    attempt = attempt_from_hits(record, hits, question="What does passage 0 say?")
    assert attempt.evidence_ids == tuple(f"doc:{index}" for index in range(10))
    assert "doc:11" not in attempt.evidence_ids
    assert "passage 11" not in attempt.answer_text
    assert attempt.ranked_ids[-1] == "doc:11"


def test_second_run_reuses_the_judgment_cache(tmp_path: Path) -> None:
    attempt = _attempt()
    first, reused_first = score_attempts([attempt], QuoteJudge(), tmp_path)
    assert reused_first == 0
    assert first[0].judgment.facts[0].present is True

    class Exploding(QuoteJudge):
        def judge(
            self,
            *,
            answer: str,
            facts: tuple[str, ...],
            cited_texts: tuple[str, ...],
        ) -> object:
            raise AssertionError("the cache should have answered")

    second, reused_second = score_attempts([attempt], Exploding(), tmp_path)
    assert reused_second == 1
    assert second[0].judgment == first[0].judgment


def test_report_lists_every_question_type(tmp_path: Path) -> None:
    judge = QuoteJudge()
    rows = []
    for question_type in ("lookup", "relational", "unanswerable"):
        if question_type == "unanswerable":
            attempt = _attempt(
                qid="unanswerable-0001",
                question_type=question_type,
                expected="refuse",
                gold=(),
                answer="No retrieved passage contains the requested material.",
                refused=True,
                citations=(),
                cited=(),
                facts=(),
            )
        elif question_type == "relational":
            attempt = _attempt(
                qid="relational-0001",
                question_type=question_type,
                gold=("tm280_10:table:3-1:r1", "tm280_24p_1:parts:r1"),
                evidence=("tm280_10:table:3-1:r1",),
                ranked=("tm280_10:table:3-1:r1",),
                facts=("Step 1. Check", "5596028"),
                answer="Step 1. Check",
                cited=("Step 1. Check",),
            )
        else:
            attempt = _attempt(question_type=question_type)
        judgment = judge.judge(
            answer=attempt.answer_text,
            facts=attempt.required_facts,
            cited_texts=attempt.cited_texts,
        )
        rows.append(Judged(attempt, judgment))
    info = RunInfo("embed-test", "", "quote", 0.0, 0)
    report = render_report(info, rows)
    for question_type in ("lookup", "relational", "unanswerable"):
        assert f"| {question_type} |" in report
    assert "RRF k=60" in report
    assert "missed the parts-list row" in report
    assert "mlit_b052" not in report
    first = write_outputs(
        info,
        rows,
        report_path=tmp_path / "a.md",
        metrics_path=tmp_path / "a.json",
        results_path=tmp_path / "a.jsonl",
    )
    second = write_outputs(
        info,
        rows,
        report_path=tmp_path / "b.md",
        metrics_path=tmp_path / "b.json",
        results_path=tmp_path / "b.jsonl",
    )
    assert first == second
    assert (tmp_path / "a.json").read_text(encoding="utf-8") == (tmp_path / "b.json").read_text(
        encoding="utf-8"
    )
