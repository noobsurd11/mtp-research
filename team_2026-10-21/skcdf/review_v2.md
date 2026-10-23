# Review of SK1 protocol_v2 (agent 4, 21 Oct 2026)

## Verdict: APPROVED

**Launch gates still closed** (protocol §0):
- team-lead must relay the user's machine choice;
- team-lead must relay the user's D7 answer.

After both, run in this order: the §12 smoke set and the §7 identity checks, then my check of their logs, then the queue for the chosen D7 branch. Both the smoke and the identity-check logs come to me before the queue starts.

## What I checked
- **All 7 items of `review_v1.md` are addressed.**
  - Twins: four cell sets, both D7 branches.
  - Prior-shift control: τ = 1 fixed, τ grid on val only, a τ = 0 check against the re-score JSONs.
  - Mechanism log.
  - Deviations table; it matches my reading of the official code, including the Dice note.
  - Test count.
  - `chk_A_5pct_s0` against P12's log.
  - Machine left to the leader.
- **Diff `b90008e..0ea71df`, read in full.**
  - `data.unlabeled_exclude` refuses stems that are labelled or not in train, and logs the number dropped.
  - The mechanism log runs under `no_grad` and draws no RNG, so it cannot change training.
  - No bug found.
- **Tests on gaint:** `pytest tests/test_absh.py` gives 15 passed.
- **Exclusion list** `data/splits/d7_twin_train_cells.txt` (7 stems) equals `data/decision.md` D7 exactly.
- **Specs, diffed by script:**
  - D7-yes BsDB5/BsDBn5 differ from D7-no only by `data.unlabeled_exclude`;
  - AB5 is identical in both branches;
  - the `sk1_BsD` re-runs differ from P17's BsD5 only by `absh.enabled=false` and the exclusion. The re-run code is 0ea71df rather than f2f20d3, which the identity check covers.
  - All arms are one change from their comparison.
- **Launcher rc bug: confirmed.**
  - `bash -c 'false; echo "[$(date +%s)] rc=$?"'` prints rc=0.
  - `launch_set_p17.sh:16,18` have the bug; `launch_set_sk1.sh:17-20` captures rc first.
  - P-series "rc = 0" statements therefore rest on the logs and JSONs only. This goes to team-lead for a handbook note (doc 14) and to the ALHVR track if it reuses the old launcher.
- **Aborted runs (§12 disclosure).** review_v1 allowed them. They were stopped before step 110, and only training-loss lines were seen. No val or test exposure; acceptable.

## Minor points (no new version needed; handle in the analysis)
1. **Logit-adjustment output.** Absent classes get π_min, so τ = 1 boosts them as much as the rarest present class.
   - Add one field: the share of test pixels predicted as a class absent from the 23 labelled cells, at each τ.
   - If it is above 0.1% at τ = 1, report LA with those classes masked out as well. Mark it descriptive.
2. **Expect LA at τ = 1 to over-predict crack heavily.** log(π_bg/π_crack) ≈ 5.7 nats. Report relP@2 and precision next to it, as §8 item 5 already requires.
3. **Smoke acceptance criteria** (I will check these):
   - `head_drift` falls over the 300 steps;
   - `main_pred_crack` moves toward `aux_pred_crack`;
   - `aux_keep_l` is consistent with the keep probs (about 0.5–2% of pixels plus the band);
   - `aux_keep_u` > 0 once λ is on;
   - no NaN;
   - `smoke_BsDBx` logs "dropped 7 of 455".
4. **Identity checks:** I will diff the logs myself. Every field except time must match exactly; otherwise §7's re-run rule applies with no discretion.

## What I will verify on the results
Before anything reaches the leader, I will:
- recompute rule 1 for the primary and both secondaries, the four cell sets, the bootstrap and the LA control from the raw re-score JSONs, per-cell counts and LA JSON, with my own script;
- check rc and log completeness of every run;
- check the MD5 relay to gaint.

---
## Addendum (21 Oct ~15:45 IST): smoke and identity checks. LAUNCH APPROVED (D7 = yes branch, cv02, `sk1_queue_d7yes.spec`)
- **Identity checks** (my own diff of cv02 stdout, time and speed fields stripped):
  - `chk_BsD_5pct_s0` vs `el_p17` p17_BsD s0: 60/60 lines identical;
  - `chk_A_5pct_s3` vs `el_p13` p13_A s3: 57/57 identical;
  - `chk_A_5pct_s0` vs `el_p11` p12_A s0: 58/58 identical.
  - So A5c s0–4 are reused. BsD5 is re-run (D7 = yes).
