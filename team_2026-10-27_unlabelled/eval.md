# eval.md: measurement side (evalx), 27 Oct 2026

Draft v4 (v4: literature effect sizes in §1.3; v2: robustness, component and cell-level metrics, scuff threshold; v3: judge r1 answered, half-cut cross-tab, E1 sealed outside CV). Scripts in `evalx_scripts/`, outputs beside them (`*_out.txt`). Tags: **E** measured here (file path given), **R** reasoned or literature, **S** speculation.
"clean" = the 50 test cells minus `CSIR_00070_r8_c4` (49 cells). Seeds: 5 v 5 unless stated. Rule 1 = P8 rule 1 (threshold max(0.01, 2*sqrt((sdA^2+sdB^2)/3))).
Inputs: per-cell counts in `results/e1/raw_v2/*.json` (test 50 + ext 106 per run; they reproduce the re-scores, A5c crack IoU 0.3037 = `la_sa_test.json`), Track M `m0/*.json` and `final/final_cells.json` (confusion, relaxed@2, components), GT masks from `~/mtp/datasets/escdd_full`.

## 0. Answer in five lines
1. **For the Cs recipe (S20, S50, Sx100), the SSL null at 20-100% labels is not a power failure for crack, in-distribution.** The best recipe, BsM, was never run at >= 50%, and BsM20 - A20 clean crack IoU +0.013 [-0.002, +0.033] does not exclude +0.01 to +0.03. On clean cells, 95% intervals with seed and cell noise combined: Sx100 - A100 crack IoU -0.002 [-0.007, +0.003]; S50 - A50 +0.002 [-0.009, +0.013]; S20 - A20 +0.002 [-0.011, +0.016]. A +0.01 gain is excluded at 100%; +0.02 is excluded at all three. P16's "+0.028" was the noisy cell; the seed median on all 50 cells gives -0.002 too (E).
2. **Inactive is underpowered.** 80%-power MDE for inactive IoU is 0.032 (100%) to 0.084 (5%) on seeds alone, 0.037-0.13 with cell sampling. A real +0.01 to +0.03 inactive gain would be invisible (E).
3. **Strict crack IoU is mostly a width/offset score at 100% labels.** 70% of the FINAL model's crack IoU loss is pixels within 2 px of the right place. A perfect localiser offset by 1 px scores IoU 0.50-0.55; the same cell labelled twice in our data scores IoU 0.53 against itself on E-SCDD masks, 0.21 on the old masks (E).
4. **The E1 "unseen module" gap is mostly one cell type and defect type together.** 20 E1 crack cells are half-cut multi cells (none in our train or test) that also hold scuff (class 25, not in our taxonomy, ignored in scoring). They carry 75% of E1 crack px, and FINAL recall there is 0.126. The other 12 E1 crack cells have recall 0.29-0.55. The crack labels sit near the scuff (median 12 px away) but do not trace its edge (14% within 3 px) (E).
5. **Recommendation:** keep the 50-cell test; report E1 as two readouts (scuff + half-cut, other) and keep it sealed; change the crack primary for future protocols to component recall at a val-chosen fixed precision, IoU beside it; run a module-grouped CV over the 693 non-E1 labelled cells only if inactive at >= 50% labels is the question (about 100 GPU-h per SSL contrast) (R, from 1-4).

## 1. Power, and where the variance is (Q1)
Script `evalx_scripts/power.py`, output `power_out.txt`.

### 1.1 Seed vs cell variance (E)
For one run's absolute score, cell sampling dominates: seed share of variance is 0.01-0.21 on clean cells for every arm and metric (A100 crack IoU: seed sd 0.0025, cell-bootstrap sd 0.031).
For a paired contrast the cell part mostly cancels; seed and cell are then comparable:

| contrast (clean) | metric | delta | seed SE | cell sd of delta | seed share |
|---|---|---|---|---|---|
| Sx100 - A100 | crack IoU | -0.0021 | 0.0020 | 0.0018 | 0.56 |
| Sx100 - A100 | inactive IoU | +0.0020 | 0.0095 | 0.0094 | 0.50 |
| BsM5 - A5c | crack IoU | +0.0289 | 0.0061 | 0.0072 | 0.42 |
| BsM5 - A5c | inactive IoU | +0.109 | 0.018 | 0.043 | 0.15 |

