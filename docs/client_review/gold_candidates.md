# Choice B questions and source evidence

Choice B: bounded manual relationships. Full repair chains are not required.
Client acceptance is shown per case. The full benchmark is not frozen or approved.
Batch 2 must be reviewed before M3. Wording was prepared with AI assistance.
Expected answers are review notes, not complete service procedures.
This file contains 50 cases: 25 accepted and 25 pending review.
PDF pages below are one-based physical file pages, not printed manual page labels.

| ID | Scope | Type | Batch | Client review |
|---|---|---|---|---|
| review-no-crank-cable | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-no-start-purge | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-smoke-air-cleaner | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-overheat-fan | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-overheat-coolant | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-oil-level-engine-off | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-fill-tube-fluid-level | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-transfer-shift-precautions | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-parking-brake-start | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-wheel-lug-follow-up | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-hard-steering-fluid | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-winch-reset | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-mount-unlock | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-ambulance-fuse | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-ceiling-bulb-safety | operator_reference_and_instruction | multi_hop | 1 | client_accepted |
| review-water-pump-62 | maintenance_catalogue_identity | relational | 1 | client_accepted |
| review-water-pump-65 | maintenance_catalogue_identity | relational | 1 | client_accepted |
| review-fuel-tank-branch | maintenance_catalogue_identity | relational | 1 | client_accepted |
| review-right-cable-bracket | maintenance_catalogue_identity | relational | 1 | client_accepted |
| review-left-cable-bracket | maintenance_catalogue_identity | relational | 1 | client_accepted |
| review-retaining-nut-upgrade | maintenance_catalogue_identity | relational | 1 | client_accepted |
| review-alternator-pulley | maintenance_catalogue_identity | relational | 1 | client_accepted |
| review-brake-adapter-access | maintenance_catalogue_identity | relational | 1 | client_accepted |
| review-cover-basic-front-left | maintenance_catalogue_identity | relational | 1 | client_accepted |
| review-cover-basic-front-right | maintenance_catalogue_identity | relational | 1 | client_accepted |
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

## review-no-crank-cable

The truck won't turn over. If I reach the external-start procedure after the initial checks, what warning applies before connecting the cable?

Expected answer for review: Table 3-1 refers to paragraph 2-23, Slave Starting Operation. Its warning requires all battery cables in the disabled vehicle to be properly connected before the slave cable is connected.

Required facts for scoring:

- `tm280_10:table:3-1:r1`: 2-23
- `tm280_10:2-23:step-c:2`: Ensure all battery cables in disabled vehicle are properly connected before connecting slave cable.

Evidence:

- `tm280_10:table:3-1:r1`, PDF page 281: Attempt to slave-start vehicle (para. 2-23).
- `tm280_10:2-23`, PDF page 179: 2-23. SLAVE STARTING OPERATION
- `tm280_10:2-23:step-c:2`, PDF page 179: Ensure all battery cables in disabled vehicle are properly connected before connecting slave cable.

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-no-start-purge

The engine turns over but won't start after running out of fuel. Which procedure does troubleshooting refer me to for air in the fuel system, and what tells me to stop cranking during the purge?

Expected answer for review: The fault row refers to paragraph 3-10, Fuel Filter Maintenance. In its air-purging procedure, crank until the rag over the filter outlet is wet with fuel. This is a selected check, not the full fuel-handling procedure.

Required facts for scoring:

- `tm280_10:table:3-1:r3`: 3-10
- `tm280_10:3-10:step-b:2:step-p4:2`: Crank engine until rag is wet with fuel.

Evidence:

- `tm280_10:table:3-1:r3`, PDF page 281: Purge fuel system of air (para. 3-10).
- `tm280_10:3-10`, PDF page 291: 3-10. FUEL FILTER MAINTENANCE
- `tm280_10:3-10:step-b:2:step-p4:2`, PDF page 291: Crank engine until rag is wet with fuel.

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-smoke-air-cleaner

The warm engine is smoking heavily and the air cleaner is restricted. In an emergency, which service instructions apply, and what restriction do they place on running the engine?

Expected answer for review: The fault row permits emergency air-cleaner servicing under paragraph 3-15; outside an emergency it directs notification of unit maintenance. The servicing caution prohibits operating the engine without the air-cleaner element.

Required facts for scoring:

- `tm280_10:table:3-1:2:r5`: 3-15
- `tm280_10:3-15:step-a:2:caution`: Do not operate engine without air cleaner element.

Evidence:

- `tm280_10:table:3-1:2:r5`, PDF page 282: Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance.
- `tm280_10:3-15`, PDF page 296: 3-15. AIR CLEANER SERVICING (EMERGENCY PROCEDURE)
- `tm280_10:3-15:step-a:2:caution`, PDF page 296: Do not operate engine without air cleaner element.

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-overheat-fan

