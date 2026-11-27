# la_ce (train-time logit offsets) screen read (lead, 18 Nov 2026, 05:58 IST)

**Verdict (pre-registered, harness/w2b/READ_PLAN_w2b.md section 1; rulings in log.md 17 Nov 17:33 and 19:06): DROP for this offset vector.** The primary contrast (la_ce at argmax minus PF with the post-hoc class-bias layer OP-C, mIoU-R13) is below 0 on both cell sets. **Not a closure of the train-time-offset idea:** the follow-up pre-declared on 17 Nov 18:00, la_ce_full (offset in both the CE and the Dice term), stays owed before that hypothesis is closed.

Read: harness/w2b/run_read_w2b.sh (8d644288; harness MD5.txt verified), 18 Nov 05:46 to 05:52 on gaint CPU, rc 0; tools bench_wt_b b5bf0ae (bench_read_w1.py fdb56b78), w2b_counts.py a23dd544, w2b_verdict.py 1ace40f7; worktrees clean. Inputs: gaint only (one device), split cv5v2, 532 out-of-fold cells and the 416 clean cells; arms LACE = w2b_lace_f[0-4]_s[56] (f678381, card la_ce_pf_v11 with per-fold offsets: each run's LA_CE line named its own fold's row), PF = W1-G seeds 5, 6, PFC = PF at OP-C seeds 5, 6, PFAA = PF seeds 5 to 8 for the A/A (M = 0.010 for mIoU-R13, 0.054 for inactive). Tables: results/w2b_lace_read/ (read.txt, read_x416.txt, read.json, verdict.txt, counts_532.txt, counts_416.txt, run.log, MD5.txt). E = measured, S = judgement.

## Verdict lines (E, verdict.txt)
| Element | 532 cells | 416 clean cells | Result |
|---|---|---|---|
| P1 LACE - PFC, mIoU-R13 (primary) | -0.0022 [-0.0112, +0.0060] | -0.0018 [-0.0136, +0.0070] | FAIL (point <= 0: DROP) |
| P2 LACE - PF, mIoU-R13 | +0.0112 [+0.0017, +0.0204] | +0.0124 [+0.0004, +0.0222] | PASS |
| G1 crack IoU / relF1@2 vs PF at OP-A and OP-W | +0.0002 to +0.0011 | +0.0003 to +0.0011 | PASS |
| G2 inactive IoU vs PFC | -0.0134 [-0.0732, +0.0559] | | PASS (>= -0.054) |
| G3 per R13 class vs PFC | worst class 5: -0.0177 | | PASS (>= -0.03) |
| G4 area ratio per FREE class, 0.85 to 1.15 x PFC | none outside | | PASS |
| G5 predicted px on cells without the class, <= 1.5 x PFC | class 1: 4,503 vs 3,315; class 5: 122,580 vs 65,742 | | FAIL |

## Reading (S)
- Training with the offsets reaches the same mIoU-R13 level as applying them after training: la_ce 0.6229 against PF at OP-C 0.6250 and PF at argmax 0.6117. The post-hoc layer is free, so la_ce as built adds nothing.
- Inactive does not gain (la_ce 0.494 against PF 0.498 and PF at OP-C 0.508); region recall 0.58 against 0.62. This fits the reviewer's note N4: the Dice term acts on the unshifted logits and pushes against the -4 inactive offset. That is exactly what la_ce_full tests.
- Cracks are untouched (every crack metric within 0.0011 of PF; false crack px on crack-free cells 208 against 301).

## Next (lead's rulings)
- la_ce (this vector, CE-only): dropped; ledger line cites la_ce_full.
- la_ce_full: built and reviewed later (a small change: the offset also on the Dice term), screened the same way on gaint after the layered_ci screen and the TTA block. Low priority: even a pass must beat a free post-hoc layer.
