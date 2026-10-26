"""Build report: counts, orphan nodes, provenance, and the derived-edge sample."""

from dataclasses import dataclass
from pathlib import Path

from graphrag_poc.graph.build import GraphData
from graphrag_poc.graph.client import make_driver
from graphrag_poc.ingest.catalog import ROOT
from graphrag_poc.models.graph import EdgeType, GraphLabel

REPORT_PATH = ROOT / "docs" / "graph_build_report.md"
_SAMPLE_LIMIT = 100
_ORPHAN_LIST_LIMIT = 20
_LABELS = [item.value for item in GraphLabel]
_EDGES = [item.value for item in EdgeType]


@dataclass(frozen=True)
class Orphan:
    """A node with no relationship."""

    label: str
    key: str


@dataclass(frozen=True)
class DerivedEdge:
    """One model-extracted edge in the review sample."""

    type: str
    start_id: str
    end_id: str
    rule: str
    weight: float


@dataclass(frozen=True)
class BuildSurvey:
    """Facts the report prints. Counts are the database counts."""

    counts: dict[str, int]
    orphans: list[Orphan]
    missing_provenance: int
    doubled_provenance: int
    derived_total: int
    derived_sample: list[DerivedEdge]


def orphan_nodes(graph: GraphData) -> list[tuple[str, str]]:
    """Nodes in the build that no edge touches, as (label, business key)."""

    linked: set[str] = set()
    for edge in graph.edges:
        linked.add(edge.start_id)
        linked.add(edge.end_id)
    found: list[tuple[str, str]] = []
    found.extend(("Document", row["doc_key"]) for row in graph.documents if row["id"] not in linked)
    found.extend(
        ("Passage", str(row["node_id"])) for row in graph.passages if str(row["id"]) not in linked
    )
    found.extend(
        ("Malfunction", str(row["node_id"]))
        for row in graph.malfunctions
        if str(row["id"]) not in linked
    )
    found.extend(("Part", row["part_number"]) for row in graph.parts if row["id"] not in linked)
    found.extend(("Model", row["name"]) for row in graph.models if row["id"] not in linked)
    found.extend(
        ("Case", str(row["case_id"])) for row in graph.cases if str(row["id"]) not in linked
    )
    found.sort()
    return found


def survey_database() -> BuildSurvey:
    """Read counts, orphans, provenance, and derived edges from Neo4j."""

    driver = make_driver()
    try:
        with driver.session() as session:
            counts: dict[str, int] = {}
            for record in session.run(
                "MATCH (n) UNWIND labels(n) AS label RETURN label, count(n) AS c"
            ):
                counts[str(record["label"])] = _as_int(record["c"])
            for record in session.run("MATCH ()-[r]->() RETURN type(r) AS label, count(r) AS c"):
                counts[str(record["label"])] = _as_int(record["c"])
            orphans = [
                Orphan(str(record["label"]), str(record["key"]))
                for record in session.run(
                    "MATCH (n) WHERE NOT (n)--() "
                    "RETURN labels(n)[0] AS label, "
                    "CASE labels(n)[0] "
                    "WHEN 'Document' THEN n.doc_key "
                    "WHEN 'Passage' THEN n.node_id "
                    "WHEN 'Malfunction' THEN n.node_id "
                    "WHEN 'Part' THEN n.part_number "
                    "WHEN 'Model' THEN n.name "
                    "WHEN 'Case' THEN n.case_id "
                    "ELSE coalesce(n.node_id, n.name) END AS key "
                    "ORDER BY label, key"
                )
            ]
            missing = session.run(
                "MATCH ()-[r]->() "
                "WHERE r.case_id IS NULL AND (r.doc_key IS NULL OR r.page_start IS NULL) "
                "RETURN count(r) AS n"
            ).single()
            doubled = session.run(
                "MATCH ()-[r]->() "
                "WHERE r.case_id IS NOT NULL AND r.doc_key IS NOT NULL "
                "RETURN count(r) AS n"
            ).single()
            derived_count = session.run(
                "MATCH ()-[r]->() WHERE r.derived = true RETURN count(r) AS n"
            ).single()
            sample = [
                DerivedEdge(
                    str(record["type"]),
                    str(record["start_id"]),
                    str(record["end_id"]),
                    str(record["rule"]),
                    _as_float(record["weight"]),
                )
                for record in session.run(
                    "MATCH (a)-[r]->(b) WHERE r.derived = true "
                    "RETURN type(r) AS type, "
                    "coalesce(a.node_id, a.part_number, a.case_id, a.doc_key, a.name) AS start_id, "
                    "coalesce(b.node_id, b.part_number, b.case_id, b.doc_key, b.name) AS end_id, "
                    "r.rule AS rule, r.weight AS weight "
                    "ORDER BY type, start_id, end_id LIMIT $limit",
                    limit=_SAMPLE_LIMIT,
                )
            ]
    finally:
        driver.close()
    if missing is None or doubled is None or derived_count is None:
        raise RuntimeError("the graph survey did not return a count")
    return BuildSurvey(
        counts=dict(sorted(counts.items())),
        orphans=orphans,
        missing_provenance=_as_int(missing["n"]),
        doubled_provenance=_as_int(doubled["n"]),
        derived_total=_as_int(derived_count["n"]),
        derived_sample=sample,
    )


