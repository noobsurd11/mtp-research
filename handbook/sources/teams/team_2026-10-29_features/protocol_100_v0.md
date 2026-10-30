# Protocol 100: MIM100 and CP100 vs SUP100 at 100% labels (v0, draft for coach)

runner, 30 Oct 2026 ~11:15 IST. Status: **v0 draft, not approved; no GPU run beyond smokes.** Ordered by the user via team-lead (30 Oct ~10:45 IST): all 5% work stops (CP5 stopped, not scored); everything moves to 100% labels; DDeP dropped (fine-tuning overwrites the pretrained decoder: final-vs-init cosine 0.09, `results/ddep5`).

## What I had seen when writing this
- MIM5 (CONFIRMED: n.d., every delta negative, crack −0.012), DDeP5 (CONFIRMED: n.d., crack +0.007, below the free bias), AM KILL; CP5 2k smoke and decoy go/no-go (PASS), CP5 never scored (no CP5 test number exists or was opened; its s1/s3 rescore JSONs were written automatically and are unopened).
- SUP100 numbers (Track M baseline.md; FINAL 0.492). No 100% number of any new arm.

## Question
At 100% labels (478 train cells), does (a) the MIM encoder (`encoder_final.pth`, md5 1c3df959) or (b) crack copy-paste onto unlabelled pool backgrounds beat SUP100, everything else fixed?

## Arms (one change each vs SUP100-g; 5 seeds; 20,000 steps, batch 8, final weights)
| Arm | Change | Runs |
|---|---|---|
| **SUP100-g** | none (SUP100 recipe re-run on gaint at the deploy commit) | `f3_SUP_100pct_s0..4` |
| **MIM100** | `model.encoder_init=/home/noob/work/el_f1/experiments/f1_mim_pre_s0/encoder_final.pth` | `f3_MIM_100pct_s0..4` |
| **CP100** | `cp` stream, λ 1 (CP5 loss design), library from the 100% train labels, pool backgrounds only | `f3_CP_100pct_s0..4` |

- SUP100 opts (Track M SUP100 = P6 L3 s0-2 + P16 A100 s3-4): `supervised.yaml seed=K data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice` (train.txt, 478 cells, md5 842f27c4 on gaint el_m and el_f2).
- The cv02 SUP100 (0.474 −noisy; FINAL 0.492) is another machine: descriptive only, unless the arms run on cv02 (below).

