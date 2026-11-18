# Split integrity: physical-module identity over all image ids, and what it does to cv5v2 (stage C, 15 Nov 2026)

Task: lead's ruling of 15 Nov 17:59 (log.md). Follow-up of results/stageB/SAMECELL_AUDIT.md. Builder: split-integrity agent.
Tags: E = measured here (file named), S = judgement. Pixels only for sealed cells (ruling L2): no label, mask, prediction or label summary of a legacy-test or E1 cell was read; no sealed image, and no cell of an image id that holds a sealed cell, is on any sheet. **Nothing was applied: cv5v2.json, cv5v2_groups.tsv, dup_crossfold_v1.tsv, pool_t9.txt and every existing list are untouched; the three new files under benchmark/splits/ are proposals.**
Code: /home/noob/work/bench_wt_split, branch bench_split (from bench_b b5bf0ae). Tool outputs: /home/noob/work/bench_reads/stageC/split/ (called O/ below). Tables and sheets: results/stageC/split_integrity/ (called R/ below).
Words: **pool cell** = one of the 532 labelled cells of cv5v2; **unlabelled pool** = the 11,938 unlabelled crops; **pool-only image id** = an image id with unlabelled crops only; **training image id** = an image id that holds pool cells. Outcome in short: section 11. The pre-set rule of section 1 turned out too loose for one kind of image-id pair; section 3b says where, section 3c gives the rule I would now choose, and every result is given under both.

## 1. Decision rule (written 15 Nov 18:45 IST, after the calibration pass of section 2 and BEFORE the full run; not changed after)

Unit: an image id (ARTS_00013). Two image ids are the same physical module if at least one link below holds; physical modules are the connected groups of links. BMRK and SDLE have one image id per cell and no neighbours in the crop: for them only "same physical cell" can be decided, never the module.

**Evidence class `serial` (ARTS only).** The printed serial in the right-hand border is cut from the r1_c6 crop (whole text) or the r2_c6 crop (its tail), turned, scaled to 24 px height, and two strips are compared in windows of 14 px, each window at its best shift within 4 px (bench/modid.py text_strip, strip_score). Score = the LOWEST window correlation.
- S1 `serial`: two whole strips, lengths within 6%, score >= **0.80**: same serial, same module.
- S2 `serial_tail`: a tail against a whole strip or another tail (aligned at the end, first 22 px of the tail skipped, at least 15 windows), score >= **0.80**: same last characters. Weaker (about 6 characters); accepted as a link and listed among the weak links.
- S3 different serial: two whole strips with score < 0.80 (or lengths more than 6% apart) are different modules. If a prior link (cells.tsv) joins two such image ids and the matcher gives no link, the prior link is dropped and reported. If the matcher links two image ids with different serials, both verdicts are reported as a conflict and the ids are NOT joined.

**Evidence class `match` (all sources).** Matcher: bench/samecell.py of the stage B audit, unchanged (masked SIFT, ratio 0.75, RANSAC similarity, 3 px). Applied to every cell image on disk (12,641: the 688 labelled pool / test / E1 cells, 26 other labelled cells, 11,927 unlabelled pool crops; 700 image ids).
- Cell pairs matched: (v) every pair of cell images, any source and any grid position, that a retrieval step proposes (one kd-tree over all 16.3 M descriptors, 16 neighbours per descriptor; a neighbour at <= 0.8 x the distance of the 16th neighbour is a vote; pairs with >= 5 votes); (s) same-source pairs at the same grid position with >= 3 votes; (l) every labelled pool, test or E1 cell against every same-source cell of another image id within one row and one column, exhaustively; (x) every pair inside CFVS, BMRK, SDLE.
- Grid relation of a matched cell pair: the fitted translation must be a whole number of cell pitches (256 px) within 40 px and the rotation 0 or 180 degrees within 8 degrees; then g = (position of b) - (position of a) - (crop offset in pitches) is the grid shift between the two images under which both crops show the same physical cells. **M0 eligible:** upright with |g| <= 1 row and <= 1 column, or turned by 180 degrees.
- **M1 `match`:** the best eligible cell pair of the two image ids has >= **30** inliers. Labelled `match_strong` when it has >= 320 (above every match of two different cells of one module seen in calibration).
- **M2 `match_multi`:** or at least two eligible cell pairs of >= **20** inliers agree on one relation.
- **M3 dominance guard:** the inlier sum of the winning relation (cell pairs >= 8 inliers) must be >= **2 x** the sum on all other relations. If M1 or M2 holds and M3 fails: `undecided`, listed, not linked.
- A best eligible pair of 20 to 29 inliers alone is a `candidate`: listed, not linked.
- Many weak pairs never add up to a link (reason: section 2c).

**Evidence class `cells_tsv` (prior).** The module groups already in cells.tsv (built 12 Nov from label overlap and high-pass correlation of labelled cells). Kept as links unless S3 drops them. Marked as not re-confirmed by pixels when no serial or match link supports them.

**Cells.** Inside one physical module with grid shift g: two cells are the **same physical cell** if their grid indices agree after g, **neighbouring crops** if they differ by at most one row and one column (the crops share a half or a quarter of their area), else **same module, no shared area**. For a link without a matcher relation (serial or cells_tsv only) g = (0, 0) is assumed and said so.

**Thresholds are not tuned after the full run.** If one turns out unusable, the result is given under this rule and, separately and labelled, under what I would now choose.

