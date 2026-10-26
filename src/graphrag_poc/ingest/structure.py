"""Turn extracted lines into Appendix A nodes with stable ids and real links."""

import re
from dataclasses import dataclass, field

from graphrag_poc.ingest.catalog import DocumentSpec
from graphrag_poc.ingest.extract import RawLine
from graphrag_poc.models import AppliesTo, DocType, Edition, Element, Node, NodeType, TableContent

# Models named in the HMMWV manuals. Tokens such as M998A2 are not in this set.
VEHICLE_MODELS = {
    "M998",
    "M998A1",
    "M1038",
    "M1038A1",
    "M1097",
    "M1097A1",
    "M1097A2",
    "M1123",
    "M1025",
    "M1025A1",
    "M1025A2",
    "M1026",
    "M1026A1",
    "M1043",
    "M1043A1",
    "M1043A2",
    "M1044",
    "M1044A1",
    "M1045",
    "M1045A1",
    "M1045A2",
    "M1046",
    "M1046A1",
    "M966",
    "M966A1",
    "M996",
    "M996A1",
    "M997",
    "M997A1",
    "M997A2",
    "M1035",
    "M1035A1",
    "M1035A2",
    "M1036",
    "M1037",
    "M1042",
    "M1121",
}

CHAPTER_RE = re.compile(r"^CHAPTER\s+(\d+)\b\s*(.*)$", re.IGNORECASE)
SECTION_RE = re.compile(r"^SECTION\s+([IVXLC0-9]+)\.?\s*(.*)$", re.IGNORECASE)
PARA_RE = re.compile(r"^(\d{1,2}-\d{1,3}(?:\.\d+)*)\.\s+(\S.*)$")
TABLE_RE = re.compile(r"^Table\s+(\d{1,2}-\d{1,3})\.\s*\S", re.IGNORECASE)
FIGURE_RE = re.compile(r"^(?:Figure|Fig\.)\s+(\d{1,2}-\d{1,3})\.?\s*(.*)$", re.IGNORECASE)
CALLOUT_RE = re.compile(r"^(WARNING|CAUTION|NOTE|警告|注意)$")
LETTER_STEP_RE = re.compile(r"^([a-z])\.\s+(\S.*)$")
WORD_STEP_RE = re.compile(r"^Step\s+(\d{1,2})\.\s+(\S.*)$", re.IGNORECASE)
PAREN_STEP_RE = re.compile(r"^\(([a-z]|\d{1,2})\)\s+(\S.*)$")
NUMBER_STEP_RE = re.compile(r"^(\d{1,2})\.\s+(\S.*)$")
JA_HEAD_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(\S.*)$")
CALIB_RE = re.compile(r"^(\d{3,4})\s+(\S+)\s+(\S.*)$")
MODEL_RE = re.compile(r"\b(M\d{3,4})(A\d)?\b")
PUMP_RE = re.compile(r"\bDB\d{4}-\d{4}\b")
PARA_REF_RE = re.compile(r"\b(?:paragraphs?|paras?\.|para\.)\s*(\d{1,2}-\d{1,3})\b", re.IGNORECASE)
TABLE_REF_RE = re.compile(r"\btables?\s+(\d{1,2}-\d{1,3})\b", re.IGNORECASE)
FIG_REF_RE = re.compile(
    r"\b(?:figures?|figs?\.)\s+(\d{1,2}-\d{1,3})\b",
    re.IGNORECASE,
)
JA_REF_RE = re.compile(r"(?<!\d)(\d+(?:\.\d+)+)(?!\d)")
SMR_RE = re.compile(r"^[A-Z]{5}$")
NSN_RE = re.compile(r"^\d{13}$")
CAGE_RE = re.compile(r"^[A-Z0-9]{5}$")
PARTS_HEADERS = [
    "ITEM NO",
    "SMR CODE",
    "NSN",
    "CAGE",
    "PART NUMBER",
    "DESCRIPTION",
    "USABLE ON CODE",
    "QTY",
]
MALFUNCTION_HEADERS = ["MALFUNCTION", "TEST OR INSPECTION AND CORRECTIVE ACTION"]
CALIB_HEADERS = ["RPM", "THROTTLE POSITION", "LIMITS"]
CELL_GAP = 30.0

