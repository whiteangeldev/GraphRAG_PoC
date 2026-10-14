"""Fusion and answers that stay inside the retrieved passages."""

from graphrag_poc.generate.answer import answer_from_passages
from graphrag_poc.index.store import Hit
from graphrag_poc.retrieve.fusion import FusedHit, fuse


def _hit(node_id: str, text: str, *, kind: str = "step", page: int = 32) -> Hit:
    return Hit(
        node_id=node_id,
        text=text,
        lang="en",
        score=1.0,
        page_start=page,
        page_end=page,
        doc_key="tm280_20_2",
        type=kind,
    )


def _fused(node_id: str, text: str, *, kind: str = "step", page: int = 32) -> FusedHit:
    hit = _hit(node_id, text, kind=kind, page=page)
    return FusedHit(
        node_id=hit.node_id,
        text=hit.text,
        lang=hit.lang,
        page_start=hit.page_start,
        page_end=hit.page_end,
        doc_key=hit.doc_key,
        type=hit.type,
        channels=("sparse",),
        best_rank=1,
        rrf_score=1 / 61,
    )


def test_fusion_sums_both_channels_and_keeps_the_best_rank() -> None:
    shared = _hit("doc:shared", "shared passage")
    dense_only = _hit("doc:dense", "dense only")
    sparse_only = _hit("doc:sparse", "sparse only")
    repeated = _hit("doc:shared", "shared passage again")
    fused = fuse(
        {
            "dense": [shared, dense_only, repeated],
            "sparse": [sparse_only, shared],
        }
    )
    by_id = {hit.node_id: hit for hit in fused}
    assert fused[0].node_id == "doc:shared"
    assert by_id["doc:shared"].channels == ("dense", "sparse")
    assert by_id["doc:shared"].best_rank == 1
    assert by_id["doc:shared"].rrf_score == (1 / 61) + (1 / 62)
    assert by_id["doc:dense"].channels == ("dense",)
    assert by_id["doc:sparse"].best_rank == 1


def test_lookup_cites_the_code_row_and_unknown_code_is_refused() -> None:
    row = _hit(
        "tm280_10:table:3-1:r4",
        "4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER Step 1. Check battery cable connections.",
        kind="table_row",
        page=282,
    )
    other = _hit("tm280_10:other", "Battery service.", kind="paragraph", page=10)
    question = "What is the corrective action for 4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER?"
    found = answer_from_passages(
        question,
        [
            _fused(other.node_id, other.text, kind="paragraph", page=10),
            _fused(row.node_id, row.text, kind="table_row", page=282),
        ],
    )
    assert not found.refused
    assert found.text.startswith("4. VEHICLE NOT CHARGING")
    assert found.citations[0].node_id == "tm280_10:table:3-1:r4"
    assert found.citations[0].page == 282
    assert found.temperature == 0
    missing = answer_from_passages(
        "What is the corrective action for 99. ZZZNOTACODE FAILURE?",
        [_fused(row.node_id, row.text, kind="table_row", page=282)],
    )
    assert missing.refused
    assert "Searched: What is the corrective action for 99. ZZZNOTACODE FAILURE?" in missing.text
    assert missing.citations == ()


def test_procedure_orders_steps_and_includes_the_retrieved_caution() -> None:
    caution = _hit(
        "tm280_20_2:3-8:caution",
        "WARNING Do not drain oil when engine is hot. Severe injury to personnel will result.",
        kind="caution",
    )
    second = _hit(
        "tm280_20_2:3-8:step-3",
        "3. Connect two engine oil cooler supply and return lines.",
    )
    first = _hit(
        "tm280_20_2:3-8:step-1",
        "1. Disconnect two engine oil cooler supply and return lines.",
    )
    question = (
        "What are the steps to disconnect the engine oil cooler supply and return lines, "
        "including the warning not to drain oil when the engine is hot?"
    )
    unrelated = _fused(
        "tm280_20_2:9-16:step-b",
        "b. Installation Install the rear crossmember on the engine cooler lines.",
    )
    result = answer_from_passages(
        question,
        [
            unrelated,
            _fused(second.node_id, second.text),
            _fused(first.node_id, first.text),
            _fused(caution.node_id, caution.text, kind="caution"),
        ],
    )
    assert unrelated.node_id not in {citation.node_id for citation in result.citations}
    assert result.text.index("WARNING Do not drain oil") < result.text.index("1. Disconnect")
    assert result.text.index("1. Disconnect") < result.text.index("3. Connect")
    assert {citation.node_id for citation in result.citations} == {
        caution.node_id,
        first.node_id,
        second.node_id,
    }