The noisy cell turns crack into a seed problem: on all 50, A100 crack IoU seed sd is 0.078 (one seed fails), on clean 0.0025. Seed share of a single run's crack IoU variance: 0.86 with the cell, 0.01 without.

### 1.2 Minimum detectable effects, 50 cells, 5 v 5 seeds (E)
thr = rule-1 threshold (a true effect this size passes about half the time). rule1_80 = true effect rule 1 detects 80% of the time (seed noise only). gen_80 = two-sided 5%, 80% power, seed + cell variance (what generalises to other test-like cells).

| labels | metric | thr all / clean | rule1_80 clean | gen_80 clean |
|---|---|---|---|---|
| 100% | crack IoU | 0.091 / 0.010 | 0.012 | 0.007 (below rule1_80 only because rule 1 has a 0.01 floor; adding cell variance never shrinks a true MDE) |
| 100% | relF1@2 | 0.122 / 0.010 | 0.013 | 0.011 |
| 100% | crack recall | 0.014 / 0.014 | 0.018 | 0.018 |
| 100% | inactive IoU | 0.025 / 0.025 | 0.032 | 0.037 |
| 50% | crack IoU / relF1 / rec / inact | clean 0.010 / 0.010 / 0.017 / 0.035 | 0.013 / 0.013 / 0.023 / 0.046 | 0.015 / 0.018 / 0.024 / 0.049 |
| 20% | crack IoU / relF1 / rec / inact | clean 0.012 / 0.012 / 0.023 / 0.050 | 0.016 / 0.016 / 0.031 / 0.066 | 0.025 / 0.034 / 0.043 / 0.101 |
| 5% | crack IoU / relF1 / rec / inact | clean 0.014 / 0.022 / 0.027 / 0.063 | 0.019 / 0.029 / 0.035 / 0.084 | 0.025 / 0.038 / 0.038 / 0.133 |

### 1.3 Could a real +0.01 to +0.03 gain have been invisible? (E)
- **Crack, 20-100% labels: not at +0.02 or more; +0.01 only ruled out at 100%.** Clean-cell cell-bootstrap 95% CIs (2,000 paired resamples, seeds fixed):
  - Sx100 - A100: crack IoU -0.0021 [-0.0054, +0.0016]; relF1@2 -0.0023 [-0.0077, +0.0024]; crack recall **-0.0109 [-0.0166, -0.0037]** (Sx100 slightly lower, n.d. on seeds, thr 0.0137).
  - S50 - A50: crack IoU +0.0021 [-0.0055, +0.0085]; relF1@2 -0.0011 [-0.0136, +0.0078].
  - S20 - A20: crack IoU +0.0024 [-0.0081, +0.0143].
  - P16's Sx100 "+0.028 crack IoU, n.d." is A100 s3 failing on the noisy cell (75,217 FP px, `results/p16/README.md`). Without the cell it is -0.002. The n.d. came from a threshold of 0.091 on all 50; on clean cells the threshold is 0.010 and the estimate is still about 0.
  - **Robustness (E, `robust_null.py`, `robust_null_out.txt`):**
    - all 50 cells, seed **median** instead of mean (no cell dropped): Sx100 - A100 crack IoU -0.002, S50 - A50 +0.006, S20 - A20 +0.001;
    - seed + cell noise in one 95% interval, clean: Sx100 [-0.007, +0.003], S50 [-0.009, +0.013], S20 [-0.011, +0.016];
    - clean and without the 7 twins (42 cells): Sx100 [-0.011, +0.007], S50 [-0.014, +0.018], S20 [-0.017, +0.027].
  - **So:** +0.01 is excluded at 100% only; +0.02 is excluded at 100% and 50% in every cell set and at 20% with twins; without twins, 20% labels cannot exclude +0.02 to +0.027. These bounds are for test-like cells (hand-picked, crack-heavy); on E1 unseen modules Sx100 - A100 is -0.006 [-0.016, +0.011] (module CI), which does not exclude +0.01.
