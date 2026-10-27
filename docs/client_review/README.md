# Choice B review follow-up - 27 October 2026

The client accepted Choice B and the first 25 candidates with catalogue corrections.
The minimum remains 50; the new 25 must be reviewed before M3. No full benchmark
approval, freeze or new evaluation score is claimed.

For the requested follow-up, share:

1. [The additional 25 cases](additional_25_candidates.md): new source/reference evidence
   cases, with questions, expected answers, required facts, physical pages and limits.
2. [Catalogue corrections](catalogue_corrections.md): required catalogue-specific facts
   added to the accepted cases, including the five flagged in the feedback.
3. [Normal evaluation records](../../data/eval/bounded_questions.jsonl): all 50 prepared
   cases with gold node IDs and required facts. Batch 1 is accepted; batch 2 is pending.

The [combined source-evidence pack](gold_candidates.md) includes both batches. The
[decision record](decision_record.md) records the scope decision and exact remaining
review obligation, based on [the feedback relayed by the owner](client_feedback_2026_10_27.md).
The client can reply by message; editing the record is not required.

## Scope and source checks

Read the [agreed scope](scope_and_acceptance.md) and
[evidence limits/conflicts](evidence_gaps.md). Candidate metadata is in
[review_candidates.jsonl](../../data/eval/review_candidates.jsonl); the reproducible
PDF/node audit is [review_audit.json](../../data/eval/review_audit.json).
Every selected fact has exact node evidence and a physical page. The manual PDFs are
in `data/corpus/source/`; page numbers in the pack are one-based PDF pages.

Catalogue answers require information unavailable from the maintenance source alone.
Maintenance paragraph references resolve to actual body/procedure occurrences, not
merely a table-of-contents alias. New questions were prepared with AI assistance and
have not been approved by the client. Synthetic cases and keyword part candidates are
not independent evidence of a repair.

Validate without model inference:

```bash
make review-check
make gold-check
```

After an intentional candidate/fact edit, regenerate and inspect artifacts with:

```bash
.venv/bin/python -m graphrag_poc.eval.review_package --write
```

The active 155-question legacy set, historical scores, graph and caches are not replaced
by this review package. The old keyword targets remain excluded. The executable
acceptance contract stays pending and blocks M3. Local stores and the small model smoke
test have passed earlier checks; this does not measure the new benchmark.

Validation on 27 October: 50 source-backed cases, 146 selected excerpts across 76 PDF
pages, and all 50 normal evaluation records passed their checks. The five flagged
catalogue rows were also visually verified for part-number/NSN column alignment.
The earlier test suite passed 172 tests and skipped 8 database/demo integration tests because
the local stores were unavailable; lint/formatting and type checking passed. No model
inference or new baseline/M3 scoring was performed. Acceptance checking remains blocked.

Subsequent engineering verification, including the rebuilt graph and live stores, is
recorded in [the current verification record](../verification_status.md). These checks
do not approve the pending cases or establish the required evaluation gains.

After review, apply corrections, fill any rejected-case gap, align traversal, freeze the
50 target IDs and fingerprint with traceable approval, and run the fresh comparable
baseline/graph evaluation. Final delivery also requires the
[M4 schema mapping](../schema_mapping.md), GitLab history and handover evidence.
