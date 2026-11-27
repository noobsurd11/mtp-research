# Dataset-fault audit: plan (dataset_auditor, 19 Nov 2026, written 01:20 IST before any measure in this folder was computed)

Goal (user, 19 Nov): "can we somehow quantitatively or qualitatively benchmark the dataset, like its faults, somehow proving its cons".
This file fixes the axes, the measure for each, the rule that declares a fault, and what each measure cannot show. It is written before
any number below exists. Changes after the first number are added as dated amendments at the end, never by editing the text above them.
Tags used later: E = measured, S = judgement, P = taken from an earlier record (file named).

## 0. Scope, inputs, rules
- **Cells.** Pool P532 only (legacy train + val; `benchmark/splits/pool532_manifest.tsv` d352f509). Every stem is checked against
  `forbidden_v1.txt` and the legacy test list before any mask or dump is opened (fail closed). No label, prediction or label summary of
  the legacy test (50) or E1 (106) is read; `cells.tsv` sealed rows are dropped before any column is used. Image-side checks use P532
  pixels (and, if time allows, a random sample of the unlabelled pool); sealed images are not read by this audit at all.
- **Labels.** v1.1 (`/home/noob/work/bench_data/masks_v11/masks`, MANIFEST f88907f2; 255 = ignore, never scored). Old labels for axis d:
  BenchmarkEL `20211104` (`el-fault-detection/data/labeled/masks_coded`). Crack = class 14, inactive = class 11.
- **Predictions (no training, no GPU).** Primary consensus: the 25 cv5v3 out-of-fold models per cell relayed from cv02
  (`bench_relay/`): PF `c3_pf_v11`, HOUSE `c3_house_v11`, HRNET `c3h_hrnet_w18_unetpp_pf`, SWADBN `c3s_swad_v11` (primary readout,
  folder without `.swad`), C3X `c3x_hrnet_swad_v11` (folder without `.swad`); seeds 5 to 9 each; split cv5v3 (285 groups, d880a769).
  Replication set: cv5v2 W1-G PF seeds 5 to 8 (gaint, `bench_dumps/w1g`), a different split, machine and fold assignment.
- **Check before use.** My own pooled levels for PF, HOUSE, HRNET at argmax on 532 cells (mean over 5 seeds) must equal
  `results/C3HRNET_READ.md` section 3 (PF 0.365 / 0.846, HOUSE 0.383 / 0.852, HRNET 0.366 / 0.857, strict crack IoU / relF1@2) to 3
  decimals. If not, I stop and find the difference before any contrast below is read.
- **Statistics.** Two-stage group bootstrap as the protocol (cv5v3 groups with replacement, then one seed per fold per arm), 2,000
  draws, `numpy.random.default_rng(0)`, 95% percentile intervals. M = 0.010 (protocol, both machines). One variant per measure.
- CPU only, `nice -n 19`, at most 8 workers. Scripts in `scripts/`, tables in `out/` with md5s in `out/MD5.txt`. Gallery stays local.

## 1. Axes, measures and fault rules

### a. Label errors from multi-model out-of-fold consensus (method: Northcutt et al. 2021 confident learning, doi:10.1613/jair.1.12125; Rottmann & Reese 2023 component-level detection, doi:10.1109/wacv56688.2023.00323; Lad & Mueller 2023 softmin image score, arxiv:2307.05080)
Per cell: V_c = number of the 25 models whose argmax is class c (c = crack, inactive), Q_c = mean score p_c over the 25.
- **Missed crack (MC):** pixels with V_crack >= 20 (80% of models), on scored px, farther than 2 px from every v1.1 crack px; 8-connected
  components of these px with >= 20 px. Kind = "whole" if the full consensus component never comes within 2 px of v1.1 crack, else
  "extension".
- **Spurious crack (SC):** v1.1 crack component (8-connected, >= 20 px) where >= 90% of its px have at most 2 of 25 models predicting
  crack within 2 px (v2 = max of V_crack over the 5 x 5 neighbourhood <= 2).
- **Missed inactive (MI):** component of {V_inact >= 20} with >= 100 px and < 10% of its px labelled inactive.
- **Spurious inactive (SI):** v1.1 inactive component >= 100 px with >= 90% of its px at V_inact <= 2.
- **Image evidence (independent of the models):** local contrast z = (median grey on the component - median grey on a ring 3 to 6 px
  away, other crack px excluded) / (1.4826 x MAD of the ring). Cracks and inactive areas are dark in EL. Support for MC/MI: z <= -1.0;
  support for SC/SI (label on a region that is not darker than its surroundings): z > -0.5. Printed also at -0.5 / -2.0 and 0 / -1.0.