# Table 3-1 group labels, and the models the operator manual assigns to each group.
# Series models are the M998 family named on the title page. Winch, armament, and
# ambulance lists are the subsets that title page and Table 3-1 name for those bodies.
SERIES_MODELS = (
    "M966",
    "M966A1",
    "M996",
    "M996A1",
    "M997",
    "M997A1",
    "M997A2",
    "M998",
    "M998A1",
    "M1025",
    "M1025A1",
    "M1025A2",
    "M1026",
    "M1026A1",
    "M1035",
    "M1035A1",
    "M1035A2",
    "M1036",
    "M1037",
    "M1038",
    "M1038A1",
    "M1042",
    "M1043",
    "M1043A1",
    "M1043A2",
    "M1044",
    "M1044A1",
    "M1045",
    "M1045A1",
    "M1045A2",
    "M1046",
    "M1046A1",
    "M1097",
    "M1097A1",
    "M1097A2",
    "M1121",
    "M1123",
)
WINCH_MODELS = (
    "M1036",
    "M1038",
    "M1038A1",
    "M1044",
    "M1044A1",
    "M1046",
    "M1046A1",
)
ARMAMENT_MODELS = (
    "M966",
    "M966A1",
    "M1025",
    "M1025A1",
    "M1025A2",
    "M1026",
    "M1026A1",
    "M1036",
    "M1043",
    "M1043A1",
    "M1043A2",
    "M1044",
    "M1044A1",
    "M1045",
    "M1045A1",
    "M1045A2",
    "M1046",
    "M1046A1",
    "M1121",
)
AMBULANCE_MODELS = (
    "M996",
    "M996A1",
    "M997",
    "M997A1",
    "M997A2",
    "M1035",
    "M1035A1",
    "M1035A2",
)
TROUBLE_GROUPS: dict[str, tuple[str, ...] | None] = {
    "ENGINE": SERIES_MODELS,
    "HEATING SYSTEM": SERIES_MODELS,
    "TRANSMISSION": SERIES_MODELS,
    "TRANSFER CASE": SERIES_MODELS,
    "BRAKES": SERIES_MODELS,
    "WHEELS AND TIRES": SERIES_MODELS,
    "STEERING": SERIES_MODELS,
    "WINCH": WINCH_MODELS,
    "SPECIAL PURPOSE BODIES": None,
    "TOW/ARMAMENT CARRIER": ARMAMENT_MODELS,
    "AMBULANCE": AMBULANCE_MODELS,
}
TROUBLE_CHROME = re.compile(
    r"^(?:MALFUNCTION|TEST OR INSPECTION|CORRECTIVE ACTION)"
    r"(?:\s+(?:MALFUNCTION|TEST OR INSPECTION|CORRECTIVE ACTION))*$"
)
PAGE_MARK_RE = re.compile(r"^(?:Change\s+\d.*|\d{1,2}\s*-\s*\d{1,2})$")
PARTS_BANNER_RE = re.compile(r"^(?:GROUP|FIG\.|FIGURE)\b", re.IGNORECASE)
GRID_DATA_RE = re.compile(r"±|\blbs\b|\bin\.|\bmm\b|\d/\d")
MEASURE_RE = re.compile(r"±|\bmm\b|\bN\b|\blbs\b|\bin\.")


@dataclass
class OpenBlock:
    """A heading or step that is still collecting lines."""

    kind: str
    node_id: str
    title: str
    lines: list[RawLine] = field(default_factory=list)
    parent: str | None = None
    breadcrumb: list[str] = field(default_factory=list)
    has_steps: bool = False
    bound_cautions: list[str] = field(default_factory=list)
    emit_row: bool = False
    number: str = ""
    title_line_count: int = 1
    malfunction_table_id: str | None = None
    malfunction_models: tuple[str, ...] = ()


@dataclass
class _PartsFields:
    item: str
    smr: str
    nsn: str
    cage: str
    part: str
    desc: str
    uoc: str
    qty: str


