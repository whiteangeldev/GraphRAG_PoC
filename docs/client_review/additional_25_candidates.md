# Additional 25 Choice B candidates for review

Choice B: bounded manual relationships. Full repair chains are not required.
Client acceptance is shown per case. The full benchmark is not frozen or approved.
Batch 2 must be reviewed before M3. Wording was prepared with AI assistance.
Expected answers are review notes, not complete service procedures.
This file contains 25 cases: 0 accepted and 25 pending review.
PDF pages below are one-based physical file pages, not printed manual page labels.

| ID | Scope | Type | Batch | Client review |
|---|---|---|---|---|
| review-slow-crank-slave-connection | operator_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-rough-running-filter-drain | operator_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-rough-running-element-cleaning | operator_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-all-range-slip-level-check | operator_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-all-ambulance-lights-normal | operator_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-ambulance-spotlight-bulb-base | operator_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-ambulance-spotlight-switch | operator_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-ambulance-cooling-engine-running | operator_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-ambulance-outlet-isolate | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-transmission-electronic-codes | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-steering-test-rpm-setting | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-oil-adapter-filter-followon | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-oil-pan-starter-support | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-drainage-bracket-dust-unloader | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-return-check-valve-air-horn | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-filter-element-bleed-endpoint | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-muffler-tailpipe-fasteners | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-crossover-rear-heat-shield | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-radiator-refill-heater-valve | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-oil-cooler-steering-lines | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-tank-vent-propeller-inspection | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-fuel-pump-ground-first | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-filter-bleed-transducer-seal | maintenance_reference_and_instruction | multi_hop | 2 | source_checked_pending_client |
| review-surge-tank-stock-replacement | maintenance_catalogue_identity | relational | 2 | source_checked_pending_client |
| review-surge-hose-trim-adaptation | maintenance_catalogue_identity | relational | 2 | source_checked_pending_client |

## review-slow-crank-slave-connection

The starter turns the engine slowly. If the troubleshooting checks lead to starting it from another vehicle, which paragraph applies and how should I fit the cable to the receptacle?

Expected answer for review: Table 3-1 refers to paragraph 2-23. Fit the slave cable to the receptacle using a twisting motion.

Required facts for scoring:

- `tm280_10:table:3-1:r2`: 2-23
- `tm280_10:2-23:step-c:2`: Use a twisting motion when installing slave cable to the receptacle.

Evidence:

- `tm280_10:table:3-1:r2`, PDF page 281: Attempt to slave-start vehicle (para. 2-23).
- `tm280_10:2-23`, PDF page 179: 2-23. SLAVE STARTING OPERATION
- `tm280_10:2-23:step-c:2`, PDF page 179: Use a twisting motion when installing slave cable to the receptacle.

Limits:

- Operator troubleshooting reference and selected instruction only; this is not a complete repair chain.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-rough-running-filter-drain

The engine starts but runs rough, and I am checking for water in the fuel filter. Which service paragraph does troubleshooting point to, and about how much fuel does its drain step call for?

Expected answer for review: Table 3-1 refers to paragraph 3-10. Open the fuel draincock and drain approximately 1 pint (0.47 L) of fuel into a suitable container.

Required facts for scoring:

- `tm280_10:table:3-1:2:r6`: 3-10
- `tm280_10:3-10:step-a:2:step-p3:2`: Open fuel draincock (4) and allow approximately 1 pint (0.47 L) of fuel to drain into a suitable container.

Evidence:

- `tm280_10:table:3-1:2:r6`, PDF page 282: Drain fuel filter (para. 3-10).
- `tm280_10:3-10`, PDF page 291: 3-10. FUEL FILTER MAINTENANCE
- `tm280_10:3-10:step-a:2:step-p3:2`, PDF page 291: Open fuel draincock (4) and allow approximately 1 pint (0.47 L) of fuel to drain into a suitable container.

Limits:

- Operator troubleshooting reference and selected instruction only; this is not a complete repair chain.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-rough-running-element-cleaning

The engine is misfiring or low on power and the intake filter is restricted. In an emergency, which service paragraph applies, and which way should I hold the element while tapping out the dirt?

Expected answer for review: Table 3-1 refers to paragraph 3-15 for emergency air-cleaner servicing. Hold the filter element with its open end facing the ground.

Required facts for scoring:

