# Benchmark protocol v1.0: defect segmentation in EL images of solar cells

protocol_v1 (writer, lead's team), 22 Nov 2026; state of the files at about 12:40 IST. Consolidates `v0.2` (15 Nov 16:00, left unchanged) with every ruling, read and audit recorded since. The thesis benchmark chapter is this file in prose, so it is meant to stand alone. Written from files only: no training, no GPU, nothing on cv02, no sealed label or prediction read (result files and verdicts only).
**Status.** v1.0, frozen 23 Nov 2026. Freeze edit (23 Nov) on eeb3379a, once the R6 conditions were met (section 11): T3b result in 8.3 (`T3V` bfe583db); GPU latency in 6.4 (`IC` 1e5a9002); `RW` pinned (f2a6adcd); review closed (`RVP` 797e63bb: round 2 FIX, its three edits made and closed by the lead's diff check as the reviewer allowed, `log` 22 Nov 12:39); user rulings R1 to R10 and the lead items (`log` 22 Nov 12:49); HOUSE rule read (`HCS` 9efd43ac); release staged as commit 36fdcdc. Still open, not an R6 condition: the E1 label builder for outside entries (12.3 item 7; section 13).
**Tags.** E = stated in a cited file. D = decision, with who and when (record = `log` entry time unless named). S = judgement of this writer. "derived" = computed here, formula given. Where two sources disagree, the result file wins and the line says so.
**Short paths** (relative to T = `/home/yugma/mtp/research/team_2026-11-12_frontier/`; md5 prefix as read on 22 Nov; `T3V`, `HCS`, `IC` and `RW` as read on 23 Nov):
`v0.2` benchmark/PROTOCOL_v0.2.md (b8b7f66a); `draft` benchmark/PROTOCOL_DRAFT.md (761fdd8d); `log` log.md (entry time given); `BRIEF` BRIEF.md;
`FOR` results/FINAL_OPENING_READ.md (16e3f1e7); `ERR` results/FINAL_OPENING_READ_ERRATA.md (af55915f, supersedes named lines of FOR); `TTA` results/FINAL_TTA_READ.md (b64f964e);
`HRN` results/C3HRNET_READ.md (450bf943); `HRNr` results/c3hrnet_read/read.txt (d22b9855); `SWD` results/C3SWAD_READ.md (c841f618); `C3X` results/C3X_READ.md (da841902); `C3Xr` results/c3x_read/read.txt (95a3a5ca); `LEAK` results/C3_LEAK_READ.md (43e8009e);
`R1` results/ROWS1_READ.md (07c93594); `R2` results/ROWS2_READ.md (3fef30d4); `W1C` results/W1C_READ.md (3a437100); `W2A` results/W2A_READ.md (90c781a8); `LACE` results/W2B_LACE_READ.md (91a8e726); `LCI` results/W2B_LCI_READ.md (957d174f);
`U1` results/U1_READ.md (289853e0); `U2U4` results/stageB/U2U4_READ.md (ab7e10cb); `B5` results/stageB/B5_msc_tta.md (876cf2df); `SPI` results/stageC/SPLIT_INTEGRITY.md (26b3c76a); `CV3` results/stageC/CV5V3_BUILD.md (3e0be996);
`FRULE` harness/final/FINAL_RULE.md (82867156); `ADD1` harness/final/FINAL_RULE_ADDENDUM_1.md (be50433b); `ORULE` harness/final/opening/OPENING_RULE.md (065a7ddd); `T3R` harness/t3b/T3B_RULE.md (0c006d44); `T3A` harness/t3b/AMENDMENT_1.md (937a6cbf); `PUB` harness/final/PUBLIC_BENCH.md (136e27cb); `RR2` harness/REVIEW_ROWS2.md (46cf7b7e); `RBF` harness/REVIEW_STAGEB_FIX.md (d086b13c); `W3` cards/WAVE3_REVIEW.md (e3f8efbd);
`AUD` dataset_audit/REPORT.md (9d7e0d27); `RAT` dataset_audit/rater/RESULT.md (c119a04f); `SEV` results/severity/SEVERITY_SUMMARY.md (57e2bb4c); `S0` results/severity/S0_DOWNLOADS.md (b3664c24);
`TL` benchmark/test_openings.md (2629ed93); `EL` /home/yugma/mtp/research/team_2026-10-31_next/e1_openings.md (52432548); `TT` thesis/THESIS_TABLES.md (707c7c46); `GAPS` thesis/GAPS.md (b4e5f655); `IC` thesis/INFERENCE_COST.md (1e5a9002; CPU and GPU parts); `HPF` results/HOUSEPF_READ.md (71e5a382); `HCS` results/HOUSECS_READ.md (9efd43ac); `T3V` results/t3b_open9_read/verdict.txt (bfe583db); `LIC` benchmark/release_v1/LICENCE_AUDIT.md (f267ea23); `REL` benchmark/release_v1/files/README.md (690dac25); `RVO` harness/REVIEW_OPENING.md (f81cb703); `RVP` harness/REVIEW_PROTOCOL_V1.md (round 1 7bfecedd; round 2 appended, 797e63bb); `LAB` benchmark/LABELS_V11.md; `RW` thesis/RELATED_WORK.md (f2a6adcd, written 22 Nov 11:56 by the related_work agent); `m0core` harness/el_bench_src/bench/m0core.py (d92aa38a, source snapshot); `IST` = INFO_SHEET_TEMPLATE.md (this folder).

## 0. The protocol in fifteen lines
1. **Data.** BenchmarkEL `dataset_20211104`: 582 cells = 478 train / 54 val / 50 test, 24 classes (E `BRIEF` s2). Label set v1.1; ignore px are not scored (E `v0.2` 2.2).
2. **Sets.** Development pool P532 = train + val. Sealed: legacy test50 and E1 (106 cells with no module link to the pool found; "unseen" is supported by pixels, not proven; E `SPI` 5a; `GAPS` G-W7). No development step reads a sealed label or prediction (D brief 1, via `v0.2` 3.3).
3. **Split of record.** cv5v3: 5 folds, 285 module groups, none spans folds; every pool cell scored once out of fold; the 532 cells and the 416 clean cells are read together and both decide (E `CV3`; D lead 16 Nov 00:39; E `FRULE` s3). cv5v2 holds the 2-seed screens only.
4. **Headline.** Crack relF1@2 decides every crack contrast; strict crack IoU is printed only with its convention band +-0.019 and decides nothing (D user 21 Nov 00:22; E `FRULE` s2).
5. **Guards** (which apply on which set: 5.2): width ratio pooled and per source (0.85 to 1.15), false crack px on crack-free cells (at most 1.5 x the reference), inactive IoU and mIoU-R13 (drop at most M) (E `FRULE` s2; `ORULE` s4).
6. **Operating points.** CV5: OP-A (argmax) and OP-W (width-matched) decide; OP-F printed only; OP-C is the comparator for prior-shifting arms. Sealed sets: OP-A only (E `v0.2` s11 item 8 for OP-C; `ORULE` s2 for sealed sets, a deviation from `v0.2` 5.4 per `RVO` N5).
7. **Statistics.** CV5: two-stage group bootstrap, M = max(0.01, 2 x SE of the PF A/A) per machine and cell set. Sealed sets: seed-aware two-stage bootstrap over clusters and models, M 0.010 fixed (E `v0.2` 5.4; `ORULE` s4).
8. **Verdict words.** CONFIRMED; GAIN, FAILING GUARDS NAMED; NOT CONFIRMED (NO LOSS or LOSS). A 2-seed screen PASS promotes to a 5-seed confirmation and is never a result (E `FRULE` s2; `v0.2` 5.4).
9. **Seeds.** Screen 2, table row and candidate 5 (seeds 5 to 9), with the L6 exception (D lead 15 Nov 16:01). Its application now needs a ruling (R1).
10. **Entries.** Four entry classes, two data tracks, a fairness record and an info sheet per entry, leakage guards (section 6; `IST`).
11. **Legacy test50.** Continuity and public table only: 19 counted openings, the last (#19) a public table that decides nothing; no further opening (E `TL` B; D user 21 Nov 00:22).
12. **E1.** Opening #8, the final evaluation: C2 - C1 crack relF1@2 +0.0430 [+0.0013, +0.1043], CONFIRMED (E `FOR`); scope (7.4): mean over seeds 5 to 9, carried by the 44 full cells (half-cut cells n.d.), 101 of 106 cells CSIR, OP-A only, MDE about 0.074 (derived). Opening #9 = T3b few-shot track, opened 23 Nov: P = ALL - ZS crack relF1@2 +0.2213 [+0.0977, +0.3504], CONFIRMED, guards G1 and G2 pass (E `T3V`; scope 8.3). From 22 Nov E1 is training data for T3b models; this team makes no later zero-shot claim on E1 (E `EL` #9).
13. **Suite.** A 5-seed tier on cv5v3 (PF, HOUSE, HRNet-W18, SWAD, HRNet + SWAD, D4 arms) and a 2-seed screen tier on cv5v2 (EL-paper rows, decoders, losses, samplers, averaging, layers). On CV5 only D4 TTA on PF is CONFIRMED; the final recipe C2 passes its CV5 check (selection-biased) and is CONFIRMED on E1 (section 7).
14. **Data faults** are part of the benchmark: line-width convention, labelling ceiling, window geometry, label errors, source conventions, a few groups carrying contrasts (E `AUD` F1 to F11; `RAT`).
15. **Release.** Lists and code only (D user 22 Nov 11:40), as a public repository: MIT for code, CC BY 4.0 for lists and results (D user 22 Nov 12:08); staged locally as commit 36fdcdc; URL to be added at publication. Pool-trained models, C2 included, are research-only as trained: the 50 BMRK cells are ELPV images under CC BY-NC-SA 4.0 (E `LIC` s2, s7 D4).

## 1. Why published EL segmentation numbers cannot be compared
- **The v0.1 audit stands** (E `v0.2` s1; `draft` s1): three releases of one dataset (582, 642, 695 cells) with reshuffled splits (186 of 582 cells change split); augmented and synthetic images in train folders; test cells that are the same physical cell as train cells; validation drawn from test; different class lists and metric conventions; strict IoU on 1 to 2 px labels; single runs without intervals.
- **New measurements since v0.2** (E `AUD`):
  - The label release moves levels more than any method: on P532, 20211104 against v1.1, PF strict crack IoU 0.320 vs 0.365, relF1@2 0.822 vs 0.846; the largest method gain when the audit ran (19 Nov; +0.015 relF1@2) is 0.6 of the relF1@2 shift (F6). Since 21 Nov the C2 recipe on CV5 (CS_D4 - PF) is +0.0222 (selection-biased; `TTA`), 0.89 of the shift (derived: 0.0222 / 0.025). The largest CV5 contrast printed against PF is CB_D4 - PF +0.0243 [+0.0160, +0.0338] (information only; final_tta_read/read.txt l481), 0.97 of the shift (derived).
  - Strict crack IoU measures the line-width convention: the same PF predictions score 0.233 (1-px centreline labels), 0.365 (v1.1), 0.414 (3-px labels); relF1@2 0.824 / 0.846 / 0.849 (F1).
  - Release splits leak: E-SCDD has 44 of 82 test cells sharing a module with train (F11, citing handbook 17). On test50, 8 cells are the same physical cell as a pool cell (7 confirmed by pixels, 1 `CFVS_00063_r3_c1` on the cells.tsv link only), 7 are neighbouring crops, 19 more share a module (E `SPI` 5b; wording `ERR` item 3).
  - The source is identifiable from global image statistics: balanced accuracy 0.94 against chance 0.20 (F8).
- **Under equal training on CV5 the EL papers' models sit below the baseline** (E `R1` s2, cv5v2, 2 seeds, relF1@2 at OP-A): UCF-EL's DeepLabV3 / ResNet-50 -0.0773 [-0.0892, -0.0594], Pratt's weighted CE -0.0932 [-0.1113, -0.0774]; Hanifi's VGG-16 U-Net not separated (-0.0064 [-0.0189, +0.0042]).
- **Reading** (S, unchanged from `v0.2` s1): a comparable number states release, label set, split, class list, metric convention, operating-point rule and seed count together. This protocol fixes all of them, and its checklist (section 12) makes an entry state them.
- **Published numbers on our image family** (E `PUB` s2; `FOR`): only the test50 rows of Pratt 2023, SEiPV-Net and PV-S3 can meet our models, on the old masks v0; they appear in the public table of opening #19 as context, never as a claim (section 7.4).
- **Related-work table** (E `RW` s1 to s4; D `v0.2` 6.6 item 4): 22 papers with pixel-level EL numbers read in full text (2018 to 2026) plus 7 abstract-level rows, each with release, split, classes, metric convention, number, interval and a comparability verdict. Over the 22 (E `RW` s4): no interval, seed count or repeat on any reported number in 18; a split stated to be module- or panel-disjoint in 0; test overlapping training, or the test set selecting the model, in 7; metric undefined or numbers inconsistent in 15; background inside the headline mean in 10; a distance-tolerant crack metric in 0; a number on unseen modules in 0; release, split and metric all stated in 2. Only three papers score on test50 (Pratt 2023, SEiPV-Net, PV-S3). Reading (S `RW` s4 item 5): no published row is comparable with relF1@2, OP-A or E1; three are "partly" comparable on test50 by re-scoring our models in their convention, as context only.

## 2. Corpus, labels, terms
### 2.1 What exists (E `v0.2` 2.1; `ORULE` s1; `FOR`)
816 real labelled cells in the three BenchmarkEL releases and E-SCDD, 787 unique physical cells, 463 module groups; the 93 synthetic E-SCDD files are excluded everywhere.

| Role | Cells | Use in v1.0 | Record |
|---|---|---|---|
| P532 = legacy train + val | 478 + 54; ARTS 182, BMRK 50, CFVS 169, CSIR 114, SDLE 17 | development, CV5, full-pool training of the final models | E `v0.2` 2.1; `FRULE` s1 |
| legacy test50 | 50 cells, 48 image ids | sealed; public table #19 only | E `ORULE` s1; `TL` |
| E1 (release `20221008` cells not in the 582 and not in the unlabelled pool) | 106 = CSIR 101 + BMRK 5; 71 image ids; 62 half-cut, 44 full; crack in 32 cells, inactive in 10; 74 crack-free | sealed; final evaluation #8; T3b #9 | E `ORULE` s1, s10; `FOR` G3 and strata |
| `_rf` cells (Hanifi labels) | 117 (F51, H36) | development reads only | E `v0.2` 2.1 |

### 2.2 Label sets
| Set | Definition | Used for | Record |
|---|---|---|---|
| v0 | BenchmarkEL 20211104 `labeled/masks_coded`, values 0 to 23, no ignore | test50 public table #19 only | E `ORULE` s3 |
| v1 | the E-SCDD mask (577 cells) with classes >= 24 set back to the `20211104` label, and the `20211104` mask for the 5 cells missing from E-SCDD (project name `masks_escdd`) | pre-protocol P-series; ablation arm PFV1 | E `LAB` s1; `TT` T3a |
| **v1.1** | v1 with every scuff and star px set to ignore (255); `BMRK_00031_cell0091` given back its 20220723 mask; masks_v11 MANIFEST 9c0e0687 | training and scoring of every CV5 read and of the full-pool models; test50 v1.1 rows | E `v0.2` 2.2; `ORULE` s3; D user 12 Nov 20:15 |
| E1 set | `ext117/masks` (release 20221008): class 24 to 2, classes 25 to 28 (scuff, corrosion cell, brightening, star) to ignore, with `ext117/ignore` | scoring E1 openings #1 to #9 | E `ORULE` s3 |
| E1 training map (T3b only) | 0 to 23 kept; 24 to 2; 29 to 1; 25 to 28 to 255; every px with ignore > 0 to 255; equals the scoring GT on every kept px | training of T3b models only | E `T3R` s6 |

- v1.1 against v1: train 16 cells and 3,484 px to ignore, test 2 cells and 236 px; training on v1 instead of v1.1 changes no pooled metric measurably (PFV1 - PF relF1@2 -0.0014 [-0.0099, +0.0064], 2 seeds) (E `v0.2` 2.2; `TT` T3c).
- **Label variants for robustness checks** (E `AUD` F1, s2): the same predictions re-scored on the old release (20211104), the 1-px centreline of v1.1, a 3-px redraw, and v1.1 with the audit's candidate px ignored. Under every variant, relF1@2 contrasts move by at most 0.0031; strict-IoU contrasts move by up to 0.019 (the convention band, section 5.1).
- Label issues 3 to 8 of `draft` 2.5 (mask copies, the one double annotation, `_rf` crack labels with speck-level H36 cracks, the E1 label convention, noisy images, dotted labels) are unchanged (E `v0.2` 2.2). The audit covers the double annotation, noisy images and copies (F2, F10, F11), not the `_rf` or dotted-label issues.
- **E1 labels are wider:** about 1.5 x the pool labels, so a model trained on E1 learns the wider width; this is why T3b prints width and does not guard it (E `T3R` s8, citing the T3b proposal s5).

### 2.3 Label quality: the dataset-fault audit (E `AUD`; `RAT`; numbers on P532, v1.1, 25 out-of-fold cv5v3 models)
| Fault | Key numbers | Status (source wording) |
|---|---|---|
| F1 strict IoU measures the line-width convention | PF strict crack IoU 0.233 / 0.365 / 0.414 (centreline / v1.1 / 3 px); a label shifted 1 px against itself: IoU 0.483 | solid |
| F2 labelling ceiling | the one double annotation: mask against mask strict crack IoU 0.259, relF1@2 0.829; PF 0.365 / 0.846; 25-model vote 0.398 / 0.868 | suggestive (one double annotation) |
| F3 images are windows of about 3 x 3 cells | 57% of crack px and 71% of inactive px lie outside the centre cell; 117 of 229 "crack cells" have no crack px in their centre cell | solid |
| F4 inactive labels | spurious-inactive candidates 31,039 px = 10.9% of inactive px; inactive px in 33 of 285 groups, Kish n_eff 12.9; raters: spurious inactive 30 of 40 model error, so the label is mostly right there (`RAT`; `log` 21 Nov 05:21) | measured with AI raters |
| F5 crack label errors | missed 1.8% of crack px, spurious 2.5%; ignoring all candidates moves no contrast by more than 0.003; rater share of label errors among image-supported candidates 0.244 [0.105, 0.436] (corrected) | measured: exist, a minority |
| F7 per-source conventions | crack label width ARTS 1.59, CFVS 2.06, CSIR 2.25, BMRK 3.09 px per centreline px; 10 of 24 classes occur in one source only | solid |
| F9 few groups carry the contrasts | crack px in 125 of 285 groups, Kish n_eff 24.1; HRNET - PF falls under M after removing 1 group (`CFVS_00139`); HOUSE - PF reaches 0 after 4 | solid; greedy removal is a worst case |
| F10, F11 | 2 pool images with noise sigma > 10; 41 look-alike cross-group pairs, no new leak | solid |

- Implications adopted as protocol text (from `AUD` s2; D lead, `log` 22 Nov 12:49; section 11): relF1@2 decides (F1, F5, F6); absolute levels from this dataset are not compared with another dataset or release (F6); an entry reports which module groups carry its gain (F9; checklist item 9); a cell-level quantity describes a window (F3; ruling R4).
- The AI raters are three runs of one model; calibration: each rater sensitivity 29/30, specificity 30/30 on 60 planted items (E `TT` T19a; `RAT`). They measure consistency, not independent human reliability.

### 2.4 Terms of use and release
- E `v0.2` 2.3; `LIC` s2: BenchmarkEL has no licence file (GitHub API `license: null`; its README asks for a citation); E-SCDD is MIT on Hugging Face and re-hosts BenchmarkEL images (its MIT claim cannot clear the BenchmarkEL part, S `LIC` s2); UCF-EL has no licence file; smp-hub ImageNet weights (ResNet, VGG) carry the tag "other" with no licence text.
- Verified 22 Nov (E `LIC` s2): ELPV, the source of the 50 pool and 5 E1 BMRK cells: images CC BY-NC-SA 4.0, commercial use forbidden without the holder's permission; SDLE (CWRU set): CC BY 4.0; HRNet-W18 ImageNet weights (timm, file md5 e6bb005d): MIT (`RR2` l12, l85); SegFormer MiT-B2 weights: NVIDIA SegFormer licence, non-commercial, so research-only weights and a benchmark row only (`RR2` l11, l15, l92; HF field "other", l90).
- **Fact for the tracks** (E `LIC` s7 D4): every pool-trained row, C1 and C2 included, trains on the 50 BMRK (ELPV) cells, and BenchmarkEL states no licence. C2 is research-only as trained.
- Severity sets, analysis only: Polenghi CC BY 4.0; ELPVPower CC BY, version unverified; both downloads approved by the user 15 Nov (E `S0` l3, l14).
- **Release** (D user 22 Nov 11:40 and 12:08): lists and code only, as a public repository, MIT for code and CC BY 4.0 for lists and results; README `REL`. No image, mask, weight, or label or per-cell result of test50 or E1 is shipped (E `REL` s2; `LIC` s5). Staged locally as commit 36fdcdc (65 files, no remote; E `log` 22 Nov 12:08, 15:25); not yet public; URL to be added at publication. Email to Pratt not sent (E `log` 22 Nov 12:08).
- **Ruled** (D user 22 Nov 12:49; section 11): "clear terms" for the main track, R2 (a); the release decisions of `LIC` s7, R8.

## 3. Sets and split
### 3.1 cv5v3, the split of record
- Files: `benchmark/splits/cv5v3.json` (7a700b00), `cv5v3_groups.tsv` (d880a769); roots `/home/noob/work/bench_data_v3b`; every cv5v3 read passes `--groups .../bench_data_v3b/meta/cv5v3_groups.tsv` (E `v0.2` s11 item 11; `CV3` s13).
- Groups: cv5v2 groups, the physical modules of the identity audit, the four open image-id pairs, the earlier links, and the SDLE modules named in the stems (A1, A10, A11): 285 groups, none spans folds; the lead's recount found 0 of 304 physical modules spanning folds (E `log` 16 Nov 01:04).
- Folds: held-out sizes 107 / 110 / 103 / 101 / 111; 47 cells moved from cv5v2; crack-cell spread 4 (cv5v2: 9), inactive 7 (8); costs accepted: SDLE cells are held out in folds 0, 2 and 4 only (D lead 16 Nov 00:39).
- Module identity: 700 image ids = 561 physical modules under rule B (a rule chosen after the full run, stated as post hoc; the pre-set rule gives 527); BMRK and SDLE are not decidable from pixels (E `SPI` s3c, s11). BMRK (50 pool cells) stays grouped by image id: a stated limit (D lead 16 Nov 00:39).
- **Clean cells:** `benchmark/splits/score_exclude_v3.txt` (6d48dfbd): 116 cells excluded, 416 left: the 91 cells held out in cv5v2 while a cell of their module trained, the 8 cells of the 4 open image-id pairs, and the 17 SDLE cells; none of the 416 changes fold between cv5v2 and cv5v3 (E `v0.2` s11 items 10, 11; `log` 16 Nov 00:39, 01:04). Every read prints 532 and 416; both decide (E `FRULE` s3).
- The pool has 0 half-cut cells, so CV5 cannot measure unseen layouts (E `TT` T1).

### 3.2 cv5v2 (screens only) and the leak it carried
- `cv5v2.json` (441d118f), 330 groups (E `v0.2` 3.1). The module audit found 24 physical modules spanning two folds; 91 pool cells (ARTS 48, CFVS 32, CSIR 11; 22.7% of crack px) were held out while a cell of their module trained (E `SPI` s4, s11).
- **Leakage read** (pre-registered 16 Nov, run 17 Nov; E `LEAK`): difference in differences cv5v3 - cv5v2 on the affected, unmoved cells (69) against the clean cells; PF 5 seeds: strict crack IoU -0.0041 [-0.0136, +0.0069], relF1@2 +0.0026 [-0.0092, +0.0174]; every interval of both arms and both strata holds 0: **"not separated"** (wording per `GAPS` G-W8, not "no leak").
- Screens stay on cv5v2 with clean-cell scoring (D lead `v0.2` s11 item 10 (d)); excluding the 91 cells changed no contrast sign, no screen flag and no row order; M stays 0.010 (inactive 0.055 to 0.061) (E `SPI` s11 item 5).
- The 528-cell rule of v0.2 (4 duplicated cells) is superseded by the clean-cell set (E `v0.2` s11 items 9 to 11; `GAPS` G-N8).

### 3.3 Full-pool training of the final models
- All 532 pool cells, label set v1.1, root `pool532_v11` (DATA_MANIFEST 33e65b3f, identical on gaint and cv02; E `log` 21 Nov 01:29); val = test = the cv5v3 fold-0 held-out list as an in-sample monitor whose numbers are never read (E `FRULE` s1, s5).
- The 10 full-pool runs: steps 1 to 18,000 under commit F (821dfad), steps 18,001 to 20,000 resumed under F2 (9967d59) after the final-validation stop of 21 Nov; CPU resume is bit-equal to an uninterrupted F2 run; on GPU only atomics noise remains (E `ADD1` items 1 to 3, completion).
- No held-out score of a full-pool model exists by design; the CV5 rows describe the recipe through the cv5v3 fold models (E `GAPS` G-N6).

### 3.4 Legacy test50 (continuity and public table)
- 19 counted openings (24 Oct to 21 Nov); before 24 Oct test was scored in every experiment, uncounted (E `TL` A, B).
- Opening #19 (21 Nov, with E1 #8): C1, C2, C1-D4 on v0 and v1.1; public table only, decides nothing alone; rows on all 50 cells, the 49 without the noisy cell `CSIR_00070_r8_c4`, and the 16 cells whose image id has no pool cell in its module (E `ORULE` s7; `FOR`). No further opening (D user 21 Nov 00:22: "Go, once").
- Every test50 number is an in-distribution number with known leakage (section 1), read after 18 earlier counted openings (E `FOR`).
- Numbers of the earlier openings stay as published: legacy split, v1 labels, all 50 cells, the clean 49 and the clean 42 without twins (E `v0.2` 3.2). #19 prints the 16 cells without a module link in place of the clean 42; no clean-42 row exists for #19 (E `GAPS` G-N9, open, low priority).
- `TL` section E ("benchmark openings", from 12 Nov) has no row.

### 3.5 E1 and the sealing rule
- **Policy** (D user 31 Oct; `EL` header): E1 is a second test set; any protocol may pre-register E1 co-primaries, read once at its single opening, never for tuning, selection or threshold choice; every opening is reported.
- **Sealing** (D brief 1; `v0.2` 3.3, unchanged): no development step reads a label or prediction of a test50 or E1 cell; the duplicate tool may read sealed images as pixels and writes pair lists only. `forbidden_v1.txt` holds the 167 stems no training list may contain (legacy test 50 + ext117 117) (E `v0.2` 3.3). The cell tables carry label summaries of the 156 sealed rows; no reader uses or prints those columns (E `v0.2` 3.3); the release ships those rows with identity columns only (E `REL` s2).
- **Registered openings** (E `EL`): #1 to #7 (1 Nov to 14 Nov); **#8 the final evaluation** (registered 21 Nov 11:22:35, REGISTERED.txt 4c783a77; opened 11:25:30 to 12:06:09; CONFIRMED); **#9 T3b** (registration 1 fb2c424c superseded by amendment 1 before any E1 file reached cv02; registration 2 22 Nov 03:13, REGISTERED.txt 5f18a820; opened 23 Nov 08:40:46 to 13:39:27, read once 13:38:00 to 13:39:27; CONFIRMED, 8.3; E `log` 23 Nov 13:39, 13:40; `T3V`).
- **Prior looks, reference wording** (E `ERR` item 5, quoting verdict.txt l138): "E1 7 registered openings (3 looks at one contrast) plus reads before 31 Oct and one use of published E1 contrasts (R0, 15 Nov); the final models were never scored on either set." The ledger phrase "4th look" is not used.
- **"Unseen modules"** (E `SPI` 5a): no E1 image id is linked to any training image id; the largest inlier count of an E1 cell with a pool cell is 7 (noise level); the test covers about a third of the image-id pairs; "supported, not proven".
- **After #9** (E `EL` #9 bullet; `T3R` s0, s12): E1 is training data for T3b models; this team makes no later zero-shot claim on E1. S: for an outside entrant that never trains on E1 labels E1 could stay a zero-shot set, but no outside registration path, E1 label builder or released C1 per-cell E1 record exists (12.3; ruling R10). The info sheet records E1 use (`IST` field B7).

## 4. Class list and label policy
- Output: the 24 legacy classes; mIoU-R13 = mean IoU over background, ribbons, padding, border, gridline, sp mono, crack, sp multi, material, frame edge, splice, inactive, edge dark; the 13 per-class IoUs are printed beside it (E `v0.2` s4).
- Class ids and the 13 ids of mIoU-R13: section 12.3 item 2.
- An absent class is never scored 0 or 1; all-class mIoU only as "mIoU over the k classes with ground truth", with k (S `draft` 4.2, unchanged).
- Crack inside inactive: single-label masks scored as they are (S `draft` 4.4, unchanged); 26 of 47 inactive cells have cracks drawn inside the inactive area (E `AUD` F4).
- One-source classes (10 of 24, among them splice, ARTS only, and corrosion, SDLE only): their per-class IoU measures source recognition (E, S `AUD` F7).
- Weak classes: at argmax on cv5v2, gridline 0.302, splice 0.021; at OP-C gridline 0.362, splice 0.113 with splice precision 0.20 (E `log` 15 Nov 17:59). On E1 the one clear per-class loss of C2 is sp mono, 0.243 to 0.166 (E `FOR`).
- **Unit "cell".** Every read so far scores the whole image window (E `AUD` F3: about 3 x 3 cells for ARTS, CFVS, CSIR). Crack-free cells, inactive area and any severity value therefore describe a window. Whether the benchmark keeps the window as its unit: ruling R4.

## 5. Metrics, operating points, statistics, decision rules
### 5.1 Headline card (D user 21 Nov 00:22; definitions E `draft` 5.1, `m0core` l47 to l49)
| Metric | Definition | Role in v1.0 |
|---|---|---|
| crack relF1@2 | relP@2 = share of predicted crack px within 2 px of ground-truth crack; relR@2 = share of ground-truth crack px within 2 px of a predicted crack px; distance = Euclidean distance transform per image, ignore px excluded, counts pooled over the scored set | **decides every crack contrast** |
| relP@2, relR@2, relF1@1 | as above (relF1@1 at 1 px) | printed; never R without P. v0.2 also printed relF1@3; dropped (D lead, 22 Nov: it decides nothing and no read used it; the CV5 read tool prints @1 and @2 only, grep of `results/final_tta_read/read.txt`) (section 14) |
| strict crack IoU | TP / (TP + FP + FN) from one confusion matrix over all scored px | printed with its convention band; **decides nothing** |
| inactive IoU | same, inactive class | printed; a guard in confirmations (drop at most M); never decides a sealed-set claim |
| mIoU-R13 | section 4 | balance metric; a guard |

- **Convention band +-0.019** (E `FRULE` s2; `AUD` F1): the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels. A strict-IoU delta is printed as "inside" or "outside the band", and decides nothing either way.
- The v0.2 level band 0.48 to 0.60 (legacy test masks) is not used in tables (E `GAPS` G-D7).
- Tolerance stays 2 px (E `v0.2` 5.1, A4: annotator-distance 95th percentile 2.000 px). Centreline F1@2 is not eligible: it rewards a 1-px dilation (E `v0.2` 5.1, A2m).
- Inactive band: about +-0.05 to 0.07, the interval size of inactive contrasts (E `AUD` s2; `ORULE` s4). It is not label noise: the raters found the spurious-inactive candidates mostly model errors (E `RAT` l47 to l50).

### 5.2 Guards
| Guard | Rule | CV5 confirmations | E1 opening #8 | T3b #9 | Record |
|---|---|---|---|---|---|
| width, pooled | predicted / GT crack px of the entry over that of the reference, 0.85 to 1.15 | yes | G1 | printed, not a guard | E `FRULE` s2; `ORULE` s4; `T3R` s8 |
| width, per source | same, each source with >= 40 cells in the cell set (ARTS, BMRK, CFVS, CSIR on P532; CSIR only on E1) | yes | G2 | no | same |
| false crack px | on crack-free cells (crack-free by the scoring label set: 303 of 532 and 226 of 416 pool cells; 74 E1 cells), entry <= 1.5 x reference | yes | G3 | G1 | E `HRN` s2; `FOR`; `T3R` s8; `v0.2` s11 item 5 |
| inactive IoU | delta >= -M(inactive) | yes | reported only | reported only | E `FRULE` s2; `ORULE` s4 |
| mIoU-R13 | delta >= -M (CV5) or >= -0.010 (sealed) | yes | G4 | G2 | same |

- Printed beside every row, deciding nothing: share of crack-free cells with >= 50 false crack px; crack component recall and precision (components >= 20 px); any-hit component recall; per-source and per-class values (E `v0.2` 5.2; `ORULE` s5). PF on cv5v3 (532, OP-A): false crack px 212, share 0.13%, any-hit recall 0.884 (E `HRN` s3; `C3X`).
- Point values decide; bounds inclusive; each guard is judged at every decision operating point and cell set (E `FRULE` s2).
- **Known issue** (E `HRN` s3, s4): PF averages under 1 false px per crack-free cell, so 1.5 x PF is tight for every arm without PF's partial freeze (HOUSE sits at 3.7 x); the question whether later entries keep this reference is open with the user since 18 Nov. Ruling R3.

### 5.3 Operating points
| Point | Definition | Role | Record |
|---|---|---|---|
| OP-A | argmax over the 24 classes | decides on CV5 and sealed sets; the final model's rule | E `FRULE` s3; `ORULE` s2 |
| OP-W | crack bias cross-fitted on the other folds so the width ratio matches the reference | decides on CV5; impossible on sealed sets (needs folds; a bias fitted there would be tuning) | E `v0.2` 5.3; `ORULE` s2 |
| OP-F | crack bias cross-fitted for F1 | printed, decides nothing; unstable under A/A (-0.0118 [-0.0357, -0.0005] crack IoU) | E `W1C` s2 |
| OP-C | argmax plus per-class biases for 11 of the 13 robust classes, fitted on the other 4 folds | **adopted** 15 Nov 16:07 as comparator for prior-shifting arms; entry class "decision layer"; variant 1 only (variant 2, inactive grid to +8.0, failed its rule) | E `v0.2` s11 items 8, 9; `log` 15 Nov 17:59 |

- OP-C passed its pre-set rule on both machines: mIoU-R13 +0.0137 [+0.0107, +0.0169] (gaint), +0.0126 [+0.0077, +0.0167] (cv02); whenever OP-C is used, gridline and splice IoU and their precision on cells without the class are printed beside mIoU-R13 (E `v0.2` s11 item 8).
- A prior-shifting arm's inactive or weak-class gain counts only at OP-A and against the baseline at OP-C (E `v0.2` 5.3; `W3` G18).
- Final-step weights only, or a readout fixed in the card (for example `swad`); no best-validation checkpoint (E `v0.2` 5.3; `FRULE` s1).

### 5.4 Statistics
- **CV5 interval** (E `v0.2` 5.4; `FRULE` s2): two-stage group bootstrap, module groups (285 on cv5v3, 330 on cv5v2), then one seed per fold and arm; 2,000 draws; 95% percentile. The read tool draws seeds unpaired, which is conservative; seed-paired differences are printed beside (E `FRULE` s2 (b)).
- **Margin** M = max(0.01, 2 x SE of the PF A/A {5,6} v {7,8}), per machine and cell set:

| Machine, split, cells | relF1@2 | strict crack IoU | mIoU-R13 | inactive IoU | Record |
|---|---|---|---|---|---|
| cv02, cv5v2, 532 | 0.010 | 0.010 | 0.010 | 0.049 (mean of 15 two-seed splits) | E `v0.2` 5.4; D lead `v0.2` s11 item 3 |
| gaint, cv5v2, 532 | 0.010 | 0.010 | 0.010 | 0.054 | E `R1` s4 |
| cv02, cv5v2, 416 clean | 0.0111 | | | | E `R2` s2 |
| cv02, cv5v3, 532 | 0.0100 (A/A -0.0002, SE 0.0037) | | | 0.0462 (allowed drop in the TTA read) | E `C3X`; `TT` T4, T7b |
| cv02, cv5v3, 416 clean | 0.010 | | | | E `SWD`; `HRN` s1 |
| E1, opening #8 | 0.010 fixed, not re-estimated (A/A C1 {7,8} - {5,6}: +0.0022 [-0.0425, +0.0507], SE 0.0225, descriptive) | | | reported only | E `ORULE` s4; `FOR` |
| U1 (LOSO-2, gaint) | 0.044 (frontier 0.064) | 0.032 | | | E `log` 17 Nov 18:46; `U1` |

- "M covers seed noise, not the choice of folds": the split-variance probe was never run (D lead `v0.2` s11 item 4; still true).
- **Sealed-set interval** (E `ORULE` s4; `T3R` s8): seed-aware two-stage bootstrap: per draw the clusters (71 source images on E1, 48 on test50) with replacement, then for each arm independently n models with replacement from its n (n = 5; 3 in T3b); each model's pooled metric on the weighted cells; arm value = their mean; 2,000 draws, `random.Random(0)`, 95% percentile. The fixed-model interval (clusters only) is printed beside; it speaks about the trained models, not the recipe.
- **Screen error rate:** 0 of 15 A/A splits would be promoted on any headline metric (E `v0.2` 5.4, A1).
- **Smallest detectable effect** (power 0.8): CV5 on cv5v2, at 2 / 3 / 5 seeds, relF1@2 0.0087 / 0.0071 / 0.0055, strict crack IoU 0.0083 / 0.0067 / 0.0052, mIoU-R13 0.0067 / 0.0055 / 0.0042, inactive IoU 0.0518 / 0.0423 / 0.0328 (E `v0.2` 5.4, A1). E1 opening #8: MDE = 2.80 x 0.0265 = 0.0742 (derived; ruled by the lead 21 Nov 15:13; flagged derived in `TT` T4, T8); the log's "about 0.05" from opening #7's SE is not used (E `GAPS` G-N4). T3b: about +0.085 at an assumed SE of about 0.030 (S `T3R` s11).
- **Multiplicity:** one pre-declared primary per arm and per opening; everything printed beside is descriptive; the ledgers count contrasts and openings (E `v0.2` 5.4; `ORULE` s10).
- **Machines:** a read never mixes machines; one GPU model for all dumps of an opening (E `v0.2` 5.4; `ORULE` s8).

### 5.5 Decision rules and verdict words
| Read | Pass condition | Verdict words | Record |
|---|---|---|---|
| Screen (2 seeds, cv5v2) | delta >= M and lower end > 0 at OP-A and OP-W, on 532 and 416 cells; pooled width held; per-source width failures are flagged and re-checked at 5 seeds (E `W2A` l48, l54) | SCREEN PASS (promotes to a 5-seed confirmation) / SCREEN FAIL, closed | E `R2` s2; `v0.2` 5.4 |
| Confirmation (5 seeds, cv5v3) | headline: delta >= M and lower end > 0 at all four values (OP-A, OP-W x 532, 416) | CONFIRMED = headline and every guard pass; NOT CONFIRMED, reported as a gain with failing guard items named = headline passes, a guard fails; NOT CONFIRMED (no confirmed gain) = headline fails, worded NO LOSS if the lower end > -M at all four, else LOSS | E `FRULE` s2; `log` 18 Nov 00:22 |
| Sealed opening (E1) | Delta >= M, lower end > 0, guards G1 to G4 | CONFIRMED / GAIN, FAILING GUARDS NAMED / NOT CONFIRMED ("WORSE" if the upper end < 0, else "interval holds 0" or "below M") | E `ORULE` s4 |

- **Selection-biased:** any CV5 number of an arm whose readout or component was chosen on the same cells carries this label on every line, and cannot confirm the arm (E `FRULE` s0).
- **Inactive:** pooled inactive IoU promotes no trained arm at 2 seeds; inactive arms are read by region counts or at 5 seeds (E `v0.2` 5.4).
- **Robustness duty** (from `AUD` F1, F9; protocol text, D lead, `log` 22 Nov 12:49; section 11): a CV5 gain is printed with its label-variant shifts and with k_0, the number of module groups whose removal takes it to 0, where the audit has computed them (section 7.1).

### 5.6 Seeds
- Screen = 2 seeds; table row and candidate = 5 seeds, 5 to 9 (D brief 6, via `v0.2` 5.4).
- L6 (D lead 15 Nov 16:01, `v0.2` s11 item 1): a row whose 2-seed interval against PF lies wholly below 0 at OP-A and OP-W stays at 2 seeds, printed as "2 seeds" with that interval; every other row and every candidate gets 5 seeds. S: under relF1@2 this keeps `ucf_dlv3_r50_pf` and `pratt_dlv3p_wcec` at 2 seeds (E `R1` s2: both relF1@2 intervals wholly below 0 at OP-A and OP-W).
- The other closed 2-seed rows were never run at 5 seeds and the user ruled no new experiments after T3b (D user 22 Nov 11:40). Ruling R1.
- Final models: 5 full-pool seeds per candidate (E `FRULE` s1). T3b: seeds 5, 6, 7 (D user 21 Nov 15:01).

## 6. Entries, tracks, fairness, leakage, governance
### 6.1 Entry classes (D brief 7, via `v0.2` 6.1; examples E as cited)
| Class | Content | Rule | Example in v1.0 |
|---|---|---|---|
| (a) trained single model | one set of weights, one forward pass | the default column | each C1 seed model (PF, one view) |
| (b) decision layer | post-hoc step on a trained model (class biases, rules, refiners) | never in the default column; credited only against the same model's argmax | OP-C (E `v0.2` s11 item 8) |
| (c) ensemble | several models or views | printed beside the equal-cost comparator; TTA rows print the view count (D `W3` G16) | C2: one weight set per seed, 8 D4 views, each seed scored as a single model (E `FRULE` s1); class (c) by views (E `RVO` N4). C3: 5 models x 8 views. C3 beside E-PF: "C3 costs 8 x E-PF" in forwards (E `FOR`), 11.8 x in FLOPs (E `IC` s2), so not equal cost; no equal-cost comparator exists for C3 either |
| (d) uses source metadata | source id at test time | separate row class, never in the default track | none; per-source bias closed (E `TT` T16a, src_calib) |

- The first v1.0 draft put a fixed TTA into class (a). No record supports that (E `RVP` B1); it is proposed only, not in force: ruling R7.

### 6.2 Data tracks (D user 15 Nov 12:40, via `v0.2` 6.2)
- Main track: only data and weights with clear terms ("clear terms" undefined: R2). As trained, C1, C2 and every pool-trained row use the 50 BMRK (ELPV, CC BY-NC-SA 4.0) cells, so C2 is research-only (2.4). Extra-data track, labelled: may train on UCF-EL and MultiSolSegment; nothing from them is redistributed. No extra-data entry exists in v1.0.
- A row with research-only weights is a benchmark row only and says so (D lead 15 Nov 12:49).
- **trained_on_e1** (E `T3R` s9): every T3b dump, record and run carries the mark; the read tools refuse marked records outside the T3b card; no T3b number enters a T3 table or an E1 column of any other track.

### 6.3 Tracks
| Track | State in v1.0 | Record |
|---|---|---|
| T1 full labels, CV5 | in force: cv5v3 5-seed tier and cv5v2 screen tier | E section 7 |
| T2 label efficiency | not part of v1.0; no CV5 run | D lead `v0.2` s11 item 4; D user 22 Nov 11:40 |
| T3 unseen modules (zero-shot) | E1 opening #8 decides; U-dev instruments are guards or descriptive | E `FOR`; section 8.2 |
| T3b few-shot inside E1 | E1 opening #9: P = ALL - ZS +0.2213 [+0.0977, +0.3504], CONFIRMED | E `T3R`; `T3V`; section 8.3 |
| T4 deployment | fairness record (6.4); CPU and GPU latency measured for the E1 candidates (scope: D lead 22 Nov 12:49) | E `IC` s3 |
| T5 post-evaluation, severity | appendix only; no watt or power band; "inactive area beats crack length" not supported | D lead 16 Nov 12:15; E `SEV` |

### 6.4 Fairness record per row (guard G16; E `W3` s6; `RR2` s3)
- Every row states: total and trainable parameters, GFLOPs at 512 px per view, output stride, steps x batch, images seen, pretraining data and weights with licence, peak memory, step time, view count for TTA, deviations from the paper it stands for.

| Row | Params (encoder) | GFLOPs per view | Stride | Peak MiB (training) | s/step | Steps x batch | Record |
|---|---|---|---|---|---|---|---|
| PF (house R34 U-Net++) | 26,075,672 (21,278,400) | 148.0 | 1 | 5,736 (cv02) | 0.18 | 20k x 8 | E `RR2` s3 |
| HRNet-W18 U-Net++ | 20,795,692 (10,947,028) | 218.0 | 1 | 8,430 (cv02) | 0.32 | 20k x 8 | E `RR2` s3 |
| HRNet-W18 U-Net++ + SWAD (C2 card) | as HRNet | as HRNet | 1 | 9,462 (gaint path smoke); cv02 estimate 8,634 to 8,740 | n/r | 20k x 8 | E `log` 17 Nov 19:48 |
| SegFormer MiT-B2 | 24,722,008 (24,190,016) | 50.0 | 4 | 7,444 | 0.19 | 20k x 8 | E `RR2` s3 |

- Per cell at inference (E `IC` s2, computed there): C1 148, E-PF 740, C1-D4 1,184, C2 1,744, C3 8,722 GFLOPs.
- G16 line: above 2 x the house training or inference cost, the PF 2-seed ensemble is printed as the equal-cost comparator; TTA rows print the view count (D `W3` G16). HRNet alone is below the line (1.47 x FLOPs, 1.8 x step time; E `RR2` s3).
- C2 with D4 is above the G16 line at inference (1,744 GFLOPs per cell, 11.8 x C1; E `IC` s2). G16's comparator, a PF 2-seed ensemble, was not printed for C2 on CV5 or E1, and no FLOP-matched PF comparator exists in any read (the C1-D4 E1 jobs wrote no logp, E `IC` s4; no CV5 ensemble read exists, E `FRULE` s1). Printed instead:
  - same-view controls PF_D4 (CV5) and C1-D4 (E1), 1,184 GFLOPs per cell, 0.68 x C2 (derived: 1,184 / 1,744). They isolate the model part (C2 - C1-D4 +0.0451 [+0.0173, +0.0699], E `FOR`) but are not equal cost, and on E1 they draw cracks thinner: width ratio C2 / C1-D4 = 0.463 / 0.345 = 1.34 (derived from `TT` T11a); no guard was printed for that contrast;
  - on E1 only, E-PF (5-seed PF ensemble, 740 GFLOPs per cell, 0.42 x C2, derived: 740 / 1,744), contrasted with C3 and C1, not with C2. C2 - E-PF = 0.4897 - 0.4489 = +0.0408 at point level (derived from `TT` T11a; no interval).
- This deviation from G16 was not ruled before the opening and is disclosed here first (S; E `RVP` B1). Ruling R7.
- Stride: a row with output stride above 1 is printed with its stride and the head-resolution ceiling (E `v0.2` 6.4); stride 4 costs about 0.02 strict IoU and 0.02 relF1@2 once width is matched, stride 8 about 0.08 to 0.10 (E `R1` s3). For stride 4 (strict crack IoU / relF1@2): the stride-1 model pooled to stride 4 gives 0.159 / 0.533 at OP-A and 0.279 / 0.717 at OP-W; the ground-truth lower bound of the ceiling is 0.521 / 0.955 at width ratio 1.365. The ceiling bars nothing: a stride-4 row that passes the standard rule is a candidate like any other (E `v0.2` 6.4).
- **Latency** (E `IC` s3.3; gaint CPU, AMD Threadripper 7960X, 16 threads, batch 1, fp32, network time only): median s per cell (p90) C1 0.216 (0.233), E-PF 1.40 (1.48), C1-D4 2.23 (2.37), C2 3.88 (4.38), C3 16.6 (19.2); C2 is 18.0 x C1 in CPU time against 11.8 x in FLOPs. Peak RSS of C2 at 16 threads: 1,376 MiB (batch 1), 4,382 MiB (batch 8) (E `IC` s3.1). The host was shared during the runs (E `IC` s3.1). Observed cv02 dump wall times are upper bounds dominated by fixed costs (C2 on E1: 100 s per 106-cell job, 0.94 s per cell with logp writes; E `IC` s4). **GPU latency** (E `IC` s3.4; cv02, one RTX A6000, fp32, TF32 off, network time only, 200 timed cells per config; measured 22 Nov 17:50 to 18:04 IST): median s per cell at batch 1 (p90) C1 0.0112 (0.0112), E-PF 0.0559 (0.0561), C1-D4 0.0911 (0.0915), C2 0.174 (0.177), C3 0.855 (0.862); at batch 8: C1 0.0099, E-PF 0.0491, C1-D4 0.0800, C2 0.133, C3 0.675; C2 is 15.5 x C1 at batch 1; C2 with its 8 views in one batch 0.134 (0.135). The host was shared during the run, so these are upper bounds for an idle A6000 at these settings (S `IC` s3.4). Scope: the E1 candidates only, not every row as `v0.2` s11 item 4 said (D lead, `log` 22 Nov 12:49; brief `log` 22 Nov 11:30).

### 6.5 Leakage guards (E `v0.2` 6.5 unless stated)
- **Pool list:** `benchmark/splits/pool_t9_v2.txt` (4,949 cells, 39877ede) replaces `pool_t9.txt` (6,424): 1,475 pool cells sat in physical modules that hold labelled cells (pre-set rule; 1,003 under rule B, E `SPI` l124) (D lead 15 Nov 22:14, `v0.2` s11 item 10 (e)). A pool cell is out if it shares a module, an md5, embedding cosine >= 0.98 or band-pass NCC >= 0.80 with any labelled or sealed image. Not searched: the 159k full pool.
- **Weights:** third-party weights trained on SCDD or E-SCDD are forbidden; generic public weights (ImageNet, DINOv2, SAM 2) are allowed and named (D `W3` G14).
- **Teachers:** a teacher, generator or labeller never saw the student's held-out fold; the assert fails closed (D `W3` G14).
- **Roots:** full-pool roots list no sealed stem (E `FRULE` s1); T3b fold roots list and link no held-out E1 cell, and the train smoke runs with the held-out files deleted (E `T3R` s4).
- **Sealed dumps** run only under a registered opening (`--opening`), relayed with checksums, unstaged from cv02 after the read (E `ORULE` s8, s9; `T3R` s10).
- UCF-EL, if used: 227 images excluded by the near-duplicate rule (E `v0.2` 6.2).
- Limits: BMRK and SDLE carry no module id in pixels (SDLE modules come from the stems), so neighbouring-window leakage cannot be excluded there (E `AUD` F11; `SPI` s11).

### 6.6 Reporting governance
1. **Info sheet per entry:** `IST` (template + the C2 worked example). The generator script `bench_infosheet.py` of v0.2 was not built; the sheet is filled by hand from result files (E: no file of that name found on gaint, `find /`, 22 Nov).
2. **Reporting checklist, 10 items:** section 12.1, as a fill-in table. **Scoring procedure for a new entry:** section 12.3, citing the release README `REL`.
3. **Ledgers:** `TL` (test50) and `EL` (E1). One opening per locked protocol; the rule's md5 and REGISTERED.txt md5 are written in the ledger before any sealed dump; the read runs once; repeats need a TAG and are not the registered read; an amendment is a dated ledger line with its own md5, reviewed before it runs (E `ORULE` s9; `T3R` s10; `T3A`).
4. **Errata:** a result file is never edited after its md5 is pinned; corrections go in an errata file that names the lines it supersedes (E `ERR` header).
5. **Scoped wording** (E `GAPS` C): "unseen modules: supported, not proven"; leakage "not separated"; TTA "robust on CV5 (known modules); on E1 the D4 part is not resolved"; "one double annotation" with every ceiling statement.
6. **Related-work table:** `RW` (section 1).
7. **Guards G17, G19, G20 are protocol text** (D lead, `log` 22 Nov 12:49; wording E `W3` s6 items 17, 19, 20; `v0.2` Open 9): G17 BN contamination: every second-stream arm states `bn` and reports `arm_bn`. G19 post-hoc and CPU results: parameters fixed before the read or cross-fitted; explored on W1-G, confirmed unchanged on W1-C1; Holm over the variants read; entered in the benchmark as a decision-layer entry class, never in the default column. G20 inactive reads: leave-top-3-groups-out, region counts, the BMRK row, fold-level values; F51 and H36 inactive in no promotion rule (4 and 3 cells).

## 7. Baseline suite
### 7.1 Tier 1: cv5v3, 5 seeds (cv02, seeds 5 to 9, folds 0 to 4, out of fold, OP-A, mean over seeds)
Levels (E `TT` T5, copied from `C3X`, `HRN`, `SWD`, `TTA` and final_tta_read; CS and CS_D4 selection-biased; n/r = not reported in the cited file):

| Arm | Strict crack IoU (decides nothing) | relF1@2 | Inactive IoU | mIoU-R13 | False crack px | Width ratio | relF1@2, 416 |
|---|---|---|---|---|---|---|---|
| PF (U-Net++ / ResNet-34, encoder-preserving fine-tune; C1 recipe) | 0.3653 | 0.8463 | 0.5042 | 0.6116 | 212 | 1.0189 | 0.8264 |
| HOUSE (plain fine-tune) | 0.383 | 0.852 | 0.514 | 0.607 | 774 | 1.13 | n/r |
| HRNET (HRNet-W18 U-Net++, PF recipe) | 0.3661 | 0.8567 | 0.5142 | 0.6138 | 767 | 0.97 | 0.8379 |
| SWADBN (swad_const, readout swad_bn) | 0.3834 | 0.8532 | 0.5196 | 0.6189 | 339 | n/r | 0.8362 |
| SWAD (same runs, readout swad) | 0.383 | 0.853 | 0.525 | 0.612 | n/r | n/r | n/r |
| CB = COMBO (HRNet + SWAD, swad_bn) | 0.3753 | 0.8617 | 0.5042 | 0.6182 | 384 | 1.0093 | 0.8431 |
| CS = COMBO_SWAD (swad; selection-biased) | 0.3814 | 0.8629 | 0.5203 | 0.6189 | 213 | 0.9986 | 0.8439 |
| PF_D4 (PF + D4; C1-D4 recipe) | 0.3883 | 0.8597 | 0.5306 | 0.6200 | 32 | 1.0401 | 0.8395 |
| CS_D4 (C2 recipe on CV5; selection-biased) | 0.3942 | 0.8684 | 0.5370 | 0.6232 | 98 | 1.0118 | 0.8494 |
| CB_D4 (information only) | 0.3954 | 0.8706 | 0.5284 | 0.6255 | 168 | 1.0275 | 0.8522 |

Contrasts and registered verdicts (relF1@2, arm - reference, 95% interval; E `TT` T6, T7a and the files named; `HPF` s1, s3 for HOUSE - PF and the strict-IoU intervals; `HCS` s1, s2, s4 for the two HOUSE-rule rows):

| Contrast | 532 OP-A | 532 OP-W | 416 OP-A | 416 OP-W | Strict crack IoU, 532 OP-A (decides nothing) | Failing guard items | Verdict | Record |
|---|---|---|---|---|---|---|---|---|
| HRNET - PF | +0.0104 [+0.0012, +0.0203] | +0.0117 [+0.0019, +0.0220] | +0.0115 [+0.00001, +0.0259] | +0.0126 [+0.0006, +0.0273] | +0.0008 [-0.0105, +0.0111] | false crack px 2.90 to 4.15 x PF (all four values); ARTS width 1.162 (416, OP-W) | NOT CONFIRMED, reported as a gain with failing guard items | E `HRN` s1, s2; `HRNr` l213 |
| SWADBN - PF | +0.0070 [-0.0007, +0.0156] | +0.0048 [-0.0036, +0.0141] | +0.0098 [+0.0009, +0.0198] | +0.0071 [-0.0025, +0.0176] | +0.0180 [+0.0108, +0.0262] | ARTS width; false crack px 1.60 x (5 items) | NOT CONFIRMED (no confirmed gain) | E `SWD` |
| SWAD - PF (secondary readout) | +0.0064 [-0.0009, +0.0138] | +0.0053 [-0.0022, +0.0128] | +0.0075 [-0.0009, +0.0165] | +0.0058 [-0.0030, +0.0150] | +0.0181 [+0.0106, +0.0257] | ARTS width at OP-A (2 items) | not confirmed (neither readout passes the headline) | E `SWD` |
| COMBO - PF | +0.0154 [+0.0065, +0.0260] | +0.0158 [+0.0069, +0.0264] | +0.0167 [+0.0055, +0.0298] | +0.0166 [+0.0054, +0.0298] | +0.0099 [-0.0007, +0.0207] | ARTS width; false crack px (8 items) | NOT CONFIRMED, reported as a gain with the failing guards named | E `C3X`; `C3Xr` l327; `HPF` s3 |
| CS - PF (declared secondary; selection-biased) | +0.0166 [+0.0082, +0.0263] | +0.0173 [+0.0087, +0.0272] | +0.0176 [+0.0071, +0.0300] | +0.0180 [+0.0076, +0.0305] | +0.0161 [+0.0066, +0.0258] | ARTS width, 416 cells (2 items) | cannot be claimed from the c3x read | E `C3X`; `TT` T6 |
| (a) PF_D4 - PF | +0.0134 [+0.0066, +0.0207] | +0.0132 [+0.0062, +0.0205] | +0.0132 [+0.0047, +0.0220] | +0.0132 [+0.0047, +0.0223] | +0.0230 [+0.0154, +0.0306] | none | **CONFIRMED** | E `TTA`; `TT` T7a |
| (b) CS_D4 - CS | +0.0055 [-0.0002, +0.0115] | +0.0055 [-0.0009, +0.0118] | +0.0054 [-0.0023, +0.0129] | +0.0049 [-0.0033, +0.0125] | +0.0128 [+0.0053, +0.0202] | none | NOT CONFIRMED, NO LOSS; FLAG D4, ruled "keep D4" (D user 21 Nov 11:21) | E `TTA`; `TT` T7a |
| (c) CS_D4 - PF | +0.0222 [+0.0138, +0.0308] | +0.0228 [+0.0141, +0.0320] | +0.0230 [+0.0127, +0.0341] | +0.0229 [+0.0124, +0.0340] | +0.0288 [+0.0197, +0.0374] | ARTS width 1.159 (416, OP-A and OP-W) | C2 PASSES ITS CV5 CHECK (selection-biased; the E1 opening is the test) | E `TTA`; `TT` T7a |
| CS_D4 - PF_D4 (descriptive) | +0.0087 [+0.0017, +0.0157] | +0.0096 [+0.0022, +0.0172] | +0.0099 [+0.0016, +0.0190] | +0.0097 [+0.0013, +0.0192] | +0.0058 [-0.0006, +0.0121] | | decides nothing | E `TT` T7a |
| HRNET - HOUSE (secondary) | +0.0045 [-0.0069, +0.0157] | +0.0083 [-0.0041, +0.0209] | | | -0.0171 [-0.0291, -0.0068] | | decides nothing | E `HRN` s3; `HRNr` l237, l238, l254 |
| COMBO - HRNET / COMBO - SWADBN (secondary) | +0.0050 [-0.0041, +0.0141] / +0.0085 [-0.0017, +0.0183] | | | | | | NO LOSS | E `C3X` |
| HOUSE - PF (printed intervals; no registered rule) | +0.0059 [-0.0043, +0.0152] | +0.0034 [-0.0075, +0.0127] | +0.0066 [-0.0068, +0.0191] | +0.0025 [-0.0116, +0.0156] | +0.0179 [+0.0093, +0.0266], inside the band | 9 items outside a bound: ARTS width at all four values (1.307 / 1.167 / 1.370 / 1.190), CFVS width 1.164 (416, OP-A), false crack px 2.55 to 3.66 x PF (all four values) | decides nothing; relF1@2 not separated at any of the four values | E `HPF` s1, s2 |
| CS_D4 - HOUSE (HOUSE rule; selection-biased; printed intervals, no registered rule; 8 views against HOUSE's 1) | +0.0163 [+0.0051, +0.0284] | +0.0194 [+0.0080, +0.0319] | +0.0164 [+0.0033, +0.0318] | +0.0204 [+0.0073, +0.0369] | +0.0110 [+0.0029, +0.0198], inside the band | ARTS width 0.847 (532) and 0.846 (416) at OP-A, below 0.85 (2 items) | decides nothing | E `HCS` s1, s4 |
| CS - HOUSE (HOUSE rule, single view on both sides; selection-biased; printed intervals, no registered rule) | +0.0107 [-0.0009, +0.0229] | +0.0140 [+0.0017, +0.0269] | +0.0110 [-0.0028, +0.0264] | +0.0155 [+0.0013, +0.0320] | -0.0018 [-0.0109, +0.0078], inside the band | CFVS width 0.841 (416, OP-A) (1 item) | decides nothing | E `HCS` s2, s4 |

- **HOUSE rule** (D lead, `W1C` s3, 14 Nov; `v0.2` s7): any arm that claims an in-distribution crack gain is also printed against HOUSE. Kept (D lead, `log` 22 Nov 12:49). Applied to HRNet (HRNET - HOUSE above) and to the C2 recipe (the two HOUSE-rule rows above; E `HCS` s1, s2; selection-biased, no registered rule, decides nothing): CS_D4 - HOUSE relF1@2 at 532 OP-A +0.0163 [+0.0051, +0.0284]; CS - HOUSE +0.0107 [-0.0009, +0.0229]. HOUSE - PF has intervals (E `HPF`). **Limitation:** no HOUSE_D4 dumps exist (E `HCS` s3), so CS_D4 - HOUSE sets an 8-view arm against a single-view reference, a recorded limitation; CS - HOUSE, single view on both sides, is the like-for-like line (S `HCS` s9); no new runs (D user 22 Nov 11:40).
- Wording for the (c) row (D lead 21 Nov 15:22, adopted from `GAPS` D1): "On CV5 the C2 recipe (CS_D4) passes its check against PF (selection-biased); the ARTS width guard fails on the 416 clean cells at OP-A and OP-W (1.159 against the 1.15 band; named) and passes on the 532 cells." verdict.txt prints both "GAIN, FAILING GUARDS NAMED" (l126) and "C2 PASSES ITS CV5 CHECK" (l170) (E `GAPS` G-D2).
- Correction to `TT` T6 and `GAPS` G-N2: the strict-IoU intervals of HRNET - PF and COMBO - PF exist in the read files (`HRNr` l213, l229; `C3Xr` l327, l343); the read files win (E `log` 22 Nov 11:41); `HPF` s3 reproduces them exactly.
- Robustness (E `AUD` s2, `TT` T19b): HRNET - PF relF1@2 +0.0104 moves to +0.0073 on 3-px labels, k_0 17; COMBO - PF stays a pass under all four label variants, k_0 31; SWADBN and HOUSE strict-IoU passes do not survive the centreline variant (+0.0047, +0.0015).
- Swad vs swad_bn: the `swad` readout of C2 was chosen after the c3x read on these cells; every CS and CS_D4 number is selection-biased (E `FRULE` s0).
- Screen shrinkage (E `SWD` s3): swad_const relF1@2 +0.0135 on the cv5v2 screen, +0.0070 on cv5v3 at 5 seeds; S `SWD`: winner's curse on a screen-selected arm.

### 7.2 Tier 2: cv5v2 screens (2 seeds unless stated; argmax; 532 cells; mean over seeds)
Levels E `TT` T15 (from `R1`, `R2`, `W2A`); strides E `R1` s1 and `RR2` s3; primary contrasts and verdicts E `TT` T16a (from `R1`, `R2`, `W2A`, `LACE`, `LCI`).

| Row | Machine | Stride | relF1@2 | Strict IoU | Inactive | mIoU-R13 | Width | Primary contrast [95%] | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| PF (comparator) | cv02, 5 seeds | 1 | 0.844 | 0.365 | 0.503 | 0.612 | 1.00 | | |
| HOUSE | cv02 | 1 | 0.850 | 0.382 | 0.522 | 0.609 | 1.11 | strict IoU vs PF +0.0173 [+0.0107, +0.0241] (OP-A) | screen flag; row of its own (D `W1C` s3, via `v0.2` s7) |
| unet_r34_pf | cv02 | 1 | 0.843 | 0.364 | 0.522 | 0.612 | 1.00 | relF1@2 -0.0016 [-0.0110, +0.0073] | not separated |
| hanifi_vgg16_unet_pf | cv02 | 1 | 0.838 | 0.349 | 0.498 | 0.610 | 0.96 | -0.0064 [-0.0189, +0.0042] | not separated |
| dlv3p_r34_pf | cv02 | 4 | 0.835 | 0.354 | 0.478 | 0.609 | 1.21 | -0.0093 [-0.0204, +0.0019]; OP-W -0.0199 [-0.0325, -0.0086] | below at OP-W |
| ucf_dlv3_r50_pf | cv02 | 8 | 0.767 | 0.287 | 0.497 | 0.574 | 1.23 | -0.0773 [-0.0892, -0.0594]; OP-W -0.0984 [-0.1113, -0.0799] | below at both; L6: 2 seeds |
| pratt_dlv3p_wcec | cv02 | 4 | 0.751 | 0.258 | 0.506 | 0.604 | 3.05 | -0.0932 [-0.1113, -0.0774]; OP-W -0.0899 [-0.1130, -0.0693] | below at both; L6: 2 seeds |
| hrnet_w18_unetpp_pf | cv02 | 1 | 0.856 | 0.365 | 0.522 | 0.618 | 0.94 | +0.0114 [+0.0032, +0.0203]; OP-W +0.0128 [+0.0041, +0.0221] | SCREEN PASS, promoted to tier 1 |
| skr01_pf_v11 (Skeleton Recall) | cv02 | 1 | 0.848 | 0.372 | 0.480 | 0.611 | 1.13 | +0.0039 [-0.0027, +0.0115] | SCREEN FAIL, closed |
| segformer_mitb2_pf | cv02 | 4 | 0.842 | 0.348 | 0.530 | 0.608 | 1.20 | -0.0026 [-0.0132, +0.0095]; OP-W -0.0135 [-0.0259, -0.0005] | SCREEN FAIL, closed; research-only weights, benchmark row only (E `RR2` l11, l15, l92; `LIC` s2) |
| PF (W1-G comparator) | gaint | | 0.842 | 0.362 | 0.498 | 0.612 | 1.01 | | |
| swad_const (swad_bn) | gaint | | 0.855 | 0.387 | 0.508 | 0.620 | 1.07 | +0.0135 [+0.0051, +0.0221] | SCREEN PASS, promoted to tier 1 |
| rcs (rare-class sampling) | gaint | | 0.833 | 0.344 | 0.485 | 0.614 | 0.94 | -0.0085 [-0.0187, -0.0004] | FAIL, closed |
| ema_9998_bn | gaint | | 0.838 | 0.363 | 0.497 | 0.610 | 0.98 | vs raw_bn +0.0018 [-0.0047, +0.0081] | null, closed |
| jml_hard (control) | gaint | | 0.841 | 0.364 | 0.513 | 0.613 | 0.99 | -0.0004 [-0.0086, +0.0064] | null control |
| encoder_spd | gaint | | 0.842 | 0.374 | 0.501 | 0.606 | 1.08 | +0.0007 [-0.0272, +0.0130] | gate failed, descriptive |
| soft_band_jml | gaint | | | | | | | vs jml_hard +0.0046 [-0.0033, +0.0127] | SCREEN FAIL, closed |
| la_ce (train-time logit offsets) | gaint | | | | | | | mIoU-R13 vs PF at OP-C -0.0022 [-0.0112, +0.0060] | DROP; la_ce_full owed, not run |
| layered_ci (inactive aux head + layer) | gaint | | | | | | | inactive region recall vs PF at OP-C -0.0140 [-0.0767, +0.0556] | PARK, no promotion at 2 seeds |

- Decision layers read on cv02 (E `TT` T16a; `W1C`): src_calib (per-source bias) and dti_hysteresis closed (no gain); OP-F unstable; OP-C adopted (5.3).
- Limits (E `R1` s3; `R2` s5): 2 seeds, one machine per read, pool cells of known modules only; ucf row uses ImageNet weights (not COCO) and no auxiliary head; pratt row uses the house augmentation with the paper's loss.

### 7.3 Final models (definition fixed before any number; E `FRULE` s1; `ORULE` s2)
| Id | Definition | Weights key | Inference |
|---|---|---|---|
| C1 | full-pool PF, card `house_r34_unetpp_pf_v11` (a4a46a52), seeds 5 to 9 | `model` | plain, one view, fp32, OP-A |
| **C2** (the final model) | full-pool HRNet-W18 U-Net++ + SWAD, card `hrnet_w18_unetpp_swad_const_pf_v11` (98f152de, commit 03375d4), seeds 5 to 9; deployable single model = seed 5 | `swad` (uniform average over steps 10,000 to 20,000, no BN re-estimate) | D4: 8 views, softmax per view averaged, fp32; pred = argmax of log(p + 1e-12); OP-A |
| C3 | 5-seed mean-softmax ensemble of C2 | `swad` | as C2, then mean over seeds |
| E-PF, C1-D4 | comparators beside: 5-seed ensemble of C1; C1 with D4 | `model` | |

- C2 is primary, C3 beside (D lead 21 Nov 01:29, ruling Q1); candidates approved by the user (D user 21 Nov 00:22).

### 7.4 E1 opening #8 and test50 opening #19 (E `FOR`; wording `ERR`)
Decision (106 cells, 71 clusters, OP-A):

| Item | Value | Outcome |
|---|---|---|
| **P = C2 - C1, crack relF1@2** | **+0.0430 [+0.0013, +0.1043]** seed-aware (SE 0.0265); fixed-model [+0.0067, +0.1007] | **CONFIRMED** |
| G1 width pooled / G2 width CSIR | 1.013 / 1.013 | pass |
| G3 false crack px, 74 crack-free cells | C2 2421 vs C1 3218 (0.75 x) | pass |
| G4 mIoU-R13 | +0.0249 | pass |
| inactive IoU (10 cells; reported only) | +0.0996 [-0.0310, +0.2162] | n.d. |
| strict crack IoU | +0.0263 [+0.0022, +0.0651], outside the band | decides nothing |

- Levels, relF1@2, mean over 5 seeds (range): C1 0.447 (0.439 to 0.457), C2 0.490 (0.466 to 0.507), C3 0.487, E-PF 0.449, C1-D4 0.445 (E `FOR`; source of these levels is read_e1/read.txt, not verdict.txt: `GAPS` G-D4).
- Printed beside, deciding nothing: C2 - C1-D4 +0.0451 [+0.0173, +0.0699]; C1-D4 - C1 -0.0021 [-0.0423, +0.0575]; S3 C3 - C2 -0.0025 [-0.0254, +0.0157]; S1 C3 - C1 +0.0405 [-0.0044, +0.1108]; S2 C3 - E-PF +0.0383 [+0.0007, +0.0904]; S4 C2 seed 5 - C1 +0.0189 [-0.0403, +0.1068]; S5 E-PF - C1 +0.0023 [-0.0165, +0.0279].
- Strata of P (cells / clusters): CSIR 101 / 66 +0.0433 [+0.0015, +0.0984]; BMRK 5 / 5 -0.1843 [-0.5529, 0.0000] (C2 0.0000, C1 0.1843 [0.0000, 0.9216]; C1-D4, C3, E-PF also 0.0000; rests on 5 cells, `ERR` item 4); full cells 44 / 24 +0.1464 [+0.0420, +0.2278]; half-cut cells 62 / 47 +0.0110 [-0.0289, +0.0722]; crack cells 32 / 21 +0.0340 [-0.0114, +0.0862].
- **Reading, errata wording** (E `ERR` items 1, 2, 5): "Most of the gain is the model. C2 - C1-D4 (both 8 views) is +0.0451 [+0.0173, +0.0699]. The D4 part is not resolved on E1." "On E1 the point effect is about 2 to 3 x its CV5 size: +0.043 vs +0.015 to +0.022. ... The E1 interval [+0.0013, +0.1043] contains the CV5 values, so E1 does not show a larger effect than CV5." No candidate, readout or threshold was selected on E1 cells, but C2's readout (swad) and D4 were chosen on pool cells.
- **Scope of the claim** (E `TT` s0; `ORULE` s4): the recipe averaged over seeds 5 to 9, not one checkpoint; carried by the full cells; half-cut cells n.d.; 101 of 106 cells CSIR; OP-A only; nothing about inactive, test50 or cells unlike E1. n.d. rows cannot exclude effects below about 0.074 at 80% power (derived MDE, 5.4).
- **test50 #19, public table, decides nothing** (E `FOR`): on v0, Pratt rule A median IoU crack C2 0.383 (C1 0.337), inactive 0.588 (0.570), mean of 3 0.424 (0.405), against Pratt 2023 model 4c 0.25 / 0.38 / 0.28; PV-S3 crack IoU C2 0.441 (C1 0.418) against their 0.58 (split and background rule not stated); SEiPV family micro IoU C2 0.896, fw-IoU 0.903 against their 'IoU' 0.7447 / 'mIoU' 0.8604 (averaging not defined). On v1.1: C2 - C1 relF1@2 +0.0102 [-0.0094, +0.0291] (all 50), +0.0102 (clean 49), +0.0322 [+0.0036, +0.0584] (16 cells without a module link); levels C1 0.891, C2 0.901, C1-D4 0.901. These rows are context only, never a claim to beat a published model.

### 7.5 What passed, in one list (E as cited)
- CONFIRMED on CV5: D4 TTA on PF, (a) +0.0134 [+0.0066, +0.0207] (`TTA`).
- Passed a registered non-inferiority score claim (gaint, cv5v2, W1-G PF, 2 seeds, M from ROWS1, no A/A in the read): D4MS "counts as a non-inferior score arm", the first method to pass its full registered claim (19 Nov); D4MS - PLAIN relF1@2 +0.0142 [+0.0079, +0.0202] (`B5` l3, l7, l12; `log` 19 Nov 01:24).
- CONFIRMED on E1: C2 - C1 (`FOR`).
- Gains with failing guards (5 seeds): HRNet-W18 (false crack px at all four values; ARTS width 1.162 at 416, OP-W), HRNet + SWAD swad_bn (ARTS width, false crack px) (`HRN`; `C3X`).
- Not confirmed: swad_const (headline), D4 on top of HRNet + SWAD (NO LOSS) (`SWD`; `TTA`).
- Closed at screen: skr01, segformer, rcs, ema_9998, soft_band_jml, la_ce (CE vector); parked: layered_ci, gin_ipa (`TT` T16a; `log` 17 Nov 18:46).

## 8. Unseen modules, other instruments, deferred items
### 8.1 Levels of the PF recipe across instruments (E `TT` T14; models differ per row, so no interval exists for the gaps)
CV5 cv5v3 532 cells 0.8463; 416 clean 0.8264; U2 simulated unseen-module views 0.769; U1 held-out sources (CSIR, BMRK) 0.733; test50 v1.1 0.8905; test50 cells without a module link 0.8227; E1 all 0.4467 [0.4387, 0.4574] (range over seeds); E1 full cells 0.4808; E1 half-cut cells 0.4312. S (`FOR`): a large domain gap.

### 8.2 Development instruments (U-dev)
| Read | State in v1.0 | Record |
|---|---|---|
| U1 LOSO-2 (CSIR 114, BMRK 50 held out; pooled 164 cells, effective n crack 17.7) | rule fixed before any run; read 17 Nov: SKR01 - PF at the frontier +0.0206 [-0.0518, +0.0744]: **U1 is a guard, not a primary**; gin_ipa parked | E `U1`; `log` 17 Nov 18:46 |
| U2 synthetic half-cut views (1,064) | rebuilt (shvoof_v2), passed re-review; read 19 Nov 01:23 to 01:28 (file written 21 Nov), all descriptive: SWADBN differs above (wider), EMABN below | E `RBF`; `U2U4` |
| U3 F51 | not built: udev_tta_f51 not armed, F51 descriptive only | E `log` 19 Nov 01:24 |
| U4 H36 crack-free (19), pool half-cells (943, label-free) | false alarms only on the labelled cells; read 19 Nov 01:23 to 01:28 (file written 21 Nov), descriptive | E `U2U4` |
| U5 CSIR multi cells (32) | guard and descriptive stratum | E `v0.2` 8.1 |

- Rule (D `W3` G15; `v0.2` 8.1): development proxies never support a claim about E1; only a registered opening does.

### 8.3 T3b: few-shot layout adaptation inside E1 (E1 opening #9; E `T3R`; `EL` #9)
- Question: how much the final recipe gains on E1 layouts once it has labelled E1 cells, measured out of fold by image id, against the same recipe zero-shot.
- Folds: K = 5 by image id (`benchmark/out/t3b_draft_folds.tsv` 49e70413, unchanged since 12 Nov); held-out 22 / 22 / 20 / 21 / 21 cells; lists LISTS.md5 5c86318a.
- Arms (33 trainings): ALL = 532 pool cells + every E1 cell outside fold k; HALF = 532 + a fixed half of the training-side E1 image ids; deployable `t3b_deploy_s5..7` (532 + 106, never scored on E1). Recipe exactly C2's (card 98f152de), seeds 5 to 7, readout `swad`, D4, OP-A. Comparator ZS = opening #8's C2 dumps of seeds 5 to 7, re-scored.
- Primary: P = ALL - ZS, pooled out-of-fold crack relF1@2 over the 106 cells; seed-aware two-stage bootstrap (71 clusters x 3 models), 2,000 draws, M 0.010. Guards: false crack px on 74 crack-free cells ALL <= 1.5 x ZS; mIoU-R13 >= -0.010. Width printed, not a guard (E1 labels about 1.5 x wider). Printed beside: HALF - ZS, ALL - HALF, any-hit recall, strata full / half-cut / hard (half-cut + scuff) / half-cut without scuff, inactive, strict IoU with band.
- Registration 2: 22 Nov 03:13, REGISTERED.txt 5f18a820 (jobs d77f3a94 / 9423cb91); progress at 11:12: 7 of 33 trained and relayed (E `log` 22 Nov 11:12).
- **T3b result** (E `T3V` l5 to l14, l75; read once 23 Nov 13:38:00 to 13:39:27 IST, `log` 23 Nov 13:39): P = ALL - ZS, pooled out-of-fold crack relF1@2, OP-A, 106 cells, 71 clusters: Delta +0.2213, seed-aware 95% interval [+0.0977, +0.3504] (SE 0.0643); M 0.010; fixed-model interval (the 6 trained models fixed; clusters only) [+0.1066, +0.3390]. G1 false crack px on the 74 crack-free cells: ALL 541 <= 1.5 x ZS 2231 (ratio 0.242), PASS. G2 mIoU-R13 delta +0.1385 >= -0.01, PASS. **P: CONFIRMED.** Verdict line: "T3B VERDICT: P (ALL - ZS pooled out-of-fold crack relF1@2) CONFIRMED; Delta +0.2213 [+0.0977, +0.3504]; width ratio ALL / ZS 1.426 (reported)."
- Printed beside, deciding nothing (E `T3V` l10 to l33): width ratio ALL / ZS 1.426 (ALL 0.631, ZS 0.443; reported, not a guard); strict crack IoU +0.1803 [+0.0929, +0.2606], outside the band; inactive IoU +0.1463 [-0.0525, +0.4829] (reported only); HALF - ZS +0.2042 [+0.0718, +0.3366]; ALL - HALF +0.0171 [-0.0246, +0.0625]; any-hit recall, arm mean over 3 seeds: ALL 0.666, HALF 0.682, ZS 0.400. Strata of ALL - ZS relF1@2 (cells / clusters): full 44 / 24 +0.1525 [+0.0260, +0.4423]; half-cut 62 / 47 +0.2530 [+0.0878, +0.3885]; hard (half-cut + scuff) 29 / 17 +0.3002 [+0.1445, +0.4748]; half-cut without scuff 33 / 31 -0.0701 [-0.3019, +0.0517]; crack cells 32 / 21 +0.1967 [+0.0680, +0.3222]; CSIR 101 / 66 +0.2215 [+0.0977, +0.3415]; BMRK 5 / 5 +0.0000 [+0.0000, +0.0000].
- **Scope and disclosures** (E `T3V` l64 to l72): E1 is training data for the T3b models from the registration of this opening; no later zero-shot claim on E1 by this team; the T3 table (opening #8) is frozen before it. ZS = opening #8's C2 dumps of seeds 5 to 7, re-scored; it never saw an E1 cell. Recipe fixed before any T3b number: no threshold, bias or checkpoint was chosen on E1. Half of E1's crack px sit in 3 image ids, so the pooled score has the uncertainty of about 9 images. Folds are by image id; the out-of-fold number may be optimistic for a truly new site. A T3b model learns the wider E1 label width, which lifts strict IoU and pixel recall without finding more cracks. 3 seeds; all 33 dumps on cv02 (one GPU model), read on gaint CPU; one primary contrast. Inactive: 10 cells in 7 image ids, reported, never decides. Prior looks: #9 is the ninth registered E1 opening, and ZS re-scores the dumps of opening #8 (E `EL`; 3.5).

### 8.4 Severity (T5; appendix only; E `SEV`; `TT` T18; D lead 16 Nov 12:15)
Per-cell output = predicted inactive area fraction a: MAE 0.12 pp over 532 cells, band kappa 0.78, CSIR sensitivity 0.20 (PF, out of fold; not validated on unseen modules or half-cut cells). External sets: Polenghi NULL (rho 0.56 against stage number alone 0.91); ELPVPower NULL by the pre-set rule (rho 0.87 [0.80, 0.91], crack length 0.89); DTU A3 borderline on a subset. "Inactive area predicts power better than crack length": not supported. No watt figure or power band per cell is given.

### 8.5 Deferred or not done
- rank_stability: never run; its deferral condition (at least 8 rows with 2 seeds; D brief 13) is met by the tier 2 rows. Ruling R5.
- Split-variance probe: not run (5.4).
- la_ce_full (owed since 17 Nov 18:00) and the U2 TTA re-run: not run; no new experiments after T3b (D user 22 Nov 11:40).
- E1 numbers for HRNet alone, SWAD alone or HOUSE do not exist; E1 separates the model part from D4, not HRNet from SWAD (E `GAPS` G-N3).
- AUD s5 GPU items (planted-error recall, a cleaned-labels arm, centre-cell training): not run.
- Labelling pack (24 pool half-cut cells with model pre-labels; development reads only, never training; a half-cut crack set, not a scuff set): the user said yes on 15 Nov 12:40, then "Q3 later" on 17 Nov 13:24; not filled; no ruling since (E `v0.2` 8.1; `log` 17 Nov 13:24).

### 8.6 Risks (S)
- Inactive stays under-powered: n_eff 12.9 groups on the pool (E `AUD` F4); 10 inactive cells on E1.
- The E1 claim is near its floor: lower end +0.0013, carried by 44 full cells; the half-cut stratum, the reason E1 is hard, is n.d.
- The crack contrasts rest on few groups (F9): HRNET - PF goes under M after one group.
- C2 is research-only as trained (ELPV cells, 2.4); a model WattCycle can sell needs a retrain without the BMRK cells or the holder's permission (`LIC` D4).
- One team, one dataset family, one GPU model per read; the 2-seed tier sits on the leaky cv5v2 split, read with clean-cell columns.

## 9. Resolution of the ten contradictions listed in v0.2 section 10
| # | v0.2 contradiction | Resolution | Record | Status |
|---|---|---|---|---|
| 1 | cv02 inactive margin 0.049 (A1) vs 0.050 (W1C, ROWS1) | 0.049 = mean over the 15 two-seed splits is the value; 0.050 is one canonical split; gaint keeps 0.054. cv5v3 reads compute their own M (inactive 0.0462 on 532 cells, TTA read) | D lead 15 Nov 16:01 (`v0.2` s11 item 3); `GAPS` G-D6; `TT` T4 | resolved |
| 2 | seeds of a table row: brief 6 vs HO5 L6 | L6 refines "5 seeds" (5.6) | D lead 15 Nov 16:01 (`v0.2` s11 item 1) | resolved as a rule; its application needs ruling R1 |
| 3 | stale statements (README 17 openings; "0 groups cut"; LABELS_V11 header "open") | corrected (`v0.2` s11 item 6); LABELS_V11 header now says decided (E, read 22 Nov). New staleness found 22 Nov (E, read today): `benchmark/README.md` says 18 counted openings (`TL` B: 19), "final tables score 528 cells" (superseded by 416), and lists no cv5v3 or pool_t9_v2 file; `benchmark/splits/README.md` has no cv5v3 entry, and its "cv5v2 0 groups cut" holds for image-id groups only (`SPI` s4: 24 physical modules span folds) | `v0.2` s11 item 6; `TL`; `SPI` | resolved: the new stale lines fixed in both READMEs at the freeze edit, 23 Nov (D lead, `log` 22 Nov 12:49) |
| 4 | pool cells after rules 1 to 3: 6,696 (POOL) vs 6,694 (A6) | not reconciled in any file. S: `pool_t9.README.md` l8 records the tool run that built the list (6,696); A6 l76 states 6,694 as an option of the earlier analysis; the built list's record wins. The list itself is superseded by `pool_t9_v2.txt` (4,949), and no read since 15 Nov names a pool-list arm (S) | `v0.2` s11 item 10 (e) | superseded |
| 5 | SDLE cells 18 (B1) vs 17 (pool) | both counts are right for different sets: 18 SDLE cells in the 582 legacy cells (`BRIEF` s2), 17 in P532 (`v0.2` 2.1; `TT` T1), 1 SDLE image id in test50 (`SPI` 5b); 17 + 1 = 18 (derived). B1 l28 gives 18 for a pool read, where 17 applies | `BRIEF`; `SPI` 5b; B1 l28 | resolved |
| 6 | crack-free 303 (v1) vs 3 cells losing all crack under v1.1 | 303 is the v1.1 count (v1 gives 300); reads define crack-free by the scoring label set; cv5v3 reads: 303 of 532, 226 of 416 | D lead `v0.2` s11 item 5; `log` 15 Nov 17:59; `HRN` s2 | resolved |
| 7 | E1: 67 modules / 58 half-cut (BRIEF) vs 71 image ids / 62 half-cut (draft) | the result files win: 71 image ids = 71 clusters, 62 half-cut, 44 full, CSIR 101, BMRK 5 | `ORULE` s1; `SPI` 5a; `FOR`; `GAPS` G-D3 | resolved |
| 8 | B3 says U2 reproduces SHV1; RB says it does not | it does not: U2 was rebuilt (build_shvoof_v2); its val views differ from SHV1 by at most 98 grey levels with equal masks (a different draw); the rebuilt set passed re-review | `RBF` l24, l30; `v0.2` s11 item 9 | resolved |
| 9 | brief 5 and 12 treat the existence of RB as the end of "pending review" | RB finished 15 Nov 16:07 (OP-C adopted; U2 FAIL then PASS after the fix round 17:59) | `v0.2` s11 items 8, 9; `log` 15 Nov 16:07, 17:59 | resolved |
| 10 | W3 Y1 planned with inactive SE 0.038; A1 measured 0.0245 | no conflict: the measurement supersedes the plan | `v0.2` s10 item 10 | resolved (no action) |

Tally: resolved 9 (one of them, #2, with a follow-on ruling R1; #3 by the freeze edit of the two READMEs), superseded 1 (#4), still open 0.

Disagreements found since v0.2, and how v1.0 reads them (E as cited): test50 "8 pool cells" (`FOR` l61) vs `SPI` 5b, read per `ERR` item 3; TTA (c) verdict words l126 vs l170, both printed (7.1); E1 MDE "about 0.05" vs 0.0742 derived, 0.0742 used (`GAPS` G-N4); `TT` T6 "no interval" for two strict-IoU contrasts vs the read files, read files used (7.1); HRNet and SegFormer stride "n/r" in `TT` T15 vs `RR2` s3 (1 and 4), `RR2` used; T3b seeds 2 (proposal) vs 3, 3 used (D user 21 Nov 15:01); `EL` #8 "4th look" vs verdict.txt l138, l138 used (`ERR` item 5); `HRN` md5 afbfea04 in `log` 18 Nov 06:00 vs 450bf943 now (wording fix 18 Nov 07:06), current file cited. The release README's oracle check (strict crack IoU 0.370 for a 1-px shift, `REL` s5.4) is on fold 0 (107 cells); `log` 22 Nov 12:01's 0.449 is on all 532 cells; both are in benchmark/release_v1/staging/e2e/E2E_RESULT.md (29f4fb4f) items 3 and 5: a set difference, not a conflict. This file's first draft cited `m0core` l45 to l47 for the distance rule; the lines are l47 to l49.

## 10. Status of the ten Open items of v0.2
| # | Item | Status | Record |
|---|---|---|---|
| 1 | OP-C | **closed**: adopted 15 Nov 16:07 as comparator for prior-shifting arms (decision layer); the one wider-grid variant failed its rule (bias at the new edge in 14 of 20 fits; inactive precision -0.0420 against the limit -0.0401); OP-C stays variant 1, ledger count 2 | `v0.2` s11 items 8, 9; `log` 15 Nov 17:59 |
| 2 | U-dev | **closed**: U1 rule fixed before LOSO-2, read: guard, not primary; U2 rebuilt, passed, read descriptive; U3 not built (F51 descriptive only); U4, U5 descriptive | `U1`; `U2U4`; `RBF`; `log` 19 Nov 01:24 |
| 3 | E1 opening | **closed**: user approved 21 Nov 00:22 ("Yes, this is it"); rule reviewed PASS; registered 21 Nov 11:22; opened 11:25 to 12:06; CONFIRMED; label set and strata in `ORULE` s3, s5 | `ORULE`; `FOR`; `EL` #8 |
| 4 | T3b | **closed** as a ruling: after the opening, own track, trained_on_e1 (D lead 15 Nov 16:01); run approved by the user 21 Nov 14:35, 3 seeds 15:01; registered as E1 #9 22 Nov 03:13; opened 23 Nov: P CONFIRMED, +0.2213 [+0.0977, +0.3504] (8.3) | `v0.2` s11 item 2; `T3R`; `EL` #9; `T3V` |
| 5 | 528-cell scoring | **superseded**: score-exclude option built; the clean set became 433, then 416 cells | `v0.2` s11 items 9 to 11; `GAPS` G-N8 |
| 6 | Seeds of a table row | **needs a ruling** (R1): L6 stands, but closed 2-seed rows that L6 sends to 5 seeds will not be run (no new experiments) | `v0.2` s11 item 1; D user 22 Nov 11:40 |
| 7 | Tracks without a ruling | **closed**: T2 and latency not part of v0.2 (lead); LOSO = U1 (done); split-variance probe deferred with the stated caveat. v1.0: T2 stays out (no new experiments); latency measured for the E1 candidates only, CPU and GPU (`IC` s3.3, s3.4); that scope ruled by the lead (`log` 22 Nov 12:49; section 11) | `v0.2` s11 item 4; D user 22 Nov 11:40; `log` 22 Nov 11:30, 12:49 |
| 8 | Release and terms | **release ruled**: lists and code only, public repository, MIT code and CC BY 4.0 lists and results; the list of cleared data and weights that Open 8 asked for is `LIC` s2 to s5; **"clear terms" (R2) and `LIC` D3 to D6 (R8) need rulings** | D user 22 Nov 11:40, 12:08; `LIC`; `v0.2` s11 item 7 |
| 9 | Governance pieces | **closed**: checklist (s12), info sheet template and C2 example (`IST`), scoring procedure (12.3, citing `REL`), errata rule, audit rewrite of s1 (from `AUD`); "with and without noisy cells" done on test50 (all 50, clean 49) and by the clean-cell columns on CV5 (leakage-flagged cells, not noise; the 2 noisy pool images of `AUD` F10 are excluded nowhere); related-work table written (`RW`, 22 Nov); G17, G19, G20 made protocol text (6.6 item 7; D lead 22 Nov 12:49) | `FOR`; `AUD` F10; `W3` s6; `log` 22 Nov 12:49 |
| 10 | Deferred analyses | **t5_post_eval and severity_external_elpvpower closed** (severity track done 16 Nov, appendix; downloads approved by the user 15 Nov); **rank_stability needs a ruling** (R5): not run, condition met | `SEV`; `S0` l3; `log` 16 Nov 12:15 |

Tally: closed 6 (#1, 2, 3, 4, 7, 9; #4 with its result in 8.3), superseded 1 (#5), needed a user ruling 2 (#6, R1; #8, R2 and R8; ruled 22 Nov, section 11), partly closed 1 (#10: rank_stability not run; R5 ruled 22 Nov).

## 11. Rulings (decided by the user, 22 Nov 2026)
The user, 22 Nov 12:49: "all as recommended, D3 = a, run the HOUSE read" (D user; `log` 22 Nov 12:49). Each ruling below uses that entry's wording. R1 to R6 come from the first draft; R7 to R10 were added after review round 1 (`RVP` B3). Options are listed short; the full option text, the writer's recommendations and reasons are in the pre-freeze version of this file (eeb3379a) and in `RVP` B3, R2-B1.

| # | Question | Options (short) | Ruled (D user 22 Nov 12:49) |
|---|---|---|---|
| R1 | Seeds per table row (Open 6): the closed 2-seed rows that L6 would send to 5 seeds (unet_r34_pf, hanifi_vgg16_unet_pf, dlv3p_r34_pf, skr01_pf_v11, segformer_mitb2_pf) | (a) a separate 2-seed screen tier; (b) run the five rows to 5 seeds (new runs); (c) drop them | (a) 2-seed rows as a separate screen tier |
| R2 | What "clear terms" means for the main track (Open 8) | (a) research use as found, with a commercial-use column; (b) an explicit licence only (no current row qualifies); (c) a main track without ELPV cells (new runs) | (a) research-use terms with a commercial column, C2 "research-only as trained" |
| R3 | Reference of the false-crack-pixel guard for later entries (`HRN` s4) | (a) 1.5 x the comparator, frozen; (b) an absolute bound per crack-free cell; (c) HOUSE as the reference | (a) false-px guard 1.5 x frozen, per-cell false px printed beside |
| R4 | Scoring unit (`AUD` s5 question 2) | (a) the image window; (b) the centre cell | (a) image window |
| R5 | Ranking with ties (checklist item 10) | (a) no ranks; (b) rank intervals from rank_stability; (c) point ranks | (a) no ranks, "not separated from PF" |
| R6 | When is v1.0 frozen? | (a) after the listed conditions; (b) now, with PENDING marked | (a) freeze after the listed conditions |
| R7 | Entry class of a fixed-view TTA, and G16's comparator (6.1, 6.4; `RVP` B1) | (a) keep v0.2: TTA is class (c), disclose C2's comparator gap; (b) class (a) includes a fixed TTA, future entries only; (c) a FLOP-matched PF comparator for future entries above 2 x | (a) C2 class (c) with the comparator gap disclosed + (c) FLOP-matched PF comparator for future entries above 2 x |
| R8 | Release decisions left open in `LIC` s7 (the user, 22 Nov 12:08: "dont worry about any permissions atleast for now, publish them all"; D2 ruled then) | D3 approval: (a) none needed for v1, (b) ask the mentor and WattCycle; D4 commercial use: (a) none on BMRK cells or MiT-B2, (b) seek ZAE Bayern's permission, (c) retrain without BMRK; D5: (a) scoring code only, (b) training code too; PF records: (a) release, (b) aggregates only | D3 (a) no mentor / WattCycle approval needed for v1, D4 (a) no commercial model on BMRK cells or MiT-B2, D5 (a) scoring code only, PF records (a) release PF pool out-of-fold per-cell records |
| R9 | Report the 18 spurious-inactive cells with and without (`AUD` s5 question 3) | (a) as labelled only; (b) with and without | (a) report the 18 spurious-inactive cells as labelled only |
| R10 | E1 for outside entries | (a) outsiders report E1 levels, with a self-declared line in a public ledger; (b) outsiders send dumps and the team runs the contrast; (c) not offered | (a) outsiders report E1 levels with a self-declared ledger line, once a tested E1 label builder is in the release (after the T3b read) |

**R6 conditions at the freeze, 23 Nov:** the T3b result written into 8.3 (`T3V`); GPU latency in 6.4 (`IC` s3.4); the md5 of `RW` pinned (f2a6adcd, header); the review closed (`RVP` 797e63bb: round 2 FIX with three one-sentence edits, which the reviewer said a lead's diff check would close; closed by that check, `log` 22 Nov 12:39); the lead's word on G17, G19, G20 and on the items below (`log` 22 Nov 12:49); R1 to R5 and R7 to R10 ruled (table).

Lead items, accepted with the user's rulings (D lead, `log` 22 Nov 12:49):
- G17, G19, G20 are protocol text (6.6 item 7).
- The three duties the draft marked "proposed" are protocol text: the 2.3 implications, the 5.5 robustness duty, and the carrying-groups clause of checklist item 9 (12.1).
- Latency scope = the E1 candidates (6.4; `IC`), not every row as `v0.2` s11 item 4 said.
- HOUSE rule kept; CS_D4 - HOUSE and CS - HOUSE read from existing dumps (7.1; `HCS`). No HOUSE_D4 dumps exist, so the 8-view against single-view asymmetry is a recorded limitation (no new runs, D user 22 Nov 11:40).
- The stale lines of `benchmark/README.md` and `benchmark/splits/README.md` fixed (s9 #3).

Pointers elsewhere in this file and in `IST` that date from before 22 Nov 12:49 ("ruling Rn", "needs a ruling", "R1 open", "to rule", "pending R2", "pending R7") are answered by the rulings recorded here.

## 12. Reporting checklist, info sheet, scoring a new model (Open 9)
### 12.1 The 10-item reporting checklist (fill-in; the C2 column is the worked example)
| # | Item | What the entry states | C2 (the final model) | Record for C2 |
|---|---|---|---|---|
| 1 | Release and label set | dataset release; training and scoring label sets with manifest md5 | BenchmarkEL 20211104, P532; trained and CV5-scored on v1.1 (masks_v11 MANIFEST 9c0e0687); E1 scored on ext117 (release 20221008) with ignore; test50 on v0 and v1.1 | `ORULE` s3; `FRULE` s1 |
| 2 | Split and grouping | split file md5; groups; clean-cell list; sealed sets with cluster counts | CV5: cv5v3 (7a700b00), 285 groups (d880a769), clean list score_exclude_v3 (6d48dfbd, 416 cells); full-pool model on all 532; E1 71 clusters; test50 48 clusters | `CV3`; `FRULE` s3; `ORULE` s1 |
| 3 | Class list and absent-class rule | output classes with ids; balance metric; how absent classes are scored | 24 classes (ids in 12.3); mIoU-R13; absent class never 0 or 1 | sections 4, 12.3 |
| 4 | Metric definitions | headline; tolerance; distance convention; deciding vs printed metrics | relF1@2 decides; 2 px, Euclidean distance transform per image, inclusive, counts pooled; strict IoU with band +-0.019, decides nothing | sections 5.1, 12.3; `m0core` |
| 5 | Operating point | rule; any bias or threshold and where it was fitted | OP-A, argmax of log(p + 1e-12) over 24 classes; no bias, threshold or view weight | `ORULE` s2 |
| 6 | Seeds and machine | seeds; GPU model; precision; where the read ran | seeds 5 to 9; cv02 RTX A6000, fp32, TF32 off; reads on gaint CPU | `FRULE` s1; `FOR` run record |
| 7 | Interval method | bootstrap units, draws, seed handling; margin | CV5 two-stage group bootstrap, 2,000 draws, seeds unpaired, M 0.010; E1 seed-aware two-stage bootstrap (71 clusters x 5 models), 2,000 draws, M 0.010 | `FRULE` s2; `ORULE` s4 |
| 8 | Contrasts and openings | primary contrast; contrasts read; set openings, with prior looks; entry class with its equal-cost comparator | one primary on E1 (C2 - C1); E1 opening #8 after 7 registered openings (3 looks at one contrast), pre-policy reads and R0; test50 #19 after 18 counted openings; class (c) by views, no equal-cost comparator printed (6.4) | `FOR`; `ERR` item 5; `TL`; `EL`; `RVO` N4 |
| 9 | With and without flagged cells | values with and without noisy or leakage-flagged cells; strata; groups that carry the gain (protocol text, D lead 22 Nov 12:49) | CV5 on 532 and 416; test50 on 50, clean 49, 16 unlinked; E1 all 106 with strata (CSIR / BMRK, full / half-cut, crack cells); carrying groups: computed for COMBO (k_0 31), not for CS_D4 | `TTA`; `FOR`; `AUD` s2 |
| 10 | Ranking with ties | rank and tie rule | no rank; ruling R5 | section 11 |

### 12.2 Model info sheet
- Template: `IST` section 1 (fields A to J: identity, data and split, training, inference and operating point, cost, leakage and provenance declarations G13 to G16, selection and multiplicity, results, artefact md5s, deviations).
- Worked example: `IST` section 2, filled for C2 with numbers copied from the result files.

### 12.3 Scoring a new model
The procedure is the release README `REL` (690dac25) s3 to s6: data layout, the v1.1 rebuild and its pixel-md5 check, the cv5v3 folds, the dump format (`bench/dumpfmt.py`), per-run records (`bench_score.py`) and the protocol read (`bench_read_w1.py`). This section adds what an entry also needs. Items marked PENDING cannot yet be done by an outsider.
1. **Rules for the entrant's own runs** (E `REL` s5.1; sections 5.3, 6.4, 6.5): one model per cv5v3 fold, trained on that fold's `train` list, predicting its held-out cells in list order; final-step weights or a readout fixed in the card, no best-validation checkpoint; unlabelled data only from `pool_t9_v2.txt`; no stem of `forbidden_v1.txt` in any training list (167 stems: test50, the 106 E1 cells and 11 more cells of release 20221008); seeds 2 for a screen, 5 for a table row; the fairness record (6.4) and an info sheet (`IST`).
2. **Class ids** (E release code `bench/cv5v3.py` CLASS_NAMES, md5 14b71c95; 255 = ignore, not scored): 0 background, 1 sp_multi, 2 sp_mono, 3 sp_dogbone, 4 ribbons, 5 border, 6 text, 7 padding, 8 clamp, 9 busbars, 10 crack_rbn_edge, 11 inactive, 12 rings, 13 material, 14 crack, 15 gridline, 16 splice, 17 dead_cell, 18 corrosion, 19 belt_mark, 20 edge_dark, 21 frame_edge, 22 jbox, 23 meas_artifact. mIoU-R13 ids: 0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21 (E release code `bench/classbias.py` l35, md5 5e0dc317).
3. **Labels:** v1.1 is rebuilt from public masks by `make_masks_v11.py` and checked against the release's pixel-md5 manifest (E `REL` s4); definitions of v1 and v1.1 in 2.2 (E `LAB` s1).
4. **Distances and components** (E `m0core` l12, l15 to l36, l47 to l49, l93 to l107):
   - relP@2 counts predicted crack px whose Euclidean distance to the nearest ground-truth crack px is <= 2.0 px (inclusive); relR@2 the reverse; the distance transform runs per image, ignore px are excluded, counts are pooled over the scored cells.
   - Components are 8-connected. A ground-truth crack component of >= 20 px is "found" if >= 50% of its px lie within 2 px of a predicted crack px, and an "any-hit" if at least 1 px does. A predicted crack component of >= 20 px counts as correct if any of its px lies within 2 px of ground-truth crack.
   - An inactive region of >= 100 px is found if >= 50% of its px are covered by predicted inactive px (overlap, no tolerance); a predicted inactive region of >= 100 px counts as correct if it overlaps ground truth.
   - A crack-free cell has no ground-truth crack px under the scoring label set (`v0.2` s11 item 5).
5. **Clusters for the sealed bootstrap** (E `ORULE` s1): the source image, that is the stem without its cell suffix; SDLE stems end in `-cell<n>`. 71 clusters on E1, 48 on test50.
6. **Comparator records and margin.** A paired contrast needs the PF baseline's per-fold dumps from the same machine and PF's own A/A ({5,6} v {7,8}) for M (5.4; a read never mixes machines). The release ships no PF dumps, no per-cell PF records and no training code (E `REL` s2; `LIC` s7 D5); `results/BASELINES.md` holds aggregates only (E `REL` s2, s7; `LIC` s3). Today an outside entrant can compare levels with those aggregates, not run a paired contrast against PF. Ways out: release PF's pool out-of-fold per-cell records, or release a PF card with training code so the entrant can retrain PF on their own machine (ruling R8).
7. **E1 label view: PENDING.** The rule is fixed (2.2: release 20221008 masks, class 24 to 2, classes 25 to 28 to ignore, with the ignore file), but `ext117/ignore` is a project file and the release has no builder (E `REL` s7; `LIC` s7 D6). A builder must be written and tested by someone cleared to read E1 masks; that waits for the T3b read and ruling R10. No E1 mask was read for this file.
8. **E1 contrasts for outside entries:** C1's per-cell E1 records are not released (E `LIC` s5), so an outsider cannot compute the seed-aware contrast against C1; only levels are comparable, against the E1 aggregates in `results/BASELINES.md` (tables T8, T10, T11a; E `LIC` s7, last paragraph). Ruling R10.
9. **Report** (E `REL` s6): 532 and 416 cells side by side; never mix machines in one read; the entry class with its equal-cost comparator; the checklist (12.1) and the info sheet.

## 13. Items PENDING before the freeze, and their state at the freeze
| Item | Where in this file | Source | State at the freeze, 23 Nov |
|---|---|---|---|
| T3b result (E1 opening #9) (done) | 8.3; 0 line 12; 3.5; 6.3; 10 #4 | `T3V` | filled from `T3V` (bfe583db): opened 23 Nov, read once 13:38:00 to 13:39:27; P CONFIRMED (`log` 23 Nov 13:39) |
| GPU latency per cell (done) | 6.4; 6.3 T4; `IST` E5 | `IC` s3.4 | filled from `IC` (1e5a9002): one cv02 RTX A6000, fp32, measured 22 Nov 17:50 to 18:04 IST |
| E1 label builder for outside entries (open; not an R6 condition) | 12.3 item 7; R10 | a tested builder in the release (`LIC` D6) | R10 (a) ruled 22 Nov; no builder in the release (`REL` 690dac25; commit 36fdcdc); none logged; no E1 mask read here |
| Related-work table (done) | 1 | `RW` | pinned (f2a6adcd, checked 23 Nov) |
| HOUSE - PF intervals (done) | 7.1 | `HPF` | filled from `HPF` (71e5a382) |
| HOUSE rule on the C2 recipe (done) | 7.1 | `HCS` | filled from `HCS` (9efd43ac); no HOUSE_D4 dumps: a recorded limitation |

## 14. Change log, v0.2 to v1.0
| # | Topic | v0.2 (15 Nov) | v1.0 (22 Nov) | Why, record |
|---|---|---|---|---|
| 1 | Split of record | cv5v2; 528 cells planned | cv5v3 (285 groups) for every 5-seed row; cv5v2 for screens only | module audit, D lead 15 Nov 22:14, 16 Nov 00:39; `SPI`; `CV3` |
| 2 | Scored cells | 532 (528 planned) | 532 and 416 clean, both decide | D lead 16 Nov 00:39; `FRULE` s3 |
| 3 | Headline | relF1@2 first, strict IoU beside | relF1@2 decides every crack contrast; strict IoU only with its band | D user 21 Nov 00:22 |
| 4 | Strict IoU band | level band 0.48 to 0.60 | convention band +-0.019 on contrasts | `AUD` F1; `FRULE` s2; `GAPS` G-D7 |
| 5 | Guards | width band, printed false-alarm and component guards | five guards at four values for confirmations; G1 to G4 on E1; G1, G2 on T3b | `FRULE` s2; `ORULE` s4; `T3R` s8 |
| 6 | OP-C | pending review | adopted, variant 1 | `v0.2` s11 items 8, 9 |
| 7 | Verdict words | screen pass or fail | CONFIRMED / GAIN, FAILING GUARDS NAMED / NOT CONFIRMED (NO LOSS, LOSS); "selection-biased" label | `FRULE` s0, s2; `ORULE` s4 |
| 8 | Statistics | CV5 two-stage bootstrap | plus the seed-aware cluster bootstrap for sealed sets, M 0.010 fixed there; E1 MDE derived | `ORULE` s4; `TT` T4 |
| 9 | Seeds | 2 / 5; L6 open | L6 ruled; final models 5 seeds; T3b 3 seeds; R1 open | `v0.2` s11 item 1; D user 21 Nov 15:01 |
| 10 | Leakage | pool_t9 (6,424); 2 duplicate cells | pool_t9_v2 (4,949); module identity over 700 image ids; leakage read "not separated"; E1 "supported, not proven" | `v0.2` s11 item 10; `LEAK`; `SPI` |
| 11 | Legacy test50 | 18 openings, none planned | 19; #19 public table only, on v0 and v1.1 | D user 21 Nov 00:22; `TL`; `FOR` |
| 12 | E1 | one opening proposed | #8 opened, CONFIRMED; #9 T3b opened 23 Nov, CONFIRMED; E1 training data for T3b from 22 Nov | `FOR`; `EL`; `T3V` |
| 13 | Baselines | 7 rows, cv02, cv5v2 | cv5v3 5-seed tier; cv5v2 screen tier; final models C1 to C3 on E1 and test50 | section 7 |
| 14 | Unseen-module instruments | U1 to U5 pending review | U1 a guard; U2 descriptive; U3 not built | `U1`; `U2U4` |
| 15 | Dataset faults | none | audit F1 to F11 with AI-rater check | `AUD`; `RAT` |
| 16 | Severity | deferred | appendix only; null on power | `SEV`; D lead 16 Nov 12:15 |
| 17 | Release | no ruling | lists and code only; public repository, MIT code and CC BY 4.0 lists and results; staged locally as commit 36fdcdc; URL to be added at publication | D user 22 Nov 11:40, 12:08; `REL` |
| 18 | Governance | four pieces listed | checklist table with C2 example; info sheet template and C2 sheet; errata rule; scoped wording; related-work table cited | sections 1, 6.6, 12; `IST`; `ERR`; `RW` |
| 19 | Cost | step time and GFLOPs per row | plus per-cell GFLOPs, CPU and GPU latency and observed wall time for the E1 candidates | `IC` |
| 20 | Public comparison | none | test50 #19 public table on v0 (context only) | `FOR`; `PUB` |
| 21 | Contradictions and Open items | 10 and 10 listed | each resolved or ruled (sections 9, 10); ten user rulings, decided 22 Nov (section 11) | this file; `log` 22 Nov 12:49 |
| 22 | Entry classes | (a) one forward pass; (c) models or views | unchanged; the first draft's "(a) includes a fixed TTA" is withdrawn and proposed as R7; C2 is class (c) with no equal-cost comparator | `RVP` B1; `RVO` N4 |
| 23 | Licences and tracks | ELPV "unverified"; no data or weight list | ELPV CC BY-NC-SA 4.0 verified; C2 research-only as trained; SegFormer MiT-B2 research-only; `LIC` is the cleared list | `LIC`; `RR2` |
| 24 | relF1@1, @2, @3 printed together | in force | @3 dropped (D lead, 22 Nov): it decides nothing and no read used it; the CV5 read tool prints @1 and @2 only | `results/final_tta_read/read.txt`; D lead 22 Nov |
| 25 | HOUSE rule | in force | carried and kept (D lead 22 Nov 12:49); applied to HRNet and to the C2 recipe (CS_D4 - HOUSE, CS - HOUSE; no HOUSE_D4 dumps, so 8 views against 1: a recorded limitation); HOUSE - PF intervals added | `W1C` s3; `HPF`; `HCS` |
| 26 | Scoring by third parties | not covered | section 12.3, citing the release README; E1 label builder PENDING; PF records and E1 for outsiders to rule (R8, R10) | `REL`; `LIC` |
| 27 | Items carried from v0.2 that the first draft left out | | v1 definition, label issues 3 to 8, clean 42, sealed-row columns, stride ceiling rule, labelling pack, screen error rate, MDEs of all four metrics | `RVP` B5 |
