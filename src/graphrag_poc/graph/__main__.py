"""Build the rule graph, load Neo4j, and write the build report."""

import json

from graphrag_poc.graph.build import GraphData, build_from_disk
from graphrag_poc.graph.export import write_csv
from graphrag_poc.graph.load import (
    OIL_COOLER_CAUTIONS,
    OIL_COOLER_NEXT,
    load_csv,
    spot_check,
)
from graphrag_poc.graph.mentions import derive_mentions
from graphrag_poc.graph.report import (
    REPORT_PATH,
    counts_in_report,
    orphan_nodes,
    survey_database,
    write_report,
)


def main() -> None:
    first = build_from_disk()
    second = build_from_disk()
    if first.fingerprint() != second.fingerprint() or first.counts() != second.counts():
        raise SystemExit("two builds of the same files differ")
    mentions = derive_mentions(first)
    if mentions != derive_mentions(second):
        raise SystemExit("two mention builds differ")
    first = GraphData(
        documents=first.documents,
        passages=first.passages,
        malfunctions=first.malfunctions,
        parts=first.parts,
        models=first.models,
        cases=first.cases,
        edges=sorted(
            [*first.edges, *mentions],
            key=lambda edge: (
                edge.type,
                edge.start_id,
                edge.end_id,
                edge.keyword,
                edge.step_number,
                edge.step_text,
            ),
        ),
    )
    directory = write_csv(first)
    load_csv(directory)
    survey = survey_database()
    if survey.counts != first.counts():
        raise SystemExit(f"database counts {survey.counts} differ from the build {first.counts()}")
    if [(item.label, item.key) for item in survey.orphans] != orphan_nodes(first):
        raise SystemExit("orphan nodes in the database differ from the build")
    text = write_report(survey)
    parsed = counts_in_report(text)
    for label, count in survey.counts.items():
        if parsed.get(label) != count:
            raise SystemExit(f"the report count for {label} does not match the database")
    if parsed.get("MENTIONS") != survey.counts.get("MENTIONS", 0):
        raise SystemExit("the report's MENTIONS count does not match the database")
    found = spot_check()
    if found["next"] != [OIL_COOLER_NEXT] or found["cautions"] != list(OIL_COOLER_CAUTIONS):
        raise SystemExit(f"oil-cooler links are wrong: {found}")
    keyword = found["candidate_keyword"]
    if not found["candidate_part"] or keyword not in {"ALTERNATOR", "GENERATOR"}:
        raise SystemExit(f"charging malfunction has no candidate part: {found}")
    if found["edges_without_provenance"] != 0:
        raise SystemExit(f"an edge has no page and no case id: {found}")
    print(
        json.dumps(
            {"report": str(REPORT_PATH), "counts": first.counts(), "spot_check": found},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
