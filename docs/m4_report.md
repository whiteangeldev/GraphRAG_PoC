# M4 delivery status

Updated 27 October 2026. The current engineering checks pass. Revised M3 measurements and
final M4 acceptance are pending. The previous report is preserved as a
[historical snapshot](historical/m4_report_pre_feedback.md); its scores and graph counts
describe the earlier data and model path.

## Implemented deliverables and validation

The package exposes `build_graph`, `link_entities`, `route`, `traverse`, and `fuse` in
`graphrag_poc.library`. The HTTP service exposes health, graph build, entity linking,
traversal and statistics. Installation and use are described in the
[architecture](architecture.md), [integration](integration.md),
[operations](operations.md) and [schema reference](schema_reference.md) guides.

Historical local check output supplied on 26 October records:

| Check | Observed result |
|---|---|
| Review package | 25 draft candidates validated against nodes and PDFs; 0 approved targets |
| Source relations | 10 source-backed partial links validated; 0 approved complete target chains |
| Model configuration | Qwen/Qwen3-8B generator and Qwen/Qwen3-14B judge valid; no endpoint calls |
| Lint and formatting | Passed; 126 files already formatted |
| Type checking | Passed on 71 source files |
| Tests | 168 passed, 8 skipped; 1 Qdrant server-version warning |

These historical results verify the code and source checks exercised then. They do not
establish live model quality or successful database integration. The skipped tests and unavailable
Qdrant compatibility check remain qualifications; rerun the relevant integration checks
with the stores available. Mocked model tests do not establish real endpoint readiness.

Historical live verification on 26 October: the corrected-data index command passed.
The graph import completed but its final spot check used a stale charging-fault node
ID. After correcting that ID, 19 focused graph, library/service and demonstration
tests passed with no skips. Lint/formatting and type checking also passed. Read-only
comparison of the imported database with the corrected source build and saved report
confirmed all node/edge counts, oil-cooler links and charging-fault candidate links,
with zero orphans and zero missing/doubled provenance. The existing import was retained.
These checks establish the exercised local integrations, not a clean-install check or
live answer/judge model quality.

## Current evaluation and data limits

The active legacy benchmark has 155 questions. Its 50 keyword-derived relational/multi-hop
questions remain exploratory and excluded from acceptance. The client has approved
Choice B and accepted the first 25 corrected cases; full repair chains are not required.
Another 25 independent cases are prepared for review. All 50 are converted to normal
evaluation records in `data/eval/bounded_questions.jsonl`, separate from the active
legacy benchmark. The complete 50-question set is not approved or frozen, and M3 remains
blocked. The 50-target minimum and +15/+10 thresholds are unchanged.

The new batch has 8 operator references, 2 maintenance/catalogue links and 15 maintenance
task references from both maintenance volumes. All 146 selected excerpts match the
physical PDFs across 76 pages after whitespace normalization. The prepared source pack
and [M4 schema mapping](schema_mapping.md) are available for review. Stored TOC aliases
now resolve to actual body occurrences and compatible continuations through the explicit
reference resolver. The bounded route follows references into instructions with at most
three actual edges, or exact part-number mentions to all matching catalogue rows within
the cap. It excludes the keyword part frame. These are implemented code changes;
the production graph has now been rebuilt from the revised code. See the
[current verification record](verification_status.md) and
[traversal preparation](traversal_alignment.md).

The earlier 27 October test run passed 172 tests with 8 store-dependent integration tests
skipped and one Qdrant compatibility warning because the stores were unavailable.
Lint/formatting and type checking passed. These historical checks do not replace a fresh
live integration run after traversal changes or the client-approved baseline/graph comparison.

An earlier traversal check passed 195 tests with two Qdrant-dependent
tests skipped and one compatibility warning because Qdrant was stopped. Lint/formatting
and type checking passed. Source/PDF review validated all 50 cases, with 25 accepted and
25 pending. No model calls or M3 scoring were made. The production corpus was retained;
those earlier fixture checks did not establish production retrieval quality.

