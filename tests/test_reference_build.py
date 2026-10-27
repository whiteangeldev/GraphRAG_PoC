"""Reference targets follow stored structure rather than contents aliases."""

import json
from pathlib import Path

from graphrag_poc.graph.build import GraphData, build_graph


def _node(
    node_id: str,
    kind: str,
    text: str,
    *,
    heading: str = "",
    page: int = 1,
    references: list[str] | None = None,
    breadcrumb: list[str] | None = None,
) -> dict[str, object]:
    return {
        "node_id": node_id,
        "doc_key": node_id.split(":", 1)[0],
        "retrievable": True,
        "type": kind,
        "text": text,
        "page_start": page,
        "page_end": page,
        "breadcrumb": breadcrumb if breadcrumb is not None else [heading] if heading else [],
        "references": references or [],
    }


def _graph(nodes: list[dict[str, object]]) -> GraphData:
    return build_graph(
        nodes,
        [],
        documents=[{"id": "doc:manual", "doc_key": "manual"}],
        part_keywords={},
        min_part_length=5,
        known_models=set(),
        fault_doc_key="faults",
        fault_header="MALFUNCTION",
        parts_doc_key="parts",
    )


def _targets(graph: GraphData) -> list[str]:
    return [edge.end_id for edge in graph.edges if edge.type == "REFERS_TO"]


def test_contents_alias_resolves_to_body_and_continuation_roots() -> None:
    nodes = [
        _node("manual:source", "step", "See paragraph 6-12.", page=8, references=["manual:6-12"]),
        _node("manual:6-12", "paragraph", "6-12. Filter Replacement 6-24", page=2),
        _node("manual:6-12:2", "procedure", "6-12. FILTER REPLACEMENT", page=28),
        _node("manual:6-12:3", "procedure", "6-12. FILTER REPLACEMENT (Cont\u2019d)", page=29),
        _node("manual:6-12:4", "paragraph", "6-12. FILTER REPLACEMENT (Cont\u2019d) 6-26", page=30),
    ]
    graph = _graph(nodes)
    assert _targets(graph) == ["passage:manual:6-12:2", "passage:manual:6-12:3"]
    references = [edge for edge in graph.edges if edge.type == "REFERS_TO"]
    assert {(edge.doc_key, edge.page_start, edge.rule) for edge in references} == {
        ("manual", 8, "references")
    }
    assert all(not edge.derived and edge.weight == 1.0 for edge in references)


def test_substantive_paragraph_bodies_are_preserved() -> None:
    heading = "2-14. ELECTRICAL TESTS"
    continuation = "2-14. ELECTRICAL TESTS (CONT\u2019D)"
    nodes = [
        _node("manual:source", "paragraph", "Refer to paragraph 2-14.", references=["manual:2-14"]),
        _node("manual:2-14", "paragraph", "2-14. Electrical tests . . . . 2-20"),
        _node(
            "manual:2-14:2",
            "paragraph",
            f"{heading} Measure the voltage across the terminals.",
            page=22,
        ),
        _node(
            "manual:2-14:3",
            "paragraph",
            f"{continuation} Record the reading before proceeding.",
            page=23,
        ),
    ]
    assert _targets(_graph(nodes)) == ["passage:manual:2-14:2", "passage:manual:2-14:3"]


def test_paragraph_resolution_rejects_contents_cross_document_and_unresolved_references() -> None:
    nodes = [
        _node(
            "manual:source",
            "step",
            "Stored references only.",
            references=["manual:4-10", "manual:4-11", "other:4-12", "manual:4-13"],
        ),
        _node("manual:4-10", "paragraph", "4-10. Pump Maintenance 4-20"),
        _node(
            "manual:4-11",
            "procedure",
            "4-11. PUMP MAINTENANCE",
            breadcrumb=["Table of Contents", "4-11. PUMP MAINTENANCE"],
        ),
        _node("other:4-12", "procedure", "4-12. PUMP MAINTENANCE"),
    ]
    assert not _targets(_graph(nodes))


def test_conflicting_body_headings_do_not_pick_an_arbitrary_occurrence() -> None:
    nodes = [
        _node("manual:source", "step", "See paragraph 7-4.", references=["manual:7-4"]),
        _node("manual:7-4", "paragraph", "7-4. Pump Maintenance 7-8"),
        _node("manual:7-4:2", "procedure", "7-4. PUMP MAINTENANCE"),
        _node("manual:7-4:3", "procedure", "7-4. VALVE MAINTENANCE"),
    ]
    assert not _targets(_graph(nodes))
    nodes[0]["references"] = ["manual:7-4:3"]
    assert _targets(_graph(nodes)) == ["passage:manual:7-4:3"]


