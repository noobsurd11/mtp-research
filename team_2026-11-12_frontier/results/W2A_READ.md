# Wave 2a: screen read (lead, 17 Nov 2026, 08:41 IST)

Status: **swad_const passes the screen and is promoted to a 5-seed confirmation on cv5v3. rcs fails. ema_9998 and jml_hard are nulls. encoder_spd failed its mechanism gate and is read descriptively only (no gain). soft_band_jml is not read yet (one run is being retrained).** (Updated 17 Nov evening: soft_band_jml is read and FAILS its screen; see the addendum at the end.) A screen pass is a promotion, not a result: 2 seeds, split cv5v2 (which holds the module leak), one machine.

Tools: reviewed read tree `bench_wt_b` b5bf0ae (`bench_read_w1.py` fdb56b78), run 08:23 to 08:36 by `harness/w2a/read/run_read_w2a.sh` (5aac565d; review PASS in `harness/REVIEW_W2A_READ.md` 9ff7918f; equal to the reviewed copy at 08:23). Gates: `results/W2A_GATES.md` (ema hash PASS, swad pre-screen PASS, spd mechanism FAIL). Tables: `results/w2a_read/` (read.txt 1c6f4ce4 = 532 cells, read_x416.txt 52ee6b32 = 416 clean cells, read.json, run.log, MD5.txt, class_guard.txt cb98b8ff) and `results/w2a_spd_read/` (the descriptive SPD read, with GATE_ACK.txt). Inputs: gaint runs only (RTX PRO 4500), deploy tree c57508e, 140 + 10 wave 2a dumps and the W1-G PF dumps; split cv5v2, out-of-fold predictions on the 532 pool cells, label set v1.1, PF recipe, 20,000 steps, batch 8, 512 px. Comparator PF = W1-G seeds 5, 6. Margin M from the A/A of PF seeds {5, 6} against {7, 8} in the same read. Clean cells = `benchmark/splits/score_exclude_v3.txt` (116 excluded). No sealed cell is in any number. E = measured, S = judgement.

## 1. Arms at argmax (E; mean over 2 seeds, 532 cells)
| Arm (readout) | Strict crack IoU | Crack relF1@2 | relP@2 / relR@2 | Inactive IoU | mIoU-R13 | Width ratio | False crack px on 303 crack-free cells |
|---|---|---|---|---|---|---|---|
| PF (comparator) | 0.362 | 0.842 | 0.893 / 0.796 | 0.498 | 0.612 | 1.01 | 301 |
| **swad_const (swad_bn, pre-declared)** | **0.387** | **0.855** | 0.911 / 0.806 | 0.508 | **0.620** | 1.07 | 263 |
| swad_const (swad, no BN re-estimate) | 0.386 | 0.855 | 0.914 / 0.803 | 0.516 | 0.613 | 1.04 | 147 |
| swad_const (ema_9998_bn) | 0.376 | 0.850 | 0.911 / 0.797 | 0.505 | 0.618 | 1.01 | 171 |
| swad_const (raw_bn, last iterate) | 0.351 | 0.829 | 0.909 / 0.762 | 0.478 | 0.604 | 0.91 | 155 |
| rcs | 0.344 | 0.833 | 0.884 / 0.788 | 0.485 | 0.614 | 0.94 | 505 |
| ema_wise_posthoc (raw_bn) | 0.360 | 0.836 | 0.899 / 0.781 | 0.495 | 0.609 | 0.97 | 249 |
| ema_wise_posthoc (ema_9998_bn) | 0.363 | 0.838 | 0.899 / 0.784 | 0.497 | 0.610 | 0.98 | 245 |
| jml_hard (control) | 0.364 | 0.841 | 0.894 / 0.795 | 0.513 | 0.613 | 0.99 | 287 |
| encoder_spd (gate failed, descriptive) | 0.374 | 0.842 | 0.888 / 0.801 | 0.501 | 0.606 | 1.08 | 736 |

A/A margin (E): PF seeds {7, 8} minus {5, 6}: relF1@2 +0.0052 [-0.0011, +0.0111], SE 0.0031, so M = 0.010 (the floor); strict crack IoU M 0.010; mIoU-R13 M 0.010; inactive IoU M 0.054 (0.060 on the clean cells).