The engine is overheating during an emergency and its fan is not running. Which override procedure is referenced, and what must happen before disconnecting the control module?

Expected answer for review: The fault row references paragraph 3-23, Emergency Fan Clutch Override. Its note requires stopping the engine before disconnecting the time-delay module. It does not prove that a fan or pump must be replaced.

Required facts for scoring:

- `tm280_10:table:3-1:2:r7`: 3-23
- `tm280_10:3-23:step-b:2:note`: Stop engine (para. 2-12) prior to disconnecting time delay module.

Evidence:

- `tm280_10:table:3-1:2:r7`, PDF page 282: If fan is not running, perform emergency fan clutch override procedure (para. 3-23).
- `tm280_10:3-23`, PDF page 310: 3-23. EMERGENCY FAN CLUTCH OVERRIDE
- `tm280_10:3-23:step-b:2:note`, PDF page 310: Stop engine (para. 2-12) prior to disconnecting time delay module.

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-overheat-coolant

After an overheating problem, I need to check the coolant once the engine has cooled. Which servicing paragraph is referenced, and what temperature-related warning applies when removing the cap?

Expected answer for review: Table 3-1 directs allowing the engine to cool and refers coolant servicing to paragraph 3-9. That paragraph warns to use extreme care removing the surge-tank cap if the temperature gauge reads above 165°F (74°C). This warning is not permission to open a hot pressurised system.

Required facts for scoring:

- `tm280_10:table:3-1:2:r7`: 3-9
- `tm280_10:3-9:caution`: Extreme care should be taken when removing surge tank filler cap if temperature gauge reads above 165°F (74°C).

Evidence:

- `tm280_10:table:3-1:2:r7`, PDF page 282: Allow engine to cool and check for low coolant level. Add coolant as necessary (para. 3-9).
- `tm280_10:3-9`, PDF page 290: 3-9. SERVICING COOLANT SURGE TANK
- `tm280_10:3-9:caution`, PDF page 290: Extreme care should be taken when removing surge tank filler cap if temperature gauge reads above 165°F (74°C).

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-oil-level-engine-off

The oil-pressure gauge reads low and I need to check the oil level. Which servicing instructions apply, and should the engine be running for the level check?

Expected answer for review: The fault row refers to paragraph 3-17, Engine Oil Servicing. Its note states that engine oil level is checked with the engine off. This does not establish that an oil pump has failed.

Required facts for scoring:

- `tm280_10:table:3-1:2:r8`: 3-17
- `tm280_10:3-17:step-a:2:note`: Engine oil level is checked with engine off.

Evidence:

- `tm280_10:table:3-1:2:r8`, PDF page 282: Check for low oil level (para. 3-17).
- `tm280_10:3-17`, PDF page 300: 3-17. ENGINE OIL SERVICING
- `tm280_10:3-17:step-a:2:note`, PDF page 300: Engine oil level is checked with engine off.

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-fill-tube-fluid-level

Fluid is coming out of the gearbox fill tube. When checking the possible overfill mentioned in troubleshooting, which service paragraph applies and where should the level read at normal operating temperature?

Expected answer for review: The overfill check refers to paragraph 3-19, Transmission Fluid Servicing. At normal operating temperature the level should be at the dipstick crosshatch marks. The fault row directs notifying unit maintenance if the fluid level is high.

Required facts for scoring:

- `tm280_10:table:3-1:3:r12`: 3-19
- `tm280_10:3-19:step-d:2`: At normal operating temperature, fluid level should be at crosshatch marks (3).

Evidence:

- `tm280_10:table:3-1:3:r12`, PDF page 283: Check fluid level for overfilling (para. 3-19). Notify unit maintenance if fluid level is high.
- `tm280_10:3-19`, PDF page 302: 3-19. TRANSMISSION FLUID SERVICING
- `tm280_10:3-19:step-d:2`, PDF page 302: At normal operating temperature, fluid level should be at crosshatch marks (3).

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-transfer-shift-precautions

The transfer-case lever won't shift. Which operating instructions does troubleshooting point to, and what conditions do they require before shifting it?

Expected answer for review: Table 3-1 refers to paragraph 2-11, Placing Vehicle in Motion. Its caution requires a stopped vehicle, engine off, and transmission in neutral before shifting the transfer case. Follow the complete paragraph and its operating-surface restrictions.

Required facts for scoring:

- `tm280_10:table:3-1:3:r14`: 2-11
- `tm280_10:2-11:step-a:2:caution`: Vehicle must be stopped, engine off, and transmission shift lever placed in “N” (Neutral), before transfer case can be shifted.

