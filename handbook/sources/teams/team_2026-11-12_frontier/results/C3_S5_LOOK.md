# First look on the corrected split cv5v3: seed 5, HRNet-W18 U-Net++ against PF (lead, 16 Nov 2026, 21:06 IST)

Status: **descriptive, 1 seed per row, no verdict.** The confirmation is the 5-seed read of both rows on cv5v3 (seeds 5 to 9, comparators PF and HOUSE), and only that read decides. This file shows whether the first complete seed on cv5v3 looks like the cv5v2 screen (`ROWS2_READ.md`: screen pass, +0.0114 / +0.0128 relF1@2 at 2 seeds against 5).

Tools: reviewed tree `bench_wt_final` 89b9ea5 (`bench_read_w1.py` fdb56b78), run 21:01 to 21:03 by `harness/w1read/run_read_c3_s5.sh` (264ae842), with `--groups cv5v3_groups.tsv` (d880a769). Tables: `results/c3_s5_look/` (read.txt = 532 cells, read_x416.txt = 416 clean cells, read.json, run.log, MD5.txt). Inputs: 10 cv02 runs (relayed, checksums equal), `c3_pf_v11_f[0-4]_s5` and `c3h_hrnet_w18_unetpp_pf_f[0-4]_s5`; split cv5v3 (the module leak is removed at the split), out-of-fold predictions on the 532 pool cells, label set v1.1, PF recipe, 20,000 steps, batch 8, 512 px. Clean cells = `benchmark/splits/score_exclude_v3.txt` (116 excluded). The cv5v2 seed 5 values come from `results/rows2_read/read.json` (per_seed). No sealed cell is in any number. E = measured, S = judgement.

## 1. Rows at seed 5 (E; argmax)
| Split | Row | Strict crack IoU | Crack relF1@2 | relP@2 / relR@2 | Inactive IoU | mIoU-R13 | Width ratio |
|---|---|---|---|---|---|---|---|
| cv5v3 | PF, U-Net++ / ResNet-34 | 0.366 | 0.849 | 0.895 / 0.807 | 0.505 | 0.615 | 1.03 |
| cv5v3 | **hrnet_w18_unetpp_pf** | 0.363 | **0.859** | 0.905 / 0.818 | 0.520 | 0.614 | 0.96 |
| cv5v2 | PF (seed 5 of 5) | 0.367 | 0.846 | 0.896 / 0.801 | 0.490 | 0.612 | 0.99 |
| cv5v2 | hrnet_w18_unetpp_pf (seed 5 of 2) | 0.363 | 0.853 | 0.895 / 0.814 | 0.501 | 0.615 | 0.95 |

On the 416 clean cells (crack IoU / relF1@2 / inactive / mIoU-R13): cv5v3 PF 0.347 / 0.828 / 0.500 / 0.609, HRNet 0.348 / 0.842 / 0.514 / 0.606; cv5v2 seed 5 PF 0.350 / 0.829 / 0.490 / 0.604, HRNet 0.344 / 0.835 / 0.494 / 0.607.

## 2. HRNet minus PF at seed 5 (E)
cv5v3 columns: difference with the 95% interval of the module bootstrap (see Limits: it holds no seed-to-seed variation). cv5v2 columns: point differences of the two seed 5 trainings, argmax / width-matched, no interval.

| Metric | cv5v3, argmax (OP-A) | cv5v3, width-matched (OP-W) | cv5v3, argmax, 416 clean | cv5v3, width-matched, 416 clean | cv5v2 seed 5, 532 | cv5v2 seed 5, 416 clean |
|---|---|---|---|---|---|---|
| crack relF1@2 (headline) | **+0.0105 [+0.0040, +0.0180]** | **+0.0126 [+0.0054, +0.0209]** | **+0.0145 [+0.0064, +0.0232]** | **+0.0163 [+0.0075, +0.0255]** | +0.0070 / +0.0079 | +0.0062 / +0.0065 |
| crack relR@2 | +0.0108 [-0.0001, +0.0231] | +0.0225 [+0.0110, +0.0356] | +0.0147 [+0.0012, +0.0297] | +0.0244 [+0.0100, +0.0402] | +0.0136 / +0.0201 | +0.0142 / +0.0196 |
| crack relP@2 | +0.0102 [+0.0027, +0.0181] | +0.0008 [-0.0077, +0.0086] | +0.0141 [+0.0040, +0.0235] | +0.0058 [-0.0052, +0.0153] | -0.0011 / -0.0070 | -0.0040 / -0.0099 |
| strict crack IoU | -0.0030 [-0.0103, +0.0055] | +0.0033 [-0.0045, +0.0124] | +0.0005 [-0.0081, +0.0109] | +0.0058 [-0.0033, +0.0169] | -0.0045 / -0.0010 | -0.0062 / -0.0036 |
| inactive IoU | +0.0157 [-0.0172, +0.0466] | +0.0131 [-0.0198, +0.0438] | +0.0140 [-0.0208, +0.0494] | +0.0117 [-0.0235, +0.0475] | +0.0105 / +0.0089 | +0.0041 / +0.0025 |
| mIoU-R13 | -0.0012 [-0.0056, +0.0031] | -0.0010 [-0.0053, +0.0034] | -0.0022 [-0.0070, +0.0033] | -0.0020 [-0.0068, +0.0035] | +0.0038 / +0.0040 | +0.0028 / +0.0029 |