- `tm280_10:table:3-1:2:r6`: 3-15
- `tm280_10:3-15:step-c:2:step-p1:2`: Hold filter element (1) so open end faces ground.

Evidence:

- `tm280_10:table:3-1:2:r6`, PDF page 282: If emergency situation exists, clean air cleaner element (para. 3-15).
- `tm280_10:3-15`, PDF page 296: 3-15. AIR CLEANER SERVICING (EMERGENCY PROCEDURE)
- `tm280_10:3-15:step-c:2:step-p1:2`, PDF page 298: Hold filter element (1) so open end faces ground.

Limits:

- Operator troubleshooting reference and selected instruction only; this is not a complete repair chain.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-all-range-slip-level-check

The transmission slips in every range. Which fluid-check procedure is referenced, and how should I position the controls before taking the level reading?

Expected answer for review: Table 3-1 refers to paragraph 3-19. With the service brake depressed, move the transmission lever through all operating ranges and reverse, then check the level in neutral with the parking brake applied.

Required facts for scoring:

- `tm280_10:table:3-1:3:r13`: 3-19
- `tm280_10:3-19:step-c:2`: While depressing service brake pedal, move transmission shift lever through all operating ranges and "R" (reverse) before checking fluid level in "N" (neutral) with parking brake applied.

Evidence:

- `tm280_10:table:3-1:3:r13`, PDF page 283: Check for low fluid level (para. 3-19).
- `tm280_10:3-19`, PDF page 302: 3-19. TRANSMISSION FLUID SERVICING
- `tm280_10:3-19:step-c:2`, PDF page 302: While depressing service brake pedal, move transmission shift lever through all operating ranges and "R" (reverse) before checking fluid level in "N" (neutral) with parking brake applied.

Limits:

- Operator troubleshooting reference and selected instruction only; this is not a complete repair chain.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-all-ambulance-lights-normal

None of the ambulance compartment lights will come on. For the control-position check in troubleshooting, which paragraph applies, and what does it say should illuminate when the interior switch is put in its normal position?

Expected answer for review: Table 3-1 refers to paragraph 2-61. With the interior switch in NORMAL, the blackout lights should illuminate.

Required facts for scoring:

- `tm280_10:table:3-1:6:r26`: 2-61
- `tm280_10:2-61:step-b:2:step-p1:2`: Place interior light switch (1) on electrical control panel (3) in "NORMAL" position. The blackout lights will illuminate.

Evidence:

- `tm280_10:table:3-1:6:r26`, PDF page 286: Place interior light switch in proper position (para. 2-61).
- `tm280_10:2-61`, PDF page 259: 2-61. AMBULANCE INTERIOR ELECTRICAL CONTROLS
- `tm280_10:2-61:step-b:2:step-p1:2`, PDF page 259: Place interior light switch (1) on electrical control panel (3) in "NORMAL" position. The blackout lights will illuminate.

Limits:

- Operator troubleshooting reference and selected instruction only; this is not a complete repair chain.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-ambulance-spotlight-bulb-base

The spotlight in an M996 ambulance is still out after the switch checks. If inspection shows its bulb needs changing, which paragraph is referenced, and what should I disconnect before removing the lens screws?

Expected answer for review: Table 3-1 refers to paragraph 3-28. For the illustrated M996/M996A1 spotlight procedure, remove the base from its wall socket before removing the lens assembly screws.

Required facts for scoring:

- `tm280_10:table:3-1:6:r29`: 3-28
- `tm280_10:3-28:step-d:2:step-p1:2`: Remove base (8) from wall socket (7).

Evidence:

- `tm280_10:table:3-1:6:r29`, PDF page 286: Replace bulb with known serviceable bulb (para. 3-28).
- `tm280_10:3-28`, PDF page 318: 3-28. AMBULANCE INTERIOR LIGHT BULB REPLACEMENT
- `tm280_10:3-28:step-d:2:step-p1:2`, PDF page 318: Remove base (8) from wall socket (7).
- `tm280_10:3-28:step-d:2:note`, PDF page 318: This procedure covers M996 and M996A1 spotlight bulb replacement for M996 and M996A1 vehicles.
- `tm280_10:3-28:step-d:2:step-p2:2`, PDF page 318: Remove four screws (6) securing lens assembly (11) to base (8) and remove lens assembly (11).

