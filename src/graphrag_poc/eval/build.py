"""Build the Appendix C evaluation set from the node files."""

import json
import re
from pathlib import Path

from graphrag_poc.cases.rules import load_rules
from graphrag_poc.eval.check import AUTHOR, QUESTIONS_PATH, load_node_text
from graphrag_poc.ingest.catalog import NODES

_STEP_FACT = re.compile(r"Step 1\.[^.]+")
_MODEL = re.compile(r"\bM\d{3,4}(?:A\d)?\b")
_DATE = "14 October 2026"


def build_questions(nodes_dir: Path | None = None) -> list[dict[str, object]]:
    """Create a deterministic question list. Facts are copied from passage text."""

    texts = load_node_text(nodes_dir)
    nodes = _load_nodes(nodes_dir)
    questions: list[dict[str, object]] = []
    questions.extend(_lookups(nodes, texts))
    questions.extend(_procedures(nodes, texts))
    questions.extend(_applicability(nodes, texts))
    questions.extend(_relational(nodes, texts))
    questions.extend(_multi_hop(nodes, texts))
    questions.extend(_unanswerable(texts))
    questions.extend(_troubleshooting(nodes, texts))
    questions.extend(_follow_ups(nodes, texts))
    questions.extend(_japanese(nodes, texts))
    return questions


def write_questions(questions: list[dict[str, object]], path: Path | None = None) -> Path:
    destination = path or QUESTIONS_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(record, ensure_ascii=False, separators=(",", ":")) for record in questions]
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination


def _lookups(nodes: list[dict[str, object]], texts: dict[str, str]) -> list[dict[str, object]]:
    rows = [node for node in nodes if _is_malfunction(node)]
    made: list[dict[str, object]] = []
    for index, node in enumerate(rows):
        fact = _step_fact(str(node["text"]))
        if fact is None:
            continue
        title = str(node["table"]["cells"][0])  # type: ignore[index]
        everyday = index % 2 == 0
        question = (
            f"The truck is showing this problem: {title}. What should I check first?"
            if everyday
            else f"What does malfunction {title} list as the first test or corrective action?"
        )
        made.append(
            _record(
                f"lookup-{index + 1:04d}",
                "lookup",
                everyday,
                "en",
                _model_in(str(node["text"])),
                question,
                "answer",
                [node],
                [{"type": "step", "text": fact}],
                [],
            )
        )
    return made


