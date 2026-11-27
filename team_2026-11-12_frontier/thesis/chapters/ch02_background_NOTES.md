# Notes for ch02_background.tex (Chapter 2, Background)

Writer: chapter writer C, 23 Nov 2026. Brief: scratchpad chapter_brief.md (e5ac12d8). Plan: OUTLINE.md (5c97648b) section 2, Chapter 2.
Files written for this chapter: `chapters/ch02_background.tex`, `chapters/ch02_background.bib`, this file.
Nothing sealed was read: no E1 or test50 label, mask, image, dump or prediction. Only text result files, docs, tables, the
official class list CSV and papers.

## 0. Sources and pins (md5, first 8 characters, read 23 Nov 2026)
Short names used below (paths relative to `~/mtp/research/` unless absolute):
- BR = `team_2026-11-12_frontier/BRIEF.md` (bc06edd2)
- H02 = `handbook/02_domain_primer_EL_and_defects.md` (6b92042c); its measured facts come from `data_analysis/benchmark_el_report.md` on the OLD (release 20211104) masks, as H02 l154 says
- H04 = `handbook/04_glossary_and_naming.md` (f1ed6b44)
- H22 = `handbook/22_thermal_desk_study.md` (d7b88c3e)
- AUD = `team_2026-11-12_frontier/dataset_audit/REPORT.md` (9d7e0d27); pool P532, label set v1.1
- P10 = `team_2026-11-12_frontier/benchmark/PROTOCOL_v1.0.md` (eeb3379a); P02 = `.../PROTOCOL_v0.2.md` (b8b7f66a)
- EV = `team_2026-10-27_unlabelled/eval.md` (47ed758e)
- SEV = `team_2026-11-12_frontier/results/severity/SEVERITY_SUMMARY.md` (57e2bb4c)
- TT = `team_2026-11-12_frontier/thesis/THESIS_TABLES.md` (81c54378); tables referenced by label in `thesis_tables.tex` (d92b3f0b)
- CSV = `/home/yugma/mtp/datasets/BenchmarkELimages/dataset_20211104/ListOfClassesAndColorCodes_20211104.csv` (4b016c66)
- PR23 = `/home/yugma/papers/2023-Pratt-A-benchmark-dataset-for-defect-detection-aa662c.md` (2b145886)
- HA18 = `literature/pdfs_inst/haase2018_jpv_crackwidth/p.txt` (220a5667)
- PR25 = `literature/pdfs_inst/pratt2025_ictas_powerloss/p.txt` (b0dbb119)
- CH22 = `literature/pdfs_inst/chen2022_pvsc_crack_inactive/p.txt` (a073e0ba)
- DH21 = `/home/yugma/papers/2021-Dhimish-An-empirical-investigation-on-the-correlation-b8e3d4.md` (1c2000d9)
- CR = Crossref records fetched 23 Nov 2026 into the session scratchpad (`bibcheck/out/doi_*`; temporary): abstracts of Fuyuki 2005, Potthoff 2010, Hoffmann 2021

## 1. Every number in the chapter, with its source