- **Inactive at 20-100%: yes, possibly.** S20 - A20 inactive +0.029 [-0.024, +0.068]; Sx100 - A100 +0.002 [-0.015, +0.020]; S50 - A50 +0.002 [-0.025, +0.017]. Gains of +0.02 to +0.03 fit inside every CI.
- **5% (BsM5): the gain is real and was seen.** BsM5 - A5c crack IoU +0.029 [+0.013, +0.041], relF1@2 +0.044, recall +0.040, inactive +0.109 [+0.029, +0.193], all BETTER under rule 1. Track D: about a fifth of the crack part sits in the inactive-edge band (`team_2026-10-24_go/trackD/verify_edge.md`).
- **Label-fraction yardstick (E):** A50 -> A100 (239 more labelled cells) is crack IoU +0.026, recall +0.063 on clean cells. So at 50% an unlabelled pool would need to deliver about 10% of what doubling the labels does to pass rule 1 on crack IoU.
- **Literature effect sizes (R, from `lit`, read in full text; lit.md §5):**
  - UniMatch V2 (doi:10.1109/tpami.2025.3528453, Table 5, same DINOv2-B encoder): Pascal 92 labels +9.4 mIoU; Pascal full 1,464 labels +2.5; ADE20K 1/4 +3.0. Realistic all-labels-plus-new-pool setting (§4.5): Cityscapes +0.3, ADE20K +0.8 to +1.6. Runs and sd not stated.
  - AEL (arxiv:2110.05474, Table 4, Cityscapes 1/32): Mean Teacher +6.2 mIoU; thin class "pole" +5.7; fence -2.4.
  - Oliver et al. (arxiv:1804.09170, Table 2): against a tuned baseline, Mean Teacher's gain shrinks from 8.4 to 4.4 error points.
  - No crack, EL or thin-defect paper reports a per-class SSL gain over a tuned supervised baseline with seed sd.
  - **Comparison (R):** the realistic all-label effect is 0.003-0.016 in IoU units. That is at or below our 100% clean crack MDE (rule1_80 0.012). Our Sx100 interval [-0.007, +0.003] excludes the top of that range (+0.016) but not the bottom (+0.003). So a literature-sized full-label gain could only just show here, at best. Literature gains also come from pools of the same distribution; ours is two sources only. The large low-label gains (+6 to +9 mIoU) match what we did see at 5% (BsM5 +0.029 crack, +0.109 inactive).

### 1.4 Would a bigger test set help? (E, extrapolated; S beyond 49 cells)
Subsampling the 49 clean cells (n = 15, 25, 35, 49; 300 draws) and fitting var = a + b/n:
- **Crack at 100%:** seed sd of a single run's crack IoU falls 0.0057 (15 cells) -> 0.0031 (49); extrapolated 0.0013 at 250 cells. Cell sd of the contrast 0.0018 -> about 0.0007. But rule 1 already sits on its 0.01 floor. **A bigger in-distribution test does not change the crack verdict; the floor does.**
- **Crack at 5%:** seed sd stays about 0.009 (the seed effect is global, not per cell); gen_80 0.025 -> 0.018 at 250 cells. Modest gain.
- **Inactive:** cell sd of BsM5 - A5c falls 0.042 (49) -> about 0.020 (250, extrapolated); gen_80 0.125 -> about 0.056. **Inactive is the metric a bigger test would actually fix,** but only if the new cells contain inactive (E-SCDD adds 20 inactive cells, see §4).

## 2. Label-noise and convention ceiling for crack (Q2)
Script `evalx_scripts/labelnoise.py`, output `labelnoise_out.txt`.

### 2.1 Where the crack IoU loss goes (E, clean cells)
Union split into: FN near (GT px within 2 px of a prediction, missed), FN far (GT px > 2 px from any prediction: missed crack), FP near (predicted px within 2 px of GT: width/offset), FP far (spurious).

| model | IoU | FN near | FN far | FP near | FP far | IoU, near errors forgiven |
|---|---|---|---|---|---|---|
| FINAL ensemble, bias +0.75 | 0.492 | 0.114 | 0.094 | 0.244 | 0.056 | 0.802 |
| FINAL, bias 0 | 0.488 | 0.140 | 0.123 | 0.214 | 0.035 | 0.799 |
| A100 single (5 seeds) | 0.474 | 0.139 | 0.126 | 0.216 | 0.046 | 0.782 |
| Sx100 (5) | 0.472 | 0.145 | 0.131 | 0.209 | 0.043 | 0.779 |
| A50 (5) | 0.448 | 0.177 | 0.149 | 0.182 | 0.044 | 0.763 |
| L3 10% (3) | 0.399 | 0.181 | 0.201 | 0.165 | 0.055 | 0.694 |
| BsM5 (5) | 0.335 | 0.203 | 0.270 | 0.143 | 0.049 | 0.628 |
| A5c (5) | 0.306 | 0.191 | 0.320 | 0.130 | 0.052 | 0.572 |

