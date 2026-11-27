# Masked same-cell audit of the 532 pool cells (stage B fix round F2, 15 Nov 2026)

Lead's finding (log.md 15 Nov 13:51; results/stageA/dup_check_lead/): two physical cells sit twice in different cv5v2 folds; global scores do not separate same cell from same layout, and a plain SIFT matcher is fooled by border text. Task: a matcher on the cell area only, calibrated on known pairs, run on every same-source cross-fold pair, with a ranked list and a contact sheet for the lead's visual check. **No split or list was changed; the lead rules.**
Tags: E = measured, S = judgement. Pixels of pool images only (no label read; no sealed image read; the sheets hold pool images only).

## 1. Matcher (bench/samecell.py, scripts/bench_samecell.py; bench_b 8f9178b, final 4920802)
- **Mask** (where keypoints may sit): the emission area, i.e. blurred intensity above half the median of the non-padding px, white padding removed, opened with a 21 px disc (printed text and other thin bright strokes vanish), holes filled, eroded by 10 px; minus a 2 px band around the long dark axis-aligned lines (busbars, gaps, fingers; black-hat with 41 px line elements). So the black module border, its serial number and the cell layout give no keypoints; grain, marks, cracks and dark areas inside the cells do.
- **Features and check:** SIFT (4,000 features, contrast threshold 0.02) on the CLAHE image inside the mask; ratio test 0.75; RANSAC similarity (3 px, seed 0 per pair, one OpenCV thread); accepted only with scale in [0.87, 1.15]; any rotation and translation (so different grid positions and 180-degree turns are covered). Score = RANSAC inliers; also printed: inlier ratio, spread (bounding box of the inliers / image area), translation (tx, ty), overlap (share of b's frame covered by a's mapped frame: about 1 = the same crop, 0.5 = crops one cell pitch apart, 0.25 = one cell diagonally).
- Determinism (E): run 1 (1 worker, 8f9178b) and run 2 (8 workers, 4920802) give the same inliers and the same rank for all 30,974 pairs.
- Tests (tests/test_bench_bfix2.py): mask drops the border, text and line bands; the same grain shifted by (6, -5) px matches with >= 50 inliers and the right translation, the same layout and the same text with other grain gives < 10; overlap geometry.

## 2. Calibration (E; parameters set by hand on these same pairs, so this is in-sample, S)
| Pairs | n | inliers |
|---|---|---|
| known same-cell pool pairs (stage A pairs_labelled known_same_cell = 1, both P532; same fold by design) | 35 | 0, 0, 0, 0, 3, 5, then 33 to 1,527 (29 of 35 >= 33) |
| lead confirmed (ARTS_00165 / 00166 r12_c5; CFVS_00076 / 00082 r1_c1) | 2 | 216; 37 |
| lead rejected (ARTS_00102 / 00118, 00009 / 00102, 00102 / 00171 r1_c6; CFVS_00045 / 00059 r4_c3; CSIR_00147 / 00227 r8_c6) | 5 | 0, 4, 0, 0, 0 |
- Known-pair recall: 0.86 at >= 5 inliers, 0.83 at >= 10 to 30, 0.74 at >= 50. The 6 known pairs below 10 are CFVS mono cells at different stress stages (00007 / 00021, 00065 / 00086, 00088 / 00112, 00114 / 00130, 00139 / 00143) and ARTS_00040 / 00061 r1_c6: few keypoints once layout is masked; the matcher misses such pairs (S: a same-cell pair of featureless mono cells can hide below the list).
- The lead's earlier unmasked SIFT gave the rejected r1_c6 pairs 44 to 81 inliers (text); the masked matcher gives them 0 to 4.

## 3. Full run (E; run 2, results/stageB/samecell_audit/run2_4920802/)
30,974 same-source pairs with different cv5v2 folds (ARTS 13,243, CFVS 11,418, CSIR 5,198, BMRK 1,000, SDLE 115), any grid position. Pairs at or above 5 / 10 / 15 / 20 / 30 / 50 inliers: 397 / 92 / 47 / 30 / 23 / 19.
Files: pairs.tsv (502bd5f6; all pairs ranked by inliers then spread; columns rank, a, fold, b, fold, same_pos, inliers, good, ratio, spread, overlap, tx, ty, scale, rot, keypoints), calibration.tsv (5a1c05cc), modules.tsv (4a47c456; image-id pairs holding pairs with >= 15 inliers), summary.json (f02e6678), summary_tables.md (the tables below), sheet_1.png to sheet_4.png (top 40, 10 pairs each; orange = emission-area contour, green = RANSAC inliers; header: rank, inliers, overlap, translation, rotation). Run 1 (identical scores, no translation columns) is kept in run1_8f9178b/.

