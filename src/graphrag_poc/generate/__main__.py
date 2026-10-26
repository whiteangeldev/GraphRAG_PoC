"""Answer one question, or run the Step 6 exit check with --check."""

import os
import sys

from qdrant_client import QdrantClient

from graphrag_poc.generate.answer import Answer, Citation, answer_from_passages
from graphrag_poc.generate.config import load_env_file as _load_env_file
from graphrag_poc.generate.model import model_answer as _model_answer
from graphrag_poc.index.client import make_client
from graphrag_poc.index.embed import Embedder, build_embedder
from graphrag_poc.retrieve.fusion import FusedHit
from graphrag_poc.retrieve.graph import RelationFrame, retrieve_question

LOOKUP = "What is the corrective action for 4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER?"
PROCEDURE = (
    "What are the steps to disconnect the engine oil cooler supply and return lines, "
    "including the warning not to drain oil when the engine is hot?"
)
UNKNOWN = "What is the corrective action for 99. ZZZNOTACODE FAILURE?"
RELATIONAL = (
    "The vehicle has this problem: 10. NO RESPONSE TO SHIFT LEVER MOVEMENT. "
    "Which transmission part number is listed?"
)
HOT_OIL = "Do not drain oil when engine is hot"
DEMONSTRATION = (
    ("Lookup", LOOKUP),
    ("Procedure", PROCEDURE),
    ("Relational", RELATIONAL),
    ("Refusal", UNKNOWN),
)
_DEMONSTRATION_NOTES = {
    "Lookup": "This is operator Table 3-1, row 4, page 281. The first check is the battery cables.",
    "Procedure": (
        "The hot-oil warning is cited before the disconnect step. Both come from task 3-8, page 32."
    ),
    "Relational": (
        "The baseline refuses. The malfunction is in the operator manual, and the question "
        "asks which transmission part to use. The answerer reads the title plus the next word, "
        "does not find that longer string, and does not reach the parts list."
    ),
    "Refusal": (
        "99. ZZZNOTACODE FAILURE is not in the manuals. "
        "The answer repeats the question and cites nothing."
    ),
}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    _load_env_file()
    if args == ["--check"]:
        return _check()
    if args == ["--demonstrate"]:
        return _demonstrate()
    if not args:
        print(
            "usage: python -m graphrag_poc.generate --check | --demonstrate | <question>",
            file=sys.stderr,
        )
        return 2
    result = ask(" ".join(args))
    _print_answer(result)
    return 0


def ask(question: str) -> Answer:
    """Answer a question. The demonstration page uses the same function."""

    result, _hits, _frame = ask_with_hits(question)
    return result


def ask_with_hits(
    question: str,
    *,
    client: QdrantClient | None = None,
    embedder: Embedder | None = None,
) -> tuple[Answer, list[FusedHit], RelationFrame]:
    """Retrieve, then answer. Returns the fused ranking and the relation frame."""

    active_embedder = embedder if embedder is not None else build_embedder()
    active_client = (
        client
        if client is not None
        else make_client(api_key=os.environ.get("QDRANT_API_KEY") or None)
    )
    hits, _decision, frame = retrieve_question(active_client, active_embedder, question)
    return compose_answer(question, hits, frame), hits, frame


def compose_answer(
    question: str,
    hits: list[FusedHit],
    frame: RelationFrame | None = None,
) -> Answer:
    """Use the configured model; unset models retain the legacy offline quote demo only."""

    if os.environ.get("GENERATION_MODEL", "").strip():
        return _model_answer(question, hits, frame)
    return _with_part(answer_from_passages(question, hits), hits, frame)


def _check() -> int:
    lookup = ask(LOOKUP)
    procedure = ask(PROCEDURE)
    unknown = ask(UNKNOWN)
    problems: list[str] = []
    if lookup.refused or "Check battery cable connections" not in lookup.text:
        problems.append("lookup did not return the charging row")
    if not any("table:3-1" in citation.node_id for citation in lookup.citations):
        problems.append(f"lookup citations were {lookup.citations}")
    if procedure.refused:
        problems.append("procedure question was refused")
    if "Disconnect two engine oil cooler" not in procedure.text:
        problems.append("procedure answer is missing the disconnect step")
    if HOT_OIL not in procedure.text:
        problems.append("procedure answer is missing the bound hot-oil warning")
    if not _steps_in_order(procedure.text):
        problems.append("procedure steps are out of order")
    if not unknown.refused or UNKNOWN not in unknown.text:
        problems.append("unknown code was not refused with the searched question")
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    print("hybrid retrieval check passed")
    return 0


def _demonstrate() -> int:
    """Run the four demonstration questions and record the answers."""

    from pathlib import Path

    sections = [
        "# Five-minute demonstration",
        "",
        "Recorded from the M1 baseline (`docs/baseline_report.md`).",
        "Open the demo with `make demo`, then go to http://127.0.0.1:8080.",
        "Ask these four questions in order. About five minutes covers them.",
        "The page calls `ask_with_hits`, the same function that produced the answers below.",
        "The recording of this page answering the four questions is `docs/m1-demonstration.mp4`.",
        "",
    ]
    for title, question in DEMONSTRATION:
        result = ask(question)
        sections.extend(_demonstration_section(title, question, result))
    path = Path(__file__).resolve().parents[3] / "docs" / "demonstration.md"
    path.write_text("\n".join(sections), encoding="utf-8")
    print(f"demonstration recorded at {path}")
    return 0


def _demonstration_section(title: str, question: str, result: Answer) -> list[str]:
    lines = [f"## {title}", "", question, "", result.text, ""]
    if result.citations:
        lines.append("Citations:")
        lines.append("")
        for citation in result.citations:
            lines.append(f"- `{citation.node_id}`, page {citation.page}")
        lines.append("")
    else:
        lines.extend(["Citations: none.", ""])
    note = _DEMONSTRATION_NOTES.get(title)
    if note:
        lines.extend([note, ""])
    return lines


def _steps_in_order(text: str) -> bool:
    first = text.find("1. Disconnect two engine oil cooler")
    later = text.find("3. Connect two engine oil cooler")
    if first < 0:
        return False
    if later < 0:
        return True
    return first < later


def _with_part(
    answer: Answer,
    hits: list[FusedHit],
    frame: RelationFrame | None,
) -> Answer:
    if frame is None or not frame.part_number or answer.refused:
        return answer
    cited = {citation.node_id for citation in answer.citations}
    extra = [hit for hit in hits if frame.part_number in hit.text and hit.node_id not in cited]
    if not extra:
        return answer
    chosen = next((hit for hit in extra if hit.node_id == frame.part_node_id), extra[0])
    citations = (*answer.citations, Citation(chosen.node_id, chosen.page_start))
    return Answer(
        answer.text + "\n" + chosen.text,
        citations,
        False,
        answer.searched,
        answer.temperature,
        answer.seed,
    )


def _print_answer(result: Answer) -> None:
    print(result.text)
    for citation in result.citations:
        print(f"cite {citation.node_id} page {citation.page}")


if __name__ == "__main__":
    raise SystemExit(main())
