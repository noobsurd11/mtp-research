# MC verification of R3 Part B (U-Net++ ResNet-50, seeds 1-5, against SUP100)

MC, 25 Oct 2026. **Verified: WORSE (inactive IoU, both cell sets). Val inclusion: EXCLUDE.** Recomputed with `mc_verify/mc_rung.py`. Per-source crack AP comes from the 1,000-bin histograms with my own AP code.
- MD5 OK; step 20000, code `3c1b72b`, seeds 1-5.

## Rule 1, 5 v 5 (test)
| set | crack IoU | inactive IoU | relF1@2 | mIoU_rob |
|---|---|---|---|---|
| all 50 | +0.031 (thr 0.090) n.d. | **−0.0240 (0.0216) WORSE** | +0.045 (0.121) n.d. | −0.012 (0.019) n.d. |
| without noisy | −0.0041 (0.0100) n.d. | **−0.0251 (0.0227) WORSE** | −0.0030 (0.0100) n.d. | −0.0090 (0.014) n.d. |

- **Bootstrap without noisy:** inactive −0.025 [−0.074, +0.011], so the over-cells CI includes 0; mIoU −0.009 [−0.020, +0.004].
- **Leave-top-3-out, inactive:** −0.039.
- **Inactive P/R:** 0.631/0.610 → 0.601/0.591. Inactive precision −0.030, within the flag.
- **Val:** crack +0.0022, relF1 +0.0026, mIoU_rob +0.0027. So EXCLUDE.
- **Noisy cell:** 0 crack px in all 5 seeds.

## Named secondaries (C's source-trade check)
| | SUP100 | rn50 | Δ (thr) |
|---|---|---|---|
| BMRK crack AP | 0.462 | 0.480 | +0.018 (0.014) better |
| BMRK relR@2 | 0.745 | 0.771 | +0.025 (0.020) better |
| **CFVS crack AP** | 0.669 | 0.652 | **−0.017 (0.015) worse** |
| CFVS inactive IoU | 0.578 | 0.534 | −0.044 (0.032) worse |
| CSIR inactive IoU (all 50) | 0.380 | 0.183 | −0.197 (0.184) worse; 3 cells |
| E1 crack IoU / recall | 0.148 / 0.178 | 0.167 / 0.214 | descriptive |

- **Reading:** the trade the frozen probe predicted is real. ResNet-50 is better on BMRK crack and on unseen-module crack, and worse on CFVS crack ranking and on inactive.
- **Not in results_r3 yet:** the CFVS AP loss. MD must add it.

## Compute
49.0M parameters; 460 vs 148 GFLOPs per forward (3.1x); about 2 vs 1.1 GPU-h per run.

## Verdict for the ladder
Not in the final model (val EXCLUDE; test WORSE on inactive). The E1 crack gain (+0.019 IoU, +0.036 recall) and the BMRK gains are worth a note for future work on unseen modules, but they are secondaries and post hoc in emphasis.
