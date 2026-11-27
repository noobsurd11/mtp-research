# NOTES for ch05_legacy.tex (Chapter 5, "Before the protocol: the legacy-split work (10 Oct to 14 Nov)") and app_t21_note.tex

T = `/home/yugma/mtp/research/team_2026-11-12_frontier`; HB = `/home/yugma/mtp/research/handbook`. Files read, md5 (first 8):
TT `T/thesis/THESIS_TABLES.md` 81c54378 (T21 rows l686 to l725, rule note l727; T17 l587 to l596); SOURCES.tsv 76814c96 traces
every T21 / T17 cell to handbook doc 11 (H11) and to the primary record (results/p3 ... p17, trackD, trackM, verify_*.md, e1_openings.md);
H11 `HB/11_results_synthesis_and_claims.md` 769e9810; H19 `HB/19_feature_learning_and_100pct_plan.md` 70351078;
H20 `HB/20_pf2_and_domain_ideas.md` e5b75fe4; H04 `HB/04_glossary_and_naming.md` f1ed6b44; BR `T/BRIEF.md` bc06edd2;
P02 `T/benchmark/PROTOCOL_v0.2.md` b8b7f66a; TL `T/benchmark/test_openings.md` 2629ed93; W1C `T/results/W1C_READ.md` 3a437100;
V8 `T/results/final_opening_read/verdict.txt` bbb5f3b4; ML `T/cards/ledger/MASTER.tsv` e8aeeaa7 (used only for the DINOv3 id, P190).
No sealed label, mask, image, dump or prediction was read.

## 1. Every number in Chapter 5, with its source

### Intro and 5.1 Conditions
| Number / phrase | Source |
|---|---|
| 38 rows of T21 | TT l65, l680 |
| seven registered E1 openings before the final one | TT T17 rows 1 to 7 |
| legacy split 478 / 54 / 50 | TT T21 caption (l684) |
| primaries on test50 with revised (v1) labels | TT T21 caption (l684) |
| E1 read without registration during the P-series | TT T21 row "E1 extension (106 cells)" (H11 l81); T17 caption "read many times before the 31 Oct policy" |
| registered E1 co-primaries from 1 Nov | TT T17 row 1 (opened 1 Nov) |
| rule: Delta > max(0.01, 2 sqrt((sd_A^2 + sd_B^2)/3)) on any primary, none worse; "robust" definition | TT l727 (T21 note, from H11 conventions) |
| 8 same physical cell, 7 neighbouring crops | TT T2 (SI l208, l209; errata l19 to l21) |
| P-series: no model selected on test (final weights, val-based choices only) | TL l24 |
| MDE crack IoU about 0.012 at 5 v 5; inactive decided by 3 cells | BR l68 |
| rule about 2 SE, one-sided p about 0.06 at 3 seeds; two-sided 95% needs 2.8 | H11 l526 |

### 5.2 SSL period
| Number | Source |
|---|---|
| five causes (regime, handicap, seeds, tuning asymmetry, data); "the rules were not the problem; the design was" | H11 l523 to l540 |
| inactive in only 2 or 4 labelled cells at 5 to 10% | H11 l530 |
| handicap: stronger labelled view, then joint BN | H11 l531 to l534 |
| P12 Dm5 - A5c -0.017 [-0.024, -0.010] | TT T21 row "P11 to P13 (BN audit)" (H11 l77; results/p12/README.md l79) |
| 3 seeds for effects 0.01 to 0.02 | H11 l535 |
| 4-step ladder on val; SSL hyperparameters never tuned | H11 l536 |
| in-domain pool 239 to 455 cells; external pool two sources, half low-contrast | H11 l537 to l539 |
| unlabelled loss about 10 x smaller; CutMix ratio 0.77 | H11 l541 |
| P13 CsM5 - A5c: inactive +0.117 [+0.042, +0.189], relF1@2 +0.033 [+0.006, +0.055], crack IoU +0.014 n.d. | TT T21 row P13 primary (H11 l76; results/p13/README.md l98) |
| BsM5 - A5c crack IoU +0.029 [+0.014, +0.041], secondary | TT T21 row "P13 Amendment 2" (H11 l76; results/p13/README.md l81) |
| BsM5 seeds 3 to 4 added after the 3-seed result | H04 l30, l348 |
| P16 n.d. at 20%, 50%, 100%; Cs recipe, CutMix off by val pick | TT T21 row P16 (H11 l83; results/p16/README.md l72 to l74) |
| P10 Cx5 - Dx5: crack IoU -0.012 [-0.026, -0.001] (robust over cells, n.d. by seeds), relF1@2 -0.027 worse by the rule; 11,938 cells; joint BN; 5% | TT T21 row "P9 / P10" (H11 l78; results/p10/README.md l48, l71); H04 l337 (P10 at 5%) |
| P15 worse on all three at 10%, 3 seeds | TT T21 row P15 (H11 l80; results/p15/README.md l45) |
| UCF-EL pretraining under the house fine-tune that erased the encoder | BR l78 |
| AL1: WORSE on all three primaries in all four cell sets | TT T21 row AL1 (H11 l90) |
| turned to 100% labels from 24 Oct (Track M); SSL framing dropped | TL l20 to l21; BR l12 |

