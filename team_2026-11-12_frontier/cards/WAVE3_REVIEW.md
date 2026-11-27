# Wave 3 review: 47 proposed items from families T6 to T13 (critic, 14 Nov 2026)

Read: BRIEF.md (all), PROTOCOL_DRAFT.md sections 0, 3, 5, 8, DESIGN.md 1.3 to 1.6 and 2, LEAD_INSTRUCTIONS.md, WAVE2_REVIEW.md (in force), the eight spec files in full, `log.md`, the tail of `BUILD_LOG.md`, `harness/el_bench_src` (to check that `bench_smp` and `bench_timm` exist: they do), `cards/T8_precheck/c_phys.out` and `escdd_synth.out`, and `benchmark/cells.tsv` (my own counts below are from it).
Tags: E = in our files, R = from a paper as quoted by a spec, S = my judgement. No GPU, no server, no sealed data touched. Nothing here is launched.

State when written (E, log.md): W1-G trained (10 PF runs, gaint), W1-G2 (PF seeds 7, 8, gaint) queued behind it, W1-C on cv02 28 of 45 started. Wave 2a (6 arms + CPU tools) merged at bench_w2, queue written, not armed. No margin M exists yet. Every GPU verdict means "may be built and queued", never "may be judged".

Verdict words: GO; GO after (a named pre-check or gate); FIX (exact fix given, then GO); DROP (reason given; "parked" means it reopens on the stated event).

---

## 1. Fourteen cross-arm findings

**Y1. Inactive cannot be screened by training runs, and more seeds will not fix it.** Six trained arms take inactive IoU on CV as primary (ucf_partial_joint, the two paste arms, layered_ci, vfm_ctx_r34_pf, fm_align_pool). Each expects +0.00 to +0.05. The measured SE of an inactive contrast at 2 seeds is 0.038 (E, PROTOCOL 3.2), split as groups 0.031 and seeds about 0.022. The group part does not shrink with seeds: at 5 seeds the SE is still about 0.034 (S, from those two numbers), so M stays near 0.07. T6 and T8 ask for 3 or 5 seeds; that buys almost nothing. Rules:
- No inactive arm gets extra seeds until `aa_calibration` part (e) has fitted V(k) = a + b/k for inactive IoU. If 2 x sqrt(a) is above 0.05, pooled inactive IoU is never a screen primary for a trained arm.
- Trained inactive arms then promote on count-based readouts with large n, all pre-declared: inactive region recall (regions >= 100 px), predicted inactive px on the 484 inactive-free cells, inactive precision, and delta inactive IoU > 0 (direction only). Read against baseline + the cross-fitted inactive bias (Y6).
- At most one trained inactive arm is built in the next 10 days, chosen by the atlas (Y4). Post-hoc arms come first because they are paired on the same predictions.
- F51 has 4 inactive cells and H36 has 3 (E, my count from cells.tsv). "F51 inactive IoU, paired over 10 models" appears as a promotion look in T6 arms 1 and 2, T8 arm 1 and T10's transfer check. With 4 cells it can only be a non-inferiority guard. It is in no promotion rule.

**Y2. No development read can see the stratum that holds 75% of E1 crack pixels, and the retrodiction check as written would select for width.** T7 says this plainly and builds a panel of five proxies. Three problems remain.
- R0 cannot test U1 (LOSO-2), because no old checkpoint was trained leave-source-out. U1 is the primary of gin_ipa, the top unseen-module GPU arm, and the base of t3b_fewshot_rule.
- R0's two "crack movers" are weak anchors: SKR w1.0 moved E1 with wider predictions (BRIEF 5), and SKR2 w0.1 is a narrow pass whose replication (SKR2C) is trained and not yet opened. A rule that keeps the proxies on which SKR looks good keeps the proxies that reward width.
- R0's old checkpoints are read on SHV1 (54 val cells, 23 with crack). Five contrasts on 54 cells is a sign test with almost no power.
Fixes: (a) every R0 contrast is read at the frontier (relR@2 at the baseline's relP@2) with the width ratio beside it and a bootstrap interval; an interval that includes 0 is "no information", not a pass. (b) SKR2C is opened first (the user already agreed); if it does not replicate, R0 has no confirmed crack mover and only the inactive contrast and the HC null remain. (c) Add `skr01_pf_v11` as an anchor arm: the SKR w0.1 card already exists in el_bench as an identity arm (E, BUILD_LOG), so it is config only. Run it on LOSO-2 (4 runs, 4.4 GPU-h) and on cv5v2 (10 runs, 11 GPU-h). It is the only mechanism with E1 evidence and nobody carried it into the new harness. If skr01 minus PF is not positive on U1 at the frontier, U1 is a guard, not a primary. (d) R0 is allowed (my answer to T7's question): it reads no new E1 number and selects no model. Log one line in `e1_openings.md` saying published contrasts were used to choose instruments.

**Y3. Problem tags do not match the instruments.** hiera_bp_unetpp_pf and hiera_bp_adapter_frozen are tagged unseen_modules with a CV mIoU-R13 primary. vfm_ctx_r34_pf and ucf_partial_joint claim transfer but are read on CV inactive. ad_prior's "main hope" is unseen layouts and its primary is CV crack. For these arms a CV null does not test the claim and a CV pass does not show it. Rule: the card states the claim the primary can test (in-distribution), and the transfer claim is listed as "untested until the E1 opening". Each such arm pre-declares U2, U5 and H36 false alarms as secondary reads once U-dev exists.

**Y4. Four teams wrote the same inactive error anatomy with different thresholds.** T10 A0 (missed = coverage < 10%), T6 `inactive_anatomy.py` (< 20%), T8 C3 (< 50%) and C-BMRK, T13's gate (reads A0). Build one: T10's atlas. It writes per-region coverage, so every gate is evaluated at its own stated threshold from one output. Two additions: every gate share carries a group-bootstrap interval and a leave-top-3-groups-out value (3 groups hold 39% of P532 inactive px, effective n 13.2, E), and shares are reported by region count as well as by pixel. A gate opens only if it also holds without the top 3 groups; otherwise the lead decides.