def _procedures(nodes: list[dict[str, object]], texts: dict[str, str]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for node in nodes:
        if node.get("type") != "step" or node.get("doc_key") not in {"tm280_20_2", "tm280_10"}:
            continue
        text = str(node.get("text") or "")
        if len(text) > 400 or not re.match(r"^\d+\.", text):
            continue
        grouped.setdefault(_task_prefix(str(node["node_id"])), []).append(node)
    made: list[dict[str, object]] = []
    for prefix, steps in sorted(grouped.items()):
        ordered = sorted(steps, key=lambda item: _step_number(str(item["text"])))
        if len(ordered) < 2:
            continue
        chosen = ordered[:3]
        facts = [{"type": "step", "text": str(step["text"])} for step in chosen]
        caution = _caution_for(prefix, nodes)
        gold = list(chosen)
        if caution is not None and len(str(caution["text"])) <= 400:
            gold.append(caution)
            warning = _warning_fact(str(caution["text"]))
            if warning:
                facts.append({"type": "caution", "text": warning})
        everyday = len(made) % 2 == 0
        title = str(chosen[0]["text"])
        question = (
            f"How do I carry out this job, in order? It starts with: {title}"
            if everyday
            else f"List the numbered steps, in order, that begin with: {title}"
        )
        made.append(
            _record(
                f"procedure-{len(made) + 1:04d}",
                "procedure",
                everyday,
                "en",
                _model_in(" ".join(str(step["text"]) for step in chosen)),
                question,
                "answer",
                gold,
                facts,
                [],
            )
        )
        if len(made) == 22:
            break
    return made


def _applicability(
    nodes: list[dict[str, object]], texts: dict[str, str]
) -> list[dict[str, object]]:
    made: list[dict[str, object]] = []
    seen: set[str] = set()
    for node in nodes:
        if node.get("lang") != "en" or node.get("type") in {"boilerplate", "chapter"}:
            continue
        text = str(node.get("text") or "")
        if len(text) > 500:
            continue
        model = _model_in(text)
        if model is None or model in seen:
            continue
        if model not in text:
            continue
        seen.add(model)
        everyday = len(made) % 2 == 0
        question = (
            f"Does this instruction mention the {model}?"
            if everyday
            else f"Which vehicle model is named for this content, and is it the {model}?"
        )
        made.append(
            _record(
                f"applicability-{len(made) + 1:04d}",
                "applicability",
                everyday,
                "en",
                model,
                question,
                "answer",
                [node],
                [{"type": "value", "text": model}],
                [],
            )
        )
        if len(made) == 22:
            break
    return made


def _relational(nodes: list[dict[str, object]], texts: dict[str, str]) -> list[dict[str, object]]:
    made: list[dict[str, object]] = []
    for row, part, keyword in _fault_part_pairs(nodes):
        step_fact = _step_fact(str(row["text"]))
        part_no = str(part["table"]["cells"][4])  # type: ignore[index]
        if step_fact is None or part_no not in str(part["text"]):
            continue
        everyday = len(made) % 2 == 0
        symptom = str(row["table"]["cells"][0])  # type: ignore[index]
        question = (
            f"The vehicle has this problem: {symptom}. "
            f"Which {keyword.lower()} part number is listed?"
            if everyday
            else f"For malfunction {symptom}, which parts-list item matches {keyword}?"
        )
        made.append(
            _record(
                f"relational-{len(made) + 1:04d}",
                "relational",
                everyday,
                "en",
                _model_in(str(row["text"])),
                question,
                "answer",
                [row, part],
                [
                    {"type": "step", "text": step_fact},
                    {"type": "value", "text": part_no},
                ],
                [],
            )
        )
        if len(made) == 26:
            break
    return made


def _multi_hop(nodes: list[dict[str, object]], texts: dict[str, str]) -> list[dict[str, object]]:
    made: list[dict[str, object]] = []
    for row, part, keyword in _fault_part_pairs(nodes):
        step = _short_step_with(nodes, keyword, exclude=str(row["node_id"]))
        step_fact = _step_fact(str(row["text"]))
        part_no = str(part["table"]["cells"][4])  # type: ignore[index]
        if step is None or step_fact is None or part_no not in str(part["text"]):
            continue
        step_text = str(step["text"])
        if keyword.lower() not in step_text.lower():
            continue
        everyday = len(made) % 2 == 1
        symptom = str(row["table"]["cells"][0])  # type: ignore[index]
        question = (
            f"My truck has this fault: {symptom}. The manual also mentions {keyword.lower()}. "
            f"What part number should I look up?"
            if everyday
            else (
                f"Trace malfunction {symptom} through the {keyword.lower()} step to the parts list."
            )
        )
        made.append(
            _record(
                f"multi-{len(made) + 1:04d}",
                "multi_hop",
                everyday,
                "en",
                _model_in(str(row["text"]) + step_text),
                question,
                "answer",
                [row, step, part],
                [
                    {"type": "step", "text": step_fact},
                    {"type": "step", "text": step_text},
                    {"type": "value", "text": part_no},
                ],
                [],
            )
        )
        if len(made) == 26:
            break
    return made


def _unanswerable(texts: dict[str, str]) -> list[dict[str, object]]:
    prompts = [
        "99. ZZZNOTACODE FAILURE",
        "E9999-NO-SUCH-CODE",
        "part number ZZ-NO-SUCH-PART",
        "malfunction 88. INVENTED GEARBOX WHISTLE",
        "fault code QX-404",
        "NSN 0000000000000",
        "procedure 99-99 on the M000",
        "warning about the flux capacitor",
        "model M0000A9 belt tension",
        "Table 99-9. Imaginary calibration",
        "para. 99-99 slave start",
        "pump model DB0000-0000",
        "cage code 00000 part ZZZZ",
        "malfunction 77. LEFT TURN SIGNAL ON THE MOON",
        "document tm000_00 page 9999",
        "別添99の存在しない灯火基準",
    ]
    made: list[dict[str, object]] = []
    corpus = "\n".join(texts.values())
    for index, prompt in enumerate(prompts):
        if prompt in corpus:
            continue
        everyday = index % 2 == 0
        language = "ja" if index == len(prompts) - 1 else "en"
        question = (
            f"What does this mean in the manual: {prompt}?"
            if not everyday
            else f"Can you explain {prompt}? I can't find it in the book."
        )
        made.append(
            _record(
                f"unanswerable-{len(made) + 1:04d}",
                "unanswerable",
                everyday,
                language,
                None,
                question,
                "refuse",
                [],
                [],
                [{"type": "value", "text": prompt}],
            )
        )
    return made


def _troubleshooting(
    nodes: list[dict[str, object]], texts: dict[str, str]
) -> list[dict[str, object]]:
    made: list[dict[str, object]] = []
    for node in _malfunctions(nodes)[:10]:
        fact = _step_fact(str(node["text"]))
        if fact is None:
            continue
        symptom = str(node["table"]["cells"][0])  # type: ignore[index]
        question = f"{symptom.capitalize()} — where do I start?"
        made.append(
            _record(
                f"trouble-{len(made) + 1:04d}",
                "troubleshooting",
                True,
                "en",
                _model_in(str(node["text"])),
                question,
                "answer",
                [node],
                [{"type": "step", "text": fact}],
                [],
            )
        )
    return made


def _follow_ups(nodes: list[dict[str, object]], texts: dict[str, str]) -> list[dict[str, object]]:
    made: list[dict[str, object]] = []
    for node in nodes:
        if node.get("lang") != "en" or len(str(node.get("text") or "")) > 400:
            continue
        text = str(node["text"])
        if "M998" not in text or "M1123" not in text:
            continue
        prior = "Does this instruction mention the M1123?"
        question = "And on the M998?"
        made.append(
            _record(
                f"follow-{len(made) + 1:04d}",
                "follow_up",
                True,
                "en",
                "M998",
                question,
                "answer",
                [node],
                [{"type": "value", "text": "M998"}],
                [],
                turns=[
                    {"role": "user", "text": prior},
                    {"role": "user", "text": question},
                ],
            )
        )
        if len(made) == 8:
            break
    return made


def _japanese(nodes: list[dict[str, object]], texts: dict[str, str]) -> list[dict[str, object]]:
    made: list[dict[str, object]] = []
    for node in nodes:
        if node.get("lang") != "ja" or node.get("type") not in {"section", "paragraph"}:
            continue
        text = str(node.get("text") or "")
        fact = _japanese_fact(text)
        if fact is None:
            continue
        everyday = len(made) % 2 == 0
        question = (
            f"「{fact[:12]}」について、やさしく言うと何ですか?"
            if everyday
            else f"別添52の「{fact[:12]}」には何と書かれていますか?"
        )
        made.append(
            _record(
                f"lookup-ja-{len(made) + 1:04d}",
                "lookup",
                everyday,
                "ja",
                None,
                question,
                "answer",
                [node],
                [{"type": "value", "text": fact}],
                [],
            )
        )
        if len(made) == 10:
            break
    return made


def _record(
    qid: str,
    question_type: str,
    everyday: bool,
    language: str,
    model: str | None,
    question: str,
    action: str,
    gold_nodes: list[dict[str, object]],
    facts: list[dict[str, str]],
    forbidden: list[dict[str, str]],
    turns: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    return {
        "id": qid,
        "slice": {
            "question_type": question_type,
            "vocabulary": "user" if everyday else "manual",
            "language": language,
            "model": model,
        },
        "question": question,
        "expected_action": action,
        "gold": {
            "doc_keys": [str(node["doc_key"]) for node in gold_nodes],
            "pages": [int(str(node["page_start"])) for node in gold_nodes],
            "node_ids": [str(node["node_id"]) for node in gold_nodes],
        },
        "required_facts": facts,
        "forbidden_facts": forbidden,
        "turns": turns,
        "notes": f"written by {AUTHOR}, {_DATE}",
    }


def _fault_part_pairs(
    nodes: list[dict[str, object]],
) -> list[tuple[dict[str, object], dict[str, object], str]]:
    rules = load_rules()
    parts = [node for node in nodes if _part_number(node) is not None]
    pairs: list[tuple[dict[str, object], dict[str, object], str]] = []
    for row in _malfunctions(nodes):
        number = str(row["table"]["cells"][0]).split(".", 1)[0]  # type: ignore[index]
        keywords = rules.part_keywords.get(number, [])
        if not keywords:
            continue
        keyword = keywords[0]
        match = next(
            (part for part in parts if keyword in _part_description(part).upper()),
            None,
        )
        if match is not None:
            pairs.append((row, match, keyword))
    return pairs


def _short_step_with(
    nodes: list[dict[str, object]], keyword: str, *, exclude: str
) -> dict[str, object] | None:
    folded = keyword.lower()
    for node in nodes:
        if node.get("type") != "step" or str(node.get("node_id")) == exclude:
            continue
        text = str(node.get("text") or "")
        if 40 <= len(text) <= 350 and folded in text.lower():
            return node
    return None


def _part_description(node: dict[str, object]) -> str:
    cells = _item_cells(node)
    if cells is None or len(cells) < 6:
        return ""
    return str(cells[5])


def _part_number(node: dict[str, object]) -> str | None:
    cells = _item_cells(node)
    if cells is None or len(cells) < 6:
        return None
    part_no = str(cells[4]).strip()
    description = str(cells[5]).strip()
    if len(part_no) < 5 or not description:
        return None
    return part_no


def _item_cells(node: dict[str, object]) -> list[object] | None:
    table = node.get("table")
    if node.get("type") != "table_row" or not isinstance(table, dict):
        return None
    headers = table.get("headers")
    cells = table.get("cells")
    if not isinstance(headers, list) or not isinstance(cells, list) or not headers:
        return None
    if headers[0] != "ITEM NO":
        return None
    return cells


def _malfunctions(nodes: list[dict[str, object]]) -> list[dict[str, object]]:
    return [node for node in nodes if _is_malfunction(node)]


def _is_malfunction(node: dict[str, object]) -> bool:
    table = node.get("table")
    if node.get("type") != "table_row" or not isinstance(table, dict):
        return False
    headers = table.get("headers")
    return isinstance(headers, list) and bool(headers) and headers[0] == "MALFUNCTION"


def _caution_for(prefix: str, nodes: list[dict[str, object]]) -> dict[str, object] | None:
    for node in nodes:
        if node.get("type") != "caution":
            continue
        if str(node.get("node_id", "")).startswith(prefix + ":"):
            return node
    return None


def _warning_fact(text: str) -> str | None:
    for marker in ("Do not drain oil when engine is hot", "WARNING", "CAUTION"):
        if marker in text:
            return marker if marker != "WARNING" and marker != "CAUTION" else text[:80]
    return None


def _step_fact(text: str) -> str | None:
    match = _STEP_FACT.search(text)
    if match is None:
        return None
    fact = match.group(0).strip()
    if fact in text and len(fact) >= 12:
        return fact
    return None


def _japanese_fact(text: str) -> str | None:
    collapsed = " ".join(text.split())
    if len(collapsed) < 20:
        return None
    fact = collapsed[:40]
    if fact in collapsed:
        return fact
    return None


def _model_in(text: str) -> str | None:
    match = _MODEL.search(text)
    return match.group(0) if match else None


def _step_number(text: str) -> int:
    match = re.match(r"(\d+)", text)
    return int(match.group(1)) if match else 999


def _task_prefix(node_id: str) -> str:
    parts = node_id.split(":")
    while parts and (
        parts[-1].isdigit() or parts[-1].startswith("step-") or parts[-1].startswith("caution")
    ):
        parts.pop()
    return ":".join(parts)


def _load_nodes(nodes_dir: Path | None) -> list[dict[str, object]]:
    root = nodes_dir or NODES
    nodes: list[dict[str, object]] = []
    for path in sorted(root.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                nodes.append(loaded)
    nodes.sort(key=lambda node: str(node.get("node_id", "")))
    return nodes
