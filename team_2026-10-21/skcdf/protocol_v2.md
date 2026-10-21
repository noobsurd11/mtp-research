# SK1 protocol v2: SKCDF's auxiliary balanced head (ABSH), adapted to EL cells, at 5% labels

Status: DRAFT v2 for review (agent 4). Not locked. Changes from v1 answer `review_v1.md` items 1–7 (list at the end).
Launch gates:
1. `APPROVED` in `review_v2.md`;
2. team-lead relays the user's machine choice;
3. team-lead relays the user's D7 answer (`data/decision.md`).

No run, smoke or identity check before all three.
Written 21 Oct 2026, agent 3. Design: `design.md`.

**What I had seen when writing:**
- all P13 to P19 results;
- 5% labelled class counts;
- `data/decision.md` D6 and its post hoc twin sensitivity on P13/P17;
- the first ~100 steps of three smoke runs (loss values only; launched before the leader's no-launch instruction reached me, stopped at 13:57 IST, outputs moved to cv02 `el_sk1/reports/aborted_2026-10-21/`; see §12).

No SK1 test or val number exists.

## Decisions recorded (21 Oct, relayed by team-lead from the user)
- **Machine: cv02.** All SK1 arms and the reused A5c run on cv02; outputs relayed to gaint with MD5 afterwards.
- **D7: yes.** The D7-yes branch of §5 applies (`sk1_queue_d7yes.spec`, 20 runs): the 7 train twins are out of the 5% pool in every SSL arm; BsD5 is re-run (`sk1_BsD_5pct_s0..4`, absh off); A5c is reused after the §7 A5c checks; `chk_BsD_5pct_s0` is kept as a code-identity check only.
- Smoke and identity checks allowed now; **final launch held** (team-lead is checking a possible new dataset that may change the data decision; needs team-lead's go).

## 1. Question
On the P17 decoupled recipe (BsD5) at 5% labels, does SKCDF's auxiliary balanced head, adapted to thin rare classes on 2-D EL cells, raise test crack IoU, inactive IoU or crack relF1@2 over BsD5?
Secondary questions:
- Q2: is any effect SSL-specific?
- Q3: does the thin-structure band matter?
- Q4 (descriptive): is it more than a fixed prior shift?

## 2. Hypothesis
H1: the balanced head moves the evaluated head's class prior toward crack and inactive. That cuts confident misses (bin-0 share 0.53 / 0.54 in BsD5) and raises rare-class IoU.
Risks: lower precision; wider cracks.
Competing explanation H0p: the same gain comes from a free logit bias (§8, control 6).

## 3. Data (D0, per `data/decision.md` D2)
- BenchmarkEL `dataset_20211104`, revised masks (`labeled/masks_escdd`), split seed 0.
- 5% = 23 labelled cells; test 50 cells, val 54 cells.
- Unlabelled pool: in-domain (455 cells), or 448 under D7 "yes" (§5).
- Same files as P13/P17 (cv02 `el_p7/data`). md5 of `train/val/test.txt` and `seed0/{labeled,unlabeled}_5pct.txt` checked identical to `el_p7/data` on 21 Oct.
- No synthetic `_rf` image, E1 cell or E-SCDD extra cell is used (D2, D4).

## 4. Code and deviations from the official code
**Code**
- gaint worktree `/home/noob/work/el_sk1`, branch `sk1`:
  - `b90008e`: the absh switch (reviewed in v1);
  - **`0ea71df`**: review additions:
    - mechanism log;
    - `data.unlabeled_exclude` + `data/splits/d7_twin_train_cells.txt`;
    - `scripts/rescore_logit_adjust.py`.
- Diff: `git -C /home/noob/work/el_sk1 diff f2f20d3 0ea71df`.
- Deployed by `git archive` to cv02 `/tmp/noob_el/el_sk1`:
  - `REVISION` 0ea71df;
  - `data -> /tmp/noob_el/el_p7/data`;
  - the exclusion list copied to `/tmp/noob_el/el_sk1/d7_twin_train_cells.txt`.
- Switches, all opt-in; off keeps `f2f20d3` bit for bit:
  - `absh.enabled`;
  - `absh.ref_classes` [14, 11];
  - `absh.band_radius` 2;
  - `absh.head_ema` 0.99;
  - `data.unlabeled_exclude`.
- **Tests:** `tests/test_absh.py` has **15** tests: v1 had 14 (I wrote 16 in v1; that was wrong), and v2 adds the mechanism-log test. Full suite on gaint: 222 pass, 3 skipped. The skips fell from 7 because the data links now exist.
- **Mechanism log**, every step, averaged per 50-step log line, so it is denser than the every-500-steps the review asked for:
  - `head_drift` = ‖main_l − aux_l‖₂ over head parameters;
  - on the labelled batch, the share of pixels predicted crack / inactive by the main head and by the aux head (`main_pred_*`, `aux_pred_*`), next to the GT share (`gt_*`).
- Plus `aux_keep_l`, `aux_keep_u`, the aux PL crack/inactive share, and `loss_aux_sup` / `loss_aux_con`.

**Deviations from the official code** (`yinguanchun/SKCDF @ 12f807d`, `SKCDF/code/train_skcdf.py`):

| Item | Official | SK1 | Why |
|---|---|---|---|
| Keep-prob reference | `min(class_size)/class_size` over all classes, first 4 labelled volumes (`:191-206`) | min(1, N_ref/N_c), N_ref = min(N_crack, N_inactive), all 23 labelled cells; absent classes p = 1 | splice (1,944 px, not a target) would set crack's p to 0.11 |
| Band | none | rare-target pixels and their 2 px Chebyshev band always kept (BsDBn5 tests without) | width of 1–2 px cracks |
| Aux CE masking | logits × 0, label × 0: zero gradient, CE averaged over all px (`:259`, `:276`) | CE on kept px, summed / all px | same scaling, explicit ignore |
| Aux Dice | masked px stay in Dice as zero-logit background, so a uniform 1/K softmax enters every class's Σp (`:259`) | Dice (crack, inactive, as `ce_dice`) over kept px only | the official version adds a constant to Dice denominators; ours is a clean ignore |
| Unlabelled aux PL | argmax of current student's labelled aux head, no threshold (`:265`) | argmax of EMA teacher's aux head, ≥ 0.95, same CutMix box | keep BsD5's PL rule; one change = balancing |
| Main PL | current student labelled decoder, no threshold, joint BN | EMA teacher, ≥ 0.95, separate BN (BsD5 as is) | base recipe |
| Anneal | per epoch, 1 → p over max_epoch (`:267`) | per step, 1 → p over 20,000 steps | iteration-based trainer |
| Transfer timing | top of each iteration, H→D→H (`:215-238`) | after each optimizer step, H (before teacher EMA) → D → H | same sequence, half a step later |
| Transfer content | decoder_u (incl. both heads) ← decoder_l | same: decoder_u, main_u, aux_u ← labelled counterparts | |
| ω | 0.99 | 0.99 (heads and decoder) | |
| λu | 10, sigmoid ramp over the whole run (`:26`, `:55-65`) | 1.0, 0 until step 2,000, linear to 1 by 4,000 (BsD5) | one change; λ is a v-next question |
| Optimizer | SGD 0.3, momentum 0.9, poly | Adam 1e-3, cosine, clip 1; aux heads own Adam, same settings | base recipe |
| Selection | best val Dice, early stop (`:338-346`) | final step 20,000 | standing rule |
| Inference | decoder_u main head (`:315`) | teacher main head (primary); decoder_u main/aux and teacher aux heads secondary | comparability with P13–P17 |
| SKCM | cross-attention between L and U halves | not ported | design §3 |
| Aux head init | separate init | copy of the main head at step 0 | transfer starts as a no-op |

## 5. Arms (5% labels, 20,000 steps, final-step weights, cv02 if the leader confirms)
**Fixed for all arms**
- SSL arms: P17's BsD5 option string (`scripts_cv02/p17_queue.spec`).
- Supervised arms: P12/P13's A5c option string.
- Spec files differ from these only by the arm's keys (diffed 21 Oct).

### Branch D7 = "no" (pools unchanged; `scripts_cv02/sk1_queue.spec`, 15 new runs)

| Arm | Runs | Change vs comparison | Seeds | Source |
|---|---|---|---|---|
| A5c | `p12_A_5pct_s0..2` (24590fb), `p13_A_5pct_s3..4` (bac5264) | reference | 0–4 | cv02, reused after §7 |
| BsD5 | `p17_BsD_5pct_s0..4` (f2f20d3) | reference | 0–4 | cv02, reused after §7 |
| **BsDB5** | `sk1_BsDB_5pct_s0..4` | BsD5 + `absh.enabled=true` | 0–4 | new |
| AB5 | `sk1_AB_5pct_s0..4` | A5c + `absh.enabled=true` | 0–4 | new |
| BsDBn5 | `sk1_BsDBn_5pct_s0..4` | BsDB5 with `absh.band_radius=0` | 0–4 | new |

### Branch D7 = "yes" (7 train twins out of the pool; `scripts_cv02/sk1_queue_d7yes.spec`, 20 new runs)
- Every SSL arm gets `data.unlabeled_exclude=/tmp/noob_el/el_sk1/d7_twin_train_cells.txt`: 455 → 448 pool cells. All 7 are in the seed-0 5% unlabelled list and none is labelled (checked 21 Oct); the code refuses otherwise.
- BsD5 is **re-run** on the reduced pool with the new code (`sk1_BsD_5pct_s0..4`, absh off). The P17 BsD5 runs are not used.
- BsDB5 and BsDBn5 are as above, plus the exclusion.
- A5c and AB5 are unchanged (no pool); A5c is still reused after §7.
- Disclosed as a methodology change made after the P-series (D7).

## 6. Metrics
**Primary** (P8 on): test crack IoU, inactive IoU, crack relF1@2.
- Revised masks; argmax; EMA teacher main head (model for supervised arms); step 20,000.

**Secondary**
- crack/inactive precision and recall; relP@2 (width check); AP and bin-0 share; val;
- E1 per-cell (test and ext);
- `test_final_absh` paths (teacher aux, decoder_u aux) and `test_final_secondary` (decoder_u main);
- mechanism log (§4);
- the prior-shift control (§8, item 6).

## 7. Identity checks (before any reference is reused)
- New code with absh off, on cv02, same env as P17, stopped by `--exit_after_step 2500` (hard exit after the step-2,500 log line).
- Check: every logged loss/λ/conf_frac field must equal the reference stdout up to step 2,500. `steps_per_sec` and wall time are excluded.

| Check | Reference log | Code of reference |
|---|---|---|
| `chk_BsD_5pct_s0` | `el_p17/experiments/p17_BsD_5pct_s0.stdout` | f2f20d3 |
| `chk_A_5pct_s3` | `el_p13/experiments/p13_A_5pct_s3.stdout` | bac5264 |
| `chk_A_5pct_s0` | `el_p11/experiments/p12_A_5pct_s0.stdout` | 24590fb (review_v1 item 6: A5c s0–2 provenance) |

- The checks also confirm that an absh-off run writes no absh keys. Logic: `test_final_absh` is written only when absh is on. The checks exit before `metrics.json`, so the absence is confirmed with one extra 20-step absh-off run reaching `metrics.json` (`chk_off_metrics`, part of the smoke set, §12).
- A crashed (rc ≠ 0) run is not re-scored. The launcher now logs the train rc and calls the re-scorer only on rc = 0.
- If a check differs (e.g. a driver change since 13 Oct), that reference arm is re-run on cv02 at 0ea71df with absh off, all 5 seeds, and only the re-runs are used.
- If A5c s0 fails but s3 passes: A5c s0–2 are re-run; s3–4 are kept.
- Under D7 "yes", only the A5c checks matter (BsD5 is re-run anyway).

## 8. Decision rules (P8 rule 1, 5 vs 5, `scripts/ssl_rules.py`)
1. **Primary: BsDB5 − BsD5.**
   - BETTER on ≥ 1 primary and none WORSE → "adapted ABSH helps on the decoupled recipe".
   - WORSE on any primary → "harms".
   - Otherwise n.d., reported with each threshold as a share of BsD5 − A5c. P17's thresholds suggest about 0.013 crack / 0.043 inactive / 0.017 relF1@2, so a crack gain below about 0.013 is n.d. at 5 seeds.
2. Secondary: **AB5 − A5c** (Q2).
3. Secondary: **BsDB5 − BsDBn5** (Q3).
4. Descriptive:
   - (BsDB5 − BsD5) − (AB5 − A5c), bootstrap CI over cells;
   - BsDB5 − A5c;
   - BsDB5 − BsM5 (two changes; D7 "no" only);
   - per seed, BsDB5's `decoder_u` main path vs its teacher.
5. Width check: crack relP@2 drop > 0.05 vs the comparison arm is flagged; crack precision is reported next to every crack IoU.
6. **Prior-shift control (descriptive, review_v1 item 2).**
   - What is scored: the final checkpoints of BsD5 and A5c (the arms used in the rules), no training, `scripts/rescore_logit_adjust.py`.
   - Logit adjustment z_c − τ·log π_c:
     - π = class pixel frequency in the 23 labelled cells (the counts `absh_p` uses);
     - classes absent from those cells get the smallest non-zero π (fixed now);
     - **τ = 1, fixed now.**
     - An optional τ grid {0.25, 0.5, 0.75, 1, 1.5, 2} is scored on **val only** and reported as such. It never selects anything for test.
     - τ = 0 must reproduce the re-score JSONs (the script reports the max difference).
   - Reported:
     - BsD5+LA next to BsDB5, and A5c+LA next to AB5, on all primaries, precision, recall, AP and bin-0 share;
     - the rule-1 arithmetic BsDB5 − (BsD5+LA) and AB5 − (A5c+LA), descriptive.
   - Reading map:
     - BsDB5 ≈ BsD5+LA on IoU, with AP unchanged → ABSH acts as a prior shift and is described so.
     - BsDB5 > BsD5+LA, or AP/bin-0 improve → the balanced head changes the ranking, not only the prior.
   - Same for the supervised pair.
- **Contrast count:** 1 primary, 2 secondary, 4 descriptive + the control. No multiplicity correction; the primary is the only confirmatory claim.
- **Reading map:**
  - rule 1 passes, rule 2 n.d. → SSL-specific;
  - both pass at similar size → head rebalancing, not SSL;
  - then item 6 tells whether a logit bias already does it.

## 9. Robustness (reported, never changes a verdict)
- Paired image bootstrap (2,000), leave-top-3-out, source split, E1 per-cell metrics.
- **Every contrast in four cell sets** (D6, labelled post hoc relative to the P-series):
  - all 50;
  - without `CSIR_00070_r8_c4`;
  - without the 7 twin test cells (`CFVS_00006_r5_c5`, `CFVS_00033_r8_c4`, `CFVS_00035_r8_c4`, `CFVS_00042_r8_c4`, `CFVS_00018_r4_c4`, `CFVS_00027_r4_c4`, `ARTS_00020_r5_c1`; 39.5% of test crack px);
  - without both.
- Computed from per-cell counts with a sanity check against the re-score JSONs (as `scripts/p17_excell.py`).
- Per-run crack FP pixels on `CSIR_00070_r8_c4`.
- Flood watch: a run whose predicted test crack share exceeds 5× GT is flagged, never excluded.

## 10. Selection and stopping
- No selection on test. In v2, val is used only for the descriptive τ grid.
- Final-step weights only.
- A crashed run is resumed from `latest.pth` (bitwise resume), never replaced by another seed.
- No seed extension in v2. An extension to 8 seeds may be proposed in v3 only if the primary is n.d. with |Δ| above half the threshold on a metric; it would be disclosed as post hoc.

## 11. Compute (machine: the leader's call, to be recorded here)
- Proposed: **cv02**; the critic supports it (review_v1 item 7).
  - Reasons: the references exist only on cv02; gaint has 1 GPU shared with the ALHVR track.
  - Fallback if gaint: all arms re-run on gaint, 5 seeds (25 runs under D7 "no", same under "yes"), no reuse.
- **cv02 rules:**
  - no GPU where another user holds > 4 GB;
  - the queue takes only GPUs < 1,000 MiB;
  - one queue (`gpu_queue_sk1.sh`) in tmux `=sk1`;
  - 3 identity checks first, in tmux `=sk1chk`.
- **Time:** ~2.2 h per SSL run and ~1.5 h per supervised run, alone on a GPU. 15–20 runs ≈ 5–8 h on 5–7 GPUs.
- **Booking:** `gpu_ledger.md` before launch, freed after.
- **After the runs:**
  - relay run dirs and checkpoints to gaint `/home/noob/work/cv02_noob_el/el_sk1` through the laptop, manifest + MD5;
  - check that the relay finished (handbook D19).
- **Launcher fix (found 21 Oct).**
  - `launch_set_p17.sh` and its predecessors logged `rc=\$?` after a `$(date)` substitution, so the logged rc was always 0, whatever the training exit code. Reproduced: `false; echo "[$(date)] rc=$?"` prints rc=0.
  - `launch_set_sk1.sh` captures rc first and re-scores only on rc = 0.
  - Earlier "all rc = 0" statements in P-series READMEs therefore rest on the re-score JSONs and logs, not on the rc field. Reported to the critic and the leader.

## 12. Smoke (after all gates, before the real launch)
`scripts_cv02/sk1_smoke.spec`:
- `smoke_BsDB` and `smoke_AB`: 300 steps, λ on from step 0;
- `smoke_BsDBx`: 60 steps with the D7 exclusion; its log must say "dropped 7 of 455";
- `chk_off_metrics`: 20 steps, absh off, no absh keys in `metrics.json`.

Checked by the critic, with the mechanism log (head_drift, predicted vs GT rare shares), before the real launch.

**Disclosure.** At 13:55 IST on 21 Oct I launched the identity checks and v1 smoke runs on cv02 GPUs 4–6:
- the critic had allowed this in `review_v1.md`;
- the leader's no-launch instruction reached me about 2 minutes later.

What happened:
- The checks died at start: hyphenated `--exit-after-step`, which argparse rejects.
- I stopped the smoke runs at 13:57 IST: smoke_BsDB about step 60, smoke_AB about 110, smoke_BsDBx about 50.
- Outputs moved to cv02 `el_sk1/reports/aborted_2026-10-21/`; ledger rows freed.
- Seen: training-loss lines only (no val/test). They will be re-run under §12 after the gates.

## 13. Not claimed
SKCDF itself or its numbers; SKCM; λu = 10; current-model PLs; other fractions or split seeds (critic ideas.md #5: needed for a thesis claim, not for SK1); tuning of ω, R or the keep probabilities.

## Changes from v1 (review_v1 items)
1. Twins: §9 four cell sets; §5 both D7 branches with specs; `data.unlabeled_exclude` in code.
2. Prior-shift control: §8 item 6, script `rescore_logit_adjust.py` (τ = 1 fixed, val-only grid).
3. Mechanism log: §4, in code and tests; checked in the smoke run.
4. Deviations table: §4.
5. Test count: 14 in v1 (not 16), 15 now.
6. A5c provenance: §7 adds `chk_A_5pct_s0` against P12's log.
7. Machine: §11, leader's decision pending, recorded here when made.
Plus: launcher rc bug and the `--exit_after_step` flag (critic's message) fixed; smoke disclosure (§12).
