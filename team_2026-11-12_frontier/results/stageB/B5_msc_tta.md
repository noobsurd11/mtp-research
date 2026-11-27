# msc_tta CV5 read: test-time augmentation on the W1-G PF models (lead, 18 Nov 2026, 19:20 IST)

**Verdict (19 Nov 01:25 IST): score claim PASS on all three parts: msc_tta (D4MS) counts as a non-inferior score arm** (rule section 1: "If 1 to 3 hold, msc_tta counts as a non-inferior score arm"). Parts 1 and 2 on CV5 (18 Nov 19:09), part 3 on H36 and the pool half-cells (19 Nov 01:21, after udev_infer's plain dumps; tables results/stageB/b5_part3_read/, MD5.txt 70734dbd).

Rule: results/stageB/B5_tta_module.md section 1 (written 15 Nov 14:40, before any TTA number). Runs: gaint queue bq/udev_tta (80 dump jobs, deploy ae4dd10, cuda fp32, armed 18 Nov 16:13 after the pathfinder: peak 4,080 MiB, 52 s for 107 cells; chain done 18:55:24, 79 rc 0; the one failed job is a U2 line, tta_d4_shvoof_f1_w1g_pf_v11_f1_s5, dump self-check, cause under investigation; U2 decides nothing). Read: /home/noob/work/bench_reads/stageB/B5/run_cv5_read.sh (b9927942) = jobs_tta/PREP.md commands, 19:01 to 19:09 on gaint CPU, from bench_wt_b b5bf0ae (bench_read_w1.py fdb56b78, bench_ens_dump.py 80f93914, both equal to the deploy's), worktree clean. Tables: results/stageB/b5_cv5_read/ (read.txt = 532 cells, read_x416.txt = 416 clean cells beside, read.json, run.log, the script, MD5.txt). E = measured, S = judgement.

Arms (same W1-G checkpoints, split cv5v2, 532 out-of-fold cells): PLAIN = existing dumps, seeds 5, 6; D4 = 8 views (flips and rotations), seeds 5, 6; D4MS = 24 views (D4 x scales 0.75, 1.0, 1.25), seeds 5, 6; D4ENS3 = mean of the D4 dumps of seeds 5, 6, 7 (24 forward passes per cell, equal cost to D4MS). M = 0.010 (rule: gaint's M from ROWS1_READ; this read has no A/A).

## Score claim (E)
| Part | Rule | Value | Result |
|---|---|---|---|
| 1 | D4MS - PLAIN relF1@2 >= -M at OP-A / OP-W | +0.0142 [+0.0079, +0.0202] / +0.0157 [+0.0096, +0.0215] | PASS |
| 1 | D4MS - PLAIN strict crack IoU >= -M at OP-A / OP-W | +0.0262 [+0.0191, +0.0343] / +0.0276 [+0.0206, +0.0362] | PASS |
| 2 | width ratio D4MS / PLAIN within 0.85 to 1.15, OP-A, pooled and per source (n >= 40) | pooled 0.968; ARTS 0.912, BMRK 0.922, CFVS 0.986, CSIR 0.933 | PASS |
| 3 | pooled predicted crack px D4MS / PLAIN <= 1.5 on H36 and on pool_half_p0..3 | H36 0.179; pool p0 0.276, p1 0.176, p2 0.236, p3 0.316 (D4 beside: 0.319; 0.513, 0.295, 0.360, 0.434) | PASS |

Part 3 detail (E, bench_labelfree.py ca9af858 from bench_wt_b, run_part3.sh 1fbd1493): on the 19 H36 cells labelled crack-free, false crack px per cell PLAIN 0.8 to 8.7 per run, D4 0 in 9 of 10 runs (1.7 in one), D4MS 0 in 9 of 10 (1.1 in one). TTA also raises the label-free "unsure px" count per cell (H36 PLAIN 4 to 10, D4 25 to 68, D4MS 84 to 293).

## Levels (E, OP-A, 532 cells, mean of 2 seeds; D4ENS3 one ensemble)
| | crack IoU | relF1@2 | relP@2 / relR@2 | inactive IoU | mIoU-R13 | false crack px on crack-free cells (read.txt column fa_px) |
|---|---|---|---|---|---|---|
| PLAIN | 0.3624 | 0.8417 | 0.893 / 0.796 | 0.4980 | 0.6117 | 301 |
| D4 (8 views) | 0.3894 | 0.8589 | 0.917 / 0.808 | 0.5228 | 0.6197 | 34 |
| D4MS (24 views) | 0.3887 | 0.8558 | 0.926 / 0.796 | 0.5382 | 0.6175 | 66 |
| D4ENS3 (3 seeds x D4) | 0.3923 | 0.8606 | 0.920 / 0.809 | 0.5371 | 0.6225 | 23 |

Printed beside, deciding nothing (E): D4 - PLAIN relF1@2 +0.0173 [+0.0115, +0.0230], crack IoU +0.0270 [+0.0208, +0.0344], mIoU-R13 +0.0080 [+0.0018, +0.0147], inactive IoU +0.0247 [-0.0216, +0.0781] (equal at OP-A and OP-W); D4MS - D4 relF1@2 -0.0031 [-0.0088, +0.0026], crack IoU -0.0008, width -0.049 [-0.073, -0.021] (the scale views draw cracks thinner); D4MS - D4ENS3 relF1@2 -0.0048 [-0.0092, -0.0009], mIoU-R13 -0.0050 [-0.0091, -0.0008]. 416 clean cells: D4MS - PLAIN relF1@2 +0.0132 [+0.0051, +0.0210], crack IoU +0.0242 [+0.0169, +0.0313]; D4 - PLAIN relF1@2 +0.0173 [+0.0104, +0.0245], crack IoU +0.0260 [+0.0197, +0.0323].

## Reading (S)
- Test-time augmentation is the largest crack gain this benchmark has measured: about +0.015 relF1@2 and +0.027 strict crack IoU over plain inference with intervals well above 0, at OP-A and OP-W, on 532 and on 416 cells; false crack pixels on crack-free cells fall from about 300 to 23 to 66. It needs no training, only 8 to 24 forward passes per cell.
- The scale views add nothing over the 8 flip and rotation views (D4MS - D4 about 0 on cracks, thinner widths); at equal cost, 3 seeds x D4 beats 1 seed x D4MS. The practical choice for the final model is S: D4 views on an ensemble of seeds, but only D4MS is the registered score arm; D4 and D4ENS3 are printed beside and would need their own registered rule (or the final-model rule) to be claimed.
- The spec expected -0.005 to +0.01 relF1@2 (Y10); the measured gain is above that range.

- Part 3 caps volume increases only. On half-cells TTA predicts 0.18 to 0.51 times the plain crack volume, and false alarms on crack-free half-cells go to about 0; whether it also misses true half-cell cracks cannot be told without labels (S: a fair question for the E1 opening, whose half-cut context is where cracks were hardest).

## Owed
1. (done 19 Nov 01:21) Part 3 guards.
2. U2 (upper bound, deciding nothing): after udev_infer and the re-run of the failed U2 job (fix under review first).
3. F51 (descriptive): udev_tta_f51 after stage A7's plain F51 dumps.

## Limits
2 seeds of one model family (W1-G PF, ResNet-34 UNet++), one machine (gaint), split cv5v2; not yet tested on the cv02 HRNet or cv5v3 models.
