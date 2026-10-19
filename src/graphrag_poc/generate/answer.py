"""Answers written only from the fused passages."""

import math
import os
import re
from dataclasses import dataclass

from graphrag_poc.index.tokenize import tokenize
from graphrag_poc.retrieve.fusion import FusedHit

_LABEL = re.compile(r"\d+\.\s+[A-Z][A-Z0-9 ,'/().°-]{8,}")
_MIXED_TITLE = re.compile(r"\d+\.\s+.+?(?=\s+\u2014\s+)")
MODEL_PASSAGE_LIMIT = 1500
_STEP_NUMBER = re.compile(r"^(?:step\s+)?(\d+)\b", re.IGNORECASE)
_STEP_LETTER = re.compile(r"^([a-z])\.\s", re.IGNORECASE)


@dataclass(frozen=True)
class Citation:
    """A source passage. `page` is the passage's first page."""

    node_id: str
    page: int


@dataclass(frozen=True)
class Answer:
    text: str
    citations: tuple[Citation, ...]
    refused: bool
    searched: str
    temperature: float
    seed: int


def clip_for_model(text: str, limit: int = MODEL_PASSAGE_LIMIT) -> str:
    """Keep the start of a passage for a model prompt. The slice stays an exact substring."""

    if len(text) <= limit:
        return text
    return text[:limit]


def answer_from_passages(question: str, hits: list[FusedHit]) -> Answer:
    """Compose an answer from `hits` only, or refuse when they do not contain it."""

    temperature = float(os.environ.get("GENERATION_TEMPERATURE", "0"))
    seed = int(os.environ.get("GENERATION_SEED", "0"))
    label = _requested_label(question)
    if label is not None and not any(label.lower() in hit.text.lower() for hit in hits):
        return _refuse(question, temperature, seed)
    if not hits:
        return _refuse(question, temperature, seed)

    if label is not None:
        chosen = _hits_containing(hits, label)
        rows = [hit for hit in chosen if hit.type == "table_row"]
        if rows:
            chosen = rows
        chosen.sort(key=lambda hit: (hit.best_rank, hit.node_id))
        return _quote(question, chosen, temperature, seed)

    procedure = _procedure_hits(question, hits)
    if procedure:
        return _quote(question, procedure, temperature, seed)

    return _quote(question, [hits[0]], temperature, seed)


def _refuse(question: str, temperature: float, seed: int) -> Answer:
    text = f"No retrieved passage contains the requested material. Searched: {question}"
    return Answer(text, (), True, question, temperature, seed)


def _quote(question: str, hits: list[FusedHit], temperature: float, seed: int) -> Answer:
    text = "\n".join(hit.text for hit in hits)
    citations = tuple(Citation(node_id=hit.node_id, page=hit.page_start) for hit in hits)
    return Answer(text, citations, False, question, temperature, seed)


def _requested_label(question: str) -> str | None:
    """The malfunction title named in the question, without the words that follow it."""

    matches = _LABEL.findall(question)
    if matches:
        return _strip_title_tail(str(max(matches, key=len)))
    mixed = _MIXED_TITLE.search(question)
    if mixed is None:
        return None
    return mixed.group(0).strip()


def _strip_title_tail(label: str) -> str:
    """Drop a trailing comma or the single capital of the next word."""

    trimmed = label.strip()
    if trimmed.endswith(","):
        trimmed = trimmed[:-1].rstrip()
    if (
        len(trimmed) >= 4
        and trimmed[-3] == "."
        and trimmed[-2] == " "
        and trimmed[-1].isascii()
        and trimmed[-1].isupper()
    ):
        trimmed = trimmed[:-3].rstrip()
    return trimmed


def _hits_containing(hits: list[FusedHit], label: str) -> list[FusedHit]:
    return [hit for hit in hits if label.lower() in hit.text.lower()]


def _is_step(hit: FusedHit) -> bool:
    return hit.type == "step" or _STEP_NUMBER.match(hit.text) is not None


def _is_caution(hit: FusedHit) -> bool:
    opening = hit.text.lstrip().upper()
    return hit.type == "caution" or opening.startswith(("CAUTION", "WARNING"))


def _procedure_hits(question: str, hits: list[FusedHit]) -> list[FusedHit]:
    """Steps and cautions from the one task that best matches the question."""

    steps = [
        hit
        for hit in hits
        if _is_step(hit) and _overlaps(question, hit.text) and len(hit.text) <= 2500
    ]
    if not steps:
        return []
    anchor = max(steps, key=lambda hit: (_precision(question, hit), -hit.best_rank))
    prefix = _task_prefix(anchor.node_id)
    selected = [
        hit
        for hit in hits
        if _task_prefix(hit.node_id) == prefix
        and (_is_caution(hit) or (_is_step(hit) and _overlaps(question, hit.text)))
    ]
    cautions = [hit for hit in selected if _is_caution(hit)]
    ordered = sorted((hit for hit in selected if _is_step(hit)), key=_step_key)
    return cautions + ordered


def _task_prefix(node_id: str) -> str:
    parts = node_id.split(":")
    while parts and (
        parts[-1].isdigit() or parts[-1].startswith("step-") or parts[-1].startswith("caution")
    ):
        parts.pop()
    return ":".join(parts)


def _precision(question: str, hit: FusedHit) -> float:
    return _overlap_count(question, hit.text) / math.log(len(hit.text) + 10)


def _overlap_count(question: str, text: str) -> int:
    content = [token for token in tokenize(question) if len(token) >= 5]
    folded = text.lower()
    return sum(token in folded for token in content)


def _overlaps(question: str, text: str) -> bool:
    content = [token for token in tokenize(question) if len(token) >= 5]
    if not content:
        return True
    folded = text.lower()
    return sum(token in folded for token in content) >= 2


def _step_key(hit: FusedHit) -> tuple[int, int, str]:
    number = _STEP_NUMBER.match(hit.text.strip())
    if number is not None:
        return (0, int(number.group(1)), hit.node_id)
    letter = _STEP_LETTER.match(hit.text.strip())
    if letter is not None:
        return (1, ord(letter.group(1).lower()), hit.node_id)
    return (2, hit.page_start, hit.node_id)
