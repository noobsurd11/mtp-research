# BenchmarkELimages `dataset_20211104`: first-hand data analysis

Date: 2026-10-08. Local analysis on the public clone (commit `768b5e7`), 478 train / 54 val / 50 test, all 512 × 512.
Scripts: `data_analysis/scripts/` (run with `python -I <script> <dataset dir> ...`). Raw outputs: `data_analysis/out/*.json`.
Figures: `data_analysis/figs/`. Convention: **measured** = computed here; **interpretation** = marked as such.

## 0. Verdict on the handoff's data facts

| Handoff claim | Here | Status |
|---|---|---|
| 478 / 54 / 50; crack 14, inactive 11; bg 69.2%, padding 17.3%, crack 0.186% of train pixels | same | confirmed |
| Crack pixels 232,914 / 27,873 / 70,626 | same | confirmed |
| All 50 test images contain crack; 41–43% in train/val | 205/478 = 42.9%, 22/54 = 40.7%, 50/50 | confirmed |
| Inactive in 34% of test vs ~9% elsewhere; always with crack in train | 17/50; 43/478, 5/54; inactive never occurs without crack in **any** split | confirmed (stronger) |
| 7 classes absent from val, 8 from test | same | confirmed |
| Sources ARTS 162, CFVS 146, CSIR 111, BMRK 42, SDLE 17 | same | confirmed |
| 20/54 val and 24/50 test from modules with train images | same (322 / 49 / 48 modules; 9 modules shared val↔test) | confirmed |
| "BenchmarkEL cracks are 2 to 3 px wide" | labels: median 1.75 px (IQR 1.25–2.5); CFVS/CSIR/ARTS ≈ 1.5–1.75, BMRK/SDLE ≈ 3 | **partly wrong**: most labels are 1–2 px |
| "Test cracks are bigger and easier" | per crack image: median 502 vs 476 px (similar), mean 1,413 vs 1,136; test cracks are **darker** (median relative darkness 0.187 vs 0.140) | "easier" supported via contrast; "bigger" only in the mean |

## 1. What the images and classes are (measured + visual, `figs/peek_sources.png`)

- Every image is a module crop: the central cell plus fragments of its neighbours. Cracks are labelled in the neighbour fragments as well.
- BMRK (and SDLE) cells are downscaled to roughly a quarter of the frame and surrounded by **padding** (class 7). That is why padding is 17% of train pixels.
- `sp multi` / `sp mono` are the dark spacing between cells; `ribbons` are the vertical interconnect ribbons; `gridline` (a defect class) marks short horizontal finger interruptions.
- Inactive regions are almost always bounded by cracks: 99% of inactive components touch a crack label within 3 px (train 440/445, val 18/18, test 51/52). Inside inactive regions the crack network is often also labelled as crack; 20% of train crack pixels (16% test) lie in or at inactive regions.
- Inactive never occurs in an image without a crack label (all splits). Test inactive regions are darker relative to their surroundings (median inside/ring intensity ratio 0.34) than train (0.55); 6% of train inactive area is barely darker than its surroundings (ratio > 0.8), none in val/test.

## 2. Crack geometry (measured, `out/geometry_ceiling.json`, `out/verify_dups_width.json`)

| | train | val | test |
|---|---|---|---|
| crack images | 205 | 22 | 50 |
| crack components (8-connected) | 3,589 | 269 | 1,570 |
| components < 20 px | 76% (3% of crack pixels) | 59% (2%) | 88% (5%) |
| label width, area/skeleton length, length-weighted (components ≥ 15 px skeleton) | 2.17 | 1.93 | 2.66 |
| local orientation (skeleton tangents): diagonal / parallel to ribbons (vertical) / horizontal | 62 / 34 / 4% | – | 66 / 28 / 7% |

Per-point profile measurement (9,302 skeleton points, unsmoothed, normal profiles): **label width median 1.75 px (IQR 1.25–2.5); visible dark-line FWHM median 4.0 px (IQR 3.0–4.75)**. In 77% of points the visible line is at least 1 px wider than its label.

