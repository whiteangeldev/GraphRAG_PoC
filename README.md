# GraphRAG PoC

Milestone 1 baseline: hybrid retrieval over an approved public corpus, cited answers, and a fixed evaluation. Graph construction is a later milestone.

## Corpus

The approved list, licences, and page counts are in [`docs/corpus_register.md`](docs/corpus_register.md). Source PDFs are in `data/corpus/source/`. Node files are in `data/nodes/`. Synthetic service cases are in `data/cases/`.

## Setup

Python 3.12. From the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

Qdrant runs from Docker Compose (`qdrant/qdrant:v1.19.2` on port 6333).

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

## Reproduce the baseline

```bash
make eval
```

That command starts Qdrant, builds the passage and case index when either collection is missing or the dense vector size does not match the configured model, validates the saved node files, checks that 別添52 is in the index, scores `data/eval/questions.jsonl`, and writes `docs/baseline_report.md`. Judgments already in `data/eval/judgments/` are reused when the answer is unchanged.

The cached report was produced with:

```bash
EMBEDDING_BACKEND=fastembed
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

`GENERATION_MODEL` and `JUDGE_MODEL` were empty. `make eval` uses those embedding defaults unless the variables are already set. A run passes when every metric stays within 0.02 of the cached report (2 percentage points for the share metrics, 0.02 for MRR).

## Demo

```bash
make demo
```

Open http://127.0.0.1:8080. The page shows the answer, each citation with document and page, and the fused ranking.

The five-minute demonstration is four questions: one lookup, one procedure that includes the hot-oil caution, one relational question, and one refusal. The questions, the recorded answers, and what to say about each are in [`docs/demonstration.md`](docs/demonstration.md). Regenerate that file with:

```bash
python -m graphrag_poc.generate --demonstrate
```

Use the same embedding variables as `make eval`.

## Milestone

[`docs/milestone_note.md`](docs/milestone_note.md) is the one-page note: what was built, what the baseline fails to connect, and what M2 should classify. The numbers are in [`docs/baseline_report.md`](docs/baseline_report.md).
