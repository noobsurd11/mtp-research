# P16: SSL vs supervised at 20%, 50% and 100% labels (cv02). Results

Protocol: `protocols/P16_label_fraction_curve.md`. Part A was locked before any P16 run. Part B (Amendment 1) was locked before any SSL run; it fixed the recipe and let P13's validation numbers decide CutMix.

**Runs**
- **Part A (supervised, 9 runs).**
  - When and where: 11 Oct 17:28–22:06 IST, cv02 GPUs 1, 2 and 5, worktree `el_p13` at `bac5264`. All 18 train/rescore steps have rc = 0.
  - Pooling: A20 and A100 pool P6's `p6_L3_20pct` / `p6_L3_100pct` seeds 0–2 (`824fab0`) with P16 seeds 3–4. The supervised path is unchanged between the two commits (protocol).
- **Part B (SSL, 15 runs).**
  - When and where: 11 Oct 21:04 to 12 Oct 04:24 IST, cv02 GPUs 0, 3, 4, 5 and 6, worktree `el_p16` (branch `p16` at `d51b60f` per the protocol; the cv02 worktree has no `REVISION` file). All 30 steps have rc = 0.
  - Options: P13's Cs options verbatim, except the label fraction and, for Sx100, `data.unlabeled_pool=external`, checked against `p13_Cs_5pct_s0` in P13's queue spec. That means Mean Teacher with tolerant pseudo-labels (radius 2, t_pos 0.95), a separate-BN student forward, λ = 1 after warm-up and ramp, and 8 labelled + 8 unlabelled images per step.
- **All runs:** 20,000 steps; final weights (the EMA teacher for SSL); revised (`masks_escdd`) labels.
- **CutMix was off,** chosen by the locked val rule (`selection.txt`):
  - P13 val score CsM5 0.3507, Cs5 0.3652, so off.
  - P13's passing primary arm was CsM5 (with CutMix). On P13 *test*, CsM5 − Cs5 was n.d. on seeds, with crack IoU +0.010 [+0.004, +0.017] over cells. P16 therefore tests the Cs recipe, not CsM.

**Files**
- `raw/`: re-score JSONs and both launch logs.
- `p16_rules.txt`: locked rules, plus the bars figure log.
- `per_image_test.txt`: bootstrap and source split.
- `per_image_{A,S}.json` and `hist_revised_{A,S}.npz`.
- `fig_p16_bars.png` and `fig_p16_curve.png` (with `p16_curve.txt`).
- `sensitivity_excell.txt` and `fig_p16_curve_excell.png`: the post-hoc check without one test cell (below).
- `cell_noise_rank.txt` and `diag_csir70.txt` (the noisy-cell diagnostic, `scripts/diag_csir70.py`).
- `diag_csir70/*_pcrack.png`: p(crack) maps of `CSIR_00070_r8_c4` (512×512, grey = p × 255) for the 10 runs in `diag_csir70.txt`; copied 13 Oct from cv02 `/tmp/noob_el/diag/csir70/`, which a reboot wipes.
- E1: `../e1/e1_p16.md`.
- Reproduce with:
  - `bash scripts/post_p16.sh <cv02 gpu>`;
  - `scripts/diag_csir70.py`, run from the code worktree on cv02 (`el_p13` for A runs, `el_p16` for S runs);
  - `.venv/bin/python scripts/p16_excell.py --out results/p16/fig_p16_curve_excell.png`;
  - `.venv/bin/python scripts/cell_noise_rank.py`.

## Results
Test, revised labels, mean ± sd over seeds 0–4.

| Arm | Labels / unlabelled pool | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|
| **A20** (P6 s0–2 + P16 s3–4) | 95 / – | 0.398±0.006 | 0.361±0.037 | 0.822±0.010 | 0.942±0.006 | 0.434±0.007 | 0.352±0.040 |
| **S20** | 95 / 383 in-domain | 0.358±0.060 | 0.390±0.026 | 0.752±0.096 | 0.789±0.187 | 0.402±0.062 | 0.396±0.028 |
| **A50** | 239 / – | 0.408±0.076 | 0.412±0.012 | 0.808±0.117 | 0.839±0.203 | 0.486±0.106 | 0.399±0.014 |
| **S50** | 239 / 239 in-domain | 0.447±0.005 | 0.418±0.027 | 0.861±0.004 | 0.933±0.002 | 0.539±0.006 | 0.396±0.034 |
| **A100** (P6 s0–2 + P16 s3–4) | 478 / – | 0.435±0.078 | 0.436±0.013 | 0.828±0.105 | 0.853±0.187 | 0.567±0.054 | 0.433±0.028 |
| **Sx100** | 478 / 11,938 external | 0.463±0.013 | 0.439±0.017 | 0.868±0.013 | 0.925±0.035 | 0.586±0.015 | 0.438±0.029 |

