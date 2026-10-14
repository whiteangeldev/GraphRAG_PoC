# Corpus register

This is the M1 corpus list for Sodick's approval. Conversion waits on that approval.

Family: HMMWV (M998 series) and its 6.2 L / 6.5 L diesel engine. English manuals are US government works. The Japanese document is a different subject, used only to prove the pipeline on Japanese.

Local copies are in `data/corpus/source/`. Counts below were taken from those files with pdfplumber 0.11.10 (text, character bounding boxes, and tables) and pdfminer.six (full-text census).

## Size gates

| Gate | Result |
|---|---|
| At least four English documents and 800 pages | 5 documents, 3,670 pages |
| At least 300 fault-code or parameter table rows | Met. Operator Table 3-1 has malfunction rows 1–30. Operator PMCS Table 2-2 has item numbers through 76 (71 rows matched an interval word). Engine calibration charts contribute 600 data rows. |
| At least 500 part numbers | 4,436 unique 13-digit NSNs in the parts list, from 6,780 parsed item rows |
| Procedures with warnings, cautions, and cross-references | Present. See the per-document counts. |
| Model applicability | More than 30 model designators, including cargo, armament, ambulance, shelter, and A2 variants |
| One Japanese technical document of at least 50 pages | 117 pages |
| Material for 2,000 synthetic service records | The malfunction list, model designators, and part numbers are sufficient for the Step 4 generator. The records themselves are not in this register. |

## English documents

Licence for every English file: work of the United States Government, public domain under 17 USC 105. Each manual is marked "Approved for public release; distribution is unlimited." A download site does not own the text. Derived node files and case records may be redistributed to Sodick.

### tm280_10 — operation

| Field | Value |
|---|---|
| Title | Operator's Manual for Truck, Utility, 1-1/4 Ton, 4x4, M998 series |
| Publication | TM 9-2320-280-10, Air Force TO 36A12-1A-2091-1, Marine Corps TM 2320-10/6B |
| Edition | Supersedes the 18 June 1991 edition. Change 2 is dated 30 November 2001. |
| Pages | 405 |
| Link | https://www.nsndepot.com/Files/library/TM/HMMWV/TM-9-2320-280-10/TM-9-2320-280-10.pdf |
| File | `data/corpus/source/TM-9-2320-280-10.pdf` |
| Role | Operation. Also contains PMCS Table 2-2 and troubleshooting Table 3-1. |
| Text layer | Yes. 404 pages have extracted text. Character bounding boxes are present. |
| Tables | pdfplumber reads PMCS Table 2-2 (sample: PDF page 113, columns Item No., Interval, Location, Procedure). |
| Structure | Warnings 83, cautions 86, cross-references 243. Table 3-1 malfunction numbers 1 through 30, with ordered steps and paragraph references. PMCS item numbers run through 76. |

### tm280_20_2 — maintenance

| Field | Value |
|---|---|
| Title | Unit Maintenance, Volume 2: engine, electrical, transmission, axles, brakes, steering, and frame |
| Publication | TM 9-2320-280-20-2, Air Force TO 36A12-1A-2092-1-2, Marine Corps TM 2320-20/7B |
| Edition | Supersedes the 19 January 1990 edition |
| Pages | 953 |
| Link | https://image.nsnlookup.com/equipment-intelligence/land/hmmwv/technical-manual/tm-9-2320-280-20-2/tm-9-2320-280-20-2.pdf |
| File | `data/corpus/source/TM-9-2320-280-20-2.pdf` |
| Role | Maintenance procedures |
| Text layer | Yes. Sample procedure pages contain numbered steps and bounding boxes. PDF page 1 yields 7 tables. |
| Structure | Warnings 41, cautions 36, cross-references 1,038. Tasks name the applicable models (for example serpentine-belt work applies to M997A2, M1025A2, M1097A2, M1123, and other A2 vehicles). Specification tables include belt tension, toe-in, and toe-out, with values that differ by model and tyre type. |

### tm280_20_1 — troubleshooting

| Field | Value |
|---|---|
| Title | Unit Maintenance, Volume 1: service and troubleshooting |
| Publication | TM 9-2320-280-20-1, Air Force TO 36A12-1A-2092-1-1, Marine Corps TM 2320-20/7B |
| Edition | Supersedes the 19 January 1990 edition |
| Pages | 890 |
| Link | https://image.nsnlookup.com/equipment-intelligence/land/hmmwv/technical-manual/tm-9-2320-280-20-1/tm-9-2320-280-20-1.pdf |
| File | `data/corpus/source/TM-9-2320-280-20-1.pdf` |
| Role | Code reference / troubleshooting |
| Text layer | Prose, warnings, and the index have a text layer and bounding boxes. PDF page 1 yields 14 tables. Diagnostic flowchart pages carry a header line; the flowchart artwork is not text. |
| Structure | Warnings 93, cautions 35, cross-references 955. STE/ICE-R test sections are indexed (cooling, compression, electrical, brakes, drivetrain, ambulance). The text-backed fault table for questions is operator Table 3-1, not these flowchart pages. |