class Builder:
    """One document. Nodes are emitted as soon as their block closes."""

    def __init__(
        self,
        spec: DocumentSpec,
        content: list[RawLine],
        boilerplate: dict[int, list[RawLine]],
        page_count: int,
        cover_pages: list[int] | None = None,
    ) -> None:
        self.spec = spec
        self.content = content
        self.boilerplate = boilerplate
        self.page_count = page_count
        if cover_pages is None:
            self.cover_pages = list(range(1, page_count + 1))
        else:
            self.cover_pages = cover_pages
        self.nodes: list[Node] = []
        self.ids: set[str] = set()
        self.chapter: OpenBlock | None = None
        self.section: OpenBlock | None = None
        self.heading: OpenBlock | None = None
        self.letter_step: OpenBlock | None = None
        self.nested_step: OpenBlock | None = None
        self.callout: OpenBlock | None = None
        self.loose: OpenBlock | None = None
        self.pending_cautions: list[str] = []
        self.in_troubleshooting = False
        self.in_calibration = False
        self.table_id: str | None = None
        self.parts_table_id: str | None = None
        self.parts_row: Node | None = None
        self.parts_seq = 0
        self.calib_seq = 0
        self.malfunction_seq = 0
        self.group_models: tuple[str, ...] = ()
        self.in_spec_table = False
        self.spec_header_tokens: list[tuple[float, str]] = []
        self.spec_headers: list[str] | None = None
        self.spec_row: Node | None = None
        self.spec_measure_extra = 0
        self._emit_root()

    def build(self) -> list[Node]:
        for line in self.content:
            kind = self._classify(line)
            if kind == "skip":
                self._add_boilerplate_line(line)
                continue
            if kind == "parts":
                self._emit_parts_row(line)
                continue
            if kind == "parts_cont" and self.parts_row is not None:
                self._extend_parts_row(line)
                continue
            self.parts_row = None
            if kind == "grid":
                self._emit_grid_row(line)
                continue
            if kind == "grid_cont":
                self._extend_grid_row(line)
                continue
            if kind == "calibration":
                self._emit_calibration_row(line)
                continue
            if kind == "continuation":
                self._append(line)
                continue
            self._open(kind, line)
        self._close_callout()
        self._close_nested()
        self._close_letter()
        self._close_heading()
        self._close_section()
        self._close_chapter()
        self._close_loose()
        self._bind_leftover_cautions(self.spec.doc_key)
        self._cover_empty_pages()
        self._resolve_references()
        self._inherit_applicability()
        self._assign_siblings()
        return self.nodes

    def _emit_root(self) -> None:
        self.ids.add(self.spec.doc_key)
        self.nodes.append(
            self._node(
                node_id=self.spec.doc_key,
                node_type=NodeType.CHAPTER,
                breadcrumb=[self.spec.title],
                lines=[],
                parent=None,
                text=self.spec.title,
                page_start=1,
                page_end=max(self.page_count, 1),
            )
        )

    def _classify(self, line: RawLine) -> str:
        text = line.text.strip()
        if self._is_parts_header(text):
            return "skip"
        if self.spec.doc_type is DocType.PARTS and PARTS_BANNER_RE.match(text):
            self.parts_row = None
            return "continuation"
        if self.spec.doc_type is DocType.PARTS and _parse_parts(line) is not None:
            return "parts"
        if (
            self.spec.doc_type is DocType.PARTS
            and self.parts_row is not None
            and not _starts_structure(text)
        ):
            return "parts_cont"
        if CHAPTER_RE.match(text):
            return "chapter"
        if SECTION_RE.match(text):
            return "section"
        if TABLE_RE.match(text):
            return "table"
        if FIGURE_RE.match(text):
            return "figure"
        callout = CALLOUT_RE.match(text)
        if callout:
            return "note" if callout.group(1) in {"NOTE", "注"} else "caution"
        if PARA_RE.match(text):
            return "heading"
        if self.spec.lang == "ja" and line.x0 < 96 and JA_HEAD_RE.match(text):
            return "ja_heading"
        if self.in_troubleshooting and (TROUBLE_CHROME.match(text) or PAGE_MARK_RE.match(text)):
            return "skip"
        if self.in_troubleshooting and text in TROUBLE_GROUPS:
            models = TROUBLE_GROUPS[text]
            if models is not None:
                self.group_models = models
            return "skip"
        if self.in_troubleshooting and _is_malfunction(text):
            return "malfunction"
        if self.in_calibration and CALIB_RE.match(text):
            return "calibration"
        if self.in_spec_table and text.startswith("FOLLOW-ON"):
            self.in_spec_table = False
        elif self.in_spec_table and len(_split_cells(line)) >= 2:
            return "grid"
        elif (
            self.in_spec_table
            and self.spec_row is not None
            and len(text) <= 24
            and not text[:1].isdigit()
        ):
            return "grid_cont"
        if LETTER_STEP_RE.match(text):
            return "step_letter"
        if WORD_STEP_RE.match(text) or PAREN_STEP_RE.match(text):
            return "step_nested"
        if NUMBER_STEP_RE.match(text) and not _mostly_upper(text):
            return "step_nested"
        return "continuation"

    def _open(self, kind: str, line: RawLine) -> None:
        self._close_callout()
        if kind == "chapter":
            self._close_nested()
            self._close_letter()
            self._close_heading()
            self._close_section()
            self._close_chapter()
            self._close_loose()
            self.in_troubleshooting = False
            self.in_spec_table = False
            match = CHAPTER_RE.match(line.text.strip())
            assert match is not None
            number = match.group(1)
            title = _clean(match.group(2) or f"Chapter {number}")
            self.chapter = self._start(
                "chapter", f"{self.spec.doc_key}:ch{number}", title, line, self.spec.doc_key
            )
            self.chapter.number = number
        elif kind == "section":
            self._close_nested()
            self._close_letter()
            self._close_heading()
            self._close_section()
            self._close_loose()
            match = SECTION_RE.match(line.text.strip())
            assert match is not None
            number = match.group(1).upper()
            title = _clean(match.group(2) or f"Section {number}")
            parent = self.chapter.node_id if self.chapter else self.spec.doc_key
            chapter_bit = self.chapter.number if self.chapter else "0"
            self.section = self._start(
                "section",
                f"{self.spec.doc_key}:ch{chapter_bit}:sec{number}",
                title,
                line,
                parent,
            )
            self.section.number = number
        elif kind == "heading":
            self._close_nested()
            self._close_letter()
            self._close_heading()
            self._close_loose()
            match = PARA_RE.match(line.text.strip())
            assert match is not None
            number = match.group(1)
            title = _clean(f"{number}. {match.group(2)}")
            self.in_calibration = "CALIBRATION" in title.upper()
            self.in_troubleshooting = False
            self.in_spec_table = False
            parent = self._heading_parent()
            self.heading = self._start(
                "heading", f"{self.spec.doc_key}:{number}", title, line, parent
            )
            self.heading.number = number
            if self.in_calibration:
                self.table_id = self._ensure_table(f"table:{number}", title, line)
                self.calib_seq = 0
        elif kind == "ja_heading":
            self._close_nested()
            self._close_letter()
            self._close_heading()
            self._close_loose()
            match = JA_HEAD_RE.match(line.text.strip())
            assert match is not None
            number = match.group(1)
            title = _clean(f"{number} {match.group(2)}")
            parent = self._japanese_parent(number)
            self.heading = self._start(
                "ja_heading", f"{self.spec.doc_key}:{number}", title, line, parent
            )
            self.heading.number = number
        elif kind == "malfunction":
            self._close_nested()
            self._close_letter()
            self._close_heading()
            self._close_loose()
            self.malfunction_seq += 1
            match = NUMBER_STEP_RE.match(line.text.strip())
            assert match is not None
            title = _clean(line.text.strip())
            parent = self.table_id or self._heading_parent()
            block = self._start(
                "malfunction",
                f"{self.spec.doc_key}:m{self.malfunction_seq}",
                title,
                line,
                parent,
            )
            block.emit_row = True
            block.number = match.group(1)
            block.malfunction_table_id = self.table_id
            block.malfunction_models = self.group_models
            self.heading = block
        elif kind == "table":
            self._close_nested()
            self._close_letter()
            match = TABLE_RE.match(line.text.strip())
            assert match is not None
            number = match.group(1)
            title = _clean(line.text.strip())
            self.in_troubleshooting = "troubleshoot" in title.lower()
            if self.in_troubleshooting and not self.group_models:
                self.group_models = SERIES_MODELS
            self.in_spec_table = not self.in_troubleshooting
            self.spec_headers = None
            self.spec_header_tokens = []
            self.spec_row = None
            self.table_id = self._ensure_table(f"table:{number}", title, line)
            self.malfunction_seq = 0
        elif kind == "figure":
            self._close_nested()
            self._close_letter()
            match = FIGURE_RE.match(line.text.strip())
            assert match is not None
            number = match.group(1)
            title = _clean(line.text.strip())
            parent = self.heading.node_id if self.heading else self._heading_parent()
            node_id = self._alloc(f"{self.spec.doc_key}:fig:{number}")
            self.nodes.append(
                self._node(
                    node_id=node_id,
                    node_type=NodeType.FIGURE,
                    breadcrumb=self._crumb(title),
                    lines=[line],
                    parent=parent,
                    text=title,
                )
            )
        elif kind in {"caution", "note"}:
            label = line.text.strip()
            parent = self._step_parent()
            prefix = "caution" if kind == "caution" else "note"
            node_id = self._alloc(f"{parent}:{prefix}")
            self.callout = OpenBlock(
                kind=kind,
                node_id=node_id,
                title=label,
                lines=[line],
                parent=parent,
                breadcrumb=self._crumb(label),
            )
        elif kind == "step_letter":
            self._close_nested()
            self._close_letter()
            match = LETTER_STEP_RE.match(line.text.strip())
            assert match is not None
            parent = self._step_parent()
            self._mark_parent_has_steps(parent)
            node_id = self._alloc(f"{parent}:step-{match.group(1)}")
            self.letter_step = self._start("step", node_id, _clean(line.text.strip()), line, parent)
            self._take_pending(self.letter_step)
        elif kind == "step_nested":
            self._close_nested()
            marker = _step_marker(line.text.strip())
            parent_block = self.letter_step or self.heading
            parent = parent_block.node_id if parent_block else self._heading_parent()
            self._mark_parent_has_steps(parent)
            node_id = self._alloc(f"{parent}:step-{marker}")
            self.nested_step = self._start("step", node_id, _clean(line.text.strip()), line, parent)
            self._take_pending(self.nested_step)
        else:
            self._append(line)

    def _append(self, line: RawLine) -> None:
        target = (
            self.callout
            or self.nested_step
            or self.letter_step
            or self.heading
            or self.section
            or self.chapter
        )
        if target is None:
            if self.loose is None:
                node_id = self._alloc(f"{self.spec.doc_key}:p{line.page}")
                self.loose = OpenBlock(
                    kind="loose",
                    node_id=node_id,
                    title=line.text.strip(),
                    lines=[],
                    parent=self.spec.doc_key,
                    breadcrumb=self._crumb(line.text.strip()[:80]),
                )
            target = self.loose
        if (
            self.heading is not None
            and target is self.heading
            and self.heading.kind == "malfunction"
            and not self.heading.has_steps
            and len(self.heading.lines) == self.heading.title_line_count
            and _mostly_upper(line.text)
        ):
            self.heading.title = _clean(f"{self.heading.title} {line.text}")
            self.heading.title_line_count += 1
        target.lines.append(line)

    def _start(self, kind: str, base_id: str, title: str, line: RawLine, parent: str) -> OpenBlock:
        block = OpenBlock(
            kind=kind,
            node_id=self._alloc(base_id),
            title=title,
            lines=[line],
            parent=parent,
            breadcrumb=self._crumb(title),
        )
        return block

    def _close_callout(self) -> None:
        block = self.callout
        if block is None:
            return
        self.callout = None
        node_type = NodeType.CAUTION if block.kind == "caution" else NodeType.PARAGRAPH
        node = self._node(
            node_id=block.node_id,
            node_type=node_type,
            breadcrumb=block.breadcrumb,
            lines=block.lines,
            parent=block.parent,
            text=_block_text(block),
        )
        self.nodes.append(node)
        if block.kind == "caution":
            self.pending_cautions.append(node.node_id)

    def _close_nested(self) -> None:
        block = self.nested_step
        if block is None:
            return
        self.nested_step = None
        self._emit_step(block)

    def _close_letter(self) -> None:
        self._close_nested()
        block = self.letter_step
        if block is None:
            return
        self.letter_step = None
        self._emit_step(block)

    def _emit_step(self, block: OpenBlock) -> None:
        node = self._node(
            node_id=block.node_id,
            node_type=NodeType.STEP,
            breadcrumb=block.breadcrumb,
            lines=block.lines,
            parent=block.parent,
            text=_block_text(block),
            bound_cautions=list(block.bound_cautions),
        )
        self.nodes.append(node)

    def _close_heading(self) -> None:
        self._close_nested()
        self._close_letter()
        block = self.heading
        if block is None:
            return
        self.heading = None
        self._bind_leftover_cautions(block.node_id, block)
        node_type = _heading_type(block)
        node = self._node(
            node_id=block.node_id,
            node_type=node_type,
            breadcrumb=block.breadcrumb,
            lines=block.lines,
            parent=block.parent,
            text=_block_text(block),
            bound_cautions=list(block.bound_cautions),
        )
        if block.emit_row:
            self._apply_group_models(node, block.malfunction_models)
        self.nodes.append(node)
        if block.emit_row:
            self._emit_malfunction_row(block)

    def _close_section(self) -> None:
        self._close_heading()
        block = self.section
        if block is None:
            return
        self.section = None
        self.nodes.append(
            self._node(
                node_id=block.node_id,
                node_type=NodeType.SECTION,
                breadcrumb=block.breadcrumb,
                lines=block.lines,
                parent=block.parent,
                text=_block_text(block),
            )
        )

    def _close_chapter(self) -> None:
        self._close_section()
        block = self.chapter
        if block is None:
            return
        self.chapter = None
        self.nodes.append(
            self._node(
                node_id=block.node_id,
                node_type=NodeType.CHAPTER,
                breadcrumb=block.breadcrumb,
                lines=block.lines,
                parent=block.parent,
                text=_block_text(block),
            )
        )

    def _close_loose(self) -> None:
        block = self.loose
        if block is None:
            return
        self.loose = None
        if not block.lines:
            return
        self.nodes.append(
            self._node(
                node_id=block.node_id,
                node_type=NodeType.PARAGRAPH,
                breadcrumb=block.breadcrumb,
                lines=block.lines,
                parent=block.parent,
                text=_block_text(block),
            )
        )

    def _emit_malfunction_row(self, block: OpenBlock) -> None:
        if block.malfunction_table_id is None:
            return
        steps = [
            item.text
            for item in self.nodes
            if item.parent == block.node_id and item.type is NodeType.STEP
        ]
        unnumbered = [line.text for line in block.lines[block.title_line_count :]]
        body = " ".join([*unnumbered, *steps])
        cells = [block.title, body]
        row_id = self._alloc(f"{block.malfunction_table_id}:r{block.number}")
        row = self._node(
            node_id=row_id,
            node_type=NodeType.TABLE_ROW,
            breadcrumb=self._crumb(block.title),
            lines=block.lines,
            parent=block.malfunction_table_id,
            text=" ".join(cells),
            table=TableContent(headers=MALFUNCTION_HEADERS, cells=cells),
        )
        self._apply_group_models(row, block.malfunction_models)
        self.nodes.append(row)

    def _ensure_table(self, suffix: str, title: str, line: RawLine) -> str:
        node_id = self._alloc(f"{self.spec.doc_key}:{suffix}")
        parent = (
            self.heading.node_id
            if self.heading and self.heading.kind != "malfunction"
            else self._heading_parent()
        )
        self.nodes.append(
            self._node(
                node_id=node_id,
                node_type=NodeType.TABLE,
                breadcrumb=self._crumb(
                    title,
                    include_heading=self.heading is None or self.heading.kind != "malfunction",
                ),
                lines=[line],
                parent=parent,
                text=title,
            )
        )
        return node_id

    def _emit_parts_row(self, line: RawLine) -> None:
        parsed = _parse_parts(line)
        assert parsed is not None
        if self.parts_table_id is None:
            self.parts_table_id = self._ensure_table("parts", "Repair parts", line)
        self.parts_seq += 1
        cells = [
            parsed.item,
            parsed.smr,
            parsed.nsn,
            parsed.cage,
            parsed.part,
            parsed.desc,
            parsed.uoc,
            parsed.qty,
        ]
        row_id = self._alloc(f"{self.parts_table_id}:r{self.parts_seq}")
        row = self._node(
            node_id=row_id,
            node_type=NodeType.TABLE_ROW,
            breadcrumb=self._crumb(f"Item {parsed.item} {parsed.part}"),
            lines=[line],
            parent=self.parts_table_id,
            text=" ".join(cell for cell in cells if cell),
            table=TableContent(headers=PARTS_HEADERS, cells=cells),
        )
        self.nodes.append(row)
        self.parts_row = row

    def _extend_parts_row(self, line: RawLine) -> None:
        row = self.parts_row
        assert row is not None and row.table is not None
        cells = list(row.table.cells)
        qty_tokens = [
            token for x, token in line.tokens if x >= 530 and re.fullmatch(r"\d{1,4}", token)
        ]
        body_tokens = [token for x, token in line.tokens if x < 530]
        body = " ".join(body_tokens).strip()
        if qty_tokens and not cells[7]:
            cells[7] = qty_tokens[-1]
        if body.startswith("UOC:") or (cells[6] and re.fullmatch(r"[A-Z0-9, ]+", body)):
            extra = body.removeprefix("UOC:").strip(" ,")
            cells[6] = (cells[6] + " " + extra).strip()
        elif body:
            cells[5] = (cells[5] + " " + body.strip(" .")).strip()
        row.table = TableContent(headers=PARTS_HEADERS, cells=cells)
        row.elements.append(_element(line))
        row.page_end = max(row.page_end, line.page)
        row.text = " ".join(cell for cell in cells if cell)

    def _apply_group_models(self, node: Node, models: tuple[str, ...]) -> None:
        if models and node.type in {NodeType.PROCEDURE, NodeType.TABLE_ROW}:
            node.applies_to.models = list(models)

    def _emit_grid_row(self, line: RawLine) -> None:
        cells = _split_cells(line)
        if self.table_id is None or not cells:
            return
        table = next(node for node in self.nodes if node.node_id == self.table_id)
        if not GRID_DATA_RE.search(line.text):
            self.spec_header_tokens.extend(cells)
            table.elements.append(_element(line))
            table.page_start = min(table.page_start, line.page)
            table.page_end = max(table.page_end, line.page)
            table.text = _clean(f"{table.text} {line.text}")
            return
        cells = _collapse_label_cells(cells)
        if self.spec_headers is None:
            self.spec_headers = _headers_for_bands(
                self.spec_header_tokens,
                [x for x, _ in cells],
            )
        headers = self.spec_headers
        values = [text for _, text in cells]
        if (
            self.spec_row is not None
            and self.spec_row.table is not None
            and len(values) < len(self.spec_row.table.cells)
            and all(MEASURE_RE.search(value) for value in values)
        ):
            self._merge_measure_cells(values, line)
            return
        if len(values) != len(headers):
            headers = [f"Column {index + 1}" for index in range(len(values))]
        row_id = self._alloc(f"{self.table_id}:r{self.parts_seq + 1}")
        self.parts_seq += 1
        row = self._node(
            node_id=row_id,
            node_type=NodeType.TABLE_ROW,
            breadcrumb=self._crumb(values[0][:80]),
            lines=[line],
            parent=self.table_id,
            text=" ".join(values),
            table=TableContent(headers=headers, cells=values),
        )
        self.nodes.append(row)
        self.spec_row = row
        self.spec_measure_extra = 0

    def _merge_measure_cells(self, values: list[str], line: RawLine) -> None:
        row = self.spec_row
        assert row is not None and row.table is not None
        cells = list(row.table.cells)
        offset = len(cells) - len(values)
        for index, value in enumerate(values):
            cells[offset + index] = _clean(f"{cells[offset + index]} {value}")
        row.table = TableContent(headers=list(row.table.headers), cells=cells)
        row.elements.append(_element(line))
        row.page_end = max(row.page_end, line.page)
        row.text = " ".join(cells)

    def _extend_grid_row(self, line: RawLine) -> None:
        row = self.spec_row
        if row is None or row.table is None:
            return
        cells = list(row.table.cells)
        if MEASURE_RE.search(line.text) and len(cells) > 1:
            index = min(1 + self.spec_measure_extra, len(cells) - 1)
            cells[index] = _clean(f"{cells[index]} {line.text}")
            self.spec_measure_extra += 1
        else:
            cells[0] = _clean(f"{cells[0]} {line.text}")
        row.table = TableContent(headers=list(row.table.headers), cells=cells)
        row.elements.append(_element(line))
        row.page_end = max(row.page_end, line.page)
        row.text = " ".join(cells)

    def _emit_calibration_row(self, line: RawLine) -> None:
        match = CALIB_RE.match(line.text.strip())
        assert match is not None
        if self.table_id is None:
            parent_title = self.heading.title if self.heading else "Calibration"
            anchor = line
            self.table_id = self._ensure_table("calibration", parent_title, anchor)
            self.calib_seq = 0
        self.calib_seq += 1
        cells = [match.group(1), match.group(2), match.group(3)]
        row_id = self._alloc(f"{self.table_id}:r{self.calib_seq}")
        parent = self.table_id
        self.nodes.append(
            self._node(
                node_id=row_id,
                node_type=NodeType.TABLE_ROW,
                breadcrumb=self._crumb(f"{cells[0]} {cells[1]}"),
                lines=[line],
                parent=parent,
                text=" ".join(cells),
                table=TableContent(headers=CALIB_HEADERS, cells=cells),
            )
        )

    def _take_pending(self, block: OpenBlock) -> None:
        if not self.pending_cautions:
            return
        block.bound_cautions.extend(self.pending_cautions)
        for caution_id in self.pending_cautions:
            caution = next(node for node in self.nodes if node.node_id == caution_id)
            caution.parent = block.node_id
        self.pending_cautions.clear()

    def _bind_leftover_cautions(self, parent_id: str, block: OpenBlock | None = None) -> None:
        if not self.pending_cautions:
            return
        if block is not None:
            block.bound_cautions.extend(self.pending_cautions)
        else:
            parent = next(node for node in self.nodes if node.node_id == parent_id)
            parent.bound_cautions.extend(self.pending_cautions)
        for caution_id in self.pending_cautions:
            caution = next(node for node in self.nodes if node.node_id == caution_id)
            caution.parent = parent_id
        self.pending_cautions.clear()

    def _mark_parent_has_steps(self, parent_id: str) -> None:
        for block in (self.heading, self.section, self.chapter, self.letter_step):
            if block is not None and block.node_id == parent_id:
                block.has_steps = True

    def _heading_parent(self) -> str:
        if self.section:
            return self.section.node_id
        if self.chapter:
            return self.chapter.node_id
        return self.spec.doc_key

    def _step_parent(self) -> str:
        if self.letter_step:
            return self.letter_step.node_id
        if self.heading:
            return self.heading.node_id
        return self._heading_parent()

    def _japanese_parent(self, number: str) -> str:
        parts = number.split(".")
        for end in range(len(parts) - 1, 0, -1):
            prefix = ".".join(parts[:end])
            candidate = f"{self.spec.doc_key}:{prefix}"
            if candidate in self.ids:
                return candidate
        return self._heading_parent()

    def _crumb(self, label: str, *, include_heading: bool = True) -> list[str]:
        crumbs = [self.spec.title]
        if self.chapter:
            crumbs.append(self.chapter.title)
        if self.section:
            crumbs.append(self.section.title)
        if include_heading and self.heading and label != self.heading.title:
            crumbs.append(self.heading.title)
        short = label if len(label) <= 140 else label[:137] + "..."
        if not crumbs or crumbs[-1] != short:
            crumbs.append(short)
        return crumbs

    def _alloc(self, base: str) -> str:
        node_id = base
        suffix = 2
        while node_id in self.ids:
            node_id = f"{base}:{suffix}"
            suffix += 1
        self.ids.add(node_id)
        return node_id

    def _add_boilerplate_line(self, line: RawLine) -> None:
        self.boilerplate.setdefault(line.page, []).append(line)

    def _cover_empty_pages(self) -> None:
        for page in self.cover_pages:
            lines = self.boilerplate.get(page, [])
            has_body = any(
                element.page == page
                for node in self.nodes
                if node.type is not NodeType.BOILERPLATE
                for element in node.elements
            )
            if not has_body or lines:
                self._emit_boilerplate(page, lines)

    def _emit_boilerplate(self, page: int, lines: list[RawLine]) -> None:
        text = " ".join(line.text for line in lines) if lines else "no text layer"
        node_id = self._alloc(f"{self.spec.doc_key}:boilerplate:p{page}")
        self.nodes.append(
            self._node(
                node_id=node_id,
                node_type=NodeType.BOILERPLATE,
                breadcrumb=[self.spec.title, "boilerplate"],
                lines=lines,
                parent=self.spec.doc_key,
                text=text,
                page_start=page,
                page_end=page,
                retrievable=False,
            )
        )

    def _resolve_references(self) -> None:
        ids = {node.node_id for node in self.nodes}
        for node in self.nodes:
            found: list[str] = []
            if self.spec.lang == "ja":
                for match in JA_REF_RE.finditer(node.text):
                    candidate = f"{self.spec.doc_key}:{match.group(1)}"
                    if candidate in ids and candidate != node.node_id:
                        found.append(candidate)
            else:
                for pattern, prefix in (
                    (PARA_REF_RE, ""),
                    (TABLE_REF_RE, "table:"),
                    (FIG_REF_RE, "fig:"),
                ):
                    for match in pattern.finditer(node.text):
                        candidate = f"{self.spec.doc_key}:{prefix}{match.group(1)}"
                        if candidate in ids and candidate != node.node_id:
                            found.append(candidate)
            deduped: list[str] = []
            for item in found:
                if item not in deduped:
                    deduped.append(item)
            node.references = deduped[:12]

    def _inherit_applicability(self) -> None:
        by_id = {node.node_id: node for node in self.nodes}
        for _ in range(6):
            changed = False
            for node in self.nodes:
                parent = by_id.get(node.parent or "")
                if parent is None:
                    continue
                if not node.applies_to.models and parent.applies_to.models:
                    node.applies_to.models = list(parent.applies_to.models)
                    changed = True
                if not node.applies_to.variants and parent.applies_to.variants:
                    node.applies_to.variants = list(parent.applies_to.variants)
                    changed = True
            if not changed:
                break

    def _assign_siblings(self) -> None:
        groups: dict[tuple[str | None, NodeType], list[Node]] = {}
        for node in self.nodes:
            if node.parent is None:
                continue
            groups.setdefault((node.parent, node.type), []).append(node)
        for group in groups.values():
            for index, node in enumerate(group):
                siblings: list[str] = []
                if index > 0:
                    siblings.append(group[index - 1].node_id)
                if index + 1 < len(group):
                    siblings.append(group[index + 1].node_id)
                node.siblings = siblings

    def _node(
        self,
        *,
        node_id: str,
        node_type: NodeType,
        breadcrumb: list[str],
        lines: list[RawLine],
        parent: str | None,
        text: str,
        page_start: int | None = None,
        page_end: int | None = None,
        bound_cautions: list[str] | None = None,
        table: TableContent | None = None,
        retrievable: bool = True,
    ) -> Node:
        elements = [_element(line) for line in lines]
        if page_start is None:
            page_start = elements[0].page if elements else 1
        if page_end is None:
            page_end = elements[-1].page if elements else page_start
        models, variants = _applicability(text)
        return Node(
            node_id=node_id,
            doc_key=self.spec.doc_key,
            lang=self.spec.lang,
            edition=Edition(version=self.spec.edition),
            doc_type=self.spec.doc_type,
            type=node_type,
            breadcrumb=breadcrumb or [self.spec.title],
            page_start=page_start,
            page_end=page_end,
            elements=elements,
            text=text.strip() or self.spec.title,
            parent=parent,
            siblings=[],
            bound_cautions=bound_cautions or [],
            references=[],
            applies_to=AppliesTo(
                models=models,
                series=list(self.spec.series),
                variants=variants,
            ),
            table=table,
            retrievable=retrievable,
        )

    def _is_parts_header(self, text: str) -> bool:
        if self.spec.doc_type is not DocType.PARTS:
            return False
        upper = text.upper()
        if upper.startswith(("ITEM ", "(1)", "NO CODE", "ITEM NO")):
            return True
        return "SMR" in upper and "NSN" in upper and "DESCRIPTION" in upper


