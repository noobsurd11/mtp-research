# NOTES for ch04_data.tex (Chapter 4, "Data, labels and the dataset audit"; draft 23 Nov 2026)

T = `/home/yugma/mtp/research/team_2026-11-12_frontier`. Short names and md5 (first 8) of every file read for this chapter:
TT `thesis/THESIS_TABLES.md` 81c54378 (table cells; SOURCES.tsv 76814c96 traces each cell to its file and line);
BR `BRIEF.md` bc06edd2; P02 `benchmark/PROTOCOL_v0.2.md` b8b7f66a; P10 `benchmark/PROTOCOL_v1.0.md` eeb3379a;
AUD `dataset_audit/REPORT.md` 9d7e0d27; RAT `dataset_audit/rater/RESULT.md` c119a04f; SI `results/stageC/SPLIT_INTEGRITY.md` 26b3c76a;
LK `results/C3_LEAK_READ.md` 43e8009e; LAB `benchmark/LABELS_V11.md` 70872c46; OR `harness/final/opening/OPENING_RULE.md` 065a7ddd;
V8 `results/final_opening_read/verdict.txt` bbb5f3b4; TL `benchmark/test_openings.md` 2629ed93; W1C `results/W1C_READ.md` 3a437100;
H03 `/home/yugma/mtp/research/handbook/03_datasets_and_splits.md` a4cfe1db; LOG `log.md` df3ca2a2 (entry 22 Nov 12:49, l363).
No sealed label, mask, image, dump or prediction was read; verdict.txt is a text result file.

## 1. Every number in the chapter, with its source

### Intro and recipe paragraph
| Number / phrase | Source |
|---|---|
| PF = U-Net++ / ImageNet ResNet-34, encoder-preserving fine-tune; HOUSE plain fine-tune; HRNET = HRNet-W18 U-Net++; SWAD readouts; C3X = HRNet + SWAD | TT l19 to l23 (conventions); AUD l8 to l9 |
| 25 models per pool cell, five recipes x seeds 5 to 9 | AUD l8 to l9 |

