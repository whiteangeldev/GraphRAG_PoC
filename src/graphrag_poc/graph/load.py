"""Load neo4j-admin CSV into a fresh Community database, then add constraints."""

import subprocess
import time
from pathlib import Path
from typing import TypedDict

from graphrag_poc.graph.client import make_driver
from graphrag_poc.graph.export import node_arguments
from graphrag_poc.ingest.catalog import ROOT

_CONSTRAINTS = (
    "CREATE CONSTRAINT document_doc_key IF NOT EXISTS FOR (n:Document) REQUIRE n.doc_key IS UNIQUE",
    "CREATE CONSTRAINT passage_node_id IF NOT EXISTS FOR (n:Passage) REQUIRE n.node_id IS UNIQUE",
    "CREATE CONSTRAINT malfunction_node_id IF NOT EXISTS "
    "FOR (n:Malfunction) REQUIRE n.node_id IS UNIQUE",
    "CREATE CONSTRAINT part_part_number IF NOT EXISTS FOR (n:Part) REQUIRE n.part_number IS UNIQUE",
    "CREATE CONSTRAINT model_name IF NOT EXISTS FOR (n:Model) REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT case_case_id IF NOT EXISTS FOR (n:Case) REQUIRE n.case_id IS UNIQUE",
    "CREATE INDEX passage_page_start IF NOT EXISTS FOR (n:Passage) ON (n.page_start)",
    "CREATE INDEX malfunction_code IF NOT EXISTS FOR (n:Malfunction) ON (n.code)",
)


class SpotCheck(TypedDict):
    next: list[str]
    cautions: list[str]
    candidate_code: str
    candidate_part: str
    candidate_keyword: str
    edges_without_provenance: int


CHARGING_MALFUNCTION = "tm280_10:table:3-1:2:r4"


OIL_COOLER_STEP = "tm280_20_2:3-8:step-a:3:2:step-1:2"
OIL_COOLER_NEXT = "tm280_20_2:3-8:step-a:3:2:step-2:2"
OIL_COOLER_CAUTIONS = (
    "tm280_20_2:3-8:step-a:3:2:caution",
    "tm280_20_2:3-8:step-a:3:2:caution:2",
)


def load_csv(import_dir: Path) -> None:
    """Stop Neo4j, replace the database, start it, and add constraints."""

    _compose("stop", "neo4j")
    completed = subprocess.run(
        _import_command(import_dir),
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    started = subprocess.run(
        ["docker", "compose", "up", "-d", "--wait", "neo4j"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        detail = f"{completed.stdout}\n{completed.stderr}".strip()
        raise RuntimeError(detail or "neo4j-admin import failed")
    if started.returncode != 0:
        detail = f"{started.stdout}\n{started.stderr}".strip()
        raise RuntimeError(detail or "Neo4j did not start after import")
    _wait_until_ready()
    apply_constraints()


def apply_constraints() -> None:
    driver = make_driver()
    try:
        with driver.session() as session:
            for statement in _CONSTRAINTS:
                session.run(statement).consume()
    finally:
        driver.close()


def spot_check() -> SpotCheck:
    """The oil-cooler step, its next step and warnings, and one candidate part."""

    driver = make_driver()
    try:
        with driver.session() as session:
            nxt = [
                str(item)
                for item in session.run(
                    "MATCH (s:Passage {node_id: $step})-[:NEXT]->(n:Passage) "
                    "RETURN n.node_id AS id ORDER BY id",
                    step=OIL_COOLER_STEP,
                ).value("id")
            ]
            cautions = [
                str(item)
                for item in session.run(
                    "MATCH (s:Passage {node_id: $step})-[:BOUND_CAUTION]->(c:Passage) "
                    "RETURN c.node_id AS id ORDER BY id",
                    step=OIL_COOLER_STEP,
                ).value("id")
            ]
            part = session.run(
                "MATCH (m:Malfunction {node_id: $node_id})-[r:CANDIDATE_PART]->(p:Part) "
                "WHERE r.keyword IN ['ALTERNATOR', 'GENERATOR'] "
                "RETURN m.code AS code, p.part_number AS part, r.keyword AS keyword LIMIT 1",
                node_id=CHARGING_MALFUNCTION,
            ).single()
            missing = session.run(
                "MATCH ()-[r]->() "
                "WHERE (r.case_id IS NOT NULL AND r.doc_key IS NOT NULL) "
                "OR (r.case_id IS NULL AND (r.doc_key IS NULL OR r.page_start IS NULL)) "
                "RETURN count(r) AS n"
            ).single()
    finally:
        driver.close()
    if part is None or missing is None:
        raise RuntimeError("the imported graph is missing the spot check")
    return {
        "next": nxt,
        "cautions": cautions,
        "candidate_code": str(part["code"]),
        "candidate_part": str(part["part"]),
        "candidate_keyword": str(part["keyword"]),
        "edges_without_provenance": _as_int(missing["n"]),
    }


def database_counts() -> dict[str, int]:
    """Label and relationship counts in the imported database."""

    driver = make_driver()
    try:
        with driver.session() as session:
            counts: dict[str, int] = {}
            nodes = session.run("MATCH (n) UNWIND labels(n) AS label RETURN label, count(n) AS c")
            for record in nodes:
                counts[str(record["label"])] = _as_int(record["c"])
            edges = session.run("MATCH ()-[r]->() RETURN type(r) AS label, count(r) AS c")
            for record in edges:
                counts[str(record["label"])] = _as_int(record["c"])
    finally:
        driver.close()
    return dict(sorted(counts.items()))


def _import_command(import_dir: Path) -> list[str]:
    return [
        "docker",
        "compose",
        "run",
        "--rm",
        "--no-deps",
        "-T",
        "-e",
        "HEAP_SIZE=1G",
        "-v",
        f"{import_dir.resolve()}:/import:ro",
        "neo4j",
        "neo4j-admin",
        "database",
        "import",
        "full",
        "neo4j",
        "--overwrite-destination=true",
        "--id-type=string",
        "--array-delimiter=|",
        "--ignore-empty-strings=true",
        "--bad-tolerance=0",
        "--max-off-heap-memory=1G",
        "--report-file=/tmp/import.report",
        *node_arguments(),
    ]


def _as_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RuntimeError(f"unexpected count {value!r}")
    return value


def _compose(*args: str) -> None:
    subprocess.run(["docker", "compose", *args], cwd=ROOT, check=True)


def _wait_until_ready(timeout: float = 120) -> None:
    deadline = time.monotonic() + timeout
    last = "Neo4j did not accept a connection"
    while time.monotonic() < deadline:
        driver = make_driver()
        try:
            driver.verify_connectivity()
            return
        except Exception as exc:
            last = str(exc)
            time.sleep(2)
        finally:
            driver.close()
    raise RuntimeError(last)