Evidence:

- `tm280_10:table:3-1:3:r14`, PDF page 283: Ensure proper shifting sequence is used (para. 2-11).
- `tm280_10:2-11`, PDF page 160: 2-11. PLACING VEHICLE IN MOTION
- `tm280_10:2-11:step-a:2:caution`, PDF page 160: Vehicle must be stopped, engine off, and transmission shift lever placed in “N” (Neutral), before transfer case can be shifted.

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-parking-brake-start

The parking brake won't hold. Which adjustment instructions are referenced, and what is the first preparation step before adjusting it?

Expected answer for review: The fault row refers to paragraph 3-13, Parking Brake Adjustment and Cleaning. Its first step is to chock the wheels and release the parking-brake handle. If the brake still fails to hold, the fault row directs notification of unit maintenance.

Required facts for scoring:

- `tm280_10:table:3-1:4:r18`: 3-13
- `tm280_10:3-13:step-a:2`: Chock wheels and release parking brake handle (5).

Evidence:

- `tm280_10:table:3-1:4:r18`, PDF page 284: Clean and adjust parking brake (para. 3-13) If parking brake still fails to hold vehicle, notify unit maintenance.
- `tm280_10:3-13`, PDF page 295: 3-13. PARKING BRAKE ADJUSTMENT AND CLEANING
- `tm280_10:3-13:step-a:2`, PDF page 295: Chock wheels and release parking brake handle (5).

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-wheel-lug-follow-up

I found loose wheel nuts while checking a wheel wobble. Which procedure is referenced, and is tightening them myself the end of the job?

Expected answer for review: The fault row refers to paragraph 3-26, Wheel Assembly Replacement, for tightening loose lug nuts. Its installation instructions still require unit maintenance to apply proper torque as soon as possible; operator tightening does not close that follow-up.

Required facts for scoring:

- `tm280_10:table:3-1:4:r19`: 3-26
- `tm280_10:3-26:step-b:2:step-p4:2`: Notify unit maintenance to tighten lug nuts (9) to proper torque as soon as possible.

Evidence:

- `tm280_10:table:3-1:4:r19`, PDF page 284: Tighten loose lug nuts (para. 3-26) and notify unit maintenance to properly torque lug nuts.
- `tm280_10:3-26`, PDF page 313: 3-26. WHEEL ASSEMBLY REPLACEMENT
- `tm280_10:3-26:step-b:2:step-p4:2`, PDF page 314: Notify unit maintenance to tighten lug nuts (9) to proper torque as soon as possible.

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-hard-steering-fluid

The steering is hard to turn and I am checking its fluid reservoir. Which service instructions apply, and at what dipstick reading is fluid required whether the engine is warm or cool?

Expected answer for review: The fault row refers to paragraph 3-20, Power Steering Fluid Servicing. Its level-check instruction requires adding fluid if the reading is below ADD in either warm or cool conditions. The normal ranges differ by temperature; this does not diagnose a failed steering component.

Required facts for scoring:

- `tm280_10:table:3-1:5:r22`: 3-20
- `tm280_10:3-20:step-b:2`: In either condition, fluid must be added if level reads below "ADD” mark.

Evidence:

- `tm280_10:table:3-1:5:r22`, PDF page 285: Check power steering reservoir for low fluid level (para. 3-20).
- `tm280_10:3-20`, PDF page 303: 3-20. POWER STEERING FLUID SERVICING
- `tm280_10:3-20:step-b:2`, PDF page 303: Pull out cap/dipstick (5) and check steering fluid level. If engine is warm, level should be between "HOT” and “COLD” marks. If engine is cool, level should be between “ADD" and “COLD" marks. In either condition, fluid must be added if level reads below "ADD” mark.

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-winch-reset

The winch stopped while I was using it. Which operating instructions does troubleshooting reference, and when do those instructions require maintenance notification if it stays stopped?

Expected answer for review: The fault row refers to paragraph 2-26, Electric Winch Operation. Its note requires notification of unit maintenance if the winch is still inoperative after five minutes. This selected reference does not establish a replacement part or replace the complete winch safety instructions.

Required facts for scoring:

- `tm280_10:table:3-1:5:r23`: 2-26
- `tm280_10:2-26:step-d:2:note`: If after five minutes winch is still inoperative, notify unit maintenance.

Evidence:

- `tm280_10:table:3-1:5:r23`, PDF page 285: Refer to para. 2-26 for winch operation.
- `tm280_10:2-26`, PDF page 189: 2-26. ELECTRIC WINCH OPERATION
- `tm280_10:2-26:step-d:2:note`, PDF page 190: If after five minutes winch is still inoperative, notify unit maintenance.

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-mount-unlock

