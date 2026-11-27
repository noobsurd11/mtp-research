# swad_const 5-seed confirmation on cv5v3 (lead, 17 Nov 2026, 23:33 IST)

**Verdict (pre-registered rule, harness/LAUNCH_REQUEST_c3swad.md section 7): NOT CONFIRMED (no confirmed gain).** The primary readout swad_bn does not pass the headline (crack relF1@2) at any of the four required values; the declared secondary readout swad does not either. swad_const is therefore not a confirmed component of the final model on the registered headline.

Read: harness/c3swad/run_read_c3swad.sh (10ed79a6), 17 Nov 23:25 to 23:32 on gaint CPU, rc 0; tool scripts/bench_read_w1.py fdb56b78 at 89b9ea5 (worktree clean before and after); verdict harness/c3swad/c3swad_verdict.py (61ce4ba0), class table c3swad_class_guard.py (c9022bcc). Inputs: cv02 runs only (manifest check 75 dumps, one device NVIDIA RTX A6000), split cv5v3 (285 module groups), label set v1.1, out-of-fold predictions on 532 cells and the 416 clean cells. PF = c3_pf_v11 seeds 5 to 9 (25 runs); SWADBN = c3s_swad_v11 seeds 5 to 9 with readout swad_bn (primary); SWAD = the same runs with readout swad (declared secondary). M from the PF A/A {5,6} v {7,8} in the same read: relF1@2 M 0.010 on both cell sets. Tables: results/c3swad_read/ (read.txt, read_x416.txt, read.json, verdict.txt, class_guard.txt, run.log, MD5.txt). E = measured, S = judgement.

## 1. Headline: crack relF1@2, arm minus PF (E)
| | 532 cells, OP-A | 532 cells, OP-W | 416 clean, OP-A | 416 clean, OP-W |
|---|---|---|---|---|
| SWADBN (primary) | +0.0070 [-0.0007, +0.0156] | +0.0048 [-0.0036, +0.0141] | +0.0098 [+0.0009, +0.0198] | +0.0071 [-0.0025, +0.0176] |
| SWAD (secondary) | +0.0064 [-0.0009, +0.0138] | +0.0053 [-0.0022, +0.0128] | +0.0075 [-0.0009, +0.0165] | +0.0058 [-0.0030, +0.0150] |
A gain counts only if delta >= M (0.010) and the lower end > 0 at all four: no value meets M. Per seed (SWADBN, 532 cells, OP-A): +0.0061, +0.0104, +0.0064, +0.0063, +0.0056: all positive, mean below M.

## 2. Guards (E; the point value decides)
- SWADBN fails 5 guard items: per-source width on ARTS (1.248 and 1.153 on 532 cells, 1.290 and 1.181 on the clean cells, OP-A and OP-W) and false crack px on crack-free cells at OP-A (339 against 212 = 1.60 x, limit 1.5). Pooled width, inactive IoU and mIoU-R13 pass.
- SWAD fails 2 items: ARTS width at OP-A (1.158 and 1.187).
- The carry rule (swad carries the claim when swad_bn passes the headline and fails only per-source widths) does not apply: neither readout passes the headline.

## 3. Beside the verdict (descriptive, decides nothing; E)
| arm minus PF | strict crack IoU, OP-A | strict crack IoU, OP-W | relP@2, OP-W | relR@2, OP-W | mIoU-R13, OP-A |
|---|---|---|---|---|---|
| SWADBN, 532 cells | +0.0180 [+0.0108, +0.0262] | +0.0131 [+0.0051, +0.0219] | +0.0171 [+0.0083, +0.0272] | -0.0049 [-0.0187, +0.0110] | +0.0073 [+0.0002, +0.0147] |
| SWADBN, 416 clean | +0.0209 [+0.0122, +0.0300] | +0.0143 [+0.0045, +0.0241] | +0.0202 | -0.0025 | +0.0077 |
| SWAD, 532 cells | +0.0181 [+0.0106, +0.0257] | +0.0154 [+0.0078, +0.0232] | +0.0162 | -0.0034 | +0.0001 |
- Strict crack IoU rises by 0.013 to 0.021 at both operating points on both cell sets, with every interval above 0 and every seed positive (SWADBN, 532 cells, OP-A: +0.017, +0.018, +0.016, +0.022, +0.016). The gain is precision at an unchanged recall: the averaged model draws fewer wrong crack pixels inside crack regions, and the 2 px-tolerant metric (relF1@2) moves much less. Strict crack IoU is a protocol metric but not the registered headline; this is reported, not claimed.
- Levels (OP-A, 532 cells, mean over 5 seeds): PF strict crack IoU 0.365, relF1@2 0.846, inactive 0.504, mIoU-R13 0.612; SWADBN 0.383, 0.853, 0.520, 0.619; SWAD 0.383, 0.853, 0.525, 0.612.
- Per class (class_guard.txt, SWADBN minus PF, 532 cells): material +0.031, edge_dark +0.011, inactive +0.015, splice -0.015 (splice is near zero for every arm: PF 0.016).
- Encoder cosine to the ImageNet start at step 20,000: layer3 about 0.83, layer4 0.79 to 0.81 in all runs.
- Against the 2-seed screen on cv5v2 (results/W2A_READ.md): relF1@2 +0.0135 there, +0.0070 here on the same 532 cells with the corrected split and 5 seeds; strict crack IoU +0.0245 there, +0.0180 here. The screen effect shrank by about half on the headline, as a screen-selected arm is expected to (winner's curse); the leakage read found no measurable leak on cv5v2 (results/C3_LEAK_READ.md), so the split change alone does not explain it (S).

## 4. Consequences (lead's rulings, logged 17 Nov)
- swad_const is **not confirmed** on the registered headline. It stays in the benchmark table as a 5-seed row on cv5v3 with its numbers.
- The c3x combination (HRNet-W18 + swad_const, 25 runs, prepared and reviewed) still runs as registered: its own rule decides the final-model candidate and falls back to "the best confirmed single arm" when the combination does not pass; cv02 has no other prepared work, so it costs only otherwise idle GPU time (S).
- For the thesis (S): the result shows a consistent strict-IoU and precision gain from weight averaging that the tolerance-based headline does not reward; this is a finding about the metric choice as much as about the method, and is reported as such, not as a confirmed gain.

## 5. Limits
- One machine (cv02), one split (cv5v3), 5 seeds; argmax and width-matched operating points only.
- The carry rule was widened with the screen's ARTS width values known (review note); it did not come into play.
- The guards and the headline are judged on point values and intervals as written; no post-hoc metric was promoted.
