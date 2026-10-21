# Protocol AL1 (v2): ALHVR adapted to EL on the P-series base, 5% labels (agent 1, 21 Oct 2026)

**v2 = v1 (APPROVED with launch conditions, review_v1.md) plus a pre-launch amendment from the user's answers (relayed by team-lead, about 14:45 IST): (a) machine cv02; (b) D7 = yes: the 7 train twins of test cells leave the unlabelled pool of every SSL arm, so BsM5 is re-run (+5); (c) add ALd5 at λ 0.3 (arm ALdh5, +5). No run of the main queue has started; no test number of any new run has been seen. Changes from v1 are marked [v2]. The final launch also waits for team-lead's go on a possible new (Kaggle) dataset.**

Status: v2 for review by agent 2. v1 status line, kept: Nothing beyond functional smoke (≤ 150 steps, gaint) and inference diagnostics (D0, D0b, D0c) has run. No test number of any new run has been seen.
Design and diagnostics: `alhvr/design.md` (§D0-results, §4). Code: gaint `/home/noob/work/el_alhvr`, branch `alhvr_el`, commit `3a94457` on top of `f2f20d3` (219 tests pass, 3 skipped). Any fix after review gets a new commit, recorded here and in `REVISION`.

## 1. Question
At 5% labels (23 labelled cells, in-domain unlabelled pool), does ALHVR, adapted to 2-D EL cells and run on today's supervised base with a schedule under which its unlabelled loss is actually applied, beat the step-matched supervised baseline?

Secondary questions (each with the contrast that answers it, §5):
- Does ALHVR's routing premise (no unlabelled loss on Ω1, where both networks are confident) help on thin rare classes, or does it waste the 65–69% of crack that D0 finds in Ω1?
- Does CG-CPCL add anything over DTCT alone?
- Where does the best two-network arm stand against the project's best SSL recipe (BsM5)?

## 2. Hypotheses
- **H1 (primary):** AL5 − A5 passes P8 rule 1 (5 v 5) on at least one primary metric, with none worse.
- Prior, stated before any run (reading of D0): ALHVR routing puts loss on about 9% of pixels and 31–35% of GT crack. The BsM rule trains on 96% of pixels and covers 35–37% of crack as crack at higher precision. So a crack gain smaller than BsM5's is expected; an inactive gain is plausible (Ω2+Ω3 hold 45–55% of inactive).
- **H2 (routing):** CPSm5 − CPS5 (the Ω1 mask is the only change). ALHVR's Table 1 predicts better; D0 predicts worse or n.d. on crack.
- **H3 (CPCL):** AL5 − ALd5. The paper's Table 5 predicts better; the critic's prior and D0 (cross-network crack prototype accuracy 0.09 / 0.33) predict n.d.

## 3. Arms (cv02, one code commit, seeds 0–4, `data.split_seed=0`)
Fixed for all arms (= A5c / BsM5 options): `data.labeled_fraction=0.05 training.total_steps=20000 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice`. Adam 1e-3, 200-step warm-up, cosine to 0, gradient clip 1.0, bf16. Two-network arms: `training.unlabeled_batch_size=8`, config `configs/alhvr_el.yaml` (separate BN forward, λ 0 for 2k steps then linear to λ_max by 4k, FeatureNoise on encoder levels 1–5, β 0.8, `x_0_4` features, prototype scale 10, pull to target prototype, class-normalised sharpening T 0.1, detached DTCT target, label-safe single view for unlabelled images, no CutMix).

