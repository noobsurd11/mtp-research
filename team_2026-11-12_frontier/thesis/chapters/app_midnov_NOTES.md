# app_midnov_NOTES.md: sources for app_midnov.tex (writer midnov, 27 Nov 2026)

Path prefixes. `L:` = laptop repo `/home/yugma/mtp/research/`. `S:` = server (the "second machine", read only) `/home/yugma/mtp/research/`.
The handbook docs 17 to 21 and `team_2026-10-31_next/verify_pf2.md` are byte-identical on L and S (md5, 27 Nov: 17 e8b26c65, 18 9478acc6, 19 70351078, 20 e5b75fe4, 21 63386725, verify_pf2 c2c07f29). Server-only sources: `S:team_2026-10-31_next/e1_openings.md` (3ead9149) and `S:team_2026-10-31_next/verify_skr2c.md` (0f7237da).
Line numbers are `cat -n` lines. Quotes are copied (Unicode arrows and minus signs as in the source). "H17" = `L:handbook/17_escdd_dataset_audit.md`, H18, H19, H20, H21 likewise; "LEDGER" = `S:team_2026-10-31_next/e1_openings.md`; "VS2C" = `S:team_2026-10-31_next/verify_skr2c.md`; "VPF2" = `L:team_2026-10-31_next/verify_pf2.md`; "SR1104" = `L:handbook/sources/session_records/SESSION_RECORD_2026-11-03_to_11-04.md`; "TT" = the thesis `thesis_tables.tex`.

Machine naming (rule 6): "training machine" = cv02 (8 GPUs; T21 uses the same mapping, e.g. TT l877 "AL1 (training machine ...)"); "second machine" = gaint (one GPU). H19 l59-60: "gaint memory rule. One RTX PRO 4500 (32.6 GB). Root's `finllm_chat.py` (5.9 GB) must never run out of memory, so ≥ 2 GB stays free at all times." / "cv02. All 8 GPUs were held by other users for the whole session except the DDeP slot."

People: "a collaborator" = the person named in the sources (31 Oct and 1 Nov idea files; role unconfirmed, so not "a team member": audit 27 Nov); "the user" = the student driving the sessions. No other person is named. "E-SCDD cells" replaces the sources' "Hanifi cells / _rf cells".

---

## Opening paragraph
- AL1 on 23 Oct: TT l877 "AL1 (training machine, 5 v 5, locked; 23 Oct)".
- Benchmark build from 12 Nov: `S:handbook/23_frontier_benchmark_12_to_15_nov.md` l1 "The frontier team and the new benchmark protocol: 12 to 15 Nov 2026"; l15 "## 1. What changed on 12 Nov".
- E1 opening #7 on 14 Nov: LEDGER l26 "**opened 14 Nov 2026 00:22:45-03:54:57**".
- Thermal desk study 4 Nov, separate team: SR1104 l1 "the thermal (IR) desk study"; l4 "`team_2026-11-04_thermal/` (thermal desk study and picks 1 and 3)".

## §Conditions
- Legacy split 478 / 54 / 50; v1 labels: thesis ch04_data.tex l22 ("legacy split of 478 train, 54 validation and 50 test cells"), l66-67 ("v1 is the E-SCDD mask ... The pre-protocol work (Chapter~\ref{ch:legacy}) trained and scored on v1 unless stated").
- clean 49 = without the noisy cell: H19 l14 "\"Clean\" / \"without noisy\" = the 50 test cells without `CSIR_00070_r8_c4`".
- test50 in-distribution, known leakage, context only: ch04_data.tex l134-135 ("test50 numbers are in-distribution numbers with known leakage and are used as context only").
- Pooled IoU convention: `L:handbook/07_methodology_rules_and_statistics.md` l85 "**Primary metrics (P8 on).** Test crack IoU, test inactive IoU, test crack relaxed F1@2. Pooled (dataset-level)."; thesis ch02 sec:bg_metrics (IoU from one confusion matrix over all scored pixels).
- mIoU_rob: H18 l43 "Mean IoU over the 13 classes with GT in ≥ 3 of the 50 test cells: 0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21" (class 0 = background).
- Crack AP: `L:handbook/04_glossary_and_naming.md` l32 "rank every pixel by the model's softmax probability for a class ... computed over 1,000 uniform probability bins, dataset-level".
- Rule 1 and the two verdict sets: H19 l51 "Δ > max(0.01, 2·sqrt((sd_A² + sd_B²)/3)), divisor 3 even at 5 v 5. Better on one primary, worse on none. ... Verdict sets: all 50 and without `CSIR_00070_r8_c4` (pass = BETTER on both, or BETTER on one with a same-sign n.d. on the other)."
- Ensemble pass = interval wholly above 0, 2,000 resamples, 71 clusters: VS2C l115 "95% CIs, 2,000 resamples, seed 0. Test: paired image bootstrap. E1: 71-cluster bootstrap. Threshold for a primary: CI wholly above 0 (pass)".
- Guards: H21 l45 "**Guards (G1, G2, G3):** pre-registered FAIL rules ... any trip fails the arm whatever else passes."
- Second machine 2 GB rule (wording fixed in audit 27 Nov: "at least 2 GB had to stay free"): H19 l59 "Root's `finllm_chat.py` (5.9 GB) must never run out of memory, so ≥ 2 GB stays free at all times."
- Seeds never pooled across machines: `L:handbook/07_methodology_rules_and_statistics.md` l141 "seeds are never pooled across machines".
- SUP100-g retrained: H19 l236 "**SUP100-g** | none: fresh SUP100 on gaint at the deploy commit (the cv02 seeds are other hardware and commits)".
- E1 policy ~15:00 31 Oct: LEDGER l3 "**User policy 31 Oct ~15:00:** E1 is a second test set; any protocol may pre-register E1 co-primaries, read once at that protocol's single opening, never for tuning, selection or threshold choice".
- Reads before policy: LEDGER l7-11 (P13 onward, Track M rungs, "27 Oct unlabelled team", "D (30 Oct ...)", "protocol_100 opening 1 ... and opening 2").
- Not blind: LEDGER l13 "FINAL and protocol_100 seeds 0-4 are **not blind** on E1".

