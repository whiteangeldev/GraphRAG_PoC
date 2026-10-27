"""Exact known part numbers, including catalogue decimal and parenthesis suffixes."""

import re
from collections.abc import Iterable

_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9/-]{4,}")
_LEFT = re.compile(r"(?:[A-Za-z0-9/-]|[A-Za-z0-9][.(])$")
_RIGHT = re.compile(r"^(?:[A-Za-z0-9/-]|[.(][A-Za-z0-9])")


class PartMatcher:
    """Keep common tokens fast; match unusual stored numbers literally."""

    def __init__(self, numbers: Iterable[str]) -> None:
        self._numbers = {number.upper(): number for number in numbers}
        self._literal = [
            (number, re.compile(re.escape(number), re.IGNORECASE))
            for number in self._numbers.values()
            if _TOKEN.fullmatch(number) is None
        ]

    def find(self, text: str) -> set[str]:
        found = set()
        for match in _TOKEN.finditer(text):
            number = self._numbers.get(match[0].upper())
            if number is not None and _complete(text, match.start(), match.end()):
                found.add(number)
        folded = text.upper()
        for number, pattern in self._literal:
            if number.upper() not in folded:
                continue
            if any(_complete(text, match.start(), match.end()) for match in pattern.finditer(text)):
                found.add(number)
        return found


def _complete(text: str, start: int, end: int) -> bool:
    return not (_LEFT.search(text[max(0, start - 2) : start]) or _RIGHT.search(text[end : end + 2]))
