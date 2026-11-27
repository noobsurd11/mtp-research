# U2 / U4 reads: wave 2a arms on unseen-module views and half-cells (lead, 21 Nov 2026)

**All descriptive.** Rule: results/stageB/B3.md (R0, rule 3: with no confirmed crack mover, no read can be a crack primary; a contrast "differs" only if |delta| >= M with its 95% interval excluding 0 at OP-A AND the frontier contrast has the same sign with its interval excluding 0; any interval holding 0 is "no information"). U2 is an upper bound (simulated unseen-module views; gamed for scale-changing arms, which none of these is). U4 is label-free volume and the 19 H36 crack-free cells.

Runs: gaint, cv5v2, PF = W1-G seeds 5 to 8; arms = wave 2a seed-5 runs (EMA and SWAD runs with two readouts each: `model` = last iterate, `*_bn` = the averaged weights with BN re-estimated). Dumps: bq/udev_infer (174 of 174 rc 0, 19 Nov 01:21). Reads 19 Nov 01:23 to 01:28 (run_u2u4.sh; bench_udev_read.py ff033a62, bench_labelfree.py ca9af858, from bench_wt_b b5bf0ae, clean). Tables: results/stageB/u2u4_read/ (MD5.txt d6452ede). E = measured, S = judgement.

## U2 (1,064 views of 532 cells, 330 groups, effective n crack 20.6; A/A M relF1@2 0.0115, frontier 0.0212)
| Arm - PF | relF1@2 OP-A | frontier relR@2 (width B/A) | strict crack IoU | inactive IoU | reading |
|---|---|---|---|---|---|
| SWADBN | +0.0128 [+0.0021, +0.0232] | +0.0353 [+0.0157, +0.0536] (1.29) | +0.0279 [+0.0199, +0.0367] | -0.016, n.i. | differs, above (wider) |
| SOFTBAND | +0.0061, n.i. | -0.0009, n.i. (0.95) | +0.0067, n.i. | +0.042, n.i. | no information |
| JMLHARD | -0.0008, n.i. | -0.0015, n.i. | +0.0005 | -0.029, n.i. | no information |
| RCS | -0.0008, n.i. | -0.0068, n.i. | -0.0078 | -0.022, n.i. | no information |
| EMA (model) | -0.0042, n.i. | -0.0130, n.i. | -0.0048 | +0.012, n.i. | no information |
| EMABN | -0.0147 [-0.0265, -0.0049] | -0.0207 [-0.0418, -0.0011] | -0.0065, n.i. | -0.007, n.i. | differs, below |
| SWAD (model, last iterate) | -0.0156 [-0.0285, -0.0045] | -0.0179 [-0.0402, +0.0016] | -0.0088, n.i. | -0.059 [-0.119, -0.006] | no information (frontier holds 0) |
PF levels on U2: crack IoU 0.311, relF1@2 0.769 (against 0.846 on the plain CV5 cells), inactive IoU 0.369.

## U4 (label-free; pooled predicted crack px per cell, ratio to PF)
| Arm | H36 (36 cells) | pool half p0 / p1 / p2 / p3 | H36 crack-free cells: false crack px per cell (runs with any) |
|---|---|---|---|
| PF | 1.00 | 1.00 each | 3.3 (20 of 20) |
| SWADBN | 1.32 | 1.53 / 0.99 / 1.52 / 1.42 | 3.5 (3 of 5) |
| SOFTBAND | 1.06 | 1.36 / 0.74 / 0.93 / 0.99 | 1.3 (3 of 5) |
| EMABN | 0.75 | 0.80 / 0.65 / 0.93 / 0.86 | 1.6 (3 of 5) |
| JMLHARD | 0.82 | 0.91 / 0.83 / 0.75 / 1.08 | 2.6 (5 of 5) |
| RCS | 2.46 | 1.68 / 2.61 / 3.00 / 2.00 | 10.1 (5 of 5) |
| SWAD (model) | 3.14 | 3.69 / 2.16 / 3.60 / 2.64 | 10.1 (4 of 5) |

## Reading (S)
- The weight-averaged readout (SWADBN) is the only wave 2a arm that also gains on the unseen-module views (+0.013 relF1@2, +0.028 crack IoU), but it draws cracks about 1.3 x wider there and predicts up to 1.5 x more crack volume on half-cells; its H36 false alarms stay at PF's level. This matches the CV5 picture (gain plus ARTS width flag) and supports keeping a width guard on any SWAD-based final model.
- The SWAD run's last-iterate readout and RCS predict 2 to 3.7 x more crack on half-cells and 3 x more false crack on crack-free half-cells: half-cell false-alarm behaviour is a real risk for some training changes, and E1 (about 60 half-cut cells) is where it would show.
- U2 costs PF about 0.08 relF1@2 against plain CV5 cells, the simulated part of the unseen-source gap (U1 measured about 0.11 on real held-out sources).
- Not read here: the TTA side of U2 (one TTA dump job failed on 18 Nov; its re-run waits for the ttafix review; U2 is an upper bound for TTA anyway).
