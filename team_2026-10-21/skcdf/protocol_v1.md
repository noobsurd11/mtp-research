# SK1 protocol v1: SKCDF's auxiliary balanced head (ABSH), adapted to EL cells, at 5% labels

Status: DRAFT for review (agent 4). Not locked. No run, real or smoke, before `APPROVED` in `review_v1.md`.
Written 21 Oct 2026, agent 3. Design and reasoning: `design.md` (same folder).

**What I had seen when writing:** all P13 to P19 results (incl. P17 BsD5, BsM5, A5c test numbers and bin-0 shares); class pixel counts of the 5% labelled cells (train split only, 21 Oct). No SK1 number exists. The ABSH adaptations in `design.md` §4 were fixed from the paper, the official code and train-split counts, without any test or val number.

## 1. Question
On the P17 decoupled recipe (BsD5) at 5% labels, does SKCDF's auxiliary balanced segmentation head, adapted to thin rare classes on 2-D EL cells, raise test crack IoU, inactive IoU or crack relF1@2 over BsD5?
Secondary: is any effect SSL-specific (Q2), and does the thin-structure band matter (Q3)?

## 2. Hypothesis
H1: the balanced head moves the evaluated head's class prior toward crack and inactive, cutting confident misses (bin-0 share 0.53 / 0.54 in BsD5) and raising rare-class IoU. Risk: lower precision and wider cracks.

## 3. Data (version D0)
BenchmarkEL `dataset_20211104` images, revised masks (`labeled/masks_escdd`), split seed 0, 5% = 23 labelled cells, in-domain unlabelled pool (455 cells), test 50 cells, val 54 cells. Same files as P13/P17 (cv02 `el_p7/data`).
**Dependency:** `data/decision.md` (critics). If it keeps D0, nothing changes. If it changes only the test set, all SK1 and reference checkpoints are re-scored on it (no retraining) and both test sets are reported. If it changes the training split, this protocol is re-issued as v2 and every arm, references included, is retrained on one machine.

## 4. Code
- gaint worktree `/home/noob/work/el_sk1`, branch `sk1`, commit **`b90008e`** on top of `f2f20d3` (P17). Diff: `git -C /home/noob/work/el_sk1 diff f2f20d3 b90008e` (4 files, +440/−8). Tests: `tests/test_absh.py` 16; full suite 217 pass, 7 skipped.
- Code check (21 Oct 13:47, gaint, 20 steps, batch 2+2, not a smoke run): both arm types run end to end, rc 0; logged keep probs at 5% match design §4 (bg 0.0049, padding 0.0113, inactive 0.8761, crack 1.0); `test_final_absh` written.
- New opt-in switches (defaults off keep `f2f20d3` bit for bit):
  - `absh.enabled` (bool); `absh.ref_classes` [14, 11]; `absh.band_radius` (2; 0 = no band); `absh.head_ema` (0.99).
  - Implementation as `design.md` §4: keep prob p_c = min(1, N_ref/N_c) from all labelled cells; band of always-kept pixels within R of a rare target; aux CE summed over kept pixels / all pixels, aux Dice over kept pixels; aux heads copied from the main head at step 0; unlabelled aux loss on `decoder_u` with PL = teacher aux head argmax (≥ 0.95), keep prob annealed 1 → p_c linearly over steps; head transfer H→D→H after each step; teacher = EMA of student incl. `aux_l`.
