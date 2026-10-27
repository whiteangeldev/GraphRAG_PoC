# Client scope and gold decision record

Status: Choice B approved; the first 25 candidates accepted with corrections. The
additional 25 require review. The complete 50-question benchmark is not yet approved
or frozen, and M3 must not run yet.

The [client feedback](client_feedback_2026_10_27.md) was relayed by the project owner on
27 October 2026. The client's name and original message timestamp were not supplied;
no signature, original decision timestamp or final benchmark approval is invented here.

| Decision | Recorded client response |
|---|---|
| Scope | Choice B: bounded manual relationships; full repair chains not required |
| Accepted relationships | Explicit troubleshooting-to-paragraph references; maintenance part number to catalogue row; additional maintenance task-to-paragraph references requested |
| First batch | All original 25 accepted, subject to catalogue-specific facts and normal evaluation-format conversion |
| Catalogue corrections | Mandatory NSN or catalogue-description facts added to all catalogue cases, including the five specifically identified |
| Additional batch | 25 new independent cases prepared separately for review; acceptance pending |
| Minimum | Retain 50 |
| Gains | Retain +15 percentage points evidence recall and +10 required-fact recall |
| HVAC mismatch | Exclude HVAC-to-3-28; a separate, valid HVAC-to-2-61 control reference is a new pending candidate |
| Water pumps | Keep bounded 6.2L / non-detuned 6.5L questions; no 6.5L-detuned applicability claim |
| Deferrals | Synonym/Term nodes, reranker and graphic troubleshooting pages accepted as deferred |
| Japanese sample | Pipeline coverage only |
| Synthetic cases | Demo data only |
| Final evaluation | Fresh baseline and graph results on the frozen 50 target questions; same model configuration for both |
| M4 | Schema mapping required |
| Delivery | Sodick GitLab with repository history required; project URL not supplied |
| Full benchmark approval, freeze and final acceptance | Pending |

The accepted first-batch IDs are recorded in `accepted_candidate_ids` in
`data/eval/target_set.json`. The corrected first batch and the new batch are in
[the combined evidence pack](gold_candidates.md). Send only the new cases in
[additional_25_candidates.md](additional_25_candidates.md) for the requested review.
The new cases have different source/reference evidence pairs; they are not rewordings
of the accepted cases.

All prepared cases are converted to the ordinary evaluation record structure in
`data/eval/bounded_questions.jsonl`: question, slice, expected action, gold node IDs,
document keys/pages and required facts. Each fact identifies its source node. Batch 1
is marked client-accepted; batch 2 remains pending. These records are separate from
the active legacy benchmark; writing this decision record does not start scoring.

After the next review: apply corrections/rejections, complete any resulting count gap,
align reference/part traversal with the agreed cases, and freeze the actual 50 target
IDs and question fingerprint with a traceable approval record. Keep source applicability
limits and the exclusion of the old keyword gold. Then run the same models on baseline
and graph and report the actual outcomes, including any failed gates. GitLab delivery
and handover attendance are separate obligations.