| source | visible FWHM median | label width median |
|---|---:|---:|
| ARTS | 3.0 | 1.5 |
| BMRK | 5.0 | 3.0 |
| CFVS | 4.25 | 1.75 |
| CSIR | 3.5 | 1.75 |
| SDLE | 4.5 | 3.25 |

Label width depends on the source (annotation convention), not only on the crack: BMRK/SDLE labels are about twice as wide as CFVS/CSIR/ARTS labels.

`crack rbn edge` (class 10): 5 train components (104 px, width 1.9–4.2), 2 val, 4 test components 6.4–11.6 px wide. Not learnable as a class from this data.

## 3. How much strict IoU can a perfect-but-jittered crack prediction get? (measured, `out/geometry_ceiling.json`)

Dataset-level IoU between the ground truth and a perturbed copy of itself:

| perturbation | crack train | crack val | crack test | inactive test |
|---|---:|---:|---:|---:|
| shift 1 px (mean of 4 directions) | 0.503 | 0.469 | 0.559 | 0.943 |
| shift 1 px diagonal | 0.363 | 0.336 | 0.434 | 0.909 |
| dilate 1 px (3 × 3) | 0.427 | 0.408 | 0.461 | 0.897 |
| erode 1 px (cross) | 0.205 | 0.167 | 0.296 | 0.902 |
| shift 2 px | 0.276 | 0.254 | 0.336 | 0.891 |

