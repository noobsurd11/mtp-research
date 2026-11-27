# Notes for ch03_related.tex (Chapter 3, Related work and why published numbers do not compare)

Writer: chapter writer C, 23 Nov 2026. Brief: scratchpad chapter_brief.md (e5ac12d8). Plan: OUTLINE.md (5c97648b) section 2, Chapter 3.
Files written for this chapter: `chapters/ch03_related.tex`, `chapters/ch03_related.bib`, this file.
Nothing sealed was read. The related-work tables are NOT rebuilt: the chapter references `tab:rw_main`, `tab:rw_abs`, `tab:rw_out`,
`tab:rw_counts` in `related_work.tex` (3425f25f, appendix `app:related` in main.tex) and `tab:T2`, `tab:T3c`, `tab:T13a` to
`tab:T13c`, `tab:T16a`, `tab:T21` and the method tables in `thesis_tables.tex` (d92b3f0b). Two new tables are defined here:
`tab:rw_datasets` (public datasets) and `tab:rw_arms` (origin of each arm); neither copies a TT table.

## 0. Sources and pins (md5, first 8 characters, read 23 Nov 2026)
- RW = `thesis/RELATED_WORK.md` (f2a6adcd); RWT = `thesis/related_work.tex` (3425f25f); RWS = `thesis/RW_SOURCES.tsv` (ff466591)
- TT = `thesis/THESIS_TABLES.md` (81c54378)
- BR = `BRIEF.md` (bc06edd2); P02 = `benchmark/PROTOCOL_v0.2.md` (b8b7f66a); P10 = `benchmark/PROTOCOL_v1.0.md` (eeb3379a)
- PB = `harness/final/PUBLIC_BENCH.md` (136e27cb); V8 = `results/final_opening_read/verdict.txt` (bbb5f3b4)
- ML = `cards/ledger/MASTER.tsv` (e8aeeaa7); AUD = `dataset_audit/REPORT.md` (9d7e0d27)
- H02 = `~/mtp/research/handbook/02_domain_primer_EL_and_defects.md` (6b92042c); H17 = `.../17_escdd_dataset_audit.md` (e8b26c65)
- SYN = `~/mtp/research/team_2026-10-27_unlabelled/SYNTHESIS.md` (dd031cc1)
- PR23 = `/home/yugma/papers/2023-Pratt-A-benchmark-dataset-for-defect-detection-aa662c.md` (2b145886)
- UM2 = `/home/yugma/papers/2025-Yang-UniMatch-V2-Pushing-the-Limit-of-cd81b3.md` (13a6298e)
(paths relative to `T/` unless absolute or `~`)

## 1. Every number in the chapter, with its source

