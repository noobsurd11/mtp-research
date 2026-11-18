# Benchmark rows tranche 2: PRELIMINARY read (lead, 16 Nov 2026, 14:05 IST)

**Superseded on 16 Nov 19:14 IST by `ROWS2_READ.md`** (skr01 at 2 seeds: screen fail; HRNet numbers unchanged; segformer still open at 2 seeds).

Status: preliminary. 27 of 30 rows 2 runs were relayed when this was read. Only arms with all five folds are in it: **hrnet_w18_unetpp_pf seeds 5 and 6 (complete for the screen)**, segformer_mitb2_pf seed 5 only, skr01_pf_v11 seed 5 only. Missing: segformer f4 s6 (trained; its dump waits for cv02 GPU 2), skr01 f3 s6 (training), skr01 f4 s6 (waits for a lane). The full read (`results/ROWS2_READ.md`) replaces this file; the HRNet numbers will not change in it.

Tools: reviewed read tools at `bench_wt_b` b5bf0ae (`bench_read_w1.py` fdb56b78), run 13:57 to 14:02 by `harness/w1read/run_read_rows2_prelim.sh`. Tables: `results/rows2_prelim_read/` (read.txt = 532 cells, read_x416.txt = 416 clean cells, MD5.txt). Inputs: cv02 runs only (relayed, checksums equal), split cv5v2, out-of-fold predictions, label set v1.1, PF recipe, 20,000 steps, batch 8, 512 px. Comparator PF = 5 cv02 seeds. Clean cells = `benchmark/splits/score_exclude_v3.txt` (116 excluded). No sealed cell is in any number. E = measured, S = judgement.

## 1. Rows (E; argmax, mean over seeds)
| Row | Seeds | Strict crack IoU | Crack relF1@2 | relP@2 / relR@2 | Inactive IoU | mIoU-R13 | Width ratio |
|---|---|---|---|---|---|---|---|
| PF (comparator), U-Net++ / ResNet-34 | 5 | 0.365 | 0.844 | 0.894 / 0.799 | 0.503 | 0.612 | 1.00 |
| HOUSE (plain fine-tune) | 2 | 0.382 | 0.850 | 0.897 / 0.807 | 0.522 | 0.609 | 1.11 |
| **hrnet_w18_unetpp_pf**, U-Net++ / HRNet-W18 | 2 | 0.365 | **0.856** | 0.902 / 0.814 | 0.522 | 0.618 | 0.94 |
| segformer_mitb2_pf, SegFormer MiT-B2 | 1 | 0.350 | 0.843 | 0.880 / 0.809 | 0.551 | 0.609 | 1.21 |
| skr01_pf_v11, PF + Skeleton Recall loss | 1 | 0.373 | 0.849 | 0.883 / 0.818 | 0.477 | 0.612 | 1.14 |

On the 416 clean cells: PF 0.347 / 0.826 / 0.505 / 0.604 (crack IoU / relF1@2 / inactive / mIoU-R13); HOUSE 0.366 / 0.831 / 0.523 / 0.601; hrnet 0.346 / 0.838 / 0.516 / 0.609; segformer 0.338 / 0.828 / 0.549 / 0.602; skr01 0.356 / 0.831 / 0.474 / 0.603.

