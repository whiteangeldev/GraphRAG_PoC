# M1 milestone note

14 October 2026.

## What was built

The milestone is a hybrid-retrieval baseline over the approved public corpus, with cited answers and a fixed evaluation.

The corpus is the HMMWV M998-series set (operator manual, both unit-maintenance volumes, the parts list, and the 6.2 L / 6.5 L engine manual) plus MLIT 別添52 (117 pages), processed by the same pipeline. Licences and page counts are in `docs/corpus_register.md`. Node files follow Appendix A. Two thousand synthetic service cases use Table 3-1 labels, real part numbers, and the models named for those rows.

Retrieval is one dense vector and one sparse vector in Qdrant, merged by reciprocal rank fusion with `k = 60`. The dense index uses `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Answers and judgments use `Qwen3-0.6B` through the OpenAI-compatible endpoint. The reranker is off. Each answer is written from the retrieved passages and cites node id and page. A judged fact counts only when the model returns a quote that is an exact span of a cited passage. The demo is the page served by `make demo`.

The evaluation set has 157 questions. Twenty of them, with the gold passage text copied from the node files, are in `docs/gold_review_sample.md` for review. `make eval` starts Qdrant, builds a missing index, checks the node files and the Japanese sample, scores the set, and keeps the run only when every metric stays within 0.02 of `docs/baseline_report.md`.

M2 keeps those M1 scores in `docs/m1_baseline_report.md` and replaces `docs/baseline_report.md` with the improved baseline, after the title reader was stopped at the malfunction name. The failure classes and the schema are in `docs/M2_LIMITATION_ANALYSIS.md` and `docs/M2_GRAPH_SCHEMA.md`.

## What the M1 baseline failed to connect

A relational question needs the malfunction row and a parts-list row. All 25 miss at least one of those in the ten passages given to the generator. Nineteen keep the malfunction row and miss the part. Required-fact recall and action accuracy on that slice are 0. On 22 of those questions a retrieved passage already contains the malfunction title, and the answerer still refuses: the title string it reads from the question includes the comma or the next word, and that longer string is not in the passage.

Procedures are found (hit@10 is 100%) while only 38.9% of the gold steps sit in those ten passages. Applicability hit@10 is 4.5%. Troubleshooting hit@10 is 100% and its required-fact recall is 22.2. Overall required-fact recall is 17.7 and claim precision is 8.4. The three follow-up questions do not land on their passage. Three of 16 unanswerable questions are refused; the other 13 do not look like a malfunction title, and the answerer returns a retrieved passage.

## What M2 classified

Each failing question has one class in `docs/M2_LIMITATION_ANALYSIS.md`. The M1 run already separated the kinds named in the requirements:

- Evidence split across a code row and a parts row.
- A relation required between a code and a part.
- Applicability to a model left unresolved.
- A procedure found without the rest of its steps.
- Keyword mismatch between the question and the manual, including the title reader that consumes the next word.
- A passage quoted for a question the corpus does not answer.

A class that a tighter title boundary or a synonym list would fix should be marked as outside the graph, and corrected in the baseline when the change is cheap. The schema proposal should say which of the remaining classes a traversal can address, and what gain in evidence recall and required-fact recall is expected on the relational and multi-hop questions.
