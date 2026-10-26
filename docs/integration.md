# Integration

Sodick produces Appendix A.1 node files in its own pipeline and calls this library. The developer does not see that data. Field names in Appendix A stay fixed. Additional fields are allowed.

## Install

```bash
pip install -e ".[dev]"
```

The install name is `graphrag-poc`. Python is 3.12. Neo4j Community 5.26 is the graph store. The demonstration also uses Qdrant. A retriever Sodick already runs does not need Qdrant.

## Feed node files

`build_graph` reads JSON Lines. One file per document is the expected layout. Several files are accepted. The case file may be omitted. The rules file names the fault header, the parts document, the keyword map, and the model list.

```python
from pathlib import Path
from graphrag_poc.library import build_graph

build_graph(
    [Path("nodes/operator.jsonl"), Path("nodes/parts.jsonl")],
    Path("cases.jsonl"),
    Path("rules.json"),
    "bolt://neo4j:7687",
    "plant-2026",
)
```

Use a new build id for each load you may want to delete later. The public corpus id is `corpus`.

## Call traversal from another retriever

```python
from graphrag_poc.library import Entity, fuse, link_entities, route, traverse

entities = [Entity(text=question, type="")]
seeds = link_entities(entities, "plant-2026")
decision = route(question_type, seeds)
if decision.enabled:
    result = traverse(seeds, question_type, decision.hops, 200, "plant-2026", question=question)
    graph_list = result.candidates
else:
    graph_list = []
fused = fuse(
    {"dense": dense_candidates, "sparse": sparse_candidates, "graph": graph_list},
    {"dense": 1.0, "sparse": 1.0, "graph": 1.0},
)
```

`Candidate.passage_node_id` is the node id to join back to the caller's passage store. `channels` lists every list that found the passage. `via` lists the edge types on the graph path. The default graph weight is 1.0 and the default hop depth is 2. Those are the values measured in `docs/m3_report.md`.

The router turns the graph on for `relational`, `multi_hop`, `troubleshooting`, and `applicability`. A lookup stays off unless a seed is a malfunction, a part, or a case. A lookup that only names a model stays off.

## Service

Build, link, traverse, and stats are also HTTP on port 8088. `route` and `fuse` stay in the library.

| Method | Path | Body |
|---|---|---|
| GET | `/health` |  |
| POST | `/graph/build` | `node_files`, `case_file`, `rules`, `build` |
| POST | `/graph/link` | `entities`, `build` |
| POST | `/graph/traverse` | `seeds`, `question_type`, `hops`, `cap`, `build` |
| GET | `/graph/stats?build=` |  |

`POST /graph/build` writes through Bolt using `NEO4J_URI`. Set `out` to a directory path when the caller wants CSV instead.

## Tune

Change the `graph` weight in `fuse` and the `hops` argument to `traverse`. Record the pair you keep. Do not raise the evidence cutoff above 10. That would change hit@10. Leave the reranker off unless a later measurement says otherwise.

## Five fixture questions

`tests/fixtures/m4` is a six-node graph. `tests/test_library.py` builds it and checks five outcomes: the crank code links, an unknown code does not, the relational walk returns the starter part, the procedure walk returns the next step and the hot-oil caution, and the lookup answer quotes the starter check. Copy that fixture shape when trying a new node file before loading a full manual.