### 5.3 Labels
| Number | Source |
|---|---|
| H11 claim 1: label version moves crack IoU more than any SSL effect | H11 l74 |
| P3 re-scoring +0.05 to +0.07 crack IoU (exploratory) | TT T21 row P3 (H11 l74; results/p3_label_versions/README.md l28) |
| P14 L3 - L3o +0.082 [+0.046, +0.129]; unseen modules (E1 cells) +0.030 [+0.012, +0.048] | TT T21 row P14 (H11 l74; results/p14/README.md l43, l92) |
| P14 L3To - L3o -0.004 (recovers 0%) | TT T21 row P14 tolerance (H11 l79; results/p14/README.md l35) |
| label-safe augmentation = flips, rot90, brightness / contrast only | BR l42 |
| P6 crack AP +0.020, inactive AP +0.028; 10% to 100% crack IoU +0.075, inactive +0.135 | TT T21 row P6 (H11 l86; results/p6/README.md l37, l123, l124) |
| Track D Tc - R relF1@2 +0.030 [+0.020, +0.042], oracle-selected, 5% base + 12 cells | TT T21 row Track D (H11 l93; trackD/labelset_results.md l55) |
| release moves PF relF1@2 (+0.025) by more than CS_D4 - PF (+0.0222) | Chapter 4 (TT T3c; TT T7a) |

### 5.4 Encoder erasure and PF
| Number | Source |
|---|---|
| house recipe: Adam lr 1e-3, coupled weight decay 1e-4, 20,000 steps | BR l42; H04 l409 |
| cosine layer3 0.005 to 0.018, layer4 -0.001 to 0.001; ImageNet and MIM inits; 5% and 100% | TT T21 row "Encoder audit" (H11; H19 l148 to l149) |
| at step 2,000: layer3 / layer4 cosine 0.070 / 0.003 | H19 l154 |
| MIM5 / DDeP5 n.d. at 5% under the house fine-tune | TT T21 row "MIM5 / DDeP5" |
| MIM5 tested conv1 / layer1 transfer only | H19 l103, l152 to l153 |
| PF: frozen 1k steps, ramped to 0.1 x lr over 1k steps, encoder weight decay 0 | H04 l410; BR l43 |
| PF layer3 / layer4 cosine 0.996 / 0.997 at 2k | H19 l155 |
| PF2, seeds 5 to 9, E1 opening #1: E1 inactive 0.0481 to 0.2371, +0.1890 (thr 0.0433) BETTER; replicated, same E1 cells | TT T21 row "PF2 (gaint, seeds 5 to 9; E1 opening #1)"; H20 l113, l117 |
| test relF1@2 +0.0117 / +0.0120 (floor 0.0100), pass by 0.0017 / 0.0020, a few cells | TT T21 row "PF2 (test)" |
| E1 crack recall n.d. (+0.0271, thr 0.0370) | TT T21 row "PF2 (E1 crack recall)" |
| PF2E E-PF - E-house E1 inactive +0.2141 [+0.0303, +0.3820] PASS; test n.d.; not independent of #1 | TT T21 row PF2E; TT T17 row 4 |
| B6: PF - house pooled out-of-fold inactive -0.0144 [-0.0977, +0.0570]; an in-distribution gain as large as the E1 gain excluded; 2 seeds | TT T21 row B6 |
| RN50-PF - SUP100-PF test inactive -0.0289 (thr 0.0251) WORSE | TT T21 row "PF2 (ResNet-50 under PF)" |
| PF adopted for its behaviour on unseen modules (PF2 opening) | W1C l56 |
| prior looks list includes the 7 registered openings | V8 l138 |