def build_nodes(
    spec: DocumentSpec,
    content: list[RawLine],
    boilerplate: dict[int, list[RawLine]],
    page_count: int,
    cover_pages: list[int] | None = None,
) -> list[Node]:
    """Structure one document. `cover_pages` limits the page-coverage pass."""

    return Builder(spec, content, boilerplate, page_count, cover_pages).build()


def _split_cells(line: RawLine, gap: float = CELL_GAP) -> list[tuple[float, str]]:
    """Group tokens into cells when a wide gap separates columns."""

    cells: list[tuple[float, list[str]]] = []
    previous_x: float | None = None
    for x, token in line.tokens:
        if previous_x is None or x - previous_x >= gap:
            cells.append((x, [token]))
        else:
            cells[-1][1].append(token)
        previous_x = x
    return [(x, " ".join(words)) for x, words in cells]


def _collapse_label_cells(
    cells: list[tuple[float, str]],
) -> list[tuple[float, str]]:
    """Join a short label fragment such as '@ curb' into the condition cell."""

    if len(cells) < 3:
        return cells
    collapsed: list[tuple[float, str]] = [cells[0]]
    for x, text in cells[1:]:
        later_has_measure = any(MEASURE_RE.search(value) for _, value in cells)
        if later_has_measure and not MEASURE_RE.search(text) and len(text) <= 20:
            start, previous = collapsed[-1]
            collapsed[-1] = (start, _clean(f"{previous} {text}"))
        else:
            collapsed.append((x, text))
    return collapsed


