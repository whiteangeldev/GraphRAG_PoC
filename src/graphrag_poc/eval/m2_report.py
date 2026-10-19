"""Write the M2 limitation analysis from the saved result rows."""

from pathlib import Path

from graphrag_poc.eval.check import QUESTIONS_PATH, load_node_text, load_questions
from graphrag_poc.eval.failures import (
    CLASS_ORDER,
    M1_RESULTS_PATH,
    RESULTS_PATH,
    Assignment,
    assign_all,
    counts,
    failing,
    load_results,
)

ROOT = Path(__file__).resolve().parents[3]
REPORT_PATH = ROOT / "docs" / "M2_LIMITATION_ANALYSIS.md"

CLASS_TITLE = {
    "keyword_mismatch": "Keyword mismatch: the title reader refuses a retrieved row",
    "unanswerable_answered": "A question with no answer is given a passage",
    "follow_up_unresolved": "The follow-up does not find the other model",
    "applicability_unresolved": "Applicability to a model is not resolved",
    "code_part_relation": "A code and a part stay in different passages",
    "procedure_incomplete": "A procedure is found without the rest of its steps",
    "wrong_section": "Right manual, the section is not retrieved",
    "ranked_too_low": "The right passage is retrieved below the ten",
    "answer_omitted_fact": "The gold passage is in the ten and the fact is still missed",
}

CLASS_FIX = {
    "keyword_mismatch": "outside the graph, and fixed in the improved baseline",
    "unanswerable_answered": "outside the graph; not changed in this milestone",
    "follow_up_unresolved": "a graph traversal",
    "applicability_unresolved": "a graph traversal",
    "code_part_relation": "a graph traversal",
    "procedure_incomplete": "a graph traversal",
    "wrong_section": "a graph traversal where a neighbour was retrieved; otherwise still retrieval",
    "ranked_too_low": "outside the graph; a reranker could reorder these hits",
    "answer_omitted_fact": "outside the graph; the judge requires an exact quote",
}

