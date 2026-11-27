# TRACE_REPORT: every number in the thesis chapters against its source (trace_pass, 23 Nov 2026, 12:05 to 12:40 IST)

Independent read-only check for the lead. Writers' NOTES were used as pointers only; each source line was opened.
No chapter, table or source was edited. No E1 or test50 dump, label, mask, image or prediction was opened; only aggregate
result text files (verdict.txt, read.txt, *.md). Nothing under `/home/noob/work/bench_reads/t3b_open9` or the t3bopen relay dir
was read. The \PENDING{T3b ...} markers (ch01 1, ch06 5, ch09 10, ch11 1, ch12 2) are expected and are not counted.

T = `/home/yugma/mtp/research/team_2026-11-12_frontier`. Short names as in OUTLINE section 0.

## 1. Files checked (md5, first 8)
Chapters: ch01 ff4199e4, ch02 57dbcf56, ch03 4a8544e6, ch04 28871f63, ch05 ca2d93a3, ch06 570768f0, ch07 affcdbd4,
ch08 b9ead9ec, ch09 442428b5, ch10 a35a8845, ch11 f42a9b24, ch12 33bed4bd, app_t21_note 16c75005 (unchanged during the check).
Tables: TT 8c550be1 (the NOTES cite 81c54378 / 91c867f0; values used are unchanged), SOURCES.tsv 23cf56e8.
Key sources: V8 bbb5f3b4, R8 82cea48a, ER af55915f, FOR 16e3f1e7, VT a95f89e8, RT 54214525.

## 2. Method
1. **Table layer.** Script over all 1,638 non-derived rows of SOURCES.tsv: open the file, take the cited line, test that the value is a
   substring. 1,636 exact; 2 differ only in quoting (T2 "Unseen modules" in quotes at SI l200; T4 `"n_groups": 330` at cv5v2.json
   l63). No source md5 changed since SOURCES.tsv was written. So a chapter number that equals a TT cell traces to a source line.
2. **Token layer.** Script extracted 2,544 number tokens from prose, captions and in-text tables of the 13 files (decimals, intervals,
   counts, percentages, ratios; skipped years, LaTeX lengths, section and opening numbers `#n`, identifiers such as relF1@2, R13, W18).
   - every token but 6 was found in a file cited by that chapter's NOTES or in TT; the 6 were checked by hand: ch03 "159,000"
     ("159k", BR l27), ch05 and ch07 "1,000" (H04 l410), ch05 0.996 / 0.997 (H19 l155), ch10 467 (FIGURES_B.md l191);
   - 133 "x [lo, hi]" triples: each point and both ends co-occur on one line of a cited source;
   - lines with two or more 3-decimal values: each pair co-occurs on one source line, or is a legitimate combination (8 lines, checked).
3. **Hand layer.** Read line by line against the source: ch08, ch07, ch06, ch04, ch01, ch12 in full; ch02, ch03, ch05, ch09, ch10,
   ch11 and the appendix note in full with source spot checks for every non-TT number. Context checked: E1 scope phrase,
   "selection-biased" on CV5 numbers of the C2 recipe (CS, CS_D4), the test50 phrase, and that each number is the right cell
   (OP-A vs OP-W, 532 vs 416, arm, set).
4. Spelled-out counts that carry a claim were checked by hand and added to the counts (ch12 claim-class counts; app note "three seeds").

## 3. Counts per chapter
| Chapter | OK | OK-rounded | DERIVED-right | DERIVED-wrong | MISMATCH | UNSOURCED | Total |
|---|---|---|---|---|---|---|---|
| ch08 E1 result | 381 | 1 | 10 | 0 | 0 | 0 | 392 |
| ch07 methods | 384 | 1 | 1 | 0 | 14 | 0 | 400 |
| ch06 protocol | 241 | 0 | 2 | 0 | 0 | 0 | 243 |
| ch04 data | 363 | 0 | 0 | 0 | 4 | 0 | 367 |
| ch01 intro | 122 | 2 | 1 | 0 | 3 | 0 | 128 |
| ch12 conclusion | 64 | 0 | 8 | 0 | 0 | 0 | 72 |
| ch02 background | 179 | 1 | 0 | 0 | 5 | 0 | 185 |
| ch03 related | 147 | 1 | 0 | 0 | 0 | 0 | 148 |
| ch05 legacy | 180 | 0 | 0 | 0 | 7 | 0 | 187 |
| ch09 T3b | 150 | 0 | 0 | 0 | 0 | 0 | 150 |
| ch10 deployment | 172 | 1 | 2 | 0 | 0 | 0 | 175 |
| ch11 limitations | 74 | 0 | 1 | 0 | 0 | 0 | 75 |
| app_t21_note | 29 | 0 | 0 | 0 | 1 | 0 | 30 |
| **Total** | **2,486** | **7** | **25** | **0** | **34** | **0** | **2,552** |

