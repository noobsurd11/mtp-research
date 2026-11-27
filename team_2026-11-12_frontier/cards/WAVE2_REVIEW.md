# Wave 2 review: 29 proposed arms from families T1 to T5 (critic, 13 Nov 2026)

Read: BRIEF.md (all), PROTOCOL_DRAFT.md sections 0, 3.2, 5, 8, DESIGN.md 1.3 to 1.6 and 2, LEAD_INSTRUCTIONS.md, BUILD_LOG.md, the five spec files in full, parts of the family files, `T1_rcs_precheck.py` (md5 6b4c60d0 confirmed), `T5_precheck/*.out`, handbook 11 and 20 for the Skeleton Recall / clDice / P14 history.
Tags: E = in our files, S = my judgement. No GPU, no server, no sealed data touched. Nothing here is launched.

State when written (E): W1a (house + PF, cv5v2_v11, seeds 5 and 6) is not launched yet. No margin M exists. Every GPU verdict below therefore means "may be built and queued", never "may be judged".

Verdict words: GO; GO after (a named pre-check or gate); FIX (exact fix given, then GO); DROP (reason given; "parked" means it reopens on the stated event).

---

## 1. Twelve cross-arm findings (these matter more than any single arm)

**X1. The margins cannot be estimated from W1a as planned.** Two seeds per arm give one degree of freedom for the seed sd of a pooled out-of-fold metric. Every drop rule in all five specs is written in units of M. Fix: add PF seeds 7, 8, 9 on cv5v2_v11 (15 runs, 16.5 GPU-h, no build) to wave 1. They give a 5-seed sd, they are the extra teachers T2 asks for, and they allow an A/A null: score PF seeds {7, 8} against PF seeds {5, 6} exactly as an arm would be scored (same pooled OOF, same two-stage bootstrap, same three operating points). Proposed rule for the lead: M(metric) = max(0.01, 2 x SE of the A/A contrast). The A/A contrast is printed beside every arm contrast.

**X2. Multiplicity.** 29 arms x 4 headline metrics x 2 to 3 operating points x up to 6 readouts, at 2 seeds. Several false passes are expected by chance. Rules: (a) each arm has one pre-declared primary metric and one primary readout (given in section 2; the other metrics are guards); (b) a screen pass is a promotion to a 5-seed confirmation (seeds 7 to 9 added, 16.5 GPU-h), never a result; (c) the ledger records the number of contrasts read per arm.

**X3. Five teams define the "matched operating point" five ways.** T1: bias that maximises relF1@2 with a relP guard. T2: relR@2 at the baseline's relP@2 plus a cross-fitted bias. T3: bias that matches width. T4: bias that maximises strict IoU. T5: best relF1@2 inside the hysteresis grid. Arms would not be comparable and each team could pick the reading that suits it. Fix: one module `bench/crossfit_op.py`, built once, used by every arm and by the baseline:
- OP-A: argmax (primary, PROTOCOL 5.3).
- OP-F: crack bias cross-fitted on the other 4 folds to maximise relF1@2, refused if relP@2 falls by more than 0.05.
- OP-W: crack bias cross-fitted on the other 4 folds so that the arm's pooled width ratio equals the baseline's.
- Frontier (descriptive): relR@2 at the baseline's relP@2 and the reverse.
A crack gain counts only if it is present at OP-A and at OP-W. A gain at OP-A alone is reported as an operating-point shift.

**X4. Tolerance metrics do not punish width.** A predicted pixel up to 2 px beside the label is "correct" for relP@2, so thickening raises relR@2 for free. Every table therefore carries relF1@1, strict IoU and the width ratio beside relF1@2, and a pass needs the width ratio inside 0.85 to 1.15 x the baseline's, pooled and for each source with 40 or more cells.

