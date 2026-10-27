# GraphRAG PoC

The [client review follow-up](docs/client_review/README.md) records the client's Choice B
approval and acceptance of the first 25 cases with catalogue corrections. Another 25
independent cases are prepared for review, with normal evaluation records and source
evidence. The minimum remains 50 and M3 is blocked until the full set is reviewed and
frozen. Validate the prepared cases against the source PDFs with `make review-check`.

While client review is pending, [model readiness and smoke checks](docs/model_smoke.md)
can proceed separately: `make model-smoke-plan` makes no endpoint calls;
`make model-probe` lists served models without inference. `make model-smoke` explicitly
runs the bounded live suite after the endpoints pass their probes.

The 26 October feedback data revision is described in [the case quality note](docs/case_quality.md).
Saved baseline/M3/M4 scores describe the earlier data. Corrected nodes and cases require
reindexing and fresh evaluation. [The question revision](docs/question_revision.md) rewrites
all 50 relational/multi-hop prompts and removes the two invalid procedure entries.
The active legacy set has 155 questions. The new 50-case bounded set is prepared
separately in `data/eval/bounded_questions.jsonl`; its second batch still needs review.

The [current M4 delivery status](docs/m4_report.md) separates implemented interfaces,
local checks and remaining acceptance work. The [schema mapping](docs/schema_mapping.md)
is a draft; GitLab delivery and attended handover sessions remain pending.

[Bounded traversal preparation](docs/traversal_alignment.md) adds actual procedure
resolution and explicit part/reference paths. `make bounded-plan` checks the proposed
50 targets plus 105 retained controls without activating data or calling models.
The local corpus has been rebuilt with the revised code; the
[verification record](docs/verification_status.md) records the current checks.
Approval and the final benchmark freeze remain pending.

Ten source-checked partial links are in [the relation review](docs/source_relation_review.md).
The existing 50 keyword questions are explicitly exploratory. `make gold-check` validates
the source manifest. `make eval` and M3 acceptance stop before inference until the reviewed
target set and scope agreement are ready; the +15/+10 targets remain unchanged.
The [model evaluation revision](docs/model_evaluation_revision.md) removes the title gate
and citation/part patching from the model path and configures separate answer/judge models.

Hybrid retrieval over an approved public corpus, a Neo4j graph, and an installable library Sodick can call from its own retriever.

## Corpus

The approved list, licences, and page counts are in [`docs/corpus_register.md`](docs/corpus_register.md). Source PDFs are in `data/corpus/source/`. Node files are in `data/nodes/`. Synthetic service cases are in `data/cases/`.

## Setup

Python 3.12. From the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

Qdrant and Neo4j run from Docker Compose. Qdrant is `qdrant/qdrant:v1.19.2` on port 6333. Neo4j Community is `neo4j:5.26.12` on Bolt port 7687.

## Environment

Copy `.env.example` to `.env` when you want a local override. Secrets stay in the environment, not in code.

| Variable | Role |
|---|---|
| `QDRANT_URL` | Qdrant HTTP API. Default `http://127.0.0.1:6333`. |
| `QDRANT_API_KEY` | Leave empty for the local Compose service. |
| `EMBEDDING_BACKEND` | `fastembed` for the local model, or `openai` for an OpenAI-compatible `/v1/embeddings` endpoint. |
| `EMBEDDING_MODEL` | Model name. The cached report uses `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. |
| `OPENAI_BASE_URL` | Base URL when the backend or the generator is `openai`. Default `http://127.0.0.1:8000/v1`. |
| `OPENAI_API_KEY` | Key for that endpoint. The local server accepts any value. |
| `GENERATION_MODEL` | Answer model. Evaluation defaults to `Qwen/Qwen3-8B`; empty is rejected for evaluation. |
| `JUDGE_MODEL` | Separate judge. Evaluation defaults to `Qwen/Qwen3-14B`; empty or the same model as the generator is rejected. Positive judgments require exact source quotes. |
| `GENERATION_BASE_URL`, `GENERATION_API_KEY` | Optional answer endpoint/key overrides; otherwise use `OPENAI_BASE_URL` / `OPENAI_API_KEY`. |
| `JUDGE_BASE_URL`, `JUDGE_API_KEY` | Judge endpoint/key overrides; otherwise use `OPENAI_BASE_URL` / `OPENAI_API_KEY`. |
| `GENERATION_MAX_TOKENS`, `JUDGE_MAX_TOKENS` | Output limits, default 1536 / 4096. Truncation stops the run. |
| `GENERATION_EXTRA_BODY`, `JUDGE_EXTRA_BODY` | Optional JSON server extensions. Qwen3 defaults disable thinking; set `{}` if the server does not support the extension. |
| `GENERATION_CACHE_DIR` | Evaluation defaults to `data/eval/answers`; explicitly empty disables answer caching. |
| `GENERATION_TEMPERATURE` | `0` during evaluation. |
| `GENERATION_SEED` | `0` during evaluation. |
| `RERANK_ENABLED` | Leave `false` for the reported baseline. |
| `DEMO_PORT` | Demo page port. Default `8080`. |
| `NEO4J_URI` | Bolt URI. Default `bolt://localhost:7687`. The service container uses `bolt://neo4j:7687`. |
| `NEO4J_USER` | Neo4j user. Default `neo4j`. |
| `NEO4J_PASSWORD` | Neo4j password. Default `graphrag-poc`. |
| `GRAPH_BUILD` | Build id the service reads when a request omits one. Default `corpus`. |

