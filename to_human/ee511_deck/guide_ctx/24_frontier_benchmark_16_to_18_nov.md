# 24. The frontier benchmark, 16 to 18 Nov 2026: the corrected split, the 5-seed confirmations and the screens (state 18 Nov, 07:00 IST)

## What this covers
This file continues doc 23 (12 to 15 Nov). It explains the results of 16 to 18 Nov 2026 from the agent team in `team_2026-11-12_frontier/`. It is written for the guide agent.
- **The corrected split cv5v3** and why it exists (§1), and **the leakage read**: did the module leak in the old split inflate scores? (§2)
- **Screens on the old split cv5v2:** benchmark rows tranche 2 (§3), wave 2a (§4), la_ce (§7).
- **The unseen-source read U1** (LOSO-2) (§5).
- **The two 5-seed confirmations on cv5v3:** swad_const and HRNet-W18 (§6). Neither is confirmed; §6.3 says what that means for the final model.
- **What is running, what is owed** (§8), **the open questions for the student** (§9), **GPU sharing on cv02** (§10), **incidents** (§11), **where the files are** (§12).

**Tags.** E = measured in our files (path given), S = judgement. Every number below is E unless marked S. All result files are under `team_2026-11-12_frontier/results/` unless another path is given.

**Verdict and reading.** "Verdict" is what the rule written before the numbers says, quoted from the result file. "Reading (S)" is interpretation and decides nothing. The two are kept apart below.

**Words used in this doc** (doc 23 §2 has the full protocol):
- **PF** = the encoder-preserving fine-tune of doc 20 (U-Net++ / ResNet-34), the comparator of every arm. **HOUSE** = the same model with the plain fine-tune.
- **OP-A** = plain argmax. **OP-W** = width-matched: a crack bias fitted on the other folds so the arm draws cracks as wide as PF does.
- **M** = the decision margin from an A/A comparison of PF seeds {5, 6} against {7, 8}: M = max(0.01, 2 x its standard error). It is 0.010 for the crack metrics and mIoU-R13 in every CV5 read below, and about 0.05 for inactive IoU (U1 has its own, larger margins, §5).
- **Screen** = 2 seeds on cv5v2. A screen pass is "a promotion to a 5-seed confirmation, never a result" (protocol section 5, quoted in `ROWS2_READ.md` §2). **Confirmation** = 5 seeds on cv5v3, read once.
- **532 cells / 416 clean cells:** every read prints both. The 416 clean cells exclude the 116 cells touched by the module leak (§1).

## 1. The corrected split cv5v3, and why it exists
- **The leak in cv5v2 (E, doc 23 §6; `results/stageC/SPLIT_INTEGRITY.md`).** cv5v2 kept each module group in one fold, but its groups were built from image ids, and one physical module can carry several image ids. So 24 physical modules spanned two folds, and 91 of the 532 cells were scored by a model that had seen another cell of their module.
- **One more link found on 16 Nov (E, log 16 Nov 00:39).** The SDLE file names contain the module name (A1, A10, A11), and the cells of those three modules sat in all five cv5v2 folds. So the clean-cell list became `benchmark/splits/score_exclude_v3.txt`: **116 cells excluded, 416 clean** (the 99 of doc 23 §6 plus 17 SDLE cells). This replaces the "99 excluded, 433 left" of doc 23 §6.
- **cv5v3 (E, `benchmark/PROTOCOL_v0.2.md` §11 item 11; `benchmark/splits/cv5v3_check.txt`).** Published and reviewed 16 Nov 01:04 (`harness/REVIEW_CV5V3.md`, delta review PASS).
  - Groups = the cv5v2 groups plus the physical modules of the audit, four open image-id pairs and the SDLE modules: **285 groups, none spans two folds** (physical modules spanning folds: 0 of 304, against 24 in cv5v2).
  - A group that sat in one cv5v2 fold keeps its fold; a group that spanned folds goes to its majority fold. **47 cells move.** Held-out sizes 107 / 110 / 103 / 101 / 111.
  - Balance: crack cells spread 4 across folds (9 in cv5v2), inactive cells 7 (8 in cv5v2). Accepted costs: SDLE cells are scored in folds 0, 2 and 4 only; BMRK (50 cells) carries no module information in pixels or names, so it stays grouped by image id (a stated limit).
  - The 416 clean cells keep their fold in cv5v3, so the same cells can be compared across the two splits.
