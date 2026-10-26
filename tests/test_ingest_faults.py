"""Malfunction titles and corrective text keep their source table boundaries."""

import pytest

from graphrag_poc.cases.sources import parse_steps
from graphrag_poc.ingest.catalog import BY_KEY
from graphrag_poc.ingest.convert import convert_document
from graphrag_poc.ingest.extract import RawLine
from graphrag_poc.ingest.structure import build_nodes
from graphrag_poc.ingest.validate import validate_nodes
from graphrag_poc.models import Node, NodeType


def _line(text: str, y: float) -> RawLine:
    return RawLine(1, 75, y, 500, y + 10, text, ((75, text),))


def test_wrapped_title_stops_at_unnumbered_corrective_text() -> None:
    title = "5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING"
    continuation = "TEMPERATURE 190°-230°F (88°-110°C)"
    texts = [
        "Table 3-1. Troubleshooting",
        title,
        continuation,
        "All causes.",
        "Notify unit maintenance.",
        "OEM SUPPORT REQUIRED",
    ]
    nodes = build_nodes(
        BY_KEY["tm280_10"],
        [_line(text, 100 + 15 * index) for index, text in enumerate(texts)],
        {},
        1,
    )
    assert validate_nodes(nodes, [1]) == []
    row = next(node for node in nodes if node.type is NodeType.TABLE_ROW)
    assert row.table is not None
    assert row.table.cells == [
        f"{title} {continuation}",
        "All causes. Notify unit maintenance. OEM SUPPORT REQUIRED",
    ]
    assert [element.text for element in row.elements] == texts[1:]
    assert row.text.count(title) == 1


def test_corrective_preamble_is_preserved_before_numbered_steps() -> None:
    texts = [
        "Table 3-1. Troubleshooting",
        "1. ENGINE FAILS TO CRANK",
        "Use approved test equipment.",
        "Step 1. Check the battery connections.",
        "Notify unit maintenance if damaged.",
    ]
    nodes = build_nodes(
        BY_KEY["tm280_10"],
        [_line(text, 100 + 15 * index) for index, text in enumerate(texts)],
        {},
        1,
    )
    assert validate_nodes(nodes, [1]) == []
    row = next(node for node in nodes if node.type is NodeType.TABLE_ROW)
    assert row.table is not None
    assert row.table.cells == [texts[1], " ".join(texts[2:])]


@pytest.fixture(scope="module")
def source_fault_nodes() -> list[Node]:
    pages = list(range(281, 288))
    nodes = convert_document(BY_KEY["tm280_10"], pages=pages)
    assert validate_nodes(nodes, pages) == []
    return nodes


@pytest.fixture(scope="module")
def source_fault_rows(source_fault_nodes: list[Node]) -> dict[int, Node]:
    return {
        int(node.table.cells[0].split(".", 1)[0]): node
        for node in source_fault_nodes
        if node.type is NodeType.TABLE_ROW and node.table is not None
    }


@pytest.mark.parametrize(
    ("number", "title", "body"),
    [
        (11, "ROUGH SHIFTING", "All causes. Notify unit maintenance."),
        (15, "POOR SERVICE BRAKING ACTION", "All causes. Notify unit maintenance."),
        (16, "SERVICE BRAKES DRAGGING", "All causes. Notify unit maintenance."),
        (
            18,
            "PARKING BRAKE FAILS TO HOLD VEHICLE",
            "Clean and adjust parking brake (para. 3-13) "
            "If parking brake still fails to hold vehicle, notify unit maintenance.",
        ),
        (25, "CARGO SHELL DOOR WILL NOT SEAL PROPERLY", "All causes. Notify unit maintenance."),
    ],
)
def test_unnumbered_fault_body_matches_source(
    source_fault_rows: dict[int, Node], number: int, title: str, body: str
) -> None:
    row = source_fault_rows[number]
    label = f"{number}. {title}"
    assert row.table is not None
    assert row.table.cells == [label, body]
    assert row.text == f"{label} {body}"
    assert all(not cause.isdigit() for cause, _ in parse_steps(body))
    assert row.elements


def test_wrapped_heater_title_and_model_group_are_preserved(
    source_fault_rows: dict[int, Node],
) -> None:
    heater = source_fault_rows[9]
    assert heater.table is not None
    assert heater.table.cells[0] == (
        "9. HOT WATERPERSONNEL HEATER FAILS TO PRODUCE HEAT AFTER ENGINE "
        "REACHES OPERATING TEMPERATURE"
    )
    assert heater.table.cells[1].startswith("Step 1. Check operating controls")
    assert "M998" in heater.applies_to.models
    assert "M998" not in source_fault_rows[25].applies_to.models


@pytest.mark.parametrize(
    ("number", "included_model", "excluded_model"),
    [(22, "M998", None), (23, "M1038", "M966"), (25, "M966", "M996")],
)
def test_fault_keeps_its_original_model_group(
    source_fault_rows: dict[int, Node],
    number: int,
    included_model: str,
    excluded_model: str | None,
) -> None:
    models = source_fault_rows[number].applies_to.models
    assert included_model in models
    if excluded_model is not None:
        assert excluded_model not in models


def test_faults_remain_in_their_source_table(source_fault_nodes: list[Node]) -> None:
    by_id = {node.node_id: node for node in source_fault_nodes}
    titles = {
        node.table.cells[0]
        for node in source_fault_nodes
        if node.type is NodeType.TABLE_ROW and node.table is not None
    }
    for node in source_fault_nodes:
        if node.type is NodeType.TABLE_ROW:
            assert node.parent is not None
            table = by_id[node.parent]
            assert table.type is NodeType.TABLE
            assert table.page_start == node.page_start
            assert table.parent is not None
            assert by_id[table.parent].type is not NodeType.PROCEDURE
            assert not titles.intersection(table.breadcrumb)


def test_numbered_steps_can_continue_across_a_table_header() -> None:
    texts = [
        "Table 3-1. Troubleshooting",
        "ENGINE",
        "1. ENGINE FAILS TO CRANK",
        "Step 1. Check the battery connections.",
        "Table 3-1.Troubleshooting (Cont'd)",
        "Step 2. Check the starter.",
        "WINCH",
        "2. WINCH STOPS DURING NORMAL OPERATION",
        "Step 1. Check the clutch lever.",
    ]
    nodes = build_nodes(
        BY_KEY["tm280_10"],
        [_line(text, 100 + 15 * index) for index, text in enumerate(texts)],
        {},
        1,
    )
    assert validate_nodes(nodes, [1]) == []
    first = next(
        node
        for node in nodes
        if node.type is NodeType.TABLE_ROW
        and node.table is not None
        and node.table.cells[0] == texts[2]
    )
    assert first.table is not None
    assert first.table.cells[1] == f"{texts[3]} {texts[5]}"
    assert first.parent == "tm280_10:table:3-1"
    assert "M998" in first.applies_to.models