MISMATCH counts tokens; they form 8 items (section 4). No value mismatch was found: every MISMATCH is context (scope, label or
attribution). Section 6 lists wording issues that carry no number token and are not in the counts.

## 4. Non-OK items: MISMATCH (context) and UNSOURCED
Ordered by severity. "Claimed source" is the NOTES entry.

| # | Where | Number(s) | Claimed source | What the source says | Proposed fix |
|---|---|---|---|---|---|
| M1 | ch02 l135 to l138 | 0.233, 0.365, 0.414; 0.824 to 0.849 | AUD l24 to l25; TT T19a F1 | AUD l24: "Same 25 models, same predictions" = the 25 cv5v3 out-of-fold pool models (PF row). The chapter says "On the pool, **the same predictions** score ...", right after the pre-protocol best model on the 49 clean test50 cells (EV l87). It ties the pool PF numbers to the test50 Track M ensemble. | "On the pool, PF's out-of-fold predictions (cv5v3, 5 seeds) score strict crack IoU 0.233, 0.365 and 0.414 ..." |
| M2 | ch07 l169 to l171 (Sec. TTA, "D4 on the candidate") | CS_D4 - CS +0.0055 [-0.0002, +0.0115]; false px 213 to 98; CS_D4 - PF_D4 +0.0087 [+0.0017, +0.0157] | TT T7a (b), desc. row; FTR l21, l28 | TT T7a caption: "Every CS and CS_D4 number is selection-biased." The chapter states the selection bias only from Sec. 7.5 (l179 to l180). ch10 l110 to l111 labels the same +0.0055 "selection-biased". | Add "(selection-biased: the swad readout was chosen on these cells)" to the paragraph. |
| M3 | ch01 l110 to l111 (contribution 5) | C3 - C2 -0.0025 [-0.0254, +0.0157] | TT T9 (V8 l45) | V8 l45: E1 opening #8, printed beside, decides nothing. The sentence gives no set and no scope, so it reads as a general or CV5 fact. Rule 3 (OUTLINE s0). | "its five-seed ensemble ... adds nothing measurable over its members on E1 (-0.0025 [-0.0254, +0.0157]; OP-A, recipe means over seeds 5 to 9, 101 of 106 cells CSIR; decides nothing)". |
| M4 | ch07 l144 | CS - PF +0.0166 [+0.0082, +0.0263] | TT T6 CS row; CX l20 | TT T6 row: "CS - PF (c3x, swad readout, declared secondary; selection-biased)". Chapter says only "declared secondary ... cannot be claimed". | Add "selection-biased" (the swad readout was later chosen on these cells). |
| M5 | app_t21_note l10 to l11 | "Arms have **three** seeds unless the row states another count" | none in ch05 NOTES s4 | Not stated in TT T21 caption or H04. Contradicted by rows that state no count: THIN-B3 used seeds 5 to 9 (`team_2026-10-31_next/verify_thin_b3.md` l1 "seeds 5-9"; ch05 l119 "all 5 seeds"); PF2 and later E1 protocols used 5 seeds. | Drop the sentence, or: "Seed counts are as stated in each row or its record; most P-series arms (10 to 13 Oct) have three." |
| M6 | ch04 l96 | 20 of 20; 0 of 2,906 | P02 l262; SI l284 | SI l92 (section 3a, full run under the pre-set rule): "all 20 same-serial pairs also carry a match_strong link ... None of the 2,906 different-serial pairs is linked by the matcher". It is the full-run cross-check, not the calibration. (SI l284 is the "Sister cells" item.) | "In the full run, all 20 same-serial pairs were also linked by pixels and none of the 2,906 different-serial pairs was." |
| M7 | ch07 l97 | LA-CE "mIoU-R13 at OP-C -0.0022 [-0.0112, +0.0060]" | TT T16a la_ce row | W2B_LACE_READ l3: primary = "la_ce at argmax minus PF with the post-hoc class-bias layer OP-C". The arm is at argmax; only the comparator is at OP-C. | "train-time logit offsets (mIoU-R13 at argmax against PF at OP-C, -0.0022 [-0.0112, +0.0060], dropped)". |
| M8 | ch05 l80, l106, l115 | P14 +0.082 [+0.046, +0.129] "on test50"; RN50 -0.0289 (thr 0.0251) "on test50 inactive"; SKR -0.0136 (thr 0.0100) "test50 crack IoU" | TT T21 | Values exact. The sentences lack "in-distribution, known leakage, context only" (OUTLINE s0 rule 4). The chapter states it once for all its numbers (l30 to l32), and l102 and l127 to l128 repeat it. Low severity. | Lead's call: add the phrase to the three sentences, or keep the chapter-level statement and say so in the rule. |