The weapon mount won't rotate. Which operating paragraph is referenced for checking its brake handle, and how does that paragraph say to unlock the mount?

Expected answer for review: The fault row refers to paragraph 2-54, TOW Weapon Station Operation. Its before-operation instructions say to raise the brake handle to unlock the station. This is a handle-position check, not a finding that the turret must be replaced.

Required facts for scoring:

- `tm280_10:table:3-1:5:r24`: 2-54
- `tm280_10:2-54:step-a:2:step-p3:2`: Raise weapon station brake handle (4) to unlock weapon station (9).

Evidence:

- `tm280_10:table:3-1:5:r24`, PDF page 285: Check to see if brake handle is in proper position (para. 2-54).
- `tm280_10:2-54`, PDF page 249: 2-54. TOW WEAPON STATION OPERATION
- `tm280_10:2-54:step-a:2:step-p3:2`, PDF page 249: Raise weapon station brake handle (4) to unlock weapon station (9).

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-ambulance-fuse

The regular and blackout ceiling lights on one side of the ambulance are out. If the fuse is blown, which instructions cover it and what fuse rating do they specify for that control box?

Expected answer for review: The fault row refers to paragraph 2-61, Ambulance Interior Electrical Controls, for the fuse replacement. Its fuse-replacement instructions specify 20-amp control-box fuses. This does not select a catalogue fuse or prove that the fuse is the cause without inspection.

Required facts for scoring:

- `tm280_10:table:3-1:6:r27`: 2-61
- `tm280_10:2-61:step-e:2`: All fuses in the control box are 20 amp.

Evidence:

- `tm280_10:table:3-1:6:r27`, PDF page 286: Replace fuse if blown (para. 2-61).
- `tm280_10:2-61`, PDF page 259: 2-61. AMBULANCE INTERIOR ELECTRICAL CONTROLS
- `tm280_10:2-61:step-e:2`, PDF page 260: All fuses in the control box are 20 amp.

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-ceiling-bulb-safety

One ceiling light in the ambulance has failed. If a bulb change is needed after inspection, which procedure is referenced and what must be turned off first?

Expected answer for review: The fault row refers to paragraph 3-28, Ambulance Interior Light Bulb Replacement. Its warning requires the system containing the bulb being changed to be turned off. No catalogue bulb identity is established by this reference.

Required facts for scoring:

- `tm280_10:table:3-1:6:r28`: 3-28
- `tm280_10:3-28:step-a:2:caution`: When changing light bulbs, ensure the system in which the bulb is being replaced is turned off.

Evidence:

- `tm280_10:table:3-1:6:r28`, PDF page 286: Replace bulb with known serviceable bulb (para. 3-28).
- `tm280_10:3-28`, PDF page 318: 3-28. AMBULANCE INTERIOR LIGHT BULB REPLACEMENT
- `tm280_10:3-28:step-a:2:caution`, PDF page 318: When changing light bulbs, ensure the system in which the bulb is being replaced is turned off.

Limits:

- Operator-manual reference and selected instruction only; no maintenance-task-to-catalogue chain is established.
- Selected evidence is not the complete procedure or all warnings; use the full manual for service work.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-water-pump-62

I am installing a water pump on a 6.2-litre engine from 1990 or later. Which part does the installation caution specify, and what NSN does the parts catalogue give for it?

Expected answer for review: The installation caution specifies water pump 251-591 for the 6.2L engine. Its catalogue row gives NSN 2930013535794 and says to use it with the 1990 engine and above. This answer excludes 6.5L detuned applicability, where the sources conflict.

Required facts for scoring:

- `tm280_20_2:3-76.1:3:step-c:2`: Ensure water pump P/N 251-591 is used on 6.2L engines
- `tm280_24p_1:parts:r671`: 2930013535794
- `tm280_24p_1:parts:r671`: USE WITH 1990 ENGINE AND ABOVE

Evidence:

- `tm280_20_2:3-76.1:3:step-c:2`, PDF page 156: Ensure water pump P/N 251-591 is used on 6.2L engines, or damage to equipment will result.
- `tm280_24p_1:parts:r671`, PDF page 133: 251-591
- `tm280_24p_1:parts:r671`, PDF page 133: 2930013535794
- `tm280_24p_1:parts:r671`, PDF page 133: USE WITH 1990 ENGINE AND ABOVE

Parsed catalogue fields for `tm280_24p_1:parts:r671` (check effectivity and fit against the PDF):

