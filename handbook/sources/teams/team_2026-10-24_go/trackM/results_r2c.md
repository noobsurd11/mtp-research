# R2c results: soft Dice on crack, inactive and gridline (dice_weight 1.5), 100% labels

MD, 25 Oct 2026. Status: **VERIFIED by MC** (`verify_r2c.md`): n.d., val EXCLUDE.
Protocol: `protocol_r2c.md` (APPROVED, low priority, F1/F2). Runs `m_r2c_dice3_s0..4`, cv02 `el_mt` (`3c1b72b`), GPUs 0-1, `=mq2c`. All rc = 0, step 20,000.
Files: `r2c/m_r2c_dice3_s*.json` (MD5 = cv02, `r2c/md5_cv02.txt`), `r2c/*.stdout`, `r2c/r2c_tables.txt`. Comparator: SUP100 (`m0b/`). This is Track M test opening no. 4.

## Verdict
**R2c is n.d.** on all four primaries in both cell sets; none is worse. **Val inclusion: EXCLUDE.** R2c does not enter the stack.

| set | crack IoU Δ (thr) | inactive IoU Δ (thr) | relF1@2 Δ (thr) | mIoU_rob Δ (thr) |
|---|---|---|---|---|
| all 50 | +0.0279 (0.0909) | −0.0031 (0.0211) | +0.0408 (0.1229) | +0.0045 (0.0197) |
| without noisy | −0.0024 (0.0100) | −0.0048 (0.0215) | −0.0011 (0.0100) | +0.0051 (0.0162) |
| val | −0.0033 (0.0100) | +0.0273 (0.0483) | −0.0007 (0.0100) | +0.0035 (0.0110) |

- Bootstrap without the noisy cell: every CI includes 0. mIoU_rob +0.0051 [−0.0043, +0.0172].
- All 50: the positive point estimates again come from no seed failing badly on the noisy cell (crack px 7,230 / 10 / 0 / 2 / 0 vs SUP100 s3's 75,468).
- **Guard F2:** crack recall 0.642 → 0.635 (−0.007) and relR@2 0.830 → 0.830, both within the 0.01 guard. No flag.
- **Grad norm:** 2.09 / 2.10 (s0 / s3) vs 1.80 for the SUP100 config (×1.16, below the 1.5× kill); clip rate 0.34 vs 0.25.
- **Multiplicity:** 8 tests.

## Gridline (the target) and other classes, test without the noisy cell
- Gridline IoU 0.283 → 0.357; precision 0.680 → 0.568, recall 0.326 → 0.491. Val: 0.308 → 0.385. As with R2, the gain is recall bought with precision.
- material 0.411 → 0.378, border 0.692 → 0.708, edge_dark 0.306 → 0.320; splice 0.000 → 0.001.
- crack 0.474 → 0.471, inactive 0.449 → 0.445.

## Per source and E1
- Per source, crack and inactive are flat: BMRK 0.379 → 0.381, ARTS 0.456 → 0.465, CFVS 0.522 → 0.517, CSIR without noisy 0.475 → 0.474.
- E1: crack 0.148 → 0.132, recall 0.178 → 0.161, inactive 0.064 → 0.083. Identical without `CSIR_00300_r25_c1`.

## Reading
Adding gridline Dice alone raises gridline about +0.07 IoU at a precision cost, but mIoU_rob does not move detectably (+0.005), as MC expected. Crack is unharmed this time: the grad norm rose only 16%, against ×3.7 for R2. This supports reading R2's crack loss as clip and dilution, but it is not a test of that.
