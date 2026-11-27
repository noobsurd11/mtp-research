# NOTES for ch01_intro.tex (Chapter 1, "Introduction")

Written 23 Nov 2026, last of my four chapters. Framing per OUTLINE s7 risk 1: a benchmark plus one confirmed recipe gain, not
"captures almost all cracks" (E1 relR@2 0.4157). No sealed file was read.

Short paths (T = /home/yugma/mtp/research/team_2026-11-12_frontier; md5 prefix as read 23 Nov):
BR = BRIEF.md (bc06edd2); TT = thesis/THESIS_TABLES.md (91c867f0, after the 09:24 rebuild; the values used are unchanged from
81c54378 except T20 #19); RW = thesis/RELATED_WORK.md (f2a6adcd); P02 = benchmark/PROTOCOL_v0.2.md (b8b7f66a);
P10 = benchmark/PROTOCOL_v1.0.md (eeb3379a); AUD = dataset_audit/REPORT.md (9d7e0d27); V8 = results/final_opening_read/verdict.txt
(bbb5f3b4, via TT); R8 = results/final_opening_read/read_e1/read.txt (via TT T11a); RT = results/final_tta_read/read.txt;
ER = results/FINAL_OPENING_READ_ERRATA.md (af55915f); IC = thesis/INFERENCE_COST.md (1e5a9002); SEV = results/severity/SEVERITY_SUMMARY.md
(57e2bb4c); H02 = ~/mtp/research/handbook/02_* (via ch02 NOTES); ch02 to ch10 = drafted chapters and their NOTES.

## 1. Every number, with its source
### 1.1 Task
| Number / fact | Source |
|---|---|
| EL shows defects invisible to the eye; used before shipping and over life | ch02 s2.1 (pratt2023benchmark) |
| cracks dark lines; cut-off part produces no power, inactive area | ch02 s2.1 (haase2018crackwidth); kontges2011risk (title: risk of power loss due to micro-cracks) |
| grayscale 512 x 512, one cell plus parts of neighbours | BR l16 |
| 24 classes, 12 structural, 12 defects | BR l20 |
| BenchmarkEL 20211104; 582 = 478 / 54 / 50 | BR l20; TT T1 |
| five sources, different contrast and label conventions | BR l23 |
| crack in 206 of 478 train cells under v1.1 (209 under v1) | TT T3b row "Crack cells v1 to v1.1" (209 to 206; LAB l16) |
| inactive most directly tied to lost power | ch02 s2.4 ("Of all classes, it is the most directly tied to the electrical consequence of a defect") |
| WattCycle PV recycling / inspection; EL rig 2 to 3 months away as of 4 Nov | BR l9; SEV l64 |
| crack micrometres wide; dark line median FWHM 4.0 px; label median 1.75 px; half of label points > 1 px off ridge | ch02 s2.3 (H02 l161 to l163, l187); BR l33 to l34 |
| 1 px shift IoU 0.559 on legacy test masks | ch02 s2.3 (H02 l217); BR l35 gives 0.56 |
| inactive in 42 of 478 train cells | BR l22; ch02 s2.4 |

### 1.2 Goal
| Number / fact | Source |
|---|---|
| goal, quoted verbatim | BR l7 |
| target relR@2 >= 0.90 at relP@2 >= 0.90 | BR l57 |
| E1 C2 relP@2 0.5995, relR@2 0.4157 (mean over seeds 5 to 9, OP-A) | R8 l7; TT T11a |
| CV5 CS_D4 relP@2 0.9216, relR@2 0.8211 (OP-A, selection-biased) | RT l14 (checked); ch07 s7.6; OUTLINE O1 |
| "a benchmark for this very unorganised field" (quoted) | BR l11 |

### 1.3 Why numbers do not compare
| Number / fact | Source |
|---|---|
| 22 full-text papers | RW l84 (s4 heading); ch03 s3.2 |
| releases 582 / 642 / 695; 186 of 582 change split | P02 l22; P10 l34; ch03 table |
| later test sets each hold 51 of our pool cells | RW l47 (via ch03 NOTES l31) |
| test50: 8 same physical cell (7 by pixels, 1 by link), 7 neighbouring crops, 19 share a module | ER l19 to l21; TT T2 |
| UCF-EL crack is a region class about crack plus inactive | BR l28; ch03 s3.1 |
| rules A / B / C: 0.405 / 0.202 / 0.541 (C1, v0, 50 cells) | TT T13b l432, l435, l436 (via ch03 NOTES l57; = V8 l100, l103, l104) |
| published crack 0.25 (Pratt 2023, per-image median) and 0.58 (PV-S3, pooled) | TT T13a; V8 l97, l106; ch03 s3.2 |
| PF strict 0.233 / 0.365 / 0.414; relF1@2 0.824 / 0.846 / 0.849 | TT T19a F1 (AUD l24 to l25) |
| release: strict 0.320 vs 0.365; relF1@2 0.822 vs 0.846 | TT T3c (AUD l101) |
| 18 of 22 no interval; 0 of 22 module-disjoint; 0 tolerance metric; 0 unseen modules; 2 of 22 release, split and metric | RW l88, l92, l99, l100, l101 |
| seven elements; none of the 22 states all | P10 l41 (reading, S); ch03 s3.2 ("None of the 22 full-text papers states all of them") |

### 1.4 Approach
| Number / fact | Source |
|---|---|
| SSL helped only at 5% labels under the old rule; framing dropped | TT T21 rows P13, P16 (via ch05 NOTES); BR l12; ch05 s5.2 |
| measurement failures (test scored every run, overlap, effects near noise, inactive decided by few cells) motivate the protocol | ch05 s5.1 conditions list; BR l24, l68 |
| five rules from the audit | ch06 s6.1 ("Five choices follow from the measurements") |
| E1 106 cells, later release (20221008) | TT T1; ch04 s4.1 |

### 1.5 Contributions
| Number / fact | Source |
|---|---|
| cv5v3: 5 folds, 285 groups, none spans folds | TT T1 (P02 l263) |
| cv5v2: 24 modules span two folds, 91 cells | TT T2 (P02 l262) |
| tolerance 2 px = 95th percentile of distance between two annotations | ch06 s6.3 (P10) |
| convention band +-0.019; M = 0.010 | TT T4 |
| info sheet with entry class, cost, seed count | ch06 s6.7 (P10 s12; INFO_SHEET_TEMPLATE.md) |
| released as lists and code only, no images, masks or weights | ch06 s6.8 (P10 item 15); ch06 carries \PENDING{release URL} |
| 57% crack px, 71% inactive px outside centre cell | TT T19a F3 (AUD l54) |
| label errors corrected share 0.244 [0.105, 0.436]; no contrast moves > 0.003 | TT T20 #18; T19a F5 |
| relF1@2 contrasts move by at most 0.0031 | TT T20 #17; T19a |
| release moves strict IoU +0.045, more than any method gain | TT T20 #19 (narrowed, l682) |
| EL-paper models -0.0773 [-0.0892, -0.0594]; -0.0932 [-0.1113, -0.0774] | TT T16a; T20 #14 |
| three 5-seed arms (HRNET, SWADBN, COMBO) none confirmed | TT T6; ch07 summary |
| D4 on PF +0.0134 [+0.0066, +0.0207] CONFIRMED, known modules | TT T7a (a); T20 #6 |
| E1 P +0.0430 [+0.0013, +0.1043] CONFIRMED; guards pass | TT T8 (V8 l11 to l15) |
| scope: seeds 5 to 9; OP-A; 101 of 106 CSIR | V8 l140, l142; TT T8 caption |
| full +0.1464 [+0.0420, +0.2278]; half-cut +0.0110 [-0.0289, +0.0722] | TT T10 (V8 l55, l56) |
| MDE about 0.074 (derived) | TT T8 note; GP G-N4 |
| C2 - C1-D4 +0.0451 [+0.0173, +0.0699]; "Most of the gain is the model"; "The D4 part is not resolved on E1" | TT T9; ER l16, l17 |
| readout and views chosen on pool cells; E1 7 earlier registered openings | ER l29; V8 l139, l138 |
| C2 1,744 GFLOPs per cell; 11.8 x C1 | IC l23, l24; TT T22 |
| about 0.17 s per cell, one GPU, batch 1 (0.174 s) | IC l76; TT T22; ch10 s10.5 |
| C3 8,722 GFLOPs; C3 - C2 -0.0025 [-0.0254, +0.0157]; E1 scope added 23 Nov: OP-A, recipe means over seeds 5 to 9, 101 of 106 cells CSIR | IC l23; TT T22; TT T9 (V8 l45); scope per OUTLINE s0 rule 3 |
| severity validated only for PF on pool cells; power claim not supported | SEV l16; TT T20 #21 |

### 1.6 Not claimed
| Number / fact | Source |
|---|---|
| relR@2 0.4157, about 0.42 | R8 l7; TT T11a |
| test50 overlap; context only | OUTLINE s0 rule 4; TT T2 |
| E1 training data from opening #9 | EL l35 (../team_2026-10-31_next/e1_openings.md) |

## 2. Judgement sentences kept
1. "Our reading (judgement): a comparable number must state seven things together ..., and no published EL number we found states
   all seven." (P10 l41, S; ch03.)
2. "The first obstacle was not a model but a measurement." (framing; OUTLINE s7 risk 1, BR l11.)
3. "This thesis therefore reports a benchmark first, and one model gain measured under it." (framing.)
4. "The headline is a benchmark plus one confirmed recipe gain, not a model that finds almost all cracks" (OUTLINE s7 risk 1; A2).
5. Contribution list wording: every E1 sentence carries seeds 5 to 9, OP-A, 101 of 106 CSIR, full cells carry it (OUTLINE s0 rule 3);
   test50 sentences carry "in-distribution, known leakage, context only" (rule 4); "Most of the gain is the model" + "The D4 part is not
   resolved on E1" (G-W2); readout and D4 chosen on pool cells (G-W11); "supported, not proven" at first use of unseen modules (G-W7).

## 3. Placeholders and citations
- \PENDING: 0 since 23 Nov (t3b_fill). Former marker: `\PENDING{T3b verdict: one sentence with the verdict word, Delta = ALL $-$ ZS and its interval, and the half-cut stratum}`; see section 5.
- \CITE: 0. \FIG: 0 (OUTLINE s4 assigns F12 to Ch 1 and 7; ch07 already places F12, so the intro does not repeat it).
- Citations (all in references.bib): pratt2023benchmark, haase2018crackwidth, kontges2011risk, jha2025pvs3. No new .bib file.
- Cross-references: every chapter label (ch:background, ch:related, ch:data, ch:legacy, ch:protocol, ch:methods, ch:e1_result,
  ch:t3b, ch:deployment, ch:limitations, ch:conclusion) and app:tables, app:related, app:t21 (all exist in main.tex / chapter files).

## 4. Notes for the lead
- Length about 1,990 words, about 4.4 pages against a 5-page budget; room for F12 or a short paragraph on WattCycle's use case if
  wanted.
- kontges2011risk is cited only for "cut-off parts lose power" by its title; if the lead prefers, cite haase2018crackwidth alone
  (as ch02 does).
- Contribution 1 says the benchmark "is released as lists and code only", as ch06 does; the release itself still waits for approval
  (ch06 \PENDING{release URL}). Change to "is prepared for release" if it is not public by submission.

## 5. T3b fill (23 Nov 2026, t3b_fill, after the read)
Sources (T = /home/yugma/mtp/research/team_2026-11-12_frontier): VT = T/results/t3b_open9_read/verdict.txt (bfe583db);
RT = T/results/t3b_open9_read/read_t3b/read.txt (922b965e). Numbers copied as printed; none recomputed. No raw record, E1
image, label or dump was read.

| Text (ch01) | Value | Source |
|---|---|---|
| contribution 6: "It is CONFIRMED" | CONFIRMED | VT l9, l76 |
| out of fold over 5 folds of E1; seeds 5 to 7; OP-A; 106 cells | 5 folds; seeds 5 to 7; OP-A; 106 cells | T/results/t3b_open9_read/run.log l7 (5 folds); VT l65 (seeds 5 to 7); VT l5 (OP-A, 106 cells, 71 clusters) |
| 101 of them CSIR | 101 / 66 | VT l32 |
| ALL beats ZS by +0.2213 [+0.0977, +0.3504] | | VT l6 |
| both guards passing | G1, G2 PASS | VT l7, l8 |
| half-cut +0.2530 [+0.0878, +0.3885] | | VT l27 |
| without scuff -0.0701 [-0.3019, +0.0517] | | VT l29 |
| ALL - HALF +0.0171 [-0.0246, +0.0625], not separated; "half of the labelled images give about the same gain" | HALF - ZS +0.2042 [+0.0718, +0.3366] | VT l18, l17 |
| "labelled cells of a layout help, not that the model handles a new layout without them" | scope sentence | VT l2 (ZS printed beside, never a T3b model), l64 (E1 is training data); ch09 s9.4 |
| s1.6: "one confirmed zero-shot recipe gain" (was "one confirmed recipe gain"); new sentence "The few-shot gain needs labelled cells of the layout and is measured inside E1 only." | wording only | scope of VT l5, l64 |