def render_report(survey: BuildSurvey) -> str:
    """Render the survey as the build report."""

    lines = [
        "# Graph build report",
        "",
        "The rule build reads the node files and the service cases and loads Neo4j.",
        "The counts are the counts in the database.",
        "",
        "## Counts",
        "",
        "| Label | Count |",
        "|---|---:|",
    ]
    for label, count in _ordered_counts(survey.counts):
        lines.append(f"| {label} | {count} |")
    lines.extend(["", "## Orphan nodes", ""])
    lines.append("An orphan node has no relationship.")
    if survey.orphans:
        lines.append(f"This build has {len(survey.orphans)} orphan nodes.")
        lines.extend(["", "| Label | Key |", "|---|---|"])
        listed = survey.orphans[:_ORPHAN_LIST_LIMIT]
        lines.extend(f"| {item.label} | {item.key} |" for item in listed)
        if len(survey.orphans) > len(listed):
            lines.append("")
            lines.append(f"The table lists {len(listed)} of {len(survey.orphans)} orphan nodes.")
    else:
        lines.append("This build has no orphan nodes.")
    lines.extend(
        [
            "",
            "## Provenance",
            "",
            f"{survey.missing_provenance} edges have no document page and no case id.",
            f"{survey.doubled_provenance} edges name both a document page and a case id.",
            "",
            "## Derived edges",
            "",
        ]
    )
    if survey.derived_total == 0:
        lines.append("This build has no derived edges. The sample of 100 derived edges is empty.")
    else:
        sample_size = len(survey.derived_sample)
        lines.append(f"The sample lists {sample_size} of {survey.derived_total} derived edges.")
        lines.extend(["", "| Type | Start | End | Rule | Weight |", "|---|---|---|---|---:|"])
        for edge in survey.derived_sample:
            lines.append(
                f"| {edge.type} | {edge.start_id} | {edge.end_id} | {edge.rule} | {edge.weight} |"
            )
    lines.append("")
    return "\n".join(lines)


def counts_in_report(text: str) -> dict[str, int]:
    """Read the count table back from a rendered report."""

    found: dict[str, int] = {}
    in_counts = False
    for line in text.splitlines():
        if line == "## Counts":
            in_counts = True
            continue
        if in_counts and line.startswith("## "):
            break
        if not in_counts or not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == 2 and cells[1].isdigit():
            found[cells[0]] = int(cells[1])
    return found


def write_report(survey: BuildSurvey, path: Path | None = None) -> str:
    """Write the report and return its text."""

    text = render_report(survey)
    destination = REPORT_PATH if path is None else path
    destination.write_text(text, encoding="utf-8")
    return text


def _ordered_counts(counts: dict[str, int]) -> list[tuple[str, int]]:
    order = [*_LABELS, *_EDGES]
    rows = [(name, counts.get(name, 0)) for name in order]
    rows.extend((name, counts[name]) for name in sorted(counts) if name not in order)
    return rows


def _as_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RuntimeError(f"unexpected count {value!r}")
    return value


def _as_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise RuntimeError(f"unexpected weight {value!r}")
    return float(value)
