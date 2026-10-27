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

Named Bolt builds share global uniqueness constraints. Their document keys, passage IDs,
malfunction IDs, part numbers, model names, and case IDs must be disjoint from every other
build, including the public corpus. The writer rejects a conflicting key before deleting
or replacing existing data. Use a separate Neo4j database for overlapping snapshots;
changing only the build name does not create an isolated copy of shared keys.

The name `corpus` is reserved for the public import. The library cannot replace or clear
it. Nodes without a `build` property are treated as corpus nodes when checking collisions.
`POST /graph/build` returns HTTP 400 for invalid or conflicting builds and leaves the
service's active build unchanged.

## Verify

```bash
curl http://127.0.0.1:8088/health
curl "http://127.0.0.1:8088/graph/stats?build=corpus"
```

`/health` returns `ok` and the active build id; it does not query Neo4j or model servers.
`/graph/stats` queries the graph and returns counts, the orphan count, and the share of
derived edges. An orphan is a node with no relationship. Verify those values after the
corrected-data rebuild; historical graph counts do not establish the current load.

Start the service with `make service`. It listens on port 8088.

## Rebuild

Run `python -m graphrag_poc.graph` again for the public corpus. This full import replaces
the entire database, including any named builds; preserve the required backup first.

For a named Bolt build, call `build_graph` again with the same id. After checking key
ownership, the writer deletes and replaces that build in one transaction. A collision,
missing edge endpoint, or write failure leaves the previous build intact. Other builds
and untagged corpus nodes retain their data. Schema constraints are applied separately;
a failed replacement may still have created an absent constraint or index.

## Roll back

A named Bolt build is removed with the following call. This deletes that build; it does
not restore an earlier version. To restore one, call `build_graph` with the archived
source files and the same build id.

```python
from graphrag_poc.graph.client import make_driver
from graphrag_poc.library import clear_build

driver = make_driver()
try:
    clear_build(driver, "customer-1")
finally:
    driver.close()
```

For the public corpus, preserve a complete earlier CSV folder outside
`data/graph/import`, which the graph command regenerates. Import that preserved folder
directly from the project directory:

```python
from pathlib import Path
from graphrag_poc.graph.load import load_csv

load_csv(Path("backups/previous-graph-import"))
```

This stops Neo4j, replaces its entire database from the saved CSV, restarts it, and
reapplies constraints. Running `python -m graphrag_poc.graph` instead regenerates CSV from
the current inputs and does not restore the backup. Alternatively, restore the
`neo4j_data` Docker volume from a copy taken before the load.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

GitHub Actions installs the package and runs the same tests against Neo4j 5.26. The workflow also builds the service image.
