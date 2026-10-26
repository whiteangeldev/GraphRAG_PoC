# Handover

Two sessions, two hours each, with Sodick's developers. Record both. Write the answers under each question after the session. The agenda below is what the repository can show before the meeting.

## Session 1 — Build and verify

1. Install the package and start Neo4j with Docker Compose.
2. Build `tests/fixtures/m4` with `build_graph` and read the report: counts, orphans, derived edges.
3. Open `/health` and `/graph/stats`.
4. Walk the fixture: the crank code links, the starter part comes back, the next step and the hot-oil caution come back.
5. Rebuild the public corpus with `python -m graphrag_poc.graph` only if the audience wants the full load. That command replaces the `neo4j` database.
6. Read `docs/graph_build_report.md` and the sample of 100 derived edges.

Questions from the session:

| Question | Answer |
|---|---|
|  |  |

## Session 2 — Call the library from another retriever

1. `link_entities`, `route`, `traverse`, and `fuse` on a question Sodick brings as text, using the public corpus or the fixture.
2. Show the relation frame for the charging fault: code, steps, part `12339317`, and the case ids.
3. Change the graph weight and the hop depth and say what the M3 measurement used (weight 1.0, depth 2).
4. Roll back a Bolt build id with `clear_build`.
5. Walk `docs/integration.md` and `docs/schema_reference.md`. Confirm which labels Sodick will send.

Questions from the session:

| Question | Answer |
|---|---|
|  |  |

The recordings belong next to this file when they exist. The written answers stay in the tables above.