Limits:

- Operator troubleshooting reference and selected instruction only; this is not a complete repair chain.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-ambulance-spotlight-switch

The ambulance ceiling lamps work but the spotlight does not. Which operating paragraph is referenced for the switch check, and where is the switch I should engage?

Expected answer for review: Table 3-1 refers to paragraph 2-61. Activate the spotlight with the switch on the back of the spotlight assembly.

Required facts for scoring:

- `tm280_10:table:3-1:6:r29`: 2-61
- `tm280_10:2-61:step-b:2:step-p3:2`: To activate spotlights, engage switch on back of spotlight assembly.

Evidence:

- `tm280_10:table:3-1:6:r29`, PDF page 286: Place spotlight switch in proper position (para. 2-61).
- `tm280_10:2-61`, PDF page 259: 2-61. AMBULANCE INTERIOR ELECTRICAL CONTROLS
- `tm280_10:2-61:step-b:2:step-p3:2`, PDF page 259: To activate spotlights, engage switch on back of spotlight assembly.

Limits:

- Operator troubleshooting reference and selected instruction only; this is not a complete repair chain.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-ambulance-cooling-engine-running

The air conditioning in an M997 ambulance is performing poorly. Following the operating-control reference in troubleshooting, which paragraph should I use, and can its compressor operate with the engine stopped?

Expected answer for review: Table 3-1 refers to paragraph 2-61 for operating controls. The engine must be running to operate the air-conditioner compressor.

Required facts for scoring:

- `tm280_10:table:3-1:7:r30`: 2-61
- `tm280_10:2-61:step-a:2`: The engine must be running to operate the air-conditioner compressor.

Evidence:

- `tm280_10:table:3-1:7:r30`, PDF page 287: Set operating controls (para. 2-61).
- `tm280_10:2-61`, PDF page 259: 2-61. AMBULANCE INTERIOR ELECTRICAL CONTROLS
- `tm280_10:2-61:step-a:2`, PDF page 259: The engine must be running to operate the air-conditioner compressor.

Limits:

- Operator troubleshooting reference and selected instruction only; this is not a complete repair chain.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-ambulance-outlet-isolate

The ambulance DC outlet voltage is outside the range in the periodic inspection. Which troubleshooting section is referenced, and what does it say to isolate before looking for the defective component?

Expected answer for review: The inspection sends the technician to paragraph 2-39, Ambulance Electrical System Tests. Its general troubleshooting rules say to isolate the system where the malfunction occurs before locating the defective component.

Required facts for scoring:

- `tm280_20_1:table:2-1:20`: 2-39
- `tm280_20_1:2-39:2:step-p5:2`: Always isolate the system where the malfunction occurs and then locate the defective component.

Evidence:

- `tm280_20_1:table:2-1:20`, PDF page 115: Reefer to para. 2-39, electrical troubleshooting, if voltage is not within the specified range.
- `tm280_20_1:2-39:2`, PDF page 599: 2-39. AMBULANCE ELECTRICAL SYSTEM TESTS
- `tm280_20_1:2-39:2:step-p5:2`, PDF page 599: Always isolate the system where the malfunction occurs and then locate the defective component.

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_1:2-39 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_1:2-39:2; traversal must resolve that alias before scoring.
- This question uses the text-only inspection and general troubleshooting rules; graphic diagnostic branches and ambulance variants outside the listed inspection are not assessed.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-transmission-electronic-codes

I reached the transmission tests but the truck has the electronically controlled four-speed unit. Where does the manual redirect me, and what must I do before disconnecting the battery?

Expected answer for review: The 3L80 test introduction redirects a 4L80-E vehicle to paragraph 2-35. Its caution says to record the Trouble Codes before disconnecting the battery because disconnecting it loses the diagnostic test codes.

Required facts for scoring:

- `tm280_20_1:2-34:2`: 2-35
- `tm280_20_1:2-35:2:caution`: Do not disconnect battery without recording Trouble Codes.

Evidence:

- `tm280_20_1:2-34:2`, PDF page 504: (4L80-E) Transmission system tests, refer to (para. 2-35).
- `tm280_20_1:2-35:2`, PDF page 515: 2-35. TRANSMISSION SYSTEM TESTS (4L80-E)
- `tm280_20_1:2-35:2:caution`, PDF page 515: Do not disconnect battery without recording Trouble Codes. Failure to do so will result in loss of diagnostic test codes.

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_1:2-35 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_1:2-35:2; traversal must resolve that alias before scoring.
- The vehicle in the question has a 4L80-E transmission. This tests the text redirect and caution, not a graphic diagnostic branch.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-steering-test-rpm-setting

