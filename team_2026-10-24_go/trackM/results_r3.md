# R3 results: encoder pilots (val only) and Part B (U-Net++ ResNet-50, seeds 1-5)

MD, 25 Oct 2026. Status: **VERIFIED by MC** (`verify_r3.md`): Part B WORSE on inactive, val EXCLUDE. Protocol: `protocol_r3.md` (APPROVED with F1-F3).

## Part A: pilots (val only, verified by MC)
| pilot | change | params | val crack IoU | val relF1@2 | val mIoU_rob | val inactive | score | qualifies (> 0.6414) |
|---|---|---|---|---|---|---|---|---|
| reference SUP100 (5 seeds) | – | 26.1M | 0.4226 | 0.8811 | 0.6156 | 0.4112 | 0.6398 (sd 0.0016) | – |
| P-cnxt: U-Net + ConvNeXt-T | encoder + decoder | 31.9M | 0.4087 | 0.8665 | 0.6202 | 0.3827 | 0.6318 | no |
| P-effb4: U-Net++ + EfficientNet-B4 | encoder | 20.8M | 0.4248 | 0.8865 | 0.6287 | 0.4854 | 0.6467 | yes |
| **P-rn50: U-Net++ + ResNet-50** | encoder | 49.0M | 0.4324 | 0.8893 | 0.6204 | 0.4408 | **0.6474** | yes, **selected** |

- **Near-tie:** rn50 beat effb4 by 0.0007, under one seed sd (0.0016). The locked rule (highest qualifying) picked rn50; effb4 was not swapped in or run as a second Part B (MC).
- **Pilot test outputs:** the lanes' rescore JSONs and the trainer's built-in TEST lines in `train.log`, `metrics.json` and stdout exist for all three pilots. **None was read.** The rescore JSONs are sealed in cv02 `el_mt/reports/sealed_pilot_test_all.tgz` (md5 `de16e362...`; per-file md5s in `log.md`).
- Pilot JSONs in `pilots/` hold val only (`sets_scored: ['val']`).

## Part B: U-Net++ ResNet-50, seeds 1-5, vs SUP100
Runs `m_r3_rn50_s1..5`, cv02 `el_mt` (`3c1b72b`), `=mq3b`. Three ran on GPU 7; s4 and s5 ran on GPUs 0 and 1 beside the R2c lanes (same hardware type). 24 Oct 20:32 IST to 25 Oct 02:30 IST. All rc = 0, step 20,000.
Files: `r3b/m_r3_rn50_s*.json` (MD5 = cv02, `r3b/md5_cv02.txt`), `r3b/*.stdout`, `r3b/r3b_tables.txt`. This is Track M test opening no. 5.

### Verdict
**WORSE** on inactive IoU (rule 1, design §1/C6). **Val inclusion: EXCLUDE**: at 5 seeds, nothing passes on val. The pilot's val margin did not hold up. R3 does not enter the stack.

| set | crack IoU Δ (thr) | inactive IoU Δ (thr) | relF1@2 Δ (thr) | mIoU_rob Δ (thr) |
|---|---|---|---|---|
| all 50 | +0.0314 (0.0897) n.d. | **−0.0240 (0.0216) WORSE** | +0.0452 (0.1213) n.d. | −0.0120 (0.0193) n.d. |
| without noisy | −0.0041 (0.0100) n.d. | **−0.0251 (0.0227) WORSE** | −0.0030 (0.0100) n.d. | −0.0090 (0.0140) n.d. |
| val (inclusion) | +0.0022 (0.0100) | +0.0135 (0.0609) | +0.0026 (0.0100) | +0.0027 (0.0100) |

- **Bootstrap, without noisy:** inactive −0.0251 [−0.0721, +0.0094], P(Δ>0) 0.08. The CI includes 0, so the inactive loss is seed-consistent but not robust over cells. Leave-top-3-out inactive −0.039.
- **Inactive capture:** precision 0.631 → 0.601, recall 0.610 → 0.591, component recall 0.773 → 0.738. The loss sits mainly in CSIR inactive (without noisy 0.707 → 0.333; 3 cells) and CFVS (0.578 → 0.534).
- **Width flag:** inactive precision −0.030 (< 0.05), no flag. Crack component precision −0.034.
- **Noisy cell:** no rn50 seed failed badly on it (all-50 crack sd 0.004).

### Named secondaries (descriptive, rule-1 arithmetic; MC F3)
| | SUP100 | rn50 | Δ (thr) |
|---|---|---|---|
| BMRK crack AP | 0.462 | 0.480 | **+0.018 (0.014)** |
| BMRK relR@2 | 0.745 | 0.771 | **+0.025 (0.020)** |
| BMRK crack recall | 0.516 | 0.530 | +0.014 (0.017) |
| CSIR crack IoU, without noisy | 0.475 | 0.473 | −0.002 |
| CSIR inactive IoU, without noisy | 0.707 | 0.333 | **−0.374 (0.331)** |
| ARTS crack IoU | 0.456 | 0.466 | +0.010 (0.026) |

Also (MC): **CFVS crack AP 0.669 → 0.652 (−0.017, thr 0.015)**, worse, and CFVS inactive −0.044. The over-cells CI for inactive without noisy includes 0, [−0.074, +0.011] in MC's bootstrap: the seed rule says WORSE, but cell-robustness is weak.

These match Track D's frozen-probe prior: ResNet-50 features rank BMRK crack better, while CSIR is weaker. A source trade lies behind the pooled n.d. on crack. The per-source passes are descriptive.

**E1 ext** (secondary, never used for selection): crack 0.148 → **0.167**, crack recall 0.178 → **0.214**, inactive 0.064 → 0.074, mIoU 0.411 → 0.423. Same without `CSIR_00300_r25_c1`. Unseen-module crack is the largest relative change any rung has shown (+0.036 recall), but it is secondary and descriptive.

### Compute (vs ResNet-34)
- Params 49.0M vs 26.1M.
- 460.4 vs 148.0 GFLOPs per forward at 512 (`torch.utils.flop_counter`), about 3.1×.
- Wall time: about 5.9 h per run at 3 per GPU (GPU 7), against about 3.2 h for R34 runs at similar packing (R2/R4 at 4-6 per GPU took 6.6-8.7 h). Roughly 2 GPU-h per run, vs about 1.1.

## Reading
- A bigger encoder alone does not beat R34 at 100% labels under the L3 recipe. Crack and relF1 are flat, inactive is worse, and val does not include it.
- The BMRK crack and E1 gains agree with the probe. They point to an encoder benefit on hard and unseen crack that the pooled test metrics do not reward, and that is offset by inactive losses.
- An encoder ensemble (R34 + rn50) might combine both. Per the final protocol that is only allowed through E-union of an **included** recipe, so it is not open now. It would need a new protocol.
