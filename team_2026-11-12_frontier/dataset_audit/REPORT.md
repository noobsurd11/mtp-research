# Dataset-fault audit of the benchmark pool (dataset_auditor, 19 Nov 2026, 02:20 IST)

Question (user, 19 Nov): can the dataset's faults be benchmarked, quantitatively or qualitatively. Plan with thresholds fixed before
any number: `PLAN.md` (pre-registration md5 3a0726b5 in `out/PLAN_prereg.md5`; Amendment 1 lists what was added after the first
numbers). Tags: **E** = measured here, **S** = judgement, **P** = an earlier record, file named. CPU only (nice 19, 8 workers, about
2 CPU-minutes in all); no training; no sealed label, prediction or label summary used (one disclosed print, PLAN Amendment 1).

**Data and models.** Pool P532 (legacy train + val), label set v1.1, old labels BenchmarkEL `20211104`. 25 out-of-fold models per cell:
cv5v3 PF, HOUSE, HRNET, SWADBN, C3X x seeds 5 to 9 (cv02 relay). Replication set: cv5v2 W1-G PF seeds 5 to 8 (gaint). Check passed:
my pooled levels equal the registered reads (PF 0.3653 / 0.8463 / 0.5042 strict crack IoU / relF1@2 / inactive IoU; HOUSE 0.3832 /
0.8522; HRNET 0.3661 / 0.8567; W1-G seeds 5, 6 0.3624 / 0.8417 / 0.4980), and my bootstrap gives HRNET - PF relF1@2 +0.0104
[+0.0010, +0.0209] against the read's [+0.0012, +0.0203].

**Literature (Research MCP ids).** Confident learning, Northcutt et al. 2021 (doi:10.1613/jair.1.12125); test-set label errors that
reorder benchmarks, Northcutt et al. 2021 (arxiv:2103.14749); image-level softmin label-quality score for segmentation, Lad & Mueller
2023 (arxiv:2307.05080, method section read); component-level label-error detection in segmentation, Rottmann & Reese 2023
(doi:10.1109/wacv56688.2023.00323); near-duplicates between train and test, Barz & Denzler 2020 (doi:10.3390/jimaging6060041);
annotation noise as an upper bound on scores, Tschirschwitz & Rodehorst 2025 (doi:10.1109/wacv61041.2025.00666); visual dataset bias
survey, Fabbrizzi et al. 2022 (doi:10.1016/j.cviu.2022.103552). Only abstracts and one method section were read.

## 1. Ranked faults

### F1. Strict crack IoU measures the annotators' line-width convention more than the model (E)
- Same 25 models, same predictions, labels redrawn from the v1.1 centreline: PF strict crack IoU **0.233** (1-px centreline), **0.365**
  (v1.1), **0.414** (centreline drawn 3 px wide). relF1@2 stays 0.824 / 0.846 / 0.849 (`out/contrasts.txt`).
- The label against itself: shifted 1 px, IoU **0.483**; shifted 2 px, **0.249**; reduced to its centreline, **0.465**; redrawn
  3 px wide, **0.605** (pooled over the 229 crack cells; `out/labels_audit.txt` f1). relF1@2 of each of these is 1.0.
- Contrasts that change their verdict with the convention (rule: shift >= 0.005 or PASS changes):
  - HOUSE - PF strict IoU +0.0179 PASS on v1.1; **+0.0015 (no pass) on centreline labels**; +0.0367 on 3-px labels.
  - SWADBN - PF strict IoU +0.0180 PASS; **+0.0047 (no pass) on centreline labels**; +0.0342 on 3-px labels.
  - HRNET - PF strict IoU +0.0008 on v1.1, **-0.0109 on 3-px labels (sign change)**; relF1@2 +0.0104 PASS, +0.0073 (no pass) on 3-px.
  - relF1@2 contrasts move by at most 0.0031 under every variant.
- Method: re-scoring the stored argmax maps against label variants; two-stage group bootstrap (285 groups, then one seed per fold).
- Limit: the variants are synthetic conventions, not a second annotator; the 3-px variant is BMRK's convention applied everywhere.
- Implication (S): strict crack IoU gains of arms that draw wider cracks (HOUSE, SWAD) are convention effects; relF1@2 as the
  deciding crack metric is supported. Strict IoU should be printed with its convention band, never decide.