| Arm | What | Differs from | λ_max | Runs |
|---|---|---|---|---|
| A5 | supervised, `configs/supervised.yaml`, new commit | – (loss-off control: two-network arms' network A equals A5 while λ = 0; check C1) | – | 5 |
| AL5 | ALHVR-EL: CG-CPCL on Ω2, DTCT on Ω3, nothing on Ω1 | A5: unlabelled loss on | 0.1 | 5 |
| ALd5 | AL5 with `alhvr.cpcl=false` | AL5: CPCL off (one change) | 0.1 (inherited) | 5 |
| ALdh5 [v2] | AL5 with `alhvr.cpcl=false`, λ_max 0.3 (D0c's own matched value for DTCT-only) | ALd5: λ_max (one change) | 0.3 | 5 |
| CPS5 | same two-network pipeline, `alhvr.loss=cps`: CE from each network's perturbed output to the partner's clean argmax, every pixel | A5: unlabelled loss on | 1.0 | 5 |
| CPSm5 | `alhvr.loss=cps_routed`: CPS5 with Ω1 pixels zeroed (sum over Ω2∪Ω3, divided by all pixels) | CPS5: Ω1 mask (one change) | 1.0 (inherited) | 5 |
| BsM5 | P13 BsM recipe (reference only) | recipe comparison, not one change: EMA teacher, CutMix, hard PL ≥ 0.95 | 1.0 | [v2] re-run on the new commit with the D7 pool, 5 seeds (D7 = yes) |

**λ_max (rule D0-4, fixed before D0 ran):** λ_max = BsM ratio / arm ratio of the median gradient norm ‖∇L_u‖/‖∇L_sup‖ at λ 1, network A, surrogate pairs, mean over 2 pairs, rounded on a log scale to {0.01, 0.03, 0.1, 0.3, 1, 3, 10}. D0c measured it with the worktree's own loss code and the exact arm configs (`alhvr/d0/d0c_grad.json`): AL 0.110, 0.132 → 0.121 → **0.1**; ALd 0.30 → 0.3; CPS 0.451, 0.731 → 0.591 → **1.0**; CPSm 0.914 → 1.0. (D0b, with my reimplementation and the pull term off, gave CPS 0.553, a near-tie with the log midpoint 0.548; D0c, on the actual code, is clear of it.) One-change ablations inherit their parent's λ (ALd5 from AL5, CPSm5 from CPS5), so each ablation contrast changes one thing; [v2] ALd's own matched value 0.3 is now run as the extra arm ALdh5, so DTCT-only is tested both at the parent's λ and at a matched gradient share. The paper's λ 0.1 coincides with AL5's.
- LR-weighted mean λ under the cosine schedule: 0.715 · λ_max = 0.0715 for AL5 (reference at constant LR 0.039; old port 0.0156). 62% of the LR mass falls after step 4,000, where λ = λ_max.

**Deviations, all disclosed:** from the paper: §4 of design.md (base, BN, perturbation, feature layer, CPCL scale and pull, sharpening, detach, λ schedule). From CPS (Chen 2021): the supervised net is the perturbed pass, not the clean one, and both nets share the ImageNet encoder init; this keeps the forward identical to AL5's. Two-network arms train 2× parameters and compute; only network A is scored, so no ensemble enters a rule.

## 4. Data (per `data/decision.md`)
- BenchmarkEL `20211104`, 478 / 54 / 50, `masks_escdd` for training and scoring. Labelled: `splits/seed0/labeled_5pct.txt` (23). Unlabelled: `splits/seed0/unlabeled_5pct.txt` (455), in-domain. No external pool, no E1 cell, no `_rf` cell, no synthetic image.
- **Pool [v2]: D7 = yes.** Every two-network arm and the BsM5 re-run use `data.unlabeled_exclude=reports/al1/d7_twins.txt` (cv02 `/tmp/noob_el/el_alhvr/reports/al1/`, md5 `991875f2…`): CFVS_00003_r5_c5, CFVS_00037_r8_c4, CFVS_00032_r8_c4, CFVS_00020_r4_c4, CFVS_00022_r4_c4, CFVS_00031_r4_c4, ARTS_00081_r5_c1, all checked to be in seed-0 `unlabeled_5pct.txt`. Pool 455 → 448 cells. A5 is unaffected (no pool). This is a methodology change relative to the P-series pools and is disclosed as such.

## 5. Decision rules and contrasts (P8 rule 1, handbook 07 §5; 5 v 5; final step; network A for two-network arms)
Primaries: test crack IoU, inactive IoU, crack relF1@2; argmax; revised masks; 50 test cells.

| # | Contrast | Role | Supports |
|---|---|---|---|
| P | **AL5 − A5** | **primary claim** (rules R2 = R3, since A5 is the loss-off control) | "ALHVR-EL beats supervised" |
| S1 | CPSm5 − CPS5 | secondary, one change | the routing premise (Ω1 masked) |
| S2 | AL5 − ALd5 | secondary, one change | CG-CPCL |
| S3 | ALd5 − A5, ALdh5 − A5 [v2], CPS5 − A5, CPSm5 − A5 | secondary | each two-network loss vs supervised |
| S6 [v2] | ALdh5 − ALd5 | secondary, one change (λ) | DTCT strength |
| S4 | AL5 − CPSm5 | secondary, method contrast (same routing; loss form and λ differ) | ALHVR's modules vs plain cross-PL on the same regions |
| S5 | best two-network arm − BsM5 | descriptive recipe comparison, never a one-change claim | standing against the project best |

Contrast count [v2]: 1 primary + 9 secondary + 1 descriptive; no multiplicity correction; only P carries the claim.
- Width check: crack relP@2 drop > 0.05 vs A5 flagged (vs the parent arm for S1, S2).
- Gap closed (X − A5)/(L3@100% − A5), descriptive; L3@100% from cv02 P6/P16 (cross-commit, descriptive).
- Robustness, reported, never changing a verdict: paired image bootstrap (2,000), leave-top-3-out, source split, and every test table **with and without** (a) `CSIR_00070_r8_c4` and (b) the 7 twin test cells of data/decision.md D6 (both lists labelled post hoc relative to the P-series).
- Secondary metrics: AP and bin-0 share, val (never for selection), E1 per-cell metrics; network B and the A+B ensemble, descriptive.
- If S5's best arm is chosen after seeing results, it is labelled as such.

## 6. Pre-launch checks (cv02, same commit and deployment as the runs; smoke ≤ 300 steps unless stated)
- **C1 λ = 0 identity.** AL5 seed 0 and A5 seed 0 on the new commit, `--exit_after_step 300 training.checkpoint_every=300` (λ = 0 throughout): network A's state dict must equal the supervised one tensor for tensor (`torch.equal`), and the logged `sup_a` at steps 50–300 must equal the supervised `loss_sup`. Also compared with the old cv02 A5c seed 0 log (`p12_A_5pct_s0.stdout`); a mismatch there is reported (environment drift) and A5 is re-run anyway. CPU unit test already passes (`tests/test_alhvr_el.py`).
- **C2 MT pipeline check [v2: BsM5 is re-run regardless].** BsM seed 0 on the new commit to step 2,050 (first logged step with λ > 0). Run with the P-series pool so it can be compared with old `p13_BsM_5pct_s0.stdout`: every logged line must equal except timing. It shows the MT code path at 3a94457 is the P13 one; a mismatch is reported and investigated before the launch.
- **C3 memory and speed.** AL5 and CPS5 seed 0 with `alhvr.warmup_steps=50 alhvr.ramp_steps=50`, 300 steps, batch 8+8: peak memory (nvidia-smi), steps/s, and that every logged term is finite. Packing per GPU is set from this. (gaint functional smoke, batch 8+4, 150 steps: rc 3 = intended exit, all terms finite; batch 8+8 OOMs on gaint's 26 GB free.)
- Results of C1–C3 go to `alhvr/log.md` with the log diffs; agent 2 checks them before the final launch.

## 7. Watches during the runs (logged; never test numbers)
- Every 50 steps: λ, sup_a/sup_b, each unlabelled term, `share_a = λ·L_u/L_sup`, γ, region pixel fractions, network disagreement rate; every 500 steps `gshare_a = ‖∇λL_u‖/‖∇L_sup‖`; every 100 steps `regions.csv` with GT-crack and GT-inactive shares per region and target accuracy (hidden masks of unlabelled cells, logging only).
- **Activity rule.** At step 6,000 (about 1 h), mean `share_a` over steps 4,000–6,000 per SSL arm is compared with BsM5's logged share there (0.13–0.20 on s0/s1). If an arm is < 0.03 ("not active") or > 3 ("dominant"), agent 2 may stop that arm; λ_max is then multiplied by 0.15/share, rounded on the grid, and the arm restarts under a written amendment (training logs only seen).
- **Routing/collapse flags.** If Ω2+Ω3 < 1% of pixels on average over steps 4,000–20,000, the AL/ALd/CPSm arm is reported "routing inactive" and stays in the analysis. If the A/B argmax disagreement rate < 0.5% over the same window, the arm is flagged "co-training collapsed".
- Rescoring uses `latest.pth` (step 20,000) only; `metrics.json` best-val entries and `best.pth` are never read for any reported number.

## 8. Compute
- cv02 (8 × A6000 48 GB). gaint cannot hold it: one GPU, 26 GB free, batch 8+8 does not fit, and ~100 GPU-h would block the SKCDF track for days.
- Runs [v2]: 5 supervised (~1.5 h each at 1/GPU) + 25 two-network (estimate 4–6 h each at 1/GPU, to be fixed by C3) + 5 BsM5 (~2.2 h each): 35 runs, about 120–160 GPU-h. GPUs split with agent 3 by ledger rows at the go (agent 3 proposes 4–6 for SK1; AL1 takes 0–3 and any GPU freed later, under the < 1,000 MiB start rule and the > 4 GB other-user rule).
- Deployment: `git archive` of the reviewed commit to `/tmp/noob_el/el_alhvr`, `data -> /tmp/noob_el/el_p7/data` (byte-identical splits checked by md5 against gaint), cv02 venv `/tmp/noob_el/el-fault-detection/.venv`, `REVISION` written. Queue: `gpu_queue` pattern (GPU < 1,000 MiB used before a run starts; never a GPU where another user holds > 4 GB), tmux `-t "=al1"`, one window per run, rescore after training. GPUs booked in `gpu_ledger.md`, coordinated with agent 3 (SKCDF, also cv02).
- Backup: every run dir and checkpoint is relayed to gaint `cv02_noob_el/el_alhvr` with MD5 checks after the runs (memory note on cv02 backup).

## 9. Analysis outputs
`results/al1/README.md` (to be written by agent 1; recomputed independently by agent 2 from the raw per-run JSONs before anything is reported): per-seed table, rule table, robustness tables with/without the two cell lists, watches, figures.
