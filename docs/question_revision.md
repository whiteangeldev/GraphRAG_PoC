# Question revision — 26 October 2026

Historical revision of the legacy keyword benchmark. The current Choice B records and
approval status are described in [the client review follow-up](client_review/README.md).

Client feedback item 2 is implemented for review: all 25 relational and 25 multi-hop
questions now use individually edited symptom descriptions, without copied malfunction
titles, diagnostic keyword hints, or answer part numbers. Replacement requests are
conditional on evidence rather than assuming that a symptom establishes a failed part.
The wording was revised with AI assistance and still needs client review.

The maintained input is [question_wording.jsonl](../data/eval/question_wording.jsonl).
Each prompt is pinned to its existing question ID and source malfunction node. Regeneration
fails on missing, extra, duplicate, or mismatched entries instead of falling back to the
old templates. All 50 are marked `vocabulary: user` because of their revised wording.

`procedure-0001` and `procedure-0003` are removed from the builder and saved set. Their
document-root front-matter groups mixed unrelated instructions and cautions. The remaining
procedure IDs are unchanged; no replacement questions were added to conceal the removal.

| Current set | Count |
|---|---:|
| All questions | 155 |
| Relational | 25 |
| Multi-hop | 25 |
| Procedure | 20 |

The 50 questions retain the same gold passages, required facts, and explicit
`keyword_exploratory` status as the corrected-data snapshot in
[keyword_exploratory.jsonl](../data/eval/keyword_exploratory.jsonl). Natural wording does
not validate those heuristic relationships. None counts toward the M3 acceptance targets.
The source-chain and scope agreement remain pending, with the +15/+10 targets unchanged.
The [review sample](gold_review_sample.md) now displays this limitation beside the gold.

Historical regeneration commands, without inference:

```bash
.venv/bin/python -m graphrag_poc.eval
.venv/bin/python -m graphrag_poc.eval.review
```

The first command overwrites the active `data/eval/questions.jsonl` with the legacy
keyword set. Do not use it to stage or activate the bounded benchmark, or after a
reviewed bounded set has been activated. Use `make bounded-plan` for a report that
preserves the active questions and approval contract.

The pending target manifest fingerprints the revised set. Any later question edit must
update that fingerprint before agreement; an approved set must undergo renewed review.
The original pre-feedback set, corrected-data keyword snapshot, old model outputs, and
reported scores are preserved as historical artifacts. No model scoring, embedding,
reindexing, or service startup was performed for this revision.

Validation: 133 tests passed; Ruff and strict mypy passed (66 source files). The saved
questions and review sample match regeneration. All ten partial source relations still
validate, and M3 acceptance remains blocked while gold/scope approval is pending.

The next implementation step is the realistic answer generator and separate judge,
including removal of the regex title gate. A new scored M3 result still requires reviewed
gold and written agreement on which slices count toward acceptance.