- Unit tests: off = old step (bit-identical losses/params after N steps on CPU); keep-prob table; band; annealing; transfer order; checkpoint/resume bitwise; supervised arm works.
- Logged every 50 steps in addition: `loss_aux_sup`, `loss_aux_con`, kept-pixel share, PL class counts for crack and inactive from the main and aux teacher heads (`pl_csv`).
- Extra evaluation at the final step (test, secondary, never for selection): teacher aux head; student encoder + `decoder_u` main head (SKCDF's inference path); student encoder + `decoder_u` aux head.

## 5. Arms (5% labels, 20,000 steps, final-step weights, cv02)
Fixed for all: P17's BsD5 option string (P13/P17 recipe: `smp_unetpp`, `ce_dice`, labelsafe aug, batch 8 + 8, Adam 1e-3, cosine, `t_pos` 0.95, λ 0 to step 2,000 then ramp to 1.0 by 4,000, separate BN forward, CutMix 0.5, `decouple_decoder`, ω 0.99) for SSL arms; P12/P13 A5c option string for supervised arms.

| Arm | Run names | Change vs its comparison arm | Seeds | Status |
|---|---|---|---|---|
| A5c | `p12_A_5pct_s0..2`, `p13_A_5pct_s3..4` | reference (supervised) | 0–4 | exists, cv02 (reuse after §7 check) |
| BsD5 | `p17_BsD_5pct_s0..4` | reference (P17) | 0–4 | exists, cv02 (reuse after §7 check) |
| **BsDB5** | `sk1_BsDB_5pct_s0..4` | BsD5 + ABSH (`absh.enabled=true`, band 2) | 0–4 | new |
| AB5 | `sk1_AB_5pct_s0..4` | A5c + ABSH, labelled side only | 0–4 | new |
| BsDBn5 | `sk1_BsDBn_5pct_s0..4` | BsDB5 with `absh.band_radius=0` (SKCDF's mask, our reference/clip) | 0–4 | new |

15 new runs. Seeds 0–4 everywhere; training seed varies, split seed 0.

## 6. Metrics
- Primary (P8 on): test crack IoU, inactive IoU, crack relF1@2; revised masks; argmax; EMA teacher main head; step 20,000.
- Secondary: crack/inactive precision and recall; relP@2 (width check); AP and bin-0 share; val; E1 per-cell (test and ext); the three extra paths of §4; PL rare-class counts over training.

## 7. Reference reuse: identity check (before any SK1 run is counted)
New code with `absh.enabled=false`, on cv02, same Python env as P17:
- `chk_BsD_5pct_s0`: BsD5 s0 options, 2,500 steps (past the λ ramp start) → every logged line must equal `p17_BsD_5pct_s0.stdout` up to step 2,500.
- `chk_A_5pct_s3`: A5c s3 options, 2,500 steps → must equal `p13_A_5pct_s3.stdout` (bac5264) up to 2,500.
If both match: A5c and BsD5 are reused (pooling rule: identical config and code path, same machine). If either differs (e.g. a driver change since 13 Oct): rerun A5c and BsD5 s0–4 under the new code on cv02 before analysis (10 more runs), and use only the reruns.

## 8. Decision rules (P8 rule 1, 5 vs 5, `scripts/ssl_rules.py`)
1. **Primary: BsDB5 − BsD5.** BETTER on ≥ 1 primary and none WORSE → "adapted ABSH helps on the decoupled recipe". WORSE on any → "harms". Otherwise n.d., reported with each threshold as a share of BsD5 − A5c.
2. Secondary: **AB5 − A5c** (Q2: does ABSH help without unlabelled data).
3. Secondary: **BsDB5 − BsDBn5** (Q3: band).
4. Descriptive: interaction (BsDB5 − BsD5) − (AB5 − A5c) with a bootstrap CI over test cells; BsDB5 − A5c; BsDB5 − BsM5 (two changes); `decoder_u` main vs teacher within BsDB5 (paired per seed).
5. Width check: crack relP@2 drop > 0.05 vs the comparison arm is flagged; crack precision reported next to every crack IoU.
- Contrast count: 1 primary, 2 secondary, 4 descriptive. No multiplicity correction; the primary is the only confirmatory claim.
- Reading map (design §5): rule 1 pass + rule 2 n.d. → SSL-specific; both pass at similar size → head rebalancing, not SSL.

## 9. Robustness (reported, never changes a verdict)
Paired image bootstrap (2,000), leave-top-3-out, source split, **every contrast with and without `CSIR_00070_r8_c4`** (the balanced head may raise false crack there; per-cell FP on that cell reported per run), E1 per-cell metrics.
Collapse / flood watch: kept-pixel share and PL crack/inactive counts at steps 4,000 and 20,000; a run whose predicted crack share on test exceeds 5x GT is flagged (not excluded).

## 10. Selection and stopping
- No selection on test, ever. No val-based choice in v1 (all settings fixed above).
- Final-step weights only. If a run crashes, it is resumed from `latest.pth` (bitwise resume); no reruns with another seed.
- No seed extension in v1. If the primary is n.d. with |Δ| above half the threshold on a metric, an extension to 8 seeds may be proposed as v2, disclosed as post hoc.

## 11. Compute
- Proposed: **cv02** (references exist there; gaint has 1 GPU shared with ALHVR; `design.md` §7). One run per GPU, on GPUs with < 1,000 MiB used by others (21 Oct 13:39 IST: GPUs 4–6 free, 0–3 at 792 MiB, 7 has 5.5 GB of another user, excluded). ~2.2 h per SSL run, ~1.5 h per supervised run alone; 15 runs + 2 checks ≈ 5–7 h.
- Deployment: `git archive` of the `sk1` commit to `/tmp/noob_el/el_sk1`, `REVISION` file, `data -> /tmp/noob_el/el_p7/data`, md5 of the split files and masks checked against `el_p17`.
- tmux session `=sk1`, queue `gpu_queue` + `launch_set` copies, one queue only. Booked in `gpu_ledger.md` before launch.
- After the runs: relay run dirs and checkpoints to gaint `/home/noob/work/cv02_noob_el/el_sk1` with MD5 checks.
- If the leader rules gaint instead: all five arms rerun on gaint at 5 seeds (25 runs), no reuse; this protocol is re-issued with that change.

## 12. Smoke test (after APPROVED, before launch)
`smoke_BsDB` and `smoke_AB` 300 steps with λ forced on from step 0 (`ssl.warmup_steps=0 ssl.ramp_steps=0`) to exercise every path; plus the §7 identity checks. Checked by the critic before the real launch.

## 13. Not claimed
SKCDF itself or its numbers; SKCM; λu = 10; current-model PLs; other fractions or splits; tuning of ω, R or the keep probabilities.
