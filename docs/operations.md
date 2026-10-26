# Operations

## Start the stores

```bash
docker compose up -d --wait qdrant neo4j
```

Neo4j Bolt is `bolt://localhost:7687`. The user is `neo4j` and the password is `graphrag-poc` unless `NEO4J_PASSWORD` is set. Qdrant HTTP is `http://localhost:6333`.

## Build the public corpus

```bash
python -m graphrag_poc.graph
```

That command reads `data/nodes` and `data/cases`, writes `data/graph/import`, loads a fresh `neo4j` database with `neo4j-admin`, and writes `docs/graph_build_report.md`. Two builds of the same files must match before the load. This replaces the `neo4j` database. It is the full rebuild.

## Build from another node-file set

From Python, with the files on disk:

```python
from pathlib import Path
from graphrag_poc.library import build_graph

report = build_graph(
    [Path("nodes/manual.jsonl")],
    Path("cases.jsonl"),
    Path("rules.json"),
    "bolt://localhost:7687",
    "customer-1",
)
```

`out` may instead be a folder. The folder receives the neo4j-admin CSV and nothing is written to Bolt. The rules file has the same fields as `data/cases/rules.json`: fault header, parts document, part keywords, and the model list.

## Verify

```bash
curl http://127.0.0.1:8088/health
curl "http://127.0.0.1:8088/graph/stats?build=corpus"
```

`/health` returns `ok` and the active build id. `/graph/stats` returns counts, the orphan count, and the share of derived edges. An orphan is a node with no relationship. The corpus build has none.

Start the service with `make service`. It listens on port 8088.

## Rebuild

Run `python -m graphrag_poc.graph` again for the public corpus. For a Bolt build id, call `build_graph` again with the same id. The writer deletes that id first, then writes the new nodes. `corpus` nodes, which have no `build` property, are left in place.

## Roll back

A Bolt build id is removed with:

```python
from graphrag_poc.graph.client import make_driver
from graphrag_poc.library import clear_build

driver = make_driver()
clear_build(driver, "customer-1")
driver.close()
```

The public corpus is rolled back by importing an earlier CSV folder with the same `python -m graphrag_poc.graph` path, or by restoring the `neo4j_data` Docker volume from a copy taken before the load.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

GitHub Actions installs the package and runs the same tests against Neo4j 5.26. The workflow also builds the service image.
