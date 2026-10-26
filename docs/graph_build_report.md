# Graph build report

The rule build reads the node files and the service cases and loads Neo4j.
The counts are the counts in the database.

## Counts

| Label | Count |
|---|---:|
| Document | 6 |
| Passage | 22952 |
| Malfunction | 30 |
| Part | 4478 |
| Model | 43 |
| Case | 2000 |
| IN_DOCUMENT | 22952 |
| PARENT | 22946 |
| NEXT | 7952 |
| BOUND_CAUTION | 382 |
| REFERS_TO | 1518 |
| STATES | 30 |
| HAS_STEP | 77 |
| APPLIES_TO | 13620 |
| LISTS | 8099 |
| CANDIDATE_PART | 1065 |
| ABOUT | 2000 |
| INSTALLED | 2000 |
| ON_MODEL | 2000 |
| MENTIONS | 12398 |

## Orphan nodes

An orphan node has no relationship.
This build has no orphan nodes.

## Provenance

0 edges have no document page and no case id.
0 edges name both a document page and a case id.

## Derived edges

The sample lists 100 of 12398 derived edges.

| Type | Start | End | Rule | Weight |
|---|---|---|---|---:|
| MENTIONS | tm280_10 | M998 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10 | M1097 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10 | M1097A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10 | M1097A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10 | M1123 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-a:2 | M1097 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-a:2 | M1097A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-a:2 | M1097A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-a:2 | M1123 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-a:2 | M998 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-a:2 | M998A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-b:2 | M1097 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-b:2 | M1097A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-b:2 | M1097A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-b:2 | M1123 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-c:2 | M1097 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-c:2 | M1097A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-c:2 | M1097A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-e:2:step-p3:2 | M1097 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-e:2:step-p3:2 | M1097A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-e:2:step-p3:2 | M1097A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-10:step-e:2:step-p3:2 | M1123 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11 | M1036 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11 | M1121 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11 | M966 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11 | M966A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-a:2 | M1036 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-a:2 | M1121 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-a:2 | M966 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-a:2 | M966A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-b:2 | M1036 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-b:2 | M1121 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-b:2 | M966 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-b:2 | M966A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-c:2 | M1036 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-c:2 | M966 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-c:2 | M966A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-e:2:step-p2:2 | M1036 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-e:2:step-p2:2 | M1121 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-e:2:step-p2:2 | M966 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-11:step-e:2:step-p2:2 | M966A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12 | M1045 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12 | M1045A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12 | M1045A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12 | M1046 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12 | M1046A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-a:2 | M1045 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-a:2 | M1045A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-a:2 | M1045A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-a:2 | M1046 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-a:2 | M1046A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-b:2 | M1045 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-b:2 | M1045A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-b:2 | M1045A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-b:2 | M1046 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-b:2 | M1046A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-c:2 | M1045 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-c:2 | M1045A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-c:2 | M1045A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-c:2 | M1046 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-c:2 | M1046A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-e:2:step-p2:2 | M1045 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-e:2:step-p2:2 | M1045A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-e:2:step-p2:2 | M1045A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-e:2:step-p2:2 | M1046 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-12:step-e:2:step-p2:2 | M1046A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13 | M1025 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13 | M1025A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13 | M1025A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13 | M1026 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13 | M1026A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:2 | M1123 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-a:2 | M1025 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-a:2 | M1025A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-a:2 | M1025A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-a:2 | M1026 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-a:2 | M1026A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-b:2 | M1025 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-b:2 | M1025A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-b:2 | M1025A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-b:2 | M1026 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-b:2 | M1026A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-e:2:step-p2:2 | M1025 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-e:2:step-p2:2 | M1025A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-e:2:step-p2:2 | M1025A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-e:2:step-p2:2 | M1026 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-13:step-e:2:step-p2:2 | M1026A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14 | M1043 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14 | M1043A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14 | M1043A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14 | M1044 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14 | M1044A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14:2 | M1123 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14:step-a:2 | M1043 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14:step-a:2 | M1043A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14:step-a:2 | M1043A2 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14:step-a:2 | M1044 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14:step-a:2 | M1044A1 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14:step-b:2 | M1043 | surface form in the passage text | 0.4 |
| MENTIONS | tm280_10:1-14:step-b:2 | M1043A1 | surface form in the passage text | 0.4 |
