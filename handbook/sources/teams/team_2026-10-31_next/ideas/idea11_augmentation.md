# Idea 11: appearance augmentation for unseen panels

Author: `domain`, 31 Oct 2026. Tags: E measured (file), R literature (Research MCP id), S judgement. CPU only.
- **E1 use:** E1 images enter §2 as descriptive coverage statistics only (allowed read, labelled descriptive). No augmentation range below is set from E1; ranges come from train / pool / Hanifi spreads.
- **Test:** no test image was read.
- **calib's intensity stats** (gaint `calib_intensity.py`) were queued but not out when this was written. The numbers below are from my `dom_appearance.py` (same PIL `L` conversion as the loader), cross-checked against judge's `judge/out/intensity_stats.tsv`.
- **Outputs:** `ideas/domain_out/ap_local.tsv`, `ap_pool.tsv`.

## 0. Verdict (proposed): no standalone arm (DROP as an arm)
- **Covered already:** the house augmentation covers E1's brightness and contrast range.
- **Gaps not covered:** histogram shape (sparse dark features on a uniform bright cell), half-cut geometry and scale, 9-busbar layout, the letterbox frame.
- **Where the gaps go:**
  - geometry → idea 5 (its simulator includes intensity matching);
  - histogram shape → idea 2's test-time histogram mapping (calib, `cellhist`). A training-time gamma covers only a little of it (§2.3).
- **What remains as cheap generic aug:** gamma, blur, noise, busbar-count variation. Expected E1 effect ≤ +0.01 crack recall: E1's failure is concept coverage (scuff + half-cut), not photometry (§3).

## 1. What the house augmentation does (E, gaint `el_f3` at e544133)
- **Recipe used by protocol_100, PF2 and BEST:** `data.augmentation=labelsafe` (`el_f3/reports/f100_queue.sh` base string; `scripts/train.py` l.424-436 → `get_labelsafe_augmentation`).
- **`get_labelsafe_augmentation`** (`src/data/augmentations.py`; Albumentations 2.0.8 on gaint), in order:
  1. `A.Resize(512, 512)` (identity for 512 inputs; squashes anything else);
  2. `HorizontalFlip(p 0.5)`, `VerticalFlip(p 0.5)`, `RandomRotate90(p 0.5)`: exact pixel permutations, 8 dihedral poses;
  3. `RandomBrightnessContrast(brightness_limit ±0.2, contrast_limit ±0.2, p 0.4)`. Verified on gaint: `brightness_by_max=True`, `ensure_safe_range=False`. So I' = α·I + β·255 with α ∈ [0.8, 1.2], β ∈ [−0.2, 0.2], clipped; applied to 40% of samples;
  4. `Normalize(mean 0.5, std 0.25, max 255)`: a fixed global map, no per-image normalisation; `ToTensorV2`.
- **Not in the house recipe:**
  - in `strong` (old era) but dropped in P6 as crack-erasing: ±5° rotation, Gaussian blur 3-7 px, Gaussian noise σ 3.2-7.1;
  - never used: gamma, CLAHE / histogram equalisation, scale or aspect change, elastic, cutout, letterbox / white padding, synthetic busbars.
  - P6 rationale: `protocols/P6_corrected_baseline.md`; handbook 03 §10, 14 §2.4. The old noise bug that erased cracks: handbook 03 §10.

## 2. E1-vs-train gaps and what the house augmentation covers (E; E1 descriptive)
### 2.1 Statistics
Content = non-white rows/cols and not padding class 7. The house jitter can move mean and sd. It cannot move these ratios, which a linear map leaves unchanged:
- shape = (p50 − p5)/(p95 − p5), a histogram-shape / gamma proxy;
- sharp = mean |Laplacian| / sd, sharpness relative to contrast;
- noise = 1.4826 MAD(I − median5 I) / sd.