CLASS_BODY = {
    "keyword_mismatch": (
        "The dense and sparse lists already contain a gold passage inside the ten given to "
        "the generator, and the answer is still a refusal. The title string read from the "
        "question included the comma after the malfunction title or the first capital of the "
        "next word. That longer string is not in the manual, so the answerer treated the "
        "title as missing. Changing the embedding model or the fusion constant does not "
        "repair a check that runs after retrieval. The improved baseline stops the title at "
        "the malfunction name, including a mixed-case title that ends at an em dash. "
        "Questions that then succeed leave this class. Questions that still miss a second "
        "gold passage move into the class for that miss."
    ),
    "unanswerable_answered": (
        "The evaluation expects a refusal, and the answer quotes a retrieved passage. "
        "These questions do not look like a Table 3-1 title, so the title check never runs. "
        "The answerer then quotes the first fused passage. The invented code is not in the "
        "corpus, which is why the gold list is empty. A graph has no true node to walk to. "
        "The fix is a generator rule: when the question's distinctive token is absent from "
        "the retrieved passages, refuse and repeat the question. That rule was not applied "
        "here. A threshold on token overlap would also refuse some short Japanese lookups, "
        "and tuning that threshold on this set would not be a fair graph comparison."
    ),
    "follow_up_unresolved": (
        'The question is the second turn, "And on the M998?", after a turn that names the '
        "M1123. Retrieval receives both turns. The gold passage names both models and is not "
        "in the fused list. The words in the question are common model tokens, so many "
        "passages match and the one passage that states the pair does not win. Adding "
        "synonyms for M998 does not choose among the passages that already contain M998. "
        "A traversal from the model in the first turn, along APPLIES_TO, can prefer a "
        "passage that also applies to the model in the second turn. Three questions are in "
        "this class. The expected change is that those passages enter the ten."
    ),
    "applicability_unresolved": (
        "The question asks whether a named model is in the instruction. The gold passage "
        "contains that model and is outside the ten. Many passages in the M998 series name "
        "some model, so dense and sparse search return a popular model mention instead of "
        "the passage written for this one. A synonym table cannot separate M1045 from M1025. "
        "APPLIES_TO, drawn from applies_to.models and from the model token in the passage, "
        "lets the question's model select its own passages. This is the class where "
        "applicability hit@10 has to move. The M1 figure is 4.5 percent, one question in 22."
    ),
    "code_part_relation": (
        "The question needs both a malfunction row and a parts-list row. One of them, "
        "usually the malfunction row or a step that contains the group keyword, is inside "
        "the ten. The parts row is not. The two passages share a keyword such as NOZZLE or "
        "TRANSMISSION and otherwise have no stored link. Raising the fusion constant or "
        "the evidence size does not create that link: the parts row is often far down the "
        "list or absent, because its description is a catalogue line and the question is a "
        "fault. CANDIDATE_PART, from the committed keyword map in data/cases/rules.json, "
        "plus LISTS back to the parts-list passage, is the traversal that can put the part "
        "into fusion. The M3 acceptance target, 15 points of evidence recall on relational "
        "and multi-hop questions, has to come from this class and from procedure steps that "
        "are likewise split. The edge is a candidate, not a proof that the part fits the "
        "repair. The keyword and the description stay on the edge."
    ),
    "procedure_incomplete": (
        "Hit@10 on procedures is 100 percent: some step of the task is in the ten. "
        "Evidence recall is much lower because the question quotes the first line of the "
        "task and the later steps, and often the caution, share little of that line. "
        "They are stored as separate nodes. A longer query that pasted every step would "
        "be circular. NEXT, in step-number order under the same task prefix, and "
        "BOUND_CAUTION, which the node file already records, pull the rest of the task "
        "once any step is found. Most of the missing nodes are later steps. A smaller "
        "number are cautions. Tuning the dense model does not attach a warning that the "
        "question never named."
    ),
    "wrong_section": (
        "No gold passage appears anywhere in the fused list. The retrieved pages are "
        "from the same corpus and answer a neighbouring question. For a Japanese lookup "
        "the gold section is in mlit_b052 and the hits are other sections, or none of "
        "that document. For an English malfunction the Table 3-1 row itself was not "
        "returned. PARENT helps only when a passage from the same section was retrieved "
        "and the gold node is its child or its parent. Where the list contains nothing "
        "from the gold document, the graph has no seed and the miss stays a retrieval "
        "miss. The report's examples show which of those two situations the question is in."
    ),
    "ranked_too_low": (
        "A gold passage is in the fused list and its rank is worse than 10, so it is "
        "not given to the generator. Hit@10 is defined on those ten passages. Widening "
        "the cutoff would change the metric rather than the retriever. A cross-encoder "
        "could move a hit from rank 13 into the ten when it actually answers the "
        "question. That is a reranker, and the reported baseline leaves the reranker "
        "off. The graph helps this class only when a passage already inside the ten "
        "is a PARENT, NEXT, or CANDIDATE_PART neighbour of the low-ranked row. It is "
        "not the class the schema is built for."
    ),
    "answer_omitted_fact": (
        "Every gold passage is inside the ten, and the action matches. A required fact "
        "is still not accepted. The judge counts a fact only when it returns a quote "
        "that is an exact span of a cited passage. The passage can be present in the "
        "ranking while the answer cites a different hit, or the model's quote can differ "
        "by a character from the manual. Neither failure is a missing edge. The title "
        "fix moves some of these questions out of the class by quoting the malfunction "
        "row itself. What remains is generator and judge behaviour. It is outside the graph."
    ),
}