## Evaluate the revised benchmark

```bash
make model-check
```

This checks model settings without contacting endpoints. Defaults are `Qwen/Qwen3-8B`
for answers and `Qwen/Qwen3-14B` for judging. Configure the actual served model IDs and
endpoints in `.env` or exported variables. The same settings apply to both baseline
and graph subprocesses. Docker Compose starts the stores and graph service; model servers
must be supplied separately. See [the model setup and validation note](docs/model_evaluation_revision.md).

After client agreement on gold and scope, rebuild the indexes and establish a fresh baseline:

```bash
make up
make index
make graph
make baseline
make m3
```

`make baseline`, `make m3`, and `make eval` check acceptance readiness and model configuration
before starting services. Rebuild both indexes and the graph from corrected data before scoring; existing
collections with matching vector sizes can still contain earlier data.

Use `make eval` to reproduce the new baseline and graph reports after that first run.
It rejects a different question fingerprint or model protocol before indexing/inference.
Historical reports used Qwen3-0.6B for both roles and the earlier 157-question set;
those scores remain historical and cannot validate the revised benchmark.

Answers, validated citation IDs, and evidence IDs are retained in the run results.
Answer caching reuses identical prompts and settings; judge caching also tracks facts,
source text, judge endpoint/settings, and protocol version. Changing the inputs invalidates
the corresponding cache. The 20-question client review sample is
[`docs/gold_review_sample.md`](docs/gold_review_sample.md).

M2's earlier classification is in [`docs/M2_LIMITATION_ANALYSIS.md`](docs/M2_LIMITATION_ANALYSIS.md).
The graph schema is [`docs/M2_GRAPH_SCHEMA.md`](docs/M2_GRAPH_SCHEMA.md).

## Demo

```bash
make demo
```

Open http://127.0.0.1:8080. The page shows the answer, each citation with document and page, and the fused ranking.

The five-minute demonstration is four questions: one lookup, one procedure that includes the hot-oil caution, one relational question, and one refusal. The recording is [`docs/m1-demonstration.mp4`](docs/m1-demonstration.mp4). The questions, the answers, and what to say about each are in [`docs/demonstration.md`](docs/demonstration.md). Regenerate that file with:

```bash
python -m graphrag_poc.generate --demonstrate
```

Use the same embedding variables as `make eval`.

## Library and service

The Appendix A.4 functions are `build_graph`, `link_entities`, `traverse`, `route`, and `fuse` in `graphrag_poc.library`. The Appendix A.5 service listens on port 8088:

```bash
make service
```

`GET /health` returns the active build id. The guides are [`docs/architecture.md`](docs/architecture.md), [`docs/operations.md`](docs/operations.md), [`docs/integration.md`](docs/integration.md), and [`docs/schema_reference.md`](docs/schema_reference.md). The measured graph result is [`docs/m3_report.md`](docs/m3_report.md). The M4 report is [`docs/m4_report.md`](docs/m4_report.md).

## Milestone

[`docs/milestone_note.md`](docs/milestone_note.md) is the one-page note: what was built, what the baseline fails to connect, and what M2 should classify. The numbers are in [`docs/baseline_report.md`](docs/baseline_report.md).