## §E-SCDD
- Download 12 Oct, no model: H17 l4 "On 12 Oct 2026 the user asked: \"download the full ESCDD data, audit it ...\""; l11 "No model was trained or scored for this."
- R4 used 107 cells: H18 l231 "585 train cells (478 + 107 E-SCDD real cells ...; 104 of them CSIR)".
- Three releases, 582, 695, joined/widened: H17 l30-31 "Our project uses the oldest, `20211104` (582 cells)." / "`20221008` (695 cells). In it they corrected many crack labels: dotted labels joined, lines widened."
- E-SCDD repackages 20221008: H17 l32.
- 265 cells; 327,754 → 396,572; 2.17 → 2.52; 5,391 → 1,288: H17 l187-194 ("Same 265 cells", "Crack pixels | 327,754 | 396,572 (+21%)", "Width, px (pooled) | 2.17 | 2.52", "Fragments | 5,391 | 1,288").
- +0.05 to +0.08: H17 l37 "the \"revised labels\" that moved crack IoU by +0.05 to +0.08 (P3, P14) are BenchmarkEL's own `20221008` corrections, delivered through E-SCDD". (Not in conflict with ch05's "+0.05 to +0.07 (P3)" and "+0.082 (P14)": the H17 range spans both.)
- 693 identical images, 627 masks, 66 differ, 62 masks, 552,426 px, 4 swaps, 0 crack/inactive: H17 l110-114.
- 903 = 693 + 117 + 93 vs 1,000 = 695 + 110 + 195; unlabelled 0: H17 l100-101.
- 93 synthetic from 4 base cells, all in train: H17 l130 "**Only 4 base cells:**", l135 "**All 93 and their bases are in train.**"; 11.7%: l137.
- 117 new: 114 CSIR, 3 ARTS: H17 l143; 128 to 380 fragments in 3 cells: l147; 100 in our pool: l145.
- 48 of 82; 39 of 50: H17 l155-156.
- Scuff 30 Oct, 12 cells, 3,246 px: H17 l206-207; remap 1,207 / 1,390 / 649 in 6 cells: l215; ARTS 5% cell 47 px all scuff: l226; test 2 cells 236 px crack: l227.
- Led to B3 and v1.1: H17 l234 (B3); thesis ch04_data.tex l77 ("The reason for the change was that v1 labels scuff streaks as crack on 649 px in 6 train cells").

## §Two analysis teams, Track D, Track M
- Why-SOTA team 24 Oct, no GPU, two analysts + critic: H18 l52, l56 "Data-side analyst R1, method-side analyst R2, critic C."
- BsM5 +0.029; +0.037 with free bias: H18 l59 "With the free bias on both sides it still passes: +0.037 (thr 0.013)"; the free bias is logit adjustment (LA, z_c − τ·log π_c over all classes, H18 l42), so the .tex says "a free logit bias (logit adjustment)", not "crack logit bias" (audit 27 Nov). a third of +0.092 (24 random cells): l60. 38% true miss: l64. 8 directions, #1 stop SSL for crack: l75-76.
- User goal quote: H18 l85 "\"take the critics decisions, and go\", with the goal \"highest scores, a model which captures almost all of the cracks, inactive and other important defects balancing the miou for other classes as well\"".
- Track D/M on cv02, dates: H18 l6-7 "Track D (24 Oct, cv02)", "Track M (24 to 25 Oct, cv02)".
- D1 setup (23 labelled 5% cells): H18 l93. D2: l120. D3: 3 draws × 3 seeds = 27 runs, oracle-selected, 3-seed break accepted: l141-142.
- Table D1: rule bar 0.215 (A5c+LA 0.165): H18 l95; ResNet-50 0.268 pass test and pool: l103; ConvNeXt-T 0.278 / 0.271 pass on test only: l104; ResNet-34 0.185, DINOv2-S 0.122, own encoder 0.171: l105-107; recall 0.020 / 0.023 (ResNet-50), 0.002 (ConvNeXt-T) vs 0.21: l110.
- D2 kill rule: `L:team_2026-10-24_go/trackD/protocol_edge.md` (fe7c2b0b) l9 "**Kill:** a gap changes sign (banded Δ past its threshold with the opposite sign to the standard Δ)." Band 11.6%: H18 l123; +0.018 to +0.027: l125; kill not triggered: l126.
- D3 rule: H18 l143 "draw-level max(0.01, 2·sqrt(var_A/3 + var_B/3)) over the 3 draw-means. Primary P1: Ts − Tc; P2: Tc − R". P2 +0.0127 (0.0118) BETTER, P1 +0.0151 (0.0212) n.d.: l159-160. Tc − R relF1@2 +0.030 [+0.020, +0.042] all four sets: l164.
- MIM gated out by D1's rule: H18 l112 "By the locked rule MIM was gated out."
- Direction-5 gate not opened, BMRK recall +0.023: H18 l173 ("Tc − R BETTER with BMRK recall ≥ +0.05"; the .tex now says $\geq +0.05$, audit 27 Nov). Volume explains Tc − R gap: l168. Reading "targeted labels beat both random labels and SSL at this budget (oracle-selected)": l175.
- Track M SUP100 recipe: H18 l40 (U-Net++, ImageNet ResNet-34, CE + Dice on crack and inactive, label-safe augmentation, 512 px, 20k steps; 5 seeds).
- M0: 0.435 ± 0.078; 0.474 ± 0.002: H18 l189-190; one seed 0.297: l194; every contrast with and without noisy cell: l198.
- Val inclusion rule; test never used to choose: H18 l45.
- Table Track M: R1 val decisions TTA off, bias +0.75: H18 l204; R1a +0.0104 (0.0100) PASS without noisy, all 50 n.d.: l207; R1b +0.0144 [+0.0118, +0.0167]: l208. R2 −0.0106 (0.0100), −0.0130 (0.0100), gridline 0.283 → 0.381, WORSE, val EXCLUDE: l218-220. R2c n.d. all four, gridline 0.283 → 0.357: l223-224. R3 pilot selection: l246-253; Part B inactive −0.0251 (0.0227) WORSE, crack −0.0041: l260. R4 +0.0010 [−0.0026, +0.0062], +0.0085 [−0.0042, +0.0277], n.d.: l233. R5 −0.0046 (0.0100), n.d.: l275; 4.0×: l278.
- Test openings order: H18 l322 "R1 no. 1, R2 no. 2, R4 no. 3, R2c no. 4, R3 Part B no. 5, R5 no. 6, FINAL no. 7".
- Clip: H18 l221 "mean pre-clip grad norm 6.74 vs 1.80 for SUP100; clip rate 0.969 vs 0.253 ... \"Dice-12 at the L3 clip\", not Dice in general."
- No rung passed → recipe SUP100; FINAL definition, +0.75 by max val relF1@2: H18 l286, l288; fallback because no bias reached 0.90 / 0.90: l204.
- FINAL verdict PASS, +0.018 [+0.013, +0.025], 0.474 → 0.492: H18 l294, l309, l314. Opening no. 7 on 25 Oct: l284 "## M7. FINAL: the best-scoring model (25 Oct, Track M test opening no. 7)".
- 10,867 px vs 2; bias 0 robust: H18 l317. 0.866 / 0.930 not reached: l318.
- E1 recall ResNet-50 0.178 → 0.214: H18 l264; R5 0.204: l277. Descriptive: l277 "(descriptive)".
- Qualifier (optimizer never varied): H18 l324 "[Qualified 30 Oct: \"every single-model change failed\" holds under the never-varied house optimizer ...]".
- Unlabelled team 27 Oct: question l332; only label propagation tested, feature learning not: l337-338; worked with few labels: l339; +0.02 excluded at 20, 50, 100%: l342; old +0.028 one seed on noisy cell: l342; 70% within 2 px: l345; 20 cells, 75%, 0.126; 0.552: l357-358; paints streak, misses branching cracks: l361; keep 50 cells, clean co-primary, E1 sealed with two readouts: l367-369; ranked plan, item 3 MIM at 5%: l379.

## §Feature learning at 5%
- 28 Oct question and answer "never run": H19 l65.
- A5c-f1, 5 seeds, 0.300 vs 0.304: H19 l52.
- 5% copied from the 27 Oct plan, user's question was about 100%: H19 l68.
- MIM pool 11,690 cells; exclusions: H19 l77-81. Recipe mask 0.6, batch 32, 36,500 steps: l82. 13:08 to 18:34; 0.914 → 0.208: l83.
- MIM5 n.d., every estimate negative; 0.3002 → 0.2886, −0.0116 (0.0186); closed: H19 l87, l91.
- AM KILL, AP 0.0166, no threshold reaches relaxed precision 0.5: H19 l111.
- DDeP 40,000 steps, cv02: H19 l114. DDeP5 n.d.; +0.0070 (0.0100); closed: l116, l120. recall 0.365 → 0.384, precision 0.628 → 0.606: l123.
- CP5: 20 components: l130; gate PASS at 2k: l131; stopped 10:50 30 Oct, s1 and s3 finished, s0 11,800, s4 12,350, s2 cancelled, not scored, no test opened: l132; ARTS paste is scuff: l130.

## §Encoder audit and PF
- House optimizer, never varied: H19 l53 "Adam lr 1e-3, coupled L2 weight decay 1e-4, 200-step warmup and cosine, 20k steps, batch 8 ... Never varied in the P-series or Track M R1 to R5."
- Table: H19 l143-149 (first column "MIM moved it: cos(MIM, ImageNet)" is the pretrained MIM encoder, not a step-20,000 fine-tune; caption says so since audit 27 Nov; all values copied; "SUP100 `p6_L3` s0: cos(final, ImageNet)" column; "Norm final/init (SUP100)" column).
- 2k smoke 0.070 / 0.003, norms 0.33 / 0.21: H19 l154.
- MIM changed layer2 to layer4: H19 l153. MIM5 tested conv1/layer1 only: l103.
- Earlier nulls under this optimizer; measured on ResNet-34 U-Net++ only: H19 l159-160.
- User quote ~10:45 30 Oct: H19 l170 "**The user (30 Oct ~10:45):** \"why 5%? I asked about adding the pool to 100% labels.\"" (quote shortened to its first two sentences; text: "why 5%? I asked about adding the pool to 100% labels.").
- Rule "(1) the method does not consume labels and (2) the 5% estimate is tight on crack; ... CP meets neither; inactive never meets (2) at 5%": H19 l194. About 20 to about 560 components: l189. "Only 2 training cells have inactive at 5%": l183. MDE 0.012 vs 0.019: l183. Pool ideas at 100% thereafter: l198.
- PF definition: H19 l54 "Encoder frozen for steps 0 to 999 (BN in train mode), then encoder lr ramps 0 → 0.1× base over 1,000 steps, encoder weight decay 0. Decoder and head as house."
- G5 gate ≥ 0.8 at 4k; 0.975 / 0.985, 0.986 / 0.990: H19 l265, l275.

## §protocol_100 and label work
- 4 arms × 5 seeds, gaint, 478 labels, 20,000 steps: H19 l232-239. CP100 house optimizer + paste stream: l239.
- Library 554 components: H19 l255.
- Gates 1-4 IDENTICAL: H19 l273; gate 1 "no switch", 2 "PF neutral", 3 "CP λ 0", 4 "Val-off identity": H19 l261-264 (hence "bit-identity checks of the new switches when off and of validation off", audit 27 Nov). Gate 6 FLAG 2.45× vs 2× line: l277. Gate 6b decided before any CP100 run: l280. Decoy fell 0.0076 → 0.0039 (2k → 4k): l394 "Gate 6b's GO rested on the decoy falling from 2k to 4k (0.0076 → 0.0039)".
- Launch 12:05:34 30 Oct: H19 l229. Fine-tunes done 00:56:44 31 Oct; CP100 00:21 to 06:52: l357. Reboot 16:28, resumed, lines IDENTICAL: l358. Openings 00:57 to 01:33 and 06:53 to 07:07: l359.
- Table: H19 l364-367 (MIM100-PF − SUP100-PF and SUP100-PF − SUP100-g rows), l388-389 (CP100 C1 rows). Inactive thresholds not printed in the table because I quote only the values the rows give.
- All n.d., also at tau 1; closed at 100%: H19 l371 "All n.d., also at tau 1 (LA on both arms). Pool and recipe are closed at 100% per the kill line."; CP: l393 "All n.d.; C3 ... n.d. No crack claim; closed."
- Cosine at 20k: 0.928 / 0.936 vs 0.015 / 0.001: H19 l372.
- E1 PF 0.213 vs 0.169 recall, 0.245 vs 0.041 inactive: H19 l379; gain only in 29 scuff + half-cut cells: l383.
- CP decoy 4.41× at 20k: H19 l394.
- Open lead, fine-tune recipe on E1 only: H19 l399 "**Open lead (S):** the fine-tune recipe, on E1 only".
- D checks ("at least +0.05" in the .tex since audit 27 Nov): rule l402 ("kill unless a variant gains ≥ +0.05 E1 recall on the 29 scuff + half-cut cells at an E1 crack-precision cost < 0.05"); table l406-411 (RN50-5 0.185 (+0.060), cost 0.047; BN-HC routed +0.174, cost 0.085; R34-5 + RN50-5 +0.036; R34-10 +0.001); "The RN50 effect is not ensemble size": l413. Dates 30 to 31 Oct: l401 header "inference-only E1 checks"; R34-10 "31 Oct" l411; LEDGER l10 "D (30 Oct, d_prereg.md) ... R34-10 control (31 Oct 01:41)".
- B1: five 50% models, 239 cells: H19 l310; flag rule all 5 confident against GT: l311; crack flags in 24 cells (10.0 per 100), not above val: l322; sheets, no mask change: l323.
- B2 v1 AUROC 0.328 / 0.396; v2 986 half-cells, mode ab; AUROC 0.384 / 0.437 "unvalidated": H19 l416-417; 90 ranked + 10 blinded random: l418. Dates: v1 on 30 Oct (l328 "running on gaint CPU since 12:09 IST 30 Oct"), v2 to the user 30 Oct (l329 "v2 (half-cells only, mode ab) went to the user on 30 Oct").
- Large pool 159,332 rows, no E1 module family, no new half-cells, download condition failed: H19 l422.

## §Eleven ideas and PF2
- 31 Oct ~13:45, user instruction: H20 l5 "Om's answers to the protocol_100 follow-up and 11 new ideas aimed at unseen panels (E1), pasted by the user with \"work on this direction further, no budget boundaries, we have 2 more months ... refrain from manual labelling unless very much needed\"". Accepted verdicts, approved PF2: `L:team_2026-10-31_next/om_2026-10-31.md` l8-9.
- Diagnosis domain generalisation: H20 l48.
- One agent per idea, judge reviews, pipeline: H20 l49-50.
- Table rows (ideas 1 to 11): H20 l56-66, copied as follows: 1 l56 + routing FAIL l77-81 ("Routing is PARKED behind a labelled half-cut set"); 2 l57 (median 143 vs 138; white letterbox; "test-time mappings lower val relF1@2 by 0.02 to 0.06"; DROP); 3 l58 ("50% of E1 cells ... have no same-module file anywhere"; "Om's version DROP; in-crop variant PARK"); 4 l59 ("the model already ignores busbars; crack vs scuff AUROC ≤ 0.45"; "DROP standalone; 3 and 4 jointly PARKED"); 5 l60 ("FINAL crack recall 0.706 → 0.563"; "PASS (narrowed) → HC"); 6 l61; 7 l62 ("per-run b_comp unstable ... → arm-level pooled OP"; "PASS (in every protocol)"); 8 l63 + probe l101-102, l110 ("DINOv3 ConvNeXt-T | 0.363", "IN-1k ConvNeXt-T | 0.310", "Pick rule (bar 0.424): nothing qualifies; DINOv3 ConvNeXt-T enters the screen by rule"); 9 l64 + T9 l91 ("Every variant fails the +0.03 term"; FA rise l87-90); 10 l65 ("75% of components < 5 px"; "SAM fails on cracks"; "crack DROP / trust-region PARK; scuff PARK; inactive S10 → PASS, method note") + S10 l94 ("pooled IoU 0.4925 → 0.5653") + l95 ("Method note; no training arm"); 11 l66 ("no arm").
- Ideas table caption, E1 reads: LEDGER l12 "31 Oct (before / around the policy): calib's idea-1 and idea-7 backfill (FINAL, SUP5, SUPPF5, MIMPF5, CP5 on E1), judge's checks and idea-1 oracle split" (the earlier caption "no new test50 or E1 read" was wrong for ideas 1 and 7; audit 27 Nov). A1-A6 opened no test or E1 file: H21 l151 "(val / `_rf` records; no test or E1 file opened)".
- F51 / H36 from modules not in train: H20 l42 (F51 "from modules not in train"); H21 l43 "Hanifi `_rf` unseen-module full cells (51; ...) and half-cuts (36; ...)". Audit 27 Nov check for H36: the 7 H36 modules in `L:team_2026-10-31_next/ideas/found_scripts/t9_rf_sets.tsv` (CSIR_00297-00299, 00301, 00333-00335) have 0 stems in the 478-line legacy train list `L:team_2026-11-12_frontier/harness/x2_src/data/splits/train.txt`.
- A1 to A6 rows: H21 l152-160 (A3 "H36 cut-line / spacing FP 123 → 3 px/run"; A4 "fragments are ≤ 5-7% of non-E1 components"; A6 "its extra px are 99.6% inside crack cells"; A4 "(S: not revived)" l160). Checked 2 Nov: judge verdict "judge 2 Nov 11:43" H21 l26; the ideas were written 1 Nov: l151.
- E1 width 3.66 vs 2.41: H20 l69. H36 crack labels unusable, 1,792 px, 48% within 10 px: l70; "No labelled half-cut crack set exists outside E1": l70.
- PF2 design and dates: H20 l113 "SUP100-g / SUP100-PF / RN50-PF, seeds 5 to 9 ... Ran 31 Oct 14:29 to 1 Nov 06:32 (15 rc 0); opened 06:33 to 08:26 (E1 opening #1)".
- PF2 verdicts: VPF2 l9 "PASS on both lines"; l10 "E1 inactive IoU 0.0481 → 0.2371, **+0.1890 (thr 0.0433) BETTER**; E1 crack recall 0.1715 → 0.1986, +0.0271 (thr 0.0370) n.d."; l11 "relF1@2 BETTER in both sets (all 50: ... +0.0117, thr 0.0100; clean: ... +0.0120, thr 0.0100); crack IoU n.d. ...; inactive IoU n.d."; l13 "RN ... FAIL. Test inactive IoU WORSE in both sets (0.4557 → 0.4269, −0.0289, thr 0.0251 ...)"; "The encoder gate is closed for RN50 under PF".
- Beside: VPF2 l17 "clears the 0.01 floor by 0.0017 / 0.0020 ... +0.0117 [−0.0034, +0.0292] ... leave-top-3-out +0.0015"; l18 "5/5 PF seeds 0.207-0.279 vs 5/5 house 0.025-0.089; strata: half-cut 58 0.162 → 0.537".
- 3-image fact, 1 Nov 23:46: H21 l145-147 "the top 3 ... hold **87%**"; "PF2's +0.189 (singles) shrinks to **+0.023 without them**"; 9,158 px in 7 source images: l146.
- PF2E: date 1 Nov 19:02-19:13: H20 l196. Design and bias rule: H20 l132 ("D2 chose b 1.25 / 1.5; both tripped the val width flag (val crack precision drop +0.0543 / +0.0753), so **the verdict is at b 0 (argmax)**"). Table: l136-140 (test +0.0027, +0.0121, +0.0237 n.d.; E1 relF1@2 +0.0355 [−0.0232, +0.0912] n.d.; E1 inactive 0.0665 → 0.2807, +0.2141 [+0.0303, +0.3820] PASS). Not independent of #1: l148. Half recall 0.304 → 0.627, half fewer false inactive px "on module-border / frame-edge px of edge cells ... three consecutive CSIR images": l144. Bonferroni 99% LB ≈ 0.000: l146. Recommendation: l151. Adoption open on 3 Nov: H21 l137 "the user's adoption is still open (doc 15 §3d row 19)" (doc 21 written 3 Nov, l16).

## §THIN-B3, A8, HC, B6
- THIN-B3 design: H20 l155 (arms SKR w 1, CLD w 1 k 10, B3; seeds 5-9; comparator PF2's SUPPF s5-9, "bit-identity shown over 2,000 steps"); co-primaries l156; trained 06:32 to 19:39 1 Nov, opened 19:40:18 to 21:13:45: l157.
- B3 = raw scuff px to new class (the 649 crack px stop being crack): H19 l340.
- Results: H20 l162-168 (SKR −0.0136 / −0.0140 thr 0.0100 WORSE; comp recall +0.0413 BETTER; E1 +0.0590 thr 0.0392 BETTER; CLD relR@2 −0.0374 / −0.0376 thr 0.015 WORSE; B3 all n.d.; verdicts FAIL / FAIL / n.d.). B3 scuff IoU 0.000 all 5 seeds: l172. SKR pred/GT 0.95 → 1.54, ×2.4, bootstrap [−0.036, +0.012], ~1.5x wider: l170 ("crack px on crack-free E1 cells ×2.4"; the .tex said "doubled", now "×2.4", audit 27 Nov).
- A8: H21 l48 (seeds 0-1, 4k steps, no test, no E1, data root test.txt = val; trained 1 Nov 21:15-22:55; scoring 22:56-23:02); GO rule and result table l51-56 (0.5448 − 0.5691 = −0.0243; LB −0.0463); KILL closes "foundation encoder": l58; 76% one cell, A8c spread 0.067, "no sign of a gain": l59. 36-module bootstrap: l54. Both under PF: l47 heading "DINOv3 under PF".
- HC: p 0.35, ~26%: H21 l63 / H20 l175; trained 1 Nov 21:41 to 2 Nov 02:17; opening 02:18:34-03:09:57: H21 l63. Co-primary table: l67-71. Verdict n.d.; mechanism 0.8192 vs 0.6959; F51 guard passed: l73. Seed-aware [−0.054, +0.005]: l75. Reading "the simulator mechanism works, real E1 half-cuts do not move": l80 (S in source; marked "our reading" in the .tex).
- Synthetic half-cut construction (cut line, gap): `L:team_2026-10-31_next/om_2026-10-31.md` l69 "cut labelled full cells, add the dark cut line and spacing".
- B6: design (5 folds, 532 cells, module groups, 2 seeds, 20 runs, pass rule LB > 0 and Δ ≥ 0.01; training cv02 only, scoring gaint, user 1 Nov 23:54): H21 l83; ALL TRAINED 21:31, scoring 22:11-22:13: l84; result −0.0144 [−0.0977, +0.0570] n.d.: l85; planned SE 0.020, realised 0.038; ~6% at +0.017 (13% stated before): l86; excludes a gain as large as the E1 gain: l87. Date 2 Nov: the run day per l84 ("cv02 qualified 13:30 ... ALL TRAINED 21:31") and H21 l22 (coach 22:18, i.e. 2 Nov).

## §SKR2, HC2, SKR2E, B2 raters
- SKR2 w 0.1; HC2 ignore inactive in synthetic views: H21 l92-93. Guards G1, G2, G3: l94. HC2 design history four steps, retention 0.399 / 0.359 vs 60% rule; user "run HC2 as built" 17:58: l95.
- Opening #5 2 Nov 20:01-21:23: H21 l172.
- Results: H21 l100-108 (SKR2 E1 +0.0364 (0.0351) BETTER; HC2 G1 TRIP −0.0256 / −0.0259; verdicts PASS / FAIL (G1)). "the other six co-primaries n.d.": l100-105 (test 3, B5 2, E1 any-hit: all n.d.). HC2 mechanism failed, max 0.776: l119.
- Margin 0.0013; 5 of 10 seed drops; seed-aware [+0.004, +0.076]: H21 l111-112. ~10% family-wise over 7 co-primaries: l174.
- HC route kept open, only (a2) closed, 2 Nov 21:51: H21 l121.
- SKR2E: shared b 0 and headline pair; run 22:24:38-22:36:52: H21 l125. E-PF headline b 0 (drop 0.0753); E-SKR2 headline 1.0 (drop 0.0485): l126. b 0 table l130-134 (test crack IoU +0.0102 [+0.0031, +0.0197]; E1 +0.0353). Guards G2a −0.0379, G2b 5,358 vs 2,528 (×2.12): l136. FAIL, E-PF stays recommended: l137. Width flag by 0.0015: l139; b 0 passes not a confirmation: l140; E-PF at b 1 equals E-SKR2 at b 0: l141.
- B2 raters: user asked 2 Nov 11:26: H21 l163. Rules (name-free bundles, judge holds key, PASS/FAIL only; gate A 40 house CSIR crack, sens and spec ≥ 0.70; gate B 32 E-SCDD pool half-cells scuff, sens ≥ 0.50, spec ≥ 0.70; two runs = consistency): l164; prereg thresholds also in `L:team_2026-10-31_next/ideas/b2_agent_marking_prereg.md` l120-127. Result identical, crack PASS 20/20, 17/20; scuff FAIL 1/8, needs ≥ 4/8; no agent marks; B2 unmarked and back with the user: l165. "4/8" = ≥ 0.50 × 8 (derived: 0.50 × 8 = 4; H21 l165 itself says "needs ≥ 4/8").

## §SKR2C
- Question, fresh seeds 10-14, 10 runs, seeds not cells, third look: H21 l177. Locked 3 Nov 02:37: l176. Stage-1 code review NOT READY, 7 must-fixes (outside-process HOLD missing, owner re-check before SIGKILL missing ...): l181. Launch 03:06, ALL TRAINED 3 Nov 11:24:04, 10 rc 0, guard never fired: l183. Data root test.txt = val: l179.
- Laptop reinstalled, no agent survived: SR1104 l24 "**12 Nov:** the laptop OS was reinstalled (disk 52 GB free, E); no agent survived" (also l69). [Audit 27 Nov: line was given as l58; corrected.]
- User OK 12 Nov "Open it now": LEDGER l30 "on the user's OK of 12 Nov \"Open it now\"". Frozen 14 Nov 00:13: LEDGER l29. Opened 00:22:45 to 03:54:57: LEDGER l26, l30.
- R FAIL by G1 (−0.0198 / −0.0207) and G2 (−0.0780, all 50); E1 relF1@2 +0.0289 (thr 0.0281) BETTER; 1 BETTER, 0 WORSE, 6 n.d.: VS2C l6-9.
- D FAIL by G1t alone (−0.0269 / −0.0283); E1 relF1@2 +0.0342 [+0.0115, +0.0544] passes: VS2C l10-12; any-hit +0.0338 [0.0000, +0.0586] n.d.: VS2C l123 (table row "E1 any-hit (114 → 124 of 296) | 0.3851 | 0.4189 | +0.0338 [0.0000, +0.0586] | | n.d.").
- Named claim REPLICATED does not hold; seed-aware CI [−0.0015, +0.0590]; three conditions: VS2C l17-20. Fixed wording quote: VS2C l21.
- SUP100-PF ensemble stays: VS2C l14. Skeleton Recall route closes for the deployable at w 0.1: LEDGER l30; VS2C l25.
- G2 one run: s13 49,713 px on the noisy cell, GT 787; clean −0.0119: VS2C l27-29.
- D's G1t null false-FAIL ~8%: VS2C l13.
- Reading "cannot tell them apart": VS2C l315 "This outcome is what such a false FAIL would look like. It is also what a small real cost would look like. The data cannot tell them apart" (S in the source).

## §Ledger table (#1 to #7)
- Rows: LEDGER l18-26 (protocol, opened times, co-primaries, results). Opened times: #1 l18 "opened 1 Nov 06:33-08:26"; #2 l19 "opened 1 Nov 19:40-21:13"; #3 l20 "opened 2 Nov 02:18:34-03:09:57"; #4 l23 "opening started 1 Nov 19:02:04" with end 19:13 from H20 l196 "1 Nov 19:02-19:13"; #5 l24 "opened 2 Nov 20:01:46-21:23:18"; #6 l25 "opened 2 Nov 22:24:38-22:36:52"; #7 l26 "opened 14 Nov 2026 00:22:45-03:54:57".
- Rules: #1 VPF2 l8 "Verdicts (protocol_PF2 §3, rule 1 /3, 5 v 5)" and LEDGER l18 co-primaries; #2 H20 l156 co-primaries, rule 1 "worse on none" from H19 l51; #3 H20 l175 ("Mechanism kill: SHV1 relR@2 at relP@2 ≥ 0.90 gain < +0.05. Harm guard on F51"); #4 LEDGER l23 ("module-cluster bootstrap, 71 clusters"), H20 l132 (headline b); #5 LEDGER l24, H21 l92-94; #6 LEDGER l25 ("co-primaries at b 0 ... guards ... at b 0 and the headline pair"); #7 LEDGER l26 and VS2C l17-20.
- Verdicts: #1 VPF2 l9-13; #2 H20 l168; #3 H21 l73; #4 H20 l140; #5 H21 l108; #6 H21 l137; #7 VS2C l6, l10, l17.
- Reuse of PF2's SUPPF files in #2, #3 (and #5 as comparator) not a new read: LEDGER l22 ("reused unchanged as the comparator in #2 and #3"); LEDGER l24 ("+ PF2's SUPPF s5-9 reused"). #4 not independent of #1: LEDGER l23; #6 not of #5: LEDGER l25; #7 third look: LEDGER l26 "3rd look". Uncorrected co-primaries within and across openings: H20 l197.

## §What the period led to (reading)
- PF replicated E1 inactive on new seeds, 3-image readout: VPF2 l12 ("PF lifts E1 inactive IoU, replicated on new seeds, same E1 cells"); H21 l148.
- Ensemble clearest test50 gain: thesis ch05_legacy.tex l128-130 ("This was the one clear win of the period"). I wrote "clearest" as our reading.
- test50 / E1 read too often, weak instrument, moved to module-grouped benchmark with PF as baseline: thesis ch05_legacy.tex l135-149 and l108 ("PF became the baseline of the protocol and of the final comparison"); move on 12 Nov: `S:handbook/23_frontier_benchmark_12_to_15_nov.md` l15.

---

## Derived values (formula)
- "4/8" (scuff gate): 0.50 × 8 items = 4 (H21 l165 states it).
- No other derived number: every other value is copied.

## MISSING_CITES
- SparK: K. Tian, Y. Jiang, Q. Diao, C. Lin, L. Wang, Z. Yuan, "Designing BERT for Convolutional Networks: Sparse and Hierarchical Masked Modeling", ICLR 2023 (arXiv 2301.03580). Used as `\CITE{SparK, Tian et al.\ 2023}`.
- clDice: S. Shit, J. C. Paetzold, et al., "clDice: A Novel Topology-Preserving Loss Function for Tubular Structure Segmentation", CVPR 2021 (arXiv 2003.07311). Used as `\CITE{clDice, Shit et al.\ 2021}`.

## UNSOURCED
- None in the .tex. Left out for lack of a direct line: the CP100 "seam-sensitivity caveat" of T21 (not found in my sources; not used); the date and content of any B2 marking after 3 Nov (the laptop's `b2v2_marks.tsv` is empty; not claimed).

## CONFLICTS (found, none contradicted in the .tex)
1. H18 l286: session record says "Six training changes all failed"; verify_final lists five rungs. The .tex lists the five tested rungs and the two val-only pilots, as the verify file does.
2. H19 l114: DDeP pretraining start time differs between the session record (15:40) and the log (~19:43, full run); the .tex gives no start time.
3. H19 l181: CP library counts 556 / 566 / 554; the .tex uses the frozen v1.1 count 554.
4. B2 agent-rater thresholds: `L:team_2026-10-31_next/log.md` l571 (2 Nov 11:36) states prereg v2.0 thresholds 0.75 / 0.60; the approved v2.2 (prereg l120-127; H21 l164) uses 0.70 / 0.50 / 0.70. The .tex uses v2.2.
5. ch05 (l141) and T17 count seven registered openings before #8; consistent with this appendix.
6. (audit 27 Nov) protocol_100 opening 1 start: LEDGER l11 "opening 1 (31 Oct 00:59-01:33)"; H19 l359 "Opening 1 scored 00:57 to 01:33 31 Oct" and `L:handbook/sources/session_records/SESSION_RECORD_2026-10-30_to_31.md` l40 "31 Oct 00:57:31 to 01:33:24 | Opening-1 scoring". The .tex keeps 00:57 (timestamped session record).
7. (audit 27 Nov) Opening #3 end: LEDGER l20 "02:18:34-03:09:57"; the .tex "02:18 to 03:10" follows H21 l171 / H20 l177 "02:18-03:10" (rounded to the minute; T17 prints the seconds).
