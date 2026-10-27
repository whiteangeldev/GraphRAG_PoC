# Review status, evidence limits and source conflicts

Choice B is accepted in the [client decision](decision_record.md). Full repair chains
are not required. The first 25 candidates are accepted with catalogue corrections;
25 additional cases are being prepared for client review before M3. The minimum remains
50 and the +15/+10 thresholds are unchanged. Preparation is not approval or a benchmark
freeze. See `data/eval/review_audit.json` for the exact case/span/page inventory.

## Independent evidence and new cases

The accepted batch covers operator troubleshooting references and maintenance/catalogue
identity. Catalogue required facts now include an NSN or description/effectivity found
only in the selected catalogue row, so a part number copied from maintenance alone
cannot satisfy the question. The five flagged questions explicitly request NSNs.

The second batch adds unused operator source/reference pairs and stored task references
in both maintenance volumes. It uses different evidence cases, not paraphrases of the
first batch. Each selected reference, instruction and required fact is pinned to node
IDs, exact text hashes, physical PDF pages and selected quotes. Exact quotations are
checked after whitespace normalization on the PDF; no fuzzy correction is used.

These are selected bounded relationships, not a random sample or 50 independent
failures. Question counts must not be presented as counts of unique faults or repairs.

## Maintenance references and table-of-contents aliases

The parsed maintenance manuals sometimes assign `doc:paragraph` to a table-of-contents
entry, with the real procedure stored at a numbered occurrence such as
`doc:paragraph:2`. New gold uses the actual procedure and its instruction descendants.
Validation requires the correct document, paragraph heading and procedure type; a
resolving TOC alias is insufficient. Some procedure continuations also have occurrence
suffixes. The physical source pages and limitations identify the selected occurrence.

Stored cross-reference traversal must be aligned with these actual procedure roots
before M3. Correcting gold does not itself repair the loaded graph. Graphic diagnostic
content remains deferred; new maintenance cases use selected textual instructions.

## Excluded HVAC reference

The operator HVAC row at `tm280_10:table:3-1:7:r30`, PDF page 287, says
`Service HVAC filters (para. 3-28).` Its target is interior bulb replacement on page 318.
The client explicitly excluded this mismatched link. It is not repaired by guessing a
replacement paragraph. A separate control-operation reference from that row to 2-61 is
valid source material and is proposed as a new case, pending review.

## Water-pump applicability conflict

Maintenance page 156 names 251-591 for 6.2L and 12534772 for 6.5L and 6.5L detuned.
Catalogue page 133 describes 251-591 as 6.2 and 6.5 detuned, with 1990-engine-and-above
effectivity, and 12534772 as 6.5 litre. The client accepted only the bounded 1990-or-later
6.2L and non-detuned 6.5L questions. No 6.5L-detuned applicability is claimed.

## Catalogue identity and remaining work

Some numbers have several catalogue occurrences, handedness, UOC and effectivity
restrictions. Cable brackets retain `USBL EFF 44825 AND ABOVE`; steering covers retain
the hub, vehicle-group and position conditions and the serviceable-cover exception.
Number identity and a row description do not prove universal fit or a diagnosis.

Review the new 25, incorporate changes and fill any rejected-case gap. Only then freeze
the target set, complete traversal validation, and run the fresh comparable measurements.
The active historical keyword gold is still excluded from acceptance. Final delivery
also requires the M4 schema mapping and Sodick GitLab history.
