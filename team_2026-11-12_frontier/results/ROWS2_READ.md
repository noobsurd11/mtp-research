# Benchmark rows tranche 2: read (lead, 16 Nov 2026, 19:14 IST; SegFormer completed 17 Nov 2026, 15:30 IST)

Status (17 Nov): **all three rows are read at the full screen (2 seeds x 5 folds). hrnet_w18_unetpp_pf: SCREEN PASS (5-seed confirmation running). skr01_pf_v11: SCREEN FAIL, closed. segformer_mitb2_pf: SCREEN FAIL, closed (section 4).** All 30 rows 2 runs are relayed. The last one, r2_segformer_mitb2_pf_f4_s6, had waited for its dump since 16 Nov because another lab user held cv02 GPU 2; on 17 Nov 15:12 the reviewed rescue tool ran that dump on GPU 5 (same GPU model, same command, strict lane rule). Sections 1 (SegFormer row) and 4 were rewritten on 17 Nov from the `SEG6=1` read; sections 2 and 3 are unchanged and their numbers are identical in the new read (checked by diff of the contrast lines). This file replaces `ROWS2_PRELIM.md`.

Tools: reviewed read tools at `bench_wt_b` b5bf0ae (`bench_read_w1.py` fdb56b78), run 19:08 to 19:12 by `harness/w1read/run_read_rows2.sh` (78f9f6b8). Tables: `results/rows2_read/` (read.txt = 532 cells, read_x416.txt = 416 clean cells, read.json, run.log, MD5.txt). The 17 Nov read with both SegFormer seeds (same script and tools, `SEG6=1`, run 15:20 to 15:24): `results/rows2_full_read/` (read.txt d59e6e70, read_x416.txt 341b5980). Inputs: cv02 runs only (relayed, checksums equal), split cv5v2, out-of-fold predictions, label set v1.1, PF recipe, 20,000 steps, batch 8, 512 px. Comparator PF = 5 cv02 seeds. Clean cells = `benchmark/splits/score_exclude_v3.txt` (116 excluded). No sealed cell is in any number. E = measured, S = judgement.

## 1. Rows (E; argmax, mean over seeds)
| Row | Seeds | Strict crack IoU | Crack relF1@2 | relP@2 / relR@2 | Inactive IoU | mIoU-R13 | Width ratio |
|---|---|---|---|---|---|---|---|
| PF (comparator), U-Net++ / ResNet-34 | 5 | 0.365 | 0.844 | 0.894 / 0.799 | 0.503 | 0.612 | 1.00 |
| HOUSE (plain fine-tune) | 2 | 0.382 | 0.850 | 0.897 / 0.807 | 0.522 | 0.609 | 1.11 |
| **hrnet_w18_unetpp_pf**, U-Net++ / HRNet-W18 | 2 | 0.365 | **0.856** | 0.902 / 0.814 | 0.522 | 0.618 | 0.94 |
| skr01_pf_v11, PF + Skeleton Recall loss | 2 | 0.372 | 0.848 | 0.884 / 0.815 | 0.480 | 0.611 | 1.13 |
| segformer_mitb2_pf, SegFormer MiT-B2 | 2 | 0.348 | 0.842 | 0.877 / 0.809 | 0.530 | 0.608 | 1.20 |

On the 416 clean cells (crack IoU / relF1@2 / inactive / mIoU-R13): PF 0.347 / 0.826 / 0.505 / 0.604; HOUSE 0.366 / 0.831 / 0.523 / 0.601; hrnet 0.346 / 0.838 / 0.516 / 0.609; skr01 0.356 / 0.831 / 0.482 / 0.604; segformer (2 seeds) 0.337 / 0.827 / 0.526 / 0.600.