def _headers_for_bands(
    tokens: list[tuple[float, str]],
    bands: list[float],
) -> list[str]:
    grouped: list[list[str]] = [[] for _ in bands]

    def band_index(x: float) -> int:
        chosen = 0
        for index, start in enumerate(bands):
            if x >= start - 8:
                chosen = index
        return chosen

    for x, token in tokens:
        grouped[band_index(x)].append(token)
    return [" ".join(words) or f"Column {index + 1}" for index, words in enumerate(grouped)]


def _heading_type(block: OpenBlock) -> NodeType:
    if block.kind == "malfunction" or block.has_steps:
        return NodeType.PROCEDURE
    if block.kind == "ja_heading":
        depth = block.number.count(".") + 1
        if depth <= 2:
            return NodeType.SECTION
        return NodeType.PARAGRAPH
    return NodeType.PARAGRAPH


def _block_text(block: OpenBlock) -> str:
    parts = [line.text.strip() for line in block.lines if line.text.strip()]
    return " ".join(parts)


def _element(line: RawLine) -> Element:
    return Element(
        page=line.page,
        bbox=[round(line.x0, 2), round(line.y0, 2), round(line.x1, 2), round(line.y1, 2)],
        text=line.text,
    )


def _clean(text: str) -> str:
    return " ".join(text.split())