**X5. Five arms bet on the same thing: placement jitter in the training labels.** soft_band_jml, matched_crack_head, the two ridge-snap arms, oof_snap. Evidence against a large effect (E): P14's offset-tolerant loss recovered none of the label gap (10% labels, old recipe, so it does not close these arms); the specs' own expected gains are +0.005 to +0.015, at or below any plausible M; symmetric jitter in training labels is averaged out by the model, and the jitter in held-out labels caps strict IoU whatever the training labels are. One free check on the W1a dumps orders the cluster before more than two of them get GPU time:
- **D0, placement diagnostic (CPU, 1.5 h build, reuses `annotation_consistency.py`).** On PF out-of-fold predictions for the 229 crack cells: (a) share of predicted crack skeleton points within 1 px of the darkest point along their normal, where the dip is at least 0.03 (the same measure that gives 0.48 for labels); (b) strict IoU of the prediction against original held-out labels and against snapped held-out labels (T3's P-RS4); (c) mean p_crack as a function of signed distance from the ridge.
- Reading, fixed now: (a) at or above 0.75 means the baseline already sits on the ridge and placement arms can only act through confidence. Then only the merged ridge_snap and soft_band_jml run, and matched_crack_head needs its corrected P-M4 to pass before any build beyond the pre-check. (a) at or below 0.60 means the model follows the jitter or is blurred, and all placement arms keep their priority. In between: the lead decides. D0 orders arms; it closes none.

**X6. Three families each train their own "helper" models.** T3 nested teachers (10 runs on 3 folds), T4 oof_snap helpers (10 runs on 2 folds), T2 cross-fitted teacher fallback. Fix: one shared asset **N0** = T3's `cv5v2n` set (10 PF runs, 11 GPU-h, card unchanged, only new roots), dumped with p_crack, p_inact, m_crack, oth. For screen fold k, a train cell in fold j takes evidence from teacher {k, j}. oof_snap then needs no helpers of its own (saves 11 GPU-h and its helpers see 319 cells, not 213). Launch N0 with wave 1.

**X7. Duplicates.** (a) T3 `ridge_snap_labels` and T4 `ridge_snap` are the same experiment with two scripts and two pass thresholds: merged, section 3. (b) T3 `adele_confident_add` and the F2 part of `oof_selective_ignore` act on the same pixels (confident unlabelled crack components) with opposite treatments, and gate G2 decides which is right: merged. (c) `src_calib` and `dti_hysteresis` are both CPU post-processing on the same dumps against a cross-fitted global bias: one job, two result rows, shared `crossfit_op`.

**X8. Missing controls.** Without them a pass cannot be attributed.
- `jml_hard` (soft_ce_jml with a = 0, no band, no teacher): the comparator for soft_band_jml and for ens_kd_jml, whose hard-label half is CE + JML, not the house loss. 0 build, 11.5 GPU-h. It is also the Jaccard metric loss row of the benchmark suite. The spec's argument that JML on hard labels equals the house Dice is only true up to a gradient factor 2 / (2 - D)^2 that varies from 0.5 to 2 during training (S).
- matched_crack_head with tau_d = 0: run with the arm, not after it, because the head replaces the softmax decision rule for crack.
- encoder_spd: one fold-0 run with lr_mult 1.0, encoder wd 0, lambda 0. Whether full encoder lr without weight decay erases layer3 / layer4 was never run; without it the mechanism gate cannot tell SPD from "no encoder weight decay".

**X9. F51 / H36 are used as pass criteria by T1.** "Beats PF on any headline metric, CV or F51 / H36" is a second lottery ticket on 51 and 36 cells. H36 crack labels are speck-level (BRIEF 2) and must be in no rule. F51 crack was dominated by one cell in the A8 screen (BRIEF 5). Rule: F51 / H36 reads are paired over the 10 fold x seed models and logged in a read ledger; an F51-only pass promotes to confirmation, not to a claim.

**X10. One machine per comparison.** Every arm runs on the machine type that ran its W1a PF comparator (gaint and cv02 differ by up to 0.056 inactive IoU, PROTOCOL 5.4). W1a checkpoints must be kept unslimmed and copied off cv02 `/tmp` (teachers for ens_kd_jml, WiSE readouts).

**X11. The wave is crack-heavy.** 24 of 29 arms target crack. Inactive (data-limited, BRIEF 4.2) is targeted by `rcs` only; the weak classes (gridline, splice, edge_dark) by `rcs` only; the unseen-layout gap by none. This follows from the five family topics, but the lead should know which other family covers problems 2 to 4.

**X12. Build time, not GPU time, is the limit.** All 29 arms as specified: about 128 build hours and about 360 GPU-h. The list in section 4 is about 100 build hours and about 296 GPU-h, with about 53 build hours and 135 GPU-h up to the end of the first tranche.

---

## 2. Verdict table (all 29 arms)

"Fake-gain path" = how the arm could look better without being better. "Primary" = the one metric and readout that decides the screen; everything else is a guard. BRIEF 5 overlap is stated where there is any.

### T1 recipes
| Arm | Verdict | Exact fix or pre-check | Fake-gain path and its guard | Primary |
|---|---|---|---|---|
| rcs | **GO** after the per-fold re-run of the pre-check on v1.1 masks (rule as written: inactive share >= 1.5x, max cell multiplier <= 5, no empty list, else T = 0.1 for all folds) | Add: inactive precision, recall and region precision; per-class IoU for splice, edge_dark, material. State in the card that pairing is broken (new sampler), so an inactive null at 2 seeds closes nothing (about +0.08 to +0.11 needed) | Larger crack and inactive prior (crack share 1.68x). Crack judged at OP-F and OP-W only; inactive by precision beside IoU | mIoU-R13 at OP-A; inactive IoU second |
| ema_wise_posthoc | **GO** (EMA part); WiSE **GO after** P1 and P2 | Keep W1a clean: do not put the averager into the baseline wave. Run the 10 PF runs with averaging on afterwards; their raw weights must equal W1a bit for bit, which is also the first determinism check of the queue. Pre-declare `ema_9998_bn` against `raw_bn` (not against raw). WiSE: one pre-declared readout (encoder a = 0.75), cross-fitted a is secondary; H36 crack out of the rule | BN recalibration alone looking like averaging (guard: `raw_bn` row). Six readouts are six looks | EMA: CV crack relF1@2, `ema_9998_bn` minus `raw_bn`. WiSE: F51 inactive IoU, paired over 10 models, CV within M |
| swad_const | **FIX** then GO | Log encoder cosine to init per stage every 2k steps. A constant lr doubles the integrated encoder lr, so PF's preservation may weaken; without the log the arm confounds averaging with less preservation. If layer3 / layer4 cosine at 20k is below 0.8, say so beside the result. Also dump the raw constant-lr weights | Smoother logits narrow the prediction, raising relP@2. Guard: width, relR@2 | CV crack relF1@2, `swad_bn` minus PF raw; F51 second |
| encoder_spd | **FIX** then GO | Add the fold-0 control of X8 (lr_mult 1.0, wd 0, lambda 0; 1.1 GPU-h) beside the pre-screen. Mechanism gate as written, plus: SPD must differ from the control on layer3 / layer4 cosine by >= 0.1, otherwise the arm is "full encoder lr", not SPD | A freer stem widens cracks toward the house model. Guard: width, crack-free false alarms | CV crack relF1@2 against PF; F51 inactive second |
| modern_recipe | **FIX**, then GO after the norm pre-check | Unstack: the arm is AdamW (decoupled wd 0.01) alone, warmup stays 200. The hypothesis and its CPU check are about coupled L2 only; the 1.5k warmup has no project evidence and is a 0-build follow-up. Make the pre-check a gate: run if the median final / init norm ratio of BN-followed decoder convs in the B6 fold-0 PF checkpoint is <= 0.7; park if above (mechanism absent). State whether BN weights and biases get weight decay (as specified they do) | None specific | CV crack relF1@2 |
| sam | **DROP** (parked) | Weakest prior in the wave (the paper cited gives 85.5 against 85.3), 2x cost, one rho, so a null would close nothing. Its question (does resisting label jitter help) is answered more cheaply by soft_band_jml and swad_const. Reopen if either passes | Narrower predictions raise relP@2 | |

### T2 losses
| Arm | Verdict | Exact fix or pre-check | Fake-gain path and its guard | Primary |
|---|---|---|---|---|
| soft_band_jml | **FIX** then GO after P1 | (1) Run the `jml_hard` control (X8) in the same batch. The band is credited only with soft_band_jml minus jml_hard. (2) P1: exclude cells whose crack mask is identical in the two versions and report their share; unchanged cells give r(d) = 0 and would trip the kill rule by dilution. (3) Drop the claim that band values below 0.5 cannot widen the argmax: in a 24-way softmax crack can win at 0.3 | Band mass moves the crack operating point and can widen. Guard: OP-W, per-source width (BMRK labels are already 3 px) | Strict crack IoU at OP-A and OP-W, against jml_hard and against PF |
| ens_kd_jml | **GO after** gate G5 (needs W1a dumps) | Comparator is `jml_hard`, then PF. Report beside the 2-seed OOF ensemble itself. Screen with 2 teachers (18 GPU-h); 5 teachers only on confirmation | Ensemble predictions are about 13% wider; the student inherits that. Guard: OP-W. Leak guard: the root md5 assert must fail closed | Strict crack IoU; share of the ensemble's own gain recovered |
| clce_crack | **FIX**, run late | Overlap with BRIEF 5 (E, handbook 20 and 11 row 41): the recall term is Skeleton Recall in log form (our label skeleton is the label; the SKR tube covered 99.2% of crack px), the precision term is clDice's predicted-skeleton term, which failed under PF at 100% labels. Only the combination is new. Fixes: (1) state in the card that weight 0.25 with skeleton-mass normalisation is about 130x the house CE weight on crack px; (2) the fold-0 pre-screen is mandatory with a width gate: width ratio above 1.25 x baseline fold 0 means one retry at weight 0.05, then drop; the gate reads width only, never a score; (3) on a pass, run the recall-term-only ablation before any topology claim; (4) read the unscored SKR2C replication first | Recall bought with width (the Skeleton Recall failure). Guard: OP-W, relF1@1 | relR@2 at OP-W |
| scnp_cedice | **FIX** then GO after the jitter-ratio check | The fallback is backwards. The 2021 and revised masks differ only in crack and inactive, so the amplification measured comes from the crack channel; restricting SCNP to channels {14, 15} keeps exactly that part. New fallback, decided before the screen: ratio <= 5 means all 24 channels as specified; ratio > 5 means the this-class (continuity) side only on channel 14, both sides on the other 23 | Lower crack confidence everywhere shows as higher relP@2 at argmax. Guard: OP-F, OP-W | Crack component recall at OP-W |
| cc_dicece_crack | **GO after** the component census | As specified. The multi-class variant stays gated | Sprayed small blobs raise component recall. Guard: component precision, crack-free false-alarm px | Crack component recall with component precision not down by more than M |
| coletra_crack | **FIX**, then GO after the inpaint check | Add a texture test to the pre-check: local high-pass energy inside the inpainted band within 0.7 to 1.3 x that of a 3 to 6 px ring in >= 80% of cells. Telea output is smooth, and a smooth 15 px blob on a line is a cue the model can learn as "crack here". If the texture test fails, add decoy windows (the same blend at an equal number of crack-free line-shaped places) so the artefact predicts nothing | False alarms on dark lines; a shortcut on the inpaint artefact | relR@2 at OP-W; crack-free false alarms as the guard |

### T3 label alignment
| Arm | Verdict | Exact fix or pre-check | Fake-gain path and its guard | Primary |
|---|---|---|---|---|
| matched_crack_head | **FIX**, then GO after P-M4 and D0 | P-M4 as written favours the arm: it redraws the jitter every time a sample is drawn and scores against the clean label. Our data has one fixed jittered label per cell, seen about 376 times, and is scored against jittered labels. Corrected P-M4: a fixed training set of 400 images with one fixed jittered label each, enough steps for about 100 epochs; arms (a) CE + Dice, (b) matched head, (c) P14 tolerant loss, (d) head with tau_d = 0; score against clean and against jittered held-out labels. Pass: (b) minus (d) >= +0.01 relF1@1 or strict IoU against the jittered labels (what CV can see), width 0.8 to 1.2. On the GPU, run the tau_d = 0 control with the arm (12 GPU-h) | The sigmoid head at 0.5 is a new decision rule: any shift in operating point looks like a gain against a softmax baseline. Guard: tau_d = 0 control, OP-W | relF1@1 against the tau_d = 0 control |
| oof_soft_distill | **GO after** the teacher check | Teachers = shared asset N0 (X6). Add inactive precision and recall | Soft targets widen. Guard: OP-W, width <= 1.15 | relR@2 at OP-W |
| ridge_snap_labels | **DROP** (duplicate) | Same experiment as T4 `ridge_snap`. Its stricter kill rule and its P-RS4 check move into the merged arm | | |
| oof_selective_ignore | **FIX**, then GO after N0, the flag-rate check and G2 | (1) F1 (labelled crack with no teacher response) risks removing the faint true cracks we most want. Add to the pre-check: share of F1 px with a visible ridge (relative darkness >= 0.03); if above 30%, F1 is off. (2) F2 (confident unlabelled components) is gated by G2 computed on the N0 teacher dumps: ridge share >= 50% in >= 20 cells means these are real cracks, F2 stays on and the variant `oof_add` (F2 set to crack, not ignore) opens as the offline replacement for ADELE; below 50% they are false alarms and F2 is off | Ignoring hard positives lowers recall on faint cracks while relP@2 rises. Guard: relR@2 on CSIR rows, OP-W | relP@2 with relR@2 not down by more than M |
| adele_confident_add | **DROP** as an online arm (merged into the row above) | Same pixels as F2, 6 build hours for an in-training curve fit, and the model that picks the additions has memorised the training labels. The screen is also biased against it: held-out labels share the gaps it fills, so precision falls by construction. The offline `oof_add` variant asks the same question with leak-free teachers and 0 trainer code | | |

### T4 label refinement and source style
| Arm | Verdict | Exact fix or pre-check | Fake-gain path and its guard | Primary |
|---|---|---|---|---|
| src_calib | **GO after** W1a dumps (CPU) | Primary contrast = src_bias minus glob_bias, both fitted on strict IoU through `crossfit_op`. The per-source branch of the pass rule (one source gains M_src) needs its own bootstrap interval above 0 and is 8 looks (4 sources x 2 variants). Extend the gate for src_film: it opens if src_calib passes, or if a source with >= 40 cells has an argmax width ratio outside 0.85 to 1.15 that the bias does not repair | A per-source bias is an operating-point device that optimises strict IoU directly. Guard: credited against the global bias only; relP@2 and false alarms per source | Strict crack IoU, src_bias minus glob_bias |
| ridge_snap (merged with T3's) | **FIX**, then GO after the merged pair check and D0 | One script: T4's `snap_crack.py` (protected classes, ignore handling, tests). Evidence = `profile` only; sato and myopic are parked, since choosing among three on about a dozen pairs picks noise. One pass rule: median pair IoU gain >= 0.05, at least 70% of pairs rise, tolerant F1@2 not down by more than 0.01, and the one clean double annotation (CFVS_00015 / 16, IoU 0.259) rises; kill if the median gain is under 0.03. Report the share of crack points left unmoved for low dip: faint cracks are exactly the ones the snap does not touch, so the claimed route to faint-crack recall is indirect. Score baseline and arm on both label views | The snapped-label view flatters the arm by design: never a pass criterion. A recall gain with a width rise is a width effect. Guard: OP-W | relR@2 at OP-W against original labels; strict IoU as a guard |
| src_film | **GO after** the src_calib gate (extended as above) | Drop rule as written (against baseline + src_bias). On a pass, one control with shuffled source ids before any claim that the source is what helps | Source-aware operating point. Guard: `own` against baseline + src_bias, `unk` row | Strict crack IoU, `own` minus (baseline + src_bias) |
| oof_snap | **GO after** ridge_snap's screen (wave 3) | Use N0 teachers, not its own half-split helpers (X6): build 4 h, 11 GPU-h | Labels move toward the model's own peak, width can shrink | relR@2 on CSIR against ridge_snap |
| src_cm | **DROP** (parked) | Double-gated (src_calib, then src_film read), 8 build hours, and the latent / noisy split is not identifiable with one label per cell (the spec says so). Reopen only on the spec's own condition after src_film is read | | |
| snap_film | **DROP** from wave 2 (parked) | A stack. It opens only if both singles pass confirmation, on the same machine and seeds | | |

### T5 thin inputs and modules
| Arm | Verdict | Exact fix or pre-check | Fake-gain path and its guard | Primary |
|---|---|---|---|---|
| dti_hysteresis | **GO after** W1a dumps (CPU) | Share `crossfit_op` with src_calib. Width guard relative to the bias comparator at the same point (<= 1.15 x), and relF1@1 and strict IoU printed beside relF1@2: the grid is tuned on relF1@2, which does not punish sideways growth | Growth beside cracks is free under a 2 px tolerance. Guard: width, relF1@1, any-hit against 50%-coverage recall | relF1@2 against the cross-fitted bias point (OP-F) |
| crackcue_input | **GO** (pre-check done) | Restate the hypothesis: the pre-check shows no gain on low-contrast crack px (AUROC 0.708 for the cue and for raw darkness) and a worse score against line classes (0.349 against 0.509). What it shows is a smaller per-source spread. So the deciding table is the per-source crack rows, not faint cracks. A pass on the synthetic probe alone makes a robustness row in the benchmark, not a candidate for the final model | More false alarms on gridlines, busbars, borders. Guard: per-class false positives, line-class IoU | CV crack relF1@2; per-source crack IoU spread second |
| liot_input | **FIX**, run last | The LIOT channels are exactly invariant to gamma and to the probe's contrast0.5 (both monotone; the spec's own unit test (a) proves it), so those two probes cannot decide the arm. Decide on blur1, noise0.02, F51 and the per-source spread only. In-distribution CV is expected flat by the spec itself, so the CV screen alone is uninformative | A probe that favours the arm by construction | Mean relF1@2 drop under blur1 and noise0.02 against the baseline's |
| thin_geometry_aux | **GO** (pre-check done) | As specified (weights from the 500-step smoke on fold-0 train stems, written into the card before the screen). Decomposition only on a pass | A too-strong FIDT term makes a halo and widens. Guard: width, mIoU-R13 | Crack component recall at OP-W |
| fullres_detail_head | **GO after** the grid-snap gate (W1a dumps) | As specified. BRIEF 5 holds a near neighbour (2x input, n.d.) and the spec's own oracle says resolution is not shown to bind, so a failed gate parks it without a run | Narrower lines matching one source's convention. Guard: per-source width, relR@2 | Strict crack IoU |
| super_decoder_x03 | **DROP** (parked) | 8 build hours from a paper with no code and no crack ablation, placement chosen by us; "a null closes only this placement" (spec). Reopen only if fullres_detail_head passes | | |

Count: 12 GO or GO-after (one of them, oof_snap, in wave 3), 11 FIX (all runnable once fixed), 6 DROP (2 merged into other arms, 4 parked).

---

## 3. Merges and what must run alone

**Merged**
1. `ridge_snap` = T4 arm 2 + T3 arm 3. One script, one pre-check, one screen (saves 11 GPU-h, 4 build hours).
2. `oof_selective_ignore` absorbs `adele_confident_add` as the gated variant `oof_add` (saves 6 build hours; 13.5 GPU-h becomes 11 only if the variant opens).
3. `N0` nested teachers serve oof_soft_distill, oof_selective_ignore, oof_snap and the ens_kd_jml fallback (saves 11 GPU-h).
4. `src_calib` + `dti_hysteresis` + D0 + the gates G5, G2 and grid-snap: one CPU job on the W1a dumps with `crossfit_op`.
5. Shared code, built once and first: `weight_avg.py` (ema, wise, swad), the aux-target hook (soft_band_jml, clce, cc_dicece, geometry aux; T2's and T5's dataset wrappers must be the same class), the cue wrapper (crackcue, liot), `bench_make_roots.py --train-masks` (ridge_snap, selective ignore, oof_snap).

**Must run alone (no stacking until each has passed confirmation):** rcs (changes the class prior), encoder_spd, swad_const, soft_band_jml with its control, matched_crack_head with its control, src_film, crackcue_input, ridge_snap. Stacks (snap_film, T2's "A1 + A3", the final recipe) come only after the singles.

**Kept separate on purpose:** ens_kd_jml (in-sample ensemble teacher, online) and oof_soft_distill (out-of-fold single teacher, offline) test different things; read them as a pair.

---

## 4. Ordered wave-2 list

Order = information per GPU-hour and per build hour: CPU jobs that decide several arms first, then arms with no new trainer code, then shared infrastructure, then gated arms.

### Stage 0: add to wave 1 (not arms)
| Item | Runs | GPU-h | Build h | Why |
|---|---|---|---|---|
| B+ : PF seeds 7, 8, 9 on cv5v2_v11 | 15 | 16.5 | 0 | margins, A/A null, extra teachers (X1) |
| N0 : nested teachers `cv5v2n`, PF, seed 5 | 10 | 11 | 1 | shared helper models (X6); also a 60%-data baseline point |

### Stage 1: CPU only
Now, no W1a needed (about 8 h compute, mostly written by the family analysts): merged ridge-snap pair check; T2 P1 (with the fix); corrected P-M1 to P-M4; SCNP jitter ratio; component census; inpaint contrast + texture check; RCS per fold on v1.1; decoder norm ratio and EMA / WiSE P1, P2 on the B6 fold-0 checkpoints.

When the W1a dumps exist (0 GPU-h):
| # | Item | Build h | Decides |
|---|---|---|---|
| 1 | `crossfit_op` module | 2 | every arm's operating points |
| 2 | src_calib | 4 | src_film (and later src_cm) |
| 3 | dti_hysteresis | 3 | itself; iternet follow-up |
| 4 | D0 placement diagnostic (+ P-RS4) | 1.5 | order of the 5 placement arms |
| 5 | gates G5, G2 (on N0 dumps), grid-snap | 2 | ens_kd_jml, oof_add / F2, fullres_detail_head |

### Stage 2a: first GPU tranche (queue as built; judged only when M exists)
| # | Arm | GPU-h | Build h | Waits for |
|---|---|---|---|---|
| 1 | rcs | 12.1 | 3 | per-fold pre-check |
| 2 | ema_wise_posthoc (EMA re-run + readouts; WiSE readouts) | 12 | 4.5 | W1a done (bit-identity check); P1, P2 for WiSE |
| 3 | soft_band_jml | 11.5 | 8 (4 shared hook + 4) | P1 |
| 4 | jml_hard control | 11.5 | 0 | none |
| 5 | ridge_snap (merged) | 12.1 | 8 | pair check |
| 6 | crackcue_input (+ perturbation probe) | 11 | 6 | none |
| 7 | swad_const | 12.1 | 1 | weight_avg built |
| 8 | oof_soft_distill (students) | 11 | 6 | N0 teacher check |
| 9 | encoder_spd (+ fold-0 control) | 14.3 | 3 | unit tests, mechanism gate |
| | **Tranche total** | **107.6** | **39.5** | |

With stage 0 and the CPU builds: about 135 GPU-h and 53 build hours. On 7 free A6000s that is under one day of wall time.

### Stage 2b: second tranche (gated or lower prior)
| # | Arm | GPU-h | Build h | Waits for |
|---|---|---|---|---|
| 10 | matched_crack_head + tau_d = 0 control | 25 | 8 | corrected P-M4, D0 |
| 11 | ens_kd_jml (2 teachers) | 18 | 5 | G5 |
| 12 | src_film | 12.1 | 6 | src_calib gate |
| 13 | cc_dicece_crack | 12 | 4 | census |
| 14 | scnp_cedice | 12.5 | 2 | ratio check, corrected fallback |
| 15 | thin_geometry_aux | 11.5 | 8 | none |
| 16 | oof_selective_ignore (+ `oof_add` if G2 opens it: +11) | 11 | 3 | N0, flag-rate + ridge check, G2 |
| 17 | modern_recipe (AdamW only) | 11 | 0.5 | norm-ratio gate |
| 18 | coletra_crack | 11 | 4 | inpaint + texture check |
| 19 | clce_crack | 13.2 | 2 | SKR2C read, fold-0 width gate |
| 20 | liot_input | 11 | 1.5 | crackcue wrapper |
| 21 | fullres_detail_head | 12.5 | 4 | grid-snap gate |
| | **Tranche total** | **160.8** | **48** | |

Wave 2 in all: about 296 GPU-h, about 100 build hours. Each screen pass adds a confirmation of 16.5 GPU-h (seeds 7 to 9).

### Not in wave 2
oof_snap (after ridge_snap's screen; 11 GPU-h, 4 h), snap_film, src_cm, super_decoder_x03, sam, online ADELE, T3's ridge_snap_labels (merged). Saved against the specs: about 95 GPU-h and 34 build hours.

### Which arms depend on the baseline wave
- **Verdict needs M from W1a + B+:** every GPU arm.
- **Cannot start before the W1a dumps:** src_calib, dti_hysteresis, D0, G5 (ens_kd_jml), grid-snap gate (fullres_detail_head), EMA bit-identity check.
- **Cannot start before the W1a checkpoints:** ens_kd_jml (teachers), WiSE readouts.
- **Need N0, not W1a:** oof_soft_distill, oof_selective_ignore (and G2), oof_snap.
- **Can be built and pre-checked today:** rcs, soft_band_jml, jml_hard, ridge_snap, crackcue_input, liot_input, thin_geometry_aux, swad_const, encoder_spd, matched_crack_head (P-M4), scnp, cc_dicece, coletra, modern_recipe (norm check).

---

## 5. Guards every arm must report (one table format for all, written by the frozen scorer)

1. **Three operating points** from `crossfit_op`: OP-A, OP-F, OP-W, plus the frontier read. Arm and baseline both.
2. **Predicted width ratio** (predicted / ground-truth crack px), pooled and per source, and mean predicted width (px per skeleton px). Pass band 0.85 to 1.15 x baseline.
3. **relP@2 beside relR@2**, never one alone; **relF1@1** and **strict IoU** beside relF1@2.
4. **False alarms on the 303 crack-free cells:** predicted crack px, and the share of crack-free cells with 50 or more predicted crack px.
5. **Component precision beside component recall;** any-hit recall beside 50%-coverage recall.
6. **Inactive precision, recall and region precision** beside inactive IoU; the per-class IoU of the 13 robust classes beside mIoU-R13.
7. **Per-source table** (ARTS, BMRK, CFVS, CSIR; SDLE descriptive, 17 cells) for crack IoU, relF1@2, width, false alarms.
8. **The A/A null contrast** beside every arm contrast, and the bootstrap interval (330 groups, then seeds).
9. **Step time and peak memory** from the 1,000-step smoke; arm and baseline on the same machine type, same commit, canonical fp32 dumps.
10. **Identity:** flag-off 5-step CPU identity IDENTICAL for the house and PF cards after every merge; the batch stream unchanged unless the arm says it changes sampling (rcs, coletra).
11. **Leak asserts that fail closed:** teachers and helpers never trained on the student's held-out fold; refined or per-fold masks linked for training stems only; held-out masks always v1.1 strict.
12. **Ledger line:** pre-declared primary, number of contrasts read, F51 / H36 reads.

A result that lacks any of 1 to 8 is not read.

---

## 6. Open questions for the lead

1. **B+ (PF seeds 7 to 9, 16.5 GPU-h) in wave 1?** Without it there is no usable margin. My answer: yes.
2. **Margin rule.** Accept M = max(0.01, 2 x SE of the A/A contrast) per metric, with promotion to a 5-seed confirmation on a pass?
3. **EMA in W1a or after?** The averager is trajectory-neutral by test, but it is new code in the baseline wave. My answer: keep W1a clean; the later re-run doubles as the bit-identity check.
4. **Which machine runs W1a PF?** All wave-2 arms must follow it. If cv02: who copies the 10 (+15) checkpoints off `/tmp` before a reboot wipes the teachers?
5. **W1a dump keys.** src_calib, dti, D0 and the gates need `pred`, `oth`, `m_crack`, `p_crack`, `p_inact` for house and PF; G5 needs the 2-seed mean softmax (either `logp`, about 13 GB, or a re-inference job). Confirm before launch.
6. **N0 with wave 1?** It is the PF card on new roots (11 GPU-h) and unlocks three arms.
7. **Source-aware entries** (src_calib, src_film): does the benchmark allow the source id at test time in the main table, or only in a labelled side table? This decides how much those arms are worth.
8. **Snapped labels as a second scoring view.** If the pair check passes (two drawings of one crack agree more after snapping), the snapped view is a lower-noise instrument for every method. Does the benchmark adopt it as a secondary label view?
9. **Coverage.** Only rcs addresses inactive and the weak classes, and nothing here addresses the unseen-layout gap. Which family or wave owns problems 2, 3 and 4?
10. **SKR2C** (Skeleton Recall w 0.1 replication) is trained and unscored. clce_crack should not run before it is read.
11. **Perturbation probe:** T5 only, or a robustness track for every arm (about 5 GPU-min per run per perturbation)?
12. **Build capacity.** About 100 build hours for the GO list under a tight usage cap. Who builds, and is the order in section 4 (CPU jobs, then shared code, then tranche 2a) accepted?
13. **F51 / H36 read ledger.** About 20 arms will read them. Accept the rule in X9 (paired over the 10 models, H36 crack in no rule, F51-only pass = promotion only)?