## 2. HRNet-W18 U-Net++ against PF (E; 2 seeds against 5; two-stage group bootstrap, 95% CI)
| Metric | Argmax (OP-A) | Width-matched (OP-W) | Argmax, 416 clean cells | Width-matched, 416 clean cells |
|---|---|---|---|---|
| crack relF1@2 (headline) | **+0.0114 [+0.0032, +0.0203]** | **+0.0128 [+0.0041, +0.0221]** | **+0.0118 [+0.0017, +0.0228]** | **+0.0130 [+0.0021, +0.0245]** |
| crack relR@2 | +0.0145 [+0.0034, +0.0276] | +0.0234 [+0.0119, +0.0371] | +0.0146 [+0.0019, +0.0297] | +0.0231 [+0.0099, +0.0384] |
| crack relP@2 | +0.0076 [-0.0049, +0.0216] | -0.0002 [-0.0124, +0.0130] | +0.0082 [-0.0075, +0.0261] | +0.0001 [-0.0150, +0.0181] |
| strict crack IoU | +0.0003 [-0.0077, +0.0087] | +0.0049 [-0.0035, +0.0138] | -0.0013 [-0.0098, +0.0078] | +0.0030 [-0.0067, +0.0128] |
| inactive IoU | +0.0190 [-0.0331, +0.0844] | +0.0170 [-0.0344, +0.0835] | +0.0106 [-0.0468, +0.0738] | +0.0086 [-0.0478, +0.0719] |
| mIoU-R13 | +0.0056 [-0.0017, +0.0136] | +0.0058 [-0.0015, +0.0139] | +0.0047 [-0.0032, +0.0128] | +0.0049 [-0.0030, +0.0130] |

- **Screen: PASS on the headline metric at both operating points, on all cells and on the clean cells** (margin M 0.010 on 532 cells, 0.0111 on the clean cells; lower CI end above 0). This is the first row or arm under the new protocol to pass on relF1@2.
- The gain is recall at equal precision: width-matched, HRNet finds 2.3 points more of the crack length (relR@2) at the same relP@2.
- Guards: width ratio 0.94 pooled; per source against PF 1.05 (ARTS), 0.99 (BMRK), 0.92 (CFVS), 0.95 (CSIR), all inside the 0.85 to 1.15 band. Cells with at least 50 false crack px among crack-free cells: 1.3% against PF 0.8%, inside the A/A margin (0.015); false crack px 695 (sd 461 over the two seeds) against 357, to be watched at 5 seeds. Inactive IoU and mIoU-R13 not worse.
- Per source, relF1@2 (hrnet / PF): ARTS 0.859 / 0.821, BMRK 0.861 / 0.835, CFVS 0.869 / 0.859, CSIR 0.800 / 0.799. Mono 0.872, multi 0.805 (PF 0.864, 0.791).
- Cost: 20.8 M parameters, 218 GFLOPs (1.47 x the house model), about 1.8 x the training time per step.
- Strict crack IoU does not move: HRNet draws cracks 6% thinner than PF at argmax, and the tolerance metric is what gains.
- **Ruling (protocol section 5: a screen pass is a promotion to a 5-seed confirmation, never a result; item 11: the final 5-seed table is trained on cv5v3):** hrnet_w18_unetpp_pf goes to a 5-seed row on cv5v3 on cv02 (seeds 5 to 9, 25 runs), read against the c3base PF and HOUSE rows.

## 3. SegFormer MiT-B2 and the Skeleton Recall anchor (E; one seed each, so descriptive only)
- **segformer_mitb2_pf (seed 5):** strict crack IoU -0.0152 [-0.0318, +0.0023] at argmax and -0.0302 [-0.0468, -0.0135] width-matched; relF1@2 -0.0010 / -0.0127 [-0.0240, -0.0005]; it draws cracks 21% wider than labelled. Inactive IoU +0.048 [-0.010, +0.116], inside the inactive margin (0.05). Reading (S): weaker on cracks (output stride 4 decoder), possibly better on inactive area; the second seed decides whether the inactive side is worth a count-based read.
- **skr01_pf_v11 (seed 5):** at argmax relR@2 +0.0182 [+0.0076, +0.0301] and strict IoU +0.0077 [+0.0020, +0.0146], with cracks 14% wider; width-matched everything is inside M (strict IoU -0.0001, relF1@2 +0.0030, relR@2 +0.0018). Reading (S): the recall gain is wider drawing, as in the earlier Skeleton Recall work; no gain shown.

## 4. Limits
- 2 seeds (hrnet) and 1 seed (the other two): screen reads. One machine. Pool cells from known modules only; nothing here says how HRNet behaves on unseen modules.
- cv5v2 has the known module leak; the clean-cell columns remove the 116 affected cells.