The large sds on A50, A100 and S20 come from one test cell; see "One test cell" below.

### Per seed (test)
| Run | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack FP px on `CSIR_00070_r8_c4` | val crack IoU |
|---|---|---|---|---|---|---|
| A20 s0 / s1 / s2 (P6) | 0.396 / 0.398 / 0.401 | 0.298 / 0.374 / 0.368 | 0.818 / 0.817 / 0.832 | 0.935 / 0.946 / 0.935 | 1,013 / 0 / 343 | 0.313 / 0.317 / 0.319 |
| A20 s3 / s4 | 0.405 / 0.389 | 0.394 / 0.372 | 0.833 / 0.811 | 0.947 / 0.946 | 297 / 393 | 0.320 / 0.317 |
| S20 s0 / s1 | 0.403 / 0.402 | 0.404 / 0.364 | 0.831 / 0.824 | 0.951 / 0.933 | 0 / 374 | 0.326 / 0.315 |
| **S20 s2** | **0.292** | 0.389 | **0.652** | **0.584** | **39,994** | 0.323 |
| S20 s3 | 0.399 | 0.425 | 0.809 | 0.892 | 3,124 | 0.321 |
| **S20 s4** | **0.293** | 0.368 | **0.643** | **0.587** | **38,928** | 0.328 |
| A50 s0 / s1 | 0.447 / 0.448 | 0.414 / 0.404 | 0.857 / 0.871 | 0.931 / 0.937 | 0 / 1 | 0.385 / 0.371 |
| **A50 s2** | **0.272** | 0.398 | **0.599** | **0.476** | **80,060** | 0.380 |
| A50 s3 / s4 | 0.442 / 0.429 | 0.414 / 0.431 | 0.862 / 0.850 | 0.935 / 0.918 | 0 / 1,180 | 0.375 / 0.375 |
| S50 s0–s4 | 0.452 / 0.448 / 0.449 / 0.445 / 0.439 | 0.407 / 0.386 / 0.460 / 0.414 / 0.421 | 0.864 / 0.865 / 0.861 / 0.860 / 0.854 | 0.931–0.935 | 43 / 0 / 15 / 113 / 0 | 0.379–0.382 |
| A100 s0 / s1 / s2 (P6) | 0.472 / 0.471 / 0.470 | 0.417 / 0.433 / 0.437 | 0.875 / 0.879 / 0.873 | 0.935 / 0.940 / 0.942 | 0 / 27 / 0 | 0.424 / 0.425 / 0.419 |
| **A100 s3** | **0.297** | 0.454 | **0.641** | **0.520** | **75,217** | 0.422 |
| A100 s4 | 0.467 | 0.437 | 0.875 | 0.931 | 0 | 0.423 |
| Sx100 s0 / s1 / s2 | 0.470 / 0.473 / 0.469 | 0.421 / 0.449 / 0.433 | 0.876 / 0.880 / 0.871 | 0.939 / 0.943 / 0.940 | 0 / 0 / 0 | 0.426 / 0.421 / 0.422 |
| Sx100 s3 | 0.441 | 0.463 | 0.847 | 0.863 | 8,093 | 0.424 |
| Sx100 s4 | 0.463 | 0.427 | 0.866 | 0.941 | 0 | 0.427 |

## Locked rules
Rule: S − A at each fraction under P8 rule 1, 5 vs 5 seeds. Each cell gives the difference, then the threshold in brackets.

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| **S20 − A20** | −0.040 (0.069) | +0.029 (0.052) | −0.070 (0.111) | **fails: n.d. on all three.** Width check: relP@2 −0.153, **flagged** (cause below) |
| **S50 − A50** | +0.039 (0.088) | +0.006 (0.034) | +0.053 (0.135) | **fails: n.d. on all three.** Width ok (+0.094) |
| **Sx100 − A100** | +0.028 (0.091) | +0.003 (0.025) | +0.040 (0.122) | **fails: n.d. on all three.** Width ok (+0.072) |