### tm280_24p_1 — parts

| Field | Value |
|---|---|
| Title | Repair Parts and Special Tools List, Volume 1 of 2 |
| Publication | TM 9-2320-280-24P-1, Air Force TO 36A12-1A-3044-1, Marine Corps TM 2320-24P/8B |
| Edition | Supersedes the 31 January 1996 edition. This file includes Change 2. The change page prints the date as "TBD". |
| Pages | 1,155 |
| Link | https://genuinehumveeparts.com/manuals/TM-9-2320-280-24P-1-wChg2.pdf |
| File | `data/corpus/source/TM-9-2320-280-24P-1.pdf` |
| Role | Parts |
| Text layer | Yes on the parts tables. Some figure sheets have no body text. On PDF page 901, pdfplumber's text strategy returns a 42-row table (item, SMR code, NSN, CAGE, part number, description, usable-on code, quantity). |
| Structure | 6,780 item rows parsed as SMR code + 13-digit NSN + CAGE + part number. 4,436 unique NSNs. Usable-on codes tie parts to model groups. |

### tm2815_34 — engine parameters

| Field | Value |
|---|---|
| Title | Direct Support and General Support Maintenance: 6.2 L and 6.5 L diesel engines |
| Publication | TM 9-2815-237-34, Air Force TO 38V1-6-2, Marine Corps TM 2815-34/3A |
| Edition | January 1996 issue, supersedes 25 June 1985 |
| Pages | 267 |
| Link | https://www.nsndepot.com/Files/library/TM/HMMWV/TM-9-2815-237-34/TM-9-2815-237-34.pdf |
| File | `data/corpus/source/TM-9-2815-237-34.pdf` |
| Role | Additional parameter tables for the same vehicle family. Included because the vehicle troubleshooting flowcharts are graphics. |
| Text layer | Yes. Title page has character bounding boxes. |
| Tables | Fuel-injection pump calibration charts on 10 pages. pdfplumber text-strategy row counts, with the header row excluded: 54, 64, 56, 63, 58, 62, 58, 65, 68, 52. Total 600 data rows. Columns include rpm, throttle position, delivery, cam movement, and housing pressure. Tables 2-2 and 2-3 are repair and replacement standards (inch and millimetre limits). Tables 1-1 and 1-2 are tabulated engine data. Tables 2-1 and 2-1.1 are run-in schedules. |
| Structure | Warnings 23, cautions 28. Procedures name the pump model (DB2829-4523, DB2829-4879, DB2831-5149, and others). |

## Japanese document

### mlit_b052

| Field | Value |
|---|---|
| Title | 灯火器及び反射器並びに指示装置の取付装置の技術基準 |
| Publication | 道路運送車両の保安基準の細目を定める告示（平成14年国土交通省告示第619号）別添52. The file header is dated 2025.9.26. |
| Pages | 117 |
| Link | https://www.mlit.go.jp/jidosha/content/B052.pdf |
| File | `data/corpus/source/mlit-b052.pdf` |
| Role | Japanese sample. Numbered technical requirements for fitting lamps, reflectors, and tell-tales. Not part of the HMMWV set. |
| Text layer | Yes. Japanese text and character bounding boxes on the sampled pages. The sample pages are numbered clauses rather than ruled grids. |
| Licence | Copyright Act of Japan, Article 13, item 2. An official notice (告示) issued by a national government organ is not a copyrighted work, so the text may be processed and derived data may be redistributed. MLIT notes that the printed Official Gazette controls if a web PDF differs. |

## Applicability examples the questions can use

- Cargo/troop: M998, M998A1, M1038, M1038A1, M1097, M1097A2, M1123
- Armament and TOW: M1025, M1026, M1043, M1045, M966, and their A1/A2 variants
- Ambulance: M996, M997, M1035, and their A1/A2 variants
- Shelter: M1037, M1042
- Engine pumps differ by year and displacement: DB2829-4523 (pre-1990 6.2 L), DB2829-4879 (1990 6.2 L), DB2831-5149 (6.5 L)

## What approval should decide

The register is ready for review. Two facts should be explicit in that review:

- Volume 1 troubleshooting flowcharts will not become text nodes. Fault questions will use operator Table 3-1 and the engine calibration charts.
- The Japanese standard is a vehicle lighting technical standard, not a HMMWV manual. It is there to exercise the same converter on Japanese.