| Section | Number(s) as written | Source (file:line or table cell) | Note |
|---|---|---|---|
| 2.1 | near 1100 nm | PR23 l25 ("photon emissions near 1100 nm") | |
| 2.1 | 5400 Pa test of IEC 61215; crack 3.4 um wide | HA18 l30 to l31 (abstract) | |
| 2.1 | a whole cell spans about 250 px | AUD l52 (centre cell median 249 to 250 px wide, ARTS / CFVS / CSIR) | rounded wording "about 250" |
| 2.2 | 582 cells, 478 / 54 / 50, 24 classes | BR l20; TT T1 row 1 | |
| 2.2 | more than 80,000 images of five sources | PR23 l33 ("80,000 + images ... five data sources") | |
| 2.2 | 512 x 512 px | PR23 l31; H02 l84 | |
| 2.2 | centre cell 25 to 30% of non-padding px; about 75% padding for single cells | AUD l52 to l53 | |
| 2.2 | window of about 3 x 3 cells | AUD l51 (F3 heading); TT T19a F3 row | |
| Table 2.1 | 24 classes, ids 0 to 23, names, feature / defect | CSV (all 25 lines); PR23 l33, l77 (12 features, 12 defects) | names copied from CSV "Desc" column; "bckgnd" written as "background" |
| 2.2 | background + padding 86.5% of train px (release masks) | H02 l141 | |
| 2.2 | four classes under 1,300 px in all 478 train images | H02 l144 | |
| 2.2 | 7 classes absent from val, 8 from test | H02 l145 | |
| 2.2 | crack 0.19% of train px, 209 of 478 train cells; inactive 42 of them | BR l22 | label set: BR l21 "Revised" masks = v1 (TT T3b: crack cells 209 to 206 from v1 to v1.1), so the text says "label set v1" |
| 2.2 | ARTS 195, CFVS 187, CSIR 122, BMRK 60, SDLE 18 | BR l23 | per-split counts in H02 l272 to l276 sum to the same |
| 2.2 | rotated 90 degrees, 300 to 256 px; 4 of 4 checked, NCC 1.000 | H02 l88, l90 | |
| 2.2 | CSIR median intensity sd 24 vs 34 to 48 | H02 l274 | |
| 2.2 | 10 of 24 classes in one source only (pool) | AUD l111; TT T19a F7 row | |
| 2.2 | source classifier balanced accuracy 0.94, chance 0.20 | AUD l119; TT T19a F8 row | |
| 2.3 | 9,302 skeleton points; FWHM median 4.0 px (IQR 3.0 to 4.75); label median 1.75 px (IQR 1.25 to 2.5); 77% | H02 l161 to l163 | release masks (H02 l154) |
| 2.3 | 61,176 points; 48% within +-1 px, 64% within +-2 px; null 11%, 21%; ARTS 75%, BMRK 38% | H02 l187, l192, l193, l198 | |
| 2.3 | label width ARTS 1.5, CFVS / CSIR 1.75, BMRK 3.0, SDLE 3.25 px | BR l34; H02 l172 to l176 | release masks |
| 2.3 | pool v1.1 width ARTS 1.59 to BMRK 3.09 px per centreline px; 29.6% of variance | AUD l107; TT T19a F7 row | |
| 2.3 | legacy test masks: 1 px shift 0.559 (4 directions), diagonal 0.434, 2 px 0.336 | H02 l217, l218, l221 | release masks, test split; label geometry only (no model) |
| 2.3 | pool v1.1, 229 crack cells: 1 px 0.483, 2 px 0.249, centreline 0.465, 3 px 0.605; relF1@2 1.0 each | AUD l26 to l27 | |
| 2.3 | two duplicate pairs: crack IoU 0.257, 0.210; tolerance F1 0.82, 0.99 | H02 l205 to l206; BR l35 | "two pairs only" stated in text |
| 2.3 | one double annotation (pool, v1.1): strict 0.259, relF1@2 0.829 | AUD l39 to l40; TT T19a F2 row | G-W10 wording kept ("one double annotation") |
| 2.3 | components under 20 px: 76% train, 59% val, 88% test | H02 l164; BR l38 ("76 to 88%") | |
| 2.3 | 7.2% of components less than 2% darker; 16% for CSIR | H02 l201 | |
| 2.3 | 49 clean legacy test cells; 70% of IoU loss = 0.358 of 0.508; 18% missed; 11% spurious | EV l73 (clean cells), l87 | best pre-protocol model = Track M "FINAL" ensemble (EV l10); test50 scope phrase added (OUTLINE rule 4) |
| 2.3 | pool: strict crack IoU 0.233 / 0.365 / 0.414; relF1@2 0.824 to 0.849 | AUD l24 to l25; TT T19a F1 row | PF's out-of-fold pool predictions (AUD l24), not the test50 model of the sentence before; wording fixed 23 Nov |
| 2.4 | 99%; 440 of 445, 18 of 18, 51 of 52; within 3 px | H02 l242 | release masks |
| 2.4 | 20% of train crack px in or at inactive | H02 l243; BR l37 | |
| 2.4 | inactive 1 px shift IoU 0.943 (legacy test masks) | H02 l217 (inactive column), l246 | |
| 2.4 | duplicate pairs inactive IoU 0.64, tolerance F1 0.92 at 2 px | H02 l247 | |
| 2.4 | inactive in 42 / 6 / 16 cells of 478 / 54 / 50 | TT T3b row "Inactive cells" (TT l136) | |
| 2.4 | three test cells hold 59% of inactive px | BR l24 | label statistic of test50 (no model result) |
| 2.5 | 13 classes of mIoU-R13 (list) | P10 l129 | |
| 2.5 | classes with ground truth in at least 3 test cells | BR l52 | |
| 2.5 | relP@r, relR@r definitions; distance transform per image; pooled | P10 l141 | |
| 2.5 | relF1@r = 2PR / (P + R) | H04 l222 | |
| 2.5 | 2 px = 95th percentile of the distance between two drawings | P02 l82 (6 pairs and the one double annotation) | |
| 2.6 | 12 cells; 25 C to 100 C | DH21 l9 (abstract) | |

No number was computed for this chapter. Rounded wording: "about 250 px" (from 249 to 250), "about half" (0.483 of a perfect 1.0
for a 1 px shift; H02 l223 uses the same phrase).

