# MC verification of R2 (soft Dice on 12 foreground classes)

MC, 24 Oct 2026. **Verified: R2 is WORSE than SUP100 and is excluded from the stack (val).** Recomputed with `mc_verify/mc_rung.py` (own code, own bootstrap, seed 0, 2,000 resamples) from `r2/m_r2_dice12_s0..4.json`.
- **Inputs:** MD5 OK against `r2/md5_cv02.txt`; step 20000 and code `3c1b72b` for all 5 runs.
- **Comparator:** SUP100 from `m0/`, identical to MD's `m0b/` (max confusion diff 0, all sets).

## Rule 1, 5 v 5 (test)
| set | crack IoU | inactive IoU | relF1@2 | mIoU_rob |
|---|---|---|---|---|
| all 50 | 0.435 → 0.459, +0.024 (thr 0.090) n.d. | −0.015 (0.023) n.d. | +0.034 (0.121) n.d. | +0.014 (0.023) n.d. |
| without noisy | 0.474 → 0.463, **−0.0106 (0.0100) WORSE** | −0.016 (0.024) n.d. | **−0.0130 (0.0100) WORSE** | +0.0003 (0.013) n.d. |

- **Bootstrap without noisy:** crack −0.0106 [−0.0173, −0.0027]; relF1 −0.0130 [−0.0235, −0.0049]; mIoU +0.0003 [−0.0078, +0.0133].
- **Leave-top-3-out:** crack −0.0064.
- **Verdict:** WORSE (worse on a primary in one cell set fails the rung, C6).
- **Why all 50 looks positive:** no R2 seed fails on the noisy cell (crack px 1,116 / 0 / 0 / 35 / 1), while SUP100's s3 does. That is a seed-count effect, not a property of the loss.
- **Val inclusion:** crack −0.0035, relF1 −0.0051, mIoU_rob +0.0092 (thr 0.0100). Nothing passes, so **EXCLUDE.**

## What R2 did (without noisy, base → R2)
- **Gridline** IoU 0.283 → 0.381, but this is **recall bought with precision**: R 0.326 → 0.540, P 0.680 → **0.563** (−0.117).
- **Edge dark** 0.306 → 0.179 (P −0.20, R −0.13; 3 cells).
- **Border, ribbons, sp classes:** +0.006 to +0.036.
- **Splice:** still 0.
- **Crack:** recall −0.025, relR@2 −0.025, precision +0.006. So R2 lost crack recall, the user's main target.
- **Inactive:** recall −0.020.
- **Per source:** CFVS crack WORSE (−0.015); BMRK relF1 WORSE (−0.027).

## The clip confound (F2), E
- R2 s0: mean pre-clip grad norm 6.72, clip rate 0.97 over the run.
- SUP100 config (`m_sup_gn_s0`, steps 0 to 9,200): 2.09 and 0.36.
- So R2 trained at a much lower effective step size. R2's crack loss **cannot be attributed to Dice dilution alone**: it is "Dice-12 at the L3 clip", as protocol F2 says.

## Ruling on MD's proposed R2c (Dice on crack + inactive + gridline)
Not recommended as the next rung. Lower priority than R3 Part B, R4 and upsampling.
1. **Expected value is below the floor.** A +0.10 gridline IoU moves a 13-class mIoU by about +0.008, under the rule-1 floor of 0.01. And the R2 gridline gain came with −0.117 precision.
2. **It is test-informed.** The choice of gridline comes from R2's per-class results. Val confirms it (0.308 → 0.409), so it is admissible only if the protocol cites the val number as the motivation and discloses the test one.
3. **If run anyway:** log the grad norm, keep crack recall as a named guard, and report gridline precision. The clip will still bind more than in SUP100 (3 terms against 2); disclose it.
