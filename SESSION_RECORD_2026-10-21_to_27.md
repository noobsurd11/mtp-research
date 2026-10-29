# Session record, 21 to 27 Oct 2026

MTP with WattCycle. BenchmarkEL 20211104 (478 / 54 / 50 cells, 24 classes), revised `masks_escdd`, final-step weights (step 20,000), cv02, unless stated.

- **Who checked the numbers:** every number below was recomputed by an independent critic agent before it was accepted.
- **Other copies:** the same record is published as an artifact page, https://claude.ai/artifact/7M4kds5ka2uJrVXCChSSN8 (private). An HTML copy is at `to_human/session_record_2026-10-21_to_27.html`.
- **"Clean test":** the 50 test cells without the corrupted cell `CSIR_00070_r8_c4`.

## Headline numbers (best model, FINAL)
| | Value | Context |
|---|---|---|
| Crack IoU, clean test | **0.492** | single model 0.474; +0.018 [+0.013, +0.025] |
| Crack segments found (≥ 20 px) | **0.834** | at segment precision 0.933; 2 px recall 0.866 |
| Inactive IoU, clean test | **0.456** | n.d. vs single model 0.449 |
| Unseen modules (E1), crack recall | **0.215** | 106 cells, 67 modules; single model 0.178 |

## 1. Conclusions
1. **Pseudo-label SSL helps only when labels are scarce.**
   - At 5% labels, BsM5 (Mean Teacher, hard pseudo-labels, CutMix, separate BN) beats supervised on crack IoU (+0.029) and inactive IoU (+0.107).
   - At 20, 50 and 100% labels, a crack gain of +0.02 or more is ruled out; at 100%, +0.01 too.
2. **The two 2025 SOTA methods did not transfer.**
   - ALHVR (ICCV 2025), adapted to EL, is worse than supervised on all three primaries and halves inactive recall.
   - SKCDF's balanced head (CVPR 2025) is n.d.: it corrects a class collapse we do not have.
3. **Labels beat SSL at equal budget.** With 12 crack-rich labelled cells added (chosen with ground truth), crack IoU is 0.352. For comparison: best SSL 0.331; 12 random cells 0.324.
4. **The best model is a 5-seed ensemble of the 100%-label recipe** with a crack bias of +0.75. Six training changes all failed the val inclusion rule.
5. **Strict crack IoU is near its labelling ceiling.** A perfect detector 1 px off scores 0.48 to 0.60, and 70% of the remaining IoU loss lies within 2 px of GT.
6. **The real gap is a defect context we never labelled.**
   - On unseen modules, 75% of crack pixels sit in half-cut cells with scuff streaks, where recall is 0.13.
   - Training has no half-cut cells and has always ignored scuff.
   - The 12k unlabelled pool barely contains such cells.
7. **The user's own intuition was never tested.** Everything run was label propagation. Self-supervised feature learning (masked-image or contrastive pretraining) was dropped early. One bounded test is proposed.

## 2. Timeline
| Date | What happened |
|---|---|
| 21 Oct | Agent team set up: ALHVR trainer and critic, SKCDF trainer and critic. Data decision D1 to D7. 7 test cells found to be physical twins of train cells. User answers: use local `escdd_full`; D7 = drop the twins from unlabelled pools; add "without twins" lines, never replace |
| 22 Oct | SK1 (SKCDF ABSH), 20 runs: n.d. S-a logit-adjustment yardstick. SKCDF track closed on the critics' advice |
| 23 Oct | AL1 v2 (ALHVR-EL), 35 runs: WORSE on all three primaries in all four cell sets. Handbook updated |
| 24 Oct | Why-SOTA team (data side, method side, critic): diagnosis and 8 ranked directions. User: "take the critics' decisions and go", with the max-score goal stated |
| 24-25 Oct | Track D (probe, edge re-score, labelled-set experiment, 27 runs) and Track M (baseline audit, ladder R1 to R5, final ensemble). Critic-verified, relayed to gaint with MD5, committed |
| 27 Oct | Unlabelled-data research team (lit, evalx, ideas, judge), Research MCP, no GPU. Converged synthesis |

