# layered_ci (inactive aux head + layered decision) screen read (lead, 18 Nov 2026, 15:45 IST)

**Verdict (pre-registered, harness/w2b/READ_PLAN_w2b.md section 2, rules L1 to L7; rulings in log.md 17 Nov 17:33 and 19:06): PARK, "no promotion at 2 seeds".** The promotion rule L1 (inactive region recall against PF with the post-hoc class-bias layer, PFC) fails on both cell sets; L2 to L7 all pass, so neither drop rule fires (L6 holds, inactive IoU direction against PFC is positive, every crack guard holds).

Read: harness/w2b/run_read_w2b.sh (8d644288), 18 Nov 15:31:01 to 15:38:34 on gaint CPU, rc 0; tools bench_wt_b b5bf0ae (bench_read_w1.py fdb56b78, worktree clean), w2b_counts.py a23dd544, w2b_verdict.py 1ace40f7; dump jobs 135778ff (30 dumps, all rc 0, chain done 15:30:42). Inputs: gaint only (one device), split cv5v2, 532 out-of-fold cells and the 416 clean cells (score_exclude_v3 6d48dfbd); arms LCI = w2b_lci_f[0-4]_s[56] layered_ci_replace at t_I 0.5 (card layered_ci_pf_v11, deploy f678381), LCIARG = the same runs' argmax of 24 logits, LCIUNI = union rule, PF = W1-G seeds 5, 6, PFC = PF at OP-C seeds 5, 6, PFAA = PF seeds 5 to 8 for the A/A (M = 0.010). Tables: results/w2b_lci_read/ (read.txt, read_x416.txt, read.json, counts_532.txt, counts_416.txt, verdict.txt, run.log, expected_dumps.tsv, MD5_read_folder.txt, MD5.txt; copies equal the read folder's md5). E = measured, S = judgement.

## Verdict lines (E, verdict.txt)
| Element | Value | Result |
|---|---|---|
| L1 inactive region recall LCI - PFC, 532 cells | -0.0140 [-0.0767, +0.0556] | FAIL |
| L1 same, 416 clean cells | -0.0124 [-0.0811, +0.0633] | FAIL |
| L2 inactive false-alarm px (484 cells without inactive) | LCI 2,412 vs PFC 10,636 (limit 12,231) | PASS |
| L3 inactive precision LCI - PFC | +0.0545 [+0.0019, +0.1360] | PASS |
| L4 inactive area LCI / PFC | 0.918 | PASS |
| L5 inactive IoU LCI - PFC (direction) | +0.0180 [-0.0338, +0.0866] | PASS |
| L6 inactive IoU LCI - LCIARG (paired) | +0.0009 [-0.0007, +0.0026] | PASS |
| L7 crack IoU / relF1@2 LCI - PF, OP-A | +0.0073 [+0.0001, +0.0158] / +0.0043 [-0.0037, +0.0111] | PASS |
| L7 same at OP-W | +0.0061 / +0.0040 | PASS |
| L7 crack width ratio (pooled; ARTS, BMRK, CFVS, CSIR) | 1.030 (PF 1.006); 0.916, 0.869, 1.093, 0.929 | PASS |
| L7 false crack px on crack-free cells | 368 vs PF 452 | PASS |

## Levels (E, mean of 2 seeds, 532 cells, OP-A)
| | crack IoU | relF1@2 | inactive IoU | mIoU-R13 | inactive region recall | inactive precision | inactive false px |
|---|---|---|---|---|---|---|---|
| PF | 0.3624 | 0.8417 | 0.4980 | 0.6117 | 0.600 | 0.767 | 8,854 |
| PFC | 0.3613 | 0.8409 | 0.5078 | 0.6250 | 0.621 | 0.746 | 10,636 |
| LCI | 0.3697 | 0.8459 | 0.5257 | 0.6142 | 0.607 | 0.800 | 2,412 |
| LCIARG | | | 0.5248 | | 0.607 | 0.802 | 2,273 |

Printed beside, deciding nothing: LCI - PF inactive IoU +0.0277 [-0.0215, +0.0950] (the spec's original primary); LCI - PFC mIoU-R13 -0.0108 [-0.0172, -0.0035] (PFC's class-bias layer lifts rare classes 15 and 16, which LCI does not have: per-class IoU -0.063 and -0.098 against PFC); LCI - PF mIoU-R13 +0.0025 [-0.0036, +0.0093]; 416 cells: crack IoU LCI - PF +0.0054 [-0.0020, +0.0124], inactive IoU LCI - PFC +0.0135.

## Reading (S)
- layered_ci makes inactive predictions cleaner but does not find more inactive regions: false inactive pixels on cells without inactive drop to about a quarter of PFC's (and of PF's), precision rises by 0.05, while region recall stays at PF's level (0.607 against 0.600 and PFC's 0.621). The promotion rule asked for more regions found, so the arm parks.
- The change comes from training with the auxiliary inactive head, not from the layered decision rule: LCI and LCIARG (plain argmax of the same model) differ by 0.0009 inactive IoU. The decision layer itself is not needed.
- Cracks are not hurt and may gain a little: crack IoU +0.0073 against PF with the 532-cell interval just above 0, but below M (0.010) and not repeated on the 416 cells; relF1@2 +0.0043, interval holds 0. Not a crack claim.
- Not tested and not pre-registered: the aux-trained model with PFC's post-hoc class-bias layer on top (the two act on different things: the layer adds rare-class recall, the aux head removes inactive false alarms). Would be a new hypothesis with its own rule before any read.

## Next (lead)
- layered_ci: parked at 2 seeds (ledger line "no promotion at 2 seeds; inactive false alarms down to 0.23 x PFC, region recall flat").
- gaint continues with the TTA block (udev_tta_path, then udev_tta), then la_ce_full (low priority).

## Limits
2 seeds, one machine (gaint), cv5v2 split; inactive intervals are wide (region recall about +-0.07), so effects under about 0.07 on region recall cannot be resolved at this size.