The deeper recheck passed 280 tests with no skips. After the final CSV-export fix,
all 28 focused storage/library/API tests passed. Lint/formatting, type checking and
dependency checks passed. The direct baseline, reproduction and M3 commands all stop
before runtime work while approval is pending. Fresh measurements remain required.

`make bounded-plan` writes a report for replacing the legacy targets with the 50 bounded
targets while retaining 105 controls for per-type regression and lookup latency checks.
It does not activate the benchmark or call models. Readiness remains blocked by the
25 pending targets and final freeze. The target-only digest is separate from the contract's
full-run digest, which must cover the same ordered 155 records for baseline and graph.

The historical corrected-node and synthetic-case store build was verified with
22,956 passages, 5,088 parts, 30 malfunctions, 2,000 cases and
12,403 `MENTIONS` edges; those counts are preserved in the
[previous build report](historical/graph_build_report_before_explicit_refs_2026_10_27.md).
The current [build report](graph_build_report.md) records 3,346 `REFERS_TO` and
12,418 `MENTIONS` edges, no orphan nodes and no missing/doubled provenance. Keyword
`CANDIDATE_PART` edges propose candidates; they do not prove a repair relationship.
Synthetic case part links do not independently confirm a diagnosis or part fit.
`MENTIONS` records deterministic surface-form matches, not model-extracted repair facts.
Neither a deterministic rule nor its `derived` flag establishes semantic validity.

The model answer path now uses structured model output with validated citations. It
bypasses title gating and does not append part numbers, frame lines or fallback
citations. A separate offline quote helper remains for demonstration/testing and does
not validate the model answer path. The bounded route supplies no keyword relation
frame; frames retained by legacy lookup/troubleshooting routes are unverified hints.

| Revised measurement | Status |
|---|---|
| Live generator/judge smoke test | Historical pass on 26 October with local Ollama qwen3:8b / qwen3:14b; supplied-evidence suite only |
| Comparable baseline and graph measurements | Pending final target review/freeze and fresh same-model measurements |
| Evidence recall gain | Pending; current threshold at least +15 percentage points |
| Required-fact recall gain | Pending; current threshold at least +10 percentage points |
| Per-type regression | Pending; loss no greater than 1 percentage point in hit@10 or required-fact recall |
| Lookup p95 added latency | Pending; current limit 100 ms |
| Reproduction of revised comparison | Pending fresh results |

Use the same frozen questions, generator, independent judge, embedding model and first
10 fused passages for both measurements. Current graph defaults are weight 1.0, depth
2 for other routes, up to 3 actual edges for bounded references, and cap 200. These are
configuration values, not a new measured result. Keep the reranker off for the agreed
comparison. A smoke pass alone does not satisfy these gates.

The passing smoke result is in `data/eval/model_smoke/results.json`. Judge calibration,
both cited positive answers and the missing-evidence refusal passed. A prior quote
punctuation failure was diagnosed and preserved; the `judge-quotes-v3` instruction keeps
exact quote validation unchanged. That protocol revision historically passed 47 focused
tests, lint and type checking. The protocol and traversal changes require fresh comparable
baseline/graph runs.

## Completion and handover

1. Obtain review of the [additional 25](client_review/additional_25_candidates.md), apply
   corrections and fill any rejected-case gap. Scope and the corrected first 25 are
   accepted. Record explicit approval and freeze the 50 targets together with the 105
   controls using the full-run digest.
2. Retain the verified current corpus graph/service and the historical
   [live smoke result](model_smoke.md). Rebuild affected artifacts if source data or
   code changes; recheck models when their answer/judge settings or prompts change.
3. Run `make baseline`, `make m3` and then `make eval`. Review failures and retained raw
   answers/citations/judgments before replacing historical result claims.
4. Review the prepared [schema mapping](schema_mapping.md) against the client's requirements,
   record a current demonstration and verify the documented installation path.
5. Deliver through Sodick's GitLab with history and without credentials. Record the
   delivered commit and perform or explicitly schedule the [handover](handover.md).

The original Requirements v1.1 document is absent from this repository, so complete
clause-by-clause compliance and the final schema mapping cannot yet be certified.
GitLab delivery, client edge review and attended handover sessions are not recorded as
completed. This report does not claim M3/M4 acceptance.
