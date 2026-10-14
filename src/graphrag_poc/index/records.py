"""Passages and cases loaded for the index."""

import json
from dataclasses import dataclass
from pathlib import Path

from graphrag_poc.cases.rules import CASES_PATH
from graphrag_poc.ingest.catalog import NODES

PASSAGE_FIELDS = (
    "node_id",
    "doc_key",
    "page_start",
    "page_end",
    "type",
    "lang",
    "text",
    "breadcrumb",
)


@dataclass(frozen=True)
class Passage:
    """One retrievable node. The payload fields are the ones Step 5 requires."""

    node_id: str
    doc_key: str
    page_start: int
    page_end: int
    type: str
    lang: str
    text: str
    breadcrumb: tuple[str, ...]

    def payload(self) -> dict[str, object]:
        return {
            "node_id": self.node_id,
            "doc_key": self.doc_key,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "type": self.type,
            "lang": self.lang,
            "text": self.text,
            "breadcrumb": list(self.breadcrumb),
        }


@dataclass(frozen=True)
class CasePoint:
    """One service case. Exact-match fields are error_codes, parts, and model."""

    case_id: str
    model: str
    error_codes: tuple[str, ...]
    parts: tuple[str, ...]
    search_text: str
    payload: dict[str, object]


def load_passages(nodes_dir: Path | None = None) -> list[Passage]:
    """Retrievable nodes only. Boilerplate stays out of the passage collection."""

    passages: list[Passage] = []
    root = nodes_dir or NODES
    for path in sorted(root.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            node = json.loads(line)
            if not node.get("retrievable") or not str(node.get("text") or "").strip():
                continue
            breadcrumb = node.get("breadcrumb") or []
            passages.append(
                Passage(
                    node_id=str(node["node_id"]),
                    doc_key=str(node["doc_key"]),
                    page_start=int(node["page_start"]),
                    page_end=int(node["page_end"]),
                    type=str(node["type"]),
                    lang=str(node["lang"]),
                    text=str(node["text"]),
                    breadcrumb=tuple(str(item) for item in breadcrumb),
                )
            )
    passages.sort(key=lambda passage: passage.node_id)
    return passages


def load_cases(path: Path | None = None) -> list[CasePoint]:
    cases: list[CasePoint] = []
    source = path or CASES_PATH
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        record = json.loads(line)
        cases.append(
            CasePoint(
                case_id=str(record["case_id"]),
                model=str(record["model"]),
                error_codes=tuple(str(code) for code in record["error_codes"]),
                parts=tuple(str(part) for part in record["parts"]),
                search_text=str(record["search_text"]),
                payload=record,
            )
        )
    cases.sort(key=lambda case: case.case_id)
    return cases
