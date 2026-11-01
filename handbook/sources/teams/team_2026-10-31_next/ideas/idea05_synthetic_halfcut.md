# Idea 5: synthetic half-cut cells from labelled full cells

Author: `domain`, 31 Oct 2026 (v3, 18:30 IST; change log §10). Tags: E measured (file), R literature (Research MCP id), S judgement. CPU only (gaint CPU at nice 19 for the pool and the model-scoring passes).
- **E1 use:** no E1 number was computed for this report. E1 facts quoted are the existing descriptive ones (27 Oct `ideas.md` F1-F11, judge j6), labelled descriptive. The simulator was designed only from non-E1 data (Hanifi `_rf`, pool half-cells, train).
- **Test:** no test cell was read.
- **Scripts** (`ideas/scripts/`): `dom_halfcut_stats.py`, `dom_hs_summary.py`, `dom_synth_halfcut.py`, `dom_label_transfer.py`, `dom_synth_variants.py`, `dom_score_synvar.py`, `dom_rf_halfcut_baseline.py`, `dom_rf_fig.py`, `dom_scuff_morph.py`.
- **Outputs:** `ideas/domain_out/` and gaint `/home/noob/work/domain_scratch/out/`.
- **Figures:** `figs/idea05_synth_vs_real.png` (top: synthetic; middle: Hanifi half-cuts with GT; bottom: pool half-cells), `figs/idea05_rf_halfcut_final.png` (Hanifi half-cut crack cells: image | GT | FINAL).

## 0. Verdict: PASS-to-protocol, narrowed (judge: PASS with conditions 1-4, all applied in v2)
- **What it targets:** the geometric + intensity simulator reproduces a real, measured part of the half-cut drop. On val cells turned into half-cuts, FINAL loses 0.14 crack recall and 0.11 relR@2 (§1.5). That matches E1's half-cut-without-scuff recall of 0.552 (descriptive, judge j6).
- **What it does not target:**
  - It does not reproduce the large failure: scuff + half-cut, 75% of E1 crack px, recall 0.126 (descriptive). No non-E1 labelled example of that morphology exists to build a scuff simulator from without tuning on E1 (§1.7).
  - The 9-busbar layout and CSIR half-cell texture are not produced (§1.3).
