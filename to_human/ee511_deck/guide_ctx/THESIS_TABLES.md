# Thesis results tables (MTP, EL defect segmentation, 24 classes; 21 Nov 2026, revised 23 Nov 2026)

Scope: the results tables of the thesis chapter, filled by copying from result files. T = the project root; paths are relative to it.
Companion files in `T/thesis/`: `thesis_tables.tex` (the same tables as booktabs floats), `SOURCES.tsv` (each copied value with
file, line and md5), `GAPS.md` (missing numbers, disagreements between sources, wording that overstates). Generator and checker:
`build/make_tables.py` with the table content in `build/tables_data.py`.

## 0. Conventions
- **Tags.** E = measured (copied from a result file). S = judgement (only in quoted "Reading" notes, marked S). Decision words are kept
  as the sources print them: CONFIRMED, NOT CONFIRMED, PASS, FAIL, n.d., NO LOSS, NULL, "decides nothing".
- **Copy, not recompute.** No value is computed or rounded here, with one ruled exception: the E1 smallest detectable effect
  (2.80 x 0.0265 = 0.0742; T4, T8), flagged `derived = yes` in `SOURCES.tsv` with its command. Where two
  files print one quantity at different precision (for example 0.8463 in a verdict and 0.846 in a summary), the table copies one and
  cites that one. Brackets are 95% intervals unless the caption says "range over seeds" or "[min, max]".
- **Check.** `make_tables.py` stops unless (1) each anchor matches exactly one line of its file, (2) each value is a substring of that
  line, (3) each value is a substring of its own table row.
- **Machines.** Training machine = the RTX A6000 machine that trained every 5-seed CV5 row and the full-pool models and made the
  dumps of the final E1 opening; second machine = the other machine, used for part of the 2-seed screens and for some pre-protocol
  runs (T21). No read mixes models of the two machines.
- **Sealed data.** Only result text files were read (verdict.txt, read.txt, *.md). No E1 or test50 label, mask, image or dump was opened.
- **Abbreviations.** relF1@2 = crack F1 at 2 px tolerance (relP@2, relR@2 its precision and recall); mIoU-R13 = mean IoU over the 13
  robust classes; OP-A = argmax; OP-W = width-matched crack bias; M = decision margin (0.010 for relF1@2). PF = U-Net++ / ResNet-34 with
  the encoder-preserving fine-tune (the baseline); HOUSE = the same model with the plain fine-tune; HRNET = HRNet-W18 U-Net++ under the
  PF recipe; SWAD = swad_const weight averaging (readouts swad and swad_bn); D4 = 8-view flip and rotation TTA; CS / CB = HRNet + SWAD
  with readout swad / swad_bn (CB = COMBO, CS = COMBO_SWAD of the c3x read). C1 = full-pool PF; C2 = full-pool HRNet + SWAD (swad) + D4
  (the final model recipe); C3 = 5-seed ensemble of C2; E-PF = 5-seed ensemble of C1; C1-D4 = C1 with D4; S4 = C2S5 = C2 seed 5 alone.
- **Errata.** `results/FINAL_OPENING_READ_ERRATA.md` (af55915f) supersedes five readings of FINAL_OPENING_READ.md; tables and notes
  use the errata wording and cite it.
- **Scope of the headline.** The confirmed E1 claim is about the C2 recipe averaged over seeds 5 to 9, not about one checkpoint; it is
  carried by the full cells; the half-cut cells are n.d. test50 rows are context only (in-distribution, known leakage) and never a
  claim to beat Pratt 2023 or any published model.

Last check run: OK: 31 tables, 344 rows, 1664 traced values, 76 source files

## 1. Outline and proposed placement

| Id | Title | Rows | Placement | Sources |
|---|---|---|---|---|
| T1 | Data, cell sets and splits | 11 | appendix | PROTOCOL_v0.2.md, OPENING_RULE.md, SPLIT_INTEGRITY.md, final_opening_read/verdict.txt, test_openings.md |
| T2 | Split integrity and leakage | 8 | appendix | PROTOCOL_v0.2.md, C3_LEAK_READ.md, SPLIT_INTEGRITY.md, FINAL_OPENING_READ_ERRATA.md, final_opening_read/verdict.txt, REPORT.md |
| T3a | Label sets | 4 | appendix | OPENING_RULE.md, LABELS_V11.md, PROTOCOL_v0.2.md |
| T3b | What v1.1 changes against v1 (legacy split) | 5 | appendix | LABELS_V11.md |
| T3c | Effect of the label set on scores | 3 | appendix | W1C_READ.md, REPORT.md |
| T4 | Protocol and decision rules | 14 | main | PROTOCOL_v0.2.md, OPENING_RULE.md, final_tta_read/verdict.txt, final_opening_read/verdict.txt, PROTOCOL_v1.0.md |
| T5 | CV5 levels on cv5v3 (training machine, seeds 5 to 9, out of fold, OP-A, mean over seeds) | 10 | appendix | final_tta_read/verdict.txt, C3HRNET_READ.md, C3X_READ.md, C3SWAD_READ.md |
| T6 | CV5 contrasts against PF on cv5v3 (5 seeds): registered verdicts | 9 | main | C3HRNET_READ.md, read.txt, HOUSEPF_READ.md, C3SWAD_READ.md, C3X_READ.md, read.txt, read_x416.txt, final_tta_read/verdict.txt, read.txt, read_x416.txt |
| T7a | CV5 TTA read on cv5v3 (FINAL_RULE section 4; 5 folds x 5 seeds per arm) | 7 | main | final_tta_read/verdict.txt, final_opening_read/verdict.txt, read.txt, read_x416.txt, HOUSECS_READ.md |
| T7b | TTA read: guard values and the earlier TTA read on the second machine (B5) | 9 | appendix | final_tta_read/verdict.txt, FINAL_TTA_READ.md, B5_msc_tta.md |
| T8 | E1 final opening #8: decision and guards | 11 | main | final_opening_read/verdict.txt, OPENING_RULE.md, FINAL_OPENING_READ.md, final_opening_read/read_e1/read.txt |
| T9 | E1 opening #8: contrasts printed beside (decide nothing) | 8 | main | final_opening_read/verdict.txt |
| T10 | E1 opening #8: strata of P (decide nothing) | 7 | main | final_opening_read/verdict.txt, final_opening_read/read_e1/read.txt |
| T11a | E1 opening #8: levels per arm (106 cells, OP-A) | 6 | appendix | final_opening_read/read_e1/read.txt |
| T11b | E1 opening #8: per model (seed) values | 15 | appendix | final_opening_read/verdict.txt |
| T12a | E1 opening #8: per-class IoU of the 13 robust classes (OP-A; arm mean; decides nothing) | 13 | appendix | final_opening_read/verdict.txt |
| T12b | E1 opening #8: component recall and precision (OP-A; arm mean; decides nothing) | 6 | appendix | final_opening_read/verdict.txt |
| T13a | test50 opening #19, public table: published rows (context only; decides nothing) | 5 | appendix | final_opening_read/verdict.txt |
| T13b | test50 opening #19: ours on v0 labels (context only; known leakage) | 22 | appendix | final_opening_read/verdict.txt |
| T13c | test50 opening #19: ours on v1.1 labels, protocol card (context only; known leakage) | 15 | appendix | final_opening_read/verdict.txt |
| T14 | Crack relF1@2 of the PF recipe across instruments: the domain gap | 10 | appendix | final_tta_read/verdict.txt, U2U4_READ.md, U1_READ.md, final_opening_read/verdict.txt, final_opening_read/read_e1/read.txt |
| T15 | Benchmark rows and wave 2a arms on cv5v2 (screens, argmax, 532 cells, mean over seeds) | 18 | appendix | ROWS1_READ.md, ROWS2_READ.md, W2A_READ.md |
| T16a | Methods that did not pass: screens and closed arms (2 seeds unless stated) | 20 | appendix | ROWS1_READ.md, ROWS2_READ.md, W2A_READ.md, W2B_LACE_READ.md, W2B_LCI_READ.md, W1C_READ.md, U1_READ.md, PROTOCOL_v0.2.md |
| T16b | Did not pass: 5-seed confirmations, the TTA increment, and E1 / test50 items that are n.d. | 12 | main | C3SWAD_READ.md, C3HRNET_READ.md, C3X_READ.md, final_tta_read/verdict.txt, final_opening_read/verdict.txt, FINAL_OPENING_READ.md, FINAL_OPENING_READ_ERRATA.md, final_opening_read/read_e1/read.txt |
| T17 | Registered E1 openings #1 to #8 (all on the same 106 cells) | 8 | appendix | e1_openings.md, final_opening_read/verdict.txt |
| T18 | Severity track: what the segmentation output says about power loss | 7 | appendix | SEVERITY_SUMMARY.md |
| T19a | Dataset and label audit of the pool (P532, v1.1; 25 out-of-fold cv5v3 models) | 12 | appendix | REPORT.md, RESULT.md |
| T19b | Robustness of the cv5v3 contrasts to label variants and to removing module groups | 4 | appendix | REPORT.md |
| T20 | Claims: evidence, interval, status | 22 | main | final_opening_read/verdict.txt, FINAL_OPENING_READ.md, FINAL_OPENING_READ_ERRATA.md, final_tta_read/verdict.txt, C3HRNET_READ.md, C3SWAD_READ.md, REPORT.md, ROWS1_READ.md, C3_LEAK_READ.md, U1_READ.md, final_opening_read/read_e1/read.txt, RESULT.md, read.txt, PROTOCOL_v1.0.md, W1C_READ.md, SEVERITY_SUMMARY.md, verdict.txt, run.log |
| T21 | Before the benchmark protocol: P-series to SKR2C (legacy split, 10 Oct to 14 Nov 2026) | 38 | appendix | 11_results_synthesis_and_claims.md, README.md, README.md, README.md, README.md, README.md, README.md, README.md, README.md, README.md, README.md, README.md, results.md, labelset_results.md, verify_labelset.md, results_final.md, verify_r2.md, verify_r3.md, verify_mim5.md, verify_ddep5.md, coach_100.md, verify_100_o1.md, verify_100_o2.md, verify_pf2.md, verify_pf2e.md, verify_thin_b3.md, verify_a8screen.md, verify_hc.md, verify_b6.md, verify_skr2_hc2.md, verify_skr2e.md, e1_openings.md, verify_skr2c.md |
| T22 | Inference cost per cell of the E1 candidates (CPU and GPU) | 5 | appendix | INFERENCE_COST.md |

Placement (as ruled on 21 Nov, round 2):
- **Main chapter:** T4, T6, T7a, T8, T9, T10, T16b, T20.
- **Appendix:** every other table, including T21 (before the benchmark protocol).

## 2. Tables

### T1. Data, cell sets and splits

Placement: appendix. Tags: E.

Cell sets used in the thesis. P532 is the development pool; E1 and test50 are sealed.

| Set | Cells | Groups / ids | Role |
|---|---|---|---|
| BenchmarkEL dataset_20211104 | 582 cells = 478 train / 54 val / 50 test, 24 classes |  | release of the pool and of test50 |
| Labelled corpus (three BenchmarkEL releases and E-SCDD) | 816 real labelled cells, 787 unique physical cells | 463 physical-module groups | inventory; 93 synthetic E-SCDD files are excluded everywhere |
| Pool P532 (legacy train + val) | 478 + 54 | by source ARTS 182, BMRK 50, CFVS 169, CSIR 114, SDLE 17 | development, CV5, and full-pool training of C1 and C2 (all 532 pool cells) |
| Clean cells (score_exclude_v3) | 116 excluded, 416 left |  | scored beside the 532 cells in every cv5v3 read |
| cv5v2 (screens) | 5 folds with held-out sizes 107 / 111 / 104 / 104 / 106 | 330 physical-module groups | 2-seed screens; holds a module leak (T2) |
| cv5v3 (corrected split) | Held-out sizes 107 / 110 / 103 / 101 / 111; 47 cells move | 285 groups, none spans folds | 5-seed rows and the CV5 TTA read |
| E1 (sealed; unseen modules) | 106 cells, 71 image ids: 66 CSIR, 5 BMRK; 101 of 106 cells CSIR, 62 half-cut cells (the pool has none), 10 inactive cells, crack in 32 cells | 71 clusters | final opening #8 (decides) |
| E1 strata (cells / clusters) | full 44 / 24; half-cut 62 / 47; crack cells 32 / 21; crack-free 74 / 55 |  | strata decide nothing |
| test50 (sealed; legacy test) | 50 cells, 48 image ids; clean49 (49 cells); nolink16 (16 cells) |  | public table #19 (decides nothing); Counted openings (24 Oct to 21 Nov 2026): 19 |
| Forbidden stems | 167 stems: legacy test 50 + ext117 117 |  | no training list may contain them |
| Half-cut cells in the pool | 0 half-cut cells |  | CV5-G cannot measure unseen layouts |

### T2. Split integrity and leakage

Placement: appendix. Tags: E (Reading column: S where the source marks S).

Module identity audit, the cv5v2 leak, the leakage read, and the links of the sealed sets to the pool.

| Check | Value | Reading |
|---|---|---|
| cv5v2 module leak (identity over all 700 image ids) | 24 physical modules span two folds; 91 pool cells (ARTS 48, CFVS 32, CSIR 11; 22.7% of crack px) are held out while a cell of their module trains | fixed at the split by cv5v3 |
| cv5v2, PF with the 91-cell exclusion (441 cells) | 0.347 strict crack IoU, 0.826 relF1@2, 0.502 to 0.505 inactive IoU, 0.606 mIoU-R13 (532 cells: 0.365 / 0.844 / 0.503 / 0.612) | no contrast changes sign |
| Leakage read (DiD, cv5v3 - cv5v2), PF 5 seeds, affected_unmoved (69 cells, primary) | strict crack IoU -0.0041 [-0.0136, +0.0069]; relF1@2 +0.0026 [-0.0092, +0.0174] | not separated |
| same, PF, affected_moved (47 cells) | strict crack IoU +0.0103 [-0.0286, +0.0252]; relF1@2 +0.0249 [-0.0286, +0.0387] | not separated |
| same, HOUSE 2 seeds, affected_unmoved | strict crack IoU +0.0049 [-0.0080, +0.0121]; relF1@2 +0.0014 [-0.0087, +0.0118] | not separated (2 seeds, no A/A) |
| E1 against every training image id (pixels) | No E1 image id is linked to any other image id; the largest inlier count of an E1 cell with a pool cell is 7 | "Unseen modules" is supported, not proven |
| test50 against the pool (pixels) | 8 test cells are the same physical cell as a pool cell (SPLIT_INTEGRITY 5b): 7 of them are confirmed by pixels; 1 (CFVS_00063_r3_c1) rests on the cells.tsv link only, "not confirmed and not refuted" (errata item 3); **7** neighbouring crops; 19 same module, no shared area; 16 cells in image ids with neither link | test50 numbers are in-distribution numbers with known leakage |
| Adjacent windows inside the pool | 61 pool images overlap a pool image of the adjacent position of the same module image (35 pairs; 16% of crack px) | same cv5v3 group, so no fold leak |