def render_report(
    improved: list[dict[str, object]],
    baseline: list[dict[str, object]],
    questions: dict[str, dict[str, object]],
    texts: dict[str, str],
    retrieved: dict[str, list[tuple[str, int, str]]] | None = None,
) -> str:
    """Limitation analysis. Counts come only from the result rows."""

    current = assign_all(improved)
    before = assign_all(baseline)
    if {item.id for item in current} != {item.id for item in before}:
        raise ValueError("the M1 results and the improved results name different questions")
    lines = [
        "# M2 limitation analysis",
        "",
        "This report classifies every question in `data/eval/questions.jsonl`.",
        "The M1 numbers are the published baseline, copied into `data/eval/m1_baseline/` "
        "before the title-reader fix.",
        "The improved numbers are the baseline M3 should be compared with.",
        "The schema those classes use is `docs/M2_GRAPH_SCHEMA.md`.",
        "",
        "## What counts as a failure",
        "",
        "A question fails when the action is wrong, any required fact is missing, or any "
        "gold passage is outside the ten passages given to the generator.",
        "Claim precision is reported in the baseline and is not, by itself, a failure class. "
        "The judge demands an exact quote, so a correct passage rewritten by the model would "
        "otherwise mark almost every answer as a failure and hide the retrieval misses.",
        "Each failing question is in exactly one class. The first matching rule wins:",
        "",
        "1. Keyword mismatch: the answer refuses, and a gold passage is inside the ten.",
        "2. Unanswerable answered: the expected action is refuse, and the answer is not a refusal.",
        "3. Follow-up unresolved: the question is a follow-up and the gold or a fact is missed.",
        "4. Applicability unresolved: the question is applicability and a gold passage is missed.",
        "5. Code and part: the question is relational or multi-hop, a parts-list row is missed, "
        "and some gold passage is inside the ten.",
        "6. Procedure incomplete: the question is a procedure, a gold step or caution is missed, "
        "and some gold passage is inside the ten.",
        "7. Wrong section: a gold passage is absent from the whole fused list.",
        "8. Ranked too low: a gold passage is in the fused list below rank 10.",
        "9. Answer omitted the fact: the action is wrong or a fact is missing, and the gold "
        "passages are inside the ten.",
        "",
        "A question that matches none of these is a success.",
        "",
        "## Counts",
        "",
        _count_table(before, current),
        "",
        _add_up(current),
        "",
        "## The cheap fix",
        "",
        "Keyword mismatch is the class a graph should not be credited for.",
        "The M1 answerer treated the malfunction title plus the next word as the string "
        "that had to appear in a passage. The improved answerer keeps the title only. "
        "A mixed-case title that ends at an em dash, which is how the troubleshooting "
        "questions are written, is read the same way.",
        "No index was rebuilt. Fusion is still reciprocal rank fusion with k = 60, "
        "the evidence size is still 10, and the reranker is still off.",
        "Generation and judging are still Qwen3-0.6B at temperature 0 and seed 0.",
        "",
        "## Classes",
        "",
    ]
    for name in CLASS_ORDER:
        lines.extend(_class_section(name, current, before, questions, texts, retrieved or {}))
    lines.extend(
        [
            "## What M3 should measure",
            "",
            "Compare M3 with the improved baseline, not with the M1 file.",
            "The graph classes are code and part, procedure incomplete, applicability, "
            "follow-up, and the wrong-section questions whose top passages are in the "
            "same document as the gold.",
            "The acceptance target from the requirements is 15 points of evidence recall "
            "and 10 points of required-fact recall on the relational and multi-hop questions, "
            "with no question type losing more than 1 point of hit@10 or required-fact recall.",
            "Those relational and multi-hop points have to come from bringing the missing "
            "parts row, and the missing middle step, into the ten.",
            "Keyword mismatch, unanswerable answers, facts omitted from a complete gold set, "
            "and passages ranked just below the ten are not that target.",
            "",
        ]
    )
    return "\n".join(lines)


def _count_table(before: list[Assignment], current: list[Assignment]) -> str:
    old = counts(before)
    new = counts(current)
    lines = [
        "| Class | M1 baseline | Improved baseline | Where the fix lives |",
        "|---|---:|---:|---|",
    ]
    for name in ("success", *CLASS_ORDER):
        place = "the question passed" if name == "success" else CLASS_FIX[name]
        lines.append(f"| {name} | {old.get(name, 0)} | {new.get(name, 0)} | {place} |")
    lines.append(f"| Total | {len(before)} | {len(current)} | |")
    return "\n".join(lines)


def _add_up(current: list[Assignment]) -> str:
    failed = failing(current)
    by_class = counts(current)
    class_sum = sum(by_class[name] for name in CLASS_ORDER)
    return (
        f"The improved baseline has {len(current)} questions. "
        f"{by_class['success']} succeed. {len(failed)} fail. "
        f"The nine class counts sum to {class_sum}."
    )