UNSOURCED: none. Caption counts that are not in the chapter NOTES trace to the figure makers' notes; add them to the NOTES:
ch10 F18 "467 cells at (0, 0)" (FIGURES_B.md l191; recomputed from F18_data.csv pool rows: 467), ch07 F21 "190 clean cells with at
least 20 crack px" (FIGURES_B.md l218; recomputed from F21_data.csv: 190), ch04 F6 "207 cells", "SDLE (2 cells)" (FIGURES_A.md l55,
l57; AUD l108), ch02 F2 "mean of 8 directions" (labels_audit.txt l77).

## 5. DERIVED and OK-rounded (all right)
| Where | Number | Source value | Check |
|---|---|---|---|
| ch08 l89, l107, l109, l133, l149, l250; ch01 l106; ch11 l12; ch12 l19 | 0.0742, "about 0.074" | SE 0.0265 (V8 l11); ruled derivation TT T4 / T8 note, GP G-N4 | 2.80 x 0.0265 = 0.07420; flagged derived in every place it is defined |
| ch06 l152 | 2.80 x 0.0265 = 0.0742 | as above | right; "derived" stated |
| ch06 l120 | 0.68 of C2's cost | 1,184 / 1,744 (T22; P10 l254 "derived") | 0.679; right |
| ch08 l196, l199 | "about 2 to 3 times", "about 2 times" (ER item 1 wording) | +0.0430 against +0.0154 and +0.0222 | 2.79 and 1.94; right |
| ch08 l196 | +0.043 | +0.0430 (V8 l11) | rounding (ER prints +0.043) |
| ch10 l95 | 106 x 0.174 = 18 s | 0.174 s (T22; IC l85) | 18.4; right |
| ch10 l33 (F18) | 467 cells at (0, 0) | F18_data.csv | 467; right |
| ch07 l225 (F21) | 190 clean cells, >= 20 crack px | F21_data.csv | 190; right |
| ch12 l12 to l13 | 21 claims: 1 / 1 / 1 / 3 / 8 / 2 / 5 | TT T20 Class column | confirmed #1; CV5-confirmed #6; passes #8; measured #17 to #19; n.d. #3, #4, #7, #10, #12, #13, #15, #20; failed #9, #21; descriptive #2, #5, #11, #14, #16; sum 21; right |
| ch01 l110; ch10 l108 | about 0.17 s | 0.174 (T22) | rounding |
| ch01 l122 | about 0.42 | relR@2 0.4157 (R8 l7) | rounding |
| ch02 l37 | about 250 px | 249 to 250 px (AUD l52) | rounding |
| ch03 l224 | about 159,000 cells | "about 159k cells" (BR l27) | rounding |
| ch07 l216 | at most 0.003 | 0.0031 (AUD l32) | rounding |

Also recomputed and right (counted OK because the source prints them): ch06 l100 212 / 303 = 0.70 ("under one false px per
crack-free cell"); ch06 l119 and ch10 l88 11.8 x (1,744 / 148 = 11.78); ch10 l92 20,700 and 930 cells per hour (3,600 / 0.174 and
3,600 / 3.88; IC l76, l64); ch05 l37 to l38 "one-sided p about 0.06 at 3 seeds, 2.8" (H11 l526); ch07 l136 "shrank by about half"
(0.0070 / 0.0135 = 0.52); ch09 l26 "84 to 86 cells" (106 - 22, 106 - 20); ch09 l24 folds 22 + 22 + 20 + 21 + 21 = 106 cells and
12 + 14 + 14 + 16 + 15 = 71 images; ch06 l49 to l50 91 + 8 + 17 = 116; ch04 l105 4 + 38 + 49 = 91.