## 2. Contrasts against the comparator (E; difference with 95% interval, two-stage group bootstrap)
| Contrast | Metric | 532, argmax (OP-A) | 532, width-matched (OP-W) | 416 clean, OP-A | 416 clean, OP-W |
|---|---|---|---|---|---|
| **swad_bn - PF** (pre-declared) | crack relF1@2 | **+0.0135 [+0.0051, +0.0221]** | **+0.0118 [+0.0033, +0.0208]** | **+0.0160 [+0.0066, +0.0252]** | **+0.0141 [+0.0044, +0.0237]** |
| | strict crack IoU | +0.0245 [+0.0164, +0.0318] | +0.0203 [+0.0116, +0.0279] | +0.0268 [+0.0202, +0.0345] | +0.0219 [+0.0153, +0.0296] |
| | mIoU-R13 | +0.0083 [+0.0018, +0.0152] | +0.0080 [+0.0015, +0.0150] | +0.0107 [+0.0033, +0.0178] | +0.0105 [+0.0030, +0.0175] |
| | inactive IoU | +0.010 [-0.033, +0.053] | +0.011 [-0.032, +0.054] | +0.019 [-0.029, +0.062] | +0.021 [-0.028, +0.063] |
| rcs - PF | crack relF1@2 | -0.0085 [-0.0187, -0.0004] | -0.0070 [-0.0175, +0.0014] | -0.0094 [-0.0216, +0.0006] | -0.0079 [-0.0203, +0.0022] |
| | strict crack IoU | -0.0182 [-0.0278, -0.0093] | -0.0136 [-0.0233, -0.0047] | -0.0171 [-0.0251, -0.0086] | -0.0127 [-0.0207, -0.0047] |
| | mIoU-R13 | +0.0022 [-0.0040, +0.0088] | +0.0024 [-0.0038, +0.0090] | +0.0030 [-0.0038, +0.0102] | +0.0032 [-0.0038, +0.0104] |
| ema_9998_bn - raw_bn (same runs) | crack relF1@2 | +0.0018 [-0.0047, +0.0081] | +0.0015 [-0.0051, +0.0079] | +0.0019 [-0.0057, +0.0098] | +0.0018 [-0.0061, +0.0101] |
| jml_hard - PF | crack relF1@2 | -0.0004 [-0.0086, +0.0064] | -0.0001 [-0.0084, +0.0066] | -0.0002 [-0.0099, +0.0081] | +0.0002 [-0.0096, +0.0084] |
| | inactive IoU | +0.015 [-0.029, +0.070] | +0.014 [-0.030, +0.069] | +0.018 [-0.035, +0.079] | +0.017 [-0.035, +0.079] |
| encoder_spd - PF (descriptive) | crack relF1@2 | +0.0007 [-0.0272, +0.0130] | +0.0004 [-0.0187, +0.0108] | -0.0029 [-0.0412, +0.0136] | -0.0019 [-0.0235, +0.0112] |
| | mIoU-R13 | -0.0062 [-0.0145, +0.0015] | -0.0064 [-0.0146, +0.0013] | -0.0071 [-0.0172, +0.0017] | -0.0072 [-0.0172, +0.0016] |

## 3. swad_const: screen PASS, with one width flag (E, then S)
The arm: PF recipe with a constant learning rate after warm-up and a uniform average of every iterate of steps 10,000 to 20,000, batch-norm statistics re-estimated on the training fold (card `swad_const_pf_v11`, arXiv:2102.08604).

