# M1 step reports

A step is recorded here only after its exit check passes. Source of the steps: `docs/M1_IMPLEMENTATION_PLAN.md`.

| Step | Status |
|---|---|
| 1. Project skeleton and data contracts | Finished, 13 October 2026 |
| 2. Corpus register | Finished, 13 October 2026 |
| 3. Convert documents to node files | Finished, 14 October 2026 |
| 4. Synthetic service records | Finished, 14 October 2026 |
| 5. Index passages and cases | Finished, 14 October 2026 |
| 6. Hybrid retrieval and cited answers | Finished, 14 October 2026 |
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

Conversion does not start until Sodick approves this register. Approval was given on 14 October 2026.

## Step 3 — Convert documents to node files

Finished 14 October 2026. `make ingest` writes one JSONL file per approved PDF under `data/nodes/`. The six files hold 26,706 nodes.

Each document goes through the same converter. Japanese text is normalized with NFKC first, so full-width digits and letters match the half-width forms. A node keeps the pdfplumber bounding box of every line it came from. Headers, contents leaders, and pages with no body text are boilerplate and are not retrievable. Procedure steps, warnings, and cautions are separate nodes. A warning or caution is bound to the step that follows it. Table rows carry headers and cells. Part rows use item, SMR code, NSN, CAGE, part number, description, usable-on code, and quantity. Parent, sibling, caution, and reference links point at node ids in the same file. `applies_to` records M998-series models and pump models stated in the passage.

| File | Nodes | Steps | Cautions | Table rows |
|---|---:|---:|---:|---:|
| `tm280_10.jsonl` | 2,327 | 1,299 | 159 | 41 |
| `tm280_20_2.jsonl` | 8,412 | 6,111 | 88 | 17 |
| `tm280_20_1.jsonl` | 2,186 | 858 | 85 | 47 |
| `tm280_24p_1.jsonl` | 10,398 | 59 | 0 | 8,213 |
| `tm2815_34.jsonl` | 2,342 | 1,447 | 50 | 258 |
| `mlit_b052.jsonl` | 1,041 | 49 | 0 | 0 |

A parts row keeps the description and usable-on code that sit on the same line as the item number. Table 3-1 keeps a wrapped title on the malfunction row, and the model list follows the group printed in that table: the M998 series, winch models, armament carriers, or ambulances. Specification grids such as the belt-tension table are table rows. Spellings such as UGHT remain as they are in the PDF text layer. Flowchart pages in volume 1 stay boilerplate, as agreed at approval, because the flowchart artwork is not text.

### Exit check

| Check | Result |
|---|---|
| Validator accepts every file | Passed. Every node matches Appendix A. Parent, sibling, caution, and reference ids exist. Bound cautions are caution nodes. |
| Every page has a node or is boilerplate | Passed. Pages with body text have an element on that page. Pages with no body text have a boilerplate node. |
| Sample matches the source pages | Passed. Operator paragraph 2-32 keeps the dusty-area procedure and the 12 psi step. The oil-cooler task binds "Do not drain oil when engine is hot" to the disconnect step. Table 3-1 row "ENGINE FAILS TO CRANK" includes the neutral-lever test. Calibration row 150 / WOT includes 28 min. Parts row 5340012564517 keeps part 5596028. The Japanese file has a section for 適用範囲 with bounding boxes. |

## Step 4 — Synthetic service records

Finished 14 October 2026. `make generate-cases` reads `data/cases/rules.json` and writes `data/cases/cases.jsonl`.

The rules file fixes the seed, the date range, the frequency range, the search-text order, and the part-description keywords. These manuals have no separate fault-code column, so the error code is the full Table 3-1 malfunction label, including a wrapped second line. The cause and the action are one step of that same row. The part number is a PART NUMBER whose description matches that malfunction. The model comes from the Table 3-1 group: series, winch, armament carrier, or ambulance.

The file has 2,000 cases. Two runs with the same rules and node files produce the same file.

### Exit check

| Check | Result |
|---|---|
| Two runs match | Passed. A second generation equals the written `cases.jsonl`. |
| At least 2,000 records | Passed. 2,000 records, `C-000001` through `C-002000`. |
| Every error code and part number exists in the node files | Passed. Each error code is a Table 3-1 cell. Each part number is a PART NUMBER cell. |

## Step 5 — Index passages and cases

Finished 14 October 2026. `make index` loads retrievable nodes into the Qdrant collection `passages` and the service cases into `cases`.

Each passage has a named dense vector and a named sparse vector. The dense vector is the configured embedding model. This run used the local multilingual model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` because no Qwen endpoint was set. `EMBEDDING_BACKEND=openai` still calls the OpenAI-compatible endpoint when that server is available. The sparse vector is term presence after full-width folding. English and part numbers split on words. Japanese text, which has no spaces, is indexed as the short phrase and as overlapping character pairs. Qdrant applies inverse document frequency at search time. The passage payload is `node_id`, `doc_key`, `page_start`, `page_end`, `type`, `lang`, `text`, and `breadcrumb`. Boilerplate is not indexed. 22,952 passages were loaded.

Cases keep a sparse vector of `search_text` and keyword indexes on `error_codes`, `parts`, and `model`. 2,000 cases were loaded.

### Exit check

| Check | Result |
|---|---|
| A known code string returns the expected passage | Passed. `4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER` returns `tm280_10:m4`, whose text is that label. The same string returns the matching case by exact match. |
| A known part number returns the expected passage | Passed. The sample case's part number is in the top passage hits, and the case filter returns that case. |
| A short Japanese span returns the sample passage | Passed. `適用範囲` returns a Japanese passage from `mlit_b052` that contains that span. |

## Step 6 — Hybrid retrieval and cited answers

Finished 14 October 2026. A question retrieves a dense list and a sparse list, then merges them with reciprocal rank fusion, `k = 60`. A passage that appears in both lists keeps its best rank and both channel names. The answer is written only from those fused passages. Each citation is a `node_id` and the passage page. Temperature is 0 and the seed is 0. The reranker stays off.

`python -m graphrag_poc.generate --check` asks the three exit questions. With no generation model configured, the answer is the text of the matching passages rather than a separate model call. `GENERATION_MODEL` switches that call to the OpenAI-compatible endpoint with the same temperature and seed.

### Exit check

| Check | Result |
|---|---|
| A lookup question returns the code row and cites it | Passed. The charging question cites `tm280_10:table:3-1:2:r4`, page 281, and the answer is that row, including the battery-cable and alternator-belt steps. |
| A procedure question returns steps in order and includes the bound caution | Passed. The oil-cooler question returns the hot-oil warning, then step 1 (disconnect) and step 3 (connect), all from task 3-8 on page 32. |
| A code that does not exist is refused | Passed. `99. ZZZNOTACODE FAILURE` is refused, and the refusal states the question that was searched. |
