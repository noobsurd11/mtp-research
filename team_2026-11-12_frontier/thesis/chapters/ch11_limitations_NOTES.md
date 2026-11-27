# NOTES for ch11_limitations.tex (Chapter 11, "Limitations and threats to validity")

Written 23 Nov 2026. Every limit is taken from a drafted chapter (ch04 to ch10, read-only) or from OUTLINE s2 Chapter 11 and
s7, and every number is copied from the table or result line that the drafted chapter's NOTES traces. No sealed file was read.

Short paths (T = /home/yugma/mtp/research/team_2026-11-12_frontier; md5 prefix as read 23 Nov):
TT = thesis/THESIS_TABLES.md (81c54378); V8 = results/final_opening_read/verdict.txt (bbb5f3b4, via TT and ch08 NOTES);
R8 = results/final_opening_read/read_e1/read.txt (via TT T11a); ER = results/FINAL_OPENING_READ_ERRATA.md (af55915f);
GP = thesis/GAPS.md (86108083); P02 = benchmark/PROTOCOL_v0.2.md (b8b7f66a); P10 = benchmark/PROTOCOL_v1.0.md (eeb3379a);
AUD = dataset_audit/REPORT.md (9d7e0d27); RAT = dataset_audit/rater/RESULT.md (via ch04 NOTES); SI = results/stageC/SPLIT_INTEGRITY.md;
IC = thesis/INFERENCE_COST.md (1e5a9002); SEV = results/severity/SEVERITY_SUMMARY.md (57e2bb4c); LIC = benchmark/release_v1/LICENCE_AUDIT.md
(via ch10 NOTES); T3R = harness/t3b/T3B_RULE.md (0c006d44); T3P = benchmark/T3B_PROPOSAL.md (569fbcb0);
EL = ../team_2026-10-31_next/e1_openings.md (52432548); OUT = thesis/OUTLINE.md.

