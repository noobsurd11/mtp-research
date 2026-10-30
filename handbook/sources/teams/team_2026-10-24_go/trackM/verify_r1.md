# MC verification of R1 (TTA, 5-seed ensemble, crack operating point; SUP100 checkpoints, inference only)

MC, 24 Oct 2026. **Verified.** All of MD's headline numbers recompute from `r1/r1_cells.json` with my own code (`mc_verify/mc_r1.py`, own bootstrap, seed 0, 2,000 resamples). Test, 50 cells, masks_escdd, final weights.
**Open item:** `r1/` has no `md5_cv02.txt`. Before team-lead commits, MD must add it, or point to where the MD5 check was recorded.

## Integrity
- **Identity:** `single_plain` equals M0's per-cell confusion for all 5 runs, val and test; max |diff| 0.
- **Val decisions re-derived from the stored cells:**
  - D1: val score ens_plain 0.6507 vs ens_tta 0.6499, so no TTA on the ensemble.
  - D2: no grid point has relR@2 ≥ 0.90 with relP@2 ≥ 0.90 (b = 1.25 gives 0.904 / 0.889), so the fallback (max val relF1@2) chose b = 0.75 (val relF1 0.8968; b = 1.0 gives 0.8967).
  - `r1_final_bias0.75` val cells equal the sweep row.
- **Test variants present:** only those the protocol lists.

## R1a: TTA vs plain, the same 5 checkpoints (rule 1, 5 v 5)
| set | crack IoU | inactive IoU | relF1@2 | mIoU_rob |
|---|---|---|---|---|
| all 50 | +0.0020 (thr 0.144) n.d. | +0.0125 (0.022) n.d. | **−0.0055** (0.197) n.d. | +0.0047 (0.022) n.d. |
| without noisy | **+0.0104 (thr 0.0100) BETTER** | +0.0122 (0.023) n.d. | +0.0067 (0.010) n.d. | +0.0059 (0.015) n.d. |

- **Verdict: PASS** under the locked rule (better without the noisy cell; same-sign n.d. on all 50; nothing worse). Crack passes at the 0.01 floor (+0.0104).
- **Paired per seed, without noisy:** +0.0101, +0.0099, +0.0099, +0.0087, +0.0132. 5 of 5 positive, and the effect is consistent. Crack precision +0.011; inactive precision −0.007 (within the flag).
- **New fact (E):** TTA **amplifies** the noisy-cell failure. On s3, crack px on `CSIR_00070_r8_c4` go 75,468 → 103,104, and its all-50 paired crack Δ is −0.033. That is why all-50 relF1@2 is negative. The other 4 seeds predict 0 crack px there with or without TTA.

## R1b: 5-seed ensemble (plain) vs mean single seed (paired image bootstrap)
| set | crack IoU | inactive IoU | relF1@2 | mIoU_rob |
|---|---|---|---|---|
| all 50 | +0.0497 [+0.0125, +0.0785] | +0.0041 [−0.0050, +0.0182] | +0.0584 [+0.0072, +0.1109] | −0.0001 [−0.0040, +0.0082] |
| without noisy | **+0.0144 [+0.0119, +0.0167]** | +0.0041 [−0.0052, +0.0188] | **+0.0102 [+0.0062, +0.0159]** | +0.0027 [−0.0020, +0.0091] |

- **Verdict: PASS** on crack IoU and relF1@2 on both sets. Inactive and mIoU are n.d.
- **Leave-one-out spread** (crack, without noisy): 4-member ensembles 0.4857 to 0.4882, against the 5-member 0.4882 and the single-seed mean 0.4738.
- **All-50 inflation** (as expected, C2): averaging cancels s3's noisy-cell failure. The ensemble predicts **2 crack px** on the noisy cell, against s3's 75,468. Reading: this is a real deployment benefit (robustness to a failure that hits 1 seed in 5 or 6), and it is separate from the +0.014 seen on clean cells.
- **Cost:** 5 trained models and 5× inference.

## R1c: crack bias +0.75 on the ensemble (descriptive)
| set | crack IoU | crack P | crack R | relP@2 | relR@2 | relF1@2 | inactive | mIoU_rob |
|---|---|---|---|---|---|---|---|---|
| all 50 | 0.485 → 0.453 | 0.662 → **0.563** | 0.645 → 0.699 | 0.953 → **0.844** | 0.829 → 0.863 | 0.887 → 0.853 | 0.440 → 0.442 | 0.547 → 0.545 |
| without noisy | 0.488 → 0.492 | 0.662 → 0.621 | 0.650 → 0.703 | 0.953 → 0.930 | 0.837 → 0.866 | 0.891 → 0.897 | 0.454 → 0.456 | 0.583 → 0.583 |

- On clean cells it trades 0.041 crack precision for 0.053 recall, at flat IoU.
- **On all 50 the bias re-opens the noisy-cell failure:** 2 → 10,867 crack px on `CSIR_00070_r8_c4`. Crack precision −0.099 and relP@2 −0.109, both beyond the 0.05 width flag.
- The "almost all cracks" target (relR@2 ≥ 0.90 at relP@2 ≥ 0.90) is **not reachable by an operating point** on val or test.

## What this means for the ladder (reading)
1. The ensemble is the clearest gain so far: +0.014 crack IoU and +0.010 relF1 on clean cells, plus immunity to the noisy-cell failure. It should be in the final model.
2. TTA on single models helps clean cells by +0.010 crack, but worsens the noisy-cell failure. On the ensemble, val said no TTA. Keep that.
3. A crack bias buys recall only at a precision cost, and it is unsafe on noisy inputs. Any final operating point needs a noisy-cell check in its protocol.
4. Recall needs a better model (R2 to R5), not a threshold: the 19% of GT crack with p < 0.001 is untouched by all of R1.
