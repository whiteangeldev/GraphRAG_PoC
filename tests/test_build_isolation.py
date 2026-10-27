"""Named graph builds cannot steal globally unique keys or lose a failed replacement."""

import copy
import importlib
import json
from collections.abc import Iterator
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from neo4j import Driver

from graphrag_poc.graph.build import Edge, GraphData
from graphrag_poc.graph.client import make_driver
from graphrag_poc.library import store

KEYS = [
    ("documents", "Document", "doc_key"),
    ("passages", "Passage", "node_id"),
    ("malfunctions", "Malfunction", "node_id"),
    ("parts", "Part", "part_number"),
    ("models", "Model", "name"),
    ("cases", "Case", "case_id"),
]


def test_csv_export_does_not_switch_the_active_database_build(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = importlib.import_module("graphrag_poc.service.app")
    from graphrag_poc.library.models import BuildReport

    monkeypatch.setattr(service.app.state, "build", "existing-build")
    monkeypatch.setattr(
        service,
        "build_graph",
        lambda *args: BuildReport(
            build="csv-export",
            output="/tmp/export",
            counts={},
            orphans=0,
            derived=0,
        ),
    )
    with TestClient(service.app) as client:
        response = client.post(
            "/graph/build",
            json={
                "node_files": ["fixture.jsonl"],
                "rules": "rules.json",
                "build": "csv-export",
                "out": "/tmp/export",
            },
        )
        assert response.status_code == 200
        assert client.get("/health").json()["build"] == "existing-build"


def _graph(prefix: str) -> GraphData:
    return GraphData(
        documents=[
            {"doc_key": prefix, "title": "Fixture", "lang": "en", "doc_type": "tm", "edition": "1"}
        ],
        passages=[
            {
                "node_id": f"{prefix}:passage",
                "text": "Original fixture passage",
                "type": "step",
                "page_start": 1,
                "page_end": 1,
                "lang": "en",
                "doc_key": prefix,
                "breadcrumb": [],
            }
        ],
        malfunctions=[
            {
                "node_id": f"{prefix}:fault",
                "code": "Fixture fault",
                "page_start": 1,
                "doc_key": prefix,
            }
        ],
        parts=[
            {
                "part_number": f"{prefix}-PART",
                "description": "Fixture part",
                "nsn": "",
                "node_id": f"{prefix}:passage",
                "doc_key": prefix,
                "page_start": "1",
            }
        ],
        models=[{"name": f"{prefix}-MODEL", "series": "Fixture"}],
        cases=[
            {
                "case_id": f"{prefix}-CASE",
                "date": "2026-01-01",
                "model": f"{prefix}-MODEL",
                "symptom": "Fixture symptom",
                "cause": "Fixture cause",
                "action": "Fixture action",
                "frequency": 1,
            }
        ],
        edges=[
            Edge("IN_DOCUMENT", f"passage:{prefix}:passage", f"doc:{prefix}", "fixture", prefix, 1)
        ],
    )


@pytest.mark.parametrize(("group", "label", "prop"), KEYS)
def test_conflict_is_rejected_before_any_mutation(group: str, label: str, prop: str) -> None:
    driver = MagicMock()
    session = driver.session.return_value.__enter__.return_value
    transaction = MagicMock()

    def run(query: str, **parameters: object) -> MagicMock:
        result = MagicMock()
        result.single.return_value = (
            {"key": "existing", "owner": "other-build"} if f"n:{label} " in query else None
        )
        return result

    transaction.run.side_effect = run
    session.execute_read.side_effect = lambda callback, *args: callback(transaction, *args)
    graph = GraphData()
    setattr(graph, group, [{prop: "existing"}])

    with pytest.raises(ValueError, match=rf"{label}\.{prop}.*other-build"):
        store.write_graph(driver, graph, "replacement-build")

    session.execute_write.assert_not_called()
    session.run.assert_not_called()
    assert all(
        "MATCH" in call.args[0] and "DELETE" not in call.args[0]
        for call in transaction.run.call_args_list
    )


@pytest.mark.parametrize("build", ["", " ", " corpus ", "corpus"])
def test_invalid_or_reserved_build_never_opens_database(build: str) -> None:
    driver = MagicMock()
    with pytest.raises(ValueError):
        store.write_graph(driver, GraphData(), build)
    with pytest.raises(ValueError):
        store.clear_build(driver, build)
    driver.session.assert_not_called()


@pytest.mark.parametrize(
    "message",
    [
        "Part.part_number 'shared-part' belongs to build 'other-build'; "
        "builds require globally disjoint keys",
        "corpus is reserved; the library cannot replace or clear it",
    ],
)
def test_service_rejected_build_returns_400_without_changing_active_build(
    monkeypatch: pytest.MonkeyPatch, message: str
) -> None:
    service = importlib.import_module("graphrag_poc.service.app")
    app = service.app

    def reject(*args: object, **kwargs: object) -> None:
        raise ValueError(message)

    monkeypatch.setattr(service, "build_graph", reject)
    monkeypatch.setattr(app.state, "build", "existing-active-build")
    with TestClient(app) as client:
        response = client.post(
            "/graph/build",
            json={
                "node_files": ["unused-nodes.jsonl"],
                "rules": "unused-rules.json",
                "build": "requested-build",
            },
        )
        assert response.status_code == 400
        assert response.json() == {"detail": message}
        assert app.state.build == "existing-active-build"
        assert client.get("/health").json()["build"] == "existing-active-build"


@pytest.fixture
def isolated_database() -> Iterator[tuple[Driver, str, str]]:
    driver = make_driver()
    try:
        driver.verify_connectivity()
    except Exception as exc:
        driver.close()
        pytest.skip(f"Neo4j unavailable for isolated build test: {type(exc).__name__}")
    prefix = f"isolation-{uuid4().hex}"
    first, second = f"{prefix}-a", f"{prefix}-b"
    try:
        yield driver, first, second
    finally:
        store.clear_build(driver, first)
        store.clear_build(driver, second)
        # This exact, unique key is used only by the untagged-node regression.
        with driver.session() as session:
            session.run(
                "MATCH (n:Passage {node_id: $key}) DETACH DELETE n",
                key=f"{prefix}-untagged",
            ).consume()
        driver.close()


def _snapshot(driver: Driver, builds: list[str]) -> str:
    with driver.session() as session:
        nodes = [
            dict(record)
            for record in session.run(
                "MATCH (n) WHERE n.build IN $builds "
                "RETURN labels(n) AS labels, properties(n) AS props",
                builds=builds,
            )
        ]
        edges = [
            dict(record)
            for record in session.run(
                "MATCH (a)-[r]->(b) WHERE r.build IN $builds "
                "RETURN properties(a) AS start, properties(b) AS end, "
                "type(r) AS type, properties(r) AS props",
                builds=builds,
            )
        ]
    return json.dumps(
        {
            "nodes": sorted(json.dumps(row, sort_keys=True) for row in nodes),
            "edges": sorted(json.dumps(row, sort_keys=True) for row in edges),
        },
        sort_keys=True,
    )


@pytest.mark.parametrize(("group", "label", "prop"), KEYS)
def test_live_collision_preserves_owner_and_replacement_target(
    isolated_database: tuple[Driver, str, str], group: str, label: str, prop: str
) -> None:
    driver, first, second = isolated_database
    source, target = _graph(first), _graph(second)
    store.write_graph(driver, source, first)
    store.write_graph(driver, target, second)
    before = _snapshot(driver, [first, second])
    incoming = copy.deepcopy(target)
    getattr(incoming, group)[0][prop] = getattr(source, group)[0][prop]

    with pytest.raises(ValueError, match=rf"{label}\.{prop}.*belongs to build"):
        store.write_graph(driver, incoming, second)

    assert _snapshot(driver, [first, second]) == before


def test_live_untagged_corpus_collision_preserves_both_graphs(
    isolated_database: tuple[Driver, str, str],
) -> None:
    driver, first, second = isolated_database
    store.write_graph(driver, _graph(first), first)
    store.write_graph(driver, _graph(second), second)
    key = f"{first.removesuffix('-a')}-untagged"
    with driver.session() as session:
        session.run(
            "CREATE (:Passage {node_id: $key, text: 'untagged corpus fixture'})", key=key
        ).consume()
    before = _snapshot(driver, [first, second])
    incoming = _graph(second)
    incoming.passages[0]["node_id"] = key

    with pytest.raises(ValueError, match="belongs to build 'corpus'"):
        store.write_graph(driver, incoming, second)

    assert _snapshot(driver, [first, second]) == before
    with driver.session() as session:
        row = session.run(
            "MATCH (n:Passage {node_id: $key}) RETURN properties(n) AS props", key=key
        ).single(strict=True)
        assert row["props"] == {"node_id": key, "text": "untagged corpus fixture"}


def test_live_same_build_replacement_succeeds_and_preserves_other_build(
    isolated_database: tuple[Driver, str, str],
) -> None:
    driver, first, second = isolated_database
    store.write_graph(driver, _graph(first), first)
    store.write_graph(driver, _graph(second), second)
    other_before = _snapshot(driver, [first])
    replacement = _graph(second)
    replacement.passages[0]["text"] = "Replacement passage"
    replacement.parts = []
    store.write_graph(driver, replacement, second)

    assert _snapshot(driver, [first]) == other_before
    with driver.session() as session:
        row = session.run(
            "MATCH (n:Passage {node_id: $key}) RETURN n.text AS text", key=f"{second}:passage"
        ).single(strict=True)
        assert row["text"] == "Replacement passage"
        assert (
            session.run(
                "MATCH (n:Part) WHERE n.build = $build RETURN count(n) AS count", build=second
            ).single(strict=True)["count"]
            == 0
        )


def test_live_failure_after_clear_rolls_back_entire_replacement(
    isolated_database: tuple[Driver, str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    driver, first, second = isolated_database
    store.write_graph(driver, _graph(first), first)
    store.write_graph(driver, _graph(second), second)
    before = _snapshot(driver, [first, second])

    def fail(*args: object) -> None:
        raise RuntimeError("injected late write failure")

    monkeypatch.setattr(store, "_write_cases", fail)
    with pytest.raises(RuntimeError, match="injected late write failure"):
        store.write_graph(driver, _graph(second), second)

    assert _snapshot(driver, [first, second]) == before


@pytest.mark.parametrize("foreign", [True, False])
def test_live_edges_cannot_attach_to_foreign_or_missing_endpoints(
    isolated_database: tuple[Driver, str, str], foreign: bool
) -> None:
    driver, first, second = isolated_database
    store.write_graph(driver, _graph(first), first)
    store.write_graph(driver, _graph(second), second)
    before = _snapshot(driver, [first, second])
    incoming = _graph(second)
    endpoint = f"{first}:passage" if foreign else f"{second}:missing"
    incoming.edges.append(
        Edge("NEXT", f"passage:{second}:passage", f"passage:{endpoint}", "fixture", second, 1)
    )

    with pytest.raises(ValueError, match="belongs to build" if foreign else "endpoint is missing"):
        store.write_graph(driver, incoming, second)

    assert _snapshot(driver, [first, second]) == before