## 3. Data decisions (`team_2026-10-21/data/decision.md`)
- **D1. No newer E-SCDD release exists.**
  - The one meant is local `escdd_full` (HF snt-ubix/escdd @ `8c8cba9a`, MIT, 1,810 files, 30 classes).
  - The shivahanifi variants are not used: they rescale cells and change crack width.
  - `sasan/scdd-unlabeled` (159,332 unlabelled cells, 76 GB) exists and was not downloaded.
- **D2.** Keep the 20211104 split with `masks_escdd`. E-SCDD's own split is unusable: 39 of our 50 test cells are in its train. Synthetic images are excluded everywhere.
- **D3.** Runs carry over only on the same machine, after a log-identity check.
- **D4.** The in-domain pool is primary. The 11,938-cell external pool is used only as a declared arm. E1 cells never enter any pool.
- **D6.** Every test number is reported in four cell sets: all 50 / without the noisy cell / without the 7 twins / without both.
- **D7 (user: yes).** Drop the 7 train twins from the unlabelled pool (455 to 448 cells) and re-run the SSL references.

**The 7 twin test cells** (CFVS time series plus one ARTS cell):

| Test cell | Train twin(s) | Crack px | Inactive px |
|---|---|---|---|
| `CFVS_00006_r5_c5` | `CFVS_00003_r5_c5` | 505 | 0 |
| `CFVS_00033_r8_c4` | `CFVS_00037_r8_c4` (+ early stage `00032`) | 4,876 | 0 |
| `CFVS_00035_r8_c4` | `CFVS_00037_r8_c4` | 5,513 | 2,728 |
| `CFVS_00042_r8_c4` | `CFVS_00037_r8_c4` | 4,202 | 3,178 |
| `CFVS_00018_r4_c4` | `CFVS_00020_r4_c4`, `00022` | 10,915 | 0 |
| `CFVS_00027_r4_c4` | `CFVS_00031_r4_c4`, `00022` | 10,211 | 5,214 |
| `ARTS_00020_r5_c1` | `ARTS_00081_r5_c1` | 183 | 0 |
| **Total** | | **36,405 (39.5%)** | **11,120 (12.1%)** |

**Effect on the old BsM5 − A5c claim (crack IoU):**
- all 50 cells: +0.029;
- without the twins: +0.019, still passing, barely.

Inactive and relF1@2 gains are not driven by the twins.

## 4. SSL experiments at 5% labels
23 labelled cells and a 448-cell pool, 20,000 steps, 5 seeds per arm. Rule 1: better on one primary, worse on none.

**Test crack IoU, 50 cells:**

| Group | Arm | Crack IoU |
|---|---|---|
| Supervised | A5c | 0.304 |
| SSL | AL5 (ALHVR-EL) | 0.287 |
| SSL | AB5 (ABSH, supervised) | 0.295 |
| SSL | CPS5 | 0.307 |
| Free bias | A5c + logit adjustment | 0.319 |
| SSL | BsD5 (decoupled) | 0.328 |
| SSL | BsM5 (best SSL) | 0.331 |
| +12 labelled | R, random | 0.324 |
| +12 labelled | Tc, crack cells | 0.337 |
| +12 labelled | Ts, weak-source crack cells | 0.352 |
| +12 labelled | Ts + logit adjustment | 0.365 |
| Reference | L3 10% labels | 0.396 |

### SK1: SKCDF balanced head (`team_2026-10-21/skcdf/results.md`)
| Contrast | crack | inactive | relF1@2 | Verdict |
|---|---|---|---|---|
| BsDB5 − BsD5 (primary) | −0.004 | −0.011 | +0.004 | n.d. |
| AB5 − A5c (supervised) | −0.008 | −0.008 | −0.007 | n.d. |
| BsDB5 − BsDBn5 (2 px band) | −0.015 | −0.017 | −0.005 | WORSE (crack) |

- The verdicts are the same in all four cell sets.
- The head converges onto the main head (drift about 0.001 at 20k), so it overwrites the labelled fit.
- Without the band, BsDBn5 equals a free logit bias on IoU.

### AL1 v2: ALHVR adapted to EL (`team_2026-10-21/alhvr/results.md`)
| Contrast | crack | inactive | relF1@2 | Verdict |
|---|---|---|---|---|
| AL5 − A5 (primary) | −0.017 | −0.132 | −0.031 | WORSE |
| CPSm5 − CPS5 (routing) | −0.003 | −0.013 | −0.003 | n.d. |
| AL5 − ALd5 (CPCL) | −0.008 | +0.017 | −0.017 | n.d. |
| CPS5 − A5 | +0.003 | +0.074 | +0.007 | n.d. |
| BsM5 − A5 (reference) | +0.027 | +0.132 | +0.041 | passes |

