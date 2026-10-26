"""Write the rule graph as neo4j-admin CSV."""

import csv
from collections.abc import Iterable
from pathlib import Path

from graphrag_poc.graph.build import Edge, GraphData
from graphrag_poc.ingest.catalog import ROOT

IMPORT_DIR = ROOT / "data" / "graph" / "import"

_NODE_FILES: dict[str, tuple[str, list[str]]] = {
    "documents.csv": (
        "Document",
        [":ID", "doc_key", "title", "lang", "doc_type", "edition"],
    ),
    "passages.csv": (
        "Passage",
        [
            ":ID",
            "node_id",
            "text",
            "type",
            "page_start:int",
            "page_end:int",
            "lang",
            "doc_key",
            "breadcrumb:string[]",
        ],
    ),
    "malfunctions.csv": (
        "Malfunction",
        [":ID", "node_id", "code", "page_start:int", "text", "doc_key"],
    ),
    "parts.csv": (
        "Part",
        [":ID", "part_number", "description", "nsn", "node_id", "doc_key", "page_start:int"],
    ),
    "models.csv": (
        "Model",
        [":ID", "name", "series:string[]"],
    ),
    "cases.csv": (
        "Case",
        [
            ":ID",
            "case_id",
            "date",
            "model",
            "symptom",
            "cause",
            "action",
            "frequency:int",
            "error_codes:string[]",
            "parts:string[]",
        ],
    ),
}

_PAGE_HEADER = [
    ":START_ID",
    ":END_ID",
    ":TYPE",
    "rule",
    "doc_key",
    "page_start:int",
    "derived:boolean",
    "weight:double",
    "keyword",
    "step_number",
    "step_text",
    "description",
]
_CASE_HEADER = [
    ":START_ID",
    ":END_ID",
    ":TYPE",
    "rule",
    "case_id",
    "derived:boolean",
    "weight:double",
]


def write_csv(graph: GraphData, directory: Path | None = None) -> Path:
    """Replace import CSV for this graph. The directory is gitignored."""

    target = directory or IMPORT_DIR
    target.mkdir(parents=True, exist_ok=True)
    for path in target.glob("*.csv"):
        path.unlink()
    _write_nodes(target, graph)
    page_edges = [edge for edge in graph.edges if edge.doc_key]
    case_edges = [edge for edge in graph.edges if edge.case_id]
    if len(page_edges) + len(case_edges) != len(graph.edges):
        raise ValueError("every edge needs a document page or a case id")
    _write(target / "page_edges.csv", _PAGE_HEADER, (_page_edge(edge) for edge in page_edges))
    _write(target / "case_edges.csv", _CASE_HEADER, (_case_edge(edge) for edge in case_edges))
    return target


def _write_nodes(target: Path, graph: GraphData) -> None:
    rows = {
        "documents.csv": [_document(row) for row in graph.documents],
        "passages.csv": [_passage(row) for row in graph.passages],
        "malfunctions.csv": [_malfunction(row) for row in graph.malfunctions],
        "parts.csv": [_part(row) for row in graph.parts],
        "models.csv": [_model(row) for row in graph.models],
        "cases.csv": [_case(row) for row in graph.cases],
    }
    for name, (_, header) in _NODE_FILES.items():
        _write(target / name, header, rows[name])


def node_arguments() -> list[str]:
    """neo4j-admin --nodes arguments for the files write_csv creates."""

    arguments = [f"--nodes={label}=/import/{name}" for name, (label, _) in _NODE_FILES.items()]
    arguments.append("--relationships=/import/page_edges.csv")
    arguments.append("--relationships=/import/case_edges.csv")
    return arguments


def _document(row: dict[str, str]) -> list[object]:
    return [row["id"], row["doc_key"], row["title"], row["lang"], row["doc_type"], row["edition"]]


def _passage(row: dict[str, object]) -> list[object]:
    return [
        row["id"],
        row["node_id"],
        row["text"],
        row["type"],
        row["page_start"],
        row["page_end"],
        row["lang"],
        row["doc_key"],
        _array(row["breadcrumb"]),
    ]


def _malfunction(row: dict[str, object]) -> list[object]:
    return [row["id"], row["node_id"], row["code"], row["page_start"], row["text"], row["doc_key"]]


def _part(row: dict[str, str]) -> list[object]:
    return [
        row["id"],
        row["part_number"],
        row["description"],
        row["nsn"],
        row["node_id"],
        row["doc_key"],
        int(row["page_start"]),
    ]


def _model(row: dict[str, str]) -> list[object]:
    return [row["id"], row["name"], row["series"]]


def _case(row: dict[str, object]) -> list[object]:
    return [
        row["id"],
        row["case_id"],
        row["date"],
        row["model"],
        row["symptom"],
        row["cause"],
        row["action"],
        row["frequency"],
        _array(row["error_codes"]),
        _array(row["parts"]),
    ]


def _page_edge(edge: Edge) -> list[object]:
    return [
        edge.start_id,
        edge.end_id,
        edge.type,
        edge.rule,
        edge.doc_key,
        edge.page_start,
        "true" if edge.derived else "false",
        f"{edge.weight:.4f}",
        edge.keyword,
        str(edge.step_number) if edge.step_number else "",
        edge.step_text,
        edge.description,
    ]


def _case_edge(edge: Edge) -> list[object]:
    return [
        edge.start_id,
        edge.end_id,
        edge.type,
        edge.rule,
        edge.case_id,
        "false",
        "1.0",
    ]


def _array(value: object) -> str:
    if isinstance(value, list):
        items = value
    elif isinstance(value, str) and value:
        items = [value]
    else:
        items = []
    cleaned = [str(item).replace("|", "/").replace("\n", " ") for item in items]
    return "|".join(item for item in cleaned if item)


def _write(path: Path, header: list[str], rows: Iterable[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
