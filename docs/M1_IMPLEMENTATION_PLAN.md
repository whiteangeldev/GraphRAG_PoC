# M1 Implementation Plan

Corpus, hybrid-retrieval baseline, and evaluation. This plan covers milestone 1 only. Graph construction, Neo4j, the router, and the integration package belong to later milestones. Node files and retrieval shapes follow Appendix A so those milestones can consume this work unchanged.

Source of truth: Requirements Definition v1.1 and the proposal dated 7 October 2026.

## Decisions

| Topic | Decision |
|---|---|
| Corpus | One US Army equipment family, public domain as a US government work. Start with the HMMWV manuals listed below. Keep the set only if the text-layer probe passes and the size gates pass. |
| Japanese sample | One Japanese technical document of at least 50 pages, processed by the same converter and the same retriever. Licence recorded in the corpus register. |
| Extraction | pdfplumber for text, tables, and bounding boxes. The PDF must have a text layer. |
| Models | OpenAI-compatible endpoint. Defaults: a Qwen3 embedding model and a Qwen3 instruct model. Names and base URL come from environment variables. |
| Reranking | Implemented behind a flag, off in the reported baseline. |
| Vector store | Qdrant with named dense and sparse vectors on the passage collection. A second collection holds synthetic cases, with payload indexes for exact match. |
| Keyword channel | Sparse vectors in Qdrant. Tokenization handles English words and Japanese text without spaces, and normalizes full-width and half-width characters. |
| Fusion | Reciprocal rank fusion, `k = 60`, over the dense list and the sparse list. |
| Generation | Answers are written only from retrieved passages, with citations. Evaluation uses temperature 0 and a fixed seed. |
| Judge | A language model judges required facts and claims and must return a quote. Judgments are cached in the repository so a re-run reproduces the report. |
| Demo | A small FastAPI page: question, answer, citations, and fused ranks. |
| Graph | Schema-ready node files only. No Neo4j in this milestone. |

### Corpus candidates

English set, subject to the probe in Step 2:

| Role | Document |
|---|---|
| Operation | TM 9-2320-280-10, operator's manual |
| Maintenance | One TM 9-2320-280-20 volume that contains numbered procedures, cautions, and troubleshooting tables |
| Code reference | The troubleshooting / fault content of that maintenance set, kept as its own `doc_key` when it is a separate volume |
| Parts | TM 9-2320-280-24P, repair parts and special tools list |

Add a further volume from the same family when the page count, fault-code rows, or part numbers fall short of the gates. Drop the family if the PDFs are scans, and replace it with another US government equipment family that has a text layer and the same four roles. Record the replacement in the corpus register before conversion continues.

Sodick manuals from Scribd stay out of the corpus. A download link is not a licence to process the text or to redistribute derived data.

### Size gates

- At least four English documents and 800 pages.
- At least 300 fault-code or parameter rows.
- At least 500 part numbers.
- Procedures with warnings, cautions, and cross-references.
- Model or variant applicability that can support the applicability questions.
- One Japanese technical document of at least 50 pages.
- At least 2,000 synthetic service records tied to the extracted codes and parts.

## Acceptance

M1 is complete when all of the following hold:

- One command runs the baseline, and every metric in the baseline report reproduces within 2%.
- Node files validate against Appendix A. Every page is represented by at least one node or marked boilerplate.
- The evaluation set has at least 150 questions: 50 relational or multi-hop, 30 lookup, 20 procedure, 20 applicability, 15 unanswerable. At least half use everyday wording. Gold passages on a 20-question sample are ready for Sodick's review.
- The Japanese document is converted and retrievable with the same code.

## Layout

```text
src/graphrag_poc/
  models/        Appendix A node and case models
  ingest/        extract, structure, write JSONL, validate pages
  cases/         seeded generator and rules
  index/         embeddings, sparse vectors, Qdrant loaders
  retrieve/      dense, sparse, reciprocal rank fusion
  generate/      cited answers
  eval/          question set, runner, judge, report
  app/           FastAPI demonstration
docker-compose.yml
Makefile
docs/corpus_register.md
data/nodes/      one JSONL file per document
data/cases/      cases.jsonl and the rules file
data/eval/       questions.jsonl and cached judgments
```

Configuration uses environment variables. Secrets stay out of the code.

## Steps

Complete each step before starting the next. A step is finished only when its exit check passes.

### Step 1 — Project skeleton and data contracts

Create the Python 3.12 package, pydantic models for every Appendix A.1 and A.2 field, ruff, mypy, pytest, `docker-compose.yml` for Qdrant, `.env.example`, and a Makefile with empty targets for the later commands.

The node model fixes the field names in Appendix A. Extra fields are allowed. Node types are `chapter`, `section`, `paragraph`, `procedure`, `step`, `caution`, `table`, `table_row`, `figure`, `boilerplate`, and `case`. Document types are `operation`, `maintenance`, `code_reference`, `parts`, and `other`.

**Exit check.** `docker compose up` starts Qdrant. A unit test round-trips one node and one case record. mypy is clean on the models package.

### Step 2 — Corpus register

Download the candidate PDFs. Probe the first pages of each file with pdfplumber and confirm a text layer, readable tables, and bounding boxes. Count pages, fault-code or parameter rows, part numbers, procedures, cautions, cross-references, and model variants. Select the Japanese document and record its licence.

Write `docs/corpus_register.md` with title, edition, link, page count, structural role, and licence for every file. Send that register for approval before full conversion.