- **Rule (E, PROTOCOL §11 item 11):** "The final 5-seed table (PF, HOUSE and every row or arm that goes to 5 seeds) is trained and scored on cv5v3." Screens already run on cv5v2 stay there and are read with the clean-cell columns beside.
- **PF on cv5v3 (E, 5 seeds, cv02, OP-A, 532 cells; `C3SWAD_READ.md` §3 and `C3HRNET_READ.md` §3 agree):** strict crack IoU 0.365, crack relF1@2 0.846, inactive IoU 0.504, mIoU-R13 0.612. On cv5v2 it was 0.365 / 0.844 / 0.503 / 0.612 (doc 23 §4.1).

## 2. Did the leak inflate the scores? The leakage read (`C3_LEAK_READ.md`, 17 Nov 18:43)
- **Rule (pre-registered 16 Nov in `harness/LAUNCH_REQUEST_c3base.md` §7, before any cv5v3 run existed).** For each seed run on both splits: DiD = [score on cv5v3 minus score on cv5v2] on the affected cells, minus the same difference on the 416 clean cells. A leak would raise the cv5v2 score of the affected cells and give a negative DiD. Primary stratum: the 69 affected cells that keep their fold ("affected_unmoved"); also the 47 that move. Interval: two-stage group bootstrap, 95%. Fixed reading: an interval containing 0 is "not separated", and nothing else is concluded.
- **Result (E):**

| Arm | Stratum | Strict crack IoU DiD [95% CI] | Crack relF1@2 DiD [95% CI] |
|---|---|---|---|
| PF (5 seeds) | affected_unmoved (69) | -0.0041 [-0.0136, +0.0069] | +0.0026 [-0.0092, +0.0174] |
| PF | affected_moved (47) | +0.0103 [-0.0286, +0.0252] | +0.0249 [-0.0286, +0.0387] |
| HOUSE (2 seeds) | affected_unmoved | +0.0049 [-0.0080, +0.0121] | +0.0014 [-0.0087, +0.0118] |
| HOUSE | affected_moved | +0.0007 [-0.0150, +0.0254] | +0.0145 [-0.0100, +0.0502] |

- **Verdict:** every interval contains 0: **"not separated"** for both arms, both strata and both metrics. The benchmark table uses cv5v3 only, as decided on 16 Nov.
- **Description beside the verdict (from the file, not a conclusion):** on the primary stratum the PF intervals reach down to -0.014 (strict crack IoU) and -0.009 (relF1@2); a leak of the size the module audit allowed as an upper bound (+0.07 crack IoU on affected cells) lies outside them.
- **Limits:** 69 and 47 cells, one machine (cv02), argmax only; HOUSE has 2 seeds and no A/A.
- **Reading (S):** the leak in cv5v2 did not measurably change scores, so the cv5v2 screens of §3, §4 and §7 stand as screens. The split was still corrected, because "every cell is predicted by a model that never saw its module" must be true for the final table.

## 3. Benchmark rows tranche 2 (screens on cv5v2, cv02; `ROWS2_READ.md`, 16 Nov 19:14, SegFormer completed 17 Nov 15:30)
Three rows, 2 seeds x 5 folds each, against 5 PF seeds. Screen rule (E, §2 of the file): the headline crack relF1@2 must gain at least M with the lower interval end above 0, at OP-A and at OP-W, on all cells and on the clean cells; guards: crack width ratio within 0.85 to 1.15 of PF pooled and per source, false crack pixels on crack-free cells at most 1.5 x PF, inactive IoU and mIoU-R13 not worse.

| Row (OP-A, 532 cells, mean over seeds) | Strict crack IoU | Crack relF1@2 | relP@2 / relR@2 | Inactive IoU | mIoU-R13 | Width ratio |
|---|---|---|---|---|---|---|
| PF (5 seeds) | 0.365 | 0.844 | 0.894 / 0.799 | 0.503 | 0.612 | 1.00 |
| HOUSE (2 seeds) | 0.382 | 0.850 | 0.897 / 0.807 | 0.522 | 0.609 | 1.11 |
| hrnet_w18_unetpp_pf (U-Net++ / HRNet-W18) | 0.365 | **0.856** | 0.902 / 0.814 | 0.522 | 0.618 | 0.94 |
| skr01_pf_v11 (PF + Skeleton Recall loss) | 0.372 | 0.848 | 0.884 / 0.815 | 0.480 | 0.611 | 1.13 |
| segformer_mitb2_pf (SegFormer MiT-B2) | 0.348 | 0.842 | 0.877 / 0.809 | 0.530 | 0.608 | 1.20 |