Three primary contrasts, all reported. None passes.

**Gap closed** (S − A) / (A100 − A):
- S20: crack −107%, inactive +39%, relF1@2 −1,110%. S50: crack +141%, inactive +24%, relF1@2 +257%.
- For crack and relF1@2 these are not informative. Failed seeds pull down A100's mean (A100 s3) and A50's (A50 s2), so the crack denominators are tiny: +0.038 at 20%, +0.028 at 50%.
- The inactive figures are not affected that way. A100 s3 has the highest inactive IoU, and the inactive denominators are 0.074 and 0.023.
- Without the cell (below): S20 +3% / +38% / +0%; S50 +8% / +11% / −7%.

**Pooling check** (P6 seeds vs P16 seeds of the same supervised arm, rule 1 arithmetic):
- L3 20%: n.d. on all three.
- L3 100%: n.d. on all three. On crack and relF1@2 that is only because A100 s3's failure inflates the threshold (crack +0.089, thr 0.139). Inactive (−0.017, thr 0.019) is not inflated by that seed.
- Without the cell the halves agree: 100% crack +0.0006, relF1@2 −0.0025; 20% crack +0.0018. Inactive differs by −0.018 (100%) and −0.038 (20%); the P16 seeds score higher on inactive.

## Robustness (rule: image bootstrap and leave-top-3-out)
Paired image bootstrap over the 50 test cells (2,000 resamples), then the Δ without the top-3 cells of that class (`per_image_test.txt`).

| Contrast | crack IoU | inactive IoU |
|---|---|---|
| S20 − A20 | −0.040 [−0.090, +0.011]; −0.032 | +0.029 [−0.020, +0.064]; +0.018 |
| S50 − A50 | +0.039 [−0.003, +0.070]; +0.048 | +0.006 [−0.021, +0.022]; +0.001 |
| Sx100 − A100 | +0.028 [−0.004, +0.047]; +0.032 | +0.003 [−0.013, +0.022]; +0.006 |

- Every CI includes 0.
- **Source split.** In the 29 CFVS/BMRK/SDLE cells, crack Δ is +0.001, +0.001 and −0.003 for the three contrasts. All the movement in crack is in the 21 CSIR/ARTS cells, which include `CSIR_00070_r8_c4`.
- Leave-top-3-out drops cells by GT area, so it cannot remove this cell's effect: its damage is false positives, and it has only 787 crack GT px.

## One test cell moves every crack contrast (diagnostic, found after the runs)
This section is post hoc: it was looked for only after 4 runs showed test crack precision near 0.5. It changes the size and sign of the crack Δs, not any verdict.
**What happens.** In 4 of the 24 P16 runs the model labels 15–31% of test cell `CSIR_00070_r8_c4` as crack: S20 s2 and s4, A50 s2, A100 s3. The cell's true crack area is 787 px.
- That is 39k–80k false-positive pixels, enough to cut the run's pooled test crack IoU by about 0.11–0.18 and relP@2 to 0.48–0.59.
- A fifth run, Sx100 s3, does it partly (8,093 px).
- The other runs predict at most about 3k crack pixels there, most of them 0–1,200.
- The failing models are confident: median p(crack) on the predicted pixels is 0.92–0.99. The result is the same in bf16 and fp32 (`diag_csir70.txt`), so it is not a numerical artefact.
- The predicted "crack" follows the image's grain in patches over the whole cell.
- Val scores of these runs are normal; val has no comparable cell.

**What is unusual about this cell.** It is the noisiest of the 582 labelled cells (`cell_noise_rank.txt`). That noise is the likely trigger; this was not tested.
- Its robust pixel-noise sigma is 46.0, against a median of 1.48 and a 95th percentile of 4.45.
- The only comparable cell is `CSIR_00070_r7_c2` (43.0), from the same module. It is in train: labelled in the 100% arms, in none of the 2–50% labelled subsets, and in the 20% and 50% unlabelled pools.
- The next cell is at 10.4.

**Not new.** The same failure hit P6's `p6_L0_10pct_s1` (71,376 FP px; test crack IoU 0.261 → 0.360 without the cell). `p6_L0_10pct_s0` had a partial case (8,980 px; 0.344 → 0.362).
- That explains most of P6's secondary bootstrap result "L1 − L0 crack IoU +0.048 [+0.003, +0.097]": without the cell it is about +0.010.
- P6's locked rule 1 (test AP) is a different metric and was not re-checked here.
- In P7–P15 no run put more than 4,600 FP px on this cell. The maximum is 4,578 px (`p10_Cx_5pct_s2`), from the E1 per-cell counts in `../e1/raw_v2`, which include P15.

