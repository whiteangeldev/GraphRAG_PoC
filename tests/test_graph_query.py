"""Entity links, the router, derived mentions, and a live traversal."""

import time

import pytest

from graphrag_poc.graph.build import GraphData
from graphrag_poc.graph.client import make_driver
from graphrag_poc.graph.config import HOP_DEPTH, NODE_CAP
from graphrag_poc.graph.link import Link, Term, TermTable, link_text
from graphrag_poc.graph.mentions import derive_mentions
from graphrag_poc.graph.traverse import Seeds, traverse
from graphrag_poc.index.embed import Embedder
from graphrag_poc.retrieve.graph import route

_CODE = "4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER"
_TABLE = TermTable(
    (
        Term("Malfunction", _CODE, _CODE, "tm280_10:table:3-1:2:r4"),
        Term("Part", "12339317", "12339317", "tm280_24p_1:parts:r1229"),
        Term("Model", "M998", "M998", "M998"),
        Term("Part", "9999999", "alternator housing", "tm280_24p_1:parts:r9"),
    )
)


class _Stub:
    dimension = 2
    model_name = "stub"

    def embed_query(self, text: str) -> list[float]:
        if "alternator" in text.lower():
            return [1.0, 0.0]
        return [0.0, 1.0]

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]


def test_exact_forms_link_the_code_the_part_and_the_model() -> None:
    question = f"{_CODE} on M998, part 12339317"
    links = link_text(question, _TABLE)
    found = {link.label: link for link in links}
    assert found["Malfunction"].key == _CODE
    assert found["Malfunction"].node_id == "tm280_10:table:3-1:2:r4"
    assert found["Part"].key == "12339317"
    assert found["Model"].key == "M998"
    assert {link.method for link in links} == {"exact"}


def test_dense_fallback_is_recorded_and_a_missing_code_is_not_replaced() -> None:
    embedder: Embedder = _Stub()
    dense = link_text("the alternator is noisy", _TABLE, embedder=embedder)
    assert [(link.key, link.method) for link in dense] == [("9999999", "dense")]
    missed = link_text(
        "What is the corrective action for 99. ZZZNOTACODE FAILURE?",
        _TABLE,
        embedder=embedder,
    )
    assert all(link.label != "Malfunction" for link in missed)


def test_router_uses_the_graph_for_relational_and_not_for_a_plain_lookup() -> None:
    plain = route("lookup", [])
    assert plain.use_graph is False
    assert plain.reason == "simple lookup"
    relational = route("relational", [])
    assert relational.use_graph is True
    assert relational.hops == HOP_DEPTH
    linked = route("lookup", [Link("Malfunction", _CODE, "row", "exact", 1.0)])
    assert linked.use_graph is True
    assert linked.reason == "linked entity has table or case edges"


def test_mentions_are_derived_and_repeatable() -> None:
    graph = GraphData(
        models=[{"id": "model:M998", "name": "M998", "series": ["M998"]}],
        parts=[
            {
                "id": "part:12339317",
                "part_number": "12339317",
                "description": "ALTERNATOR",
                "nsn": "",
                "node_id": "tm280_24p_1:parts:r1229",
                "doc_key": "tm280_24p_1",
                "page_start": "200",
            }
        ],
        passages=[
            {
                "id": "passage:note",
                "node_id": "note",
                "text": "Install M998 part 12339317.",
                "type": "paragraph",
                "page_start": 12,
                "page_end": 12,
                "lang": "en",
                "doc_key": "tm280_10",
                "breadcrumb": ["manual"],
            }
        ],
    )
    first = derive_mentions(graph)
    assert first == derive_mentions(graph)
    assert {edge.end_id for edge in first} == {"model:M998", "part:12339317"}
    assert all(edge.derived and edge.weight < 1 for edge in first)


def _ready() -> bool:
    driver = make_driver()
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            count = session.run("MATCH (n:Malfunction) RETURN count(n) AS n").single()
    except Exception:
        return False
    finally:
        driver.close()
    return count is not None and count["n"] == 30


@pytest.mark.skipif(not _ready(), reason="rule graph is not imported")
def test_oil_cooler_and_charging_fault_and_latency() -> None:
    driver = make_driver()
    try:
        oil = traverse(
            driver,
            Seeds(passages=("tm280_20_2:3-8:step-a:3:2:step-1:2",)),
            ("NEXT", "BOUND_CAUTION"),
            hops=2,
            cap=NODE_CAP,
        )
        ids = {hit.node_id for hit in oil}
        assert "tm280_20_2:3-8:step-a:3:2:step-2:2" in ids
        assert any("Do not drain oil when engine is hot" in hit.text for hit in oil)
        assert any(hit.provenance[0]["doc_key"] == "tm280_20_2" for hit in oil)
        charging = traverse(
            driver,
            Seeds(malfunctions=("tm280_10:table:3-1:2:r4",)),
            ("CANDIDATE_PART", "LISTS", "STATES"),
            hops=2,
            cap=NODE_CAP,
            question="Which alternator part number is listed?",
        )
        assert any(":parts:" in hit.node_id for hit in charging)
        samples: list[float] = []
        seeds = Seeds(
            passages=(
                "tm280_20_2:3-8:step-a:3:2:step-1:2",
                "tm280_20_2:3-8:step-a:3:2:step-2:2",
                "tm280_10:step-1:2",
                "tm280_10:step-2:2",
                "tm280_10:step-3:2",
            )
        )
        traverse(driver, seeds, ("NEXT", "BOUND_CAUTION"), hops=2, cap=NODE_CAP)
        for _ in range(20):
            started = time.perf_counter()
            traverse(driver, seeds, ("NEXT", "BOUND_CAUTION"), hops=2, cap=NODE_CAP)
            samples.append(time.perf_counter() - started)
    finally:
        driver.close()
    samples.sort()
    assert samples[int(0.95 * (len(samples) - 1))] < 0.05
