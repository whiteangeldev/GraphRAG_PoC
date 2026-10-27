# M2 graph schema proposal

> Historical design proposal. Its model-extraction wording and title-reader discussion
> describe the earlier design. Current `MENTIONS` is deterministic surface matching;
> see [the implemented schema](schema_reference.md) and [current M4 status](m4_report.md).

Proposed schema for M3. It uses the node files and case records already produced in M1. Extra properties are allowed. Names below are the ones M3 should create. A traversal reads them; it does not invent a second copy of the passage text.

Provenance is required on every edge: `doc_key` and `page_start` for an edge that comes from a manual, or `case_id` for an edge that comes from a service case. `rule` names the deterministic rule. `derived` is true only when a model extracted the edge from prose, and those edges carry a lower weight until someone reviews them.

## Node types

| Label | Source | Identity | Properties |
|---|---|---|---|
| `Document` | One node file | `doc_key` | `title`, `lang`, `doc_type`, `edition` |
| `Passage` | Every retrievable Appendix A node | `node_id` | `type`, `text`, `page_start`, `page_end`, `lang`, `breadcrumb` |
| `Malfunction` | A `table_row` whose header is `MALFUNCTION` | `node_id` of that row | `code` (the full Table 3-1 label), `page_start` |
| `Part` | A `table_row` whose header is `PART NUMBER` | part number | `description`, `nsn`, `node_id` of one source row |
| `Model` | A model token stated in a passage or case | the token, such as `M998` | `series` when the manual groups it |
| `Case` | One Appendix A.2 record | `case_id` | `date`, `symptom`, `cause`, `action`, `frequency` |

`Passage` keeps the text that retrieval already cites. `Malfunction`, `Part`, `Model`, and `Case` are the entities a question names. An entity points at the passage it was read from; it does not replace that passage.

## Edge types

| Type | From | To | Source | Rule |
|---|---|---|---|---|
| `IN_DOCUMENT` | Passage | Document | node file | `doc_key` of the node |
| `PARENT` | Passage | Passage | node file `parent` | the parent id already stored |
| `NEXT` | Passage | Passage | node file `siblings`, in step order | numbered steps that share a task prefix, in step-number order |
| `BOUND_CAUTION` | Passage | Passage | node file `bound_cautions` | the caution id must be a caution node |
| `REFERS_TO` | Passage | Passage | node file `references` | the reference id |
| `STATES` | Malfunction | Passage | the malfunction table row | the row's own `node_id` |
| `HAS_STEP` | Malfunction | Passage | the same table row | each `Step N` span inside that row |
| `APPLIES_TO` | Passage or Malfunction | Model | `applies_to.models`, or a model token in the passage text | deterministic when the token is in the text or in `applies_to` |
| `LISTS` | Part | Passage | the parts-list row | the row's own `node_id` |
| `CANDIDATE_PART` | Malfunction | Part | Table 3-1 group keyword and a part description | the keyword map in `data/cases/rules.json`; `derived` is false because the rule is committed |
| `ABOUT` | Case | Malfunction | case `error_codes` | exact match to the malfunction label |
| `INSTALLED` | Case | Part | case `parts` | exact match to the part number |
| `ON_MODEL` | Case | Model | case `model` | the model field |
| `MENTIONS` | Passage | Model or Part | prose | model extraction only; `derived` true; lower weight |

`PARENT`, `NEXT`, `BOUND_CAUTION`, and `REFERS_TO` are document structure. `STATES`, `HAS_STEP`, `APPLIES_TO`, `LISTS`, and `CANDIDATE_PART` come from tables. `ABOUT`, `INSTALLED`, and `ON_MODEL` come from case records. Only `MENTIONS` is model extraction.

`CANDIDATE_PART` is the edge the baseline cannot retrieve. The keyword is a group word such as `NOZZLE` or `TRANSMISSION`, not a guarantee that the part belongs to that repair. The edge stays, with the keyword and the part description stored on it, so a reviewer can see why it was drawn.

## What a traversal is allowed to return

From the passages already in the top 10:

- `NEXT` and `BOUND_CAUTION` add the rest of a procedure and its warning.
- `CANDIDATE_PART` and `LISTS` add the parts-list row for a malfunction that was already found.
- `APPLIES_TO` adds passages that name the model in the question.
- `ABOUT` and `INSTALLED` add cases for a code or a part the question names.
- `PARENT` adds a section when a child was found and the question is about that section.

The traversal returns passage ids, the path, and the provenance. Those ids join the same reciprocal rank fusion as the dense and sparse lists. M3 chooses the weight. This proposal does not set that weight.

## What the graph is not asked to do

A refusal that happens after the right passage was retrieved is a title-reader bug. It is fixed in the improved baseline and does not need an edge.

A question with no gold passage that still receives an answer is a generator policy. The graph's related-material behaviour belongs to M3 and is not a substitute for that policy.

A gold passage ranked 11 to 20 is still a retrieval miss at hit@10. Moving the cutoff would change the metric. A reranker could reorder those hits. That is outside this schema.