## 1. Every limit, its number(s) and source
| # | Limit (short) | Numbers | Source | Drafted chapter that states it |
|---|---|---|---|---|
| 1 | one sealed set, one primary; size not pinned | lower end +0.0013; MDE about 0.074 (derived) | V8 l11; TT T8 note; GP G-N4 | ch08 s8.2 ("does not pin down its size") |
| 2 | recipe, not one checkpoint | S4 +0.0189 [-0.0403, +0.1068] | TT T9 (V8 l46) | ch08 s8.4 |
| 3 | OP-A only, deviation; width guards for OP-W | | V8 l142 | ch08 s8.2; ch06 |
| 4 | 101 of 106 CSIR; BMRK 5 cells support nothing | | V8 l140; ER l22 to l25 | ch08 s8.3 ("we draw nothing from it") |
| 5 | full cells carry it; half-cut n.d. | +0.0110 [-0.0289, +0.0722]; 62 cells | TT T10 (V8 l55) | ch08 s8.3 |
| 6 | unseen modules supported, not proven; about a third of image-id pairs testable; half-cut ids and BMRK no counterpart | | SI l200; P02 l262; SI l196, l199 (per ch04 NOTES s4.3) | ch04 s4.3 |
| 7 | prior looks | 7 registered openings, 3 looks at one contrast, reads before 31 Oct, R0 | V8 l138 (ER l28 wording) | ch08 s8.1 |
| 8 | model vs D4 separated, HRNet vs SWAD not; D4 part not resolved | | GP G-N3 (l13); ER l17 | ch08 s8.1, s8.4 |
| 9 | inactive n.d. on E1 | +0.0996 [-0.0310, +0.2162]; 10 cells | TT T8 (V8 l17) | ch08 s8.5 |
| 10 | width ratio on E1 under 0.5; cause not separated | 0.458, 0.463 | R8 l6, l7 (TT T11a) | ch08 s8.6 |
| 11 | E1 spent by opening #9 | | EL l35; T3R l150 | ch06, ch08, ch09 |
| 12 | selection bias of CV5 C2 numbers | +0.0222 [+0.0138, +0.0308] | TT T7a (c); V8 l139; ER l29 | ch07 s7.6; ch08 s8.1 |
| 13 | full-pool models: no held-out score | | GP G-N6 (l16) | ch07, ch08 |
| 14 | no HOUSE_D4; single-view CS - HOUSE holds 0 at OP-A | +0.0107 [-0.0009, +0.0229] | TT T7a HOUSE rows and note ("CS_D4 - HOUSE_D4: not read, no HOUSE D4 dump exists") | ch06 s6.6; ch07 s7.6 |
| 15 | no equal-cost comparator; 11.8 x C1 in FLOPs | 11.8 | IC l24; P10 (equal-cost deviation, via ch06 NOTES) | ch06 s6.4 |
| 16 | M covers seed noise, not folds; split-variance probe never run | | P02 l256; P10 (ch06 s6.5) | ch06 s6.5, s6.9 |
| 17 | few groups carry the passing contrasts | 17 (HRNET), 31 (C3X), 125 groups with crack px | AUD l128 to l131; TT T19b | ch04 s4.5; ch07 s7.7 |
| 18 | 2-seed tier on leaky cv5v2, two machines, read per machine | | P10 R1 ruling (ch06 s6.4 "Seeds and tiers"); ch07 intro | ch06, ch07 |
| 19 | one double annotation | strict 0.259, relF1@2 0.829 | AUD l39 to l41; TT T19a F2 | ch04 s4.5 (G-W10 wording kept: "one double annotation") |
| 20 | label errors minority; detector recall unknown; raters one model | 0.244 [0.105, 0.436] | RAT l32; TT T19a F5; AUD l94; GP G-N12 | ch04 s4.5 |
| 21 | strict IoU = convention | PF 0.233 / 0.365 / 0.414 | TT T19a F1 (AUD l24 to l25) | ch04 s4.4 |
| 22 | width is a source convention; guard partly measures annotators | ARTS 1.59, BMRK 3.09 | AUD l107 to l108; TT T19a F7 | ch04 s4.5; ch07 s7.4 (judgement there) |
| 23 | E1 labels about 1.5 x wider | 1.5 | T3R l111; P10 l68 | ch04 s4.2; ch09 |
| 24 | 2 px tolerance from few duplicate annotations; relF1@2 blind to width | 2 px | ch02 s2.5 ("on the few such pairs we have"); ch06 s6.3 (95th percentile, 2.000 px) | ch02, ch06 |
| 25 | images are windows | 57%, 71% | AUD l54; TT T19a F3 | ch04 s4.5; ch06 |
| 26 | inactive under-powered on the pool | 33 of 285 groups; Kish 12.9; +-0.05 to +-0.06 | AUD l74, l163 (per ch04 NOTES) | ch04 s4.5 |
| 27 | test50 leakage, 19 counted openings; no claim to beat a published model | 8 (7 + 1), 7, 19; 19 openings | ER l19 to l21; TT T2; TT T1 (19 counted openings); P10 l114 | ch04, ch06, ch08 s8.7 |
| 28 | BMRK and SDLE not groupable by physical module | | P02 l263; P10 (ch06 s6.9 "BMRK and SDLE cells cannot be grouped by physical module") | ch06 |
| 29 | one dataset family; source recognisable | 0.94 | AUD l119; TT T19a F8 | ch04 s4.5; ch06 s6.9 |
| 30 | weak classes unsolved; OP-C not in any final model | material, edge dark 0.0000; OP-C +0.0126 [+0.0077, +0.0167] | TT T12a (V8 l63 to l75); P02 l260 (via ch07 NOTES l131) | ch07 s7.8; ch08 s8.5; OUT O6 |
| 31 | licences: BMRK = ELPV CC BY-NC-SA 4.0; BenchmarkEL no licence file; research-only; retraining without BMRK not measured | 50 cells | P10 l86 to l88; LIC l27, l32; ch10 NOTES l113 to l121 | ch10 s10.6 |
| 32 | no WattCycle module imaged | | SEV l64; BR l30 | ch10 s10.7 |
| 33 | shared-host timing; network time only; upper bounds | | IC l13, l14, l82 | ch10 s10.5 |
| 34 | severity validated only for PF OOF on pool cells | | SEV l16; GP G-N11 | ch10 s10.1 |
| 35 | power claim not supported; no watt figure | | SEV l19 to l37; TT T20 #21; SEV l9 | ch10 s10.2 |
| 36 | few-shot: about 9 effective images; 80% power at about +0.085; folds by image id may be optimistic | 9, +0.085 | T3P l49; T3R l145; T3P l45, l83; T3R l151 to l152 | ch09 |