### T3a. Label sets

Placement: appendix. Tags: E.

Label sets v0, v1, v1.1 and the E1 label set, and where each is used.

| Label set | Definition | Used for |
|---|---|---|
| v0 | BenchmarkEL 20211104 labeled/masks_coded (the labels of Pratt 2023, SEiPV-Net and, presumably, PV-S3), no ignore, values 0 to 23 | test50 public table #19 only |
| v1 | masks_escdd: the E-SCDD mask (577 cells) with classes >= 24 set back to the 20211104 label, and the 20211104 mask for the 5 cells missing from E-SCDD | P-series (before the protocol); arm PFV1 of the label ablation |
| v1.1 | v1.1 = v1 with every scuff or star pixel set to ignore (255), and BMRK_00031_cell0091 given back its 20220723 mask. Ignore pixels are not scored | training and scoring of every frontier read and of both full-pool models; test50 v1.1 rows |
| E1 set | ext117/masks (release 20221008): class 24 to 2, classes 25 to 28 (scuff, corrosion cell, brightening, star) to ignore, with ext117/ignore | E1 openings #1 to #8 |

### T3b. What v1.1 changes against v1 (legacy split)

Placement: appendix. Tags: E.

Counts of the v1 to v1.1 change per legacy split (LABELS_V11.md section 2).

| Item | train | val | test |
|---|---|---|---|
| Cells (changed) | 478 (16) | 54 (0) | 50 (2) |
| Px to ignore (scuff / star) | 3,484 (3,246 / 238) | 0 | 236 (236 / 0) |
| Crack cells v1 to v1.1 | 209 to 206 | 23 to 23 | 48 to 46 |
| Crack px v1 to v1.1 | 271,805 to 269,608 | 37,938 (same) | 92,074 to 91,838 |
| Inactive cells, train / val / test (untouched) | 42 / 6 / 16 cells |  |  |

### T3c. Effect of the label set on scores

Placement: appendix. Tags: E (Reading: S).

Training-side and scoring-side effect of the label set.

| Effect | Value | Reading |
|---|---|---|
| Training on v1 instead of v1.1 (PFV1 - PF, 2 seeds, training machine, both scored on v1.1) | strict crack IoU +0.0004 [-0.0058, +0.0069]; relF1@2 -0.0014 [-0.0099, +0.0064]; inactive IoU -0.0140 [-0.0690, +0.0362]; mIoU-R13 -0.0020 [-0.0081, +0.0038] | changes no pooled metric by a measurable amount at 2 seeds |
| Release 20211104 against v1.1 on P532 | 169 of 532 cells change; crack px 260,084 to 307,546 (+18%) |  |
| Same 25 cv5v3 models scored on each release | PF strict IoU 0.320 vs 0.365 (+0.045), relF1@2 0.822 vs 0.846 (+0.025); contrasts move by at most 0.008 (HOUSE strict IoU -0.0076), no pass changes | a published level is meaningless without the release |

### T4. Protocol and decision rules

Placement: main. Tags: E (rules as written in the cited files).

Metrics, guards, statistics and decision rules of the CV5 reads (protocol v1.0, PROTOCOL_v1.0.md, eeb3379a) and of the final E1 opening (OPENING_RULE.md). Where v1.0 restates a rule of protocol v0.2 in other words, the cell keeps the v0.2 wording (PROTOCOL_v0.2.md); the note names what v1.0 adds. Training machine: the RTX A6000 machine of every 5-seed CV5 row and of the full-pool models; second machine: the other machine, used for part of the 2-seed screens.

