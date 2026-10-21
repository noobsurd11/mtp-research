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