- **Adaptation:** dual nets with regions Ω1 to Ω3, the DTCT loss, and CG-CPCL at the full-resolution decoder output. Perturbation is noise-only (no geometric aug on thin cracks). λ is 0.1, with warmup from 2k to 4k steps. Arms: AL5, ALd5 (no CPCL), ALdh5 (λ 0.3), CPS5, CPSm5.
- **Primary verdict:** WORSE in all four cell sets, with bootstrap CIs excluding 0 on all three primaries. Inactive recall falls from 0.276 to 0.124.
- **Mechanism:** 65 to 70% of GT crack and 56 to 60% of GT inactive fall in Ω1, which gets no unlabelled loss. The sharpened-MSE plus entropy loss on Ω2/Ω3 teaches background on inactive. Plain CPS does not harm.

### S-a: the free-bias yardstick
- **What it is:** logit adjustment, τ = 1, with the prior taken from the 23 labelled cells. It needs no training.
- **Effect on crack IoU:** A5c 0.304 → 0.319; BsD5 0.328 → 0.341.
- **Result:** with the bias on both sides, BsM5's crack gain still passes, +0.037 (+0.035 without the twins and the noisy cell).

## 5. Why standard SSL fails here (`team_2026-10-24_why/SYNTHESIS.md`)
**Measured:**
- Crack belief is bimodal: 57% of GT crack px score < 0.001 and 35% score ≥ 0.95, so pseudo-labels can act on only 8 to 19%.
- The crack gain is source-bound (without twins): CFVS +0.047, BMRK +0.002, ARTS −0.030.
- At 5%, ARTS has 0 labelled crack cells and BMRK has 2. [Correction 29 Oct (coach, E, server `masks_escdd`): the seed-0 5% set has one small ARTS crack cell, `ARTS_00051_r6_c2` (47 px), so ARTS has 1 labelled crack cell, not 0; 9 crack cells in total. `team_2026-10-29_features/review_ddep5_cp5_v0.md` P2.]
- About 38% of pool crack is a true miss, more than 2 px from any prediction. No training rule moved it by more than 0.046.
- Inactive is the counter-case: supervised under-extends regions (precision 0.77, recall 0.28), and self-training extends them (recall 0.43).

**Reasoned:**
- Self-training spreads labels through neighbourhoods the teacher already gets right (expansion assumption, arXiv 2010.03622).
- Published gains come mostly from weak baselines or blob-like classes.
- We fail Oliver et al.'s realistic-SSL conditions (arXiv 1804.09170).

**Not causes:** pool size, the twins, the noisy cell.

## 6. Track D: diagnosis (`team_2026-10-24_go/trackD/`, DX + critic C)
**Frozen-encoder probe:** a linear probe on frozen features, trained on the 23 labelled cells. The bar was BMRK crack AP 0.215.
- **Passes:** ConvNeXt-T 0.275 (test only) and ImageNet ResNet-50 0.268 (test and pool).
- **Fails:** ResNet-34 0.186 and DINOv2-S 0.128.
- **Caveat:** at A5c's precision the probes recall 0.02 of BMRK crack, against 0.21 for A5c. MIM was dropped on this result; the 27 Oct team judged that too early.

**Inactive-edge re-score (post hoc):**
- 11.6% of test crack lies within 2 px of inactive (BMRK 22.6%), and recall there is 0.18 to 0.24.
- Ignoring the band lifts crack IoU by +0.018 to +0.027 at 5 to 10% labels, and +0.007 at 100%.
- No SSL gap flips sign.

**Labelled-set experiment** (27 runs: 5% base + 12 cells, 3 draws × 3 seeds per arm):

| Arm | crack IoU | relF1@2 |
|---|---|---|
| R, random | 0.324 | 0.757 |
| Tc, crack cells | 0.337 | 0.787 |
| Ts, 6 BMRK / 4 ARTS / 2 CSIR crack cells | 0.352 (0.365 with LA) | 0.795 |

