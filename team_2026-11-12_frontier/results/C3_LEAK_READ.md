# Leakage read cv5v2 against cv5v3 (lead, 17 Nov 2026, 18:43 IST)

Pre-registered on 16 Nov, before any cv5v3 run existed: harness/LAUNCH_REQUEST_c3base.md section 7 (statistic, strata, bootstrap and the fixed reading below). Run 17 Nov 18:39 to 18:43 on gaint CPU with the commands of that section (script results/c3_leak_read/run_leak.sh f0c80967; tool scripts/bench_leak_did.py at 89b9ea5, worktree clean before and after). Tables: results/c3_leak_read/ (did_pf.txt, did_house.txt, json, run.log, MD5.txt). E = measured.

## What is measured
Per seed present in both splits, at argmax, pooled over the stratum: DiD = [m(cv5v3) - m(cv5v2)] on stratum X minus the same difference on the 416 clean, unmoved cells. Leakage across folds in cv5v2 would raise the cv5v2 score of the affected cells and give a negative DiD. X = affected_unmoved (69 cells, primary) and affected_moved (47 cells). Interval: two-stage bootstrap, B 2,000, 285 cv5v3 groups and the common seeds resampled, 95% percentile. One machine (cv02) per pair: PF c3 seeds 5 to 9 against W1-C1 seeds 5 to 9; HOUSE c3 seeds 5, 6 against W1-C2 seeds 5, 6.

## Result (E)
| Arm | Stratum | Metric | DiD [95% CI] | Per seed | Reading |
|---|---|---|---|---|---|
| PF (5 seeds) | affected_unmoved | strict crack IoU | -0.0041 [-0.0136, +0.0069] | +0.0007, -0.0107, -0.0031, -0.0013, -0.0061 | not separated |
| PF | affected_unmoved | crack relF1@2 | +0.0026 [-0.0092, +0.0174] | +0.0127, -0.0036, +0.0044, -0.0026, +0.0021 | not separated |
| PF | affected_moved | strict crack IoU | +0.0103 [-0.0286, +0.0252] | +0.0089, +0.0035, +0.0094, +0.0210, +0.0088 | not separated |
| PF | affected_moved | crack relF1@2 | +0.0249 [-0.0286, +0.0387] | +0.0296, +0.0168, +0.0367, +0.0225, +0.0187 | not separated |
| HOUSE (2 seeds) | affected_unmoved | strict crack IoU | +0.0049 [-0.0080, +0.0121] | +0.0044, +0.0055 | not separated |
| HOUSE | affected_unmoved | crack relF1@2 | +0.0014 [-0.0087, +0.0118] | +0.0000, +0.0027 | not separated |
| HOUSE | affected_moved | strict crack IoU | +0.0007 [-0.0150, +0.0254] | +0.0107, -0.0093 | not separated |
| HOUSE | affected_moved | crack relF1@2 | +0.0145 [-0.0100, +0.0502] | +0.0146, +0.0144 | not separated |

## Reading (fixed in advance)
Every interval contains 0: **"not separated"** for both arms, both strata and both metrics. By the pre-registered rule nothing else is concluded from this read; the benchmark table uses cv5v3 only, as decided on 16 Nov.

Description of the intervals (not a conclusion): the lower ends of the PF intervals on the primary stratum are -0.014 (strict crack IoU) and -0.009 (relF1@2); a leakage effect of the size the module audit allowed as an upper bound (+0.07 crack IoU on affected cells) lies outside them. The HOUSE pair has 2 seeds and no A/A, as section 7 warned.

## Limits
- 69 and 47 cells; one machine; argmax only.
- The comparison mixes two things on the moved cells (their fold assignment changed between the splits), which is why affected_unmoved is the primary stratum.