### F2. The labels agree with themselves no better than the models agree with them: a labelling ceiling (E, small n)
- The one image annotated twice in the release (`CFVS_00015_r7_c4` = `CFVS_00016_r7_c4`, identical pixels, both pool): mask against
  mask, strict crack IoU **0.259**, relF1@2 **0.829**, inactive IoU 0.829, ribbons IoU 0.437, gridline 0.288, all-pixel agreement
  0.871 (`out/crop_and_double.txt`). Models against the label on the pool: PF 0.365 / 0.846; 25-model vote 0.398 / 0.868.
- Two images of the same physical cell, no crack growth (P `benchmark/out/label_checks_summary.txt` section 3, pool pairs): strict
  IoU 0.16 to 0.37, tolerant F1@2 0.77 to 0.95; A4: 97% of mutual centreline distances within 2 px (P `results/stageA/A4.md`).
- Error decomposition (E, `out/contrasts.txt`): of each model's missed crack px (relR@2), **63%** are missed by at least 20 of the 25
  models within 2 px, 30% by 6 to 19, **7%** by 5 or fewer; of false crack px, **68%** are made by at least 20 of 25. Inactive: 74% of
  missed and 41% of false inactive px are shared by at least 20 of 25.
- Limit: one double annotation, one source (CFVS); "shared by all models" also covers shared blind spots, not only label noise.
- Implication (S): on crack, models already sit at the agreement level of two drawings of one image. Further gains of +0.01 relF1@2
  are near what these labels can resolve; most residual error is common to every recipe tried, so it is not a model-choice problem.

### F3. The images are windows of about 3 x 3 cells, and most labelled defects lie on the neighbours (E)
- ARTS, CFVS and CSIR images show one centre cell (median 249 to 250 px wide, **25 to 30% of non-padding px**) plus parts of the 8
  neighbouring cells; the labels cover the whole window. BMRK and SDLE are single cells with 75% padding.
- **57% of v1.1 crack px and 71% of inactive px lie outside the centre cell**; ARTS 68% / 100%, CFVS 62% / 79%, CSIR 72% / 78%.
- **117 of the 229 "crack cells" have no crack px in their centre cell; 28 of the 48 "inactive cells" have no inactive px there.**
- 61 pool images overlap a pool image of the adjacent position of the same module image (35 pairs; 16% of crack px), so parts of the
  same crack are scored twice (same cv5v3 group, so no fold leak).
- Defects on the neighbour parts are harder: 25-model recall@2 0.794 outside vs 0.844 inside the centre cell; px missed by at least
  20 of 25 models 14.3% vs 9.9% (`out/crop_and_double.txt` b6).
- Method: centre cell = the cell holding the image centre, bounded by mask rows / columns with > 20% cell-gap px; checked by eye on 7
  images (`out/gallery/check_centre_cell.png`). Declared post hoc (PLAN Amendment 1).
- Limit: geometry from the gap classes of the mask; 63 BMRK / SDLE images have no gap lines (single cells).
- Implication (S): every cell-level quantity (has crack, "crack-free cells" of the false-alarm guard, inactive area %, any severity
  label) describes a window, not a cell. A defect at the window edge is seen with partial context.

### F4. Inactive labels: about 1 in 9 labelled inactive px is rejected by every model, and the metric rests on about 13 groups (E + S)
- Spurious-inactive candidates (labelled region >= 100 px, >= 90% of px with at most 2 of 25 models voting inactive): **63 regions
  in 18 cells, 31,039 px = 10.9% of inactive px**; **CSIR 62%** of its inactive px, CFVS 3.4%, BMRK 12.8% (`out/a_summary.txt`).
- Missed-inactive candidates (>= 20 of 25 vote inactive, < 10% labelled): 9 regions in 7 CFVS cells, 7,745 px (2.7%).
- 22% of labelled inactive regions >= 100 px are not darker than their 3 to 6 px ring (contrast z > -0.5).
- Conventions vary between cells: share of an inactive boundary that carries a crack label 0.10 to 1.00 per cell (median 0.78); 26
  of 47 inactive cells have cracks drawn inside the inactive area (18,954 px); 41% of the models' "missed crack" px lie inside
  labelled inactive (`out/labels_audit.txt` b3; `out/a_summary.txt`).
