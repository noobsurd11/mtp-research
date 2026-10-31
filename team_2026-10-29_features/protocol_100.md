# Protocol 100: SUP100-PF, MIM100-PF and CP100 vs SUP100 at 100% labels (v1)

runner, 30 Oct 2026 12:02 IST (v1.1), 16:41 IST (v1.2: resume section). Status: **v1.2. v1 APPROVED by coach conditional on gates 1-7 + G5 (`review_100_v1.md`); gate results below (v1.1 section). All gates pass except gate 6 (CP100 decoy go/no-go at 2k: shortcut FLAG); coach's gate 6b (4k, three pre-stated conditions) gave GO at 12:27 IST. Launched 12:05:34 IST.** v1 kept as `protocol_100_v1.md`. v1.1 kept as `protocol_100_v1.1.md`. Ordered by the user via team-lead (30 Oct 10:45): all 5% work stops (CP5 stopped, not scored); everything moves to 100% labels. Binding inputs: `coach_100.md` (accepted in full by team-lead), coach's pre-review of v0 and rulings 1-5. v0 is kept as `protocol_100_v0.md`.

## What I had seen when writing this
- MIM5 (CONFIRMED n.d., every delta negative), DDeP5 (CONFIRMED n.d.), AM KILL. CP5: 2k smoke and decoy PASS only; never scored (its s1/s3 rescore JSONs were written automatically at run end and are unopened).
- SUP100 / FINAL numbers (Track M). The encoder-erasure table (`coach_100.md` §0), re-derived by me (below). `diag_5pct_to_100pct.md` (not read in full by me; coach's rulings after it are in `coach_100.md`).
- No 100% number of any new arm.

## Questions (contrasts)
1. **Pool via the encoder:** MIM100-PF − SUP100-PF (does the MIM encoder help when fine-tuning keeps it?). The direct answer to the user's question.
2. **Recipe:** SUP100-PF − SUP100-g (does the encoder-preserving fine-tune itself help?).
3. **Pool via copy-paste:** CP100 − SUP100-g (C1, tau 0) with C2 (both arms with logit adjustment tau 1) as co-condition for a crack claim; C3 (CP100 tau 0 vs SUP100-g + LA) reported.
4. Reported, not a verdict: MIM100-PF − SUP100-g (bottom line).

## Arms (5 seeds each, 0-4; 20,000 steps, batch 8, final weights; all 478 train labels)
| Arm | Change vs SUP100-g | Runs |
|---|---|---|
| **SUP100-g** | none (SUP100 recipe, fresh on gaint at the deploy commit) | `f3_SUP_100pct_s0..4` |
| **SUP100-PF** | `training.encoder_pf` {freeze 1000, ramp 1000, lr_mult 0.1, wd 0} | `f3_SUPPF_100pct_s0..4` |
| **MIM100-PF** | PF as SUP100-PF + `model.encoder_init=` encoder_final.pth (md5 1c3df959) | `f3_MIMPF_100pct_s0..4` |
| **CP100** | `cp` stream λ 1 (house optimizer) | `f3_CP_100pct_s0..4` |

- Base opts (Track M SUP100): `supervised.yaml seed=K data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice` (train.txt 478 cells, md5 842f27c4).
- Plus, for every arm, `training.val_every=20000` (val only at the final step) **if** the val-off identity passes (speed-ups below); else val every 500.
- The cv02 SUP100 (p6_L3 s0-2 at 824fab0 + p16_A s3-4 at bac5264; 0.474 −noisy) and FINAL 0.492 are another machine and two commits: yardsticks only.

## Machine
- cv02 at 10:51 IST: **0 of 8 GPUs** qualify (each has other users' processes of 9-42 GB). So **gaint, all 4 arms** (one hardware type, one commit).
- A watcher checks cv02 every 10 min. If ≥ 3 GPUs qualify, team-lead is told before anything moves. cv02 is used only if ≥ 4 GPUs qualify **and** I1 at the deploy commit on an A6000 (100% opts, all switches off) is bit-identical for 2,000 steps (loss/lr/val lines) to both `p6_L3_100pct_s0.stdout` and `p16_A_100pct_s3.stdout` with md5-identical data; then the cv02 SUP100 seeds are reused there. The choice is written here before launch.

## Code (gaint `el_f3`, branch f3; deploy commit **e544133**)
- e544133 = 2751aa8 + `20aad52` (CP at 100%: no unlabelled-train list at labeled_fraction ≥ 1, pool backgrounds only; optional `cp.library_exclude`) + PF (`training.encoder_pf`: two param groups, group 0 = all but `encoder.*` with house lr / wd / schedule, group 1 = `encoder.*` with lr × lr_mult, wd, multiplier = house × 0 for steps < freeze, then a linear ramp over `ramp`; no requires_grad toggling, BN in train mode, RNG unchanged; encoder lr on its own "PF encoder lr=" log line, the step line unchanged).
- `git diff 2751aa8 e544133`: `src/data/copy_paste.py`, `src/trainers/trainer.py`, `scripts/train.py` + tests.
- **Disclosure (coach):** during the PF freeze (lr 0) the encoder gradients still count in the global grad-clip norm (1.0), so decoder steps can be clipped by encoder gradients, unlike a requires_grad=False freeze. It holds identically in both PF arms. Suite: 285 passed, 3 skipped (F1_IMAGENET=1); new tests: CP 100% without the unlabelled list, library_exclude, < 100% unchanged; PF absent = one group / one lambda, PF neutral (freeze 0, ramp 0, mult 1, wd = base) = house bit for bit, freeze keeps encoder weights while BN statistics adapt, group-1 lr / wd, off in the configs.

## CP100 design (coach_100.md (b))
- **Library:** all train cells minus the 7 D7 twins (`cp.library_exclude=data/splits/d7_twin_train_cells.txt`), CP5 filters (≥ 20 px, edge ring, inactive ring, contrast ≥ 3 GL) + P3 residual fix: **566 components, 151,993 px** (CFVS 302, CSIR 175, ARTS 68, BMRK 21) from 832 candidates. With the twins it would be 591 / 184,686 px: the twins alone are 25 components and 18% of the px (test-cell cracks), hence excluded. Kept-list md5: from the smoke's `cp_library.json` (frozen here before launch).
- **Backgrounds:** pool part of `mim_pool_v11.txt` only (11,219 cells; R1-R4); held-out `mim_monitor_v11.txt` (256) for the decoy control only. No train backgrounds at 100% (coach: each labelled cell is already seen about 335 times; pasting onto labelled cells needs GT-aware ring code).
- **Rate and weight as CP5:** λ 1, cp.batch 4, K ~ U{1,2,3}, components uniform, no source rebalancing; loss crack on M, ignore 1 px band, not-crack 2-6 px ring, / N_lab, no Dice on the stream. Labelled crack px per step at 100% (masks): 478 cells × mean 569 px × batch 8 ≈ **4,549 px/step** (5%: 6,252) < 12k, so cp.batch stays 4; the measured pasted px/step comes from the smoke (expected about 2.1k, ratio about 0.47 ≥ 0.4).
- House optimizer (one change per arm).

## Gates before launch (all at e544133 on gaint; smokes running since 11:04 IST, `reports/f100/smoke`)
1. **I1-100 at f3:** no switch, 100% opts s0, vs el_m 1be64e1 (`i1_elm`, already run): loss/lr/val lines bit-identical for 1,000 steps (a1, which runs to 2,000).
2. **PF neutral + encoder_init=mim_step0** vs no switch, 1,000 steps (a2 vs a1).
3. **CP λ 0** (CP100 section, λ 0) vs no switch, 1,000 steps (a3 vs a1).
4. **Val-off identity (speed-up 1):** loss/lr lines bit-identical for 2,000 steps (4 skipped vals), house opts (b1 val off vs a1) and CP opts (b3 val off vs b2).
5. **PF smoke (val-blind gate):** SUP100-PF (c1) and MIM100-PF (c2) seed 0 to 2,000 steps: per-stage mean cosine of layer3 and layer4 to their init ≥ 0.5 (ImageNet for c1, encoder_final for c2); 2k loss reported. **F2-100:** c2's log shows "Encoder initialised ... md5 1c3df959".
6. **CP smoke (b2):** finite losses, `cp_*` logs, measured pasted crack px/step, library summary; **decoy go/no-go** at 2k vs the SUP 2k checkpoint (a1, same seed and machine): flag if CP's decoy crack rate > 2× SUP's or > 0.05 (library and held-out cells as CP100).
7. **Optional 4th lane (speed-up 3):** d1 (no switch + `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`) bit-identical to a1 for 1,000 steps, and reserved memory per fine-tune ≤ 5.5 GB; then 4 fine-tunes at once under the 2 GB rule.
- Already logged at 2751aa8 (useful, not sufficient): el_m vs el_f2, el_m vs el_f1, el_f2 + mim_step0, all IDENTICAL for 1,000 steps at 100%.

## Primaries, rule, outcomes
- Primaries: test crack IoU, crack relF1@2, inactive IoU (revised masks, argmax, final weights). Rule 1, house divisor 3 (/5 descriptive). Verdict sets all 50 and −noisy: pass = BETTER on both, or BETTER on one with a same-sign n.d. on the other; WORSE on either fails. −twins / −both reported.
- **Power (E, Track M / diag):** −noisy SUP100 sds give thresholds at the 0.01 floor for crack and relF1; clean MDE crack **0.012**, inactive **0.032**. On all 50 one SUP100 seed in five can fail on CSIR_00070 (sd 0.078, threshold about 0.09-0.13), so in practice a pass is −noisy BETTER with a same-sign n.d. on all 50.
- **CP100 crack claim:** C1 BETTER on crack IoU or relF1@2 and C2 BETTER on the same primary, worse on none, two-set rule; width flag crack relP@2 drop > 0.05.
- **If a contrast passes:** the arm's 5-seed mean-softmax ensemble vs its comparator's ensemble on the same machine (MIM100-PF vs SUP100-PF, with SUP100-g also shown; SUP100-PF vs SUP100-g; CP100 vs SUP100-g), crack bias chosen on val by FINAL's rule (max val relF1@2, val crack precision drop < 0.05, TTA off), paired image bootstrap as Track M contrast 1. FINAL 0.492 descriptive. One more test opening, counted.
- **Kill:** n.d. on all three primaries in both sets, or WORSE on any: that contrast is closed at 100%.
- Multiplicity: 3 contrasts × 3 primaries × 2 sets (+ CP C2), no correction, disclosed.

## Pre-stated expectations (S), next to the MDE (crack 0.012, inactive 0.032)
- **SUP100-PF − SUP100-g:** crack −0.01 to +0.02, sign uncertain (coach). ImageNet's deep features may help BMRK (Track D's frozen-feature ranking) or underfit EL at 0.1×.
- **MIM100-PF − SUP100-PF:** unknown under PF (coach ruling 1). diag's −0.010 to +0.005 applied to plain MIM100 (erased layers), not to PF.
- **CP100 − SUP100-g:** crack 0 to +0.015 at tau 0, n.d. likeliest after LA (C2); crack precision −0.01 to −0.03; inactive n.d.

## Reported (never change a verdict)
Four cell sets; per source; per class; crack capture (P, R, relP/relR@2, component recall/precision); mIoU_rob; paired image bootstrap and leave-top-3-out; LA tau 1 for every arm; E1 (ext 106) crack recall split scuff + half-cut vs other (`scripts/e1_context.tsv`), crack IoU, inactive IoU; crack px on crack-free cells (test / val / ext); CP E3b decoy on the 20k checkpoints of CP100 and SUP100-g; **encoder cosine table** (per-stage cosine and norm ratio to init, `scripts/f3/enc_cosine.py`) at 2k (smoke) and 20k for all four arms.

## Runner's re-derivation of coach_100.md §0 (E, `scripts/f3/enc_cosine.py`, gaint CPU, `el_f3/reports/f100/enc_cosine_rederive.json` md5 89ed1365)
Per 4-D encoder conv tensor cosine, mean per stage; norm ratio = stage-concatenated L2 (final / init).

| pair | conv1 | layer1 | layer2 | layer3 | layer4 |
|---|---|---|---|---|---|
| MIM final vs ImageNet | 0.996 / 0.87 | 0.859 / 0.99 | 0.761 / 1.12 | 0.618 / 1.45 | 0.533 / 1.71 |
| A5c-f1 s0 vs ImageNet | 0.980 / 0.77 | 0.379 / 0.53 | 0.135 / 0.51 | 0.010 / 0.07 | −0.001 / 0.02 |
| A5c-f1 s1 vs ImageNet | 0.962 / 0.76 | 0.377 / 0.51 | 0.147 / 0.55 | 0.006 / 0.07 | −0.000 / 0.02 |
| MIM5 s0 vs MIM init | 0.976 / 0.79 | 0.327 / 0.49 | 0.139 / 0.48 | 0.005 / 0.05 | −0.000 / 0.00 |
| SUP100 p6_L3 s0 vs ImageNet | 0.985 / 0.86 | 0.396 / 0.75 | 0.150 / 0.63 | 0.018 / 0.10 | 0.001 / 0.06 |
| SUP100 p6_L3 s1 vs ImageNet | 0.983 / 0.85 | 0.395 / 0.73 | 0.152 / 0.66 | 0.005 / 0.08 | 0.001 / 0.06 |
| SUP100 s0 vs s1 (finals) | 0.997 | 0.623 | 0.223 | 0.037 | 0.007 |

Every cosine matches coach's table to 3 decimals; norm ratios differ slightly by definition (coach: layer2 0.60, layer3 0.09 for SUP100 s0). conv1 ranges 0.96-0.99 (not 0.98 flat).

## Lanes, order, ETA (gaint)
- Memory (E, 5%): fine-tune 6.8 GB, CP 9.5 GB, finllm 5.9 GB of 32.1; gates own peak + 2 GB (fine-tune 9,000, CP 11,600 MiB), flock + 120 s spacing (f2g run_one v5 logic). 3 fine-tunes leave 4.9 GB; 2 CP + 0 fine-tune leave about 6.4 GB; 1 CP + 2 fine-tunes leave 2.2 GB.
- **Order (team-lead: the PF contrasts first; coach: seeds in order across arms, score once after all 20):** waves of the three fine-tune arms by seed (SUP100-g sK, SUP100-PF sK, MIM100-PF sK for K = 0..4), then CP100 s0..s4 two at a time. A stopped queue leaves matched seeds in the PF contrasts.
- Speeds (E, 5%; same step cost at 100%): fine-tune 2.25 steps/s with 3 at once (about 2.5 h per run); 2 CP at once about 2.2 steps/s each (2.5 h).
- **ETA from launch:** fine-tune waves about 12.3 h (5 × 2.47 h), then CP about 6.8 h (2 + 2 + 1): **about 19 h**; with val off about 5-10% less (about 17.5-18 h); with a 4th lane (if d1 passes) less again. Launch about 12:15-12:30 IST after APPROVED → fine-tunes done about 00:30-01:00, CP about 06:30-07:30 on 31 Oct, scoring (m0 default + tau 0/1, LA, manifest, E3b, crack-free px, cosine table) about 30 min after, then coach's recompute.
- Interleaving CP from the start (1 CP + 2 fine-tunes) ends at about the same time (about 19 h) but delays the PF contrasts, so fine-tunes first.

## Not claimed
CP at 5% (stopped, not scored); DDeP at 100% (dropped: fine-tuning overwrites the decoder, final-vs-init cosine 0.09); plain MIM100 (dropped by coach: it would test only conv1/layer1); cross-machine contrasts with the cv02 SUP100 / FINAL beyond descriptive; anything about pool representation learning beyond these arms.

## v1.1: gate results (smokes 11:04-11:57 IST at e544133, gaint; `el_f3/reports/f100/smoke/GATES.txt`)
| gate | check | result |
|---|---|---|
| 1 | I1-100: a1 (no switch) first 1,000 steps vs el_m 1be64e1 (loss/lr/val lines) | IDENTICAL (22 lines) |
| 2 | PF neutral + encoder_init=mim_step0 (a2) vs a1, 1,000 steps | IDENTICAL (22 lines) |
| 3 | CP λ 0 (a3) vs a1, 1,000 steps | IDENTICAL (22 lines) |
| 4 | val off vs val every 500, step lines 2,000 steps: house (b1 vs a1), CP (b3 vs b2) | IDENTICAL (40 / 40 lines; 0 val lines in b1, b3) |
| 5 | PF smoke at 2k, layer3 / layer4 cosine to init ≥ 0.5 | SUP100-PF 0.996 / 0.997, MIM100-PF 0.998 / 0.999: PASS |
| G5 | resumed to 4k, layer3 / layer4 ≥ 0.8 | SUP100-PF 0.975 / 0.985, MIM100-PF 0.986 / 0.990: PASS (lr_mult 0.1 kept) |
| F2-100 | MIM100-PF log "Encoder initialised (216 tensors, md5 1c3df959)" = encoder_final.md5 | PASS |
| 6 | CP100 smoke (b2) + decoy go/no-go at 2k vs SUP a1 (248 held-out cells, 553 components) | smoke OK; decoy SUP 0.0031, CP 0.0076 (> 2 × SUP; < 0.05): **FLAG** |
| 7 | d1 expandable_segments vs a1 1,000 steps; reserved per fine-tune | IDENTICAL; 6,442 MiB (vs 6,830): 4 × 6.44 + 5.9 = 31.7 GB > 30.1 allowed, **no 4th lane**, setting not used |

- House reference at 2k (a1, SUP100-g s0 vs ImageNet): conv1 0.997, layer1 0.731, layer2 0.444, layer3 0.070, layer4 0.003 (norm 0.33 / 0.21): the house recipe has already erased layer3/4 at 2k; PF keeps them (≥ 0.975 at 4k).
- 2k losses: SUP100-g 0.711, SUP100-PF 0.620, MIM100-PF 0.699, CP100 0.699 (sup 0.692); 4k: SUP100-PF 0.491, MIM100-PF 0.499. PF encoder lr at steps 1,000 / 1,500 / 2,000: 1.0e-7 / 5.0e-5 / 9.8e-5 (freeze, ramp, 0.1 × house).
- **CP100 library, frozen:** `cp.library_exclude = el_f3/reports/f100/cp100_library_exclude.txt` (13 stems: 7 D7 twins + 6 train cells whose E-SCDD scuff (25) px are crack in masks_escdd, 649 px: ARTS_00051_r6_c2, CSIR_00092_r11_c5, CSIR_00117_r8_c4, CSIR_00155_r5_c5, CSIR_00161_r4_c6, CSIR_00176_r5_c2; md5 903293c9). Library from 465 cells: 816 candidates, **554 kept, 151,039 px (CFVS 302, CSIR 164, ARTS 67, BMRK 21)**, kept-list md5 **a326dffd60549e8c03af6a2b1e7f0a87** (`el_f3/reports/f100/smoke/cp100_library_kept.tsv`). BMRK's 21 is a disclosed limit. `CFVS_00024_r3_c3` keeps 54 px of E-SCDD star (28) labelled crack (coach: not excluded; it stays in B1 list S).
- Paste rate: `cp_crack_px` is logged per image: 516 px/image × batch 4 = **2,064 pasted crack px/step**, 0.45 × the labelled 4,549 (≥ 0.4): cp.batch 4 confirmed. Ring 2,303 px/image; 4.6 placement fails per step; p14 on paste 0.306, on ring 0.030 at 2k.
- **Gate 6b (coach, `review_100_v1.md`; post-hoc amendment, disclosed; the CP verdict rule is unchanged and E3b at 20k keeps the original thresholds):** a1 and b2 resumed 2k → 4k (bit-identical `--resume`), cp_decoy rerun on the same 248 cells / 553 components at step 4,000. Pre-stated GO rule (before the 4k numbers): (1) CP decoy ≤ 0.05; (2) CP decoy ≤ 2 × SUP decoy or ≤ 0.0094; (3) CP decoy / CP real ≤ 0.036 (condition 3 added by coach before the numbers; the first gate-6b script lacked it and was stopped before its decision, el_f3/reports/f100_gate6b2.sh decided). 4k: SUP real 0.2462, decoy 0.0010, background 0.0006 | CP real 0.2713, decoy 0.0039, background 0.0007 → (1) yes; (2) yes, only through the 0.0094 floor (CP decoy is 3.7 × SUP's, above 2 × SUP = 0.0021); (3) 0.0143 yes. **Decision: GO** (CP_GO written 12:27:37 IST; HOLD removed). CP100 runs to completion after the 15 fine-tunes, whatever opening 1 shows.
  - **Hindsight (31 Oct 2026, 07:14 IST, after opening 2):** at 20k the CP100 decoy rate is 0.0125 (SUP100-g 0.0028; 4.41 ×; original rule FLAG; 6b condition 2 fails, 3 holds at 0.031), about 3 × its 4k value (0.0039): the gate-6b premise that the decoy rate was not growing did not hold. See coach's note "Gate 6b in hindsight" in `review_100_v1.md`. CP100's verdict is n.d. on every primary, so no claim rests on it.
- **Gate 6 FLAG:** per the pre-registered rule no CP100 launch until coach rules. The CP100 jobs come last in the queue (after the 15 fine-tunes, about 11-12 h after launch); the queue waits at the first CP job for `reports/f100/CP_GO` (run) or `CP_STOP` (CP100 not run, logged). Pre-commitment kept: the CP decision uses the decoy evidence only, made before opening 1, never on opening-1 numbers.

## v1.1: launch settings
- Deploy e544133; `VAL=training.val_every=20000` for every arm (gate 4); `MAXC=3`, no expandable_segments (gate 7); gates fine-tune 9,000 / CP 11,600 MiB + 120 s spacing under `reports/f100/gate.lock`; rc captured before $(date).
- Scoring in two pre-registered openings (coach + team-lead): **opening 1** = the 15 fine-tunes when all 15 trained rc 0 (`el_f3/reports/f100/post_opening1/`; final line `[date] f3 opening1 scoring done: post rc=N` in `el_f3/reports/f100/launch.log`); **opening 2** = CP100 (if run) when its 5 runs trained rc 0, reusing SUP100-g's opening-1 per-cell files unchanged (manifest re-checked), plus E3b decoy at 20k and crack px on crack-free cells (`post_opening2/`, line `f3 opening2 scoring done`). No per-run scoring; CP100 is never stopped, re-ordered or re-parameterised on opening-1 numbers; no protocol_100 parameter changes after opening 1.
- ETA (val off saves the in-training val passes): fine-tune waves about 11.5-12 h from launch → opening 1 about 00:00-01:00; CP100 (if GO) about 6.5 h more → opening 2 about 07:00 on 31 Oct.

## v1.2: gaint reboot and resume (30 Oct; coach re-diffed independently: the s1 runs count as-is)
- **Event:** gaint rebooted at 16:28 IST (orderly systemd shutdown 16:28:37 in the user-session journal, boot 16:29; no OOM / kernel / watchdog line, no pending update; likely a manual reboot from the console; the system journal is not readable by our account). Root's finllm restarted by itself. All our tmux sessions ended. cv02 unaffected.
- **Runs hit:** wave 2 (s1) only; wave 1 (s0) had finished. Atomic checkpoints and lost steps: SUP100-g s1 at step 16,000 (log reached 16,450; 450 steps re-computed), SUP100-PF s1 at 12,000 (12,600; 600), MIM100-PF s1 at 12,000 (12,150; 150).
- **Integrity before any overwrite** (`el_f3/reports/f100/ckpt_integrity_1635.txt`, md5 a59fcf60): s1 latest.pth md5 / step: SUP 1f6ee1cb / 16,000, SUPPF dee1d13c / 12,000, MIMPF 87a1768f / 12,000; s0 finals SUP fa8550ca, SUPPF 15bea4c6, MIMPF 9c78b857 (step 20,000); all torch.load OK. Data, splits, lists, CP library / exclude list, MIM encoder (1c3df959) and pool image bytes (855daabd) md5-checked; masks_escdd and labelled images identical to cv02; 0 tracked changes at e544133.
- **Resume:** `el_f3/reports/f100_resume.sh` (scripts/f100_resume_gaint.sh): pre-reboot stdout copies `<run>.prereboot.stdout` (SUP 4e50bba6, SUPPF ee1d7a25, MIMPF 628364fb) made before any append; `train.py --resume` from latest.pth with the queue's opts (val off, no --overwrite), output appended to the run stdout after one marker line ("===== RESUME after the gaint reboot of 30 Oct 16:28 (train.py --resume from checkpoints/latest.pth) ====="); "trained <run> rc=N (resumed)" in launch.log (rc before date; counted by the opening-1 trigger). Each start through the f100 gate. Then the queue (skipped the 6 existing s0 / s1 dirs, continues with s2) and the opening trigger were restarted. CP_GO present, no HOLD.
- **Identity:** the resumed loss/lr lines over the re-computed steps equal the pre-reboot lines (timestamps and speed stripped; `el_f3/reports/f100/resume_idchk.txt`, md5 8d47af70; script `reports/f100_resume_idchk.sh` md5 99793238): SUP s1 16,050-16,450 IDENTICAL (9 lines); SUPPF s1 12,050-12,600 IDENTICAL (12) and PF encoder lr lines IDENTICAL (12); MIMPF s1 12,050-12,150 IDENTICAL (3) and PF IDENTICAL (3). Coach's independent re-diff agrees (1 marker, 2 headers, 0 tracebacks each). The resumed s1 runs are bit-identical continuations and count as-is.
- **Disclosed slip:** the first automatic run of the identity check reported "DIFFER or incomplete (0 lines)" for the loss/lr part because of an awk field-index bug (it read the "step" token instead of the step number, so nothing was selected on either side); fixed and re-run before any decision.
- **Timing:** the resumed s1 runs ended at 16:56 / 17:32 / 17:35, within about 30 min of the pre-reboot plan; opening 1 about 01:00-01:30 IST (my 16:30 estimate of 03:00-03:30 was too pessimistic); CP100 / opening 2 about 08:00 on 31 Oct.

## Opening 1 memory disclosure (31 Oct 2026, 01:46 IST)
- Opening-1 scoring (rescore, m0 default / tau 0 / tau 1, LA; 00:59-01:33 IST) overlapped CP100 s0/s1 training on the same GPU; the minimum free GPU memory over the overlap was not recorded (gate reads ≥ 6,000 MiB only between passes; estimate ~2.2-2.6 GB); root's finllm_chat.py ran throughout (PID 6206, up since 16:29:40 30 Oct); no out-of-memory error in any log. From 01:45 a 10 s free-memory log runs on gaint (`el_f3/reports/f100/gpumem.log`); the m0 pass peak is measured in opening 2 and any later concurrent gate is that peak + 2 GB.
- **Correction (31 Oct 2026, 07:11 IST), from the peaks measured in opening 2 with finllm alone (1 s samples):** rescore 4,398 MiB, m0 passes 4,002, LA 5,106, cp_decoy 3,292. On the measured opening-1 baseline (two CP100 runs + finllm: 6,609-6,612 MiB free) the estimated minimum is ~2.2 GB during rescore, ~2.6 GB during the m0 passes, and **~1.5 GB during the LA pass (01:27:47-01:33:19, about 5.5 min): below the 2 GB finllm floor** (estimate, not a reading). finllm (PID 6206) survived; no out-of-memory error in any log. The earlier "~2.2-2.6 GB" covered rescore and m0 only. Later concurrent gates for scoring passes = measured peak + 2,048 MiB (LA 7,154 MiB).