- **HRNet-W18: SCREEN PASS** (first row or arm under the new protocol to pass on relF1@2). relF1@2 minus PF: **+0.0114 [+0.0032, +0.0203]** at OP-A, **+0.0128 [+0.0041, +0.0221]** at OP-W; on the clean cells +0.0118 and +0.0130, both intervals above 0.
  - The gain is recall at equal precision: width-matched relR@2 +0.023, relP@2 -0.0002. Strict crack IoU does not move (+0.0003 at OP-A): HRNet draws cracks 6% thinner.
  - Guards pass; false crack px on crack-free cells 695 against PF 357, "to be watched at 5 seeds".
  - Cost: 20.8 M parameters, 218 GFLOPs (1.47 x the house model); about 107 minutes per run against about 80 for PF.
  - Ruling: promoted to a 5-seed row on cv5v3 (§6.2).
- **Skeleton Recall anchor skr01: SCREEN FAIL, closed.** relF1@2 +0.0039 [-0.0027, +0.0115] at OP-A, +0.0022 [-0.0047, +0.0097] at OP-W. At argmax the recall gain (+0.016) comes with 13% wider cracks and lower precision; width-matched, every crack metric is within 0.005 of PF. Reading in the file (S): the loss moves the operating point, not the frontier.
- **SegFormer MiT-B2: SCREEN FAIL, closed.** relF1@2 -0.0026 at OP-A, -0.0135 [-0.0259, -0.0005] at OP-W; strict crack IoU -0.031 width-matched (interval below 0). Width guard fails: cracks drawn 20% wider than PF (ARTS 1.43 x). Inactive IoU +0.028 (interval holds 0; the first seed alone had shown +0.048). Reading in the file (S): the stride-4 decoder costs thin-crack accuracy.
- Both closed rows stay in the benchmark table as screened rows on cv5v2.

## 4. Wave 2a (screens on cv5v2, gaint; `W2A_READ.md`, 17 Nov 08:41, addendum 17 Nov 19:43)
Six trained arms, 2 seeds each, read against the gaint PF seeds 5 and 6. Gates in `W2A_GATES.md`. The arms (cards in `harness/LAUNCH_REQUEST_w2a.md` §3):
- **swad_const:** PF with a constant learning rate after warm-up and a uniform average of every weight iterate from step 10,000 to 20,000, batch-norm statistics re-estimated (readout `swad_bn`, declared before the read; arXiv:2102.08604).
- **rcs:** rare-class sampling (cells with rare classes drawn more often).
- **ema_wise_posthoc:** exponential moving averages of the PF weights.
- **jml_hard / soft_band_jml:** the JML (Jaccard metric) loss on crack and inactive, with hard labels (the control) or with a soft 2 px band around crack labels.
- **encoder_spd:** an optimizer term that pulls the encoder back towards its pretrained weights (selective projection decay).

| Arm (OP-A, 532 cells, mean of 2 seeds) | Strict crack IoU | Crack relF1@2 | Inactive IoU | mIoU-R13 | Width ratio | False crack px (303 crack-free cells) |
|---|---|---|---|---|---|---|
| PF (comparator) | 0.362 | 0.842 | 0.498 | 0.612 | 1.01 | 301 |
| **swad_const (swad_bn)** | **0.387** | **0.855** | 0.508 | **0.620** | 1.07 | 263 |
| rcs | 0.344 | 0.833 | 0.485 | 0.614 | 0.94 | 505 |
| ema_wise_posthoc (ema_9998_bn) | 0.363 | 0.838 | 0.497 | 0.610 | 0.98 | 245 |
| jml_hard (control) | 0.364 | 0.841 | 0.513 | 0.613 | 0.99 | 287 |
| encoder_spd (gate failed, descriptive) | 0.374 | 0.842 | 0.501 | 0.606 | 1.08 | 736 |

**Verdicts (E, quoted from the file):**
- **swad_const: screen PASS, with one width flag.** relF1@2 minus PF **+0.0135 [+0.0051, +0.0221]** (OP-A), **+0.0118 [+0.0033, +0.0208]** (OP-W); clean cells +0.0160 and +0.0141. Strict crack IoU +0.0245 at OP-A. Width-matched, the gain is precision at equal recall (relP@2 +0.024). The averaging is the cause, not the constant rate: the last iterate of the same runs is below PF (relF1@2 -0.0127). **Flag:** ARTS crack width at argmax 1.20 x PF, outside the 0.85 to 1.15 band. Promoted to a 5-seed confirmation (§6.1).
- **rcs: FAIL, closed.** Strict crack IoU -0.018 at OP-A (interval below 0); false crack px 1.68 x PF (above the 1.5 x guard). It buys the rare splice class (+0.067 IoU) and pays with crack and inactive.
- **ema_9998 over the PF runs: null, closed.** +0.0018 [-0.0047, +0.0081], a fifth of M.
- **jml_hard: null control** (relF1@2 -0.0004 [-0.0086, +0.0064]).
- **encoder_spd: mechanism gate FAIL** (layer3 / layer4 cosine to the start 0.53 to 0.60 against the 0.8 threshold in 10 of 10 runs), read descriptively only: no gain, false crack px 2.4 x PF. Pre-registered consequence: one re-run at lambda 2.2 (fold 0, seed 5 first); if its gate fails, SPD is dropped and L2-SP is the fallback arm.
- **soft_band_jml (addendum, 17 Nov 19:43, after one run was retrained): SCREEN FAIL, closed.** Read against jml_hard: relF1@2 +0.0046 [-0.0033, +0.0127] at OP-A, +0.0037 [-0.0040, +0.0116] at OP-W. The recall gain at argmax (relR@2 +0.013) comes with cracks drawn 7% wider; width-matched it shrinks to +0.005. Consequence (pre-set gate): **label_jitter_crack is not opened** (it needed soft_band minus jml_hard >= M).

