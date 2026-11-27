# B1 classbias_xfit: cross-fitted per-class logit biases, operating point OP-C (stage B1, 15 Nov 2026)

Spec: cards/T10_rare_classes_spec.md "Arm 2. classbias_xfit". Critic: WAVE3_REVIEW Y6 (OP-C), verdict line "classbias_xfit: GO; becomes OP-C; report the fold-to-fold spread of each bias; confirm on W1-C1", Y8, G18, G19, Y1. Lead: L3 (decision layers are a labelled entry class; OP-C is the comparator for prior-shifting arms), L4 (inactive policy).
Tags: E = measured, S = judgement. No sealed cell is read anywhere in this item.

## 1. Reading rule (written 15 Nov 14:20 IST, before any fit or number of this item)

**What OP-C is.** For one arm and one seed: the argmax of the 24 log-probabilities (`logp`, float16 in the dump) plus a bias vector b (24 values). b[0] = 0 (reference), b[14] = 0 (crack keeps OP-A / OP-F / OP-W), b = 0 for every class outside R13; the 11 classes FREE = {1, 2, 4, 5, 7, 11, 13, 15, 16, 20, 21} get a fitted bias. For held-out fold k, b_k is fitted on the out-of-fold cells of the other 4 folds of the same seed and applied to fold k (cross-fitted; the fit never reads a fold-k cell, asserted).

**Fit (as the spec).** Coordinate ascent, 3 sweeps, classes in the order 16, 20, 11, 13, 15, 21, 5, 4, 2, 1, 7; each b[c] chosen from the grid -1.5 to 4.0 step 0.25 (23 values) to maximise the pooled mIoU over R13 without crack (12 classes, pooled confusion over the fit cells, ignore px not counted); ties: the value closest to 0, then the lower value.

**Two deviations from the spec text, fixed now.**
1. The baseline of the contrast is S1 = argmax of the dump's float16 `logp` (b = 0), not the dump's fp32 `pred`. The spec's test "b = 0 reproduces pred exactly" cannot hold through float16 (stage A5 found 1,698 of 278.9 M px differ); with S1 the contrast contains only the bias. The S1 - dump-pred difference (px and the four headline metrics) is printed.
2. Contested-px cache: the spec's rule ("a FREE class within 4 nats of the top, or the top in FREE") is replaced by the exact invariance rule: a px is cached if its argmax can change for some b in the grid box (runner-up with +4.0 on FREE classes reaches the top with -1.5 if the top is FREE, 0 otherwise). Every other px keeps its S1 class for every b. Unit-tested against a full recompute.

**Primary and pass (spec, unchanged).** Primary: mIoU-R13 at OP-C minus OP-A (S1), same dumps, pooled out-of-fold over the 532 pool cells, mean over seeds. Pass on one machine needs all of:
- delta mIoU-R13 >= 0.010 and its 95% interval low > 0;
- crack strict IoU delta >= -0.005 and crack relF1@2 delta >= -0.005 (point, crack at argmax on both sides);
- inactive IoU delta >= -0.010 (point);
- no R13 class with IoU delta < -0.030 (point, mean over seeds).
Interval: two-stage group bootstrap (330 groups of cv5v2_groups.tsv, then one seed per fold, the same seed for both readouts because they are two readouts of the same runs: `boot_pair(..., paired_seeds=True)`, as src_calib), 2,000 draws, seed 0. M for mIoU-R13 is 0.010 on both machines (A1), equal to the spec's floor.

