# Baseline report

The Step 6 retriever scored every question in `data/eval/questions.jsonl`.
Dense and sparse lists are merged with reciprocal rank fusion.
The generator receives the first 10 fused passages.
The reranker is off.

| Setting | Value |
|---|---|
| Embedding model | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Generation | none; the answer is the text of the cited passages |
| Judge | quote check, because JUDGE_MODEL is empty. A fact or sentence counts only when its quote is an exact span of a cited passage. Set JUDGE_MODEL to use the language-model judge; the same quote rule still applies. |
| Fusion | RRF k=60, dense + sparse |
| Evidence size | 10 |
| Temperature | 0 |
| Seed | 0 |

## Scores

| Question type | Questions | hit@10 | MRR | Evidence recall | Required-fact recall | Claim precision | Action accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|
| Overall | 157 | 69.5 | 0.461 | 39.1 | 24.4 | 82.2 | 59.2 |
| lookup | 35 | 71.4 | 0.470 | 71.4 | 34.3 | 73.1 | 62.9 |
| procedure | 22 | 100.0 | 0.890 | 38.9 | 38.9 | 100.0 | 100.0 |
| applicability | 22 | 4.5 | 0.023 | 4.5 | 63.6 | 100.0 | 100.0 |
| relational | 25 | 76.0 | 0.447 | 38.0 | 0.0 | 0.0 | 0.0 |
| multi_hop | 25 | 88.0 | 0.525 | 29.3 | 14.7 | 63.6 | 48.0 |
| troubleshooting | 9 | 100.0 | 0.463 | 100.0 | 0.0 | 100.0 | 100.0 |
| follow_up | 3 | 0.0 | 0.000 | 0.0 | 0.0 | 100.0 | 100.0 |
| unanswerable | 16 | — | — | — | — | — | 18.8 |

hit@10, MRR, and evidence recall cover the 141 questions that have a gold passage. The 16 unanswerable questions have none, so those three cells are blank. Required-fact recall divides facts judged present, each with a quote from a cited passage, by the facts required. Claim precision divides supported sentences by the sentences shown. Both cover answerable questions. Action accuracy covers every question: a refusal for an unanswerable question, and an answer for every other expected action. Shares are percentages. MRR is the mean of 1/rank.

## Relational questions the baseline misses

Of 25 relational questions, 25 did not place every gold passage in the 10 passages given to the generator. 19 of those kept the malfunction row and missed the parts-list row. 6 missed some other gold passage. 0 relational questions had every gold passage in the evidence set and every required fact in the answer. Examples: relational-0002 missed tm280_24p_1:parts:r4993; relational-0003 missed tm280_24p_1:parts:r4993; relational-0004 missed tm280_24p_1:parts:r4553. The answerer refused questions whose retrieved passages contain the malfunction title: 22 relational questions, 12 lookup questions, and 12 multi-hop questions. The title string it read from the question also included the comma or the next word, and that longer string is not in the passage.

On 13 applicability questions the required fact is a model token found in a cited passage other than the gold passage. Required-fact recall for that type is therefore higher than hit@10.

3 of 16 unanswerable questions were refused. 3 of those read as a malfunction title that is not in the retrieved passages. The other 13 do not read as a title, so the answerer quotes a retrieved passage.

11 questions are Japanese. 10 of them have gold passages in mlit_b052.
