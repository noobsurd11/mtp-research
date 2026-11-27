# NOTES for ch08_e1_result.tex (Chapter 8, Final model and the sealed E1 result)

Written 23 Nov 2026. Read only result text files, docs and tables; no E1 or test50 dump, label or prediction.

## Source keys (path relative to T = ~/mtp/research/team_2026-11-12_frontier; md5 prefix as read 23 Nov)
- V8 = results/final_opening_read/verdict.txt (bbb5f3b4)
- R8 = results/final_opening_read/read_e1/read.txt (82cea48a)
- FOR = results/FINAL_OPENING_READ.md (16e3f1e7)
- ER = results/FINAL_OPENING_READ_ERRATA.md (af55915f); its wording wins over FOR
- OR = harness/final/opening/OPENING_RULE.md (065a7ddd)
- ADD = harness/final/FINAL_RULE_ADDENDUM_1.md (be50433b)
- SI = results/stageC/SPLIT_INTEGRITY.md (26b3c76a)
- EL = ../team_2026-10-31_next/e1_openings.md (52432548), the E1 openings ledger
- TT = thesis/THESIS_TABLES.md (81c54378); TEX = thesis/thesis_tables.tex (d92b3f0b)
- GP = thesis/GAPS.md (86108083); P10 = benchmark/PROTOCOL_v1.0.md (eeb3379a); BR = BRIEF.md (bc06edd2)

## Every number in the chapter, with its source
### Intro and 8.1 (registration)
| Number / fact | Source |
|---|---|
| 106 cells; 101 of 106 CSIR; seeds 5 to 9; OP-A only | V8 l10, l140, l142; TT T8 caption (l261) |
| "supported, not proven" | SI l200 |
| opening #8 (E1), #19 (test50) | V8 l1 |
| 532 pool cells, v1.1, seeds 5 to 9, 20,000 steps (step 20000) | OR l33 to l35 |
| swad readout = uniform average over steps 10,000 to 20,000, no BN re-estimate | OR l42; P10 7.3 (l352) |
| D4 = 8 views (rot90 0 to 3 quarter turns, with and without flip), softmax averaged | OR l42 |
| C1-D4 included because (a) replicated | V8 l6; OR l54 to l55; TT T7a row (a) l226 |
| deployable = C2 seed 5, designated before any number | OR l47 |
| C2 entry class (c), P = whole candidate vs PF one view; only C1-D4 separates | V8 l141; P10 l221 |
| no E1 number for HRNet alone or SWAD alone | GP l13 (G-N3) |
| rule written before any number of the final models | OR l3 to l5 |
| registered 11:22:35 IST, 21 Nov 2026; ledger rows before any dump | FOR l8 to l9; V8 l3; TT T8 caption |
| 30 dumps, one GPU model (RTX A6000), fp32 | FOR l11, l13; R8 l1 |
| read once 12:02:30 to 12:06:09, rc 0 ("without error") | FOR l13 |
| no threshold, bias, class weight or view weight on a sealed cell | V8 l2; OR l45 |
| full-pool runs: final validation stop, latest checkpoint at step 18,000, resumed under F2 | ADD l8 to l14; V8 l143 |
| CPU resume bit-equal; GPU reproducible only up to atomic-accumulation noise | ADD l24 to l28 |
| selection: swad after c3x read, D4 from B5, pool cells only; swad_bn NOT CONFIRMED | V8 l139; ER l29; OR l190 to l193 |
| kept D4 after (b) NOT CONFIRMED, NO LOSS | V8 l3, l7; TT T7a row (b) l227 |
| C1 / C2 have no held-out score of their own | GP l16 (G-N6) |
| prior looks: test50 18 counted openings ...; E1 7 registered openings (3 looks at one contrast) ... R0, 15 Nov; final models never scored | V8 l138 (reference wording per ER l28) |
| pre-opening power: SE about 0.019 (range 0.017 to 0.021, OR l127 to l128); 80% power at about 0.048 to 0.059 (2.8 x SE over that range); "NOT CONFIRMED, interval holds 0" likeliest | OR l123 to l131 (S statement of the rule, stated as what the rule recorded) |
| realised SE 0.0265 | V8 l11 |