- **Declared fault:** a component meeting the MC, SC, MI or SI rule is a *candidate*; a candidate with image support is a *supported
  candidate*. Both are counted (components, px, cells, share of v1.1 crack px), per source and in total.
- **Class under the candidate:** the v1.1 classes under each MC / MI component are tabulated (e.g. a consensus "crack" on labelled
  gridline is a convention or model question, not a missed crack).
- **Replication:** share of MC / SC candidates that the cv5v2 W1-G PF set (4 models, rule >= 3 of 4 / <= 0 of 4) also flags.
- **Ranking for review:** per cell the Lad & Mueller softmin (tau = 0.1) of the binary self-confidence (Q_crack on labelled crack px,
  1 - Q_crack elsewhere; the same for inactive); the gallery shows the 30 candidates with the most px plus the 10 lowest-softmin cells.
- **My own visual check (S):** I look at up to 40 gallery panels and put each candidate in one of: "label error likely", "ambiguous /
  convention", "model error likely". This is an S tag, one non-expert look; it never replaces an annotator.
- Cannot show: whether a candidate is truly a label error (no second annotator); errors the models share with the labels (all models were
  trained on the same conventions, so systematic label errors that the models learned are invisible); recall of the detector (no planted
  errors, which would need retraining).

### b. Annotation conventions per source, from the masks (P532, v1.1)
- Crack label width per cell = crack px / skeleton length (`bench/skel.py`, the frozen implementation); pooled and median per source;
  **eta^2** = share of the variance of per-cell width explained by source (one-way ANOVA on cells with >= 50 skeleton px).
- Fragmentation: crack components per 100 skeleton px; share of crack px in components < 20 px (specks).
- Placement against the image: mean grey profile at distance d = 0..8 px from the label skeleton, normalised to the 6 to 8 px ring;
  dark-trough full width at half depth vs label width, per source (ratio > 1.3 or < 0.77 = label wider / narrower than the visible
  trough; fault declared if two sources differ in this ratio by > 0.3).
- Darkness of labelled defects: per source share of v1.1 crack components with z > -0.5 (labels on lines that are not dark); mean z of
  inactive regions.
- Class vocabulary per source: cells per class per source (24 x 5); classes that occur in one source only.
- Fault declared: eta^2 >= 0.25 for width (source decides a large share of label width), or a between-source width ratio >= 1.3.
- Cannot show: which convention is "right"; whether width differences come from the annotation tool, image resolution or real crack
  width (partly separable with the trough ratio only).

### c. Duplicates, near-duplicates and leakage
- Mostly measured already; I consolidate with numbers and files (P): `results/stageC/SPLIT_INTEGRITY.md`, `results/stageA/A6_duplicates.md`,
  `benchmark/splits/dup_crossfold_v1.tsv`, `module_identity_v3.tsv`, handbook 17 section 5.6 (release splits), `cells.tsv` flags
  (`dup_image`, `mask_copy_*`, `wrong_mask_v1`).
- New and cheap (E): exact duplicates in P532 by grey-pixel md5 (`pool532_manifest.tsv`); near-duplicates by a 64-bit DCT perceptual
  hash, Hamming distance <= 6, between P532 cells of different physical cells (cv5v3 groups), listed with NCC for the lead's eyes.
- Mask copies: pairs of P532 cells of one physical cell whose crack masks have raw IoU >= 0.85 (count, px).
- Fault declared: any pair across cv5v3 groups with hash distance <= 6 and NCC >= 0.9 (new leak), any mask copy.
- Cannot show: module identity for BMRK and SDLE (no ids); leakage through look-alike cells of different modules.

### d. Label-version change (20211104 vs v1.1) on P532
- Cells changed (crack, inactive, any class), px changed, crack components joined.
- Score shift: the 25 cv5v3 models scored against v1.1 and against 20211104 (v1.1 ignore px ignored in both); levels and the four
  contrasts (HOUSE, HRNET, SWADBN, C3X minus PF) under each version.
- Fault declared: level shift >= M (0.010) on a headline metric; a contrast is "label-version sensitive" if it moves by >= 0.005 or its
  pass / fail at M changes.
- Cannot show: which version is closer to the truth; the models were trained on v1.1, so the shift is biased in favour of v1.1.

### e. Coverage and statistical power
- Per class (24) and per source: cells, cv5v3 groups, px. Classes with < 10 groups in P532 are "not measurable" as a pooled IoU.
- Kish effective n over cv5v3 groups, n_eff = (sum w)^2 / sum w^2, with w = labelled px per group (crack, inactive), for the pooled
  metrics.
- Fragility of the reported contrasts (HRNET, HOUSE, SWADBN, C3X minus PF; relF1@2 and strict crack IoU at argmax, mean over seeds,
  532 cells): greedy removal of whole groups in order of largest contribution to the delta; k_M = groups removed until delta < M,
  k_0 = until delta <= 0. Fault declared: a contrast with k_0 <= 5 groups is "decided by a handful of cells".
