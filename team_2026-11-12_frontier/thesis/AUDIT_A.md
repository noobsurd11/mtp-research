# Audit A: abstract, ch01 to ch05, app_t21_note (27 Nov 2026)

Scope: chapters/abstract.tex, ch01_intro.tex, ch02_background.tex, ch03_related.tex, ch04_data.tex, ch05_legacy.tex,
app_t21_note.tex (working copy). Server read only (cat, sed, grep, ls, md5sum). Primary records copied to my scratchpad by `cat`
over ssh; md5 prefixes as read today: verdict.txt bbb5f3b4, read_e1/read.txt 82cea48a, final_tta_read/read.txt 54214525,
FINAL_OPENING_READ_ERRATA.md af55915f, t3b verdict.txt bfe583db, t3b run.log 261a1132, INFERENCE_COST.md 1e5a9002,
dataset_audit/REPORT.md 9d7e0d27, rater/RESULT.md c119a04f, SPLIT_INTEGRITY.md 26b3c76a, C3_LEAK_READ.md 43e8009e,
LABELS_V11.md 70872c46, PROTOCOL_v0.2.md b8b7f66a, PROTOCOL_v1.0.md 01804c54 (frozen 23 Nov on eeb3379a), BRIEF.md bc06edd2,
RELATED_WORK.md f2a6adcd, THESIS_TABLES.md d58e803a (identical to the server copy). T = team_2026-11-12_frontier.
Placeholders: none left in my files (\FIG uses all resolve to figures/F*.pdf; no \PENDING, \CITE, "??"); no em / en dash; every
\cite key exists in references.bib; every \ref target exists (fig:F* labels come from the \FIG macro).

## 1. CHANGES

| file:line | old text | new text | evidence |
|---|---|---|---|
| ch01_intro.tex:70-71 | "under the rule of that time, pseudo-labels helped only at 5\% labels" | "... helped only at 5\% and 10\% labels" | ~/mtp/research/results/p11/README.md:38 "\| **Cm − A (rule 3)** \| +0.002 (0.012) \| **+0.071 (0.067)** \| **+0.013 (0.012)** \| **Cm beats supervised** (credited: rule 2 holds) \|" (P11 is at 10% labels: handbook/11 l181 "\| 10% \| P11 \| joint BN, matched view \| Cm − A \| ... \| passes (credited) \|"). The thesis's own T21 row "P11 / P12" also reads "supported for inactive" at 10%. Category 5 (claim stronger than evidence). |
| ch02_background.tex:76-77 | "On the revised labels (label set v1, Chapter~\ref{ch:data}), crack takes 0.19\% of the train pixels and occurs in 209 of the 478 train cells;" | "On the release masks crack takes 0.19\% of the train pixels; on the revised labels (label set v1, Chapter~\ref{ch:data}), crack occurs in 209 of the 478 train cells;" | ~/mtp/research/data_analysis/benchmark_el_report.md:1 "# BenchmarkELimages `dataset_20211104`: first-hand data analysis" (8 Oct, before revised labels), l11 "\| 478 / 54 / 50; crack 14, inactive 11; bg 69.2%, padding 17.3%, crack 0.186% of train pixels \| same \| confirmed \|"; handbook/03 l106 cites the 7 Oct handoff. Under v1 the train crack px are 271,805 (TT T3b), i.e. not 0.19%. The 209 is the v1 count (TT T3b "Crack cells v1 to v1.1 \| 209 to 206"). Category 1 (number attached to the wrong label set). |
| ch03_related.tex:124-125 | "print a mean IoU of 95.98 on the validation set and 72.52 on the 360 test images" | "95.98\% ... 72.52\%" | RW_SOURCES.tsv:151 "R17 stc "validation" MIoU 95.98 Table I, PDF p. 5"; :155 "R17 stc test MIoU 72.52 Table II". Paper prints percent; the chapter's other IoU values are on 0 to 1 (e.g. 0.7447 two lines above), so the scale must be labelled (brief: percent vs 0 to 1). |
| ch03_related.tex:226-227 | "scores 67.0 mIoU ... and 83.7 ..., while UniMatch V2 scores 79.0 and 86.7" | "67.0\% mIoU ... 83.7\% ... 79.0\% and 86.7\%" | /home/yugma/papers/2025-Yang-UniMatch-V2-...-cd81b3.md:274-275 "\|Labeled Only (85.0)\|-\|\|67.0\|75.6\|81.8\|83.7\|85.6\|\|" and "\|**UniMatch V2**\|Ours\|DINOv2-S\|79.0\|85.5\|85.9\|86.7\|87.8\|"; header l253 "1/16 (92) ... 1/2 (732)" (values and fractions correct; scale was unlabelled). |
| ch03_related.tex:235 | "adding the external unlabelled pool at full labels did not help." | "... gave no detectable gain." | handbook/10 l816 "**External pool at 100%:** n.d. on every primary, test and unseen modules"; handbook/11 l195 "\| 100% \| P16 \| same, external pool \| Sx100 − A100 (5 v 5) \| ... \| n.d. (−0.002 / +0.002 / −0.002) \|"; BRIEF l75 "n.d. at 100% with the external pool". Category 3 (n.d. worded as no effect). |
| ch04_data.tex:186 | "These candidates are not label noise: in a blind check by AI raters (below), 30 of 40 were judged model errors and 5 of 40 label errors" | "Most of these candidates are not label noise: ..." | T/dataset_audit/rater/RESULT.md (c119a04f) "inactive: model error 30, ambiguous 5, no majority 1. By type: ... **spurious inactive 5/40 label error, 30/40 model error**" and "only about 0.22 [0.08, 0.53] of the image-supported inactive candidates ... are label errors". The old sentence contradicted its own 5 of 40. Category 5. (Suggested by the writer in ch04 NOTES s2 item 8.) |
| ch05_legacy.tex:104 | "(B6, 2 seeds) found no in-distribution inactive difference" | "found no detectable in-distribution inactive difference" | THESIS_TABLES.md T21 row B6 "inactive IoU Δ −0.0144, two-stage CI [−0.0977, +0.0570] \| **not detectable** (n.d., low power)". Category 3. |