### 3a. All 47 pairs with >= 15 inliers (tier and flags are descriptive, S)
"same cell?" = overlap >= 0.9; "same module, neighbouring crop?" = overlap < 0.9 (the two crops share part of their area: half a cell or a corner). hub = a cell whose strong pairs reach >= 3 other images (S: on CSIR these are flat mono cells matched at near-zero shift, likely a fixed camera pattern rather than one cell); clustered = spread < 0.05.

| rank | a (fold) | b (fold) | inliers | inlier ratio | overlap | shift (tx, ty) | rot | spread | tier | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ARTS_00011_r1_c1 (0) | ARTS_00024_r2_c1 (4) | 940 | 0.77 | 0.50 | (-3, -256) | -0.2 | 0.39 | same module, neighbouring crop? |  |
| 2 | ARTS_00106_r1_c5 (2) | ARTS_00107_r1_c4 (4) | 919 | 0.98 | 0.50 | (+256, -0) | -0.0 | 0.34 | same module, neighbouring crop? |  |
| 3 | ARTS_00008_r3_c6 (3) | ARTS_00021_r2_c6 (1) | 871 | 0.81 | 0.50 | (-0, +256) | +0.0 | 0.34 | same module, neighbouring crop? |  |
| 4 | ARTS_00013_r2_c6 (4) | ARTS_00026_r1_c6 (3) | 804 | 0.84 | 0.50 | (+1, +257) | -0.1 | 0.35 | same module, neighbouring crop? |  |
| 5 | ARTS_00029_r2_c5 (0) | ARTS_00171_r1_c6 (2) | 421 | 0.82 | 0.24 | (-248, +259) | +0.0 | 0.23 | same module, neighbouring crop? |  |
| 6 | CFVS_00101_r5_c1 (3) | CFVS_00102_r4_c1 (4) | 412 | 0.96 | 0.50 | (+0, +256) | +0.0 | 0.36 | same module, neighbouring crop? |  |
| 7 | ARTS_00002_r4_c2 (2) | ARTS_00081_r5_c1 (1) | 330 | 0.82 | 0.24 | (+260, -244) | -0.0 | 0.23 | same module, neighbouring crop? |  |
| 8 | ARTS_00006_r10_c3 (3) | ARTS_00062_r8_c3 (2) | 253 | 0.83 | 0.50 | (-1, +256) | -0.0 | 0.46 | same module, neighbouring crop? |  |
| 9 | ARTS_00165_r12_c5 (3) | ARTS_00166_r12_c5 (1) | 216 | 0.42 | 0.98 | (+3, -3) | +0.6 | 0.67 | same cell? | lead yes |
| 10 | ARTS_00002_r6_c1 (2) | ARTS_00081_r5_c1 (1) | 210 | 0.43 | 0.48 | (+4, +266) | -1.4 | 0.31 | same module, neighbouring crop? |  |
| 11 | ARTS_00002_r6_c1 (2) | ARTS_00020_r7_c1 (1) | 204 | 0.34 | 0.47 | (+22, -258) | +1.9 | 0.31 | same module, neighbouring crop? |  |
| 12 | ARTS_00008_r3_c6 (3) | ARTS_00021_r1_c6 (1) | 110 | 0.48 | 0.98 | (+2, +6) | -0.1 | 0.31 | same cell? |  |
| 13 | CFVS_00132_r7_c4 (0) | CFVS_00134_r6_c3 (3) | 98 | 0.69 | 0.25 | (+255, +256) | -0.2 | 0.19 | same module, neighbouring crop? |  |
| 14 | CSIR_00107_r9_c3 (3) | CSIR_00117_r8_c4 (1) | 93 | 0.85 | 0.25 | (-254, +256) | +0.0 | 0.22 | same module, neighbouring crop? |  |
| 15 | CFVS_00109_r11_c1 (4) | CFVS_00112_r10_c1 (1) | 89 | 0.62 | 0.50 | (-0, +256) | +0.0 | 0.32 | same module, neighbouring crop? |  |
| 16 | ARTS_00029_r4_c3 (0) | ARTS_00171_r1_c3 (2) | 77 | 0.55 | 0.50 | (+1, +254) | +0.2 | 0.36 | same module, neighbouring crop? |  |
| 17 | ARTS_00025_r8_c1 (0) | ARTS_00117_r7_c2 (4) | 73 | 0.22 | 0.22 | (-196, +247) | +4.9 | 0.19 | same module, neighbouring crop? |  |
| 18 | CFVS_00019_r1_c4 (4) | CFVS_00027_r2_c4 (3) | 65 | 0.61 | 0.50 | (-1, -258) | -0.1 | 0.44 | same module, neighbouring crop? |  |
| 19 | CFVS_00168_r1_c5 (4) | CFVS_00170_r2_c4 (0) | 57 | 0.36 | 0.24 | (+241, -232) | -3.2 | 0.19 | same module, neighbouring crop? |  |
| 20 | CFVS_00156_r5_c6 (4) | CFVS_00160_r5_c5 (1) | 48 | 0.31 | 0.48 | (+248, +10) | -2.4 | 0.40 | same module, neighbouring crop? |  |
| 21 | ARTS_00011_r1_c4 (0) | ARTS_00024_r11_c6 (4) | 47 | 0.60 | 1.00 | (-0, -6) | -0.2 | 0.11 | same cell? |  |
| 22 | CFVS_00076_r1_c1 (2) | CFVS_00082_r1_c1 (4) | 37 | 0.43 | 1.00 | (-2, -4) | +0.0 | 0.53 | same cell? | lead yes |
| 23 | CFVS_00065_r1_c3 (2) | CFVS_00070_r1_c4 (3) | 35 | 0.50 | 0.50 | (-257, -1) | -0.1 | 0.28 | same module, neighbouring crop? |  |
| 24 | CFVS_00021_r3_c1 (4) | CFVS_00022_r11_c1 (3) | 28 | 0.28 | 0.99 | (+1, +0) | -0.3 | 0.70 | same cell? |  |
| 25 | ARTS_00002_r3_c2 (2) | ARTS_00081_r5_c1 (1) | 28 | 0.51 | 0.24 | (+258, -244) | +0.2 | 0.18 | same module, neighbouring crop? |  |
| 26 | ARTS_00106_r1_c5 (2) | ARTS_00107_r8_c4 (4) | 27 | 0.48 | 1.00 | (+513, +521) | -179.6 | 0.12 | same cell? |  |
| 27 | CFVS_00106_r12_c1 (2) | CFVS_00109_r11_c1 (4) | 27 | 0.24 | 0.48 | (+0, +262) | +0.5 | 0.07 | same module, neighbouring crop? |  |
| 28 | CFVS_00132_r1_c2 (0) | CFVS_00144_r1_c1 (1) | 26 | 0.23 | 0.57 | (+222, -58) | +0.2 | 0.03 | same module, neighbouring crop? | clustered |
| 29 | CSIR_00221_r6_c2 (2) | CSIR_00224_r6_c4 (0) | 24 | 0.18 | 1.00 | (-1, -1) | +0.1 | 0.80 | same cell? | hub |
| 30 | CFVS_00150_r2_c2 (1) | CFVS_00151_r3_c1 (2) | 20 | 0.22 | 0.27 | (+263, -296) | +2.0 | 0.09 | same module, neighbouring crop? |  |
| 31 | CSIR_00222_r6_c2 (3) | CSIR_00224_r6_c4 (0) | 19 | 0.16 | 1.00 | (+0, +2) | -0.0 | 0.68 | same cell? | hub |
| 32 | CSIR_00231_r11_c6 (0) | CSIR_00234_r9_c6 (1) | 19 | 0.17 | 1.00 | (-2, -4) | -0.0 | 0.49 | same cell? |  |
| 33 | CFVS_00027_r2_c4 (3) | CFVS_00029_r10_c5 (2) | 18 | 0.16 | 0.99 | (+516, +513) | -180.0 | 0.81 | same cell? |  |
| 34 | CSIR_00221_r6_c2 (2) | CSIR_00231_r6_c2 (0) | 18 | 0.16 | 1.00 | (-1, -2) | +0.2 | 0.75 | same cell? | hub |
| 35 | CSIR_00221_r6_c2 (2) | CSIR_00233_r5_c2 (4) | 18 | 0.13 | 1.00 | (-2, +0) | -0.1 | 0.74 | same cell? | hub |
| 36 | CFVS_00029_r10_c5 (2) | CFVS_00031_r5_c5 (3) | 18 | 0.21 | 1.00 | (-2, +0) | -0.1 | 0.50 | same cell? |  |
| 37 | ARTS_00029_r4_c3 (0) | ARTS_00171_r7_c2 (2) | 18 | 0.43 | 0.25 | (+256, -256) | -0.2 | 0.04 | same module, neighbouring crop? | clustered |
| 38 | CSIR_00233_r5_c2 (4) | CSIR_00234_r10_c4 (1) | 17 | 0.13 | 1.00 | (-1, -3) | +0.0 | 0.63 | same cell? | hub |
| 39 | CSIR_00224_r6_c4 (0) | CSIR_00230_r4_c5 (3) | 17 | 0.14 | 1.00 | (+513, +509) | +179.6 | 0.61 | same cell? | hub |
| 40 | CSIR_00221_r6_c2 (2) | CSIR_00225_r9_c4 (4) | 16 | 0.13 | 1.00 | (-0, -4) | +0.1 | 0.67 | same cell? | hub |
| 41 | CSIR_00221_r6_c2 (2) | CSIR_00222_r6_c2 (3) | 16 | 0.14 | 1.00 | (-2, -2) | -0.1 | 0.41 | same cell? | hub |
| 42 | CSIR_00178_r7_c1 (1) | CSIR_00207_r7_c5 (0) | 16 | 0.36 | 0.27 | (+748, +261) | -179.4 | 0.10 | same module, neighbouring crop? |  |
| 43 | ARTS_00011_r6_c2 (0) | ARTS_00024_r2_c1 (4) | 16 | 0.21 | 0.47 | (+267, +4) | -1.0 | 0.05 | same module, neighbouring crop? |  |
| 44 | CSIR_00224_r6_c4 (0) | CSIR_00234_r10_c4 (1) | 15 | 0.13 | 1.00 | (-1, -2) | -0.3 | 0.83 | same cell? | hub |
| 45 | CSIR_00222_r6_c2 (3) | CSIR_00231_r6_c2 (0) | 15 | 0.14 | 1.00 | (-0, -0) | +0.0 | 0.82 | same cell? | hub |
| 46 | CSIR_00231_r6_c2 (0) | CSIR_00234_r10_c4 (1) | 15 | 0.12 | 1.00 | (-2, -0) | -0.2 | 0.69 | same cell? | hub |
| 47 | CFVS_00098_r1_c6 (0) | CFVS_00102_r1_c6 (4) | 15 | 0.14 | 0.98 | (+20, -14) | +3.3 | 0.13 | same cell? |  |

