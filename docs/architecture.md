# Architecture

The package has two layers. The demonstration chatbot answers a question. The library builds a graph and returns passages another retriever can fuse. Sodick calls the library. The chatbot is only the proof.

## Flow

1. Node files (Appendix A.1) and an optional case file (Appendix A.2) enter `build_graph`.
2. Deterministic rules create document, passage, malfunction, part, model, and case nodes, and the edges between them. A passage that writes a model name or a part number also gets a derived `MENTIONS` edge.
3. The graph is either a folder of neo4j-admin CSV or a Bolt write into Neo4j Community.
4. `link_entities` matches codes, part numbers, and model names to nodes.
5. `route` decides whether the graph list is used.
6. `traverse` walks one or two hops and returns passage ids, scores, and paths.
7. `fuse` merges that list with the caller's dense and sparse lists by reciprocal rank fusion.

The demonstration page does the same steps for the public corpus and shows the relation frame: code, cause, remedy, part, and cases.

## What is stored

Neo4j holds the graph. Qdrant holds the dense and sparse passage vectors for the demonstration retriever. The library does not read Qdrant. A caller that already has a retriever passes its own ranked lists into `fuse`.

The live labels are the ones in `docs/schema_reference.md`. They are the schema M3 loaded. Appendix A.3's example names (`ErrorCode`, `NEXT_STEP`) are the generic sketch in the requirements. This repository did not rename the working graph.

## Build id

Each Bolt write stamps `build` on the nodes and relationships it creates. The corpus loaded by `python -m graphrag_poc.graph` has no `build` property and is treated as `corpus`. A later fixture or customer build uses its own id and does not delete `corpus`.

## What the walk returns

Traversal returns passages, not parts or cases. A malfunction seed walks `CANDIDATE_PART` and `LISTS` to the parts-list row, and `STATES` back to the malfunction row. A step seed walks `NEXT` and `BOUND_CAUTION`. The relation frame carries the case ids and the part description beside those passages.
