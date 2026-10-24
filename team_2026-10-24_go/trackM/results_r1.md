# R1 results: post hoc layer on SUP100 (TTA, 5-seed ensemble, crack operating point)

MD, 24 Oct 2026. Status: **VERIFIED by MC** (`verify_r1.md`, 24 Oct): every headline recomputes.
Protocol: `protocol_r1.md` (APPROVED with F1). Runs: cv02 GPU 7, tmux `=r1`, 24 Oct about 11:57-12:02 IST (val 137 s, test 91 s).
Files: `r1/r1_cells.json`, `r1/r1_val_decisions.json`, `r1/r1.log` (MD5 = cv02, `r1/md5_cv02.txt`), tables `r1/r1_tables.txt`. Scripts: `scripts/m1_r1.py`, `scripts/m1_analyze.py`.

## Checks
- **Identity:** `single_plain/<run>` per-cell confusion equals M0's for all 5 checkpoints on test and val, max |diff| = 0.
- **Val decisions,** written before test inference (`r1_val_decisions.json`):
  - **D1:** TTA on the ensemble **off**. Val score: plain ensemble 0.6507 vs TTA ensemble 0.6499.
  - **D2:** crack bias **+0.75**, by the fallback: max val relF1@2. On val no bias in 0-3 reached relR@2 ≥ 0.90 with relP@2 ≥ 0.90.
  - The R1 model is therefore the plain 5-seed ensemble at crack bias +0.75.

## Verdicts (test; primaries crack IoU, inactive IoU, crack relF1@2, mIoU_rob)
**R1a, TTA − plain (rule 1, 5 v 5): PASS on crack IoU** (passes without the noisy cell; n.d. with the same sign on all 50). No primary is worse in either set.

| set | crack IoU Δ (thr) | inactive IoU Δ (thr) | relF1@2 Δ (thr) | mIoU_rob Δ (thr) |
|---|---|---|---|---|
| all 50 | +0.0020 (0.1436) n.d. | +0.0125 (0.0222) n.d. | −0.0055 (0.1970) n.d. | +0.0047 (0.0219) n.d. |
| without noisy | **+0.0104 (0.0100) BETTER** | +0.0122 (0.0231) n.d. | +0.0067 (0.0100) n.d. | +0.0059 (0.0151) n.d. |

- Paired per seed, without noisy: crack +0.0104 (5/5 > 0, min +0.0087); relF1 +0.0067 (5/5); inactive +0.0122 (5/5); mIoU_rob +0.0059 (4/5).
- Bootstrap, without noisy: crack +0.0104 [+0.0074, +0.0138]; relF1 +0.0067 [+0.0032, +0.0111]; mIoU_rob +0.0059 [+0.0004, +0.0115]; inactive [−0.015, +0.038].
- **Caveats:**
  - The crack pass sits on the 0.01 floor: +0.0104 vs 0.0100.
  - On all 50, TTA makes the failing seed (A100 s3) worse on the noisy cell: crack px 75,468 → 103,104. That is why all 50 is n.d.
  - Cost: 8× inference.

**R1b, 5-seed ensemble − mean single seed (paired bootstrap, 2,000): PASS** on crack IoU and relF1@2 in both sets. Inactive and mIoU_rob CIs include 0.

| set | crack IoU | inactive IoU | relF1@2 | mIoU_rob |
|---|---|---|---|---|
| all 50 | +0.0497 [+0.0125, +0.0785] | +0.0041 [−0.0050, +0.0182] | +0.0584 [+0.0072, +0.1109] | −0.0001 [−0.0040, +0.0082] |
| **without noisy** (read here, C2) | **+0.0144 [+0.0118, +0.0167]** | +0.0041 [−0.0054, +0.0182] | **+0.0102 [+0.0062, +0.0157]** | +0.0027 [−0.0019, +0.0088] |

- LOO 4-member spread, without noisy: crack 0.4857-0.4882 (ensemble 0.4882); relF1 0.8886-0.8923.
- All 50 is inflated as expected: the ensemble removes s3's noisy-cell failure (2 crack px on that cell vs 75,468).
- Cost: 5 training runs (already paid) and 5× inference.
- TTA on top of the ensemble (descriptive): crack −0.0001 [−0.0036, +0.0038], relF1 −0.0018, mIoU_rob +0.0037 [−0.0039, +0.0109]. That matches D1: no gain.

