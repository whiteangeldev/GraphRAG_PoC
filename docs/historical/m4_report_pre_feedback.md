# M4 report

The graph measured in M3 is now a library and a service. This report records the result, the limits that remain, and what to do with Sodick's own node files. The numbers are copied from `docs/m3_report.md` and `docs/graph_build_report.md`. The 157 questions were not scored again for this milestone.

## Result

The comparison is the improved baseline against the same retriever plus the graph. The graph weight is 1.0. The hop depth is 2. The traversal cap is 200. Hit@10 still uses the first 10 fused passages. The reranker is off. Generation and judging used Qwen3-0.6B. A judged fact counts only when its quote is an exact span of a cited passage.

| Question type | hit@10 | Evidence recall | Required-fact recall |
|---|---:|---:|---:|
| Overall | 78.7 | 61.3 | 32.3 |
| lookup | 82.9 | 82.9 | 51.4 |
| procedure | 100.0 | 38.9 | 45.8 |
| applicability | 4.5 | 4.5 | 0.0 |
| relational | 100.0 | 96.0 | 36.0 |
| multi_hop | 100.0 | 64.0 | 20.0 |
| troubleshooting | 100.0 | 100.0 | 22.2 |
| follow_up | 0.0 | 0.0 | 0.0 |

Against the improved baseline, evidence recall on relational and multi-hop questions rose 44.0 points. Required-fact recall on those questions rose 15.2 points. No question type lost more than 1 point of hit@10 or required-fact recall. Lookup latency at the 95th percentile rose 65.5 ms, inside the 100 ms limit.

The relational gain is the parts-list row. The malfunction row was often already retrieved. The walk from that malfunction, through the keyword on `CANDIDATE_PART` and the canonical `LISTS` row, puts the part passage in the graph list. Fusion then places it in the ten passages given to the generator. The relation frame names the code, the first two steps, the part number, and up to five cases. When the question asks for a part, those lines are added to the answer only if they are exact spans of a retrieved passage.

The corpus graph has 22,952 passages, 30 malfunctions, 4,478 parts, 2,000 cases, and 12,398 derived `MENTIONS` edges. No node is an orphan. No edge is missing a page or a case id. A sample of 100 derived edges is in `docs/graph_build_report.md`.

## Limits

Applicability hit@10 stays at 4.5. The questions ask whether one instruction mentions a model. `APPLIES_TO` connects many passages to that model, and boosting passages that were already retrieved does not find an instruction the keyword search missed.

Follow-up stays at 0. The three questions depend on the previous turn naming a different model. The router does not treat a model-only link as a table or case edge, so the graph stays off. Turning it on without a better seed would add a fan-out of model passages and risk the lookup scores.

Unanswerable questions are still a generator policy. A code that is not in the term table does not become a different malfunction. The graph does not refuse for the caller. The demonstration answerer refuses when the requested title is absent from the retrieved passages.

Procedure hit@10 was already 100. The graph stays off for a procedure that does not name a code, a part, or a case, so procedure evidence stays 38.9. The traversal API still returns the next step and the bound caution when the caller passes the step as a seed. The oil-cooler check does that.

Two relational questions do not reach their gold part. The gold row's description contains the keyword and the canonical part row does not, so `CANDIDATE_PART` is not drawn. That is fault 8, keyword `OIL PUMP`.

Derived `MENTIONS` edges are surface forms: a model token or a part number written in the passage, with weight 0.4. They are not a second copy of `APPLIES_TO`. Sodick's review of 50 of the 100 sampled edges is still open. The sample is the review set. It is not a claim that the review has been done.

The required-fact gain depends on the answer containing the part number and the step span. The frame supplies those strings only when the retrieved passage contains them. A model that paraphrases and drops the number loses the fact under the quote rule. The measured run appends the frame line in that case.

## Recommendations

Keep the public function names in Appendix A.4. Keep the labels in `docs/schema_reference.md` until a review asks for a rename. Appendix A.3's example labels are a generic sketch. Renaming the loaded graph would break the measured reports.

Build the first Sodick graph from a small node file, on the pattern of `tests/fixtures/m4`, before loading a full manual. Call `link_entities` and `traverse` from the existing retriever. Start with graph weight 1.0 and hop depth 2. Change those two numbers only, and keep hit@10 on the first 10 fused passages.

Use a new `build` id for each customer load. Roll that id back with `clear_build` if the load is wrong. Leave `corpus` in place until the customer graph replaces the demonstration.

Do not raise the cutoff, and do not turn the reranker on to chase applicability or follow-up. Those two types need a seed that names the instruction, not a longer walk. The Japanese sample is already in the node files. The same library reads it. No English-only branch is required.

Review the derived-edge sample against the source pages as part of the joint M3 and M4 check. If a sampled edge's surface form is not on that page, delete that rule before using `MENTIONS` on plant documents.

## Handover

Two sessions are described in `docs/handover.md`. The recordings and the written answers are added after Sodick's developers attend. The package they need before those sessions is this repository: `pip install`, `make service`, and the four guides.