- ITEM NO: 3
- SMR CODE: PAOZZ
- NSN: 2930013535794
- CAGE: 61928
- PART NUMBER: 251-591
- DESCRIPTION: PUMP,COOLING SYSTEM 6.2 AND 6.5 DETUNED,USE WITH 1990 ENGINE AND ABOVE
- USABLE ON CODE: AVY,A11,A13,A14,A15,A20,A24,A25 A26,A27,B16,B17,B18,HVY,H11,H13,H14 H15,H16,H17,H18,H20,H21,H24,H25,H26 H27,H28,MMM
- QTY: 1

Limits:

- Only a maintenance-to-catalogue link; no fault-to-maintenance link established.
- Do not extend this to 6.5L detuned engines: the maintenance caution and catalogue descriptions differ.
- Exact part-number identity only; catalogue row does not by itself approve vehicle fit, UOC decoding, or a repair diagnosis.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-water-pump-65

For water-pump installation on the 6.5-litre engine, excluding the detuned variant, which part number is specified and what NSN does the catalogue give for it?

Expected answer for review: For the non-detuned 6.5L engine, the installation caution names water pump 12534772. Its catalogue row gives NSN 2930014446649 and describes it as PUMP,COOLING SYSTEM 6.5 LITER. The conflicting 6.5L detuned applicability is outside this question.

Required facts for scoring:

- `tm280_20_2:3-76.1:3:step-c:2`: water pump P/N 12534772
- `tm280_24p_1:parts:r672`: 2930014446649

Evidence:

- `tm280_20_2:3-76.1:3:step-c:2`, PDF page 156: Ensure water pump P/N 12534772 is used on 6.5L and 6.5L detuned engines, or damage to equipment will result.
- `tm280_24p_1:parts:r672`, PDF page 133: 12534772
- `tm280_24p_1:parts:r672`, PDF page 133: 2930014446649

Parsed catalogue fields for `tm280_24p_1:parts:r672` (check effectivity and fit against the PDF):

- ITEM NO: 3
- SMR CODE: PAOZZ
- NSN: 2930014446649
- CAGE: 7X677
- PART NUMBER: 12534772
- DESCRIPTION: PUMP,COOLING SYSTEM 6.5 LITER
- USABLE ON CODE: BVY,B15,B20,B24,B25,C17,NNN
- QTY: 1

Limits:

- Only a maintenance-to-catalogue link; no fault-to-maintenance link established.
- 6.5L detuned applicability conflicts with the description of 251-591 in the catalogue; client must resolve it before an applicability question.
- Exact part-number identity only; catalogue row does not by itself approve vehicle fit, UOC decoding, or a repair diagnosis.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-fuel-tank-branch

The fuel-tank removal notes branch into a separate baffle-removal sequence. Which tank does that branch apply to, and what NSN does the parts list give for that tank?

Expected answer for review: The removal note selects steps 8.1 through 8.5 for fuel tank 12460105. Its catalogue row gives NSN 2910014473911 and description TANK,FUEL,ENGINE. This identifies the branch, not a diagnosis that a tank needs replacing.

Required facts for scoring:

- `tm280_20_2:3-24:6:step-c:2:step-8:2`: Perform steps 8.1 through 8.5 for vehicles with fuel tank P/N 12460105.
- `tm280_24p_1:parts:r415`: 2910014473911

Evidence:

- `tm280_20_2:3-24:6:step-c:2:step-8:2`, PDF page 62: Perform steps 8.1 through 8.5 for vehicles with fuel tank P/N 12460105.
- `tm280_24p_1:parts:r415`, PDF page 95: 12460105
- `tm280_24p_1:parts:r415`, PDF page 95: 2910014473911

Parsed catalogue fields for `tm280_24p_1:parts:r415` (check effectivity and fit against the PDF):

- ITEM NO: 13
- SMR CODE: PAOZZ
- NSN: 2910014473911
- CAGE: 34623
- PART NUMBER: 12460105
- DESCRIPTION: TANK,FUEL,ENGINE
- USABLE ON CODE: BVY,B15,B20,B24,B25,C17,NNN
- QTY: 1

Limits:

- Only a maintenance-to-catalogue link; no fault-to-maintenance link established.
- Exact part-number identity only; catalogue row does not by itself approve vehicle fit, UOC decoding, or a repair diagnosis.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-right-cable-bracket

While replacing the right parking-brake cable, which clamp bracket must be installed according to the note, and what NSN does its catalogue row give?

Expected answer for review: The right cable installation note requires clamp bracket 12342965. The cited catalogue row lists the right-hand mounting bracket with that number. The selected catalogue row is marked USBL EFF 44825 AND ABOVE; matching the number does not waive that effectivity restriction. The selected catalogue row for 12342965 gives NSN 5340013942408.

Required facts for scoring:

- `tm280_20_2:7-23:2:step-b:3:2`: Ensure clamp bracket (P/N 12342965) is installed on vehicle.
- `tm280_24p_1:parts:r3980`: 5340013942408

Evidence:

- `tm280_20_2:7-23:2:step-b:3:2`, PDF page 771: Ensure clamp bracket (P/N 12342965) is installed on vehicle.
- `tm280_24p_1:parts:r3980`, PDF page 581: 12342965
- `tm280_24p_1:parts:r3980`, PDF page 581: 5340013942408

Parsed catalogue fields for `tm280_24p_1:parts:r3980` (check effectivity and fit against the PDF):

- ITEM NO: 15
- SMR CODE: PAOZZ
- NSN: 5340013942408
- CAGE: 19207
- PART NUMBER: 12342965
- DESCRIPTION: BRACKET,MOUNTING R.H. USBL EFF 44825 AND ABOVE
- USABLE ON CODE: 
- QTY: 1

Limits:

- Only a maintenance-to-catalogue link; no fault-to-maintenance link established.
- Exact part-number identity only; catalogue row does not by itself approve vehicle fit, UOC decoding, or a repair diagnosis.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-left-cable-bracket

During left parking-brake cable and mounting-bracket replacement, which clamp bracket does the installation note require, and what NSN is listed for it in the catalogue?

Expected answer for review: The left cable installation note requires clamp bracket 12342966. The cited catalogue row lists the left-hand mounting bracket with that number. The selected catalogue row is marked USBL EFF 44825 AND ABOVE; matching the number does not waive that effectivity restriction. The selected catalogue row for 12342966 gives NSN 5340013948496.

Required facts for scoring:

- `tm280_20_2:7-24:4:step-b:2:step-1:2`: Ensure clamp bracket (P/N 12342966) is installed on vehicle.
- `tm280_24p_1:parts:r3985`: 5340013948496

Evidence:

- `tm280_20_2:7-24:4:step-b:2:step-1:2`, PDF page 775: Ensure clamp bracket (P/N 12342966) is installed on vehicle.
- `tm280_24p_1:parts:r3985`, PDF page 581: 12342966
- `tm280_24p_1:parts:r3985`, PDF page 581: 5340013948496

Parsed catalogue fields for `tm280_24p_1:parts:r3985` (check effectivity and fit against the PDF):

- ITEM NO: 20
- SMR CODE: PAOZZ
- NSN: 5340013948496
- CAGE: 19207
- PART NUMBER: 12342966
- DESCRIPTION: BRACKET,MOUNTING L.H. USBL EFF 44825 AND ABOVE END OF FIGURE 155-1
- USABLE ON CODE: 
- QTY: 1

Limits:

- Only a maintenance-to-catalogue link; no fault-to-maintenance link established.
- Exact part-number identity only; catalogue row does not by itself approve vehicle fit, UOC decoding, or a repair diagnosis.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-retaining-nut-upgrade

During the geared-hub spindle-seal job I found the older four-slot retaining nut. What replacement does the note recommend, and what NSN does the catalogue give for that replacement?

Expected answer for review: The maintenance note recommends replacing four-slotted TN-07 with eight-slotted retaining nut 12342680. Its catalogue row gives NSN 5310013825031 and description NUT,PLAIN,ROUND 1-3/8. This is a documented recommendation, not a diagnosis.

Required facts for scoring:

- `tm280_20_2:6-13:2:step-b:2:step-3:2`: If four-slotted retaining nut TN-07 is present, it is recommended to replace it with eight-slotted retaining nut 12342680.
- `tm280_24p_1:parts:r3551`: 5310013825031

Evidence:

- `tm280_20_2:6-13:2:step-b:2:step-3:2`, PDF page 666: If four-slotted retaining nut TN-07 is present, it is recommended to replace it with eight-slotted retaining nut 12342680.
- `tm280_24p_1:parts:r3551`, PDF page 530: 12342680
- `tm280_24p_1:parts:r3551`, PDF page 530: 5310013825031

Parsed catalogue fields for `tm280_24p_1:parts:r3551` (check effectivity and fit against the PDF):

- ITEM NO: 19
- SMR CODE: PAOZZ
- NSN: 5310013825031
- CAGE: 19207
- PART NUMBER: 12342680
- DESCRIPTION: NUT,PLAIN,ROUND 1-3/8
- USABLE ON CODE: AVY,A11,A13,A14,A15,A20,A24,A25 A26,A27,B16,B17,B18,HVY,H11,H13,H14 H15,H16,H17,H18,H20,H21,H24,H25,H26 H27,H28,MMM
- QTY: 1

Limits:

- Only a maintenance-to-catalogue link; no fault-to-maintenance link established.
- Exact part-number identity only; catalogue row does not by itself approve vehicle fit, UOC decoding, or a repair diagnosis.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-alternator-pulley

