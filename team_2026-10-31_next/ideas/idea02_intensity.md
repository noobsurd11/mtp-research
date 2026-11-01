# Idea 2: per-module intensity normalisation (premise check)

calib, 31 Oct 2026, v1. Tags: E measured (file path), R literature (Research MCP id), S judgement.
- **E1 is a second test set** (user, 31 Oct): every E1 number here is DESCRIPTIVE and chooses nothing.
- The go/no-go read uses val and Hanifi `_rf` F51 only.
- Test images were read for image statistics only (no labels, no predictions).

## Verdict (S, from E below): NO-GO for a normalisation arm
1. **The premise "E1 is brighter" is a frame artefact.** On content px, E1's brightness matches train: median 143 vs 138, AUROC 0.52.
   - The whole-image gap (median 194 vs 158, AUROC 0.71) is the white letterbox around 55 of 58 E1 half-cuts, which no train cell has (domain found this first; reproduced).
2. **Brightness is module-level, as Om expected (89% of the pool's between-cell variance), but train already spans it.**
   - Train covers a between-module sd of 28 grey levels.
   - The house jitter reaches 98% of E1 cells in content mean and sd.
3. **Where E1 differs:**
   - lower content contrast (sd 27 vs 37);
   - fewer dark lines across the cell (9 vs 11 columns: busbar/cut layout);
   - the frame.
   - But Hanifi `_rf` differs from train just as much (multivariate AUROC 0.81 vs E1's 0.78), and the models do well on its unseen-module full cells (F51 relF1@2 0.84-0.86, near val).
   - So separation in intensity space does not predict failure.
4. **Within E1, crack-cell recall does not follow brightness** (Spearman −0.03).
   - E1 cracks are fainter than train cracks: relative darkness 0.071 vs 0.135, from the 27 Oct table. But faintness does not predict recall either (Spearman −0.06).
   - Recall follows the stratum: half-cut without scuff 0.86 vs half-cut + scuff 0.16 at similar brightness.
5. **Direct test: mapping each cell into the train intensity distribution at test time never helps, and usually hurts.** Three mappings (per-cell affine, per-module affine, per-cell histogram matching, content px only), applied to FINAL and the SUP100-PF seeds:
   - lower val relF1@2 by 0.02-0.06;
   - change `_rf` F51 by −0.03 to +0.016;
   - lower E1 relF1@2 in every stratum (descriptive). Histogram matching, which targets the one gap the jitter cannot reach (histogram shape, domain), is the worst.
   - All three fail the pre-stated GO rule.
6. **Caveat (S):** a test-time mapping on models trained without it is a weaker test than training with the normalisation.
   - But points 1-4 leave no premise for such an arm, and its expected gain is small or negative.
   - A CLAHE / local-contrast arm is the one variant this does not test. It belongs with idea 11 (appearance augmentation, domain) as one of its options, not as its own arm.

## 1. What the house pipeline already does (E, gaint `el_f3` e544133)
- **Loader** (`src/data/benchmark_el.py:110`): `PIL.Image.open(...).convert("L")`, uint8.
- **Normalisation** (`configs/base.yaml` data.mean 0.5 / std 0.25; `A.Normalize(..., max_pixel_value=255)` in every pipeline, `src/data/augmentations.py`): one fixed global affine, (x/255 − 0.5)/0.25.
  - No per-image, per-module, histogram or CLAHE step; grep for CLAHE / Equalize / gamma finds nothing.
- **Training augmentation** (`get_labelsafe_augmentation`, `data.augmentation: labelsafe` in the f3 configs):
  - flips and 90° rotations;
  - `RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.4)`: out = α·x + β·255, α ∈ [0.8, 1.2], β ∈ [−0.2, 0.2];
  - no gamma, blur or noise (dropped in P6 to protect 1-2 px cracks).
- **SSL strong view** (not used at 100%): ±0.25 at p 0.8 + Gaussian noise.

## 2. Premise check (E)
**Run:**
- `scripts/calib_intensity.py` (64f7b70b), gaint CPU, 1 thread, nice 19, 14:41-14:56 IST.
- 12,732 cells: train 478, val 54, test 50 (images only), E1 106, `_rf` 106, pool 11,938.
- Content px = the F6 letterbox rule (rows/columns with ≥ 98% px ≥ 250 are frame), plus GT ≠ 7/255 where a mask exists.
- Per cell: content mean, sd, percentiles, robust contrast, noise, dark-line counts on the row and column profiles, content fraction, letterbox flag.
- Output: `calib_out/intensity.tsv` (47d71e77); train content reference `calib_out/train_ref.npz` (8a702b81: mean 138.2, sd 49.1, 256-bin cdf).
- Analysis: `scripts/idea2_analysis.py` (c64e7bd1) → `calib_out/idea2_summary.txt` (78b3e026). Figure `figs/idea2_intensity.png`.

### 2.1 Medians per set (content px)
| set | content mean | content sd | robust contrast | dark columns | content fraction | letterbox | whole-image mean |
|---|---|---|---|---|---|---|---|
| train 478 | 137.9 | 36.7 | 0.9 | 11 | 0.9 | 0% | 158.4 |
| val 54 | 133.6 | 37.1 | 0.9 | 11 | 0.9 | 0% | 162.9 |
| test 50 (image only) | 142.8 | 37.3 | 0.9 | 11 | 1.0 | 0% | 167.1 |
| E1 106 | 143.0 | 26.7 | 0.7 | 9 | 0.5 | 52% (55 of 58 half-cuts) | 193.5 |
| `_rf` 106 | 132.1 | 27.1 | 0.6 | 8 | 1.0 | 0% | 148.8 |
| pool 11,938 | 130.0 | 22.8 | 0.5 | 10 | 1.0 | 0% | 144.5 |

**E1 strata, content mean / sd:**
- full 40: 167.5 / 34.2;
- full + scuff 8: 83.6 / 17.1 (darker than ~97% of train);
- half-cut 29: 137.7 / 22.0, letterbox 93%;
- half-cut + scuff 29: 141.0 / 37.2, letterbox 97%.

### 2.2 Separation from train (AUROC; 0.5 = same)
| set | content mean | content sd | contrast | dark columns | content fraction | whole-image mean | multivariate (leave-one-module-out logistic) |
|---|---|---|---|---|---|---|---|
| val | 0.48 | 0.53 | 0.57 | 0.51 | 0.47 | 0.52 | 0.48 |
| test (in-domain reference) | 0.50 | 0.52 | 0.54 | 0.48 | 0.50 | 0.56 | 0.60 |
| **E1** | **0.52** | 0.35 | 0.30 | 0.26 | 0.31 | **0.71** | 0.78 |
| `_rf` | 0.47 | 0.30 | 0.34 | 0.32 | 0.57 | 0.37 | 0.81 (F51: 0.76) |

- E1 vs train with brightness only (content mean, p50): 0.31, i.e. no brightness signal.
- E1 vs train with contrast / noise only: 0.73. With frame / structure only (content fraction, dark rows and columns): 0.73.
- E1 full cells only: 0.78, brightness only 0.50.

### 2.3 Augmentation reach and module structure
**Share of cells whose content (mean, sd) is reachable from some train cell under the house jitter:**
- val 1.00, test 1.00, E1 0.98, `_rf` 1.00, pool 0.997.

**Inside train's [p1, p99] of both mean and sd:**
- val 1.00, test 0.96, E1 0.93, `_rf` 0.94, pool 0.84.

**Between-module share of cell-mean variance:**

| set | modules | share | within-module sd | between-module sd |
|---|---|---|---|---|
| pool (≥ 5 cells/module) | 284 | 0.89 | 11.5 | 38.2 |
| train (≥ 2 cells/module) | 100 | 0.87 | 10.6 | 27.7 |
| E1 | 17 | 0.98 | 6.6 | 43.2 |
| `_rf` | 22 | 0.67 | 14.8 | 22.1 |

- **Reading:** brightness is a module property, as Om expected. Train already contains modules across that range, and the jitter fills the gaps.

### 2.4 Link to the failure (FINAL at +0.75, crack cells ≥ 20 px)
- **Spearman of per-cell relR@2 with content mean:** val +0.36 (n 23); E1 −0.03 (n 32).
- **E1 relR@2 with content sd:** −0.36; with content fraction: +0.37. Both are confounded by the half-cut frame.
- **Strata at similar brightness:** E1 half-cut no-scuff crack cells median relR@2 0.86 (n 6, content mean 136); half-cut + scuff 0.16 (n 20, content mean 146).
- **Crack faintness** (27 Oct `team_2026-10-27_unlabelled/ideas_scripts/e1_shift.csv`, train and E1 rows only):
  - relative crack darkness vs a ring 3-8 px away: train 0.135, E1 0.071; only 12% of train crack cells are as faint.
  - Within E1, Spearman with recall is −0.06.
  - So E1 cracks are fainter, but faintness is not what separates found from missed.

## 3. Direct test: test-time intensity mapping (E)
**Rule pre-stated** in `scripts/idea2_tt.py`'s docstring before any of its numbers:
- md5 f568a67a at 14:50 IST, amended before any number was read: the E1 branch was dropped after the user's E1 decision; current md5 e4b5b69d.
- GO needs a variant that, for both FINAL and the SUP100-PF seed mean:
  - does not lower val relF1@2 at OP-rel by more than 0.01, AND
  - raises `_rf` F51 relF1@2 at OP-rel by ≥ 0.02.

**Variants:** `calib_dump.py --tt` (c172717e), content px only, frame untouched.
- cellz: per-cell affine to the train content mean / sd;
- modz: per-module affine; E1 modules have 1-2 cells, so it is close to cellz there;
- cellhist: per-cell histogram matching to the pooled train content histogram, which fixes shape, domain's gap.
- The OP-rel b is re-chosen on each variant's own val.
- Records: `calib_out/rec_tt/` (MANIFEST 1c55a2d5). Output `calib_out/idea2_tt.txt` (c474d806).

**relF1@2 at the val-chosen OP-rel (Δ vs no mapping); SUP100-PF = mean of 5 seeds:**

| model | set | none | cellz | modz | cellhist |
|---|---|---|---|---|---|
| FINAL | val | 0.897 | −0.025 | −0.025 | −0.059 |
| | `_rf` F51 | 0.855 | +0.006 | +0.005 | −0.017 |
| | E1 (descr.) | 0.436 | −0.035 | −0.021 | −0.080 |
| | E1 sh29 oracle relF1 (descr.) | 0.490 | −0.001 | +0.003 | −0.059 |
| SUP100-PF | val | 0.888 | −0.019 | −0.019 | −0.056 |
| | `_rf` F51 | 0.811 | +0.016 | +0.016 | −0.028 |
| | E1 (descr.) | 0.450 | −0.029 | −0.023 | −0.096 |
| | E1 sh29 oracle relF1 (descr.) | 0.447 | −0.028 | −0.026 | −0.109 |

- **All three: NO-GO** (val loss > 0.01 for both models, and the F51 gain < 0.02).
- Mappings mostly move recall down and precision up: the models use absolute grey level as a cue. Histogram matching costs val relR@2 0.10-0.11.
- On `_rf`, cellz / modz nudge F51 precision up (+0.02-0.04) at a small recall cost. Within noise (SUP100-PF F51 sd 0.06).

## 4. Prior tries in the repo
- **27 Oct `ideas_scripts/e1_shift.py` and critique J0.7:** "E1 CSIR brighter (180 vs 135), higher contrast (sd 57.7 vs 37.4), fainter cracks (9 vs 16), wider labels (3.6 vs 2.5 px)", measured on the central 80% of the image, frame included. The brightness part is the letterbox (§2.1); fainter cracks and wider labels stand (judge's 1.5x width, PF2 §3b).
- **Handbook 03 §6 / judge 27 Oct:** pool CSIR brightness matches labelled CSIR (141 vs 142).
- **Domain, 31 Oct** (`ideas/domain_out/ap_local.tsv`, `scripts/dom_appearance.py`): E1 content mean / sd within the house jitter for 96-100% of cells; histogram-shape statistic E1 half-cuts 0.84 vs train 0.69. Consistent with §2.3; §3 tests the shape gap directly.
- No run has trained with per-image or per-module normalisation or CLAHE. P6 dropped blur / noise from the augmentation; brightness / contrast jitter has been on since P6.

## 5. Literature (R)
- Deitsch et al. (doi:10.1007/s00138-021-01191-9): EL images are "uncalibrated". Module-level acquisition varies, and their cell segmentation uses robust preprocessing. That supports the module-level brightness premise, confirmed in §2.3.
- Stain normalisation at train and test time improves cross-site nuclei segmentation (doi:10.1016/j.csbj.2023.12.042). That works where the shift is low-level appearance; here the low-level appearance of E1 content is within train's range (§2).
- Domain-generalisation review (doi:10.1109/jproc.2024.3507831): appearance normalisation / augmentation are the cheapest DG levers. They help for appearance shift, not for content or geometry shift. E1's shift is the frame, cut-cell layout and scuff context (geometry / content).

## 6. Cost, expected effect, kill, protocol
- **Spent:** ~1.1 CPU-h on gaint (intensity 15 min; three mapping dumps 42 min; records 8 min).
- **A normalisation training arm would cost** ~12.5 GPU-h (5 seeds, gaint) plus a protocol.
- **Expected E1 effect (S):** ≤ 0. There is no brightness gap, brightness does not track per-cell recall, and test-time mapping hurts everywhere.
- **Kill:** met (pre-stated GO rule failed for all three variants). **DROP.**
- **What to do instead (S):**
  - Fold "contrast / histogram-shape jitter" and "letterbox / frame jitter" into idea 11 (domain), as augmentations rather than a normalisation.
  - The frame is the only appearance feature that is both E1-specific and absent from train. Synthetic half-cuts with a frame (idea 5) cover it.

## 7. Files (md5, first 8)
| file | md5 |
|---|---|
| `scripts/calib_intensity.py` | 64f7b70b |
| `scripts/idea2_analysis.py` | c64e7bd1 |
| `scripts/idea2_tt.py` (amended before reading) | e4b5b69d |
| `scripts/calib_dump.py` (`--tt`) | c172717e |
| `calib_out/intensity.tsv` (12,732 cells, per-cell stats) | 47d71e77 |
| `calib_out/train_ref.npz` | 8a702b81 |
| `calib_out/idea2_summary.txt` | 78b3e026 |
| `calib_out/idea2_tt.txt` | c474d806 |
| `calib_out/rec_tt/MANIFEST.md5` (90 per-cell record files) | 1c55a2d5 |
| `figs/idea2_intensity.png` | b4271b52 |

---

## judge verdict (31 Oct 2026, 17:36 IST from date; report md5 72b5b8a6 as reviewed)

**Verdict: DROP (NO-GO for a normalisation arm). Agreed.**
- The premise is absent: content brightness matches train.
- Brightness does not track recall.
- The pre-stated test-time GO rule fails for all three mappings.

### What I reproduced (E)
Own code (`judge/idea2_recompute.py`, md5 b43b38ac).
- **(a/b) From my own intensity table** (`judge/out/intensity_stats.tsv`, non-padding px; written before calib's, different content rule):
  - E1 content mean median 143.0 vs train 138.0, AUROC 0.52;
  - content sd 26.7 vs 36.8, AUROC 0.35.
  - **Match.**
- **(d)** E1 crack cells (n = 32, FINAL +0.75, calib's records): Spearman of per-cell relR@2 with content mean −0.04 (calib −0.03). **Match.**
- **(e)** relF1@2 at each variant's own val-chosen OP-rel, from `calib_out/rec_tt/` (MANIFEST OK):

  | Model | Set | none | cellz | modz | cellhist |
  |---|---|---|---|---|---|
  | FINAL | val | 0.897 | 0.872 | 0.872 | 0.837 |
  | FINAL | F51 | 0.855 | 0.861 | 0.859 | 0.837 |
  | SUPPF5 (5-seed mean) | val | 0.888 | 0.869 | 0.869 | 0.832 |
  | SUPPF5 (5-seed mean) | F51 | 0.811 | 0.827 | 0.827 | 0.783 |

  **Match** (calib Δs within 0.001). Every variant loses more than 0.01 on val, and none gains 0.02 on F51 for both models. NO-GO.
- **Rule history checked against `log.md`:**
  - `idea2_tt.py` was written 14:47 (f568a67a) before any mapping number;
  - it was amended at 17:32 before reading, dropping the E1 branch after the user's E1 = test decision;
  - the report followed at 17:34.
  - The amendment is direction-neutral and moot: every variant fails on val first.

### Notes (S)
1. **E1 crack "faintness"** (0.071 vs 0.135 relative darkness, 27 Oct table) is measured over GT crack px. E1 crack labels are ~1.5x wider (area/skeleton 3.66 vs 2.41 px, `judge/crack_width.py`), so their mean darkness is diluted by edge px. Part of the "fainter" gap is a label-width artefact. It does not change the verdict: faintness does not predict recall either (−0.06).
2. **Test images.** calib read the 50 test images for appearance statistics only (no labels, no predictions). Disclosure, for symmetry: my own `intensity_stats.py` read the test images and test masks for class 7 (padding) only, to exclude padding px. No defect class or prediction was read. Both are descriptive and choose nothing.
3. **CLAHE / local contrast** is the one untested variant. idea 11 concluded "no appearance arm" on the measured gaps, so it stays untested. That is consistent with the evidence: E1's shift is frame, cut layout and scuff context, not tone.

### Tags
- E: (a), (b), (d), (e) reproduced.
- R: 3 ids not re-resolved (no arm depends on them).
- S: notes 1 and 3.
