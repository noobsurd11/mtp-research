# c3x read: HRNet-W18 U-Net++ + weight averaging (swad_const) on cv5v3 (lead, 19 Nov 2026, 01:20 IST)

**Verdict (registered, harness/LAUNCH_REQUEST_c3x.md section 6; rule fixed 17 Nov before any c3x run): NOT CONFIRMED, reported as a gain with the failing guards named.** The primary readout COMBO (swad_bn) passes the headline on both cell sets but fails the ARTS width band and the false-crack-pixel guard. **COMBO is not the final-model candidate under this rule**; its fallback, the best confirmed single arm, has no confirmed arm to name (HRNet and SWAD were both NOT CONFIRMED).

Read: harness/c3x/run_read_c3x.sh (060e24a2 = request line 128), run once, 18 Nov 19:23:00 to 19:36:21 on gaint CPU, rc 0, bench_wt_final 89b9ea5 clean (bench_read_w1.py fdb56b78); C3X 03375d4; manifest check 125 dumps, one device (NVIDIA RTX A6000, cv02), one writer (bench_infer.py afd91642). Arms, all cv02, split cv5v3, seeds 5 to 9, folds 0 to 4: PF c3_pf_v11 (baseline, A/A {5,6} v {7,8}), HRNET c3h_hrnet_w18_unetpp_pf, SWADBN c3s_swad_v11 (swad_bn), COMBO c3x_hrnet_swad_v11 (swad_bn, primary), COMBO_SWAD the same runs' swad readout (declared secondary). Cells: 532 and the 416 clean cells (score_exclude_v3). Tables: results/c3x_read/ (read.txt, read_x416.txt, read.json, verdict.txt, class_guard.txt, expected_dumps.tsv, run.log, MD5_read_folder.txt, MD5.txt). E = measured, S = judgement.

## Levels (E, OP-A, mean over 5 seeds)
| Arm | crack IoU | relF1@2 | inactive IoU | mIoU-R13 | false crack px on crack-free cells | crack component recall (any hit) |
|---|---|---|---|---|---|---|
| PF | 0.3653 | 0.8463 | 0.5042 | 0.6116 | 212 | 0.884 |
| HRNET | 0.3661 | 0.8567 | 0.5142 | 0.6138 | 767 | 0.908 |
| SWADBN | 0.3834 | 0.8532 | 0.5196 | 0.6189 | 339 | 0.891 |
| COMBO | 0.3753 | 0.8617 | 0.5042 | 0.6182 | 384 | 0.910 |
| COMBO_SWAD | 0.3814 | 0.8629 | 0.5203 | 0.6189 | 213 | 0.903 |
416 clean cells, relF1@2: PF 0.8264, HRNET 0.8379, SWADBN 0.8362, COMBO 0.8431, COMBO_SWAD 0.8439.

## Verdict lines (E, verdict.txt)
| | COMBO (primary) | COMBO_SWAD (secondary) |
|---|---|---|
| relF1@2 - PF, 532, OP-A / OP-W | +0.0154 [+0.0065, +0.0260] / +0.0158 | +0.0166 [+0.0082, +0.0263] / +0.0173 |
| relF1@2 - PF, 416, OP-A / OP-W | +0.0167 [+0.0055, +0.0298] / +0.0166 | +0.0176 [+0.0071, +0.0300] / +0.0180 |
| width pooled | 0.991 to 1.003, PASS | 0.980 to 1.000, PASS |
| width ARTS (band 0.85 to 1.15) | 1.174 / 1.186 (532), 1.239 / 1.242 (416): FAIL | 1.126 / 1.149 (532) PASS; 1.185 / 1.202 (416) FAIL |
| false crack px vs PF (max 1.5 x) | 1.81 / 1.84 (532), 1.67 / 1.62 (416): FAIL | 1.01 / 1.06 (532), 0.87 / 0.88 (416): PASS |
| inactive IoU - PF | -0.0001 (532), PASS | +0.0161 (532), PASS |
| mIoU-R13 - PF | +0.0066 [-0.0003, +0.0144], PASS | +0.0073 [+0.0005, +0.0150], PASS |
| failing guard items | 8 | 2 (ARTS width, 416 cells) |
A/A (532): relF1@2 delta -0.0002, SE 0.0037, M 0.0100. Per-seed relF1@2 COMBO - PF, 532 OP-A: +0.0138, +0.0201, +0.0163, +0.0136, +0.0134 (all five seeds positive; COMBO_SWAD +0.0141 to +0.0215).
Secondary contrasts (pre-declared): COMBO - HRNET +0.0050 [-0.0041, +0.0141] and COMBO - SWADBN +0.0085 [-0.0017, +0.0183] at OP-A: NO LOSS (the combination does not add a confirmed step over either part).

## Reading (S)
- The combination gives the largest trained-model crack gain on the corrected split (about +0.015 to +0.017 relF1@2, every seed positive), but the swad_bn readout buys it with more false crack pixels and wider ARTS cracks, as HRNet alone did.
- The swad readout of the same runs keeps PF's false-alarm level and widens ARTS cracks less; it fails only ARTS width on the 416 clean cells. It was declared secondary, so it cannot be claimed from this read. Choosing it now as the base of the final model is a post hoc choice: its CV5 numbers on these cells are selection-biased, and its claim needs a fresh test (registered in harness/final/FINAL_RULE.md, being built 19 Nov, with a sealed-set opening for the unbiased number).
- The ARTS width failures look like an annotation-convention issue as much as a model issue (ARTS labels are thinner than the model draws, PF itself 0.868); the dataset audit (dataset_audit/, started 19 Nov) measures per-source label widths.

## Next (lead)
- Final model package (harness/final/, final_builder): D4 test-time augmentation on the c3x and PF runs of cv5v3, then full-pool models of the candidate and PF; registered rule before any number.