**Y5. Duplicates.**
- T8 `inactive_grid_paste` and T10 `inact_paste` are one experiment (real inactive regions with their bounding crack, same source and cell type, same position). Merged, section 3.
- T11 `suite_hetero_ens` and T6 readout 1b (PF + Hiera against PF + PF) are one readout. T12 `bench_ens_dump.py`, T9 P1(a) and T2 gate G5(b) are one computation. Build the derived-dump tool once.
- T8 C0 (NCC duplicate search of UCF against our sets), T12 `leakage_audit_v02` (embedding search) and T9's `pool_t9.txt` exclusions are one job with one output family of exclusion lists.
- T12 item 6 "isolation risk" repeats T8's E4 rule. E (`c_phys.out`): the isolation rule from GT cracks fires on 38 of 48 inactive cells and on 18 of 180 crack-only cells, pixel recall 0.274, precision 0.575. Reuse that script; do not rebuild it.
- T11 row 1 and the harness "W1c DeepLabV3+" pathfinder are the same card. W1c was never launched (E, LEAD_INSTRUCTIONS update 09:30), so T11 owns it.

**Y6. Prior shift is the inactive and weak-class version of width.** rcs, la_ce, the paste arm, ucf_partial_joint and Pratt's weighted CE all raise how often a rare class is predicted. A decision bias does the same for free. I accept T10's proposal and make it a rule: `classbias_xfit` defines operating point **OP-C** (argmax plus cross-fitted per-class biases, crack bias excluded). A gain in inactive IoU or mIoU-R13 from a prior-shifting arm counts only if it is present at OP-A and against baseline at OP-C, exactly as crack gains must hold at OP-W.

**Y7. Three teams add a second data stream to the trainer in three ways.** T8: concatenated forward, B = 8 + 2, stream id 7. T7 mic: concatenated forward, B = 8 + 4 + 4, Mean Teacher path. T9: two separate forwards with BN running statistics frozen on the pool forward, stream id 7. Build one "second stream" block: a second `BatchStream` with a registered stream id (7 = external labelled, 8 = pool), a loss hook, a GPU augmentation hook seeded by (seed, stream, step), and a `bn` option {joint, separate_frozen_running} that each card must state. Every second-stream arm also reports an `arm_bn` row (BN statistics recalibrated on the fold's BenchmarkEL train images only, using wave 2a's `weight_avg` recalibration). If arm and `arm_bn` differ by more than M, the effect is BN contamination, not learning.

**Y8. The W1-G dumps are about to be read by fifteen analyses.** Atlas, class biases, rules, SAM refiner, metric probes, head ceiling, stacking, ensembles. Fixed parameters and cross-fitting control most of the risk. Add one rule: W1-G (gaint, seeds 5 and 6) is the exploration set; any post-hoc or CPU result is called a result only after the same script, unchanged, reproduces it on the W1-C1 dumps (cv02, seeds 5 to 9). The number of variants read per tool goes into the ledger.

**Y9. Expected gains below M make several nulls uninformative by the specs' own numbers.**
- pool_ens_distill expects +0.000 to +0.012 strict crack IoU; its gate P1 opens at a teacher edge of +0.005; M is at least 0.01. A student cannot beat its teacher's edge, so at an edge under M the arm cannot pass and a null closes nothing. Fix in section 2.
- gin_ipa expects +0.01 to +0.04 on U1. LOSO-CSIR crack pixels are concentrated: the top 3 module groups hold 53%, effective n 8.3 (E, my count). M_U1 will be large (S: 0.03 or more).
- hiera expects +0.005 to +0.02 mIoU-R13; vfm_ctx expects 0 to +0.03 inactive against M near 0.08.
Rule: before a GPU arm is built, its spec's expected range is compared with the measured M for its primary (from `aa_calibration`, per machine). If the top of the range is below M, the arm needs a better instrument (paired readout, more groups) or it waits.

**Y10. BRIEF 5 overlaps that the specs under-state.**
- mic_halfcell: the closed Mean Teacher run used the 11.9k pool, which contains the 1,152 half-cells, with an EMA teacher and confident hard labels, and was n.d. on unseen modules. New here are only masking, the half-cell-only target and the joint BN. It is a partial repeat.
- gin_ipa: the photometric half of its hypothesis (histogram shape) is partly contradicted by the failed inference-time intensity normalisation and per-panel BN adaptation. The spatial blending (IPA) half is untested.
- msc_tta: bounded by HC (n.d. on E1) and by the 2x input null.
- ucf_partial_joint: not the same as the closed UCF pretraining. But "+107 E-SCDD cells: n.d." is evidence against "more labelled cells fix inactive" under the house fine-tune, and P037 itself reports only +0.5 Dice on the fully labelled set's own classes (R, T8 spec).
- pool_ens_distill: differs from the closed pool SSL in teacher, targets and perturbation. Not closed.
None of these is a reason to void an arm. Each lowers the prior and is used in section 5.

**Y11. The benchmark needs the published EL baselines more than a third scratch crack network.** PROTOCOL 8 says credibility rests on re-running the published baselines under the protocol. T11 ranks Fioresi's DeepLabv3-R50 and Hanifi's VGG16-UNet at priority 45, below a 6-hour Mamba port. Each costs 0.2 to 0.3 build hours. Reorder: all rows from EL papers (Pratt architecture, Pratt recipe, U-Net, Fioresi, Hanifi, EL SegFormer) go into tranche 1. One crack specialist (RIFT) and one Mamba row (SCSegamba, if its gate passes) follow. MixerCSeg, Hybrid-Segmentor and HrSegNet are dropped (11 to 14.5 build hours for rows that answer no new question).

**Y12. Fairness for new architectures and for arms that cost more per step.** gin_ipa runs 16 forwards per step, mic 16, pool distillation 16, UCF 10, Hiera-B+ about 2.4x step time with 3.3x the encoder parameters. Scratch rows use the house recipe, which nobody tuned for them. Guards in section 6 (G16): every row prints parameters, GFLOPs, step time, images per step, pretraining data and recipe source; any candidate above 2x house training or inference cost is also compared with the PF 2-seed ensemble (equal cost); scratch rows are labelled "pretraining: none, house recipe" and a loss against PF is not a claim about the architecture.

**Y13. Headline metric and tolerance must not move under the arms.** T12 items 2 and 4 can change the first column (to centreline F1@2) and the tolerance (to 3 px). Both rules are fixed before numbers, which is right. Two limits: (a) arms whose primary is already pre-declared (all of wave 2, and this wave) keep it; the new headline applies to the benchmark table and to arms specified after the change. (b) A wider tolerance punishes width even less, so the tolerance moves only on strong evidence (fix in section 2), and relF1@1, @2, @3 and the width ratio are always printed together. Centreline F1 is blind to width by construction, so the width band stays a pass condition whatever leads the table.