## 6. Wording issues with no number token (not counted)
| # | Where | Issue | Source | Fix |
|---|---|---|---|---|
| W1 | ch07 l166 | "This is the one confirmed CV5 gain of the thesis." Sec. 7.8 (l234) says OP-C "passed its pre-set rule on both machines" (+0.0126 mIoU-R13; P02 l260 "OP-C is adopted"). | P02 l260 | "the one confirmed CV5 crack gain" (or "the one CONFIRMED contrast of a 5-seed CV5 read"). |
| W2 | ch08 l196 to l198 | Names the rows behind ER's "+0.015 to +0.022": COMBO - PF (swad_bn, +0.0154) and CS_D4 - PF. ER and FOR name no rows; the NOTES admit the attribution. The like-for-like readout of C2 without D4 is CS - PF +0.0166 (swad). Values right; attribution is the writer's. | ER l11; TT T6 | Keep ER wording without row names, or add "(our attribution)". |
| W3 | ch06 l88 vs ch04 l188, ch11 l62 | Inactive interval width "about +-0.05 to 0.07" (P10 l150) vs "about +-0.05 to +-0.06" (AUD l163). Both sourced; the thesis gives two sizes. | P10 l150; AUD l163 | Pick one (AUD is the measurement). |
| W4 | ch05 l98 to l99 vs ch07 l28 to l29, ch03 tab:rw_arms l162 | PF schedule: "ramps it to 0.1 x over the next 1,000 steps" (H04 l410) vs "then trains it at 0.1 times" (BR l43). | H04 l410; BR l43 | Use the H04 wording in ch07 and ch03. |
| W5 | ch05 l86 | "the label release moves PF's relF1@2 by more than the final recipe gains over PF on CV5": true (+0.025 vs +0.0222) but the CV5 C2 gain is selection-biased and not labelled. | TT T7a (c) | Add "(selection-biased)". |
| W6 | ch08 l60 to l62 | "With the SE expected (about 0.019), the smallest effect with 80% power was about 0.048 to 0.059": the range is for SE 0.017 to 0.021 (OR l127 to l128); at 0.019 it is about 0.053. | OR l123 to l128 | "about 0.019 (0.017 to 0.021), ... about 0.048 to 0.059". |
| W7 | ch01 l32 to l34; ch12 l46 to l48 | E1 levels 0.5995 / 0.4157 carry "seeds 5 to 9" and "OP-A" but not "101 of 106 cells CSIR". Levels, not claims; optional. | OUTLINE s0 rule 3 | Optional: add "101 of 106 cells CSIR". |

## 7. What was checked and holds (main chapters)
- ch08: every E1 number (P, both intervals, SE, G1 to G4, levels and seed ranges, fixed-model, relP / relR / relF1@1, strict IoU,
  printed-beside contrasts, A/A, strata with cells / clusters, BMRK levels per ER item 4, inactive, per-class, components), the test50
  table (v1.1 contrasts, levels, Pratt A, PV-S3, SEiPV readings) and registration times trace exactly to V8, R8, FOR, ER, OR, ADD.
  ER wording is used for items 1 to 5; every E1 claim sentence carries its scope; every test50 sentence carries its phrase.
- ch07: T5, T6, T7a, T7b, T15, T16a, T19b values; HR, SW, CX, R1, R2, W2A, HCS lines; RT l5 / l14 relP / relR (not in TT, gap O1)
  exact; GP D1 sentence verbatim (VT l111, l119: 1.159 at OP-A and OP-W; l95, l103: 1.107 / 1.121 pass on 532); OP-C values P02 l103,
  l260.
- ch06: every P10 line cited (l34, l36, l37, l41, l43, l53, l62, l76, l99, l114 to l116, l122, l123, l149, l150, l163, l193, l194,
  l211, l253, l254, l261, l464, l472), REL l27, l66, l95 to l96, HCS l46, l110. T20 #19 is used in its narrowed (strict IoU) form.
- ch04: T1, T2, T3a to T3c, T19a, T19b; AUD l24 to l163; SI l92, l193, l244, l246, l283, l301; LK; BR l24, l26.
- ch01, ch12: all values match TT, R8, RT, IC, SEV, AUD l192, RW l47, H02 l161 to l163, l217.
- ch02, ch03, ch05, ch09, ch10, ch11, app: spot checks of H02, EV, PR23, HA18, DH21, class CSV, RW s1 and s4, UniMatch V2 table,
  H17, BR l27, l75, P16 README (external pool at 100% labels: Sx100, so ch03 l235 holds), H11 l526 to l541, H19 l154 to l155,
  H04 l337, l410, P02 l56, T3R l20 to l46, l140 to l147, T3P l15 to l20, l30 to l50, l81, log.md l382 to l386, IC l12, l21, l31 to
  l35, l64, l67, l76, l84, l85, S1 / S3 severity notes.

## 8. Limits of this check
- Token extraction skips opening numbers (`#8`) and most spelled-out numbers; those were read by hand in the main chapters only.
- Citations (bibliographic fields) and figure contents were not checked; captions were.
- thesis_tables.tex was not compared with THESIS_TABLES.md; the chapters reference its tables by label only.
- One OUTLINE rule is applied as written (every test50 / E1 sentence carries its phrase); the lead may accept chapter-level scope
  statements instead (items M8, W7).