**Exit check.** Every size gate is met on paper, every English PDF has a text layer, and the register is the file that goes to Sodick.

### Step 3 — Convert documents to node files

Parse each approved PDF into one JSONL file. Preserve hierarchy, page ranges, procedure steps, cautions bound to steps, tables, table rows, figures, and cross-references. Fill `elements[].bbox` wherever pdfplumber provides a box. Set `retrievable` to false on boilerplate.

Identifiers stay stable inside the corpus, in the form `doc_key:section:step`. Parent, sibling, caution, and reference links point at real node ids. `applies_to` carries the models, series, and variants stated in the manual. Table rows store headers and cells. Run the Japanese document through this same path after full-width and half-width normalization.

**Exit check.** The validator accepts every file. Every page of every document has a node or is marked boilerplate. A sample of procedures, cautions, code rows, and part rows matches the source pages.

### Step 4 — Synthetic service records

Write a generator whose rules are a committed file. It reads the extracted fault-code rows and part numbers. Each record uses a real error code, a cause and action consistent with that row, a real part number, a model the manual applies to that content, a date, and a frequency. The search text is the concatenation used later for retrieval. The seed is fixed.

**Exit check.** Two runs on the same inputs produce the same `cases.jsonl`. The file contains at least 2,000 records. Every error code and part number in the file exists in the node files.

### Step 5 — Index passages and cases

Embed retrievable nodes with the configured embedding model. Build sparse vectors with a tokenizer that splits English on words and Japanese without requiring spaces. Load passages into Qdrant as one collection with named dense and sparse vectors. Payload includes `node_id`, `doc_key`, `page_start`, `page_end`, `type`, `lang`, `text`, and `breadcrumb`.

Load cases into a second collection. Create payload indexes on `error_codes`, `parts`, and `model` for exact match.

**Exit check.** A known code string, a known part number, and a short Japanese span from the sample document each return the expected node or case from Qdrant.

### Step 6 — Hybrid retrieval and cited answers

Retrieve a dense list and a sparse list. Merge them with reciprocal rank fusion (`k = 60`). Duplicates keep the best rank and the union of channels. Generate the answer from the fused passages only, and attach citations as `node_id` plus page. Unanswerable questions produce a refusal that states what was searched. Temperature is 0 and the seed is fixed. The optional reranker stays off for the reported run.

**Exit check.** A lookup question returns the code row and cites it. A procedure question returns steps in order and includes the bound caution when it is in the retrieved set. A code that does not exist is refused.

### Step 7 — Demonstration interface

Serve a single FastAPI page. The user submits a question and sees the answer, each citation with document and page, and the fused ranking with channel tags. The page reads the same retrieval and generation code as the command-line path.

**Exit check.** The three questions from the Step 6 exit check succeed in the browser against the running stack.

### Step 8 — Evaluation set

Write at least 150 questions in the Appendix C JSONL format. Use real codes, parts, procedures, and models from the node files. Gold `node_ids` must exist. Relational and multi-hop questions cite two or more passages, because those questions are the ones the later graph is meant to improve.

Counts:

| Slice | Minimum |
|---|---|
| Total | 150 |
| Relational or multi-hop | 50 |
| Lookup | 30 |
| Procedure | 20 |
| Applicability | 20 |
| Unanswerable | 15 |
| Everyday wording | half of the set |

Use the remaining questions for troubleshooting and follow-up, following Appendix B. Include a Japanese subset drawn from the Japanese document so retrieval of that document is visible in the report. Each record has `slice`, `expected_action` (`answer`, `refuse`, `clarify`, or `related`), `gold`, `required_facts`, `forbidden_facts`, and notes naming the author.

**Exit check.** A script checks the counts, resolves every gold node id, and rejects a question whose required fact cannot be found in a gold passage.

### Step 9 — Evaluation runner and baseline report

Score the full set with the baseline from Step 6. Compute hit@10, MRR, evidence recall, required-fact recall, claim precision, and action accuracy, overall and per question type. Required-fact recall and claim precision use the language-model judge and a quote from the cited passage. Store each judgment in `data/eval/judgments/`. A later run reuses the cache.

Write the baseline report with the per-type table, the model names, the fusion parameters, and a short note on the relational questions the baseline misses.

**Exit check.** A second run with the cache reproduces every metric exactly. The report lists every question type that has questions.

### Step 10 — Reproduction package and milestone note

`make eval` starts Qdrant, builds any missing index, runs the evaluation, and writes the report. The README documents the environment variables, the corpus register, the one-command path, and how to open the demo. Record a five-minute demonstration: one lookup, one procedure that includes a caution, one relational question, and one refusal. Write the one-page milestone note: what was built, what the baseline fails to connect, and what M2 should classify.

**Exit check.** A clean checkout plus the documented model endpoint reproduces the cached report within 2% on every metric. The node validator passes. The Japanese sample is present in the index and appears in the report.

## M1 deliverables

| Id | Artifact |
|---|---|
| D1.1 | Corpus register, source PDFs, node files, synthetic cases, generator, and rules |
| D1.2 | Baseline code, Docker Compose, README, five-minute recording |
| D1.3 | Evaluation set, runner, cached judgments, baseline report |
| D1.4 | One-page milestone note |

## Explicitly deferred

These are required by the engagement and are out of this plan:

- Failure classification and the graph schema proposal (M2).
- Neo4j, CSV import, entity linking, traversal, router, and graph fusion (M3).
- The installable library, Appendix A.4 service, CI handover package, and handover sessions (M4).