- **Expected effect:** modest. E1 crack recall +0.01 to +0.03, mostly on the non-scuff half-cuts; inactive on half-cuts possibly more (§5).
- **Proposed arm:** one arm on SUP100-PF (§7). It needs the user's OK (not Om-approved). coach writes the protocol; §7 and §4 give the spec, md5s and data budget.
- **Readouts:**
  - test (expected n.d. by design: 0 half-cuts) and val, as house primaries;
  - **E1 co-primary slot**: the user decided on 31 Oct that E1 is a second test set, pre-registered, read once, never for selection;
  - **non-E1 mechanism readout on SHV1**, the frozen synthetic half-cut val set built from val (§1.8). Primary (v3, judge 31 Oct): **SHV1 relR@2 at relP@2 ≥ 0.90**. Baseline ~0.69-0.73 on SHV1 vs ~0.88-0.89 on V0 (calib's routing pre-check, reproduced by judge). The oracle-bias shift V0 → SHV1 is reported;
  - F51 (51 unseen-module `_rf` full cells) as the non-E1 not-worse guard.
  - H36 (Hanifi half-cut crack labels) is unusable for crack (judge ruling) and is for false alarms only.

## 1. Premise checks (E)
### 1.1 What the house loader expects (gaint `el_f3` `src/data/benchmark_el.py`, `augmentations.py`, commit e544133)
- Image: any PNG, converted to uint8 grey (PIL `L`), shape (H, W, 1).
- Mask: single-channel (L/P/I), values 0-23 only (else ValueError).
- **Every pipeline starts with `A.Resize(512, 512)`.** A non-square synthetic image would be squashed without warning. Synthetic cells must therefore be written at exactly 512 × 512.
- House augmentation (labelsafe): flips, rot90, brightness/contrast ±0.2 at p 0.4, normalise mean 0.5 / sd 0.25 (idea 11 §1).

### 1.2 Real half-cut appearance (non-E1)
Measured on the 1,008 pool half-cells (1,152 minus CSIR_00300) and the 43 Hanifi `_rf` half-cuts; train and val for contrast (`domain_out/hs_*.tsv`; median [IQR]).
- **Hygiene:** every simulator target (x pitch 342, row pitch 163, intensity 154 / 24) is taken from the 1,008 pool half-cells, which exclude E1's shared module CSIR_00300. The 43-cell Hanifi column includes the 7 CSIR_00300 cells and is shown for comparison only; it agrees with the pool. The scored Hanifi readout (§1.6) uses calib's hygiene set (36 half-cuts, CSIR_00300 dropped).

| Statistic | pool half (1,008) | Hanifi half (43) | train multi (165) | train mono (106) | synthetic, raw sim (162) | synthetic + intensity match (V4, val 108) |
|---|---|---|---|---|---|---|
| content (h × w) | 512 × 512 [473-512 w] | 512 × 512 | 512 × 512 | 512 × 512 | 480 × 512 (white rows; fixed in V-series) | 512 × 512 |
| cell pitch x (px) | 342 [341-343] | 342 [341-343] | 256 | 256 | 350 [333-367] (jitter ±8%) | 343 [341-379] |
| half-cell row pitch (gap spacing, px) | 163 [161-165] | 164 [162-166] | (256) | (256) | 156 [150-162] | 158 [157-159] |
| gap width at half depth (px) | 10 [9-11.6] | 9.5 [9-10.5] | 8 [7-11] | 9.5 [7.5-12] | 9 [8-11.5] | 11 [9-12] |
| gap depth (1 − min / plateau) | 0.33 [0.29-0.41] | 0.36 [0.30-0.40] | 0.41 | 0.52 | 0.44 [0.34-0.80] | 0.32 [0.25-0.37] |
| cut-edge asymmetry \|below − above\| / plateau | 0.030 | 0.029 | 0.036 | 0.034 | 0.026 | 0.019 |
| busbar period (px) | 69 [36-69] (36 = 9 BB; 69 = 2nd harmonic) | 39 [35-69] | 83 [54-85] | 56 [50-78] | 66 [58-111] | 58 [44-75] |
| mean grey (content) | 154 [144-162] | 156 [136-163] | 111 | 141 | 108 | 154 |
| sd | 23.7 [19.7-29.1] | 22.7 [20.1-29.1] | 33.9 | 30.4 | 34.7 | 24.0 |
| mean \|Laplacian\| | 2.84 [2.5-3.2] | 2.51 [2.2-3.0] | 10.7 | 6.6 | 6.0 | 2.79 |
| crack width (px / skeleton) | – | 2.70 [2.28-3.70] | 1.79 | 2.63 | 2.42 | 3.22 |

Findings:
- **The cut line.** In these modules every half-cell row is separated by a ~9-10 px dark gap at a 163 px pitch, 0.33-0.36 deep. There is no measurable cut-edge darkening: the asymmetry between the two long edges (0.03) equals that of ordinary full-cell edges (0.03-0.05). So the simulator needs a gap, not a special cut-edge profile.
- **Two-row periodicity.** The y-autocorrelation peaks at 2 × 163 (320-330 px) more often than at 163. Consecutive half-cell rows are not identical; mirrored halves are likely (S).
- **Size, orientation, scale.** Half-cells are landscape, 342 × ~155 px of cell area, with busbars vertical (along the short side): 9 busbars, period ~36-39 px. Relative to full cells (256 px pitch), x scale is 342/256 = 1.34 and the half-row scale is 163/(128 + gap) ≈ 1.2-1.3. Real half-cell crack width (2.70) is consistent with train crack width × ~1.3 (S).
- **Frame.** All non-E1 half-cuts are 512 squares with neighbouring half-cell rows visible. That includes the 4 non-E1 half-cuts among the 11 pool cells of ext117 (content 512 × 472-512; `domain_out/ext11_frame.txt`). E1's letterboxed strip frame (27 Oct F6, descriptive) is specific to E1's module family. The simulator therefore does not imitate it; doing so would be tuning on E1.

### 1.3 Simulator (`dom_synth_halfcut.py`; deterministic diagnostic version `dom_synth_variants.py`)
Per labelled full cell:
1. Find the centre cell's top/bottom gaps from the row profile (found in 158 of 162 train multi cells; fallback 128 / 384).
2. Split the centre cell at its midline and insert a copy of the image's own gap band, image and mask rows together. The inserted gap carries the source's spacing and ribbon labels.
3. Rescale: sx = 342/256, sy = 163/(128 + g), each with U(0.92, 1.08) jitter in the training version. Image bilinear, mask nearest.
4. Crop 512 × 512 centred on the top or bottom half, clamped inside the source.
5. Optional intensity match: linear map of content px to a target mean/sd. In the diagnostic: 154 / 24, the pool medians. In training: drawn from the pool half-cell distribution.

Not produced:
- 9 busbars (the source keeps its 2-5; busbar period 58-66 vs 36-39 real);
- CSIR half-cell multi texture (dark dislocation clusters; see the figure);
- scuff.

After intensity matching, the synthetic cells match the pool on mean, sd, sharpness (2.79 vs 2.84), gap depth (0.32 vs 0.33), x pitch and row pitch (158 vs 163).

### 1.4 Label transfer (`dom_label_transfer.py`, 162 synthetic from train multi)
- Loader format violations: 0 (all L mode, values ≤ 23, 512 × 512). E-SCDD 24-29 are mapped as in P6 (24→2, 29→1, 25-28→0); that last map is disclosed and only matters for the 12 train scuff cells.
- **Crack/image alignment:** paired crack CNR ratio synthetic/source, median 0.95 (n 46). A misaligned mask would drive it toward 0; the 5% loss is bilinear smoothing.
- Crack fragment count ratio 1.00. Crack survives the crop in 48 of 57 source crack cells (the crop keeps one half of the centre cell plus neighbours). Inactive is kept in 6 of 6.
- Inactive and crack masks are cut exactly at the inserted gap. A crack crossing the midline becomes two cracks, as a real cut would make (S).
- **Gap label mapping (judge condition 4), one convention everywhere.** A half-cut gap pixel is **sp multi (1)** for multi cells and **sp mono (2)** for mono cells:
  - synthetic training/SHV1: the inserted gap rows copy the source's own spacing labels (1 or 2);
  - Hanifi `_rf` (calib's build): class 29 → 1, 24 → 2;
  - E1 scoring (release 20221008 masks): half-cut multi gaps are already 1 (class 29 exists only in E-SCDD), and class 24 → 2 (handbook 03 §7).
  - Spacing is not a scored class; this matters only for training targets.
  - Training must use the house `masks_escdd` (as SHV1 does), not raw E-SCDD masks, so classes 24-29 never appear.

### 1.5 Does the current model fail on synthetic half-cuts? (key premise test; `dom_score_synvar.py`, `gaint domain_scratch/logs/synvar.log`)
Val cells (54) transformed into half-cuts, both halves (108 images per variant). Scored against the transformed GT. FINAL ensemble, crack at bias +0.75; read-only checkpoints, CPU fp32.

| Variant | crack cells | recall | precision | IoU | relR@2 | cells detected | inactive IoU |
|---|---|---|---|---|---|---|---|
| V0 original val | 23 | 0.706 | 0.533 | 0.436 | 0.887 | 23/23 | 0.429 |
| V1 gap inserted only | 46 | 0.672 | 0.537 | 0.425 | 0.858 | 46/46 | 0.374 |
| V2 half-cell scale only | 40 | 0.621 | 0.546 | 0.410 | 0.850 | 36/40 | 0.313 |
| V3 gap + scale | 40 | 0.606 | 0.541 | 0.400 | 0.829 | 37/40 | 0.305 |
| V4 V3 + pool intensity | 40 | 0.563 | 0.562 | 0.391 | 0.774 | 37/40 | 0.369 |
| V5 V4 + blur σ 0.8 | 40 | 0.560 | 0.554 | 0.386 | 0.759 | 37/40 | 0.260 |

- At bias 0 the same pattern holds: recall 0.656 → 0.503 (V4), relR@2 0.859 → 0.725.
- **SUP100-PF (BEST; 5-seed ensemble, same images; +0.75 shown for comparability, bias 0 in the log):**

  | Variant | recall | precision | IoU | relR@2 | cells detected | inactive IoU |
  |---|---|---|---|---|---|---|
  | V0 | 0.678 | 0.572 | 0.450 | 0.883 | 23/23 | 0.513 |
  | V1 | 0.643 | 0.569 | 0.433 | 0.855 | 43/46 | 0.416 |
  | V2 | 0.569 | 0.588 | 0.407 | 0.847 | 36/40 | 0.497 |
  | V3 | 0.554 | 0.579 | 0.395 | 0.822 | 36/40 | 0.469 |
  | V4 | 0.504 | 0.588 | 0.373 | 0.769 | 37/40 | 0.467 |
  | V5 | 0.498 | 0.584 | 0.367 | 0.752 | 37/40 | 0.421 |

  At bias 0: recall 0.612 → 0.432 (V4), relR@2 0.856 → 0.715. Full log: `domain_out/synvar.log`.

- **Per image (v2 re-run, 31 Oct 18:27):** `domain_out/synvar_percell.tsv` (md5 758b2884; `dom_score_synvar.py` v2 4afd4d90). Re-aggregation (`dom_synvar_check.py` 1741a064) reproduces every pooled number above exactly, and the v1/v2 aggregate lines are identical.
- **Paired by source cell** (21 val crack cells with GT ≥ 20 px in both V0 and the variant; both halves summed), +0.75:

  | Model | V3 − V0 recall, median / mean | V3: cells worse | V4 − V0 recall, median / mean | V4: cells worse |
  |---|---|---|---|---|
  | FINAL | −0.103 / −0.137 | 18/21 | −0.117 / −0.159 | 18/21 |
  | SUP100-PF | −0.107 / −0.150 | 19/21 | −0.137 / −0.172 | 19/21 |

  The drop is broad across cells, not driven by a few (E).

Readings:
- **E:** half-cut geometry plus pool-like intensity costs FINAL 0.14 crack recall, 0.11 relR@2 and 0.045 IoU on val content. SUP100-PF loses 0.17 recall, 0.11 relR@2 and 0.077 IoU. The cost comes from scale (V2) and intensity (V4); the gap itself costs little (V1).
- **Inactive:** FINAL loses 0.06-0.12 IoU. SUP100-PF holds inactive better (0.513 → 0.467 at V3/V4, −0.05). That fits PF's descriptive E1 inactive gain on half-cut/scuff cells (0.041 → 0.245).
- **E/S, descriptive:** this matches E1's half-cut-without-scuff crack recall of 0.552 (6 cells; judge j6) and V3/V4's 0.56-0.61. It is far from E1's scuff + half-cut 0.126, from FINAL's E1 half-cut recall 0.165 (F3) and from the Hanifi half-cuts (§1.6). So the simulator covers the "half-cut geometry" part of the failure, which a model can learn invariance to. The rest is not geometry.

### 1.6 Non-E1 validation: the Hanifi half-cuts
calib's hygiene set: 117 − 7 CSIR_00300 − 4 val/test-module = 106; 36 half-cuts. Scored from calib's read-only FINAL dump (`domain_out/rf_baseline_final.txt`).

| Stratum (FINAL +0.75) | cells | recall | precision | IoU | relR@2 | cells detected |
|---|---|---|---|---|---|---|
| Hanifi full, crack ≥ 20 px | 21 | 0.692 | 0.514 | 0.419 | 0.872 | 13/21 |
| **Hanifi half-cut, crack ≥ 20 px** | 17 | 0.031 | 0.064 | 0.021 | **0.036** | **1/17** |
| val crack cells | 23 | 0.706 | 0.533 | 0.436 | 0.887 | 23/23 |

- Crack-free Hanifi half-cuts (19): 27 predicted crack px per cell, 2 cells with ≥ 20 px. The model is conservative there, not noisy.
- **Caveat (E, figure `idea05_rf_halfcut_final.png`):** the Hanifi half-cut crack GT is 1,792 px over 17 cells (median ~70 px per cell). It is short marks, mostly at gaps and busbar ends; 6 of the 17 cells also have scuff. Speckled SAM-assisted labels are documented for these cells (handbook 17 §5.5; Om D10). judge measured 48% of these px within 10 px of spacing/border/cut line.
- **Ruling (judge, 14:23; coach 14:23):** H36 crack labels are unusable for any decision. H36 is for false alarms only (19 crack-free cells: FINAL 27 px per cell, 2 cells ≥ 20 px). There is no labelled non-E1 half-cut crack set; SHV1 (§1.8) is the synthetic substitute. Half-cut inactive: 3 cells, 1,238 px, too few.

### 1.7 Scuff, the larger part (`dom_scuff_morph.py`, non-E1 labels only)

| Group | scuff components ≥ 50 px | cells | area, median [min-max] | length (skeleton) | width | darkness vs ring | cells with crack within 15 px of scuff |
|---|---|---|---|---|---|---|---|
| Hanifi half-cut | 25 | 11 | 134 [60-1,120] | 30 | 6.1 | 0.14 | 0 |
| train | 14 | 10 | 186 [62-667] | 35 | 3.8 | 0.05 | 1 |

- **Reading (E/S):** non-E1 scuff labels are small, faint patches with no crack branching. E1's failure morphology is 2.5k-4.6k px streaks with crack branches 7.6-31 px away (F11, descriptive). It has no non-E1 labelled example.
- A scuff + branch simulator (Om's "optionally add scuff-like texture"; 27 Oct rank 2) could only take its geometry from E1, which breaks the seal on design. It should wait for non-E1 examples: B2 marks on the 986 pool half-cells (user, pending), or B3's scuff class plus mining.

### 1.8 SHV1: frozen synthetic half-cut val set (built 31 Oct 17:34 for the team; team-lead request)
- **Where:** gaint `/home/noob/work/domain_scratch/shv1/` (read-only). Metadata copy: `ideas/domain_out/shv1_meta/` (README.md, MANIFEST.md5, stems_eval.txt, shv1_context.tsv).
- **What:**
  - all 54 val cells × both halves = 108 images, 512 × 512 L;
  - house masks (`masks_escdd`) transformed with the image; layout as calib's `data/rf` (images/, masks/, ignore/ all zero, stems_eval.txt).
- **How:**
  - generator `dom_synth_val.py` (md5 6e702c36; copy inside the folder), seed 20261031, gaint CPU (CUDA hidden, nice 19, 1 thread), rc 0;
  - MANIFEST.md5 63dd5469 (328 files, `md5sum -c` OK); stems_eval.txt f809683f; shv1_context.tsv 7f943406.
  - Geometry is deterministic (no jitter): gap found in 54/54 cells, sx = 342/256, sy = 163/(128 + g).
  - Intensity: one (mean, sd) pair per image drawn with the frozen seed from the 1,008 pool half-cells' content pairs (`ap_pool.tsv` md5 a78a2d2a).
- **Content:** 40 crack images (from 21 of 23 val crack cells; 88,272 crack px); 11 inactive images (6/6 val inactive cells; 26,529 px); 68 crack-free images.
- **Appearance vs pool half-cells (E, `domain_out/hs_shv1.tsv`, `ap_shv1.tsv`; medians):**
  - matched: mean 153 / 154, sd 25.6 / 23.7, mean |Laplacian| 3.15 / 2.84, x pitch 343 / 342, row pitch 158 / 163, gap 11 / 10 px, gap depth 0.31 / 0.33;
  - not matched: busbar count (2-5 vs 9), multi texture, histogram shape (0.69 vs 0.79; a linear map keeps val's shape), scuff.
  - BMRK val cells (single cells in a white frame) become single half-cells in white.
- **Relation to V4:** same geometry. V4 used the pool-median intensity (154 / 24) for every image; SHV1 draws per-image pairs from the pool distribution.
- **Use:**
  - non-E1 selection/readout: the idea-5 mechanism readout (oracle bias and relR@2 on V0 vs SHV1), and a half-cut-specific crack bias for the routing lever (calib idea 1) without E1;
  - anything chosen on SHV1 is chosen on val.
  - **Never** score E1 or test with it. It has not been scored by me.

### 1.9 Baseline on SHV1 from calib's routing pre-check (E, `ideas/routing_precheck.md`; records `ideas/calib_out/rec_shv1/`, MANIFEST f089abce; judge reproduced)
- **Matched-precision relR@2 (max relR@2 at relP@2 ≥ 0.90), V0 → SHV1:** FINAL 0.892 → 0.730; SUP100-PF 0.876 → 0.694. This is the baseline of HC's primary mechanism readout.
- **Oracle-bias shift V0 → SHV1:** FINAL +0.4; SUP100-PF pooled +0.9 (per seed +0.8 to +3.2).
- **Routing pre-check: FAIL.** A half-cut bias chosen on SHV1 gains +0.008 / +0.001 in-sample and +0.002 / −0.003 cross-fitted. PF2 §13 is void.
- **Reading (E):** the half-cut deficit is ranking, not threshold. This is the case for a training-side fix (HC) over a routed bias.

### 1.10 Label-free half-cut detector (built 31 Oct for the routing pre-check; now PARKED)
- **Frozen:** gaint `domain_scratch/halfcut_detector_v1` (read-only, MANIFEST b8badda4).
  - Features: `dom_halfcut_detector2.py` (afa6af10).
  - Rule: `dom_halfcut_apply.py` (e3b3b683): half-cut iff max F(240-272 px) < 0.14 AND max S(140-190 px) ≥ 0.14.
- **History:** the pre-stated rule R1 (0fade57a) failed (FP 9.45%). R2b's (a, b) were then fitted on a DEV split (train + pool half modules 297-299; `dom_halfcut_rule2.py` 3f29a634).
- **Numbers:**
  - in-sample targets met narrowly: pool half recall 989/1008 = 98.1%; labelled FP 5/582 = 0.86%, which includes the fit cells;
  - held-out FP misses: val 3/54 = 5.6%, pool full multi 3.5% (full cells cropped at ~1.5× scale).
  - judge: "not a deployable router as is; keep it frozen as a descriptive tool, always quoted with its held-out FP". True full-cell FP is ~1-4%.
- **Hygiene note (coach, 31 Oct):** R1 and R2b were computed on the 50 test images (structure only, no labels, no scores); the frozen README lists "0/50 routed". No evaluation number came from test. From now on, test cells are excluded from every detector set (DEV and check = train + val + pool only).
- **Status:** routing is parked after the pre-check failed. No further detector work unless team-lead asks.

## 2. Prior tries in the repo
- **No half-cut simulator** (grep for synthetic half / cut line / simulate over `research/`).
- **R4** (Track M; `team_2026-10-24_go/trackM/results_r4.md`, `protocol_r4.md`): trained on 107 Hanifi `_rf` cells including the 43 half-cuts, scuff → ignore. Test n.d.; E1 half-cut recall 0.133 → 0.123 (F4b; vetter finding 2).
  - **Why HC is not a repeat of R4 (judge condition 3; E + S).** R4's half-cut crack labels are the H36 kind: 1,792 px of edge marks and specks over 17 cells, 48% within 10 px of spacing/border/cut line. The other 26 half-cuts had no crack. So R4 mostly taught "half-cuts have almost no crack", which plausibly lowered crack scores on half-cuts. Whether the baseline's half-cut loss is a bias offset or a ranking loss is decided by the SHV1 sweep: calib's pre-check points to mostly ranking (§7).
  - HC gives the opposite signal: full-cell crack and inactive labels (176 of 203 train crack cells keep crack after the cut, §4) transferred into half-cut geometry.
  - The mechanism readout (§7) tests exactly this: does the oracle bias gap between V0 and SHV1 shrink?
- **CP5 / CP100** (copy-paste of crack labels, `team_2026-10-29_features/protocol_cp5.md`, `verify_100_o2.md`; handbook 19): CP100 n.d. on test; E3b decoy flag. Synthetic composition of real crack pixels has not paid at 100% labels so far.
- **27 Oct `ideas.md`:** rank 2 (synthetic branch cracks along real scuff streaks) and rank 5 V2 ("content × 0.77", an inference-time rescale of half-cuts). Neither was run. V2 here is the training-side twin of that rescale.
- **E-SCDD's 93 diffusion images** (handbook 17 §5.4): 0 half-cut images released, 4 base cells; not usable.

## 3. Literature (R)
- Hanifi et al. 2025, arxiv:2511.09604: mask-conditioned diffusion (PV-DDPM) fine-tuned per cell type, including half-cut multi. No segmentation evidence; its released synthetic half-cuts number 0 (handbook 17 §5.1).
- Jaziri et al. 2024, doi:10.1109/wacv57701.2024.00844: fractal crack simulation plus a hybrid system to learn real crack segmentation from simulation. Evidence that simulated cracks can transfer when combined with real data; concrete, not EL.
- Prakash et al. 2019, doi:10.1109/icra.2019.8794443: structured domain randomisation. Context-aware placement beats unstructured randomisation, which supports keeping the real cell context (gaps, neighbours) rather than pasting.
- Ghiasi et al. 2021, doi:10.1109/cvpr46437.2021.00294: Copy-Paste (via 27 Oct ideas). Our CP100 replication was n.d. (above).
- Ebied et al. 2025, doi:10.1038/s41598-025-14478-y: GAN-generated EL cells against class imbalance, for cell classification (ELPV-style labels), not segmentation.

## 4. Simulator spec, cost and data budget (for coach / builder)
### 4.1 Spec (reference implementations: `dom_synth_val.py` md5 6e702c36, deterministic; `dom_synth_halfcut.py` md5 a380a208, with jitter)
- **Input:** a house train cell, image (PIL `L`) + `masks_escdd` mask (0-23).
- **Content mask:** rows/cols with ≥ 98% px ≥ 250 are letterbox; content = the rest, AND mask != 7.
- **Gap rows:**
  - Row profile = mean of content px per row (NaN → median), uniform filter 3.
  - In y ∈ [128 ± 45] and [384 ± 45], take the minimum row y.
  - Plateau = median of the profile over y ± 60. Band [a, b] = rows below half depth around y. Depth = 1 − min / plateau.
  - "Found" iff both depths > 0.08 and 200 < y_bot − y_top < 310.
  - **Training:** if not found, skip synthesis for that sample (use the real cell). Measured: found in 462 of 474 train cells (ARTS 158/161, BMRK 42/42, CFVS 145/146, CSIR 101/108, SDLE 16/17).
- **Cut:** y_mid = round((y_top + y_bot)/2). Insert image rows [a_top, b_top] and the same mask rows at y_mid, so g = b_top − a_top + 1.
- **Scale:**
  - sx = 342/256 · U(0.92, 1.08) and sy = 163/(128 + g) · U(0.92, 1.08) in training; no jitter for SHV1.
  - Image bilinear (`scipy.ndimage.zoom` order 1), mask nearest (order 0). A torch/cv2 port must reproduce nearest-mask semantics.
- **Crop:** half h ∈ {0, 1} uniform. Centre y = ((y_top + y_mid)/2 or (y_mid + g + y_bot + g)/2) · sy; centre x = 256 · sx. Take a 512 × 512 window clamped inside the scaled image.
- **Intensity:** content px (as above, after the transform) are linearly mapped to (mean, sd) drawn uniformly from the 1,008 pool half-cell pairs (`ap_pool.tsv`, md5 a78a2d2a). Round, clip to uint8.
- **Then** the house labelsafe pipeline as usual (flips, rot90, B/C ±0.2 at p 0.4, normalise).
- **Determinism:** draws (half, jitter, pool index) come from the per-sample seed of `stream.py`, so a resumed run is bit-identical.
- **Unit tests:**
  - p = 0 is bit-identical to the house pipeline;
  - with jitter off and a fixed pool index, it equals `dom_synth_val.py` on the 54 val cells (|Δ| ≤ 1 GL, masks exact);
  - mask values stay in 0-23;
  - the gap-found count is logged per run.

### 4.2 Data budget
- **Per run:** 20,000 steps × batch 8 = 160k labelled samples. At p 0.25, ~40k are synthetic. That is ~84 synthetic views per train cell (~335 views per cell in total), each a fresh draw of half / jitter / intensity.
- **Label content after the cut (one draw per cell, E):** crack kept in 176 of 203 train crack cells (87%; ARTS 34/42, BMRK 24/24, CFVS 74/88, CSIR 42/47, SDLE 2/2); inactive kept in 36 of 41 (CFVS 23/25, CSIR 6/9).
  - Crack px per synthetic view are about the same as in the source: total ratio 1.04, per crack cell median 1.11 (E, one draw per train cell). The ~1.7x area upscale offsets cropping away half the centre cell.
  - What drops is the share of crack-bearing views: 13% of crack cells lose their crack in the crop. That is ~3% of all views at p 0.25.
- **CPU:** ~40 ms per synthetic sample (numpy), ~27 CPU-min per run spread over loader workers. Negligible next to the GPU step.
- **Storage:** 0 on the fly.
  - Alternative: a frozen bank of K = 8 draws per cell ≈ 3,800 images + masks ≈ 0.6 GB on gaint. It can be md5-manifested but has less variety.
  - S: on the fly with stream seeds is preferred; the bank is the fallback if a loader port is risky.
- **GPU:** one 5-seed arm, ~12.5 lane-h on gaint (5 × ~2.5 h), ~5 h wall with 3 lanes.
- **Code:** about 1 day (builder).
- **Readout scoring:** SHV1 + V0 for 15 runs on CPU ~10 min each, or batch 8 bf16 on GPU behind the 7,154 MiB scoring gate (~1 min each).

## 5. Expected effect (S)
- **Test:** n.d. (0 half-cuts in test). Small risk from replacing 20-30% of real samples. Guard: no primary WORSE.
- **Synthetic val half-cuts (V4):** recall should recover most of the 0.14 loss. This checks the mechanism only (in-distribution for the arm).
- **E1 (descriptive unless co-primary):**
  - non-scuff half-cut crack recall toward full-cell level (≤ +0.1 on ~8% of E1 crack px);
  - scuff + half-cut 0 to +0.03;
  - overall E1 crack recall +0.01 to +0.03;
  - E1 inactive on half-cuts possibly +0.05 to +0.15 IoU. Inactive loses 0.06-0.12 under the transforms (§1.5), and PF's E1 inactive gain (0.041 → 0.245) sat on these cells.
- **Hanifi half-cuts:** possibly a few more cells detected; labels too sparse to read a pixel effect.

## 6. Kill criteria (v2, judge condition 1 + user decision)
- **Pre-arm (passed):** the model must lose ≥ 0.05 crack recall or relR@2 on V3/V4 vs V0. Observed: FINAL −0.14 / −0.11, SUP100-PF −0.17 / −0.11. Below that, a geometric simulator would have nothing to teach.
- **Arm (non-E1 only; v3):** stop idea 5 (geometry) if any of these holds:
  - any test primary is WORSE (rule 1, both test sets);
  - the mechanism fails: **SHV1 matched-precision relR@2 (relR@2 at relP@2 ≥ 0.90) gain < +0.05 vs baseline** (judge). The bias gap is reported, not in the kill (coach);
  - F51 crack AP is worse with a module-cluster bootstrap upper bound < 0.
- **E1** is a pre-registered co-primary verdict (read once at the opening), reported whatever it shows. It is not a kill input and not a selection input (user decision, 31 Oct).

## 7. Protocol sketch (coach writes the protocol; needs the user's OK)
- **Arm HC:** SUP100-PF + `synth_halfcut` (§4.1; p 0.25, jitter ±8%, pool-drawn intensity, skip when no gap found).
  - One change vs the shared SUP100-PF s5-9 baseline (protocol_PF2): same commit, data, steps, final weights, 5 seeds.
- **Test primaries (house):** crack IoU / relF1@2 / inactive IoU, rule 1 on all 50 and clean. Plus component recall at P ≥ 0.90 and relR@2 at relP@2 ≥ 0.90 (val-chosen). Expected n.d. (0 half-cuts): the test verdict is "not worse".
- **E1 co-primaries (coach, protocol_HC v0.1):** E1 crack relF1@2 (argmax) and E1 inactive IoU, plus strata (29 scuff + half-cut, 29 half-cut without scuff, 48 other). Read once at the opening. relF1 also charges a precision cost and matches THIN-B3; it replaces my relR@2-at-val-OP suggestion.
- **Mechanism readout, pre-registered, non-E1 (judge condition 2; v3 per judge's matched-precision ruling):**
  - **Primary:** SHV1 relR@2 at relP@2 ≥ 0.90 (max over the bias sweep), HC vs baseline (SUP100-PF s5-9; FINAL as reference). Kill if the gain is < +0.05.
  - **Reported:** calib's `el_metrics` sweep on V0 (val) and SHV1: oracle crack bias b* on each and the gap b*_SHV1 − b*_V0; SHV1 pixel recall / relR@2 / IoU at the val-chosen OP; v4_frozen as a sensitivity row (MANIFEST 95ff7219).
  - **Hypothesis, decided by the SHV1 sweep (not shown by §1.5):** the baseline's half-cut loss is mostly ranking, not a bias offset.
    - calib's pre-check (reproduced by judge; §1.9): baseline Δb only +0.4 (FINAL) / +0.9 (SUPPF5), while matched-precision relR@2 drops 0.892 → 0.730 (FINAL) and 0.876 → 0.694 (SUPPF5). The routing pre-check FAILED, so PF2 §13 is void.
    - In §1.5, relP@2 falls slightly on V4 (0.910 → 0.895, FINAL), so §1.5 does not show pure under-confidence (judge's erratum).
    - HC is expected to raise the matched-precision curve. Invariance to half-cut geometry is a ranking fix, which training can deliver and a threshold cannot.
  - HC trains on the same simulator family as SHV1, so an SHV1 gain is a **mechanism check**. Transfer evidence is the E1 co-primary.
  - The synvar V0-V5 per-image readout (`synvar_percell.tsv`) is a secondary diagnostic.
- **Routing (calib idea 1 lever):** dropped. The pre-check on SHV1 failed (routing is a no-op; §1.9).
- **Non-E1 guard:** F51 crack AP with a module-cluster bootstrap (as idea 8/9). H36 for false alarms only.
- **Reported:** cell-level metrics (idea 7); BMRK separately.
- **Source set and dose (coach, protocol_HC §3/§5, 31 Oct):**
  - Source rule_p: gaps found AND band g ≤ 20 AND band class-7 fraction < 0.4. My count was 349 train cells (ARTS 131, CFVS 122, CSIR 96; 162 crack, 34 inactive); only the single-cell BMRK/SDLE crops are excluded.
  - With house masks the count is **353** (builder, el_hc c2e6973; build_hc.md v3). The extra 4 are the train cells with no raw E-SCDD mask (ARTS_00057_r2_c5, CSIR_00178_r7_c1, CSIR_00179_r12_c4, CSIR_00179_r6_c1), which my local index lacked. Where both masks exist, no cell differs.
  - Kept cells have band padding ≤ 0.248; excluded cells ≥ 0.494.
  - builder's `synthesize()` reproduces `dom_synth_val.py` pixel for pixel on all 80 eligible SHV1 images. Its rule_p eligibility matches `rule_p_pass` on 108/108.
  - p 0.35 per eligible sample ≈ 26% synthetic views.
  - Reported subset SHV1-p: 80/108 images whose source passes rule_p. Files: `domain_out/shv1_meta/shv1c_subset.tsv` a9afc2df, column `rule_p_pass`; plain list `shv1p_stems_eval.txt` 7f651fc7.
- **Order:** after PF2 / B3 / the thin-crack arms, which are Om-approved.
- **Scuff:** a separate later arm, once non-E1 scuff + crack examples exist (B2 marks or mining), never designed from E1.

## 8. Reproduction (scripts, md5, per-cell outputs)
Scripts in `ideas/scripts/` (laptop `~/mtp/research/.venv/bin/python -I`; gaint `el-fault-detection/.venv/bin/python -I`, CUDA hidden, nice 19).

| Step | Script (md5) | Output |
|---|---|---|
| index, cell type | `dom_index.py` (1f243032), `dom_ctype.py` (26016c83) | `domain_out/dom_index2.tsv` (per cell) |
| half-cut appearance | `dom_halfcut_stats.py` (06ede7d7), `dom_hs_summary.py` (4da15aa7) | per image: `domain_out/hs_local.tsv`, `hs_pool.tsv` (1,008), `hs_syn.tsv`, `hs_synvar.tsv`, `hs_shv1.tsv` (crack width on gaint uses a fallback without skimage; ignore that column there) |
| intensity pairs | `dom_appearance.py` (725514ea) | per image: `ap_local.tsv`, `ap_pool.tsv`, `ap_shv1.tsv` |
| simulator (jitter) | `dom_synth_halfcut.py` (a380a208) | `domain_out/synth_multi_log.tsv` (per synthetic image: gap, g, sx, sy, half, px counts) |
| label transfer | `dom_label_transfer.py` (3d5c50f8) | stdout (§1.4) |
| V-series images | `dom_synth_variants.py` (f34f98ab) | gaint `domain_scratch/synvar/` (594 images + masks + list.tsv) |
| V-series scoring | `dom_score_synvar.py` v1 (d61787e1) → v2 (4afd4d90, adds `--percell`) | `domain_out/synvar.log` (aggregates); per image: gaint `domain_scratch/out/synvar_percell.tsv` (v2 re-run, tmux domsynv2) |
| Hanifi baseline | `dom_rf_halfcut_baseline.py` (b4b885fa), `dom_rf_fig.py` (35e980b9) | `domain_out/rf_baseline_final.txt`; figure |
| scuff morphology | `dom_scuff_morph.py` (be436e58) | stdout (§1.7) |
| SHV1 | `dom_synth_val.py` (6e702c36) | gaint `domain_scratch/shv1/` (MANIFEST 63dd5469); `domain_out/shv1_meta/` |

## 9. Note on the gap convention in the prototype
- The local prototypes (`dom_synth_halfcut.py`, `dom_synth_variants.py`) read E-SCDD masks and map 24→2, 29→1, 25-28→0.
- SHV1 and the protocol use the house `masks_escdd` directly. For val the two are identical in crack/inactive (val has 0 scuff px; handbook 17 §5.11).

## 10. Change log
- e403917e: v1, reviewed by judge.
- v3.1 (18:45): §1.9 pre-check baseline and FAIL (PF2 §13 void, routing dropped from §7); §1.10 detector parked plus the test-image hygiene note; §7 source rule_p + dose + SHV1-p.
- v3 (18:30): judge's matched-precision ruling (primary mechanism readout and kill = SHV1 relR@2 at relP@2 ≥ 0.90, gain ≥ +0.05); the under-confidence prediction turned into a hypothesis decided by the sweep; coach's E1 co-primaries (relF1@2 argmax + inactive IoU) and unsoftened kill adopted; v4_frozen named as the sensitivity row.
- v2 (18:05): §0 readouts; §1.4 gap mapping (condition 4); §1.6 H36 ruling; §1.8 SHV1; §2 R4 (condition 3); §4 spec + data budget; §6 kill without E1 (condition 1 + user decision); §7 E1 slot, mechanism readout (condition 2), routing note, F51; §8 reproduction. No measured number changed.

---

## judge verdict (31 Oct 2026, 14:53 IST from date; report md5 e403917e as reviewed)

**Verdict: PASS-to-protocol (narrowed), with conditions 1 to 4.** This is the best-founded of the new E1-aimed arms.
- It is cheap: 12.5 lane-h + ~1 day of code.
- Test risk is low.
- Its premise is measured on non-E1 data.
- Its value as a claim depends on the user's E1 decision (condition 1).

### What I checked (E)
- **The premise-test scorer is consistent with the established numbers.**
  - V0 (original val, FINAL +0.75) in `domain_out/synvar.log`: recall 0.706, IoU 0.436, relR@2 0.887, relP@2 0.910.
  - calib's independent records give FINAL val pixel recall 0.706, crack IoU 0.435, relR@2 0.887, relP@2 0.906.
  - So the V-series deltas come from a scorer that reproduces the house numbers.
- **The V4 pattern** (synvar.log), FINAL at +0.75:
  - recall 0.706 → 0.563 and relR@2 0.887 → 0.774;
  - pixel precision rises 0.533 → 0.562;
  - false px on crack-free images stay flat (6 → 5 per image).
  - SUP100-PF shows the same pattern: precision 0.572 → 0.588, recall 0.678 → 0.504.
  - Recall falling at a fixed bias, with precision and false alarms unchanged or better, is the signature of **under-confidence**. That is the half-cut calibration offset found in idea 1 (half-cuts under-confident by about 5 to 7 log-odds on E1; judge's idea-1 verdict).
- **Literature:** all 5 ids resolve, and the abstracts match the claims (arxiv:2511.09604, doi:10.1109/wacv57701.2024.00844, doi:10.1109/icra.2019.8794443, doi:10.1038/s41598-025-14478-y; doi:10.1109/cvpr46437.2021.00294 is checked in handbook 11).
- **Not reproduced:** the simulator itself and the half-cell appearance stats (gaint). These are design inputs, not claims the verdict rests on.
- **E1 hygiene:**
  - the simulator targets come from the 1,008 pool half-cells, with CSIR_00300 excluded;
  - E1's letterbox frame is deliberately not imitated;
  - scuff is deliberately not simulated from E1 geometry;
  - no E1 number was computed.
  - **Good discipline.**

### Conditions for the protocol
1. **Deciding readout (interim rule).**
   - The arm's target (half-cuts) has no non-E1 labelled crack readout: H36 is unusable, and half-cut inactive is 3 cells.
   - Test has 0 half-cuts, so test is expected n.d. by design. The verdict is then "test not worse" + mechanism.
   - Write "E1 co-primary slot (pending user)".
   - Remove E1 from the **kill** (§6, third bullet) unless the user authorises it. Killing a method on E1 is a selection use of E1.
2. **Add the calibration mechanism as a pre-registered readout.**
   - Run calib's `el_metrics` bias sweep on the V0 and V4 synthetic-val dumps and report the oracle bias on each.
     - Baseline: SUP100-PF s5-9 and FINAL.
     - Arm: HC.
   - Prediction (S): the baseline needs a higher b on V4 than on V0, and HC shrinks that gap. This is measurable on non-E1 data.
   - It is the arm's best case: idea 1 shows a two-bias cell-type split is worth +0.06 to +0.09 E1 relF1@2 at oracle (FINAL 0.432 → 0.518). Training on synthetic half-cuts could remove that offset without any labelled half-cut set.
   - Keep "V4 relR@2 gain ≥ +0.05" as the mechanism kill.
3. **Address R4 explicitly in §2.** R4 added 43 real half-cuts and E1 half-cut recall did not move.
   - The likely reason (E + S): those cells' crack GT is 1,792 px of edge marks and specks over 17 cells (48% within 10 px of spacing/border/cut line). R4 effectively taught "half-cuts have almost no crack", which may have reinforced the under-confidence.
   - Transferred full-cell labels give the opposite signal. Say this, so the arm is not read as a repeat of R4.
4. **Label mapping of the inserted gap.**
   - The gap carries the source's spacing labels (class 1/2).
   - E1/Hanifi half-cut gaps are class 29, mapped to 1 by calib's `_rf` build and to sp mono for class 24 in E1 scoring.
   - State the mapping once for training, `_rf` and E1, so a gap pixel is the same class everywhere.

### Expected effect, cost, kill (S)
- **Expected:**
  - test n.d. (0 half-cuts), with a small risk from replacing 25% of samples;
  - E1 crack +0.01 to +0.03 (domain's S). If condition 2's mechanism holds, up to a share of the +0.06 to +0.09 relF1 calibration headroom.
  - inactive on half-cuts possibly more. PF already holds inactive better on V4 (0.513 → 0.467 vs FINAL 0.429 → 0.369).
- **Cost:** 12.5 lane-h + 1 day of code (opt-in loader transform, p = 0 bit-identical test).
- **Kill:** real once condition 1 is applied (test WORSE, or mechanism fail).
- **Order:** after PF2 / B3 / the thin-crack arms (Om-approved). Needs the user's OK.

### Tags
- E: V0 consistency and the V4 under-confidence pattern from the logs.
- R: 5 ids resolved.
- S: the calibration-mechanism reading.

- **judge erratum, 17:33 IST (E, `domain_out/synvar.log`).** My "signature of under-confidence" reading above used pixel precision. relP@2 tells a different story.
  - relP@2 falls slightly on V4: FINAL +0.75: 0.910 -> 0.895; b 0: 0.931 -> 0.922.
  - At matched relP@2 (~0.91), V4 relR@2 is ~0.75 vs V0 0.887 (interpolated between b 0 and +0.75). Most of the V4 drop is therefore ranking, with at most a small calibration part.
  - This is exactly what condition 2 (the oracle-b sweep on V0 / V4) must settle. The condition stands; the reading is weakened.

- judge, 17:41 IST: v2 (md5 96120d8f) checked. Conditions 1 to 4 are applied: E1 is a pre-registered co-primary and not in the kill; the SHV1 oracle-b mechanism readout is in place; R4 is explained; the gap mapping is unified. The PASS-to-protocol stands.
  - **One wording fix for §7:** the prediction says "under-confidence: at a fixed bias, recall falls while precision and false alarms stay flat, as in §1.5". Per my erratum above, relP@2 falls slightly on V4, so §1.5 does not show that.
  - Phrase it as a hypothesis: "baseline b*_SHV1 > b*_V0 if half-cuts carry a calibration offset; the sweep decides".
  - Note for coach: HC trains on the same simulator family that generates SHV1 (from train cells, not val). An SHV1 relR@2 gain is therefore a mechanism check, not evidence of transfer. The transfer evidence is the E1 co-primary.

- judge, 18:26 IST: v3 (md5 09c1c8a1) checked. The primary mechanism readout and its kill are now SHV1 relR@2 at relP@2 >= 0.90 (gain < +0.05 kills). The bias gap is reported only. Section 7 states the calibration offset as a hypothesis decided by the sweep. PASS-to-protocol stands.

- judge, 18:27 IST: synvar_percell.tsv (md5 758b2884) spot-checked with my own aggregation.
  - Pooled recall / relR@2 at +0.75 reproduce synvar.log: FINAL V0 0.706 / 0.887, V4 0.563 / 0.774; SUPPF5 0.678 / 0.883, 0.504 / 0.769.
  - Paired by source cell (21 cells): V4 - V0 recall median FINAL -0.117 (18/21 worse) and SUPPF5 -0.137 (19/21 worse). **Exact.**
  - The synthetic half-cut drop is broad, not carried by a few cells. Report md5 89e6a21a noted; the verdict stands.
