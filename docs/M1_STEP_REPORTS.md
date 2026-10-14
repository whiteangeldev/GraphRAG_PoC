# M1 step reports

A step is recorded here only after its exit check passes. Source of the steps: `docs/M1_IMPLEMENTATION_PLAN.md`.

| Step | Status |
|---|---|
| 1. Project skeleton and data contracts | Finished, 13 October 2026 |
| 2. Corpus register | Finished, 13 October 2026 |
| 3. Convert documents to node files | Not started |
| 4. Synthetic service records | Not started |
| 5. Index passages and cases | Not started |
| 6. Hybrid retrieval and cited answers | Not started |
| 7. Demonstration interface | Not started |
| 8. Evaluation set | Not started |
| 9. Evaluation runner and baseline report | Not started |
| 10. Reproduction package and milestone note | Not started |

## Step 1 — Project skeleton and data contracts

Finished 13 October 2026.

The repository now has a Python 3.12 package, pydantic models for every Appendix A.1 node field and every Appendix A.2 case field, ruff, mypy, pytest, `docker-compose.yml` for Qdrant 1.19.2, `.env.example`, and a Makefile. Later commands (`ingest`, `generate-cases`, `index`, `demo`, `eval`) exist as reserved targets and do no work yet.

Node types are `chapter`, `section`, `paragraph`, `procedure`, `step`, `caution`, `table`, `table_row`, `figure`, `boilerplate`, and `case`. Document types are `operation`, `maintenance`, `code_reference`, `parts`, and `other`. Additional fields are preserved. `table` is required when `type` is `table_row` and rejected otherwise. `node_id` must equal `doc_key` or begin with `{doc_key}:`.

### Exit check

| Check | Result |
|---|---|
| `docker compose up` starts Qdrant | Passed. Container `graphrag_poc-qdrant-1` is healthy. `GET /healthz` returned `healthz check passed`. |
| Unit test round-trips one node and one case record | Passed. `tests/test_models.py`: 6 passed. The Appendix A step node and case `C-000123` survive `model_dump_json` / `model_validate_json`, including an extra field on each. |
| mypy clean on the models package | Passed. `mypy src/graphrag_poc/models`: no issues in 3 source files. |
| ruff | Passed. Lint and format check are clean. |

### Environment

The virtualenv is `.venv` on CPython 3.12.15. Homebrew's `python@3.12` on this machine cannot run pip (`platform.mac_ver()` is empty, and `pyexpat` is linked to the wrong `libexpat`), so the interpreter is the standalone CPython installed by `uv python install 3.12`. `make test` and `make typecheck` use `.venv/bin/python`.

## Step 2 — Corpus register

Finished 13 October 2026. The approval file is `docs/corpus_register.md`. PDFs are in `data/corpus/source/`.

The English set is the HMMWV M998 family plus its 6.2 L / 6.5 L engine manual: five documents, 3,670 pages, all with a text layer on the prose and tables that the baseline needs. pdfplumber reads PMCS tables, parts rows, and the engine calibration charts. The parts list has 4,436 unique NSNs. Operator Table 3-1 has 30 malfunction rows, and the engine calibration charts have 600 data rows. Procedures carry warnings, cautions, cross-references, and model applicability.

Diagnostic flowchart pages in TM 9-2320-280-20-1 are graphics. Fault questions will use the operator malfunction table and the engine calibration charts.

The Japanese document is MLIT Public Notice attachment 別添52, 117 pages, with a text layer and character bounding boxes. It is an official notice, so under Copyright Act Article 13, item 2, it is not a copyrighted work.

Conversion does not start until Sodick approves this register.