Per-image **median** IoU (Pratt's convention) under a 1 px shift: **0.12** for crack (val 0.13, test 0.12). One-pixel-wide labels shifted by one pixel give zero overlap in many images.

## 4. Annotation consistency (the central finding)

### 4.1 Two annotations of the same image (measured, `out/duplicate_agreement.json`, `figs/duplicate_pairs_masks.png`)

The dataset contains two duplicate images with independent masks:

| pair | image identity | crack IoU between the two masks | crack tolerance-F1 at 1 / 2 / 3 px |
|---|---|---:|---|
| `train/CFVS_00015_r7_c4` = `train/CFVS_00016_r7_c4` | pixel-identical | **0.257** | 0.70 / 0.82 / 0.87 |
| `train/ARTS_00081_r5_c1` ≈ `test/ARTS_00020_r5_c1` | correlation 0.9999 (same cell, re-encoded) | **0.210** | 0.87 / 0.99 / 1.00 |

Same pairs, other classes: inactive IoU 0.64 (tolerance-F1 2 px 0.92), gridline 0.24–0.36, ribbons 0.44–0.52 (tolerance-F1 2 px 0.91–0.995).
Visually, the two annotations trace the same cracks about 1 px apart; in the CFVS pair one annotation also includes a crack segment the other omits.
**Caveat: n = 2 pairs.** This is an estimate of label agreement, not a measured inter-annotator study.

### 4.2 Where labels sit relative to the visible dark line (measured, `out/annotation_consistency.json`, `figs/crack_normal_profiles.png`)

At 61,176 skeleton points of crack components ≥ 15 px (96% have a visible dip > 3%), the darkest point along the normal (search ±4 px, image smoothed σ 0.7) lies:

| within | label skeleton | null: random background points |
|---|---:|---:|
| ±0.5 px | 27% | 5.5% |
| ±1 px | 48% | 11% |
| ±2 px | 64% | 21% |
| > 2 px | 36% | 79% |

- Labels are clearly on the cracks, but **half of the label points are more than 1 px from the darkest line.** ARTS is best (75% within 1 px), BMRK worst (38%).
- The label-centred mean profile has its minimum at 0 for most source/split groups, so there is no large systematic offset. There is a small consistent horizontal bias: the dark line is on average 0.2 px left of the crack label (profile method, all sources −0.09 to −0.47 px). Ribbons agree: the best horizontal shift of vertical ribbon labels has mean −0.37 px (left half) and −0.47 px (right half), with no left/right difference (no scale mismatch). Sub-pixel; cause unknown (rasterisation convention is one candidate).
- Median dip depth is 17.6% at the darkest point but only 10.7% at the label centre.

### 4.3 Contrast of labelled cracks (measured)

Crack components ≥ 10 px against a 2–4 px background ring: median relative darkness 0.148. 7.2% of components are < 2% darker than their surroundings (essentially invisible) and 4.9% are brighter. CSIR is worst: 16% of its components are < 2% darker; CSIR images also have the lowest contrast (median intensity sd 24 vs 34–48). Test cracks are darker (median 0.187) than train cracks (0.140).

### 4.4 Fragmented ("dotted") labels (measured + visual, `figs/inspect_fragments.png`)

In some images the crack label is a dotted or dashed trace along a continuous visible crack, or speckle inside inactive regions:
14 train, 3 val and 5 test images have ≥ 30% of their crack pixels in components ≤ 10 px (2.5%, 1.6% and 3.8% of crack pixels). Examples: `val/ARTS_00166_r12_c5`, `val/ARTS_00152_r12_c5`, `test/CSIR_00173_r4_c4`, `train/CFVS_00114_r8_c2` and `test/CFVS_00114_r6_c5` (same module in train and test). A model that predicts the continuous visible crack is scored as false positive on every gap.

### 4.5 Unlabelled cracks (visual)

- Clear case: `train/CSIR_00094_r16_c5` has two parallel, equally visible diagonal cracks; only one is labelled (`figs/inspect_closeups.png`).
- In `test/ARTS_00073_r4_c2` a visible dark crack-like line next to a labelled inactive region is not labelled (`figs/crack_overlays_1.png`, row 1).
- An automatic ridge-detector search (`figs/unlabelled_line_candidates.png`) found 331 non-axis-aligned dark-line candidates ≥ 30 px, ≥ 6 px away from any label (48 train, 2 val, 8 test images). On inspection most of the top 30 are dark spots, dislocation clusters and noise (notably the very noisy test image `test/CSIR_00070_r8_c4`). Only a few look like real unlabelled cracks. **No reliable rate of missed cracks can be given from this**; it would need manual review.

### 4.6 Overlays (visual, `figs/crack_overlays_1..4.png`, 24 images across splits and sources)

Labels follow visible cracks in every sample. Typical deviations: labels thinner than the visible line (CFVS, CSIR), thick labels (BMRK, SDLE), dashed labels (ARTS val), cracks traced as the boundary of a dark region (BMRK, inactive borders).

## 5. Near-duplicates and leakage (measured, `out/dups_fragments.json`, `out/verify_dups_width.json`)

- **Cross-split duplicate:** `train/ARTS_00081_r5_c1` ≈ `test/ARTS_00020_r5_c1` (same cell, different module IDs, MAD 2.4 grey levels, correlation 0.9999). The test copy has its own, different crack mask (IoU 0.21 to the train mask).
- Within-train duplicate: `CFVS_00015_r7_c4` = `CFVS_00016_r7_c4` (pixel-identical, different masks).
- The many other high-correlation pairs (BMRK, ARTS `r1_c6`) are different cells; their correlation comes from shared padding or frame. Their crack masks do not overlap.
- Module sharing: 20/54 val and 24/50 test images come from modules that also have train images; 9 modules are shared between val and test.
- Nearest-train correlation: 18 test and 23 val images have a train image with thumbnail correlation ≥ 0.95. Mostly structural similarity (same cell type), not duplicates.

## 6. Class weights and the operating point (measured, `out/inventory.json`)

Current rule: w = 1/√freq over present classes, capped at 10 × median, normalised to mean 1, zero for absent classes.

| labelled subset (seed 0) | n | w(bg) | w(crack) | crack : bg | p(crack) above which weighted CE prefers crack over bg | crack share of weighted loss | structural + bg share | zero-weight classes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 100% | 478 | 0.018 | 0.351 | 19.3 | 0.049 | 1.8% | 80% | 0 |
| 50% | 239 | 0.020 | 0.356 | 18.2 | 0.052 | 1.9% | 81% | 2 |
| 20% | 95 | 0.035 | 0.559 | 16.0 | 0.059 | 2.1% | 82% | 6 |
| 10% | 47 | 0.049 | 0.738 | 15.2 | 0.062 | 2.2% | 82% | 7 |
| 5% | 23 | 0.075 | 1.440 | 19.2 | 0.050 | 1.7% | 85% | 10 |
| 2% | 9 | 0.113 | 1.668 | 14.7 | 0.064 | 2.3% | 88% | 12 |

("Structural + bg" = background, padding, ribbons, border, spacing, frame edge.)
- The weighted loss tells the network to call a pixel crack once p(crack) > ≈ 0.05–0.06 against background.
- Crack still gets only about 2% of the total loss signal and inactive about 2%; padding alone gets 17–25%.
- The capped classes change with the subset (100%: clamp, crack rbn edge, rings, meas artifact; 2%: material). So the "same" loss is a different operating point at every label fraction.

## 7. What this means for training methodology (INTERPRETATION, not measured)

1. **Strict crack IoU on this dataset has a low and noisy ceiling.** Two annotations of the same image agree at crack IoU 0.21–0.26 (n = 2), and a perfect prediction shifted by 1 px scores about 0.5. Our models' test crack IoU of about 0.30 is already in the range where label jitter, not the model, dominates. Differences of ±0.03 in strict crack IoU between methods are not interpretable without a tolerance-aware metric (tolerance-F1 at 1–2 px, clDice, or relaxed IoU), and the Pratt-style per-image median is even worse (0.12 for a 1 px shift).
2. **The "cannot fit cracks on training images" result (P 0.33, R 0.95) is largely explained by the labels plus the loss.**
   - The visible crack is about 4 px wide where the label is about 1.75 px.
   - Labels sit up to 1–2 px off the darkest line and are sometimes dashed.
   - Weighted CE prefers crack once p > 0.05.
   - Together these predict exactly a model that covers the visible line: high recall, precision about 0.3–0.5.
   - What remains to be shown is whether a no-augmentation, unweighted CE run memorises the labels anyway (protocol P1). If it does not, the labels are not memorisable at pixel level, which is a property of the data.
3. **Thin, jittered, source-dependent labels argue for losses that are tolerant to 1–2 px misplacement:**
   - distance- or skeleton-based terms (clDice / skeleton recall);
   - boundary-tolerant Dice;
   - label smoothing across a 1–2 px band;
   - training targets dilated by 1 px, evaluated with a matching tolerance.

   Per-pixel weighted CE on 1 px labels rewards exact placement that the labels themselves do not have.
4. **Rare-class focus should be per defect type, not per class index.** Crack (thin, jittered) and inactive (blobby, consistent: shift-1 IoU 0.94, duplicate IoU 0.64 / tolerance-F1 0.92) have opposite label quality. One method treating them the same way will be noise-limited on crack and data-limited on inactive.
5. **Pseudo-labelling thin cracks inherits label jitter.** A teacher trained on jittered 1–2 px labels produces jittered pseudo-labels, and strict-IoU consistency on them is mostly noise. This is consistent with the handoff's 40–50% wrong pseudo-labels where defects are. An ALHVR-style method that routes low-confidence pixels should expect most crack pixels to be "ambiguous" for label reasons, not model reasons.
6. **The 24-class label set wastes most of the loss on structure.** Background plus structural classes take 80–88% of the weighted loss, and several defect classes are effectively unlearnable (crack rbn edge: 104 train px; rings, clamp, meas artifact under 1,300 px). A defect-focused head or a merged label set is worth testing (handoff option 9).
7. **Evaluation set issues to fix or report:**
   - one train↔test duplicate with a different mask;
   - module overlap between splits;
   - an all-crack test set with darker, more visible cracks and inactive regions than train;
   - fragmented test labels in 5 images.

   Reporting results on a module-disjoint split, or with cross-validation, alongside the official split would make conclusions sturdier.
