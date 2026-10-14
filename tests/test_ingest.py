"""Converter checks: links, page coverage, and samples against the source pages."""

from graphrag_poc.ingest.catalog import BY_KEY, NODES
from graphrag_poc.ingest.convert import convert_document
from graphrag_poc.ingest.extract import RawLine
from graphrag_poc.ingest.normalize import normalize_text
from graphrag_poc.ingest.structure import build_nodes
from graphrag_poc.ingest.validate import validate_nodes
from graphrag_poc.models import Node, NodeType


def _line(
    page: int,
    text: str,
    *,
    y: float = 100,
    x0: float = 60,
    x1: float = 500,
    tokens: tuple[tuple[float, str], ...] | None = None,
) -> RawLine:
    if tokens is None:
        tokens = tuple((x0, word) for word in text.split())
    return RawLine(page, x0, y, x1, y + 10, text, tokens)


def _types(nodes: list[Node], node_type: NodeType) -> list[Node]:
    return [node for node in nodes if node.type is node_type]


def test_warning_is_bound_to_the_following_step() -> None:
    spec = BY_KEY["tm280_20_2"]
    lines = [
        _line(1, "3-8. ENGINE OIL COOLER MAINTENANCE", y=70),
        _line(1, "WARNING", y=100),
        _line(1, "Do not drain oil when engine is hot.", y=120),
        _line(1, "1. Disconnect two engine oil cooler supply and return lines.", y=150),
    ]
    nodes = build_nodes(spec, lines, {}, 1, [1])
    assert validate_nodes(nodes, [1]) == []

    step = next(node for node in _types(nodes, NodeType.STEP) if "Disconnect" in node.text)
    caution = next(node for node in nodes if node.node_id == step.bound_cautions[0])
    assert caution.type is NodeType.CAUTION
    assert "Do not drain oil when engine is hot." in caution.text
    assert caution.parent == step.node_id
    procedure = next(node for node in nodes if node.node_id == step.parent)
    assert procedure.type is NodeType.PROCEDURE
    assert procedure.node_id == "tm280_20_2:3-8"


def test_parts_row_keeps_nsn_and_usable_on_code() -> None:
    spec = BY_KEY["tm280_24p_1"]
    item = _line(
        1,
        "22 PFOZZ 5340012564517 34623 5596028 BRACKET,DOUBLE 8",
        tokens=(
            (52.0, "22"),
            (70.0, "PFOZZ"),
            (106.0, "5340012564517"),
            (190.0, "34623"),
            (226.0, "5596028"),
            (328.0, "BRACKET,DOUBLE"),
            (562.0, "8"),
        ),
    )
    continuation = _line(1, "UOC:B17,B18", y=120, tokens=((328.0, "UOC:B17,B18"),))
    nodes = build_nodes(spec, [item, continuation], {}, 1, [1])
    assert validate_nodes(nodes, [1]) == []
    row = _types(nodes, NodeType.TABLE_ROW)[0]
    assert row.table is not None
    assert row.table.headers[2] == "NSN"
    assert row.table.cells[2] == "5340012564517"
    assert row.table.cells[4] == "5596028"
    assert "B17" in row.table.cells[6]
    assert row.table.cells[7] == "8"


def test_japanese_heading_uses_the_same_path_after_normalization() -> None:
    full_width = "\uff11\uff12\uff13\uff21\u3000適用"
    assert normalize_text(full_width, lang="ja") == "123A 適用"
    spec = BY_KEY["mlit_b052"]
    lines = [
        _line(1, "1 適用範囲", y=120, x0=87, x1=200),
        _line(1, "本技術基準は灯火器に適用する。", y=140, x0=108, x1=400),
        _line(1, "2 定義", y=160, x0=87, x1=200),
        _line(1, "2.1 横断面とは、車両中心面に直交する鉛直面をいう。", y=180, x0=87, x1=400),
    ]
    nodes = build_nodes(spec, lines, {}, 1, [1])
    assert validate_nodes(nodes, [1]) == []
    clause = next(node for node in nodes if node.text.startswith("1 適用範囲"))
    assert clause.type is NodeType.SECTION
    assert clause.lang == "ja"
    assert "本技術基準は灯火器に適用する。" in clause.text
    child = next(node for node in nodes if node.node_id == "mlit_b052:2.1")
    assert child.parent == "mlit_b052:2"


def test_operator_procedure_matches_the_source_page() -> None:
    nodes = convert_document(BY_KEY["tm280_10"], pages=[200])
    assert validate_nodes(nodes, [200]) == []
    procedure = next(node for node in nodes if "OPERATING IN DUSTY, SANDY AREAS" in node.text)
    assert procedure.type is NodeType.PROCEDURE
    step = next(
        node for node in _types(nodes, NodeType.STEP) if "Reduce tire inflation" in node.text
    )
    assert step.parent is not None
    assert "12 psi" in step.text