- Headline (E): relF1@2 gain is at or above M, with the interval above 0, at both operating points and on both cell sets (table 2). Per seed, swad_bn minus PF: +0.0150 and +0.0119 at argmax, +0.0133 and +0.0104 width-matched (clean cells: +0.0172, +0.0148 and +0.0150, +0.0132).
- What the gain is (E): width-matched, it is precision at equal recall: relP@2 +0.024 [+0.014, +0.036], relR@2 +0.002. On the bias curve, at PF's own precision, relR@2 is 0.827 and 0.819 against 0.797 and 0.795.
- Per source at argmax, relF1@2 swad_bn / PF (E): ARTS 0.851 / 0.830, BMRK 0.857 / 0.827, CFVS 0.867 / 0.857, CSIR 0.809 / 0.795. All four sources with at least 40 cells gain.
- The averaging is the cause, not the constant rate (E): the last iterate of the same runs is below PF (raw_bn minus PF: relF1@2 -0.0127 [-0.0258, -0.0026]). swad_bn minus raw_bn of the same runs, per seed: +0.0228 and +0.0296 at argmax, +0.0170 and +0.0266 width-matched (tool interval +0.0262 [+0.0161, +0.0393]; the tool draws seeds unpaired, so the per-seed differences are the firmer evidence).
- Guards (E):
  - Width against PF, pooled: 1.065 at argmax, 0.997 width-matched; inside 0.85 to 1.15.
  - **Width per source at argmax: ARTS 1.20 times PF (1.22 on the clean cells), outside the band.** BMRK 1.08, CFVS 1.05, CSIR 1.08 are inside. Width-matched: ARTS 1.13, BMRK 1.01, CFVS 0.99, CSIR 1.01, all inside. In absolute terms PF draws ARTS cracks at 0.87 of the label width and swad_bn at 1.04.
  - False crack on the 303 crack-free cells: share of cells with at least 50 false px 0.0050 against 0.0050; 263 px against 301. No rise.
  - Inactive IoU and mIoU-R13 do not drop (both rise; mIoU-R13 +0.008, at M on the clean cells).
  - Per class at argmax (class_guard.txt, descriptive): material +0.032, edge_dark +0.012, inactive +0.010, splice -0.023 (0.002 against 0.025; splice is 63 k px and PF's own seed sd is 0.031). Inactive precision falls (0.716 against 0.767) while recall rises (0.636 against 0.587).
- Beside the result, as the gate asks (E): layer4 cosine to the ImageNet start at 20k is below 0.8 in 7 of 10 swad runs (0.782 to 0.810; PF 0.926 to 0.946). The averaged model sits further from the pretrained encoder than PF does.
- Not pre-declared (E): the `swad` readout without the BN re-estimate gains the same on cracks (+0.0131 [+0.0066, +0.0199] / +0.0120 [+0.0052, +0.0191]), keeps every per-source width inside the band at both operating points (ARTS 1.14 at argmax), has fewer false crack px (147), but no mIoU-R13 gain (+0.002). The ema_9998 readouts of the swad runs gain less (+0.008 to +0.010). Of the seven swad contrasts only swad_bn against PF was declared before the read.
- Verdict (S): screen pass on the headline at both operating points. The ARTS width at argmax is a guard flag, not a cure: it is checked again on the 5-seed means, where both readouts (swad_bn and swad) are dumped; if swad_bn still breaks the ARTS band at argmax, the claim is made at the width-matched point or with the `swad` readout, and that choice is written into the confirmation request before any cv5v3 number is seen.

## 4. rcs: screen FAIL (E)
Crack gets worse (strict crack IoU -0.018 at argmax and -0.014 width-matched, both intervals below 0; relF1@2 -0.009 / -0.007). Per seed relF1@2: -0.0053 and -0.0116 at argmax. mIoU-R13 does not move (+0.002, interval includes 0). False crack px on crack-free cells 505 against 301 at argmax (1.68 times, above the 1.5 times guard) and 593 width-matched; the share of cells with at least 50 false px stays at 0.005 / 0.008. Per class (descriptive): splice +0.067 (0.092 against 0.025), material +0.004, edge_dark -0.008, inactive -0.014. The sampler buys the rare splice class and pays with crack and inactive. Closed.

## 5. ema_9998 over the PF runs: null (E)
ema_9998_bn minus raw_bn of the same runs: +0.0018 [-0.0047, +0.0081] at argmax. Per seed +0.0019 and +0.0016 (width-matched +0.0016, +0.0014): a consistent but tiny difference, a fifth of M. The interval is wide because the tool draws the two seeds unpaired. Beside (not a registered contrast): raw_bn is the PF model with re-estimated BN statistics (the raw weights are bit-equal to W1-G PF by the hash gate), and it is 0.006 below PF on relF1@2 (0.836 against 0.842), so the BN re-estimate alone does not help the PF recipe. Closed.

## 6. jml_hard: null control (E)
relF1@2 -0.0004 [-0.0086, +0.0064]; per seed +0.0042 and -0.0051. Inactive IoU +0.015 (per seed +0.0155, +0.0141), a quarter of its margin 0.054. It stays as the comparator of soft_band_jml, which is read with `TAG=softband ARMS="jmlhard softband"` after the retrained w2a_softband_f1_s6 is dumped.

## 7. encoder_spd: gate failed, descriptive (E)
Mechanism gate FAIL (layer3 / layer4 cosine 0.58 to 0.60 / 0.53 to 0.56 against the 0.8 threshold in 10 of 10 runs). Read under GATE_ACK: relF1@2 +0.0007 [-0.0272, +0.0130] at argmax and +0.0004 width-matched; mIoU-R13 -0.006; false crack px 736 against 301 (2.4 times) and the share of crack-free cells with at least 50 false px 0.017 against 0.005; seed sd of relF1@2 0.009 against PF's 0.001. Nothing here argues for the arm at lambda 1.0. The pre-registered consequence stands: one re-run at lambda 2.2 under a new card version, done in the cheap form first (one fold-0 seed-5 run to test the gate); if the gate fails again, SPD is dropped and L2-SP (alpha 0.01) is the fallback arm.

## 8. Limits
- 2 seeds per arm, 5 folds, one machine. M rests on one A/A of 2 against 2 PF seeds; the A/A difference itself is +0.005 on relF1@2, half of M.
- Split cv5v2 holds the module leak (cells of one module on both sides of a fold). The confirmation runs on cv5v3, where it is removed.
- Pool cells from known modules only; nothing here says how swad_const behaves on unseen modules.
- swad_const is a new training run per fold and seed, not a post-hoc step on PF checkpoints, so the comparison with PF is between separate trainings of the same seeds.

## 9. Next (S)
1. swad_const confirmation on cv5v3: seeds 5 to 9, same machine as its PF comparator, readouts swad_bn (declared) and swad, with the ARTS width rule of section 3 written into the request. Needs a launch request and a review before any start.
2. If the HRNet-W18 confirmation (running on cv02) and this one both hold, the combination HRNet-W18 with swad_const is the candidate for the final model and gets its own registered run.
3. soft_band_jml read after the retrain; the SPD gate test at lambda 2.2.

## Addendum, 17 Nov 2026 (19:43 IST): soft_band_jml read (2 seeds, after the retrain of w2a_softband_f1_s6)
Read: harness/w2a/read/run_read_w2a.sh (5aac565d, cmp-equal to the reviewed copy) with TAG=softband ARMS="jmlhard softband", 19:37 to 19:43 on gaint CPU, rc 0, bench_wt_b and bench_wt_w2 clean; manifest check 20 dumps, one device. w2a_softband_f1_s6 was retrained from step 0 with the reviewed job line (the first run had been stopped by the auto-stop guard on 16 Nov at step 12,000); it trained to step 20,000, rc 0, and was dumped rc 0. Tables: results/w2a_softband_read/ (read.txt, read_x416.txt, read.json, run.log, MD5.txt). Same comparator design as above: soft_band_jml is read against its control jml_hard (the same JML loss without the soft band); M = 0.010 (A/A PF {5,6} v {7,8}).

| SOFTBAND minus JMLHARD (E) | OP-A | OP-W | OP-A, 416 clean | OP-W, 416 clean |
|---|---|---|---|---|
| crack relF1@2 (headline) | +0.0046 [-0.0033, +0.0127] | +0.0037 [-0.0040, +0.0116] | +0.0052 [-0.0047, +0.0148] | +0.0039 [-0.0058, +0.0131] |
| strict crack IoU | +0.0033 [-0.0042, +0.0103] | -0.0011 [-0.0079, +0.0058] | +0.0041 [-0.0048, +0.0125] | -0.0008 [-0.0090, +0.0069] |
| relR@2 / relP@2 | +0.0132 [+0.0019, +0.0253] / -0.0060 | +0.0050 [-0.0068, +0.0171] / +0.0020 | | |
| width ratio | +0.071 [+0.037, +0.102] | -0.000 | | |
| inactive IoU | +0.0006 [-0.0385, +0.0341] | +0.0022 | | |
| mIoU-R13 | -0.0010 [-0.0068, +0.0048] | -0.0012 | -0.0014 | -0.0016 |

- **soft_band_jml: SCREEN FAIL, closed.** No metric gains M at both operating points; every headline interval holds 0. The recall gain at argmax (relR@2 +0.013, interval above 0) comes with crack drawn 7% wider (width ratio +0.071) and lower precision; width-matched it shrinks to +0.005 with the interval holding 0: an operating-point shift, not a better frontier. False crack px on the 303 crack-free cells 390 against 287 for jml_hard (1.36 x, inside the 1.5 x guard).
- **Consequence (pre-set gate):** label_jitter_crack needed softband minus jml_hard >= M on the headline; not met, so label_jitter_crack is not opened.
- jml_hard minus PF stays a null control (relF1@2 -0.0004 [-0.0086, +0.0064]).