## Machine (team-lead: one hardware type per comparison)
- cv02 at 10:50 IST: **0 of 8 GPUs** usable (every GPU has other users' processes of 9-42 GB). So **gaint** for all three arms, SUP100 re-run there (SUP100-g).
- Opportunistic: if ≥ 3 cv02 GPUs are free (< 4 GB used by others) before MIM100 starts on gaint, MIM100 may move to cv02 against the existing cv02 SUP100 (checkpoints + stdouts backed up on gaint `cv02_noob_el/el_p6`, `el_p13`, step 20,000), after a cv02 identity check (deploy commit vs the SUP100 code at 100%, 1,000 steps) and the encoder file relayed with md5. Written here before launch.

## Code
- Deploy commit for all arms: **2751aa8** (`el_f2`) plus one CP-only change (new commit `f3`, to be made and reviewed): in `build_cp_stream`, at `labeled_fraction >= 1` there is no unlabelled train list (today it would read the missing `splits/seed0/unlabeled_100pct.txt`), so backgrounds are the pool part only; optional `cp.library_exclude` (a stem list removed from the library). No change to the no-switch or encoder_init path (diff + tests + identity, below).
- **Identity at 100% (smoke, running on gaint since 11:0x):** SUP100 opts seed 0, 1,000 steps, cwd el_f2: el_m 1be64e1 vs el_f2 2751aa8 (I1-100), el_f1 603e0d5 (I1f1-100), el_f2 + `encoder_init=mim_step0.pth` (I2-100). To be repeated for the f3 commit if coach wants it (or accepted by diff, cp-only).

## CP100 design (CP5 v1 + changes for 100%; coach to rule)
- Library: crack components (≥ 20 px, edge-ring / inactive-ring / contrast < 3 GL drops, P3 residual fix) from **all 478 train cells**, minus the 7 D7 twins? (proposal: exclude them, via `cp.library_exclude = data/splits/d7_twin_train_cells.txt`, as for every pool rule; they stay in the labelled stream as in SUP100). Count, px and source mix recorded before launch.
- Backgrounds: the pool part of `mim_pool_v11.txt` (11,219, R1-R4 filtered); held-out 256 (`mim_monitor_v11.txt`) for the decoy control only; no train backgrounds at 100% (every train cell is labelled). `p_pool` irrelevant (no (b) list).
- Loss / targets / placement / λ / batch 4 / logging: as CP5 v1 (crack on M, ignore 1 px band, not-crack ring 2-6 px, / N_lab, no Dice on the stream).
- Gates: λ 0 identity at 100% (1,000 steps vs SUP100-g no switch); CP100 smoke 2,000 steps; decoy go/no-go at 2k vs the SUP100 step-2,000 checkpoint of the same seed (flag: CP decoy rate > 2x SUP's or > 0.05); E3b decoy on the final checkpoints of both arms (reported).
- MIM100 gate F2-100: a 200-step fine-tune with `encoder_final.pth` (md5 1c3df959 in the log, finite loss).

## Primaries, rule, outcomes
- Primaries: test crack IoU, crack relF1@2, inactive IoU (revised masks, argmax, final weights). Rule 1, house divisor 3 (/5 descriptive), per arm vs SUP100-g; verdict sets all 50 and −noisy (pass on both, or on one with a same-sign n.d. on the other; worse on either fails); −twins / −both reported.
- Power (S, from cv02 SUP100): −noisy crack sd 0.002, relF1 0.004 → thresholds at the 0.01 floor; inactive sd 0.014 → about 0.023. All 50: one SUP100 seed fell to 0.297 on the noisy cell (sd 0.078), so the all-50 crack threshold may be about 0.13: the −noisy set carries the crack test.
- CP100 crack claim (as CP5): C1 CP100 − SUP100-g BETTER on crack IoU or relF1@2, and C2 (both arms with logit adjustment tau 1) BETTER on the same primary, worse on none. (Coach: keep C2 at 100%? FINAL's own +0.75 crack bias says the free bias still matters at 100%.)
- If an arm passes: its 5-seed mean-softmax ensemble with the crack bias chosen on val (Track M m9 procedure) vs the SUP100-g ensemble by the same procedure (same machine, the decisive contrast), and vs FINAL 0.492 (cv02, descriptive). One more test opening, counted.
- Kill: n.d. on all three primaries in both sets, or WORSE on any: closed at 100%.
- Secondaries: mIoU_rob, crack P/R, relP/relR@2, per source, E1 crack recall (scuff + half-cut vs other, `scripts/e1_context.tsv`), crack px on crack-free cells (test / val / ext), width flag (crack relP@2 drop > 0.05).
- Multiplicity: 2 arms x 3 primaries x 2 sets (+ CP C2), no correction, disclosed.

## Pre-stated expectation (S)
- MIM100: n.d. (MIM5 was negative on every primary; at 100% the labels dominate further). If anything, crack −0.01 to +0.005.
- CP100: crack 0 to +0.015 at tau 0, n.d. likeliest after LA; crack precision −0.01 to −0.03; inactive n.d.

## Compute and GPU plan (gaint, 3 lanes, gates own peak + 2 GB: fine-tune 9,000 MiB, CP 11,600 MiB, flock + 120 s spacing)
- Lane S: SUP100-g s0..4; lane M: MIM100 s0..4; lane C: CP100 s0..4 (one CP at a time: 1 CP 9.5 + 2 fine-tunes 6.8 + finllm 5.9 GB leaves 2.2 GB).
- Measured speeds (5%, same step cost): fine-tune 2.25 steps/s with 3 runs (2.5 h per run); CP 1.46 steps/s beside 2 fine-tunes (3.8 h), faster alone.
- About 15-16 h of runs from launch: S and M lanes done about 12.5 h after launch, CP lane about 16 h. Scoring as f2 (m0 default + tau 0/1, LA, manifest), then coach's recompute.
- Before launch (about 1-1.5 h): coach review, f3 commit + tests, identity 100% (running), CP100 library recount + preview, λ 0 identity, CP smoke 2k + decoy go/no-go, MIM gate F2-100.

## Not claimed
Anything at 5% for CP (stopped, not scored). DDeP at 100% (dropped). Cross-machine contrasts with the cv02 SUP100/FINAL beyond descriptive.
