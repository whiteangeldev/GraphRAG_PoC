# Handover

Status: agenda prepared; attendance, recordings and final delivery are pending. No
completed session is recorded here. See the [current M4 status](m4_report.md).

Two sessions, two hours each, with Sodick's developers. Record both. Write the answers under each question after the session. The agenda below is what the repository can show before the meeting.

## Session 1 — Build and verify

1. Install the package and start Neo4j with Docker Compose.
2. Build `tests/fixtures/m4` with `build_graph` and read the report: counts, orphans, derived edges.
3. Open `/health` and `/graph/stats`.
4. Walk the fixture: the crank code links, the starter part comes back, the next step and the hot-oil caution come back.
5. Rebuild the public corpus with `python -m graphrag_poc.graph` only if the audience wants the full load. That command replaces the `neo4j` database.
6. Read the newly rebuilt `docs/graph_build_report.md` and its derived-edge sample. The saved pre-feedback report is historical until replaced by a verified rebuild.

Questions from the session:

| Question | Answer |
|---|---|
|  |  |

## Session 2 — Call the library from another retriever

1. `link_entities`, `route`, `traverse`, and `fuse` on a question Sodick brings as text, using the public corpus or the fixture.
2. Show an explicit paragraph or part-number path and its source passages. Bounded routes return no keyword relation frame. Explain the limits of surface mentions and synthetic cases. Use a client-approved example.
3. Show graph weight 1.0, the bounded route's three-edge limit, and the legacy two-hop default. Explain the revised M3 measurement only after its results are available.
4. Roll back a Bolt build id with `clear_build`.
5. Walk `docs/integration.md`, `docs/schema_reference.md` and `docs/schema_mapping.md`. Confirm which labels Sodick will send.

Questions from the session:

| Question | Answer |
|---|---|
|  |  |

The recordings belong next to this file when they exist. The written answers stay in the tables above.

## Delivery record

| Item | Evidence |
|---|---|
| Sodick GitLab project URL and delivered commit/tag | Pending |
| Requirements version and accepted schema mapping | Pending |
| Revised benchmark approval and evaluation reports | Pending |
| Clean-install/service verification | Pending |
| Current demonstration recording | Pending |
| Session 1 date, attendees, recording and open actions | Pending |
| Session 2 date, attendees, recording and open actions | Pending |

Preserve repository history and omit credentials from delivery. Record actual dates,
attendees and evidence after completion; scheduling a session does not record attendance.