### 3b. Image-id pairs behind the strongest pairs (>= 50 inliers) and all their pool cells (fold)

| image a | pool cells of a | image b | pool cells of b | best inliers |
|---|---|---|---|---|
| ARTS_00011 | r1_c1 (0), r1_c4 (0), r6_c2 (0) | ARTS_00024 | r11_c6 (4), r2_c1 (4) | 940 |
| ARTS_00106 | r1_c5 (2) | ARTS_00107 | r10_c4 (4), r1_c4 (4), r8_c4 (4) | 919 |
| ARTS_00008 | r3_c6 (3), r4_c1 (3), r6_c4 (3) | ARTS_00021 | r1_c6 (1), r2_c6 (1), r6_c2 (1) | 871 |
| ARTS_00013 | r1_c3 (4), r2_c6 (4) | ARTS_00026 | r1_c6 (3) | 804 |
| ARTS_00029 | r2_c5 (0), r4_c3 (0) | ARTS_00171 | r1_c3 (2), r1_c6 (2), r7_c2 (2) | 421 |
| CFVS_00101 | r5_c1 (3) | CFVS_00102 | r1_c6 (4), r2_c1 (4), r4_c1 (4), r6_c6 (4) | 412 |
| ARTS_00002 | r3_c2 (2), r4_c2 (2), r6_c1 (2) | ARTS_00081 | r5_c1 (1), r9_c6 (1) | 330 |
| ARTS_00006 | r10_c3 (3) | ARTS_00062 | r5_c4 (2), r8_c3 (2) | 253 |
| ARTS_00165 | r12_c5 (3) | ARTS_00166 | r12_c5 (1) | 216 |
| ARTS_00002 | r3_c2 (2), r4_c2 (2), r6_c1 (2) | ARTS_00020 | r10_c1 (1), r4_c6 (1), r7_c1 (1), r8_c6 (1), r9_c6 (1) | 204 |
| CFVS_00132 | r1_c2 (0), r7_c4 (0) | CFVS_00134 | r6_c3 (3) | 98 |
| CSIR_00107 | r9_c3 (3) | CSIR_00117 | r8_c1 (1), r8_c4 (1) | 93 |
| CFVS_00109 | r11_c1 (4), r1_c2 (4) | CFVS_00112 | r10_c1 (1), r4_c3 (1) | 89 |
| ARTS_00025 | r8_c1 (0) | ARTS_00117 | r2_c6 (4), r7_c2 (4) | 73 |
| CFVS_00019 | r1_c4 (4) | CFVS_00027 | r2_c4 (3) | 65 |
| CFVS_00168 | r1_c5 (4) | CFVS_00170 | r2_c4 (0) | 57 |

