# Protocol R2c: soft Dice on crack, inactive and gridline (3 classes), 100% labels

MD, 24 Oct 2026. Status: **APPROVED by MC at low priority** (`review_r2c.md`), with F1 and F2 applied. It runs only in lanes not needed by R3 Part B or R5. MC expects about +0.008 mIoU_rob, below the decision floor.

## What I had seen when writing this
- R2's results (`results_r2.md`, draft):
  - 12-class Dice was WORSE on crack (−0.011) and relF1 (−0.013) without the noisy cell;
  - gridline IoU +0.10 on test and val;
  - grad norm about 3×, clipping on 97% of steps.
- **Motivation (F1):** on **val**, R2 raised gridline IoU 0.308 → 0.409. Test agreed (0.283 → 0.381).
- This rung is **post hoc**: it was designed after seeing R2's test numbers. It is disclosed as such, and its own test result is confirmatory only for R2c.

## Question
Does adding an overlap loss for gridline alone (the robust class with the largest deficit: 45 test cells, IoU 0.28, recall 0.33) raise gridline and mIoU_rob without the crack loss R2 showed?

## Hypothesis
- R2's crack loss came from diluting the update: 10 added Dice terms tripled the grad norm under clip 1.0.
- A single added term should move the grad norm and clip rate far less (checked from the logs) while keeping most of the gridline gain.
- Expected (S): gridline +0.05 to +0.10 IoU, so mIoU_rob +0.004 to +0.008; crack within ±0.005.

## The one change
- SUP100: `dice_classes=(14, 11)`, `dice_weight=1.0` (per class 0.5).
- **R2c:** `loss.dice_classes=[14,11,15] loss.dice_weight=1.5` (per class 0.5). Only gridline's Dice term is added.
- Absent-class behaviour as in R2: gridline is in 318 of 478 train cells, so it is in about 99% of batches of 8.
- No code change. Unit-tested path (`tests/test_m_dice.py`).
- `training.log_grad_norm=true` (logging only).

## Fixed, arms, decision
- As protocol_r2: SUP100 comparator, 5 seeds (`m_r2c_dice3_s0..4`, seeds 0-4), cv02 `el_mt` (`3c1b72b`; identity-checked).
- Rule 1 on 4 primaries on both cell sets with the design §1/C6 pass rule; val inclusion (C1); 8 tests.
- Named secondaries:
  - gridline IoU / P / R (test and val);
  - crack recall and relR@2;
  - grad norm and clip rate vs `m_sup_gn_s0`.
- **Guard (F2):**
  - a crack recall or relR@2 drop > 0.01 vs SUP100 (without the noisy cell) is flagged;
  - gridline precision is reported beside recall.
- **Kill:** if the R2c grad norm is above 1.5× SUP100's, this is reported as the same confound as R2.

## Compute
5 runs at about 1.1-1.5 GPU-h each, on cv02 GPUs 6-7. Ledger before launch.
