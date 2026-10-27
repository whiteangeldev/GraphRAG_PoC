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

The implemented labels are in [the schema reference](schema_reference.md). The draft
[requirements mapping](schema_mapping.md) explains local equivalents for `ErrorCode`
and `NEXT_STEP`; final compatibility needs the original requirements and client review.
The revised M3 measurements remain pending.

## Build id

Each Bolt write stamps `build` on the nodes and relationships it creates. The corpus loaded by `python -m graphrag_poc.graph` has no `build` property and is treated as `corpus`. A later fixture or customer build uses its own id and does not delete `corpus`.

## What the walk returns

Traversal returns passages, not parts or cases. The bounded route starts from retrieved
passages and follows explicit paragraph references into procedure instructions, or
literal part-number mentions through `Part` and `LISTS` to catalogue rows. It omits the
keyword part frame. A step seed can walk `NEXT` and `BOUND_CAUTION`. Legacy routes retain
their unverified keyword candidates. [Traversal preparation](traversal_alignment.md)
describes the new build and three-edge limit; applying it requires a graph rebuild.

Keyword candidates and synthetic case links are unverified hints. Source provenance
does not establish a complete repair chain. The model answer path receives the frame
as context and must produce its own supported answer and citations; no rule appends
part numbers or fallback citations to that output.
