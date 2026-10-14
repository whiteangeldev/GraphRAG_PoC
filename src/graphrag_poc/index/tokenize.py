"""Lexical tokens for the sparse channel.

English and part numbers split on word boundaries. Japanese runs have no spaces,
so each run is kept whole when it is short and is also split into overlapping
character pairs. Full-width characters are folded to half-width first.
"""

import hashlib
import re
import unicodedata

_LATIN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_JAPANESE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]+")
_MAX_WHOLE_RUN = 16


def normalize_token_text(text: str) -> str:
    """NFKC-fold and lowercase so full-width and half-width forms match."""

    folded = unicodedata.normalize("NFKC", text).replace("\u3000", " ")
    return " ".join(folded.split()).lower()


def tokenize(text: str) -> list[str]:
    """Return the sparse-channel tokens for one passage or query."""

    normalized = normalize_token_text(text)
    tokens: list[str] = []
    for match in _LATIN.finditer(normalized):
        token = match.group()
        if len(token) >= 2:
            tokens.append(token)
    for match in _JAPANESE.finditer(normalized):
        run = match.group()
        if len(run) <= _MAX_WHOLE_RUN:
            tokens.append(run)
        if len(run) >= 2:
            tokens.extend(run[index : index + 2] for index in range(len(run) - 1))
    return tokens


def token_index(token: str) -> int:
    """Stable unsigned 32-bit id. Python's hash() is not stable across processes."""

    digest = hashlib.blake2s(token.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(digest, "big")


def term_frequencies(text: str) -> tuple[list[int], list[float]]:
    """Sparse indices and presence weights. A token counts once.

    Presence keeps a long page from outranking the short passage that actually
    contains the query. Qdrant applies inverse document frequency at search time.
    """

    present: dict[int, float] = {}
    for token in tokenize(text):
        present[token_index(token)] = 1.0
    ordered = sorted(present.items())
    return [index for index, _ in ordered], [weight for _, weight in ordered]
