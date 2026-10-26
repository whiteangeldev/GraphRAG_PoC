"""Deterministic rule edges from the node files and the service cases.

MENTIONS is not produced here. That edge comes from a model in a later step.
"""

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from graphrag_poc.cases.rules import CASES_PATH, Rules, load_rules
from graphrag_poc.ingest.catalog import DOCUMENTS, NODES, DocumentSpec

_MODEL = re.compile(r"\bM\d{3,4}(?:A\d)?\b")
_NUMBERED = re.compile(r"^(\d+)\.")
_LETTERED = re.compile(r"^\(([0-9]+|[A-Za-z])\)")
_STEP_SPAN = re.compile(r"(Step\s+(\d+)\.(?:(?!Step\s+\d+\.).)*)", re.DOTALL)

RULE_NEXT = "numbered steps that share a task prefix"
RULE_CAUTION = "bound caution"
RULE_PARENT = "parent"
RULE_REFERS = "references"
RULE_DOCUMENT = "doc_key"
RULE_STATES = "malfunction table row"
RULE_STEP = "step span in the malfunction row"
RULE_APPLIES = "applies_to or model token in the text"
RULE_LISTS = "parts-list row"
RULE_PART = "part description contains the fault keyword"
RULE_ABOUT = "case error code"
RULE_INSTALLED = "case part number"
RULE_MODEL = "case model"


@dataclass(frozen=True)
class Edge:
    """One rule edge. A manual page or a case id is set, never both."""

    type: str
    start_id: str
    end_id: str
    rule: str
    doc_key: str = ""
    page_start: int = 0
    case_id: str = ""
    keyword: str = ""
    step_number: int = 0
    step_text: str = ""
    description: str = ""
    derived: bool = False
    weight: float = 1.0

    def __post_init__(self) -> None:
        has_page = bool(self.doc_key) and self.page_start >= 1
        has_case = bool(self.case_id)
        if has_page == has_case:
            raise ValueError(f"{self.type} needs a document page or a case id")
        if self.type == "MENTIONS":
            if not self.derived or not 0 < self.weight < 1:
                raise ValueError("MENTIONS is a derived edge and its weight is below 1")
        elif self.derived or self.weight != 1.0:
            raise ValueError("a rule edge has weight 1 and is not derived")
        if self.type == "CANDIDATE_PART" and not (self.keyword and self.description):
            raise ValueError("CANDIDATE_PART stores the keyword and the part description")
        if self.type == "HAS_STEP" and (self.step_number < 1 or not self.step_text):
            raise ValueError("HAS_STEP stores the step number and the step span")


@dataclass
class GraphData:
    """Nodes and edges ready to export. Lists are sorted."""

    documents: list[dict[str, str]] = field(default_factory=list)
    passages: list[dict[str, object]] = field(default_factory=list)
    malfunctions: list[dict[str, object]] = field(default_factory=list)
    parts: list[dict[str, str]] = field(default_factory=list)
    models: list[dict[str, str]] = field(default_factory=list)
    cases: list[dict[str, object]] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    def counts(self) -> dict[str, int]:
        totals: dict[str, int] = {
            "Document": len(self.documents),
            "Passage": len(self.passages),
            "Malfunction": len(self.malfunctions),
            "Part": len(self.parts),
            "Model": len(self.models),
            "Case": len(self.cases),
        }
        for edge in self.edges:
            totals[edge.type] = totals.get(edge.type, 0) + 1
        return dict(sorted(totals.items()))

    def fingerprint(self) -> str:
        digest = hashlib.sha256()
        for document in self.documents:
            digest.update(document["id"].encode())
        for passage in self.passages:
            digest.update(str(passage["id"]).encode())
            digest.update(str(passage["text"]).encode())
        for malfunction in self.malfunctions:
            digest.update(str(malfunction["id"]).encode())
        for part in self.parts:
            digest.update(part["id"].encode())
        for model in self.models:
            digest.update(model["id"].encode())
        for case in self.cases:
            digest.update(str(case["id"]).encode())
        for edge in self.edges:
            digest.update(repr(edge).encode())
        return digest.hexdigest()


