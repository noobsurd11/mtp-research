# NOTES for ch09_t3b.tex (Chapter 9, "Few-shot layout adaptation: track T3b, E1 opening #9")

Written 23 Nov 2026, before the T3b read. Read only docs, rules, the ledger and the log (counts and dates only). Nothing under
the T3b read output, the t3bopen relay, or any E1 / test50 dump, label or prediction was read.

Short paths (relative to T = /home/yugma/mtp/research/team_2026-11-12_frontier; md5 prefix as read 23 Nov):
- T3R = harness/t3b/T3B_RULE.md (0c006d44; = the registered rule pin in the ledger and OUTLINE s8)
- T3P = benchmark/T3B_PROPOSAL.md (569fbcb0)
- EL = ../team_2026-10-31_next/e1_openings.md (52432548), the E1 openings ledger
- LOG = log.md (100caf5e as read 23 Nov about 09:20; append-only, line numbers of that read)
- TT = thesis/THESIS_TABLES.md (81c54378 when read; rebuilt 91c867f0 at 09:24, no value used here changed); V8 = results/final_opening_read/verdict.txt (via TT)
- BR = BRIEF.md (bc06edd2); OUT = thesis/OUTLINE.md section 2, Chapter 9 entry (l171 to l177)
- ch06 / ch08 = the drafted chapters (wording reused, not re-derived)

## 1. Every number in the chapter, with its source

### Opening paragraph
| Number / fact | Source |
|---|---|
| 62 half-cut cells; C2 - C1 on half-cut +0.0110 [-0.0289, +0.0722], n.d. | TT T10 (V8 l55); ch08 s8.3 |
| pool holds no half-cut cell | V8 l140 (via ch08 NOTES); ch06 "The pool has no half-cut cell" |
| question: "how much does the final recipe gain on E1's layouts once it has labelled cells of them" | T3R l18 to l19 (paraphrase) |
| E1 opening #9 | T3R l22; EL l28 |
| Table T3b unrelated (name clash) | OUT section 6, O2; ch04 l10 does the same |

### 9.1 Motivation and design
| Number / fact | Source |
|---|---|
| 62 half-cut cells; 37 cells with a scuff streak >= 500 px | T3P l14, l15 |
| 36 E-SCDD half-cells (H36), speck-level crack labels, validation only | BR l26 |
| judgement "what WattCycle needs to plan labelling" | T3P l80 (S in the proposal); marked judgement |
| 106 cells, 71 source images = 71 modules | T3R l20; T3P l13 |
| 32 crack cells, 32,294 crack px, 296 components >= 20 px; 74 crack-free | T3P l16, l18 |
| hard stratum = half-cut + scuff; 20 crack cells; 75% of crack px | T3P l17 (24,246 px, 75%); T3R l114 ("hard = half-cut + scuff") |
| K = 5 folds by image id; deterministic; hard-stratum crack px balanced first | T3P l22 ("deterministic greedy folds by image id, hard-stratum crack px balanced first"); T3R l26 |
| drawn 12 Nov from GT masks and lists only (no prediction) | T3P l3 ("Counts are from ground-truth masks and lists only"; dated 12 Nov); T3R l26 (draft folds md5 49e70413, 12 Nov) |
| frozen with md5 before any run | T3R l25 (LISTS.md5 5c86318a); T3P l71 (rule 5) |
| held-out 22 / 22 / 20 / 21 / 21 cells; 12 / 14 / 14 / 16 / 15 image ids | T3R l28 |
| intervals resample the same 71 clusters as opening #8 | T3R l20 to l21 |
| ALL = 532 + E1 cells outside fold k (84 to 86) | T3R l45 |
| HALF = 532 + half of the train-side image ids (42 or 43 cells) | T3R l30 to l32, l46 |
| half cell share 0.494 to 0.506; hard crack px share 0.496 to 0.501 | T3R l36 to l40 (cells share column 0.500 / 0.500 / 0.500 / 0.494 / 0.506; hard crack px share 0.499 / 0.501 / 0.500 / 0.501 / 0.496) |
| each fold model dumps only its held-out set; 5 fold records joined to one OOF record, each copied from the one model | T3R l86 to l90 |
| 3 deployable models (532 + 106), never scored on E1 | T3R l47 |
| seeds 5, 6, 7; 33 trainings = 15 ALL + 15 HALF + 3 deployable | T3R l42 to l47, l50 |
| recipe exactly C2's: HRNet-W18 U-Net++, PF encoder schedule, SWAD uniform average steps 10,000 to 20,000, 20,000 steps, v1.1 on the pool | T3R l48 to l50 |
| only the training list differs from fin_hrnet_swad_v11_pool_s<s> | T3R l49 to l50 |
| swad readout of final weights (step 20000), D4 8 views, argmax over 24 classes (OP-A) | T3R l51 to l52 |
| no threshold, bias, view weight or checkpoint set on / chosen with any E1 cell | T3R l52 to l53 |
| E1 labels in their scoring view; classes 25 to 28 and ignore px -> ignore (255) | T3R l78 to l79 (full map: 0 to 23 unchanged, 24 -> 2, 29 -> 1, 25 to 28 -> 255, ignore -> 255) |
| training label = scoring GT on every scored (kept) px | T3R l80 to l81 |
| monitor = fixed set of 107 pool training cells (cv5v3 fold 0), numbers never read | T3R l59 to l61 |
| no fold's training list lists or links its held-out cells | T3R l61 to l63 |
| ZS = opening #8 C2 dumps of seeds 5, 6, 7 (swad, D4), re-scored, never trained on E1; same recipe, seeds, inference | T3R l91 to l93; EL l28, l35 |

