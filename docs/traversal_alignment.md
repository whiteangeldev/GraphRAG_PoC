# Bounded manual traversal preparation

27 October 2026. This implementation uses manual structure and exact part-number
mentions. It does not import review/gold files into graph construction or retrieval,
activate the new benchmark, or run model inference.

## Reference build

Stored paragraph references resolve within their own document to actual body headings
and compatible continuation occurrences. Contents-page aliases, conflicting titles and
unresolved paragraphs do not become instruction links. Explicit occurrence suffixes
remain specific. Edges retain the source document/page and deterministic rule provenance.
The source node files and the client's question/evidence records are unchanged.

## Traversal and retrieval

Relational/multi-hop questions seed the graph with the first ten baseline passages and
exact entities from the question. The route follows `REFERS_TO` and reverse `PARENT`
links to referenced instructions, or exact `MENTIONS`/`LISTS` paths to catalogue rows.
It returns all matching catalogue occurrences within the cap rather than assuming the
canonical row proves fit. An explicit part seed can also follow `LISTS` directly.

The bounded route uses at most three actual edges: one paragraph reference plus up to
two structural parent links, or two edges for a part mention and catalogue listing.
Returned paths record every edge and its provenance, including the derived weight of
surface mentions. The passage cap stays 200 and generator evidence stays at ten. Other
routes retain their two-hop default. HTTP callers should specify `hops: 3` for bounded
manual relationships; the library router supplies that value.

Explicit references rank ahead of inferred part mentions. Within referenced content,
question-term overlap orders instructions before structural distance; this uses no
model calls, gold IDs or case-specific rules. Duplicate paths do not consume the
unique-passage cap. Reference targets are ordered by the same word overlap inside
Neo4j before that cap is applied, so early headings cannot consume the query limit
before a more relevant instruction is considered. Public library and HTTP paths
include the per-edge provenance records. All traversal routes and legacy relation
frames constrain source nodes, intermediate nodes and relationships to the selected
build.

Keyword `CANDIDATE_PART` traversal and its relation frame are not used by the bounded
route. Legacy lookup/troubleshooting demonstrations can still expose those unverified
candidates. Exact source references are not proof of semantic correctness: the excluded
HVAC-to-3-28 link remains excluded from gold. No case-specific answer selection or
review-list IDs are used by production traversal.

The graph settings and explicit-manual retrieval protocol are included in evaluation
fingerprints; fresh baseline/graph measurements are required. Supplied-evidence model
smoke checks do not measure this retrieval change.

## Offline benchmark preparation

```bash
make bounded-plan
```

This writes only `data/eval/staging/plan.json`. It plans replacement of the 50 legacy
keyword targets with the 50 prepared bounded targets while preserving the 105 original
non-target controls. Those controls supply lookup latency and per-type regression
samples. Target gains remain reported on the frozen 50, separate from the controls.

The plan reports pending reviews, source/schema validation, target and combined
fingerprints, and historical baseline mismatch. Planning succeeds without granting
approval or activating the set. Current readiness remains false because 25 targets and
the final freeze await the client. Existing acceptance checks still block scoring.
The contract lists 50 target IDs but its full-run question digest must cover the same
ordered 155 records for both baseline and graph. The target-only digest is recorded
separately. A plan does not probe model endpoints or verify a loaded graph.

## Applying the code

Synthetic fixture tests exercise paragraph aliases, continuation instructions, exact
part links, catalogue occurrences, depth/cap limits and provenance. Corpus-only checks
compare source links and parent depth without issuing questions to models. They do not
establish hit@10 or a +15/+10 gain.

Verification on 27 October: lint/formatting and type checking passed. The full suite
passed 195 tests, with two Qdrant-dependent tests skipped and a Qdrant compatibility
warning because Qdrant was stopped. The isolated live Neo4j traversal and library/API
selection passed all seven tests. Review/PDF, source-gold and model-configuration checks
passed; the staging plan has zero record-validation errors and correctly reports
25 pending targets. No inference or scored evaluation was run.

An additional source-backed regression uses the maintenance manual's cooling-system
reference: the stored TOC alias resolves to body occurrences and reaches the draincock
instruction through one reference and two parent edges. The reference-build test file
passed all seven tests after adding this case.

The production graph has now been rebuilt with the revised resolver and exact part
matching. It contains 3,346 reference edges and 12,418 surface-mention edges, with no
orphans or missing/doubled provenance. The deeper recheck passed 280 tests without
skips; the final CSV-export fix passed all 28 focused storage/library/API tests.
See [the current verification record](verification_status.md) for service checks and
remaining acceptance work. Benchmark activation still requires final approval/freeze.
Engineering checks and the staging plan do not authorize baseline/M3 scoring.
