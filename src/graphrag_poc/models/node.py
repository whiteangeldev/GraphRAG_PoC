"""Appendix A.1 node file records."""

from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

BBox = Annotated[list[float], Field(min_length=4, max_length=4)]


class DocType(StrEnum):
    """Document role. Field name in the node file is doc_type."""

    OPERATION = "operation"
    MAINTENANCE = "maintenance"
    CODE_REFERENCE = "code_reference"
    PARTS = "parts"
    OTHER = "other"


class NodeType(StrEnum):
    """Passage kind. Field name in the node file is type."""

    CHAPTER = "chapter"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    PROCEDURE = "procedure"
    STEP = "step"
    CAUTION = "caution"
    TABLE = "table"
    TABLE_ROW = "table_row"
    FIGURE = "figure"
    BOILERPLATE = "boilerplate"
    CASE = "case"


class Edition(BaseModel):
    """Document edition. twin_doc_key points at a paired edition when one exists."""

    model_config = ConfigDict(extra="allow")

    version: str = Field(min_length=1)
    twin_doc_key: str | None = None


class Element(BaseModel):
    """A located text span. bbox is [x0, y0, x1, y1] in PDF coordinates when known."""

    model_config = ConfigDict(extra="allow")

    page: int = Field(ge=1)
    bbox: BBox
    text: str


class AppliesTo(BaseModel):
    """Models, series, and variants a passage applies to."""

    model_config = ConfigDict(extra="allow")

    models: list[str] = Field(default_factory=list)
    series: list[str] = Field(default_factory=list)
    variants: list[str] = Field(default_factory=list)


class TableContent(BaseModel):
    """Headers and cells of one table row. Present only when type is table_row."""

    model_config = ConfigDict(extra="allow")

    headers: list[str] = Field(min_length=1)
    cells: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def headers_match_cells(self) -> Self:
        if len(self.headers) != len(self.cells):
            raise ValueError("headers and cells must have the same length")
        return self


class Node(BaseModel):
    """One JSONL record from an Appendix A.1 node file.

    Additional fields are preserved. `table` is required on table_row nodes and
    forbidden on every other type.
    """

    model_config = ConfigDict(extra="allow")

    node_id: str = Field(min_length=1)
    doc_key: str = Field(min_length=1, pattern=r"^[^:\s]+$")
    lang: str = Field(pattern=r"^[a-z]{2,3}(-[a-z0-9]+)*$")
    edition: Edition
    doc_type: DocType
    type: NodeType
    breadcrumb: list[str] = Field(min_length=1)
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    elements: list[Element] = Field(default_factory=list)
    text: str
    parent: str | None = None
    siblings: list[str] = Field(default_factory=list)
    bound_cautions: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    applies_to: AppliesTo
    table: TableContent | None = None
    retrievable: bool

    @model_validator(mode="after")
    def check_contract(self) -> Self:
        if self.page_end < self.page_start:
            raise ValueError("page_end must be greater than or equal to page_start")
        if self.parent is not None and not self.parent:
            raise ValueError("parent must be a node id or null")
        if not (self.node_id == self.doc_key or self.node_id.startswith(f"{self.doc_key}:")):
            raise ValueError(f"node_id must equal doc_key or start with '{self.doc_key}:'")
        for element in self.elements:
            if not self.page_start <= element.page <= self.page_end:
                raise ValueError("element.page must lie within page_start and page_end")
        for label, values in (
            ("siblings", self.siblings),
            ("bound_cautions", self.bound_cautions),
            ("references", self.references),
        ):
            if any(not value for value in values):
                raise ValueError(f"{label} entries must be non-empty node ids")
        if self.type is NodeType.TABLE_ROW and self.table is None:
            raise ValueError("table is required when type is table_row")
        if self.type is not NodeType.TABLE_ROW and self.table is not None:
            raise ValueError("table is allowed only when type is table_row")
        return self
