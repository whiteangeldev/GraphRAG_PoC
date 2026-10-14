"""Sparse tokenization and a small Qdrant round-trip."""

import uuid

import pytest

from graphrag_poc.index.client import make_client
from graphrag_poc.index.embed import Embedder
from graphrag_poc.index.records import CasePoint, Passage
from graphrag_poc.index.store import find_cases, index_corpus, search_passages
from graphrag_poc.index.tokenize import normalize_token_text, term_frequencies, tokenize


class HashEmbedder:
    """Deterministic stand-in so the Qdrant wiring can be tested without a model server."""

    dimension = 8
    model_name = "hash-test"

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)

    def _vector(self, text: str) -> list[float]:
        values = [0.0] * self.dimension
        for token in tokenize(text):
            values[sum(token.encode()) % self.dimension] += 1.0
        total = sum(values) or 1.0
        return [value / total for value in values]


def test_tokenizer_folds_width_and_splits_both_languages() -> None:
    full_width = "\uff11\uff12\uff13\uff21"
    assert normalize_token_text(full_width) == "123a"
    assert tokenize("ENGINE FAILS TO CRANK") == ["engine", "fails", "to", "crank"]
    assert "5705628" in tokenize("part 5705628 bracket")
    japanese = tokenize("適用範囲")
    assert "適用範囲" in japanese
    assert "適用" in japanese and "範囲" in japanese
    half_width = "\uff71\uff72\uff73"
    assert tokenize(half_width) == tokenize("\u30a2\u30a4\u30a6")
    indices, weights = term_frequencies("crank crank")
    assert len(indices) == len(weights) == 1
    assert weights == [1.0]


def test_embedder_protocol() -> None:
    embedder: Embedder = HashEmbedder()
    assert len(embedder.embed_query("engine")) == embedder.dimension


def _qdrant_ready() -> bool:
    try:
        return make_client(timeout=5).get_collections() is not None
    except Exception:
        return False


@pytest.mark.skipif(not _qdrant_ready(), reason="Qdrant is not running on localhost:6333")
def test_sparse_search_and_case_exact_match() -> None:
    suffix = uuid.uuid4().hex[:8]
    passages_name = f"passages_test_{suffix}"
    cases_name = f"cases_test_{suffix}"
    client = make_client(timeout=30)
    passages = [
        Passage(
            node_id="tm280_10:table:3-1:r1",
            doc_key="tm280_10",
            page_start=281,
            page_end=281,
            type="table_row",
            lang="en",
            text="1. ENGINE FAILS TO CRANK Step 1. Check the transmission shift lever.",
            breadcrumb=("Operator", "Table 3-1"),
        ),
        Passage(
            node_id="tm280_24p_1:parts:r1",
            doc_key="tm280_24p_1",
            page_start=46,
            page_end=46,
            type="table_row",
            lang="en",
            text="5705628 ENGINE AND CONTAINER",
            breadcrumb=("Parts",),
        ),
        Passage(
            node_id="mlit_b052:1",
            doc_key="mlit_b052",
            page_start=1,
            page_end=1,
            type="section",
            lang="ja",
            text="1 適用範囲 本技術基準は灯火器に適用する。",
            breadcrumb=("別添52",),
        ),
    ]
    cases = [
        CasePoint(
            case_id="C-000001",
            model="M998",
            error_codes=("1. ENGINE FAILS TO CRANK",),
            parts=("5705628",),
            search_text="M998 1. ENGINE FAILS TO CRANK 5705628",
            payload={
                "case_id": "C-000001",
                "model": "M998",
                "error_codes": ["1. ENGINE FAILS TO CRANK"],
                "parts": ["5705628"],
                "search_text": "M998 1. ENGINE FAILS TO CRANK 5705628",
            },
        )
    ]
    try:
        index_corpus(
            client,
            HashEmbedder(),
            passages,
            cases,
            passage_collection=passages_name,
            case_collection=cases_name,
        )
        code_hits = search_passages(
            client,
            "1. ENGINE FAILS TO CRANK",
            collection=passages_name,
            limit=3,
        )
        assert code_hits[0].node_id == "tm280_10:table:3-1:r1"
        part_hits = search_passages(client, "5705628", collection=passages_name, limit=3)
        assert part_hits[0].node_id == "tm280_24p_1:parts:r1"
        japanese_hits = search_passages(client, "適用範囲", collection=passages_name, limit=3)
        assert japanese_hits[0].node_id == "mlit_b052:1"
        assert japanese_hits[0].lang == "ja"
        matched = find_cases(
            client,
            error_code="1. ENGINE FAILS TO CRANK",
            part="5705628",
            collection=cases_name,
        )
        assert matched[0]["case_id"] == "C-000001"
        assert matched[0]["model"] == "M998"
    finally:
        for name in (passages_name, cases_name):
            names = {item.name for item in client.get_collections().collections}
            if name in names:
                client.delete_collection(name)
