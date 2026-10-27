# Schema reference

These are the labels the library reads and writes. Additional properties are allowed.
Current loaded counts need verification after the corrected-data rebuild. The
[requirements mapping](schema_mapping.md) is a draft pending the original requirements
and client confirmation.

## Nodes

| Label | Identity | Properties |
|---|---|---|
| Document | `doc_key` | `title`, `lang`, `doc_type`, `edition` |
| Passage | `node_id` | `text`, `type`, `page_start`, `page_end`, `lang`, `doc_key`, `breadcrumb` |
| Malfunction | `node_id` | `code`, `page_start`, `doc_key` |
| Part | `part_number` | `description`, `nsn`, `node_id`, `doc_key`, `page_start` |
| Model | `name` | `series` |
| Case | `case_id` | `date`, `model`, `symptom`, `cause`, `action`, `frequency` |

`code` is the full malfunction label, such as `4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER`. `node_id` on a part is the parts-list row the part was read from.

A Bolt build also sets `build` on each node. Corpus nodes loaded by `neo4j-admin` have no `build` property. Stats treat those nodes as build `corpus`.

## Edges

| Type | From | To | Rule |
|---|---|---|---|
| IN_DOCUMENT | Passage | Document | the node's `doc_key` |
| PARENT | Passage | Passage | the stored parent id |
| NEXT | Passage | Passage | the next numbered step in the sibling list |
| BOUND_CAUTION | Passage | Passage | a bound caution id |
| REFERS_TO | Passage | Passage | a reference id that is a passage |
| STATES | Malfunction | Passage | the malfunction row |
| HAS_STEP | Malfunction | Passage | one `Step N` span in that row |
| APPLIES_TO | Passage or Malfunction | Model | `applies_to.models` or a model token in the text |
| LISTS | Part | Passage | a parts-list row for that part number |
| CANDIDATE_PART | Malfunction | Part | the fault keyword is in the part description |
| ABOUT | Case | Malfunction | the case error code equals `code` |
| INSTALLED | Case | Part | the case part number |
| ON_MODEL | Case | Model | the case model |
| MENTIONS | Passage | Model or Part | the surface form is written in the passage |

Every edge has `rule`, `derived`, and `weight`. A manual edge also has `doc_key` and `page_start`. A case edge has `case_id` and not a page. `CANDIDATE_PART` stores `keyword` and `description`. `HAS_STEP` stores `step_number` and `step_text`. `MENTIONS` is the only derived edge. Its weight is 0.4.

`MENTIONS` uses deterministic surface-form matching; it does not use a language model.
`CANDIDATE_PART` is a keyword hypothesis, and `INSTALLED` copies synthetic case data.
Neither `derived=false` nor provenance alone proves a confirmed fault-to-part repair.

## Constraints

Uniqueness: `Document.doc_key`, `Passage.node_id`, `Malfunction.node_id`, `Part.part_number`, `Model.name`, `Case.case_id`.

Indexes: `Passage.page_start`, `Malfunction.code`.

## Traversal

Relational and multi-hop walks use explicit `REFERS_TO`, reverse `PARENT`, and
`MENTIONS`/`LISTS` paths, with `STATES` for an explicit malfunction seed. Paragraph
references resolve to actual body/continuation occurrences during a new build.
The bounded route has a three-edge limit; other routes retain a two-edge default.
Procedure walks use `NEXT` and `BOUND_CAUTION`; applicability walks `APPLIES_TO`.
Legacy lookup/troubleshooting may still use keyword candidates and case links.
The cap remains 200 passages. See [traversal preparation](traversal_alignment.md).