**Limits (E, §8 of the file):** 2 seeds, one machine, cv5v2 (with the leak), pool cells from known modules only.

## 5. Unseen sources: the U1 read on LOSO-2 (`U1_READ.md`, 17 Nov 18:46)
- **What LOSO-2 is:** two extra trainings per seed, each on all sources but one, scored on the held-out source: CSIR (114 cells) and BMRK (50 cells). Pooled U1 = 164 cells, effective n for crack about 17.7. It measures behaviour on sources the model never saw, without opening E1. PF seeds 5 to 8, Skeleton Recall anchor (SKR01) seeds 5 and 6; gaint.
- **Rule (written before any LOSO-2 run: `results/stageB/B3.md` §1b rule 6):** the deciding contrast is SKR01 minus PF at the frontier (relR@2 at PF's own relP@2), pooled. If its interval is not above 0, U1 is a guard, not a primary. "Inconsistent" = the two sources give opposite signs, each at least that source's own A/A margin.

| (E) | PF (4 seeds) | SKR01 (2 seeds) |
|---|---|---|
| strict crack IoU | 0.293 | 0.312 |
| crack relF1@2 | 0.733 | 0.744 |
| relP@2 / relR@2 | 0.892 / 0.623 | 0.902 / 0.634 |
| width ratio | 0.61 | 0.70 |
| inactive IoU | 0.197 | 0.214 |

- A/A margins on U1: crack IoU 0.032, relF1@2 0.044, frontier relR@2 0.064, inactive IoU 0.077.
- Deciding contrast: **+0.0206 [-0.0518, +0.0744]**. Per source (cannot decide alone): CSIR +0.0317, BMRK -0.0066.
- **Verdict:** "U1 is a guard, not a primary"; opposite signs but neither source reaches its own margin, so **not "inconsistent"**.
- **Consequence (lead's ruling, logged 17 Nov):** the planned unseen-module arm **gin_ipa** (GIN + IPA augmentation) is **parked, not closed**: its expected effect (+0.01 to +0.04) is below U1's margins. It can return only with a stronger unseen-module instrument (U2, or the registered E1 opening in the last week).
- **Descriptive (S, from the file):** on held-out sources PF loses about 0.11 relF1@2 against its CV5 level (0.733 against 0.844), draws cracks thinner than labelled (width ratio 0.61; part of this is BMRK's 3 px label style), and its false crack px on crack-free cells rise (1,726 against about 357). The unseen-source gap is real and large; this read cannot rank methods on it, because on U1 only effects of about +0.05 or more can be seen.

## 6. The 5-seed confirmations on cv5v3 (cv02)
**The rule, the same for both** (E; `harness/LAUNCH_REQUEST_c3swad.md` §7 for swad_const; for HRNet written in `log.md` 18 Nov 00:22, before seeds 8 and 9 existed, "so the two confirmations are judged alike"):
- **Headline:** crack relF1@2, arm minus PF. A gain counts only if delta >= M and the interval's low end > 0 **at all four values**: OP-A and OP-W, on the 532 and on the 416 clean cells.
- **Guards** (point values, both cell sets, both operating points): width ratio arm / PF within 0.85 to 1.15, pooled and per source with at least 40 cells; **false crack px on crack-free cells at most 1.5 x PF**; inactive IoU delta >= -M(inactive); mIoU-R13 delta >= -M.
- **Three outcomes:** CONFIRMED (headline passes and every guard passes); **NOT CONFIRMED, reported as a gain with the failing guard items named** (headline passes, a guard fails); **NOT CONFIRMED (no confirmed gain)** (headline fails).

**Levels on cv5v3** (E; OP-A, 532 cells, 5 seeds each; `C3HRNET_READ.md` §3, `C3SWAD_READ.md` §3):

| Row | Strict crack IoU | Crack relF1@2 | Inactive IoU | mIoU-R13 | False crack px on 303 crack-free cells |
|---|---|---|---|---|---|
| PF | 0.365 | 0.846 | 0.504 | 0.612 | 212 |
| HOUSE | 0.383 | 0.852 | 0.514 | 0.607 | 774 |
| HRNet-W18 U-Net++ | 0.366 | **0.857** | 0.514 | 0.614 | 767 |
| swad_const (swad_bn) | **0.383** | 0.853 | 0.520 | **0.619** | 339 |

### 6.1 swad_const: NOT CONFIRMED (no confirmed gain) (`C3SWAD_READ.md`, 17 Nov 23:33)
| relF1@2, arm minus PF (E) | 532, OP-A | 532, OP-W | 416, OP-A | 416, OP-W |
|---|---|---|---|---|
| swad_bn (primary) | +0.0070 [-0.0007, +0.0156] | +0.0048 [-0.0036, +0.0141] | +0.0098 [+0.0009, +0.0198] | +0.0071 [-0.0025, +0.0176] |
| swad (declared secondary) | +0.0064 [-0.0009, +0.0138] | +0.0053 [-0.0022, +0.0128] | +0.0075 [-0.0009, +0.0165] | +0.0058 [-0.0030, +0.0150] |

- **Verdict:** no value reaches M (0.010), so the headline fails: **NOT CONFIRMED (no confirmed gain)**. Every seed is positive (+0.0056 to +0.0104), with the mean below M.
- Guards (E): swad_bn fails 5 items: ARTS width (1.248 and 1.153 on 532 cells, 1.290 and 1.181 on the clean cells) and false crack px at OP-A (339 against 212 = 1.60 x). The carry rule (the `swad` readout carries the claim if swad_bn fails only per-source widths) does not apply, because neither readout passes the headline.
- **Beside the verdict (E, descriptive, decides nothing):** strict crack IoU rises by +0.013 to +0.021 at both operating points on both cell sets, every interval above 0 and every seed positive (+0.0180 [+0.0108, +0.0262] at OP-A on 532 cells). Width-matched, it is precision at unchanged recall (relP@2 +0.017). mIoU-R13 +0.0073.
- **Screen against confirmation (E):** relF1@2 +0.0135 on the cv5v2 screen, +0.0070 here; strict crack IoU +0.0245 there, +0.0180 here.
- **Reading (S, from the file):** the screen effect shrank by about half, as an arm picked on a screen is expected to (the "winner's curse"); the leakage read found no measurable leak, so the split change alone does not explain it. For the thesis, weight averaging gives a consistent strict-IoU and precision gain that the 2 px-tolerant headline does not reward; this is "a finding about the metric choice as much as about the method", reported, not claimed.
- swad_const stays in the benchmark table as a 5-seed row on cv5v3.

### 6.2 HRNet-W18 U-Net++: NOT CONFIRMED, reported as a gain with failing guards (`C3HRNET_READ.md`, 18 Nov 06:00)
| relF1@2, HRNet minus PF (E) | 532, OP-A | 532, OP-W | 416, OP-A | 416, OP-W |
|---|---|---|---|---|
| delta [95% CI] | +0.0104 [+0.0012, +0.0203] | +0.0117 [+0.0019, +0.0220] | +0.0115 [+0.00001, +0.0259] | +0.0126 [+0.0006, +0.0273] |

- **Headline: passes all four** (M 0.010; on the clean cells at OP-A the low end is 0.000014). Every seed positive (+0.0071 to +0.0126). The gain is recall at equal precision (relR@2 +0.015 at OP-A, +0.023 at OP-W), as in the screen.
- **Guards (E):** two fail.
  - **False crack px on crack-free cells, all four values:** 767 against 212 = 3.62 x (532, OP-A), 4.15 x (532, OP-W), 2.90 x and 3.29 x (416). Limit 1.5 x.
  - **ARTS width at OP-W on the 416 clean cells: 1.162** against the 1.15 bound.
  - Pooled widths, inactive IoU (+0.0100) and mIoU-R13 (+0.0022) pass.
- **Verdict:** **NOT CONFIRMED, reported as a gain with the failing guard items named.**
- **Secondary, pre-declared, decides nothing (E):** HRNet minus HOUSE relF1@2 +0.0045 [-0.0069, +0.0157] (OP-A), +0.0083 [-0.0041, +0.0209] (OP-W); strict crack IoU -0.0171 [-0.0291, -0.0068] at OP-A.
- **Beside the guard (E, from §3 of the file):** in absolute terms HRNet's excess is about 1.8 false crack px per crack-free cell. The share of crack-free cells with 50 or more false px: PF 0.13%, HOUSE 1.2%, HRNet 1.5%. HOUSE, which is not judged here, sits at 3.7 x PF.
- **Reading (S, from the file):** PF's partial encoder freeze makes it unusually clean on crack-free cells (under 1 false px per cell on average), so a 1.5 x PF bound is tight for every arm without the freeze. HRNet is "the only arm so far whose headline gain holds at 5 seeds on the corrected split".

### 6.3 What this means for the final model
- **The combination run c3x** (HRNet-W18 + swad_const, 25 runs, cv5v3, cv02) was prepared on 17 Nov and started 18 Nov 05:01 (§8). Its rule (E, `harness/LAUNCH_REQUEST_c3x.md` §6, fixed 17 Nov before any c3x run): COMBO is the final-model candidate only if its headline passes with every guard and it "adds" or shows "no loss" against both single arms; **otherwise the candidate is "the best confirmed single arm"** per the single arms' own verdicts.
- **No single arm is confirmed** (§6.1, §6.2), so that fallback has nothing to point to. The lead's rulings (logged 18 Nov 06:00): the c3x run continues as registered; how the final model is chosen when no arm is confirmed is **a question for the student** (§9). The two verdicts above stand as written.

## 7. la_ce: train-time logit offsets (screen on cv5v2, gaint; `W2B_LACE_READ.md`, 18 Nov 05:58)
- **What it is:** the cross-entropy loss is trained with per-class offsets added to the logits, taken from the post-hoc class-bias layer of stage B (the bias fitted on the other folds; "OP-C"). The question: does training with the offsets beat simply applying them after training?
- **Rule (pre-registered in `harness/w2b/READ_PLAN_w2b.md` §1; rulings in `log.md` 17 Nov 17:33 and 19:06):** primary P1 = la_ce at argmax minus PF with the post-hoc layer (PFC), on mIoU-R13; a point value at or below 0 means DROP.

| Element (E, verdict.txt) | 532 cells | 416 clean cells | Result |
|---|---|---|---|
| P1 la_ce minus PFC, mIoU-R13 (primary) | -0.0022 [-0.0112, +0.0060] | -0.0018 [-0.0136, +0.0070] | FAIL (point <= 0: DROP) |
| P2 la_ce minus PF (no post-hoc layer), mIoU-R13 | +0.0112 [+0.0017, +0.0204] | +0.0124 [+0.0004, +0.0222] | PASS |
| G1 crack metrics against PF | within +0.0011 | within +0.0011 | PASS |
| G5 predicted px on cells without the class, at most 1.5 x PFC | class 1: 4,503 vs 3,315; class 5: 122,580 vs 65,742 | | FAIL |

- **Verdict:** **DROP for this offset vector.** The file states this is **not a closure of the train-time-offset idea**: the follow-up la_ce_full (offset in both the CE and the Dice term), pre-declared 17 Nov 18:00, stays owed.
- **Reading (S, from the file):** training with the offsets reaches the level of applying them after training (mIoU-R13 0.6229 against PFC 0.6250 and PF 0.6117), and the post-hoc layer is free, so la_ce as built adds nothing. Inactive does not gain (0.494 against PF 0.498), which fits the reviewer's note that the Dice term pushes against the inactive offset; la_ce_full tests exactly that. Low priority: even a pass must beat a free post-hoc layer.

## 8. Running now (18 Nov, about 07:00 IST) and owed
From `log.md` 18 Nov 05:04, 05:49, 06:00 and 06:56.

**Running:**
- **gaint: the layered_ci screen** (wave 2b). The arm adds a sigmoid "inactive region" layer beside the 24-class softmax, trained on the inactive region together with the crack pixels in or at it. At test time this layer decides inactive (threshold 0.5): where it says inactive the pixel becomes inactive; where it does not, an inactive call of the softmax goes to the next class; crack pixels are never changed (card `layered_ci_pf_v11`, spec `cards/T10_rare_classes_spec.md` arm 3). It is the one trained inactive arm chosen at stage A (doc 23 §4.5). 10 runs (`w2b_lci_f[0-4]_s[56]`), started 05:27; at 06:56 the first two were at steps 18,000 and 17,100 of 20,000, no error. Its rule (`harness/w2b/READ_PLAN_w2b.md` §2, written before any w2b run): compared with PF plus the post-hoc inactive layer (PFC), on counts of inactive regions, not on pooled inactive IoU. **Promote** to a 5-seed confirmation if inactive region recall rises with the interval above 0 on both cell sets and the guards L2 to L7 hold (false alarms, precision, area, direction, mechanism, crack). **Drop** if the layer does not beat its own model's argmax, if inactive IoU falls against PFC, or if a crack guard fails. Otherwise **park**.
- **cv02: c3x**, HRNet-W18 + swad_const, 25 runs (folds 0 to 4, seeds 5 to 9), armed 05:01. At 06:56: 8 runs training, one per GPU (4 of them beside other users under the sharing rule of §10), steps 6,100 to 17,600, no error, none finished. Read once, when all 25 are relayed, by the rule of §6.3; no earlier look.

**Owed:**
1. **layered_ci read** (CPU on gaint, after its 10 runs and dumps).
2. **c3x read** (after all 25 runs; may wait on cv02 disk, §9 question 3).
3. **TTA block** on gaint, after the last w2b chain: D4 (8 flip / rotation views) and D4 with 3 scales (24 views) on the existing PF checkpoints, against a 3-seed D4 ensemble at equal cost. Rule written 15 Nov before any TTA number: `results/stageB/B5_tta_module.md` §1. Queues `bq/udev_tta_path`, `bq/udev_tta`, `bq/udev_tta_f51` (`harness/LAUNCH_REQUEST_udev.md`). Lead's reason for its place (log 17 Nov 17:57 and later): TTA is inference only and can be applied to any checkpoints later; training screens sit on the critical path.
4. **la_ce_full** (built and reviewed later; screened like la_ce; low priority).
- Also carried (S, from the log and `W2A_READ.md` §9): the encoder_spd re-run at lambda 2.2; udev_infer (unseen-module dumps, when gaint disk allows); the labelling pack (the user said "later" on 17 Nov); the benchmark protocol text; one registered E1 opening in the last week.

## 9. Open questions for the student (as of 18 Nov 07:00)
1. **How to pick the final model when no arm is confirmed.** Facts: HRNet-W18 passes the headline at 5 seeds but fails two guards (§6.2); swad_const fails the headline but gains strict crack IoU at every value (§6.1); c3x is running, and its fallback "best confirmed single arm" has no arm to name (§6.3). Raised by the lead in `C3HRNET_READ.md` §4.
2. **Whether the false-crack-pixel guard should keep PF x 1.5 as its reference** (for later arms only; the verdicts above stand). Facts: PF predicts 212 crack px in total over the 303 crack-free cells on cv5v3 (under 1 px per cell); HOUSE 774 and HRNet 767. The PF reference also varies between reads: 212 (cv02, cv5v3), 301 (gaint, cv5v2, 2 seeds), 357 (cv02, cv5v2, 5 seeds). Options named by the lead: keep 1.5 x PF, use an absolute bound, or use HOUSE as the reference.
3. **cv02 disk** (asked 17 Nov 18:08, open at 18 Nov 05:00). cv02 holds the full checkpoints (latest.pth) of finished runs whose outputs are already relayed to gaint; every run also keeps a slim checkpoint on cv02 and on gaint. Options: C1 rows 1 (50 files, 19.8 GiB), C2 rows 2 (30 files, 10.7 GiB), C3 W1-C (45 files, 17.5 GiB); the lead recommends C1. Without an answer the lead armed c3x anyway (ruling 18 Nov 04:59: otherwise the cv02 GPUs sit idle); a disk guard puts c3x on HOLD below 20 GB free, so c3x runs until then and waits, and nothing is lost. c3x needs about 51 to 54 GB; cv02 had 29 GB free at 06:56.

## 10. GPU sharing on cv02 (operational)
- cv02 is a shared lab machine (eight A6000, one shared login). Until 17 Nov our rule was strict: start a run only on a GPU where other users hold under 4 GB (doc 23 §8).
- **17 Nov 13:03 (E, log):** no GPU was free of other users (free memory per GPU 3.6 to 25 GB; four GPUs held memory at 0% use), so our queue could start no further run (1 of 62 started).
- **The student's decision (17 Nov 13:24, "Q1 D+B+C"):**
  - D: ask the other user or the lab admin to release idle GPUs;
  - B: a waiting dump (about 3.2 GB, 100 s) may run beside another user if the GPU has at least 10 GB free;
  - C: one training run of ours may start beside another user if at least 20 GB are free, still one of ours per GPU.
- **How it was built (lead's rulings R1 to R9):** the strict rule is tried first and a strict GPU is always preferred; a shared training start needs at least 20,480 MiB free on two checks at least 30 s apart; a shared dump needs 10,240 MiB. The two floors are the student's and cannot be lowered without asking. They are read live from files in the queue folder (`SHARE_TRAIN`, `SHARE_DUMP`); a missing or lower value switches sharing off at once. Reviewed (`harness/REVIEW_C3LANE.md`) and live from 17 Nov 15:28.
- **18 Nov about 00:23 (E, log 01:19):** other users started processes on GPUs 0 and 1 beside two of our runs; free memory fell to 15 MiB and 3 MiB. Our runs showed no error and kept going; two of the other processes ended after about 10 minutes (why is not known). The same happened on GPU 0, where our run had a strict start, so the pile-up "does not come from the sharing rule alone" (S). Ruling: sharing stays on (the student accepted the small out-of-memory risk); if the student or a lab member objects, it goes off at once.

## 11. Incidents (so nobody repeats them)
- **16 Nov 02:06:** the second account hit its weekly limit; both running workflows died, and nothing was read or launched until the session resumed at 11:58.
- **16 Nov 04:27 to 06:38, gaint:** a GPU process that was not ours joined our two runs; free memory fell to 1,972 MiB and the auto-stop guard did its job: HOLD on the queue and a stop of our newest run (`w2a_softband_f1_s6`, step about 12,000). Nobody lifted the HOLD because no tick ran; the GPU sat idle 05:05 to 12:01. The stopped run was retrained from step 0 on 17 Nov (rc 0), which is why soft_band_jml was read last (§4).
- **17 Nov 14:58:** files of the lane-rule change were altered after the fix report and before the review; the lead logged it as its own error, held the review and restored the reviewed set before launch.
- **17 Nov 15:31 to 16:56:** a gap on the account limit; around 17:11 two builder agents stopped on a model limit and were restarted on another model.
- **Disk:** gaint deletions approved by the student: the 50 dump folders of the finished rows 1 read (49 GB, "Q2 i", 17 Nov); the dumps of the closed rows 2 rows skr01 and SegFormer (19 GB, "D1"); the wave 2a dumps of closed arms after the soft_band read ("D2"). Old-era folders ("D3") only after asking again. Checkpoints are kept in every case.

## 12. Where the files are (all under `research/team_2026-11-12_frontier/` unless stated)
| What | File |
|---|---|
| Day-by-day record (16 to 18 Nov: log lines 77 to 197) | `log.md` |
| Protocol, incl. the cv5v3 ruling (§11 item 11) | `benchmark/PROTOCOL_v0.2.md` |
| cv5v3 build, check and files | `results/stageC/CV5V3_BUILD.md`, `benchmark/splits/cv5v3_check.txt`, `cv5v3.json`, `cv5v3_groups.tsv`, `score_exclude_v3.txt`; review `harness/REVIEW_CV5V3.md` |
| Leakage read | `results/C3_LEAK_READ.md`, tables `results/c3_leak_read/`; rule `harness/LAUNCH_REQUEST_c3base.md` §7 |
| Rows tranche 2 | `results/ROWS2_READ.md` (replaces `ROWS2_PRELIM.md`), tables `results/rows2_read/`, `results/rows2_full_read/` |
| Wave 2a | `results/W2A_READ.md`, `results/W2A_GATES.md`, tables `results/w2a_read/`, `w2a_spd_read/`, `w2a_softband_read/`; cards `harness/LAUNCH_REQUEST_w2a.md` |
| U1 (LOSO-2) | `results/U1_READ.md`, tables `results/u1_read/`; rule `results/stageB/B3.md` §1b rule 6 |
| First cv5v3 look (seed 5, descriptive, no verdict) | `results/C3_S5_LOOK.md` |
| swad_const confirmation | `results/C3SWAD_READ.md`, tables `results/c3swad_read/`; rule `harness/LAUNCH_REQUEST_c3swad.md` §7 |
| HRNet-W18 confirmation | `results/C3HRNET_READ.md`, tables `results/c3hrnet_read/`; rule `log.md` 18 Nov 00:22 |
| la_ce and layered_ci | `results/W2B_LACE_READ.md`, tables `results/w2b_lace_read/`; rules `harness/w2b/READ_PLAN_w2b.md`; request `harness/LAUNCH_REQUEST_w2b.md` |
| c3x (combination) | `harness/LAUNCH_REQUEST_c3x.md` §6, review `harness/REVIEW_C3X.md` |
| TTA block | `results/stageB/B5_tta_module.md` §1, `harness/LAUNCH_REQUEST_udev.md` |
| Lane rule v2 (cv02 sharing) | `harness/LAUNCH_REQUEST_c3lane.md`, `harness/REVIEW_C3LANE.md`; decisions in `log.md` 17 Nov 13:24 |
