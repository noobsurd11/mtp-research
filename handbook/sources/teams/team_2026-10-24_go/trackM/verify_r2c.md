# MC verification of R2c (Dice on crack, inactive and gridline)

MC, 25 Oct 2026. **Verified: n.d. on all four primaries in both cell sets, none worse. Val inclusion: EXCLUDE.** Recomputed with `mc_verify/mc_rung.py` from `r2c/m_r2c_dice3_s0..4.json`.
- MD5 OK; step 20000, code `3c1b72b`.

| set | crack IoU | inactive IoU | relF1@2 | mIoU_rob |
|---|---|---|---|---|
| all 50 | +0.028 (thr 0.091) n.d. | −0.003 (0.021) n.d. | +0.041 (0.123) n.d. | +0.0045 (0.020) n.d. |
| without noisy | −0.0024 (0.0100) n.d. | −0.0048 (0.0215) n.d. | −0.0011 (0.0100) n.d. | +0.0051 (0.016) n.d. |

- **Bootstrap without noisy:** every CI includes 0 (mIoU +0.0051 [−0.0046, +0.0175]).
- **Val:** crack −0.0033, relF1 −0.0007, mIoU_rob +0.0035 (thr 0.0110). So EXCLUDE.
- **F2 guard:** crack recall −0.007, relR@2 −0.000. Within 0.01; not flagged.
- **Gridline:** IoU 0.283 → 0.357, again recall for precision (R 0.326 → 0.491, P 0.680 → 0.568).
- **All-50 positive values:** as in R2, no R2c seed fails on the noisy cell. Seed luck.
- **E1:** crack 0.148 → 0.132 (descriptive).
- **Grad norm:** ×1.16 against SUP100, under the 1.5 flag. The clip confound is small here.

**Reading:** as predicted in review_r2c, the gridline gain (+0.074 IoU) moves a 13-class mIoU by about +0.005, below the floor. It is bought with gridline precision. Not in the final model.
