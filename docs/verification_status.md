# Current verification — 27 October 2026

The local engineering checks pass. M3 results and final M4 acceptance are still
pending. No LLM inference, benchmark activation or scored evaluation was run during
this recheck. Existing answer/judge smoke results and historical scores were retained.

| Check | Observed result |
|---|---|
| Full test suite | 280 passed, no skips or warnings |
| Final CSV-export correction | All 28 focused storage/library/API tests passed after that change; these overlap the full suite |
| Lint and formatting | Passed; 143 Python files formatted |
| Type checking | Passed on 74 source files |
| Dependency checks | Host environment and rebuilt Docker service passed `pip check` |
| Source/PDF review | 50 cases, 146 excerpts across 76 physical pages validated; 25 accepted, 25 pending |
| Source-seeded path audit | All 50 cases can reach their required source facts; no missing paths within the configured bounds |
| Qdrant payload audit | All 22,956 passages and 2,000 cases match source payloads; no missing or mismatched records; search checks passed |
| Production Neo4j rebuild | Passed deterministic builds, loaded counts, orphan and provenance checks; 3,346 references and 12,418 mentions |
| Running services | Qdrant, Neo4j and graph service healthy |
| Installed Docker package | All 75 Python source files match the workspace code |
| Real HTTP checks | Corpus instruction path/provenance, punctuated part number, fixture build/link/traverse, rejected collision and CSV export passed |
| Runtime cleanup | HTTP fixture removed, default service build restored to `corpus`, corpus statistics unchanged |
| Model endpoint probe | `qwen3:8b` and `qwen3:14b` ready; no inference requested |
| Evaluation gates | Direct baseline, reproduction and M3 commands stop at pending acceptance before runtime work |
| Benchmark preservation | Active 155 and prepared 50 question digests unchanged; no frozen IDs or approval invented |
| Staging plan | 50 targets plus 105 unchanged controls; record validation clean, readiness false as required |

The full test suite uses mocked model responses for answer/judge logic. Source-seeded
path checks start from known evidence nodes; they do not measure retrieval from a user
question, generator quality, hit@10 or either acceptance gain.

This review found and corrected issues beyond the earlier passing tests:

- Direct Python scoring could bypass the Makefile approval check. Every scoring entry
  point now checks acceptance before model/index work; incomplete baseline metrics fail
  closed instead of omitting comparison gates.
- Standard Ollama and Hugging Face Qwen aliases could evade size or independent-model
  checks. Those aliases are now recognized consistently.
- Named graph builds could overwrite another build's globally unique keys. Conflicts
  are rejected, replacements are atomic, and cross-build traversal/frame paths are
  excluded. Named builds require globally disjoint business keys; overlapping snapshots
  require a separate database or a future composite-key implementation.
- Reference candidates were capped before relevance ordering. Ordering now happens
  before the unique-passage cap, and public paths retain every edge's provenance.
- Thirteen catalogue part-number spellings with decimal or parenthesis suffixes were
  not matchable. Literal linking and surface mentions now support them without matching
  shorter number prefixes; all 5,088 catalogue identities pass the literal-link check.
- A CSV export could switch the active database build. It now leaves that build intact;
  rejected builds return HTTP 400 without switching it.

The previous database dump and import CSVs are retained locally under
`data/graph/backups/graphrag-pre-verification-w913_860/`, excluded from Git. Its
[previous graph report](historical/graph_build_report_before_explicit_refs_2026_10_27.md)
is preserved separately. Current counts are in the [graph report](graph_build_report.md).
Machine-readable path and runtime checks are in
[path_audit.json](../data/eval/staging/path_audit.json) and
[runtime_audit.json](../data/eval/staging/runtime_audit.json).

| Remaining acceptance/delivery work | Current status |
|---|---|
| Additional 25 and final freeze | Awaiting client review; the first 25 remain accepted |
| Fresh same-model baseline and graph runs | Not run; approval gate intentionally blocks them |
| +15 evidence / +10 fact gains, regression and latency gates | Unmeasured for the new benchmark; no pass claimed |
| M4 schema mapping | Prepared; original Requirements v1.1 / complete Appendix A.3 absent locally, so complete compliance is not certified |
| GitLab delivery with history | Not delivered; local history has 13 commits, only a GitHub remote is configured, and current changes are uncommitted |
| Final demonstration and handover | No completed acceptance demonstration or attended handover recorded |

No additional code failure remains in the checks above. Passing them does not establish
the pending acceptance measurements or certify every requirement in an unavailable
requirements document. Recheck affected artifacts if the client requests data changes.