def build_from_disk(
    nodes_dir: Path | None = None,
    cases_path: Path | None = None,
    rules: Rules | None = None,
) -> GraphData:
    """Read the corpus and return one deterministic graph."""

    active = rules or load_rules()
    return build_graph(
        _load_jsonl(nodes_dir or NODES),
        _load_jsonl(cases_path or CASES_PATH),
        documents=[_document_row(spec) for spec in DOCUMENTS],
        part_keywords=active.part_keywords,
        min_part_length=active.min_part_length,
        known_models=set(active.family_models),
        fault_doc_key=active.fault_doc_key,
        fault_header=active.fault_header,
        parts_doc_key=active.parts_doc_key,
    )


def build_graph(
    nodes: list[dict[str, object]],
    cases: list[dict[str, object]],
    *,
    documents: list[dict[str, str]],
    part_keywords: dict[str, list[str]],
    min_part_length: int,
    known_models: set[str],
    fault_doc_key: str,
    fault_header: str,
    parts_doc_key: str,
) -> GraphData:
    """Create nodes and rule edges. Output order does not depend on input order."""

    passages = [node for node in nodes if node.get("retrievable") is True]
    by_node = {str(node["node_id"]): node for node in passages}
    steps = {node_id: node for node_id, node in by_node.items() if node.get("type") == "step"}
    docs = sorted(documents, key=lambda row: row["doc_key"])
    doc_ids = {row["doc_key"] for row in docs}
    passage_rows = [_passage_row(node) for node in passages]
    passage_rows.sort(key=lambda row: str(row["node_id"]))
    malfunctions = [
        _malfunction_row(node)
        for node in passages
        if _is_malfunction(node, fault_doc_key, fault_header)
    ]
    malfunctions.sort(key=lambda row: str(row["node_id"]))
    parts, listings = _parts(passages, parts_doc_key, min_part_length)
    model_names = _model_names(passages, cases, known_models)
    models = [
        {
            "id": f"model:{name}",
            "name": name,
            "series": "M998" if name in known_models else "",
        }
        for name in sorted(model_names)
    ]
    case_rows = sorted((_case_row(case) for case in cases), key=lambda row: str(row["case_id"]))
    edges = _edges(
        passages,
        by_node,
        steps,
        doc_ids,
        malfunctions,
        parts,
        listings,
        model_names,
        case_rows,
        part_keywords,
        known_models,
    )
    return GraphData(
        documents=docs,
        passages=passage_rows,
        malfunctions=malfunctions,
        parts=parts,
        models=models,
        cases=case_rows,
        edges=edges,
    )


def _edges(
    passages: list[dict[str, object]],
    by_node: dict[str, dict[str, object]],
    steps: dict[str, dict[str, object]],
    doc_ids: set[str],
    malfunctions: list[dict[str, object]],
    parts: list[dict[str, str]],
    listings: list[dict[str, str]],
    model_names: set[str],
    case_rows: list[dict[str, object]],
    part_keywords: dict[str, list[str]],
    known_models: set[str],
) -> list[Edge]:
    edges: dict[tuple[str, str, str, str, int, str], Edge] = {}
    _structure_edges(edges, passages, by_node, steps, doc_ids, model_names, known_models)
    _malfunction_edges(
        edges, malfunctions, by_node, parts, model_names, known_models, part_keywords
    )
    for row in listings:
        _add(
            edges,
            Edge(
                "LISTS",
                row["id"],
                f"passage:{row['node_id']}",
                RULE_LISTS,
                row["doc_key"],
                int(row["page_start"]),
            ),
        )
    _case_edges(edges, case_rows, malfunctions, parts, model_names)
    return sorted(edges.values(), key=_edge_key)


