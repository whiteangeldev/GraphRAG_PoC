"""Appendix A.4 types. Extra fields are allowed; the listed names stay fixed."""

from pydantic import BaseModel, ConfigDict, Field


class Entity(BaseModel):
    """One span from a question. `type` is code, part, model, or empty."""

    model_config = ConfigDict(extra="allow")

    text: str = Field(min_length=1)
    type: str = ""


class Seed(BaseModel):
    """A graph node linked from an entity."""

    model_config = ConfigDict(extra="allow")

    node_id: str = Field(min_length=1)
    confidence: float
    matched_form: str
    label: str = ""


class Candidate(BaseModel):
    """One passage returned to reciprocal rank fusion."""

    model_config = ConfigDict(extra="allow")

    passage_node_id: str
    score: float
    channels: list[str] = Field(default_factory=lambda: ["graph"])
    via: list[str] = Field(default_factory=list)


class GraphPath(BaseModel):
    """How one candidate was reached."""

    model_config = ConfigDict(extra="allow")

    passage_node_id: str
    via: list[str]
    score: float
    provenance: list[dict[str, str | int | float | bool | None]] = Field(default_factory=list)


class RelationFrame(BaseModel):
    """code, cause, remedy, part, and cases."""

    model_config = ConfigDict(extra="allow")

    code: str = ""
    cause: str = ""
    remedy: str = ""
    part: str = ""
    cases: list[str] = Field(default_factory=list)


class TraversalResult(BaseModel):
    """Passages, the paths that found them, and the relation frame."""

    model_config = ConfigDict(extra="allow")

    candidates: list[Candidate]
    paths: list[GraphPath]
    frame: RelationFrame | None = None


class RouterDecision(BaseModel):
    """Whether the graph list is used for this question."""

    model_config = ConfigDict(extra="allow")

    enabled: bool
    hops: int
    reason: str


class BuildReport(BaseModel):
    """Counts from one graph build."""

    model_config = ConfigDict(extra="allow")

    build: str
    output: str
    counts: dict[str, int]
    orphans: int
    derived: int
