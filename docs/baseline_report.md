# Baseline report

> Historical snapshot before the client-feedback revision.
> Its scores, counts, model behavior and demonstration outputs do not validate the
> corrected data or current implementation. See [current M4 status](m4_report.md).

The Step 6 retriever scored every question in `data/eval/questions.jsonl`.
Dense and sparse lists are merged with reciprocal rank fusion.
The generator receives the first 10 fused passages.
The reranker is off.
The malfunction title is read without the following word. This is the improved baseline.

| Setting | Value |
|---|---|
| Embedding model | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Generation | Qwen3-0.6B |
| Judge | language model Qwen3-0.6B. A positive judgment counts only when its quote is an exact span of a cited passage. |
| Fusion | RRF k=60, dense + sparse |
| Evidence size | 10 |
| Temperature | 0 |
| Seed | 0 |

## Scores

| Question type | Questions | hit@10 | MRR | Evidence recall | Required-fact recall | Claim precision | Action accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|
| Overall | 157 | 69.5 | 0.465 | 39.1 | 24.1 | 21.4 | 88.5 |
| lookup | 35 | 71.4 | 0.466 | 71.4 | 42.9 | 28.4 | 97.1 |
| procedure | 22 | 100.0 | 0.898 | 38.9 | 45.8 | 25.9 | 100.0 |
| applicability | 22 | 4.5 | 0.023 | 4.5 | 0.0 | 0.0 | 100.0 |
| relational | 25 | 76.0 | 0.467 | 38.0 | 16.0 | 8.9 | 88.0 |
| multi_hop | 25 | 88.0 | 0.525 | 29.3 | 8.0 | 1.8 | 96.0 |
| troubleshooting | 9 | 100.0 | 0.463 | 100.0 | 22.2 | 45.7 | 100.0 |
| follow_up | 3 | 0.0 | 0.000 | 0.0 | 0.0 | 0.0 | 100.0 |
| unanswerable | 16 | — | — | — | — | — | 18.8 |

hit@10, MRR, and evidence recall cover the 141 questions that have a gold passage. The 16 unanswerable questions have none, so those three cells are blank. Required-fact recall divides facts judged present, each with a quote from a cited passage, by the facts required. Claim precision divides supported sentences by the sentences shown. Both cover answerable questions. Action accuracy covers every question: a refusal for an unanswerable question, and an answer for every other expected action. Shares are percentages. MRR is the mean of 1/rank.

## Relational questions the baseline misses

Of 25 relational questions, 25 did not place every gold passage in the 10 passages given to the generator. 19 of those kept the malfunction row and missed the parts-list row. 6 missed some other gold passage. 0 relational questions had every gold passage in the evidence set and every required fact in the answer. Examples: relational-0002 missed tm280_24p_1:parts:r4993; relational-0003 missed tm280_24p_1:parts:r4993; relational-0004 missed tm280_24p_1:parts:r4553.

3 of 16 unanswerable questions were refused. 3 of those read as a malfunction title that is not in the retrieved passages. The other 13 do not read as a title, so the answerer quotes a retrieved passage.

11 questions are Japanese. 10 of them have gold passages in mlit_b052.
