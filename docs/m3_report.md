# Graph comparison

The same 157 questions were scored with the improved baseline and with the graph.
Graph weight is 1.0. Hop depth is 2. The traversal cap is 200.
The reranker is off. Hit@10 still uses the first 10 fused passages.

| Setting | Value |
|---|---|
| Embedding model | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Generation | Qwen3-0.6B |
| Judge | Qwen3-0.6B |
| Graph weight | 1.0 |
| Hop depth | 2 |

## Scores with the graph

| Question type | Questions | hit@10 | MRR | Evidence recall | Required-fact recall |
|---|---:|---:|---:|---:|---:|
| Overall | 157 | 78.7 | 0.703 | 61.3 | 32.3 |
| lookup | 35 | 82.9 | 0.776 | 82.9 | 51.4 |
| procedure | 22 | 100.0 | 0.898 | 38.9 | 45.8 |
| applicability | 22 | 4.5 | 0.023 | 4.5 | 0.0 |
| relational | 25 | 100.0 | 0.900 | 96.0 | 36.0 |
| multi_hop | 25 | 100.0 | 1.000 | 64.0 | 20.0 |
| troubleshooting | 9 | 100.0 | 0.463 | 100.0 | 22.2 |
| follow_up | 3 | 0.0 | 0.000 | 0.0 | 0.0 |
| unanswerable | 16 | — | — | — | — |

## Gates

| Gate | Change | Required | Result |
|---|---:|---:|---|
| relational and multi-hop evidence recall | 44.0 | 15 | pass |
| relational and multi-hop required-fact recall | 15.2 | 10 | pass |
| lookup p95 latency | 65.5 | 100 | pass |
| lookup hit@10 | 11.4 | -1 | pass |
| lookup required-fact recall | 8.6 | -1 | pass |
| procedure hit@10 | 0.0 | -1 | pass |
| procedure required-fact recall | 0.0 | -1 | pass |
| applicability hit@10 | 0.0 | -1 | pass |
| applicability required-fact recall | 0.0 | -1 | pass |
| relational hit@10 | 24.0 | -1 | pass |
| relational required-fact recall | 20.0 | -1 | pass |
| multi_hop hit@10 | 12.0 | -1 | pass |
| multi_hop required-fact recall | 12.0 | -1 | pass |
| troubleshooting hit@10 | 0.0 | -1 | pass |
| troubleshooting required-fact recall | 0.0 | -1 | pass |
| follow_up hit@10 | 0.0 | -1 | pass |
| follow_up required-fact recall | 0.0 | -1 | pass |
| unanswerable hit@10 | 0.0 | -1 | pass |
| unanswerable required-fact recall | 0.0 | -1 | pass |

## Demonstration

relational-0001 asks which alternator part is listed for the charging fault.
The graph channel is in the top 10: True.
Relation frame:
code: 4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER
cause: Step 1. Check battery cable connections for looseness, damage, or corrosion. Notify unit maintenance of any damage to battery cables.
remedy: Step 2. Check for broken or missing alternator belts. Notify unit maintenance if alternator belts are broken or missing.
part: 12339317 LEAD,ELECTRICAL 200 AMP,MAKE FROM WIRE,P/N M13486/1-14,58 INCHES LONG USE WITH 200 AMP ALTERNATOR
cases: C-000001, C-000031, C-000061, C-000091, C-000121