def _mostly_upper(text: str) -> bool:
    letters = [char for char in text if char.isalpha()]
    if len(letters) < 4:
        return False
    return sum(char.isupper() for char in letters) / len(letters) > 0.8


def _is_malfunction(text: str) -> bool:
    match = NUMBER_STEP_RE.match(text)
    if match is None:
        return False
    body = match.group(2)
    return _mostly_upper(body) and len(body) <= 140


def _step_marker(text: str) -> str:
    word = WORD_STEP_RE.match(text)
    if word:
        return f"step{word.group(1)}"
    paren = PAREN_STEP_RE.match(text)
    if paren:
        return f"p{paren.group(1)}"
    number = NUMBER_STEP_RE.match(text)
    if number:
        return number.group(1)
    return "x"


def _starts_structure(text: str) -> bool:
    return bool(
        CHAPTER_RE.match(text)
        or SECTION_RE.match(text)
        or PARA_RE.match(text)
        or TABLE_RE.match(text)
        or FIGURE_RE.match(text)
        or CALLOUT_RE.match(text)
    )


def _parse_parts(line: RawLine) -> _PartsFields | None:
    tokens = [(x, token) for x, token in line.tokens if token != "*"]
    if len(tokens) < 4:
        return None
    if not re.fullmatch(r"\d{1,4}", tokens[0][1]) or not SMR_RE.fullmatch(tokens[1][1]):
        return None
    # In this manual the item and SMR columns are at the left margin. Group
    # headings such as "1000 FRONT AXLE ASSEMBLY" have the same token shapes,
    # but start in the description column instead.
    if not 0 <= tokens[0][0] < tokens[1][0] < 100:
        return None
    rest = tokens[2:]
    qty_tokens = [token for x, token in rest if x >= 530 and re.fullmatch(r"\d{1,4}", token)]
    body = [(x, token) for x, token in rest if x < 530]
    qty = qty_tokens[-1] if qty_tokens else ""
    if not body:
        return None
    nsn = ""
    if body[0][0] < 175 and NSN_RE.fullmatch(body[0][1]):
        _, nsn = body.pop(0)
    cage = ""
    if body and 175 <= body[0][0] < 210 and CAGE_RE.fullmatch(body[0][1]):
        _, cage = body.pop(0)
    # A five-character part number is valid in the part column. Its shape alone
    # must never make it a CAGE code when that cell (or the NSN cell) is blank.
    if not body or not 210 <= body[0][0] < 320:
        return None
    _, part = body.pop(0)
    desc = " ".join(token for _, token in body).strip(" .")
    return _PartsFields(tokens[0][1], tokens[1][1], nsn, cage, part, desc, "", qty)


def _applicability(text: str) -> tuple[list[str], list[str]]:
    models: list[str] = []
    variants: list[str] = []
    for match in MODEL_RE.finditer(text):
        token = match.group(1) + (match.group(2) or "")
        if token in VEHICLE_MODELS and token not in models:
            models.append(token)
        if match.group(2) and match.group(2) not in variants:
            variants.append(match.group(2))
    for match in PUMP_RE.finditer(text):
        if match.group(0) not in models:
            models.append(match.group(0))
    if re.search(r"\bA2\b", text) and "A2" not in variants:
        variants.append("A2")
    return models, variants
