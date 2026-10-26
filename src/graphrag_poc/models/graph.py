"""Graph node and edge contracts from the M2 schema."""

from datetime import date
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GraphLabel(StrEnum):
    """Node label stored in Neo4j."""

    DOCUMENT = "Document"
    PASSAGE = "Passage"
    MALFUNCTION = "Malfunction"
    PART = "Part"
    MODEL = "Model"
    CASE = "Case"


class EdgeType(StrEnum):
    """Relationship type stored in Neo4j."""

    IN_DOCUMENT = "IN_DOCUMENT"
    PARENT = "PARENT"
    NEXT = "NEXT"
    BOUND_CAUTION = "BOUND_CAUTION"
    REFERS_TO = "REFERS_TO"
    STATES = "STATES"
    HAS_STEP = "HAS_STEP"
    APPLIES_TO = "APPLIES_TO"
    LISTS = "LISTS"
    CANDIDATE_PART = "CANDIDATE_PART"
    ABOUT = "ABOUT"
    INSTALLED = "INSTALLED"
    ON_MODEL = "ON_MODEL"
    MENTIONS = "MENTIONS"


class Provenance(BaseModel):
    """Where an edge came from. A manual page or a case id, not both."""

    model_config = ConfigDict(extra="allow")

    rule: str = Field(min_length=1)
    derived: bool = False
    weight: float = 1.0
    doc_key: str | None = None
    page_start: int | None = Field(default=None, ge=1)
    case_id: str | None = None

    @model_validator(mode="after")
    def one_source(self) -> Self:
        has_page = bool(self.doc_key) and self.page_start is not None
        has_case = bool(self.case_id)
        if has_page == has_case:
            raise ValueError("provenance requires a document page or a case id")
        if self.derived and self.weight >= 1:
            raise ValueError("a derived edge must have weight below 1")
        return self


class DocumentNode(BaseModel):
    """One manual or the Japanese sample."""

    model_config = ConfigDict(extra="allow")

    doc_key: str = Field(min_length=1)
    title: str = Field(min_length=1)
    lang: str = Field(min_length=2)
    doc_type: str = Field(min_length=1)
    edition: str = Field(min_length=1)


class PassageNode(BaseModel):
    """A retrievable Appendix A node. The text cited by an answer stays here."""

    model_config = ConfigDict(extra="allow")

    node_id: str = Field(min_length=1)
    text: str
    type: str = Field(min_length=1)
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    lang: str = Field(min_length=2)
    breadcrumb: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def page_order(self) -> Self:
        if self.page_end < self.page_start:
            raise ValueError("page_end must be greater than or equal to page_start")
        return self


class MalfunctionNode(BaseModel):
    """A Table 3-1 malfunction row. `code` is the full label."""

    model_config = ConfigDict(extra="allow")

    node_id: str = Field(min_length=1)
    code: str = Field(min_length=1)
    page_start: int = Field(ge=1)


class PartNode(BaseModel):
    """A parts-list row. The part number is the identity."""

    model_config = ConfigDict(extra="allow")

    part_number: str = Field(min_length=1)
    description: str
    nsn: str = ""
    node_id: str = Field(min_length=1)


class ModelNode(BaseModel):
    """A model token such as M998."""

    model_config = ConfigDict(extra="allow")

    name: str = Field(min_length=1)
    series: list[str] = Field(default_factory=list)


class CaseNode(BaseModel):
    """One synthetic service case."""

    model_config = ConfigDict(extra="allow")

    case_id: str = Field(min_length=1)
    date: date
    symptom: str
    cause: str
    action: str
    frequency: int = Field(ge=1)


class GraphEdge(BaseModel):
    """One typed relationship. Provenance is required."""

    model_config = ConfigDict(extra="allow")

    type: EdgeType
    start_id: str = Field(min_length=1)
    end_id: str = Field(min_length=1)
    provenance: Provenance
    keyword: str | None = None

    @model_validator(mode="after")
    def edge_rules(self) -> Self:
        if self.type is EdgeType.CANDIDATE_PART and not self.keyword:
            raise ValueError("CANDIDATE_PART requires the keyword that selected the part")
        if self.type is EdgeType.MENTIONS and not self.provenance.derived:
            raise ValueError("MENTIONS is a derived edge")
        if self.type is not EdgeType.MENTIONS and self.provenance.derived:
            raise ValueError("only MENTIONS edges are derived")
        return self
