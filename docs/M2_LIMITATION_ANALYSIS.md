# M2 limitation analysis

This report classifies every question in `data/eval/questions.jsonl`.
The M1 numbers are the published baseline, copied into `data/eval/m1_baseline/` before the title-reader fix.
The improved numbers are the baseline M3 should be compared with.
The schema those classes use is `docs/M2_GRAPH_SCHEMA.md`.

## What counts as a failure

A question fails when the action is wrong, any required fact is missing, or any gold passage is outside the ten passages given to the generator.
Claim precision is reported in the baseline and is not, by itself, a failure class. The judge demands an exact quote, so a correct passage rewritten by the model would otherwise mark almost every answer as a failure and hide the retrieval misses.
Each failing question is in exactly one class. The first matching rule wins:

1. Keyword mismatch: the answer refuses, and a gold passage is inside the ten.
2. Unanswerable answered: the expected action is refuse, and the answer is not a refusal.
3. Follow-up unresolved: the question is a follow-up and the gold or a fact is missed.
4. Applicability unresolved: the question is applicability and a gold passage is missed.
5. Code and part: the question is relational or multi-hop, a parts-list row is missed, and some gold passage is inside the ten.
6. Procedure incomplete: the question is a procedure, a gold step or caution is missed, and some gold passage is inside the ten.
7. Wrong section: a gold passage is absent from the whole fused list.
8. Ranked too low: a gold passage is in the fused list below rank 10.
9. Answer omitted the fact: the action is wrong or a fact is missing, and the gold passages are inside the ten.

A question that matches none of these is a success.

## Counts

| Class | M1 baseline | Improved baseline | Where the fix lives |
|---|---:|---:|---|
| success | 14 | 20 | the question passed |
| keyword_mismatch | 40 | 0 | outside the graph, and fixed in the improved baseline |
| unanswerable_answered | 13 | 13 | outside the graph; not changed in this milestone |
| follow_up_unresolved | 3 | 3 | a graph traversal |
| applicability_unresolved | 21 | 21 | a graph traversal |
| code_part_relation | 11 | 41 | a graph traversal |
| procedure_incomplete | 22 | 22 | a graph traversal |
| wrong_section | 10 | 10 | a graph traversal where a neighbour was retrieved; otherwise still retrieval |
| ranked_too_low | 9 | 9 | outside the graph; a reranker could reorder these hits |
| answer_omitted_fact | 14 | 18 | outside the graph; the judge requires an exact quote |
| Total | 157 | 157 | |

The improved baseline has 157 questions. 20 succeed. 137 fail. The nine class counts sum to 137.

## The cheap fix

Keyword mismatch is the class a graph should not be credited for.
The M1 answerer treated the malfunction title plus the next word as the string that had to appear in a passage. The improved answerer keeps the title only. A mixed-case title that ends at an em dash, which is how the troubleshooting questions are written, is read the same way.
No index was rebuilt. Fusion is still reciprocal rank fusion with k = 60, the evidence size is still 10, and the reranker is still off.
Generation and judging are still Qwen3-0.6B at temperature 0 and seed 0.

## Classes

### Keyword mismatch: the title reader refuses a retrieved row

Class id: `keyword_mismatch`. Improved-baseline count: 0. Fix: outside the graph, and fixed in the improved baseline.

The dense and sparse lists already contain a gold passage inside the ten given to the generator, and the answer is still a refusal. The title string read from the question included the comma after the malfunction title or the first capital of the next word. That longer string is not in the manual, so the answerer treated the title as missing. Changing the embedding model or the fusion constant does not repair a check that runs after retrieval. The improved baseline stops the title at the malfunction name, including a mixed-case title that ends at an em dash. Questions that then succeed leave this class. Questions that still miss a second gold passage move into the class for that miss.

The improved baseline has no question in this class. The examples are from the M1 baseline, before the title-reader fix.

Examples (M1 baseline):

#### lookup-0003

The truck is showing this problem: 6. ENGINE STARTS BUT MISFIRES, RUNS ROUGH, OR LACKS POWER. What should I check first?

Gold:

- `tm280_10:table:3-1:2:r6`, page 282. 6. ENGINE STARTS BUT MISFIRES, RUNS ROUGH, OR LACKS POWER Step 1. Check for water in fuel filter by draining. Drain fuel filter (para. 3-10). Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit maintenance.

Retrieved, in fused order, up to the first five:

- `tm280_10:m2:2`, page 282. 6. ENGINE STARTS BUT MISFIRES, RUNS ROUGH, OR LACKS POWER
- `tm280_10:table:3-1:2:r6`, page 282. 6. ENGINE STARTS BUT MISFIRES, RUNS ROUGH, OR LACKS POWER Step 1. Check for water in fuel filter by draining. Drain fuel filter (para. 3-10). Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit maintenance.
- `tm280_10:m3`, page 281. 3. ENGINE CRANKS BUT DOES NOT START
- `tm280_20_1:2-22:2:note`, page 186. NOTE Rapidly accelerating the engine with the transmission in neutral doesn't work for this engine because the fuel supply can’t increase as fast as the engine can accelerate so you won’t get good test results. Proper engine performanceis dependent upon the availability of the correct fuel volume to the injection pump. Pay attention to when the engine runs rough. If it runs rough only while warming up after a cold st...
- `tm280_10:m1`, page 281. 1. ENGINE FAILS TO CRANK

#### lookup-0005

The truck is showing this problem: 10. NO RESPONSE TO SHIFT LEVER MOVEMENT. What should I check first?

Gold:

- `tm280_10:table:3-1:3:r10`, page 283. 10. NO RESPONSE TO SHIFT LEVER MOVEMENT Step 1. Check to see if transfer case lever is in “N” (neutral) or “P” (Park) for M1123 and A2 vehicles. Place transmission shift lever in “N” (neutral) or “P” (Park) and select transfer gear range. Step 2. Other causes. Notify unit maintenance.

Retrieved, in fused order, up to the first five:

- `tm280_10:table:3-1:3:r10`, page 283. 10. NO RESPONSE TO SHIFT LEVER MOVEMENT Step 1. Check to see if transfer case lever is in “N” (neutral) or “P” (Park) for M1123 and A2 vehicles. Place transmission shift lever in “N” (neutral) or “P” (Park) and select transfer gear range. Step 2. Other causes. Notify unit maintenance.
- `tm280_10:m2:3`, page 283. 10. NO RESPONSE TO SHIFT LEVER MOVEMENT
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...
- `tm280_10:m4`, page 281. 4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER
- `tm280_20_1:2-35:2:note:3`, page 521. NOTE Run the BRAKES and DRIVETRAIN tests in this manual. If you don’t find any faults, notify DS maintenance. TM 8-2320-280-20-1 TRANSMISSION SYSTEM (4L80-E) 2-417 Page 2-412 Para. 4-39 Page 2-420 2-418 PARA 4-29 PARA. 4-85 PARA 4-42 PARA 4-42 Page 2-418 PAGES 2-428 THROUGH 2-443 PAGE 2-421 PARA. 4-42. 2-420 REFERENCE INFORMATION TRANSMISSION SYSTEM (4L80-E) The following chart will help you find the code you need. T...

#### lookup-0007

The truck is showing this problem: 12. FLUID THROWN FROM TRANSMISSION FILL TUBE. What should I check first?

Gold:

- `tm280_10:table:3-1:3:r12`, page 283. 12. FLUID THROWN FROM TRANSMISSION FILL TUBE Step 1. Check to see if transmission dipstick is loose. Secure dipstick. Step 2. Check fluid level for overfilling (para. 3-19). Notify unit maintenance if fluid level is high. Step 3. Other causes. Notify unit maintenance.

Retrieved, in fused order, up to the first five:

- `tm280_10:m4:3`, page 283. 12. FLUID THROWN FROM TRANSMISSION FILL TUBE
- `tm280_20_2:step-6:2`, page 2. 6. BE AWARE, the field protective mask for nuclear, biological or chemical (NBC) protection will not protect you from carbon monoxide poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. a WARNING SUMMARY • Drycleaning solvent is flammable and will not be used near an open flame. A fire extinguisher will be kept nearby when the solvent is used. Use only in well-ventilated places. Failure to...
- `tm280_10:ch3:secC:step-b:4:2:caution:3`, page 395. CAUTION • Do not overfill trans- mission. The fluid level rises as the fluid tem- perature increases. There- fore, do not check level before the transmission has reached normal operating temperature. The safe operating level is within the crosshatch marks on the dipstick. Overfilling will result in damage to transmission. • Use Dexron® II (3L80) or D e x r o n® III (4L80-E) for filling transmission. Fa i l u r e to u...
- `tm280_24p_1:parts:r7924`, page 1109. 1 PAOFF 2540014504019 19207 12340676-31 TOP ASSEMBLY TRUCK CAMOUFLAGE PART OF KIT P/N 57K3501 A13,A14,BVY,H13,H14,NNN 1
- `tm280_10:table:3-1:3:r12`, page 283. 12. FLUID THROWN FROM TRANSMISSION FILL TUBE Step 1. Check to see if transmission dipstick is loose. Secure dipstick. Step 2. Check fluid level for overfilling (para. 3-19). Notify unit maintenance if fluid level is high. Step 3. Other causes. Notify unit maintenance.

### A question with no answer is given a passage

Class id: `unanswerable_answered`. Improved-baseline count: 13. Fix: outside the graph; not changed in this milestone.

The evaluation expects a refusal, and the answer quotes a retrieved passage. These questions do not look like a Table 3-1 title, so the title check never runs. The answerer then quotes the first fused passage. The invented code is not in the corpus, which is why the gold list is empty. A graph has no true node to walk to. The fix is a generator rule: when the question's distinctive token is absent from the retrieved passages, refuse and repeat the question. That rule was not applied here. A threshold on token overlap would also refuse some short Japanese lookups, and tuning that threshold on this set would not be a fair graph comparison.

Examples (improved baseline):

#### unanswerable-0002

What does this mean in the manual: E9999-NO-SUCH-CODE?

Gold: none. The expected action is refuse.

Retrieved, in fused order, up to the first five:

- `tm280_20_1:2-16:3`, page 131. 2-16. ELECTRIC CIRCUIT DESCRIPTION (CONT’D) When there is no electrical connection, such as when a wire is disconnected, the resistance is infinite (too large to be measured). No current will flow through the wires, because the circuit is no longer continuously connected. This is referred to as an “open circuit” or simply an "open”. Remember that an electrical circuit is formed by continuous loops of devices connecte...
- `tm280_24p_1:ch0:secII:2:step-a:2`, page 36. a. Usable on Code. The Usable on Code appears in the lower left corner of the DESCRIPTION column heading. Usable on Codes are shown as UOC: . . . . . . . in the DESCRIPTION column (justified left) on the first line of applicable item description/nomenclature. Uncoded items are applicable to all models and title description will indicate all M998, M998A1, and M998A2 models. Identification of the Usable on Codes used i...
- `tm280_20_1:2-15:2`, page 129. 2-15. GLOSSARY OF ABBREVIATIONS AND COMMONLY USED TERMS PCB - Protective Control Box, located on the firewall above the brake pedal. STE/ICE-R - Simplified Test Equipment for Internal Combustion Engines - Reprogrammable, a testing system used for performing tests and measurements on the vehicle. In addition to acting as a conventional digital multimeter to measure voltage, current and resistance, it is also capable o...
- `tm280_24p_1:parts:r1321`, page 207. 5 XAOZZ 34623 5581211 PANEL INSTRUMENT 1
- `tm280_20_2:4-42.1`, page 295. 4-42.1. E-PROMReplacement 4-66.2

#### unanswerable-0003

Can you explain part number ZZ-NO-SUCH-PART? I can't find it in the book.

Gold: none. The expected action is refuse.

Retrieved, in fused order, up to the first five:

- `tm280_20_1:2-35:2:note:3`, page 521. NOTE Run the BRAKES and DRIVETRAIN tests in this manual. If you don’t find any faults, notify DS maintenance. TM 8-2320-280-20-1 TRANSMISSION SYSTEM (4L80-E) 2-417 Page 2-412 Para. 4-39 Page 2-420 2-418 PARA 4-29 PARA. 4-85 PARA 4-42 PARA 4-42 Page 2-418 PAGES 2-428 THROUGH 2-443 PAGE 2-421 PARA. 4-42. 2-420 REFERENCE INFORMATION TRANSMISSION SYSTEM (4L80-E) The following chart will help you find the code you need. T...
- `tm280_24p_1:ch0:secII:394`, page 486. SECTION II PART P/N 12342643-1 AND 12447125.........
- `tm280_20_1:2-12:step-e:2`, page 121. e. The STE/ICE-R is an integral part of these troubleshooting procedures. It should be used whenever possible, although other options are given, when available. The Vehicle Identification Number (VIN) assigned to the M998 series vehicles is 21 (14 is the temporary VIN). On page 2-753, you will find information on STE/ICE-R description and operation. Use this information to become familiar with STE/ICE-R operation and...
- `tm280_24p_1:ch0:secII:428`, page 526. SECTION II PART B25,C17,NNN
- `tm280_24p_1:ch0:secII:680`, page 827. SECTION II PART B25,C17,NNN

#### unanswerable-0005

Can you explain fault code QX-404? I can't find it in the book.

Gold: none. The expected action is refuse.

Retrieved, in fused order, up to the first five:

- `tm280_10:2-27`, page 195. 2-27. MALFUNCTION
- `tm280_20_1:2-35:2:note:3`, page 521. NOTE Run the BRAKES and DRIVETRAIN tests in this manual. If you don’t find any faults, notify DS maintenance. TM 8-2320-280-20-1 TRANSMISSION SYSTEM (4L80-E) 2-417 Page 2-412 Para. 4-39 Page 2-420 2-418 PARA 4-29 PARA. 4-85 PARA 4-42 PARA 4-42 Page 2-418 PAGES 2-428 THROUGH 2-443 PAGE 2-421 PARA. 4-42. 2-420 REFERENCE INFORMATION TRANSMISSION SYSTEM (4L80-E) The following chart will help you find the code you need. T...
- `tm280_20_1:2-38:2:note:2`, page 584. NOTE Check fluid for a burnt smell, grit, discoloration, air bubbles, or a milky appearance. o Burnt smell, discolration, or grit indicates worn or damaged internalcomponents. Notify DS maintenance. o Bubbles indicate of an overfilled system or air leaks in the syetem. Drain the fluid and refill to proper level, refer to (para 5-2). o Milkyappearance is due to watar in the system. Replace fluid, and replace fifter. I...
- `tm280_20_1:ch13:secI:step-b:3:2:step-3:2`, page 25. 3. Look for “SERVICE AND TROUBLESHOOTING INSTRUCTIONS” in the chapter list on the cover. This is where the troubleshooting information is located.
- `tm280_20_1:2-27:2:note:25`, page 312. NOTE page 2-218. page 2-222. ALTERNATOR F.1. 2-224.6. 2-224.10.

### The follow-up does not find the other model

Class id: `follow_up_unresolved`. Improved-baseline count: 3. Fix: a graph traversal.

The question is the second turn, "And on the M998?", after a turn that names the M1123. Retrieval receives both turns. The gold passage names both models and is not in the fused list. The words in the question are common model tokens, so many passages match and the one passage that states the pair does not win. Adding synonyms for M998 does not choose among the passages that already contain M998. A traversal from the model in the first turn, along APPLIES_TO, can prefer a passage that also applies to the model in the second turn. Three questions are in this class. The expected change is that those passages enter the ten.