- **Smoke runs** (rc = 0, no NaN or traceback):
  - keep probs as designed (bg 0.0049, inactive 0.876, crack 1.0);
  - `aux_keep_l` ≈ 0.044;
  - `smoke_BsDBx` logs "dropped 7 of 455 pool cells" and trains on 448;
  - `chk_off_metrics` writes no absh keys.
- **Mechanism:**
  - `smoke_BsDB` step 300: main pred crack 0.0049, aux 0.0087, GT 0.0030.
  - `smoke_AB` step 300: 0.0034 / 0.0042 / 0.0032.
  - My earlier criterion "head_drift falls" was mis-stated: the heads start identical, so the drift grows from 0. Withdrawn.
- **Unlabelled ABSH path.** It was not exercised at 300 steps (conf_frac 0), so I asked for two more runs.
  - `smoke_BsDB_t0` (t_pos 0, 100 steps):
    - conf_frac 1, loss_con 2.76 → 1.39, loss_aux_con 2.76 → 1.35;
    - aux_keep_u 0.98–0.999;
    - `test_final_absh` has `teacher_aux` and `decoder_u_aux`.
  - `smoke_BsDB_lowema` (EMA 0.9, 150 steps), a realistic proxy:
    - conf_frac rises from 0 to 0.54;
    - aux_keep_u falls to 0.037 (annealed keep working);
    - aux PL crack appears (0.007 at step 150).
  - All paths ran.
- **Watch item for the real runs.** Early aux PL crack share (0.007) is about 2× GT crack (0.003). The protocol §9 flood watch and the PL crack counts at steps 4,000 and 20,000 cover this. I will read them.
- **Approved:** launch of the D7 = yes queue on cv02, under the booking and relay rules of protocol §11.

---
## Results addendum (agent 4, 22 Oct): independent recompute of SK1

**Method.** I did not use agent 3's tables.
- My own scorer (`verify_a4/c4_percell.py`) ran on cv02 GPU 5, inference only. It loaded each run's `latest.pth` (EMA teacher for SSL arms, model for supervised) and wrote per-cell counts for all 50 test cells.
- Rule-1 arithmetic, the four cell sets and a paired image bootstrap (2,000 resamples) were computed from those counts.
- Output: `verify_a4/sk1_verify_a4.txt`, `verify_a4/c4_percell.json`.

**Integrity checks.**
- All 25 scored checkpoints (A5c ×5, BsD5, BsDB5, BsDBn5 and AB5 ×5 each) are at step 20,000, and so are all 20 SK1 re-score JSONs.
- My per-cell counts, pooled, equal the re-score JSONs exactly (max |diff| 0.0 on crack IoU, inactive IoU, relF1@2 and relP@2).
- My A5c per-cell counts equal E1 `raw_v2` exactly.
- launch.log shows rc = 0 for train and rescore of all 20 runs, and the launcher now records rc correctly.
- Agent 3's `results/sk1/sk1_rules.txt` all-50 numbers match mine to 4 decimals.

**Verdicts (5 v 5, rule 1; Δ (threshold); crack IoU / inactive IoU / crack relF1@2)**

| Contrast | All 50 | Without noisy cell | Without 7 twins | Without both | Bootstrap, all 50 (95% CI) |
|---|---|---|---|---|---|
| **BsDB5 − BsD5 (rule 1, primary)** | −0.0044 (0.0100) / −0.0113 (0.0282) / +0.0044 (0.0100): **n.d.** | n.d. | n.d. | n.d. | crack [−0.0099, +0.0016]; inact [−0.036, +0.023]; relF1 [−0.004, +0.015] |
| AB5 − A5c (rule 2) | −0.0083 (0.0128) / −0.0083 (0.0681) / −0.0065 (0.0189): **n.d.** | n.d. | n.d. | n.d. | crack **[−0.0121, −0.0049]** (below 0); relF1 [−0.015, +0.001] |
| BsDB5 − BsDBn5 (rule 3) | −0.0145 (0.0100) / −0.0173 (0.0452) / −0.0049 (0.0103): **WORSE (crack IoU)** | WORSE | WORSE | WORSE | crack [−0.021, −0.010] |
| BsD5 − A5c (desc.) | +0.0243 / +0.1311 / +0.0359: passes all three | passes | passes | passes | |
| BsDB5 − A5c (desc.) | +0.0199 / +0.1198 / +0.0403: passes all three | passes | passes | passes | |
| BsDBn5 − BsD5 (desc., NOT a rule; two-step from the protocol arms) | +0.0101 (0.0100) / +0.0061 / +0.0093: passes on crack by 0.0001 | +0.0085 (0.0100): n.d. | +0.0159 (0.0134): passes on crack | +0.0139 (0.0127): passes on crack | crack [+0.004, +0.019] |

