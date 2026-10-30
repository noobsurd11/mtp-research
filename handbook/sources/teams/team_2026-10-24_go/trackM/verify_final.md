# MC verification of the FINAL (protocol_final, test opening no. 7)

MC, 25 Oct 2026. **Verified.** Recomputed from `final/final_cells.json` with my own code. Inputs: MD5 OK; `m9_final.py` md5 225fe015.

## Integrity
- **Order:** the script writes `final_val_decisions.json` (line 142) before the test/ext loop (line 147).
- **Val decisions, re-read:**
  - recipe = SUP100 (no rung included: R2, R2c, R3B, R4, R5 all verified EXCLUDE);
  - E-rec only;
  - no TTA (val score 0.6507 vs 0.6499);
  - bias +0.75 by max val relF1@2;
  - val crack precision drop 0.033 < 0.05, so the headline bias is +0.75.
- **Identity:** `final_b0` = R1 `ens_plain`, `final_b0.75` = R1 `r1_final_bias0.75`, and the singles equal R1's; max |diff| 0 (val, test). Contrast 2 is dropped (F2), and contrast 3 equals contrast 1.

## The final model
**The 5-seed ensemble of U-Net++/ResNet-34 trained on 100% labels (L3 recipe), mean softmax, no TTA, crack logit +0.75.** It uses 5 trained models and 5 forward passes per image.

## Contrast 1: FINAL − SUP100 mean single seed (paired image bootstrap, 2,000)
| operating point | set | crack IoU | relF1@2 | inactive IoU | mIoU_rob | crack P | crack R |
|---|---|---|---|---|---|---|---|
| **b +0.75 (headline)** | without noisy | **+0.018 [+0.013, +0.025]** | **+0.016 [+0.010, +0.025]** | +0.007 [−0.003, +0.020] | +0.003 [−0.001, +0.010] | −0.023 | **+0.061** |
| b +0.75 | all 50 | +0.018 [−0.029, +0.024] | +0.025 [−0.016, +0.031] | +0.006 n.d. | −0.002 n.d. | −0.023 | +0.062 |
| b 0 | without noisy | +0.014 [+0.012, +0.017] | +0.010 [+0.006, +0.016] | +0.004 n.d. | +0.003 n.d. | +0.018 | +0.008 |
| b 0 | all 50 | +0.050 [+0.013, +0.079] | +0.058 [+0.007, +0.111] | +0.004 n.d. | −0.000 n.d. | +0.076 | +0.008 |

- **Verdict (locked rule): PASS** on crack IoU and relF1@2 at both operating points. At b +0.75 the CI excludes 0 without the noisy cell, with a same-sign estimate on all 50; no primary has a CI wholly below 0. Inactive and mIoU are n.d.
- **Absolute numbers, test without the noisy cell (b +0.75):**
  - crack IoU 0.492, P 0.621, R 0.703, relF1@2 0.897;
  - inactive 0.456;
  - mIoU_rob 0.583.
  - Baseline single model: 0.474 / 0.644 / 0.642 / 0.881 / 0.449 / 0.580.
- **Disclosed fragility:** on all 50 at b +0.75 the noisy cell gets 10,867 crack px; crack precision is 0.563 against 0.662 at b 0. At b 0 the ensemble predicts 2 px there.
- **E1 ext (unseen modules, never used for selection):**
  - b 0: crack IoU 0.148, R 0.170;
  - b +0.75: crack IoU 0.172, R 0.215, P 0.459;
  - inactive 0.085.
- **Note:** MD's all-50 b +0.75 crack CI is [−0.024, +0.024], mine [−0.029, +0.024]. Same verdict; the difference is resampling draws.

## MC's reading for the user
- The best model found is the **5-seed ensemble of the existing 100% recipe**.
  - Without a bias, it is the safe choice: +0.014 crack IoU, and it does not fail on the noisy cell.
  - With the val-chosen bias, crack recall rises from 0.64 to 0.70 at 0.62 precision.
  - "Almost all cracks" (relaxed recall ≥ 0.90 at relaxed precision ≥ 0.90) is **not** reached: relR@2 0.866.
- **Every single-model change tried at 100% labels failed to beat L3:** Dice on more classes, two stronger encoders, 2x resolution, +107 CSIR cells.
- The remaining levers are data (BMRK-like and unseen-module labelled cells) and generalisation. ResNet-50 and 2x resolution both lifted unseen-module crack (E1 0.148 → 0.167) while not helping in-split test. That is a lead for a separate, locked study on unseen modules, not a claim.
