"""Index retrievable passages and service cases in Qdrant."""

from graphrag_poc.index.store import index_corpus, search_passages

__all__ = ["index_corpus", "search_passages"]