- At 100% labels, **0.358 of the 0.508 IoU gap (70%) is near errors**; missed cracks are 0.094 (18%), spurious 0.056 (11%).
- At 5% labels the picture flips: missed cracks are 0.32 of the union, the largest share. **The BsM5 gain over A5c is mostly FN far (0.320 -> 0.270): SSL found more cracks at 5%.** At 100% the FN-far share left to win is 0.09-0.13.
- Headroom if every missed crack were found at the current width accuracy: about +0.09 IoU (FINAL); if every width/offset error were fixed: about +0.31.

### 2.2 A perfect localiser with another convention (E, GT-only simulation, 50 test masks)
Test GT: 91,838 crack px, skeleton 31,232 px, mean width 2.94 px; local width at the skeleton is 1 px for 39%, 2 px 27%, 3 px 33%.

| perfect localiser drawn as | crack IoU | relF1@2 |
|---|---|---|
| GT shifted 1 px (x) | 0.547 | 1.000 |
| GT shifted 1 px (x and y) | 0.498 | 0.999 |
| GT shifted 2 px | 0.283 | 1.000 |
| GT dilated 1 px (cross / 3x3) | 0.603 / 0.525 | 1.000 |
| GT eroded 1 px | 0.481 | 1.000 |
| 1 px centreline | 0.340 | 0.993 |
| 3 px line on the centreline | 0.745 | 0.999 |
| 5 px line on the centreline | 0.595 | 1.000 |