### 5.5 Other arms
| Number | Source |
|---|---|
| SKR w 1: E1 relF1@2 +0.0590 (thr 0.0392) BETTER; test crack IoU -0.0136 (thr 0.0100) WORSE; FAIL | TT T21 row THIN-B3 SKR; T17 row 2 |
| SKR2 w 0.1: +0.0364 (thr 0.0351); ~10% family-wise false-BETTER over 7 co-primaries | TT T21 row SKR2 |
| SKR2E: FAIL by G2a, G2b; not independent of #5 | TT T21 row SKR2E; T17 row 6 |
| SKR2C seeds 10 to 14, 14 Nov: replication not shown, seed-aware CI [-0.0015, +0.0590] | TT T21 row SKR2C; T17 row 7 |
| soft clDice FAIL; scuff class train IoU 0.000 in all 5 seeds | TT T21 rows THIN-B3 CLD, B3 |
| HC: E1 relF1@2 +0.0135 (thr 0.0429), all n.d. | TT T21 row HC |
| A8: -0.0243, lower bound -0.0463, GO needs > 0, KILL, "no sign of a gain"; 2 seeds; F51; no test, no E1 | TT T21 row A8 |
| Track M R2 Dice-12 -0.0106; R3 ResNet-50 inactive -0.0251 | TT T21 row "Track M R2 to R5" |
| +107 E-SCDD cells n.d.; 2 x resolution n.d. | BR l81, l84 |
| protocol_100: MIM100-PF and CP100 not supported at 100% | TT T21 rows protocol_100 openings 1 and 2 |
| ensemble FINAL - single +0.018 [+0.013, +0.025], clean test, locked protocol, val-only choices | TT T21 row "Track M FINAL" |
| "the one clear win" | BR l85 ("the only clear win") |

### 5.6 What the period taught
| Number | Source |
|---|---|
| test50 scored in every experiment before 24 Oct, uncounted; 18 counted openings to 14 Nov | P02 l56 |
| 3 cells hold 59% of inactive px; noisy cell wrecks about 1 run in 6 | BR l24 |
| 7 registered openings 1 to 14 Nov; 3 looks at one contrast; #4 not independent of #1, #6 not of #5; pre-policy reads not counted | TT T17 caption and rows; V8 l138 |
| one registered opening, candidates fixed before any number | P02 l60 |
| 0.012; 3 cells | BR l68 |
| ~10% family-wise false pass over 7 co-primaries | TT T21 row SKR2 |
| 532 cells out of fold, 5 seeds, A/A margin, one primary per arm | TT T4 |
| 70% of the best model's crack IoU loss within 2 px | BR l36 |

## 2. Judgement sentences kept (S)
1. "It is short because its numbers decide nothing in this thesis, and it is here because its measurement failures are the reasons for the protocol" (OUTLINE s1).
2. The four "cannot show" items of 5.1 (TT T21 caption; OUTLINE s3 G-W12; BR l68; H11 l526). Item 3: "both sets were seen so often that later choices cannot be called blind to them" is my judgement.
3. "``Supported'' under this rule is not ``confirmed'' under the protocol." (G-W12.)
4. "An audit of the design, not of the decision rule, found five causes" (H11 l523 to l529, S in source).
5. "Our reading: SSL helped this model at 5% labels and no gain was detectable from 20% labels up, for the recipe that was run. This closes only those conditions ... It does not show that SSL fails on EL images." (OUTLINE A9; BR l13.)
6. "The clearest pattern of the period was that the label version moved crack scores more than any SSL effect did." (H11 claim 1, l74.)
7. "This finding changed the reading of earlier nulls." (H19 l103, l152 to l153.)
8. "PF became the baseline ... because of these E1 reads. The choice of the baseline was therefore informed by E1" (W1C l56; V8 l138). Not stated in OUTLINE; added for honesty.
9. "This was the one clear win of the period." (BR l85.)
10. The four lessons of 5.6 (OUTLINE 5.5; P02 l7 to l19).
11. Closing "What survives from the period are mechanisms and directions, each measured under its own conditions".

