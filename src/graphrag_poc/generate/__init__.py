"""Cited answers from fused passages."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from graphrag_poc.generate.answer import answer_from_passages

__all__ = ["answer_from_passages"]


def __getattr__(name: str) -> Any:
    """Keep configuration/preflight imports free of embedding-runtime side effects."""

    if name == "answer_from_passages":
        from graphrag_poc.generate.answer import answer_from_passages

        return answer_from_passages
    raise AttributeError(name)
