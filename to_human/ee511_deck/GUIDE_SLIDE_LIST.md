# Guide's running slide list (EE511 deck). Kept by the guide session; source of each check in brackets.

## Deck plan v1 (from mtp-87, 25 Nov), with the guide's checks
| # | Slide | Check | Flag sent to mtp-87 |
|---|---|---|---|
| 1 | Title | ok | |
| 2 | Problem: crack 0.19% px, 1-2 px labels; inactive rare; 24 classes | ok (handbook 00, 11) | |
| 3 | Related work timeline + gap 22 / 0 / 18 | ok (RELATED_WORK s4; handbook 05 s3.2 Pratt 2021 U-Net; R07 Fioresi DeepLabv3) | |
| 4 | Data: P532 by source, E1 106 (101 CSIR, 5 BMRK, 62 half-cut), test50; F1 | ok (T1). Pool has 0 half-cut cells (T1) | suggest adding "pool has 0 half-cut cells" |
| 5 | Journey + effort strip | "1,000+ trained models" not in any file found | yes: trace or drop |
| 6 | What we tried | +0.117 is CsM5 (tolerant PL + CutMix + separate BN), not hard PL (BsM5 +0.107); "SKCDF" must be "SKCDF-style decoupled decoder"; copy-paste is not pretraining; phase 1-2 numbers are legacy protocol (test50) | yes |
| 7 | Measurement traps | "8 test cells = pool cells" -> "same physical cell as a pool cell, 7 confirmed by pixels" (errata 3); 1 px shift 0.47-0.56 is old-label (FAQ Q2); v1.1 alternative: PF 0.233 / 0.365 / 0.414 (T20 r17) | yes |
| 8 | Protocol | ok (T4) | |
| 9 | Rows table (T15) | numbers match T15; mixed seeds (PF 5, rest 2); screens decide only promotion | label it |
| 10 | Final model on E1 | numbers match FINAL_OPENING_READ; add recipe-not-checkpoint, full vs half-cut, errata 2 on D4 | yes |
| 11 | Few-shot T3b; F20 | ZS 0.488 / ALL 0.709 are means of the 3 per-seed values (derived); "carried by half-cut" = half-cut with scuff (+0.300); half-cut without scuff -0.070 n.d.; full +0.153 also above 0 | yes |
| 12 | Qualitative F21 | F21 shows CV5 pool cells (out of fold), PF vs CS_D4, not E1; CS_D4 is selection-biased (T5) | yes |
| 13 | Conclusion | "literature models 0.08-0.09 below": only 2 of 3 (Hanifi VGG16 -0.0064 n.d.); "a few target cells beat any method" overstates | yes |
| 14 | Weaknesses & further | ok; thermal and severity were looked at with nulls (doc 23 s7b, handbook 11 r53-55) | suggest wording |
| 15 | Thank you | | |

