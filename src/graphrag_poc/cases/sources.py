"""Read fault rows and part numbers out of the node files."""

import json
import re
from dataclasses import dataclass
from pathlib import Path

from graphrag_poc.cases.rules import Rules
from graphrag_poc.ingest.catalog import NODES

_STEP = re.compile(r"\bStep\s+\d+\.\s*")
_IF = re.compile(r"(?<=[.)])\s+If\s+")
_IF_PREFIX = re.compile(
    r"^(?:not|any of these conditions exist),\s*",
    re.IGNORECASE,
)
_TITLE = re.compile(r"^\d+\.\s+(.*)$")
_PAGE_MARK = re.compile(r"\s+Change\s+\d.*$")


@dataclass(frozen=True)
class CatalogPart:
    """A part number and the description stored on its parts-list row."""

    number: str
    description: str


@dataclass(frozen=True)
class Fault:
    """One malfunction row and the cause/action pairs taken from its steps."""

    node_id: str
    code: str
    symptom: str
    steps: tuple[tuple[str, str], ...]
    models: tuple[str, ...]


def load_faults(rules: Rules, nodes_dir: Path | None = None) -> list[Fault]:
    faults: list[Fault] = []
    for node in _rows(rules.fault_doc_key, nodes_dir):
        table = node.get("table")
        if not isinstance(table, dict):
            continue
        headers = table.get("headers")
        cells = table.get("cells")
        if not isinstance(headers, list) or not isinstance(cells, list):
            continue
        if not headers or headers[0] != rules.fault_header or len(cells) < 2:
            continue
        code = _norm(str(cells[0]))
        body = _norm(str(cells[1]))
        if not code or not body:
            continue
        title = _TITLE.match(code)
        symptom = title.group(1) if title else code
        steps = tuple(parse_steps(body))
        faults.append(
            Fault(
                node_id=str(node["node_id"]),
                code=code,
                symptom=symptom,
                steps=steps,
                models=tuple(_models(node)),
            )
        )
    faults.sort(key=lambda fault: fault.node_id)
    if not faults:
        raise ValueError(f"no {rules.fault_header} rows in {rules.fault_doc_key}")
    return faults


def load_parts(rules: Rules, nodes_dir: Path | None = None) -> list[CatalogPart]:
    found: dict[str, str] = {}
    for node in _rows(rules.parts_doc_key, nodes_dir):
        table = node.get("table")
        if not isinstance(table, dict):
            continue
        headers = table.get("headers")
        cells = table.get("cells")
        if not isinstance(headers, list) or not isinstance(cells, list):
            continue
        if rules.part_header not in headers or "DESCRIPTION" not in headers:
            continue
        part = _norm(str(cells[headers.index(rules.part_header)]))
        description = _norm(str(cells[headers.index("DESCRIPTION")]))
        if len(part) < rules.min_part_length or not description:
            continue
        found[part] = _clean_join(found.get(part, ""), description)
    parts = [CatalogPart(number, found[number]) for number in sorted(found)]
    if not parts:
        raise ValueError(f"no {rules.part_header} values in {rules.parts_doc_key}")
    return parts


def load_stated_models(doc_key: str, nodes_dir: Path | None = None) -> set[str]:
    """Models named on nodes of one document."""

    stated: set[str] = set()
    for node in _rows(doc_key, nodes_dir):
        stated.update(_models(node))
    return stated


def cell_values(nodes_dir: Path | None = None) -> set[str]:
    """Every table cell in the corpus, used to prove codes and parts are real."""

    values: set[str] = set()
    root = nodes_dir or NODES
    for path in sorted(root.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            node = json.loads(line)
            table = node.get("table")
            if not isinstance(table, dict):
                continue
            cells = table.get("cells")
            if isinstance(cells, list):
                values.update(_norm(str(cell)) for cell in cells if _norm(str(cell)))
    return values


def parse_steps(body: str) -> list[tuple[str, str]]:
    """Split a malfunction body into (cause, action) pairs taken from its own steps."""

    normalized = _norm(body)
    chunks = [chunk.strip(" .") for chunk in _STEP.split(normalized) if chunk.strip(" .")]
    if not chunks:
        chunks = [normalized]
    steps: list[tuple[str, str]] = []
    for chunk in chunks:
        match = _IF.search(chunk)
        if match:
            cause = chunk[: match.start()].strip(" .") or chunk
            action = _IF_PREFIX.sub("", chunk[match.end() :]).strip(" .") or chunk
        else:
            pieces = _sentences(chunk)
            if len(pieces) >= 2:
                cause = pieces[0]
                action = ". ".join(pieces[1:])
            else:
                cause = chunk
                action = chunk
        steps.append(
            (
                _PAGE_MARK.sub("", cause).strip(" ."),
                _PAGE_MARK.sub("", action).strip(" ."),
            )
        )
    return steps


def _sentences(text: str) -> list[str]:
    """Split outside references; `para. 2-23` is not a sentence boundary."""

    pieces: list[str] = []
    start = depth = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "." and not depth and text[index + 1 : index + 2] == " ":
            word = text[start : index + 1].lower().split()[-1]
            if word in {"para.", "paras.", "fig.", "figs.", "no.", "e.g.", "i.e."}:
                continue
            piece = text[start:index].strip(" .")
            if piece:
                pieces.append(piece)
            start = index + 1
    remaining = text[start:].strip(" .")
    if remaining:
        pieces.append(remaining)
    return pieces


def usable_step(cause: str, action: str) -> bool:
    """An informative diagnostic instruction with an actionable, sourced response.

    This does not turn an inspection into a confirmed field diagnosis.
    """

    cause = _norm(cause).strip(" .")
    action = _norm(action).strip(" .")
    if len(cause.split()) < 2 or len(action.split()) < 2 or cause == action:
        return False
    if cause.lower() in {"all causes", "other causes"}:
        return False
    if "notify unit maintenance" in action.lower():
        corrective = action.lower().split("notify unit maintenance", 1)[0]
        return bool(
            re.search(
                r"\b(add|adjust|charge|clean|disengage|drain|engage|fill|inflate|deflate|"
                r"place|purge|remove|replace|secure|select|start|tighten)\b",
                corrective,
                re.IGNORECASE,
            )
        )
    return True


def _rows(doc_key: str, nodes_dir: Path | None) -> list[dict[str, object]]:
    path = (nodes_dir or NODES) / f"{doc_key}.jsonl"
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line:
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                rows.append(loaded)
    return rows


def _models(node: dict[str, object]) -> list[str]:
    applies = node.get("applies_to")
    if not isinstance(applies, dict):
        return []
    models = applies.get("models")
    if not isinstance(models, list):
        return []
    return [_norm(str(model)) for model in models if _norm(str(model))]


def _norm(text: str) -> str:
    return " ".join(text.split())


def _clean_join(left: str, right: str) -> str:
    return _norm(f"{left} {right}")