### 9.2 Registration, rule and power
| Number / fact | Source |
|---|---|
| rule written 21 Nov before any T3b number, no T3b model trained | T3R l3 to l4 |
| reviewed before registration | T3R l129 (independent review PASS pinned to the rule md5) |
| registered 22 Nov 2026 03:13 IST; ledger: from that date E1 is training data for T3b models | EL l35 (also EL l28) |
| 33 trainings ended rc 0 on 22 Nov; registered repairs: none | LOG l382 ("33 of 33 trained rc 0", 19:13 to 19:16 IST), l384 ("registered repairs: none") (facts only) |
| 30 sealed dump jobs, one per fold model, started 23 Nov | LOG l386 (armed 08:40:46 IST, 30 jobs) (fact only); T3R l86 |
| read once, only after all 30 exist | T3R l133, l138 |
| metric: crack relF1@2 at OP-A, pooled over scored px of the 106 cells (opening #8's definition) | T3R l96 |
| P = mean over seeds 5 to 7 of relF1@2(ALL_s, OOF) - mean over seeds 5 to 7 of relF1@2(ZS_s) | T3R l97 |
| seed-aware two-stage bootstrap: 71 clusters, then 3 models per arm with replacement; 2,000 draws; 95% percentile | T3R l98 to l100 |
| M = 0.010 | T3R l100 |
| outcome words and conditions (CONFIRMED / GAIN, FAILING GUARDS NAMED / NOT CONFIRMED: WORSE, interval holds 0, below M) | T3R l102 to l106 |
| G1: false crack px on the 74 crack-free cells, ALL <= 1.5 x ZS; G2: mIoU-R13 Delta >= -0.010; arm means over 3 seeds; bounds inclusive | T3R l108 to l109 |
| width ratio ALL / ZS printed, not a guard; E1 labels about 1.5 x wider | T3R l110 to l111 |
| printed beside (HALF - ZS, ALL - HALF, any-hit recall, strata, inactive, strict IoU +-0.019); full list incl. strata full 44 / half-cut 62 / hard 29 / half-cut without scuff 33 used in the PENDING markers and F20 | T3R l112 to l116 |
| SE 0.0265 at opening #8 (5 v 5); about 0.030 with 3 seeds (S) | T3R l143 to l144 |
| power about 52% at +0.06, 76% at +0.08, 91% at +0.10; smallest effect with 80% power about +0.085 | T3R l144 to l145 |
| +0.10 or more plausible if layout labels close part of the hard-stratum gap; zero-shot recall 0.13 there | T3R l146 to l147 (S in the rule); T3P l56 (0.126, earlier model, eval.md s5); BR l61 |
| top 1 / 3 / 5 / 10 image ids hold 0.22 / 0.50 / 0.69 / 0.86 of crack px | T3P l20 |
| 20 hard crack cells in 10 image ids | T3P l17, l48 |
| with K = 5 two folds are in effect one image each; only the pooled score usable; about 9 images, effective n 8.6 | T3P l48 to l49 |
| smaller gains, ALL - HALF, strata, inactive under-powered (about 9 effective images) | T3R l147 |
| inactive: 10 cells, 7 image ids, top 3 hold 87%; cannot be answered | T3P l19, l51 |

### 9.3 Result
Filled 23 Nov 2026 (about 21:40 IST, t3b_fill, after the read). Every value: section 5 below.

### 9.4 What it can and cannot show
| Number / fact | Source |
|---|---|
| detectable about +0.085 at 80% power | T3R l145 |
| G1 1.5 x and G2 0.010 restated | T3R l108 to l109 |
| 14 to 18 hard crack cells on a training side (K = 5), from at most 9 image ids; two honest points; which images matter more than how many | T3P l41 table (train-side hard crack cells 16 / 16 / 14 / 18 / 16), l81 ("14 to 18 hard crack cells"), l50 |
| folds by image id may be optimistic for a new site; CSIR ids 300 to 2,328; neighbouring ids same batch not measured | T3P l45, l83; T3R l151 to l152 |
| E1 labels about 1.5 x wider; relF1@2 less width-sensitive than strict IoU but not immune; any-hit recall printed | T3R l152 to l153; T3P l64 |
| 101 of 106 CSIR | TT T1 / T8 caption (V8 l140) |
| 3 seeds, one primary contrast | T3R l153 to l154 |
| deployable models: no held-out score; expected score = the OOF number (S) | T3P l8 |
| trained_on_e1 mark on runs and records; read tools refuse marked records outside the T3b card | T3R l120 to l125 |
| no T3b number in a T3 table or E1 column of any other track | T3R l126; T3P l68 |
| E1 training data from the registration; no later zero-shot claim on E1 | EL l35; T3R l150; LOG l291 |
| last zero-shot result on E1 in this work | ch08 closing sentence (same wording) |

## 2. Judgement sentences kept
1. 9.1 "Our reading (judgement): what labelled cells of a new layout buy is what WattCycle needs to know to plan labelling, and
   only E1 can measure it here." (T3P l80, S there.)
3. 9.2 Power paragraph, flagged as "judgement in the rule" (T3R s11 is tagged S).
4. 9.2 "The cell count overstates the information." (T3P l49: "its uncertainty is that of about 9 images").
5. 9.4 "NOT CONFIRMED would not show that labels of the layout do not help" (consequence of the power statement; mine).
6. 9.4 deployable models' expected score = the OOF number of ALL (T3P l8, S there), worded as judgement.
7. 9.4 pending judgement sentence on what the verdict means for labelling (left as a \PENDING marker).

## 3. Placeholders
- \PENDING: 0 since 23 Nov (t3b_fill). The 10 T3b markers below were replaced from the T3b read; section 5 maps each
  to its text and source lines. Former list (as it was in the .tex):
  1. `\PENDING{T3b verdict: the verdict line as printed by the read (CONFIRMED; GAIN, FAILING GUARDS NAMED; or NOT CONFIRMED with its reason), with the date and times of the read}`
  2. `\PENDING{T3b verdict: Delta = ALL $-$ ZS, crack relF1@2 at OP-A, mean over seeds 5 to 7, with its seed-aware 95\% interval and SE, and the fixed-model interval}`
  3. `\PENDING{T3b verdict: levels of ZS, HALF and ALL (relF1@2, relP@2, relR@2; mean over seeds 5 to 7 with the range over seeds)}`
  4. `\PENDING{T3b verdict: guards, G1 false crack pixels on the 74 crack-free cells for ALL and ZS with their ratio, and G2 the mIoU-R13 change; pass or fail each}`
  5. `\PENDING{T3b verdict: width ratio ALL / ZS, printed, not a guard}`
  6. `\PENDING{T3b verdict: printed beside, HALF $-$ ZS and ALL $-$ HALF with seed-aware and fixed-model intervals}`
  7. `\PENDING{T3b verdict: any-hit crack component recall and recall at 50\% coverage for ZS, HALF and ALL (of 296 components)}`
  8. `\PENDING{T3b verdict: strata of ALL $-$ ZS and HALF $-$ ZS with intervals: full 44, half-cut 62, hard 29, half-cut without scuff 33, crack cells 32, crack-free 74 (false crack pixels), CSIR 101, BMRK 5}`
  9. `\PENDING{T3b verdict: inactive IoU ALL $-$ ZS (reported only), strict crack IoU ALL $-$ ZS against the band $\pm$0.019, and per-class IoU changes of note}`
  10. `\PENDING{T3b verdict: one or two sentences on what the verdict means for labelling cells of a new layout, worded at the strength the verdict allows}` (9.4)
- \CITE: 0. \FIG: 1 (F20, OUTLINE s4; caption written before the result; check the strata named in it against the read).
- Citations: wang2021hrnet, zhou2018unetpp, cha2021swad (all in references.bib). No new .bib file.
- Cross-references: ch:e1_result, ch:methods, ch:protocol, ch:limitations; tab:T3b (to disown the name clash). Section labels
  sec:t3b-design, sec:t3b-rule, sec:t3b-result, sec:t3b-scope.

## 4. Notes for the lead
- When the read lands: the result paragraph is one block of markers; replace it with prose and, if the read prints a table, a new
  table (OUTLINE 9.3 says "(new table)"). The \FIG{F20} caption names four strata; extend if the plot shows more.
- If the verdict is CONFIRMED or GAIN, the first sentence of the 9.4 "Cannot" paragraph still holds (it is about power); if NOT
  CONFIRMED, it is the key sentence. The OUTLINE 9.4 consequence line is used as written.
- The 02:24 first registration and its amendment (EL l33, l34) are not in the text; the 03:13 registration is the one stated.
- Page estimate: about 1,730 words including about 230 words of \PENDING text, about 3.8 pages; the result prose will replace the
  markers. The chapter states the 9.2 rule in one paragraph; if it still runs long, the Concentration sentences of the Power
  paragraph can move to an appendix.

## 5. T3b result (filled 23 Nov 2026 by t3b_fill; numbers copied as printed, none recomputed)

Sources (T = /home/yugma/mtp/research/team_2026-11-12_frontier): VT = T/results/t3b_open9_read/verdict.txt (bfe583db, 76 lines);
RT = T/results/t3b_open9_read/read_t3b/read.txt (922b965e); RL = T/results/t3b_open9_read/run.log (261a1132);
EL = ../team_2026-10-31_next/e1_openings.md (3ead9149 as read 23 Nov 21:40; row 9 at l28, "#9 OPENED" bullet at l38);
LOG = T/log.md (d05980ed as read 23 Nov 21:40). No raw record, E1 image, label or dump was read.

### 5.1 Section 9.2 additions (run description)
| Text | Value | Source |
|---|---|---|
| opening ran 23 Nov 08:40:46 to 13:39:27 IST | times | EL l38 (also EL l28) |
| 30 sealed jobs, all ended without error | 30 dumped rc 0 | EL l38; LOG l419 ("30 dumped rc 0") |
| 29 of them each on a GPU with no other job above 4,096 MiB | 29 (derived: 30 minus the one SHARED start); 4,096 MiB = strict-lane limit "other-user max 4096 MiB" | LOG l386 (strict lanes, other-user max 4096 MiB), l418, l419 |
| sharing allowed for the last two jobs, 13:34:35 to 13:35:49 IST; outside the reviewed plan; logged | SHARE_DUMP on 13:34:35, removed 13:35:49 | LOG l418 ("deviates from the reviewed plan's strict lanes"), l419; EL l38 ("a lead deviation from the reviewed strict lanes, logged in log.md 13:34") |
| one started on a GPU that had freed; the last ran beside another user's job | half_f3_s7 "strict start" 13:34:42; all_f3_s7 "SHARED ... beside" another user's job 13:35:15 | LOG l419. NB: the lead's brief said both of the last two ran shared; LOG l419 records one strict start and one shared start; the text follows the log |
| deterministic fp32 dumps; the read checks each manifest | fp32; manifest check of 33 dumps OK | LOG l418 (lead: "deterministic fp32 dumps whose manifests the registered read checks"); RT l1 ("fp32"); RL l2 ("manifest check: 33 dumps (30 T3b, 3 zero-shot), device ['NVIDIA RTX A6000']: OK") |
| one GPU model (RTX A6000) | | RT l1; RL l2; VT l71 ("one GPU model") |
| read ran once 13:38:00 to 13:39:27 IST, without error | rc 0 | EL l38 ("13:38:00 to 13:39:27, rc 0"); RL l1 (log start 13:38:26), l31 (13:39:27, "verdict rc 0") |
| ZS re-scored identical to opening #8 | IDENTICAL, 106 cells | RL l4 to l6 |
| labels of all 106 cells on the training machine from staging to clean-up; held-out labels present, not linked from the fold root; deployable models need all 106 | | VT l74 |

### 5.2 Section 9.3 (one row per former marker)
| Marker | Replaced by | Value(s) | Source |
|---|---|---|---|
| 1 verdict line and read times | quoted verdict line; read 23 Nov 2026 13:38:00 to 13:39:27 IST | CONFIRMED; +0.2213 [+0.0977, +0.3504]; 1.426 | VT l76 (= RL l30); times EL l38 |
| 2 Delta, interval, SE, fixed-model | Primary contrast paragraph | +0.2213; [+0.0977, +0.3504]; SE 0.0643; M 0.010; fixed-model [+0.1066, +0.3390] | VT l6, l11; RT l10 |
| 3 levels | relF1@2 ZS 0.4881 [0.4656, 0.5067], HALF 0.6924 [0.6797, 0.7005], ALL 0.7094 [0.6943, 0.7309]; relP@2 0.6098 / 0.8119 / 0.8403; relR@2 0.4095 / 0.6038 / 0.6140 | brackets = range over seeds (they equal the min and max of the per-seed values at VT l36 to l44) | RT l7, l8, l9 |
| 3 (cont.) relP@2, relR@2 contrasts | ALL - ZS relP@2 +0.2306 [+0.1394, +0.3440]; relR@2 +0.2046 [+0.0356, +0.3835] | | VT l14 |
| 4 guards | G1 541 vs 2231, ratio 0.242, bound 1.5, 74 crack-free cells, PASS; G2 +0.1385, bound -0.010 (printed -0.01), PASS | | VT l7, l8 |
| 5 width ratio | 1.426 (ALL 0.631, ZS 0.443); E1 labels about 1.5 x wider; learned width lifts strict IoU and pixel recall without finding more cracks | | VT l10, l70 |
| 6 printed beside | HALF - ZS +0.2042 [+0.0718, +0.3366] (fixed [+0.0773, +0.3274]); ALL - HALF +0.0171 [-0.0246, +0.0625] (fixed [-0.0183, +0.0506]) | "about the same", "not separated" are wording on these intervals | VT l17, l18 (= RT l11, l12) |
| 7 components | any-hit ZS 0.400 [0.301, 0.490], HALF 0.682 [0.645, 0.703], ALL 0.666 [0.635, 0.693]; >= 50% 0.245 / 0.591 / 0.598; precision 0.659 / 0.817 / 0.836; definition of any-hit; arm mean over 3 seeds [min, max] | 296 components from T3P l16, l18 (section 1) | VT l20 to l23 |
| 7 (cont.) judgement | "a rise in component recall of this size is hard to explain by line width alone" | judgement, mine | VT l70 (width lifts pixel recall, not crack count) as the basis |
| 8 strata (prose and Table tab:t3b-strata) | all cells / clusters, ALL - ZS, HALF - ZS, ALL - HALF per stratum | full 44 / 24; half-cut 62 / 47; hard 29 / 17; half-cut without scuff 33 / 31; crack cells 32 / 21; crack-free 74 / 55; CSIR 101 / 66; BMRK 5 / 5 | VT l26 (full), l27 (half-cut), l28 (hard), l29 (no scuff), l30 (crack), l31 (crack-free), l32 (CSIR), l33 (BMRK); all-cells row VT l6, l17, l18 |
| 8 (cont.) levels in strata | no scuff ZS 0.8870 [0.8797, 0.8928], ALL 0.8168 [0.8034, 0.8340]; BMRK ALL 0.0000, HALF 0.5443 [0.0000, 0.9908], ZS 0.0000; crack-free false crack px 541 / 1366 / 2231, relF1@2 0.0000 | | RT l107, l109; RT l17 to l19; RT l67 to l69 |
| 9 other metrics | inactive IoU +0.1463 [-0.0525, +0.4829], reported only; 10 inactive cells in 7 images; strict crack IoU +0.1803 [+0.0929, +0.2606], band +-0.019 | | VT l13, l72, l12 |
| 9 (cont.) per class | crack 0.1866 / 0.3438 / 0.3669 (ZS / HALF / ALL); sp mono 0.1924 / 0.2039 / 0.7966; material and edge dark 0.0000; splice n/a | "cause not examined" is a statement of what was not done | VT l57, l51, l56, l60, l59 |

### 5.3 Section 9.4
| Text | Value | Source |
|---|---|---|
| Can: judgement on labelling (marker 10) | +0.2213 [+0.0977, +0.3504]; HALF about the same; 42 or 43 E1 cells per HALF fold model | VT l6, l17, l18; 42 or 43 from T3R l30 to l32, l46 (section 1); the WattCycle sentence is judgement (mine), scoped "on this evidence" |
| Cannot, first sentence re-tensed (was the NOT CONFIRMED conditional) | 80% power at about +0.085; interval [+0.0977, +0.3504] | T3R l145 (section 1); VT l6 |

### 5.4 Not used, and why
- Single-fold numbers: not printed by the read (VT l68).
- VT l3 (registration line) names a host and a user: not in the text.
- Table T20 row 22 (tables_data.py) carries the claim; anchors there point at VT l5, l6, l7, l8, l9, l10, l11, l17, l18, l27, l29,
  l32, l65 and RL l7.
- The F20 caption was rewritten by the figure maker (fig_F20) at about 13:48 on 23 Nov; not by t3b_fill; kept as is.