- **Tc − R: BETTER.** relF1@2 +0.030 [+0.020, +0.042] in every cell set. Crack-pixel volume explains the gap.
- **Ts − Tc: n.d.**
- **Ts − R: BETTER** in every cell set. BMRK recall rises from 0.24 to 0.31, and Ts's BMRK IoU of 0.259 beats L3 10% (0.219).
- **Costs:** unseen-module crack false alarms rise to 0.26 to 0.30, against 0.20. All-class mIoU is n.d.
- **Gate:** the gate for SSL on the better-covered set was not met, so that run did not happen.

## 7. Track M: best model (`team_2026-10-24_go/trackM/`, MD + critic MC)
| Rung | Change | Verdict | Note |
|---|---|---|---|
| R1 | 5-seed ensemble, TTA, crack bias | PASS | +0.014 crack IoU; TTA adds nothing |
| R2 | Dice on 12 classes | WORSE | crack; clipping bound 97% of steps |
| R2c | Dice on crack, inactive, gridline | n.d. | |
| R3 | ResNet-50 encoder | WORSE | inactive −0.025; BMRK AP +0.018; E1 crack recall +0.036 |
| R4 | +107 leak-free E-SCDD cells | n.d. | |
| R5 | 2x internal resolution | n.d. | E1 crack recall +0.026 |

**FINAL** is U-Net++ / ImageNet ResNet-34 trained on 100% labels:
- **Loss and training:** CE plus Dice on crack and inactive, label-safe aug, 512 px, 20k steps.
- **Ensemble:** 5 seeds, mean softmax.
- **Crack bias:** +0.75 on the crack logit, chosen on val.

| Clean test | Single (mean of 5) | FINAL +0.75 | FINAL bias 0 |
|---|---|---|---|
| crack IoU | 0.474 | **0.492** | 0.488 |
| crack P / R | 0.644 / 0.642 | 0.621 / 0.703 | 0.662 / 0.650 |
| crack 2 px P / R | 0.938 / 0.830 | 0.930 / 0.866 | 0.953 / 0.837 |
| crack relF1@2 | 0.881 | 0.897 | 0.891 |
| crack segments found | 0.798 | 0.834 | 0.807 |
| inactive IoU | 0.449 | 0.456 | 0.454 |
| inactive segments found | 0.773 | 0.800 | 0.800 |
| mIoU (13 robust classes) | 0.580 | 0.583 | 0.583 |
| E1 crack IoU / recall | 0.148 / 0.178 | 0.172 / 0.215 | 0.148 / 0.170 |

- **Verdict: PASS** on crack IoU and relF1@2. Inactive and mIoU are n.d.
- **Fragility:** on the noisy cell, bias +0.75 calls 10,867 px crack (bias 0 calls 2), and all-50 crack precision drops to 0.563. Bias 0 is the robust operating point.
- **"Almost all cracks"** (2 px recall ≥ 0.90 at 2 px precision ≥ 0.90): not reached, at 0.866 / 0.930.
- **Per source** (crack IoU, single → FINAL):
  - ARTS 0.456 → 0.503;
  - BMRK 0.379 → 0.411 (2 px recall 0.812);
  - CFVS 0.522 → 0.535;
  - CSIR clean 0.475 → 0.485.
- **Per class:**
  - **Strongest:** padding 0.994, background 0.906, frame_edge 0.809, sp_mono 0.743, sp_multi 0.733, ribbons 0.634.
  - **Weakest robust classes:** gridline 0.288 (recall 0.33) and splice 0.000, which is never predicted.
- **Noisy cell:** it alone moves all-class mIoU by 0.033.

## 8. Unlabelled data (`team_2026-10-27_unlabelled/SYNTHESIS.md`)
The question: ~480 labelled cells give a result, and ~12k unlabelled cells exist. Why didn't using them help?

The answer:
- What we ran spreads labels the model already has. It cannot invent a crack the model scores at 0.001.
- The pool lacks the cells the model fails on.
- Feature learning was never tested.

**Measurement (evalx):**
- **Crack:** the test can see small crack gains. The detectable effect at 100% labels is 0.010 to 0.012, and Sx100 measured −0.002 [−0.007, +0.003]. The old "+0.028" came from one supervised seed failing on the noisy cell.
- **Inactive:** there are 16 test cells, so a +0.01 to +0.03 gain would be invisible. The detectable effect is 0.032 at 100% labels and 0.084 at 5%.
- **Where FINAL's crack IoU loss goes:** 70% within 2 px of GT, 18% missed cracks, 11% false alarms. One cell labelled twice agrees with itself at 0.53.
- **Scope:** the 20 to 100% null covers the Cs recipe only. BsM was never run at 50 to 100%, and at 20% its +0.013 [−0.002, +0.033] is not ruled out.