## 2. Judgement sentences kept
- #22 "so the per-source width guard partly measures the annotators" (ch07 s7.4: "the guard measures an annotation convention as much as
  a model", marked judgement there).
- #1 "E1 supports a gain without pinning down its size" (ch08 s8.2 judgement, shortened).
- #29 "a shortcut open to any model" (AUD l124: "a shortcut is available, not that a model uses it"; the chapter does not say any
  model uses it).
- All other items are statements of what was or was not measured.

## 3. Placeholders and citations
- \PENDING: 0 since 23 Nov (t3b_fill). Former marker: `\PENDING{T3b verdict: one sentence on the limit its result adds, for example that a NOT CONFIRMED verdict leaves gains below about +0.085 open}`; see section 5.
- \CITE: 0. \FIG: 0. No citations (all limits refer to earlier chapters); no .bib file.
- Cross-references: tab:T20 only (the earlier chapters are not \ref'd item by item to save space; add if the lead wants them).

## 4. Notes for the lead
- Not included (kept out for length; each is in an earlier chapter): GPU nondeterminism of the resumed full-pool runs (ch08 s8.1);
  the published-row conventions of the test50 table (ch08 s8.7; folded into item 27); ELPVPower licence version not stated (ch10).
- Length: 1,021 words in 36 one-sentence items, about 2.3 pages with list spacing. Item 24 (tolerance) and item 29 (one family) are
  the first to cut if the chapter must be 2 pages.
- OUTLINE Ch 11 says "34 module groups hold all pool inactive cells" (P02 l195); ch04 and the audit use 33 of 285 groups (AUD l74).
  I used 33 (the audit's later count, as in ch04 and ch06).

## 5. T3b fill (23 Nov 2026, t3b_fill, after the read)
Sources (T = /home/yugma/mtp/research/team_2026-11-12_frontier): VT = T/results/t3b_open9_read/verdict.txt (bfe583db);
RT = T/results/t3b_open9_read/read_t3b/read.txt (922b965e). Numbers copied as printed; none recomputed. No raw record, E1
image, label or dump was read.

| Text (ch11, item 36 and new item 37) | Value | Source |
|---|---|---|
| confirmed gain +0.2213 [+0.0977, +0.3504] | CONFIRMED | VT l6, l9 |
| few-shot result inside E1; 3 seeds; 101 of 106 cells CSIR | 3 seeds; 101 / 66 | VT l71 (Seeds: 3), l32 |
| says nothing about a new layout without labels | scope | VT l2, l64; ch09 s9.4 |
| ALL - HALF not separated, +0.0171 [-0.0246, +0.0625]; does not say how many labelled cells a layout needs | | VT l18 |
| new item 37: models learn the about 1.5 x wider E1 labels; width ratio ALL / ZS 1.426 (reported); lifts strict IoU and pixel recall without finding more cracks; relF1@2 decides, less sensitive, not immune | 1.426 | VT l10, l70; "not immune" from ch09 s9.4 (T3R l152 to l153) |