| Element | CV5 reads (cv5v2 screens, cv5v3 rows) | E1 final opening #8 |
|---|---|---|
| Headline | Crack relF1@2 with relP@2 and relR@2; Tolerance 2 px | crack relF1@2 at OP-A |
| Strict crack IoU | relF1@2 decides; strict crack IoU is printed with its convention band and decides nothing; convention band +-0.019 = the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels | printed with the convention band +-0.019, decides nothing |
| Operating points | OP-A (argmax) and OP-W (width-matched) decide. OP-F is printed and decides nothing. | OP-A only, a stated deviation from protocol 5.4 |
| Interval | Two-stage group bootstrap, module groups (285 on cv5v3, 330 on cv5v2), then one seed per fold and arm; 2,000 draws; 95% percentile | seed-aware two-stage bootstrap: the 71 clusters are drawn with replacement, then for each arm independently 5 models are drawn with replacement from its 5; 2,000 draws; 95% percentile interval |
| Margin M | M = max(0.01, 2 x SE of the A/A contrast), per machine; cv5v2, 532 cells: training machine 0.010 for crack IoU, relF1@2, mIoU-R13, 0.049 for inactive IoU; second machine 0.010, 0.054 | M = 0.010 (the protocol's relF1@2 margin on [the training machine], section 5.4; fixed now, not re-estimated on E1) |
| A/A of the deciding read | cv5v3 PF {5,6} v {7,8}, 532 cells: relF1_2 delta -0.0002 SE 0.0037 M 0.0100 | A/A C1 {7,8} - {5,6} (descriptive): relF1@2 +0.0022 [-0.0425, +0.0507], SE +0.0225 |
| A gain counts if | It counts only if it holds at OP-A and at OP-W inside the width band, with delta at least M and the 95% interval above 0 | CONFIRMED: Delta >= M, lower end of the 95% interval > 0, and every guard G1 to G4 passes |
| Width guard | pass band 0.85 to 1.15 x the baseline's, pooled and per source with at least 40 cells (ARTS, BMRK, CFVS, CSIR) | G1 width, pooled: in 0.85 to 1.15; G2 width per source with >= 40 cells in E1: CSIR (101 cells) only |
| False crack px guard | false crack px on crack-free cells against PF (max 1.5) | G3: C2 <= 1.5 x C1 |
| mIoU-R13 guard | allowed drop 0.0100 | G4: Delta >= -0.010 |
| Inactive IoU | promotes no trained arm at 2 seeds; in the TTA read a guard with allowed drop 0.0462 (532 cells) | Inactive IoU is reported, never decides |
| Seeds | Screen = 2 seeds; table row = 5 seeds | seeds 5 to 9 per arm |
| Smallest detectable effect (power 0.8) | relF1@2 0.0087 / 0.0071 / 0.0055 at 2 / 3 / 5 seeds (cv5v2) | derived (not printed by any read): MDE = 2.80 x SE = 2.80 x 0.0265 = 0.0742, two-sided 0.05, power 0.80, normal approximation; SE = the printed seed-aware SE of P (T8 note) |
| Multiplicity | One pre-declared primary per arm | one primary contrast; prior looks: test50 18 counted openings; E1 7 registered openings (3 looks at one contrast) |

- Protocol v1.0 states the rules of the CV5 column as v0.2 does and adds two conditions: "the 532 cells and the 416 clean cells are read together and both decide" (section 0, item 3), and M is set "per machine and cell set" (section 5.4). The cv5v2 group count agrees with its split file (benchmark/splits/cv5v2.json, md5 441d118f: "n_groups": 330; PROTOCOL_v1.0.md section 3.2: 330 groups).

### T5. CV5 levels on cv5v3 (training machine, seeds 5 to 9, out of fold, OP-A, mean over seeds)

Placement: appendix. Tags: E.

Levels on the 532 pool cells (last column: 416 clean cells). CS and CS_D4 levels are selection-biased (swad readout chosen after the c3x read on these cells). Width ratio = predicted / ground-truth crack px. n/r = not reported in the cited .md file.

| Arm | strict crack IoU (decides nothing) | relF1@2 | inactive IoU | mIoU-R13 | false crack px (crack-free cells) | width ratio | relF1@2, 416 clean |
|---|---|---|---|---|---|---|---|
| PF (c3_pf_v11, U-Net++ / ResNet-34, encoder-preserving fine-tune; the C1 recipe) | 0.3653 | 0.8463 | 0.5042 | 0.6116 | 212 | 1.0189 | 0.8264 |
| HOUSE (c3_house_v11, plain fine-tune) | 0.383 | 0.852 | 0.514 | 0.607 | 774 | 1.13 | n/r |
| HRNET (HRNet-W18 U-Net++, PF recipe) | 0.3661 | 0.8567 | 0.5142 | 0.6138 | 767 | 0.97 | 0.8379 |
| SWADBN (swad_const, readout swad_bn) | 0.3834 | 0.8532 | 0.5196 | 0.6189 | 339 | n/r | 0.8362 |
| SWAD (swad_const, readout swad) | 0.383 | 0.853 | 0.525 | 0.612 | n/r | n/r | n/r |
| CB (c3x HRNet + SWAD, readout swad_bn; = COMBO) | 0.3753 | 0.8617 | 0.5042 | 0.6182 | 384 | 1.0093 | 0.8431 |
| CS (c3x HRNet + SWAD, readout swad; = COMBO_SWAD; selection-biased) | 0.3814 | 0.8629 | 0.5203 | 0.6189 | 213 | 0.9986 | 0.8439 |
| PF_D4 (PF + D4 8-view TTA; the C1-D4 recipe) | 0.3883 | 0.8597 | 0.5306 | 0.6200 | 32 | 1.0401 | 0.8395 |
| CS_D4 (CS + D4; the C2 recipe on CV5; selection-biased) | 0.3942 | 0.8684 | 0.5370 | 0.6232 | 98 | 1.0118 | 0.8494 |
| CB_D4 (CB + D4; information only) | 0.3954 | 0.8706 | 0.5284 | 0.6255 | 168 | 1.0275 | 0.8522 |

- As written in FINAL_TTA_READ.md (E): "Every CS / CS_D4 number on these cells is selection-biased: the swad readout was chosen after the c3x read on the same cells; the unbiased test is the E1 opening."
- Strict crack IoU decides nothing (kept as a familiar literature metric). "convention band +-0.019 = the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels" (final_tta_read/verdict.txt; dataset_audit/REPORT.md F1).

### T6. CV5 contrasts against PF on cv5v3 (5 seeds): registered verdicts

Placement: main. Tags: E.

Arm minus PF, crack relF1@2 with 95% two-stage group-bootstrap intervals; M 0.010. Verdict wording as registered. CS and CS_D4 rows are selection-biased.

| Contrast | relF1@2 532 OP-A | 532 OP-W | 416 OP-A | 416 OP-W | strict crack IoU, 532 OP-A (decides nothing) | Failing guard items | Verdict |
|---|---|---|---|---|---|---|---|
| HRNET - PF | +0.0104 [+0.0012, +0.0203] | +0.0117 [+0.0019, +0.0220] | +0.0115 [+0.00001, +0.0259] | +0.0126 [+0.0006, +0.0273] | +0.0008 [-0.0105, +0.0111] | false crack px 2.90 to 4.15 x PF (all four values); ARTS width 1.162 (416, OP-W) | NOT CONFIRMED, reported as a gain with failing guard items |
| SWADBN - PF (primary readout) | +0.0070 [-0.0007, +0.0156] | +0.0048 [-0.0036, +0.0141] | +0.0098 [+0.0009, +0.0198] | +0.0071 [-0.0025, +0.0176] | +0.0180 [+0.0108, +0.0262] | fails 5 guard items: ARTS width; false crack px 1.60 x | NOT CONFIRMED (no confirmed gain) |
| SWAD - PF (declared secondary readout) | +0.0064 [-0.0009, +0.0138] | +0.0053 [-0.0022, +0.0128] | +0.0075 [-0.0009, +0.0165] | +0.0058 [-0.0030, +0.0150] | +0.0181 [+0.0106, +0.0257] | fails 2 items: ARTS width at OP-A | not confirmed: neither readout passes the headline |
| COMBO - PF (c3x HRNet + SWAD, swad_bn, primary) | +0.0154 [+0.0065, +0.0260] | +0.0158 [+0.0069, +0.0264] | +0.0167 [+0.0055, +0.0298] | +0.0166 [+0.0054, +0.0298] | +0.0099 [-0.0007, +0.0207] | 8 (ARTS width; false crack px) | NOT CONFIRMED, reported as a gain with the failing guards named |
| CS - PF (c3x, swad readout, declared secondary; selection-biased) | +0.0166 [+0.0082, +0.0263] | +0.0173 [+0.0087, +0.0272] | +0.0176 [+0.0071, +0.0300] | +0.0180 [+0.0076, +0.0305] | +0.0161 [+0.0066, +0.0258], inside the convention band | 2 (ARTS width, 416 cells) | cannot be claimed from the c3x read; information for FLAG D4 |
| CS_D4 - PF (the C2 recipe on CV5; selection-biased) | +0.0222 [+0.0138, +0.0308] | +0.0228 [+0.0141, +0.0320] | +0.0230 [+0.0127, +0.0341] | +0.0229 [+0.0124, +0.0340] | +0.0288 [+0.0197, +0.0374], outside the band | failing guard items 2: ARTS width 1.159 (416, OP-A and OP-W) | C2 PASSES ITS CV5 CHECK (selection-biased; the E1 opening is the test) |
| HRNET - HOUSE (secondary) | +0.0045 [-0.0069, +0.0157] | +0.0083 [-0.0041, +0.0209] |  |  | -0.0171 [-0.0291, -0.0068] |  | decides nothing |
| HOUSE - PF (HOUSE - PF read, 22 Nov 2026; printed intervals, no verdict) | +0.0059 [-0.0043, +0.0152] | +0.0034 [-0.0075, +0.0127] | +0.0066 [-0.0068, +0.0191] | +0.0025 [-0.0116, +0.0156] | +0.0179 [+0.0093, +0.0266] | outside a bound, 9 items: ARTS width at all four values (1.307 / 1.167 / 1.370 / 1.190); CFVS width 1.164 (416, OP-A); false crack px 2.55 to 3.66 x PF (all four values) | Printed intervals only. No verdict; nothing here decides. |
| COMBO - HRNET / COMBO - SWADBN (pre-declared secondary) | +0.0050 [-0.0041, +0.0141] / +0.0085 [-0.0017, +0.0183] |  |  |  |  |  | NO LOSS |

- Reading, as written in C3HRNET_READ.md (S): "In absolute terms HRNET's excess is about 1.8 px per crack-free cell; PF's partial encoder freeze makes it unusually clean on these cells, so a 1.5 x PF bound is tight for every arm without the freeze"
- Strict crack IoU decides nothing (kept as a familiar literature metric). "convention band +-0.019 = the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels" (final_tta_read/verdict.txt; dataset_audit/REPORT.md F1).
- Reading, as written in HOUSEPF_READ.md (S): "HOUSE's strict IoU edge (+0.018) sits inside the convention band +-0.019 (T6 note) at every value; its relF1@2 interval includes 0 at every value."
- Strict crack IoU at the other three values, 532 OP-W / 416 OP-A / 416 OP-W (E; decides nothing): HOUSE - PF +0.0120 [+0.0022, +0.0216] / +0.0182 [+0.0065, +0.0295] / +0.0093 [-0.0036, +0.0215]; HRNET - PF +0.0050 [-0.0070, +0.0156] / -0.0004 [-0.0123, +0.0121] / +0.0030 [-0.0092, +0.0166]; COMBO - PF +0.0109 [+0.0002, +0.0217] / +0.0099 [-0.0020, +0.0224] / +0.0096 [-0.0027, +0.0223]. HRNET - PF and COMBO - PF as first printed by the c3hrnet and c3x reads; the HOUSE - PF read of 22 Nov 2026 "equals the earlier reads exactly" (HOUSEPF_READ.md section 3).

### T7a. CV5 TTA read on cv5v3 (FINAL_RULE section 4; 5 folds x 5 seeds per arm)

Placement: main. Tags: E.

D4 = 8-view flip and rotation TTA. Every CS and CS_D4 number is selection-biased. Strict crack IoU decides nothing (band +-0.019). The two HOUSE rows are from the HOUSE-rule read of 22 Nov 2026 (HOUSECS_READ.md), not from FINAL_RULE: the same CS and CS_D4 dumps against HOUSE, printed intervals, no verdict.

| Item | Contrast | relF1@2 532 OP-A | 532 OP-W | 416 OP-A | 416 OP-W | strict crack IoU, 532 OP-A (decides nothing) | Decision |
|---|---|---|---|---|---|---|---|
| (a) | PF_D4 - PF | +0.0134 [+0.0066, +0.0207] | +0.0132 [+0.0062, +0.0205] | +0.0132 [+0.0047, +0.0220] | +0.0132 [+0.0047, +0.0223] | +0.0230 [+0.0154, +0.0306], outside the band | CONFIRMED; failing guard items 0 |
| (b) | CS_D4 - CS | +0.0055 [-0.0002, +0.0115] | +0.0055 [-0.0009, +0.0118] | +0.0054 [-0.0023, +0.0129] | +0.0049 [-0.0033, +0.0125] | +0.0128 [+0.0053, +0.0202], inside the convention band | NOT CONFIRMED, NO LOSS; failing guard items 0; FLAG D4 ruled: keep D4: user 21 Nov 2026 11:21 IST |
| (c) | CS_D4 - PF | +0.0222 [+0.0138, +0.0308] | +0.0228 [+0.0141, +0.0320] | +0.0230 [+0.0127, +0.0341] | +0.0229 [+0.0124, +0.0340] | +0.0288 [+0.0197, +0.0374], outside the band | verdict.txt l170: "(c) C2 PASSES ITS CV5 CHECK (selection-biased; the E1 opening is the test)"; verdict.txt l126: "=> (c) CS_D4 - PF: GAIN, FAILING GUARDS NAMED; failing guard items 2: width_source src:ARTS OP-A 416 clean cells; width_source src:ARTS OP-W 416 clean cells (selection-biased)" |
| info | CS - PF (plain candidate) | +0.0166 [+0.0082, +0.0263] | +0.0173 [+0.0087, +0.0272] | +0.0176 [+0.0071, +0.0300] | +0.0180 [+0.0076, +0.0305] | +0.0161 [+0.0066, +0.0258], inside the convention band | information for FLAG D4 |
| desc. | CS_D4 - PF_D4 | +0.0087 [+0.0017, +0.0157] | +0.0096 [+0.0022, +0.0172] | +0.0099 [+0.0016, +0.0190] | +0.0097 [+0.0013, +0.0192] | +0.0058 [-0.0006, +0.0121], inside the convention band | descriptive; decides nothing |
| HOUSE rule | CS_D4 - HOUSE (the rule as written; HOUSE-rule read, 22 Nov 2026; selection-biased) | +0.0163 [+0.0051, +0.0284] | +0.0194 [+0.0080, +0.0319] | +0.0164 [+0.0033, +0.0318] | +0.0204 [+0.0073, +0.0369] | +0.0110 [+0.0029, +0.0198], inside the convention band | Printed intervals only. No verdict; nothing here decides. Outside a bound (reference HOUSE): 2 items, ARTS width at OP-A 0.847 (532) and 0.846 (416), below 0.85 |
| HOUSE rule, beside | CS - HOUSE (single view on both sides; HOUSE-rule read, 22 Nov 2026; selection-biased) | +0.0107 [-0.0009, +0.0229] | +0.0140 [+0.0017, +0.0269] | +0.0110 [-0.0028, +0.0264] | +0.0155 [+0.0013, +0.0320] | -0.0018 [-0.0109, +0.0078], inside the convention band | Printed intervals only. No verdict; nothing here decides. Outside a bound (reference HOUSE): 1 item, CFVS width 0.841 (416, OP-A) |

- Reading, as written in FINAL_TTA_READ.md (S): "TTA (D4) is now replicated twice on the baseline ([the second machine] B5 and this [the training machine] read): about +0.013 relF1@2 and about 7x fewer false crack pixels on crack-free cells."
- Strict crack IoU decides nothing (kept as a familiar literature metric). "convention band +-0.019 = the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels" (final_tta_read/verdict.txt; dataset_audit/REPORT.md F1).
- HOUSE rows (E, HOUSECS_READ.md): "Rule: PROTOCOL_v1.0.md section 7.1, HOUSE rule (l312)." "Every CS and CS_D4 number is selection-biased". "CS_D4 - HOUSE_D4: not read, no HOUSE D4 dump exists". Strict crack IoU at 532 OP-W / 416 OP-A / 416 OP-W: CS_D4 - HOUSE +0.0179 [+0.0082, +0.0281], inside / +0.0095 [-0.0004, +0.0197], inside / +0.0181 [+0.0083, +0.0296], inside; CS - HOUSE +0.0060 [-0.0041, +0.0165], inside / -0.0029 [-0.0138, +0.0082], inside / +0.0070 [-0.0038, +0.0192], inside.
- Reading, as written in HOUSECS_READ.md (S): "As written, the rule compares an 8-view arm with a single-view reference." "CS - HOUSE alone holds 0 at OP-A on both cell sets and excludes 0 at OP-W." "So the HRNet+SWAD model alone does not beat HOUSE on strict IoU in distribution; D4 does."

### T7b. TTA read: guard values and the earlier TTA read on the second machine (B5)

Placement: appendix. Tags: E.

Guard values of the TTA read (532 cells, OP-A unless stated) and the B5 read on the second machine that D4 was adopted from.

| Item | Value | Result |
|---|---|---|
| False crack px on crack-free cells, (a) | PF_D4 32 against PF 212 = 0.15 x (max 1.5) | PASS |
| False crack px on crack-free cells, (c) | CS_D4 98 against PF 212 = 0.46 x (max 1.5) | PASS |
| Width pooled, (a) | width 1.0401 / 1.0189 = 1.021 (band 0.85 to 1.15; PF_D4 / PF) | PASS |
| ARTS width, (c), 416 clean cells, OP-A | src:ARTS (n 131): width 0.9078 / 0.7832 = 1.159 (band 0.85 to 1.15; CS_D4 / PF) | FAIL |
| mIoU-R13, (c) | mIoU-R13 CS_D4 - PF = +0.0117 [+0.0046, +0.0193], allowed drop 0.0100 | PASS |
| Inactive IoU, (c) | inactive IoU CS_D4 - PF = +0.0328 [-0.0128, +0.0826], allowed drop 0.0462 | PASS |
| Per seed, CS - PF relF1@2 | positive in all 5 seeds (+0.014 to +0.022) | descriptive |
| B5 (second machine, cv5v2, W1-G PF, 2 seeds): D4MS (24 views) - PLAIN, relF1@2 OP-A / OP-W | +0.0142 [+0.0079, +0.0202] / +0.0157 [+0.0096, +0.0215] | score claim PASS on all three parts |
| B5, printed beside: D4 (8 views) - PLAIN, relF1@2 | +0.0173 [+0.0115, +0.0230] | decides nothing |

### T8. E1 final opening #8: decision and guards

Placement: main. Tags: E.

E1, 106 cells, 71 clusters, OP-A. C1 = full-pool PF (1 view); C2 = full-pool HRNet-W18 U-Net++ + SWAD (swad readout) + D4 (8 views); 5 seeds each. Registered 21 Nov 2026 11:22:35 IST; read once.

| Item | Value | Rule | Outcome |
|---|---|---|---|
| P = C2 - C1, crack relF1@2 | Delta +0.0430, seed-aware 95% interval [+0.0013, +0.1043] (SE 0.0265) | Delta >= M, lower end of the 95% interval > 0, and every guard G1 to G4 passes; M 0.010 | **CONFIRMED** |
| Fixed-model interval of P (the 10 trained models fixed; clusters only) | [+0.0067, +0.1007] | printed with P | decides nothing |
| G1 width ratio C2 / C1, pooled | 1.013 (C2 0.463, C1 0.458) | band 0.85 to 1.15 | PASS |
| G2 width ratio C2 / C1 on CSIR (101 cells) | 1.013 | band 0.85 to 1.15 | PASS |
| G3 false crack px on the 74 crack-free cells | C2 2421 <= 1.5 x C1 3218 (ratio 0.752) | <= 1.5 x C1 | PASS |
| G4 mIoU-R13 delta | +0.0249 | >= -0.01 | PASS |
| Inactive IoU (10 inactive cells) | +0.0996 seed-aware [-0.0310, +0.2162], fixed-model [-0.0000, +0.2007] | reported, never decides | n.d. |
| Strict crack IoU | +0.0263 [+0.0022, +0.0651] | outside the convention band +-0.019 | decides nothing |
| relP@2 / relR@2 / relF1@1 (C2 - C1) | relP@2 +0.0524 [-0.0226, +0.1373]; relR@2 +0.0371 [-0.0058, +0.0948]; relF1@1 +0.0441 [+0.0032, +0.1038] | printed with P | decides nothing |
| Levels, relF1@2 (mean over 5 seeds [range over seeds]) | C1 0.4467 [0.4387, 0.4574]; C2 0.4897 [0.4656, 0.5067] |  |  |
| Verdict line | FINAL OPENING VERDICT: E1 P (C2 - C1 relF1@2) CONFIRMED; Delta +0.0430 [+0.0013, +0.1043]; test50: public table only. |  |  |

- Selection (E, verdict.txt disclosures): "readout swad chosen after the c3x CV5 read; D4 adopted from the B5 CV5 read; both on pool cells only; the candidates were fixed by the user before any number of the final models; HRNet + SWAD (swad_bn) failed its CV5 confirmation (C3X_READ.md)."
- Entry class (E): "P is the contrast of the whole candidate (HRNet-W18 U-Net++ + SWAD, D4: 8 views) against PF (one view)". Prior looks (E): "test50 18 counted openings and many uncounted reads; E1 7 registered openings (3 looks at one contrast) plus reads before 31 Oct and one use of published E1 contrasts (R0, 15 Nov); the final models were never scored on either set."
- Provenance (E): "the 10 full-pool runs, steps 1 to 18,000 under F, the rest under F2 by the fin2 resume" (FINAL_RULE_ADDENDUM_1.md); "Read run ONCE: run_opening_read.sh (2525575e) 12:02:30 to 12:06:09, rc 0"; "No read.txt holds a NaN; every decision value is finite."
- E1 against CV5 size, errata wording (E; FINAL_OPENING_READ_ERRATA.md item 1, superseding FINAL_OPENING_READ.md l76): "On E1 the point effect is about 2 to 3 x its CV5 size: +0.043 vs +0.015 to +0.022." "Against CS_D4 - PF (+0.0222, selection-biased) it is about 2 x." "The E1 interval [+0.0013, +0.1043] contains the CV5 values, so E1 does not show a larger effect than CV5."
- Prior looks and selection, errata wording (E; FINAL_OPENING_READ_ERRATA.md item 5): the reference wording is verdict.txt l138 (quoted above); "Reading 1 (l66 to l67), "No candidate, readout or threshold was selected on these cells", holds for E1. But C2's readout (swad) and D4 were chosen on pool cells (verdict.txt l139)." The ledger phrase "4th look at these 106 cells" is not used (GAPS.md G-D9).
- Smallest detectable effect of P on E1 (DERIVED; ruled 21 Nov; not printed by any read): MDE = 2.80 x SE = 2.80 x 0.0265 = 0.0742 (about 0.074), two-sided alpha 0.05, power 0.80, normal approximation (2.80 = 1.96 + 0.84), SE 0.0265 = the printed seed-aware SE of P (verdict.txt l11). The log's "about 0.05" (from opening #7's SE 0.019) is not used. Read with it: the n.d. rows of T9 and T10 cannot exclude effects below about 0.074 at 80% power.

### T9. E1 opening #8: contrasts printed beside (decide nothing)

Placement: main. Tags: E.

Seed-aware 95% intervals unless stated. C3 = 5-seed ensemble of C2 (mean softmax); E-PF = 5-seed ensemble of C1; C1-D4 = C1 with D4 (8 views); S4 = C2 seed 5 alone (one deployable model).