| Section | Number(s) as written | Source (file:line or table cell) |
|---|---|---|
| 3.1 table | BenchmarkEL 20211104: 582 cells, 478 / 54 / 50, 24 classes | BR l20; TT T1 |
| 3.1 table | 8 test cells same physical cell as a pool cell | TT T2 row "test50 against the pool" (TT l108); errata item 3 wording |
| 3.1 table | 20220723 / 20221008: 28 and 29 classes; 642 and 695 cells | H17 l45 to l46; RW R05 (l21: 15 defect + 13 feature), R04 (29 classes); P02 l22 (582, 642, 695) |
| 3.1 table | 20221008 corrects crack labels (dotted joined, widened) | H17 l31, l46 |
| 3.1 table | 186 of the 582 cells change split | P02 l22; P10 l34 |
| 3.1 table, text | later test sets 66 and 72 cells, each 51 of our pool cells; 38 of the 50 test cells | RW l47 (PB section 3) |
| 3.1 table | E-SCDD: crack and inactive px of 20221008 unchanged; one class added; 117 real + 93 synthetic; 903 files = 693 + 117 + 93 | H17 l32 to l37, l47, l240 |
| 3.1 table | E-SCDD: 44 of 82 test cells from modules with train cells | H17 l158 |
| 3.1 table | UCF-EL public release 9,562 / 2,289; paper data 17,064 incl. 256 simulated; twins 25 to 44% | BR l28; RW R07 (l25) |
| 3.1 table | PV-Vision 1,837 cells from 29,664 cells of 445 module images; random split | RW R12 (l33) |
| 3.1 table | MultiSolSegment 585 mono-Si images; augmented before random split | RW R15 (l36) |
| 3.1 table | PVEL-S 1,200 poly-Si cells from PVEL-AD; 840 / 360; evaluated on validation set | RW R16 (l37) |
| 3.1 table | ELPV 2,624 cells; contains BMRK | BR l29; RW l66 |
| 3.1 table | PVEL-AD 36,543 NIR cells, boxes, by request | BR l29; RW l68 |
| 3.1 table | UCF-EL "one pre-protocol pretraining test" | TT T21 row P15 (TT l698) |
| 3.1 text | UCF-EL crack mask shifted 1 px keeps IoU 0.954; BenchmarkEL legacy test 0.559 | H02 l312 (and l217) |
| 3.1 text | E1: 106 cells | TT T1 (TT l88) |
| 3.2 | 22 full-text papers; 7 abstract-level; 2018 to 2026 | RW l9 |
| 3.2 | counting rule (paper counts once; problem counts if any row has it) | RW l131 |
| 3.2 bullets | 0 of 22 module- or panel-disjoint | RW l92 |
| 3.2 bullets | 4 split not stated; 1 conflicting | RW l90, l91 |
| 3.2 bullets | 7 of 22 overlap or test selects model; 14 not checkable | RW l95, l96 |
| 3.2 bullets | 18 of 22 no interval, seed count or repeat; other 4 side quantity only; none on headline | RW l88, l89, l106 |
| 3.2 bullets | 15 of 22 metric undefined or inconsistent; 10 of 22 background in the mean | RW l97, l98 |
| 3.2 bullets | 7 of 22 release not stated or not public data | RW l93 |
| 3.2 bullets | 0 of 22 distance-tolerant; 0 of 22 unseen modules; 2 of 22 release, split and metric | RW l99, l100, l101 |
| 3.2 | three papers on test50; Torpey 20220723; Mazen, Ramadan, Hanifi 20221008; cross-test-set ranking | RW l104; RW R06a (l22: PV-S3 Table 6 against Pratt's medians) |
| 3.2 | quote "fifty images with a prevalence of cracks, gridline defects, and inactive areas" | PR23 l39 |
| 3.2 | 8 same physical cell (7 by pixels, 1 by link), 7 neighbouring crops, 19 same module | TT T2 l108; errata item 3 (via TT T13a notes) |
| 3.2 | 1,769 of 2,289 UCF-EL test images in PV-S3 train lists | RW R06c (l24); RW l105 |
| 3.2 | Fioresi validates on test each epoch; Duan evaluates on validation; MultiSolSegment and Saleh augment before split | RW R07 (l25), R16 (l37), R15 (l36), R18 (l39); RW l105 |
| 3.2 | rule A 0.405, rule B 0.202, rule C 0.541 (C1, mean over seeds, v0 labels, 50 cells) | TT T13b l432, l435, l436 (= V8 l100, l103, l104) |
| 3.2 | SEiPV-style per-image absent = 1 0.855; absent skipped 0.545; micro IoU 0.891 | TT T13b l447, l448, l444 |
| 3.2 | rule definitions A / B / C | H04 `handbook/04_glossary_and_naming.md` l24; PB l61 |
| 3.2 | crack 0.25 (Pratt) and 0.58 (PV-S3) | TT T13a l412, l415; RW l107 |
| 3.2 | SEiPV "IoU" 0.7447 = Dice 0.8531 / (2 - Dice) within 0.001; "mIoU" 0.8604; Ramadan reprints as wIoU | PB l28 (note "0.8531 -> 0.7438"); TT T13a l414; RW R10a (l28) |
| 3.2 | STC-Net 95.98 (validation), 72.52 (360 test images) | RW R17 (l38) |
| 3.2 | PF strict 0.320 vs 0.365; relF1@2 0.822 vs 0.846; contrasts move at most 0.008 | TT T3c l148 |
| 3.2 | four published rows on test50; four further papers on other overlapping test sets | TT T13a l412 to l416; V8 l89 to l93 |
| 3.2 | the seven items (release, label set, split, class list, metric convention, operating-point rule, seed count) | P10 l41 (reading, S) |
| 3.3 | PF recipe: 20,000 steps, batch 8, 512 px, label set v1.1 | TT T15 caption (TT l506) |
| 3.3 table | PF: encoder frozen 1,000 steps, then ramped to 0.1 x lr over the next 1,000 steps, no encoder weight decay | H04 l410; method card house_r34_unetpp_pf_v11.yaml (training.encoder_pf: freeze 1000, ramp 1000, lr_mult 0.1, wd 0). BR l43 omits the ramp |
| 3.3 table | D4 = 8-view flip and rotation | TT section 0 conventions (TT l20 to l22) |
| 3.3 table | MiT-B2 | TT T15 row segformer_mitb2_pf |
| 3.3 text | UCF-EL model -0.0773 [-0.0892, -0.0594]; Pratt weighted CE -0.0932 [-0.1113, -0.0774]; Hanifi VGG-16 U-Net -0.0064 [-0.0189, +0.0042] | TT T16a l542, l543, l540 (= P10 l40) |
| 3.3 text | cv5v2 carried a module leak | TT T1 l86; T2 row 1 |
| 3.4 | "ten common benchmarks" | arXiv abstract of 2103.14749 ("10 of the most commonly-used ... datasets") |
| 3.5 | 11,938 unlabelled CSIR / ARTS cells; about 159k public pool | BR l27 |
| 3.5 | UniMatch V2 Pascal: labelled-only DINOv2-S 67.0 (1/16) and 83.7 (1/2); UniMatch V2 79.0 and 86.7 | UM2 l274 to l275 (Table 1) |
| 3.5 | Torpey: R7 and R8 run once; five runs per regime | RW R05 (l21) |
| 3.5 | 5% labels: inactive +0.117 [+0.042, +0.189]; relF1@2 +0.033 [+0.006, +0.055] | TT T21 row P13 (TT l693) |
| 3.5 | n.d. from 20% up | TT T21 row P16 (TT l699) |
| 3.5 | external pool at full labels n.d. | BR l75 |

No number was computed for this chapter. The arithmetic identity for SEiPV is quoted from PB l28, not recomputed for the text.

## 2. Judgement sentences kept
1. Chapter intro: "published EL segmentation numbers cannot be compared with each other or with ours: almost none states its split and metric together, and none gives an interval on its headline number." (RW l101, l106; RW reading 5, S.)
2. 3.1: "None of the pixel-labelled sets we could check comes with a module-disjoint split."
3. 3.2 paragraph heading "Convention moves the number as much as the method." (RW l107, reading 4, S.)
4. 3.2: "the two differ in model, metric and possibly split, so the gap cannot be assigned to any one of them."
5. 3.2: "In our judgement, a published EL number is comparable only if it states release, label set, split, class list, metric convention, operating-point rule and seed count together." (P10 l41, S.)
6. 3.3: "Under one protocol, the published EL models sit at or below our U-Net++ baseline." (P10 l40; 2-seed screens on cv5v2, said in the same paragraph.)
7. 3.3: "We tried them because the unseen-module problem of this thesis is a domain shift and the crack is a thin structure, not because they were shown to work on EL."
8. 3.4: "Each of these has an EL counterpart in our data ..."
9. 3.5: "Our own pre-protocol results agree with this shape"; "In our reading it did show that, with every label in use, the measurable problems of this work lay elsewhere: in the split, the metric and the unseen modules."
Wordings from OUTLINE section 3 applied: A1 (no claim to beat a published model; test50 rows context only), A9 (a past SSL null closes
only its run conditions; SSL helped at 5%), G-W3 (8 test cells, 7 by pixels, 1 by link), G-W7 ("unseen modules: supported, not
proven" at the one mention of E1), OUTLINE rule 4 (both test50 passages carry "in-distribution, known leakage, context only").
Deliberately NOT written: that our models score higher than Pratt 2023 on test50 (T13a's own reading says so for Pratt only; PV-S3's
printed crack IoU 0.58 is above our PV-S3-style 0.418, so a general "higher" would be false, and A1 forbids the comparison anyway).

## 3. Placeholders
- `\CITE{...}`: 3, all in Table `tab:rw_arms`: "ResNet, He et al. 2016"; "segmentation_models_pytorch library"; "U-Net, Ronneberger et al. 2015". No id is recorded on disk for any of the three (OUTLINE O5; refs_extra.bib covers HRNet, U-Net++, Skeleton Recall, DeepLabV3+ only).
- `\FIG{...}`: 0 (OUTLINE section 4 assigns no figure to Chapter 3).
- `\PENDING{...}`: 0.

## 4. Bibliography (`ch03_related.bib`): what was verified and what differs from RW
- Scope: entries only for papers whose DOI or arXiv id is recorded on disk: RW (rows R01 to R21, A1 to A7, section 3), ML
  (method papers: P012, P017, P018, P036, P039, P049, P260; MASTER.tsv lines 13, 18, 19, 37, 40, 50, 261), AUD l14 to l19
  (label-noise papers, "Research MCP ids"), SYN l11 and ML P086 (UniMatch V2). Strictly, the lead's instruction names RW_SOURCES.tsv
  and RELATED_WORK.md only; the ML and AUD ids are included because OUTLINE section 2 (Ch 3, rows 3.3 and 3.4) lists them as the
  verified ids for these sections. Drop them (and use `\CITE`) if a strict reading is wanted: 15 keys (7 ML, 7 AUD, 1 SYN).
- Every field was copied from the Crossref record of the DOI or the arXiv API record (fetched 23 Nov 2026); no field is from memory.
- Differences from RW (Crossref used): Mazen 2024 pages 100792 to 100804 (RW: "100793ff"); Mahboob SegFormer (A1) issue year 2025
  (RW: 2024); RERN (A6) issue year 2024 (RW: 2023); "PV-ReAD" (A4) Crossref title "A novel reconstruction-based method for
  unsupervised photovoltaic cell defect detection using electroluminescence images", Solar Energy 321 (2027 issue); Hanifi IEA/AIE
  chapter issued 2025 (volume printed 2026; LNCS volume number not in Crossref).
- RW reading 4 (RW l107) attaches the Dice identity to SEiPV's "mIoU" 0.8604; PB l28 shows it holds for "IoU" 0.7447 and Dice
  0.8531. The chapter follows PB.
- Keys defined here and also cited by Chapter 2: pratt2023benchmark, deitsch2019elpv, pratt2025ictas, hoffmann2021power, chen2022pvsc.

## 5. Cross-references assumed
`ch:background`, `ch:data`, `ch:protocol`, `ch:methods`, `ch:legacy` (labels found in the chapter files on 23 Nov 09:03);
`ch:intro` (assumed from the file name `ch01_intro` in main.tex); `app:related` (main.tex). New labels: `ch:related`,
`sec:rw_data`, `sec:rw_numbers`, `sec:rw_methods`, `sec:rw_noise`, `sec:rw_ssl`, `tab:rw_datasets`, `tab:rw_arms`.

## 6. Word count
About 2,100 words of prose (LaTeX stripped) plus two scriptsize tables (about 680 words): about 6 pages.
