# Gold passage review sample

Twenty questions from `data/eval/questions.jsonl` for Sodick's review.
Each gold passage below is copied from the node file named in the heading.
Relational/multi-hop gold is keyword-based, exploratory, and excluded from M3 targets.
Revised wording and source relations still need client review.
An unanswerable question has no gold passage. The correct action is to refuse.

| # | Id | Type | Language | Action |
|---:|---|---|---|---|
| 1 | lookup-0001 | lookup | en | answer |
| 2 | lookup-0002 | lookup | en | answer |
| 3 | lookup-ja-0001 | lookup | ja | answer |
| 4 | lookup-ja-0002 | lookup | ja | answer |
| 5 | procedure-0005 | procedure | en | answer |
| 6 | procedure-0006 | procedure | en | answer |
| 7 | procedure-0014 | procedure | en | answer |
| 8 | applicability-0001 | applicability | en | answer |
| 9 | applicability-0002 | applicability | en | answer |
| 10 | applicability-0003 | applicability | en | answer |
| 11 | relational-0001 | relational | en | answer |
| 12 | relational-0005 | relational | en | answer |
| 13 | relational-0010 | relational | en | answer |
| 14 | multi-0002 | multi_hop | en | answer |
| 15 | multi-0004 | multi_hop | en | answer |
| 16 | trouble-0001 | troubleshooting | en | answer |
| 17 | trouble-0005 | troubleshooting | en | answer |
| 18 | follow-0001 | follow_up | en | answer |
| 19 | unanswerable-0001 | unanswerable | en | refuse |
| 20 | unanswerable-0016 | unanswerable | ja | refuse |

## 1. lookup-0001

- Type: lookup
- Vocabulary: user
- Language: en
- Expected action: answer

The truck is showing this problem: 5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING TEMPERATURE 190°-230°F (88°-110°C). What should I check first?

Required facts:

- (step) Step 1. Check oil level for overfilling (Appendix G)

Gold passages:

### tm280_10:table:3-1:2:r5

Page 282.

````
5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING TEMPERATURE 190°-230°F (88°-110°C) Step 1. Check oil level for overfilling (Appendix G). Notify unit maintenance if fluid level is high. Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit maintenance.
````

## 2. lookup-0002

- Type: lookup
- Vocabulary: manual
- Language: en
- Expected action: answer

What does malfunction 6. ENGINE STARTS BUT MISFIRES, RUNS ROUGH, OR LACKS POWER list as the first test or corrective action?

Required facts:

- (step) Step 1. Check for water in fuel filter by draining

Gold passages:

### tm280_10:table:3-1:2:r6

Page 282.

````
6. ENGINE STARTS BUT MISFIRES, RUNS ROUGH, OR LACKS POWER Step 1. Check for water in fuel filter by draining. Drain fuel filter (para. 3-10). Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit maintenance.
````

## 3. lookup-ja-0001

- Type: lookup
- Vocabulary: user
- Language: ja
- Expected action: answer

「1. 適用範囲 本技術基」について、やさしく言うと何ですか?

Required facts:

- (value) 1. 適用範囲 本技術基準は、灯火器及び反射器並びに指示装置の自動車(二輪自動車

Gold passages:

### mlit_b052:1

Page 1.

````
1. 適用範囲 本技術基準は、灯火器及び反射器並びに指示装置の自動車(二輪自動車、側車付二輪 自動車並びにカタピラ及びそりを有する軽自動車を除く。)への取り付けについて適用す る。なお、型式の指定等を行う以外の場合にあっては、3.18.3.の規定中「適合するもの でなければならない」とあるのは「適合するものでなければならない。ただし、自動車 の運搬を行うため使用される自動車であって、自動車の構造上これによりがたい場合に あっては、前段の規定にかかわらず、取付位置、幾何学的視認性、色及び光度に係る基 準を可能な限り満たすように灯火等を取り付ければよいものとする」と、3.19.1.の規定 中「取り付けている場合」とあるのは「取り付けている場合(自動車の構造上これによ りがたい場合にあっては、取付位置、幾何学的視認性、色及び光度に係る基準を可能な 限り満たすように灯火等を取り付けている場合)」と、4.2.5.、4.3.5.、4.4.5.、4.5.5.、 4.6.6.、4.9.5.、4.11.5.、4.12.5.、4.13.5.、4.14.6.、4.15.5.、4.16.6.、4.17.6.、 4.18.5.、4.20.5.及び4.21.5.の規定中「角度α及び角度β」とあるのは「角度α及び角 度β(角度α及び角度βは、±3°の公差が許容されるものとする。)」と、4.8.7.1.の規 定中「操作できるものでなければならない。」とあるのは「操作できるものでなければな らない。ただし、じんかい又はし尿の収集又は運搬を行うため使用される自動車に備え る非常点滅表示灯は、当該収集又は運搬に係る操作装置と連動して手動で操作できるも のであってもよい。」と読み替える。
````

## 4. lookup-ja-0002

- Type: lookup
- Vocabulary: manual
- Language: ja
- Expected action: answer

別添52の「1.1. すれ違い用前照」には何と書かれていますか?

Required facts:

- (value) 1.1. すれ違い用前照灯の下方への垂直傾斜は、いかなる場合であっても、取扱説明

Gold passages:

### mlit_b052:1.1

Page 110.

````
1.1. すれ違い用前照灯の下方への垂直傾斜は、いかなる場合であっても、取扱説明書に 明瞭に説明された単純な方法により操作されるものでなければならない。
````

## 5. procedure-0005

- Type: procedure
- Vocabulary: user
- Language: en
- Expected action: answer

How do I carry out this job, in order? It starts with: 1. Loosen bolt (8), and remove ring clamp (1), cover (2), and gasket (3) from air cleaner assembly (6).

Required facts:

- (step) 1. Loosen bolt (8), and remove ring clamp (1), cover (2), and gasket (3) from air cleaner assembly (6).
- (step) 1. Check gasket (3) for dents, tears, rips, and other damage. Make sure the gasket has not taken a set. Make sure there are no hard dirt ridges on the sealing surfaces.
- (step) 2. Remove nut and washer assembly (7) and filter element (4) from stud (5) and air cleaner assembly(6).
- (caution) WARNING

Gold passages:

### tm280_20_2:3-12:2:step-a:3:2:step-1:2

Page 42.

````
1. Loosen bolt (8), and remove ring clamp (1), cover (2), and gasket (3) from air cleaner assembly (6).
````

### tm280_20_2:3-12:2:step-b:3:2:step-1:2

Page 42.

````
1. Check gasket (3) for dents, tears, rips, and other damage. Make sure the gasket has not taken a set. Make sure there are no hard dirt ridges on the sealing surfaces.
````

### tm280_20_2:3-12:2:step-a:3:2:step-2:2

Page 42.

````
2. Remove nut and washer assembly (7) and filter element (4) from stud (5) and air cleaner assembly(6).
````

### tm280_20_2:3-12:2:step-c:2:caution

Page 42.

````
WARNING
````

## 6. procedure-0006

- Type: procedure
- Vocabulary: manual
- Language: en
- Expected action: answer

List the numbered steps, in order, that begin with: 1. Hold nozzle at least one inch away from element (1) and direct compressed air against clean side of element (1) (in direction opposite to normal air flow). Move air stream up and down length of pleats until you can not see dust being blown out.

Required facts:

- (step) 1. Hold nozzle at least one inch away from element (1) and direct compressed air against clean side of element (1) (in direction opposite to normal air flow). Move air stream up and down length of pleats until you can not see dust being blown out.
- (step) 1. Remove screen or rag from housing opening.
- (step) 2. Prepare a solution of five gallons warm water (80-110° F (26.7-43.3° C)) and approximately one cup of non-sudsing detergent in a container large enough to submerge the element (1). Never use gasoline or solvents of any kind to clean elements.
- (caution) WARNING Compressed air used for cleaning purpose will not exceed 30 psi (207 kPa

Gold passages:

### tm280_20_2:3-13:3:step-1:2

Page 44.

````
1. Hold nozzle at least one inch away from element (1) and direct compressed air against clean side of element (1) (in direction opposite to normal air flow). Move air stream up and down length of pleats until you can not see dust being blown out.
````

### tm280_20_2:3-13:3:step-e:2:step-1:2

Page 44.

````
1. Remove screen or rag from housing opening.
````

### tm280_20_2:3-13:3:step-2:2

Page 44.

````
2. Prepare a solution of five gallons warm water (80-110° F (26.7-43.3° C)) and approximately one cup of non-sudsing detergent in a container large enough to submerge the element (1). Never use gasoline or solvents of any kind to clean elements.
````

### tm280_20_2:3-13:3:caution

Page 44.

````
WARNING Compressed air used for cleaning purpose will not exceed 30 psi (207 kPa). Use only with effective chip guarding and personnel protective equipment (goggles/shield, gloves, etc.).
````

## 7. procedure-0014

- Type: procedure
- Vocabulary: manual
- Language: en
- Expected action: answer

List the numbered steps, in order, that begin with: 1. Remove fuel tank filler cap (1).

Required facts:

- (step) 1. Remove fuel tank filler cap (1).
- (step) 1. Disconnect large vent line (4) from filler spout (5).
- (step) 1. Thoroughly clean outside of tank (17) to prevent dirt contamination.
- (caution) WARNING Drycleaning solvent is flammable and will not be used near an open flame

Gold passages:

### tm280_20_2:3-24:2:step-a:3:2:step-1:2

Page 58.

````
1. Remove fuel tank filler cap (1).
````

### tm280_20_2:3-24:2:step-b:3:2:step-1:2

Page 58.

````
1. Disconnect large vent line (4) from filler spout (5).
````

### tm280_20_2:3-24:6:step-c:2:step-1:2

Page 62.

````
1. Thoroughly clean outside of tank (17) to prevent dirt contamination.
````

### tm280_20_2:3-24:7:step-d:2:caution

Page 64.

````
WARNING Drycleaning solvent is flammable and will not be used near an open flame. A fire extinguisher will be kept nearby when the solvent is used. Use only in well-ventilated places. Failure to do this may result in injury to personnel or damage to equipment.
````

## 8. applicability-0001

- Type: applicability
- Vocabulary: user
- Language: en
- Expected action: answer

Does this instruction mention the M1097?

Required facts:

- (value) M1097

Gold passages:

### tm280_10:1-10

Page 21.

````
1-10. HEAVY VARIANT CARGO/TROOP CARRIERS (M1097, M1097A1, M1097A2, AND M1123)
````

## 9. applicability-0002

- Type: applicability
- Vocabulary: manual
- Language: en
- Expected action: answer

Which vehicle model is named for this content, and is it the M966?

Required facts:

- (value) M966

Gold passages:

### tm280_10:1-11

Page 23.

````
1-11. TOW CARRIERS, ARMORED (M966, M966A1, M1036, AND M1121)
````

## 10. applicability-0003

- Type: applicability
- Vocabulary: user
- Language: en
- Expected action: answer

Does this instruction mention the M1045?

Required facts:

- (value) M1045

Gold passages:

### tm280_10:1-12

Page 25.

````
1-12. TOW CARRIERS, W/SUPPLEMENTAL ARMOR (M1045, M1045A1, M1045A2, M1046, AND M1046A1)
````

## 11. relational-0001

- Type: relational
- Vocabulary: user
- Language: en
- Expected action: answer

Even after the engine warms up, there's a lot of smoke from the exhaust. Can you help me work out whether any replacement part is called for and find its part number?

Benchmark slice: `keyword_exploratory`. Evidence basis: `keyword_heuristic`. M3 target eligible: `False`.

Required facts:

- (step) Step 1. Check oil level for overfilling (Appendix G)
- (value) SF-5597692

Gold passages:

### tm280_10:table:3-1:2:r5

Page 282.

````
5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING TEMPERATURE 190°-230°F (88°-110°C) Step 1. Check oil level for overfilling (Appendix G). Notify unit maintenance if fluid level is high. Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit maintenance.
````

### tm280_24p_1:parts:r4992

Page 725.

````
4 PAOZZ 5640013093866 34623 SF-5597692 INSULATION,NOZZLE R.H.,USBL EFF 46162 AND ABOVE 1
````

## 12. relational-0005

- Type: relational
- Vocabulary: user
- Language: en
- Expected action: answer

Moving the gear selector doesn't make the truck respond. What should be checked before deciding whether there is a part I need to order?

Benchmark slice: `keyword_exploratory`. Evidence basis: `keyword_heuristic`. M3 target eligible: `False`.

Required facts:

- (step) Step 1. Check to see if transfer case lever is in “N” (neutral) or “P” (Park) for M1123 and A2 vehicles
- (value) 12460092-2

Gold passages:

### tm280_10:table:3-1:3:r10

Page 283.

````
10. NO RESPONSE TO SHIFT LEVER MOVEMENT Step 1. Check to see if transfer case lever is in “N” (neutral) or “P” (Park) for M1123 and A2 vehicles. Place transmission shift lever in “N” (neutral) or “P” (Park) and select transfer gear range. Step 2. Other causes. Notify unit maintenance.
````

### tm280_24p_1:parts:r2414

Page 373.

````
10 PAOZZ 6220014126420 9C234 12460092-2 LIGHT,INDICATOR TRANSMISSION BVY,B15,B20,B24,B25,C17,NNN 1
````

## 13. relational-0010

- Type: relational
- Vocabulary: user
- Language: en
- Expected action: answer

The brake warning light is on. What needs checking before I can know whether a replacement part is required?

Benchmark slice: `keyword_exploratory`. Evidence basis: `keyword_heuristic`. M3 target eligible: `False`.

Required facts:

- (step) Step 1. Check to see if parking brake is partially applied
- (value) 12460229

Gold passages:

### tm280_10:table:3-1:4:r17

Page 284.

````
17. BRAKE WARNING LAMP ASSEMBLY ON Step 1. Check to see if parking brake is partially applied. Disengage parking brake. Step 2. Check for low brake fluid level (TM 9-2320-280-20). Add brake fluid (Appendix G). Step 3. Other causes. Notify unit maintenance.
````

### tm280_24p_1:parts:r1403

Page 217.

````
11 PAOZZ 3040014445640 34623 12460229 CONNECTING LINK,RIG BRAKE LIGHT SWITCH BVY,B15,B20,B24,B25,C17,NNN 1
````

## 14. multi-0002

- Type: multi_hop
- Vocabulary: user
- Language: en
- Expected action: answer

My engine starts but runs rough and feels weak. Walk me through the checks and any follow-up work, then show the part number only if those findings support a replacement.

Benchmark slice: `keyword_exploratory`. Evidence basis: `keyword_heuristic`. M3 target eligible: `False`.

Required facts:

- (step) Step 1. Check for water in fuel filter by draining
- (step) (1) To operate fire extinguisher (4), remove from stowage bracket (5). Remove locking pin (2) and direct nozzle (6) to source of flames.
- (value) SF-5597692

Gold passages:

### tm280_10:table:3-1:2:r6

Page 282.

````
6. ENGINE STARTS BUT MISFIRES, RUNS ROUGH, OR LACKS POWER Step 1. Check for water in fuel filter by draining. Drain fuel filter (para. 3-10). Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit maintenance.
````

### tm280_10:2-27:step-b:2:step-p1:2

Page 195.

````
(1) To operate fire extinguisher (4), remove from stowage bracket (5). Remove locking pin (2) and direct nozzle (6) to source of flames.
````

### tm280_24p_1:parts:r4992

Page 725.

````
4 PAOZZ 5640013093866 34623 SF-5597692 INSULATION,NOZZLE R.H.,USBL EFF 46162 AND ABOVE 1
````

## 15. multi-0004

- Type: multi_hop
- Vocabulary: user
- Language: en
- Expected action: answer

I'm getting a low oil-pressure reading. What checks and servicing instructions apply, and what evidence would I need before choosing a replacement from the parts list?

Benchmark slice: `keyword_exploratory`. Evidence basis: `keyword_heuristic`. M3 target eligible: `False`.

Required facts:

- (step) Step 1. Check for low oil level (para
- (step) 2. Loosen nut (2) and remove RPM sensor (1) from oil pump drive (6).
- (value) 8682194

Gold passages:

### tm280_10:table:3-1:2:r8

Page 282.

````
8. LOW ENGINE OIL PRESSURE ACCORDING TO OIL PRESSURE GAUGE Step 1. Check for low oil level (para. 3-17). Add oil (Appendix G). Step 2. Other causes. Notify unit maintenance.
````

### tm280_20_2:4-32:2:step-a:3:2:step-2:2

Page 291.

````
2. Loosen nut (2) and remove RPM sensor (1) from oil pump drive (6).
````

### tm280_24p_1:parts:r3014

Page 461.

````
5 XAHZZ 7X677 8682194 BODY,OIL PUMP 1995,96 BVY,B15,B20,B24,B25,C17,NNN 1
````

## 16. trouble-0001

- Type: troubleshooting
- Vocabulary: user
- Language: en
- Expected action: answer

5. excessive exhaust smoke after engine reaches normal operating temperature 190°-230°f (88°-110°c) — where do I start?

Required facts:

- (step) Step 1. Check oil level for overfilling (Appendix G)

Gold passages:

### tm280_10:table:3-1:2:r5

Page 282.

````
5. EXCESSIVE EXHAUST SMOKE AFTER ENGINE REACHES NORMAL OPERATING TEMPERATURE 190°-230°F (88°-110°C) Step 1. Check oil level for overfilling (Appendix G). Notify unit maintenance if fluid level is high. Step 2. Check for restricted air cleaner. If emergency situation exists, clean air cleaner element (para. 3-15). If emergency situation does not exist, notify unit maintenance. Step 3. Other causes. Notify unit maintenance.
````

## 17. trouble-0005

- Type: troubleshooting
- Vocabulary: user
- Language: en
- Expected action: answer

10. no response to shift lever movement — where do I start?

Required facts:

- (step) Step 1. Check to see if transfer case lever is in “N” (neutral) or “P” (Park) for M1123 and A2 vehicles

Gold passages:

### tm280_10:table:3-1:3:r10

Page 283.

````
10. NO RESPONSE TO SHIFT LEVER MOVEMENT Step 1. Check to see if transfer case lever is in “N” (neutral) or “P” (Park) for M1123 and A2 vehicles. Place transmission shift lever in “N” (neutral) or “P” (Park) and select transfer gear range. Step 2. Other causes. Notify unit maintenance.
````

## 18. follow-0001

- Type: follow_up
- Vocabulary: user
- Language: en
- Expected action: answer

And on the M998?

Required facts:

- (value) M998

Gold passages:

### tm280_10:2-44:step-a:2

Page 226.

````
a. General. The troop seat kit is used to convert M998, M998A1, M1097, M1097A1, M1097A2, and M1123 cargo vehicles into troop carriers.
````

## 19. unanswerable-0001

- Type: unanswerable
- Vocabulary: user
- Language: en
- Expected action: refuse

Can you explain 99. ZZZNOTACODE FAILURE? I can't find it in the book.

Forbidden facts:

- (value) 99. ZZZNOTACODE FAILURE

Gold passages: none.

## 20. unanswerable-0016

- Type: unanswerable
- Vocabulary: manual
- Language: ja
- Expected action: refuse

What does this mean in the manual: 別添99の存在しない灯火基準?

Forbidden facts:

- (value) 別添99の存在しない灯火基準

Gold passages: none.
