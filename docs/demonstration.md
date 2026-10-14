# Five-minute demonstration

Recorded from the M1 baseline (`docs/baseline_report.md`).
Open the demo with `make demo`, then go to http://127.0.0.1:8080.
Ask these four questions in order. About five minutes covers them.
The page calls `ask_with_hits`, the same function that produced the answers below.
The recording of this page answering the four questions is `docs/m1-demonstration.mp4`.

## Lookup

What is the corrective action for 4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER?

4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER Step 1. Check battery cable connections for looseness, damage, or corrosion. Notify unit maintenance of any damage to battery cables. Step 2. Check for broken or missing alternator belts. Notify unit maintenance if alternator belts are broken or missing. Step 3. Other causes. Notify unit maintenance.

Citations:

- `tm280_10:table:3-1:2:r4`, page 281

This is operator Table 3-1, row 4, page 281. The first check is the battery cables.

## Procedure

What are the steps to disconnect the engine oil cooler supply and return lines, including the warning not to drain oil when the engine is hot?

WARNING Do not drain oil when engine is hot. Severe injury to personnel will result.
1. Disconnect two engine oil cooler supply and return lines (7) from engine oil cooler ports (9).
3. Connect two engine oil cooler supply and return lines (7) to engine oil cooler ports (9).

Citations:

- `tm280_20_2:3-8:step-a:3:2:caution`, page 32
- `tm280_20_2:3-8:step-a:3:2:step-1:2`, page 32
- `tm280_20_2:3-8:step-a:3:2:step-3:3:2`, page 32

The hot-oil warning is cited before the disconnect step. Both come from task 3-8, page 32.

## Relational

The vehicle has this problem: 10. NO RESPONSE TO SHIFT LEVER MOVEMENT. Which transmission part number is listed?

No retrieved passage contains the requested material. Searched: The vehicle has this problem: 10. NO RESPONSE TO SHIFT LEVER MOVEMENT. Which transmission part number is listed?

Citations: none.

The baseline refuses. The malfunction is in the operator manual, and the question asks which transmission part to use. The answerer reads the title plus the next word, does not find that longer string, and does not reach the parts list.

## Refusal

What is the corrective action for 99. ZZZNOTACODE FAILURE?

No retrieved passage contains the requested material. Searched: What is the corrective action for 99. ZZZNOTACODE FAILURE?

Citations: none.

99. ZZZNOTACODE FAILURE is not in the manuals. The answer repeats the question and cites nothing.