- Power: inactive px sit in **33 of 285 groups, Kish n_eff 12.9 groups**; the top 5 groups hold 54% of inactive px.
- Ignoring the candidate px raises PF inactive IoU **0.504 to 0.574 (+0.069)**, above the inactive margin M (0.049 to 0.054).
- Visual check of the largest candidates (S, `out/a_visual_check.tsv`): missed inactive 4 of 5 "label error likely" (dark regions
  enclosed by cracks, while similar regions nearby are labelled); spurious inactive 2 of 7 "label error likely" (`CSIR_00055_r6_c3`,
  a region as bright as the rest of the cell), 5 ambiguous (slightly darker regions, multi-crystalline dark grains, an under-exposed image).
- Limit: candidates are model-defined; one non-expert look, no annotator.
- Implication (S): pooled inactive IoU is bounded by label disagreement of the same size as every inactive effect tested so far;
  inactive claims need region counts or 5 seeds (as the protocol already rules) and a stated label-noise band.

### F5. Crack label errors exist, are visible, replicate across splits, and do not reorder the arms (E + S)
- Missed crack (>= 20 of 25 models, > 2 px from any label, >= 20 px): **128 segments in 42 cells, 5,436 px (1.8% of crack px)**; 38
  whole cracks, 90 extensions of labelled cracks. 41% of these px are labelled inactive (crack-inside-inactive convention, F4).
- Spurious crack (labelled component >= 20 px with >= 90% of px at most 2 of 25 models within 2 px): **53 components in 28 cells,
  7,567 px (2.5%)**; CSIR 9.7% of its crack px, ARTS 4.3%, CFVS 0.5%.
- Replication on the independent cv5v2 W1-G models: 97% of missed and 91% of spurious candidates. Image support: 46 of 128 and 32 of 53.
- Visual check of the 18 largest (S): 4 label error likely (a displaced label 8 to 10 px parallel to the visible crack in
  `CSIR_00094_r16_c5`; an unlabelled crack extension in `CSIR_00092_r12_c5`), 7 convention (crack inside or on the edge of
  inactive), 5 ambiguous, 1 model error, 1 unverifiable (`CSIR_00070_r7_c2`, a noise image).
- Effect: ignoring every candidate px raises PF relF1@2 0.846 to 0.864 and strict IoU 0.365 to 0.378, but **no contrast moves by
  more than 0.003** (candidates hit all models alike).
- Limit: the detector finds only errors the models do not share; its recall is unknown (no planted errors, which need retraining).
- Implication (S): crack label errors cost about 0.02 relF1@2 in level, not in ranking. Rankings are not label-error artefacts on
  this evidence; absolute levels are.

### F6. The label release moves scores more than any method (E; extends handbook doc 11 row 1 to the pool and current models)
- 20211104 to v1.1 on P532: 169 of 532 cells change; crack px 260,084 to 307,546 (+18%); crack components 3,859 to 1,121; 91 cells'
  crack px differ (`out/labels_audit.txt` d).
- Same 25 models scored on each version: PF strict IoU **0.320 vs 0.365 (+0.045)**, relF1@2 **0.822 vs 0.846 (+0.025)**; inactive
  unchanged. Contrasts move by at most 0.008 (HOUSE strict IoU -0.0076), no pass changes.
- Limit: the models were trained on v1.1, which favours v1.1.
- Implication (S): a published level is meaningless without the release; the largest method gain (+0.015 relF1@2) is 0.6 of it.

### F7. Each source has its own label conventions and vocabulary (E)
- Crack label width (px / centreline px): ARTS **1.59**, CFVS 2.06, CSIR 2.25, BMRK **3.09**; source explains **29.6%** of the
  variance of per-cell width (eta^2, n 207 cells; Kruskal-Wallis p 3e-12). Fault declared (rule eta^2 >= 0.25; ratio 1.94 >= 1.3).
- Labels are drawn at about half the width of the visible dark line in every source (label / trough FWHM 0.45 to 0.63; trough
  2.9 px ARTS, 4.3 to 4.9 px CSIR / CFVS / BMRK), so part of the width difference follows image blur; BMRK is relatively widest.
- **10 of 24 classes occur in one source only** (splice in 60 ARTS cells and nowhere else; corrosion SDLE only; text, jbox, rings,
  clamp, measurement artefact ARTS only; dead cell, belt mark, sp dogbone CSIR only). Gridline is labelled in 82% of ARTS, 78% of
  CFVS and 38% of CSIR images. 9 classes have fewer than 10 groups (`out/labels_audit.txt` b4).
