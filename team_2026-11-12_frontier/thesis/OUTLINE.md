# Thesis outline and writing plan (MTP, EL defect segmentation, 24 classes; thesis_outline, 22 Nov 2026)

Scope: a chapter-by-chapter plan that maps every section to the files, tables and numbers that fill it. Writing starts 24 Nov.
Only result text files were read (no E1 or test50 label, mask, image or prediction). Nothing here is a new number: every value is
copied from the cited line. Status words: **ready** (source exists and is final), **pending (input)** (named input not yet on disk),
**gap (id)** (no file states it; ids G-* from `thesis/GAPS.md`, ids O* new in this file, section 6).

## 0. How to use this file
- **Short paths** (relative to T = `~/mtp/research/team_2026-11-12_frontier/`; md5 prefix as read 22 Nov, section 8):
  TT = `thesis/THESIS_TABLES.md`; GP = `thesis/GAPS.md`; BR = `BRIEF.md`; P02 = `benchmark/PROTOCOL_v0.2.md`;
  P10 = `benchmark/PROTOCOL_v1.0.md` (pending); AUD = `dataset_audit/REPORT.md`; SI = `results/stageC/SPLIT_INTEGRITY.md`;
  FOR = `results/FINAL_OPENING_READ.md`; ER = `results/FINAL_OPENING_READ_ERRATA.md` (its wording wins over FOR);
  V8 = `results/final_opening_read/verdict.txt`; R8 = `results/final_opening_read/read_e1/read.txt`;
  FTR = `results/FINAL_TTA_READ.md`; VT = `results/final_tta_read/verdict.txt`; RT = `results/final_tta_read/read.txt`;
  HR = `results/C3HRNET_READ.md`; SW = `results/C3SWAD_READ.md`; CX = `results/C3X_READ.md`; LK = `results/C3_LEAK_READ.md`;
  U1 = `results/U1_READ.md`; R1 = `results/ROWS1_READ.md`; R2 = `results/ROWS2_READ.md`; SEV = `results/severity/SEVERITY_SUMMARY.md`;
  T3R = `harness/t3b/T3B_RULE.md`; T3P = `benchmark/T3B_PROPOSAL.md`; IC = `thesis/INFERENCE_COST.md` (in progress);
  RW = `thesis/RELATED_WORK.md` (pending); HP = `results/HOUSEPF_READ.md` (pending); LOG = `log.md`; ML = `cards/ledger/MASTER.tsv`;
  H02, H11, H20, H22 = `~/mtp/research/handbook/02_...`, `11_...`, `20_...`, `22_...`.
- **Table ids** are the TT ids (T1 to T21). In the thesis they get chapter numbers (Table 6.1 and so on); see O2 on the "T3b" clash.
- **Rules for every chapter writer.**
  1. Copy numbers from TT (or `thesis/thesis_tables.tex`); each value is traced in `thesis/SOURCES.tsv`. Never retype from memory.
  2. Use the ER wording wherever FOR lines 61, 66 to 67, 69 to 70, 47 or 76 would be quoted (section 3 of this file).
  3. Every E1 sentence carries its scope: recipe averaged over seeds 5 to 9; OP-A only; 101 of 106 cells CSIR; full cells carry it.
  4. Every test50 sentence carries "in-distribution, known leakage, context only".
  5. "Decides nothing" items (strict crack IoU, strata, printed-beside contrasts, inactive IoU) never carry a claim sentence alone.
  6. Style: terse, plain English, no em-dashes, measurements over adjectives; judgement sentences are worded as judgement.

## 1. Chapter list and page budget

Changes from the lead's example order (S):
- **Data and the audit come before the protocol**, because the audit's findings (F1 convention band, split integrity, release effect)
  are the reasons for the protocol's rules.