def _structure_edges(
    edges: dict[tuple[str, str, str, str, int, str], Edge],
    passages: list[dict[str, object]],
    by_node: dict[str, dict[str, object]],
    steps: dict[str, dict[str, object]],
    doc_ids: set[str],
    model_names: set[str],
    known_models: set[str],
) -> None:
    for node in passages:
        node_id = str(node["node_id"])
        start = f"passage:{node_id}"
        page = _page(node)
        doc_key = str(node.get("doc_key") or node_id.split(":", 1)[0])
        if doc_key in doc_ids:
            _add(edges, Edge("IN_DOCUMENT", start, f"doc:{doc_key}", RULE_DOCUMENT, doc_key, page))
        parent = str(node.get("parent") or "")
        if parent in by_node:
            _add(edges, Edge("PARENT", start, f"passage:{parent}", RULE_PARENT, doc_key, page))
        for caution_id in _id_list(node.get("bound_cautions")):
            caution = by_node.get(caution_id)
            if caution is not None and caution.get("type") == "caution":
                _add(
                    edges,
                    Edge(
                        "BOUND_CAUTION",
                        start,
                        f"passage:{caution_id}",
                        RULE_CAUTION,
                        doc_key,
                        page,
                    ),
                )
        for reference_id in _id_list(node.get("references")):
            if reference_id in by_node and reference_id != node_id:
                _add(
                    edges,
                    Edge(
                        "REFERS_TO",
                        start,
                        f"passage:{reference_id}",
                        RULE_REFERS,
                        doc_key,
                        page,
                    ),
                )
        for model in _models_for(node, known_models):
            if model in model_names:
                _add(
                    edges,
                    Edge("APPLIES_TO", start, f"model:{model}", RULE_APPLIES, doc_key, page),
                )
    for left, right in _next_pairs(steps):
        source = steps[left]
        doc_key = str(source.get("doc_key") or left.split(":", 1)[0])
        _add(
            edges,
            Edge("NEXT", f"passage:{left}", f"passage:{right}", RULE_NEXT, doc_key, _page(source)),
        )


def _malfunction_edges(
    edges: dict[tuple[str, str, str, str, int, str], Edge],
    malfunctions: list[dict[str, object]],
    by_node: dict[str, dict[str, object]],
    parts: list[dict[str, str]],
    model_names: set[str],
    known_models: set[str],
    part_keywords: dict[str, list[str]],
) -> None:
    catalog = [(row["id"], row["description"]) for row in parts]
    for row in malfunctions:
        doc_key = str(row["doc_key"])
        page = int(str(row["page_start"]))
        start = str(row["id"])
        _add(edges, Edge("STATES", start, f"passage:{row['node_id']}", RULE_STATES, doc_key, page))
        source = by_node[str(row["node_id"])]
        for model in _models_for(source, known_models):
            if model in model_names:
                _add(
                    edges,
                    Edge("APPLIES_TO", start, f"model:{model}", RULE_APPLIES, doc_key, page),
                )
        for match in _STEP_SPAN.finditer(str(row["text"])):
            _add(
                edges,
                Edge(
                    "HAS_STEP",
                    start,
                    f"passage:{row['node_id']}",
                    RULE_STEP,
                    doc_key,
                    page,
                    step_number=int(match.group(2)),
                    step_text=match.group(1).strip(),
                ),
            )
        number = str(row["code"]).split(".", 1)[0].strip()
        # INJECT is a substring of unrelated words and matches no approved part description.
        keywords = [word for word in part_keywords.get(number, []) if word.upper() != "INJECT"]
        for part_id, description in catalog:
            keyword = next((word for word in keywords if word.upper() in description.upper()), None)
            if keyword is None:
                continue
            _add(
                edges,
                Edge(
                    "CANDIDATE_PART",
                    start,
                    part_id,
                    RULE_PART,
                    doc_key,
                    page,
                    keyword=keyword,
                    description=description,
                ),
            )


