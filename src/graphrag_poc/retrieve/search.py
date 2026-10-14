"""Dense and sparse retrieval, then reciprocal rank fusion.

The optional reranker stays off. RERANK_ENABLED is not applied in this baseline.
"""

from qdrant_client import QdrantClient

from graphrag_poc.index.embed import Embedder
from graphrag_poc.index.store import (
    PASSAGE_COLLECTION,
    search_passages,
    search_passages_dense,
)
from graphrag_poc.retrieve.fusion import RRF_K, FusedHit, fuse


def retrieve(
    client: QdrantClient,
    embedder: Embedder,
    question: str,
    *,
    collection: str = PASSAGE_COLLECTION,
    limit: int = 12,
    k: int = RRF_K,
) -> list[FusedHit]:
    """Return the fused dense and sparse lists. No reranker is applied."""

    dense = search_passages_dense(client, embedder, question, collection=collection, limit=limit)
    sparse = search_passages(client, question, collection=collection, limit=limit)
    return fuse({"dense": dense, "sparse": sparse}, k=k)
