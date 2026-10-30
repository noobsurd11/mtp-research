# MC verification of R5 (internal resolution x2, about 4x compute)

MC, 25 Oct 2026. **Verified: n.d. on all four primaries in both cell sets, none worse. Val inclusion: EXCLUDE** (crack +0.0011, relF1 +0.0018, mIoU_rob +0.0073; thr 0.0100).
- Recomputed with `mc_verify/mc_rung.py`.
- MD5 OK; step 20000, code `1be64e1`.

| set | crack IoU | inactive IoU | relF1@2 | mIoU_rob |
|---|---|---|---|---|
| all 50 | +0.030 (thr 0.090) n.d. | −0.003 (0.022) n.d. | +0.046 (0.121) n.d. | −0.001 (0.026) n.d. |
| without noisy | −0.0046 (0.0100) n.d. | −0.0036 (0.022) n.d. | −0.0012 (0.0100) n.d. | −0.0113 (0.014) n.d.; boot [−0.022, +0.000] |

- **Confident misses** (GT crack with p < 0.001), the quantity this rung targeted: test 0.189 → **0.208** (worse); ext 0.704 → 0.687.
- **Crack recall** without noisy: −0.012.
- **E1 (descriptive):** crack IoU 0.148 → 0.167, recall 0.178 → 0.204. The same pattern as ResNet-50.
- **Per source:** CFVS mIoU −0.025 (thr 0.017), worse by the arithmetic; BMRK flat.
- **Compute:** 591.9 vs 148.0 GFLOPs per forward (4.0x), about 4.2 GPU-h per run.

**Reading:** at 4x compute, x2 internal resolution does not reach the confidently missed cracks on test. The hypothesis behind the rung (thin cracks lost to the encoder stride) is not supported at 100% labels.

## Consequence (locked protocol_final)
- No rung (R2, R2c, R3B, R4, R5) passes val inclusion, so the recipe is SUP100. Under F2, FINAL is the R1 model if D1/D2 repeat.
- MD launched the final scoring before this recompute. That is acceptable, because the inclusion decision is mechanical from val and this recompute confirms it.