def _case_edges(
    edges: dict[tuple[str, str, str, str, int, str], Edge],
    case_rows: list[dict[str, object]],
    malfunctions: list[dict[str, object]],
    parts: list[dict[str, str]],
    model_names: set[str],
) -> None:
    by_code: dict[str, list[str]] = {}
    for row in malfunctions:
        by_code.setdefault(str(row["code"]), []).append(str(row["id"]))
    part_ids = {row["part_number"]: row["id"] for row in parts}
    for case in case_rows:
        case_key = str(case["id"])
        case_id = str(case["case_id"])
        for code in _id_list(case.get("error_codes")):
            for malfunction_id in by_code.get(code, []):
                _add(edges, Edge("ABOUT", case_key, malfunction_id, RULE_ABOUT, case_id=case_id))
        for part_number in _id_list(case.get("parts")):
            part_id = part_ids.get(part_number)
            if part_id is not None:
                _add(edges, Edge("INSTALLED", case_key, part_id, RULE_INSTALLED, case_id=case_id))
        model = str(case.get("model") or "")
        if model in model_names:
            _add(edges, Edge("ON_MODEL", case_key, f"model:{model}", RULE_MODEL, case_id=case_id))


def _next_pairs(steps: dict[str, dict[str, object]]) -> set[tuple[str, str]]:
    """Follow the sibling list.

    A step stores its neighbors as previous, then next. Step numbers restart
    inside one task, so the list order is the procedure order.
    """

    pairs: set[tuple[str, str]] = set()
    for node_id, node in steps.items():
        siblings = _step_siblings(node, steps)
        if len(siblings) == 2:
            pairs.add((node_id, siblings[1]))
            continue
        if len(siblings) != 1:
            continue
        other = siblings[0]
        other_siblings = _step_siblings(steps[other], steps)
        chain_start = len(other_siblings) == 2 and other_siblings[0] == node_id
        pair = len(other_siblings) == 1 and _order_key(node) < _order_key(steps[other])
        if chain_start or pair:
            pairs.add((node_id, other))
    return pairs


def _step_siblings(node: dict[str, object], steps: dict[str, dict[str, object]]) -> list[str]:
    return [item for item in _id_list(node.get("siblings")) if item in steps]


def _order_key(node: dict[str, object]) -> tuple[int, int, str]:
    text = str(node.get("text") or "").lstrip()
    node_id = str(node.get("node_id") or "")
    numbered = _NUMBERED.match(text)
    if numbered is not None:
        return (0, int(numbered.group(1)), node_id)
    lettered = _LETTERED.match(text)
    if lettered is not None:
        token = lettered.group(1)
        value = int(token) if token.isdigit() else ord(token.lower())
        return (1, value, node_id)
    return (2, 0, node_id)


def _model_names(
    passages: list[dict[str, object]],
    cases: list[dict[str, object]],
    known_models: set[str],
) -> set[str]:
    names: set[str] = set()
    for node in passages:
        names.update(_models_for(node, known_models))
    for case in cases:
        model = str(case.get("model") or "").strip()
        if model:
            names.add(model)
    return names


def _models_for(node: dict[str, object], known_models: set[str]) -> list[str]:
    found: set[str] = set()
    applies = node.get("applies_to")
    if isinstance(applies, dict):
        raw = applies.get("models")
        if isinstance(raw, list):
            found.update(str(item).strip() for item in raw if str(item).strip())
    for token in _MODEL.findall(str(node.get("text") or "")):
        if token in known_models:
            found.add(token)
    return sorted(found)