def test_maintenance_caution_matches_the_source_page() -> None:
    nodes = convert_document(BY_KEY["tm280_20_2"], pages=[32])
    assert validate_nodes(nodes, [32]) == []
    title = "ENGINE AND TRANSMISSION OIL COOLER ASSEMBLY MAINTENANCE"
    procedure = next(node for node in nodes if title in node.text)
    assert procedure.type is NodeType.PROCEDURE
    step = next(
        node
        for node in _types(nodes, NodeType.STEP)
        if "Disconnect two engine oil cooler" in node.text
    )
    texts = [node.text for node in nodes if node.node_id in step.bound_cautions]
    assert any("Do not drain oil when engine is hot" in text for text in texts)


def test_fault_row_matches_the_operator_troubleshooting_table() -> None:
    nodes = convert_document(BY_KEY["tm280_10"], pages=[281])
    assert validate_nodes(nodes, [281]) == []
    row = next(
        node for node in _types(nodes, NodeType.TABLE_ROW) if "ENGINE FAILS TO CRANK" in node.text
    )
    assert row.table is not None
    assert "neutral" in row.table.cells[1].lower()
    step = next(
        node for node in _types(nodes, NodeType.STEP) if "transmission shift lever" in node.text
    )
    parent = next(node for node in nodes if node.node_id == step.parent)
    assert "ENGINE FAILS TO CRANK" in parent.text


def test_engine_calibration_row_matches_the_source_page() -> None:
    nodes = convert_document(BY_KEY["tm2815_34"], pages=[147])
    assert validate_nodes(nodes, [147]) == []
    row = next(
        node
        for node in _types(nodes, NodeType.TABLE_ROW)
        if node.table is not None and node.table.cells[0] == "150" and node.table.cells[1] == "WOT"
    )
    assert "28" in row.table.cells[2]
    assert any(node.applies_to.models and "DB2829-4523" in node.applies_to.models for node in nodes)


def test_parts_description_stays_on_its_item_row() -> None:
    nodes = convert_document(BY_KEY["tm280_24p_1"], pages=[46])
    assert validate_nodes(nodes, [46]) == []
    row = next(
        node
        for node in _types(nodes, NodeType.TABLE_ROW)
        if node.table is not None and "2815013147940" in node.table.cells
    )
    assert row.table is not None
    assert "5705628" in row.table.cells
    assert "ENGINE" in row.table.cells[5].upper()
    assert row.table.cells[5].count("ENGINE,WITH CONTAIN") <= 1


def test_wrapped_malfunction_title_stays_on_the_row() -> None:
    nodes = convert_document(BY_KEY["tm280_10"], pages=[281, 282, 286])
    assert validate_nodes(nodes, [281, 282, 286]) == []
    smoke = next(
        node
        for node in _types(nodes, NodeType.TABLE_ROW)
        if node.table is not None and node.table.cells[0].startswith("5. ")
    )
    assert smoke.table is not None
    assert "TEMPERATURE" in smoke.table.cells[0]
    assert "MALFUNCTION" not in smoke.table.cells[1]
    lights = next(
        node
        for node in _types(nodes, NodeType.TABLE_ROW)
        if node.table is not None and node.table.cells[0].startswith("26. ")
    )
    assert lights.table is not None
    assert lights.table.cells[0].endswith("ILLUMINATE")
    assert "M996" in lights.applies_to.models
    assert "M998" not in lights.applies_to.models


def test_belt_tension_table_is_a_row() -> None:
    nodes = convert_document(BY_KEY["tm280_20_2"], pages=[167])
    assert validate_nodes(nodes, [167]) == []
    row = next(
        node
        for node in _types(nodes, NodeType.TABLE_ROW)
        if node.table is not None and node.table.cells[0] == "All belts"
    )
    assert row.table is not None
    assert "105" in row.table.cells[1]
    assert "90" in row.table.cells[2]
    assert "(467" in row.table.cells[1]


def test_parts_page_matches_the_source_nsn() -> None:
    nodes = convert_document(BY_KEY["tm280_24p_1"], pages=[901])
    assert validate_nodes(nodes, [901]) == []
    row = next(
        node
        for node in _types(nodes, NodeType.TABLE_ROW)
        if node.table is not None and "5340012564517" in node.table.cells
    )
    assert "5596028" in row.table.cells


def test_japanese_sample_page_is_sectioned() -> None:
    nodes = convert_document(BY_KEY["mlit_b052"], pages=[1])
    assert validate_nodes(nodes, [1]) == []
    clause = next(
        node for node in nodes if "適用範囲" in node.text and node.type is not NodeType.BOILERPLATE
    )
    assert clause.lang == "ja"
    assert any(element.bbox[2] > element.bbox[0] for element in clause.elements)


def test_saved_node_files_cover_every_approved_page() -> None:
    missing = [
        spec.doc_key for spec in BY_KEY.values() if not (NODES / f"{spec.doc_key}.jsonl").exists()
    ]
    assert not missing, f"run make ingest first, missing {missing}"
    for spec in BY_KEY.values():
        nodes: list[Node] = []
        for line in (NODES / f"{spec.doc_key}.jsonl").read_text(encoding="utf-8").splitlines():
            if line:
                nodes.append(Node.model_validate_json(line))
        page_count = max(node.page_end for node in nodes)
        errors = validate_nodes(nodes, list(range(1, page_count + 1)))
        assert errors == [], errors[:8]
        assert all(node.doc_key == spec.doc_key for node in nodes)
        assert any(node.lang == spec.lang for node in nodes)
