# Source relation review candidates

26 October 2026. These links were selected from explicit source statements, independently of graph keyword rules. Every quote was checked against its saved node and source PDF page; node text hashes detect later changes. Client review remains pending.

Eight maintenance-to-catalogue links and two fault-to-operator references are recorded. None is a complete approved fault → operator instruction → maintenance task → catalogue part chain. Do not count them or the existing 50 keyword questions toward M3 acceptance targets. The +15/+10 thresholds and 50-question minimum remain unchanged.

The water-pump sources disagree about 6.5L detuned applicability. Preserve that conflict; do not turn it into an unqualified gold answer.

Validate with `make gold-check`. The graph builder does not read this manifest.
The corrected-data keyword snapshot is retained separately in
`data/eval/keyword_exploratory.jsonl`. Those 50 questions remain explicitly excluded from
acceptance in the provisional main set. Their wording has now been rewritten, but their
keyword-derived gold remains unchanged and ineligible for acceptance.
Both `make eval` and `make m3` check acceptance readiness before starting stores or models.

## water-pump-62

The installation caution names 251-591 for a 6.2L engine.

- Source: `tm280_20_2:3-76.1:3:step-c:2`, PDF page 156. Ensure water pump P/N 251-591 is used on 6.2L engines, or damage to equipment will result.
- Target: `tm280_24p_1:parts:r671`, PDF page 133. 251-591
- Limitation: Only a maintenance-to-catalogue link; no fault-to-maintenance link established.
- Limitation: Do not extend this to 6.5L detuned engines: the maintenance caution and catalogue descriptions differ.

## water-pump-65

The caution names 12534772; the catalogue lists that cooling-system pump.

- Source: `tm280_20_2:3-76.1:3:step-c:2`, PDF page 156. Ensure water pump P/N 12534772 is used on 6.5L and 6.5L detuned engines, or damage to equipment will result.
- Target: `tm280_24p_1:parts:r672`, PDF page 133. 12534772
- Limitation: Only a maintenance-to-catalogue link; no fault-to-maintenance link established.
- Limitation: 6.5L detuned applicability conflicts with the description of 251-591 in the catalogue; client must resolve it before an applicability question.

## fuel-tank

The note selects steps 8.1–8.5 for tank 12460105; the catalogue lists that tank.

- Source: `tm280_20_2:3-24:6:step-c:2:step-8:2`, PDF page 62. Perform steps 8.1 through 8.5 for vehicles with fuel tank P/N 12460105.
- Target: `tm280_24p_1:parts:r415`, PDF page 95. 12460105
- Limitation: Only a maintenance-to-catalogue link; no fault-to-maintenance link established.

## clamp-right

Installation explicitly requires bracket 12342965; the catalogue lists the right-hand mounting bracket.

- Source: `tm280_20_2:7-23:2:step-b:3:2`, PDF page 771. Ensure clamp bracket (P/N 12342965) is installed on vehicle.
- Target: `tm280_24p_1:parts:r3980`, PDF page 581. 12342965
- Limitation: Only a maintenance-to-catalogue link; no fault-to-maintenance link established.

## clamp-left

Installation explicitly requires bracket 12342966; the catalogue lists the left-hand mounting bracket.

- Source: `tm280_20_2:7-24:4:step-b:2:step-1:2`, PDF page 775. Ensure clamp bracket (P/N 12342966) is installed on vehicle.
- Target: `tm280_24p_1:parts:r3985`, PDF page 581. 12342966
- Limitation: Only a maintenance-to-catalogue link; no fault-to-maintenance link established.

## retaining-nut

The note recommends 12342680 in place of four-slotted TN-07; the catalogue lists the nut.

- Source: `tm280_20_2:6-13:2:step-b:2:step-3:2`, PDF page 666. If four-slotted retaining nut TN-07 is present, it is recommended to replace it with eight-slotted retaining nut 12342680.
- Target: `tm280_24p_1:parts:r3551`, PDF page 530. 12342680
- Limitation: Only a maintenance-to-catalogue link; no fault-to-maintenance link established.

## alternator-200a-a

The pulley note identifies 12338796-1 as a 200-amp alternator; the catalogue lists that generator.

- Source: `tm280_20_2:4-3:2:step-b:3:2:step-4:2`, PDF page 195. For 200 amp alternators (12447109 or 12338796-1), tighten locknut to 115-125 lb-ft (156-169 N m).
- Target: `tm280_24p_1:parts:r886`, PDF page 163. 12338796-1
- Limitation: Only a maintenance-to-catalogue link; no fault-to-maintenance link established.
- Limitation: This does not establish that replacing the alternator repairs a charging fault.

## alternator-200a-b

The pulley note identifies 12447109 as a 200-amp alternator; the catalogue lists that generator.

- Source: `tm280_20_2:4-3:2:step-b:3:2:step-4:2`, PDF page 195. For 200 amp alternators (12447109 or 12338796-1), tighten locknut to 115-125 lb-ft (156-169 N m).
- Target: `tm280_24p_1:parts:r860`, PDF page 157. 12447109
- Limitation: Only a maintenance-to-catalogue link; no fault-to-maintenance link established.
- Limitation: This does not establish that replacing the alternator repairs a charging fault.

## fault-28-operator-procedure

The ceiling-light malfunction explicitly refers to operator bulb replacement.

- Source: `tm280_10:table:3-1:6:r28`, PDF page 286. Replace bulb with known serviceable bulb (para. 3-28).
- Target: `tm280_10:3-28`, PDF page 318. 3-28. AMBULANCE INTERIOR LIGHT BULB REPLACEMENT
- Limitation: Only an operator-manual reference; no maintenance-task/catalogue-part bridge established.

## fault-8-operator-procedure

The low-pressure malfunction explicitly refers to operator oil servicing.

- Source: `tm280_10:table:3-1:2:r8`, PDF page 282. Check for low oil level (para. 3-17).
- Target: `tm280_10:3-17`, PDF page 300. 3-17. ENGINE OIL SERVICING
- Limitation: Only an operator-manual reference; no maintenance-task/catalogue-part bridge established.

## Next acceptance decision

Client review must define which source-supported scopes count toward the targets. Build a reviewed question set for those scopes before measuring M3. `target_set.json` deliberately remains pending and lists no approved IDs. A source-chain review reference is required on each eligible question, along with a dated scope agreement and frozen question hash. Keyword-only questions must be reported separately. M3 now fails before model calls while these conditions are unmet. Existing scores remain historical.

The [question revision](question_revision.md) completes the natural-wording pass and removes
the two invalid procedure questions. It does not approve these source relations or establish
complete repair chains.