**Explore and confirm (Y8, G19).** Exploration = gaint PF v1.1 (W1-G + W1-G2, seeds 5 to 8). Confirmation = the same script, unchanged, on cv02 PF v1.1 (W1-C1, seeds 5 to 9). **classbias_xfit PASSES only if both machines pass.** One variant is read (the spec's), so Holm changes nothing; the count goes into the ledger. If it fails: la_ce stays closed (spec drop rule).

**OP-C exists whatever the outcome.** The pass rule decides whether the bias is credited as a decision-layer entry with a gain and whether la_ce opens. OP-C dumps of the baseline are written in either case (L3, Y6): a prior-shifting arm (rcs, la_ce, inact_paste, ucf_partial_joint, layered_ci) counts an inactive or mIoU-R13 gain only if it is present at OP-A and against the baseline at OP-C.

**Guards (printed; decide nothing beyond the pass rule).**
- Per-class IoU, precision, recall for the 13 classes at S1 and OP-C with the paired bootstrap interval of each IoU delta; per source (ARTS, BMRK, CFVS, CSIR; SDLE has 18 cells and is printed with its n).
- Fold-to-fold spread of each b_c: mean, min, max over (seed, fold); a class whose fitted b takes both signs (ignoring zeros) is marked UNSTABLE.
- G18 columns for every FREE class: predicted px on cells without that class in GT, and predicted / GT px ratio, at S1 and OP-C. They describe the prior shift that OP-C makes; they are pass conditions for arms read against OP-C, not for this device.
- Crack guards at argmax: relP@2, relR@2, width ratio.
- Inactive (Y1, L4): inactive IoU enters only as the guard above. Count-based readouts printed for S1 and OP-C: inactive region recall (GT regions >= 100 px, >= 50% covered), predicted inactive px on inactive-free cells, inactive precision and recall, predicted / GT inactive px, and the direction of the inactive IoU delta. They promote nothing here; they are what an inactive arm must beat at OP-C.

**HOUSE row (descriptive).** HOUSE (cv02, seeds 5 and 6) dumps carry no `logp`; OP-C for HOUSE is computed on CPU fp32 re-dumps with `logp` from the relayed slim checkpoints (S1 and OP-C both from those re-dumps; agreement of the re-dump's argmax with the original cv02 dump is printed). HOUSE does not enter the pass decision.

## 2. Numbers (E unless marked S)

Tools: bench_b **43ebf79** (bench/classbias.py cd9904d3, scripts/bench_classbias.py bceb35ed, scripts/bench_classbias_read.py cd66b301), run 15 Nov 14:22 to 15:16 by bench_reads/stageB/B1/run_b1.sh in tmux bench_b_B1 (CPU, nice 19, 8 workers, OMP 1). Inputs: gaint W1-G + W1-G2 PF dumps (20 runs, cuda fp32, logp); cv02 W1-C1 PF dumps via the symlink view (25 runs); cv02 HOUSE re-dumped on gaint CPU fp32 with logp (10 runs, below). Input manifest md5s are printed in logs/fit_*.log and fit_*/fit.json. 532 out-of-fold cells, label set v1.1, 330 groups, 2,000 draws.
Outputs: /home/noob/work/bench_reads/stageB/B1/{fit_gaint_pf, fit_cv02_pf, fit_cv02_house}/{classbias_b.tsv, fit.json, fit.txt} (classbias_b.tsv d6a2bf00 / 2b9f5691 / e792f404) and {read_gaint_pf, read_cv02_pf, read_cv02_house}/read.{txt,json} (read.txt 8a7035df / 20a410d7 / 4d7b38fe). OP-C and S1 dumps: /home/noob/work/bench_udev/opc/dumps_gaint/elbench1/pf_v11_{opc,s1}, dumps_cv02/elbench1/{pf_v11,house_v11}_{opc,s1} (no logp; the OP-C manifests carry `classbias_b` and `fit_folds`).

### 2a. Checks
- Contested-px cache share: 0.14 to 0.16 of scored px (PF), 0.16 to 0.19 (HOUSE). Fit time about 100 s per (seed, fold).
- S1 against the dump's fp32 pred: 3,346 px of 1.12 G differ on gaint (22 crack px), 4,216 on cv02 (27); headline metrics of S1 and ORIG equal to 4 dp except mIoU-R13 on gaint (0.6129 v 0.6130).
- HOUSE CPU re-dump against the original cv02 GPU dump: 5 of 278.9 M px differ (1 crack px of 685,381). Shim: config_used.yaml with only data.root changed (2 diff lines), latest.pth = symlink to the relay's slim.pth (md5 = relay RUN.md5, all 10).
- Cross-fit: every OP-C manifest names its fit folds (never its own fold; asserted again by the read). In-sample objective on the fit cells rose from 0.633 to 0.649 (gaint mean over fits), the held-out gain below is +0.0137: a small optimism, as expected (S).

### 2b. Primary and pass rule (OP-C minus S1, paired)
| Machine | Seeds | mIoU-R13 S1 -> OP-C | delta [95% CI] | crack IoU delta | crack relF1@2 delta | inactive IoU delta | worst class delta | Rule |
|---|---|---|---|---|---|---|---|---|
| gaint PF (explore) | 5-8 | 0.6129 -> 0.6266 | **+0.0137 [+0.0107, +0.0169]** | -0.0011 [-0.0035, +0.0016] | -0.0006 [-0.0033, +0.0026] | +0.0104 [+0.0010, +0.0189] | background -0.0032 | **PASS** |
| cv02 PF (confirm) | 5-9 | 0.6122 -> 0.6248 | **+0.0126 [+0.0077, +0.0167]** | -0.0008 [-0.0034, +0.0023] | -0.0001 [-0.0032, +0.0036] | +0.0101 [+0.0009, +0.0195] | background -0.0033 | **PASS** |
| cv02 HOUSE (descriptive, CPU re-dumps) | 5, 6 | 0.6093 -> 0.6183 | +0.0091 [+0.0067, +0.0115] | -0.0021 [-0.0046, +0.0008] | -0.0017 [-0.0045, +0.0012] | +0.0026 [-0.0070, +0.0129] | border -0.0030 | (would fail: delta < 0.010) |

### 2c. Per class (mIoU-R13 classes; IoU S1 -> OP-C, delta [95% CI]; gaint / cv02)
| Class | gaint | cv02 |
|---|---|---|
| gridline (15) | 0.302 -> 0.362, +0.060 [+0.047, +0.073] | 0.304 -> 0.361, +0.058 [+0.044, +0.071] |
| splice (16) | 0.021 -> 0.113, +0.092 [+0.060, +0.124] | 0.013 -> 0.088, +0.075 [+0.015, +0.119] |
| inactive (11) | 0.503 -> 0.513, +0.010 [+0.001, +0.019] | 0.503 -> 0.513, +0.010 [+0.001, +0.020] |
| material (13) | 0.394 -> 0.404, +0.010 [-0.009, +0.025] | 0.399 -> 0.412, +0.012 [+0.001, +0.025] |
| ribbons (4) | +0.007 [+0.003, +0.011] | +0.008 [+0.003, +0.012] |
| edge_dark (20) | +0.004 [-0.002, +0.010] | +0.003 [-0.003, +0.009] |
| background (0) | -0.0032 [-0.0039, -0.0025] | -0.0033 [-0.0045, -0.0025] |
| crack (14, not biased) | -0.0011 | -0.0008 |
| sp_multi, sp_mono, border, padding, frame_edge | within +-0.0014 | within +-0.0012 |
Gridline gains recall (0.37 -> 0.58) at precision 0.63 -> 0.49; splice recall 0.02 -> 0.21 at precision 0.34 -> 0.20 (gaint). HOUSE: gridline +0.069, splice 0.000 -> 0.049, inactive +0.003, material +0.001.
Per source (mIoU-R13 delta, gaint / cv02): ARTS +0.015 / +0.015, BMRK +0.011 / +0.011, CFVS +0.006 / +0.006, CSIR +0.007 / +0.009 (all intervals above 0); splice appears only in ARTS.

### 2d. Fitted biases: fold-to-fold spread (mean, min, max over seed x fold)
| Class | gaint (20 fits) | cv02 (25) | HOUSE (10) |
|---|---|---|---|
| inactive 11 | +4.00, +4.00, +4.00 | +4.00, +4.00, +4.00 | +3.38, +0.50, +4.00 |
| splice 16 | +1.84, +1.75, +2.00 | +1.90, +1.25, +3.00 | +2.98, +2.50, +3.25 |
| material 13 | +1.35, +0.75, +1.75 | +1.43, +1.00, +1.75 | +0.50, +0.25, +0.75 |
| gridline 15 | +1.00, +1.00, +1.00 | +0.98, +0.75, +1.00 | +1.00, +1.00, +1.00 |
| edge_dark 20 | +0.55, +0.50, +0.75 | +0.54, +0.25, +0.75 | +0.23, 0, +0.50 |
| ribbons 4 | +0.45, +0.25, +0.50 | +0.44, +0.25, +0.50 | +0.30, +0.25, +0.50 |
| sp_multi 1, sp_mono 2 | +0.23 / +0.25 | +0.24 / +0.26 | +0.25 / +0.23 |
| border 5 | -0.08, -0.50, +0.25 **UNSTABLE** | -0.22, -0.75, +0.25 **UNSTABLE** | -0.28, -0.75, 0 |
| padding 7 | +0.20, -0.75, +1.00 **UNSTABLE** | -0.08, -1.00, +1.00 **UNSTABLE** | -0.15, -0.50, 0 |
| frame_edge 21 | +0.03, -0.50, +0.75 **UNSTABLE** | -0.21, -1.50, +0.50 **UNSTABLE** | -0.25, -0.50, 0 |
- The inactive bias sits at the grid edge (+4.0) in all 45 PF fits: the optimum may lie above the grid. Even at +4 nats the inactive area moves only 0.77 -> 0.83 of GT (PF inactive logits are very confident). The grid is the spec's and stays (no change after seeing a number); S: a wider grid for class 11 is a question for the lead, not this item.
- The three UNSTABLE classes are large structural classes whose IoU moves by at most 0.0014; the sign flips do not affect the primary.

### 2e. G18 prior columns and inactive count-based readouts (S1 -> OP-C)
| | gaint PF | cv02 PF | HOUSE |
|---|---|---|---|
| inactive region recall (>= 100 px, >= 50% covered) | 0.609 -> 0.629 | 0.625 -> 0.645 | 0.607 -> 0.614 |
| inactive precision / recall | 0.769 / 0.592 -> 0.749 / 0.619 | 0.762 / 0.596 -> 0.743 / 0.624 | 0.766 / 0.621 -> 0.739 / 0.644 |
| pred inactive px on the 484 inactive-free cells | 10,035 -> 11,408 | 8,417 -> 9,583 | 4,786 -> 6,093 |
| pred / GT inactive px | 0.769 -> 0.826 | 0.783 -> 0.841 | 0.811 -> 0.872 |
| gridline pred / GT px; px on the 174 cells without gridline | 0.58 -> 1.20; 15,648 -> 46,389 | 0.59 -> 1.19; 15,783 -> 46,061 | |
| splice pred / GT px; px on the 472 cells without splice | 0.06 -> 1.05; 194 -> 12,710 | 0.06 -> 1.87; 1,478 -> 58,283 | |
| material pred / GT px | 0.69 -> 0.85 | 0.69 -> 0.84 | |
Crack guards (gaint / cv02): relP@2 +0.006 / +0.008, relR@2 -0.006 / -0.006 (both intervals exclude 0), width ratio -0.025 / -0.027, false crack px on crack-free cells unchanged.

## 3. Outcome under the rule
- **classbias_xfit PASSES** on gaint (exploration) and on cv02 (confirmation, same script unchanged): mIoU-R13 +0.0137 [+0.0107, +0.0169] and +0.0126 [+0.0077, +0.0167], crack IoU and relF1@2 within -0.0011, inactive IoU +0.010, no R13 class down by more than 0.0033. One variant read (ledger count 1).
- It is a decision layer, credited only against the same model's argmax (L3): the gain is almost all gridline (+0.06) and splice (+0.08 to +0.09), bought by predicting gridline 3 times and splice 39 to 65 times as often on cells that lack them (G18 table). The spec's drop rule does not fire, so **la_ce opens** (its gate was "classbias_xfit passes"; it must be read against baseline + classbias_xfit).
- **OP-C is defined and written** for PF on both machines (and for HOUSE): a prior-shifting arm's mIoU-R13 or inactive gain counts only if present at OP-A and against these OP-C dumps (Y6, G18). On PF, OP-C moves inactive IoU by +0.010, region recall by +0.02 and inactive false-alarm px by +14%: those are the margins an inactive arm must clear at OP-C.
- HOUSE (descriptive): +0.0091 [+0.0067, +0.0115], below 0.010; the bias helps the plain fine-tune less (splice 0 -> 0.05, inactive +0.003).
- S: about a third of the gain sits on splice (63k GT px, ARTS only) and is driven by one class's prior; the splice precision at OP-C is 0.15 to 0.20. Benchmark text should print gridline and splice beside mIoU-R13 whenever OP-C is used.

## 4. Owed (exact)
1. Lead: ledger lines for classbias_xfit (PASS, 1 variant, both machines) and for OP-C as the comparator of prior-shifting arms; `la_ce` gate open.
2. Wave 2a reads of rcs (and later la_ce, inact_paste, layered_ci): fit OP-C for the arm too only if the lead wants arm-at-OP-C; the critic's rule needs only baseline-at-OP-C, which exists:
   `python scripts/bench_read_w1.py --arm PFC=/home/noob/work/bench_udev/opc/dumps_gaint/elbench1/pf_v11_opc:'w1g_pf_v11_f[0-4]_s[5-8]' --arm RCS=<w2a rcs dump dir>:'<regex>' --baseline PFC --labels v11 --out /home/noob/work/bench_reads/<name> --workers 8`
   (gaint; for cv02 arms use dumps_cv02/elbench1/pf_v11_opc with 'w1c1_pf_v11_f[0-4]_s[5-9]').
3. For a new arm at OP-C with its own biases: `python scripts/bench_classbias.py --arm ARM=<method dir>:'<regex>' --labels v11 --fit-out <dir> --dumps <root> --method-opc <m>_opc --method-s1 <m>_s1 --workers 8` (needs logp dumps), then `bench_classbias_read.py` as in run_b1.sh.
4. HOUSE CPU re-dumps with logp (9.4 GB, bench_udev/opc/house_cpu_dumps) may be deleted once the lead no longer needs HOUSE at OP-C; MANIFEST of bench_udev/opc: bench_udev/opc/MANIFEST.md5 (12,888 files, md5 e1cabf4c).
5. Full pytest at the final bench_b commit 60fcf70: 579 passed, 4 skipped (bench_reads/stageB/B5/logs/pytest_full_3.log).

## 5. Variant 2: inactive grid to +8.0 (stage B fix round F2; reading rule written 15 Nov 15 Nov 16:34 IST, before any code or number of this variant)

Lead's ruling (log.md 15 Nov 16:07; PROTOCOL_v0.2 s11 item 8): one wider-grid variant for the inactive bias, ledger count 2 for classbias_xfit. Variant 1 (sections 1 to 4) stays the registered OP-C whatever happens here.

**Definition.** Identical to variant 1 (section 1) in objective (pooled mIoU over R13 without crack, ignore px not counted), cross-fitting (b_k for held-out fold k fitted on the other 4 folds of the same seed, asserted), class order (16, 20, 11, 13, 15, 21, 5, 4, 2, 1, 7), 3 sweeps, tie rule (closest to 0, then lower), FREE set, b[0] = b[14] = 0, input logp (float16) and the exact contested-px cache. **Only change:** the grid of class 11 (inactive) runs from -1.5 to +8.0 in steps of 0.25 (39 values); every other class keeps -1.5 to +4.0 (23 values). The contested-px box uses +8.0 as the upper bound for class 11 (so the cache stays exact for the wider grid). Its dumps are a separate family OP-C2: /home/noob/work/bench_udev/opc2/dumps_<machine>/elbench1/pf_v11_opc2 (derivation classbias_xfit_v2); the baseline S1 is the existing S1 family of variant 1 (opc/dumps_<machine>/elbench1/pf_v11_s1, the same argmax of the same logp).

**Explore and confirm.** Explore on gaint PF v1.1 seeds 5 to 8 (20 fits), confirm with the same script unchanged on cv02 PF v1.1 seeds 5 to 9 (25 fits). Variant 2 PASSES only if both machines pass.

**Pass rule on one machine** (all must hold; point values are means over seeds, pooled out-of-fold over the 532 pool cells; interval = two-stage group bootstrap with paired seeds, 2,000 draws, seed 0, as variant 1):
1. Variant 1's rule unchanged for OP-C2 minus S1: delta mIoU-R13 >= 0.010 with 95% interval low > 0; crack strict IoU delta >= -0.005; crack relF1@2 delta >= -0.005; inactive IoU delta >= -0.010; no R13 class with IoU delta < -0.030.
2. Not worse than variant 1 on mIoU-R13 by more than 0.002: mIoU-R13(OP-C2) >= mIoU-R13(OP-C) - 0.002 (point).
3. Inactive precision: OP-C2 must not lower inactive precision by more than variant 1 does plus 0.02. The lead's words are "inactive precision on cells without inactive area"; precision computed only on cells without inactive GT is 0 by definition, so I read it as the precision loss caused by inactive predictions on those cells, and check two versions, both must hold:
   - 3a. pooled inactive precision P = TP / predicted inactive px over all 532 cells: (P(OP-C2) - P(S1)) >= (P(OP-C) - P(S1)) - 0.02;
   - 3b. inactive "cell precision" Pc = share of predicted inactive px that lie on cells with inactive GT (1 minus the share on the 484 inactive-free cells): (Pc(OP-C2) - Pc(S1)) >= (Pc(OP-C) - Pc(S1)) - 0.02.
   If the lead meant a different quantity, both numbers are printed and the lead decides; the thresholds stay.

**Edge rule.** If b[11] = +8.0 (the new edge) in any of the 20 gaint fits, this is reported, no third grid is built, and the variant stops after the gaint read: its gaint numbers are printed, no cv02 confirmation is run, and variant 2 does not pass (it cannot pass without the confirmation).

**Printed beside it (decide nothing):** the variant 1 lines of section 2 for OP-C2 (per class, per source, G18 columns, inactive counts, bias spread), gridline and splice IoU and their false px on cells without the class, and every headline value on the 528 cells without the 4 duplicate cells of benchmark/splits/dup_crossfold_v1.tsv beside the 532-cell value (the 532-cell values decide, as for variant 1).

### 5a. Variant 2 numbers (E unless marked S; 15 Nov 17:16 to 17:25 IST, then one read again at 17:26)
Tools: bench_b fdb6a5c (variant code; the fit log names 8f9178b, the next commit, which changed no classbias file; tree clean), read again at b5bf0ae (bench_classbias_read fix of the 528-cell table, below). Chain stageBfix/F2/run_f2.sh in tmux bench_bfix_f2 (CPU, nice 19, 7 workers). Inputs: gaint W1-G + W1-G2 PF dumps (20 runs, logp), variant 1 S1 and OP-C families in bench_udev/opc (unchanged). Outputs: fit /home/noob/work/bench_reads/stageBfix/F2/v2/fit_gaint_pf (classbias_b.tsv 1b56049d), read v2/read_gaint_pf_r2/read.txt (11ea2f46; the first read v2/read_gaint_pf, 82f65d5f, has the same 532-cell part line for line; its 528-cell headline lines repeated the 532 values, a tool slip fixed in b5bf0ae with a test that fails on the old code). OP-C2 dumps: /home/noob/work/bench_udev/opc2/dumps_gaint/elbench1/pf_v11_opc2 (20 runs, derivation classbias_xfit_v2, manifests carry classbias_b, fit_folds, classbias_variant), MANIFEST /home/noob/work/bench_udev/opc2/MANIFEST.md5 415a523d (2,148 files, 2.6 GB).

**Edge rule fires.** b[11] = +8.0 (the new edge) in **14 of 20** gaint fits (mean +7.60, min +5.00, max +8.00); the other 10 classes got the variant 1 value in 217 of 220 (seed, fold, class) cells (differences: s6 f1 border 0.25 -> 0, padding 1.0 -> 0.75; s7 f4 material 0.75 -> 1.0). Per the rule: reported, no third grid, **no cv02 confirmation run, variant 2 does not pass.**

Gaint read (pooled out-of-fold, 532 cells, mean over seeds 5 to 8; paired two-stage bootstrap, 2,000 draws):
| | S1 | OP-C (variant 1) | OP-C2 (variant 2) |
|---|---|---|---|
| mIoU-R13 | 0.6129 | 0.6266 | 0.6267 |
| crack IoU / relF1@2 | 0.3646 / 0.8443 | 0.3635 / 0.8437 | 0.3609 / 0.8411 |
| inactive IoU | 0.5025 | 0.5129 | 0.5166 |
| inactive precision (pooled) / recall | 0.7694 / 0.5916 | 0.7493 / 0.6190 | 0.7274 / 0.6404 |
| inactive cell precision (share of pred px on cells with inactive) | 0.9542 | 0.9516 | 0.9499 |
| pred inactive px on the 484 inactive-free cells; pred / GT inactive px | 10,035; 0.769 | 11,408; 0.826 | 12,564; 0.880 |
| inactive region recall (>= 100 px, >= 50% covered) | 0.609 | 0.629 | 0.640 |

- Rule 1 (variant 1's rule for OP-C2 - S1): mIoU-R13 +0.0138 [+0.0105, +0.0174], crack IoU -0.0037, relF1@2 -0.0031, inactive IoU +0.0141 [-0.0020, +0.0295], worst class crack -0.0037: **holds**.
- Rule 2: mIoU-R13 0.6267 >= 0.6266 - 0.002: **holds** (OP-C2 - OP-C +0.0001 [-0.0006, +0.0008]).
- Rule 3a (pooled inactive precision): OP-C2 - S1 = -0.0420, limit = (OP-C - S1) - 0.02 = -0.0201 - 0.02 = -0.0401: **fails** (by 0.0019).
- Rule 3b (cell precision): -0.0043 against limit -0.0026 - 0.02 = -0.0226: holds.
- **Variant 2: FAIL on gaint** (rule 3a) and stopped by the edge rule. Variant 1 stays the registered OP-C; classbias_xfit ledger count is now 2.
- OP-C2 - OP-C (descriptive): crack IoU -0.0026 [-0.0050, -0.0003], relF1@2 -0.0025 [-0.0051, -0.0001], relR@2 -0.0072, width ratio -0.022, inactive IoU +0.0037 [-0.0038, +0.0117]. S: the larger inactive bias takes crack px inside or next to inactive regions (crack at argmax loses recall) and buys inactive recall with precision; the inactive optimum still lies at or past +8 nats in most fits, so the PF inactive logits are very confident and a class prior shift is a poor lever for inactive.
- 528 cells (dup_crossfold_v1 excluded): every value within 0.0004 of the 532 value; T10 rule PASS and variant 2 rule FAIL on both (read.txt last section).
