# R2 results: soft Dice on 12 classes (dice_weight 6), 100% labels

MD, 24 Oct 2026. Status: **VERIFIED by MC** (`verify_r2.md`): WORSE, excluded on val.
Protocol: `protocol_r2.md` (APPROVED with F1, F2). Runs `m_r2_dice12_s0..4`, cv02 `el_mt` (`3c1b72b`), GPUs 6-7, `=mq`, 24 Oct 12:06-18:55 IST. All rc = 0, step 20,000 (asserted by the scorer).
Files:
- `r2/m_r2_dice12_s*.json`: M0 scorer, val/test/ext; MD5 = cv02 (`r2/md5_cv02.txt`);
- `r2/*.stdout`: training logs with grad norms;
- `r2/r2_tables.txt`: the full output of `scripts/m2_rung.py`.

Comparator: SUP100 (`m0b/`, the same scorer).
This is Track M test opening no. 2.

## Verdict
**R2 is WORSE** (rule 1, design §1/C6). Without the noisy cell, crack IoU and crack relF1@2 are worse beyond threshold. **Val inclusion: EXCLUDE**: on val nothing passes, and mIoU_rob is +0.009 against a 0.010 threshold. R2 does not enter the stack.

| set | crack IoU Δ (thr) | inactive IoU Δ (thr) | relF1@2 Δ (thr) | mIoU_rob Δ (thr) |
|---|---|---|---|---|
| all 50 | +0.0240 (0.0897) n.d. | −0.0149 (0.0229) n.d. | +0.0342 (0.1213) n.d. | +0.0136 (0.0234) n.d. |
| without noisy | **−0.0106 (0.0100) WORSE** | −0.0155 (0.0240) n.d. | **−0.0130 (0.0100) WORSE** | +0.0003 (0.0133) n.d. |
| val (inclusion) | −0.0035 (0.0100) n.d. | −0.0088 (0.0755) n.d. | −0.0051 (0.0100) n.d. | +0.0092 (0.0100) n.d. |

- **Bootstrap, without the noisy cell:** crack −0.0106 [−0.0171, −0.0029]; relF1 −0.0130 [−0.0234, −0.0054]; mIoU_rob +0.0003 [−0.0086, +0.0132]; inactive −0.0155 [−0.046, +0.007].
- **All 50:** the positive point estimates come from robustness, not from better crack. No R2 seed fails on the noisy cell: crack px on it are 1,116 / 0 / 0 / 35 / 1 vs SUP100 s3's 75,468, and the crack IoU sd is 0.003 vs 0.078.
- **Width flags:** none. Crack precision 0.644 → 0.650; the losses are in recall (crack R 0.642 → 0.617, relR@2 0.830 → 0.805, component recall 0.798 → 0.769, inactive R 0.610 → 0.590).
- **Multiplicity:** 8 tests.

## What R2 did per class (test without the noisy cell, IoU SUP100 → R2; P/R)
| class | IoU | P | R |
|---|---|---|---|
| gridline (45 cells) | **0.283 → 0.381** | 0.680 → 0.563 | **0.326 → 0.540** |
| border (24) | 0.692 → 0.728 | | 0.840 → 0.874 |
| ribbons (49) | 0.647 → 0.663 | | |
| sp_multi, sp_mono, frame_edge | +0.004 to +0.007 | | |
| crack (47) | 0.474 → 0.463 | 0.644 → 0.650 | 0.642 → 0.617 |
| inactive (15) | 0.449 → 0.434 | | 0.610 → 0.590 |
| material (11) | 0.411 → 0.402 | | |
| edge_dark (3) | 0.306 → 0.179 | | |
| splice (4) | 0.000 → 0.000 | never predicted, either arm | |

Val agrees on gridline: 0.308 → 0.409.

## Per source and named secondaries
- BMRK crack recall 0.516 → 0.484 (−0.032, thr 0.024, worse by the arithmetic); BMRK relR@2 0.745 → 0.694 (worse); BMRK crack AP 0.462 → 0.461 (n.d.).
- ARTS crack 0.456 → 0.446 (n.d.).
- CSIR crack without the noisy cell 0.475 → 0.476. CSIR inactive 0.707 → 0.481 (n.d.; 3 cells).
- **E1 ext:** crack 0.148 → 0.141, inactive 0.064 → 0.089, ext mIoU 0.411 → 0.430. Dropping `CSIR_00300_r25_c1` changes nothing (it is not an R4 matter here).

## Mechanism check (F2: grad norm and clip rate)
`m_sup_gn_s0` (the SUP100 config on `el_mt` with logging on) reproduces `p6_L3_100pct_s0` exactly after 20k steps: test and val crack and inactive IoU and relF1@2 are identical to 6 decimals. Logging changes nothing, and the deployment equals P6.

| run | mean pre-clip grad norm | clip rate (clip 1.0) |
|---|---|---|
| R2 s0 | 6.74 (steps 2k-20k about 7.0) | 0.969 |
| R2 s3 | 6.58 | 0.964 |
| SUP100 config (`m_sup_gn_s0`, full 20k) | 1.80 (1-2k 2.06; 2k-10k 2.13; 10k-20k 1.49) | 0.253 (0.54 / 0.30 / 0.16) |

**Reading:**
- With 12 Dice terms the gradient norm triples, and clipping binds on about 97% of steps (vs about 36%). The CE and crack/inactive-Dice part of each update therefore shrinks by roughly 3× in step size. The extra classes also share the step.
- R2 thus changes two things in effect: which classes get an overlap loss, and the effective learning rate for crack. The protocol named this side effect and fixed it as part of the change; the verdict stands as written.
- Gridline gains a lot (recall +0.21), so overlap losses do reach under-called thin classes.

## Notes from MC's verification
- The gridline gain is recall bought with precision (P 0.680 → 0.563).
- Crack recall falls 0.025, against the user's main target.
- The all-50 "gain" comes from no R2 seed failing on the noisy cell: seed luck, not the loss.
- Clip rate 0.97 vs 0.36, so the attribution is "Dice-12 at the L3 clip", not Dice in general.

## What this means for the ladder (reading)
1. R2 as specified is out. The gridline effect is real (test and val agree, +0.10 IoU) and is the largest single-class mIoU lever seen so far.
2. (Withdrawn after MC's advice: expected about +0.008 mIoU_rob, below the 0.01 floor, with a precision cost and a test-informed choice.) A narrower rung could keep it without diluting crack: R2c, Dice on crack, inactive and **gridline** only (3 classes), at the same per-class weight (dice_weight 1.5). It adds one class to the overlap loss instead of ten. The expected grad-norm rise is small, which the switch would confirm. It needs its own protocol.
3. R2's robustness on the noisy cell (5/5 seeds clean) is notable but unexplained, and is not a claim.
