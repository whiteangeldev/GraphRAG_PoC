"""Appendix A.2 case records."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CaseRecord(BaseModel):
    """One JSONL record from the synthetic service-case file.

    Additional fields are preserved. error_codes and parts are the exact-match
    keys used when the case collection is indexed.
    """

    model_config = ConfigDict(extra="allow")

    case_id: str = Field(min_length=1)
    date: date
    model: str = Field(min_length=1)
    symptom: str
    cause: str
    action: str
    parts: list[str]
    error_codes: list[str]
    frequency: int = Field(ge=1)
    search_text: str
