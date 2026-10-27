# Agreed Choice B scope and acceptance basis

Choice B was accepted in feedback relayed on 27 October 2026. See the
[decision record](decision_record.md) and [feedback text](client_feedback_2026_10_27.md).
Full repair chains are not required. The first 25 candidates are accepted with the
specified catalogue corrections; the next 25 must be reviewed before M3.

## Included scope

- Explicit operator troubleshooting reference to a paragraph and selected instruction.
- Explicit maintenance part number to the matching catalogue row, with a required NSN
  or catalogue-only description fact. Identity is not a diagnosis or universal fit.
- Explicit maintenance task reference to a paragraph and selected textual instruction
  in the -20-1 and -20-2 manuals.

Source evidence retains exact quotes, node text hashes, physical PDF pages, typed part
number equality, actual procedure-root resolution and per-case applicability limits.
Repeated wording of the same source/reference case does not increase the question count.

## Acceptance rules

| Rule | Agreed or retained basis |
|---|---|
| Target count | 50; all reviewed and frozen before the M3 run |
| Evidence recall gain | At least +15 percentage points |
| Required-fact recall gain | At least +10 percentage points |
| Comparability | Same frozen target questions and model configuration for baseline and graph |
| Evidence cutoff | First 10 fused passages, unchanged |
| Per-type regression | Existing no-more-than-1-point loss rule retained; not amended in this feedback |
| Lookup p95 added latency | Existing 100 ms limit retained; not amended in this feedback |
| Keyword-derived gold | Remains excluded |
| Final package | Fresh results, M4 schema mapping and Sodick GitLab delivery with history |

The 50 prepared target records are separate from the active 155-question historical
benchmark. Scope approval does not silently replace those records or their reports.
The supplemental non-target question types may be retained for regression/latency
checks, clearly separated from the frozen-50 target results. Their treatment must be
made explicit when wiring the final scoring run; no lookup-latency pass can be inferred
from a target-only set that contains no lookup questions.

## Accepted limits and deferrals

Synonym/Term nodes, reranking and graphic troubleshooting extraction are deferred.
The Japanese sample demonstrates pipeline coverage only. Synthetic service cases are
demo data, not observed outcomes. Retain the bounded 1990-or-later 6.2L and non-detuned
6.5L water-pump questions; exclude 6.5L-detuned applicability. Exclude the incorrect
HVAC-to-3-28 reference. Catalogue handedness, UOC, serial effectivity and serviceable-part
exceptions remain limitations rather than universal replacement recommendations.

The [M4 schema mapping](../schema_mapping.md) records implemented labels and interfaces.
The original Requirements v1.1 document is absent locally; this is not a complete
clause-by-clause certification of an unavailable document. Final client acceptance,
the delivered GitLab commit and handover evidence remain to be recorded.
