# M4 schema mapping for Choice B

Status: implementation mapping prepared for the client-approved Choice B scope;
final acceptance pending. The original Requirements v1.1
and complete Appendix A.3 are absent from this repository. This page maps the names
and concepts described in the existing implementation documents; it is not a certified
complete mapping of the client's requirements.

| Requirement name or concept recorded locally | Implementation | Qualification |
|---|---|---|
| `ErrorCode` | `Malfunction`, keyed by source row `node_id`, with full malfunction label in `code` | Public manual labels are not normalized plant error codes |
| `NEXT_STEP` | `NEXT` between `Passage` nodes | Ordered numbered sibling steps, not a complete diagnostic decision tree |
| Explicit troubleshooting/task paragraph reference | `REFERS_TO` resolves stored paragraph IDs to body occurrences and compatible continuations; reverse `PARENT` reaches instructions | Same-document resolver skips TOC occurrences, conflicting headings and unresolved paragraphs; bounded traversal uses at most three actual edges |
| Maintenance part number to catalogue identity | Exact `MENTIONS` through `Part` and `LISTS`, or direct part seeds | Returns all matching catalogue rows within the cap; catalogue-specific NSN/description gold does not establish universal fit or a repair diagnosis |
| Source content and provenance | `Document`, `Passage`, `IN_DOCUMENT`, `PARENT`, `STATES`, `LISTS` | Source node IDs, document keys and physical pages remain available |
| Procedure cautions and references | `BOUND_CAUTION`, `REFERS_TO`, `HAS_STEP` | Explicit reference resolution and instruction traversal are implemented; they do not prove complete repair chains |
| Parts and applicability | `Part`, `Model`, `APPLIES_TO` | Part identity and surface model mentions do not prove universal fit |
| Service histories | `Case`, `ABOUT`, `INSTALLED`, `ON_MODEL` | Public PoC cases are synthetic, not observed repair outcomes |
| Fault-to-part candidate | `CANDIDATE_PART` | Keyword heuristic; excluded as an independent gold source |
| Text entity mentions | `MENTIONS` | Deterministic surface forms; `derived=true`, weight 0.4; not LLM extraction |
| `Term` / `SAME_AS` | No dedicated graph label/edge | Deferral accepted in the Choice B feedback |

The [schema reference](schema_reference.md) lists actual labels, keys and edges. The
library returns passage IDs and paths for the caller to join to its passage store.
`build_graph`, `link_entities`, `traverse`, `route`, and `fuse` provide the locally
documented Appendix A.4 interface; the HTTP routes are in the
[integration guide](integration.md).

The bounded relational/multi-hop route seeds from retrieved passages and exact entities,
excludes the keyword `CANDIDATE_PART` frame, and keeps the 200-passage cap and ten-passage
generator evidence limit. Other routes retain their two-hop default. These changes
have been applied to the rebuilt local corpus graph. Current engineering verification
is recorded in [the verification record](verification_status.md). Named builds must
use globally disjoint business keys; conflicting writes are rejected atomically.
See
[traversal preparation](traversal_alignment.md).

`make bounded-plan` prepares a report for 50 bounded targets plus the 105 retained
controls, without activation or model calls. Twenty-five targets and the final freeze
remain pending. The contract lists 50 target IDs, while its full-run digest must freeze
the same ordered 155 records for baseline and graph.

Before full requirements certification, compare every row with the actual Appendix A.3,
add omitted requirements, agree any normalization or adapter needed for Sodick data, and record the reviewer,
requirements version/date and accepted exceptions in the delivery record. Do not infer
approval of label differences from the historical reports.