## Deck v2 (EE511_EL_segmentation.pdf, 25 Nov 13:30): all 8 v1 fixes in; effort_count.md traces 1,000+ (987 legacy + >= 380 benchmark)
Flags sent for v2:
1. S4 / S8 / S10 "E1 read once / opened once": wrong for E1; final models read once (#8), E1 had 7 earlier registered openings (verdict.txt l138, errata 5).
2. S8 "D4 TTA: confirmed": only on PF, CV5 (+0.0134); on the candidate CS_D4 - CS +0.0055 NOT CONFIRMED, NO LOSS (T7a).
3. S10 "full-resolution branch, so 1-2 px cracks survive": thesis says "keeps a high-resolution branch"; mechanism not measured; measured = recall at equal precision.
4. S10 SWAD: swad_const = constant LR, uniform average of iterates 10k-20k (fixed window).
5. S5 footnote "every experiment ... protocol" overstates (P3, P18 exploratory); "gain is gone" -> "not detectable".
6. S7 "+0.045 more than any method gain" -> "on CV5" (T20 r19; max strict-IoU contrast +0.0333).
7. S14 "gains under 0.01 can hide" -> E1 MDE about 0.074 (T4).
Minor: S6 ALHVR "halves inactive recall" is post hoc.

## Q&A facts collected (for coaching)
- HRNET - PF relF1@2 +0.0104 falls below M after removing 1 module group (greedy), and to +0.0073 (no pass) on 3 px labels; C3X - PF passes under all 4 label variants (thesis p. 27 to 28, Table A.28).
- relF1@2 of PF on centreline / v1.1 / 3 px: 0.824 / 0.846 / 0.849 (strict IoU 0.233 / 0.365 / 0.414) (thesis p. 27).

## Deck v3 (25 Nov): all 7 v2 items + minor applied; checked pages 4 to 8, 10, 14. No open flags. Copy in ~/Downloads.
## Coaching progress
- S1, S2: coached (waiting for the user's say-back of S2).
- S3: coached.

## Deck v4 plan (19 slides, plots; 25 Nov). New order:
1 Title, 2 Problem, 3 Related work, 4 Dataset, 5 Journey, 6 Exp I: SSL plot (inactive IoU vs label fraction, test50), 7 Exp II: tried table,
8 Measuring (F5 + chips), 9 Protocol, 10 Results I (T15), 11 Results II (T5 levels + T6/T7a forest), 12 Final model + cost,
13 Results III E1 (T11a table + T9 forest), 14 Results IV few-shot (bars + strata forest), 15-17 qualitative (pool methods; E1 base vs final; E1 ZS vs few-shot), 18 Conclusion + limits, 19 Thanks.
Checked: S6 values = p13 README l23-26, p16 README l38-43; S11 = T5; S12 = T22; S13 = T11a / T9; S14 = t3b_verdict.
Notes sent: S6 legacy test50 + seed sd + pool differs at 100% + no 10% point; S11 registered verdict words + selection bias; S12 network time only;
S13 only C2-C1 decides; S14 strata decide nothing; S15-17 selection rule fixed before viewing, rows-1 dumps deleted 17 Nov, out-of-fold only.
Coaching: old S1-S5 = new S1-S5 (done). Next: new S6 (SSL plot).
## Deck v4 built 13:40 (19 pages); pages 6-14 checked: all values match. Minor notes sent: S10 "same training" except Pratt wCE; S10 inactive highlights are noise at 2 seeds (M inactive ~0.05).

## Deck v5 (13:48; ~/Downloads copy). Order: 1 Title, 2 Problem, 3 Related work, 4 Dataset, 5 Research path (table), 6 SSL plot, 7 What we tried,
8 Protocol, 9 Final model + cost, 10 Quant I (T15), 11 Quant II (CV5), 12 Quant III (E1), 13 Quant IV (few-shot), 14 Qual I (EL-paper models, pool, PF),
15 Qual II (E1 C1 vs C2), 16 Qual III (E1 ZS vs ALL), 17 Conclusion I: questioning the dataset, 18 Conclusion II + further discussion, 19 Questions.
Flags sent (S17): scuff-as-crack is the original release (v1.1 ignores); 8 test cells = same physical cell; add leak check "not separated";
scope 11,938 pool (P16, 2 sources); "no protocol" -> 0/22 module-disjoint, 18 no interval; add label errors minority (T20 r18).
Minor: S5 row 3 different contrasts; S18 "equal training" except Pratt wCE; S14 "Ours" = PF.
Coaching done: S1-S4, S6 (SSL plot). Next: S5 (quick), S7.
## Deck v5 final (~/Downloads): S17 fixes applied and checked; S15-16 landscape figures checked against QUAL_NOTES (rule v2 mechanical; v1 with another rule viewed first: disclose if asked). No open flags.
Coaching: S1-S4, S6 done; S14-S17 coached next (builder request); then S5, S7-S13, S18.
- 13:5x: full presenter script for the 19-slide deck written to PRESENTER_SCRIPT.md (relF1@2 definition from thesis s6.3: pixel-level, not skeleton).

## MTP deck v1 (27 Nov; built by the guide in to_human/ee511_deck/mtp/, EE511 files untouched)
16 pages: 1 Title (Yash Patil B23222, Muskan B23274, Guide Dr. Praful Hambarde), 2 Problem, 3 Data, 4 Prior work reproduced, 5 Everything we tried,
6 SSL plot, 7 Measuring fairly, 8 Protocol, 9 Architecture study (own schematics + T16a screens), 10 Final model (no params / compute, user's call),
11 Pool 5-seed forest (T6/T7a), 12 E1 forest + levels (T table E1 levels, FINAL_OPENING_READ, t3b), 13 Qual E1 C1 vs C2 (qual_e1_final_wide.png),
14 relP@2 vs relR@2 (T15 training-machine rows), 15 Conclusion, 16 Thanks. Few-shot photo strip dropped (2-slide qualitative limit).
## MTP deck v2 (27 Nov): user rejected v1 style ("cheap, big numbers, cartoon architecture"). Rebuilt in the mid-sem deck style
(to_human/build_midterm_deck.py constants: Archivo Black / Inter, panel #142B29, accent #2A7F78, booktabs tables, one takeaway line).
Files: mtp/deck2_src.html, mtp/build2.py, mtp/MTP_EL_segmentation_v2.pdf. Architecture figures = crops of the original papers' figures
(arXiv 1505.04597 Fig 1, 1807.10165 Fig 1a, 1802.02611 Fig 2, 1908.07919 Fig 2) in mtp/fig/, credited on slides 9-10.
Slide 9 table = T16a screens; slide 11 = T6/T7a; slide 12 = FINAL_OPENING_READ + E1 levels table + t3b. No pptx: python-pptx not installed (no-install rule).
- 27 Nov: order changed (user): 5 SSL, 6 Measuring, 7 Everything we tried. Muskan 1-6, Yash 7-15. Companion and Muskan context docs (Claude Docs) updated to match.