Examples (improved baseline):

#### follow-0001

And on the M998?

Gold:

- `tm280_10:2-44:step-a:2`, page 226. a. General. The troop seat kit is used to convert M998, M998A1, M1097, M1097A1, M1097A2, and M1123 cargo vehicles into troop carriers.

Retrieved, in fused order, up to the first five:

- `tm280_10:2-52:step-a:2`, page 245. a. This section provides operating instructions for components found on M966, M966A1, M1036, M1045, M1045A1, M1045A2, M1046, M1046A1, and M1121 TOW carriers and on M1025, M1025A1, M1025A2, M1026, M1026A1, M1043, M1043A1, M1043A2, M1044, and M1044A1 armament carriers.
- `tm280_10:ch3:secII:10:step-p1:2`, page 344. (1) (2) (3) (4) (5) NATIONAL STOCK ITEM NUMBER LEVEL NUMBER DESCRIPTION U/M 24 C 7930-00-935-3794 POLISH: plastic, liquid, removable (80244) P-P-560, Type I 7930-00-634-5340 1 Pint Container PT 25 C RAG: wiping, cotton and cotton-synthetic (58536) A-A-531 7920-00-205-1711 50 Pound Bale LB 26 C CREAM CLEANER: plastic, liquid 8520-00-262-7177 1 Pint Container PT 27 C DISTILLED WATER: 6810-00-682-6867 1 Gallon Container...
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...
- `tm280_20_1:table:1-2:4:r19`, page 64. M1097A2, and M1123 . . . . . . . . . . . . . . . . . . . . . . 0.438 in. ± 0.125 in.
- `tm280_20_1:1-10`, page 32. 1-10. EQUIPMENT CHARACTERISTICS, CAPABILITIES, AND FEATURES The 1-1/4 ton, 4x4, M998 series of vehicles are tactical vehicles designed for use over all types of roads, as well as cross-country terrain in all weather conditions. The vehicles have four driving wheels powered by a V-8, liquid-cooled, diesel engine. Four-wheel hydraulic service brakes and a mechanical parking brake are common to all models in the M998 se...

#### follow-0002

And on the M998?

Gold:

- `tm280_10:ch3:secC`, page 378. Section Chest 17 Water Cans (2) 18 Spade 19 Jack, Scissors (A2 and M1123 only) F-22 Change 1 INTERNAL TOP VIEW Change 1 F-23/(F-24 blank) APPENDIX G LUBRICATION INSTRUCTIONS G 1. SCOPE This appendix gives lubrication requirements for the M998 series vehicles which are the responsibility of the operator/crew. G-2. GENERAL LUBRICATION REQUIREMENTS

Retrieved, in fused order, up to the first five:

- `tm280_10:2-52:step-a:2`, page 245. a. This section provides operating instructions for components found on M966, M966A1, M1036, M1045, M1045A1, M1045A2, M1046, M1046A1, and M1121 TOW carriers and on M1025, M1025A1, M1025A2, M1026, M1026A1, M1043, M1043A1, M1043A2, M1044, and M1044A1 armament carriers.
- `tm280_10:ch3:secII:10:step-p1:2`, page 344. (1) (2) (3) (4) (5) NATIONAL STOCK ITEM NUMBER LEVEL NUMBER DESCRIPTION U/M 24 C 7930-00-935-3794 POLISH: plastic, liquid, removable (80244) P-P-560, Type I 7930-00-634-5340 1 Pint Container PT 25 C RAG: wiping, cotton and cotton-synthetic (58536) A-A-531 7920-00-205-1711 50 Pound Bale LB 26 C CREAM CLEANER: plastic, liquid 8520-00-262-7177 1 Pint Container PT 27 C DISTILLED WATER: 6810-00-682-6867 1 Gallon Container...
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...
- `tm280_20_1:table:1-2:4:r19`, page 64. M1097A2, and M1123 . . . . . . . . . . . . . . . . . . . . . . 0.438 in. ± 0.125 in.
- `tm280_20_1:1-10`, page 32. 1-10. EQUIPMENT CHARACTERISTICS, CAPABILITIES, AND FEATURES The 1-1/4 ton, 4x4, M998 series of vehicles are tactical vehicles designed for use over all types of roads, as well as cross-country terrain in all weather conditions. The vehicles have four driving wheels powered by a V-8, liquid-cooled, diesel engine. Four-wheel hydraulic service brakes and a mechanical parking brake are common to all models in the M998 se...

#### follow-0003

And on the M998?

Gold:

- `tm280_10:table:1-19`, page 49. Table 1-19. Vehicle Bridge Classification Empty Cross-Country Highway M966, M966A1, M996, M996A1, M997, 3 4 4 M997A1, M997A2, M998, M998A1, M1025, M1025A1, M1025A2, M1026, M1026A1, M1036, M1044, M1044A1, M1045, M1045A1, M1045A2, M1046, M1046A1, M1121 M1035, M1035A1, M1035A2 2 3 3 M1037, M1038, M1038A1, M1042, M1043, 2 4 4 M1043A1, M1043A2, M1097, M1097A1, M1097A2, M1123 Change 1

Retrieved, in fused order, up to the first five:

- `tm280_10:2-52:step-a:2`, page 245. a. This section provides operating instructions for components found on M966, M966A1, M1036, M1045, M1045A1, M1045A2, M1046, M1046A1, and M1121 TOW carriers and on M1025, M1025A1, M1025A2, M1026, M1026A1, M1043, M1043A1, M1043A2, M1044, and M1044A1 armament carriers.
- `tm280_10:ch3:secII:10:step-p1:2`, page 344. (1) (2) (3) (4) (5) NATIONAL STOCK ITEM NUMBER LEVEL NUMBER DESCRIPTION U/M 24 C 7930-00-935-3794 POLISH: plastic, liquid, removable (80244) P-P-560, Type I 7930-00-634-5340 1 Pint Container PT 25 C RAG: wiping, cotton and cotton-synthetic (58536) A-A-531 7920-00-205-1711 50 Pound Bale LB 26 C CREAM CLEANER: plastic, liquid 8520-00-262-7177 1 Pint Container PT 27 C DISTILLED WATER: 6810-00-682-6867 1 Gallon Container...
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...
- `tm280_20_1:table:1-2:4:r19`, page 64. M1097A2, and M1123 . . . . . . . . . . . . . . . . . . . . . . 0.438 in. ± 0.125 in.
- `tm280_20_1:1-10`, page 32. 1-10. EQUIPMENT CHARACTERISTICS, CAPABILITIES, AND FEATURES The 1-1/4 ton, 4x4, M998 series of vehicles are tactical vehicles designed for use over all types of roads, as well as cross-country terrain in all weather conditions. The vehicles have four driving wheels powered by a V-8, liquid-cooled, diesel engine. Four-wheel hydraulic service brakes and a mechanical parking brake are common to all models in the M998 se...

### Applicability to a model is not resolved

Class id: `applicability_unresolved`. Improved-baseline count: 21. Fix: a graph traversal.

The question asks whether a named model is in the instruction. The gold passage contains that model and is outside the ten. Many passages in the M998 series name some model, so dense and sparse search return a popular model mention instead of the passage written for this one. A synonym table cannot separate M1045 from M1025. APPLIES_TO, drawn from applies_to.models and from the model token in the passage, lets the question's model select its own passages. This is the class where applicability hit@10 has to move. The M1 figure is 4.5 percent, one question in 22.

Examples (improved baseline):

#### applicability-0001

Does this instruction mention the M1097?

Gold:

- `tm280_10:1-10`, page 21. 1-10. HEAVY VARIANT CARGO/TROOP CARRIERS (M1097, M1097A1, M1097A2, AND M1123)

Retrieved, in fused order, up to the first five:

- `tm280_10:2-52:step-a:2`, page 245. a. This section provides operating instructions for components found on M966, M966A1, M1036, M1045, M1045A1, M1045A2, M1046, M1046A1, and M1121 TOW carriers and on M1025, M1025A1, M1025A2, M1026, M1026A1, M1043, M1043A1, M1043A2, M1044, and M1044A1 armament carriers.
- `tm280_10:ch3:secII:10:step-p1:2`, page 344. (1) (2) (3) (4) (5) NATIONAL STOCK ITEM NUMBER LEVEL NUMBER DESCRIPTION U/M 24 C 7930-00-935-3794 POLISH: plastic, liquid, removable (80244) P-P-560, Type I 7930-00-634-5340 1 Pint Container PT 25 C RAG: wiping, cotton and cotton-synthetic (58536) A-A-531 7920-00-205-1711 50 Pound Bale LB 26 C CREAM CLEANER: plastic, liquid 8520-00-262-7177 1 Pint Container PT 27 C DISTILLED WATER: 6810-00-682-6867 1 Gallon Container...
- `tm280_10:2-57:step-a:2`, page 252. a. This section provides operating instructions for components found on M996, M996A1, M997, M997A1, M997A2, M1035, M1035A1, and M1035A2 ambulances.
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...
- `tm280_20_1:1-10`, page 32. 1-10. EQUIPMENT CHARACTERISTICS, CAPABILITIES, AND FEATURES The 1-1/4 ton, 4x4, M998 series of vehicles are tactical vehicles designed for use over all types of roads, as well as cross-country terrain in all weather conditions. The vehicles have four driving wheels powered by a V-8, liquid-cooled, diesel engine. Four-wheel hydraulic service brakes and a mechanical parking brake are common to all models in the M998 se...

#### applicability-0002

Which vehicle model is named for this content, and is it the M966?

Gold:

- `tm280_10:1-11`, page 23. 1-11. TOW CARRIERS, ARMORED (M966, M966A1, M1036, AND M1121)

Retrieved, in fused order, up to the first five:

- `tm280_20_1:1-10`, page 32. 1-10. EQUIPMENT CHARACTERISTICS, CAPABILITIES, AND FEATURES The 1-1/4 ton, 4x4, M998 series of vehicles are tactical vehicles designed for use over all types of roads, as well as cross-country terrain in all weather conditions. The vehicles have four driving wheels powered by a V-8, liquid-cooled, diesel engine. Four-wheel hydraulic service brakes and a mechanical parking brake are common to all models in the M998 se...
- `tm280_10:ch3:secI:3`, page 335. Section I. INTRODUCTION C-1. SCOPE This appendix lists additional items authorized for support of M998 series vehicles. C-2. GENERAL This list identifies items that do not have to accompany the vehicle and do not have to be turned in with it. These items are all authorized to you by CTA, MTOE, TDA, or JTA. C-3. EXPLANATION OF LISTING National stock numbers, descriptions, and quantities are provided to help you identi...
- `tm280_10:1-7`, page 18. 1-7. EQUIPMENT CHARACTERISTICS, CAPABILITIES, AND FEATURES The 1-1/4 ton, 4x4, M998 series vehicles are tactical vehicles designed for use over all types of roads, as well as cross-country terrain in all weather conditions. The vehicles have four driving wheels powered by a V-8 liquid-cooled diesel engine. Fo u r -wheel hydraulic service brakes and a mechanical parking brake are common to all models in the M998 serie...
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...
- `tm280_20_1:1-10:step-b:3:2`, page 39. b. SPECIAL LIMITATIONS: Weapon station azimuth is limited to 300° left and right of vehicle centerline when Vehicle Power Condition (VPC) cables are connected. With launcher installed, elevation is limited to 20° and depression is limited to 10°. ARMAMENT CARRIERS, W/SUPPLEMENTAL ARMOR M1043, M1043A1, M1043A2, M1044, AND M1044A1 PURPOSE: These models are used to transport, mount, and operate the M2 and M60 machine gu...

#### applicability-0003

Does this instruction mention the M1045?

Gold:

- `tm280_10:1-12`, page 25. 1-12. TOW CARRIERS, W/SUPPLEMENTAL ARMOR (M1045, M1045A1, M1045A2, M1046, AND M1046A1)

Retrieved, in fused order, up to the first five:

- `tm280_10:2-52:step-a:2`, page 245. a. This section provides operating instructions for components found on M966, M966A1, M1036, M1045, M1045A1, M1045A2, M1046, M1046A1, and M1121 TOW carriers and on M1025, M1025A1, M1025A2, M1026, M1026A1, M1043, M1043A1, M1043A2, M1044, and M1044A1 armament carriers.
- `tm280_10:ch3:secII:10:step-p1:2`, page 344. (1) (2) (3) (4) (5) NATIONAL STOCK ITEM NUMBER LEVEL NUMBER DESCRIPTION U/M 24 C 7930-00-935-3794 POLISH: plastic, liquid, removable (80244) P-P-560, Type I 7930-00-634-5340 1 Pint Container PT 25 C RAG: wiping, cotton and cotton-synthetic (58536) A-A-531 7920-00-205-1711 50 Pound Bale LB 26 C CREAM CLEANER: plastic, liquid 8520-00-262-7177 1 Pint Container PT 27 C DISTILLED WATER: 6810-00-682-6867 1 Gallon Container...
- `tm280_20_1:1-10`, page 32. 1-10. EQUIPMENT CHARACTERISTICS, CAPABILITIES, AND FEATURES The 1-1/4 ton, 4x4, M998 series of vehicles are tactical vehicles designed for use over all types of roads, as well as cross-country terrain in all weather conditions. The vehicles have four driving wheels powered by a V-8, liquid-cooled, diesel engine. Four-wheel hydraulic service brakes and a mechanical parking brake are common to all models in the M998 se...
- `tm280_20_1:table:1-2:4:r19`, page 64. M1097A2, and M1123 . . . . . . . . . . . . . . . . . . . . . . 0.438 in. ± 0.125 in.
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...

### A code and a part stay in different passages

Class id: `code_part_relation`. Improved-baseline count: 41. Fix: a graph traversal.

The question needs both a malfunction row and a parts-list row. One of them, usually the malfunction row or a step that contains the group keyword, is inside the ten. The parts row is not. The two passages share a keyword such as NOZZLE or TRANSMISSION and otherwise have no stored link. Raising the fusion constant or the evidence size does not create that link: the parts row is often far down the list or absent, because its description is a catalogue line and the question is a fault. CANDIDATE_PART, from the committed keyword map in data/cases/rules.json, plus LISTS back to the parts-list passage, is the traversal that can put the part into fusion. The M3 acceptance target, 15 points of evidence recall on relational and multi-hop questions, has to come from this class and from procedure steps that are likewise split. The edge is a candidate, not a proof that the part fits the repair. The keyword and the description stay on the edge.

Examples (improved baseline):

#### relational-0002

For malfunction 5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING TEMPERATURE 190°-230°F (88°-110°C), which parts-list item matches NOZZLE?

Gold:

- `tm280_10:table:3-1:2:r5`, page 282. 5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING TEMPERATURE 190°-230°F (88°-110°C) Step 1. Check oil level for overfilling (Appendix G). Notify unit maintenance if fluid level is high. Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit mainten...
- `tm280_24p_1:parts:r4993`, page 725. 4 PAOZZ 5640013093866 34623 SF-5597692 INSULATION,NOZZLE R.H.,USBL EFF 46162 AND ABOVE 1

Retrieved, in fused order, up to the first five:

- `tm280_10:m1:2`, page 282. 5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING TEMPERATURE 190°-230°F (88°-110°C)
- `tm280_10:table:3-1:2:r5`, page 282. 5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING TEMPERATURE 190°-230°F (88°-110°C) Step 1. Check oil level for overfilling (Appendix G). Notify unit maintenance if fluid level is high. Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit mainten...
- `tm280_10:3-23:step-g:2`, page 310. g. Allow engine to cool at idle until engine temperature lowers to normal operating temperature of 190°- 230°F (88°-110°C).
- `tm280_20_1:2-34:2:step-5:2`, page 508. 5. Bring engine to operating temperature.
- `tm280_10:table:1-6`, page 40. Table 1-6. Cooling System Data Surge tank cap pressure.................................................................................................... 15 psi (103 kPa) Starts to open....................................................................................................................... 190°F (88°C) Fully open..............................................................................................

#### relational-0003

The vehicle has this problem: 6. ENGINE STARTS BUT MISFIRES, RUNS ROUGH, OR LACKS POWER. Which nozzle part number is listed?

Gold:

- `tm280_10:table:3-1:2:r6`, page 282. 6. ENGINE STARTS BUT MISFIRES, RUNS ROUGH, OR LACKS POWER Step 1. Check for water in fuel filter by draining. Drain fuel filter (para. 3-10). Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit maintenance.
- `tm280_24p_1:parts:r4993`, page 725. 4 PAOZZ 5640013093866 34623 SF-5597692 INSULATION,NOZZLE R.H.,USBL EFF 46162 AND ABOVE 1

Retrieved, in fused order, up to the first five:

- `tm280_10:m2:2`, page 282. 6. ENGINE STARTS BUT MISFIRES, RUNS ROUGH, OR LACKS POWER
- `tm280_10:table:3-1:2:r6`, page 282. 6. ENGINE STARTS BUT MISFIRES, RUNS ROUGH, OR LACKS POWER Step 1. Check for water in fuel filter by draining. Drain fuel filter (para. 3-10). Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit maintenance.
- `tm280_24p_1:ch0:secII:4`, page 46. SECTION II PART GROUP 01 ENGINE 0100 ENGINE ASSEMBLY FIG. 1 ENGINE AND CONTAINER ASSEMBLY
- `tm280_10:m3`, page 281. 3. ENGINE CRANKS BUT DOES NOT START
- `tm280_20_1:2-22:2`, page 182. 2-22. FUEL SYSTEM TESTS These Fuel System tests can be run any time you think there maybe a problem with the fuel system or if you were sent here from another test. If you are running this test because the engine runs rough remember that air intake and exhaust as well as internal mechanical problems can also cause this condition. At the bottom of this page is a simplified block diagram which shows how the different f...

#### relational-0004

For malfunction 7. ENGINE OVERHEATS ACCORDING TO ENGINE COOLANT TEMPERATURE GAUGE, which parts-list item matches RADIATOR?

Gold:

- `tm280_10:table:3-1:2:r7`, page 282. 7. ENGINE OVERHEATS ACCORDING TO ENGINE COOLANT TEMPERATURE GAUGE Step 1. Check to see if fan is running. If fan is not running, perform emergency fan clutch override procedure (para. 3-23). Step 2. Allow engine to cool and check for low coolant level. Add coolant as necessary (para. 3-9). Step 3. Check for debris blocking radiator fins. Remove debris. Step 4. Check for broken or missing fan belts. Notify unit mainte...
- `tm280_24p_1:parts:r4553`, page 671. 10 PFOZZ 5340012127711 34623 5584077 BRACKET,ANGLE LOWER RADIATOR MOUNT 1

Retrieved, in fused order, up to the first five:

- `tm280_10:m3:2`, page 282. 7. ENGINE OVERHEATS ACCORDING TO ENGINE COOLANT TEMPERATURE GAUGE
- `tm280_10:table:3-1:2:r7`, page 282. 7. ENGINE OVERHEATS ACCORDING TO ENGINE COOLANT TEMPERATURE GAUGE Step 1. Check to see if fan is running. If fan is not running, perform emergency fan clutch override procedure (para. 3-23). Step 2. Allow engine to cool and check for low coolant level. Add coolant as necessary (para. 3-9). Step 3. Check for debris blocking radiator fins. Remove debris. Step 4. Check for broken or missing fan belts. Notify unit mainte...
- `tm280_24p_1:ch0:secII:73`, page 121. SECTION II PART GROUP 05 COOLING SYSTEM 0501 RADIATOR,EVAPORATIVE COOLER OR HEAT EXCHANGE FIG. 26 RADIATOR AND MOUNTING HARDWARE
- `tm280_24p_1:ch0:secII:4`, page 46. SECTION II PART GROUP 01 ENGINE 0100 ENGINE ASSEMBLY FIG. 1 ENGINE AND CONTAINER ASSEMBLY
- `tm2815_34:table:2-3:2`, page 238. Table 2-3. General Repair Standards (6.5L) (Cont’d). Piston Pin Rocker Arm Ratio 1.5:1 1.5:1 Face Angle 45° 45° Seat Angle 46° 46° Valve Spring Force Timing Chain Deflection APPENDIX A This appendix lists all forms, field manuals, and technical manuals for use with this manual. A-2. PUBLICATIONS INDEX The following index should be consulted frequently for latest changes or revisions and for new publications relating...

### A procedure is found without the rest of its steps

Class id: `procedure_incomplete`. Improved-baseline count: 22. Fix: a graph traversal.

Hit@10 on procedures is 100 percent: some step of the task is in the ten. Evidence recall is much lower because the question quotes the first line of the task and the later steps, and often the caution, share little of that line. They are stored as separate nodes. A longer query that pasted every step would be circular. NEXT, in step-number order under the same task prefix, and BOUND_CAUTION, which the node file already records, pull the rest of the task once any step is found. Most of the missing nodes are later steps. A smaller number are cautions. Tuning the dense model does not attach a warning that the question never named.

Examples (improved baseline):

#### procedure-0001

How do I carry out this job, in order? It starts with: 1. Remove old pages and insert new pages as indicated below.

Gold:

- `tm280_10:step-1:2`, page 2. 1. Remove old pages and insert new pages as indicated below.
- `tm280_10:step-1:3:2`, page 5. 1. Two new models have been added to the front cover. The new cover, located at the end of the change package, replaces the existing cover.
- `tm280_10:step-1:4:2`, page 8. 1. Do not operate your vehicle engine in enclosed areas.
- `tm280_10:1-18:caution`, page 42. CAUTION instructions. "H" (high range) "H/L" (high lock range) "L" (low range) "N" (neutral) 1-27

Retrieved, in fused order, up to the first five:

- `tm280_24p_1:step-1:2`, page 3. 1. Remove old pages and insert new pages as indicated below.
- `tm280_20_2:step-1:5:2`, page 12. 1. Remove old pages and insert new pages as indicated below.
- `tm280_20_1:step-1:3:2`, page 5. 1. Remove old pages and insert new pages as indicated below.
- `tm280_10:step-1:2`, page 2. 1. Remove old pages and insert new pages as indicated below.
- `tm280_20_2:step-2:4:2`, page 8. 2. Remove old pages and insert new pages as indicated below.

#### procedure-0002

List the numbered steps, in order, that begin with: 2. Winch Wire Rope. .WARNING. Wear leather gloves when handling winch wire rope. Do not handle wire rope with bare hands. Broken wires cause injury. After each use, clean and lubricate winch wire rope. Clean entire wire rope with wire brush. Do not lubri- cate winch wire rope in dry, dusty

Gold:

- `tm280_10:ch3:secC:step-b:4:2:step-2:2`, page 394. 2. Winch Wire Rope. .WARNING. Wear leather gloves when handling winch wire rope. Do not handle wire rope with bare hands. Broken wires cause injury. After each use, clean and lubricate winch wire rope. Clean entire wire rope with wire brush. Do not lubri- cate winch wire rope in dry, dusty
- `tm280_10:ch3:secC:step-b:4:2:step-3:2`, page 394. 3. Pintle. Every 3,000 mi (4,827 km), or semi- a n n u a l l y, whichever occurs first, clean pintle with wire bush and lubricate rear plate fitting with seasonal grade OE. periodic changing. Change 1 G-15 NOTES
- `tm280_10:ch3:secC:step-b:4:2:step-4:2`, page 394. 4. Steering System.