**Y14. Build time is still the limit, and gaint is now a second one.** The 47 items as specified: about 199 build hours and about 550 GPU-h. Wave 2 still holds about 70 unbuilt build hours and about 230 GPU-h. gaint ran W1-G at about 1.1 GPU-h of work per wall hour (E: 10 runs in about 9.7 h), so 10 days give about 260 GPU-h there, and the w2a queue alone takes 67. The plan in section 4 is about 100 new build hours (35 of them behind gates) and about 390 GPU-h.

---

## 2. Verdict table (all 47 items)

"Null?" = would a null be informative with the stated instrument. "Fake-gain path" = how it could look better without being better. BRIEF 5 overlap is in Y10 unless stated.

### T7 unseen modules
| Item | Verdict | Exact fix or pre-check | Null? and fake-gain path | Primary |
|---|---|---|---|---|
| udev_instrument | **GO** (U2, U4, U5 sets, LOSO-2 roots); R0 **FIX** | R0 as in Y2: frontier read with width and interval, SKR2C opened first, skr01 anchor on LOSO-2 and cv5v2, a ledger line. Print effective n for each read (LOSO-CSIR crack 8.3). Mark U2 as "gamed" for every arm that trains or tests with scale changes: msc_tta, pool_ens_distill (affine 0.8 to 1.25), nnU-Net rows (scaling 0.7 to 1.4). U4 pool part is label-free: only the H36 crack-free cells count as false alarms | Not an arm. Risk: a proxy passes R0 by rewarding width | none |
| gin_ipa | **FIX**, then GO after P-GIN and the U1 anchor | (1) Read the GIN repo for the conv bias and the LeakyReLU slope before build (the spec flags both as unverified). (2) Add P-GIN (d), 0.5 h on the atlas output: PF OOF crack relR@2 in the top decile of histogram shape against the rest, per source. If there is no deficit, the photometric half has no support here; say so before the screen. (3) Stage A decides at 2 seeds only if M_U1 <= 0.03; otherwise add arm seeds 7 and 8 (8.8 GPU-h) before any verdict. (4) State 16 forwards per step in the card. On a pass, run two controls before attribution: KL between two house-augmented views without GIN (same cost), and GIN without IPA | Null at 2 seeds is weak (Y9). Fake gain: KL softens predictions, relP@2 rises at argmax (frontier read guards it); LOSO measures a source shift, not layout or scuff | U1 crack relF1@2 at OP-A, frontier same sign |
| mic_halfcell | **FIX**, build waits | (1) State the overlap with the closed pool Mean Teacher run (Y10). (2) Add a blindness census to G-MIC, on U2 where labels exist: share of GT crack px on the synthetic half-cut views that the teacher labels confident non-crack (max prob >= 0.968). Variant B protects only px with p_crack >= 0.01, and 70% of E1 crack px get p < 0.001 (BRIEF 3). If the share is above 50%, self-training teaches background on the cracks we want: park. (3) U2 has train texture, so it cannot see adaptation to real half-cell texture. New primary: predicted crack px on the 19 H36 crack-free cells, paired over models, with U2 relR@2 at matched precision not down by more than M. The arm is a half-cell precision arm; say so. (4) Use the shared second-stream block; report `arm_bn`. (5) Pool list = `pool_t9.txt` half-cell subset. Only the G-MIC census (1 h) is built in the next 10 days | Null on U2 uninformative as specified. Fake gain: suppression of all crack on half-cells looks like fewer false alarms | H36 crack-free false alarms (after fix) |
| msc_tta | **FIX**, then GO as a benchmark row | The U2 primary is circular (the 0.75 view inverts the simulator's 1.34 scale). U2 is printed as an upper bound and cannot promote. Score claim = CV5 crack relF1@2 and strict IoU not worse than -M at OP-A and OP-W, H36 and pool half-cell crack px <= 1.5x, F51 crack paired. Print 24 views beside D4 (8 views) and beside a 3-seed D4 ensemble (equal cost). `bench/tta.py` is shared with T9's labelling job | Fake gain: averaging 24 maps widens thin cracks; OP-W and width band decide | CV5 non-inferiority; table row |

### T6 foundation backbones
| Item | Verdict | Exact fix or pre-check | Null? and fake-gain path | Primary |
|---|---|---|---|---|
| hiera_bp_unetpp_pf | **FIX**, then GO | (1) Y3: the card claims in-distribution mIoU-R13; transfer is "untested". Secondary reads U2, U5, H36 false alarms. F51 crack is a promotion look; F51 inactive (4 cells) is a guard only. (2) Wrapper control at equal seeds: the HR-stem ConvNeXt-T IN-1k card runs seeds 5 and 6 on cv02 with it (about 15 GPU-h, S). (3) Equal-cost comparator: PF 2-seed ensemble printed beside it. (4) One encoder lr is tried; a retry is allowed only on the mechanism log (stage cos-to-init), never on a score. (5) Readout 1b moves into the merged hetero-ensemble readout | Null at 2 seeds closes only Hiera-B+ at this lr. Fake gain: wider cracks from the stride-4 first stage; a win from the HR stem, not the backbone | mIoU-R13 at OP-A |
| vfm_ctx_r34_pf | **GO after** two gates | Gate 1: the atlas shares, as the spec says. Gate 2 (new, 3 build h, about 0.5 GPU-h): a late-fusion test. Extract frozen DINOv2 ViT-L tokens (448 px, blocks 12, 18, 24) for the 532 cells; per fold, fit a logistic model on the other four folds from [PF p_inact logit, 1x1-projected tokens] to GT inactive; write the stacked inactive margin into a copy of the PF dump; score paired. Pass: stacked minus PF inactive IoU >= +0.01 with interval above 0, or a region classifier on PF false regions and missed regions reaches AUROC >= 0.75. P497 (probes do not predict fine-tuning) does not apply, because the branch stays frozen in the arm. Fail = park | CV null uninformative at M near 0.08 (Y1). Fake gain: inactive prior shift (OP-C) | inactive count-based readouts (Y1) |
| nnunet_resenc_2d | **FIX**, GO as a row in week 2 | (1) Predict from `checkpoint_final.pth` only; nnU-Net also saves a best-validation checkpoint chosen on the held-out fold, which PROTOCOL 5.3 forbids. (2) N1 (160k images) is far below the budget nnU-Net is designed for from scratch; label it "step-matched, under its design budget". The citable row is N2 native, 1 seed x 5 folds, when cv02 is idle. (3) Record the planner's patch and batch size and the installed version; test torch 2.14 compatibility in the venv before any export work | Row is reported whatever it scores. Fake gain: its scaling augmentation moves U2 (gamed); foreground oversampling shifts the operating point | crack relF1@2 at OP-A |
| hiera_bp_adapter_frozen | **GO after** its gate; outside the 10 days | Gate as written. If arm 1 fails with cos < 0.95 it still runs once (a null on arm 1 does not close frozen + adapters, BRIEF rule 9), but only after the suite rows | as arm 1 | mIoU-R13; arm 4 minus arm 1 |

### T8 more data
| Item | Verdict | Exact fix or pre-check | Null? and fake-gain path | Primary |
|---|---|---|---|---|
| ucf_partial_joint | **FIX**, then GO after gates | (1) Build in two steps. Step A (3 h, CPU): converter and tests; C0 runs inside the shared duplicate tool. Then a zero-shot read C4 (1 h): PF fold models on 200 UCF images rendered in our geometry: region recall on kept inactive regions and PF inactive px on NEG px. Reading fixed now: recall >= 0.9 with NEG false alarms at our crack-free rate means UCF adds easy examples; expect a null and let the lead decide before step B. (2) Step B (6.5 h: second-stream block, partial CE, card) only if the atlas shows missed or false regions >= 30% of inactive error and C4 does not predict a null. (3) First screen with `ext.ucf.crack_positive=false`. The arm otherwise changes three things at once (inactive positives, crack skeletons from polygons, NEG background) and its primary is inactive. (4) `bn: joint` stated, `arm_bn` row reported. (5) Promotion by the Y1 rule; read at OP-C. (6) Licence line in the card; user question U1 | CV null at 2 seeds closes nothing under about 0.07. Fake gain: inactive prior shift; BN contamination; convention leak (busbars inside UCF polygons) | inactive count-based readouts (Y1) |
| inactive_grid_paste | **DROP** (merged) | Same experiment as T10 `inact_paste`. Its C-REAL held-out test and its multiplicative rendering move into the merged arm | | |
| elpv_bmrk_negatives | **DROP** (parked) | ELPV has no module ids and BMRK cells are ELPV cells. Defect-free siblings of held-out BMRK cells would enter training in every CV fold, and that leak acts exactly on the arm's own primary (BMRK relP@2: fewer false alarms on a module whose background was seen). It cannot be excluded or measured. 50 cells, effective n 16, CC BY-NC-SA. Reopen only if ELPV module membership can be recovered and validated | | |
| pvddpm_fold_synth | **DROP** (parked) | 12 build hours and about 70 GPU-h on a repo with no licence shown and no segmentation evidence, to render what the paste arm transplants. Its leak analysis is kept as guard G14. Reopen only if the merged paste arm passes confirmation | | |

### T10 inactive and weak classes
| Item | Verdict | Exact fix or pre-check | Null? and fake-gain path | Primary |
|---|---|---|---|---|
| ci_error_atlas | **GO** now | Y4: one atlas for T6, T8 and T13; intervals, leave-top-3-out and region counts on every gate; thresholds stay as written by each team. Add P-GIN (d). Label list published only if the positive control passes, as specified | Not an arm | none |
| ci_rules_posthoc | **GO after** atlas part (d) | (1) Y8: confirm on W1-C1. (2) Rule a deletes inactive that has no predicted crack nearby. On unseen half-cuts crack recall is 0.17, and PF's E1 inactive gain (0.05 to 0.24) is the one unseen-module win we have. Before rule a enters any model: apply it on U2 (synthetic half-cuts, labels exist) and report inactive IoU with and without. Any E1 read reports both. (3) Enters the benchmark as a decision-layer entry (question L3) | Paired, so a null is informative at the 0.01 floor. Fake gain: none on crack (asserted); rule b raises inactive area (precision guard) | inactive IoU, rule minus no rule |
| classbias_xfit | **GO** | Becomes OP-C (Y6). Report the fold-to-fold spread of each bias as specified. Confirm on W1-C1 | Paired; informative. It is an operating-point device and is credited only as one | mIoU-R13 at OP-C minus OP-A |
| layered_ci | **FIX**, then GO after G-layer | (1) The within-model contrast (layered decision against the same model's argmax) is biased toward the arm: the auxiliary loss can make the softmax inactive worse and the layer then "wins". It is mechanism evidence only. (2) Comparator for promotion = PF with the best post-hoc inactive layer (rule b, OP-C inactive bias), by the Y1 rule. (3) The union proxy on existing dumps becomes part of the gate: if neither O1 + O5 >= +0.04 nor the proxy is positive with interval above 0, park. (4) Build the auxiliary head and decision module once, shared with wave 2's matched_crack_head | Between-model null uninformative (Y1). Fake gain: a sigmoid at 0.5 predicts more area | inactive count-based readouts against PF + post-hoc |
| inact_paste (merged with T8's) | **GO after** G-paste and the merged pre-check | One transform, T10 owns it. Keep T10's decoys (equal rate) and seam test, and T8's C-REAL (held-out donors and targets, held-out fold model, pasted recall within +-0.15 of real, pooled over the 5 folds). Two renderings exist (T8: darken the target's own texture; T10: transplant donor px with ring gain). Choose by C-REAL distance to real recall, before any training; this selects on realism, not on a score. Run alone, never with rcs. Read at OP-C | Null at 2 seeds weak (Y1). Fake gain: seam shortcut (decoys), inactive and crack prior shift | inactive count-based readouts (Y1) |

Gated follow-up `la_ce`: as specified, read against OP-C.

### T11 method suite
| Item | Verdict | Exact fix or pre-check | Note |
|---|---|---|---|
| head_res_ceiling | **FIX** (small), GO now | Average-pooling the log-probabilities of a model trained at stride 1 is not a bound in either direction (the spec says so). Add the GT-side construction as the stated lower bound of the ceiling: pool the GT crack mask to stride s, upsample bilinearly, sweep the threshold for best IoU. The result is printed beside stride-4 rows and bars nothing: a stride-4 row that passes the standard rule at OP-A and OP-W inside the width band is a candidate like any other | 1 h |
| dlv3p_r34_pf | **GO** | Pooling swap and unit test as specified. Tranche 1 | Pratt's architecture |
| unet_r34_pf | **GO** | Tranche 1 | |
| pratt_dlv3p_wcec | **GO**, moved to tranche 1 | `ignore_index` fix and test as specified. Printed at OP-A and OP-W; it is the textbook width case and a prior-shift case (OP-C for gridline) | the dataset authors' recipe |
| hanifi_vgg16_unet_pf | **GO**, moved to tranche 1 | none | E-SCDD authors' model |
| ucf_dlv3_r50_pf | **GO**, moved to tranche 1 | none | UCF-EL authors' model; 22 GPU-h |
| segformer_mitb2_pf | **GO** after the weights are placed | Licence line (user question U2). One lr retry on the failure gate only | our re-implementation, variant unverified |
| hrnet_w18_unetpp_pf | **GO after** the CPU build gate | Candidate rule applies; inactive guard (ResNet-50 lost inactive) | |
| rift_b | **GO** | Build `bench_vendored` once (1.5 h) | crack specialist row |
| rift_b_paper | **GO after** rift_b trains | none | |
| suite_hetero_ens | **GO after** 2 rows have logp dumps | Merged with T6 1b and built on the shared derived-dump tool. One primary for both: strict crack IoU at OP-W, hetero pair minus homo pair; relF1@2 second. State the cost of each pair. Contrast count in the ledger | CPU |
| scsegamba | **GO after** G-MAMBA | Gate first (2 h). Week 2 | Mamba row |
| dscnet_2d | **GO after** the memory smoke | Week 2, if cv02 has room (27.5 GPU-h) | |
| hrsegnet_b48 | **DROP** (parked) | Third scratch crack network, 3.5 h Paddle port, no new question. Reopen if build time is left in the last week | |
| mixercseg | **DROP** | 6 h and a second selective-scan build; RIFT's own table ranks it below RIFT-B (R, spec) | |
| hybrid_segmentor | **DROP** | 5 h, lowest prior of the coded rows | |

For every suite row: G16 columns; seed policy in question L6.

### T12 benchmark protocol
| Item | Verdict | Exact fix or pre-check |
|---|---|---|
| aa_calibration | **GO**, first item | Run per machine: W1-C1 (5 seeds) for cv02 arms, W1-G + W1-G2 (4 seeds, 3 splits) for gaint arms. If the seed stage of the bootstrap is replaced, it is replaced for all arms at once through a new function, before any wave-2 verdict. Part (e) decides the inactive policy (Y1) |
| metric_validity_probe | **FIX** (scope), GO now | Rules as written. Add Y13: pre-declared primaries stay; the width band stays a pass condition under any headline; freeze one skeleton implementation and test it on blobby predictions (spurs lower Tp). Confirm on W1-C1 before v0.2 text changes |
| rank_stability | **GO**, week 2 | Needs at least 4 independent entries to say anything; run when tranche 1 rows are scored |
| tau_from_annotators | **FIX**, then GO | (1) Distances from mutually nearest skeleton points, not every px inside a 10 px cut: the cut mixes crack growth between stress stages into a jitter statistic. (2) The headline tolerance leaves 2 px only if the lower end of the interval is above 2.5 px on the pairs that are not growth-affected and on the one clean double annotation; about 12 pairs cannot move a headline on a point estimate. Default stays @2 |
| leakage_audit_v02 | **GO after** the lead's OK (question L2), moved up | It gates every pool arm and every external-data arm. One tool with T8 C0 and T9's pool list (Y5). Outputs are pair lists only |
| t5_post_eval | **FIX** (small), GO in week 2 | Isolation risk: reuse T8's `c_phys.py`. The pre-check must also be run with predicted crack and ribbons from the OOF dumps, since that is what the score would use (crack pixel recall is about 0.64) |
| reporting_governance | **GO**, week 2 | Add the G13 to G16 declarations to the info sheet |
| severity_external_elpvpower | **DROP** from the 10 days (parked) | Needs the user's OK, 8 build hours, an unverified licence. Last week, only if the user wants it (question U3) |

### T9 pool, teachers, ensembles
| Item | Verdict | Exact fix or pre-check | Null? and fake-gain path |
|---|---|---|---|
| pool_ens_distill | **FIX**, build waits | (1) Raise P1: the teacher (2-seed ensemble, with D4 if built) must beat the single models at OP-W by at least the measured M for strict crack IoU, not by 0.005 (Y9). (2) Read ens_kd_jml's gate G5 from the same computation; build the pool arm only after ens_kd_jml is read or parked. (3) Shared second-stream block, `bn: separate_frozen_running`, `arm_bn` row. (4) U2 is gamed by its scale augmentation. (5) `pool_t9.txt` after the duplicate audit | Null uninformative if the edge is under M. Fake gain: the ensemble's 13% extra width |
| ad_prior | **FIX**: stage A in two steps; stage B gated | Step A0 (2 h): fold 0 only, random bank subsample. Kill rule fixed now: the map's pixel AUROC for crack must beat local darkness (0.708 on low-contrast crack px, E T5 pre-check) and it must flag >= 15% of PF-missed crack components at t95. If not, stop and print the AUROC numbers as the one label-free reference row. Otherwise finish stage A (3.5 h) as specified. The AD track is one row (ours); PatchCore, EfficientAD, Dinomaly and their venv are cut. Its stacking code is the shared cross-fitted stacker (also vfm_ctx gate 2) | A 10.7 px patch holds a 1 to 2 px crack as 10% of its px; on half-cells the whole layout is anomalous against a full-cell bank |
| fm_align_pool | **DROP** (parked) | Gated on vfm_ctx passing, which itself has two gates and no instrument. Reopen on that event |

### T13 few-shot and open sweep
| Item | Verdict | Exact fix or pre-check |
|---|---|---|
| sam_prompt_refine | **GO after** the atlas gate, then P-SAM | Order fixed: read the atlas gate first; P-SAM (1 h) only if it opens. Credit only against `morph_ctrl` and against rule b. Confirm on W1-C1 |
| icl_oof_probe | **DROP** from the 10 days (parked) | 6 build hours to decide whether to build a labeller that has no spec and whose consumer (mic_halfcell) is waiting. Reopen in the T3b week, only for the in-context rows, and only if few-shot rows survive arm 3 |
| t3b_fewshot_rule | **GO after** the LOSO-2 base models | BMRK has 86 crack components >= 20 px in all (E, my count), so a 60% score set has about 52 and fails the spec's own 100 minimum: BMRK runs K = 4 only, as the spec foresaw. CSIR decides the rule on an effective n near 8, so keep 5 draws. Width guard as written |

Count: 25 GO or GO-after, 13 FIX, 9 DROP (1 merged, 8 parked or cut).

---

## 3. Merges, shared machinery, and what must run alone

**Build once (order = how many items each unlocks)**
| # | Shared piece | Used by | Build h |
|---|---|---|---|
| S1 | Derived-dump writer + ensemble dump (`derived_from` in the manifest) | metric probe, P1, G5, hetero ensembles, class biases, rules, SAM refiner, head ceiling | 2 |
| S2 | One inactive atlas | gates of T6, T8, T10, T13; P-GIN (d) | 5 |
| S3 | Duplicate tool: md5 + NCC + embedding, pixel-only on sealed sets; outputs `pool_t9.txt`, external exclusion lists, new group links | T12, T8, T9, T7 | 4.5 |
| S4 | U-dev sets, LOSO-2 roots, label-free scorer mode | every unseen-module read, T13 arm 3 | 7 |
| S5 | `bench/tta.py` | msc_tta, T9 labelling, the TTA row | 2.5 |
| S6 | Cross-fitted fitting loop on top of `crossfit_op` (biases, stacking) | classbias_xfit, ad_prior, vfm_ctx gate 2 | inside the first user |
| S7 | Second-stream trainer block with stream-id registry, GPU aug hook, `bn` option, `arm_bn` readout | ucf, pool distillation, mic, gin_ipa (hook only) | 4 |
| S8 | Auxiliary head + `bench/decision.py` | layered_ci, matched_crack_head, UCF variant 1b | inside the first user |
| S9 | `bench_vendored` registry | RIFT, SCSegamba, DSCNet | 1.5 |
| S10 | F51 dump job for the W1 PF models + read ledger | T6, T8, T10, T11, T13 | 0.5, 0.2 GPU-h |
| S11 | DINOv2 loaders (ViT-S once, ViT-L once) | duplicate tool, AD map, vfm_ctx | inside the first user |

**Merged:** the two paste arms; hetero-ensemble readouts; ensemble dumps and P1 / G5; the three duplicate searches; four inactive anatomies; isolation-risk scripts.

**Must run alone until each has passed confirmation:** gin_ipa; ucf_partial_joint; the merged paste arm (never with rcs); layered_ci; hiera (with its wrapper control); pool_ens_distill (not with ens_kd_jml); mic_halfcell. Post-hoc layers (class biases, rules a and b, SAM refiner) are each read alone first; one stack (biases, then rules, then refiner) is read only after the singles.

**Kept separate on purpose:** rcs (resampling) and paste (new contexts) ask different questions, read as a pair at OP-C. ens_kd_jml (labelled cells) and pool_ens_distill (pool volume) are read as a pair.

---

## 4. Merged ordered plan, 14 to 23 Nov (waves 2 and 3)

Order = CPU jobs that decide many arms, then config-only benchmark rows, then post-hoc arms, then the unseen-module instrument and its first arm, then at most one trained inactive arm and one data arm behind their gates.
Queue advice for gaint (S): run the w2a seed-5 block (31 jobs), then the U-dev block (LOSO-2 baseline, skr01, inference), then the w2a seed-6 block. A one-seed w2a read cannot be judged anyway, and the U-dev block unblocks three teams.

### Stage A: CPU on existing dumps, days 1 to 2 (20 build h, 0.2 GPU-h)
| # | Item | Build h | Decides |
|---|---|---|---|
| A1 | aa_calibration (per machine) | 3 | M for every arm; inactive policy (Y1) |
| A2 | S1 + metric_validity_probe + P1 / G5 | 5 | headline metric; pool_ens_distill; ens_kd_jml |
| A3 | ci_error_atlas (S2) | 5 | every inactive arm, P-GIN (d) |
| A4 | tau_from_annotators (fixed) | 1.5 | tolerance |
| A5 | head_res_ceiling | 1 | how stride-4 rows are read |
| A6 | duplicate tool (S3) | 4.5 | pool and external-data arms, fold links |
| A7 | F51 dumps (S10) | 0.5 | transfer looks |
Wave 2 CPU reads already armed (src_calib, dti_hysteresis, D0) are read here too.

### Stage B: post-hoc arms and the unseen-module instrument, days 2 to 4 (16 build h; gaint 16 GPU-h)
| # | Item | Build h | GPU-h | Waits for |
|---|---|---|---|---|
| B1 | classbias_xfit (defines OP-C) | 4 | 0 | A2 |
| B2 | ci_rules_posthoc | 2 | 0 | A3 part (d) |
| B3 | U-dev sets, LOSO-2 roots, R0 (S4) | 7 | 8.8 baseline + 1 | lead OK for R0; SKR2C opening |
| B4 | skr01 anchor on LOSO-2 | 0.5 | 4.4 | B3 roots |
| B5 | msc_tta (S5) | 2.5 | 2 | B3 |

### Stage C: benchmark rows, config only, days 2 to 5 (7.5 build h; cv02 about 190 GPU-h at 2 seeds)
| # | Rows | Build h | GPU-h |
|---|---|---|---|
| C1 | unet_r34_pf, dlv3p_r34_pf, pratt_dlv3p_wcec, hanifi_vgg16_unet_pf, ucf_dlv3_r50_pf | 1.6 | 11 + 9 + 8 + 16.5 + 22 |
| C2 | segformer_mitb2_pf, hrnet_w18_unetpp_pf | 1 | 15.5 + 16.5 |
| C3 | hiera_bp_unetpp_pf + HR-stem ConvNeXt-T control + UPerNet ConvNeXt-T (card exists) | 2 | 28 + 15 + 15 |
| C4 | skr01_pf_v11 on cv5v2; modern_recipe (AdamW, wave 2, after its norm gate) | 0.2 | 11 + 11 |
| C5 | bench_vendored + rift_b, rift_b_paper | 2.7 | 5.5 + 5 |
Pathfinders run on gaint (about 12 GPU-h in all). Hetero-ensemble readout (1 h, CPU) as soon as two rows have logp dumps.

### Stage D: first GPU arms, days 4 to 7 (new build 14 to 26 h)
| # | Item | Build h | GPU-h | Waits for |
|---|---|---|---|---|
| D1 | P-GIN, then gin_ipa (pathfinder + stage A) | 5 | 11 (+8.8 if M_U1 > 0.03) | B3, B4 |
| D2 | One trained inactive arm: merged paste, or layered_ci, whichever atlas gate opens with the larger oracle gain | 7 | 12 | A1 part (e), A3, pre-check |
| D3 | sam_prompt_refine | 5 | 0.2 | atlas gate, P-SAM |
| D4 | ucf step A (converter, C4 zero-shot read) | 4 | 0 | A6 |
| D5 | vfm_ctx gate 2 (late fusion) | 3 | 0.5 | A3 gate 1 |
| D6 | G-MAMBA; G-MIC census with the blindness share | 2 + 1 | 0.3 | B3 |
| D7 | Wave 2 as built by its own builders: w2a reads, ridge_snap, crackcue_input, oof_soft_distill (N0), then scnp, clce (after SKR2C), cc_dicece, ens_kd_jml (after G5), oof_selective_ignore | about 36 | about 100 | their gates |

### Stage E: days 7 to 10 (new build 16 to 35 h)
| # | Item | Build h | GPU-h | Waits for |
|---|---|---|---|---|
| E1 | t3b_fewshot_rule | 4 | 17.6 | B3 base models |
| E2 | rank_stability, reporting_governance (v0.2 text) | 6 | 0 | tranche 1 rows scored |
| E3 | scsegamba | 4 | 22 | G-MAMBA |
| E4 | nnunet_resenc_2d N1 (N2 native when cv02 is idle) | 9 | 17 (+75) | venv test |
| E5 | S7 + ucf step B, or pool_ens_distill; only one, by gates | 6.5 or 11 | 16 or 26 | D4 and atlas; or P1 at M and ens_kd_jml read |
| E6 | ad_prior step A0 (then the rest of stage A) | 2 (+3.5) | 0 | S6 |
| E7 | t5_post_eval; dscnet_2d | 3 + 2 | 27.5 | room |
| E8 | gin_ipa stage B (CV5 guards); 5-seed confirmations (16.5 GPU-h each) | 0 | 22 + n x 16.5 | passes |

Totals for waves 2 and 3 in these 10 days: about 100 new build hours (65 firm, 35 behind gates) plus about 36 for wave 2's remaining arms; gaint about 150 GPU-h firm and 70 conditional (limit about 260); cv02 about 240 GPU-h for rows plus confirmations.
**Cut line if build capacity is 80 hours:** drop E6, E7, D3, D5 and move E4 to days 11 to 14. The benchmark deliverable then still has: the calibrated margin, the metric and tolerance decisions, the duplicate audit, 11 architecture rows at 2 seeds, the TTA and ensemble rows, OP-C, and the v0.2 text.

### Cut or deferred
- **Dropped or parked from wave 3:** inactive_grid_paste (merged), elpv_bmrk_negatives, pvddpm_fold_synth, fm_align_pool, hrsegnet_b48, mixercseg, hybrid_segmentor, severity_external_elpvpower, icl_oof_probe. Saved: about 60 build hours, about 215 GPU-h.
- **Waiting outside the 10 days:** mic_halfcell (build), hiera_bp_adapter_frozen, ad_prior stage B, la_ce, nnU-Net native, the other AD rows.
- **Suggested deferral inside wave 2 (the lead decides; it is crack-heavy and D0 has not been read):** coletra_crack, liot_input, fullres_detail_head, src_film, thin_geometry_aux, matched_crack_head stay behind this plan unless their CPU gates open clearly. That frees about 31 build hours and 84 GPU-h.

---

## 5. Portfolio: best bet per problem, and honest priors

"Prior" = my chance that the arm moves its primary by a plausible real margin (stated), not the chance it passes a 2-seed screen.

| Problem | Best per build hour | Best per GPU-hour | Prior and evidence | Still uncovered |
|---|---|---|---|---|
| 1 Crack, in-distribution | hetero-ensemble readout (1 h on S1) | same (0 GPU-h) | 25% that a mixed pair beats an equal-size PF pair by >= M at OP-W. For: ensembling is the only clear win (+0.014 to +0.018). Against: stride-4 partners widen. pool_ens_distill 12% (edge likely under M); hrnet_w18 15% (no thin-line evidence) | nothing new; the ceiling is the labels (wave 2 owns that) |
| 2 Inactive | ci_rules_posthoc (2 h) | same | 30% for >= +0.01 paired. For: precision 0.63, 99% of inactive touches a crack. Against: the model has probably learned the co-occurrence. Trained arms: paste 20% for a true +0.03 (about 8% to pass at 2 seeds), UCF 25% and 10% (P037 +0.5 on own classes; +107 cells was n.d.), layered_ci 20%, vfm_ctx 15%, sam_refine 20% | an instrument: no set resolves under about 0.07 for trained arms (Y1) |
| 3 Unseen modules | U-dev reads of arms already trained (7 h makes about 10 arms readable); msc_tta (2.5 h) | gin_ipa (11 GPU-h) | msc_tta: 60% to move U2 (by construction), 25% for >= +0.015 on E1 half-cuts. gin_ipa: 25% to pass U1, 10 to 15% for >= +0.03 on the E1 hard stratum (the photometric half is partly contradicted). hiera: 20% for mIoU-R13 >= M on CV. skr01: the only arm with E1 evidence, 50% that SKR2C replicates. t3b_fewshot_rule: 75% that K = 16 labelled cells give >= +0.02 on the proxy; T3b is the realistic route to a large E1 number, under the `trained_on_e1` mark | **half-cut + scuff with labels.** No arm trains on it and no read contains it (question U4) |
| 4 Other classes | classbias_xfit (4 h) | same | 50% for mIoU-R13 >= +0.01 with interval above 0. For: R2c moved gridline 0.283 to 0.357 by a shift; splice is never predicted. Against: 11 fitted parameters on few groups for splice and edge_dark | splice label quality (atlas part (c) reads it) |
| 5 Measurement | aa_calibration (3 h) | same | 60% that it changes M materially (the bootstrap draws one seed per fold for a 2-seed mean, E T12). metric probe: 70% that relF1@2 fails the dilation test | inactive power |
| Method suite | the five EL-paper rows (1.6 h for 5 rows) | rift_b (5.5 GPU-h) | 90% that each config-only row lands; RIFT 85%; SCSegamba 50% (kernel build); nnU-Net N1 60% inside 10 days | a Mamba row if G-MAMBA fails; SEiPV-Net and PV-MambaSeg have no code (state it) |

---

## 6. Additional guards for the new kinds of arms (continue WAVE2 section 5, items 1 to 12)

13. **External data provenance (G13).** Each external set: host, version, file list with md5, licence text, redistribution yes or no. Label mapping table with thresholds and the share of regions kept and dropped. Duplicate search against all 816 labelled stems, E1 106 and the 117 `_rf` cells (pixels only), hits listed, and a line for what could not be checked. Rows of any source the external set touches are flagged (BMRK with ELPV, SDLE with MultiSolSegment CWRU). The plain comparator is the same card without the stream, same machine and seeds.
14. **Generator, teacher, labeller and bank leakage (G14).** Every model or feature bank that produces training signal lists its training stems; the assert that it never saw the student's held-out fold fails closed. Third-party weights trained on SCDD or E-SCDD are forbidden (released PV-DDPM; the 93 E-SCDD synthetic cells: 35 derive from a legacy test cell, 38 from F51 cells, E). Generic public weights (SAM 2, DINOv2, ImageNet) are allowed and named. Teacher seeds are disjoint from student seeds or the coupling is stated. One pool list for everyone (`pool_t9.txt`): module, md5 and embedding exclusions against every evaluation set.
15. **Instrument validity for unseen modules (G15).** No U-dev read is a claim about E1. A read is used as a primary only if R0 has not falsified it at matched width. An arm trained or tested with the transformation a simulator applies cannot be read on that simulator (HC, msc_tta, scale augmentation on U2). Label-free pool reads count as false alarms only on cells labelled crack-free. LOSO reads print effective n and use their own A/A. All E1 claims wait for one registered opening with at most 3 zero-shot candidates named by a rule written beforehand, plus the T3b track. Decision layers that depend on predicted cracks (rule a) are reported with and without on E1.
16. **Size, cost and step fairness (G16).** Every row prints total and trainable parameters, GFLOPs at 512 px, step time, peak memory, images per step and in total, pretraining data, and recipe source (house or paper). Above 2x house training or inference cost, the PF 2-seed ensemble is printed as the equal-cost comparator. TTA rows print the view count. Scratch rows carry "pretraining: none, house recipe". Budget-matched and native-budget rows of an external codebase are separate, labelled rows, both from final weights.
17. **BN contamination (G17).** Every second-stream arm states `bn` and reports `arm_bn`.
18. **Prior shift (G18).** Inactive and weak-class gains are read at OP-A and against baseline at OP-C. Predicted px of the class on cells without it, and the predicted to GT area ratio (0.85 to 1.15 x baseline), are pass conditions.
19. **Post-hoc and CPU results (G19).** Parameters fixed before the read or cross-fitted. Explored on W1-G, confirmed unchanged on W1-C1. Holm over the variants read. Entered in the benchmark as a decision-layer entry class, never in the default column.
20. **Inactive reads (G20).** Leave-top-3-groups-out, region counts, the BMRK row, fold-level values. F51 and H36 inactive in no promotion rule (4 and 3 cells).

---

## 7. Open questions

### For the lead
- **L1. R0.** Allowed with the Y2 fixes and a ledger line? My answer: yes.
- **L2. Sealed pixels.** May the duplicate tool read legacy test and E1 images (pixels only, pair lists out)? My answer: yes; the module rule already did. It gates every pool and external-data arm.
- **L3. Decision layers.** Per-class biases, co-occurrence rules and the SAM refiner as a labelled entry class, with OP-C as the comparator for prior-shifting arms? My answer: yes to both.
- **L4. Inactive policy.** Accept Y1: no extra seeds for inactive, count-based promotion, at most one trained inactive arm before A1 part (e) is read?
- **L5. The anchor arm.** Add `skr01_pf_v11` (0 build, 15.4 GPU-h) and open SKR2C before R0?
- **L6. Seeds for table rows.** Proposal: a row whose 2-seed interval lies wholly below PF gets no more seeds and is printed with n = 2 and its rank interval; rows that overlap PF get seeds 7 to 9. This saves about 200 GPU-h on cv02.
- **L7. Headline stability.** Accept Y13 (pre-declared primaries stay; tolerance moves only on the interval rule)?
- **L8. gaint queue order.** Interleave the U-dev block between the two w2a seed blocks? All LOSO runs on gaint (T7's request): yes.
- **L9. Wave 2 deferrals.** The six wave-2 crack arms listed under "Cut or deferred".
- **L10. E1 opening.** One registered zero-shot opening with at most 3 candidates, chosen by which rule? Proposal: positive at the frontier on at least two reads that R0 has not falsified, CV5 guards held.
- **L11. One pool list and one stream-id registry** as protocol rules (T9's request): yes.
- **L12. Build capacity.** How many build hours per day are real under the usage caps? The cut line in section 4 assumes 80 in 10 days.

### For the user
- **U1. Training on data without a clear licence.** UCF-EL has no licence file; MultiSolSegment states none. Is training on them acceptable for the thesis and for an "extra data" benchmark track that redistributes nothing?
- **U2. Commercial use.** Must the final model be usable commercially by WattCycle? If yes, non-commercial items stay benchmark rows only: ELPV (CC BY-NC-SA), SegFormer MiT weights (NVIDIA licence, unverified), SOFS.
- **U3. ELPVPower.** OK to download the Juelich module set with measured power for a severity check in the last week (8 build hours, licence unverified)? It is the only public link between EL and power; it is not needed for the benchmark.
- **U4. A small labelled half-cut + scuff development set.** This is the one case where I think minimal labelling is truly needed. 75% of E1 crack pixels sit in half-cut cells with scuff, training has none, and no development set has usable labels there, so every unseen-module arm is tuned blind until the single E1 opening. Proposal: about 24 pool half-cells with scuff from modules outside E1, pre-drawn by the PF and SKR models plus a ridge filter, the user only accepts, deletes or extends components (about 2 to 3 hours). Used for development reads only, never for training. Yes or no?
- **U5. PVEL-AD.** It needs a hand-signed form from an institutional email. Parked unless the user wants to send it.
- **U6. Gated weights.** None needed for this plan. DINOv3 ViT-L and SAM 3 are only for follow-ups that have not opened.
- **U7. cv02.** The benchmark rows need about 240 GPU-h there in 10 days. If other users keep it full, may table rows run on gaint with a gaint baseline (slower, about 1.1 GPU-h per wall hour)?