- **A model that finds every crack perfectly but disagrees with the annotator by 1 px in offset or width scores crack IoU 0.48-0.60.** FINAL's 0.492 is inside that band. relF1@2 is 0.99-1.00 for all of them: it is blind to the convention, as intended.
- **Annotator self-agreement (E, n = 1):** the one cell that appears twice in our data (`ARTS_00081_r5_c1` train = `ARTS_00020_r5_c1` test, doc 03) has E-SCDD crack masks that agree at IoU 0.534, relF1@2 0.997 (113 vs 183 px). On the old 20211104 masks the same pair gives IoU 0.210 (37 vs 107 px; `judge_r1_out.txt`), matching doc 03's 0.21. Handbook 13 A5's 0.257 cites a situation report I did not recompute. The revision raised agreement but it is still about 0.5.
- R: so strict IoU near 0.5 is close to the label-agreement ceiling for 1-3 px structures. Differences of 0.01 in IoU at 100% labels can come from a width shift alone (Track M's bias +0.75 gave +0.018 IoU with precision -0.041 on clean cells, `trackM/results_final.md`).

## 3. Is the metric the goal? (Q3)
The user's goal: catch almost all cracks and inactive, keep mIoU balanced.

| metric | measures | convention-sensitive | usable on test? | current value, FINAL clean |
|---|---|---|---|---|
| pooled crack IoU | pixel agreement incl. width | yes (§2.2) | yes | 0.492 |
| relR@2 / relP@2, relF1@2 | crack found within 2 px, pixel-weighted | no | yes | 0.866 / 0.930, 0.897 |
| crack component recall (>=20 px, >=50% within 2 px) / precision | cracks found, each counted once | no | yes (187 GT comps >= 20 px, clean) | 0.834 / 0.933 |
| crack cell-level detection | any crack in cell | no | **no**: 48 of 50 test cells have crack | - |
| inactive pooled IoU | area agreement | weakly | 3 cells hold 59% of px | 0.456 |
| inactive region recall (>=100 px, >=50% covered) | regions found | no | yes, few regions | 0.800 |
| per source | where it fails | - | BMRK 10, SDLE 1 cell | BMRK relR@2 0.812 |

(Values: `trackM/results_final.md`, recomputed in `labelnoise_out.txt` and `e1_split_out.txt` section A.)

- R: for "catch almost all cracks", the matching measure is **component recall at a fixed component precision**, plus relR@2 at relP@2 >= 0.90 (Track M already used this target). **The operating point must be fixed on val before test** (`judge` r1.4): choose the crack logit bias as the smallest value whose val component precision is >= 0.90 (val: 23 crack cells, 125 GT components >= 20 px, so that precision has SE about 0.03), freeze it in the protocol, then score test once. Report the full test component recall-precision curve as secondary, never to pick the point. Pixel-weighted metrics let a few long cracks dominate; components count each crack once.
- **Strict IoU is misleading as a goal measure** (§2) **but not misleading about the SSL verdict:** relF1@2 and recall show the same null at 20-100% on clean cells (§1.3). Changing the metric would not have turned P16 into a win.
- **The goal metrics on Sx100 - A100 (E, `comp_contrast.py`, `comp_contrast_out.txt`, clean test, 5 v 5):** crack component recall 0.798 -> 0.800, +0.002 (thr 0.020), cell CI [-0.014, +0.020]; component precision +0.001 [-0.022, +0.022]; inactive region recall 0.773 -> 0.773, 0.000 (thr 0.030) [-0.024, +0.021]. On E1 ext: component recall -0.010 [-0.025, +0.009]. **No hidden gain.** Note the cost: component metrics count 187 cracks and 45 inactive regions, so their thresholds (0.020, 0.030) are 2-3x the pixel-IoU floor. They are the right goal measure but need a bigger test to be powerful.
- Sensitivity (E, delta / sqrt(seedSE^2 + cellSD^2), clean): A50 -> A100: IoU 2.6, relF1 1.5, recall 4.5. BsM5 - A5c: IoU 3.1, relF1 3.2, recall 2.9. A5c -> L3 10%: IoU 3.3, relF1 5.9, recall 4.3. No metric is uniformly more sensitive; recall is the most sensitive to label count at high fractions.
- Cell-level crack detection only works on a set with crack-free cells (E1 ext has 74; test has 2). Pratt 2023 hand-picked test for crack prevalence (doc 03 §2.2).
- **Cell level tells a different story from pixels (E, `cell_detect.py`, `cell_detect_out.txt`).** Positive = GT crack >= 20 px; flagged = >= 50 px predicted crack (outside ignored px).
  - E1 ext crack: FINAL +0.75 flags 24 of 32 crack cells (0.75) with 16 of 74 false alarms (0.22); bias 0: 0.72 / 0.14; single A100 models 0.69-0.84 / 0.14-0.19.
  - Test inactive (>= 0.5% of cell, clean): 9-10 of 12 cells flagged, 0-1 false alarms in 34.
  - E1 ext inactive: only 1 cell reaches 0.5% area, so it cannot be scored this way.
  - Stricter hit, from `ideas` (TP-based, so the flag must touch the crack): SUP100 has >= 20 TP px in 82% of E1 half-cut crack cells while recovering 13% of their px.
  - **Is cell level what the user needs? (`ideas` Q2):** the data cannot say. The user's words are "catches almost all cracks and inactive". For screening (is this cell defective?) the cell flag is the unit; for repair, grading or crack-length estimates, components and pixels are. R: report both, and let the user pick the headline.
  - Caveat: a flag is "any crack predicted in the cell", not "the right crack"; with a 0.14-0.22 false-alarm base rate some hits are luck. Still, at cell level the model is far closer to the user's goal on unseen modules than pixel recall 0.21 suggests.

## 4. Changing the test set, honestly (Q4)

| option | cells | crack cells | inactive cells (top-3 px share) | leak risk for existing models | comparability |
|---|---|---|---|---|---|
| keep: our test | 50 | 48 | 16 (59%) | none | full |
| E-SCDD official test | 82 | see audit | 9 (81.5%) | **48 of 82 are in our train, 3 in our val**; 10 `_rf` in our pool (x-arms); 13 are E1 cells | none; only usable after a full retrain on E-SCDD's split, which itself has 39 of our test cells in its train |
| E1 ext, split by module | 106 (71 SRC_##### prefixes) | 32 in 21 modules; top-3 modules 50% of crack px | 10 in 7 modules (87%) | 1 module shared with our 582 (doc 03) | already scored for every arm since P6 |
| audit option A: test + E1 105 + 17 `_rf` not in pool | 172 | 86 | 26 (53.5%) | none for P-series; check R4's 107 extra train cells against the 17 | new numbers; old test reported beside |
| module-grouped 5-fold CV, E1 105 + 17 `_rf` kept sealed outside | 693 (582 + 100 `_rf` + 11 ext117, all 111 from our pool) | 329 (280 + 49) | 74 (64 + 10) | controlled by design (below) | new base; contrasts comparable in kind, not in level |

Counts: doc 17 §5.6-5.8 and `results/escdd_audit/README.md` §5, §8; E1 module counts `e1_split_out.txt`.

- **E-SCDD official test is out** for existing models (leak) and is worse for inactive than ours (9 cells, 81.5% in 3).
- **E1 is good for crack transfer, useless for inactive** (9,158 inactive px in total).
- **CV is the only option that fixes inactive power** (74 inactive cells vs 16, 4.6x). E1 (105) and the 17 `_rf` cells not in the pool stay sealed outside CV as the only unseen-module set (`judge` r1.3). Cost, using `judge`'s per-run figures (al1 launch.log): 5 folds x 5 seeds x 1.1 GPU-h = about 27 GPU-h per supervised arm, about 70 GPU-h per BsM arm (2.8 GPU-h/run). One SSL contrast is about 100 GPU-h. Expected inactive gen_80 (S, extrapolated from §1.4 with 1/sqrt(cells), seed part unchanged or averaged over 5 fold models): 100% labels 0.037 -> 0.017-0.029; 5% 0.133 -> about 0.06-0.07. Worth it only if the question is inactive at >= 50% labels. For crack in-distribution it buys nothing the clean test does not already give. Requirements, fixed before any run:
  1. folds grouped by module (`SRC_#####`); known twins in one fold (`ARTS_00020_r5_c1`/`ARTS_00081_r5_c1`, `CFVS_00015/16_r7_c4`, the 5-cell BMRK cluster);
  2. each fold's test cells removed from every unlabelled pool (100 `_rf` + 11 ext117 cells are in the external pool);
  3. fold assignment drawn once with a fixed seed and committed (hash the list) before any training;
  4. `_rf` crack labels are noisier (specks, 1-px ARTS lines; audit §6): pre-declare whether they are scored, and report with and without;
  5. image-only noise rule: cells with robust noise sigma > 10 are reported separately (flags `CSIR_00070_r8_c4`, `CSIR_00070_r7_c2`, `CSIR_00069_r7_c1` in our 582; `results/p16/cell_noise_rank.txt`). Decided from images, not from model outputs.
- **Pre-registration (R):** write the protocol (set, metrics, rule, cell exclusions, which models get scored) and commit it before any model is scored on the new set; score every existing arm once; report the old 50-cell numbers beside, never instead; any contrast that is significant only on the new set is labelled as such.
- **Is a bigger test needed to settle the unlabelled-data question?** For crack in-distribution at 20-100%: **no** for effects of +0.02 or more, which the clean-cell intervals already exclude (+0.01 too at 100%; §1.3). Resolving +0.01 at 20-50% would need about 2-4x the cells (S: from the 1/sqrt(n) scaling in §1.4). For inactive: **yes**. For transfer: E1 already exists and is where SSL shows (§5).

## 5. The unseen-module gap (Q5)
Scripts `e1_split.py`, `e1_scuff.py`, `e1_montage.py`; outputs `e1_split_out.txt`, `e1_scuff_out.txt`, `e1_lowrecall_modules.png`, `e1_highrecall_modules.png`.

- **Sizes (E):** 106 cells, 101 CSIR + 5 BMRK. Crack in 32 cells (31 CSIR, 1 BMRK with 55 px). Inactive in 10 cells, 9,158 px.
- **Concentration (E):** 21 modules have crack; the top 3 (`CSIR_01717`, `CSIR_01637`, `CSIR_01679`) hold 50% of crack px, top 5 69%. FINAL recall in those three: 0.15, 0.13, 0.07.
- **Label shape (E):** E1 crack is wider and more fragmented than test: 3.66 vs 2.94 px per skeleton px; median component 65 vs 180 px; 333 components in 32 cells vs 211 in 48.
- **Scuff (E):** 88% of E1 crack px (28,314) are in 22 cells with >= 500 px of class 25 scuff. Scuff is not in our 24 classes and is ignored in E1 scoring.

| E1 crack cells | cells / modules | crack px | FINAL recall | relR@2 | comp recall | IoU | A100 recall |
|---|---|---|---|---|---|---|---|
| with scuff | 22 / 12 | 28,314 (88%) | 0.181 | 0.308 | 0.180 (278 comps) | 0.161 | 0.149 |
| without scuff | 10 / 9 | 3,980 (12%) | 0.455 | 0.692 | 0.667 (18 comps) | 0.398 | 0.386 |
| test, clean (reference) | 47 / - | - | 0.703 | 0.866 | 0.834 | 0.492 | 0.642 |

- **Not a threshold artefact (E, `e1_scuff_thr.py`, `e1_scuff_thr_out.txt`):** scuff px in the 32 crack cells is either 0 (9 cells) or 256-5,369 (23 cells). Split at >= 1 px: FINAL recall 0.181 (23 cells) vs 0.489 (9 cells); at >= 2,000 px: 0.124 vs 0.316. The 500 px cut was mine, chosen before the recall split was computed; any cut gives the same picture.
- Caveat (E/R): E1 scoring drops predictions on ignored px (A100 predicts about 8,500 crack px on ignored area per run, `e1_scuff_out.txt`). A model that paints the whole scuff streak as crack gets no relaxed credit for branch cracks along its edge. This can depress relR@2 in scuff cells; it cannot explain the strict-recall gap, which only counts GT crack px.
- Visual check (`e1_lowrecall_modules.png`): the scuff modules show a broad dark streak across the cell; the crack labels are short branches off the streak, not the streak itself. Measured (`judge_r1.py`): in the 20 scuff + half-cut cells, GT crack px within 1 / 3 / 10 / 20 px of scuff: 0.05 / 0.14 / 0.45 / 0.67, median 12 px. So the labels are cracks branching from the scuff, not its outline. The high-recall modules (`e1_highrecall_modules.png`) show ordinary thin and dendritic cracks.
- **Cross-tab with half-cut cells (E, `judge_r1_out.txt`; `ideas` found the half-cut link, `judge` j6 agrees). E1 crack cells >= 20 px, FINAL +0.75:**

| E1 group | cells | crack px | within 3 px of scuff | width px | ring - crack grey | FINAL recall |
|---|---|---|---|---|---|---|
| scuff + half-cut | 20 | 24,246 (75%) | 0.144 | 3.65 | 11.2 | 0.126 |
| half-cut, no scuff | 6 | 2,491 | 0 | 3.49 | 8.4 | 0.552 |
| scuff, not half-cut | 2 | 4,068 | 0 (median 284 px away) | 3.86 | 4.7 | 0.514 |
| neither | 4 | 1,489 | 0 | 3.59 | 7.4 | 0.291 |
| our test (ref.) | 46 | 91,838 | no scuff | 2.94 | 15.0 | 0.703 (clean) |
| our train CSIR (ref.) | 47 | 54,355 | 3 cells with any scuff | 2.67 | 10.2 | - |

- R: the failure is the conjunction, scuff-associated branch cracks on half-cut multi cells. Half-cut alone (0.55) and scuff alone (0.51) are near the in-distribution level. Every E1 group's labels are 0.8-1.2 px wider than train CSIR, so a width convention gap applies to all of E1. It costs IoU but cannot explain recall of 0.13: relR@2 in scuff cells is 0.31, so most GT px are > 2 px from any prediction.
- E1 cracks are fainter than test cracks (ring - crack 7-11 vs 15 grey levels), at the level of train CSIR (10.2). Test was hand-picked for visible cracks (doc 03 §2.2).
- R: so most of "E1 recall 0.21 vs test 0.70" is a cell type plus defect type we never trained on, not a generic module shift. On other unseen-module cracks the gap is smaller (0.29-0.55 vs 0.70) but rests on 12 cells.
- **Power on E1 (E):** module-cluster bootstrap sd of a crack IoU contrast is 0.004-0.009, close to the cell-level sd. Crack MDE about 0.02; inactive sd 0.05-0.09 (useless).
- **Where SSL showed up (E, secondary, 7 contrasts x 3 metrics looked at, no correction):** S50 - A50 crack IoU +0.019, module CI [+0.004, +0.031]; BsM20 - A20 +0.029 [+0.014, +0.043]; BsM5 - A5c +0.009 [-0.001, +0.016]; **Sx100 - A100 -0.006 [-0.016, +0.011]**. The S50 and BsM20 gains are in the scuff cells (S50 recall 0.080 -> 0.110; BsM20 0.058 -> 0.094); on scuff-free cells S50 - A50 recall is -0.012.
- **Is E1 a good primary target?** For crack transfer, yes as two pre-registered readouts: scuff + half-cut (20 crack cells, 75% of px) and other (12 crack cells, descriptive only), with module-cluster CIs. For inactive, no. Its crack labels are not "clean" in the test-set sense (wider by about 1 px, fainter, tied to an untrained class and cell type). Keep it sealed: no training, tuning or selection on it.

## 6. Recommendation (R)
1. **Keep the 50-cell test** as the continuity set; make the clean (no-noisy-cell) set co-primary by an image-only rule written now (§4 item 5).
2. **Do not change the test set to rescue the SSL question for crack:** at 20-100% the crack null is already tight on clean cells (gains of +0.02 or more excluded).
3. **Change the primary crack metric for future protocols** to component recall at component precision >= 0.90 plus relR@2 at relP@2 >= 0.90; keep pooled IoU and mIoU_rob as balance checks. Existing verdicts stay under their locked metrics.
4. **Add, pre-registered:** (a) E1 as two readouts (scuff + half-cut, other) with module-cluster CIs, sealed; (b) if the question is inactive at >= 50% labels, a module-grouped 5-fold CV over the 693 non-E1 labelled cells (about 27 GPU-h per supervised arm, 70 per BsM arm).
5. Old and new numbers side by side, always.

## Response to judge r1
1. **Scope (accepted).** §0.1 now reads "for the Cs recipe". BsM was never run at >= 50%. BsM20 - A20 clean crack IoU +0.0126 [-0.002, +0.033] (`power_out.txt`) does not exclude +0.01 to +0.03, so for BsM the 20% question is open.
2. **Scuff-edge convention? Partly, not mainly (E, `judge_r1.py`, `judge_r1_out.txt`).**
   - In the 20 scuff + half-cut cells, 14.4% of GT crack px are within 3 px of scuff px (45% within 10 px, median 12 px).
   - In the 6 half-cut cells without scuff: 0% (no scuff).
   - The labels are branch cracks running off the scuff, not its outline. R: this is a defect type (scuff-linked branch cracks on half-cut multi cells) plus a +1 px width convention on all of E1. It is not mostly a boundary convention.
   - Could unlabelled images fix it? The external pool has 1,152 multi half-cells (doc 03 §6), yet Sx100 - A100 on E1 is -0.006 [-0.016, +0.011]. R: an unlabelled pool that contains the cell type did not help under the Cs recipe; the missing piece looks like labels for that defect type.
3. **CV and E1 (accepted).** E1 (105) and the 17 non-pool `_rf` cells stay sealed outside CV. CV covers 693 cells (329 crack, 74 inactive). GPU-h is added to §4: about 27 per supervised arm, 70 per BsM arm, about 100 per SSL contrast. Worth it only for inactive at >= 50% labels.
4. **Operating point.** Fixed on val before test: the smallest crack bias with val component precision >= 0.90 (125 val GT components, SE about 0.03). Frozen in the protocol; the test curve is secondary only (§3).
5. **0.534 vs 0.257.** Same pair: old masks 0.210 (37 vs 107 px; doc 03 says 0.21), E-SCDD masks 0.534. Handbook 13's 0.257 cites a situation report I did not recompute. Either way, agreement is about 0.2-0.5.
6. **gen_80 below rule1_80.** That comes from rule 1's 0.01 floor, not from cell variance; noted in §1.2.

## Open items
- Literature numbers received from `lit` and added in §1.3.
- Sensitivity of component recall per contrast at 5% needs component counts for P-series arms (only Track M runs have them).