Retrieved, in fused order, up to the first five:

- `tm280_10:ch3:secC:step-b:4:2:step-2:2`, page 394. 2. Winch Wire Rope. .WARNING. Wear leather gloves when handling winch wire rope. Do not handle wire rope with bare hands. Broken wires cause injury. After each use, clean and lubricate winch wire rope. Clean entire wire rope with wire brush. Do not lubri- cate winch wire rope in dry, dusty
- `tm280_10:2-26.1:step-c:2:caution:2`, page 191. WARNING • Wear leather gloves when handling winch cable. Do not handle cable with bare hands. • When fully extending winch cable, ensure that five wraps of winch cable remain on drum at all times. Failure to do this may cause injury or death to personnel.
- `tm280_10:2-26:step-c:2:step-p1:2`, page 189. (1) Turn clutch lever (1) counterclockwise to “FREE SPOOL.” WWAARRNNIINNGG (cid:127) Wear leather gloves when handling winch cable. Do not handle cable with bare hands. (cid:127) When fully extending winch cable, ensure that four wraps of winch cable remain on drum at all times. Failure to do this may cause injury or death to personnel. NNOOTTEE Allow 1 ft (30.5 cm) of slack in winch cable prior to start of winching...
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...
- `tm280_20_1:step-6:2`, page 2. 6. BE AWARE, the field protective mask for nuclear, biological or chemical (NBC) protection will not protect you from carbon monoxide poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. a WARNING SUMMARY (Cont'd) • Drycleaning solvent is flammable and will not be used near an open flame. A fire extinguisher will be kept nearby when the solvent is used. Use only in well-ventilated places. Fa...

#### procedure-0003

How do I carry out this job, in order? It starts with: 1. Do not operate your vehicle engine in enclosed areas.

Gold:

- `tm280_20_2:step-1:2`, page 2. 1. Do not operate your vehicle engine in enclosed areas.
- `tm280_20_2:step-1:3:2`, page 5. 1. Remove old pages and insert new pages as indicated below.
- `tm280_20_2:step-1:4:2`, page 8. 1. Two new models have been added to the front cover. The new cover, located at the end of the change package, replaces the existing cover.
- `tm280_20_2:3-12:2:step-c:2:caution`, page 42. WARNING

Retrieved, in fused order, up to the first five:

- `tm280_20_1:step-1:2`, page 2. 1. Do not operate your vehicle engine in enclosed areas.
- `tm280_20_2:step-1:2`, page 2. 1. Do not operate your vehicle engine in enclosed areas.
- `tm280_10:step-1:4:2`, page 8. 1. Do not operate your vehicle engine in enclosed areas.
- `tm2815_34:step-1:2`, page 2. 1. DO NOT operate your vehicle engine in enclosed area.
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...

### Right manual, the section is not retrieved

Class id: `wrong_section`. Improved-baseline count: 10. Fix: a graph traversal where a neighbour was retrieved; otherwise still retrieval.

No gold passage appears anywhere in the fused list. The retrieved pages are from the same corpus and answer a neighbouring question. For a Japanese lookup the gold section is in mlit_b052 and the hits are other sections, or none of that document. For an English malfunction the Table 3-1 row itself was not returned. PARENT helps only when a passage from the same section was retrieved and the gold node is its child or its parent. Where the list contains nothing from the gold document, the graph has no seed and the miss stays a retrieval miss. The report's examples show which of those two situations the question is in.

Examples (improved baseline):

#### lookup-0014

What does malfunction 17. BRAKE WARNING LAMP ASSEMBLY ON list as the first test or corrective action?

Gold:

- `tm280_10:table:3-1:4:r17`, page 284. 17. BRAKE WARNING LAMP ASSEMBLY ON Step 1. Check to see if parking brake is partially applied. Disengage parking brake. Step 2. Check for low brake fluid level (TM 9-2320-280-20). Add brake fluid (Appendix G). Step 3. Other causes. Notify unit maintenance.

Retrieved, in fused order, up to the first five:

- `tm280_10:2-2`, page 51. 2-2. CONTROLS, INDICATORS, AND EQUIPMENT a. Driver's Compartment. KEY ITEM AND FUNCTION 1 Rotary switch has “ENG STOP," 'RUN," and “START." When positioned to "RUN," glow plugs are activated to heat engine precombustion chambers. When positioned to “START," the starter will engage and crank the engine. 2 Wait-to-start lamp assembly illuminates when glow plugs are activated, goes out when engine is ready to be started...
- `tm280_10:m3:4`, page 284. 17. BRAKE WARNING LAMP ASSEMBLY ON
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...
- `tm280_20_2:4-17.1`, page 248. 4-17.1. Brake Warning Lamp Replacement 4-36.2
- `tm280_20_1:2-28:2:caution:2`, page 329. WARNING Disconnect negative battery cable before disconnecting and reconnecting protective control box/distribution box harness. Failure to do so may result in injury to personnel or damage to equipment. START LED 10 momentarily "ON" and then remains "OFF" (starter motor (ENGINE frequency lockout). CRANKING- If LED 11 and 13 remain "ON" or engine does not crank; check battery Replace protective control box, refer to...

#### lookup-0019

The truck is showing this problem: 22. HARD STEERING. What should I check first?

Gold:

- `tm280_10:table:3-1:4:r22`, page 285. 22. HARD STEERING Step 1. Check tire air pressure. Inflate or deflate tires to correct air pressure. Step 2. Check power steering reservoir for low fluid level (para. 3-20). Add steering fluid (Appendix G). Step 3. Check for broken or missing power steering belts. Notify unit maintenance if belts are broken or missing. Step 4. Check power steering cooler for bent fins or any other air flow obstructions. Remove obstru...

Retrieved, in fused order, up to the first five:

- `tm280_20_1:2-37:2:step-b:5:2`, page 563. b. Adjust loose power steering drivebelts (para 3-82). While travelling at a moderate speed (20mph) (32 kmph), apply the brakes while applying minimal pressure to the steering wheel. If pull to one side or the other occurs, make a note of the speed at which it occurs and on what side of the vehicle it occurs. Repeat this procedure for different speeds and braking forces. If the vehicle seems to steer straight while b...
- `tm280_24p_1:parts:r7924`, page 1109. 1 PAOFF 2540014504019 19207 12340676-31 TOP ASSEMBLY TRUCK CAMOUFLAGE PART OF KIT P/N 57K3501 A13,A14,BVY,H13,H14,NNN 1
- `tm280_10:3-24`, page 311. 3-24. REARVIEW MIRROR ADJUSTMENT (FOR VEHICLE SERIAL NUMBER 99,999 AND BELOW)
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...
- `tm280_10:3-25`, page 312. 3-25. REARVIEW MIRROR ADJUSTMENT (FOR VEHICLE SERIAL NUMBER 100,000 AND ABOVE)

#### lookup-0028

What does malfunction 1. ENGINE FAILS TO CRANK list as the first test or corrective action?

Gold:

- `tm280_10:table:3-1:r1`, page 281. 1. ENGINE FAILS TO CRANK Step 1. Check to see if transmission shift lever is in “N” (neutral) or “P” (park) for M1123 and A2 vehicles. If not, place lever in“N” (neutral) or “P” (park). Step 2. Check battery fluid level and check battery connections for looseness, damage, or corrosion. If any of these conditions exist, notify unit maintenance. Step 3. Attempt to slave-start vehicle (para. 2-23). Step 4. Other causes....

Retrieved, in fused order, up to the first five:

- `tm280_10:m1`, page 281. 1. ENGINE FAILS TO CRANK
- `tm280_20_1:2-28:2:caution:2`, page 329. WARNING Disconnect negative battery cable before disconnecting and reconnecting protective control box/distribution box harness. Failure to do so may result in injury to personnel or damage to equipment. START LED 10 momentarily "ON" and then remains "OFF" (starter motor (ENGINE frequency lockout). CRANKING- If LED 11 and 13 remain "ON" or engine does not crank; check battery Replace protective control box, refer to...
- `tm280_20_1:2-17:2`, page 132. 2-17. STARTABILITY TESTS This is a top level test for problems with an engine that doesn’t start, or starts but immediately stops, or is very hard to start. If the engine starts but doesn’t run well after starting, try the "STARTABILITY" tests first. FOR THE ENGINE TO START, ALL OF THE BASIC SYSTEMS SHOWN BELOW MUST BE WORKING. THESE STARTABILITY TESTS WILL HELP YOU TO VERIFY THE CONDITION OF EACH OF THESE SYSTEMS. 2...
- `tm280_20_1:2-24:2`, page 228. 2-24. COMPRESSION/MECHANICAL TESTS The main intent of this paragraph is to determine if the engine has internal compression or mechanical problems and to fix everything possible without having to notify DS maintenance. 2-143 DIAGNOSTIC FLOWCHART COMPRESSION/MECHANICAL Page 2-734 page 2-148 Page 2-41 Page 2-739 Page 2-65 Page 2-146 2-144 REFERENCE INFORMATION COMPRESSION/MECHANICAL COMPRESSION / MECHANICAL FROM 3, Pag...
- `tm280_10:m3`, page 281. 3. ENGINE CRANKS BUT DOES NOT START

### The right passage is retrieved below the ten

Class id: `ranked_too_low`. Improved-baseline count: 9. Fix: outside the graph; a reranker could reorder these hits.

A gold passage is in the fused list and its rank is worse than 10, so it is not given to the generator. Hit@10 is defined on those ten passages. Widening the cutoff would change the metric rather than the retriever. A cross-encoder could move a hit from rank 13 into the ten when it actually answers the question. That is a reranker, and the reported baseline leaves the reranker off. The graph helps this class only when a passage already inside the ten is a PARENT, NEXT, or CANDIDATE_PART neighbour of the low-ranked row. It is not the class the schema is built for.

Examples (improved baseline):

#### lookup-0001

The truck is showing this problem: 4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER. What should I check first?

Gold:

- `tm280_10:table:3-1:2:r4`, page 281. 4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER Step 1. Check battery cable connections for looseness, damage, or corrosion. Notify unit maintenance of any damage to battery cables. Step 2. Check for broken or missing alternator belts. Notify unit maintenance if alternator belts are broken or missing. Step 3. Other causes. Notify unit maintenance.

Retrieved, in fused order, up to the first five:

- `tm280_10:m4`, page 281. 4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER
- `tm280_20_1:2-32:2:note`, page 428. NOTE The wait-to-start lamp is not an accurate indication of glowplug operation. Make sure the glowplugs are operating property BEFORE you check out the light. Go to the Glowplug Tests, page 2-303. Return here if the light still doesn't operate property. The wait-t-start lamp should come on when the engine is below 120°F (49° C) and the rotary switch is first turned to the RUN position. 2-321 DIAGNOSTIC FLOWCHART INS...
- `tm280_20_1:2-35:2:note:3`, page 521. NOTE Run the BRAKES and DRIVETRAIN tests in this manual. If you don’t find any faults, notify DS maintenance. TM 8-2320-280-20-1 TRANSMISSION SYSTEM (4L80-E) 2-417 Page 2-412 Para. 4-39 Page 2-420 2-418 PARA 4-29 PARA. 4-85 PARA 4-42 PARA 4-42 Page 2-418 PAGES 2-428 THROUGH 2-443 PAGE 2-421 PARA. 4-42. 2-420 REFERENCE INFORMATION TRANSMISSION SYSTEM (4L80-E) The following chart will help you find the code you need. T...
- `tm280_24p_1:parts:r7924`, page 1109. 1 PAOFF 2540014504019 19207 12340676-31 TOP ASSEMBLY TRUCK CAMOUFLAGE PART OF KIT P/N 57K3501 A13,A14,BVY,H13,H14,NNN 1
- `tm280_10:3-24`, page 311. 3-24. REARVIEW MIRROR ADJUSTMENT (FOR VEHICLE SERIAL NUMBER 99,999 AND BELOW)

#### lookup-0008

What does malfunction 13. SLIPPAGE IN ALL RANGES list as the first test or corrective action?

Gold:

- `tm280_10:table:3-1:3:r13`, page 283. 13. SLIPPAGE IN ALL RANGES Step 1. Check for low fluid level (para. 3-19). Add fluid (Appendix G). Step 2. Other causes. Notify unit maintenance.

Retrieved, in fused order, up to the first five:

- `tm280_10:m5`, page 283. 13. SLIPPAGE IN ALL RANGES
- `tm280_24p_1:ch0:secI:2:step-b:3:2`, page 32. b. SMRCode (Column (2). The Source, Maintenance, and Recoverability (SMR) code is a 5-position code containing supply/requisitioning information, maintenance category authorization criteria, and disposition instruction, as shown in the following breakout: Source Maintenance Recoverability Code Code Code 1st two XX XX X 5th position positions How you get an item 3d position 4th position Who determines disposition acti...
- `tm280_10:m4:5:step-step1:2`, page 286. Step 1. Perform malfunction 26, steps 1 through 3.
- `tm280_20_1:2-28:2:caution:2`, page 329. WARNING Disconnect negative battery cable before disconnecting and reconnecting protective control box/distribution box harness. Failure to do so may result in injury to personnel or damage to equipment. START LED 10 momentarily "ON" and then remains "OFF" (starter motor (ENGINE frequency lockout). CRANKING- If LED 11 and 13 remain "ON" or engine does not crank; check battery Replace protective control box, refer to...
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...

#### lookup-0029

The truck is showing this problem: 2. ENGINE CRANKS SLOWLY. What should I check first?

Gold:

- `tm280_10:table:3-1:r2`, page 281. 2. ENGINE CRANKS SLOWLY Step 1. Check battery fluid level and check battery cable connections for looseness, damage, or corrosion. If any of these conditions exist, notify unit maintenance. Step 2. Attempt to slave-start vehicle (para. 2-23). Step 3. Other causes. Notify unit maintenance.

Retrieved, in fused order, up to the first five:

- `tm280_10:m2`, page 281. 2. ENGINE CRANKS SLOWLY
- `tm280_20_1:2-30:2`, page 355. 2-30. STARTER CIRCUIT TESTS STARTER CIRCUIT WITHOUT STARTER LOCKOUT VEHICLE BATTERIES PROTECTIVE CONTROL BOX/ DISTRIBUTION BOX STARTER SOLENOID STARTER ENGINE MECHANICAL GENERAL DESCRIPTION ROTARY SWITCH NEUTRAL SAFETY SWITCH The Starter Circuit consists of the batteries, starter solenoid, starter motor, rotary switch, neutral safety switch, protective control box/distribution box, and related electrical wiring. The...
- `tm280_10:m3`, page 281. 3. ENGINE CRANKS BUT DOES NOT START
- `tm280_20_1:2-31.1:2`, page 411. 2-31.1. GLOWPLUGS CIRCUIT TESTS (DISTRIBUTION BOX) These tests of the Glowplugs Circuit can be run anytime you think there may be a problem with the glowplugs, or if you were sent here from another test. If you were sent from another test, be sure to mark where you came from so you will be able to return. If you are running this test because the engine is hard to start when cold, remember that there is also a cold st...
- `tm280_10:m4`, page 281. 4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER

### The gold passage is in the ten and the fact is still missed

Class id: `answer_omitted_fact`. Improved-baseline count: 18. Fix: outside the graph; the judge requires an exact quote.

Every gold passage is inside the ten, and the action matches. A required fact is still not accepted. The judge counts a fact only when it returns a quote that is an exact span of a cited passage. The passage can be present in the ranking while the answer cites a different hit, or the model's quote can differ by a character from the manual. Neither failure is a missing edge. The title fix moves some of these questions out of the class by quoting the malfunction row itself. What remains is generator and judge behaviour. It is outside the graph.

Examples (improved baseline):

#### lookup-0002

What does malfunction 5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING TEMPERATURE 190°-230°F (88°-110°C) list as the first test or corrective action?

Gold:

- `tm280_10:table:3-1:2:r5`, page 282. 5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING TEMPERATURE 190°-230°F (88°-110°C) Step 1. Check oil level for overfilling (Appendix G). Notify unit maintenance if fluid level is high. Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit mainten...

Retrieved, in fused order, up to the first five:

- `tm280_10:m1:2`, page 282. 5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING TEMPERATURE 190°-230°F (88°-110°C)
- `tm280_10:table:3-1:2:r5`, page 282. 5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING TEMPERATURE 190°-230°F (88°-110°C) Step 1. Check oil level for overfilling (Appendix G). Notify unit maintenance if fluid level is high. Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit mainten...
- `tm280_20_1:2-25:2:caution:4`, page 243. WARNING Do not remove surge tank filler cap before releasing internal pressure when engine temperature is above 190 °F (88°C). Steam or hot coolant under pressure will cause injury. Check seal and spring on pressure cap. Replace pressure cap, refer to (para. 3-60). Flush cooling system, refer to (para. 3-60). For surge tank and radiator support replacement procedures, refer to (paras. 3-63 and 3-64). For oil cooler a...
- `tm280_20_1:2-34:2:step-5:2`, page 508. 5. Bring engine to operating temperature.
- `tm280_20_1:step-6:2`, page 2. 6. BE AWARE, the field protective mask for nuclear, biological or chemical (NBC) protection will not protect you from carbon monoxide poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. a WARNING SUMMARY (Cont'd) • Drycleaning solvent is flammable and will not be used near an open flame. A fire extinguisher will be kept nearby when the solvent is used. Use only in well-ventilated places. Fa...

#### lookup-0005

The truck is showing this problem: 10. NO RESPONSE TO SHIFT LEVER MOVEMENT. What should I check first?

Gold:

- `tm280_10:table:3-1:3:r10`, page 283. 10. NO RESPONSE TO SHIFT LEVER MOVEMENT Step 1. Check to see if transfer case lever is in “N” (neutral) or “P” (Park) for M1123 and A2 vehicles. Place transmission shift lever in “N” (neutral) or “P” (Park) and select transfer gear range. Step 2. Other causes. Notify unit maintenance.

Retrieved, in fused order, up to the first five:

- `tm280_10:table:3-1:3:r10`, page 283. 10. NO RESPONSE TO SHIFT LEVER MOVEMENT Step 1. Check to see if transfer case lever is in “N” (neutral) or “P” (Park) for M1123 and A2 vehicles. Place transmission shift lever in “N” (neutral) or “P” (Park) and select transfer gear range. Step 2. Other causes. Notify unit maintenance.
- `tm280_10:m2:3`, page 283. 10. NO RESPONSE TO SHIFT LEVER MOVEMENT
- `tm280_10:step-6:2`, page 8. 6. BE AWARE, the field protective mask and ambulance Nuclear-Biological-Chemical (NBC) system will not protect you from exhaust poisoning. THE BEST DEFENSE AGAINST EXHAUST POISONING IS ADEQUATE VENTILATION. warning a WARNING SUMMARY • Never open one end of cargo shell door without first ensuring that the opposite end is securely closed. Not doing so may cause both ends to open at the same time, causing damage to equi...
- `tm280_10:m4`, page 281. 4. VEHICLE NOT CHARGING ACCORDING TO VOLTMETER
- `tm280_20_1:2-35:2:note:3`, page 521. NOTE Run the BRAKES and DRIVETRAIN tests in this manual. If you don’t find any faults, notify DS maintenance. TM 8-2320-280-20-1 TRANSMISSION SYSTEM (4L80-E) 2-417 Page 2-412 Para. 4-39 Page 2-420 2-418 PARA 4-29 PARA. 4-85 PARA 4-42 PARA 4-42 Page 2-418 PAGES 2-428 THROUGH 2-443 PAGE 2-421 PARA. 4-42. 2-420 REFERENCE INFORMATION TRANSMISSION SYSTEM (4L80-E) The following chart will help you find the code you need. T...

#### lookup-0009

The truck is showing this problem: 8. LOW ENGINE OIL PRESSURE ACCORDING TO OIL PRESSURE GAUGE. What should I check first?

Gold:

- `tm280_10:table:3-1:3:r8`, page 282. 8. LOW ENGINE OIL PRESSURE ACCORDING TO OIL PRESSURE GAUGE Step 1. Check for low oil level (para. 3-17). Add oil (Appendix G). Step 2. Other causes. Notify unit maintenance.

Retrieved, in fused order, up to the first five:

- `tm280_10:table:3-1:3:r8`, page 282. 8. LOW ENGINE OIL PRESSURE ACCORDING TO OIL PRESSURE GAUGE Step 1. Check for low oil level (para. 3-17). Add oil (Appendix G). Step 2. Other causes. Notify unit maintenance.
- `tm280_10:m4:2`, page 282. 8. LOW ENGINE OIL PRESSURE ACCORDING TO OIL PRESSURE GAUGE
- `tm280_20_1:2-35:2:note:3`, page 521. NOTE Run the BRAKES and DRIVETRAIN tests in this manual. If you don’t find any faults, notify DS maintenance. TM 8-2320-280-20-1 TRANSMISSION SYSTEM (4L80-E) 2-417 Page 2-412 Para. 4-39 Page 2-420 2-418 PARA 4-29 PARA. 4-85 PARA 4-42 PARA 4-42 Page 2-418 PAGES 2-428 THROUGH 2-443 PAGE 2-421 PARA. 4-42. 2-420 REFERENCE INFORMATION TRANSMISSION SYSTEM (4L80-E) The following chart will help you find the code you need. T...
- `tm280_20_1:2-32:2:note`, page 428. NOTE The wait-to-start lamp is not an accurate indication of glowplug operation. Make sure the glowplugs are operating property BEFORE you check out the light. Go to the Glowplug Tests, page 2-303. Return here if the light still doesn't operate property. The wait-t-start lamp should come on when the engine is below 120°F (49° C) and the rotary switch is first turned to the RUN position. 2-321 DIAGNOSTIC FLOWCHART INS...
- `tm280_20_1:2-37:2:step-b:5:2`, page 563. b. Adjust loose power steering drivebelts (para 3-82). While travelling at a moderate speed (20mph) (32 kmph), apply the brakes while applying minimal pressure to the steering wheel. If pull to one side or the other occurs, make a note of the speed at which it occurs and on what side of the vehicle it occurs. Repeat this procedure for different speeds and braking forces. If the vehicle seems to steer straight while b...

## What M3 should measure

Compare M3 with the improved baseline, not with the M1 file.
The graph classes are code and part, procedure incomplete, applicability, follow-up, and the wrong-section questions whose top passages are in the same document as the gold.
The acceptance target from the requirements is 15 points of evidence recall and 10 points of required-fact recall on the relational and multi-hop questions, with no question type losing more than 1 point of hit@10 or required-fact recall.
Those relational and multi-hop points have to come from bringing the missing parts row, and the missing middle step, into the ten.
Keyword mismatch, unanswerable answers, facts omitted from a complete gold set, and passages ranked just below the ten are not that target.
