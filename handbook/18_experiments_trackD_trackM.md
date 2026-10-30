# 18. Track D, Track M and the two analysis teams (24 to 27 Oct 2026)

## What this covers
This file covers the agent-team work of 24 to 27 Oct, after AL1 (doc 10):
- **Why-SOTA team (24 Oct, no GPU):** why standard SSL fails on EL crack, and 8 ranked directions;
- **Track D (24 Oct, cv02):** diagnosis. A frozen-encoder probe, an inactive-edge re-score, and a 27-run labelled-set experiment;
- **Track M (24 to 25 Oct, cv02):** the best-scoring model. A baseline audit (M0), a one-change ladder (R1 to R5) and the FINAL model;
- **Unlabelled-data team (27 Oct, no GPU):** why ~12k unlabelled cells did not help, whether the test set or metric should change, and a ranked plan.

Each experiment follows the layout of docs 08 to 10 (Question, Why, Setup, Rules, Results, Verdicts, Robustness, Reading, Next), compressed as in doc 10's SK1 and AL1 sections. Feature learning from the pool and the move to 100% labels (28 to 30 Oct) are in `19_feature_learning_and_100pct_plan.md`. Cross-experiment claims are in `11_results_synthesis_and_claims.md` rows 18 to 24.

Added 30 Oct 2026 (handbook refresh). No earlier doc text is changed except for dated "[Qualified 30 Oct: ...]" notes.

**Tags.** E = measured (file), R = literature (Research MCP id), S = judgement. "Clean" = the 50 test cells without `CSIR_00070_r8_c4`. All numbers: cv02, split seed 0, revised masks (`masks_escdd`), final-step weights (step 20,000), unless stated.

**Status at writing (30 Oct 2026, ~12:00 IST)**

| Item | Status | Where the results are |
|---|---|---|
| Why-SOTA team | done 24 Oct (CPU recomputes only) | `team_2026-10-24_why/SYNTHESIS.md`, `critique.md` |
| Track D probe | done, critic CONFIRMED | `team_2026-10-24_go/trackD/verify_probe.md`, `probe_results.md`, `results/trackD_probe/` |
| Track D edge re-score | done, CONFIRMED | `trackD/verify_edge.md`, `edge_results.md`, `results/trackD_edge/` |
| Track D labelled set | done (27 runs), CONFIRMED | `trackD/verify_labelset.md`, `labelset_results.md`, `results/trackD_labelset/` |
| Track M M0, R1 to R5 | done, each VERIFIED by MC | `team_2026-10-24_go/trackM/baseline.md`, `results_r*.md`, `verify_r*.md` |
| Track M FINAL | done 25 Oct, VERIFIED by MC | `trackM/results_final.md`, `verify_final.md` |
| Unlabelled-data team | done 27 Oct (no GPU) | `team_2026-10-27_unlabelled/SYNTHESIS.md` |

