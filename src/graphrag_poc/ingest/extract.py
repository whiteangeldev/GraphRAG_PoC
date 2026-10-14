"""Read a text-layer PDF into lines with bounding boxes."""

import itertools
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

import pdfplumber

from graphrag_poc.ingest.normalize import normalize_text
from graphrag_poc.models import DocType

WORD_BAND = 2.5
COLUMN_GAP = 28.0


@dataclass(frozen=True)
class RawLine:
    """One visual line, already split when a wide horizontal gap marks a second column."""

    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    tokens: tuple[tuple[float, str], ...]


def extract_document(
    path: str,
    *,
    lang: str,
    doc_type: DocType,
    pages: Sequence[int] | None = None,
) -> tuple[list[RawLine], dict[int, list[RawLine]], int]:
    """Return content lines, boilerplate lines by page, and the PDF page count.

    `pages` is a 1-based inclusive filter. The returned page count is still the
    full document, so callers that convert a slice pass the slice length themselves.
    """

    wanted = set(pages) if pages is not None else None
    content: list[RawLine] = []
    boilerplate: dict[int, list[RawLine]] = {}
    with pdfplumber.open(path) as pdf:
        page_count = len(pdf.pages)
        for index, page in enumerate(pdf.pages, start=1):
            if wanted is not None and index not in wanted:
                continue
            words = page.extract_words(keep_blank_chars=False, use_text_flow=False) or []
            lines = _lines_from_words(words, page=index, width=float(page.width), lang=lang)
            # A parts row is one baseline: the item is on the left and the description
            # is on the right. Column-major order would separate them.
            ordered = _reading_order(
                lines,
                float(page.width),
                preserve_rows=doc_type is DocType.PARTS,
            )
            for line in ordered:
                if _is_boilerplate(line, float(page.height), doc_type):
                    boilerplate.setdefault(index, []).append(line)
                else:
                    content.append(line)
    return content, boilerplate, page_count


def _coord(word: dict[str, object], key: str) -> float:
    value = word[key]
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        raise TypeError(f"word {key} is not a number")
    return float(value)


def _lines_from_words(
    words: Iterable[dict[str, object]],
    *,
    page: int,
    width: float,
    lang: str,
) -> list[RawLine]:
    ordered = sorted(words, key=lambda word: (_coord(word, "top"), _coord(word, "x0")))
    bands: list[list[dict[str, object]]] = []
    for word in ordered:
        if bands and abs(_coord(word, "top") - _coord(bands[-1][0], "top")) <= WORD_BAND:
            bands[-1].append(word)
        else:
            bands.append([word])

    lines: list[RawLine] = []
    for band in bands:
        band.sort(key=lambda word: _coord(word, "x0"))
        segments: list[list[dict[str, object]]] = [[band[0]]]
        for previous, word in itertools.pairwise(band):
            gap = _coord(word, "x0") - _coord(previous, "x1")
            if gap > COLUMN_GAP:
                segments.append([word])
            else:
                segments[-1].append(word)
        # Several fragments on one baseline are table cells, not text columns.
        # A bare rpm such as "400" sits apart from "4 max." on the calibration charts.
        left = " ".join(str(word["text"]) for word in segments[0]).strip()
        if len(segments) >= 3 or (len(segments) == 2 and re.fullmatch(r"\d{3,4}", left)):
            segments = [[word for segment in segments for word in segment]]
        for segment in segments:
            text = normalize_text(" ".join(str(word["text"]) for word in segment), lang=lang)
            if not text:
                continue
            tokens = tuple(
                (_coord(word, "x0"), normalize_text(str(word["text"]), lang=lang))
                for word in segment
            )
            tokens = tuple((x, token) for x, token in tokens if token)
            x0 = min(_coord(word, "x0") for word in segment)
            x1 = max(_coord(word, "x1") for word in segment)
            y0 = min(_coord(word, "top") for word in segment)
            y1 = max(_coord(word, "bottom") for word in segment)
            if x1 < x0:
                x0, x1 = x1, x0
            if y1 < y0:
                y0, y1 = y1, y0
            if x1 == x0:
                x1 = min(width, x0 + 0.5)
            lines.append(RawLine(page, x0, y0, x1, y1, text, tokens))
    return lines


def _reading_order(
    lines: list[RawLine],
    width: float,
    *,
    preserve_rows: bool = False,
) -> list[RawLine]:
    """Read a full-width line in place, and read the left column before the right.

    `preserve_rows` keeps left and right fragments of the same baseline together.
    Parts lists need that so the description stays with its item number.
    """

    if not lines or preserve_rows:
        return sorted(lines, key=lambda line: (line.y0, line.x0))
    mid = width * 0.5
    full: set[int] = set()
    left_count = 0
    right_count = 0
    for line in lines:
        spans_page = (line.x1 - line.x0) > width * 0.45 or (
            line.x0 < mid - 40 and line.x1 > mid + 40
        )
        if spans_page:
            full.add(id(line))
        elif line.x0 < mid:
            left_count += 1
        else:
            right_count += 1
    if left_count < 4 or right_count < 4:
        return sorted(lines, key=lambda line: (line.y0, line.x0))

    ordered: list[RawLine] = []
    pending_left: list[RawLine] = []
    pending_right: list[RawLine] = []

    def flush() -> None:
        ordered.extend(sorted(pending_left, key=lambda line: line.y0))
        ordered.extend(sorted(pending_right, key=lambda line: line.y0))
        pending_left.clear()
        pending_right.clear()

    for line in sorted(lines, key=lambda item: (item.y0, item.x0)):
        if id(line) in full:
            flush()
            ordered.append(line)
        elif line.x0 < mid:
            pending_left.append(line)
        else:
            pending_right.append(line)
    flush()
    return ordered


def _is_boilerplate(line: RawLine, page_height: float, doc_type: DocType) -> bool:
    text = line.text.strip()
    if text.startswith(("ARMY TM", "AIR FORCE TO", "MARINE CORPS TM")):
        return True
    if text.startswith("TM 9-") or text.startswith("TM9-"):
        return True
    if text.startswith("道路運送車両") or text.startswith("別添"):
        return True
    near_bottom = line.y0 > page_height - 48
    compact = text.replace(" ", "")
    if near_bottom and compact.replace("-", "").isdigit() and len(compact) <= 6:
        return True
    # Contents entries ("CHAPTER 2 ..... 2-1") are running matter. Parts rows also
    # use dot leaders, so those stay in the body and are parsed as item lines.
    dotted = "...." in text or "…" in text
    if dotted and text.startswith(("CHAPTER", "Chapter", "SECTION", "Section", "APPENDIX")):
        return True
    if dotted and doc_type is not DocType.PARTS:
        tail = text.split()[-1].replace("-", "")
        if tail.isdigit():
            return True
    return False