## 2. HRNet-W18 U-Net++ against PF (E; 2 seeds against 5; two-stage group bootstrap, 95% CI): SCREEN PASS
| Metric | Argmax (OP-A) | Width-matched (OP-W) | Argmax, 416 clean cells | Width-matched, 416 clean cells |
|---|---|---|---|---|
| crack relF1@2 (headline) | **+0.0114 [+0.0032, +0.0203]** | **+0.0128 [+0.0041, +0.0221]** | **+0.0118 [+0.0017, +0.0228]** | **+0.0130 [+0.0021, +0.0245]** |
| crack relR@2 | +0.0145 [+0.0034, +0.0276] | +0.0234 [+0.0119, +0.0371] | +0.0146 [+0.0019, +0.0297] | +0.0231 [+0.0099, +0.0384] |
| crack relP@2 | +0.0076 [-0.0049, +0.0216] | -0.0002 [-0.0124, +0.0130] | +0.0082 [-0.0075, +0.0261] | +0.0001 [-0.0150, +0.0181] |
| strict crack IoU | +0.0003 [-0.0077, +0.0087] | +0.0049 [-0.0035, +0.0138] | -0.0013 [-0.0098, +0.0078] | +0.0030 [-0.0067, +0.0128] |
| inactive IoU | +0.0190 [-0.0331, +0.0844] | +0.0170 [-0.0344, +0.0835] | +0.0106 [-0.0468, +0.0738] | +0.0086 [-0.0478, +0.0719] |
| mIoU-R13 | +0.0056 [-0.0017, +0.0136] | +0.0058 [-0.0015, +0.0139] | +0.0047 [-0.0032, +0.0128] | +0.0049 [-0.0030, +0.0130] |

- **Screen: PASS on the headline metric at both operating points, on all cells and on the clean cells** (margin M 0.010 on 532 cells, 0.0111 on the clean cells; lower CI end above 0). First row or arm under the new protocol to pass on relF1@2.
- The gain is recall at equal precision: width-matched, HRNet finds 2.3 points more of the crack length (relR@2) at the same relP@2. On the bias curve, at PF's own precision, HRNet's relR@2 is 0.813 and 0.829 (seeds 5, 6) against PF 0.801 and 0.799.
- Guards: width ratio 0.94 pooled; per source against PF 1.05 (ARTS), 0.99 (BMRK), 0.92 (CFVS), 0.95 (CSIR), all inside the 0.85 to 1.15 band. Cells with at least 50 false crack px among crack-free cells: 1.3% against PF 0.8%, inside the A/A margin (0.015); false crack px 695 (sd 461 over the two seeds) against 357, to be watched at 5 seeds. Inactive IoU and mIoU-R13 not worse.
- Per source, relF1@2 (hrnet / PF): ARTS 0.859 / 0.821, BMRK 0.861 / 0.835, CFVS 0.869 / 0.859, CSIR 0.800 / 0.799. Mono 0.872, multi 0.805 (PF 0.864, 0.791).
- Cost: 20.8 M parameters, 218 GFLOPs (1.47 x the house model); measured on cv02 with three of our runs training, about 107 minutes per run against about 80 for PF.
- Strict crack IoU does not move: HRNet draws cracks 6% thinner than PF at argmax, and the tolerance metric is what gains.
- **Ruling (protocol section 5: a screen pass is a promotion to a 5-seed confirmation, never a result; item 11: the final 5-seed table is trained on cv5v3):** hrnet_w18_unetpp_pf runs as a 5-seed row on cv5v3 on cv02 (seeds 5 to 9, 25 runs; launched 16 Nov 14:08, since 14:59 inside the merged queue `c3all`), read against the cv5v3 PF and HOUSE rows.

## 3. Skeleton Recall anchor skr01_pf_v11 against PF (E; 2 seeds against 5): SCREEN FAIL, closed
| Metric | Argmax (OP-A) | Width-matched (OP-W) | Argmax, 416 clean cells | Width-matched, 416 clean cells |
|---|---|---|---|---|
| crack relF1@2 (headline) | +0.0039 [-0.0027, +0.0115] | +0.0022 [-0.0047, +0.0097] | +0.0046 [-0.0031, +0.0136] | +0.0028 [-0.0052, +0.0115] |
| crack relR@2 | +0.0159 [+0.0052, +0.0276] | +0.0010 [-0.0093, +0.0121] | +0.0155 [+0.0029, +0.0294] | +0.0017 [-0.0113, +0.0148] |
| crack relP@2 | -0.0107 [-0.0196, +0.0007] | +0.0036 [-0.0054, +0.0155] | -0.0092 [-0.0211, +0.0042] | +0.0042 [-0.0075, +0.0189] |
| strict crack IoU | +0.0068 [+0.0004, +0.0140] | -0.0001 [-0.0060, +0.0066] | +0.0089 [+0.0023, +0.0165] | +0.0020 [-0.0043, +0.0087] |
| inactive IoU | -0.0225 [-0.0698, +0.0180] | -0.0182 [-0.0667, +0.0232] | -0.0232 [-0.0731, +0.0234] | -0.0189 [-0.0695, +0.0287] |
| mIoU-R13 | -0.0008 [-0.0068, +0.0053] | -0.0010 [-0.0071, +0.0050] | -0.0008 [-0.0077, +0.0064] | -0.0010 [-0.0081, +0.0062] |

