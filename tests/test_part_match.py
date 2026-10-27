"""Catalogue identities must survive punctuation without matching partial numbers."""

import pytest

from graphrag_poc.graph.build import GraphData, build_from_disk
from graphrag_poc.graph.link import Term, TermTable, link_text
from graphrag_poc.graph.mentions import derive_mentions
from graphrag_poc.graph.part_match import PartMatcher


@pytest.mark.parametrize("number", ["12338330-19.5", "12340721-1.25", "16386(75)", "HC-9.56"])
def test_literal_punctuated_number_links_question_and_source(number: str) -> None:
    table = TermTable((Term("Part", number, number, "parts:row"),))
    assert [link.key for link in link_text(f"Which NSN belongs to ({number.lower()})?", table)] == [
        number
    ]
    graph = GraphData(
        parts=[{"part_number": number}],
        passages=[
            {
                "id": "passage:source",
                "text": f"Install {number}.",
                "doc_key": "manual",
                "page_start": 1,
            }
        ],
    )
    assert [edge.end_id for edge in derive_mentions(graph)] == [f"part:{number}"]


def test_number_prefixes_and_cage_substrings_do_not_become_part_links() -> None:
    matcher = PartMatcher(["12338330-19", "12338330-19.5", "16386", "16386(75)", "AB-12345"])
    assert matcher.find("Use 12338330-19.5 and 16386(75).") == {"12338330-19.5", "16386(75)"}
    assert matcher.find("XAB-12345 AB-12345-X") == set()
    assert matcher.find("Use (AB-12345).") == {"AB-12345"}


def test_every_stored_catalogue_number_can_be_linked_literally() -> None:
    numbers = [row["part_number"] for row in build_from_disk().parts]
    matcher = PartMatcher(numbers)
    assert all(number in matcher.find(f"Part ({number}).") for number in numbers)