While setting up the steering-system analyzer test, I am told to connect STE/ICE-R to measure engine speed. Which reference is given, and what TEST SELECT setting does its engine-speed test use?

Expected answer for review: The steering test refers to paragraph 2-43. The Engine RPM (Average) test instructs setting the TEST SELECT switches to 10.

Required facts for scoring:

- `tm280_20_1:2-37:2:step-b:5:2:step-11:2`: 2-43
- `tm280_20_1:2-43:2:step-1:2`: Set TEST SELECT switches to 10

Evidence:

- `tm280_20_1:2-37:2:step-b:5:2:step-11:2`, PDF page 573: Connect STE/ICE-R to vehicle diagnostic connector and set for measuring RPM (para. 2-43).
- `tm280_20_1:2-43:2`, PDF page 830: 2-43. STE/ICE-R TEST PROCEDURES
- `tm280_20_1:2-43:2:step-1:2`, PDF page 831: Set TEST SELECT switches to 10

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_1:2-43 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_1:2-43:2; traversal must resolve that alias before scoring.
- This tests a text setup step and the referenced RPM test instruction; interpreting graphic troubleshooting is outside scope.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-oil-adapter-filter-followon

I have replaced the engine oil-filter adapter. Which follow-on paragraph covers fitting the filter, and how much should I turn it after the gasket first contacts the adapter?

Expected answer for review: The adapter replacement task sends filter installation to paragraph 3-5. Hand-tighten the filter until its gasket contacts the adapter, then tighten an additional 1/2 to 3/4 turn by hand.

Required facts for scoring:

- `tm280_20_2:3-4:step-b:3:2:step-2:2`: 3-5
- `tm280_20_2:3-5:2:step-c:3:2:step-2:2`: Install oil filter (1) on oil filter adapter (2) and tighten by hand until gasket contacts filter adapter (2). Tighten additional 1/2-3/4 turn by hand.

Evidence:

- `tm280_20_2:3-4:step-b:3:2:step-2:2`, PDF page 25: FOLLOW-ON TASK: Install engine oil filter (para. 3-5).
- `tm280_20_2:3-5:2`, PDF page 26: 3-5. ENGINE OIL SERVICE
- `tm280_20_2:3-5:2:step-c:3:2:step-2:2`, PDF page 26: Install oil filter (1) on oil filter adapter (2) and tighten by hand until gasket contacts filter adapter (2). Tighten additional 1/2-3/4 turn by hand.

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_2:3-5 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_2:3-5:2; traversal must resolve that alias before scoring.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-oil-pan-starter-support

The oil-pan replacement setup requires the starter to be removed. Which paragraph is referenced, and what handling precaution does that paragraph give for removing and installing the starter?

Expected answer for review: The oil-pan setup refers to paragraph 4-8. The starter must be supported during removal and installation to avoid personnel injury or equipment damage.

Required facts for scoring:

- `tm280_20_2:3-6:2:step-a:3:2`: 4-8
- `tm280_20_2:4-8:2:step-b:2`: Starter must be supported during removal and installation.

Evidence:

- `tm280_20_2:3-6:2:step-a:3:2`, PDF page 28: Starter removed (para. 4-8).
- `tm280_20_2:4-8:2`, PDF page 242: 4-8. STARTER REPLACEMENT
- `tm280_20_2:4-8:2:step-b:2`, PDF page 242: Starter must be supported during removal and installation. Failure to support starter may cause injury to personnel or damage to equipment.

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_2:4-8 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_2:4-8:2; traversal must resolve that alias before scoring.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-drainage-bracket-dust-unloader

Once the air-cleaner drainage bracket is installed, which follow-on paragraph is listed, and what clamp torque does it give for refitting the dust unloader?

Expected answer for review: The drainage-bracket task refers to paragraph 3-12 for installing the air-cleaner assembly. In that procedure, the dust-unloader clamp is tightened to 45-50 lb-in. (5-6 N.m).

Required facts for scoring:

