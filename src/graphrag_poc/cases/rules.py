"""Load the committed case-generation rules."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from graphrag_poc.ingest.catalog import ROOT

CASES_DIR = ROOT / "data" / "cases"
RULES_PATH = CASES_DIR / "rules.json"
CASES_PATH = CASES_DIR / "cases.jsonl"


class Rules(BaseModel):
    """Deterministic rules for the synthetic service-case file."""

    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1)
    seed: int
    count: int = Field(ge=1)
    date_start: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    date_end: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    frequency_min: int = Field(ge=1)
    frequency_max: int = Field(ge=1)
    fault_doc_key: str = Field(min_length=1)
    fault_header: str = Field(min_length=1)
    parts_doc_key: str = Field(min_length=1)
    part_header: str = Field(min_length=1)
    min_part_length: int = Field(ge=1)
    family_models: list[str] = Field(min_length=1)
    search_text_fields: list[str] = Field(min_length=1)
    part_keywords: dict[str, list[str]]


def load_rules(path: Path | None = None) -> Rules:
    source = path or RULES_PATH
    return Rules.model_validate_json(source.read_text(encoding="utf-8"))
