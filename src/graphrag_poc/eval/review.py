"""The 20-question gold-passage sample for Sodick's review."""

from pathlib import Path

from graphrag_poc.eval.check import load_node_text, load_questions

ROOT = Path(__file__).resolve().parents[3]
SAMPLE_PATH = ROOT / "docs" / "gold_review_sample.md"

# Twenty questions spread across the evaluation slices, including Japanese.
SAMPLE_IDS = (
    "lookup-0001",
    "lookup-0002",
    "lookup-ja-0001",
    "lookup-ja-0002",
    "procedure-0005",
    "procedure-0006",
    "procedure-0014",
    "applicability-0001",
    "applicability-0002",
    "applicability-0003",
    "relational-0001",
    "relational-0005",
    "relational-0010",
    "multi-0002",
    "multi-0004",
    "trouble-0001",
    "trouble-0005",
    "follow-0001",
    "unanswerable-0001",
    "unanswerable-0016",
)


def render_sample(
    questions: list[dict[str, object]] | None = None,
    nodes: dict[str, str] | None = None,
) -> str:
    """Copy each gold passage from the node files into one review document."""

    records = {str(record["id"]): record for record in (questions or load_questions())}
    texts = nodes if nodes is not None else load_node_text()
    missing = [qid for qid in SAMPLE_IDS if qid not in records]
    if missing:
        raise KeyError(f"review sample ids are not in the evaluation set: {missing}")
    lines = [
        "# Gold passage review sample",
        "",
        "Twenty questions from `data/eval/questions.jsonl` for Sodick's review.",
        "Each gold passage below is copied from the node file named in the heading.",
        "An unanswerable question has no gold passage. The correct action is to refuse.",
        "",
        "| # | Id | Type | Language | Action |",
        "|---:|---|---|---|---|",
    ]
    for index, qid in enumerate(SAMPLE_IDS, start=1):
        record = records[qid]
        slice_ = _slice(record)
        lines.append(
            f"| {index} | {qid} | {slice_.get('question_type', '')} | "
            f"{slice_.get('language', '')} | {record.get('expected_action', '')} |"
        )
    lines.append("")
    for index, qid in enumerate(SAMPLE_IDS, start=1):
        lines.extend(_section(index, records[qid], texts))
    return "\n".join(lines).rstrip() + "\n"


def write_sample(path: Path | None = None) -> Path:
    destination = path or SAMPLE_PATH
    destination.write_text(render_sample(), encoding="utf-8")
    return destination


def _section(index: int, record: dict[str, object], texts: dict[str, str]) -> list[str]:
    qid = str(record["id"])
    slice_ = _slice(record)
    lines = [
        f"## {index}. {qid}",
        "",
        f"- Type: {slice_.get('question_type', '')}",
        f"- Vocabulary: {slice_.get('vocabulary', '')}",
        f"- Language: {slice_.get('language', '')}",
        f"- Expected action: {record.get('expected_action', '')}",
        "",
        str(record.get("question", "")),
        "",
    ]
    lines.extend(_facts("Required facts", record.get("required_facts")))
    lines.extend(_facts("Forbidden facts", record.get("forbidden_facts")))
    gold = record.get("gold")
    node_ids: list[str] = []
    pages: list[object] = []
    if isinstance(gold, dict) and isinstance(gold.get("node_ids"), list):
        node_ids = [str(node_id) for node_id in gold["node_ids"]]
        raw_pages = gold.get("pages")
        pages = list(raw_pages) if isinstance(raw_pages, list) else []
    if not node_ids:
        lines.extend(["Gold passages: none.", ""])
        return lines
    lines.append("Gold passages:")
    lines.append("")
    for position, node_id in enumerate(node_ids):
        if node_id not in texts:
            raise KeyError(f"{qid}: gold node {node_id} does not exist")
        page = pages[position] if position < len(pages) else ""
        lines.append(f"### {node_id}")
        lines.append("")
        lines.append(f"Page {page}.")
        lines.append("")
        lines.append(_fence(texts[node_id]))
        lines.append("")
    return lines


def _facts(title: str, value: object) -> list[str]:
    if not isinstance(value, list) or not value:
        return []
    lines = [f"{title}:", ""]
    for fact in value:
        if isinstance(fact, dict):
            lines.append(f"- ({fact.get('type', '')}) {fact.get('text', '')}")
    lines.append("")
    return lines


def _fence(text: str) -> str:
    body = text.replace("\r\n", "\n").rstrip("\n")
    width = 4
    while "`" * width in body:
        width += 1
    mark = "`" * width
    return f"{mark}\n{body}\n{mark}"


def _slice(record: dict[str, object]) -> dict[str, object]:
    slice_ = record.get("slice")
    if isinstance(slice_, dict):
        return slice_
    return {}


def main() -> int:
    path = write_sample()
    print(f"wrote {len(SAMPLE_IDS)} review questions to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
