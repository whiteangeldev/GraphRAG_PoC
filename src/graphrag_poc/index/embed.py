"""Dense embeddings from the configured model."""

import os
from typing import Protocol


class Embedder(Protocol):
    """Passage and query embeddings from one model."""

    dimension: int
    model_name: str

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        """Embed documents. Order matches `texts`."""

    def embed_query(self, text: str) -> list[float]:
        """Embed one search string."""


def embedding_input(text: str, *, limit: int = 1500) -> str:
    """Keep the start of a very long passage inside a typical embedding window."""

    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[:limit]


class OpenAIEmbedder:
    """OpenAI-compatible `/v1/embeddings` endpoint."""

    def __init__(self, *, model: str, base_url: str, api_key: str) -> None:
        from openai import OpenAI

        self.model_name = model
        self._client = OpenAI(base_url=base_url, api_key=api_key or "not-needed", timeout=120.0)
        probe = self.embed_passages(["engine"])
        self.dimension = len(probe[0])

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(
            model=self.model_name,
            input=[embedding_input(text) for text in texts],
        )
        ordered = sorted(response.data, key=lambda item: item.index)
        return [list(item.embedding) for item in ordered]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_passages([text])[0]


class FastEmbedEmbedder:
    """Local ONNX embedder. E5 models use the passage/query prefixes they were trained with."""

    def __init__(self, model: str) -> None:
        from fastembed import TextEmbedding

        self.model_name = model
        self._model = TextEmbedding(model_name=model)
        self._e5 = "e5" in model.lower()
        probe = self.embed_passages(["engine"])
        self.dimension = len(probe[0])

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        prepared = [self._prepare(text, passage=True) for text in texts]
        vectors = []
        for vector in self._model.embed(prepared):
            vectors.append([float(value) for value in vector.tolist()])
        return vectors

    def embed_query(self, text: str) -> list[float]:
        prepared = self._prepare(text, passage=False)
        vector = next(iter(self._model.embed([prepared])))
        return [float(value) for value in vector.tolist()]

    def _prepare(self, text: str, *, passage: bool) -> str:
        body = embedding_input(text)
        if not self._e5:
            return body
        prefix = "passage: " if passage else "query: "
        return prefix + body


def build_embedder() -> Embedder:
    """Select the embedder from EMBEDDING_BACKEND and EMBEDDING_MODEL."""

    model = os.environ.get("EMBEDDING_MODEL", "").strip()
    backend = os.environ.get("EMBEDDING_BACKEND", "openai").strip().lower()
    if not model:
        raise RuntimeError("EMBEDDING_MODEL is empty. Set it before indexing.")
    if backend == "fastembed":
        return FastEmbedEmbedder(model)
    if backend == "openai":
        return OpenAIEmbedder(
            model=model,
            base_url=os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:8000/v1"),
            api_key=os.environ.get("OPENAI_API_KEY", ""),
        )
    raise RuntimeError(f"unknown EMBEDDING_BACKEND {backend!r}")