def _parts(
    nodes: list[dict[str, object]],
    parts_doc_key: str,
    min_length: int,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    chosen: dict[str, dict[str, str]] = {}
    listings: list[dict[str, str]] = []
    for node in nodes:
        if str(node.get("doc_key") or "") != parts_doc_key:
            continue
        cells = _item_cells(node)
        if cells is None or len(cells) < 6:
            continue
        number = cells[4].strip()
        description = cells[5].strip()
        if len(number) < min_length or not description:
            continue
        row = {
            "id": f"part:{number}",
            "part_number": number,
            "description": description,
            "nsn": cells[2].strip(),
            "node_id": str(node["node_id"]),
            "doc_key": parts_doc_key,
            "page_start": str(_page(node)),
        }
        listings.append(row)
        current = chosen.get(number)
        if current is None or row["node_id"] < current["node_id"]:
            chosen[number] = row
    return [chosen[number] for number in sorted(chosen)], listings


def _passage_row(node: dict[str, object]) -> dict[str, object]:
    node_id = str(node["node_id"])
    return {
        "id": f"passage:{node_id}",
        "node_id": node_id,
        "text": str(node.get("text") or ""),
        "type": str(node.get("type") or ""),
        "page_start": _page(node),
        "page_end": _page(node, "page_end"),
        "lang": str(node.get("lang") or ""),
        "doc_key": str(node.get("doc_key") or node_id.split(":", 1)[0]),
        "breadcrumb": _id_list(node.get("breadcrumb")),
    }


def _malfunction_row(node: dict[str, object]) -> dict[str, object]:
    node_id = str(node["node_id"])
    return {
        "id": f"malfunction:{node_id}",
        "node_id": node_id,
        "code": _cell(node, 0).strip(),
        "page_start": _page(node),
        "text": str(node.get("text") or ""),
        "doc_key": str(node.get("doc_key") or node_id.split(":", 1)[0]),
    }


def _case_row(case: dict[str, object]) -> dict[str, object]:
    case_id = str(case["case_id"])
    frequency = case.get("frequency")
    return {
        "id": f"case:{case_id}",
        "case_id": case_id,
        "date": str(case.get("date") or ""),
        "model": str(case.get("model") or ""),
        "symptom": str(case.get("symptom") or ""),
        "cause": str(case.get("cause") or ""),
        "action": str(case.get("action") or ""),
        "frequency": frequency if _is_int(frequency) else 1,
        "error_codes": _id_list(case.get("error_codes")),
        "parts": _id_list(case.get("parts")),
    }


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _document_row(spec: DocumentSpec) -> dict[str, str]:
    return {
        "id": f"doc:{spec.doc_key}",
        "doc_key": spec.doc_key,
        "title": spec.title,
        "lang": spec.lang,
        "doc_type": spec.doc_type.value,
        "edition": spec.edition,
    }


def _is_malfunction(node: dict[str, object], doc_key: str, header: str) -> bool:
    if str(node.get("doc_key") or "") != doc_key or node.get("type") != "table_row":
        return False
    table = node.get("table")
    if not isinstance(table, dict):
        return False
    headers = table.get("headers")
    cells = table.get("cells")
    if not isinstance(headers, list) or not headers or headers[0] != header:
        return False
    return isinstance(cells, list) and bool(cells) and bool(str(cells[0]).strip())


def _item_cells(node: dict[str, object]) -> list[str] | None:
    table = node.get("table")
    if node.get("type") != "table_row" or not isinstance(table, dict):
        return None
    headers = table.get("headers")
    cells = table.get("cells")
    if not isinstance(headers, list) or not isinstance(cells, list) or not headers:
        return None
    if headers[0] != "ITEM NO":
        return None
    return [str(item) for item in cells]


def _cell(node: dict[str, object], index: int) -> str:
    table = node.get("table")
    if not isinstance(table, dict):
        return ""
    cells = table.get("cells")
    if not isinstance(cells, list) or index >= len(cells):
        return ""
    return str(cells[index])


def _page(node: dict[str, object], key: str = "page_start") -> int:
    value = node.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        value = node.get("page_start")
    if isinstance(value, int) and not isinstance(value, bool) and value >= 1:
        return value
    return 1


def _id_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    files = sorted(path.glob("*.jsonl")) if path.is_dir() else [path]
    rows: list[dict[str, object]] = []
    for file in files:
        for line in file.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                rows.append(loaded)
    return rows


def _add(edges: dict[tuple[str, str, str, str, int, str], Edge], edge: Edge) -> None:
    edges.setdefault(_edge_key(edge), edge)


def _edge_key(edge: Edge) -> tuple[str, str, str, str, int, str]:
    return (edge.type, edge.start_id, edge.end_id, edge.keyword, edge.step_number, edge.step_text)