During pulley replacement, which alternator assemblies does the 200-amp locknut note cover, and what NSN does the parts catalogue give for each assembly?

Expected answer for review: The torque note covers alternator assemblies 12447109 and 12338796-1. The catalogue maps 12447109 to NSN 2920014209968 and 12338796-1 to NSN 2920012646542; both entries are described as GENERATOR,ENGINE AC 200 AMP. This identifies the assemblies covered by the note and does not establish interchangeability or a charging-fault diagnosis.

Required facts for scoring:

- `tm280_20_2:4-3:2:step-b:3:2:step-4:2`: 200 amp alternators (12447109 or 12338796-1)
- `tm280_24p_1:parts:r886`: 2920012646542
- `tm280_24p_1:parts:r860`: 2920014209968

Evidence:

- `tm280_20_2:4-3:2:step-b:3:2:step-4:2`, PDF page 195: For 200 amp alternators (12447109 or 12338796-1), tighten locknut to 115-125 lb-ft (156-169 N m).
- `tm280_24p_1:parts:r886`, PDF page 163: 12338796-1
- `tm280_24p_1:parts:r860`, PDF page 157: 12447109
- `tm280_24p_1:parts:r886`, PDF page 163: 2920012646542
- `tm280_24p_1:parts:r860`, PDF page 157: 2920014209968

Parsed catalogue fields for `tm280_24p_1:parts:r886` (check effectivity and fit against the PDF):

- ITEM NO: 1
- SMR CODE: PAOFF
- NSN: 2920012646542
- CAGE: 19207
- PART NUMBER: 12338796-1
- DESCRIPTION: GENERATOR,ENGINE AC 200 AMP
- USABLE ON CODE: AVY,A15,B16,HVY,H15,H16
- QTY: 1

Parsed catalogue fields for `tm280_24p_1:parts:r860` (check effectivity and fit against the PDF):

- ITEM NO: 4
- SMR CODE: PAOFF
- NSN: 2920014209968
- CAGE: 19207
- PART NUMBER: 12447109
- DESCRIPTION: GENERATOR,ENGINE AC 200 AMP
- USABLE ON CODE: BVY,B15,B20,B24,B25,C17,NNN
- QTY: 1

Limits:

- Only a maintenance-to-catalogue link; no fault-to-maintenance link established.
- This does not establish that replacing the alternator repairs a charging fault.
- Exact part-number identity only; catalogue row does not by itself approve vehicle fit, UOC decoding, or a repair diagnosis.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-brake-adapter-access

The differential-cover instructions describe a special access procedure for newer, cut-away brake adapters. Which adapter number selects that procedure, and what NSN does the cited catalogue row give?

Expected answer for review: The maintenance note identifies brake adapter 10453002. A catalogue row lists that exact number as an adapter, brake valve. Several catalogue occurrences exist; no universal fit or mounting position is inferred. The selected catalogue row for 10453002 gives NSN 2530013141129.

Required facts for scoring:

- `tm280_20_2:6-21:2:step-b:2:note`: The following procedure applies to vehicles with new brake adapters, P/N 10453002.
- `tm280_24p_1:parts:r4034`: 2530013141129

Evidence:

- `tm280_20_2:6-21:2:step-b:2:note`, PDF page 684: The following procedure applies to vehicles with new brake adapters, P/N 10453002.
- `tm280_24p_1:parts:r4034`, PDF page 587: 10453002
- `tm280_24p_1:parts:r4034`, PDF page 587: 2530013141129

Parsed catalogue fields for `tm280_24p_1:parts:r4034` (check effectivity and fit against the PDF):

- ITEM NO: 22
- SMR CODE: PAFZZ
- NSN: 2530013141129
- CAGE: 22075
- PART NUMBER: 10453002
- DESCRIPTION: ADAPTER,BRAKE VALVE REAR,L.H. AND R.H
- USABLE ON CODE: AVY,A11,A13,A14,A15,A20,A24,A25 A26,A27,B16,B17,B18,HVY,H11,H13,H14 H15,H16,H17,H18,H20,H21,H24,H25,H26 H27,H28,MMM
- QTY: 2

Limits:

- Maintenance-to-catalogue identity only; no preceding fault/diagnosis chain is established.
- Multiple catalogue occurrences may differ in position or applicability. Matching the number does not establish universal fit.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-cover-basic-front-left

For a basic or A1 vehicle receiving hub 5598766 at the left-front or right-rear position, which steering-arm cover does the installation note name, and what NSN does the catalogue give for that cover?

