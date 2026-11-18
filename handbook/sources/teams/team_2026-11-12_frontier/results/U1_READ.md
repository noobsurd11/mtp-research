# U1 read: leave-source-out LOSO-2, Skeleton Recall anchor against PF (lead, 17 Nov 2026, 18:46 IST)

Rule written before any LOSO-2 run existed: results/stageB/B3.md section 1b rule 6 with the lead's additions of 15 Nov (16:07, 16:14, 17:58). Runs: gaint queue bq/udev_loso2 (12 runs, 20,000 steps, all rc 0, dumps rc 0, chain done 17 Nov 18:43). Read 18:44 to 18:46 on gaint CPU with the commands of /home/noob/work/bench_udev/jobs_v2/PREP.md (script results/u1_read/run_U1.sh 1e67b76e; tool bench_udev_read.py ff033a62 at ae4dd10, worktree clean). Tables: results/u1_read/. E = measured, S = judgement.

## Set
LOSO-2: two folds, each trains on all sources but one and is scored on the held-out source: CSIR (114 cells, 51 with cracks, effective n 8.3) and BMRK (50 cells, 30 with cracks, effective n 16.2). Pooled U1 = 164 cells, 126 groups, effective n crack 17.7. PF seeds 5 to 8, SKR01 (Skeleton Recall anchor skr01_pf_v11) seeds 5, 6. Labels v1.1.

## Result (E)
| | PF (4 seeds) | SKR01 (2 seeds) |
|---|---|---|
| strict crack IoU | 0.293 | 0.312 |
| crack relF1@2 | 0.733 | 0.744 |
| relP@2 / relR@2 | 0.892 / 0.623 | 0.902 / 0.634 |
| width ratio | 0.61 | 0.70 |
| inactive IoU | 0.197 | 0.214 |

A/A margins on U1 (PF {5,6} against {7,8}): crack IoU 0.032, relF1@2 0.044, frontier relR@2 0.064, inactive IoU 0.077.

**Deciding contrast (pooled 164 cells), SKR01 minus PF at the frontier (relR@2 at PF's relP@2): +0.0206 [-0.0518, +0.0744]**, width ratio against PF 1.22 [0.79, 1.58]. At OP-A: relF1@2 +0.0111 [-0.0206, +0.0527], strict crack IoU +0.0187 [-0.0057, +0.0465]; every interval holds 0.
Per source (printed beside, cannot decide alone): CSIR frontier +0.0317 [-0.0365, +0.0739] (own M 0.050); BMRK -0.0066 [-0.1173, +0.0853] (own M 0.127).

## Reading (rule 6)
- The frontier interval is not above 0: **U1 is a guard, not a primary (Y2 (c)).**
- Inconsistency clause (opposite signs, each at least that source's own A/A margin): the signs are opposite, but neither source reaches its own margin: **not "inconsistent"**.
- S: U1 is a weak instrument at this size: its margins (0.044 relF1@2, 0.064 at the frontier) are three to six times the CV5 margins (0.010), so on U1 only effects of about +0.05 or more can be seen.

## Consequences (lead's rulings, logged 17 Nov)
- **gin_ipa** (GIN + IPA augmentation, the planned unseen-module arm; U1 was its primary, WAVE3_REVIEW line 75: "stage A decides at 2 seeds only if M_U1 <= 0.03"): M_U1 is 0.044 (relF1@2) and 0.064 (frontier), above 0.03, and its expected effect (+0.01 to +0.04 on U1, WAVE3_REVIEW line 45) is below these margins; with U1 a guard and the photometric pre-check P-GIN (d) showing no deficit, **gin_ipa is parked, not closed**: it is not run on U1; it can return only with a stronger unseen-module instrument (U2 after the unseen-module dumps, or the registered E1 opening in the last week).
- Descriptive (S): on held-out sources PF loses about 0.11 relF1@2 against its CV5 level (0.733 against 0.844) and draws cracks thinner than labelled (width ratio 0.61; 0.73 on CSIR, 0.42 on BMRK, whose labels are drawn 3 px wide, so part of this is label style); false crack pixels on crack-free cells rise (1,726 against about 357 on CV5). The unseen-source gap is real and large; this read cannot rank methods on it.

## Limits
Two held-out sources, one machine (gaint), 2 SKR01 seeds; effective n 17.7 crack cells pooled.