(Record: this section stood in the file before the full run; the rule's constants are in commit f8120c9 of 18:44:41, bench/modid.py T_STRONG 30, T_PAIR 20, T_SUM 8, DOMINANCE 2.0, G_MAX 1, and scripts/bench_modid_serial.py SERIAL_T 0.80. Added to this section after the run: only the count "700 image ids".)

## 2. Calibration (E; in-sample: the thresholds were set on these pairs, so recall and false-match rates here are optimistic)

Calibration image ids (O/cal_ids.txt, 134 ids): the 73 open ARTS ids with a whole serial strip, every image id of the 15 multi-id module groups of cells.tsv, the 16 image-id pairs of SAMECELL_AUDIT 3b, the lead's 5 rejected pairs. Calibration pass: O/pairs_calib (42,582 cell pairs: retrieval votes, every same-position pair, labelled neighbourhoods and every CFVS pair among these ids, plus null pairs inside each open image id). Serial calibration: the open strips only, truth = my reading of the strips (R/serial_reading.tsv, 73 whole strips and 16 tails; the strips are on R/serial_sheets/ for a person to check).

### 2a. Serial (E: O/serial/serial_calib.json)
| Mode | pairs with the same text (by reading) | their lowest score | pairs with different text | their highest score | at 0.80: recall | false matches |
|---|---|---|---|---|---|---|
| whole v whole | 20 | 0.937 | 2,608 | 0.728 | 20 / 20 | 0 / 2,608 |
| tail v whole | 31 | 0.848 | 1,137 | 0.624 | 31 / 31 | 0 / 1,137 |
| tail v tail | 7 | 0.999 | 113 | 0.433 | 7 / 7 | 0 / 113 |
- The closest different serials differ in one or two characters (…TSPC-265 v …TSPC-256: 0.728; …CSOC-053 v …056: 0.59). The text is a software overlay, so equal serials give near-identical strips (11 of the 20 pairs score >= 0.999).
- Two text formats: 20 characters (SA150911P636USYC-242) and 15 (SA2018112000304). The tail on r2_c6 exists only for the long format.
- Blind: 123 of the 205 ARTS image ids have no strip (no r1_c6 or r2_c6 crop on disk, or a module type without printed text: the mono modules ARTS_00004, 00006, 00062, 00173 and up).

### 2b. Match rule on image-id pairs with known truth (E: O/pairs_calib, O/decide_calibtest/idpairs.tsv)
| Known pairs | n | linked by the rule | best eligible cell pair (inliers) |
|---|---|---|---|
| ARTS, same serial (open ids) | 20 | **20** (all `match_strong`) | 867 to 3,418; relation (0, 0) in all |
| ARTS, different serial (open ids) | 2,608 | **0** | at most 16 (18 on any relation); largest sum of pairs >= 8 inliers: 179 (16 weak pairs, ARTS_00039 / 00040) |
| image-id pairs inside cells.tsv module groups | 59 | **51** | 33 to 1,527 for the linked ones |
| the 16 image-id pairs of SAMECELL_AUDIT 3b | 16 | 16 (found by the same matcher: not independent) | 57 to 3,103; ARTS_00006 / 00062 with a grid shift of one row |
| CFVS calibration ids in different cells.tsv groups | 979 | 5 (the 5 CFVS pairs of audit 3b) | not linked: at most 13 eligible, 28 on a far relation |
| lead's 5 rejected cell pairs | 5 | 0 | under 5 inliers each |
- The 8 cells.tsv pairs without a link: ARTS_00040 / 00061 (6 inliers; **their serials differ**: SA2018112000838 v SA2018112202893, so this prior link is wrong, S3) and 7 CFVS pairs with 0 to 5 inliers (CFVS_00007 / 00021 / 00063, 00065 / 00086, 00088 / 00112, 00114 / 00130, 00139 / 00143: mono cells at different stress stages, the misses the audit already named). Matcher recall on prior links, the wrong one removed: **51 of 58 = 0.88**.
- Margins (S): the weakest known link has 33 inliers, the strongest known non-link on an eligible relation 16 (28 on a far relation). T = 30 sits between; it was placed after seeing both.

### 2c. Null inside one image id: different cells of one module (E: pairs_calib tags cfar; 11,184 pairs, 40 per open image id, at least two grid positions apart)
| Source, cell type | pairs | with >= 30 inliers | largest |
|---|---|---|---|
| ARTS multi | 1,909 | 160 (8.4%) | 303 |
| CSIR multi | 3,408 | 58 (1.7%) | 246 |
| CSIR multi half cells | 278 | 13 | 241 (half-cut crops two rows apart do share area) |
| ARTS mono | 2,038 | 0 | 24 |
| CSIR mono | 3,460 | 12 | 47 |
| CFVS | 86 | 0 | 21 |
- **Different multicrystalline cells of one module match strongly at zero shift** (ARTS_00169 r6_c6 v r8_c6: 303 inliers): wafers cut next to each other from one brick carry almost the same grain pattern ("sister" cells; S for the cause, E for the numbers). 58 such pairs land on an eligible relation (up to 114 inliers), so one strong cell pair between two image ids is not by itself proof of one physical cell.
- Why the rule still holds on ARTS (E): across the 2,608 different-serial image-id pairs no cell pair exceeds 18 inliers. Sister cells stay inside a module there. For CSIR and CFVS there is no serial to check this; the dominance guard M3 and the label `match_strong` (>= 320) are the protection, and the links below 320 between multi cells are on the weak-link sheets (section 8).
- Why weak pairs are never summed (E): the known-different mono modules ARTS_00034 to 00040 reach sums of 100 to 179 from 10 to 16 pairs of 9 to 17 inliers each at the same grid position (a fixed pattern of that cell type).

### 2d. Retrieval step (E)
- Against exhaustive matching in the calibration pass: of the cell pairs with >= 20 inliers, 390 of 390 had >= 5 votes; 15 to 19 inliers: 6 of 7; 10 to 14: 66 of 90; 8 to 9: 90 of 137.
- Against the stage B audit (30,974 cross-fold pool pairs, all matched): every pair with >= 8 inliers (129) had >= 5 votes.
- So the rule's inputs (pairs of >= 20 and >= 30 inliers) are complete as far as measured; the sums of the dominance guard (pairs from 8 inliers) can miss some weak pairs outside the exhaustive sets.

### 2e. Where the method is blind (S unless marked)
1. BMRK (65 cells) and SDLE (18): one padded cell per image, no neighbours, no module id in any file. Only a repeated cell can be found.
2. CFVS (112 image ids): no unlabelled crops on disk, only the 187 labelled cells (1 to 5 per image id). Two image ids of one module are linked only if a labelled crop of one overlaps a labelled crop of the other, and the cells are mono (few keypoints). E: 7 of the 56 CFVS image-id pairs inside cells.tsv groups are invisible to the matcher.
3. Image ids with few crops on disk: 90 of 205 ARTS ids hold 1 to 4 crops (E: O/feats/inventory.tsv).
4. Mono cells without marks (E: section 2b misses); mirror images; scale changes beyond 0.87 to 1.15.
5. Half-cut layouts: the row pitch is not 256 px, so only same-crop matches get a grid relation.
6. No metadata: the dataset files carry nothing on modules, capture order or stress stage beyond the image id (E: BenchmarkELimages README and file lists; pool meta has stem, cell type, native size only).

## 3. Full run and module identity (E unless marked)

Order of events (clock of gaint, 15 Nov): features of 12,641 crops 18:08 to 18:12 (193 s); retrieval 18:24 to 18:31 (tmux bench_split_knn, 16.29 M descriptors, 636,775 image pairs with >= 3 votes); calibration pass 18:31 to 18:37; **rule commit f8120c9 at 18:44:41; full run started 18:44:45 from that commit** (first line of O/logs/pairs_full.log), tmux bench_split_pairs, 392,200 cell pairs (retrieval 122,378; labelled neighbourhoods 232,467; same position 18,867; small sources 19,463; nulls 14,200), ended 19:10:00 rc 0; O/pairs_full/cellpairs.tsv 6a4abb85 (80,246 rows: every pair with >= 5 inliers and every null pair). Serial: 77 whole strips (73 open ids, 4 ids that hold a legacy-test cell), 16 tails (5 ids with a tail only). Decision step: O/decide_fixed (pre-set rule), O/decide_posthoc (rule B, section 3c); copies in R/fixed_rule and R/rule_b.

### 3a. Under the pre-set rule
- 294 links: 20 `serial`, 59 `match_strong`, 159 `match`, 49 `match_multi`, 1 `serial_tail` alone, 6 `cells_tsv` alone. 700 image ids fall into **527 physical modules**.
- Serial against matcher, two independent kinds of evidence: all 20 same-serial pairs also carry a `match_strong` link (best pair 867 to 3,418). None of the 2,906 different-serial pairs is linked by the matcher (best eligible pair 16). No conflict.
- Tail-only ids: ARTS_00142 joins ARTS_00015 / 00028 / 00141 (tail 0.999, and match 1,580 to 3,385); ARTS_00017 joins ARTS_00030 (tail 0.867, and match 3,255; ARTS_00030 holds a legacy-test cell, section 5); ARTS_00168 joins ARTS_00161 by the tail alone (0.967; the two ids share no crop position on disk). ARTS_00117 and 00139 fit no strip.
- Prior links of cells.tsv (28, counted per image id against the first id of its group): 21 confirmed by a match link; 6 kept without pixel support (CFVS_00007 / 00021, 00007 / 00063, 00065 / 00086, 00088 / 00112, 00114 / 00130, 00139 / 00143); 1 dropped by S3 (ARTS_00040 / 00061: different serials, 6 inliers).
- BMRK, SDLE: no repeated cell. The strongest BMRK pair has 13 inliers (BMRK_00796_cell1630 with BMRK_00797_cell1631, and 00222_cell0882 with 00223_cell0883: ELPV neighbours in the numbering, not the same cell by the rule).

### 3b. The pre-set rule is unusable for image ids that both hold many crops (said as the brief asks)
M1 at 30 inliers and M2 were calibrated on pairs with few crops per image id or with near-identical images. In the full run three families of image ids with 20 to 144 crops each get linked although they are different modules (S, with the E facts below):
1. **ARTS_00173 to 00209 (mono modules without printed serial).** The pre-set rule merges 20 image ids into one module (and 5 more into another) through 56 links whose best pair has 20 to 35 inliers. E: only 17 to 56% of the same-position crop pairs match (15 to 36 positions per link); median inlier ratio 0.15 to 0.23 (the real weak links of this run: 0.27 and up). The module mosaics (R/sheets/family_ARTS_00174_mosaics.png) show different cell brightness patterns under the same horizontal bands: a pattern of the camera set-up, fixed in the image, not the module (S).
2. **CSIR_00031 to 00056 with CSIR_02427 to 02451 (multi modules).** The pre-set rule gives two modules of 15 image ids each. E: the strong structure inside is clean and one-to-one: CSIR_00031 + k goes with CSIR_02427 + k (k = 0 to 8) and with one or two later image ids each (for example CSIR_00039, 02435, 02441, 02447); 46 of these 48 links match on 60 to 100% of the same positions (median 93%). These groups are chained by 17 weak links: 10 on a 180-degree relation that the 12-row grid does not allow (k = (11, 7) where a turned 12 x 6 module gives (13, 7); for example CSIR_02430 with 02447: best pair 97, 7 of 29 positions), 7 with 9 to 33% of same positions matching. S: sister cells of other modules, as in section 2c, now seen between modules.
3. **Half-cut ids with 144 crops** (CSIR_00298 / 00334, 00299 / 00334, 00333 / 00335): 4 or 5 of 110 to 120 same positions, on a turned relation that does not fit the 24-row grid.
- The same full run also holds real weak links that only many agreeing cells can show: CSIR_00205, 00217 to 00220 (5 image ids; a same-position pair has 12 to 124 inliers at the median; 88 to 100% of 26 to 66 same positions match; two orientations that are consistent over all ten pairs); CSIR_02363 to 02382 (mono, each id has exactly one partner, 65 to 100% of positions). So "many weak pairs agree" is evidence when nearly all positions agree, and is not when a third do.

### 3c. Rule B: what I would now choose (POST HOC: chosen with the full-run result in view; not pre-registered; every number is given under both rules)
Rule B = the pre-set rule plus two guards on match links (bench/modid.py posthoc_guard):
- **B0 grid fit:** a 180-degree relation k must map every crop of one image onto row and column >= 1 of the other, and, when an image id holds >= 20 crops, k may exceed the largest row / column seen by at most 2.
- **B2 coverage:** if at least **5** crop pairs at the same physical position exist on disk for the two image ids, at least **60%** of them must match (>= 8 inliers on the winning relation). Exempt: a best pair of >= 320 inliers, or >= 100 when both cells are mono (mono cells have no sister cells; the largest match of two different mono cells of one image id in calibration is 47).
- Effect: 80 of the 287 match links of the pre-set rule are dropped (67 coverage, 13 grid fit): 56 in family 1, 19 in family 2 (the 17 chaining links and 2 real ones, below), 3 in family 3, plus ARTS_00011 / 00116 (117 inliers, 0 of 5 positions) and CSIR_00178 / 00207 (19 of 32 positions; the two stay in one module through CSIR_00204 and 00206). **561 physical modules.**
- On the calibration pairs of section 2b rule B decides exactly as the pre-set rule (all those links are strong or have fewer than 5 same-position pairs).
- **The cv5v2 tables of section 4 and the sealed-set tables of section 5 are byte-identical under the two rules** (E: cmp of O/decide_fixed and O/decide_posthoc files). The rules differ only in pool-only image ids.
- Links rule B keeps that I doubt (S; on R/sheets/weak_*.png): CSIR_00034 / CSIR_02431 (`match_multi`, two pairs of 20 and 22 inliers on a turned relation, 2 of 4 positions; it joins two of the nine CSIR groups of family 2); ARTS_00150 / 00151 (127 inliers, multi cells, 0 of 3 positions). True links rule B drops but that stay joined through other image ids: CSIR_00037 / 02433 (3 of 7 positions), CSIR_02430 / 02448 (310 inliers, 14 of 28).

### 3d. Physical modules and image ids per source
| Source | image ids | modules, pre-set rule | modules, rule B | modules with >= 2 image ids (rule B) | image ids in them | how the image ids are linked (rule B, best class per id) |
|---|---|---|---|---|---|---|
| ARTS | 205 | 139 | **164** | 30 | 71 | serial 31, match_strong 32, match 6, serial_tail 2, single 134 |
| CSIR | 300 | 230 | **239** | 34 | 95 | match_strong 44, match 51, single 205 |
| CFVS | 112 | 75 | **75** | 18 | 55 | match_strong 6, match 41, cells_tsv only 8, single 57 |
| BMRK | 65 | 65 | 65 | 0 | 0 | not decidable (single-cell crops); no repeated cell found |
| SDLE | 18 | 18 | 18 | 0 | 0 | not decidable; no repeated cell found |
| all | 700 | 527 | **561** | 82 | 221 | |
- The 532 pool cells: 354 image ids, 330 cv5v2 groups, **304 physical modules** (both rules): ARTS 107 ids in 92 modules, CFVS 104 in 73, CSIR 76 in 72, BMRK 50, SDLE 17. 100 of the 354 pool image ids sit in a module with another image id.
- Of the 82 multi-id modules, 50 hold pool cells, 12 hold legacy-test cells, 0 hold E1 cells, 28 are unlabelled-pool only (R/modules_multi_id_rule_b.tsv).
- Side finding for pool arms (E: R/pool_t9_in_labelled_modules.tsv): pool_t9.txt was cleaned by image id. Under rule B **1,003 of its 6,424 cells (33 image ids) belong to a physical module that holds labelled cells**: 564 to modules with pool (P532) cells, 439 to modules with `_rf` cells, 1 to a module with a legacy-test cell (ARTS_00010, twin of ARTS_00023), 0 to E1 modules. Under the pre-set rule 1,475.
- Side finding for the label pack U4: its 7 image ids are 6 physical modules (CSIR_00298 = CSIR_00299, match 1,405); none is linked to E1.

### 3e. Not linked, listed (R/rule_b/idpairs.tsv, column match_cls)
- `undecided` 28 (dominance guard): 15 among half-cut ids, 4 in family 2, 3 inside CSIR_00209 to 00212 (joined anyway by other links), 4 of CSIR_00180 with CSIR_00209 to 00212 (sums 6,901 to 9,097 against 3,615 to 5,409 on another relation; S: probably one more image of that module, pool only), ARTS_00007 / 00063, ARTS_00102 / 00103.
- `candidate` 69 (one pair of 20 to 29 inliers): 30 in family 1, 30 among half-cut ids, 7 other CSIR, 2 CFVS (section 4d).

## 4. What it does to cv5v2 (E: R/rule_b/cv5v2_*.tsv; identical under both rules)

### 4a. Counts
- **24 physical modules span two cv5v2 folds** (none spans three). They hold 57 image ids and **91 pool cells**: every one of these cells is held out while at least one pool cell of its physical module trains.
- The stage B audit had 16 image-id pairs (15 modules, 60 cells); 9 modules are new here.

| Source | modules spanning folds | image ids | cells affected | fold 0 | fold 1 | fold 2 | fold 3 | fold 4 |
|---|---|---|---|---|---|---|---|---|
| ARTS | 12 | 26 | 48 | 7 | 12 | 12 | 7 | 10 |
| CFVS | 8 | 23 | 32 | 3 | 4 | 3 | 10 | 12 |
| CSIR | 4 | 8 | 11 | 3 | 3 | 1 | 4 | 0 |
| BMRK, SDLE | 0 | 0 | 0 | | | | | |
| all | 24 | 57 | **91** | 13 | 19 | 16 | 21 | 22 |
- The 91 cells hold 22.7% of the ground-truth crack px and 13.2% of the inactive px of the pool (35 of 229 crack cells, 8 of 48 inactive cells; E: O/effect_cv02).
- Closest training cell of the same module, by grid geometry: **same physical cell 4 cells** (the two pairs of dup_crossfold_v1: ARTS_00165 / 00166 r12_c5, 216 inliers; CFVS_00076 / 00082 r1_c1, 37), **neighbouring crop (shared half or quarter) 38 cells**, same module without shared area 49 cells. Cross-fold cell pairs: 2 same cell, 21 neighbouring crops, 66 without shared area (R/rule_b/cv5v2_cellpairs_crossfold.tsv).

### 4b. The 24 modules
| physical module | image ids (fold, pool cells) | cells | evidence between its image ids | in the stage B audit |
|---|---|---|---|---|
| ARTS_00002 | ARTS_00002(f2,3), ARTS_00020(f1,5), ARTS_00081(f1,2) | 10 | match 314; match_strong 330; match_strong 1,004 | yes |
| ARTS_00006 | ARTS_00006(f3,1), ARTS_00062(f2,2) | 3 | match 262 (mono; grid shifted by one row) | yes |
| ARTS_00008 | ARTS_00008(f3,3), ARTS_00021(f1,3) | 6 | serial 0.994, match 2,352 | yes |
| ARTS_00011 | ARTS_00011(f0,3), ARTS_00024(f4,2) | 5 | serial 1.000, match 3,103 | yes |
| ARTS_00012 | ARTS_00025(f0,1), ARTS_00117(f4,2) | 3 | match_strong 1,725 | yes |
| ARTS_00013 | ARTS_00013(f4,2), ARTS_00026(f3,1) | 3 | serial 0.991, match 2,958 | yes |
| ARTS_00016 | ARTS_00029(f0,2), ARTS_00171(f2,3) | 5 | serial 0.949, match 1,577 | yes |
| ARTS_00018 | ARTS_00019(f2,1), ARTS_00031(f2,1), ARTS_00032(f4,1) | 3 | serial 0.991; match_strong 3,260 and 3,218 | **new** |
| ARTS_00106 | ARTS_00106(f2,1), ARTS_00107(f4,3) | 4 | serial 1.000, match 2,790 | yes |
| ARTS_00111 | ARTS_00111(f0,1), ARTS_00114(f3,1) | 2 | match_strong 810 | **new** |
| ARTS_00118 | ARTS_00118(f1,1), ARTS_00119(f2,1) | 2 | match_strong 2,166 | **new** |
| ARTS_00165 | ARTS_00165(f3,1), ARTS_00166(f1,1) | 2 | match 263 (lead: same crack) | yes (dup v1) |
| CFVS_00017 | CFVS_00017(f3,1), 00019(f4,1), 00020(f3,1), 00022(f3,2), 00027(f3,1), 00031(f3,2) | 8 | 00019 joins by match 65 with 00027; the rest match 52 to 159 | yes |
| CFVS_00065 | CFVS_00065(f2,1), CFVS_00070(f3,1), CFVS_00086(f2,1) | 3 | 00065 / 00070 match 35; 00065 / 00086 cells_tsv only | **new** |
| CFVS_00076 | CFVS_00076(f2,1), CFVS_00082(f4,1) | 2 | match 37 (lead: same cell) | dup v1 |
| CFVS_00088 | CFVS_00088(f1,1), CFVS_00109(f4,2), CFVS_00112(f1,2) | 5 | 00109 / 00112 match 89; 00088 / 00112 cells_tsv only | yes |
| CFVS_00101 | CFVS_00101(f3,1), CFVS_00102(f4,4), CFVS_00103(f4,2) | 7 | match_strong 412; match 185 | yes |
| CFVS_00132 | CFVS_00132(f0,2), CFVS_00134(f3,1) | 3 | match 98 | yes |
| CFVS_00156 | CFVS_00156(f4,1), CFVS_00160(f1,1) | 2 | match 48 | **new** |
| CFVS_00168 | CFVS_00168(f4,1), CFVS_00170(f0,1) | 2 | match 57 | yes |
| CSIR_00104 | CSIR_00104(f0,1), CSIR_00135(f3,3) | 4 | match 63, 43 of 43 same positions, 138 agreeing cell pairs | **new** |
| CSIR_00106 | CSIR_00106(f2,1), CSIR_00116(f0,1) | 2 | match_strong 1,551 | **new** |
| CSIR_00107 | CSIR_00107(f3,1), CSIR_00117(f1,2) | 3 | match_strong 1,563 | yes |
| CSIR_00178 | CSIR_00178(f1,1), CSIR_00207(f0,1) | 2 | through pool-only CSIR_00204 and 00206 (match 70, 118, 89; turned and shifted relations consistent); direct pair match 77, 19 of 32 positions | **new** |
- The module is named after its smallest image id, which can be a pool-only id (ARTS_00012, 00016, 00018).
- Weakest evidence in this table (S): CFVS_00065 / 00070 (35 inliers, one neighbouring crop), CFVS_00076 / 00082 (37; confirmed by the lead), CFVS_00156 / 00160 (48), the two cells.tsv-only links, CSIR_00178 / 00207. All CFVS links are single crop pairs: CFVS has no other crops on disk.

### 4c. Inside one fold
cv5v2 has 330 groups, the module map 304 modules for the same cells: besides the 24 above, the map joins cv5v2 groups that already sit in one fold. Those need no action for scoring; they matter for the group bootstrap (fewer independent groups). R/rule_b/module_identity.tsv has them.

### 4d. Pairs the rule does not link but that would add cells (not decided; R/eye_candidates_cells.tsv, R/sheets/crossfold_not_linked_1.png)
| pair (folds) | evidence | my reading (S) |
|---|---|---|
| CFVS_00098 (f0) / CFVS_00102 (f4), r1_c6 both | 15 inliers, same crop | **same cell by eye**: the same crack and the same dash (tile 8 of the sheet). The matcher is blind here |
| CFVS_00106 (f2) / CFVS_00109 (f4) | 27 inliers, neighbouring crop | likely one module (candidate class) |
| CFVS_00150 (f1) / CFVS_00151 (f2) | 20 inliers, diagonal neighbour | open |
| ARTS_00007 (f3) / ARTS_00063 (f0) | 97 inliers, undecided: 542 on the winning relation against 286 elsewhere, 2 of 27 positions | open; ARTS_00006 / 00062 are the neighbours in id and are linked |
If all four are accepted, 8 more pool cells join the list (99 in all). 59 unlinked cross-fold pool pairs have >= 10 inliers (R/crossfold_pairs_not_linked.tsv); the others are far relations or the flat CSIR_0022x mono cells the audit called hubs.

## 5. The sealed sets (pixels only; ids and scores only; E: R/sealed/)

### 5a. E1 (106 cells, 71 image ids: 66 CSIR, 5 BMRK)
- **No E1 image id is linked to any other image id** under either rule: not to an image id with pool cells, not to a legacy-test id, not to a pool-only id. No E1 image id is shared with pool cells. pool_t9 holds 0 cells of an E1 module.
- **No E1 cell matches any pool cell:** the largest inlier count of an E1 cell with a pool cell is 7 (BMRK single cells, no grid relation), below every level in section 2. Between crops of E1 image ids and crops of image ids with pool cells (any crop, any position, any turn): at most 7.
- Coverage of the test (E: R/sealed/sealed_cover.json): 66 x 76 = 5,016 pairs of an E1 CSIR image id with a CSIR image id that holds pool cells. 1,626 of them (32%) have crops on disk that would share area under one grid. Every E1 cell was matched against every same-source crop within one row and one column: 10,603 cell pairs of an E1 cell with a crop of a training image id (1,150 of them with a pool cell itself); the unlabelled crops of E1 image ids were matched where the retrieval proposed them. **None reached 5 inliers** (BMRK: 7).
  - 19 E1 image ids are full-cell modules (18 multi, 1 mono): each could be tested against 17 to 62 of the 76 training image ids (median 39); 698 of 1,444 id pairs testable, 288 with multi cells on both sides.
  - 47 E1 image ids are half-cut modules (62 cells). The pool has no half-cut cell, so by layout none of the 76 training image ids can be a twin. 10 of them have no overlapping crop with any training id.
  - 48 of the 66 E1 image ids have one crop on disk (the E1 cell itself); 25 of the 76 training ids too.
- One relation of an E1 image id that is NOT a link: unlabelled pool crops CSIR_00300 r19 to r21 c5 (the E1 half-cut module) match CSIR_00335 r2 to r4 c5 (pool only, in label pack U4) with 38 to 51 inliers, ratio 0.5 to 0.7, at a grid shift of 17 rows. S: sister half-cells of another module, not the same module (a module twin cannot be 17 rows off). The pack cells of CSIR_00335 (r2_c2, r8_c4, r9_c4, r10_c4) are not these cells.
- 5 BMRK E1 cells against 50 BMRK pool cells: every pair matched, at most 7 inliers. Module identity of BMRK cannot be tested at all.
- **Verdict (S): on the pixels on disk E1 holds no module and no cell that the pool trains on, and no neighbouring crop.** What this cannot exclude: a full-cell E1 module and a training image id of the same module whose crops on disk do not overlap (52% of the full-cell id pairs), and any BMRK module identity. "Unseen modules" is supported, not proven.

### 5b. Legacy test (50 cells, 48 image ids)
| | image ids | cells |
|---|---|---|
| the test image id itself also holds pool cells (known design of the legacy split; rows 1 and 2 overlap) | 25 (ARTS 10, CFVS 9, CSIR 6) | |
| a twin image id holds pool cells | 14 (ARTS 3: 00020, 00030, 00166; CFVS 11) | |
| neither | 16 (ARTS_00047, CFVS_00104, CFVS_00129, CSIR_00057, CSIR_00173, 10 BMRK, 1 SDLE) | 16 |
| test cell is the same physical cell as a pool cell | | **8** (ARTS_00020_r5_c1 = ARTS_00081_r5_c1, 1,004 inliers; CFVS_00006_r5_c5; CFVS_00018_r4_c4; CFVS_00027_r4_c4; CFVS_00033 / 00035 / 00042 r8_c4; CFVS_00063_r3_c1 by the cells.tsv link only, 0 and 5 inliers) |
| test cell is a neighbouring crop of a pool cell (closest relation) | | **7** (ARTS_00023_r7_c4, ARTS_00073_r4_c2, ARTS_00145_r5_c2, CFVS_00180_r11_c4, CSIR_00055_r7_c4 inside their own image id; CFVS_00026_r9_c5 with CFVS_00029_r10_c5, 92 inliers; CFVS_00174_r2_c3 with CFVS_00170_r2_c4, 115) |
| same module, no shared area | | 19 |
- The 7 D6 test twins that cells.tsv records are confirmed by pixels (58 to 1,004 inliers); CFVS_00063_r3_c1 (`twin_candidate_unchecked`) is not confirmed and not refuted (mono, matcher blind).
- **New by pixels (not in the module groups of cells.tsv):** ARTS_00030 (test) = ARTS_00017 (pool cells in fold 1): serial tail 0.867 and match 3,255; cells.tsv had ARTS_00030_r8_c6 only as an unchecked candidate. CFVS_00026 (test) with CFVS_00029 (92). CFVS_00174 (test) with CFVS_00168 / 00170 (115). ARTS_00023 (test, 3 pool cells in its own id) = ARTS_00010 (pool only, match 3,303).
- Lists by image id and by cell pair with inlier counts: R/sealed/sealed_image_ids.tsv, sealed_cellpairs.tsv (124 pairs), sealed_candidates.tsv, sealed_cover.tsv.

## 6. Effect size, no retraining (E)

### 6a. Reads with the proposed exclude list (91 cells) beside 532 cells
bench_read_w1.py with --score-exclude benchmark/splits/score_exclude_v2.txt (adcdf4af), run from bench_wt_split at f101e8e, commands of harness/w1read plus the option (O/run_reads.sh); caches copied from the stage B fix reads. Operating points, tables, contrasts and the A/A margin are refitted on the 441 kept cells. R/reads/.

| arm (OP-A) | crack IoU 532 / 441 | relF1@2 | inactive IoU | mIoU-R13 |
|---|---|---|---|---|
| PF, gaint, 4 seeds | 0.3646 / 0.3465 | 0.8443 / 0.8262 | 0.5025 / 0.5017 | 0.6130 / 0.6057 |
| PF, cv02, 5 seeds | 0.3648 / 0.3471 | 0.8441 / 0.8263 | 0.5027 / 0.5053 | 0.6122 / 0.6058 |
| HOUSE | 0.3821 / 0.3655 | 0.8496 / 0.8316 | 0.5217 / 0.5227 | 0.6093 / 0.6027 |
| unet_r34_pf | 0.3644 / 0.3434 | 0.8425 / 0.8203 | 0.5222 / 0.5195 | 0.6122 / 0.6047 |
| dlv3p_r34_pf | 0.3543 / 0.3396 | 0.8349 / 0.8162 | 0.4779 / 0.4670 | 0.6092 / 0.6018 |
| hanifi_vgg16_unet_pf | 0.3491 / 0.3308 | 0.8377 / 0.8192 | 0.4979 / 0.4936 | 0.6095 / 0.6019 |
| ucf_dlv3_r50_pf | 0.2866 / 0.2806 | 0.7669 / 0.7576 | 0.4972 / 0.4908 | 0.5741 / 0.5674 |
| pratt_dlv3p_wcec | 0.2582 / 0.2507 | 0.7510 / 0.7348 | 0.5063 / 0.5019 | 0.6039 / 0.5996 |
- **A/A margin M on the clean cells:** gaint crack IoU 0.0100, relF1@2 0.0100, inactive 0.0612 (532: 0.0543), mIoU-R13 0.0100; cv02 0.0100, 0.0106 (532: 0.0100), 0.0550 (532: 0.0503), 0.0100.
- Every arm drops: crack IoU by 0.006 to 0.021, relF1@2 by 0.009 to 0.022, mIoU-R13 by 0.004 to 0.008; inactive IoU moves by -0.011 to +0.003. PF: -0.018 crack IoU and -0.018 relF1@2 on both machines.
- **No contrast changes its reading.** Order of the seven arms by crack IoU and by relF1@2 is the same on 441 cells. HOUSE - PF crack IoU: +0.0173 [+0.0107, +0.0241] on 532, +0.0183 [+0.0107, +0.0257] on 441 (PASS* both; OP-W +0.0110 and +0.0107, PASS* both). No other PASS*, no interval changes sign (full table R/reads/rows1_table.md). Largest shifts of a contrast: ucf_dlv3_r50_pf - PF crack IoU -0.078 to -0.067; pratt -0.107 to -0.096; unet_r34_pf relF1@2 -0.0016 to -0.0059 (inside M).
- OP-W values and the 441-cell report: R/reads/rows1_read.txt, w1g4_read.txt (section "score-exclude"), read_x441.txt in O/reads.

### 6b. Direct estimate: PF scores on affected against unaffected cells (bench_split_effect.py; PF at argmax, pooled; R/effect/)
| cells (PF cv02, 5 seeds; gaint 4 seeds in brackets) | n | crack cells | crack IoU | relF1@2 | relR@2 | relP@2 | inactive IoU | mIoU-R13 |
|---|---|---|---|---|---|---|---|---|
| unaffected | 441 | 194 | 0.347 (0.347) | 0.826 (0.826) | 0.775 | 0.884 | 0.505 | 0.606 |
| affected | 91 | 35 | 0.424 (0.424) | 0.902 (0.902) | 0.881 | 0.924 | 0.490 | 0.633 |
| affected, same cell trains | 4 | 2 | 0.462 | 0.943 | 0.916 | 0.971 | n/a | 0.773 |
| affected, neighbouring crop trains | 38 | 14 | 0.311 | 0.864 | 0.864 | 0.864 | 0.390 | 0.615 |
| affected, same module only | 49 | 19 | 0.473 | 0.917 | 0.885 | 0.951 | 0.492 | 0.637 |
| unaffected, same source and cell type as the affected | 333 | 129 | 0.339 | 0.817 | 0.766 | 0.876 | 0.514 | 0.606 |
- Same source and cell type, weighted by the affected cells' crack px: affected minus unaffected **crack IoU +0.072 (gaint +0.073), relF1@2 +0.059 (+0.059), relR@2 +0.077 (+0.080), relP@2 +0.038 (+0.035)**; mIoU-R13 +0.054 (+0.056, weighted by cells); inactive IoU -0.015 (+0.003): one CSIR cell holds a quarter of the affected inactive px.
- By stratum (cv02): CFVS mono 0.397 against 0.362 crack IoU, 0.887 against 0.836 relF1@2 (52,135 crack px affected); ARTS multi 0.339 against 0.291, 0.867 against 0.811 (2,914 px); CSIR mono 0.553 against 0.339, 0.966 against 0.878 (14,263 px on 4 crack cells).
- Reading (S): descriptive, not causal. The affected modules were not drawn at random: they are modules imaged several times, many of them stress-test modules with large cracks. The gap does not grow with closeness (neighbouring crops score lowest), which a pure leakage effect would. Upper bound if the whole gap were leakage: 0.227 (share of crack px) x 0.072 = about **0.016 crack IoU** and about 0.013 relF1@2 on the 532-cell headline, the same size as the drop of section 6a (0.018). So the exclude read cannot tell "these cells are easier" from "these cells leak"; only a retrain on a regrouped split can. Absolute levels on cv5v2 as built are too high by at most about 0.02 in crack IoU and relF1@2 (S).

## 7. Proposals (new files, NOT applied; built from rule B; identical under the pre-set rule for every pool cell)
| File | md5 | Content |
|---|---|---|
| benchmark/splits/module_identity_v3.tsv | 94a357a8 | 700 rows: image_id, physical_module (rule B), evidence_class, score (serial: lowest window correlation; match: best pair inliers), source, image ids in the module, crops on disk, sets; plus physical_module_fixed_rule and evidence_class_fixed_rule |
| benchmark/splits/score_exclude_v2.txt | adcdf4af | 91 pool cells (section 4), '#' comment head, read by bench.w1read.load_exclude; holds the 4 cells of dup_crossfold_v1 |
| benchmark/splits/cv5v3_proposal.tsv | 15c505aa | 532 rows: stem, legacy_split, group_v3 (cv5v2 group joined with physical module), cv5v2_group, physical_module, fold_cv5v2, fold_cv5v3, moved |
- **cv5v3:** 303 groups (cv5v2: 330). Each of the 24 fold-spanning groups goes to the fold that already holds most of its cells (ties: the smaller fold, then the lower id). **31 cells move** (ARTS 18, CFVS 9, CSIR 4): the minimum for "no group spans folds"; 501 cells keep their fold. Moves: R/cv5v3_moves.tsv.

| fold | cells v2 / v3 | groups | crack cells | crack px (v1.1) | inactive cells | inactive px | ARTS | BMRK | CFVS | CSIR | SDLE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 107 / 106 | 66 / 61 | 51 / 52 | 49,311 / 56,901 | 10 / 12 | 56,753 / 57,585 | 36 / 34 | 10 | 34 / 36 | 23 / 22 | 4 |
| 1 | 111 / 110 | 67 / 62 | 44 / 45 | 60,467 / 60,474 | 8 / 8 | 57,565 / 57,565 | 39 / 37 | 10 | 36 / 37 | 22 / 22 | 4 |
| 2 | 104 / 106 | 63 / 59 | 46 / 44 | 57,196 / 56,810 | 7 / 7 | 57,142 / 57,142 | 37 / 38 | 10 | 31 / 31 | 23 / 24 | 3 |
| 3 | 104 / 105 | 67 / 59 | 46 / 47 | 99,932 / 92,831 | 15 / 14 | 56,785 / 56,334 | 34 / 37 | 10 | 34 / 32 | 23 / 23 | 3 |
| 4 | 106 / 105 | 67 / 62 | 42 / 41 | 40,640 / 40,530 | 8 / 7 | 56,775 / 56,394 | 36 / 36 | 10 | 34 / 33 | 23 / 23 | 3 |
- Balance holds: fold sizes 105 to 110, crack cells 41 to 52, inactive px within 1.5% of cv5v2. The three classes with held-out px and no training px in one fold stay the same (class 19 in fold 0, class 12 in fold 2, class 8 in fold 3). Per-class cell counts per fold: R/cv5v3_class_cells.tsv; tables R/cv5v3_balance.md.
- Folds change for 31 cells but training sets change in all five folds, so a cv5v3 table needs new runs of every arm (S). The exclude list needs none.
- If the lead accepts pairs of section 4d by eye, group_v3 and the exclude list change for those cells; rerun scripts/bench_split_propose.py after adding the links.

## 8. For the lead's eyes (pool and labelled POOL cells only; no cell of an image id that holds a sealed cell)
| Sheet (R/sheets/, with a .tsv beside) | Content |
|---|---|
| strong_new_1 to 3.png | the 30 strongest links that cells.tsv did not have (inlier sums 40,254 to 343,731, best pair 257 to 3,418) |
| weak_1 to 4.png | 40 tiles: the accepted match links with the weakest best pair (21 to 78 inliers; 30 `match`, 5 `match_multi`), the tail-only link, 4 cells.tsv-only links. Tile header: classes, best pair, sum, pairs, relation, same positions matched / possible. 7 links are not drawn because an image id holds a sealed cell |
| dropped_by_rule_b_1, 2.png | the 20 strongest links of the pre-set rule that rule B drops |
| not_linked_1, 2.png | undecided and candidate pairs |
| crossfold_not_linked_1, 2.png | the 20 strongest unlinked pool pairs in different folds (section 4d) |
| family_ARTS_00174_mosaics.png | four module mosaics of family 1 |
| R/serial_sheets/strips_full_1, 2.png, strips_tail.png | every serial strip of the open ARTS ids, equal serials adjacent; my reading in R/serial_reading.tsv |
- Limits of the sheets (S): for the weak CSIR links between dark low-texture cells (CSIR_00205 family) one tile cannot convince; the evidence is the share of positions that agree, printed in the header.

## 9. Limits, and what I could not decide
1. **CFVS is only partly visible.** 112 image ids, 187 crops. A link needs two labelled crops that overlap. 6 prior links have no pixel support; the 4 pairs of section 4d are open; more CFVS twins without overlapping crops can exist and cannot be found on this data (S).
2. **BMRK and SDLE:** no module identity at all. If ELPV's cell numbering follows modules (not checked: ELPV is not on disk), BMRK cells with neighbouring numbers share a module.
3. **E1:** section 5a. Not excluded: twins without overlapping crops; BMRK.
4. **Rule B is post hoc.** Its guards (5 positions, 60%, 100 for mono) were set on the same full run they are applied to. It changes nothing for pool or sealed cells; it changes the module count of ARTS and CSIR pool-only ids (527 against 561). Two links under rule B look wrong to me (section 3c). A pre-registered rerun would need new data.
5. **Sister cells** (section 2c, 3b): different cells with the same grain pattern exist inside modules and, in CSIR, between modules. A single multi-cell pair under 320 inliers between image ids with few crops (ARTS_00165 / 00166 at 263 is confirmed by the lead; ARTS_00002 / 00020, ARTS_00150 / 00151) rests on the serial calibration (0 of 2,906) and on the eye.
6. **Thresholds are in-sample** (section 2); recall on prior links 0.88; the weakest known link (33) is close to T = 30.
7. Serial: 123 ARTS ids without a strip; the tail covers about 6 characters.
8. The leak estimate is descriptive (section 6b).
9. Not done: a dense matcher for featureless mono cells; mirror images; the 159k full pool (not on disk).

## 10. Record
- Code: /home/noob/work/bench_wt_split, branch bench_split from bench_b b5bf0ae, 13 files added, none changed: bench/modid.py, bench/splitfix.py, scripts/bench_modid_{feats,match,serial,decide,sheets,sealed_cover}.py, scripts/bench_split_{propose,effect,readtable,extras}.py, tests/test_bench_modid.py (25 tests). Commits f8120c9 (rule, 18:44:41), 2ef7160, 9682207, f101e8e (decide under both rules, proposals, reads), f966127 (side tables tool). Full pytest: 638 passed, 4 skipped at f101e8e (O/logs/pytest_full_f101e8e.log); 639 passed, 4 skipped at f966127 (O/logs/pytest_full.log). No push; worktree clean.
- Which tool wrote what: R/fixed_rule, R/rule_b, R/sealed (decide, sealed_cover); R/serial, R/serial_sheets (serial); R/sheets strong / weak / not_linked / dropped (sheets); R/cv5v3_*, the three proposal files (propose); R/reads (bench_read_w1.py, readtable); R/effect (effect); R/modules_multi_id_rule_b.tsv, pool_t9_in_labelled_modules.tsv, crossfold_pairs_not_linked.tsv, eye_candidates_cells.tsv, sheets/crossfold_not_linked_*, sheets/family_* (extras). Commands and logs: O/logs/.
- Commit messages end with the attribution line this session is required to use (Claude Fable 5.2 and the session link), not with the Opus 5.5 line of the brief: the brief's line would name a model that did not write the code.
- Sessions I started, all ended by themselves: tmux bench_split_knn (pane 2158801), bench_split_pairs (pane 2300408), bench_split_reads (pane 3575646), bench_split_pytest (panes 3636877, 3656473). One own process stopped by its PID (2108588, a profiling script that re-read an array in a loop). At most 8 workers, CPU only, nice 19. No other tree, queue or session touched; el_bench, bench_wt_w2, bench_wt_b, bench_wt_udev and the others unchanged by me.
- Work stopped 18:58 to 21:36 (usage limit); the full run had been started before and finished alone.
- Serial tool: run three times. Run 1 and 2 used a single 40% border-column rule that I had loosened for one large-print crop after the calibration; it widened the band on 7 crops. Run 3 keeps the calibrated 70% rule and falls back to 40% only when no strip is found. No verdict differs between the runs (4,278 pairs compared; O/serial_run1_padbug, serial_run2_bandbug, serial). Thresholds unchanged.
- Existing lists untouched (E: md5 of every file in benchmark/splits before and after, O/splits_md5_before.txt; SPLITS.md5 check OK): cv5v2.json, cv5v2_groups.tsv, dup_crossfold_v1.tsv, pool_t9.txt and the rest.
- Owed (lead): O/feats/feats_*_sealedid.npz hold SIFT descriptors of crops of sealed image ids (outside the project tree, as in stage A); delete them when this audit is closed. The data links data/labeled, data/unlabeled, data/escdd_masks in bench_wt_split are git-ignored symlinks as in bench_wt_b.

## 11. Outcome in short
1. Module identity: 700 image ids are 561 physical modules under rule B (527 under the pre-set rule, which over-links pool-only ids): ARTS 164 of 205, CSIR 239 of 300, CFVS 75 of 112; BMRK 65 and SDLE 18 not decidable.
2. cv5v2: 24 physical modules span two folds; 91 pool cells (ARTS 48, CFVS 32, CSIR 11) are held out while a cell of their module trains; 4 of them have the same cell in training, 38 a neighbouring crop. Same answer under both rules. 4 more pairs are open (8 cells).
3. E1: no link, no matching cell, nothing above 7 inliers; testable for a third of the id pairs.
4. Legacy test: 8 cells are a pool cell, 7 more are neighbouring crops; ARTS_00030 = ARTS_00017 is new.
5. Excluding the 91 cells lowers PF by 0.018 crack IoU and 0.018 relF1@2 and changes no contrast, no PASS* flag and no order of arms; M stays 0.010 (inactive 0.055 to 0.061).
6. Leakage is worth at most about 0.02 in the absolute crack numbers; not separable from "easier cells" without a retrain.
7. Proposals written, nothing applied: module_identity_v3.tsv, score_exclude_v2.txt (91 cells), cv5v3_proposal.tsv (31 cells move).