Expected answer for review: For those hub, position, and vehicle-group conditions, the maintenance note names steering-arm cover 5591280. The selected catalogue row gives NSN 2530012035662 and description COVER,STEERING ARM L.H. The note permits retaining the existing cover if serviceable. The selected catalogue description does not establish handedness or fit for every occurrence.

Required facts for scoring:

- `tm280_20_2:6-11:2:step-b:3:2:step-2:2`: If geared hub received is P/N 5598766 and left front or right rear installation is required, replace steering arm cover P/N 5591279 with P/N 5591280 for basic and A1 vehicles
- `tm280_24p_1:parts:r3550`: 2530012035662

Evidence:

- `tm280_20_2:6-11:2:step-b:3:2:step-2:2`, PDF page 660: If geared hub received is P/N 5598766 and left front or right rear installation is required, replace steering arm cover P/N 5591279 with P/N 5591280 for basic and A1 vehicles and P/N 6005121 for M 1123 and A2 vehicles. • If geared hub received is P/N 5598767 and right front or left rear installation is required, replace steering arm cover P/N 5591280 with P/N 5591279 for basic and A1 vehicles and P/N 6005120 for M 1123 and A2 vehicles. • Use existing steering arm cover if serviceable.
- `tm280_24p_1:parts:r3550`, PDF page 530: 5591280
- `tm280_24p_1:parts:r3550`, PDF page 530: 2530012035662

Parsed catalogue fields for `tm280_24p_1:parts:r3550` (check effectivity and fit against the PDF):

- ITEM NO: 18
- SMR CODE: PAOZZ
- NSN: 2530012035662
- CAGE: 34623
- PART NUMBER: 5591280
- DESCRIPTION: COVER,STEERING ARM L.H
- USABLE ON CODE: AVY,A11,A13,A14,A15,A20,A24,A25 A26,A27,B16,B17,B18,HVY,H11,H13,H14 H15,H16,H17,H18,H20,H21,H24,H25,H26 H27,H28,MMM
- QTY: 1

Limits:

- Maintenance-to-catalogue identity only; no preceding fault/diagnosis chain is established.
- Multiple catalogue occurrences may differ in position or applicability. Matching the number does not establish universal fit.

Client disposition: client_accepted. Full benchmark freeze: pending.

## review-cover-basic-front-right

On a basic or A1 vehicle, the replacement hub is 5598767 for the right-front or left-rear position. Which cover is named by the installation note, and what NSN does the catalogue give for it?

Expected answer for review: For those hub, position, and vehicle-group conditions, the maintenance note names steering-arm cover 5591279. The selected catalogue row gives NSN 2530012035663 and description COVER,STEERING ARM R.H. The note permits retaining the existing cover if serviceable. Handedness and full UOC fit across catalogue occurrences are outside this identity question.

Required facts for scoring:

- `tm280_20_2:6-11:2:step-b:3:2:step-2:2`: If geared hub received is P/N 5598767 and right front or left rear installation is required, replace steering arm cover P/N 5591280 with P/N 5591279 for basic and A1 vehicles
- `tm280_24p_1:parts:r3565`: 2530012035663

Evidence:

- `tm280_20_2:6-11:2:step-b:3:2:step-2:2`, PDF page 660: If geared hub received is P/N 5598766 and left front or right rear installation is required, replace steering arm cover P/N 5591279 with P/N 5591280 for basic and A1 vehicles and P/N 6005121 for M 1123 and A2 vehicles. • If geared hub received is P/N 5598767 and right front or left rear installation is required, replace steering arm cover P/N 5591280 with P/N 5591279 for basic and A1 vehicles and P/N 6005120 for M 1123 and A2 vehicles. • Use existing steering arm cover if serviceable.
- `tm280_24p_1:parts:r3565`, PDF page 532: 5591279
- `tm280_24p_1:parts:r3565`, PDF page 532: 2530012035663

Parsed catalogue fields for `tm280_24p_1:parts:r3565` (check effectivity and fit against the PDF):

- ITEM NO: 33
- SMR CODE: PAOZZ
- NSN: 2530012035663
- CAGE: 34623
- PART NUMBER: 5591279
- DESCRIPTION: COVER,STEERING ARM R.H
- USABLE ON CODE: AVY,A11,A13,A14,A15,A20,A24,A25 A26,A27,B16,B17,B18,HVY,H11,H13,H14 H15,H16,H17,H18,H20,H21,H24,H25,H26 H27,H28,MMM
- QTY: 1

Limits:

- Maintenance-to-catalogue identity only; no preceding fault/diagnosis chain is established.
- Multiple catalogue occurrences may differ in position or applicability. Matching the number does not establish universal fit.

Client disposition: client_accepted. Full benchmark freeze: pending.

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