- Limit: cannot tell annotator style from real differences between module types.
- Implication (S): the per-source width guard of the protocol is needed; per-class IoU of one-source classes measures source
  recognition; U1's thin predictions on BMRK (width ratio 0.42) are partly label style (P `results/U1_READ.md`).

### F8. The source is identifiable from global image statistics (E)
- Balanced accuracy of a source classifier, 5-fold CV grouped by cv5v3 group (chance 0.20): **0.94** (logistic regression, all
  features), 0.89 without padding and cell size, **0.85 from the 8-bin power spectrum alone** (`out/image_audit.txt` g2).
- High-frequency power (share above 0.25 cycles/px): ARTS 0.031, CSIR 0.040, CFVS 0.003, BMRK 0.002, SDLE 0.001 (10 to 40 x), i.e.
  CFVS / BMRK / SDLE images are upsampled. CSIR: 37 images carry colour, 29 have > 1% black px, 19 are under-exposed (p99 < 128).
- Defect prevalence differs by source: crack in 26% of ARTS, 59% of CFVS, 60% of BMRK images; inactive 1% to 17%.
- Limit: shows a shortcut is available, not that a model uses it.
- Implication (S): source carries prevalence and label style; the unseen-source drop of 0.11 relF1@2 (P U1) is consistent with this.

### F9. A handful of module groups decide the reported crack contrasts (E)
- Crack px sit in 125 of 285 groups; **Kish n_eff 24.1 groups**; the top 5 groups hold 37% of crack px.
- Greedy removal of whole groups (relF1@2, 5 seeds, 532 cells): HOUSE - PF +0.0059 **reaches 0 after 4 groups** (fault rule
  k_0 <= 5); HRNET - PF +0.0104 falls under M after 1 group (`CFVS_00139`) and to 0 after 17; SWADBN - PF 0 after 24; C3X - PF under
  M after 5, 0 after 31. Strict IoU: HRNET 0 after 1 group; HOUSE under M after 9.
- Limit: greedy removal is a worst case, not a sampling distribution (the bootstrap interval is that).
- Implication (S): a +0.01 crack gain rests on a few CFVS modules (`CFVS_00139`, `00009`, `00017`, `00146`); an arm should report
  which groups carry its gain.

### F10. Image faults (E)
- 2 pool images with noise sigma > 10 (`CSIR_00070_r7_c2`, `CSIR_00069_r7_c1`); on `CSIR_00070_r7_c2` the labelled crack is not
  visible (S). 109 of 532 images show an 8 x 8 block grid (JPEG history; ratio > 1.10). 19 under-exposed CSIR images.

### F11. Duplicates and leakage (P, consolidated; one small new check)
- cv5v2: 24 physical modules span folds, 91 pool cells held out while their module trains; fixed by cv5v3; the effect of the leak was
  not separated (P `results/stageC/SPLIT_INTEGRITY.md`, `results/C3_LEAK_READ.md`). Legacy test: 8 cells are the same physical cell
  as a pool cell, 7 neighbouring windows, 19 share a module (P SPLIT_INTEGRITY section 5). E-SCDD: 44 of 82 test cells share a module
  with train; release splits reshuffled 186 of 582 cells (P handbook 17 section 5.6; PROTOCOL_v0.2 section 1).
- Masks: 2 exact and about 10 near copies between images of one cell; one cell carried another cell's mask (P label_checks_summary,
  LABELS_V11). Exact image duplicate: 1 pair (the double annotation of F2).
- New (E): 41 cross-group pairs with DCT-hash distance <= 6 (37 with NCC >= 0.9), all ARTS / CSIR same-position look-alikes, 1 with a
  crack label; consistent with the prior ruling (look-alike edge cells, not grouped). No new leak found.
- Implication (S): leakage is handled for CV5-G by cv5v3; the window overlap of F3 makes leakage across neighbouring windows the
  default whenever module grouping is absent (BMRK / SDLE have no module ids).