**Literature (lit):**
- **Same-encoder SSL gains** (doi:10.1109/tpami.2025.3528453): +6 to +11 mIoU at 92 to 316 labels, but only +0.3 to +1.6 at full labels with a non-matching pool.
- **Thin-structure MIM gains** are measured against training from scratch, not against ImageNet init. The closest industrial case: in-domain MAE 43.0 vs ImageNet ResNet-18 59.1 IoU on thin wires (arXiv 2605.12430).
- **Torpey** (arXiv 2402.17611), the only EL test: in-domain SimCLR 0.517 vs ImageNet-supervised 0.508, behind ImageNet-SimCLR 0.534 and COCO 0.544.
- **No EL or crack paper** shows an SSL gain on pixel crack over a tuned ImageNet baseline.
- **SAM-family models** fail on thin, low-contrast structures.

**The unseen-module failure (judge, evalx, ideas):**

| E1 crack cells | Cells | Share of crack px | FINAL recall |
|---|---|---|---|
| Half-cut multi + scuff streak | 20 | 75% | 0.126 |
| Half-cut, no scuff | | | 0.552 |
| Scuff, not half-cut | 2 | | 0.51 |

- **What the model does:** it paints the streak as crack (about 8.7k px per run) and misses the cracks branching off it, which lie a median 12 px from the streak.
- **Training coverage:** 0 half-cut cells and 1 cell with ≥ 500 scuff px; scuff is always scored as ignore.
- **Pool coverage:**
  - none of the 32 E1 crack cells comes from a pool module;
  - the pool's 1,152 half-cells carry only small thin cracks;
  - no pool SSL arm ever moved half-cut recall by more than +0.023.
- **Inside our own test:** unseen-module cells lose almost no crack (0.486 vs 0.499) but lose inactive (recall 0.43 vs 0.92).

**Test set and metric:**
- **Keep the 50 cells.** Add the clean set as co-primary, defined by an image-only noise rule fixed before any new run.
- **Do not use E-SCDD's official test:** 48 of its 82 cells are in our train.
- **Keep E1 sealed,** reported as two readouts: scuff + half-cut, and the rest.
- **New crack metric for future protocols:** segments found and 2 px recall at a fixed 90% precision, set on val, with IoU beside it. Past verdicts stay under their locked metrics.
- **Module-grouped 5-fold CV** over 693 cells (74 with inactive): only if inactive at 50%+ becomes the question. It costs about 100 GPU-h per SSL contrast.

**Ranked plan:**

| # | Item | Cheapest decisive test | Cost | Kill |
|---|---|---|---|---|
| 1 | Use the pool to find cells to label: scuff + crack half-cells via a model-based finder (AUROC 0.80, re-check on 43 labelled E-SCDD half-cuts); BMRK via ELPV after dedupe. Scuff class is a user decision | Finder on 1,008 pool half-cells; human checks the top 100 | 0.2 GPU-h + 5.5 per rung; 11-15 human-h | < 15 real cells in the top 100 |
| 2 | Stop pseudo-label SSL at 20%+ labels | none | 0 | reopen only with a matching pool or a new mechanism |
| 3 | One test of the user's intuition: continued SparK-style MIM of ResNet-34 from ImageNet on ~12.4k cells, fine-tune at 5% | MIM5 vs A5c, 5 v 5 | 1-5 GPU-h + 5.5 | n.d. on all three closes it |
| 4 | Inference-only checks: R34 + R50 ensemble, an SSL member for inactive, BN re-estimation, frame and scale | each scored once | 1-2 GPU-h | no gain ≥ +0.05 on its target |
| 5 | Synthetic branch cracks along scuff streaks, only if item 1 finds too few cells | one 5-seed rung | 5.5-11 GPU-h | scuff-cell recall Δ < +0.05 |

**Judge on the lead's position:**
- "Label propagation is not the user's intuition": holds.
- "Features are not the bottleneck": holds for strict IoU only.
- "Labels beat SSL": holds only with "oracle-selected" attached.