- **"Methods tried" is split in two**: the legacy-split work before 12 Nov (SSL era, PF, Skeleton Recall, E1 openings #1 to #7) is a
  short history chapter placed before the protocol, since its measurement failures motivate the protocol; the screens and 5-seed rows
  under the protocol (wave screens, HRNet, SWAD, TTA) form the methods chapter after it.
- **Severity and cost** are one "towards deployment" chapter.
- **The claims table T20** closes the thesis (chapter 12).

| Ch | Title | Main tables (TT) | Appendix tables | Pages |
|---|---|---|---|---|
| front | Title, certificate, declaration, acknowledgements, abstract, contents, lists, abbreviations (TT l18 to l23) | | | 8 (roman) |
| 1 | Introduction | | | 5 |
| 2 | Background: EL imaging, defect classes, crack label physics | | | 6 |
| 3 | Related work and why published numbers do not compare | (RW table, pending) | T13a | 6 |
| 4 | Data, labels and the dataset audit | | T1, T2, T3a, T3b, T3c, T19a, T19b | 8 |
| 5 | Before the protocol: the legacy-split work (10 Oct to 14 Nov) | | T17, T21 | 5 |
| 6 | The benchmark protocol | T4 | (P10 summary, info sheet) | 7 |
| 7 | Baselines and methods under the protocol | T6, T7a, T16b | T5, T7b, T15, T16a | 9 |
| 8 | Final model and the sealed E1 result | T8, T9, T10 | T11a, T11b, T12a, T12b, T13b, T13c, T14 | 8 |
| 9 | Few-shot layout adaptation (track T3b, E1 opening #9) | (T3b verdict, pending) | | 3 |
| 10 | Towards deployment: severity and inference cost | | T18 | 4 |
| 11 | Limitations and threats to validity | | | 2 |
| 12 | Conclusion and future work | T20 | | 2 |
| | **Main body** | | | **65** |
| | References | | | 5 |
| | Appendices A to E (section 2, "Appendices") | | | 14 |
| | **Total (arabic pages)** | | | **84** |

Typical IIT MTP thesis: 60 to 90 arabic pages; no IIT Mandi template or page rule was found on disk (O7). If the guide sets a lower
limit, cut appendices C and D first (the tables stay in the repository and in `thesis_tables.tex`).

## 2. Per chapter: sections, claims, sources, tables, status

### Front matter and abstract (1 p abstract)
| Claim | Source (file:line) | Table | Status |
|---|---|---|---|
| On E1 (106 cells, 71 clusters; unseen modules "supported, not proven"), the final recipe C2 averaged over seeds 5 to 9 beats full-pool PF (C1) on crack relF1@2: +0.0430 [+0.0013, +0.1043], guards G1 to G4 pass, CONFIRMED; OP-A only; full cells carry it, half-cut n.d.; 101 of 106 cells CSIR; prior looks as V8 l138; MDE about 0.074 (derived) | V8 l11, l138, l140; ER l26 to l29; GP l66 to l69 (D item 2); SI l200 | T8, T10, T20 #1 | ready |
| A benchmark protocol: corrected split cv5v3 (285 groups, none spans folds), relF1@2 decides, strict IoU only with its convention band, pre-registered reads | P02 l7 to l19, l263; LOG l224; P10 | T4 | pending (P10) |
| The label release and the line-width convention move absolute levels more than any method; relF1@2 contrasts survive them | AUD l23 to l36, l98, l159 to l162 | T3c, T19a, T19b | ready |
| Few-shot result | T3b verdict | | pending (T3b, G-N13) |

### Chapter 1. Introduction (5 pp)
| § | Claim | Source (file:line) | Table | Status |
|---|---|---|---|---|
| 1.1 Setting | Pixel segmentation of EL cell images, 24 classes, crack and inactive the focus; for WattCycle's PV recycling and inspection | BR l9, l16 to l23 | | ready |
| 1.1 | EL work at WattCycle has no rig yet (2 to 3 months away as of 4 Nov), so the model is built on public data | SEV l64; BR l30 | | ready |
| 1.2 Goal | The user's goal, quoted: "highest scores, a model which captures almost all of the cracks, inactive and other important defects balancing the miou for other classes as well" | BR l7 | | ready |
| 1.2 | The operational target "almost all cracks" = relR@2 >= 0.90 at relP@2 >= 0.90 was **not reached**: CV5 C2 recipe (CS_D4, OP-A, selection-biased) relP@2 0.9216 / relR@2 0.8211; E1 C2 0.5995 / 0.4157 | BR l57; RT l14; R8 l7 (T11a) | T11a | CV5 part: gap O1; E1 part: ready |
| 1.3 Why a benchmark | Published EL numbers cannot be compared: three releases of one dataset with reshuffled splits, test cells that are train cells, different class lists and metrics, strict IoU on 1 to 2 px labels, single runs without intervals | P02 l21 to l23; BR l11 | T13a | ready; paper counts per problem pending (RW; G-N10) |
| 1.4 Contributions | (i) protocol and corrected split; (ii) dataset audit; (iii) a method suite under one protocol; (iv) one pre-registered sealed test, CONFIRMED; (v) few-shot track; (vi) severity checks, null on power | T20 #1, #8, #14, #17 to #19, #21 | T20 | ready except (v): pending (T3b) |
| 1.5 | Thesis map | this file, section 1 | | ready |

### Chapter 2. Background (6 pp)
| § | Claim | Source (file:line) | Table | Status |
|---|---|---|---|---|
| 2.1 EL imaging | Why EL is used, what an EL image shows, cell and module anatomy (general background, cite primary sources) | H02 l32 to l79 | | ready (citations via RW) |
| 2.2 Classes and sources | 24 classes (12 structural, 12 defects); 5 sources with different contrast and label conventions: ARTS 195, CFVS 187, CSIR 122, BMRK 60, SDLE 18 | BR l20, l23; H02 l99 to l151, l257 to l282 | | ready |
| 2.3 Crack label physics | Physical crack micrometres wide; camera shows a dark line about 4 px FWHM; labels 1 to 2 px (median 1.75), half the label points more than 1 px from the ridge; width by source ARTS 1.5 to SDLE 3.25 | BR l33 to l34 | | ready |
| 2.3 | A perfect mask shifted 1 px scores crack IoU 0.56 on legacy test (0.43 diagonal); on the pool v1.1 labels 0.483 (1 px), 0.249 (2 px); two annotations agree at IoU 0.21 to 0.26, 0.82 to 0.99 within 2 px | BR l35; AUD l26 to l27 | T19a | ready (name the set with each number) |
| 2.3 | 76 to 88% of crack components are under 20 px; 70% of the best model's crack IoU loss lies within 2 px of ground truth | BR l36, l38 | | ready |
| 2.4 Inactive | Blobby and well labelled (1 px shift IoU 0.94), rare (42 of 478 train cells), never without a crack (99% touch a crack label) | BR l22, l37; H02 l233 | | ready |
| 2.5 Metrics primer | IoU, mIoU over present classes, tolerance metrics relP@2 / relR@2 / relF1@2 defined | P02 l75 to l80 | | ready |
| 2.6 Severity context | Inactive area and power loss; thermal sees inactive area and hot spots, not thin cracks | H02 l283 to l296; H22 l59 to l80 | | ready |

### Chapter 3. Related work and why published numbers do not compare (6 pp)
| § | Claim | Source (file:line) | Table | Status |
|---|---|---|---|---|
| 3.1 EL datasets | BenchmarkEL releases (582 / 642 / 695 cells; 186 of 582 change split between the first two), E-SCDD, UCF-EL (heavy train / test leakage), ELPV, PVEL-AD, MultiSolSegment, PVEL-S | P02 l22; BR l27 to l29 | | ready; per-dataset table pending (RW) |
| 3.2 Published numbers | The four published rows we can relate to test50 (Pratt 2023, SEiPV-Net, PV-S3) and why each is not comparable (rule inferred, averaging undefined, split not stated); four more papers use test sets that overlap our pool | V8 l87 to l92 | T13a | ready |
| 3.2 | Related-work table: every published EL number with release, split, convention, interval | RW | (RW table) | pending (RW; G-N10) |
| 3.3 Methods in our suite | Origins of each arm, with verified ids: SWAD arxiv:2102.08604; SegFormer arxiv:2105.15203; RCS from DAFormer doi:10.1109/cvpr52688.2022.00969; JML doi:10.52202/075280-3289; EMA arxiv:2411.18704; encoder_spd arxiv:2411.01713; GIN-IPA arxiv:2111.12525 | ML (columns paper_id, arm) | | ready for these; HRNet, U-Net++, Skeleton Recall, D4 TTA, DeepLabV3+: gap O5 |
| 3.4 Label noise and benchmark practice | Confident learning, test-set label errors that reorder benchmarks, annotation noise as an upper bound, near-duplicates between train and test (abstracts and one method section read; say so) | AUD l14 to l19 | | ready |
| 3.5 SSL context (why the framing was dropped) | With all labels, extra unlabelled data adds little in the literature; here SSL helped at 5% only | team_2026-10-27_unlabelled/SYNTHESIS.md l7 to l13 | T21 | ready |

### Chapter 4. Data, labels and the dataset audit (8 pp)
| § | Claim | Source (file:line) | Table | Status |
|---|---|---|---|---|
| 4.1 Corpus and sets | 816 real labelled cells, 787 physical, 463 module groups; pool P532 (ARTS 182, BMRK 50, CFVS 169, CSIR 114, SDLE 17); sealed test50 and E1 (106 cells, 71 image ids, 62 half-cut, pool has 0 half-cut); 167 forbidden stems | P02 l29, l33; TT l73 to l91 | T1 | ready (use 71 / 62, not BR l25's 67 / 58: G-D3) |
| 4.2 Label sets | v0, v1, v1.1 (scuff and star to ignore; one BMRK mask restored) and the E1 set; v1.1 changes 16 train cells | P02 l38 to l43; TT l110 to l135 | T3a, T3b (rename, O2) | ready |
| 4.2 | Training on v1 instead of v1.1 changes no pooled metric at 2 seeds (relF1@2 -0.0014 [-0.0099, +0.0064]); the release 20211104 against v1.1 moves PF strict IoU 0.320 to 0.365 and relF1@2 0.822 to 0.846 on the same 25 models | TT l137 to l147; AUD l98 | T3c, T20 #19, #20 | ready |
| 4.3 Split integrity | cv5v2 held a module leak (24 modules span two folds, 91 cells); cv5v3 fixes it at the split (285 groups, none spans folds); the leak read is "not separated" (every interval holds 0) | SI l131 to l188; P02 l262 to l263; LK l11 to l21 | T2, T20 #15 | ready |
| 4.3 | E1: no module or cell of the pool found on the pixels on disk; "unseen modules" is supported, not proven. test50: 8 cells are the same physical cell as a pool cell (7 by pixels, 1 by the cells.tsv link only), 7 neighbouring crops, 19 share a module | SI l191 to l213, l200; ER l18 to l21 | T2 | ready |
| 4.4 F1 convention | Strict crack IoU measures the line-width convention: PF 0.233 / 0.365 / 0.414 (centreline / v1.1 / 3 px) while relF1@2 stays 0.824 / 0.846 / 0.849; relF1@2 contrasts move by at most 0.0031; the convention band +-0.019 comes from here | AUD l23 to l36 | T19a, T20 #17 | ready |
| 4.5 Other faults | F3: images are about 3 x 3 cell windows; 57% of crack px and 71% of inactive px lie outside the centre cell | AUD l51 to l60 | T19a | ready |
| 4.5 | F5 and the rater: crack label errors exist and are a minority of image-supported candidates (corrected share 0.244 [0.105, 0.436]); ignoring them moves no contrast by more than 0.003 | AUD l83; `dataset_audit/rater/RESULT.md` | T19a, T20 #18 | ready; detector recall unknown (G-N12) |
| 4.5 | F2 (one double annotation, suggestive), F7 per-source label widths (ARTS 1.59 to BMRK 3.09; source explains 29.6% of width variance), F8 source identifiable at 0.94 balanced accuracy, F9 a few module groups carry the crack contrasts | AUD l38 to l49, l106, l118, l127 | T19a, T19b | ready (F2 wording: G-W10) |
| 4.6 Consequences | No absolute crack or inactive level from this dataset should be compared with another dataset or release; relF1@2 should decide | AUD l159 to l162; LOG l224 | T19b | ready |

### Chapter 5. Before the protocol: the legacy-split work (5 pp)
All rows: legacy 478 / 54 / 50 split, test50 scored in every P-series run, old decision rule; not comparable with chapters 7 and 8 (TT l677).
| § | Claim | Source (file:line) | Table | Status |
|---|---|---|---|---|
| 5.1 SSL era | Pseudo-label SSL helped at 5% labels (P13: inactive +0.117 [+0.042, +0.189], relF1@2 +0.033) and was n.d. at 20%, 50% and 100% (P16); the 11,938-cell external pool did not help (P10) | TT l673 to l720 (P13, P16, P9 / P10 rows); H11 l508 to l543 | T21 | ready; quote "supported" with the T21 caveat (G-W12) |
| 5.1 | Why supervised beat SSL for so long: regime, a joint-BN handicap until P13, 3 seeds, tuning asymmetry, small pool | H11 l522 to l543 | | ready |
| 5.2 Labels over methods | Training on revised labels gave +0.082 [+0.046, +0.129] crack IoU at 10% (P14); re-scoring old models on them +0.05 to +0.07 (P3) | TT T21 rows P3, P14 | T21 | ready |
| 5.3 Encoder erasure and PF | The house fine-tune erases ResNet-34 layer3 / layer4 (cosine to init about 0); PF keeps them: E1 inactive IoU 0.0481 to 0.2371 (+0.1890, E1 opening #1) | TT T21 rows "Encoder audit", "PF2"; H20 | T21, T17 | ready |
| 5.4 Other arms | Skeleton Recall (E1 pass, test FAIL), HC synthetic half-cuts n.d., DINOv3 ConvNeXt-T screen KILL, ResNet-50 worse on inactive, 5-seed ensemble +0.018 crack IoU (the one clear Phase 1 win) | TT T21 rows THIN-B3, HC, A8, Track M | T21 | ready |
| 5.5 What it taught | test50 opened 18 times and overlaps the pool; 3 cells hold 59% of its inactive px; 7 registered E1 openings; smallest detectable crack IoU change about 0.012: these motivate chapter 6 | BR l24, l68; P02 l56; TT l574 to l589 | T17 | ready |

### Chapter 6. The benchmark protocol (7 pp)
Write from P10 once it lands; until then from P02 plus its section 11 rulings and LOG l224 (relF1@2 decides). Check the diff before 1 Dec.
| § | Claim | Source (file:line) | Table | Status |
|---|---|---|---|---|
| 6.1 Design | A comparable number states release, split, class list, metric convention, operating-point rule and seed count; the protocol fixes all six | P02 l23 | | ready; final wording pending (P10) |
| 6.2 Sets and sealing | Development on P532 out of fold (cv5v3); test50 continuity only; E1 one registered opening with candidates fixed before any number; no development step reads a sealed label or prediction | P02 l48 to l63, l263; LOG l224 | T4 | ready |
| 6.3 Metrics and guards | relF1@2 decides (tolerance 2 px, backed by inter-annotator distances); centreline F1 not eligible (it rewards a 1 px dilation); strict crack IoU printed with the band +-0.019, decides nothing; guards: width band 0.85 to 1.15 pooled and per source, false crack px on crack-free cells, mIoU-R13 | P02 l75 to l94; LOG l224; TT l149 to l170 | T4 | ready (use the +-0.019 band, not P02 l85's 0.48 to 0.60: G-D7) |
| 6.4 Operating points and entries | OP-A and OP-W decide; OP-F unstable under A/A (printed only); OP-C adopted for prior-shifting arms; entry classes (a) to (d), ensembles beside an equal-cost comparator | P02 l95 to l106, l124 to l131, l260 | T4 | ready |
| 6.5 Statistics | Two-stage group bootstrap; M = max(0.01, 2 x SE of the A/A contrast) per machine (0.010 relF1@2; 0.049 inactive on cv02); 0 of 15 A/A splits promoted; MDE relF1@2 0.0055 at 5 seeds; E1: seed-aware bootstrap, MDE 0.0742 (derived) | P02 l107 to l122; TT l149 to l170; GP l13 | T4 | ready; state "M covers seed noise, not the choice of folds" (P02 l256) |
| 6.6 Governance and release | Info sheet, 10-item checklist, two ledgers, related-work table; release = lists and code only plus one email to Pratt, nothing published until the user approves | P02 l150 to l154; LOG l345 | | pending (P10, INFO_SHEET_TEMPLATE.md, benchmark/release_v1/) |

### Chapter 7. Baselines and methods under the protocol (9 pp)
| § | Claim | Source (file:line) | Table | Status |
|---|---|---|---|---|
| 7.1 Baseline suite | Under equal training (cv5v2, 2-seed screens) the EL papers' models sit below PF: UCF-EL's DeepLabV3 / ResNet-50 -0.0773 [-0.0892, -0.0594], Pratt's weighted CE -0.0932 [-0.1113, -0.0774] relF1@2; U-Net equals U-Net++; output stride 4 costs about 0.02, stride 8 about 0.08 to 0.10 | R1 l8 to l31; P02 l143 to l144 | T15, T16a, T20 #14 | ready |
| 7.1 | HOUSE (plain fine-tune) is a row of its own; HOUSE - PF on cv5v3 has point values only (+0.0059 relF1@2, +0.0179 strict IoU) | TT l209; AUD l155 | T6 | pending (HP; G-N1, G-N2) |
| 7.2 Screens that failed | SegFormer MiT-B2 (width guard fails, OP-W -0.0135), Skeleton Recall (moves the operating point, not the frontier), RCS, post-hoc EMA, JML, soft-band JML, encoder_spd, LA-CE, layered inactive head, per-source bias, DTI: none passes | R2 l36 to l64; TT l524 to l551 | T16a | ready |
| 7.3 5-seed confirmations (cv5v3) | HRNet-W18 U-Net++ - PF +0.0104 [+0.0012, +0.0203]: NOT CONFIRMED (false crack px 2.90 to 4.15 x PF; ARTS width 1.162); the gain is recall at equal precision | HR l3, l10 to l22 | T6, T16b, T20 #9 | ready |
| 7.3 | SWAD (swad_bn) - PF +0.0070 [-0.0007, +0.0156]: NOT CONFIRMED; its strict IoU gain +0.0180 is a convention effect (+0.0047, no pass, on centreline labels) | SW l3, l10 to l12, l22 to l25; AUD l30 | T6, T20 #10, #11 | ready |
| 7.3 | COMBO (HRNet + SWAD, swad_bn) - PF +0.0154 [+0.0065, +0.0260]: NOT CONFIRMED (8 failing guard items); the swad readout of the same runs fails only ARTS width on 416 cells | CX l3, l20 to l29 | T6, T16b | ready |
| 7.4 TTA | D4 on PF: +0.0134 [+0.0066, +0.0207] CONFIRMED, replicating B5; about 7 x fewer false crack px (212 to 32). D4 on the candidate: +0.0055 [-0.0002, +0.0115] NOT CONFIRMED, NO LOSS; the user kept D4 (FLAG D4) | FTR l15 to l28; VT; TT l215 to l248 | T7a, T7b, T20 #6, #7 | ready |
| 7.5 The final recipe | C2 = HRNet-W18 U-Net++ + SWAD (swad readout) + D4. "On CV5 the C2 recipe (CS_D4) passes its check against PF (selection-biased); the ARTS width guard fails on the 416 clean cells at OP-A and OP-W (1.159 against the 1.15 band; named) and passes on the 532 cells." +0.0222 [+0.0138, +0.0308] | GP l58 to l65 (D item 1); VT l95, l103, l111, l119, l126, l170 | T7a, T20 #8 | ready |
| 7.6 Robustness | The relF1@2 contrasts survive label variants (shift at most 0.003); C3X - PF passes under all four variants and needs 31 module groups removed to reach 0; the strict-IoU gains of HOUSE and SWAD do not survive a convention change | AUD l152 to l164 | T19b | ready |
| 7.7 Weak classes (BR problem 4) | OP-C (per-class biases, a decision layer) raises mIoU-R13 +0.0126 [+0.0077, +0.0167] on cv02, mostly gridline and splice; no final model uses it | P02 l103 to l104, l260 | | gap O6 (not in TT) |

### Chapter 8. Final model and the sealed E1 result (8 pp)
| § | Claim | Source (file:line) | Table | Status |
|---|---|---|---|---|
| 8.1 Candidates and registration | C1 (PF), C2, C3, with E-PF and C1-D4 printed beside; rule registered 11:22:35 before any dump; read once 12:02:30 to 12:06:09; the final models were never scored on E1 or test50 before | FOR l7 to l18; V8 l138, l141 to l143 | T8 notes | ready |
| 8.1 | Selection: the swad readout and D4 were chosen on pool cells (CV5), not on E1; the full-pool models C1 / C2 have no held-out score of their own | V8 l139; ER l29; GP l15 (G-N6) | T8 notes | ready (state G-N6 in text) |
| 8.2 Primary | P = C2 - C1 relF1@2 +0.0430, seed-aware [+0.0013, +0.1043] (SE 0.0265), fixed-model [+0.0067, +0.1007]; G1 width 1.013, G2 CSIR 1.013, G3 false px 0.752 x, G4 mIoU-R13 +0.0249: CONFIRMED | V8 l10 to l20; FOR l23 to l31 | T8, T20 #1 | ready |
| 8.2 | Smallest detectable effect of this read about 0.074 (2.80 x 0.0265, derived); the lower end of P is near 0 | GP l13; TT T8 notes | T8 | ready (derived, flagged) |
| 8.3 Where it holds | Full cells (44 / 24) +0.1464 [+0.0420, +0.2278]; half-cut (62 / 47) +0.0110 [-0.0289, +0.0722] n.d.; CSIR 101 of 106 cells; BMRK 5 cells: C2 0.0000, C1 0.1843 [0.0000, 0.9216], the stratum rests on 5 cells | V8 l52 to l59; R8; ER l22 to l25 | T10, T20 #2 | ready |
| 8.4 What carries it | "Most of the gain is the model": C2 - C1-D4 (both 8 views) +0.0451 [+0.0173, +0.0699]; "the D4 part is not resolved on E1": C1-D4 - C1 -0.0021 [-0.0423, +0.0575] | ER l14 to l17 | T9, T20 #5, #6 | ready |
| 8.4 | The 5-seed ensemble adds nothing over its members (C3 - C2 -0.0025 [-0.0254, +0.0157]); one deployable checkpoint (seed 5) vs C1 is n.d. (+0.0189 [-0.0403, +0.1068]): the claim is about the recipe, not one checkpoint | FOR l40, l43; TT l26 to l28 (scope) | T9, T16b, T20 #3, #4 | ready |
| 8.5 Inactive and other classes | Inactive IoU +0.0996 [-0.0310, +0.2162] n.d. (10 cells); inactive region recall 0.557 to 0.829 (decides nothing); sp mono is the one clear loss (0.2434 to 0.1658); material, edge dark at 0.0000 for every arm | FOR l28, l49 to l51; V8 l60 to l86 | T8, T12a, T12b | ready |
| 8.6 E1 against CV5 | The E1 point effect is about 2 to 3 x its CV5 size (+0.043 vs +0.015 to +0.022), but the interval contains the CV5 values, so E1 does not show a larger effect | ER l9 to l13 | T8 notes | ready |
| 8.6 | Absolute E1 levels (relF1@2 about 0.45 to 0.49) against about 0.85 on the pool: a large gap, levels only (different models and sets, no interval for the gap) | TT l474 to l493; FOR l74 to l75 | T14, T20 #16 | ready |
| 8.7 test50 public table | Context only (in-distribution, known leakage, after 18 counted openings): C2 - C1 +0.0102 [-0.0094, +0.0291] n.d.; ours on v0 under Pratt rule A (crack 0.383) is higher than Pratt 2023's printed 0.25, but the rule is inferred and test50 overlaps our pool: never a claim to beat a published model | FOR l53 to l62; ER l18 to l21; V8 l87 to l135 | T13a, T13b, T13c, T20 #13 | ready |

### Chapter 9. Few-shot layout adaptation: track T3b, E1 opening #9 (3 pp)
| § | Claim | Source (file:line) | Table | Status |
|---|---|---|---|---|
| 9.1 Question and design | How much does the C2 recipe gain on E1's layouts once it has labelled E1 cells: K = 5 folds by image id, arms ALL and HALF, seeds 5 to 7, primary ALL - ZS relF1@2 at OP-A, M 0.010, guards G1 false px (1.5 x) and G2 mIoU-R13; width printed, not a guard (E1 labels about 1.5 x wider) | T3R l17 to l24, l42 to l57, l95 to l117; T3P l62 to l64 | | ready |
| 9.2 Power and concentration | SE about 0.030 with 3 seeds; 80% power only at about +0.085; half of E1 crack px sit in 3 image ids; inactive cannot be answered | T3R l142 to l148; T3P l47 to l51 | | ready (S) |
| 9.3 Result | Verdict, levels, strata, any-hit component recall | T3b verdict file (from `harness/t3b/run_t3b_read.sh`) | (new table) | pending (T3b, about 23 Nov; G-N13) |
| 9.4 Consequence | From opening #9, E1 is training data for T3b models; no T3b number enters the zero-shot table or supports a claim about unseen modules without labels | LOG l291; P02 l254; T3R l118 to l127 | | ready |

### Chapter 10. Towards deployment: severity and inference cost (4 pp)
| § | Claim | Source (file:line) | Table | Status |
|---|---|---|---|---|
| 10.1 Severity output | Per cell: inactive area fraction a with a band; no watt figure. PF out of fold on pool cells: MAE 0.12 pp, kappa 0.78, sensitivity 0.73 at 0.5% (CSIR 0.20); not validated on unseen modules, half-cut cells or the final model | SEV l6 to l16 | T18 | ready; final model: gap G-N11 |
| 10.2 Power evidence | "Inactive area predicts power better than crack length" is not supported: null on Polenghi (n = 2 devices), null on ELPVPower by the pre-set rule (0.87 vs crack length 0.89; type order alone 0.83), borderline on a selected A3 subset | SEV l19 to l37, l46 to l51 | T18, T20 #21 | ready |
| 10.3 Thermal | Drone thermal flags bypass-diode and soiling faults (16 to 38 deg C), not crack severity (rho 0.19) | SEV l40 to l44 | T18 | ready |
| 10.4 Cost | Parameters PF 26.1 M, HRNet 20.8 M; GFLOPs per cell C1 148, C1-D4 1,184, C2 1,744, C3 8,722 (C3 is 8 x E-PF in forwards, 11.8 x in FLOPs); measured CPU and GPU latency | IC l20 to l24, l32 to l54 | (IC tables) | FLOPs ready; latency pending (IC sections 3, 6; G-N7) |
| 10.5 Pilot for WattCycle | What a pilot must measure: STC I-V per module, EL at known current, thermal at >= 600 W/m2; about 31 modules for a true rho of 0.5 | SEV l53 to l64 | | ready (S) |

### Chapter 11. Limitations and threats to validity (2 pp)
| Claim | Source (file:line) | Status |
|---|---|---|
| One sealed set, one primary, 101 of 106 cells CSIR; lower end +0.0013; MDE about 0.074; half-cut n.d.; OP-A only (stated deviation) | V8 l140, l142; TT T8 notes | ready |
| Recipe choices made on pool cells; earlier E1 looks (7 registered openings, 3 at one contrast, pre-policy reads, R0) | V8 l138 to l139 | ready |
| M covers seed noise, not the choice of folds; one machine per read; inactive under-powered (34 module groups hold all pool inactive cells) | P02 l195, l256 | ready |
| Labels: one double annotation; label-error detector recall unknown; 57% of crack px on neighbour cells | AUD l38 to l60; GP l21 | ready |
| E1 is spent by T3b; severity not validated on the final model; BenchmarkEL has no licence file | LOG l291; GP l20; P02 l45 | ready |

### Chapter 12. Conclusion and future work (2 pp)
| Claim | Source (file:line) | Table | Status |
|---|---|---|---|
| The claims table, as registered: 1 confirmed E1 claim, 1 CV5 pass (selection-biased), the rest n.d., failed or descriptive | TT l643 to l671 | T20 | ready (T3b row pending) |
| Next steps that would change the picture: a second independent annotation, labelled half-cut cells (T3b answers part), an expert look at the 49 candidate cells, OP-C for weak classes, a split-variance probe, a WattCycle pilot | AUD l181 to l192; P02 l256; SEV l53 to l64 | | ready |

### Appendices (14 pp)
- **A. Data and labels (3 pp):** T1, T2, T3a, T3b (renamed, O2), T3c.
- **B. Protocol (3 pp):** P10 summary, info-sheet template, reporting checklist (pending P10); reproducibility pins (md5 of rules, reads,
  verdicts; FOR l7 to l18; `SOURCES.tsv`).
- **C. CV5 detail (3 pp):** T5, T7b, T15, T16a, T19a, T19b.
- **D. E1 and test50 detail (3 pp):** T11a, T11b, T12a, T12b, T13b, T13c, T14, T17.
- **E. History and severity (2 pp):** T21 (landscape, 38 rows), T18.

## 3. Claims to avoid or reword, and where they tempt
From GP section C (l41 to l55), mapped to sections; then further temptations found while outlining (A*; S).

| Id | Tempting wording | Use instead | Tempts in |
|---|---|---|---|
| G-W1 | "about 3 x its CV5 size" (FOR l76) | ER item 1: "about 2 to 3 x ...; against CS_D4 - PF (+0.0222, selection-biased) about 2 x; the E1 interval contains the CV5 values" | abstract, 8.6, 12 |
| G-W2 | "The gain is the model, not the TTA" (FOR l69 to l70) | ER item 2: "Most of the gain is the model ... The D4 part is not resolved on E1" | abstract, 7.4, 8.4 |
| G-W3 | "8 test cells are pool cells" (FOR l61) | ER item 3: same physical cell; 7 by pixels, 1 by the cells.tsv link only | 4.3, 8.7 |
| G-W4 | BMRK stratum without its levels (FOR l47) | ER item 4: C2 0.0000, C1 0.1843 [0.0000, 0.9216]; rests on 5 cells | 8.3 |
| G-W5 | TTA "the most robust gain in the project" (FTR l26) | restrict to CV5 / known modules; on E1 the D4 part is not resolved | 7.4, 12 |
| G-W6 | "the largest crack gain this benchmark has measured" (`results/stageB/B5_msc_tta.md` l30) | date it (18 Nov) or drop it | 7.4 |
| G-W7 | "unseen modules" as fact | "unseen modules (supported, not proven)" at first use (SI l200), then "E1" | abstract, 1, 4.3, 8 |
| G-W8 | "found no measurable leak" (SW l29); "had no measurable effect" (H11 claim 35) | "not separated (every interval holds 0)" (LK l21) | 4.3, 7.3, 7.6 |
| G-W9 | "The unseen-source gap is real and large" (U1 l29) | descriptive levels only (T14) | 8.6, 11 |
| G-W10 | "models already sit at the agreement level of two drawings of one image" (AUD l48) | keep "one double annotation" every time | 2.3, 4.5, 11 |
| G-W11 | "No candidate, readout or threshold was selected on these cells" (FOR l66 to l67) | add: "C2's readout (swad) and D4 were chosen on pool cells" (ER l29) | abstract, 8.1 |
| G-W12 | P-series "supported for inactive" (H11 row 2; T21) | quote with T21's caveat: old locked rule, legacy split, test50 overlaps the pool | 5.1 to 5.4 |
| A1 | "beats Pratt 2023" / "state of the art" | "context only; test50 overlaps our training pool; never a claim to beat a published model" (TT l26 to l28; FOR l78 to l80) | abstract, 1.4, 3.2, 8.7 |
| A2 | "captures almost all cracks" | the 0.90 / 0.90 target was not reached (BR l57; RT l14; R8 l7) | abstract, 1.2, 12 |
| A3 | "C2 improves inactive" | n.d. on E1 (+0.0996 [-0.0310, +0.2162]) and on CV5 (+0.0328 [-0.0128, +0.0826], T7b) | abstract, 8.5, 12 |
| A4 | "HRNet / SWAD / COMBO gives a confirmed gain" | each is NOT CONFIRMED under its registered rule (T6) | 7.3 |
| A5 | "weight averaging improves crack segmentation" (strict IoU +0.018) | a line-width convention effect; relF1@2 n.d. (AUD l30; T20 #11) | 4.4, 7.3 |
| A6 | "the delivered model is better" / one checkpoint | the claim is the recipe averaged over seeds; S4 n.d. (T20 #3) | abstract, 8.4, 10 |
| A7 | "the ensemble helps" | C3 - C2 -0.0025 n.d.; C3 costs 11.8 x E-PF in FLOPs (IC l24) | 8.4, 10.4 |
| A8 | "half-cut cells improved" or "no effect on half-cut" | +0.0110 n.d.; "cannot exclude effects below about 0.074 at 80% power" (T8 note) | 8.3, 9, 11 |
| A9 | "SSL does not work on EL" | a past null closes only the run conditions (BR l13); SSL helped at 5% (T21 P13) | 3.5, 5.1 |
| A10 | "E1 is a clean zero-shot set" (after 22 Nov) | not after opening #9 (LOG l291) | 9, 11, 12 |
| A11 | a watt figure or power band per cell | not given; no labelled cell has an electrical measurement (SEV l9, l47) | 10.1, 10.5 |
| A12 | "C2 passed every CV5 guard" | GP D item 1 sentence (selection-biased; ARTS width fails on 416 cells, named) | 7.5 |
| A13 | "strict IoU near 0.5 is the labelling ceiling" (band 0.48 to 0.60, P02 l85) | the convention band +-0.019 of T4 (G-D7) | 2.3, 6.3 |

## 4. Figures to make (plotting later; no GPU; pool cells and result files only)
| # | Figure | Data file(s) | Ch | Status |
|---|---|---|---|---|
| F1 | One pool cell per source with v1.1 overlay (crack, inactive) | `benchmark/cells.tsv` (ids, source) + pool images and v1.1 masks it points to | 2 | ready |
| F2 | Crack label geometry: IoU of a label against itself shifted 1 / 2 px, centreline, 3 px | `dataset_audit/out/labels_audit.txt` (section f1) | 2 | ready |
| F3 | The 3 x 3 window: centre cell vs neighbours, share of crack / inactive px outside | `dataset_audit/out/gallery/check_centre_cell.png`; `out/crop_and_double.txt` | 4 | ready |
| F4 | Sets and splits schematic (P532, cv5v3 folds, test50, E1, forbidden stems) | TT T1 (no plot data) | 4 | ready |
| F5 | Strict IoU vs relF1@2 under label conventions (grouped bars, PF and 4 contrasts) | `dataset_audit/out/contrasts.txt` / `contrasts.json` | 4 | ready |
| F6 | Crack label width per source (box plot) | `dataset_audit/out/labels_percell.tsv` | 4 | ready |
| F7 | Label-error candidate examples with rater verdicts | `dataset_audit/out/gallery/sheet_00..09.png`, `index.tsv`; `dataset_audit/rater/RESULT.md` | 4 | ready (image terms: P02 l45) |
| F8 | Timeline of the project's beliefs, 7 Oct to 21 Nov | H11 l510 to l520; TT T17, T21; LOG l224, l291 | 5 | ready |
| F9 | Protocol flow: 2-seed screen, 5-seed row, registered opening | P02 l7 to l19, l117 | 6 | ready (schematic) |
| F10 | Forest plot: every arm's relF1@2 contrast against PF with 95% CI, screens and 5-seed rows marked, M line | `results/rows1_read/read.txt`, `rows2_full_read/read.txt`, `w2a_read/`, `w2b_lace_read/`, `w2b_lci_read/`, `c3hrnet_read/read.txt`, `c3swad_read/`, `c3x_read/read.txt`, RT; or `thesis/build/tables_data.py` (T6, T7a, T16a) | 7 | ready |
| F11 | Guards per arm on cv5v3: false crack px on crack-free cells and width ratio | RT l4 to l16; `results/c3x_read/read.txt` | 7 | ready |
| F12 | relP@2 vs relR@2 operating points (bias curve) for PF, PF_D4, CS, CS_D4 with the 0.90 / 0.90 target box | RT "frontier" section (l322 onward); `results/final_tta_read/read.json` | 1, 7 | ready (check that read.json holds the curve points) |
| F13 | E1 primary and printed-beside contrasts (forest) with M 0.010 and MDE 0.074 lines | V8 l10 to l21, l42 to l51; `final_opening_read/verdict.json` | 8 | ready |
| F14 | E1 strata of P (full, half-cut, CSIR, BMRK, crack cells) | V8 l52 to l59; R8 | 8 | ready |
| F15 | E1 per-seed relF1@2 for C1, C2, C1-D4 (dot plot) | V8 l22 to l41; TT T11b | 8 | ready |
| F16 | E1 per-class IoU, C1 vs C2 (13 robust classes) | V8 l60 to l76; TT T12a | 8 | ready |
| F17 | Domain-gap ladder: relF1@2 on CV5, U2, U1, test50 nolink16, E1 full, E1 half-cut (caption: levels of different models and sets, no interval) | VT; `results/stageB/U2U4_READ.md`; U1; R8; TT T14 | 8 | ready |
| F18 | Severity: predicted vs labelled inactive area fraction on pool (out of fold); ELPVPower module scatter | `/home/noob/work/bench_reads/severity/S1/` (per `results/severity/S1_POST_EVAL.md` l38); S3 outputs named in `results/severity/S3_ELPVPOWER.md` | 10 | ready (paths to confirm) |
| F19 | Cost vs quality: GFLOPs (and latency) per cell vs E1 relF1@2 for C1, C1-D4, E-PF, C2, C3 | IC l23 (+ latency tables); TT T11a | 10 | pending (IC latency) |
| F20 | Few-shot: ZS, HALF, ALL relF1@2 with intervals, per stratum | T3b read and verdict outputs | 9 | pending (T3b) |
| F21 | Qualitative CV5 examples: image, label, PF and C2-recipe out-of-fold predictions on pool cells | cv5v3 out-of-fold D4 dumps of queue fin (FTR l4; IC l43 to l49 for the job list) | 7 | ready (pool only); E1 or test50 examples: gap O4 |

## 5. Writing order and day estimates (24 Nov to 8 Dec)
Ready chapters with frozen sources first; chapters that wait on an input are written after it is due; intro, abstract and conclusion last.
A plotting agent can make F1 to F17 and F21 from 24 Nov in parallel (CPU, result files and pool cells only).

| Day | Date | Work | Depends on |
|---|---|---|---|
| 1 | Tue 24 Nov | Ch 8 (E1 result), with T8, T9, T10 | ready |
| 2 | Wed 25 Nov | Ch 7, sections 7.1 to 7.3 | HP for the HOUSE cells of T6 (else "point value, no interval") |
| 3 | Thu 26 Nov | Ch 7, sections 7.4 to 7.7; Ch 9 skeleton (9.1, 9.2, 9.4) | O1, O6 rows if the table builder adds them |
| 4 | Fri 27 Nov | Ch 6 (protocol) | P10 (else P02 + section 11 rulings, diff later) |
| 5 | Sat 28 Nov | Ch 4 (data, labels, audit) | ready |
| 6 | Sun 29 Nov | Ch 5 (legacy-split history) and the T21 appendix note | ready |
| 7 | Mon 30 Nov | Ch 2 (background) | ready |
| 8 | Tue 1 Dec | Ch 3 (related work); P10 diff into Ch 6 | RW; P10 |
| 9 | Wed 2 Dec | Ch 9 result section; Ch 10 (severity and cost) | T3b verdict; IC with GPU latency |
| 10 | Thu 3 Dec | Ch 11, Ch 12 (with T20), Ch 1 | all above |
| 11 | Fri 4 Dec | Abstract, front matter, appendices from `thesis_tables.tex`, bibliography (RW sources + ML ids + O5) | O5 |
| 12 | Sat 5 Dec | Insert figures, captions, cross-references | F1 to F21 |
| 13 | Sun 6 Dec | Trace pass: every number against SOURCES.tsv; sweep for section 3 wordings and em-dashes; regenerate tables if HP / T3b added rows | |
| 14 | Mon 7 Dec | Guide's read; fixes | |
| 15 | Tue 8 Dec | Final compile and PDF; 9 to 12 Dec left for guide comments, signatures, printing | |

## 6. Open inputs and gaps

### Pending inputs (other agents)
| Input | Feeds | Expected |
|---|---|---|
| P10 `benchmark/PROTOCOL_v1.0.md` (+ INFO_SHEET_TEMPLATE.md) | Ch 6, appendix B, abstract | being written (LOG l345) |
| RW `thesis/RELATED_WORK.md` (+ related_work.tex, RW_SOURCES.tsv) | Ch 3, Ch 1.3, bibliography (G-N10) | being written (LOG l343) |
| IC `thesis/INFERENCE_COST.md` (latency tables, GPU run after T3b) | Ch 10.4, F19 (G-N7) | sections 3, 5, 6, 7 still placeholders on 22 Nov 11:41 |
| HP `results/HOUSEPF_READ.md` | T6 HOUSE cells, Ch 7.1 (G-N1, G-N2) | being run (LOG l345) |
| T3b verdict (E1 opening #9) | Ch 9, F20, T20 new row (G-N13) | about 23 Nov |
| `benchmark/release_v1/` | Ch 6.6 | staged locally, user approval needed |

### New gaps found here (O ids)
| Id | Gap | Fix |
|---|---|---|
| O1 | The "almost all cracks" target (BR l57) has no row in TT for the final recipe on CV5: CS_D4 OP-A relP@2 0.9216 / relR@2 0.8211 and PF 0.8953 / 0.8024 are in RT l5, l14 (selection-biased for CS_D4), not in T5 | table round 4 adds relP@2 / relR@2 to T5, or Ch 1.2 cites RT with the selection-bias note |
| O2 | Name clash: TT table "T3b" (v1.1 changes) and the few-shot track "T3b" | number tables by chapter in the thesis; call the track "few-shot track (E1 opening #9)" |
| O3 | SPLIT_INTEGRITY.md is at `results/stageC/`, not `dataset_audit/` | cite the stageC path |
| O4 | Qualitative E1 or test50 figures need sealed predictions and images | lead's ruling before any such figure; otherwise pool examples only (F21) |
| O5 | No verified ids in ML for HRNet, U-Net++, U-Net, DeepLabV3+, Skeleton Recall, D4 TTA; RW covers EL papers only | retrieve and record ids (BR rule 1) before day 11 |
| O6 | Weak classes (BR problem 4): the OP-C result (P02 l103, l260) is not in TT; E1 material and edge dark 0.0000, splice n/a (T12a) | one TT row for OP-C, or cite P02 directly; state the problem as unsolved in Ch 11 |
| O7 | No IIT Mandi thesis template or page rule on disk | ask the guide; the budget in section 1 is a typical guess |

Still open from GP section A and used above: G-N1, G-N2 (HP), G-N3 (no E1 numbers for HRNet or SWAD alone; not proposed),
G-N6 (state in text), G-N7 (IC), G-N9 (low priority), G-N10 (RW), G-N11 (severity of the final model), G-N12, G-N13 (T3b).

## 7. The five biggest gaps or risks (S)
1. **The headline is thin and easy to overstate.** One sealed read: lower end +0.0013, MDE about 0.074, 101 of 106 cells CSIR, full
   cells carry it, half-cut n.d., recipe choices made on pool cells, 7 earlier E1 openings. Every chapter must use the ER wording and
   the scope sentence (section 0 rule 3); section 3 lists 25 wordings that would break it.
2. **The user's stated goal is not met, and the tables do not show the gap.** The 0.90 / 0.90 crack target was not reached (CV5
   0.9216 / 0.8211 selection-biased; E1 0.5995 / 0.4157); inactive is n.d. on E1 and CV5; material, edge dark and splice are at 0 on
   E1 and no final model addresses them. The CV5 recall numbers and OP-C are not in TT (O1, O6). The thesis should be framed as a
   benchmark plus one confirmed recipe gain on unseen modules, not as "captures almost all cracks".
3. **Four inputs sit on the critical path.** P10 (Ch 6, the benchmark claim itself), RW (Ch 3 and the "unorganised field" evidence),
   the T3b verdict (Ch 9; about 52% power at +0.06, so an n.d. is likely unless the gain is near +0.085 or more), and IC latency
   (Ch 10). If P10 or RW slip past 1 Dec, Ch 3 and Ch 6 compress and the writing order loses its buffer.
4. **E1 status changes on 22 Nov.** After opening #9, E1 is training data for T3b models: no zero-shot E1 claim from them, no T3b
   number in the zero-shot table, and any E1 or test50 qualitative figure needs a ruling (O4). test50 sentences must carry the leakage.
5. **References and format.** Method papers (HRNet, U-Net++, Skeleton Recall, D4 TTA, DeepLabV3+) have no verified ids on disk
   (O5) and BR rule 1 forbids unverified references; no IIT Mandi template or page rule was found (O7).

## 8. Source pins (md5, first 8 characters, as read 22 Nov 2026)
TT 707c7c46; GP b4e5f655; BR bc06edd2; P02 b8b7f66a; AUD 9d7e0d27; SI 26b3c76a; FOR 16e3f1e7; ER af55915f; V8 bbb5f3b4 (as pinned
in FOR l5); VT a95f89e8 (as pinned in FOR l16); FTR b64f964e; HR 450bf943; SEV 57e2bb4c; T3R 0c006d44. LOG is append-only; the
line numbers cited are of 22 Nov 11:40.
