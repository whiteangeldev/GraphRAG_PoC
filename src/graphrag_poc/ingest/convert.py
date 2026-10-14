"""Convert approved PDFs to one JSONL node file each."""

import json
from collections.abc import Sequence
from pathlib import Path

from graphrag_poc.ingest.catalog import DOCUMENTS, NODES, DocumentSpec
from graphrag_poc.ingest.extract import extract_document
from graphrag_poc.ingest.structure import build_nodes
from graphrag_poc.ingest.validate import validate_nodes
from graphrag_poc.models import Node, NodeType


def convert_document(spec: DocumentSpec, pages: Sequence[int] | None = None) -> list[Node]:
    """Convert one PDF. `pages` is an optional 1-based slice used by tests."""

    content, boilerplate, pdf_pages = extract_document(
        str(spec.path),
        lang=spec.lang,
        doc_type=spec.doc_type,
        pages=pages,
    )
    cover = list(pages) if pages is not None else list(range(1, pdf_pages + 1))
    return build_nodes(spec, content, boilerplate, pdf_pages, cover)


def write_nodes(path: Path, nodes: list[Node]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for node in nodes:
            payload = node.model_dump(mode="json")
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")


def convert_all(doc_keys: Sequence[str] | None = None) -> dict[str, list[str]]:
    """Write `data/nodes/{doc_key}.jsonl` and return validation errors by doc key."""

    selected = [spec for spec in DOCUMENTS if doc_keys is None or spec.doc_key in doc_keys]
    known = {spec.doc_key for spec in selected}
    unknown = [] if doc_keys is None else sorted(set(doc_keys) - known)
    if unknown:
        raise KeyError(f"unknown doc_key: {', '.join(unknown)}")

    errors: dict[str, list[str]] = {}
    for spec in selected:
        print(f"converting {spec.doc_key} ({spec.filename})", flush=True)
        nodes = convert_document(spec)
        destination = NODES / f"{spec.doc_key}.jsonl"
        write_nodes(destination, nodes)
        page_count = max(node.page_end for node in nodes)
        doc_errors = validate_nodes(nodes, list(range(1, page_count + 1)))
        errors[spec.doc_key] = doc_errors
        counts = _counts(nodes)
        print(
            f"  {len(nodes)} nodes, {counts['table_row']} table rows, "
            f"{counts['caution']} cautions, {counts['step']} steps"
            + ("" if not doc_errors else f", {len(doc_errors)} validation errors"),
            flush=True,
        )
    return errors


def _counts(nodes: list[Node]) -> dict[str, int]:
    counts = {kind.value: 0 for kind in NodeType}
    for node in nodes:
        counts[node.type.value] += 1
    return counts