| Group | n | mean | sd | shape | sharp | noise |
|---|---|---|---|---|---|---|
| train (all) | 478 | 138 [98-174] | 36.7 [19-51] | 0.694 [0.57-0.79] | 0.171 [0.09-0.49] | 0.044 [0-0.16] |
| val | 54 | 134 [94-174] | 37.1 [23-51] | 0.685 [0.55-0.78] | 0.146 [0.09-0.44] | 0.043 [0.03-0.15] |
| pool half-cells | 1,008 | 154 [133-167] | 23.7 [17.5-34] | 0.786 [0.72-0.84] | 0.115 [0.08-0.14] | 0 [0-0.06] |
| Hanifi half-cut | 43 | 156 [130-167] | 22.7 [18-35] | 0.783 [0.70-0.84] | 0.102 [0.07-0.12] | 0 [0-0.07] |
| Hanifi full | 74 | 126 [86-161] | 31.3 [16-46] | 0.740 [0.59-0.86] | 0.194 [0.10-0.41] | 0.052 [0-0.18] |
| E1 half-cut (descriptive) | 58 | 140 [99-164] | 25.8 [13-51] | **0.840 [0.77-0.88]** | 0.146 [0.09-0.24] | 0.056 [0-0.11] |
| E1 full (descriptive) | 48 | 162 [71-190] | 32.7 [16-42] | 0.619 [0.50-0.84] | 0.188 [0.07-0.26] | 0.044 [0.02-0.09] |

(median [p10-p90])

### 2.2 Share of cells outside the train envelope
- mean/sd: unreachable from any train cell under α ∈ [0.8, 1.2], β ∈ ±51 grey levels (5% slack).
- Invariant ratios: outside train p2.5-p97.5.

| Group | mean/sd unreachable | shape outside | sharp outside | noise outside |
|---|---|---|---|---|
| val | 0.00 | 0.06 | 0.04 | 0.00 |
| pool half-cells | 0.00 | 0.13 | 0.03 | 0.00 |
| Hanifi half-cut | 0.00 | 0.12 | 0.12 | 0.00 |
| E1 half-cut (descriptive) | 0.00 | **0.60** | 0.05 | 0.00 |
| E1 full (descriptive) | 0.04 | 0.27 | 0.10 | 0.00 |