## 4. Reading (S unless marked E)
- **The two known cross-fold duplicates are confirmed** (ranks 9 and 22, overlap 0.98 and 1.00) and **the lead's five rejected pairs score 0 to 4**.
- **The duplicate problem is larger than 4 cells, and mostly at module level.** 19 cross-fold pairs have >= 50 inliers, with inlier ratios 0.22 to 0.98 (12 of 19 above 0.6; E). 17 of the 19 are crops one cell pitch apart (translation about 256 px, overlap 0.5 or 0.25; E), so the two image ids show **the same physical module**, and the two pool cells share half a cell or a corner of physical area. 16 image-id pairs carry such a pair; their images hold 60 pool cells (E). Several agree with module links that stage A already knew inside one fold: ARTS_00002 (fold 2) matches ARTS_00020 and ARTS_00081 (fold 1), which are a known same-cell group (ARTS_00020_r9_c6 = ARTS_00081_r9_c6); CFVS_00109 (fold 4) matches CFVS_00112 (fold 1), and CFVS_00112_r10_c1 = CFVS_00088_r10_c1 is a known pair (E: calibration.tsv). So cv5v2's module groups miss some image ids of the same module.
- Same-cell candidates beyond the known two (overlap >= 0.9 with >= 25 inliers): ARTS_00008_r3_c6 (f3) / ARTS_00021_r1_c6 (f1), 110 inliers (on the sheets both images appear to carry a serial ending "C-504" in their borders; the lead should confirm); ARTS_00011_r1_c4 (f0) / ARTS_00024_r11_c6 (f4), 47 (inliers clustered on the left edge, weak); CFVS_00021_r3_c1 (f4) / CFVS_00022_r11_c1 (f3), 28; ARTS_00106_r1_c5 (f2) / ARTS_00107_r8_c4 (f4), 27 at a 180-degree turn. These need the lead's eye.
- The CSIR pairs at 15 to 24 inliers (ranks 29 to 46) are hubs of flat mono cells at near-zero shift (CSIR_00221, 00222, 00224, 00231, 00233, 00234 match each other in many combinations): more likely a fixed pattern of one camera than one physical cell. Below 15 inliers the list is dominated by such weak matches.
- What it would mean for the benchmark (for the lead to rule; nothing changed): a cell whose module twin sits in a training fold is scored with partial leakage. The size of the effect cannot be read from this audit. The score-exclude option (F2_read_options.md) takes any list, so a v2 exclude list (for example every pool cell of the 16 image-id pairs in 3b, or only the same-cell candidates) can be read beside 532 at once; a regrouped split would need new runs.

## 5. Limits
- Mirror images are not matched (no flip); scale outside [0.87, 1.15] is refused; only same-source pairs; only pool cells (532).
- Calibration is in-sample (parameters chosen on the same 42 pairs). The miss rate on featureless mono cells is about 6 of 35 known pairs.
- The hub and tier labels are descriptive; no threshold here decides anything.