## 2. What it means for the reported gains (S, from F1, F5, F6, F9)
| Contrast (cv5v3, 5 seeds, 532 cells) | relF1@2 | under label variants (old / centreline / 3 px / candidates ignored) | k_0 | strict IoU | under variants |
|---|---|---|---|---|---|
| HOUSE - PF | +0.0059 | +0.0033 / +0.0036 / +0.0079 / +0.0053 | 4 | +0.0179 PASS | +0.0103 / **+0.0015** / +0.0367 / +0.0179 |
| HRNET - PF | +0.0104 PASS | +0.0109 / +0.0107 / **+0.0073** / +0.0107 | 17 | +0.0008 | +0.0028 / +0.0032 / **-0.0109** / +0.0007 |
| SWADBN - PF | +0.0070 | +0.0050 / +0.0062 / +0.0083 / +0.0071 | 24 | +0.0180 PASS | +0.0119 / **+0.0047** / +0.0342 / +0.0188 |
| C3X - PF | +0.0154 PASS | +0.0149 / +0.0151 / +0.0128 / +0.0161 (all PASS) | 31 | +0.0099 | +0.0086 / +0.0065 / +0.0071 / +0.0104 |
- relF1@2 gains survive label version, label errors and line-width conventions (at most -0.003 shift); the strict-IoU gains of HOUSE
  and SWAD do not survive a change of line-width convention.
- Absolute levels move by 0.02 to 0.18 with the label release, the convention and the label errors: no absolute crack or inactive
  level from this dataset should be compared with another dataset or release.
- Inactive: every inactive contrast so far has an interval of about +-0.05 to +-0.06, the same size as the candidate band (+0.069).
- The crack contrasts that pass rest on 17 to 31 module groups of 125, and HOUSE's relF1@2 edge on 4.

## 3. Solid vs suggestive
- Solid (E, mechanical, reproduced): F1, F3, F6, F7 width and vocabulary, F8, F9, error decomposition of F2, candidate counts of
  F4 / F5 and their replication.
- Suggestive: F2 ceiling (one double annotation); that candidates are label errors (model-defined; 30 panels seen by one non-expert:
  10 label error likely, 7 convention, 11 ambiguous, 1 model error, 1 unverifiable); F8 as a shortcut actually used.

## 4. Files
`PLAN.md`; `out/MD5.txt` (all tables and scripts); `out/a_candidates.tsv` (every candidate, ranked), `out/a_cells.tsv` (per-cell
softmin ranking), `out/a_summary.txt`, `out/a_visual_check.tsv`; `out/contrasts.txt` / `.json` (levels, contrasts, fragility, n_eff,
error decomposition); `out/labels_audit.txt`, `out/labels_percell.tsv`; `out/image_audit.txt`, `out/image_features.tsv`,
`out/dup_hash_pairs.tsv`; `out/crop_and_double.txt`; gallery (local only) `out/gallery/sheet_00..09.png`, `index.tsv`,
`check_centre_cell.png`; consensus maps `cache/cons/` (re-creatable, 5.6 MB); `out/pass_records.pkl`. Scripts in `scripts/`
(`consensus_pass.py` first, then `contrasts.py`, `candidates.py`, `gallery.py`, `labels_audit.py`, `image_audit.py`,
`crop_and_double.py`), run with `nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python -I`.

## 5. What would need GPU time, new data or a user decision
- GPU (about 10 to 25 GPU-hours): (a) recall of the label-error detector by planting known errors (drop or shift 10% of crack
  components in the training folds of PF, 1 seed x 5 folds) and counting how many come back as candidates; (b) a "cleaned labels"
  arm, PF trained with candidate px ignored, to measure how much label noise costs held-out scores rather than levels;
  (c) centre-cell-only training and scoring, to measure the window effect of F3 on a model rather than on a consensus.
- New data: a true ceiling needs a second, independent annotation of a few dozen pool cells (the dataset has one); the E-SCDD `_rf`
  cells (Hanifi labels, dev sets F51 / H36) could give a cross-annotator convention comparison without new labelling.
- User decisions: (1) whether strict crack IoU stays on the headline card or is printed only with its convention band (F1);
  (2) whether "cell" in the benchmark means the window or the centre cell, which changes the crack-free guard, inactive area and any
  severity use (F3); (3) whether the 18 spurious-inactive cells (CSIR-heavy) are reported with and without, as the noisy-cell rule
  does (F4); (4) whether a 2 to 3 h expert look at the 49 cells with an image-supported candidate is acceptable (no relabelling;
  confirm or reject only), which would turn F4 / F5 from suggestive to measured.