### 8.2 (primary)
| Number | Source |
|---|---|
| P definition, pooled counts over scored px of 106 cells | OR l80 to l82 |
| seed-aware bootstrap: 71 clusters, 5 of 5 models per arm, 2,000 draws, 95% percentile | OR l83 to l86; TT T4 row "Interval" |
| M = 0.010, fixed, not re-estimated on E1 | OR l87; TT T4 row "Margin M" |
| CONFIRMED rule; G1 0.85 to 1.15 pooled; G2 CSIR (only source with >= 40 cells); G3 <= 1.5 x; G4 >= -0.010 | OR l91, l96 to l99; TT T8 rows |
| OP-A only deviation; OP-W needs held-out folds; G1 / G2 take its role | V8 l142 |
| P = +0.0430 [+0.0013, +0.1043] (SE 0.0265) | V8 l11; TT T8 row 1 |
| G1 1.013 (C2 0.463, C1 0.458); G2 1.013; G3 2421 vs 3218, ratio 0.752; G4 +0.0249 | V8 l12 to l15; TT T8 |
| levels C1 0.4467 [0.4387, 0.4574], C2 0.4897 [0.4656, 0.5067] | R8 l6, l7; TT T8 "Levels" row, T11a l332, l333 |
| fixed-model [+0.0067, +0.1007] | V8 l19 |
| "statement about these trained models, not the recipe" | OR l105 |
| relP@2 +0.0524 [-0.0226, +0.1373]; relR@2 +0.0371 [-0.0058, +0.0948]; relF1@1 +0.0441 [+0.0032, +0.1038] | V8 l20; TT T8 |
| strict crack IoU +0.0263 [+0.0022, +0.0651], outside band +-0.019 | V8 l18; TT T8 |
| lowest C2 model seed 5 0.4656; highest C1 model seed 7 0.4574 | V8 l28, l25; TT T11b l354, l351 |
| A/A +0.0022 [-0.0425, +0.0507], SE 0.0225 | V8 l50; TT T9 last row |
| MDE 2.80 x 0.0265 = 0.0742, about 0.074 (DERIVED; two-sided 0.05, power 0.80, normal approx.) | TT T8 note (MDE bullet); GP l14 (G-N4); SOURCES.tsv derived = yes |
| claim text (with scope) and "Not claimed" list | OR l107 to l110; TT T20 claim 1 |

### 8.3 (strata)
| Number | Source |
|---|---|
| full 44 / 24: +0.1464 [+0.0420, +0.2278]; C1 0.4808, C2 0.6272 | V8 l56; R8 l78, l79; TT T10 |
| half-cut 62 / 47: +0.0110 [-0.0289, +0.0722]; C1 0.4312, C2 0.4422 | V8 l55; R8 l60, l61; TT T10 |
| pool holds no half-cut cell | V8 l140 |
| CSIR 101 / 66: +0.0433 [+0.0015, +0.0984] | V8 l54; TT T10 |
| BMRK 5: C2 0.0000 [0.0000, 0.0000], C1 0.1843 [0.0000, 0.9216]; C1-D4, C3, E-PF 0.0000; delta -0.1843 [-0.5529, +0.0000]; rests on 5 cells | ER l23 to l25; V8 l53; R8 l24 to l29; TT T10 |
| crack cells 32 / 21: +0.0340 [-0.0114, +0.0862] | V8 l57; TT T10 |
| crack-free 74: relF1@2 0 for every arm | R8 l114 to l119; TT T10 |
| G3 ratio 0.752 | V8 l14 |

### 8.4 (printed beside)
| Number | Source |
|---|---|
| C2 - C1-D4 +0.0451 [+0.0173, +0.0699], fixed [+0.0278, +0.0597] | V8 l49; TT T9 row 1 (l292) |
| "Most of the gain is the model." / "The D4 part is not resolved on E1." | ER l16, l17 (verbatim) |
| C1-D4 - C1 -0.0021 [-0.0423, +0.0575]; inactive +0.0908 [-0.0019, +0.1936]; mIoU-R13 +0.0206 [+0.0017, +0.0419] | V8 l48; TT T9 |
| CV5 PF_D4 - PF +0.0134 | ER l17; TT T7a row (a) l226 |
| C3 - C2 -0.0025 [-0.0254, +0.0157] | V8 l45; TT T9 |
| C3 - C1 +0.0405 [-0.0044, +0.1108] | V8 l43; TT T9 |
| C3 - E-PF +0.0383 [+0.0007, +0.0904]; C3 costs 8 x E-PF | V8 l44; TT T9 |
| E-PF - C1 +0.0023 [-0.0165, +0.0279] | V8 l47; TT T9 |
| S4 +0.0189 [-0.0403, +0.1068] | V8 l46; TT T9 |
| seed 5 lowest C2 model on E1 (0.4656) | V8 l28 to l32; FOR l71 ("the weakest C2 seed on E1"); TT T11a C2S5 row |
| seed spread 0.4656 to 0.5067 | R8 l7; TT T11a |

