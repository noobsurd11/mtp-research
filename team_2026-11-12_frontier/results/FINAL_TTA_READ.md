# Final CV5 TTA read (fin): D4 on PF and on the HRNet+SWAD candidate (lead, 21 Nov 2026)

Rule: harness/final/FINAL_RULE.md (82867156) sections 2 to 4 and 7. Request LAUNCH_REQUEST_final.md c56dfee0 (review PASS, REVIEW_FINAL.md).
Inputs: cv5v3, 5 folds x 5 seeds per arm, 150 dumps (75 plain from the c3x / c3_pf runs, 75 D4 from queue fin on cv02, F 821dfad),
one device (RTX A6000), manifest check OK. Read run once 21 Nov 08:00:09 to 08:13:59 (run_read_final.sh a6e952ec, read tool
fdb56b78, verdict final_verdict.py 5acea6c4), rc 0, bench_wt_final clean. Tables: results/final_tta_read/ (verdict a95f89e8,
class_guard 57ef512a, read.txt 54214525; MD5_copy.txt). Arms: PF = c3_pf_v11 (model), CS = c3x HRNet+SWAD (swad readout),
CB = the same runs' swad_bn readout (information only); _D4 = 8-view flip/rotation TTA. relF1@2 decides; strict crack IoU is
printed with its convention band +-0.019 and decides nothing. **Every CS / CS_D4 number on these cells is selection-biased**: the
swad readout was chosen after the c3x read on the same cells; the unbiased test is the E1 opening.

## Pre-registered decisions (E)
| Item | Contrast | relF1@2, 532 cells, OP-A [95% CI] | 416 clean cells | Guards | Decision |
|---|---|---|---|---|---|
| (a) | PF_D4 - PF | +0.0134 [+0.0066, +0.0207] | +0.0132 [+0.0047, +0.0220] | all pass (width 1.02 pooled, ARTS 1.02) | **CONFIRMED**: the gaint TTA result (B5) replicates on cv5v3 / cv02 / 5 seeds |
| (b) | CS_D4 - CS | +0.0055 [-0.0002, +0.0115] | +0.0054 [-0.0023, +0.0129] | none fail | **NOT CONFIRMED, NO LOSS -> FLAG D4** (read on the cells that selected the readout) |
| (c) | CS_D4 - PF | +0.0222 [+0.0138, +0.0308] | +0.0230 [+0.0127, +0.0341] | false crack px 0.46 x PF; inactive and mIoU-R13 (+0.0117) pass; **ARTS width 1.159 on the 416 clean cells (band 1.15) named** | **C2 passes its CV5 check** (selection-biased) |
| info | CS - PF (plain candidate) | +0.0166 [+0.0082, +0.0263] | +0.0176 [+0.0071, +0.0300] | ARTS width on 416 cells fails (as in C3X_READ) | information for FLAG D4 |

Levels (532 cells, OP-A, mean over seeds): relF1@2 PF 0.846, PF_D4 0.860, CS 0.863, CS_D4 0.868 (CS numbers selection-biased);
false crack px on crack-free cells PF 212, PF_D4 32, CS 213, CS_D4 98; mIoU-R13 0.612 / 0.620 / 0.619 / 0.623.
Descriptive: CS_D4 - PF_D4 relF1@2 +0.0087 [+0.0017, +0.0157]. Per seed, CS - PF relF1@2 is positive in all 5 seeds (+0.014 to +0.022).

## Reading (S)
- TTA (D4) is now replicated twice on the baseline (gaint B5 and this cv02 read): about +0.013 relF1@2 and about 7x fewer false
  crack pixels on crack-free cells. It is the most robust gain in the project.
- On top of HRNet+SWAD the D4 increment is about +0.005 with an interval touching 0: TTA and the model change overlap. D4 still
  halves the candidate's false crack pixels (213 -> 98) and does no harm on any guard.
- FLAG D4 is the user's decision before the E1 rule is frozen (FINAL_RULE section 4): keep C2 / C3 with D4 as approved, or replace
  D4 by plain inference. The opening already prints C1-D4 (PF with D4) because (a) is confirmed, so E1 can separate the TTA part.
- The full-pool training runs of the same queue failed at their final validation (log.md 21 Nov 07:07); they do not enter this
  read (it uses the cv5v3 checkpoints only) and are being finished by fin2 (FINAL_RULE_ADDENDUM_1.md).