Diff of all seven against thesis_orig checked (`diff` shows only these lines).

## 2. CONFLICTS (sources disagree; not resolved by me)

1. **SEiPV-Net Dice identity.** RELATED_WORK.md l107 (reading 4) says SEiPV's "mIoU" 0.8604 "is a pooled pixel quantity with background
   (IoU = Dice / (2 - Dice) within 0.001)". The arithmetic holds for "IoU" 0.7447 with Dice 0.8531 (0.8531 / 1.1469 = 0.7438), as
   RELATED_WORK.md R03 (l19) and PUBLIC_BENCH l28 state. ch03 l121 follows R03 (correct). RELATED_WORK.md l107 should be fixed by
   its owner if it is quoted anywhere.
2. **Hanifi 2025 test set and our pool.** verdict.txt l93 and T13a: "Not comparable (other test sets that overlap our training
   pool): Attention-Based SegNet 2024, Ramadan 2026, Hanifi 2025, Torpey 2024"; ch03 l135-137 repeats this for all four.
   RELATED_WORK.md l96 lists "Hanifi IEA/AIE 2025" under "Overlap not checkable from the paper" (own re-split of 20221008, not
   released). Text left as is; the lead may soften "also overlap our pool" for Hanifi to "probably overlap".
3. **Unlabelled-to-supervised loss ratio.** handbook/11 l500: "The unlabelled loss was about 10× smaller than the supervised loss.
   CutMix raised the ratio to 0.77 (P13)"; handbook/11 l83 (claim 11): "unlabelled/supervised loss ratio 0.46 → 0.77" (Cs5 to
   CsM5). ch05 l58-59 copies l500. The "10×" may refer to earlier arms; not settled from the files read.
4. **BRIEF l22 vs the data report.** BRIEF puts "crack (id 14): 0.19% of train pixels, in 209 of 478 train cells" under "Labels in
   use: Revised"; the 0.186% is a release-mask (20211104) number (benchmark_el_report.md l11). Fixed in ch02 (CHANGES row 2);
   reported here because the BRIEF wording is the root.
5. **E1 description in older files.** BRIEF l25 ("106 cells from 67 modules ... 58 of them are half-cut") and handbook/03 l338
   ("67 modules, of which only 1 has cells among our 582") against SPLIT_INTEGRITY 5a / verdict.txt l140 (71 image ids; 62
   half-cut cells; "No E1 image id is linked to any other image id"). All my chapters use the later result files; no change.

## 3. UNVERIFIED (could not trace to a primary record)

- ch02 l204-207: crack modes A / B / C and power loss attributed to kontges2011risk; per ch02 NOTES s4 the 2011 paper was NOT read
  (claim taken from Pratt 2025 ICTAS, which cites the 2010 EU PVSEC version). Citation content unverified.