- The first cv5v3 seed points the same way as the cv5v2 screen: relF1@2 is higher for HRNet at both operating points, on all cells and on the clean cells (+0.011 to +0.016 here; the 2-seed cv5v2 read gave +0.011 to +0.013). Seed 5 alone on cv5v2 gave +0.006 to +0.008, so the single-seed values scatter by several thousandths.
- Width-matched, the difference is recall at equal precision: relR@2 +0.023, relP@2 +0.001. On the bias curve, at PF's own precision, HRNet's relR@2 is 0.830 against 0.807 (532 cells) and 0.806 against 0.776 (clean cells); cv5v2 seed 5: 0.813 against 0.801 and 0.788 against 0.778.
- Per source, relF1@2 at argmax (HRNet / PF): ARTS 0.865 / 0.831, BMRK 0.862 / 0.838, CFVS 0.873 / 0.864, CSIR 0.803 / 0.803 (cv5v2 seed 5: 0.862 / 0.830, 0.856 / 0.834, 0.868 / 0.861, 0.794 / 0.799). In both splits the gain sits on ARTS, BMRK and CFVS and is absent on CSIR. SDLE has 17 cells (0.923 / 0.949).
- Strict crack IoU, inactive IoU and mIoU-R13 do not differ (intervals include 0), as in the screen.
- Guards, to be checked on the 5-seed means (E, single values at one seed):
  - Width against PF, pooled: 0.93 at argmax, 1.00 width-matched; inside the 0.85 to 1.15 band.
  - Width against PF per source: CSIR at argmax 0.838 (532 cells) and 0.850 (clean cells), at the lower edge of the band; cv5v2 seed 5 had 0.98. ARTS width-matched 1.150, at the upper edge; cv5v2 seed 5 had 1.10. BMRK 0.97 / 1.03 and CFVS 0.94 / 1.01 are inside. HRNet draws CSIR cracks thinner and ARTS cracks wider than PF; part of the CSIR value is PF's own width there moving from 0.88 (cv5v2) to 0.98 (cv5v3) at this seed.
  - False crack on the 303 crack-free cells: 1 cell with at least 50 false crack px at argmax and 2 width-matched, against 0 for PF; false crack px 298 against 144. Inside the A/A margin of the cv5v2 read (0.015 share).

## 3. PF on cv5v3 beside cv5v2 (E; not a leakage read)
PF at seed 5: relF1@2 0.8485 on cv5v3 against 0.8459 on cv5v2 (532 cells), 0.8276 against 0.8292 on the clean cells; strict crack IoU 0.3658 against 0.3671; inactive IoU 0.5046 against 0.4904; mIoU-R13 0.6151 against 0.6116. These are two separate trainings at one seed, and PF's seed sd of relF1@2 on cv5v2 is 0.002 (0.003 on the clean cells). The size of the cv5v2 module leak is decided only by the pre-registered read of `harness/LAUNCH_REQUEST_c3base.md` section 7 (PF seeds 5 to 9 and HOUSE seeds 5, 6 on both splits, `bench_leak_did.py`); nothing in this file is an estimate of it.

## 4. Limits
- One seed per row. With one seed per arm the two-stage bootstrap has no seed to draw, so the interval is the module-group resampling alone (2,000 draws) and holds no seed-to-seed variation. On cv5v2 the seed sd of relF1@2 is 0.002 for PF (5 seeds) and 0.004 for HRNet (2 seeds), which adds roughly 0.004 to 0.005 of noise to a single-seed difference. The intervals above are therefore too narrow for a decision.
- No A/A margin from this read (it needs PF seeds 5 to 8 on cv5v3); M 0.010 (0.0111 on the clean cells) is the cv5v2 value and is not applied here.
- One machine (cv02, RTX A6000). Pool cells from known modules only; nothing here says how HRNet behaves on unseen modules.
- Next: the 5-seed read on cv5v3. The merged cv02 queue holds 70 runs (PF 23, HOUSE 25, HRNet 22 beside the 5 finished in the first queues); 6 of them were trained at 20:50.