| Contrast | relF1@2 | fixed-model | strict crack IoU (band +-0.019; decides nothing) | inactive IoU | mIoU-R13 |
|---|---|---|---|---|---|
| C2 - C1-D4 (same 8 views) | +0.0451 [+0.0173, +0.0699] | [+0.0278, +0.0597] | +0.0325 [+0.0168, +0.0475], outside the convention band | +0.0088 [-0.1408, +0.1685] | +0.0043 [-0.0169, +0.0292] |
| C1-D4 - C1 (D4 on PF) | -0.0021 [-0.0423, +0.0575] | [-0.0359, +0.0532] | -0.0061 [-0.0252, +0.0262], inside the convention band | +0.0908 [-0.0019, +0.1936] | +0.0206 [+0.0017, +0.0419] |
| S3 C3 - C2 (the ensemble's gain over its members) | -0.0025 [-0.0254, +0.0157] | [-0.0121, +0.0079] | -0.0017 [-0.0126, +0.0079], inside the convention band | +0.0274 [-0.0321, +0.0786] | +0.0055 [-0.0018, +0.0129] |
| S1 C3 - C1 | +0.0405 [-0.0044, +0.1108] | [-0.0010, +0.1056] | +0.0246 [-0.0010, +0.0698], outside the convention band | +0.1270 [-0.0001, +0.2185] | +0.0304 [+0.0102, +0.0508] |
| S2 C3 - E-PF (C3 costs 8 x E-PF) | +0.0383 [+0.0007, +0.0904] | [+0.0003, +0.0890] | +0.0270 [+0.0067, +0.0616], outside the convention band | +0.0956 [-0.0345, +0.2054] | +0.0172 [+0.0005, +0.0363] |
| S4 C2 seed 5 (deployable) - C1 | +0.0189 [-0.0403, +0.1068] | [-0.0379, +0.1007] | +0.0118 [-0.0156, +0.0600], inside the convention band | +0.1393 [+0.0009, +0.2103] | +0.0314 [+0.0109, +0.0508] |
| S5 E-PF - C1 | +0.0023 [-0.0165, +0.0279] | [-0.0096, +0.0239] | -0.0024 [-0.0121, +0.0123], inside the convention band | +0.0314 [-0.0332, +0.1119] | +0.0132 [-0.0009, +0.0316] |
| A/A C1 {7,8} - {5,6} | +0.0022 [-0.0425, +0.0507] | SE +0.0225 |  |  |  |

- Errata wording (E; FINAL_OPENING_READ_ERRATA.md item 2, superseding FINAL_OPENING_READ.md l69 to l70): "Most of the gain is the model. C2 - C1-D4 (both 8 views) is +0.0451 [+0.0173, +0.0699]." "The D4 part is not resolved on E1. C1-D4 - C1 is -0.0021 [-0.0423, +0.0575]. That interval does not exclude a CV5-sized D4 effect (PF_D4 - PF +0.0134 on CV5)." Both contrasts are printed beside and decide nothing.
- Strict crack IoU decides nothing (kept as a familiar literature metric). "convention band +-0.019 = the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels" (final_tta_read/verdict.txt; dataset_audit/REPORT.md F1).

### T10. E1 opening #8: strata of P (decide nothing)

Placement: main. Tags: E.

C2 - C1 with the seed-aware interval per stratum (verdict.txt); arm levels as mean over 5 seeds [range over seeds] (read_e1/read.txt). Strata decide nothing.

| Stratum (cells / clusters) | C2 - C1 relF1@2 [seed-aware 95%] | strict crack IoU (decides nothing) | C1 relF1@2 | C2 relF1@2 |
|---|---|---|---|---|
| all 106 / 71 | +0.0430 [+0.0013, +0.1043] | +0.0263 [+0.0022, +0.0651] | 0.4467 [0.4387, 0.4574] | 0.4897 [0.4656, 0.5067] |
| full cells 44 / 24 | +0.1464 [+0.0420, +0.2278] | +0.0911 [+0.0274, +0.1288], outside the convention band | 0.4808 [0.4543, 0.5179] | 0.6272 [0.5849, 0.6590] |
| half-cut cells 62 / 47 | +0.0110 [-0.0289, +0.0722] | +0.0099 [-0.0104, +0.0485], inside the convention band | 0.4312 [0.4197, 0.4368] | 0.4422 [0.3979, 0.4796] |
| CSIR 101 / 66 | +0.0433 [+0.0015, +0.0984] | +0.0265 [+0.0022, +0.0641] | 0.4469 [0.4391, 0.4579] | 0.4902 [0.4661, 0.5072] |
| BMRK 5 / 5 | -0.1843 [-0.5529, +0.0000] | -0.0867 [-0.2600, +0.0000] | 0.1843 [0.0000, 0.9216] | 0.0000 [0.0000, 0.0000] |
| crack cells 32 / 21 | +0.0340 [-0.0114, +0.0862] | +0.0246 [-0.0023, +0.0668] | 0.4904 [0.4862, 0.4970] | 0.5243 [0.4910, 0.5488] |
| crack-free cells 74 / 55 | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

- Reading, as written in FINAL_OPENING_READ.md (S): "Where it holds: the 44 full cells carry it (+0.146); on the 62 half-cut cells (a cell type absent from the training pool) the gain is +0.011, not significant. 101 of 106 cells are CSIR."
- Errata (E; FINAL_OPENING_READ_ERRATA.md item 4, not stated in FINAL_OPENING_READ.md l47): "On the 5 BMRK cells: C2 relF1@2 0.0000 [0.0000, 0.0000], C1 0.1843 [0.0000, 0.9216]." "C1-D4, C3 and E-PF also score 0.0000." "The C2 - C1 stratum delta of -0.1843 [-0.5529, 0.0000] rests on 5 cells."
- Strict crack IoU decides nothing (kept as a familiar literature metric). "convention band +-0.019 = the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels" (final_tta_read/verdict.txt; dataset_audit/REPORT.md F1).

### T11a. E1 opening #8: levels per arm (106 cells, OP-A)

Placement: appendix. Tags: E.

Copied from read_e1/read.txt (subset all). relF1@2 bracket = range over the arm's models (not an interval). Single-model arms have one value.

| Arm | models | relF1@2 [range] | relP@2 | relR@2 | strict crack IoU (decides nothing) | inactive IoU | mIoU-R13 | width ratio | false crack px |
|---|---|---|---|---|---|---|---|---|---|
| C1 | 5 | 0.4467 [0.4387, 0.4574] | 0.5471 | 0.3787 | 0.1630 | 0.2909 | 0.4725 | 0.458 | 3218 |
| C2 | 5 | 0.4897 [0.4656, 0.5067] | 0.5995 | 0.4157 | 0.1894 | 0.3905 | 0.4974 | 0.463 | 2421 |
| C3 | 1 | 0.4872 [0.4872, 0.4872] | 0.6052 | 0.4077 | 0.1877 | 0.4179 | 0.5030 | 0.441 | 2230 |
| EPF | 1 | 0.4489 [0.4489, 0.4489] | 0.5799 | 0.3662 | 0.1606 | 0.3223 | 0.4857 | 0.393 | 2353 |
| C2S5 | 1 | 0.4656 [0.4656, 0.4656] | 0.6322 | 0.3685 | 0.1748 | 0.4302 | 0.5039 | 0.380 | 1724 |
| C1D4 | 5 | 0.4446 [0.4245, 0.4576] | 0.6209 | 0.3474 | 0.1569 | 0.3817 | 0.4931 | 0.345 | 1765 |

- Strict crack IoU decides nothing (kept as a familiar literature metric). "convention band +-0.019 = the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels" (final_tta_read/verdict.txt; dataset_audit/REPORT.md F1).

### T11b. E1 opening #8: per model (seed) values

Placement: appendix. Tags: E.

Copied from verdict.txt section "E1 per model". C3 (seed 56789), EPF (seed 56789) and C2S5 (= C2 seed 5) are in T11a.

| Arm | seed | relF1@2 | strict crack IoU (decides nothing) | inactive IoU | mIoU-R13 | width ratio | false crack px |
|---|---|---|---|---|---|---|---|
| C1 | 5 | 0.4402 | 0.1601 | 0.2616 | 0.4591 | 0.451 | 3466 |
| C1 | 6 | 0.4516 | 0.1604 | 0.3417 | 0.4829 | 0.387 | 2378 |
| C1 | 7 | 0.4574 | 0.1699 | 0.2646 | 0.4522 | 0.450 | 2689 |
| C1 | 8 | 0.4387 | 0.1643 | 0.3580 | 0.4912 | 0.526 | 3831 |
| C1 | 9 | 0.4455 | 0.1605 | 0.2285 | 0.4772 | 0.474 | 3727 |
| C2 | 5 | 0.4656 | 0.1748 | 0.4302 | 0.5039 | 0.380 | 1724 |
| C2 | 6 | 0.5067 | 0.1994 | 0.4083 | 0.4993 | 0.529 | 2966 |
| C2 | 7 | 0.4920 | 0.1855 | 0.4595 | 0.5058 | 0.419 | 2003 |
| C2 | 8 | 0.4808 | 0.1899 | 0.3493 | 0.4913 | 0.511 | 3073 |
| C2 | 9 | 0.5033 | 0.1972 | 0.3052 | 0.4869 | 0.478 | 2337 |
| C1D4 | 5 | 0.4245 | 0.1478 | 0.3887 | 0.4723 | 0.319 | 1898 |
| C1D4 | 6 | 0.4461 | 0.1551 | 0.4334 | 0.5031 | 0.309 | 1252 |
| C1D4 | 7 | 0.4389 | 0.1568 | 0.4148 | 0.4844 | 0.326 | 1467 |
| C1D4 | 8 | 0.4576 | 0.1654 | 0.3660 | 0.4993 | 0.397 | 2130 |
| C1D4 | 9 | 0.4559 | 0.1594 | 0.3054 | 0.5064 | 0.374 | 2076 |

- Strict crack IoU decides nothing (kept as a familiar literature metric). "convention band +-0.019 = the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels" (final_tta_read/verdict.txt; dataset_audit/REPORT.md F1).

### T12a. E1 opening #8: per-class IoU of the 13 robust classes (OP-A; arm mean; decides nothing)

Placement: appendix. Tags: E.

Copied from verdict.txt. sp mono is the one clear loss of C2 against C1.

| class | C1 | C2 | C3 | EPF | C2S5 | C1D4 |
|---|---|---|---|---|---|---|
| 0 background | 0.9081 | 0.9156 | 0.9166 | 0.9122 | 0.9157 | 0.9131 |
| 1 sp multi | 0.6629 | 0.6918 | 0.6937 | 0.6830 | 0.6979 | 0.6768 |
| 2 sp mono | 0.2434 | 0.1658 | 0.1576 | 0.2465 | 0.2322 | 0.2745 |
| 4 ribbons | 0.4992 | 0.5095 | 0.5105 | 0.5047 | 0.5008 | 0.4942 |
| 5 border | 0.5436 | 0.6823 | 0.6990 | 0.5953 | 0.6777 | 0.6238 |
| 7 padding | 0.9912 | 0.9947 | 0.9953 | 0.9948 | 0.9957 | 0.9953 |
| 11 inactive | 0.2909 | 0.3905 | 0.4179 | 0.3223 | 0.4302 | 0.3817 |
| 13 material | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 14 crack | 0.1630 | 0.1894 | 0.1877 | 0.1606 | 0.1748 | 0.1569 |
| 15 gridline | 0.2314 | 0.2213 | 0.2228 | 0.2361 | 0.2161 | 0.2146 |
| 16 splice | 0.0000 | n/a | n/a | n/a | n/a | n/a |
| 20 edge dark | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 21 frame edge | 0.6640 | 0.7109 | 0.7315 | 0.6872 | 0.7019 | 0.6935 |

### T12b. E1 opening #8: component recall and precision (OP-A; arm mean; decides nothing)

Placement: appendix. Tags: E.

Crack components >= 20 px (found if >= 50% covered within 2 px); inactive regions >= 100 px.

| arm | crack recall | crack precision | inactive recall | inactive precision |
|---|---|---|---|---|
| C1 | 0.262 | 0.559 | 0.557 | 0.388 |
| C2 | 0.257 | 0.650 | 0.829 | 0.412 |
| C3 | 0.236 | 0.607 | 0.857 | 0.438 |
| EPF | 0.233 | 0.607 | 0.571 | 0.308 |
| C2S5 | 0.199 | 0.645 | 0.643 | 0.500 |
| C1D4 | 0.199 | 0.662 | 0.600 | 0.542 |

### T13a. test50 opening #19, public table: published rows (context only; decides nothing)

Placement: appendix. Tags: E (copied published rows).

Published numbers as copied in verdict.txt (from PUBLIC_BENCH.md 2a). No row of T13 supports a claim to beat a published model.

| Published row | Values (as copied) | Caveat (as copied) |
|---|---|---|
| Pratt 2023 model 4c (DeepLabv3+, custom weights) | median IoU: crack 0.25, gridline 0.20, inactive 0.38, mean of 3 0.28; ribbons 0.63, spacing 0.77; median recall crack 0.86 | rule A inferred; Fig. 7 / 8 |
| Pratt 2023 best per class over 12 models | crack 0.26 (1c), gridline 0.32 (1a, 2a), inactive 0.38 (4c) |  |
| SEiPV-Net (equal weights) | 'mIoU' 0.8604, 'IoU' 0.7447, Dice 0.8531, F1 0.9426, P 0.9491, R 0.9362 | averaging not defined |
| PV-S3 CSB-S1, FSL 100% | crack IoU 0.58 (P 0.86, R 0.64), gridline 0.83, inactive 0.50 (P 0.62, R 0.71), mean 0.6367 | split not stated, background rule not stated |
| Not comparable | Attention-Based SegNet 2024, Ramadan 2026, Hanifi 2025, Torpey 2024 | other test sets that overlap our training pool |

- Leakage (E), errata wording (FINAL_OPENING_READ_ERRATA.md item 3, superseding FINAL_OPENING_READ.md l61): "8 test cells are the same physical cell as a pool cell (SPLIT_INTEGRITY 5b). 7 of them are confirmed by pixels. 1 (CFVS_00063_r3_c1) rests on the cells.tsv link only, "not confirmed and not refuted"." Further, 7 neighbouring crops and 19 more cells that share a module (SPLIT_INTEGRITY 5b); "the full-pool models trained on all of them. test50 numbers are in-distribution numbers with known leakage, after 18 counted earlier openings." (FINAL_OPENING_READ.md l61 to l62).
- Reading, as written (S): "test50 decides nothing. C2 - C1 there is +0.010, not significant. Against the published Pratt 2023 numbers our models are higher, but test50 overlaps our training pool, Pratt's averaging rule is inferred, and PV-S3's split is not stated. These rows are context only, never a claim to beat a published model."
- Scope of "our models are higher" (E): the reading names Pratt 2023 only and does not extend to the other published rows. PV-S3 prints crack IoU 0.58, above our PV-S3-style crack IoU on test50 (C1 0.418, C2 0.441, C1-D4 0.434; T13b).

### T13b. test50 opening #19: ours on v0 labels (context only; known leakage)

Placement: appendix. Tags: E.

BenchmarkEL 20211104 masks_coded, all 50 cells, 512 px, OP-A; mean over seeds [min, max]. Seed-5 columns of verdict.txt omitted. Pratt rules A / B / C and the SEiPV variants are the reproduction conventions of PUBLIC_BENCH.md.

| Metric | C1 mean [min, max] | C2 mean [min, max] | C1-D4 mean [min, max] |
|---|---|---|---|
| Pratt A crack | 0.337 [0.329, 0.341] | 0.383 [0.379, 0.390] | 0.370 [0.360, 0.379] |
| Pratt A gridline | 0.308 [0.293, 0.329] | 0.301 [0.292, 0.329] | 0.309 [0.289, 0.322] |
| Pratt A inactive | 0.570 [0.552, 0.597] | 0.588 [0.495, 0.670] | 0.599 [0.561, 0.658] |
| Pratt A mean of 3 | 0.405 [0.396, 0.410] | 0.424 [0.393, 0.455] | 0.426 [0.405, 0.448] |
| Pratt A ribbons | 0.681 [0.672, 0.689] | 0.688 [0.684, 0.693] | 0.681 [0.678, 0.684] |
| Pratt A spacing | 0.822 [0.817, 0.827] | 0.824 [0.822, 0.826] | 0.827 [0.822, 0.831] |
| Pratt B mean of 3 | 0.202 [0.191, 0.210] | 0.204 [0.197, 0.214] | 0.207 [0.198, 0.215] |
| Pratt C mean of 3 | 0.541 [0.528, 0.548] | 0.555 [0.550, 0.558] | 0.553 [0.546, 0.558] |
| Pratt median recall crack | 0.581 [0.559, 0.599] | 0.664 [0.608, 0.703] | 0.658 [0.623, 0.675] |
| PV-S3 crack IoU (all px) | 0.418 [0.413, 0.424] | 0.441 [0.439, 0.442] | 0.434 [0.433, 0.438] |
| PV-S3 gridline IoU (all px) | 0.307 [0.288, 0.322] | 0.287 [0.282, 0.293] | 0.304 [0.288, 0.315] |
| PV-S3 inactive IoU (all px) | 0.484 [0.470, 0.502] | 0.473 [0.458, 0.490] | 0.487 [0.480, 0.495] |
| PV-S3 mean IoU (all px) | 0.403 [0.391, 0.413] | 0.400 [0.394, 0.404] | 0.409 [0.400, 0.414] |
| PV-S3 mean IoU (bg GT dropped) | 0.518 [0.499, 0.537] | 0.512 [0.506, 0.515] | 0.524 [0.509, 0.536] |
| SEiPV pixel acc | 0.942 [0.933, 0.946] | 0.945 [0.944, 0.946] | 0.944 [0.936, 0.947] |
| SEiPV micro IoU | 0.891 [0.875, 0.897] | 0.896 [0.895, 0.898] | 0.894 [0.880, 0.899] |
| SEiPV fw-IoU | 0.900 [0.890, 0.904] | 0.903 [0.901, 0.904] | 0.901 [0.892, 0.905] |
| SEiPV F1 weighted | 0.942 [0.936, 0.944] | 0.943 [0.942, 0.944] | 0.943 [0.937, 0.945] |
| SEiPV per-image mIoU absent=1 | 0.855 [0.851, 0.858] | 0.880 [0.877, 0.883] | 0.872 [0.860, 0.880] |
| SEiPV per-image mIoU absent skipped | 0.545 [0.538, 0.551] | 0.579 [0.574, 0.582] | 0.568 [0.552, 0.582] |
| SEiPV mIoU GT classes + bg | 0.548 [0.529, 0.558] | 0.553 [0.545, 0.565] | 0.553 [0.544, 0.559] |
| SEiPV mIoU GT classes, no bg | 0.523 [0.504, 0.533] | 0.528 [0.520, 0.541] | 0.528 [0.519, 0.535] |

- Leakage (E), errata wording (FINAL_OPENING_READ_ERRATA.md item 3, superseding FINAL_OPENING_READ.md l61): "8 test cells are the same physical cell as a pool cell (SPLIT_INTEGRITY 5b). 7 of them are confirmed by pixels. 1 (CFVS_00063_r3_c1) rests on the cells.tsv link only, "not confirmed and not refuted"." Further, 7 neighbouring crops and 19 more cells that share a module (SPLIT_INTEGRITY 5b); "the full-pool models trained on all of them. test50 numbers are in-distribution numbers with known leakage, after 18 counted earlier openings." (FINAL_OPENING_READ.md l61 to l62).

### T13c. test50 opening #19: ours on v1.1 labels, protocol card (context only; known leakage)

Placement: appendix. Tags: E.

OP-A. nolink16 = the 16 cells without a pool cell in their module. C2 - C1 is a secondary contrast and decides nothing alone.

| Subset | Arm | relF1@2 | strict crack IoU (decides nothing) | inactive IoU | mIoU-R13 | width | false crack px |
|---|---|---|---|---|---|---|---|
| all (50 cells) | C1 | 0.8905 | 0.4715 | 0.4754 | 0.5708 | 0.966 | 0 |
| all (50 cells) | C2 | 0.9006 | 0.4944 | 0.4618 | 0.5741 | 0.953 | 0 |
| all (50 cells) | C2S5 | 0.9022 | 0.4943 | 0.4552 | 0.5778 | 0.953 | 0 |
| all (50 cells) | C1D4 | 0.9013 | 0.4934 | 0.4784 | 0.5708 | 0.991 | 0 |
| clean49 (49 cells) | C1 | 0.8945 | 0.4747 | 0.4912 | 0.5840 | 0.974 | 0 |
| clean49 (49 cells) | C2 | 0.9048 | 0.4977 | 0.4767 | 0.5818 | 0.961 | 0 |
| clean49 (49 cells) | C2S5 | 0.9063 | 0.4976 | 0.4700 | 0.5858 | 0.961 | 0 |
| clean49 (49 cells) | C1D4 | 0.9054 | 0.4966 | 0.4943 | 0.5823 | 1.000 | 0 |
| nolink16 (16 cells) | C1 | 0.8227 | 0.3815 | 0.3679 | 0.5448 | 0.882 | 0 |
| nolink16 (16 cells) | C2 | 0.8548 | 0.4102 | 0.3666 | 0.5651 | 0.889 | 0 |
| nolink16 (16 cells) | C2S5 | 0.8575 | 0.4111 | 0.3416 | 0.5767 | 0.884 | 0 |
| nolink16 (16 cells) | C1D4 | 0.8509 | 0.4100 | 0.3705 | 0.5502 | 0.927 | 0 |
| all (50 cells) | C2 - C1 (secondary, decides nothing alone) | +0.0102 [-0.0094, +0.0291] | +0.0229 [+0.0082, +0.0368], outside the convention band |  |  |  |  |
| clean49 (49 cells) | C2 - C1 (secondary, decides nothing alone) | +0.0102 [-0.0090, +0.0292] | +0.0230 [+0.0083, +0.0366], outside the convention band |  |  |  |  |
| nolink16 (16 cells) | C2 - C1 (secondary, decides nothing alone) | +0.0322 [+0.0036, +0.0584] | +0.0286 [+0.0058, +0.0518], outside the convention band |  |  |  |  |

- Leakage (E), errata wording (FINAL_OPENING_READ_ERRATA.md item 3, superseding FINAL_OPENING_READ.md l61): "8 test cells are the same physical cell as a pool cell (SPLIT_INTEGRITY 5b). 7 of them are confirmed by pixels. 1 (CFVS_00063_r3_c1) rests on the cells.tsv link only, "not confirmed and not refuted"." Further, 7 neighbouring crops and 19 more cells that share a module (SPLIT_INTEGRITY 5b); "the full-pool models trained on all of them. test50 numbers are in-distribution numbers with known leakage, after 18 counted earlier openings." (FINAL_OPENING_READ.md l61 to l62).
- Strict crack IoU decides nothing (kept as a familiar literature metric). "convention band +-0.019 = the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels" (final_tta_read/verdict.txt; dataset_audit/REPORT.md F1).

### T14. Crack relF1@2 of the PF recipe across instruments: the domain gap

Placement: appendix. Tags: E (levels); the comparison across rows is S: the models differ per row.

Levels only; no interval exists for the differences between rows (different models and cell sets). E1 brackets are ranges over seeds.

| Instrument | Model | Cells | relF1@2 |
|---|---|---|---|
| CV5 cv5v3 (known modules) | PF c3_pf_v11, 5 seeds, training machine | 532, out of fold | 0.8463 |
| CV5 cv5v3, clean cells | same | 416 | 0.8264 |
| U2: simulated unseen-module views | PF W1-G seeds 5 to 8 (cv5v2, second machine) | 1,064 views of 532 cells | relF1@2 0.769 (against 0.846 on the plain CV5 cells) |
| U1: LOSO-2, held-out sources CSIR and BMRK | PF seeds 5 to 8 (second machine) | Pooled U1 = 164 cells | 0.733 |
| test50 v1.1, all cells (in-distribution, leaked) | C1 full-pool PF, 5 seeds | 50 | 0.8905 |
| test50 v1.1, cells without a pool cell in their module | C1 | nolink16 (16 cells) | 0.8227 |
| E1, all cells (unseen modules) | C1 full-pool PF, 5 seeds | 106 | 0.4467 [0.4387, 0.4574] |
| E1, full cells | C1 | 44 | 0.4808 [0.4543, 0.5179] |
| E1, half-cut cells (layout absent from the pool) | C1 | 62 | 0.4312 [0.4197, 0.4368] |
| E1, all cells | C2 (final recipe) | 106 | 0.4897 [0.4656, 0.5067] |

- Reading, as written (S): "Absolute E1 levels (relF1@2 about 0.45 to 0.49 against about 0.85 on the pool) show a large domain gap." (FINAL_OPENING_READ.md)

### T15. Benchmark rows and wave 2a arms on cv5v2 (screens, argmax, 532 cells, mean over seeds)

Placement: appendix. Tags: E.

All rows under the PF recipe unless stated, 20,000 steps, batch 8, 512 px, label set v1.1. Screens are 2 seeds; the comparator PF has 5 seeds on the training machine and 2 seeds (W1-G) on the second machine. Reads never mix machines. Machine column: training = the training machine (RTX A6000; every 5-seed CV5 row); second = the second machine.

| Row | Machine, seeds | stride | strict crack IoU (decides nothing) | relF1@2 | relP@2 / relR@2 | inactive IoU | mIoU-R13 | width ratio | false crack px |
|---|---|---|---|---|---|---|---|---|---|
| PF (comparator), U-Net++ / ResNet-34 | training, 5 | 1 | 0.365 | 0.844 | 0.894 / 0.799 | 0.503 | 0.612 | 1.00 | n/r |
| HOUSE, plain fine-tune | training, 2 | 1 | 0.382 | 0.850 | 0.897 / 0.807 | 0.522 | 0.609 | 1.11 | n/r |
| unet_r34_pf, U-Net / ResNet-34 | training, 2 | 1 | 0.364 | 0.843 | 0.896 / 0.795 | 0.522 | 0.612 | 1.00 | n/r |
| hanifi_vgg16_unet_pf, U-Net / VGG-16 (Hanifi et al.) | training, 2 | 1 | 0.349 | 0.838 | 0.882 / 0.798 | 0.498 | 0.610 | 0.96 | n/r |
| dlv3p_r34_pf, DeepLabV3+ / ResNet-34 | training, 2 | 4 | 0.354 | 0.835 | 0.884 / 0.791 | 0.478 | 0.609 | 1.21 | n/r |
| ucf_dlv3_r50_pf, DeepLabV3 / ResNet-50 (UCF-EL's model) | training, 2 | 8 | 0.287 | 0.767 | 0.809 / 0.729 | 0.497 | 0.574 | 1.23 | n/r |
| pratt_dlv3p_wcec, DeepLabV3+ / ResNet-34, the paper's weighted CE | training, 2 | 4 | 0.258 | 0.751 | 0.648 / 0.892 | 0.506 | 0.604 | 3.05 | n/r |
| hrnet_w18_unetpp_pf, U-Net++ / HRNet-W18 | training, 2 | n/r | 0.365 | 0.856 | 0.902 / 0.814 | 0.522 | 0.618 | 0.94 | n/r |
| skr01_pf_v11, PF + Skeleton Recall loss | training, 2 | n/r | 0.372 | 0.848 | 0.884 / 0.815 | 0.480 | 0.611 | 1.13 | n/r |
| segformer_mitb2_pf, SegFormer MiT-B2 | training, 2 | n/r | 0.348 | 0.842 | 0.877 / 0.809 | 0.530 | 0.608 | 1.20 | n/r |
| PF (comparator, W1-G) | second, 2 | n/r | 0.362 | 0.842 | 0.893 / 0.796 | 0.498 | 0.612 | 1.01 | 301 |
| swad_const (swad_bn, pre-declared) | second, 2 | n/r | 0.387 | 0.855 | 0.911 / 0.806 | 0.508 | 0.620 | 1.07 | 263 |
| swad_const (swad, no BN re-estimate) | second, 2 | n/r | 0.386 | 0.855 | 0.914 / 0.803 | 0.516 | 0.613 | 1.04 | 147 |
| swad_const (raw_bn, last iterate) | second, 2 | n/r | 0.351 | 0.829 | 0.909 / 0.762 | 0.478 | 0.604 | 0.91 | 155 |
| rcs | second, 2 | n/r | 0.344 | 0.833 | 0.884 / 0.788 | 0.485 | 0.614 | 0.94 | 505 |
| ema_wise_posthoc (ema_9998_bn) | second, 2 | n/r | 0.363 | 0.838 | 0.899 / 0.784 | 0.497 | 0.610 | 0.98 | 245 |
| jml_hard (control) | second, 2 | n/r | 0.364 | 0.841 | 0.894 / 0.795 | 0.513 | 0.613 | 0.99 | 287 |
| encoder_spd (gate failed, descriptive) | second, 2 | n/r | 0.374 | 0.842 | 0.888 / 0.801 | 0.501 | 0.606 | 1.08 | 736 |

- Strict crack IoU decides nothing (kept as a familiar literature metric). "convention band +-0.019 = the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels" (final_tta_read/verdict.txt; dataset_audit/REPORT.md F1).

### T16a. Methods that did not pass: screens and closed arms (2 seeds unless stated)

Placement: appendix. Tags: E (verdict wording as registered).

Primary contrast of each arm against its comparator, with the 95% two-stage group-bootstrap interval, and the verdict as written.

| Method | Read (split, machine) | Primary contrast | Value [95%] | Verdict |
|---|---|---|---|---|
| unet_r34_pf (U-Net / ResNet-34) | ROWS1, cv5v2, training machine | relF1@2 - PF, argmax | -0.0016 [-0.0110, +0.0073] | Nothing in this tranche beats PF or HOUSE |
| hanifi_vgg16_unet_pf (Hanifi et al.) | ROWS1, cv5v2, training machine | relF1@2 - PF, argmax; strict crack IoU, width-matched | -0.0064 [-0.0189, +0.0042]; -0.0134 [-0.0244, -0.0040] | as above |
| dlv3p_r34_pf (DeepLabV3+, stride 4) | ROWS1, cv5v2, training machine | relF1@2 - PF, argmax; width-matched | -0.0093 [-0.0204, +0.0019]; -0.0199 [-0.0325, -0.0086] | as above |
| ucf_dlv3_r50_pf (UCF-EL's model, stride 8) | ROWS1, cv5v2, training machine | relF1@2 - PF, argmax | -0.0773 [-0.0892, -0.0594] | as above |
| pratt_dlv3p_wcec (Pratt's weighted CE) | ROWS1, cv5v2, training machine | relF1@2 - PF, argmax | -0.0932 [-0.1113, -0.0774] | as above |
| skr01_pf_v11 (Skeleton Recall loss) | ROWS2, cv5v2, training machine | relF1@2 - PF, OP-A | +0.0039 [-0.0027, +0.0115] | SCREEN FAIL, closed |
| segformer_mitb2_pf (SegFormer MiT-B2) | ROWS2, cv5v2, training machine | relF1@2 - PF, OP-A; OP-W | -0.0026 [-0.0132, +0.0095]; -0.0135 [-0.0259, -0.0005] | SCREEN FAIL, closed |
| rcs (rare-class sampling) | W2A, cv5v2, second machine | relF1@2 - PF, OP-A | -0.0085 [-0.0187, -0.0004] | rcs: screen FAIL |
| ema_9998 (post-hoc EMA over the PF runs) | W2A, cv5v2, second machine | ema_9998_bn - raw_bn, relF1@2, OP-A | +0.0018 [-0.0047, +0.0081] | null |
| jml_hard (JML loss; control) | W2A, cv5v2, second machine | relF1@2 - PF, OP-A | -0.0004 [-0.0086, +0.0064] | null control |
| encoder_spd (lambda 1.0) | W2A, cv5v2, second machine | relF1@2 - PF, OP-A | +0.0007 [-0.0272, +0.0130] | gate failed, descriptive |
| soft_band_jml | W2A addendum, cv5v2, second machine | SOFTBAND - JMLHARD, relF1@2, OP-A | +0.0046 [-0.0033, +0.0127] | soft_band_jml: SCREEN FAIL, closed |
| la_ce (train-time logit offsets) | W2B, cv5v2, second machine | P1 LACE - PFC, mIoU-R13 (primary) | -0.0022 [-0.0112, +0.0060] | DROP for this offset vector (la_ce_full owed) |
| layered_ci (inactive aux head + layered decision) | W2B, cv5v2, second machine | L1 inactive region recall LCI - PFC, 532 cells | -0.0140 [-0.0767, +0.0556] | PARK, "no promotion at 2 seeds" |
| src_calib (per-source bias at inference) | W1C, cv5v2, training machine | src_bias - global bias, strict crack IoU, PF | +0.0003 [-0.0046, +0.0132] | no gain; Closed on both machines |
| dti_hysteresis | W1C, cv5v2, training machine | DTI minus the bias point, relF1@2, PF | +0.0011 [-0.0016, +0.0062] | no gain; Closed on both machines |
| OP-F (cross-fitted F1 bias) | W1C, cv5v2, training machine | A/A difference, crack IoU | -0.0118 [-0.0357, -0.0005] | unstable; printed, decides nothing |
| Skeleton Recall (SKR01) on U1 | U1, LOSO-2, second machine | SKR01 - PF at the frontier, pooled 164 cells | +0.0206 [-0.0518, +0.0744] | U1 is a guard, not a primary |
| Wider-grid class-bias variant (OP-C) | stage B fix round |  |  | failed its rule |
| gin_ipa (GIN + IPA augmentation) | not run |  |  | gin_ipa is parked, not closed |

### T16b. Did not pass: 5-seed confirmations, the TTA increment, and E1 / test50 items that are n.d.

Placement: main. Tags: E.

Rows from the cv5v3 confirmations, the CV5 TTA read and the final opening. E1 and test50 rows here decide nothing.

| Item | Read | Contrast | Value [95%] | Verdict / status |
|---|---|---|---|---|
| swad_const | C3SWAD, cv5v3, 5 seeds | SWADBN - PF, relF1@2, 532 OP-A | +0.0070 [-0.0007, +0.0156] | NOT CONFIRMED (no confirmed gain) |
| HRNet-W18 U-Net++ | C3HRNET, cv5v3, 5 seeds | HRNET - PF, relF1@2, 532 OP-A | +0.0104 [+0.0012, +0.0203] | NOT CONFIRMED, reported as a gain with failing guard items |
| HRNet + SWAD (c3x COMBO, swad_bn) | C3X, cv5v3, 5 seeds | COMBO - PF, relF1@2, 532 OP-A | +0.0154 [+0.0065, +0.0260] | NOT CONFIRMED, reported as a gain with the failing guards named |
| D4 on the candidate | FINAL_TTA, cv5v3, 5 seeds | CS_D4 - CS, relF1@2, 532 OP-A | +0.0055 [-0.0002, +0.0115] | NOT CONFIRMED, NO LOSS |
| 5-seed ensemble on E1 | opening #8, beside | S3 C3 - C2, relF1@2 | -0.0025 [-0.0254, +0.0157] | decides nothing |
| One deployable checkpoint on E1 | opening #8, beside | S4 C2 seed 5 - C1, relF1@2 | +0.0189 [-0.0403, +0.1068] | decides nothing |
| Half-cut cells of E1 | opening #8, stratum | C2 - C1, relF1@2, 62 / 47 | +0.0110 [-0.0289, +0.0722] | decides nothing |
| Inactive on E1 | opening #8, reported | C2 - C1, inactive IoU (10 cells) | +0.0996 seed-aware [-0.0310, +0.2162] | n.d. |
| D4 on PF, on E1 | opening #8, beside | C1-D4 - C1, relF1@2 | -0.0021 [-0.0423, +0.0575] | descriptive |
| sp mono class on E1 | opening #8, per class | IoU C1 / C2 | 0.2434 / 0.1658 | (the one clear loss) |
| BMRK cells of E1 (5 cells) | opening #8, stratum | C2 - C1, relF1@2; levels | -0.1843 [-0.5529, +0.0000]; C2 relF1@2 0.0000 [0.0000, 0.0000], C1 0.1843 [0.0000, 0.9216]; C1-D4, C3 and E-PF also score 0.0000 | decides nothing; rests on 5 cells (errata item 4) |
| test50 (v1.1) | opening #19, secondary | C2 - C1, relF1@2, all 50 | +0.0102 [-0.0094, +0.0291] | secondary, decides nothing alone |

### T17. Registered E1 openings #1 to #8 (all on the same 106 cells)

Placement: appendix. Tags: E (copied from the ledger).

Copied from team_2026-10-31_next/e1_openings.md. E1 was also read many times before the 31 Oct policy (not counted). #4 is not independent of #1, #6 not of #5. Row 8 uses the verdict.txt l138 wording on prior looks; the ledger phrase "4th look at these 106 cells" is ambiguous and superseded by errata item 5 (GAPS.md G-D9).

| # | Protocol | Opened | Outcome (copied) |
|---|---|---|---|
| 1 | protocol_PF2 | opened 1 Nov 06:33-08:26 | E1 inactive IoU +0.189 BETTER (replicated); E1 crack recall +0.027 n.d. |
| 2 | protocol_thin_b3 | opened 1 Nov 19:40-21:13 | E1 crack relF1@2 SKR +0.059 BETTER, CLD +0.037 n.d., B3 +0.001 n.d.; overall SKR FAIL (test crack IoU WORSE), CLD FAIL (B5 relR@2 WORSE), B3 n.d. (scuff class not learned) |
| 3 | protocol_HC | opened 2 Nov 02:18:34-03:09:57 | E1 crack relF1@2 +0.0135 (thr 0.0429) n.d.; E1 inactive IoU −0.0002 (thr 0.0572) n.d.; HC n.d. |
| 4 | protocol_PF2E | opening started 1 Nov 19:02:04 | E1 inactive IoU +0.214, cluster CI [+0.030, +0.382] PASS; E1 crack relF1@2 +0.036 n.d.; Not independent of #1 (same member models) |
| 5 | protocol_SKR2_HC2 | opened 2 Nov 20:01:46-21:23:18 | SKR2 PASS (E1 crack relF1@2 +0.0364, thr 0.0351, BETTER); HC2 FAIL by G1; SKR2 BETTER label fragile (5 / 10 seed drops) |
| 6 | protocol_SKR2E | opened 2 Nov 22:24:38-22:36:52 | SKR2E FAIL by G2a (test relP@2 -0.0379) + G2b (E1 crack-free px x2.12) at the headline pair; Not independent of #5 (same members) |
| 7 | protocol_SKR2C | opened 14 Nov 2026 00:22:45-03:54:57 | R FAIL; D FAIL; Named claim: REPLICATED does not hold (seed-aware CI [−0.0015, +0.0590]) |
| 8 | OPENING_RULE.md (final) | opened 21 Nov 2026 11:25:30 to 12:06:09 | CONFIRMED; Delta +0.0430 [+0.0013, +0.1043]. Prior looks (verdict.txt l138): E1 7 registered openings (3 looks at one contrast) plus reads before 31 Oct and one use of published E1 contrasts (R0, 15 Nov); the final models were never scored on either set |

### T18. Severity track: what the segmentation output says about power loss

Placement: appendix. Tags: E (values); R and S as marked in the source.

Copied from results/severity/SEVERITY_SUMMARY.md (every number reproduced by the reviewer per that file). No model was trained; external data used for inference and analysis only. a = predicted inactive area fraction.

| Evidence | Measure | Value (copied) | Status (copied) |
|---|---|---|---|
| Per-cell output on our pool (PF, out of fold) | MAE of a; band agreement; detection at 0.5% | MAE of a: 0.12 pp over 532 cells; Band agreement: kappa 0.78. Detection at 0.5%: sensitivity 0.73, false alarm 0.25%. On CSIR cells, sensitivity is only 0.20. | The output is not validated on unseen modules or half-cut cells. |
| Polenghi (2 mini-panels, 84 cumulative damage stages) | Spearman rho with power loss | Predicted inactive area tracks the loss at rho 0.56. Predicted crack length gives 0.65, and stage number alone gives 0.91. n = 2 devices. | NULL |
| ELPVPower (137 module instances, measured Pmpp; analysis only, terms unverified) | rho with power loss | rho 0.87 [0.80, 0.91] (129 modules). Predicted crack length does as well (0.89). The type order alone gives 0.83. Within T1, nothing the model sees tracks the loss (rho 0.02). | NULL by the pre-set rule |
| ELPVPower, within T3 (59 modules) | inactive area against crack length | 0.93 against 0.83 | This was seen after the fact and is not a result. |
| DTU A3 (lab-damaged modules, STC I-V; label = FF loss) | rho with FF loss | EL darkness on the 24 non-diode modules: rho 0.64 [0.24, 0.87]; on the 16 modules our cutting could handle: predicted inactive area rho 0.90, against 0.44 for EL darkness | Read it as: borderline, on a selected subset. |
| Drone thermal (module level) | rho with FF loss; added to EL | rho 0.19; ΔR2 +0.10, interval -0.18 to +0.40; diode and soiling faults 16 to 38 deg C, against about 1 deg C for the other defects | a screen for diode and soiling faults; not a crack-severity measure |
| Claim "inactive area predicts power better than crack length" |  | null on Polenghi, null on ELPVPower; on A3 borderline and on a subset | not supported |

### T19a. Dataset and label audit of the pool (P532, v1.1; 25 out-of-fold cv5v3 models)

Placement: appendix. Tags: E (numbers); S (implications, status).

Ranked faults of dataset_audit/REPORT.md and the pre-registered AI-rater check (dataset_audit/rater/RESULT.md). Status words as written in REPORT.md section 3 and RESULT.md.

| Fault | Key numbers (copied) | Status / caveat (copied) |
|---|---|---|
| F1 strict crack IoU measures the line-width convention | PF strict crack IoU 0.233 (1-px centreline), 0.365 (v1.1), 0.414 (3 px wide); relF1@2 stays 0.824 / 0.846 / 0.849; label shifted 1 px against itself: IoU 0.483; relF1@2 contrasts move by at most 0.0031 under every variant | Solid (E, mechanical, reproduced) |
| F2 labelling ceiling (one double annotation) | mask against mask: strict crack IoU 0.259, relF1@2 0.829; models: PF 0.365 / 0.846; 25-model vote 0.398 / 0.868 | Suggestive: F2 ceiling (one double annotation) |
| F3 images are windows of about 3 x 3 cells | 57% of v1.1 crack px and 71% of inactive px lie outside the centre cell; 117 of the 229 "crack cells" have no crack px in their centre cell | Solid |
| F4 inactive labels and power | spurious-inactive candidates 31,039 px = 10.9% of inactive px; 33 of 285 groups, Kish n_eff 12.9 groups; ignoring candidates raises PF inactive IoU 0.504 to 0.574 (+0.069) | rater: spurious inactive 5/40 label error, 30/40 model error; the label is right there |
| F5 crack label errors | missed: 128 segments in 42 cells, 5,436 px (1.8% of crack px); spurious: 53 components in 28 cells, 7,567 px (2.5%); ignoring all candidates: PF relF1@2 0.846 to 0.864, no contrast moves by more than 0.003 | rater: 18/78 = 0.231, cell-bootstrap [0.099, 0.405]; corrected 0.244 [0.105, 0.436]: MEASURED: label errors exist but are a minority of the image-supported candidates |
| F6 label release moves levels | PF strict IoU 0.320 vs 0.365 (+0.045), relF1@2 0.822 vs 0.846 (+0.025) (see T3c) | Solid |
| F7 per-source label conventions | crack label width ARTS 1.59, CFVS 2.06, CSIR 2.25, BMRK 3.09; source explains 29.6% of the variance of per-cell width; 10 of 24 classes occur in one source only | Solid (width and vocabulary) |
| F8 source identifiable from image statistics | balanced accuracy of a source classifier (chance 0.20): 0.94; 0.85 from the 8-bin power spectrum alone | Solid; shows a shortcut is available, not that a model uses it |
| F9 a few module groups carry the crack contrasts | crack px in 125 of 285 groups, Kish n_eff 24.1 groups; HRNET - PF +0.0104 falls under M after 1 group; HOUSE - PF +0.0059 reaches 0 after 4 groups | Solid; greedy removal is a worst case, not a sampling distribution |
| F10 image faults | 2 pool images with noise sigma > 10; 109 of 532 images show an 8 x 8 block grid; 19 under-exposed CSIR images |  |
| F11 duplicates and leakage (new check) | 41 cross-group pairs with DCT-hash distance <= 6 | No new leak found. |
| AI-rater calibration (60 blind items) | Every rater alone: sensitivity 29/30, specificity 30/30. Majority: sens 0.967 [0.833, 0.994], spec 1.000 [0.886, 1.000] | the three raters are runs of one model (consistency, not independent reliability) |

### T19b. Robustness of the cv5v3 contrasts to label variants and to removing module groups

Placement: appendix. Tags: E.

Copied from dataset_audit/REPORT.md section 2. Variants in the order old / centreline / 3 px / candidates ignored. k_0 = module groups removed (greedy) until relF1@2 reaches 0. Bold = changes the verdict, as marked in the source.

| Contrast (cv5v3, 5 seeds, 532 cells) | relF1@2 | relF1@2 under variants | k_0 | strict IoU (decides nothing) | strict IoU under variants |
|---|---|---|---|---|---|
| HOUSE - PF | +0.0059 | +0.0033 / +0.0036 / +0.0079 / +0.0053 | 4 | +0.0179 PASS | +0.0103 / **+0.0015** / +0.0367 / +0.0179 |
| HRNET - PF | +0.0104 PASS | +0.0109 / +0.0107 / **+0.0073** / +0.0107 | 17 | +0.0008 | +0.0028 / +0.0032 / **-0.0109** / +0.0007 |
| SWADBN - PF | +0.0070 | +0.0050 / +0.0062 / +0.0083 / +0.0071 | 24 | +0.0180 PASS | +0.0119 / **+0.0047** / +0.0342 / +0.0188 |
| C3X - PF | +0.0154 PASS | +0.0149 / +0.0151 / +0.0128 / +0.0161 (all PASS) | 31 | +0.0099 | +0.0086 / +0.0065 / +0.0071 / +0.0104 |

- Strict crack IoU decides nothing (kept as a familiar literature metric). "convention band +-0.019 = the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels" (final_tta_read/verdict.txt; dataset_audit/REPORT.md F1).

### T20. Claims: evidence, interval, status

Placement: main. Tags: E (evidence, interval, status wording); S (claim text and class).

Status = the source's own decision word. Class: confirmed / n.d. / failed / descriptive / measured. Claims are scoped as stated; nothing here claims to beat a published model.

| # | Claim (scope) | Evidence | Interval / value | Status (source wording) | Class |
|---|---|---|---|---|---|
| 1 | On E1 (106 unseen-module cells, 71 clusters), the final recipe C2 (HRNet-W18 U-Net++ + SWAD + D4, full pool, mean over seeds 5 to 9) has a higher crack relF1@2 than full-pool PF (C1). The confirmed claim is about the recipe averaged over seeds, not about one checkpoint. Prior looks: E1 7 registered openings (3 looks at one contrast), reads before 31 Oct, one use of published E1 contrasts; the final models were never scored on E1 before. | E1 opening #8 (T8) | +0.0430 [+0.0013, +0.1043] seed-aware; fixed-model [+0.0067, +0.1007]; guards G1 to G4 PASS | CONFIRMED | confirmed |
| 2 | Where the E1 gain sits: full cells carry it; on half-cut cells (a layout absent from the pool) it is not detected. | E1 strata (T10) | full 44 / 24: +0.1464 [+0.0420, +0.2278]; half-cut 62 / 47: +0.0110 [-0.0289, +0.0722] | strata decide nothing | descriptive (full); n.d. (half-cut) |
| 3 | One deployable checkpoint (C2 seed 5) beats C1 on E1. | S4 (T9) | +0.0189 [-0.0403, +0.1068] | printed beside; decides nothing | n.d. |
| 4 | The 5-seed ensemble C3 adds to its members on E1. | S3 (T9) | -0.0025 [-0.0254, +0.0157] | printed beside; decides nothing | n.d. |
| 5 | On E1, most of the gain is the model; the D4 part is not resolved on E1 (errata item 2). | C2 - C1-D4; C1-D4 - C1 (T9) | Most of the gain is the model. C2 - C1-D4 (both 8 views) is +0.0451 [+0.0173, +0.0699]; C1-D4 - C1 is -0.0021 [-0.0423, +0.0575] | descriptive; decides nothing | descriptive |
| 6 | D4 TTA on PF raises crack relF1@2 on CV5 (known modules); on E1 the D4 part is not resolved. | TTA (a) (T7a); C1-D4 - C1 (T9) | CV5 +0.0134 [+0.0066, +0.0207]; E1 -0.0021 [-0.0423, +0.0575] | CONFIRMED (CV5); descriptive (E1) | confirmed (CV5); n.d. (E1) |
| 7 | D4 adds to HRNet + SWAD on CV5. | TTA (b) (T7a) | +0.0055 [-0.0002, +0.0115] | NOT CONFIRMED, NO LOSS | n.d. |
| 8 | The C2 recipe beats PF on CV5 (cv5v3, 5 seeds). | TTA (c) (T7a) | +0.0222 [+0.0138, +0.0308] | C2 PASSES ITS CV5 CHECK (selection-biased; the E1 opening is the test) | passes, selection-biased |
| 9 | HRNet-W18 U-Net++ alone beats PF on CV5. | C3HRNET (T6) | +0.0104 [+0.0012, +0.0203]; false crack px 2.90 to 4.15 x PF | NOT CONFIRMED, reported as a gain with failing guard items | failed (guards) |
| 10 | Weight averaging (swad_const) alone beats PF on the headline. | C3SWAD (T6) | +0.0070 [-0.0007, +0.0156] | NOT CONFIRMED (no confirmed gain) | n.d. |
| 11 | Weight averaging raises strict crack IoU (a convention-sensitive metric). | C3SWAD; audit F1 | +0.0180 [+0.0108, +0.0262]; +0.0047 (no pass) on centreline labels | this is reported, not claimed | descriptive |
| 12 | C2 raises inactive IoU on E1 (10 inactive cells). | T8 | +0.0996 seed-aware [-0.0310, +0.2162] | reported, never decides; n.d. | n.d. |
| 13 | C2 beats C1 on test50 (v1.1, leaked, in-distribution). The public comparison is context only, never a claim to beat a published model. | opening #19 (T13) | +0.0102 [-0.0094, +0.0291] | secondary, decides nothing alone | n.d. |
| 14 | Under equal training on CV5, the models of the EL papers sit below the PF baseline (2-seed screens, cv5v2). | ROWS1 (T16a) | ucf_dlv3_r50_pf -0.0773 [-0.0892, -0.0594]; pratt_dlv3p_wcec -0.0932 [-0.1113, -0.0774] | Nothing in this tranche beats PF or HOUSE | descriptive (screens) |
| 15 | The cv5v2 module leak inflated the scores of the affected cells. | C3_LEAK (T2) | PF relF1@2 DiD +0.0026 [-0.0092, +0.0174] (affected_unmoved) | not separated | n.d. |
| 16 | The PF recipe loses much crack quality on unseen sources and unseen modules. | U1; E1 (T14) | U1: PF loses about 0.11 relF1@2 against its CV5 level (0.733 against 0.844); E1 C1 0.4467 [0.4387, 0.4574] | descriptive | descriptive (no interval for the gap) |
| 17 | Strict crack IoU measures the annotators' line-width convention more than the model; relF1@2 contrasts are stable under the variants. | audit F1 (T19a) | PF 0.233 / 0.365 / 0.414 (centreline / v1.1 / 3 px); relF1@2 contrasts move by at most 0.0031 | Solid (E, mechanical, reproduced) | measured |
| 18 | Crack label errors exist, are a minority of the image-supported candidates, and move no contrast by more than 0.003. | audit F5; rater (T19a) | corrected share 0.244 [0.105, 0.436] (78 candidates, 3 calibrated AI raters) | MEASURED: label errors exist but are a minority of the image-supported candidates | measured (AI raters) |
| 19 | On strict crack IoU, the label release (20211104 against v1.1, P532) moves the absolute level of PF more than any method gain over PF on CV5 does. Not claimed for relF1@2: there the largest CV5 contrast against PF (CB_D4 - PF, information only) is 0.97 of the release shift. | audit F6 (T3c); TTA read (read.txt); PROTOCOL_v1.0.md l36 | PF strict IoU 0.320 vs 0.365 (+0.045); strict-IoU contrasts against PF in the TTA read at most +0.0333 (CS_D4 and CB_D4, OP-F), CB_D4 - PF +0.0300 [+0.0209, +0.0390] at OP-A. relF1@2 0.822 vs 0.846 (+0.025); CB_D4 - PF +0.0243 [+0.0160, +0.0338], 0.97 of the shift | Solid | measured |
| 20 | Training on v1.1 instead of v1 changes the model measurably. | W1C (T3c) | relF1@2 -0.0014 [-0.0099, +0.0064] (PFV1 - PF, 2 seeds) | changes no pooled metric by a measurable amount at 2 seeds | n.d. |
| 21 | Predicted inactive area predicts power loss better than crack length. | severity (T18) | null on Polenghi, null on ELPVPower; on A3 borderline and on a subset | not supported | failed (null) |
| 22 | Few-shot, inside E1: trained on the pool plus the labelled E1 cells of the other folds (ALL), the C2 recipe has a higher out-of-fold crack relF1@2 than the same recipe zero-shot (ZS = opening #8 C2, seeds 5 to 7). Scope: 5 folds by source image, seeds 5 to 7, OP-A, 106 cells, 71 clusters; 101 of 106 cells CSIR. Labelled cells of the layout help; not a claim about a new layout without labels. Half of the labelled images give about the same gain; ALL - HALF is not separated. | E1 opening #9 (ch. 9) | +0.2213 [+0.0977, +0.3504] seed-aware; fixed-model [+0.1066, +0.3390]; G1 541 <= 1.5 x 2231 and G2 +0.1385: PASS. HALF - ZS +0.2042 [+0.0718, +0.3366]; ALL - HALF +0.0171 [-0.0246, +0.0625]. Half-cut 62 / 47: +0.2530 [+0.0878, +0.3885]; without scuff 33 / 31: -0.0701 [-0.3019, +0.0517]. Width ratio ALL / ZS 1.426 (reported) | P: CONFIRMED | confirmed (few-shot, inside E1) |

### T21. Before the benchmark protocol: P-series to SKR2C (legacy split, 10 Oct to 14 Nov 2026)

Placement: appendix. Tags: E (copied from handbook doc 11 rows and the cited session records); outcome words as written there.

One row per arm or decision. Legacy 478 / 54 / 50 split, primaries on the 50 test cells with revised (20221008 / E-SCDD) labels unless stated; E1 = the 106 unseen-module cells. Not comparable with the frontier tables (different split, labels, recipe and rule; test50 was scored in every P-series run). Values "(thr x)" are the locked rule's threshold. Every row traces to handbook doc 11 and to the primary record it cites (SOURCES.tsv); no row rests on the handbook alone.

| Experiment (set) | Arm or contrast | Value (as copied) | Outcome (as copied) |
|---|---|---|---|
| P3 (old era, exploratory; test) | old-era models re-scored on revised labels | re-scoring on revised labels +0.05 to +0.07 crack IoU | supported (claim row 1, with P14) |
| P14 (locked; 10% labels) | training on revised vs old labels at 10% | L3 − L3o +0.082 [+0.046, +0.129]; unseen modules (+0.030 [+0.012, +0.048]) | supported |
| P6 (locked) | supervised recipe | label-safe augmentation helps (crack AP +0.020, inactive AP +0.028); L3 10% → 100% crack IoU +0.075, inactive +0.135 | supported |
| P11 / P12 (joint BN) | pseudo-label loss vs loss-off control | P11 10% Cm − Dm: inactive +0.071 [+0.020, +0.121], relF1@2 +0.018 (joint BN); P12 5% Cm5 − Dm5: crack +0.023 [+0.005, +0.036] (joint BN) | supported for inactive; for crack IoU only against a handicapped (joint-BN) control |
| P11 to P13 (BN audit) | loss-off control vs supervised, crack IoU; separate-BN fix | P12 Dm5 − A5c −0.017 [−0.024, −0.010]; P13 fix (separate BN): Cs5 − Cm5 inactive +0.084 [+0.030, +0.143] | supported; grows as labels shrink. The fix helps inactive and false alarms, not crack IoU |
| P13 (5% labels; 5 v 5; primary) | CsM5 − A5c (separate BN + CutMix) | inactive +0.117 [+0.042, +0.189], relF1@2 +0.033 [+0.006, +0.055], crack IoU +0.014 n.d. | supported at 5% on inactive and crack relF1@2; crack IoU only with hard PL (secondary) |
| P13 Amendment 2 (5 seeds; secondary) | BsM5 − A5c (hard PL + CutMix) | crack IoU +0.029 [+0.014, +0.041] | passes on all three (secondary) |
| P13 (tolerant vs hard PL under CutMix) | CsM5 − BsM5, crack IoU | on 5 vs 5 (Amendment 2) −0.015 (thr 0.018), n.d. | not supported on the L3 base; tolerant only beat hard on the old L0 base |
| P9 / P10 (external 11,938-cell pool, joint BN) | P10 Cx5 − Dx5 | crack IoU −0.012 [−0.026, −0.001] (robust over cells, n.d. by seeds) and relF1@2 −0.027 (worse by the rule) | not supported |
| P14 (offset tolerance on human labels) | L3To − L3o | recovers 0% of the label-noise gap (L3To − L3o −0.004) | not supported for label noise; weak for inactive |
| P15 (second machine, 3 seeds; UCF-EL pretraining) | gU10 − gA10 | worse on all three (crack −0.012, inactive −0.086, relF1@2 −0.014), robust over cells | not supported for this recipe; MIM untested |
| P16 (Cs recipe; 20 / 50 / 100% labels) | SSL − supervised at each fraction | n.d. at 20%, 50%, 100% | supported in shape for the Cs recipe: a test gain at 5%, none detectable from 20% up |
| P17 (5 v 5, locked) | BsD5 − BsM5 (decoupled decoder) | −0.006 / +0.011 / −0.008, n.d. | not supported as a need; a share below about 40% of the gain is not excluded |
| E1 extension (106 cells) | test to unseen modules, crack IoU | L3 100% crack IoU 0.471 → 0.152, tolF1 0.80 → 0.41 | not supported (a measured limit) |
| AL1 (training machine, 5 v 5, locked; 23 Oct) | AL5 − A5 (full ALHVR-EL) | −0.0169 / −0.1324 / −0.0312, **WORSE** on all three primaries in all four cell sets | **not supported; contradicted** |
| Track D (5% base + 12 cells; oracle-selected) | crack cells (Tc) − random (R) | relF1@2 +0.030 [+0.020, +0.042] in every cell set | supported for crack, **oracle-selected** |
| Track M FINAL (training machine; clean test) | 5-seed SUP100 ensemble with crack bias − single model | FINAL − single +0.018 [+0.013, +0.025] | **supported** (PASS on crack IoU and relF1@2 at both biases; locked protocol, val-only choices) |
| Track M R2 to R5 (single-model changes at 100%) | Dice-12; ResNet-50; +107 E-SCDD cells; 2x resolution | R2 Dice-12 WORSE on crack (−0.0106, thr 0.0100, clean); R2c Dice on 3 classes n.d.; R3 ResNet-50 WORSE on inactive (−0.0251, thr 0.0227, clean) | **not supported** under the house recipe |
| MIM5 / DDeP5 (second machine, 5% labels, house fine-tune) | pool feature learning − A5c-f1 | MIM5 n.d., every estimate negative (crack −0.0116, thr 0.0186; ...); DDeP5 n.d., small positive (crack +0.0070, thr 0.0100) | **not supported at 5% under the house fine-tune.** |
| Encoder audit (house fine-tune) | cosine of final vs initial conv weights per ResNet-34 stage | layer3 0.005 to 0.018, layer4 −0.001 to 0.001 | **supported** for ResNet-34 U-Net++ with ImageNet and MIM inits, at 5% and 100% |
| protocol_100 opening 1 (second machine, 5 v 5) | MIM100-PF − SUP100-PF | crack +0.0048 (thr 0.0113) all 50 / −0.0017 (0.0100) without noisy | **not supported** at 100% labels; closed per protocol |
| protocol_100 opening 2 | CP100 − SUP100-g (crack copy-paste) | CP100 − SUP100-g C1 crack +0.0076 (0.0307) / +0.0003 (0.0100) | **not supported** at 100%; closed, with a seam-sensitivity caveat |
| protocol_100 opening 1 | SUP100-PF − SUP100-g (PF vs house fine-tune) | crack −0.0012 (0.0316) / −0.0061 (0.0100); relF1@2 +0.0117 / +0.0050; inactive +0.0150 / +0.0143; n.d. | **not supported on test.** |
| PF2 (second machine, seeds 5 to 9; E1 opening #1) | PF − house, E1 inactive IoU | 0.0481 → 0.2371, +0.1890 (thr 0.0433) BETTER | **supported: replicated on new seeds, same E1 cells** |
| PF2 (test) | PF − house, test crack relF1@2 | relF1@2 0.8730 → 0.8847, +0.0117 / +0.0120 (all 50 / clean; floor 0.0100) BETTER | **supported narrowly:** one rule pass, by 0.0017 / 0.0020, resting on a few cells |
| PF2 (E1 crack recall) | PF − house | +0.0271 (thr 0.0370) n.d. | **not replicated** |
| PF2 (ResNet-50 under PF) | RN50-PF − SUP100-PF, test inactive | 0.4557 → 0.4269, −0.0289 (thr 0.0251) WORSE in both sets | **not supported:** FAIL; RN50 closed under PF |
| PF2E (5-member ensembles; E1 opening #4) | E-PF − E-house, E1 inactive IoU | E1 inactive IoU 0.0665 → 0.2807, +0.2141 [+0.0303, +0.3820] PASS (71-cluster bootstrap) | **E1 inactive: supported with qualifications**; **test: not supported** (n.d.) |
| THIN-B3 Skeleton Recall (E1 opening #2) | SKR − SUPPF | test crack IoU −0.0136 / −0.0140 (thr 0.0100) WORSE; E1 crack relF1@2 +0.0590 (thr 0.0392) BETTER | **not supported** (FAIL by the pre-registered rule) |
| THIN-B3 soft clDice | CLD − SUPPF | B5 relR@2 at relP@2 ≥ 0.90 −0.0374 / −0.0376 (thr 0.015) WORSE | **not supported:** FAIL; no better at matched precision |
| THIN-B3 scuff class (B3) | B3 − SUPPF | all co-primaries n.d.; train scuff IoU 0.000 in all 5 seeds | **not supported:** the class was not learned |
| A8 screen (second machine, 2 seeds; F51, no test, no E1) | DINOv3 ConvNeXt-T − ImageNet ConvNeXt-T, F51 crack AP | A8 − A8c −0.0243, module-bootstrap lower bound −0.0463 (GO needs > 0) | **not supported:** KILL ("no sign of a gain", not "worse") |
| HC synthetic half-cuts (E1 opening #3) | HC − SUPPF | test crack IoU +0.0092 / +0.0089 (thr 0.0100); E1 relF1@2 +0.0135 (thr 0.0429), E1 inactive −0.0002: all n.d. | **not supported** (n.d.) |
| B6 (module-grouped 5-fold CV, 2 seeds, training machine) | PF − house, pooled out-of-fold inactive IoU | inactive IoU Δ −0.0144, two-stage CI [−0.0977, +0.0570] | **not detectable** (n.d., low power); **an in-distribution gain as large as the E1 gain is excluded** |
| SKR2 Skeleton Recall w 0.1 (E1 opening #5) | SKR2 − SUPPF, E1 crack relF1@2 | E1 crack relF1@2 +0.0364 (thr 0.0351) BETTER | **supported narrowly** (one co-primary, by 0.0013; ~10% family-wise false-BETTER over 7 co-primaries) |
| HC2 (E1 opening #5) | HC2 − SUPPF, test inactive | test inactive −0.0256 / −0.0259 → G1 TRIP | **not supported:** FAIL |
| SKR2E (ensembles; E1 opening #6) | E-SKR2 − E-PF at the headline pair | G2a test relP@2 −0.0379 and G2b E1 crack-free px ×2.12 TRIP → FAIL | **not supported:** FAIL; E-PF at argmax stays the recommended deployable candidate |
| SKR2C (fresh seeds 10 to 14; E1 opening #7) | SKR01 − SUPPF, singles (R) and ensembles (D) | Named claim: REPLICATED does not hold (seed-aware CI [−0.0015, +0.0590]) | R FAIL, D FAIL; the E1 difference appeared again but replication at recipe level was not shown |

- Verdict wording of the P-series rows (E, handbook doc 11 conventions): "**passes / fails / n.d.** is the locked rule (P8 rule 1: Δ > max(0.01, 2·√((sd_A² + sd_B²)/3)) on any primary, none worse)." "**robust** means the 95% image-bootstrap CI excludes 0 and the sign survives removing the top-3 cells."

### T22. Inference cost per cell of the E1 candidates (CPU and GPU)

Placement: appendix. Tags: E (values); S only in the quoted Reading note.

Network time per cell, copied from INFERENCE_COST.md sections 3.3 (CPU of the second machine, 16 threads, batch 1) and 3.4 (GPU of the training machine, one RTX A6000, fp32, TF32 off). Median over the timed cells, p90 in parentheses, [n] = timed cells. x C1 = time over C1 time on the same device. Closes gap G-N7.

| Row | Forwards per cell | GFLOPs per cell | CPU s per cell, batch 1, 16 threads: median (p90) | x C1 (CPU) | GPU s per cell, batch 1: median (p90) [n] | x C1 (GPU, batch 1) | GPU s per cell, batch 8: median (p90) [n] | Peak GPU alloc b1 / b8 (MiB) |
|---|---|---|---|---|---|---|---|---|
| C1 | 1 | 148 | 0.216 (0.233) | 1.0 | 0.0112 (0.0112) [200] | 1.0 | 0.0099 (0.0099) [200] | 374 / 2,289 |
| E-PF | 5 | 740 | 1.40 (1.48) | 6.5 | 0.0559 (0.0561) [200] | 5.0 | 0.0491 (0.0492) [200] | 825 / 3,076 |
| C1-D4 | 8 | 1,184 | 2.23 (2.37) | 10.3 | 0.0911 (0.0915) [200] | 8.2 | 0.0800 (0.0800) [200] | 448 / 2,873 |
| C2 | 8 | 1,744 | 3.88 (4.38) | 18.0 | 0.174 (0.177) [200] | 15.5 | 0.133 (0.134) [200] | 445 / 2,993 |
| C3 | 40 | 8,722 | 16.6 (19.2), 10 cells | 76.9 | 0.855 (0.862) [200] | 76.6 | 0.675 (0.675) [200] | 819 / 3,702 |

- What is timed (E, INFERENCE_COST.md section 1): wall time "of the whole predict for one batch (all members, all views, the D4 rotate / flip and its inverse, softmax, view and member average) divided by the batch size. It excludes image read, resize, normalise, argmax / dump maps and disk writes". Inputs: random float32 tensors (B, 1, 512, 512); no image, label or prediction of any set was read.
- D4 views (E): in the deployed path the D4 views are not batched (INFERENCE_COST.md section 1). C2 with the 8 views in one batch: GPU 0.134 (0.135) [200] s per cell (section 3.4); CPU "4.43 s against 3.88 s per cell for the deployed sequential path" (section 3.2).
- Host (E, INFERENCE_COST.md section 3.4): "GPU 6 had no other process" before every config; "The host was shared". Reading, as written there (S): "host load can only make these numbers slower, so they are upper bounds for an idle A6000 at these settings." "For deployment, C2 at batch 1 is about 0.17 s of network time per cell on one A6000, about 20,000 cells per hour; the E1 dump jobs took about 100 s for 106 cells (section 4), so network time (106 x 0.174 = 18 s) is under a fifth of the observed job time; the rest is start-up, data and writes."

## 3. Considered and not tabulated
- `results/C3_S5_LOOK.md`: one seed per row, descriptive; superseded by `C3HRNET_READ.md`.
- `results/W1G_FIRST_READ.md`, `results/ROWS2_PRELIM.md`: provisional reads superseded by `W1C_READ.md`, `ROWS1_READ.md`, `ROWS2_READ.md`.
- `results/W2A_GATES.md`: gate verdicts only (ema hash PASS, swad pre-screen PASS, spd mechanism FAIL); enters T16a through W2A_READ.md.
- `results/stageA/`, `results/stageB/` (B1, B3, F2, SAMECELL), `results/stageC/` (CV5V3_BUILD, GAP_CENSUS, LABEL_VERSION_STRATA):
  protocol evidence; cited through `benchmark/PROTOCOL_v0.2.md` in T1, T2, T4 and through `benchmark/PROTOCOL_v1.0.md` in T4, T20.
- `results/stageB/U2U4_READ.md`: all descriptive; only the PF level on U2 enters T14.
- Per-source and per-class CV5 values of the final TTA read (`final_tta_read/read.txt`, `class_guard.txt`) and per-source values of
  the E1 read beyond T10: available, not tabulated.
- Pre-protocol results (P-series, Track M, PF2 to SKR2C): now T21 (appendix), traced to handbook doc 11 and, where they print the
  same string, to the cited session records.
- `thesis/RELATED_WORK.md` (f2a6adcd; gap G-N10): the related-work table (R rows read in full text, A rows abstract-level), with its
  own generator `build/related_work/gen.py`, `related_work.tex` and `RW_SOURCES.tsv`. Not repeated here; T13a keeps the published
  rows of the test50 public table.
- `thesis/INFERENCE_COST.md` (1e5a9002) sections 3.1, 3.2 and 4 (unit runs by thread count, additivity check, dump wall times
  on the training machine): available, not tabulated; T22 copies sections 3.3 and 3.4.
- `results/HOUSECS_READ.md` (9efd43ac) sections 4 to 6 (guard values, per-seed deltas, levels): available, not tabulated; T7a
  carries its contrasts and the guard items outside a bound.
- Pending, no numbers: the U2 TTA
  re-run, la_ce_full.

## 4. Regenerate
`cd T/thesis/build && python3 -I make_tables.py` rewrites THESIS_TABLES.md, thesis_tables.tex and SOURCES.tsv, and stops on any
anchor or value mismatch. If a source file changes, its md5 in SOURCES.tsv changes on the next run.
