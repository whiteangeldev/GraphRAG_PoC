"""Qdrant collections for passages and cases."""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from graphrag_poc.index.embed import Embedder
from graphrag_poc.index.records import PASSAGE_FIELDS, CasePoint, Passage
from graphrag_poc.index.tokenize import term_frequencies

PASSAGE_COLLECTION = "passages"
CASE_COLLECTION = "cases"
DENSE = "dense"
SPARSE = "sparse"
_NAMESPACE = uuid.UUID("8d8c1c3e-6b4a-5c1e-9f0a-0c1d2e3f4a5b")


@dataclass(frozen=True)
class Hit:
    """One retrieved passage."""

    node_id: str
    text: str
    lang: str
    score: float
    page_start: int = 1
    page_end: int = 1
    doc_key: str = ""
    type: str = ""


def point_id(key: str) -> str:
    """Stable Qdrant id. Point ids cannot be arbitrary strings such as node_id."""

    return str(uuid.uuid5(_NAMESPACE, key))


def index_corpus(
    client: QdrantClient,
    embedder: Embedder,
    passages: list[Passage],
    cases: list[CasePoint],
    *,
    passage_collection: str = PASSAGE_COLLECTION,
    case_collection: str = CASE_COLLECTION,
    batch_size: int = 32,
) -> None:
    """Replace both collections. Passages get named dense and sparse vectors."""

    _recreate_passages(client, passage_collection, embedder.dimension)
    _recreate_cases(client, case_collection)
    _upsert_passages(client, embedder, passages, passage_collection, batch_size)
    _upsert_cases(client, cases, case_collection, batch_size)


def search_passages(
    client: QdrantClient,
    query: str,
    *,
    collection: str = PASSAGE_COLLECTION,
    limit: int = 5,
) -> list[Hit]:
    """Keyword search on the sparse channel. Exact strings use this channel."""

    indices, values = term_frequencies(query)
    if not indices:
        return []
    response = client.query_points(
        collection_name=collection,
        query=models.SparseVector(indices=indices, values=values),
        using=SPARSE,
        limit=limit,
        with_payload=True,
    )
    return _hits(response.points)


def search_passages_dense(
    client: QdrantClient,
    embedder: Embedder,
    query: str,
    *,
    collection: str = PASSAGE_COLLECTION,
    limit: int = 10,
) -> list[Hit]:
    """Dense search with the same embedding model that built the index."""

    vector = embedder.embed_query(query)
    response = client.query_points(
        collection_name=collection,
        query=vector,
        using=DENSE,
        limit=limit,
        with_payload=True,
    )
    return _hits(response.points)


def _hits(points: Sequence[Any]) -> list[Hit]:
    hits: list[Hit] = []
    for point in points:
        payload = point.payload or {}
        hits.append(
            Hit(
                node_id=str(payload.get("node_id", "")),
                text=str(payload.get("text", "")),
                lang=str(payload.get("lang", "")),
                score=float(point.score or 0.0),
                page_start=int(payload.get("page_start") or 1),
                page_end=int(payload.get("page_end") or payload.get("page_start") or 1),
                doc_key=str(payload.get("doc_key", "")),
                type=str(payload.get("type", "")),
            )
        )
    return hits


def find_cases(
    client: QdrantClient,
    *,
    error_code: str | None = None,
    part: str | None = None,
    model: str | None = None,
    collection: str = CASE_COLLECTION,
    limit: int = 10,
) -> list[dict[str, object]]:
    """Exact match on the case payload indexes."""

    must: list[models.FieldCondition] = []
    if error_code is not None:
        must.append(
            models.FieldCondition(key="error_codes", match=models.MatchValue(value=error_code))
        )
    if part is not None:
        must.append(models.FieldCondition(key="parts", match=models.MatchValue(value=part)))
    if model is not None:
        must.append(models.FieldCondition(key="model", match=models.MatchValue(value=model)))
    if not must:
        return []
    records, _ = client.scroll(
        collection_name=collection,
        scroll_filter=models.Filter(must=must),  # type: ignore[arg-type]
        limit=limit,
        with_payload=True,
        with_vectors=False,
    )
    return [dict(record.payload or {}) for record in records]


def _recreate_passages(client: QdrantClient, name: str, dimension: int) -> None:
    _drop(client, name)
    client.create_collection(
        collection_name=name,
        vectors_config={
            DENSE: models.VectorParams(size=dimension, distance=models.Distance.COSINE),
        },
        sparse_vectors_config={SPARSE: models.SparseVectorParams(modifier=models.Modifier.IDF)},
    )


def _recreate_cases(client: QdrantClient, name: str) -> None:
    _drop(client, name)
    client.create_collection(
        collection_name=name,
        sparse_vectors_config={SPARSE: models.SparseVectorParams(modifier=models.Modifier.IDF)},
    )
    for field in ("error_codes", "parts", "model"):
        client.create_payload_index(
            collection_name=name,
            field_name=field,
            field_schema=models.PayloadSchemaType.KEYWORD,
        )


def _drop(client: QdrantClient, name: str) -> None:
    names = {collection.name for collection in client.get_collections().collections}
    if name in names:
        client.delete_collection(name)


def _upsert_passages(
    client: QdrantClient,
    embedder: Embedder,
    passages: list[Passage],
    collection: str,
    batch_size: int,
) -> None:
    total = len(passages)
    for start in range(0, total, batch_size):
        batch = passages[start : start + batch_size]
        vectors = embedder.embed_passages([passage.text for passage in batch])
        points: list[models.PointStruct] = []
        for passage, dense in zip(batch, vectors, strict=True):
            indices, values = term_frequencies(passage.text)
            if not indices:
                continue
            points.append(
                models.PointStruct(
                    id=point_id(passage.node_id),
                    vector={
                        DENSE: dense,
                        SPARSE: models.SparseVector(indices=indices, values=values),
                    },
                    payload=passage.payload(),
                )
            )
        if points:
            client.upsert(collection_name=collection, points=points, wait=True)
        done = min(start + batch_size, total)
        if done == total or done % (batch_size * 20) == 0:
            print(f"  passages {done}/{total}", flush=True)


def _upsert_cases(
    client: QdrantClient,
    cases: list[CasePoint],
    collection: str,
    batch_size: int,
) -> None:
    for start in range(0, len(cases), batch_size):
        batch = cases[start : start + batch_size]
        points: list[models.PointStruct] = []
        for case in batch:
            indices, values = term_frequencies(case.search_text)
            if not indices:
                continue
            points.append(
                models.PointStruct(
                    id=point_id(case.case_id),
                    vector={SPARSE: models.SparseVector(indices=indices, values=values)},
                    payload=case.payload,
                )
            )
        if points:
            client.upsert(collection_name=collection, points=points, wait=True)


def passage_payload_keys() -> tuple[str, ...]:
    return PASSAGE_FIELDS
