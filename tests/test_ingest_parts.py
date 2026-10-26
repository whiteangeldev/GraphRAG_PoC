"""Parts-column regressions checked against source layout and actual PDF rows."""

import pytest

from graphrag_poc.ingest.catalog import BY_KEY
from graphrag_poc.ingest.convert import convert_document
from graphrag_poc.ingest.extract import RawLine
from graphrag_poc.ingest.structure import _parse_parts
from graphrag_poc.ingest.validate import validate_nodes
from graphrag_poc.models import NodeType


def _line(tokens: tuple[tuple[float, str], ...]) -> RawLine:
    return RawLine(1, tokens[0][0], 100, 570, 110, " ".join(t for _, t in tokens), tokens)


@pytest.mark.parametrize(
    ("nsn", "cage", "part"),
    [
        ("5310011861254", "7X677", "11501032"),
        ("2530014912681", "K5667", "1202359"),
        ("5310008094061", "96906", "MS27183-15"),
        ("", "19207", "12460163-9"),
        ("", "7X677", "11501032"),
        ("5330014255069", "73165", "91598"),
        ("5330014255069", "73165", "A1234"),
        ("5330014255069", "", "A1234"),
        ("", "", "91598"),
        ("", "19207", "1234567890123"),
    ],
)
def test_parts_fields_follow_columns_with_optional_nsn_and_cage(
    nsn: str, cage: str, part: str
) -> None:
    tokens = [(52.0, "3"), (70.0, "PAFZZ")]
    if nsn:
        tokens.append((106.0, nsn))
    if cage:
        tokens.append((190.0, cage))
    tokens.extend([(226.0, part), (328.0, ".WASHER,FLAT"), (562.0, "8")])

    parsed = _parse_parts(_line(tuple(tokens)))

    assert parsed is not None
    assert (parsed.item, parsed.smr) == ("3", "PAFZZ")
    assert (parsed.nsn, parsed.cage, parsed.part) == (nsn, cage, part)
    assert (parsed.desc, parsed.qty) == ("WASHER,FLAT", "8")


@pytest.mark.parametrize(
    "tokens",
    [
        ((359.0, "1000"), (389.0, "FRONT"), (425.0, "AXLE"), (455.0, "ASSEMBLY")),
        ((52.0, "3"), (70.0, "PAFZ"), (190.0, "7X677"), (226.0, "11501032")),
        ((52.0, "3"), (70.0, "PAFZZ"), (190.0, "7X67"), (226.0, "11501032")),
        ((52.0, "3"), (70.0, "PAFZZ"), (190.0, "7X677"), (328.0, "WASHER,FLAT")),
    ],
)
def test_headings_and_malformed_rows_do_not_become_parts(
    tokens: tuple[tuple[float, str], ...],
) -> None:
    assert _parse_parts(_line(tokens)) is None


@pytest.mark.parametrize(
    ("page", "nsn", "cage", "part", "description", "quantity"),
    [
        (48, "5310011861254", "7X677", "11501032", "WASHER,FLAT", "8"),
        (48, "", "19207", "12460163-9", "ENGINE,DIESEL", "1"),
        (55, "5330014255069", "73165", "91598", "GASKET", "1"),
        (184, "", "68505", "XA-744AV", "O-RING", "1"),
        (649, "2530014912681", "K5667", "1202359", "PUMP,POWER", "1"),
        (901, "5340012564517", "34623", "5596028", "BRACKET,DOUBLE", "8"),
    ],
)
def test_parts_columns_match_actual_source_rows(
    page: int, nsn: str, cage: str, part: str, description: str, quantity: str
) -> None:
    nodes = convert_document(BY_KEY["tm280_24p_1"], pages=[page])
    assert validate_nodes(nodes, [page]) == []
    row = next(
        node
        for node in nodes
        if node.type is NodeType.TABLE_ROW
        and node.table is not None
        and node.table.cells[4] == part
    )
    assert row.table is not None
    cells = row.table.cells
    assert cells[2:5] == [nsn, cage, part]
    assert description in cells[5]
    assert part not in cells[5]
    assert cells[7] == quantity


def test_front_axle_group_heading_is_not_a_source_parts_row() -> None:
    nodes = convert_document(BY_KEY["tm280_24p_1"], pages=[515])
    assert validate_nodes(nodes, [515]) == []
    rows = [node.table for node in nodes if node.type is NodeType.TABLE_ROW]
    assert rows
    assert all(row is not None and row.cells[0] != "1000" for row in rows)
    assert all(row is not None and "1000 FRONT AXLE ASSEMBLY" not in row.cells[5] for row in rows)