### 2.3 Findings
1. **Brightness/contrast is covered (E).** E1 content mean/sd is reachable for 96-100% of cells.
   - The often-quoted "E1 is brighter" (median mean 190, `pool_large_audit` §3.3) is the white letterbox. On non-padding px, E1 mean is 137.3 vs train 136.5, with padding fraction 0.40 vs 0.17 (judge's table, independent code). Relevant to idea 2's premise (calib told).
   - The house jitter fires on only 40% of samples, uniform. S: a wider or always-on jitter is not indicated by these numbers.
2. **Histogram shape is the photometric gap (E).** 60% of E1 half-cuts lie above train's p97.5 (0.84 vs ≤ 0.83): a bright uniform cell with sparse dark features. Pool and Hanifi half-cells show the same shift, milder (0.79, 12-13% outside).
   - A training-time gamma covers only part of it: γ 0.7 / 0.5 moves 5% / 11% of train cells to shape ≥ 0.84 (my check on the 478 train cells). The shift is mostly content (few busbars, sparse dislocation clusters), not tone curve (S).
   - Test-time histogram matching (calib's `cellhist` dump, idea 2) targets it directly.
3. **Sharpness and noise are covered (E).** E1 lies within train's range for 90-95% (sharp) and 100% (noise). Blur or noise augmentation is not indicated, and both erase thin cracks (P6).
4. **Geometry is the large gap, outside photometric augmentation (E, idea 5 §1.2):**
   - half-cell scale x × 1.34, row pitch 163 vs 256;
   - 9 busbars (period 36-39 px) vs 2-5 (50-85 px);
   - E1's letterboxed strip frame (27 Oct F6, descriptive), which is absent in all non-E1 half-cuts.
   - Scale, aspect and gap are handled by idea 5's simulator, which costs FINAL 0.14 crack recall on val cells (idea 5 §1.5). The busbar count is not handled by anything yet.
5. **Crack width.** E1 cracks are ~1.5x wider than train (judge 31 Oct log, idea 6 review; 27 Oct `eval.md`). This follows from the half-cell scale (× 1.3) and is produced by idea 5's rescale (train multi crack width 1.79 → 2.42 synthetic; val 2.61 → 3.22 in the V-series; idea 5 §1.2).

### 2.4 calib's idea-2 result (31 Oct, `ideas/idea02_intensity.md`; E, E1 descriptive)
- **Content brightness:** E1 = train (AUROC 0.52). My letterbox finding is reproduced: 55/58 E1 half-cuts are letterboxed, against 0 in train / val / test / `_rf` / pool.
- **Test-time mapping into the train content distribution** (per-cell affine, per-module affine, histogram matching; content px only; FINAL + SUPPF5 seeds):
  - val relF1@2 drops 0.02-0.06; F51 changes −0.03 to +0.016; E1 lower everywhere (descriptive).
  - Histogram matching, which targets the shape gap of §2.3, is the worst (val relR −0.10).
  - **Reading (S, calib's and mine):** the models use absolute grey level as a cue, so remapping test images hurts. This says nothing against a shape-changing augmentation at training time, which stays open.
- **E1 per-cell crack recall** vs content brightness rho −0.03; vs crack faintness −0.06; vs content fraction (frame) +0.37, confounded with half-cut + scuff.

## 3. Expected effect (S)
- **Generic photometric additions** (gamma γ ∈ [0.7, 1.4], always-on ±0.2 jitter):
  - test n.d.; E1 crack recall 0 to +0.01;
  - rationale: brightness/contrast/sharpness are already in range, and the failure population (scuff + half-cut) is a content gap. PF's E1 gain came from preserved features, not appearance.
- **Busbar-count variation** (drawing thin dark lines labelled busbar, class 9): could address the 9-busbar mismatch.
  - Risk: synthetic straight lines with a busbar label teach "thin straight dark line = not crack", which hurts axis-parallel cracks (idea 4 §1.5).
  - Unmeasured; S: low value, real risk.
- **Letterbox / white padding as augmentation** (calib suggests it, with contrast/shape jitter):
  - The frame cue exists only in E1 (55/58 half-cuts, 0 elsewhere). Under the user's policy (E1 = second test set, never for selection), an augmentation built to imitate E1's frame is E1-informed design.
  - If it is run, it must be justified and parameterised generically: random white margins of 0-35% per side, as already present in train BMRK/SDLE squares and ARTS/CFVS side pads. Its E1 effect is then a pre-registered test-set readout, never a choice.
  - Expected value is still small: letterboxed half-cuts without scuff already score 0.552 (judge j6, descriptive), and the frame correlation (+0.37) is confounded with half-cut + scuff.
- **Contrast / histogram-shape jitter at training time** (e.g. random gamma 0.5-2 plus local contrast stretch):
  - It covers ≤ 11% of the shape gap by itself (§2.3), but it would teach shape invariance, which test-time mapping cannot (§2.4).
  - Option for a later low-priority arm (one change), judged on val + F51, with E1 descriptive or co-primary.
- **Neither option changes the verdict:** the kill rule (§6) is still not met on non-E1 data (shape outside: pool 13%, Hanifi 12%).

## 4. Prior tries in the repo
- `strong` augmentation (old era, blur + noise + ±5°), replaced by `labelsafe` in P6 because blur and noise erase cracks; a pre-fix GaussNoise bug invalidated old results (handbook 03 §10, 14 §2.4).
- P7 student photometric (±0.25, p 0.8, noise p 0.3) on unlabelled images only (handbook 14 §2.4).
- 27 Oct `ideas.md` rank 5 V1 (white letterbox → grey at inference) and V2 (rescale): not run.
- Track M R5 (2× input resolution): n.d. (idea 6 review).

## 5. Literature (R)
- Zhang et al. 2020, doi:10.1109/tmi.2020.2973595 (BigAug): stacked appearance + spatial transforms for unseen-domain segmentation. Gains came where the shift is acquisition (scanner, contrast). Here the measured photometric shift is already inside the house range (§2.2).
- Su et al. 2023, doi:10.1609/aaai.v37i2.25332: global plus location-scale (local) augmentation for single-source domain generalisation in segmentation. The local variant is the closest analogue to a histogram-shape change.
- Schwonberg et al. 2023, doi:10.1109/iv55152.2023.10186752: augmentation-based domain generalisation for segmentation. Photometric randomisation helps, but its gains depend on the shift type.
- Lu et al. 2026, doi:10.1016/j.enconman.2026.121958: EL cross-domain drift attributed to cell type, injection current and imaging. Cell type is our dominant factor here (half-cut), which augmentation does not create.

## 6. Kill criterion (applied)
Do not run a standalone appearance arm unless ≥ 25% of a non-E1 shifted group (pool or Hanifi half-cells) is outside the house envelope on a jitter-movable statistic, or on a ratio that the proposed augmentation actually covers. Observed:
- mean/sd 0%;
- shape 12-13%, of which gamma covers ≤ 11% of train;
- sharp 3-12%.
The criterion is not met, so no arm.

## 7. What to do instead (S)
- Put geometry and intensity matching into idea 5's arm (already specified there).
- Leave histogram-shape handling to idea 2's test-time mapping (calib), judged on val / Hanifi, E1 descriptive.
- Revisit busbar-count variation only after idea 5's arm reports. If HC passes but half-cut errors cluster on busbars, test a 9-busbar overlay as its own arm.

## 8. Reproduction (scripts, md5, per-cell outputs)

| Step | Script (md5) | Output |
|---|---|---|
| house augmentation | read from gaint `el_f3` `src/data/augmentations.py`, `scripts/train.py` l.424-436 at e544133; Albumentations 2.0.8 defaults checked in a python one-liner on gaint | §1 |
| appearance ratios | `dom_appearance.py` (725514ea) | per image: `domain_out/ap_local.tsv` (train/val/Hanifi/E1 descriptive), `ap_pool.tsv` (1,008 pool half-cells), `ap_shv1.tsv` (SHV1) |
| coverage table | `dom_ap_summary.py` (606c4505) | stdout (§2.1-2.2) |
| gamma check | inline in the session (γ 0.5 / 0.7 / 1.5 on the 478 train cells; shape ≥ 0.84 share 0.11 / 0.05 / 0.01) | §2.3 |
| cross-check | judge's `judge/out/intensity_stats.tsv` (non-padding mean 137.3 E1 vs 136.5 train) | §2.3 |

---

## judge verdict (31 Oct 2026, 14:53 IST from date; report md5 7891cac1 as reviewed)

**Verdict: no standalone appearance arm (DROP as an arm). Agreed.** Geometry goes to idea 5, histogram shape to idea 2's test-time mapping, and the busbar overlay is revisited only after idea 5.

### What I reproduced (E)
- **House augmentation** = labelsafe: flips, rot90, B/C ±0.2 at p 0.4 (handbook 14 §2.4). It matches what I had.
- **"E1 brighter" is the letterbox** (from my `judge/out/intensity_stats.tsv`, non-padding px):
  - mean of cell means: E1 137.3 vs train 136.5;
  - padding fraction: 0.40 vs 0.17.
  - **Exact.**
- **Histogram-shape gap**, recomputed with my own content definition (class 7 excluded, letterbox rows kept), shape = (p50 − p5) / (p95 − p5):
  - E1 half-cut median 0.840, **60%** outside train p2.5 to p97.5 (train p97.5 0.832);
  - E1 full 25% (domain 27%);
  - val 6%.
  - **Match.**
- The kill criterion (≥ 25% of a **non-E1** shifted group outside the envelope) was applied to pool/Hanifi, not to E1. Correct use: E1 descriptive only.

### Notes
- Expected effect ≤ +0.01 E1 recall for generic photometrics (S). Agreed: E1 contrast and sharpness are already in range, and P1/P6 showed blur and noise hurt thin cracks.
- Idea 2 (calib) should take the histogram-shape gap as its premise. Judge it on val + `_rf` F51, E1 descriptive.

**Tags:** E (two claims reproduced); R (4 ids not re-resolved, no arm); S.