- **Rule-1 thresholds as a share of BsD5 − A5c's gain:** crack 41%, inactive 22%, relF1@2 28%. A primary effect smaller than that is not excluded.
- **Noisy cell `CSIR_00070_r8_c4`** (787 GT crack px): the largest crack FP on it is 2,153 px (BsD5 s4); every other run is ≤ 1,052. No run reaches the failure mode (39k–80k px). The verdicts are the same without the cell.
- **Twins (D7 = yes, so no SSL arm saw them):** the verdicts are the same without them.
- **BsD5 re-run on the 448-cell pool vs P17's BsD5 (455 cells):** 0.328 / 0.384 / 0.755 vs 0.327 / 0.371 / 0.756. Consistent.

**Verdict (locked rules):**
- **Primary: n.d.** Adapted ABSH on the decoupled recipe makes no detectable difference.
- **Q2: n.d.** On the supervised arm, the cell bootstrap puts crack IoU slightly *below* A5c (−0.008).
- **Q3: the 2-px band is detectably worse on crack IoU** than SKCDF's own mask (BsDBn5). This holds in all four cell sets, and the bootstrap CI excludes 0.

**Reading (mine; checks still pending).**
- **BsDBn5 is the best SK1 arm on crack.**
  - Point estimate +0.010 crack IoU over BsD5, with crack AP 0.366 vs 0.314 (agent 3's table).
  - Lower precision: 0.596 vs 0.618, relP@2 −0.013.
  - Its contrast with BsD5 changes two things (ABSH on, no band), was not a pre-registered rule, and passes the floor by 0.0001 on all 50 cells (n.d. without the noisy cell). It is **exploratory**. It can motivate a v3 protocol; it is not a finding.
- **Mechanism confound (agent 3's PL counts, to be verified).**
  - BsDBn5's conf_frac ends at 0.27 in all 5 seeds, against 0.96 for BsD5.
  - So ABSH without the band also removes about 70% of the main unlabelled loss (background self-training).
  - Any BsDBn5 gain may come from that, not from rebalancing the head.
- **Still open:**
  - the prior-shift control (logit adjustment, τ = 1) is not yet in results.md;
  - E1 is pending.
- I will compare results.md against these numbers when it arrives.

---
## Final verdict on SK1 results (agent 4, 22 Oct ~19:15 IST): CONFIRMED

`skcdf/results.md` (agent 3) agrees with my independent recompute on everything I checked.

**1. Rule-1 numbers and cell sets.**
- My per-cell scorer (`verify_a4/`) gives identical Δ and thresholds to 4 decimals:
  - for all three locked contrasts;
  - for the BsDBn5 − BsD5 exploratory contrast;
  - in all four cell sets.
- The AB5 − A5c crack bootstrap upper bound is −0.0049 in mine and −0.0051 in theirs: a resampling difference only.

**2. Steps and noisy cell.**
- Every scored checkpoint is at step 20,000.
- Noisy-cell FP per run matches (max 2,153 px, BsD5 s4).

**3. Logit-adjustment control.** Recomputed with my own scorer, LA τ = 1, π from the 23 labelled cells' `masks_escdd` counts.
- BsD5+LA: 0.3406 / 0.3891 / 0.7591.
- A5c+LA: 0.3191 / 0.2640 / 0.7284.
- Every contrast matches results.md to 4 decimals:
  - BsDB5 − (BsD5+LA) crack −0.0170 (0.0100);
  - BsDBn5 − (BsD5+LA) −0.0025 / +0.0013 / +0.0056;
  - AB5 − (A5c+LA) −0.0237 (0.0132).
- Commit `96dd86a` is a one-line path fix (`ROOT` → `DATA` for the label counts) and is correct. Before it the rescorer would have read no masks. My independent π gives the same numbers, so the fix is confirmed.

**4. Confident-pixel classes**, checked in the raw `pseudo_labels.csv` at step 20,000:
- BsDBn5 s0: background count n_0 = 0 of 282.4 M confident pixels.
- BsD5 s0: background is 719.7 M of 1,009.3 M confident pixels, i.e. 0.713 of confident pixels and 0.686 of all unlabelled pixels.
- Wording fix for the report: "0.686" is the share of *unlabelled* pixels, not of confident ones.
- Why background drops out:
  - the evaluated head converges onto the balanced head (head_drift ≈ 0.001);
  - that head was trained with background keep probability 0.0049, so it rarely reaches 0.95 confidence on background.
  - The band in BsDB5 restores the background negatives near rare targets, and background stays confident (0.60–0.66), except in s1 (0.14).

**5. E1 (secondary).** The test-cell metrics agree with the pooled ones. On the 106-cell unseen-module extension, BsDBn5 − BsD5:
- crack tolF1 +0.049 [+0.016, +0.089];
- crack false alarm **+0.105 [+0.066, +0.149]**, i.e. more crack-free cells flagged.
So BsDBn5's crack gain comes with more false alarms on unseen modules.

**6. Side result** (descriptive). The re-run BsD5 on the D7 pool, minus A5c:
- all 50 cells: +0.0243 (0.0103) / +0.1311 (0.0474) / +0.0359 (0.0174);
- it passes in all four cell sets, verified.
So the decoupled SSL recipe beats supervised at 5% with the train twins out of the pool.

**Final SK1 verdicts (locked rules)**
- **Primary BsDB5 − BsD5: n.d.**
- **Q2 AB5 − A5c: n.d.**, slightly negative over cells on crack.
- **Q3: the 2-px band is WORSE than SKCDF's mask on crack IoU.**

**Not a finding.** BsDBn5 − BsD5 is exploratory, passes by 0.0001, and matches a free logit bias on IoU.

**On the floated arm "BsD5 without background pseudo-labels"**
I do not recommend it as the next experiment. It can be offered to the user as low priority only. Reasons:
1. **On IoU there is nothing to explain.** BsDBn5 equals BsD5+LA within 0.003. The only unexplained part is ranking: crack AP +0.037 over BsD5+LA, bin-0 −0.06. AP is not a primary, so a new protocol would need AP as its primary. That is a methodology change, decided after seeing these results.
2. **The expected IoU effect sits at the seed floor.** BsDBn5 − BsD5 is +0.010 against a 0.010 threshold. 5 seeds cannot resolve it; it needs 8 or more.
3. **It has a measured cost.** On unseen modules the crack false alarm rises +0.105 [+0.066, +0.149].
4. **Strategic.** It is one more SSL tweak at one fraction, on one split (handbook 13 C13, ideas.md #5).

**Better uses of the compute:**
- (a) A pre-registered test of **logit adjustment τ = 1** on existing checkpoints, no training: P13/P17/P18 arms and other fractions. It gave +0.013 crack IoU on BsD5 and +0.015 on A5c here, for free.
- (b) Split seeds 1–2 for the main SSL-vs-supervised claim.

If the user still wants the background-exclusion question answered, it should be:
- one arm, BsD5 with background removed from the unlabelled CE;
- 8 seeds on cv02;
- crack AP and crack IoU as co-primaries;
- the comparison against BsD5+LA pre-declared;
- labelled as following up an exploratory observation.

---
## S-a recompute (agent 4, 22 Oct ~20:15 IST): CONFIRMED for the 5% arms

**Scope.**
- Independent inference with my own scorer and π: π from seed-0 5% `masks_escdd` counts; LA as z − log π.
- 23 checkpoints: A5c ×5, Cs5 ×3, CsM5 ×5, BsM5 ×5, P17 BsD5 ×5. Every one is at step 20,000.
- My τ = 0 crack IoU equals the local re-score JSONs exactly.
- **Not recomputed:** the 10–100% arms. Their π differs per fraction and they carry no crack claim against LA here.
- Output: `verify_a4/sa_verify_a4.txt`.

**Match with `results/sk1/la_sa.md` §1–2.** All 5% numbers agree to 4 decimals:
- LA gains: A5c +0.0154, Cs5 +0.0206, CsM5 +0.0199, BsM5 +0.0233, BsD5 +0.0157 crack IoU; all seeds positive.
- Precision: BsM5 0.635 → 0.554 (flag).
- SSL − (A5c+LA) on crack IoU: CsM5 −0.0017, BsM5 +0.0135 (0.0159), BsD5 +0.0079 (0.0108), Cs5 −0.0115. All n.d.

**Added: relF1@2 in the four cell sets** (my LA scorer keeps relaxed counts).
- Without the twins:
  - BsM5 − (A5c+LA) relF1@2: +0.028 (0.029), n.d.;
  - BsD5 − (A5c+LA) relF1@2: +0.024 (0.023), passes by 0.001.
- Inactive survives in every set except Cs5 without the twins.
- Cs5 − (A5c+LA) crack without the twins: −0.023 (0.014), WORSE.

**Verdict.**
- At 5%, no SSL arm's crack-IoU gain over supervised survives giving the supervised arm a free, fixed logit bias. This holds in all four cell sets.
- SSL's inactive gain survives everywhere except Cs5 without the twins. Its relF1@2 gain is marginal once the twins are removed.
- LA adds to SSL rather than replacing it: (BsM5+LA) − (A5c+LA) crack +0.037, passes.
- These are descriptive results under a protocol written before the numbers (`protocol_sa.md`). A5c's LA effect was seen before (in SK1).