- ch02 l16: kontges2014iea "Sec. 4.6" for fingers / busbars / ribbons: section number not checked (report not on disk).
- ch02 l213-215: Dhimish 2021 "12 cells", "25 to 100 °C": 12 cells confirmed (DH21 l9); the temperature range is in the abstract
  per NOTES, not re-read beyond the first clause.
- ch02 l87: CSIR "median intensity standard deviation 24, against 34 to 48" only in handbook/02 l274 (no primary output opened).
- ch02 l74-76 (86.5%, four classes under 1,300 px, 7 / 8 absent classes): handbook/02 l141-145 only.
- ch01 l17 / ch02 l216: "EL rig 2 to 3 months away as of 4 November 2026": SEVERITY_SUMMARY.md l64 "(R, thermal team)"; primary
  decision record not opened.
- ch03 table rw_datasets, E-SCDD "one class added" and "crack and inactive pixels unchanged": handbook/17 l32-47 only.
- ch05 l37-38 ("one-sided p ≈ 0.06 at 3 seeds ... two-sided needs 2.8"): handbook/11 l486 only (arithmetic not redone).
- ch05 l91-99 encoder cosines (0.005 to 0.018, −0.001 to 0.001, 0.070 / 0.003 at 2k, PF 0.996 / 0.997): handbook/19 l148-155 and
  handbook/11 row 23; the cited coach_100.md / protocol_100.md gate tables were not opened.
- F8 caption (ch05 l10): says "pre-protocol rows from Table~\ref{tab:T21}", but F8_data.csv rows 0 to 4 (P1, P7/P8, P9/P10, P14,
  7 to 12 Oct) come from handbook/11 l515-520, not from T21 (T21 has no P1, P7, P8 row). Minor attribution, not a number; not changed.

## 4. CROSS-CHAPTER

1. **Release status (abstract l17-18, ch01 l89-90; also ch06 l206, ch12 l79).** Text says the benchmark "is released" / "are
   released". Records: T/log.md 22 Nov 15:25 "nothing pushed, repo not created" and 15:40 "gh status still invalid; nothing
   pushed"; PROTOCOL_v1.0.md l90 "Staged locally as commit 36fdcdc ... not yet public; URL to be added at publication"; no later
   log entry (log ends 23 Nov 22:07) records a push. ch06 carries \PENDING{release URL}. If the repository is not public at
   submission, all four places overclaim (category 5); I did not edit, to keep the chapters consistent with ch06's open marker.
   ch01 NOTES s4 already proposes "is prepared for release".
2. **ch07 l62 and l246**: "The decoder does not matter here: plain U-Net equals U-Net++ on every metric" and "decoder choice does
   not matter". The contrast is unet_r34_pf − PF −0.0016 [−0.0110, +0.0073] (T16a, 2-seed screen): n.d., worded as no effect
   (brief rule 3). l62 is labelled judgement, but "equals" / "does not matter" should read "is not separated".
3. Abstract and ch01 checked against ch06 to ch12 and the tables: E1 P +0.0430 [+0.0013, +0.1043], full +0.1464, half-cut +0.0110,
   C2 − C1-D4 +0.0451, C3 − C2 −0.0025, MDE 0.074, relP@2 0.5995 / relR@2 0.4157, CV5 0.9216 / 0.8211, 1,744 GFLOPs / 11.8×,
   0.174 s, T3b +0.2213 / +0.2530 / −0.0701 / +0.0171, EL-paper screens −0.0773 / −0.0932, D4 on PF +0.0134, release +0.045,
   57% / 71%, 0.244 [0.105, 0.436]: all agree with ch06 to ch12 and with T6 to T22. No inconsistency found.
4. The ch01 change ("5% and 10% labels") does not conflict with ch03 / ch05, which say "helped at 5% ... n.d. from 20% up" without
   "only".

## 5. Count

About 450 numbers checked in my seven files; about 300 against a primary record (verdict / read / errata / T3b verdict / run.log,
INFERENCE_COST, dataset_audit REPORT and rater RESULT, SPLIT_INTEGRITY, C3_LEAK_READ, PROTOCOL v0.2 / v1.0, final_tta_read
read.txt, benchmark_el_report, results/p11 README, RW_SOURCES / papers), about 150 only against NOTES, THESIS_TABLES / SOURCES
or the handbook (mostly ch05 T21 values and ch02 label-statistics from handbook 02).
