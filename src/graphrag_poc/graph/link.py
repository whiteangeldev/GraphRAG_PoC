"""Link codes, part numbers, and model names in a question to graph nodes."""

import math
import re
from dataclasses import dataclass
from typing import Any

from neo4j import Driver

from graphrag_poc.graph.config import DENSE_LINK_THRESHOLD
from graphrag_poc.index.embed import Embedder

_MODEL = re.compile(r"\bM\d{3,4}(?:A\d)?\b")
_PART = re.compile(r"[A-Za-z0-9][A-Za-z0-9/-]{4,}")
_CODE_LIKE = re.compile(r"\d+\.\s+\S+")
_TABLE_OR_CASE = frozenset({"Malfunction", "Part", "Case"})


@dataclass(frozen=True)
class Term:
    """One canonical name and the surface form the question may contain."""

    label: str
    key: str
    surface: str
    node_id: str


@dataclass(frozen=True)
class Link:
    """A question span linked to one graph node."""

    label: str
    key: str
    node_id: str
    method: str
    score: float

    @property
    def has_table_or_case(self) -> bool:
        """True when this node is a malfunction, part, or case."""

        return self.label in _TABLE_OR_CASE


@dataclass
class TermTable:
    """Canonical codes, part numbers, and model names."""

    terms: tuple[Term, ...]
    _vectors: list[list[float]] | None = None

    def vectors(self, embedder: Embedder) -> list[list[float]]:
        if self._vectors is None:
            self._vectors = embedder.embed_passages([term.surface for term in self.terms])
        return self._vectors


def load_term_table(driver: Driver, build: str | None = None) -> TermTable:
    """Read the term table. `build` limits the read to that graph."""

    where = ""
    values: dict[str, Any] = {}
    if build is not None:
        where = "WHERE coalesce(n.build, 'corpus') = $build "
        values["build"] = build
    terms: list[Term] = []
    with driver.session() as session:
        for record in session.run(
            "MATCH (n:Malfunction) "
            f"{where}"
            "RETURN n.code AS key, n.node_id AS node_id ORDER BY node_id",
            **values,
        ):
            code = str(record["key"])
            terms.append(Term("Malfunction", code, code, str(record["node_id"])))
        for record in session.run(
            "MATCH (n:Part) "
            f"{where}"
            "RETURN n.part_number AS key, n.node_id AS node_id ORDER BY node_id",
            **values,
        ):
            number = str(record["key"])
            terms.append(Term("Part", number, number, str(record["node_id"])))
        for record in session.run(
            "MATCH (n:Model) "
            f"{where}"
            "RETURN n.name AS key ORDER BY key",
            **values,
        ):
            name = str(record["key"])
            terms.append(Term("Model", name, name, name))
    return TermTable(tuple(_prefer_smallest(terms)))


def link_text(
    question: str,
    table: TermTable,
    *,
    embedder: Embedder | None = None,
    dense_threshold: float = DENSE_LINK_THRESHOLD,
) -> list[Link]:
    """Exact surface forms first. A dense match is used only above the threshold."""

    exact = _exact_links(question, table)
    if exact or embedder is None or not table.terms:
        return exact
    found = list(exact)
    linked = {link.label for link in exact}
    if _CODE_LIKE.search(question):
        linked.add("Malfunction")
    for link in _dense_links(question, table, embedder, dense_threshold):
        if link.label not in linked:
            found.append(link)
            linked.add(link.label)
    return found


def _prefer_smallest(terms: list[Term]) -> list[Term]:
    best: dict[tuple[str, str], Term] = {}
    for term in terms:
        current = best.get((term.label, term.key))
        if current is None or term.node_id < current.node_id:
            best[(term.label, term.key)] = term
    return [best[key] for key in sorted(best)]


def _exact_links(question: str, table: TermTable) -> list[Link]:
    found: list[Link] = []
    codes = [
        term for term in table.terms if term.label == "Malfunction" and term.surface in question
    ]
    codes.sort(key=lambda term: len(term.surface), reverse=True)
    kept: list[Term] = []
    for term in codes:
        longer = any(term.surface in item.surface and term.surface != item.surface for item in kept)
        if longer:
            continue
        kept.append(term)
        found.append(Link("Malfunction", term.key, term.node_id, "exact", 1.0))
    numbers = {term.key.upper(): term for term in table.terms if term.label == "Part"}
    seen_parts: set[str] = set()
    for match in _PART.findall(question):
        part = numbers.get(match.upper())
        if part is None or part.key in seen_parts:
            continue
        seen_parts.add(part.key)
        found.append(Link("Part", part.key, part.node_id, "exact", 1.0))
    names = {term.key for term in table.terms if term.label == "Model"}
    for name in _MODEL.findall(question):
        if name in names:
            found.append(Link("Model", name, name, "exact", 1.0))
    return found


def _dense_links(
    question: str,
    table: TermTable,
    embedder: Embedder,
    threshold: float,
) -> list[Link]:
    query = embedder.embed_query(question)
    best: dict[str, tuple[float, Term]] = {}
    second: dict[str, float] = {}
    for term, vector in zip(table.terms, table.vectors(embedder), strict=True):
        score = _cosine(query, vector)
        current = best.get(term.label)
        if current is None or score > current[0]:
            if current is not None:
                second[term.label] = current[0]
            best[term.label] = (score, term)
        elif score > second.get(term.label, 0.0):
            second[term.label] = score
    found: list[Link] = []
    for label, (score, term) in best.items():
        if score < threshold or score - second.get(label, 0.0) < 0.05:
            continue
        found.append(Link(label, term.key, term.node_id, "dense", round(score, 4)))
    return found


def _cosine(left: list[float], right: list[float]) -> float:
    dot = norm_left = norm_right = 0.0
    for one, other in zip(left, right, strict=False):
        dot += one * other
        norm_left += one * one
        norm_right += other * other
    if norm_left == 0.0 or norm_right == 0.0:
        return 0.0
    return dot / math.sqrt(norm_left * norm_right)
