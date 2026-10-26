"""Appendix A data contracts."""

from graphrag_poc.models.case import CaseRecord
from graphrag_poc.models.graph import (
    CaseNode,
    DocumentNode,
    EdgeType,
    GraphEdge,
    GraphLabel,
    MalfunctionNode,
    ModelNode,
    PartNode,
    PassageNode,
    Provenance,
)
from graphrag_poc.models.node import (
    AppliesTo,
    DocType,
    Edition,
    Element,
    Node,
    NodeType,
    TableContent,
)

__all__ = [
    "AppliesTo",
    "CaseNode",
    "CaseRecord",
    "DocType",
    "DocumentNode",
    "EdgeType",
    "Edition",
    "Element",
    "GraphEdge",
    "GraphLabel",
    "MalfunctionNode",
    "ModelNode",
    "Node",
    "NodeType",
    "PartNode",
    "PassageNode",
    "Provenance",
    "TableContent",
]