- **Screen: FAIL.** No metric gains M at both operating points. At argmax the recall gain (+0.016) comes with 12% wider cracks (width ratio 1.13 against PF 1.00; per source 1.13, 1.09, 1.13, 1.12, inside the band) and lower precision; strict IoU +0.007 stays under M. Width-matched, every crack metric is within 0.005 of PF. At PF's own precision the relR@2 is 0.804 and 0.802 against PF 0.801 and 0.799.
- Inactive IoU is 0.480 against 0.503; the interval includes 0 and the difference is inside the inactive margin (0.05).
- Reading (S): as in the earlier Skeleton Recall work, the loss moves the operating point (wider drawing) and not the frontier. The second seed agrees with the first. **Closed: no 5-seed row.** It stays in the benchmark table as a screened loss row on cv5v2.

## 4. SegFormer MiT-B2 against PF (E; 2 seeds against 5; read of 17 Nov): SCREEN FAIL, closed
| Metric | Argmax (OP-A) | Width-matched (OP-W) | Argmax, 416 clean cells | Width-matched, 416 clean cells |
|---|---|---|---|---|
| crack relF1@2 (headline) | -0.0026 [-0.0132, +0.0095] | -0.0135 [-0.0259, -0.0005] | +0.0008 [-0.0100, +0.0142] | -0.0101 [-0.0201, +0.0029] |
| crack relR@2 | +0.0094 [-0.0067, +0.0282] | -0.0248 [-0.0445, -0.0038] | | |
| crack relP@2 | -0.0172 [-0.0304, -0.0012] | +0.0014 [-0.0134, +0.0177] | | |
| strict crack IoU | -0.0170 [-0.0345, +0.0015] | -0.0312 [-0.0487, -0.0134] | -0.0105 [-0.0262, +0.0075] | -0.0263 [-0.0419, -0.0081] |
| inactive IoU | +0.0277 [-0.0342, +0.1061] | +0.0304 [-0.0311, +0.1091] | +0.0208 [-0.0407, +0.1041] | +0.0242 [-0.0376, +0.1084] |
| mIoU-R13 | -0.0045 [-0.0133, +0.0047] | -0.0055 [-0.0142, +0.0035] | -0.0043 [-0.0141, +0.0068] | -0.0054 [-0.0151, +0.0058] |

- **Screen: FAIL.** No metric gains its margin at both operating points (M 0.010 for crack metrics, 0.050 for inactive IoU on 532 cells). The headline is level at argmax and lower width-matched; strict crack IoU is lower at both, by 0.031 width-matched with the interval below 0.
- Width guard fails: it draws cracks 20% wider than labelled at argmax (width ratio 1.20 against PF 1.00); per source against PF 1.43 (ARTS), 1.16 (BMRK), 1.19 (CFVS), 1.21 (CSIR), all outside the 0.85 to 1.15 band. Once the width is matched it finds 2.5 points less of the crack length than PF at the same precision.
- False alarms on crack-free cells are not worse: share of cells with at least 50 false crack px 0.7% against PF 0.8%; false crack px 449 against 357 (1.26 x, inside the 1.5 x guard).
- Inactive IoU: +0.028 at argmax and +0.030 width-matched, interval includes 0, below the margin. With seed 5 alone it had been +0.048; the second seed is lower (mean 0.530, sd 0.029 over the two seeds).
- Reading (S): the output-stride-4 decoder costs thin-crack accuracy, and the possible inactive-area advantage of the first seed did not hold up. **Closed: no 5-seed row.** It stays in the benchmark table as a screened architecture row on cv5v2.

## 5. Limits
- 2 seeds per row: screen reads. One machine. Pool cells from known modules only; nothing here says how HRNet behaves on unseen modules.
- cv5v2 has the known module leak; the clean-cell columns remove the 116 affected cells. The cv5v3 rows now training remove it at the split.