### 8.5 (inactive, classes, components)
| Number | Source |
|---|---|
| 10 inactive cells | V8 l17, l140 |
| inactive +0.0996 [-0.0310, +0.2162]; fixed [-0.0000, +0.2007] | V8 l17; TT T8 |
| levels 0.2909 / 0.3905 | V8 l69; TT T12a |
| inactive region recall 0.557 to 0.829; precision 0.388 to 0.412 | V8 l80, l81; TT T12b |
| S4 inactive +0.1393 [+0.0009, +0.2103] | V8 l46; TT T9 |
| CV5 inactive CS_D4 - PF +0.0328 [-0.0128, +0.0826] | TT T7b l252 |
| mIoU-R13 +0.0249 | V8 l15 |
| border 0.5436 / 0.6823; frame edge 0.6640 / 0.7109; sp multi 0.6629 / 0.6918; sp mono 0.2434 / 0.1658; gridline 0.2314 / 0.2213; material, edge dark 0.0000; splice 0.0000 (C1), n/a | V8 l63 to l75; TT T12a |
| sp mono = "dark spacing between mono cells" | ~/mtp/research/handbook/02_* l110 |
| "the one clear loss" | FOR l51; TT T12a caption |
| crack component recall 0.262 / 0.257; precision 0.559 / 0.650; >= 20 px, >= 50% within 2 px; inactive regions >= 100 px | V8 l77, l80, l81; TT T12b |

### 8.6 (E1 vs CV5, levels)
| Number | Source |
|---|---|
| "about 2 to 3 x its CV5 size: +0.043 vs +0.015 to +0.022"; "about 2 x" against CS_D4 - PF +0.0222; "interval contains the CV5 values" | ER l11 to l13 (verbatim, "x" written as "times") |
| (removed 23 Nov, lead ruling) the row attribution of ER's "+0.015 to +0.022" to COMBO - PF and CS_D4 - PF; the chapter now quotes ER's range without naming rows | ER l11 |
| GP D1 sentence on CV5 check (1.159 against 1.15; passes on 532) | GP l68 to l69 (verbatim) |
| CV5 PF 0.8463; U2 0.769; U1 0.733; E1 C1 0.4467, C2 0.4897; full 0.4808; half-cut 0.4312 | TT T14 l489 to l498 |
| width ratio E1 C1 0.458, C2 0.463; CV5 PF 1.0189 | R8 l6, l7 (TT T11a); TT T5 l181 |
| 0.90 / 0.90 target | BR l57 |
| E1 C2 relP@2 0.5995, relR@2 0.4157 | R8 l7; TT T11a l333 |

### 8.7 (test50)
| Number | Source |
|---|---|
| 8 same physical cell (7 by pixels, 1 by cells.tsv link only), 7 neighbouring crops, 19 share a module; 18 counted earlier openings | ER l19 to l21; V8 l137, l138; FOR l61 to l62 |
| clean49 = 49 cells without the noisy cell | OR l147 |
| v1.1: +0.0102 [-0.0094, +0.0291] (all), +0.0102 [-0.0090, +0.0292] (clean49), +0.0322 [+0.0036, +0.0584] (nolink16) | V8 l124, l129, l134; TT T13c |
| levels all 50: C1 0.8905, C2 0.9006, C1-D4 0.9013 | V8 l120, l121, l123; TT T13c |
| v0 Pratt A crack C2 0.383, C1 0.337; Pratt 4c 0.25 | V8 l89, l97; TT T13a, T13b |
| PV-S3 crack IoU (all px) C2 0.441, C1 0.418; theirs 0.58 | V8 l92, l106; TT T13a, T13b |
| SEiPV micro IoU C2 0.896, fw-IoU 0.903; theirs 'IoU' 0.7447, 'mIoU' 0.8604 | V8 l91, l112, l113; TT T13a, T13b |
| rule A inferred; split / background rule not stated; averaging not defined | V8 l89, l91, l92 |
| published rows single runs on old labels, 478 x 4 offline augmentation; ours 532 cells, v1.1, 5 seeds | OR l151 to l152; RELATED_WORK.md l18, l19 (R02, R03) |

### Summary and close
| Fact | Source |
|---|---|
| from opening #9 E1 is training data for few-shot models; no later zero-shot claim on E1 | EL l35; LOG l291 per OUTLINE 9.4 |