## 2. Judgement sentences kept (worded as judgement or as a reading of a cited source)
1. 2.1: "The width of a crack label is a drawing convention, not a measurement." Basis: HA18 3.4 um against a ~250 px cell; label widths differ by source (BR l34). H02 l78 says the same ("a labelling convention, not a physical measurement").
2. 2.2: "so a model can recognise the source, and with it the labelling convention, without looking at the defect." AUD F8 (l119) says "shows a shortcut is available, not that a model uses it"; the sentence says "can", not "does".
3. 2.3: "A label that is correct to within one pixel thus loses about half of its strict IoU." (H02 l223 wording.)
4. 2.3: "We read this as follows: strict crack IoU mixes detection with the line-width convention of the annotators, and a distance-tolerant metric separates the two better." Basis AUD F1 implication (l35 to l36).
5. 2.4: "Of all classes, it is the most directly tied to the electrical consequence of a defect." (H02 l238, general background.)
6. 2.4: "In our reading, crack is limited by label noise and inactive by the number of examples" (BR l64 to l65; H02 l255).
7. 2.6: "We read the cited work as saying that, for severity, the inactive map and whether a crack closes off an area matter more than the exact pixels of a crack line." (H02 l294 draws the same consequence.)
8. 2.6: "Thermal imaging sees the electrical consequence rather than the crack line." Basis DH21 abstract; H22 l79 (tagged S there).

Avoided on purpose: OUTLINE A13 ("strict IoU near 0.5 is the labelling ceiling", BR l36); G-W10 (models "at the agreement
level of two drawings"); A11 (no watt figure or power band).

## 3. Placeholders
- `\CITE{...}`: 1. (a) 2.1 "review or textbook on crystalline silicon cell and module construction" (fingers, busbars, ribbons). No on-disk source with a DOI states this anatomy; HA18 names cell interconnect ribbons only.
- `\FIG{...}`: 2. F1 (one pool cell per source with v1.1 overlay; OUTLINE section 4 F1) and F2 (crack label geometry; OUTLINE F2, data `dataset_audit/out/labels_audit.txt` section f1). The text refers to "Figure F2" by name, because `\FIG` takes no label; the lead should add `\label` when the figures are made.
- `\PENDING{...}`: 0.

## 4. Citations used and how each was verified
Keys in `ch02_background.bib` (all fields copied from the Crossref record of the DOI, 23 Nov 2026):
| Key | Claim it supports | What was read | DOI found where |
|---|---|---|---|
| fuyuki2005el | EL intensity follows minority carrier diffusion length; dark = low emission / deteriorated area | abstract (CR) | reference lists on disk: PR25 l320 area and `literature/pdfs_inst/otamendi2021_solener/p.txt` |
| potthoff2010voltage | highest EL signal of each cell proportional to its operating voltage | abstract (CR) | reference list of `/home/yugma/papers/2023-Colvin-...-4453f6.md` (ref. [22]) |
| kontges2011risk | crack modes A / B / C and power loss | NOT read (no abstract in Crossref, no full text on disk); claim taken from PR25 l155 to l160, which cites the 2010 EU PVSEC version (no DOI) | reference list of `otamendi2021_solener/p.txt` l830 to l832 |
| haase2018crackwidth | 3.4 um crack width; separated part without ribbon connection gives no power | full text on disk, abstract and introduction (HA18 l28 to l32) | Crossref title search (no DOI printed in the file); title, journal, volume 8, issue 6 and first page 1510 match the file |
| dhimish2021hotspots | no hotspot for crack-free / micro-cracked cells; hotspots likely for shaded / broken-down areas; 25 to 100 C | full text on disk (DH21 l9, l187) | printed in DH21 |
Keys from `ch03_related.bib` cited here: pratt2023benchmark (PR23 l5, l9, l25, l27, l31, l33, l77), deitsch2019elpv (BMRK = ELPV, H02 l88),
pratt2025ictas (PR25 l97 to l101 dark regions and power loss; l155 to l160 modes), hoffmann2021power (CR abstract: "we focus on
inactive regions and cracks as the predominant type of defect"), chen2022pvsc (CH22 l20: "predicting the worst-case degradation
area with cracks detected").

## 5. Cross-references assumed
`ch:data`, `ch:related`, `ch:protocol`, `ch:methods`, `ch:deployment` (labels found in the other chapter files on 23 Nov 09:03);
`ch:intro` (ch01 not written yet; label assumed from main.tex's file name `ch01_intro`). Tables: `tab:T3b`, `tab:T18`, `tab:T19a`
(thesis_tables.tex). New labels defined here: `ch:background`, `sec:bg_el`, `sec:bg_classes`, `sec:bg_crack`, `sec:bg_inactive`,
`sec:bg_metrics`, `sec:bg_severity`, `tab:bg_classes`.

## 6. Rules applied
- OUTLINE rule 4 (test50 scope): the one model result on test50 cells (EV l87) carries "in-distribution, known leakage, context only".
  Label statistics of the legacy test masks (shift IoU, component sizes, inactive pixel share) are label geometry, not results,
  and carry the set name instead.
- OUTLINE section 2, 2.3 "name the set with each number": every crack-label number names release masks / legacy test masks / pool v1.1.
- R4 (user ruling 22 Nov, image window): 2.2 says a "cell" means the image window.
- No em or en dashes in the .tex (checked by grep). The .bib uses `--` in page ranges, as `refs_extra.bib` does.

## 7. Word count
About 2,630 words of prose (LaTeX stripped), one small table, two figure placeholders: about 6.5 pages, a little over the
6-page budget. Further cuts, if needed: the dashed-label sentence in 2.3 and the thermal paragraph of 2.6.