**Not specific to SSL** (4 events, so only a count). It hits 2 of 15 supervised and 2 of 15 SSL runs (3 of 15 counting Sx100 s3's partial case), across fractions. A20, S50 and Sx100 s0–2/s4 never show it.

**Post-hoc sensitivity (not a locked rule).** The same arithmetic without this one cell, from the E1 per-cell counts. With the cell, they reproduce the re-score exactly (max difference 0.0); see `sensitivity_excell.txt`.

| Contrast, without `CSIR_00070_r8_c4` | crack IoU | inactive IoU | crack relF1@2 | rule-1 arithmetic |
|---|---|---|---|---|
| S20 − A20 | +0.0024 (0.0100) | +0.0286 (0.0538) | +0.0003 (0.0139) | n.d. |
| S50 − A50 | +0.0021 (0.0100) | +0.0023 (0.0346) | −0.0011 (0.0100) | n.d. |
| Sx100 − A100 | −0.0021 (0.0100) | +0.0020 (0.0245) | −0.0023 (0.0100) | n.d. |

Without the cell:

| Arm | crack IoU |
|---|---|
| A20 | 0.402±0.006 |
| S20 | 0.404±0.006 |
| A50 | 0.448±0.007 |
| S50 | 0.450±0.005 |
| A100 | 0.474±0.002 |
| Sx100 | 0.472±0.004 |

The width flag on S20 disappears (relP@2 −0.003). **The verdict is the same with and without the cell: n.d. on all three contrasts.** Removing it changes the reason (true differences near 0 instead of thresholds inflated by outlier seeds), not the outcome.

## Collapse watch and unlabelled-loss share
Logged at single steps; values per seed s0–s4.

| Arm | step 4,000 rare_frac | step 20,000 conf_frac | step 20,000 rare_frac | step 20,000 loss_con / loss_sup |
|---|---|---|---|---|
| S20 | 0.0030–0.0036 | 0.895–0.898 | 0.0033–0.0045 | 0.037–0.066 |
| S50 | 0.0035–0.0039 | 0.865–0.866 | 0.0038–0.0051 | 0.020–0.027 |
| Sx100 (external pool) | 0.0003–0.0009 | 0.815–0.837 | 0.0054–0.0169 | 0.032–0.059 |
| P13 Cs5 s0 (5%, for reference) | 0.0079 | 0.956 | 0.0083 | 0.46 |

- **No collapse.** rare_frac holds or rises in every run. On the external pool it rises 6–49× between steps 4,000 and 20,000.
- **The unlabelled loss is 2–7% of the supervised loss at 20–100% labels, against 46% at 5%.**
  - The consistency loss itself is similar in size (0.005–0.020 here, 0.008 in P13 Cs5).
  - The supervised loss is not: at step 20,000 it is 0.11–0.14 at 20%, 0.23–0.24 at 50% and 0.33–0.36 at 100%, against 0.018 at 5%, where 23 labelled cells are fitted almost exactly.
  - Reading (untested): with λ fixed at 1, the unlabelled term carries little weight once labels are plentiful.

## Secondary
**Bin-0 share** (GT pixels scored < 0.001), crack / inactive. A20 and A100 here are the P16 seeds 3–4 only.

| Arm | crack | inactive |
|---|---|---|
| A20 | 0.412 | 0.549 |
| S20 | 0.395 | 0.469 |
| A50 | 0.266 | 0.456 |
| S50 | 0.262 | 0.416 |
| A100 | 0.179 | 0.387 |
| Sx100 | 0.193 | 0.383 |

**E1 per-cell metrics** (`../e1/e1_p16.md`; secondary). Δ [95% bootstrap CI].

Test (50 cells):

| Contrast | crack tolF1 | inactive cell IoU |
|---|---|---|
| S20 − A20 | +0.011 [−0.008, +0.029] | +0.016 [−0.023, +0.053] |
| S50 − A50 | +0.004 [−0.011, +0.019] | −0.012 [−0.046, +0.013] |
| Sx100 − A100 | −0.002 [−0.013, +0.009] | +0.006 [−0.025, +0.036] |

- These per-cell means are barely moved by the one cell (≤ 0.003).
- One test E1 metric excludes 0: S50 − A50 inactive area error +0.189 pp [+0.056, +0.388], which is **worse** for SSL. Sx100 − A100 inactive detection F1 −0.028 [−0.079, +0.000] is borderline.
- Test crack false alarms are 0 for every arm. The noisy cell has crack GT, so it is not a crack-free cell.

Unseen-module extension (106 cells; no run fails on any single ext cell, max FP per cell about 1,500 px):

| Contrast | Metric | Δ | 95% CI |
|---|---|---|---|
| S20 − A20 | inactive cell IoU | +0.179 | [+0.011, +0.385] |
| S20 − A20 | inactive IoU (pooled) | +0.081 | [+0.006, +0.236] |
| S20 − A20 | crack false alarm (share of crack-free cells) | **+0.046 (worse)** | [+0.018, +0.076] |
| S50 − A50 | crack IoU (pooled) | +0.019 | [+0.007, +0.031] |
| S50 − A50 | crack relF1@2 (pooled) | +0.047 | [+0.019, +0.077] |
| S50 − A50 | crack tolF1 | +0.030 | [+0.003, +0.059] |
| S50 − A50 | inactive cell IoU | +0.197 | [+0.034, +0.403] |
| Sx100 − A100 | every metric | n.d. | – |

**Descriptive curve** (`fig_p16_curve.png`, `p16_curve.txt`, and `fig_p16_curve_excell.png`; cv02 only).
- The 5% SSL point is P13 Cs5 (CutMix off, to match).
- 10% has no separate-BN SSL arm, so it is supervised only.
- SSL − supervised (all cells / without the noisy cell):

  | Labels | crack IoU | inactive IoU |
  |---|---|---|
  | 5% | +0.004 / +0.007 | +0.105 / +0.109 |
  | 20% | −0.040 / +0.002 | +0.029 / +0.029 |
  | 50% | +0.039 / +0.002 | +0.006 / +0.002 |
  | 100% (external pool) | +0.028 / −0.002 | +0.003 / +0.002 |

## Reading
- **Locked verdict: P16 fails at all three fractions.**
  - With this recipe (tolerant pseudo-labels, separate BN, no CutMix), SSL is not detectably better than supervised at 20%, 50% or 100% labels on any primary metric.
  - The result is the same with and without the noisy cell. Without it, every crack and relF1@2 difference is within ±0.003.
- **Inactive.**
  - The gain shrinks as labels grow: +0.105 at 5% (P13 Cs5, a secondary contrast there, passing on inactive), then +0.029 (20%), +0.006 (50%), +0.003 (100%), all n.d. from 20% up.
  - On unseen modules (secondary), SSL still raises inactive cell IoU at 20% and 50% (+0.18, +0.20, CIs above 0) but not at 100%.
- **Crack.** With all cells, no crack contrast is detectable. Without the noisy cell (post hoc), every test crack Δ is within ±0.003.
  - On unseen modules, S50 gains +0.019 crack IoU [+0.007, +0.031] (secondary).
  - S20 raises unseen-module false alarms (+0.046).
- **External pool at 100%:** n.d. on every primary, on test and on unseen modules.
  - In the CSIR/ARTS source split Sx100 − A100 crack is +0.050 [+0.002, +0.057]. That subset holds the noisy cell, which hit A100 s3.
  - Earlier external-pool results (all joint BN, 5–10% labels) were mixed: P9 passed on inactive (not robust), P10 was worse on crack relF1@2, P11 gained unseen-module inactive, P12 had no effect.
- **Measurement finding:**
  - A single test cell, the noisiest in the dataset, swings pooled crack IoU by up to 0.18 per run, in 4 of the 24 P16 runs.
  - It inflates the crack IoU seed sd 10–31× and can manufacture or hide a difference of ±0.04 between arms.
  - This README reads each crack contrast both ways, labelled post hoc.
  - Whether to make "without `CSIR_00070_r8_c4`" a standing robustness check is the user's decision; it was not in any locked protocol.
- **Limits.**
  - One recipe: CutMix off, by the locked val rule; hard pseudo-labels (BsM) were not run at 20–100%.
  - λ fixed at 1.
  - One split; no gaint replication.
  - The 20% and 100% supervised arms pool two commits (checked).

**Not claimed:** tuning at any fraction; other splits; pooling with gaint; any rule based on the without-cell numbers.
