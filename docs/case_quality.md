# Feedback data revision

26 October 2026. This revision repairs source extraction and synthetic-case generation.
No embedding, generation, judging, graph loading, or retrieval evaluation was run.

The operator and parts node files were regenerated with the corrected parser. Cases now
sample only informative source instruction/response pairs. Sentence boundaries preserve
parenthesized references such as `para. 3-17`. Generic causes, duplicated instructions,
and escalation-only responses are excluded. Part references must occur in the catalogue's
PART NUMBER column; a value in CAGE or another column does not qualify.

There are 2,000 deterministic cases covering 22 eligible malfunction rows. Eight rows
have no eligible pair and are listed in `data/cases/quality_report.json`. Numeric causes,
generic "All causes" / "Other causes", and `7X677` substituted as a part number are zero.
These are repeated synthetic diagnostic scenarios, not 2,000 independent field observations.
The `cause` field retains the manual's diagnostic instruction rather than inventing a
confirmed diagnosis. Records explicitly carry `diagnosis_confirmed=false` and
`case_kind=synthetic_diagnostic_instruction`.

Part numbers are valid catalogue entries, but their relationship to each malfunction
still comes from the existing keyword rules. Records therefore carry
`part_relation=keyword_candidate_unverified`. Valid catalogue membership does not prove
repair compatibility. Source-checked partial links are now available in
`docs/source_relation_review.md`; complete target chains and client scope agreement remain pending.

The current question file and gold sample were mechanically refreshed to resolve corrected
node IDs and table cells. They retain the existing templates and are provisional. Their
pre-feedback versions are in `data/eval/pre_feedback/`. This is not the independent gold
and wording revision required by the client. Existing judgments, results, failure analysis,
and baseline/M3/M4 scores are historical and have not been recomputed for this revision.
They must not be presented as measurements of the corrected data.

Rebuild both Qdrant collections and the graph before new retrieval measurements. Existing
index readiness checks only vector dimensions, so it will not detect this data change.
Use fresh judgments after the benchmark is reviewed. The quality report records current
input hashes, excluded faults, and audit counts to make that handoff explicit.