def _class_section(
    name: str,
    current: list[Assignment],
    baseline: list[Assignment],
    questions: dict[str, dict[str, object]],
    texts: dict[str, str],
    retrieved: dict[str, list[tuple[str, int, str]]],
) -> list[str]:
    members = [item for item in current if item.failure_class == name]
    earlier = [item for item in baseline if item.failure_class == name]
    lines = [
        f"### {CLASS_TITLE[name]}",
        "",
        f"Class id: `{name}`. Improved-baseline count: {len(members)}. Fix: {CLASS_FIX[name]}.",
        "",
        CLASS_BODY[name],
        "",
    ]
    shown = members[:3]
    source = "improved baseline"
    if not shown:
        lines.append(
            "The improved baseline has no question in this class. "
            "The examples are from the M1 baseline, before the title-reader fix."
        )
        lines.append("")
        source = "M1 baseline"
        shown = earlier[:3]
    lines.append(f"Examples ({source}):")
    lines.append("")
    for item in shown:
        lines.extend(_example(item.id, questions, texts, retrieved.get(item.id, [])))
    return lines


def _example(
    qid: str,
    questions: dict[str, dict[str, object]],
    texts: dict[str, str],
    hits: list[tuple[str, int, str]],
) -> list[str]:
    record = questions[qid]
    lines = [f"#### {qid}", "", str(record.get("question", "")), ""]
    gold = record.get("gold")
    node_ids: list[str] = []
    pages: list[object] = []
    if isinstance(gold, dict) and isinstance(gold.get("node_ids"), list):
        node_ids = [str(node_id) for node_id in gold["node_ids"]]
        raw_pages = gold.get("pages")
        pages = list(raw_pages) if isinstance(raw_pages, list) else []
    if not node_ids:
        lines.append("Gold: none. The expected action is refuse.")
        lines.append("")
    else:
        lines.append("Gold:")
        lines.append("")
        for index, node_id in enumerate(node_ids):
            page = pages[index] if index < len(pages) else ""
            lines.append(f"- `{node_id}`, page {page}. {_clip(texts.get(node_id, ''))}")
        lines.append("")
    if hits:
        lines.append("Retrieved, in fused order, up to the first five:")
        lines.append("")
        for node_id, page, text in hits[:5]:
            lines.append(f"- `{node_id}`, page {page}. {_clip(text)}")
        lines.append("")
    return lines


def _clip(text: str, limit: int = 420) -> str:
    flat = " ".join(text.split())
    if len(flat) <= limit:
        return flat
    return flat[:limit].rstrip() + "..."


def load_question_map(path: Path | None = None) -> dict[str, dict[str, object]]:
    return {str(record["id"]): record for record in load_questions(path or QUESTIONS_PATH)}


def write_report_files() -> Path:
    improved = load_results(RESULTS_PATH)
    baseline = load_results(M1_RESULTS_PATH)
    questions = load_question_map()
    texts = load_node_text()
    current = assign_all(improved)
    earlier = assign_all(baseline)
    retrieved = _retrieve_examples(_example_ids(current, earlier), questions)
    report = render_report(improved, baseline, questions, texts, retrieved)
    REPORT_PATH.write_text(report, encoding="utf-8")
    from graphrag_poc.eval.failures import write_assignments

    write_assignments(assign_all(improved))
    return REPORT_PATH


def _example_ids(current: list[Assignment], earlier: list[Assignment]) -> list[str]:
    wanted: list[str] = []
    for name in CLASS_ORDER:
        members = [item.id for item in current if item.failure_class == name]
        if not members:
            members = [item.id for item in earlier if item.failure_class == name]
        wanted.extend(members[:3])
    return wanted


def _retrieve_examples(
    wanted: list[str],
    questions: dict[str, dict[str, object]],
) -> dict[str, list[tuple[str, int, str]]]:
    """Top fused passages for the example questions. Empty if Qdrant is down."""

    if not wanted:
        return {}
    try:
        from graphrag_poc.eval.score import retrieval_query
        from graphrag_poc.index.client import make_client
        from graphrag_poc.index.embed import build_embedder
        from graphrag_poc.retrieve.search import retrieve
    except Exception:
        return {}
    try:
        client = make_client()
        embedder = build_embedder()
    except Exception:
        return {}
    found: dict[str, list[tuple[str, int, str]]] = {}
    for qid in wanted:
        record = questions.get(qid)
        if record is None:
            continue
        try:
            hits = retrieve(client, embedder, retrieval_query(record))
        except Exception:
            return found
        found[qid] = [(hit.node_id, hit.page_start, hit.text) for hit in hits[:5]]
    return found


def main() -> int:
    path = write_report_files()
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
