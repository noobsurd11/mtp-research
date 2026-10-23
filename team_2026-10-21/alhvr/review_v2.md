# Review of protocol AL1 v2 (agent 2, ALHVR critic), 21 Oct 2026

## Verdict: APPROVED, with launch conditions

v2 is v1 (approved in `review_v1.md`) plus an amendment that carries out the user's three answers, relayed by team-lead:
- the runs go on cv02;
- D7 = yes, so the 7 train twins of test cells leave the unlabelled pool;
- an extra arm, ALdh5: ALd5 at its matched λ 0.3.

The amendment was written before any main-queue run and before any test number of a new run was seen.

**The final launch of the 35 runs needs all of the following:**
1. **C1 (λ = 0 identity) passes on cv02,** with its log diff in `alhvr/log.md` and read by me.
2. **C3 (memory and speed) passes on cv02,** with its log diff in `alhvr/log.md` and read by me.
3. **C2 (the Mean Teacher pipeline check) matches the old `p13_BsM_5pct_s0` log to step 2,050.** If it does not, the cause is found and written up before launch, even though BsM5 is re-run anyway. A changed MT code path would also mean the new BsM5 is not the P13 recipe.
4. **team-lead gives the go** (the user's Kaggle dataset question).
5. **GPUs are booked** in `gpu_ledger.md`, split with agent 3.

## Checked
- **`diff protocol_v1.md protocol_v2.md`.** Only the [v2] items change: status line, arm table (ALdh5, BsM5 re-run), the λ paragraph, the pool, contrasts S3/S6 and the count, C2, and compute. Nothing else moved.
- **`launch/al1_queue_v2.spec`.** 7 arms × 5 seeds = 35 lines.
  - `data.unlabeled_exclude` is on exactly 30 lines (25 two-network + 5 BsM5) and not on A5.
  - ALdh5 = ALd5 options + `alhvr.lambda_max=0.3`, so the only difference is λ.
  - BsM5 options = the P13/P18 BsM spec + the exclusion.
- **Exclusion code** (`scripts/train.py`, gaint `el_alhvr` 3a94457). It runs for every SSL method, Mean Teacher included, after the pool is chosen and before the datasets are built. It refuses stems not in the pool. Agent 1 reports the C1 AL run logging "excluded 7 stems".
- **Launcher.** The `rc=$?` capture is fixed (`launch_set_al1.sh` lines 14 and 18–19): train and rescore return codes are now taken before any `echo` runs.
- **λ for ALdh5.** D0c's DTCT-only match is 0.30 → 0.3, measured on the 455-cell pool. Dropping 7 of 455 cells (1.5%) does not plausibly move a median gradient ratio across a grid step. No re-probe needed.

## Points for the analysis
1. **The pool differs from the P-series** (448 vs 455 cells).
   - No new SSL arm may be pooled or compared with old cv02 SSL runs (P13/P17/P18) as if it were the same pipeline.
   - A5 is unaffected and C1 links it to the old A5c.
   - Every README table states "D7 pool".
2. **Two DTCT-only arms.** S6 (ALdh5 − ALd5) is a λ contrast within DTCT-only. If ALd5 and ALdh5 disagree against A5, report both as they are. Do not pick the better one for S5 without labelling it post hoc (protocol §5 already says this).
3. **Multiplicity.** The secondary family is now 9 contrasts. Only P (AL5 − A5) carries a claim. With about 10 contrasts and no correction, a single secondary pass at R1 is weak evidence and must be worded as such.
4. **Unchanged from review_v1:**
   - the step-6,000 activity check on every SSL arm's logged share;
   - `regions.csv` crack shares reported with S1 and P;
   - with and without rows for `CSIR_00070_r8_c4` and for the 7 twin test cells. The twin row matters less now that the leak is closed at the pool, but it stays for continuity with the P-series.

## Addendum 1: step-6k activity check (interim read 17:55 IST; final read once all four two-network seed-0 runs pass 6,000)
Read by agent 2 from cv02 `el_alhvr/experiments/*.stdout`, steps 4,000 to the latest logged step, own parser. At 17:55 IST the runs were at step AL5 4,500, ALd5 4,800, ALdh5 4,750, CPS5 5,450 and BsM5 9,550. They are slower than C3 (0.50 to 0.62 steps/s vs 0.73 to 1.01) because each GPU also carries a second lane.

| Arm (s0) | share_a = λ·L_u/L_sup, mean [min, max] | gshare_a samples (2.5k to 4.5k) | Ω1 / Ω2a / Ω2b / Ω3 | A/B disagreement | γ |
|---|---|---|---|---|---|
| AL5 (λ 0.1) | 0.277 [0.241, 0.324] | 0.32, 1.13, 0.40, 0.20, 0.40 | 0.864 / 0.029 / 0.026 / 0.081 | 1.64% | 0.978 |
| ALd5 (λ 0.1) | 0.130 [0.116, 0.140] | 0.047, 0.088, 0.064, 0.031, 0.0018 | 0.861 / 0.026 / 0.041 / 0.072 | 2.09% | 0.979 |
| ALdh5 (λ 0.3) | 0.293 [0.251, 0.341] | 0.12, 0.26, 0.30, 0.32, 1.00 | 0.868 / 0.045 / 0.040 / 0.048 | 1.40% | 0.988 |
| CPS5 (λ 1) | 0.377 [0.318, 0.517] | 0.99, 0.26, 0.70, 1.58, 0.21 | 0.869 / 0.024 / 0.024 / 0.083 | 1.74% | 0.975 |
| BsM5 (reference, s0; s2) | 0.153 [0.093, 0.215]; 0.161 [0.103, 0.287] | – | – | – | – |

- **Activity rule (protocol §7: stop if < 0.03 or > 3).** Every arm is inside the band, between 0.8× and 2.5× BsM5's share. No λ amendment.
- **Routing and collapse flags.** Ω2 + Ω3 is 13–14% of pixels (flag at < 1%). A/B disagreement is 1.4–2.1% (flag at < 0.5%). Neither fires. The two networks agree more than in D0 (9% disagreement there), as expected for same-batch co-training, but they have not collapsed.
- **Errors.** No Traceback, inf or NaN after step 2,000 in any AL1 run. A5 s0 and s1 are at about step 19,500.
- **ALd5.** The individual gshare samples fall to 0.0018 at step 4,500. The loss share is steady at 0.13, so the gradient of the masked MSE is small at times, not dead. I re-read it at the final check.
- **ALdh5 seeds 1–4** sit at the end of the queue. The hold rule is satisfied: ALdh5 s0's 4k–4.75k share of 0.29 is active and in band.
- **Interim verdict: the queue continues.** I confirm with the full 4,000–6,000 window when all four seed-0 runs reach step 6,000 (AL5 about 18:45 IST).

## Addendum 2: final step-6k check (read 19:25 to 19:35 IST, cv02 logs, own parser)
Window: steps 4,000 to 6,000, every logged step (n = 41 per run). The runs were then at steps AL5 6,450, ALd5 6,950, ALdh5 6,900 and CPS5 8,150 (all seed 0).

| Arm (s0) | share_a mean [min, max] | gshare_a at 4k / 4.5k / 5k / 5.5k / 6k | Ω1 / Ω2a / Ω2b / Ω3 | A/B disagreement | γ | unlabelled terms (mean) |
|---|---|---|---|---|---|---|
| AL5 (λ 0.1) | 0.284 [0.241, 0.384] | 0.20 / 0.40 / 0.57 / 0.24 / 0.60 | 0.872 / 0.030 / 0.024 / 0.074 | 1.5% [1.2, 1.9] | 0.981 | ce 0.168, cos 0.080, mse 0.123, ent 0.059 |
| ALd5 (λ 0.1) | 0.136 [0.116, 0.152] | 0.031 / 0.002 / 0.20 / 0.15 / 0.44 | 0.865 / 0.027 / 0.043 / 0.065 | 1.9% [1.5, 2.5] | 0.981 | mse 0.144, ent 0.051 |
| ALdh5 (λ 0.3) | 0.317 [0.251, 0.381] | 0.32 / 1.00 / 0.53 / 0.46 / 2.62 | 0.878 / 0.046 / 0.036 / 0.039 | 1.2% [0.9, 1.8] | 0.990 | mse 0.143, ent 0.024 |
| CPS5 (λ 1) | 0.380 [0.318, 0.517] | 0.70 / 1.58 / 0.21 / 0.37 / 0.55 | 0.871 / 0.024 / 0.024 / 0.080 | 1.7% [1.4, 2.1] | 0.976 | ce 0.061 |
| BsM5 (reference) s0; s2 | 0.153 [0.093, 0.215]; 0.161 [0.103, 0.287] | – | – | – | – | – |

**Verdicts**
- **Activity rule (§7):** every SSL arm's 4k–6k mean share is inside [0.03, 3], between 0.9× and 2.5× BsM5's. No arm is stopped and no λ changes.
- **Routing flag** (Ω2+Ω3 < 1%): not fired. Ω2+Ω3 = 12–14% of pixels.
- **Collapse flag** (disagreement < 0.5%): not fired. The lowest single value in the window is 0.9% (ALdh5).
- **Errors:** no Traceback, and no NaN in loss, share_a or sup_a after step 2,000, in any SSL run.
- **ALdh hold: released.** ALdh5 s0's share is 0.317, active and in band. ALdh5 s1–4 run when the queue reaches them; they are the last 4 entries of the big queue.
- **Watch (no action):** ALdh5's single gshare sample at step 6,000 is 2.62, the unlabelled gradient larger than the supervised one. The rule is on share_a, so this is not grounds to stop. If later gshare samples stay above 3, report it in the README as "unlabelled-dominated".

**Queue state, checked against the 15:20 IST launch**
- **Run dirs:** each run exists once. No duplicate `Run:` header.
  - Finished: A5 s0 and s1, trained and rescored, rc = 0. I have not opened their scores.
  - Running: AL5 s0, ALd5 s0, ALdh5 s0, CPS5 s0, BsM5 s0/s1/s2, A5 s2.
- **Big queue, 21 left:** CPSm5 s0 next, then AL5/ALd5/CPS5/CPSm5 seeds 1–4 by seed, then ALdh5 s1–4. Running plus queued = 25. OK.
- **Small queue, 4 left:** BsM5 s3, A5 s3, BsM5 s4, A5 s4. With 4 done or running and 2 finished, the total is 10. OK.
- **Throughput:**
  - The two-network runs average 0.44–0.56 steps/s with two lanes per GPU, against the protocol's estimate of 4–6 h per run.
  - So each two-network run takes about 10–12.5 h.
  - 25 runs on 4 big lanes is about 6.25 waves, so the queue ends around 24 Oct evening, not 23 Oct.
  - GPU 7 on cv02 was idle (1 MiB, 0%). Adding it as a fifth big lane would change speed only, not results: same machine, same hardware, deterministic per run. That needs a ledger booking agreed with agent 3. My recommendation, not a requirement.

## Addendum 3: CPSm5 s0 step-6k check (read by agent 2, cv02 log, own parser)
- **CPSm5 s0 (λ 1), steps 4,000–6,000, n = 41:**
  - share_a 0.346 [0.288, 0.416], inside [0.03, 3] and 2.2× BsM5's;
  - Ω1 0.864, so Ω2+Ω3 = 13.6%;
  - Ω3 0.082;
  - disagreement 1.7% [1.3, 2.1];
  - γ 0.975;
  - gshare_a samples 1.02 (step 4k), 0.73 (4.5k), 0.12 (5k);
  - no Traceback.
- **Verdict:** active, no flag fires, no amendment. This agrees with agent 1's numbers (0.345, n = 42 to step 6,050).
- **ALdh5 s0 watch:** gshare_a at steps 6.5k–8.5k is 0.34, 0.83, 1.68, 0.87, 1.59. The 2.62 at 6k was a single sample, and the arm is not unlabelled-dominated so far. The watch continues to step 20k and goes into the README.
- **All five SSL arms have now passed the step-6k activity check.**

## Addendum 4: H-cm predictions for AL1, written 22 Oct 19:33 IST, before any AL1 test number has been opened
Source: `skcdf/second_opinion_a2.md` §4. If the hypothesis "confident crack misses are not reached by confidence-gated SSL losses" (H-cm) holds, AL1 should show:
1. **Crack IoU:** AL5 − A5 is no larger than BsD5's gain over A5c in SK1 (+0.024). The rule-1 verdict on crack IoU is n.d. or a pass by less than 0.024.
2. **Bin-0:** AL5's crack bin-0 share on test (secondary metric) is within ±0.03 of A5's.
3. **S1 (CPSm5 − CPS5, Ω1 masked):** n.d. or worse on crack IoU. Masking Ω1 cannot help crack if the misses are confident.
4. **Inactive:** if any SSL arm gains, the gain is larger on inactive than on crack (as P13/P17/SK1).

These are predictions, not rules. They change no verdict. The README reports them as "H-cm prediction held / failed".

Status at writing: the AL1 queue is running. Finished A5 runs have been rescored by the trainer. I have opened no AL1 score file.

## Addendum 5: AL1 results independently recomputed, 23 Oct 06:55 IST: CONFIRMED
See `alhvr/verify_a2.md`.
- **Primary AL5 − A5: WORSE on all three primaries, in all four cell sets.** The bootstrap CIs exclude 0 on all three.
- All secondary verdicts match. A5 is bit-identical to the old A5c.
- **H-cm predictions** (addendum 4): all four held. They were weak predictions. The inactive damage (test recall 0.276 → 0.124; corrected from a test/val mix) was not predicted.

**Wording requests for results.md (non-blocking):**
- (a) Add the inactive precision/recall line to §6/§8.
- (b) ALdh5 gshare: call it "intermittently unlabelled-dominated (22/165 samples > 3, median ≤ 1.66)".
- (c) Add the H-cm prediction outcomes, citing addendum 4.
- (d) Keep §7 (network B not scored) as "not done".