## Judgement sentences kept (marked "Our reading (judgement)" or worded as judgement in the text)
1. 8.2: "E1 supports a gain of the C2 recipe over the PF recipe in crack relF1@2, but it does not pin down its size; values from near 0 to about +0.10 are compatible with the read."
2. 8.3: "part of the all-cell gain comes from fewer false crack pixels on crack-free cells, and part from the full crack cells; the crack-cell stratum alone is not decided." (Mechanism: false px on crack-free cells count in pooled relP@2; OR l80 to l81 defines relP@2 over the scored px of the 106 cells.)
3. 8.4: "a deployed single C2 model rests on the recipe-level result and on the spread of its seeds on E1 (0.4656 to 0.5067), not on a test of its own."
4. 8.5: "on E1 the relF1@2 gain is not a gain in the share of long cracks found."
5. 8.1: "What is new at opening #8 is the final models, not the cells."
6. 8.4: "On E1, neither five-seed ensemble separates from the mean of its own single models." (summary of two n.d. rows, S3 and S5)
7. 8.6: "they describe a large gap between E1 and the pool but do not measure it" (T14 reading, levels only, G-W9).
8. 8.7: "Our numbers fall above one published row and below another depending on the convention."
9. 8.6: "This read does not separate wider E1 labels from missed cracks as the cause." (no claim either way)

## Placeholders and citations
- \PENDING: 0. \CITE: 0. \FIG: 5 (F13, F14, F15, F16, F17; captions follow OUTLINE section 4). Text refers to them as plain
  "Figure~F13" etc.; replace with \ref once the figures have labels.
- Citations: \citep{pratt2023benchmark,seipv,pvs3} etc., defined in ch08_e1_result.bib (new). Verification:
  - pratt2023benchmark: doi 10.1016/j.sasc.2023.200048 in V8 l89 and RELATED_WORK.md l18; authors / title / vol. 5 / art. 200048 from the
    reference lists of /home/yugma/papers/2024-Mazen-...-7eaf9e.md ([9]) and 2026-Ramadan-...-e353bf.md ([42]); title also the
    H1 of /home/yugma/papers/2023-Pratt-A-benchmark-dataset-for-defect-detection-aa662c.md. First names not on disk: initials used.
  - seipv: doi 10.3390/en16237726 in V8 l91 and RELATED_WORK.md l19; authors / title / 16(23) / 7726 from Ramadan ref [53].
  - pvs3: doi 10.1016/j.engappai.2025.111790 in V8 l92 and RELATED_WORK.md l22 (vol. 160, 111790); title and authors from the
    arXiv PDF /home/yugma/papers/2025-Jha-...-3da279.pdf (arXiv 2404.13693v4).
  - pratt2023benchmark is also defined (same key, same DOI) in ch04_data.bib and ch06_protocol.bib: keep one copy. seipv and pvs3
    follow RW_SOURCES.tsv paper_key; no other chapter bib defines these works (checked 23 Nov 09:00).
- Cross-references to other chapters assume these labels (the other writers choose theirs; fix on merge):
  ch:data (Ch 4), ch:protocol (Ch 6), ch:methods (Ch 7, mine), ch:t3b (Ch 9), ch:deployment (Ch 10), ch:related (Ch 3).
  ch:data, ch:protocol, ch:deployment match the other writers' files (checked 23 Nov 09:00); ch:t3b is the label the other
  chapters already cite for Ch 9; ch:related is not yet defined.
  "Appendix~B" (reproducibility pins) and "Appendix~D" (E1 and test50 tables) are plain text, per OUTLINE section 2 Appendices.
- Tables referenced: T5, T6, T7a, T7b, T8, T9, T10, T11a, T11b, T12a, T12b, T13a, T13c (range T13a to T13c), T14, T17, T20.

## Departures from OUTLINE and things to check
- OUTLINE 8.1 says "read once 12:02:30 to 12:06:09"; the ledger (EL l27) gives "opened 11:25:30 to 12:06:09" (queue armed 11:25:30).
  The chapter gives registration 11:22:35 and the read 12:02:30 to 12:06:09 (FOR l8, l13), not the opening window.
- OUTLINE 8.6 and G-W1 give "+0.015 to +0.022"; ER does not name the rows. The chapter no longer attributes them (removed 23 Nov, lead ruling).
- OUTLINE 8.3 lists the BMRK levels from ER item 4; R8 l28 shows C2S5 also at 0.0000 (GP G-W4 note). The chapter lists only the
  arms ER names (C1-D4, C3, E-PF), following the errata.
- Added (not in OUTLINE): the E1 width ratio 0.458 / 0.463 against CV5 1.0189 (R8 l6 to l7, T11a; T5), the pre-opening power
  statement of OR section 6, and the resume disclosure (ADD). Remove if the lead prefers a shorter 8.1.