- `tm280_20_2:3-21:2:step-b:3:2`: 3-12
- `tm280_20_2:3-12:2:step-10:2`: Install dust unloader (16) on air cleaner assembly (9) and tighten clamp (15) to 45-50 lb-in. (5-6 N.m).

Evidence:

- `tm280_20_2:3-21:2:step-b:3:2`, PDF page 54: FOLLOW-ON TASK: Install air cleaner assembly (para. 3-12).
- `tm280_20_2:3-12:2`, PDF page 41: 3-12. AIR CLEANER ASSEMBLY AND DUST UNLOADER MAINTENANCE (Cont'd)
- `tm280_20_2:3-12:2:step-10:2`, PDF page 41: Install dust unloader (16) on air cleaner assembly (9) and tighten clamp (15) to 45-50 lb-in. (5-6 N.m).

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_2:3-12 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_2:3-12:2; traversal must resolve that alias before scoring.
- The actual numbered paragraph is retained as a continuation at physical PDF page 41; only its dust-unloader installation step is used, not the following filter-element servicing task merged later in parsed nodes.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-return-check-valve-air-horn

I have finished servicing the injection-pump return-hose check valve. Which follow-on paragraph covers refitting the air horn, and how should its mounting-screw threads be prepared?

Expected answer for review: The check-valve task refers to paragraph 3-14 for installing the air horn. Coat the mounting-screw threads with sealing compound before installing them.

Required facts for scoring:

- `tm280_20_2:3-35:3`: 3-14
- `tm280_20_2:3-14:2:step-b:3:2:step-3:2`: Coat threads of screws (2) with sealing compound.

Evidence:

- `tm280_20_2:3-35:3`, PDF page 89: FOLLOW-ON TASKS: Install air horn assembly (para. 3-14).
- `tm280_20_2:3-14:2`, PDF page 46: 3-14. AIR HORN REPLACEMENT
- `tm280_20_2:3-14:2:step-b:3:2:step-3:2`, PDF page 46: Coat threads of screws (2) with sealing compound. Install air horn (5) on intake manifold (7) with two flat washers (4), washers (3), and screws (2). Tighten screws (2) to 40-45 lb-in. (5-6 N•m).

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_2:3-14 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_2:3-14:2; traversal must resolve that alias before scoring.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-filter-element-bleed-endpoint

After changing the fuel-filter element, which follow-on paragraph should I use to bleed it, and what observation tells me to remove the bleeder tool and replace the bleed screw?

Expected answer for review: The element task refers to paragraph 3-32. In the bleeding instructions, crank and watch the fuel; remove the bleeder tool and replace the bleed screw when air bubbles stop coming through the line.

Required facts for scoring:

- `tm280_20_2:3-33:3:step-c:2:step-7:2`: 3-32
- `tm280_20_2:3-32:2:step-c:3:2:step-5:2`: When air bubbles stop coming through the line, remove bleeder tool and replace bleed screw (6).

Evidence:

- `tm280_20_2:3-33:3:step-c:2:step-7:2`, PDF page 85: FOLLOW-ON TASK: Bleed fuel filter (para. 3-32).
- `tm280_20_2:3-32:2`, PDF page 82: 3-32. FUEL FILTER MAINTENANCE
- `tm280_20_2:3-32:2:step-c:3:2:step-5:2`, PDF page 83: Crank engine and watch fuel. When air bubbles stop coming through the line, remove bleeder tool and replace bleed screw (6). Dispose of fuel in accordance with local SOP.

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_2:3-32 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_2:3-32:2; traversal must resolve that alias before scoring.
- The selected bleeding observation is not the full fuel-handling or engine-cranking procedure; the optional bleeder tool is used for the question.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-muffler-tailpipe-fasteners

On a vehicle covered by the muffler-and-insulator task, excluding M1123 and A2 vehicles, which follow-on paragraph covers the tailpipe, and what torque is specified for its three locknuts at the muffler?

Expected answer for review: The muffler-and-insulator task refers to paragraph 3-47 for tailpipe installation. Tighten the three tailpipe-to-muffler locknuts to 26 lb-ft (35 N.m).

Required facts for scoring:

- `tm280_20_2:3-48:2:step-b:3:2:step-4:2`: 3-47
- `tm280_20_2:3-47:3:step-b:2:step-1:2`: Tighten locknuts (9) to 26 lb-ft (35 N.m).

Evidence:

- `tm280_20_2:3-48:2:step-b:3:2:step-4:2`, PDF page 111: FOLLOW-ON TASK: Install tailpipe (para. 3-47).
- `tm280_20_2:3-47:3`, PDF page 109: 3-47. TAILPIPE REPLACEMENT (Cont’d)
- `tm280_20_2:3-47:3:step-b:2:step-1:2`, PDF page 109: Install gasket (8) and tailpipe (1) on muffler (7) with three washers (6), capscrews (5), washers (6), and locknuts (9). Tighten locknuts (9) to 26 lb-ft (35 N.m).

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_2:3-47 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_2:3-47:3; traversal must resolve that alias before scoring.
- The originating muffler-and-insulator task excludes M1123 and A2 vehicles; the question preserves that scope. The selected tailpipe step is on the continuation page of the same numbered paragraph.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-crossover-rear-heat-shield

After replacing the exhaust crossover pipe, which follow-on paragraph covers the rear heat shield, and what does it use to attach the clamp and shield to the transmission dipstick tube?

Expected answer for review: The crossover-pipe task refers to paragraph 3-54 for the right exhaust-manifold rear heat shield. The clamp and rear heat shield attach to the transmission dipstick tube with a capscrew and locknut.

Required facts for scoring:

- `tm280_20_2:3-50:2:step-b:3:2:step-5:2`: 3-54
- `tm280_20_2:3-54:2:step-b:3:2:step-2:2`: Install clamp (1) and rear heat shield (7) on transmission dipstick tube (3) with capscrew (2) and locknut (6).

Evidence:

- `tm280_20_2:3-50:2:step-b:3:2:step-5:2`, PDF page 115: Install right exhaust manifold rear heat shield (para. 3-54).
- `tm280_20_2:3-54:2`, PDF page 120: 3-54. RIGHT EXHAUST MANIFOLD REAR HEAT SHIELD REPLACEMENT
- `tm280_20_2:3-54:2:step-b:3:2:step-2:2`, PDF page 120: Install clamp (1) and rear heat shield (7) on transmission dipstick tube (3) with capscrew (2) and locknut (6).

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_2:3-54 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_2:3-54:2; traversal must resolve that alias before scoring.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-radiator-refill-heater-valve

After radiator and fan-shroud work, which follow-on paragraph covers refilling the cooling system, and what positions should the radiator draincock and heater control be in before filling?

Expected answer for review: The radiator task refers to paragraph 3-60. Before filling, close the radiator draincock and open the heater control valve by pulling the dashboard TEMP knob to MAX.

Required facts for scoring:

- `tm280_20_2:3-61:3:step-12:2`: 3-60
- `tm280_20_2:3-60:2:step-d:3:2:step-1:2`: Ensure radiator draincock (4) is closed and heater control valve (3) is open (pull “TEMP” knob on dash to “MAX” position).

Evidence:

- `tm280_20_2:3-61:3:step-12:2`, PDF page 137: Fill cooling system (para. 3-60).
- `tm280_20_2:3-60:2`, PDF page 130: 3-60. COOLING SYSTEM SERVICING
- `tm280_20_2:3-60:2:step-d:3:2:step-1:2`, PDF page 130: Ensure radiator draincock (4) is closed and heater control valve (3) is open (pull “TEMP” knob on dash to “MAX” position).

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_2:3-60 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_2:3-60:2; traversal must resolve that alias before scoring.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-oil-cooler-steering-lines

After fitting the oil cooler, which follow-on paragraph covers reinstalling the steering cooler, and what torque does it give for the two hose clamps?

Expected answer for review: The oil-cooler task refers to paragraph 8-28 for the power-steering cooler. Tighten its two hose clamps to 35-45 lb-in. (4-5 N·m).

Required facts for scoring:

- `tm280_20_2:3-8:step-c:3:2:step-6:2`: 8-28
- `tm280_20_2:8-28:3:step-2:2`: Tighten clamps (4) 35-45 lb-in. (4-5 N·m).

Evidence:

- `tm280_20_2:3-8:step-c:3:2:step-6:2`, PDF page 33: Install power steering cooler (para. 8-28).
- `tm280_20_2:8-28:3`, PDF page 891: 8-28. POWER STEERING COOLER REPLACEMENT (Cont’d)
- `tm280_20_2:8-28:3:step-2:2`, PDF page 891: Connect two hoses (2) and (3) to cooler (8) with two clamps (4). Tighten clamps (4) 35-45 lb-in. (4-5 N·m).

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_2:8-28 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_2:8-28:3; traversal must resolve that alias before scoring.
- Only the cooler hose installation on physical PDF page 891 is used. The following bleeding task is merged later under the same parsed continuation and is not evidence for this question.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-tank-vent-propeller-inspection

For a basic vehicle covered by the rear-propeller-shaft task, after replacing the tank filler-spout vent line, which follow-on paragraph is listed and what visible shaft damage calls for replacement?

Expected answer for review: The filler-spout vent-line task refers to paragraph 6-4 for reinstalling the rear propeller shaft. That paragraph says to inspect for cracks and dents and replace the shaft if cracked or dented.

Required facts for scoring:

- `tm280_20_2:3-29:3`: 6-4
- `tm280_20_2:6-4:2:step-b:3:2:step-1:2`: Inspect propeller shaft (5) for cracks and dents. Replace if cracked or dented.

Evidence:

- `tm280_20_2:3-29:3`, PDF page 79: FOLLOW-ON TASK: Install rear propeller shaft (para. 6-4).
- `tm280_20_2:6-4:2`, PDF page 638: 6-4. REAR PROPELLER SHAFT MAINTENANCE
- `tm280_20_2:6-4:2:step-b:3:2:step-1:2`, PDF page 638: Inspect propeller shaft (5) for cracks and dents. Replace if cracked or dented.

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_2:6-4 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_2:6-4:2; traversal must resolve that alias before scoring.
- Paragraph 6-4 applies to all except M1097, A1 and A2 series; the question is bounded to a basic vehicle within that applicability. Attachment differences for USBL effective 44825 and above are not inferred.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-fuel-pump-ground-first

Before replacing the mechanical fuel pump, which paragraph is referenced for disconnecting the battery, and what cable-disconnection order and switch position does it require?

Expected answer for review: The fuel-pump setup refers to paragraph 4-73. Disconnect both ground cables first and ensure all switches are OFF before disconnecting.

Required facts for scoring:

- `tm280_20_2:3-23:2:step-b:2`: 4-73
- `tm280_20_2:4-73:2:step-i:2`: When removing battery cable clamps, disconnect both ground cables first. Ensure all switches are in OFF position before disconnecting.

Evidence:

- `tm280_20_2:3-23:2:step-b:2`, PDF page 56: Battery ground cable disconnected (para. 4-73).
- `tm280_20_2:4-73:2`, PDF page 354: 4-73. BATTERY CABLE MAINTENANCE
- `tm280_20_2:4-73:2:step-i:2`, PDF page 354: When removing battery cable clamps, disconnect both ground cables first. Ensure all switches are in OFF position before disconnecting.

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_2:4-73 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_2:4-73:2; traversal must resolve that alias before scoring.
- The quoted battery warning requires both ground cables to be disconnected first; all applicable fuel-handling precautions remain in the full fuel-pump task.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-filter-bleed-transducer-seal

At the start of fuel-filter bleeding, which paragraph covers refitting the pressure sensor, and what must be applied to its threads before installation?

Expected answer for review: The bleeding task refers transducer installation to paragraph 4-26. Apply sealing compound to the fuel-pressure-transducer threads before installing it.

Required facts for scoring:

- `tm280_20_2:3-32:2:step-c:3:2:step-1:2`: 4-26
- `tm280_20_2:4-26:2:step-b:3:2:step-1:2`: Apply sealing compound to threads of fuel pressure transducer (1).

Evidence:

- `tm280_20_2:3-32:2:step-c:3:2:step-1:2`, PDF page 83: Install fuel pressure transducer (para. 4-26).
- `tm280_20_2:4-26:2`, PDF page 283: 4-26. FUEL PRESSURE TRANSDUCER REPLACEMENT
- `tm280_20_2:4-26:2:step-b:3:2:step-1:2`, PDF page 283: Apply sealing compound to threads of fuel pressure transducer (1).

Limits:

- Bounded explicit maintenance-manual cross-reference and selected text instruction only; no full repair chain or diagnosis is established.
- Only the quoted text instructions are assessed; this is not the complete service procedure or its full safety requirements.
- The stored reference points to the canonical tm280_20_2:4-26 alias, which is a table-of-contents entry. Evidence uses the actual numbered procedure tm280_20_2:4-26:2; traversal must resolve that alias before scoring.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-surge-tank-stock-replacement

The four-quart surge tank is no longer available from stock. Which larger tank does the replacement note identify, and what NSN does the catalogue give for that replacement?

Expected answer for review: When four-quart tank 12340062 stocks are exhausted, the maintenance note identifies four-and-one-half-quart tank 12340061 as the replacement. The catalogue gives that tank NSN 2930012565350. This identifies the documented stock replacement and does not establish universal vehicle fit.

Required facts for scoring:

- `tm280_20_2:3-64:2:step-b:2:note`: the four and one-half quart surge tank (12340061)
- `tm280_24p_1:parts:r606`: 2930012565350

Evidence:

- `tm280_20_2:3-64:2:step-b:2:note`, PDF page 140: When current stocks of the four-quart surge tank (12340062) are exhausted, the four and one-half quart surge tank (12340061) will be provided in ita place.
- `tm280_24p_1:parts:r606`, PDF page 123: 12340061
- `tm280_24p_1:parts:r606`, PDF page 123: 2930012565350

Parsed catalogue fields for `tm280_24p_1:parts:r606` (check effectivity and fit against the PDF):

- ITEM NO: 3
- SMR CODE: PAOZZ
- NSN: 2930012565350
- CAGE: 19207
- PART NUMBER: 12340061
- DESCRIPTION: TANK,RADIATOR,OVERF
- USABLE ON CODE: 
- QTY: 1

Limits:

- Maintenance instruction to catalogue identity only; no fault-to-maintenance repair chain is claimed.
- Matching the part number and NSN does not establish universal vehicle fit or waive the maintenance instruction conditions.
- The note conditions this stock replacement on exhaustion of four-quart tank 12340062.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.

## review-surge-hose-trim-adaptation

With surge tank 12340061 fitted, which surge-tank-to-lower-radiator hose does the installation note cover, what preparation does it require, and what NSN does the catalogue list for that hose?

Expected answer for review: For a vehicle equipped with tank 12340061, the note identifies hose 12339163 and requires cutting approximately four inches from its surge-tank end before installation. The catalogue gives hose 12339163 NSN 4720011961636. Its row says USE WITH OLD TANK P/N 12340062; the maintenance note supplies the stated trimming condition for the newer tank, not a claim of unconditional fit.

Required facts for scoring:

- `tm280_20_2:3-70:2:step-b:8:2`: surge tank-to-lower-radiator tube hose (12339163)
- `tm280_20_2:3-70:2:step-b:8:2`: cut approximately four inches from surge tank end of hose prior to installation.
- `tm280_24p_1:parts:r610`: 4720011961636

Evidence:

- `tm280_20_2:3-70:2:step-b:8:2`, PDF page 150: If the vehicle is equipped with surge tank (12340061) and surge tank-to-lower-radiator tube hose (12339163) is received, cut approximately four inches from surge tank end of hose prior to installation.
- `tm280_24p_1:parts:r610`, PDF page 123: 12339163
- `tm280_24p_1:parts:r610`, PDF page 123: 4720011961636

Parsed catalogue fields for `tm280_24p_1:parts:r610` (check effectivity and fit against the PDF):

- ITEM NO: 7
- SMR CODE: PAOZZ
- NSN: 4720011961636
- CAGE: 19207
- PART NUMBER: 12339163
- DESCRIPTION: HOSE,PREFORMED USE WITH OLD TANK P/N 12340062
- USABLE ON CODE: 
- QTY: 1

Limits:

- Maintenance instruction to catalogue identity only; no fault-to-maintenance repair chain is claimed.
- Matching the part number and NSN does not establish universal vehicle fit or waive the maintenance instruction conditions.
- The catalogue row describes the unmodified hose for old tank 12340062; this question concerns only the documented four-inch trim adaptation with tank 12340061.
- The source is physical PDF page 150, printed paragraph 3-73. Its preserved parsed node ID and breadcrumb currently use 3-70; the literal note and physical-page evidence are checked, and no 3-70 paragraph-reference resolution is claimed.

Client disposition: source_checked_pending_client. Full benchmark freeze: pending.