## 3. Placeholders and citations
- Chapter 5: \PENDING 0; \CITE 1 (`ALHVR, Lei et al., ICCV 2025`: title and venue on disk in `/home/yugma/mtp/research/literature/notes/B01_alhvr2025.md` l1 to l2, with the mlanthology / CVF open-access URLs; no DOI or arXiv id on disk, not verified); \FIG 1 (F8).
- Citations used: refs_extra.bib `zhou2018unetpp`, `kirchhoff2024skeletonrecall`; new in `chapters/ch05_legacy.bib`: `tarvainen2017meanteacher` (arXiv 1703.01780; on disk HB/sources/literature/papers_index.md l38), `yun2019cutmix` (arXiv 1905.04899; found on the arXiv API, not on disk), `brempong2022ddep` (arXiv 2205.11423; H19 l190), `simeoni2025dinov3` (arXiv 2508.10104; ML P190). Authors and titles checked against the arXiv API on 23 Nov. **main.tex l58 does not list `chapters/ch05_legacy` (nor `chapters/ch04_data`).**
- Cross-references used: ch:protocol, ch:methods, ch:e1_result, ch:intro, ch:data, sec:data-labels, sec:data-split, sec:data-sets, sec:data-f1, tab:T2, T4, T5, T16b, T17, T21.

## 4. Appendix note (app_t21_note.tex), sources
| Statement | Source |
|---|---|
| 38 rows, 10 Oct to 14 Nov 2026 | TT l65, l680 |
| legacy split; primaries on test50 with revised labels unless stated; clean = 49 cells | TT T21 caption l684; H04 l396 |
| rule, "(thr x)", "robust" | TT T21 caption and note (l684, l727) |
| Oracle-selected (Track D) | TT T21 row Track D |
| KILL = GO rule needs > 0; "no sign of a gain", not "worse" | TT T21 row A8 |
| not comparable; test50 scored in every P-series run | TT T21 caption l684 |
| arm codes A, B, C, D, m, x, s, M, g, c, L0 to L3, o / T, U, D (P17) | H04 l301 to l318 |
| SUP100, SUP100-g, PF, SUP100-PF, MIM100-PF, CP100 | H04 l394, l405, l407, l410 |
| Tc / R | H04 l401 |
| SKR01 = Skeleton Recall at w 0.1 | HB/24_frontier_benchmark_16_to_18_nov.md l57; HB/00_START_HERE.md l22 |
| every row traces to H11 and the primary record; no row rests on the handbook alone | TT T21 caption l684; GAPS G-N14 |
- The note is a \chapter (app:t21) because main.tex inputs it after the "Related-work table" appendix chapter; a \section would land
  inside that chapter. Change to \section if the lead moves the \input into the "Tables" appendix.

## 5. Points for the lead
- OUTLINE 5.2 heading "Labels over methods": the source (H11 claim 1) says "more than any SSL effect", not "more than any method";
  PF's E1 inactive gain (+0.1890) is larger than the label effect. The chapter uses the narrower wording.
- OUTLINE 5.3 says the house fine-tune erases layer3 / layer4 "(cosine to init about 0)"; the T21 values are layer3 0.005 to 0.018,
  layer4 -0.001 to 0.001; the chapter copies them.
- OUTLINE 5.4 lists "ResNet-50 worse on inactive" and "5-seed ensemble +0.018 crack IoU" without the test50 tag; the chapter adds
  "in-distribution, known leakage, context only" to the ensemble sentence, and states it once for all test50 numbers in 5.1.
- Not in OUTLINE but added for honesty: PF was adopted as the baseline because of E1 opening #1 (W1C l56), so the baseline choice is
  one of the prior E1 looks.