## 9. Thesis contributions so far
1. A tight null for pseudo-label SSL at 20 to 100% labels on EL crack. The old +0.028 traced to one seed on one corrupted cell.
2. SSL's benefit depends on label scarcity and class: at 5%, crack +0.029 and inactive +0.107. Inactive gains last to 20%.
3. Two 2025 SOTA methods adapted to EL, with mechanisms for their failure.
4. The free logit-bias yardstick for SSL crack claims; BsM5 still passes it (+0.037).
5. Test leakage found and handled: 7 twin cells hold 39.5% of test crack.
6. Crack IoU has a labelling ceiling, so capture metrics should judge "catch almost all cracks".
7. "Unseen modules" decomposed into a missing defect context (scuff + half-cut).
8. Labels beat SSL at equal budget for crack (oracle-selected); targeted crack cells beat random.

**Limits:**
- one split;
- 49 clean test cells and 10 E1 inactive cells;
- cv02 only;
- untuned SSL recipes;
- oracle selection in Track D.

## 10. Waiting on the user
- **Scuff:** train it as a class, or keep it as ignore?
- **ELPV:** OK to download (~0.1 GB)? It must be deduped first, since 10 BMRK test cells are ELPV images.
- **Which plan items to run.** Suggested: 4, then 1, with 3 in parallel on idle GPUs.
- **The 40-segment audit,** about 1 h: `team_2026-10-21/skcdf/audit_sheet.csv` with `audit_crops/`.
- **4 label-convention questions:**
  - cracks on inactive edges;
  - faint-crack width;
  - tiny fragments;
  - 236 restored old-mask px in `ARTS_00051_r3_c2`.
  
  The default for all four is to keep them as labelled.
- **Housekeeping:** close the idle cv02 tmux shells and refresh the handbook with Track D, Track M and the 27 Oct results.

## 11. Process and infrastructure
**How the work was run:**
- Every track had an executor and a critic. There was no launch without APPROVED, and no result was reported before the critic's own recompute.
- Rules: matched steps, final-step weights, ≥ 5 seeds, one change per arm, rule 1, cell bootstrap, four cell sets, val-only selection, E1 never used for selection.
- Expected outcomes were written down before the results (H-cm for AL1, "S" for the labelled set).

**Problems caught:**
- the launcher logged rc after `$(date)`, so rc was always 0;
- `--exit-after-step` was used where the flag is `--exit_after_step`;
- an AL1 duplicate lane after an ssh timeout;
- a scorer chdir wrote outputs into `el_sk1/`;
- the crack bias is fragile on the noisy cell.

**Compute and storage:**
- cv02 (8 A6000, shared account, `/tmp` wiped on reboot) trained everything.
- gaint holds the copies in `/home/noob/work/cv02_noob_el/` (`el_trackD`, `el_mt*`, `trackM`), relayed through the laptop with MD5 on both hops.

**Commits:**

| Commit | Content |
|---|---|
| `a4ac59f` | twins lines |
| `16128f7` | rc bug |
| `31daf1f` | team files |
| `f5013b8` | handbook SK1/S-a |
| `e2c9026` | AL1/SK1 results |
| `d4ab115` | handbook AL1 |
| `fffb6d4` | why-discussion |
| `6c50baf` | Track D |
| `b04cad3` | Track M |
| `1a0f41b` | unlabelled team |

## 12. Where things are
| File | Contents |
|---|---|
| `team_2026-10-21/README.md` | team rules, critic gate |
| `team_2026-10-21/data/decision.md` | D1 to D7, twins |
| `team_2026-10-21/alhvr/results.md` | AL1 |
| `team_2026-10-21/skcdf/results.md` | SK1, S-a |
| `team_2026-10-21/skcdf/labelling_plan.md` | audit, label questions |
| `team_2026-10-24_why/SYNTHESIS.md` | why SOTA fails |
| `team_2026-10-24_go/trackD/verify_*.md` | probe, edge, labelled set |
| `team_2026-10-24_go/trackM/results_final.md`, `results_r*.md` | best model, ladder |
| `team_2026-10-27_unlabelled/SYNTHESIS.md`, `lit.md`, `eval.md`, `ideas.md`, `critique.md` | unlabelled-data synthesis and debate |
| `results/trackD_*`, `results/al1`, `results/sk1` | raw outputs |
| `handbook/` | guide for the thesis agent (refresh pending) |
| `SESSION_HANDOFF_2026-10-21.md` | agent IDs and run state |