### 4.1 Images, sources and cell sets (Table T1)
| Number | Source |
|---|---|
| 512 x 512 px, grayscale, one cell plus parts of neighbours | BR l16 |
| 582 cells = 478 / 54 / 50, 24 classes (12 structural, 12 defects) | BR l20; TT T1 row 1 (SOURCES: P02 l8) |
| five sources, different contrast and label conventions | BR l23 |
| pool ARTS 182, BMRK 50, CFVS 169, CSIR 114, SDLE 17 | TT T1 (P02 l33) |
| BMRK = ELPV cells, downscaled and padded | BR l23 |
| 816 real labelled cells, 787 unique physical cells, 463 module groups, 93 synthetic files excluded | TT T1 (P02 l29) |
| P532 = 478 + 54 | TT T1 (P02 l33) |
| test50: 50 cells, 48 image ids | TT T1 (SI l202) |
| hand-picked; 48 with crack, 16 with inactive; 3 cells hold 59% of inactive px | BR l24 |
| 46 crack cells under v1.1 (48 under v1) | TT T3b (LAB l18) |
| scored in every experiment before 24 Oct, uncounted; 19 counted openings 24 Oct to 21 Nov 2026 | P10 l114; TT T1 (TL l26) |
| last opening (#19) a public table that decides nothing | P10 l27, l115 |
| E1 = release 20221008 cells not in the 582 and not in the unlabelled pool | OR l29; P10 l53 |
| 106 cells, 71 image ids, 66 CSIR, 5 BMRK | TT T1 (SI l191) |
| 101 of 106 CSIR; 62 half-cut (pool has none); 10 inactive; crack in 32 | TT T1 (V8 l140) |
| 44 full cells | P10 l53; OR l29 |
| strata full 44 / 24, half-cut 62 / 47, crack 32 / 21, crack-free 74 / 55 | TT T1 (V8 l55 to l58) |
| "unseen modules (supported, not proven)" | SI l200; TT T2 |
| E1 training data for the few-shot track after opening #9; no later zero-shot claim | P10 l28, l126 |
| 167 forbidden stems = legacy test 50 + ext117 117 | TT T1 (P02 l62) |
| ext117 = the 117 cells first listed for E1 from release 20221008; E1 = 106 after removing 11 unlabelled-pool cells | H03 l342, l344; OR l29 |
| 117 E-SCDD newly annotated cells; 51 full (F51), 36 half (H36) used as validation only | BR l26; P10 l54 |
| unlabelled pool 11,938 CSIR / ARTS crops | BR l27 |
| sealing; duplicate tool reads sealed images as pixels only, writes pair lists | P10 l122 |
| BenchmarkEL no licence file; ELPV CC BY-NC-SA 4.0; pool-trained models research-only as trained | P10 l86 to l88 |

### 4.2 Label sets (Tables T3a, T3b, T3c)
| Number | Source |
|---|---|
| v0: 20211104 masks_coded, values 0 to 23, no ignore; test50 public table only | TT T3a (OR l75 to l76) |
| v1: E-SCDD mask (577 cells), classes >= 24 set back, 20211104 mask for 5 missing cells | TT T3a (LAB l7) |
| v1.1: scuff / star to ignore (255); one BMRK cell given back its 20220723 mask; in v1 it carried another cell's mask | TT T3a (P02 l39); LAB l10 |
| ignore pixels not scored | TT T3a (P02 l41) |
| E1 set: class 24 (sp mono) to 2, classes 25 to 28 to ignore | TT T3a (OR l72); OR l71 to l72 |
| E1 labels about 1.5 x wider than pool labels | P10 l68 (citing harness/t3b/T3B_RULE.md s8) |
| 16 of 478 train cells change; 3,484 px (3,246 / 238); val 0; test 2 cells, 236 px | TT T3b (LAB l16 to l18) |
| train crack cells 209 to 206; inactive untouched | TT T3b (LAB l16, l20) |
| v1 labels scuff as crack on 649 px in 6 train cells | LAB l59 |
| crack-free 303 of 532, 226 of 416 (v1.1) | P10 l433 |
| PFV1 - PF: relF1@2 -0.0014 [-0.0099, +0.0064]; strict +0.0004 [-0.0058, +0.0069]; inactive -0.0140 [-0.0690, +0.0362]; mIoU-R13 -0.0020 [-0.0081, +0.0038]; 2 seeds | TT T3c (W1C l59, l60) |
| 169 of 532 cells change; crack px 260,084 to 307,546 (+18%) | TT T3c (AUD l99) |
| PF strict 0.320 vs 0.365 (+0.045); relF1@2 0.822 vs 0.846 (+0.025) | TT T3c (AUD l101) |
| inactive unchanged; contrasts move at most 0.008; no pass changes | AUD l102; TT T3c |
| models trained on v1.1 favour v1.1 | AUD l103 |
| C2 recipe on CV5 (CS_D4 - PF) +0.0222, selection-biased | TT T7a row (c) |

### 4.3 Module identity and split integrity (Table T2)
| Number | Source |
|---|---|
| cv5v2: 330 module groups | TT T1 (P02 l49) |
| audit over 700 image ids | SI l17; P02 l262 |
| serials, full run under the pre-set rule: 20 of 20 same-serial pairs also matched by pixels, 0 of 2,906 different-serial pairs | SI l92 (section 3a, full-run cross-check; corrected 23 Nov from "calibration"); P02 l262 |
| masked SIFT, RANSAC similarity, grid-shift rule | SI l17 to l22 |
| rule written before the full run; thresholds set on calibration pairs (in-sample) | SI l8, l30, l34 |
| 561 physical modules (rule B), 527 under the pre-set rule (over-links pool-only ids); BMRK, SDLE not decidable | SI l301; P10 l98 |
| rule B post hoc, changes nothing for pool or sealed cells | SI l283 |
| 24 modules span two folds; 91 cells (ARTS 48, CFVS 32, CSIR 11); 22.7% of crack px | TT T2 (P02 l262) |
| 4 same cell, 38 neighbouring crop, 49 same module no shared area | P02 l262; SI l302 |
| affected minus unaffected, same source and cell type: +0.072 crack IoU, +0.059 relF1@2 | SI l244 (cv02 values) |
| descriptive not causal; modules imaged several times, stress-test modules with large cracks; neighbouring crops score lowest | SI l246 |
| upper bound about 0.016 crack IoU, about 0.013 relF1@2 on the 532-cell headline | SI l246 |
| exclusion read: PF 0.347 / 0.826 (532: 0.365 / 0.844); no contrast changes sign | TT T2 (P02 l262) |
| cv5v3: 285 groups, none spans folds; 47 cells move; 107 / 110 / 103 / 101 / 111 | TT T1 (P02 l263) |
| cv5v3 built before any 5-seed run | P02 l262 item (d) |
| BMRK grouped by image id (stated limit); SDLE held out in folds 0, 2, 4 only | P02 l263 |
| clean cells: 116 excluded (91 + 8 + 17 SDLE), 416 left, same fold in both splits; reads print 532 and 416 | TT T1 (P02 l263); P10 l99 |
| leakage read registered before any cv5v3 run | LK l3 |
| design: pooled DiD on affected_unmoved (69 cells) against the 416 clean, unmoved cells | LK l6 |
| PF strict -0.0041 [-0.0136, +0.0069]; relF1@2 +0.0026 [-0.0092, +0.0174] | TT T2 (LK l11, l12) |
| every interval holds 0, both arms, both strata: "not separated" | LK l21 |
| upper bound +0.07 crack IoU lies outside the PF intervals (description, not conclusion) | LK l23 |
| 61 pool images, 35 pairs, 16% of crack px, same cv5v3 group | TT T2 (AUD l56 to l57) |
| no E1 image id linked; largest inlier count 7 | TT T2 (SI l192, l193) |
| about a third of image-id pairs testable; half-cut ids and BMRK have no testable counterpart | P02 l262; SI l196, l199 |
| test50: 8 same physical cell (7 by pixels, 1 by cells.tsv link only), 7 neighbouring crops, 19 same module, 16 with neither link | TT T2 (errata l19 to l21; SI l207 to l210) |
| test50 in-distribution with known leakage | TT T2 (V8 l137) |

### 4.4 Line-width convention (T19a F1, T19b)
| Number | Source |
|---|---|
| labels 1 to 2 px on a dark line about 4 px wide | BR l33 |
| self IoU shifted 1 px 0.483, 2 px 0.249, centreline 0.465, 3 px 0.605; 229 crack cells; relF1@2 1.0 | AUD l26 to l27 |
| PF strict 0.233 / 0.365 / 0.414; relF1@2 0.824 / 0.846 / 0.849 | TT T19a F1 (AUD l24 to l25) |
| HOUSE - PF strict +0.0179 PASS, +0.0015 centreline, +0.0367 3 px | AUD l29; TT T19b |
| SWADBN - PF +0.0180 PASS, +0.0047, +0.0342 | AUD l30; TT T19b |
| HRNET - PF strict +0.0008, -0.0109 on 3 px; relF1@2 +0.0104 PASS, +0.0073 on 3 px | AUD l31; TT T19b |
| relF1@2 contrasts move at most 0.0031 | AUD l32; TT T19a |
| C3X - PF passes under all four variants | TT T19b; AUD l158 |
| convention band +-0.019 definition | TT T4 row "Strict crack IoU" |
| variants synthetic; 3-px = BMRK convention | AUD l34 |

### 4.5 Other faults (T19a, T19b)
| Number | Source |
|---|---|
| centre cell 25 to 30% of non-padding px; BMRK, SDLE single cells, 75% padding | AUD l52 to l53 |
| 57% crack px, 71% inactive px outside centre cell | AUD l54; TT T19a F3 |
| 117 of 229 crack cells, 28 of 48 inactive cells without centre-cell defect px | AUD l55 |
| recall@2 0.794 outside vs 0.844 inside | AUD l58 |
| declared post hoc, checked by eye on 7 images | AUD l60 to l61 |
| window is the scoring unit | LOG l363 (ruling R4 (a)); P10 l135, l467 |
| double annotation: strict 0.259, relF1@2 0.829; PF 0.365 / 0.846; vote 0.398 / 0.868 | AUD l39 to l41; TT T19a F2 |
| same physical cell pairs: strict 0.16 to 0.37, tolerant F1@2 0.77 to 0.95 | AUD l42 to l43 |
| 63% missed by >= 20 of 25; 7% by <= 5 | AUD l44 to l45 |
| shared misses include shared blind spots | AUD l47 |
| spurious inactive: 63 regions, 18 cells, 31,039 px, 10.9% | AUD l67 to l68; TT T19a F4 |
| ignoring them: PF inactive 0.504 to 0.574 | AUD l75; TT T19a F4 |
| raters: spurious inactive 30 of 40 model error, 5 of 40 label error; missed inactive 5 of 6 label error | RAT l38 to l39 |
| 33 of 285 groups, Kish n_eff 12.9 | AUD l74 |
| inactive contrast intervals about +-0.05 to +-0.06 | AUD l163 |
| 26 of 47 inactive cells with cracks inside inactive | AUD l71 to l72 |
| report inactive as labelled | LOG l363 (ruling R9 (a)) |
| region counts and five seeds for inactive claims | AUD l81 |
| missed crack: 128 segments, 42 cells, 5,436 px, 1.8%; spurious: 53 components, 28 cells, 7,567 px, 2.5% | AUD l84 to l87; TT T19a F5 |
| raters: three runs of one model, 60 planted items, sens 29/30, spec 30/30 each | RAT l7, l23, l27; TT T19a |
| 78 image-supported crack candidates; 18/78; corrected 0.244 [0.105, 0.436] | RAT l32; TT T19a F5 |
| most of the rest ambiguous (46 ambiguous) | RAT l36, l44 |
| PF relF1@2 0.846 to 0.864 when candidates ignored; no contrast moves > 0.003 | AUD l92 to l93 |
| detector recall unknown | AUD l94; GAPS G-N12 |
| width ARTS 1.59, CFVS 2.06, CSIR 2.25, BMRK 3.09; 29.6% | AUD l107 to l108; TT T19a F7 |
| label about half the visible line (label / trough FWHM 0.45 to 0.63) | AUD l109 |
| 10 of 24 classes in one source; splice ARTS only; corrosion SDLE only | AUD l111 to l112 |
| source classifier 0.94 (chance 0.20); 0.85 from 8-bin power spectrum | AUD l119 to l120; TT T19a F8 |
| 125 of 285 groups, n_eff 24.1 | AUD l128; TT T19a F9 |
| greedy removal: HOUSE 0 after 4; HRNET under M after 1, 0 after 17; SWADBN 0 after 24; C3X 0 after 31 | AUD l129 to l131; TT T19b |
| 2 images noise sigma > 10; 109 of 532 block grid; 19 under-exposed CSIR | AUD l137 to l138 |
| 41 cross-group hash pairs, ARTS / CSIR same-position look-alikes, no new leak | AUD l147 to l148; TT T19a F11 |

### 4.6 Consequences
| Number | Source |
|---|---|
| absolute levels move 0.02 to 0.18 | AUD l161 |
| relF1@2 contrasts move at most about 0.003 | AUD l159 |
| second annotation; planted errors for detector recall | AUD l182 to l187 |

## 2. Judgement sentences kept (S), with their basis
1. "The audit comes before the protocol on purpose: its findings ... are the reasons for the rules of Chapter 6." (OUTLINE s1.)
2. "test50 ... serves as context only." (OUTLINE s0 rule 4; V8 l137.)
3. "The label set matters at scoring time, not at training time." (W1C l60: "The v1.1 fixes matter for what is scored ..., not for what the model learns".)
4. "Our reading is that a published crack level means little unless its release and label set are stated." (AUD l104, S.)
5. "The comparison is descriptive, not causal." (SI l246, S.)
6. "We read the strict-IoU gains of the arms that draw wider cracks (HOUSE and the weight-averaged arms) as convention effects, and relF1@2 as the crack metric that should decide." (AUD l35 to l36, S.)
7. "we treat this as a suggestion that crack labels limit what can be measured, not as an estimate of a ceiling" (AUD l166 to l169, "Suggestive"; G-W10: "one double annotation" kept; the AUD l48 wording "models already sit at the agreement level" is NOT used).
8. "These candidates are not label noise" (inactive spurious candidates; RAT l47 to l50, S). Wording is strong; the basis is 30 of 40 model error by the raters. Softer alternative if wanted: "Most of these candidates are not label errors".
9. "Label errors exist, and they are a minority of the image-supported candidates." (RAT l32, pre-registered reading, MEASURED.)
10. "This shows that a shortcut is available, not that a model uses it." (AUD l124.)
11. "Together these findings motivate the per-source width guard of the protocol." (AUD l115.)
12. "Greedy removal is a worst case, not a sampling distribution" (AUD l132.)
13. The five consequences of 4.6 (AUD l159 to l164; P10 l82 implications, made protocol text by the 22 Nov rulings, LOG l363).

## 3. Placeholders and citations
- \PENDING: 0. \CITE: 0. \FIG: 5 (F3, F4, F5, F6, F7; each with \label{fig:Fn} inside the caption).
- Citations: refs_extra.bib keys `zhou2018unetpp`, `wang2021hrnet`. Keys defined in `chapters/ch06_protocol.bib` (same fields as I
  checked against Crossref / arXiv on 23 Nov; not repeated in my .bib): `pratt2023benchmark` (doi:10.1016/j.sasc.2023.200048),
  `deitsch2019elpv` (doi:10.1016/j.solener.2019.02.067, arXiv 1807.02894), `hanifi2025bridgingdatagapspatially` (E-SCDD, arXiv
  2511.09604). New keys in `chapters/ch04_data.bib`: `northcutt2021confident` (doi:10.1613/jair.1.12125),
  `rottmann2023labelerrors` (doi:10.1109/wacv56688.2023.00323), `barz2020duplicates` (doi:10.3390/jimaging6060041); ids from AUD
  l14 to l19, fields checked against Crossref on 23 Nov. **main.tex l58 lists neither `chapters/ch04_data` nor
  `chapters/ch06_protocol`; add both.** ch08_e1_result.bib defines the same Pratt 2023 paper as `pratt23`: one key should go.
- Cross-references assume the labels ch:protocol, ch:methods, ch:legacy, ch:e1_result, ch:t3b, ch:background (from the main.tex file
  names and the brief's ch:<slug> rule).

## 4. Points for the lead
- OUTLINE 4.2 and T20 #19 say the release "moves absolute levels more than any method". On relF1@2 this is now narrow: release
  +0.025 against CS_D4 - PF +0.0222 (T7a), and P10 l36 notes CB_D4 - PF +0.0243 (0.97 of the shift, derived there). The chapter
  states the comparison with the C2 recipe only and avoids "more than any method".
- OUTLINE 4.4 lists only strict-IoU contrasts changing; T19b also shows one relF1@2 verdict change (HRNET - PF, +0.0073 no pass on
  3-px labels). The chapter states it.
- The rater check names the model (claude-opus-5-5) in RAT l7; the chapter says "three runs of one multimodal model". Decide
  whether the thesis names the model.
- BR l23 source counts (ARTS 195 ... SDLE 18) are over the 582 cells; the chapter uses the P532 counts of T1 only.
