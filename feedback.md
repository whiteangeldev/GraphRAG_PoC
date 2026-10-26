# GraphRAG PoC (freelancer) — M1/M2 review, 20 Oct 2026 (revised; code checked 23 Oct)

Reviewed: D:\AI\sodick-chatbot-v2\Grpah_RAG (Requirements v1.1, proposal 7 Oct 2026, GraphRAG_PoC/docs, corpus PDFs). Code delivered 23 Oct to OneDrive …\Hypervisor_Evaluation\Projects\Grpah_RAG\GraphRAG_PoC (src, tests, data in "data" + "data (1)").

Context (from Ruman): scope was reduced informally after the budget cut; nothing written. The freelancer submitted M1+M2 for approval; on approval he starts M3+M4. Review judged against a reduced-scope PoC, not the full Req v1.1.

## Verdict
Approve M1/M2 with conditions. The code is clean and reproducible. Three issues would make the M3 result meaningless, and two code bugs should be fixed with them.

## Code check (23 Oct)
Verified by running it:
- Ingest regenerates all 6 node files byte-identical to the delivered ones; the node validator passes.
- The synthetic case generator and the question builder regenerate cases.jsonl and questions.jsonl byte-identical.
- 45 of 46 tests pass (the one failure was a doc file not copied for the run). ruff is clean; mypy --strict is clean on 43 files.
- The baseline report numbers match the raw results.jsonl exactly; failure-class counts match failure_assignments.jsonl.

Not verified: rerunning retrieval and LLM scores. That needs the MiniLM embedding model and Qwen3-0.6B, and HuggingFace is blocked from the review sandbox. Run `make eval` on dev-all to close this.

Code findings:
- The "answerer" is mostly rules. Regex reads the malfunction title from the question and refuses before the LLM is called if that string is not in the passages. With no model set, the answer is just the passage text. Citations fall back to the rule's picks if the LLM does not cite. This is tuned to his own question templates and will not carry over to Sodick questions.
- The reranker is not implemented. search.py says RERANK_ENABLED is not applied, although the plan said it was behind a flag.
- All 157 questions come from string templates in eval/build.py. "Everyday wording" is `index % 2 == 0`, i.e. every other question. Every question carries the note "written by incredible9120".
- The relational gold part is the first parts-list row whose description contains the keyword from rules.json. This confirms the circular test.
- Parts table bug: 888 of 8,213 parts rows (11%) have the CAGE code in the PART NUMBER column, with the real part number pushed into the description. The most-used "part" in the synthetic cases (81 cases) is 7X677, a CAGE code, shown as "WASHER, FLAT".
- Synthetic cases are thin: only 30 malfunction codes. Cause is "Other causes" in 609 cases and a bare number ("11", "15", "16", "18") in 268 cases. Action is "Notify unit maintenance" in 574 cases.
- Front-matter step-grouping bug is small: 56 of ~9,800 steps. It affects only 2 of 22 procedure questions (procedure-0001 and -0003).

## Must fix before M3
1. Circular relational test: build relational gold from relations the manuals state (Table 3-1 para refs → -20 maintenance task → parts that task lists → -24P). Otherwise report the keyword slice separately and do not count it toward the targets.
2. Questions: rewrite the relational and multi-hop questions (~50) in real user wording, with no pasted titles and no keyword hints. Drop procedure-0001 and -0003.
3. Baseline: a realistic generator (Qwen3-8B or larger, or a hosted model, since the corpus is public) and a separate judge. Remove the regex title gate so the LLM answers and cites.
4. Fix the parts column shift (CAGE vs part number), then regenerate cases and questions.
5. Make synthetic cases usable: real cause/action text, no numeric causes, valid part numbers.

## Can relax for the reduced scope
- 300-row corpus gate met loosely (30 real malfunction rows), acceptable once item 1 is fixed.
- Schema names differ from Appendix A.3: a one-page mapping in M4 is enough. Term/SAME_AS synonyms are nice to have.
- M2 report shorter than asked; no per-class expected gain; unanswerable-refusal fix not applied; reranker missing.

## Put in writing now
- Short scope note: what was dropped or relaxed versus Req v1.1.
- M3 targets: which slices count toward the +15 / +10 point targets after item 1.
- The repo should be in Sodick's GitLab with history (the delivery was a OneDrive copy with the data split into "data" and "data (1)").

## Good points
Clean, typed, tested code; byte-reproducible pipeline; correct licence handling; honest reports whose numbers match the raw data; Japanese sample; provenance on every edge; 5-minute demo video.