def test_explicit_occurrences_and_other_reference_ids_keep_their_specific_targets() -> None:
    nodes = [
        _node(
            "manual:source",
            "step",
            "Explicit stored reference IDs.",
            references=[
                "manual:8-9:3",
                "manual:table:8-1",
                "other:fig:2-4",
                "missing:table:1-1",
                "manual:source",
            ],
        ),
        _node("manual:8-9", "paragraph", "8-9. Filter Maintenance 8-18"),
        _node("manual:8-9:2", "procedure", "8-9. FILTER MAINTENANCE"),
        _node("manual:8-9:3", "procedure", "8-9. FILTER MAINTENANCE (Cont'd)"),
        _node("manual:table:8-1", "table", "Permissible readings"),
        _node("other:fig:2-4", "figure", "Wiring layout"),
    ]
    assert _targets(_graph(nodes)) == [
        "passage:manual:8-9:3",
        "passage:manual:table:8-1",
        "passage:other:fig:2-4",
    ]


def test_reference_resolution_is_deterministic_without_discovering_new_references() -> None:
    nodes = [
        _node(
            "manual:source",
            "step",
            "See paragraph 3-7 or paragraph 3-8.",
            references=["manual:3-7", "manual:3-7", "manual:3-7:3"],
        ),
        _node("manual:3-7", "paragraph", "3-7. Hose Maintenance 3-14"),
        _node("manual:3-7:2", "procedure", "3-7. HOSE MAINTENANCE"),
        _node("manual:3-7:3", "procedure", "3-7. HOSE MAINTENANCE (Cont\u2019d)"),
        _node("manual:3-8", "procedure", "3-8. PIPE MAINTENANCE"),
    ]
    first = _graph(nodes)
    nodes[0]["references"] = ["manual:3-7:3", "manual:3-7", "manual:3-7"]
    second = _graph(list(reversed(nodes)))
    assert first.fingerprint() == second.fingerprint()
    assert _targets(first) == ["passage:manual:3-7:2", "passage:manual:3-7:3"]


def test_stored_cooling_reference_reaches_drain_instruction_in_three_edges() -> None:
    source = "tm280_20_2:3-61:2:step-c:2"
    alias = "tm280_20_2:3-60"
    body = "tm280_20_2:3-60:2"
    continuation = "tm280_20_2:3-60:3"
    subsection = "tm280_20_2:3-60:2:step-b:3:2"
    instruction = "tm280_20_2:3-60:2:step-b:3:2:step-2:2"
    path = Path(__file__).resolve().parents[1] / "data/nodes/tm280_20_2.jsonl"
    stored = {row["node_id"]: row for row in map(json.loads, path.read_text().splitlines())}
    assert alias in stored[source]["references"]
    assert stored[alias]["type"] == "paragraph"
    assert stored[alias]["text"].endswith("3-108")
    assert "Open draincock (4) and allow system to drain." in stored[instruction]["text"]

    selected = [stored[key] for key in (source, alias, body, continuation, subsection, instruction)]
    graph = _graph(selected)
    references = [edge for edge in graph.edges if edge.type == "REFERS_TO"]
    assert {edge.end_id for edge in references} == {
        f"passage:{body}",
        f"passage:{continuation}",
    }
    assert all(
        edge.doc_key == stored[source]["doc_key"]
        and edge.page_start == stored[source]["page_start"]
        for edge in references
    )
    # The stored REFERS_TO followed by two reversed PARENT edges reaches the
    # numbered instruction, without a shortcut that misreports its hop count.
    forward = {(edge.start_id, edge.end_id) for edge in references}
    reverse_parent = {(edge.end_id, edge.start_id) for edge in graph.edges if edge.type == "PARENT"}
    assert (f"passage:{source}", f"passage:{body}") in forward
    assert (f"passage:{body}", f"passage:{subsection}") in reverse_parent
    assert (f"passage:{subsection}", f"passage:{instruction}") in reverse_parent
    assert (f"passage:{body}", f"passage:{instruction}") not in reverse_parent