## R1c, crack bias +0.75 on the ensemble (descriptive only, C3)
| set | variant | crack P | crack R | crack IoU | relP@2 | relR@2 | relF1@2 | comp. recall | comp. precision | inactive IoU | mIoU_rob |
|---|---|---|---|---|---|---|---|---|---|---|---|
| without noisy | ensemble, bias 0 | 0.662 | 0.650 | 0.488 | 0.953 | 0.837 | 0.891 | 0.807 | 0.944 | 0.454 | 0.583 |
| without noisy | ensemble, bias +0.75 | 0.621 | 0.703 | 0.492 | 0.930 | 0.866 | 0.897 | 0.834 | 0.933 | 0.456 | 0.583 |
| all 50 | ensemble, bias 0 | 0.662 | 0.645 | 0.485 | 0.953 | 0.829 | 0.887 | 0.799 | 0.944 | 0.440 | 0.547 |
| all 50 | ensemble, bias +0.75 | 0.563 | 0.699 | 0.453 | 0.844 | 0.863 | 0.853 | 0.831 | **0.634** | 0.442 | 0.545 |

Readings:
- **Without the noisy cell** the bias buys recall at small cost: relR@2 +0.029, component recall +0.027, crack precision −0.041, IoU flat, mIoU_rob flat. **Width flag:** none (< 0.05).
- **On all 50** the bias puts 10,867 crack px on the noisy cell (0 without the bias). Crack precision drops 0.099 (**width flag**), component precision 0.944 → 0.634, and crack IoU −0.032. The operating point is fragile on that cell.
- **The "almost all cracks" target** (relR@2 ≥ 0.90 at relP@2 ≥ 0.90) is **not reached** by any operating point on val, and on test the chosen point gives relR@2 0.866. The rest has to come from the model (R2/R3), not the threshold.

## Per source (test, all 50; single-seed mean → ensemble → ensemble + bias)
| source | crack IoU | inactive IoU | mIoU_rob | FP px on absent classes (ensemble) |
|---|---|---|---|---|
| ARTS (13) | 0.456 → 0.472 → 0.503 | no GT | 0.530 → 0.527 → 0.530 | 32 |
| BMRK (10) | 0.379 → 0.396 → 0.411 | 0.324 → 0.324 → 0.324 | 0.576 → 0.581 → 0.583 | 1,082 |
| CFVS (18) | 0.522 → 0.534 → 0.535 | 0.578 → 0.579 → 0.585 | 0.659 → 0.662 → 0.663 | 0 |
| CSIR (8) | 0.379 → 0.464 → 0.285 | 0.380 → 0.425 → 0.421 | 0.455 → 0.466 → 0.446 | 9,464 (text, on the noisy cell) |
| SDLE (1) | 0.031 → 0.000 → 0.000 | no GT | 0.577 → 0.582 → 0.582 | 0 |

## Per class (test without the noisy cell; single → ensemble)
- Crack 0.474 → 0.488; inactive 0.449 → 0.454.
- Material 0.411 → 0.430; gridline 0.283 → 0.288 (recall still 0.33); sp_multi 0.803 → 0.809.
- Splice stays at 0.000; edge_dark 0.306 → 0.291.
- 1-cell classes: busbars 0.420 → 0.533, corrosion 0.755 → 0.769.

Full table in `r1/r1_tables.txt`.

## Notes from MC's verification
- TTA amplifies s3's noisy-cell failure (75,468 → 103,104 crack px; s3 paired all-50 crack Δ −0.033). That is why all-50 relF1 is negative for TTA.
- The ensemble predicts 2 crack px on the noisy cell. Its all-50 gain is mostly robustness to that cell, separate from the +0.014 on clean cells.
- The R1c bias re-opens the noisy-cell failure (10,867 px) and trips the width flag on all 50.

## What R1 means for the ladder
1. **The final model will be a 5-seed ensemble** (val D1: no TTA on top). It adds about +0.014 crack IoU and +0.010 relF1@2 (test, without the noisy cell), and it removes single-seed failures on the noisy cell.
2. **TTA helps single models** (+0.010 crack IoU) but adds nothing to an ensemble.
3. **A threshold cannot buy "almost all cracks"** at relP@2 ≥ 0.90. The best val operating point reaches relR@2 0.866 on test, and on the noisy cell it costs precision. Recall must come from the model.
4. **mIoU and inactive are not moved by any post hoc step here.** R2 (Dice on 12 classes) and R3 (encoder) are the levers for them.

## Multiplicity
2 verdict contrasts × 4 primaries × 2 sets = 16 tests; no correction. This is test opening no. 1 for Track M (M0 re-scored existing checkpoints and tuned nothing on test).
