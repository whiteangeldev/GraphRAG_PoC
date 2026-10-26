# GraphRAG PoC

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
| `GENERATION_MODEL` | Chat model for answers. Empty means the answer is the text of the cited passages. |
| `JUDGE_MODEL` | Model that judges required facts and claims. Empty means the quote check. A quote must be an exact span of a cited passage either way. |
| `GENERATION_TEMPERATURE` | `0` during evaluation. |
| `GENERATION_SEED` | `0` during evaluation. |
| `RERANK_ENABLED` | Leave `false` for the reported baseline. |
| `DEMO_PORT` | Demo page port. Default `8080`. |
| `NEO4J_URI` | Bolt URI. Default `bolt://localhost:7687`. The service container uses `bolt://neo4j:7687`. |
| `NEO4J_USER` | Neo4j user. Default `neo4j`. |
| `NEO4J_PASSWORD` | Neo4j password. Default `graphrag-poc`. |
| `GRAPH_BUILD` | Build id the service reads when a request omits one. Default `corpus`. |

## Reproduce the baseline

```bash
make eval
```

That command starts Qdrant, builds the passage and case index when either collection is missing or the dense vector size does not match the configured model, validates the saved node files, checks that 別添52 is in the index, scores `data/eval/questions.jsonl`, and writes `docs/baseline_report.md`. Judgments already in `data/eval/judgments/` are reused when the answer is unchanged.

The cached report was produced with:

```bash
EMBEDDING_BACKEND=fastembed
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
OPENAI_BASE_URL=http://127.0.0.1:8000/v1
GENERATION_MODEL=Qwen3-0.6B
JUDGE_MODEL=Qwen3-0.6B
```

Start that model before `make eval`. With [llama.cpp](https://github.com/ggml-org/llama.cpp), using `Qwen3-0.6B-Q8_0.gguf` from `Qwen/Qwen3-0.6B-GGUF`:

```bash
llama-server -m Qwen3-0.6B-Q8_0.gguf --host 127.0.0.1 --port 8000 -c 8192 --alias Qwen3-0.6B -ngl 99
```

`make eval` uses those defaults unless the variables are already set. A run passes when every metric stays within 0.02 of the cached report (2 percentage points for the share metrics, 0.02 for MRR).

The 20-question gold-passage sample for Sodick's review is [`docs/gold_review_sample.md`](docs/gold_review_sample.md). Every quoted passage is copied from the node file.

M2 classifies every question in [`docs/M2_LIMITATION_ANALYSIS.md`](docs/M2_LIMITATION_ANALYSIS.md). The graph schema is [`docs/M2_GRAPH_SCHEMA.md`](docs/M2_GRAPH_SCHEMA.md). The improved baseline fixes the title reader. The M1 scores from before that fix are in [`docs/m1_baseline_report.md`](docs/m1_baseline_report.md).

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
