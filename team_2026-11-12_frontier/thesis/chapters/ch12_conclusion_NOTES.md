# NOTES for ch12_conclusion.tex (Chapter 12, "Conclusion and future work")

Written 23 Nov 2026. The claim list is T20. No sealed file was read.

Short paths (T = /home/yugma/mtp/research/team_2026-11-12_frontier; md5 prefix as read 23 Nov):
TT = thesis/THESIS_TABLES.md, **91c867f0** (the 09:24 rebuild by the tables fix: T20 row 19 narrowed to strict IoU; it is now at
TT l682). Earlier read 81c54378 (row 19 unnarrowed). thesis_tables.tex c2b2bc89. Row numbers of T20 unchanged (1 to 21).
AUD = dataset_audit/REPORT.md (9d7e0d27); P02 = benchmark/PROTOCOL_v0.2.md (b8b7f66a); P10 = benchmark/PROTOCOL_v1.0.md (eeb3379a);
SEV = results/severity/SEVERITY_SUMMARY.md (57e2bb4c); RT = results/final_tta_read/read.txt; R8 = results/final_opening_read/read_e1/read.txt
(via TT T11a); BR = BRIEF.md (bc06edd2); OUT = thesis/OUTLINE.md.

## 1. Every number, with its source
| Number / fact | Source |
|---|---|
| 21 claims; class counts: confirmed 1 (#1), confirmed CV5 only 1 (#6), passes selection-biased 1 (#8), measured 3 (#17, #18, #19), n.d. 8 (#3, #4, #7, #10, #12, #13, #15, #20), failed 2 (#9, #21), descriptive 5 (#2, #5, #11, #14, #16) | TT T20 "Class" column (my grouping: #2 is "descriptive (full); n.d. (half-cut)", counted as descriptive; #6 "confirmed (CV5); n.d. (E1)", counted as confirmed on CV5) |
| claim 1: +0.0430 [+0.0013, +0.1043]; four guards pass; scope (unseen modules supported not proven; OP-A; 101 of 106 CSIR; seeds 5 to 9) | TT T20 #1, T8; V8 l11 to l15, l140, l142 |
| claim 2: full cells carry it, half-cut not detected | TT T20 #2 |
| claim 5: "most of the gain is the model" | TT T20 #5 (ER item 2 wording) |
| lower end near 0; MDE about 0.074 (derived) | TT T8 note; GP G-N4 |
| claim 6: D4 on PF CV5 +0.0134 [+0.0066, +0.0207]; "on E1 the D4 part is not resolved" | TT T20 #6; T7a (a) |
| claim 8: +0.0222 [+0.0138, +0.0308]; selection-biased; ARTS width fails on 416 clean cells | TT T20 #8; T7a (c); GP D item 1 |
| claim 17 wording | TT T20 #17 |
| claim 18: minority; no contrast moves > 0.003 | TT T20 #18 |
| claim 19 (narrowed): strict IoU 0.320 vs 0.365 (+0.045); strict-IoU contrasts against PF at most +0.0333; not claimed for relF1@2: release +0.025, CB_D4 - PF +0.0243 (information only), 0.97 of the shift | TT T20 #19 at l682 (91c867f0); P10 l36 |
| claims 3, 4, 7, 10, 12, 13, 15, 20 n.d. | TT T20 class column |
| claim 9 "fails its guards"; claim 21 "not supported" | TT T20 #9, #21 |
| claim 14: two EL-paper models below PF, 2-seed screens | TT T20 #14 (ucf -0.0773, pratt -0.0932); ch07 summary ("a third ... not separated") |
| claim 11: strict-IoU gain of weight averaging a convention effect | TT T20 #11 |
| claim 16: levels, no interval for the gap | TT T20 #16 (G-W9 wording) |
| target relR@2 >= 0.90 at relP@2 >= 0.90 | BR l57 |
| E1 C2 relP@2 0.5995, relR@2 0.4157 (mean over seeds 5 to 9, OP-A) | R8 l7; TT T11a |
| CV5 CS_D4 0.9216 / 0.8211 (OP-A, selection-biased) | RT l14 (checked 23 Nov); ch07 s7.6 |
| inactive n.d. on E1 and CV5 | TT T20 #12; T7b (CS_D4 - PF inactive +0.0328 [-0.0128, +0.0826]) |
| material, edge dark 0.0000 on E1 for every arm | TT T12a (V8 l63 to l75) |
| second annotation of a few dozen pool cells; planted errors for detector recall | AUD s5 (l181 to l187) |
| expert look 2 to 3 h at 49 cells, confirm or reject only | AUD l192 |
| split-variance probe never run | P02 l256 |
| HOUSE D4 not made; FLOP-matched comparator required for later entries | TT T7a note ("no HOUSE D4 dump exists"); ch06 s6.4 (P10 equal-cost rule) |
| OP-C raised mIoU-R13 on the pool | P02 l260 (via ch07 NOTES l131) |
| retrain without 50 BMRK cells; BenchmarkEL authors' answer | ch10 s10.6 (LIC l100, l27) |
| pilot: STC I-V, EL at known current, drone thermal >= 600 W/m2; about 31 modules for a true rho of 0.5; rule before measuring | SEV l55 to l63 |
| release as lists and code | ch06 s6.8 (P10 item 15) |

## 2. Judgement sentences kept
1. "Our reading (judgement): the lasting result of this work is the instrument rather than the model." (OUTLINE s7 risk 1 framing.)
2. "It shows that published EL segmentation numbers cannot be compared, measures why (...), and replaces them with a protocol under
   which one recipe gain survived a sealed test." (summary of ch03, ch04, ch06, ch08.)
3. "the size of the gain is open" (ch08 s8.2 judgement: "it does not pin down its size").
4. Future-work items are proposals; each names the limit it would change (ch11).
5. "with half-cut cells among them and the module identity recorded at capture" (my proposal; follows from ch04 / ch09 limits).

## 3. Placeholders and citations
- \PENDING: 0 since 23 Nov (t3b_fill). Former markers (2):
  1. `\PENDING{T3b verdict: the new row of Table~\ref{tab:T20}, the claim that labelled cells of E1's layouts raise the out-of-fold crack relF1@2 of the C2 recipe on E1 against the same recipe zero-shot, with Delta, its interval, the guards and the status word, and the half-cut stratum}`
  2. `\PENDING{T3b verdict: one sentence on what the few-shot result adds for the half-cut layout}`
- T20 row 22 added 23 Nov (t3b_fill); the count sentence now reads "Of the 22 claims ..." (section 5).
- \CITE: 0. \FIG: 0. No citations, no .bib file.

## 4. Notes for the lead
- T20 #19 as rebuilt says "more than any method contrast against PF on CV5". The cv5v2 screens hold EL-paper rows whose strict IoU
  level is much further from PF than +0.045 in the other direction (T15: ucf_dlv3_r50_pf 0.287, pratt_dlv3p_wcec 0.258 against PF
  0.365). The chapter therefore says "more than any method gain over PF on CV5"; T20's claim text may want "gain" too.
- ch06_protocol.tex l24 to l25 (md5 df63b2cc as read 23 Nov) still says "The label release moves levels more than any method"
  (unnarrowed), and P10 l36 says the same. Not my
  file; flagged for the lead.
- Length: about 1,060 words, about 2.3 pages.

## 5. T3b fill (23 Nov 2026, t3b_fill, after the read)
Sources (T = /home/yugma/mtp/research/team_2026-11-12_frontier): VT = T/results/t3b_open9_read/verdict.txt (bfe583db);
RT = T/results/t3b_open9_read/read_t3b/read.txt (922b965e). Numbers copied as printed; none recomputed. No raw record, E1
image, label or dump was read.

| Text (ch12) | Value | Source |
|---|---|---|
| "Of the 22 claims": one confirmed zero-shot on the sealed set (#1), one confirmed as a few-shot result inside it (#22), one confirmed on CV5 (#6), one passes selection-biased (#8), measured 3, n.d. 8, failed 2, descriptive 5 | 22 (derived: count of T20 rows after the rebuild); class counts derived from the T20 "Class" column, grouping as in section 1 | T/thesis/THESIS_TABLES.md T20 (rebuilt 23 Nov, 22 rows); 1+1+1+1+3+8+2+5 = 22 (derived) |
| few-shot paragraph: inside E1, out of fold over 5 folds by source image; seeds 5 to 7; OP-A; 106 cells and 71 clusters; 101 CSIR | | T/results/t3b_open9_read/run.log l7; VT l5, l65, l32, l69 (folds by image id) |
| ZS = opening #8's C2, seeds 5 to 7 | | VT l65 |
| +0.2213 [+0.0977, +0.3504]; both guards passing; CONFIRMED (claim 22) | | VT l6, l7, l8, l9 |
| half-cut +0.2530 [+0.0878, +0.3885]; without scuff -0.0701 [-0.3019, +0.0517] not separated | | VT l27, l29 |
| HALF - ZS +0.2042 [+0.0718, +0.3366]; ALL - HALF not separated | ALL - HALF +0.0171 [-0.0246, +0.0625] | VT l17, l18 |
| s12.2 sentence: labelled cells of the half-cut layout raise crack relF1@2 out of fold (+0.2530 [+0.0878, +0.3885], a stratum, decides nothing), half of the labelled images about the same gain; "on this evidence, a new layout calls for some labelled cells of it" | | VT l27 (stratum, decides nothing per VT l25); judgement (mine), inside the paragraph marked "Our reading (judgement)" |
