"""Resolve stored paragraph references without treating contents rows as instructions.

The ingester allocates a numeric suffix when a numbered heading occurs again.
An unsuffixed paragraph reference therefore names the paragraph, not necessarily
its first (often contents-page) occurrence. Resolution uses only these stored
identifiers, passage types, headings, and body text; it never discovers references
by searching the source text.
"""

import re

_PARAGRAPH = re.compile(r"^([^:]+):(\d{1,2}-\d{1,3}(?:\.\d+)*)(?::([1-9]\d*))?$")
_HEADING = re.compile(r"^(\d{1,2}-\d{1,3}(?:\.\d+)*)\.\s+(\S.*)$", re.DOTALL)
_CONTINUED = re.compile(r"\(\s*cont(?:inued|[\u2019\u2018'`]\s*d|d)?\.?\s*\)", re.IGNORECASE)
_PRINTED_PAGE = re.compile(r"\b\d{1,2}-\d{1,3}(?:\.\d+)*(?![\w.-])")
_DOT_LEADER = re.compile(r"(?:\.\s*){3,}")
_CONTENTS = re.compile(r"(?:table of )?contents|(?:alphabetical )?index", re.IGNORECASE)
_WORDS = re.compile(r"[^\W\d_]+", re.UNICODE)


class ReferenceResolver:
    """Index body occurrences once for a deterministic graph build.

    A reference to a numbered paragraph expands to its compatible body roots,
    including continuation roots. An explicit occurrence suffix keeps its exact
    target. Other explicit IDs keep the existing exact-ID semantics.
    """

    def __init__(self, passages: list[dict[str, object]]) -> None:
        self._by_id = {str(node["node_id"]): node for node in passages}
        groups: dict[tuple[str, str], list[dict[str, object]]] = {}
        for node_id, node in self._by_id.items():
            match = _PARAGRAPH.fullmatch(node_id)
            if match is not None and match[1] == _document(node):
                groups.setdefault((match[1], match[2]), []).append(node)
        self._bodies = {key: self._body_occurrences(nodes, key[1]) for key, nodes in groups.items()}

    def resolve(self, source: dict[str, object], reference_id: str) -> tuple[str, ...]:
        """Return only existing, safe targets; unresolved references add no edge."""

        source_id = str(source["node_id"])
        match = _PARAGRAPH.fullmatch(reference_id)
        if match is None:
            return (
                (reference_id,) if reference_id in self._by_id and reference_id != source_id else ()
            )
        if match[1] != _document(source):
            return ()
        targets: tuple[str, ...]
        if match[3] is not None:
            target = self._by_id.get(reference_id)
            if target is None or _document(target) != match[1]:
                return ()
            targets = (reference_id,) if _body_title(target, match[2]) else ()
        else:
            targets = self._bodies.get((match[1], match[2]), ())
        return tuple(target for target in targets if target != source_id)

    @staticmethod
    def _body_occurrences(nodes: list[dict[str, object]], number: str) -> tuple[str, ...]:
        bodies: list[tuple[str, str]] = []
        for node in nodes:
            title = _body_title(node, number)
            if title:
                bodies.append((str(node["node_id"]), title))
        # A reused paragraph number with conflicting body headings is ambiguous.
        # Never fall back to the first occurrence, which may be a contents row.
        if len({title for _, title in bodies}) != 1:
            return ()
        return tuple(sorted(node_id for node_id, _ in bodies))


def _document(node: dict[str, object]) -> str:
    return str(node.get("doc_key") or str(node["node_id"]).split(":", 1)[0])


def _body_title(node: dict[str, object], number: str) -> str | None:
    if node.get("type") not in {"procedure", "paragraph"}:
        return None
    heading = _heading(node, number)
    if heading is None or _is_contents(node, heading):
        return None
    if node.get("type") == "paragraph" and not _has_body(node, heading):
        return None
    return _normalized(_CONTINUED.sub("", heading)) or None


def _heading(node: dict[str, object], number: str) -> str | None:
    breadcrumb = node.get("breadcrumb")
    if isinstance(breadcrumb, list):
        for item in reversed(breadcrumb):
            match = _HEADING.match(str(item).strip())
            if match is not None and match[1] == number:
                return match[2].strip()
    # Elements retain the heading line when the flattened text contains prose.
    elements = node.get("elements")
    if isinstance(elements, list) and elements and isinstance(elements[0], dict):
        match = _HEADING.match(str(elements[0].get("text") or "").strip())
        if match is not None and match[1] == number:
            return match[2].strip()
    text = str(node.get("text") or "").strip()
    match = _HEADING.match(text.splitlines()[0] if text else "")
    if match is None or match[1] != number:
        return None
    heading = match[2].strip()
    # When metadata is absent, a flattened all-capitals heading can still be
    # separated from its mixed-case prose without interpreting the prose.
    title: list[str] = []
    for token in heading.split():
        if any(char.islower() for char in token) and not _CONTINUED.fullmatch(token):
            break
        title.append(token)
    return " ".join(title) if title else heading


def _is_contents(node: dict[str, object], heading: str) -> bool:
    breadcrumb = node.get("breadcrumb")
    if isinstance(breadcrumb, list) and any(
        _CONTENTS.fullmatch(str(item).strip().strip(".:")) for item in breadcrumb
    ):
        return True
    return bool(_DOT_LEADER.search(heading) or _PRINTED_PAGE.search(heading))


def _has_body(node: dict[str, object], heading: str) -> bool:
    match = _HEADING.match(str(node.get("text") or "").strip())
    if match is None:
        return False
    text = _normalized(match[2])
    title = _normalized(heading)
    if not text.startswith(title):
        return False
    # A repeated heading and a printed page footer are not body prose.
    remainder = text[len(title) :].strip()
    words = _WORDS.findall(remainder)
    return len(words) >= 3 and sum(map(len, words)) >= 12


def _normalized(text: str) -> str:
    return " ".join(re.findall(r"\w+", text.casefold()))
