"""Answer one question, or run the Step 6 exit check with --check."""

import os
import sys

from qdrant_client import QdrantClient

from graphrag_poc.generate.answer import Answer, answer_from_passages
from graphrag_poc.index.client import make_client
from graphrag_poc.index.embed import Embedder, build_embedder
from graphrag_poc.retrieve.fusion import FusedHit
from graphrag_poc.retrieve.search import retrieve

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

    result, _hits = ask_with_hits(question)
    return result


def ask_with_hits(
    question: str,
    *,
    client: QdrantClient | None = None,
    embedder: Embedder | None = None,
) -> tuple[Answer, list[FusedHit]]:
    """Retrieve, then answer. Returns the fused ranking the page displays."""

    active_embedder = embedder if embedder is not None else build_embedder()
    active_client = (
        client
        if client is not None
        else make_client(api_key=os.environ.get("QDRANT_API_KEY") or None)
    )
    hits = retrieve(active_client, active_embedder, question)
    return compose_answer(question, hits), hits


def compose_answer(question: str, hits: list[FusedHit]) -> Answer:
    """Answer from these passages. A configured generation model is used when set."""

    if os.environ.get("GENERATION_MODEL", "").strip():
        return _model_answer(question, hits)
    return answer_from_passages(question, hits)


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


def _model_answer(question: str, hits: list[FusedHit]) -> Answer:
    """Call the configured chat model. Citations must be passages that were retrieved."""

    from openai import OpenAI

    fused = hits
    grounded = answer_from_passages(question, fused)
    if grounded.refused:
        return grounded
    client = OpenAI(
        base_url=os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:8000/v1"),
        api_key=os.environ.get("OPENAI_API_KEY") or "not-needed",
        timeout=120.0,
    )
    passages = "\n\n".join(f"[{hit.node_id} page {hit.page_start}]\n{hit.text}" for hit in fused)
    response = client.chat.completions.create(
        model=os.environ["GENERATION_MODEL"],
        temperature=grounded.temperature,
        seed=grounded.seed,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer only from the passages. Cite node_id and page. "
                    "If the passages do not contain the answer, refuse and repeat the question."
                ),
            },
            {"role": "user", "content": f"Question: {question}\n\nPassages:\n{passages}"},
        ],
    )
    text = response.choices[0].message.content or ""
    if "Searched:" in text and question in text:
        return Answer(text, (), True, question, grounded.temperature, grounded.seed)
    cited = tuple(citation for citation in grounded.citations if citation.node_id in text)
    if not cited:
        cited = grounded.citations
    return Answer(text, cited, False, question, grounded.temperature, grounded.seed)


def _print_answer(result: Answer) -> None:
    print(result.text)
    for citation in result.citations:
        print(f"cite {citation.node_id} page {citation.page}")


def _load_env_file() -> None:
    from pathlib import Path

    path = Path(".env")
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


if __name__ == "__main__":
    raise SystemExit(main())