- Cannot show: power for effects on unseen sources (U1 covers that); fold-assignment variance (not run).

### f. Ambiguity and the labelling ceiling
- Error decomposition: for each of the 25 models, its relR@2 misses and relP@2 false px are split by how many of the 25 models make
  the same call within 2 px: "systematic" (>= 20 of 25), "variable" (6 to 19), "own" (<= 5). The systematic share is what averaging
  models of these recipes cannot remove: label error, convention, or a shared blind spot.
- Share of each model's error px that falls inside the a-candidates.
- Consensus as a predictor (V_crack >= 13): its pooled relF1@2 and strict IoU (an ensemble of 25, not a method claim).
- Tolerance ceiling: strict crack IoU of each v1.1 crack mask against itself shifted by 1 px (8 directions, mean), pooled over P532,
  and against its skeleton re-drawn at the pool-median width ("same centreline, other width convention"). The protocol's 0.48 to 0.60
  band was measured on the legacy test only; this re-measures it on the pool.
- Repeat-label agreement: crack relF1@2 and strict IoU between masks of the same physical cell in two P532 images (aligned by NCC,
  shift <= 8 px), copies excluded (raw IoU >= 0.85); extends A4's 6 pairs with the cv5v3 grouping. Growth is not separated except by
  A4's rule (skeleton length ratio > 1.5 = growth-affected).
- Label-noise sensitivity of contrasts: the four contrasts re-scored with all a-candidate px set to ignore. A contrast is
  "within label noise" if it moves by >= 0.005 or its pass / fail at M changes. Also re-scored against GT width variants (skeleton
  only; skeleton drawn 3 px wide): a contrast whose sign on strict IoU changes with the width convention is "convention-dependent".
- Cannot show: a true ceiling (no multi-annotator labels); the systematic share is an upper bound on label-caused error only in the
  sense that it also holds shared model failures.

### g. Image-side faults and source separability (P532)
- Per image: mean, std, p1, p99, share of px at 0 and at 255, number of grey levels used, robust noise sigma (P16 rule), Laplacian
  variance, share of spectral power above 0.25 cycles/px, 8 x 8 block-boundary ratio (JPEG), colour spread of the original file,
  padding share (pixels of the padding class).
- Source separability: logistic regression and random forest on these features plus a 16-bin grey histogram and an 8-bin radial
  spectrum, 5-fold cross-validation grouped by cv5v3 group; balanced accuracy against chance (0.20). Fault declared: balanced accuracy
  >= 0.90 ("the source is identifiable from global image statistics"), read together with per-source defect prevalence (P(crack |
  source), P(inactive | source)) as a shortcut risk.
- Cannot show: that a segmentation model uses the shortcut; native module resolution (not on disk).

## 2. Report
`REPORT.md`: ranked faults, each with number, method, E/S, limit, and what it means for the benchmark (which gains are within label
noise or convention). Ends with what needs GPU time, new data or a user decision.

## Amendments
(none yet)

### Amendment 1 (19 Nov 2026, 02:05 IST, after the first numbers; the text above is unchanged, md5 3a0726b5 in out/PLAN_prereg.md5)
Added after seeing the gallery (so these are declared post hoc, once):
- b5 crop geometry: the gallery showed that ARTS / CFVS / CSIR images are windows of one cell plus parts of its neighbours. Measure:
  centre cell = the cell holding the image centre, bounded by rows / columns with > 20% cell-gap (spacing) px; share of crack and
  inactive px outside it; cells whose every defect px is outside it. Checked on 7 images by eye (out/gallery/check_centre_cell.png).
- b6 crop effect: consensus recall@2 inside vs outside the centre cell and within 32 px of the image edge.
- f2: the one double annotation (CFVS_00015_r7_c4 / CFVS_00016_r7_c4, identical pixels) scored mask against mask on the headline metrics.
- b3 inactive conventions, measured as: share of inactive boundary px within 2 px of a crack label; crack px inside inactive = crack px
  whose 9 x 9 window has >= 70% inactive among its non-crack px.
- c1: cross-group DCT-hash pairs were checked for defect labels (all 41 are same-position look-alikes, 1 crack cell among them).
Planned and not done: repeat-label agreement over all same-cell pairs (A4 and benchmark/out/label_checks_summary.txt section 3 already
hold it for the usable pool pairs; I cite them instead of re-running); the unlabelled-pool sample for image statistics.
Deviation to disclose: while locating files I printed the first 20 lines of /home/noob/work/bench_data/masks_v11/SUMMARY.txt, which
includes per-split counts for the legacy test (the same counts published in benchmark/LABELS_V11.md section 2). Nothing from it is used.
