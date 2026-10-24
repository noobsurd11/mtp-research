# Track M FINAL: the best-scoring model, scored once on test

MD, 25 Oct 2026. Status: **VERIFIED by MC** (`verify_final.md`). MC's all-50 bias +0.75 crack CI is [−0.029, +0.024], vs mine [−0.024, +0.024]: different resampling draws, same verdict. Protocol: `protocol_final.md` (APPROVED with F1-F4, locked before any R3 Part B, R5 or R2c number was opened).

**Two operating points, read this first.**
- **Bias +0.75** (the protocol's headline): best crack recall on clean cells. But it is fragile on a corrupted image: on the noisy cell it calls 10,867 px crack, and on all 50 cells crack precision falls to 0.563.
- **Bias 0:** robust (2 crack px on the noisy cell), with slightly lower recall.
- Pick +0.75 when images are clean and recall matters most, and bias 0 when image quality is unknown.

**In one paragraph.**
- No training change on the ladder beat the 100% baseline on val, so none entered the final recipe:
  - R2 (Dice on 12 classes): worse;
  - R2c (Dice incl. gridline): n.d.;
  - R3 (ResNet-50): worse on inactive;
  - R4 (+107 E-SCDD cells): n.d.;
  - R5 (2× internal resolution): n.d.
- No included rung was WORSE on test, so F4 does not apply.
- Under the locked protocol the final recipe is SUP100 (U-Net++ / ImageNet ResNet-34, CE + Dice, label-safe augmentation, 512 px, 20k steps). **The final model is its 5-seed mean-softmax ensemble with a crack bias of +0.75**, chosen on val. It is identical to R1's model: per-cell confusion matrices match R1's with max |diff| 0. So contrast 2 (FINAL − R1) is dropped (F2), and contrast 3 equals contrast 1.
- This is Track M test opening no. 7. The earlier ones were M0 (re-score only), R1, R2, R2c, R3 Part B, R4 and R5.

## What was run
- **Script:** `scripts/m9_final.py` (md5 `225fe015...`), cv02 GPU 7, `=final`, code `el_mt5` (`1be64e1`), on the 5 SUP100 checkpoints (step 20,000 asserted).
- **Outputs:** `final/final_cells.json` and `final/final_val_decisions.json` (MD5 = cv02: `b585d0a6...`, `6dff5988...`); tables in `final/final_tables.txt` (`scripts/m9_analyze.py`).
- **Val decisions,** written before test:
  - candidate: E-rec only, since the recipe is SUP100;
  - TTA: off (val score not higher);
  - crack bias +0.75, by max val relF1@2, because no bias reached val relR@2 ≥ 0.90 at relP@2 ≥ 0.90;
  - val crack precision drop at +0.75 is 0.033 < 0.05, so the **headline bias is +0.75** under the protocol;
  - the same decisions R1 made.
- **Compute:** 5 trained models (already existed, about 5.5 GPU-h), 5 forward passes per cell at inference, no TTA, no 4×-FLOP members.

## Headline (test, 50 cells; "clean" = without the noisy cell `CSIR_00070_r8_c4`)
| | SUP100 single model (mean of 5) | **FINAL (ensemble, bias +0.75)** | FINAL at bias 0 |
|---|---|---|---|
| crack IoU, clean | 0.474 | **0.492** | 0.488 |
| crack IoU, all 50 | 0.435 (one seed fails on the noisy cell) | 0.453 | 0.485 |
| crack precision / recall, clean | 0.644 / 0.642 | 0.621 / **0.703** | 0.662 / 0.650 |
| crack relP@2 / relR@2, clean | 0.938 / 0.830 | 0.930 / **0.866** | 0.953 / 0.837 |
| crack relF1@2, clean | 0.881 | **0.897** | 0.891 |
| crack components found (≥ 20 px), clean | 0.798 | **0.834** (precision 0.933) | 0.807 (0.944) |
| inactive IoU, clean | 0.449 | 0.456 | 0.454 |
| inactive precision / recall, clean | 0.631 / 0.610 | 0.639 / 0.614 | 0.629 / 0.619 |
| inactive components found (≥ 100 px), clean | 0.773 | 0.800 | 0.800 |
| mIoU_rob (13 classes), clean | 0.580 | 0.583 | 0.583 |
| mIoU_rob, all 50 | 0.547 | 0.545 | 0.547 |

**Contrast 1 (= 3): FINAL − SUP100 mean single seed** (paired image bootstrap, 2,000 resamples, 95% CI; protocol pass rule):

| set | crack IoU | inactive IoU | relF1@2 | mIoU_rob |
|---|---|---|---|---|
| clean, bias +0.75 | **+0.018 [+0.013, +0.025]** | +0.007 [−0.002, +0.021] | **+0.016 [+0.010, +0.025]** | +0.003 [−0.001, +0.009] |
| all 50, bias +0.75 | +0.018 [−0.024, +0.024] | +0.006 [−0.003, +0.020] | +0.025 [−0.010, +0.030] | −0.002 [−0.008, +0.008] |
| clean, bias 0 | **+0.014 [+0.012, +0.017]** | +0.004 [−0.005, +0.018] | **+0.010 [+0.006, +0.016]** | +0.003 [−0.002, +0.009] |
| all 50, bias 0 | **+0.050 [+0.013, +0.079]** | +0.004 [−0.005, +0.018] | **+0.058 [+0.007, +0.111]** | −0.000 [−0.004, +0.008] |

**Verdict: PASS** on crack IoU and relF1@2, at both biases. At +0.75 it passes in the clean set, with a same-sign estimate on all 50; at 0 it passes in both sets. Inactive IoU and mIoU_rob are n.d.; no primary is worse.

**Width flag (R4) on the headline:** on all 50, crack precision at +0.75 is 0.563, against 0.662 at bias 0 and 0.586 for the single models. The bias makes the ensemble call 10,867 crack px on the noisy cell, against 2 at bias 0. On the clean cells the precision cost is 0.041 (no flag). **Reading:** the +0.75 operating point is the better choice for recall on clean cells but fragile on a corrupted image. Bias 0 is the robust choice. Both are reported; the protocol's headline is +0.75.

## "Almost all cracks" (descriptive target: relR@2 ≥ 0.90 at relP@2 ≥ 0.90)
- **Not reached.** The best is relR@2 0.866 at relP@2 0.930 (clean, bias +0.75), from 0.830 / 0.938 for a single model. Crack components found rise 0.798 → 0.834.
- p(crack) on GT crack px, clean: below 0.001 for 0.095 (single model 0.184), ≥ 0.95 for 0.488.
- What is still missed is mostly BMRK (relR@2 0.812) and the non-twin CFVS cells (without twins and the noisy cell: relR@2 0.796).

## Per source (test, all cells; crack IoU single → FINAL +0.75; recall and relR@2 for FINAL)
| source | crack IoU | crack R | relR@2 | inactive IoU | mIoU_rob |
|---|---|---|---|---|---|
| ARTS (13) | 0.456 → 0.503 | 0.638 | 0.863 | no GT | 0.530 |
| BMRK (10) | 0.379 → 0.411 | 0.596 | 0.812 | 0.324 | 0.583 |
| CFVS (18) | 0.522 → 0.535 | 0.754 | 0.893 | 0.585 | 0.663 |
| CSIR without noisy (7) | 0.475 → 0.485 | 0.737 | 0.875 | 0.778 | 0.599 |
| CSIR all (8) | 0.379 → 0.285 | 0.698 | 0.847 | 0.421 | 0.446 |
| SDLE (1) | 0.031 → 0.000 | 0.000 | 0.000 | – | 0.582 |

## All 24 classes (test, FINAL +0.75; IoU / P / R on all 50, IoU without noisy)
- **Robust classes (GT in ≥ 3 cells):**
  - background 0.906 / 0.927;
  - sp_multi 0.733 / 0.809; sp_mono 0.743; ribbons 0.634 / 0.652;
  - border 0.359 / 0.693;
  - padding 0.994;
  - inactive 0.442 (P 0.639, R 0.588) / 0.456;
  - material 0.430;
  - crack 0.453 (P 0.563, R 0.699) / 0.492;
  - **gridline 0.288 (P 0.697, R 0.329)**;
  - **splice 0.000 (never predicted)**;
  - edge_dark 0.291;
  - frame_edge 0.809.
- **1-cell classes:** busbars 0.533, corrosion 0.769.
- **Absent from test GT:** text predicted at 8,515 px (all on the noisy cell); sp_dogbone, clamp, crack_rbn_edge, rings, dead_cell, belt_mark, jbox and meas_artifact never predicted.
- **Weakest robust classes:** splice (0) and gridline (recall 0.33). R2 and R2c raised gridline recall but not mIoU.

Full table: `final/final_tables.txt`.

## Unseen modules (E1 ext, 106 cells; never used for selection, scored per rung as a secondary)
| | crack IoU | crack P / R | relR@2 | inactive IoU / R | mIoU (ext list) |
|---|---|---|---|---|---|
| SUP100 single (mean) | 0.148 | 0.466 / 0.178 | 0.300 | 0.064 / 0.185 | 0.411 |
| FINAL, bias +0.75 | 0.172 | 0.459 / 0.215 | 0.355 | 0.086 / 0.243 | 0.431 |
| FINAL, bias 0 | 0.148 | 0.537 / 0.170 | 0.289 | 0.085 / 0.243 | 0.429 |

Identical without `CSIR_00300_r25_c1`. On unseen modules the model still misses most cracks (recall 0.22): about 70% of GT crack there gets p < 0.001 (M0).

## Multiplicity and history
- 1 contrast (contrasts 2 and 3 collapse into it) × 4 primaries × 2 sets × 2 biases = 16 tests, no correction.
- 7 test openings in Track M.
- Selection was on val throughout. The R1 model was fixed by rules locked in protocol_r1, before any R1 test number existed.