## Sources
- `SESSION_RECORD_2026-10-21_to_27.md` (master for 21 to 27 Oct; §5 to §9).
- `team_2026-10-24_go/README.md` (brief, the user's goal), `gpu_ledger.md`.
- Track D: `trackD/protocol_{probe,edge,labelset}.md`, `review_*_v1.md`, `*_results.md`, `verify_{probe,edge,labelset}.md`, `critic_defaults.md`.
- Track M: `trackM/design.md`, `baseline.md`, `protocol_r1.md` to `protocol_r5.md`, `protocol_final.md`, `results_r1.md` to `results_r5.md`, `results_final.md`, `review_*.md`, `verify_*.md`.
- `team_2026-10-24_why/SYNTHESIS.md`; `team_2026-10-27_unlabelled/SYNTHESIS.md`, `eval.md`, `lit.md`, `ideas.md`, `critique.md`, `judge_notes.md`.
- Later corrections: `team_2026-10-29_features/review_ddep5_cp5_v0.md` P2 (ARTS crack cell), `coach_100.md` §0 (encoder erasure), `spec_b3_scuff.md` §1 (scuff labels).
- Copies of all these: `sources/teams/` and `sources/session_records/` (`sync_sources.sh`).

---

## Terms used in this file (short; full list in `04_glossary_and_naming.md`)
- **SUP100.** The 100%-label supervised baseline: L3 recipe (U-Net++, ImageNet ResNet-34, CE + Dice on crack and inactive, label-safe augmentation, 512 px, 20k steps). Its 5 seeds are P6 `p6_L3_100pct_s0..2` + P16 `p16_A_100pct_s3..4`.
- **FINAL.** Track M's best model: the 5-seed mean-softmax ensemble of SUP100 with +0.75 on the crack logit (§M7).
- **LA (logit adjustment).** z_c − τ·log π_c, τ = 1, prior from the labelled cells. The free-bias yardstick of S-a (doc 10).
- **mIoU_rob.** Mean IoU over the 13 classes with GT in ≥ 3 of the 50 test cells: 0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21 (`trackM/baseline.md` §1).
- **relR@2 / relP@2.** Crack recall / precision with a 2 px tolerance. **Component recall:** GT crack components ≥ 20 px counted found if ≥ 50% of their px lie within 2 px of a prediction.
- **Val inclusion rule.** Track M: a rung enters the final recipe only if it passes rule 1 on val (`trackM/design.md` §1). Test is scored per rung but never used to choose.
- **Test opening.** One scoring of test for a locked contrast. Counted and disclosed.
- **E1 / ext.** The 106 unseen-module cells (doc 10). Never used for selection.
- **Scuff + half-cut.** E1 cells that are half-cut multi cells with a scuff streak (E-SCDD class 25). 29 such cells by the 29 Oct context list (`scripts/e1_context.tsv`, doc 19).

---

## W. Why-SOTA team: why standard SSL does not work on EL crack (24 Oct, no GPU)

**Question.** After SK1 and AL1 (doc 10), why do 2025 SOTA SSL methods fail on EL crack, and what next?

**Setup.** Data-side analyst R1, method-side analyst R2, critic C. Two challenge rounds. No GPU; every number is a CPU recompute of existing outputs (`team_2026-10-24_why/SYNTHESIS.md`).

**Established (E, SYNTHESIS §1)**
- SSL is not doing nothing on crack. BsM5 beats supervised on crack IoU at 5% (+0.029, passes). With the free bias on both sides it still passes: +0.037 (thr 0.013); +0.035 without twins and the noisy cell.
- The gain is small: a third of what +24 random labelled cells buy (+0.092).
- It is source-bound. Without twins: CFVS +0.047 (thr 0.012), BMRK +0.002, ARTS −0.030. BMRK and ARTS hold 30% of test crack.
- At 5%, BMRK has 2 labelled crack cells and ARTS was stated to have 0. [Correction 29 Oct, already in the source (coach, E, server `masks_escdd`): ARTS has 1 small labelled crack cell, `ARTS_00051_r6_c2` (47 px); 9 crack cells in total (`team_2026-10-29_features/review_ddep5_cp5_v0.md` P2). Commit 882f929.] [Qualified 30 Oct: those 47 px are E-SCDD scuff (class 25) that P6's remap labelled crack, so the 5% set holds no real ARTS crack (`team_2026-10-29_features/spec_b3_scuff.md` §1; doc 17 §5.11).]
- Crack belief is bimodal: 57% of GT crack scores < 0.001 and 35% ≥ 0.95. A rule applied to the final model can act on 8% (A5) to 19% (BsM5) of GT crack (`results/al1/hist_revised.npz`).
- About 38% of pool crack is a true miss (> 2 px from any prediction). No training rule moved that by more than 0.046 (`skcdf/second_opinion_a2.md`).
- Inactive is the counter-case: supervised under-extends regions (precision 0.77, recall 0.28), self-training extends them (recall 0.43), so SSL gives +0.10 to +0.13 and survives LA.
- ABSH (SK1) corrects a prior collapse we do not have. ALHVR gives no loss to the region holding 65 to 70% of GT crack.

**Likely (R)**
- Self-training spreads labels through neighbourhoods the teacher already gets right (expansion assumption, arXiv 2010.03622).
- Published gains come mostly from weak or from-scratch baselines, or blob-like classes.
- We fail Oliver et al.'s realistic-SSL conditions (arXiv 1804.09170): labelled set not i.i.d. with the pool; val too small to tune (6 inactive cells).

**Not causes (E):** pool size; the noisy cell and the twins (they distort measurement, not mechanism); strict-IoU compression.

**Directions (SYNTHESIS §2), as ranked on 24 Oct:**
1. Stop new SSL methods for crack; BsM5 (+LA) is the SSL result.
2. The user's 40-component audit and 4 label-convention answers (pending).
3. Labelled-set composition test (run as Track D).
4. Frozen-encoder probe per source (run as Track D).
5. SSL on a better-covered labelled set (gate not met; not run).
6. Inactive-edge convention re-score (run as Track D).
7. MIM pretraining of the U-Net++ encoder (gated out on 24 Oct; run 29 Oct as MIM5, doc 19).
8. Rare-class copy-paste into BsM (not run at the time; CP5 and CP100 in doc 19).

**Next.** The user: "take the critics decisions, and go", with the goal "highest scores, a model which captures almost all of the cracks, inactive and other important defects balancing the miou for other classes as well" (`team_2026-10-24_go/README.md`). That started Track D and Track M (doc 12 D41).

---

## D1. Track D: frozen-encoder probe per source (24 Oct)

**Question.** Does any frozen pretrained encoder rank BMRK crack better than the 5% fine-tuned model? A gate for the encoder and MIM routes.

**Setup.** A linear probe on frozen stride-4/8 features, trained on the 23 labelled 5% cells. Encoders: ImageNet ResNet-34, ImageNet ResNet-50, ConvNeXt-T, DINOv2-S, A5c's own fine-tuned encoder, random. About 1 GPU-h of inference.

**Locked rule.** Pass if BMRK test crack AP beats A5c+LA by 0.05: bar 0.215 (A5c+LA 0.165). Pool bar 0.285 (A5c+LA 0.235).

**Results (E, `trackD/verify_probe.md`; two probe seeds each)**

| Encoder | BMRK test crack AP | Pool BMRK AP | Verdict |
|---|---|---|---|
| A5c (5 seeds) | 0.150 | | reference |
| A5c + LA | 0.165 | 0.235 | reference |
| ImageNet ResNet-50 | 0.268 / 0.268 | 0.322 / 0.322 | **pass** (test and pool) |
| ConvNeXt-T | 0.278 / 0.271 | 0.282 / 0.278 | pass on test only ("fragile") |
| ImageNet ResNet-34 | 0.185 / 0.187 | | fail |
| DINOv2-S | 0.122 / 0.133 | | fail |
| A5c's own encoder | 0.171 / 0.171 | | fail |
| random | 0.045 / 0.047 | | |

**Robustness and caveat (E).** The separation is at low precision. At A5c+LA's precision (P* 0.58) the probes recall 0.020 / 0.023 (ResNet-50) and 0.002 (ConvNeXt-T) of BMRK crack, against A5c's 0.21. A ranking signal, not better masks. On the 40 always-missed components the best relaxed recall is 0.097; 0 of 40 at ≥ 0.5.

**Reading (critic C).** Bigger ImageNet encoders carry BMRK crack information that our fine-tuned model throws away. By the locked rule MIM was gated out. The 27 Oct team judged that too early as a test of the user's question (§U). [Qualified 30 Oct: the probe compares frozen features with A5c's fine-tuned ResNet-34 encoder, whose layer3/4 the house optimizer erases (measured on A5c-f1, the gaint re-run of A5c; `team_2026-10-29_features/coach_100.md` §0; doc 19 §4). A fine-tune that keeps the deep features (PF) was first tested in protocol_100.]

**Next.** Track M tested fine-tuned ResNet-50 / ConvNeXt (R3, §M4) with BMRK crack AP and recall as named secondaries.

---

## D2. Track D: inactive-edge re-score (24 Oct, post hoc, inference only)

**Question.** If crack within 2 px of inactive is banded (ignored), do arms move, and does any SSL gap flip sign?

**Results (E, `trackD/verify_edge.md`)**
- Band share: 10,650 / 92,074 = 11.6% of test crack. Per source: BMRK 22.6%, CSIR 7.9%, CFVS 7.6%, ARTS 2.5%.
- In-band recall: A5c 0.178, BsM5 0.241.
- Banding raises 5 to 10% arms by +0.018 to +0.027 crack IoU; A50 by +0.012 and A100 by +0.007.
- Kill not triggered: no sign flip in any contrast, metric or cell set.
- About a fifth of SSL's crack-IoU gain sits in the band. BsM5 − A5c: +0.029 → +0.023 (all 50). Without twins: +0.019 → +0.014 (thr 0.018), BETTER → n.d. on crack IoU.
- (BsM5+LA) − (A5c+LA) passes on all three crack metrics in every cell set, banded or not.

**Wording (critic).** These are per crack metric. The rule-1 verdicts also include inactive IoU, which banding leaves untouched, so every BsM5/BsD5 − A5c rule-1 verdict stays BETTER through inactive.

**Reading.** The inactive-edge convention costs the low-label models about 0.02 crack IoU, not the full-label model. BMRK's 22.6% band share barely moves its IoU (±0.01), so the convention is not what makes BMRK hard.

---

## D3. Track D: labelled-set experiment (24 Oct, 27 runs)

**Question.** At an equal budget of +12 labelled cells on the 5% base, does it matter which cells? Is that worth more than SSL?

**Setup (`trackD/protocol_labelset.md`, `labelset_results.md`)**
- Arms: R (12 random cells), Tc (12 cells containing crack), Ts (12 crack cells from the weak sources: 6 BMRK / 4 ARTS / 2 CSIR). Cells chosen with ground truth ("oracle-selected").
- 3 draws × 3 seeds per arm = 27 runs. The 3-seed design breaks the ≥ 5-seed rule; the user accepted it by adopting the critic's decisions.
- Rule: draw-level max(0.01, 2·sqrt(var_A/3 + var_B/3)) over the 3 draw-means. Primary P1: Ts − Tc; P2: Tc − R (critic's choice).

**Results (E, all 50)**

| Arm | Crack IoU | Crack relF1@2 |
|---|---|---|
| R | 0.324 | 0.757 |
| Tc | 0.337 | 0.787 |
| Ts | 0.352 (0.365 with LA) | 0.795 |
| for comparison: BsM5 | 0.331 (0.356 with LA) | |
| for comparison: L3 10% | 0.396 | |

**Verdicts (E, `verify_labelset.md`; Δ (threshold))**

| Contrast | Crack IoU | relF1@2 | Recall | Verdict |
|---|---|---|---|---|
| P2: Tc − R | +0.0127 (0.0118) | +0.0301 (0.0106) | +0.0166 (0.0223) | **BETTER** |
| P1: Ts − Tc | +0.0151 (0.0212) | +0.0073 (0.0231) | +0.0255 (0.0275) | **n.d.** |
| Ts − R (secondary) | +0.0278 (0.0210) | +0.0374 (0.0210) | +0.0421 (0.0295) | BETTER |

**Robustness (E)**
- Tc − R is BETTER through relF1@2 in all four cell sets: +0.030 [+0.020, +0.042]. Its crack IoU pass on all 50 is marginal and n.d. at seed level.
- Ts − Tc is BETTER only without twins, on recall alone (+0.036 vs 0.033).
- Ts − R is BETTER in all four sets.
- BMRK recall: R 0.242, Tc 0.265, Ts 0.312. Ts's BMRK IoU 0.259 is above L3 10%'s 0.219.
- Crack-pixel volume: r = 0.82 over the 9 draw-means, +0.018 crack IoU per 10k added crack px. Volume explains the whole Tc − R gap; Ts keeps about +0.011 over Tc beyond it (9 points, descriptive).
- Inactive: BsM5 keeps a clear lead (0.385 vs 0.33 to 0.35).
- All-class mIoU: n.d. everywhere; point estimates −0.004 to −0.011.
- E1 (descriptive): crack-cell arms find more unseen-module crack (tolF1 0.28 to 0.29 vs 0.24) and raise false alarms (0.26 to 0.30 vs 0.20).

**Direction-5 gate: NOT opened.** "Ts − Tc BETTER, or Tc − R BETTER with BMRK recall ≥ +0.05": Ts − Tc is n.d. and BMRK recall moved +0.023. SSL on the Ts set did not run.

**Reading.** For crack, targeted labels beat both random labels and SSL at this budget (oracle-selected). +12 random cells bought +0.020 crack IoU, half the pre-stated +0.04, and R (0.324) sits below BsM5 (0.331). Whether source or crack volume matters more is unresolved.

---

## M0. Track M: baseline audit of the existing 100% checkpoints (24 Oct, no training)

**Question.** What does SUP100 score on every class and capture metric before anything is changed?

**Setup.** Re-score of the 5 SUP100 checkpoints (P-series re-scorer path, step 20,000 asserted), with definitions fixed before any number was read (`trackM/baseline.md` §0, §1). Identity: `p6_L3_100pct_s0` reproduces its P6 JSON exactly.

**Results (E, `trackM/baseline.md` §2)**

| Cells | Crack IoU | Crack relF1@2 | Inactive IoU | mIoU_rob |
|---|---|---|---|---|
| all 50 | 0.435 ± 0.078 | 0.828 ± 0.105 | 0.436 ± 0.013 | 0.547 ± 0.016 |
| without the noisy cell | 0.474 ± 0.002 | 0.881 ± 0.004 | 0.449 ± 0.014 | 0.580 ± 0.011 |
| without the 7 twins | 0.361 ± 0.087 | 0.752 ± 0.140 | 0.412 ± 0.013 | 0.539 ± 0.016 |
| without both | 0.405 ± 0.004 | 0.822 ± 0.006 | 0.428 ± 0.013 | 0.575 ± 0.011 |

- One seed fails on the noisy cell: crack IoU per seed 0.472, 0.471, 0.470, **0.297 (A100 s3)**, 0.467.
- The noisy cell also decides all-class mIoU: it costs mIoU_rob 0.033 (0.547 → 0.580). On it SUP100 predicts on average 156,897 px border and nearly all of 18,616 px of "text", a class absent from test.
- Weakest robust classes: gridline 0.278 ± 0.011 (recall 0.326); splice 0.000 (never predicted).

**Consequence for design.** Every mIoU contrast is run with and without the noisy cell.

---

## M1. R1: TTA, 5-seed ensemble, crack operating point (24 Oct, post hoc layer, inference only)

**Val decisions, written before test (E, `results_r1.md`).** D1: TTA on the ensemble off (val 0.6507 plain vs 0.6499 TTA). D2: crack bias +0.75, by the fallback (max val relF1@2), since no bias in 0 to 3 reached val relR@2 ≥ 0.90 with relP@2 ≥ 0.90.

**Verdicts (E, `verify_r1.md`)**
- **R1a, TTA − plain (rule 1, 5 v 5): PASS on crack IoU.** Without noisy +0.0104 (0.0100) BETTER, on the 0.01 floor; all 50 n.d. (TTA makes A100 s3's noisy-cell failure worse: 75,468 → 103,104 crack px). Cost 8× inference.
- **R1b, ensemble − mean single seed (paired bootstrap, 2,000): PASS.** Without noisy: crack IoU +0.0144 [+0.0118, +0.0167], relF1@2 +0.0102 [+0.0062, +0.0157]. Inactive and mIoU_rob CIs include 0. The ensemble predicts 2 crack px on the noisy cell, so its all-50 gain is mostly robustness to that cell.
- TTA on top of the ensemble adds nothing (crack −0.0001).
- **R1c, bias +0.75 (descriptive).** Clean: relR@2 +0.029, component recall +0.027, crack precision −0.041, IoU flat. All 50: 10,867 crack px on the noisy cell, crack precision −0.099 (width flag), component precision 0.944 → 0.634.

**Reading.** The final model will be an ensemble. A threshold cannot buy "almost all cracks" at relP@2 ≥ 0.90.

---

## M2. R2 and R2c: Dice on more classes (24 to 25 Oct)

**R2: soft Dice on 12 classes (dice_weight 6), 5 v 5 (E, `results_r2.md`, `verify_r2.md`): WORSE, val EXCLUDE.**
- Without noisy: crack IoU −0.0106 (0.0100) WORSE, relF1@2 −0.0130 (0.0100) WORSE; inactive and mIoU_rob n.d.
- Gridline 0.283 → 0.381 (recall 0.326 → 0.540, precision 0.680 → 0.563); val agrees (0.308 → 0.409).
- Mechanism (E): mean pre-clip grad norm 6.74 vs 1.80 for SUP100; clip rate 0.969 vs 0.253. The crack step shrinks by roughly 3×. So the attribution is "Dice-12 at the L3 clip", not Dice in general.

**R2c: soft Dice on crack, inactive and gridline (dice_weight 1.5) (E, `results_r2c.md`, `verify_r2c.md`): n.d. on all four primaries, val EXCLUDE.**
- Gridline 0.283 → 0.357 (recall 0.326 → 0.491, precision 0.680 → 0.568). mIoU_rob +0.0051 [−0.0043, +0.0172].
- Grad norm 2.09 / 2.10 vs 1.80 (×1.16); crack unharmed (−0.0024).

---

## M3. R4: +107 leakage-free E-SCDD cells (24 Oct)

**Setup.** 585 train cells (478 + 107 E-SCDD real cells cleared against `data/decision.md`; 104 of them CSIR). Steps matched, so each cell is seen about 18% less often.

**Verdict (E, `results_r4.md`, `verify_r4.md`): n.d. on all four primaries, val EXCLUDE.** Without noisy: crack +0.0010 [−0.0026, +0.0062], inactive +0.0085 [−0.0042, +0.0277].
- Post hoc leads only: ARTS crack +0.027 vs thr 0.023; BMRK inactive +0.011 (thr 0.010).
- Dead cell, newly trained from 5 cells, gives test false positives of about 1,280 px per seed on average; dead cell is absent from test GT.
- E1 crack 0.148 → 0.146. Even 104 extra CSIR cells do not help on unseen CSIR modules.

**Reading.** These labels are CSIR, where SUP100 is already strong. The data lever that would matter (ARTS/BMRK crack coverage) is not what E-SCDD offers.

---

## M4. R3: bigger encoders (24 to 25 Oct)

**Part A, pilots (val only, E, `results_r3.md`).** Qualify if val score > 0.6414.

| Pilot | Params | Val score | Qualifies |
|---|---|---|---|
| reference SUP100 (5 seeds) | 26.1M | 0.6398 (sd 0.0016) | |
| U-Net + ConvNeXt-T | 31.9M | 0.6318 | no |
| U-Net++ + EfficientNet-B4 | 20.8M | 0.6467 | yes |
| **U-Net++ + ResNet-50** | 49.0M | **0.6474** | yes, **selected** |

ResNet-50 beat EfficientNet-B4 by 0.0007, under one seed sd. The locked rule picked ResNet-50. Pilot test outputs were sealed unread.

**Part B, U-Net++ ResNet-50 seeds 1 to 5 vs SUP100 (E, `verify_r3.md`): WORSE on inactive, val EXCLUDE.**

| Set | Crack IoU | Inactive IoU | relF1@2 | mIoU_rob |
|---|---|---|---|---|
| all 50 | +0.0314 (0.0897) | **−0.0240 (0.0216) WORSE** | +0.0452 (0.1213) | −0.0120 (0.0193) |
| without noisy | −0.0041 (0.0100) | **−0.0251 (0.0227) WORSE** | −0.0030 (0.0100) | −0.0090 (0.0140) |

- Inactive bootstrap without noisy −0.0251 [−0.0721, +0.0094]: seed-consistent, not robust over cells. The loss sits in CSIR inactive (0.707 → 0.333, 3 cells) and CFVS.
- Named secondaries (descriptive): BMRK crack AP 0.462 → 0.480 (+0.018, thr 0.014); BMRK relR@2 +0.025 (0.020); CFVS crack AP −0.017 (0.015).
- E1: crack 0.148 → 0.167, crack recall 0.178 → 0.214 (+0.036), the largest relative E1 change of any rung.
- Compute: 460.4 vs 148.0 GFLOPs per forward (about 3.1×); about 2 GPU-h per run vs about 1.1.

**Reading (MD, MC).** A bigger encoder alone does not beat ResNet-34 at 100% under the L3 recipe. The BMRK and E1 gains agree with the D1 probe; they are offset by inactive losses. [Qualified 30 Oct: this holds only under the house optimizer (Adam lr 1e-3, coupled weight decay 1e-4, 20k steps), which ended encoder layer3/4 at cosine about 0 to their init in every ResNet-34 U-Net++ run measured, with ImageNet and MIM inits (`team_2026-10-29_features/coach_100.md` §0; doc 19 §4). The optimizer was never varied in R1 to R5. So R3 likely tested ResNet-50 / EfficientNet-B4 with their deep pretrained features re-learned from labels, not kept (S; not measured on the R3 encoders). For ConvNeXt (LayerNorm, not BatchNorm) the mechanism is not established. `coach_strategy.md` §2 A2 proposes ResNet-50 and ConvNeXt-T under the encoder-preserving fine-tune if SUP100-PF shows a gain.]

---

## M5. R5: 2× internal resolution (24 to 25 Oct)

**Setup.** Input 1024 bilinear, logits pooled to 512. Hypothesis: thin cracks are lost to the encoder stride.

**Verdict (E, `verify_r5.md`): n.d. on all four primaries, val EXCLUDE.** Without noisy: crack −0.0046 (0.0100), mIoU_rob −0.0113 (0.014), bootstrap [−0.022, +0.000].
- Confident misses (GT crack with p < 0.001), the target of the rung: test 0.189 → 0.208 (worse); ext 0.704 → 0.687.
- E1 crack recall 0.178 → 0.204 (descriptive), the same pattern as ResNet-50.
- Compute: 591.9 vs 148.0 GFLOPs (4.0×), about 4.2 GPU-h per run.

**Reading (MC).** At 4× compute the hypothesis is not supported at 100% labels.

---

## M7. FINAL: the best-scoring model (25 Oct, Track M test opening no. 7)

**Protocol (`trackM/protocol_final.md`, APPROVED with F1 to F4, locked before any R3 Part B, R5 or R2c number).** The recipe is chosen by the per-rung val inclusion rule. No rung passed (R2, R2c, R3 Part B, R4, R5 all EXCLUDE), so the recipe is SUP100. With D1/D2 repeating R1's choices, FINAL equals the R1 model (per-cell confusion matrices identical, max |diff| 0), so contrast 2 is dropped (F2). [Discrepancy: `SESSION_RECORD_2026-10-21_to_27.md` §1 says "Six training changes all failed"; `verify_final.md` lists five rungs (R2, R2c, R3 Part B, R4, R5). The ConvNeXt-T and EfficientNet-B4 R3 pilots were val-only and not test-scored. The verify file wins.]

**The model.** U-Net++ / ImageNet ResNet-34, 100% labels, CE + Dice on crack and inactive, label-safe augmentation, 512 px, 20k steps; 5 seeds, mean softmax; no TTA; crack logit +0.75 (max val relF1@2; val precision drop 0.033 < 0.05). 5 trained models, 5 forward passes per cell.

**Headline (E, `trackM/results_final.md`, `verify_final.md`; clean test unless stated)**

| | SUP100 single (mean of 5) | **FINAL, bias +0.75** | FINAL, bias 0 |
|---|---|---|---|
| crack IoU, clean | 0.474 | **0.492** | 0.488 |
| crack IoU, all 50 | 0.435 | 0.453 | 0.485 |
| crack P / R | 0.644 / 0.642 | 0.621 / 0.703 | 0.662 / 0.650 |
| crack relP@2 / relR@2 | 0.938 / 0.830 | 0.930 / 0.866 | 0.953 / 0.837 |
| crack relF1@2 | 0.881 | 0.897 | 0.891 |
| crack components found (≥ 20 px) | 0.798 | 0.834 (precision 0.933) | 0.807 (0.944) |
| inactive IoU | 0.449 | 0.456 | 0.454 |
| inactive components found (≥ 100 px) | 0.773 | 0.800 | 0.800 |
| mIoU_rob (13 classes) | 0.580 | 0.583 | 0.583 |
| E1 crack IoU / recall | 0.148 / 0.178 | 0.172 / 0.215 | 0.148 / 0.170 |

**Contrast 1: FINAL − SUP100 mean single seed (paired image bootstrap, 2,000; MC's CIs)**

| Operating point | Set | Crack IoU | relF1@2 | Inactive IoU | mIoU_rob |
|---|---|---|---|---|---|
| **+0.75 (headline)** | clean | **+0.018 [+0.013, +0.025]** | **+0.016 [+0.010, +0.025]** | +0.007 [−0.003, +0.020] | +0.003 [−0.001, +0.010] |
| +0.75 | all 50 | +0.018 [−0.029, +0.024] | +0.025 [−0.016, +0.031] | n.d. | n.d. |
| 0 | clean | +0.014 [+0.012, +0.017] | +0.010 [+0.006, +0.016] | n.d. | n.d. |
| 0 | all 50 | +0.050 [+0.013, +0.079] | +0.058 [+0.007, +0.111] | n.d. | n.d. |

**Verdict: PASS** on crack IoU and relF1@2 at both operating points. Inactive and mIoU_rob n.d. No primary worse. MD's all-50 +0.75 crack CI is [−0.024, +0.024], MC's [−0.029, +0.024]: different resampling draws, same verdict.

**Robustness and fragility (E)**
- On the noisy cell, bias +0.75 calls 10,867 px crack (bias 0 calls 2), and all-50 crack precision drops to 0.563 (0.662 at bias 0). **Bias 0 is the robust operating point;** +0.75 is for clean images where recall matters most.
- "Almost all cracks" (relR@2 ≥ 0.90 at relP@2 ≥ 0.90) is **not reached**: 0.866 / 0.930.
- Per source, crack IoU single → FINAL: ARTS 0.456 → 0.503; BMRK 0.379 → 0.411 (relR@2 0.812); CFVS 0.522 → 0.535; CSIR clean 0.475 → 0.485.
- Per class (FINAL +0.75, all 50 / clean): background 0.906 / 0.927; padding 0.994; frame_edge 0.809; sp_mono 0.743; sp_multi 0.733 / 0.809; ribbons 0.634 / 0.652. Weakest robust classes: gridline 0.288 (recall 0.329) and splice 0.000 (never predicted).
- p(crack) on clean GT crack px: < 0.001 for 0.095 (single model 0.184), ≥ 0.95 for 0.488. What is still missed is mostly BMRK and the non-twin CFVS cells.
- Multiplicity: 16 tests, no correction. Track M test openings: R1 no. 1, R2 no. 2, R4 no. 3, R2c no. 4, R3 Part B no. 5, R5 no. 6, FINAL no. 7. M0 re-scored existing checkpoints, tuned nothing on test and is not counted (`results_r1.md` "Multiplicity", `results_final.md`).

**Reading (MC).** The best model found is the ensemble of the existing 100% recipe. Every single-model training change tried at 100% failed to beat L3. ResNet-50 and 2× resolution both lifted unseen-module crack recall while not helping in-split test: a lead for a separate locked study, not a claim. [Qualified 30 Oct: "every single-model change failed" holds under the never-varied house optimizer (§M4 note; doc 19 §4).]

**Next.** protocol_100 (doc 19 §7) compares new 100% arms with a fresh same-machine SUP100 on gaint. FINAL 0.492 stays descriptive there.

---

## U. Unlabelled-data team (27 Oct, no GPU)

**Question (the user).** About 480 labelled cells give a result and about 12k unlabelled cells exist. Why didn't using them help?

**Setup.** `lit` (literature, Research MCP), `evalx` (measurement), `ideas` (methods), `judge` (synthesis). CPU only (`team_2026-10-27_unlabelled/SYNTHESIS.md`).

**The answer (SYNTHESIS §1)**
- What was tested: label propagation only (Mean Teacher, BsM, CPS, ALHVR, SKCDF, decoupled decoder), with the in-domain pool at 5 to 50% and the 11,938-cell CSIR/ARTS pool at 100%.
- What was not tested: the user's actual intuition, feature learning from the unlabelled cells (MIM or contrastive) then fine-tuning; and unlabelled data that looks like the cells the model fails on.
- It worked with few labels (5%: crack +0.029, inactive +0.107; inactive to 20%), not with many.

**Measurement (E, `eval.md`)**
- On clean cells, a crack gain of +0.02 or more is excluded at 20, 50 and 100%, and +0.01 at 100% (Cs recipe). Sx100 measured −0.002 [−0.007, +0.003]. The old "+0.028" at 100% was one supervised seed failing on the noisy cell.
- BsM was never run at 50 to 100%; at 20% its +0.013 [−0.002, +0.033] is not excluded.
- 80%-power MDE, clean: crack 0.010 to 0.012 at 100%; inactive 0.032 at 100%, 0.084 at 5%.
- Where FINAL's crack IoU loss goes: 70% within 2 px of GT, 18% missed cracks, 11% false alarms. A perfect detector 1 px off scores 0.48 to 0.60. One cell labelled twice agrees with itself at 0.53 (n = 1).

**Literature (R, `lit.md`)**
- Same-encoder SSL gains +6 to +11 mIoU at 92 to 316 labels, only +0.3 to +1.6 at full labels with a non-matching pool (doi:10.1109/tpami.2025.3528453).
- Thin-structure MIM gains are measured against scratch, not ImageNet init. In-domain MAE 43.0 vs ImageNet ResNet-18 59.1 IoU on thin wires (arXiv 2605.12430).
- Torpey (arXiv 2402.17611), the only EL test: in-domain SimCLR 0.517 vs ImageNet-supervised 0.508, behind ImageNet-SimCLR 0.534 and COCO 0.544.
- No EL or crack paper shows an SSL gain on pixel crack over a tuned ImageNet baseline. SAM-family models fail on thin, low-contrast structures.

**The unseen-module failure (E, judge, evalx, ideas)**

| E1 crack cells | Cells | Share of crack px | FINAL recall |
|---|---|---|---|
| half-cut multi + scuff streak | 20 | 75% | 0.126 |
| half-cut, no scuff | | | 0.552 |
| scuff, not half-cut | 2 | | 0.51 |

- The model paints the streak as crack (about 8.7k px per run) and misses the cracks branching off it, a median 12 px from the streak.
- Training: 0 half-cut cells, 12 cells with any scuff (3,246 px), 1 cell with ≥ 500 scuff px. The source says "scuff is always scored as ignore" and "every run so far treated scuff as ignore". [Qualified 30 Oct: that is true for E1 scoring only. In our training and test masks (`masks_escdd`), P6 remapped scuff px to their old labels: of the 3,246 train scuff px, 1,207 are background, 1,390 material and **649 crack in 6 cells**; the 236 test scuff px in 2 cells are crack (E, `team_2026-10-29_features/spec_b3_scuff.md` §1; doc 17 §5.11). So training has taught "scuff streak = crack" on 649 px.]
- None of the 32 E1 crack cells comes from a pool module; the pool's 1,152 half-cells carry only small thin cracks; no pool SSL arm moved half-cut recall by more than +0.023.
- Inside our own test, unseen-module cells lose almost no crack (0.486 vs 0.499) but lose inactive (recall 0.43 vs 0.92).

**Test set and metric (SYNTHESIS §2)**
- Keep the 50 cells. Add the clean set as co-primary, defined by an image-only noise rule (robust noise sigma > 10) fixed before any new run.
- Do not use E-SCDD's official test: 48 of its 82 cells are in our train.
- Keep E1 sealed, reported as two readouts: scuff + half-cut, and the rest.
- For future protocols only: crack component recall at component precision ≥ 0.90, and relR@2 at relP@2 ≥ 0.90, beside strict IoU. Past verdicts stay under their locked metrics.
- Module-grouped 5-fold CV over 693 cells (74 with inactive) only if inactive at 50%+ becomes the question (about 100 GPU-h per SSL contrast).

**Ranked plan (SYNTHESIS §3)**

| # | Item | Cheapest decisive test | Kill |
|---|---|---|---|
| 1 | Use the pool to find cells to label: scuff + crack half-cells via a model-based finder (AUROC 0.80, post hoc); BMRK via ELPV after dedupe. Scuff class is a user decision | finder on 1,008 pool half-cells; human checks the top 100 | < 15 real cells in the top 100 |
| 2 | Stop pseudo-label SSL at 20%+ labels | none | reopen only with a matching pool or a new mechanism |
| 3 | One test of the user's intuition: continued SparK-style MIM of ResNet-34 from ImageNet, fine-tune at 5% | MIM5 vs A5c, 5 v 5 | n.d. on all three closes it |
| 4 | Inference-only checks: R34 + R50 ensemble, an SSL member for inactive, BN re-estimation, frame and scale | each scored once | no gain ≥ +0.05 on its target |
| 5 | Synthetic branch cracks along scuff streaks, only if item 1 finds too few cells | one 5-seed rung | scuff-cell recall Δ < +0.05 |

[Qualified 30 Oct: item 3 was run at 5% on 29 to 30 Oct and was n.d. (doc 19 §2). On 30 Oct the 5% choice was judged a mistake: the user's question was about 100% labels, and the 5% null holds only for methods that do not consume labels, under an optimizer that erased the MIM features (doc 19 §4, §5). Item 3's kill rule ("n.d. closes it") is therefore not taken as closing MIM at 100%.]

**Judge on the lead's position.** "Label propagation is not the user's intuition": holds. "Features are not the bottleneck": holds for strict IoU only. "Labels beat SSL": holds only with "oracle-selected" attached.

**Thesis contributions so far (SESSION_RECORD_2026-10-21_to_27.md §9)**
1. A tight null for pseudo-label SSL at 20 to 100% labels on EL crack; the old +0.028 traced to one seed on one corrupted cell.
2. SSL's benefit depends on label scarcity and class.
3. Two 2025 SOTA methods adapted to EL, with mechanisms for their failure.
4. The free logit-bias yardstick for SSL crack claims; BsM5 still passes it (+0.037).
5. Test leakage found and handled: 7 twin cells hold 39.5% of test crack.
6. Crack IoU has a labelling ceiling, so capture metrics should judge "catch almost all cracks".
7. "Unseen modules" decomposed into a missing defect context (scuff + half-cut).
8. Labels beat SSL at equal budget for crack (oracle-selected).

Limits: one split; 49 clean test cells and 10 E1 inactive cells; cv02 only; untuned SSL recipes; oracle selection in Track D.

---

## Related docs
- `10_experiments_P13_P16_E1.md`: SK1, S-a and AL1, which these teams build on.
- `19_feature_learning_and_100pct_plan.md`: 28 to 30 Oct, MIM5, DDeP5, encoder erasure, protocol_100.
- `11_results_synthesis_and_claims.md`: rows 18 to 24.
- `12_decisions_log.md`: D41 onward.
- `13_problems_pitfalls_open_issues.md`: A14, A15, C14, C15, D20 onward.
- `14_code_and_infrastructure.md`: §1.2b, §5b.
- `17_escdd_dataset_audit.md` §5.11: scuff and star in our masks.
