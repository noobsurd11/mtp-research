# cv5v3 proposal: fold tables (pool cells only; crack px from cells.tsv crack_px_v11, inactive and class px from the v1.1 masks)

Merged groups (cv5v2 group joined with physical module): 303 (cv5v2: 330). Groups that span cv5v2 folds: 24; cells in them: 91; cells moved: 31 (by source: {'ARTS': 18, 'CFVS': 9, 'CSIR': 4}). Groups spanning folds after the moves: 0. Cells in a fold-spanning merged group that are not in a fold-spanning physical module (they sit in a cv5v2 group that the module map does not confirm): 0 [].

## cv5v2 (as built)

| fold | cells | groups | crack cells | crack px | inactive cells | inactive px | sources | mono/multi/other |
|---|---|---|---|---|---|---|---|---|
| 0 | 107 | 66 | 51 | 49311 | 10 | 56753 | ARTS:36 BMRK:10 CFVS:34 CSIR:23 SDLE:4 | 47/47/13 |
| 1 | 111 | 67 | 44 | 60467 | 8 | 57565 | ARTS:39 BMRK:10 CFVS:36 CSIR:22 SDLE:4 | 49/48/14 |
| 2 | 104 | 63 | 46 | 57196 | 7 | 57142 | ARTS:37 BMRK:10 CFVS:31 CSIR:23 SDLE:3 | 36/56/12 |
| 3 | 104 | 67 | 46 | 99932 | 15 | 56785 | ARTS:34 BMRK:10 CFVS:34 CSIR:23 SDLE:3 | 53/39/12 |
| 4 | 106 | 67 | 42 | 40640 | 8 | 56775 | ARTS:36 BMRK:10 CFVS:34 CSIR:23 SDLE:3 | 56/39/11 |

## cv5v3 (proposal)

| fold | cells | groups | crack cells | crack px | inactive cells | inactive px | sources | mono/multi/other |
|---|---|---|---|---|---|---|---|---|
| 0 | 106 | 61 | 52 | 56901 | 12 | 57585 | ARTS:34 BMRK:10 CFVS:36 CSIR:22 SDLE:4 | 47/46/13 |
| 1 | 110 | 62 | 45 | 60474 | 8 | 57565 | ARTS:37 BMRK:10 CFVS:37 CSIR:22 SDLE:4 | 51/45/14 |
| 2 | 106 | 59 | 44 | 56810 | 7 | 57142 | ARTS:38 BMRK:10 CFVS:31 CSIR:24 SDLE:3 | 38/56/12 |
| 3 | 105 | 59 | 47 | 92831 | 14 | 56334 | ARTS:37 BMRK:10 CFVS:32 CSIR:23 SDLE:3 | 50/43/12 |
| 4 | 105 | 62 | 41 | 40530 | 7 | 56394 | ARTS:36 BMRK:10 CFVS:33 CSIR:23 SDLE:3 | 55/39/11 |

## Classes with held-out px and no training px in a fold

- cv5v2: class 19 fold 0 (21935 px); class 12 fold 2 (1204 px); class 8 fold 3 (1238 px)
- cv5v3: class 19 fold 0 (21935 px); class 12 fold 2 (1204 px); class 8 fold 3 (1238 px)

## Moves (group, cells, folds before, fold kept, tie, moved cells)

- ARTS_00002: 10 cells, before {1: 7, 2: 3}, kept f1; moved 3: ARTS_00002_r3_c2, ARTS_00002_r4_c2, ARTS_00002_r6_c1
- ARTS_00008: 6 cells, before {1: 3, 3: 3}, kept f3 (tie); moved 3: ARTS_00021_r1_c6, ARTS_00021_r2_c6, ARTS_00021_r6_c2
- ARTS_00011: 5 cells, before {0: 3, 4: 2}, kept f0; moved 2: ARTS_00024_r11_c6, ARTS_00024_r2_c1
- ARTS_00029: 5 cells, before {0: 2, 2: 3}, kept f2; moved 2: ARTS_00029_r2_c5, ARTS_00029_r4_c3
- CFVS_00088: 5 cells, before {1: 3, 4: 2}, kept f1; moved 2: CFVS_00109_r11_c1, CFVS_00109_r1_c2
- ARTS_00006: 3 cells, before {2: 2, 3: 1}, kept f2; moved 1: ARTS_00006_r10_c3
- ARTS_00013: 3 cells, before {3: 1, 4: 2}, kept f4; moved 1: ARTS_00026_r1_c6
- ARTS_00019: 3 cells, before {2: 2, 4: 1}, kept f2; moved 1: ARTS_00032_r12_c3
- ARTS_00025: 3 cells, before {0: 1, 4: 2}, kept f4; moved 1: ARTS_00025_r8_c1
- ARTS_00106: 4 cells, before {2: 1, 4: 3}, kept f4; moved 1: ARTS_00106_r1_c5
- ARTS_00111: 2 cells, before {0: 1, 3: 1}, kept f3 (tie); moved 1: ARTS_00111_r1_c4
- ARTS_00118: 2 cells, before {1: 1, 2: 1}, kept f2 (tie); moved 1: ARTS_00118_r1_c6
- ARTS_00165: 2 cells, before {1: 1, 3: 1}, kept f3 (tie); moved 1: ARTS_00166_r12_c5
- CFVS_00017: 8 cells, before {3: 7, 4: 1}, kept f3; moved 1: CFVS_00019_r1_c4
- CFVS_00065: 3 cells, before {2: 2, 3: 1}, kept f2; moved 1: CFVS_00070_r1_c4
- CFVS_00076: 2 cells, before {2: 1, 4: 1}, kept f4 (tie); moved 1: CFVS_00076_r1_c1
- CFVS_00101: 7 cells, before {3: 1, 4: 6}, kept f4; moved 1: CFVS_00101_r5_c1
- CFVS_00132: 3 cells, before {0: 2, 3: 1}, kept f0; moved 1: CFVS_00134_r6_c3
- CFVS_00156: 2 cells, before {1: 1, 4: 1}, kept f4 (tie); moved 1: CFVS_00160_r5_c5
- CFVS_00168: 2 cells, before {0: 1, 4: 1}, kept f0 (tie); moved 1: CFVS_00168_r1_c5
- CSIR_00104: 4 cells, before {0: 1, 3: 3}, kept f3; moved 1: CSIR_00104_r4_c5
- CSIR_00106: 2 cells, before {0: 1, 2: 1}, kept f2 (tie); moved 1: CSIR_00116_r9_c1
- CSIR_00107: 3 cells, before {1: 2, 3: 1}, kept f1; moved 1: CSIR_00107_r9_c3
- CSIR_00178: 2 cells, before {0: 1, 1: 1}, kept f0 (tie); moved 1: CSIR_00178_r7_c1
