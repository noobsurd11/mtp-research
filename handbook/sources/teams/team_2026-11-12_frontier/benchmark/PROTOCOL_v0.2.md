# Benchmark protocol v0.2 (defect segmentation in EL images of solar cells)

Protocol editor, 15 Nov 2026; state of the files at 16:00 IST. Replaces `benchmark/PROTOCOL_DRAFT.md` (v0.1, 12 Nov) as the working text, for a reader who will run a method under it or cite it. Written from files only: no training, no GPU job, no sealed label or prediction read.
**Tags.** E = measured in our files. S = judgement. D = decision of the lead or the user, with the file that records it. Status words ("pending", "not built") give the state found on 15 Nov.
**Short paths** (relative to `team_2026-11-12_frontier/`): `draft` = `benchmark/PROTOCOL_DRAFT.md`; `T12` = `cards/T12_benchmark_protocol_spec.md`; `W2`, `W3` = `cards/WAVE2_REVIEW.md`, `cards/WAVE3_REVIEW.md`; `W1G`, `W1C`, `ROWS1` = `results/W1G_FIRST_READ.md`, `results/W1C_READ.md`, `results/ROWS1_READ.md`; `A1`, `A2m`, `A2e`, `A4`, `A5`, `A6` = `results/stageA/` `A1.md`, `A2_metric_probe.md`, `A2_P1_G5.md`, `A4.md`, `A5_head_res_ceiling.md`, `A6_duplicates.md`; `B1`, `B3` = `results/stageB/` `B1_classbias_xfit.md`, `B3.md`; `RA`, `RB`, `RR1` = `harness/` `REVIEW_STAGEA.md`, `REVIEW_STAGEB.md`, `REVIEW_ROWS1.md`; `HO5` = `migrate/HANDOVER.md` section 5; `LAB` = `benchmark/LABELS_V11.md`; `SPL` = `benchmark/splits/README.md`; `POOL` = `benchmark/splits/pool_t9.README.md`; `TEST` = `benchmark/test_openings.md`; `log` = `log.md` (entry time given); `brief` = `log/brief_protocol_v02.md` (ruling number given).

## 0. The protocol in twelve lines
1. **Data.** BenchmarkEL `dataset_20211104`: 582 cells = 478 train / 54 val / 50 test, 24 classes (E `BRIEF.md` section 2). Label set v1.1; ignore pixels are not scored (E `LAB`; `W1C` header).
2. **Sets.** Pool P532 = all labelled train + val cells. Sealed: the legacy test set (50 cells) and E1 (106 cells, unseen modules). Development never reads a sealed label or prediction (D `brief` 1).
3. **Split.** CV5-G = `benchmark/splits/cv5v2.json`: 5 folds, 330 module groups, every pool cell scored once out-of-fold (E `SPL`).
4. **Headline card.** Crack relF1@2 with relP@2 and relR@2; strict crack IoU; inactive IoU; mIoU over 13 robust classes (mIoU-R13). Tolerance 2 px (D `brief` 4; E `A4`).
5. **Guards with every row.** Crack width ratio, false crack px on crack-free cells, component recall and precision (section 5.2).
6. **Operating points.** OP-A (argmax) and OP-W (width-matched) decide. OP-F is printed and decides nothing. OP-C is the comparator for arms that shift class priors; its review is not finished (section 5.3).
7. **Statistics.** Two-stage group bootstrap; margin M = max(0.01, 2 x SE of the A/A contrast), per machine; a read never mixes machines (section 5.4).
8. **Seeds.** Screen = 2 seeds, table row = 5 seeds. A screen flag is not a result (D `brief` 6).
9. **Entries.** Four entry classes and two data tracks. Every row carries a fairness record and passes the leakage guards (section 6).
10. **Legacy test set.** Continuity track only: 18 counted openings exist, no further one is planned (E `TEST`; D `brief` 1).
11. **E1.** One registered opening near the end, at most 3 candidates; still to be confirmed with the user (D `HO5` L10). Development proxies never support a claim about E1 (section 8).
12. **Suite so far.** PF, HOUSE and five rows from EL papers and standard decoders, on cv02. No row beats PF or HOUSE (E `ROWS1`; section 7).

## 1. Why published EL segmentation numbers cannot be compared
- The audit of v0.1 stands: 12 problems with their evidence (E, R `draft` section 1). In short: three releases of one dataset (582, 642 and 695 cells) with reshuffled splits (186 of 582 cells change split between the first two); augmented and synthetic images in train folders; 7 test cells that are the same physical cell as a train cell; validation sets drawn from test data; different class lists and metric conventions; strict IoU on 1 to 2 px labels (a perfect crack mask shifted by 1 px scores IoU 0.56); single runs without intervals.
- Reading (S `draft` section 1): a comparable number states release, split, class list, metric convention, operating-point rule and seed count together. This protocol fixes all six.
- New since v0.1 (E `ROWS1` sections 1, 3): under equal training on CV5-G the models of the EL papers sit below the baseline. UCF-EL's DeepLabV3 / ResNet-50 reaches 0.287 strict crack IoU and 0.767 relF1@2, Pratt's weighted cross-entropy 0.258 and 0.751, against PF at 0.365 and 0.844. Hanifi's VGG-16 U-Net is close (0.349 and 0.838).
- Owed (D `brief` 10; `T12` section 7 items 4, 5): this section rewritten as an audit with counts of papers per problem, and a related-work table (Open 9).

## 2. Corpus and labels
### 2.1 What exists (E `draft` sections 2.1, 2.2)
816 real labelled cells in the three BenchmarkEL releases and E-SCDD, 787 unique physical cells, 463 physical-module groups. The 93 synthetic E-SCDD files are excluded everywhere.

| Role | Cells | Use in v0.2 | Evidence |
|---|---|---|---|
| legacy train + val = P532 | 478 + 54 | development and the in-distribution table; by source ARTS 182, BMRK 50, CFVS 169, CSIR 114, SDLE 17 | E `draft` section 2.2; `A2e` section 2 |
| legacy test | 50 | sealed; continuity only | D `brief` 1 |
| E1 (new in release `20221008`, not in the unlabelled pool) | 106 | sealed; unseen modules | D `brief` 1 |
| `_rf` cells (Hanifi labels) | 117 | development reads only (sets F51, H36) | E `B3` sections 2, 4 |

### 2.2 Label set v1.1 (E `LAB`; D user, `log` 12 Nov 20:15)
- v1 = the project's `masks_escdd`. v1.1 = v1 with every scuff or star pixel set to ignore (255) and `BMRK_00031_cell0091` given back its `20220723` mask (in v1 it carries the mask of `BMRK_00075_cell0255`).
- Size of the change: train 16 cells and 3,484 px to ignore; val none; test 2 cells and 236 px. Train crack cells 209 to 206. Inactive is untouched.
- v1.1 stays the training and scoring label set (D `W1C` section 4). Ignore pixels are not scored.
- Training on v1.1 instead of v1 changes no pooled metric measurably (PFV1 minus PF, 2 seeds, both scored on v1.1): strict crack IoU +0.0004 [-0.0058, +0.0069], relF1@2 -0.0014 [-0.0099, +0.0064], inactive IoU -0.0140 [-0.0690, +0.0362], mIoU-R13 -0.0020 [-0.0081, +0.0038] (E `W1C` section 4). The fix is a scoring-side fix (D `brief` 3).
- Label issues 3 to 8 of `draft` section 2.5 (mask copies, the one double annotation, `_rf` crack labels, the E1 label convention, noisy images, dotted labels) are unchanged.
### 2.3 Terms of use (E, R `draft` section 2.3)
BenchmarkEL has no licence file. E-SCDD is MIT on Hugging Face and re-hosts BenchmarkEL images. UCF-EL has no licence file in the local copy. ELPV (the source of the BMRK cells) is reported as CC BY-NC-SA 4.0, unverified. The two data tracks of section 6.2 follow from this. How the benchmark itself is released has no ruling (Open 8).

## 3. Sets and split
### 3.1 CV5-G (`benchmark/splits/cv5v2.json`, md5 441d118f)
- 5 folds with held-out sizes 107 / 111 / 104 / 104 / 106; 330 physical-module groups (`cv5v2_groups.tsv`, md5 e44f0668); no group of that file is cut across folds; made from the frozen B6 folds by moving 4 cells (E `SPL`).
- Every pool cell is scored once, by a model that did not train on its fold; scores are pooled over the 532 cells (E `W1C` header).
- **Known defect.** Two physical cells sit twice, in different folds: `ARTS_00165_r12_c5` (fold 3) = `ARTS_00166_r12_c5` (fold 1), and `CFVS_00076_r1_c1` (fold 2) = `CFVS_00082_r1_c1` (fold 4) (E `benchmark/splits/dup_crossfold_v1.tsv`; lead's visual check, `log` 15 Nov 13:51).
- **Ruling** (D `log` 15 Nov 13:51; `brief` 2): the split is not changed, so the 5-seed baselines stay paired with every arm. Final tables score 528 cells (these 4 excluded) and print the 532-cell value beside it. Until the read tools have a score-exclude option, screens are on 532 cells and say so. Every CV5-G number in this file is on 532 cells.
- Owed (E `log` 15 Nov 13:51): the score-exclude option, and a masked audit of the other same-position cross-fold pairs (357 same-source pairs; a first matcher did not separate them cleanly).
- Limits (E `SPL`; `draft` section 3.2): BMRK and SDLE cells have no module id, so two cells of one module can sit in different folds; the pool has 0 half-cut cells, so CV5-G cannot measure unseen layouts.
### 3.2 Legacy test set (continuity track)
- 18 counted openings since 24 Oct, the last on 14 Nov; nothing is registered and unopened. Before 24 Oct the set was scored in every experiment, uncounted (E `TEST` sections A, B, D).
- No further opening is planned (D `brief` 1). Past numbers stay as published: legacy split, v1 labels, reported for all 50 cells, the clean 49 and the clean 42 without twins (E `draft` section 3.1).
### 3.3 E1 and the sealing rule
- 7 registered openings exist; the last is SKR2C on 14 Nov (E `log` 14 Nov 05:58).
- One more registered opening near the end, with at most 3 zero-shot candidates named by a rule written beforehand (D `HO5` L10; `W3` section 6 G15). **Pending:** the user's confirmation in the last week (`brief` 1).
- Sealing (D `brief` 1; `HO5` L2): no development step reads a label or a prediction of a legacy test or E1 cell. The duplicate tool may read sealed images as pixels and writes pair lists only.
- `forbidden_v1.txt` holds the 167 stems that no training list may contain: legacy test 50 + ext117 117 (E `SPL`).
- The cell tables carry label summaries of the 156 sealed rows; no reader uses or prints those columns (E `RA` "Sealed sets"; D `log` 15 Nov 12:50; done in code in `B3` section 2).

## 4. Class list and label policy
- **Output.** The 24 legacy classes (E `BRIEF.md` section 2); every tranche 1 row predicts 24 channels (E `RR1` section 2).
- **mIoU-R13** = mean IoU over the 13 robust classes: background, ribbons, padding, border, gridline, sp mono, crack, sp multi, material, frame edge, splice, inactive, edge dark (E `draft` section 4.1). The per-class IoU of the 13 is printed beside it (D `W2` section 5 item 6).
- An absent class is never scored 0 or 1; all-class mIoU is printed only as "mIoU over the k classes with ground truth", with k (S `draft` section 4.2, unchanged).
- Weak classes on CV5-G at argmax (PF, gaint / cv02): gridline 0.302 / 0.304, splice 0.021 / 0.013 (E `B1` section 2c).
- Crack inside inactive: the single-label masks are scored as they are (S `draft` section 4.4, unchanged).
- Of the classes added by later releases, only scuff and star occur in the 582 legacy cells; v1.1 ignores both (E `LAB` section 1).

## 5. Metrics, operating points, statistics
### 5.1 Headline card (D `brief` 4; definitions E `draft` section 5.1)
| Metric | Definition | Place in v0.2 |
|---|---|---|
| crack relF1@2, with relP@2 and relR@2 | P = share of predicted crack px within 2 px of ground-truth crack; R = share of ground-truth crack px within 2 px of a prediction | first column; never R without P; relF1@1, @2, @3 and the width ratio are printed together (D `HO5` L7; `A2m` rule 6) |
| strict crack IoU | TP / (TP + FP + FN) from one confusion matrix over all scored pixels | beside relF1@2 |
| inactive IoU | same | printed; promotes no trained arm at 2 seeds (section 5.4) |
| mIoU-R13 | section 4 | the balance metric |

- **Tolerance stays 2 px** (E `A4`; `RA` A4 PASS). The 95th percentile of the distance between two drawings of one crack is 2.000 px [2.000, 2.000] on 6 pairs of different images without crack growth, and 2.000 px [1.414, 2.000] on the one double annotation. The rule moves the tolerance only if the low end of the interval is above 2.5 px on both. The evidence is thin (6 pairs, 1 double annotation): it supports keeping 2 px and could not support a move (S `A4` section 3).
- **Centreline F1@2 is not eligible as a headline.** It rewards a 1-px dilation of the prediction: +0.0137 [0.0103, 0.0170] on gaint, +0.0136 [0.0107, 0.0165] on cv02. relF1@2 does not: -0.0039 [-0.0087, 0.0011] and -0.0037 [-0.0083, 0.0006] (E `A2m` section 2).
- **No headline change in v0.2.** The probe's leading metric did not reproduce between the machines (relF1@2 on gaint, strict IoU on cv02), so relF1@2 keeps its place (E `A2m` section 3; `RA` A2; D `log` 15 Nov 12:50).
- Strict crack IoU is read beside its label-noise band of 0.48 to 0.60, measured on the legacy test masks (E `draft` section 5.2). The band is not re-measured on the pool.
### 5.2 Guards, printed with every row (D `brief` 4; `W2` section 5)
| Guard | Definition | Use | Baseline value |
|---|---|---|---|
| crack width ratio | predicted / ground-truth crack px | pass band 0.85 to 1.15 x the baseline's, pooled and per source with at least 40 cells (ARTS, BMRK, CFVS, CSIR) (D `W2` X4; `A2m` rule 6) | 1.002 (PF, cv02; E `W1C` section 1) |
| false crack px | predicted crack px on the 303 crack-free cells | printed | 357 (same) |
| cells with false alarms | share of crack-free cells with at least 50 false px | printed | 0.8% (same) |
| component recall and precision | crack components of at least 20 px (`draft` section 5.1) | printed, never one without the other | 0.800 and 0.906 (PF, gaint; E `W1G`) |

- The width band stays a pass condition whatever metric leads the table (D `HO5` L7; `W3` Y13).
### 5.3 Operating points
| Point | Definition | Role | Evidence |
|---|---|---|---|
| OP-A | argmax | decides | D `brief` 5 |
| OP-W | crack bias cross-fitted on the other folds so that the width ratio matches the baseline's | decides | D `brief` 5; E `A2m` section 1 |
| OP-F | crack bias cross-fitted for F1 | printed, decides nothing | unstable under A/A: -0.0118 [-0.0357, -0.0005] on crack IoU; the fitted bias ranges from -0.5 to +3.0 between seeds and folds (E `W1C` section 2) |
| OP-C | argmax plus per-class biases for 11 of the 13 robust classes (background and crack stay at 0), fitted on the other 4 folds | comparator for arms that shift class priors (D `HO5` L3; `W3` Y6) | definition E `B1` section 1; **review not finished** |

- **OP-C status as found (15 Nov 16:00).** The builder reports a pass under its pre-set rule on both machines: mIoU-R13 +0.0137 [+0.0107, +0.0169] on gaint and +0.0126 [+0.0077, +0.0167] on cv02 (E `B1` section 2b). `RB` exists, but its verdict for this item is still an unfilled placeholder; the reviewer's own recompute of the gaint value agrees (+0.0137; E `RB` section 4). Until `RB` gives a verdict, OP-C is "pending review" and decides nothing.
- The rule that will use it (D `W3` Y6, G18; `HO5` L3): a gain in inactive IoU or mIoU-R13 from a prior-shifting arm counts only if it is present at OP-A and against the baseline at OP-C. Gridline and splice are printed beside mIoU-R13 whenever OP-C is used (S `B1` section 3): the OP-C gain is mostly gridline (+0.060 / +0.058) and splice (+0.092 / +0.075) (E `B1` section 2c).
- A bias is an operating-point choice, not a gain: OP-F moves recall +0.013 and precision -0.018 while relF1@2 does not move (E `W1G` item 1).
- Final-step weights only; no best-validation checkpoint (S `draft` section 5.3 item 1; applied in `W3` section 2, nnunet line).
### 5.4 Statistics
- **Interval.** Two-stage group bootstrap: 330 module groups, then one seed per fold and arm; 2,000 draws (E `A1` section 1). The seed stage is unchanged (D `log` 15 Nov 12:50). It is conservative: the spread of A/A deltas is 0.48 to 0.74 of the bootstrap SE (E `A1` section 2).
- **Margin.** M = max(0.01, 2 x SE of the A/A contrast), per machine (D `log` 13 Nov 09:25 and 15 Nov 12:50):

| Machine | A/A read | Strict crack IoU | relF1@2 | mIoU-R13 | Inactive IoU | Evidence |
|---|---|---|---|---|---|---|
| cv02 | PF seeds 5 to 9, all 15 two-seed splits | 0.010 | 0.010 | 0.010 | 0.049 | E `A1` section 3; `W1C` section 2 |
| gaint | PF seeds {5, 6} against {7, 8} | 0.010 | 0.010 | 0.010 | 0.054 | E `ROWS1` section 4 |

- The screen rule holds its error rate: 0 of 15 A/A splits would be promoted on any headline metric (E `A1` section 3; `RA` A1).
- **Seeds.** Screen = 2 seeds; table row = 5 seeds (D `brief` 6; `log` 12 Nov 19:56; see Open 6). A screen pass is a promotion to a 5-seed confirmation, never a result (D `W2` X2).
- **Crack gain.** It counts only if it holds at OP-A and at OP-W inside the width band, with delta at least M and the 95% interval above 0 (D `brief` 6; `A5` section 1).
- **Machines.** A read never mixes machines (D `brief` 6). The two PF baselines agree: 0.365 / 0.844 / 0.503 / 0.612 on cv02 and 0.365 / 0.844 / 0.503 / 0.613 on gaint, for strict crack IoU / relF1@2 / inactive IoU / mIoU-R13 (E `ROWS1` sections 1, 4).
- **Inactive.** Pooled inactive IoU promotes no trained arm at 2 seeds: two identical recipes differ by +0.021 from seeds alone (E `W1C` section 2; D `HO5` L4, finding Y1 of `W3`). Inactive arms are read by region counts (recall of regions of at least 100 px, predicted inactive px on the 484 inactive-free cells, inactive precision; `W3` Y1) or at 5 seeds.
- **Smallest detectable effect** at 2 / 3 / 5 seeds (E `A1` part (e); power 0.8, `T12` section 1): strict crack IoU 0.0083 / 0.0067 / 0.0052; relF1@2 0.0087 / 0.0071 / 0.0055; mIoU-R13 0.0067 / 0.0055 / 0.0042; inactive IoU 0.0518 / 0.0423 / 0.0328.
- **Multiplicity.** One pre-declared primary per arm; the ledger records the number of contrasts read (D `W2` X2).

## 6. Entry classes, tracks and what every row declares
### 6.1 Entry classes (D `brief` 7)
| Class | Content | Rule | Evidence |
|---|---|---|---|
| (a) trained single model | one set of weights, one forward pass | the default column | D `brief` 7 |
| (b) decision layer | a post-hoc step on a trained model (class biases, rules, refiners) | labelled as such; never in the default column; credited only against the same model's argmax | D `HO5` L3; `W3` G19; `B1` section 3 |
| (c) ensemble | several models or views | always printed beside the equal-cost comparator. Reference: a 2-seed PF ensemble is +0.0116 strict crack IoU above single models, on both machines | E `A2e` section 3; D `W3` G16 |
| (d) uses source metadata | source id at test time | a flag; a separate row class, never in the default track | D `log` 13 Nov 09:25 |

### 6.2 Data tracks (D user, `log` 15 Nov 12:40)
- **Main track:** only data and weights with clear terms. The main model and the benchmark tables are in this track.
- **Extra-data track,** labelled as such: may train on UCF-EL and MultiSolSegment, which state no licence. Nothing from them is redistributed.
- A row with research-only weights is a benchmark row only and says so (D `log` 15 Nov 12:49).
- Before any use of UCF-EL: 227 of its images are excluded by the near-duplicate rule (NCC >= 0.80 against our cells; E `A6` section 2.4).
### 6.3 The five tracks of v0.1 (`draft` section 6)
T1 full labels is in force on CV5-G. T3 unseen module is the E1 opening plus the development instrument of section 8. The cost columns of T4 deployment are now in the fairness record of section 6.4; its latency item has no ruling (Open 7). T5 post-evaluation is deferred (section 8.2). T2 label efficiency has no ruling and no CV5-G run (Open 7).
### 6.4 Fairness record per row (guard G16; D `brief` 8; `W3` section 6)
- Every row states: parameters, GFLOPs at 512 px, output stride, steps x batch, pretraining data and weights with their licence, peak memory, step time, and every deviation from the paper the row stands for. The record of tranche 1 is in `RR1` section 3.
- Above 2x the house training or inference cost, the PF 2-seed ensemble is printed as the equal-cost comparator (D `W3` G16).
- A row with an output stride above 1 is printed with its stride and the head-resolution ceiling (E `A5` section 3). For stride 4, as strict crack IoU / relF1@2: the stride-1 model pooled to stride 4 gives 0.159 / 0.533 at OP-A and 0.279 / 0.717 at OP-W; the ground-truth lower bound of the ceiling is 0.521 / 0.955 at width ratio 1.365. The ceiling bars nothing: a stride-4 row that passes the standard rule is a candidate like any other.
- Confirmed on trained rows (E `ROWS1` section 3): stride 4 costs 0.02 strict IoU and 0.02 relF1@2 once width is matched; stride 8 costs about 0.08 to 0.10 on both.
### 6.5 Leakage guards (guard G14; D `brief` 9; `W3` section 6)
- **One pool list for every pool arm:** `benchmark/splits/pool_t9.txt`, 6,424 of the 11,938 pool cells on disk (E `POOL`; D `log` 15 Nov 12:50; `HO5` L11). A pool cell is out if, against any labelled or sealed image, it shares the module, has the same md5, has embedding cosine >= 0.98, or has band-pass NCC >= 0.80.
- The threshold first specified (0.830) was unusable: 6.6% false matches between different sources (E `A6` section 2.1). Not searched: the 159k full pool and two `_rf` images (E `POOL`).
- **Third-party weights trained on SCDD or E-SCDD are forbidden.** Generic public weights (SAM 2, DINOv2, ImageNet) are allowed and named (D `W3` G14).
- **A teacher, generator or labeller never saw the student's held-out fold;** the assert fails closed (D `W3` G14).
### 6.6 Reporting governance (D `brief` 10; `T12` section 7; `W3` section 2: "reporting_governance: GO, week 2", with the G13 to G16 declarations added to the info sheet)
1. **Model info sheet per entry:** split name and md5; pool and extra data with the leakage exclusions applied; declared resources (source id at test time: yes or no); seeds; machine; operating-point rule; training compute; dump manifest md5s; and the declarations of guards G13 (external data provenance), G14, G15 (unseen-module instruments) and G16. Its generator `scripts/bench_infosheet.py` is not built.
2. **Reporting checklist, 10 items:** release and label set; split and grouping; class list and absent-class rule; metric definitions with tolerance and distance convention; operating point; seeds and machine; interval method; number of contrasts and set openings; with and without noisy and flagged cells; ranking with ties (waits for `rank_stability`, section 8.2).
3. **Ledgers:** `TEST` and `team_2026-10-31_next/e1_openings.md`; one opening per locked protocol, registered before reading.
4. **Related-work table:** every published EL number with release, split, metric convention and an interval, or "no interval reported". Not written.

## 7. Baseline suite so far
All rows: cv02 unless stated, CV5-G out-of-fold over 532 cells, label set v1.1, 20,000 steps x batch 8, 512 px, ImageNet weights, argmax, mean over seeds. Every row except HOUSE uses the encoder-preserving fine-tune (PF) (E `ROWS1` header and section 1; weights, GFLOPs and stride E `RR1` section 3).

| Row | Architecture | Seeds | GFLOPs | Stride | Strict crack IoU | relF1@2 | relP@2 / relR@2 | Inactive IoU | mIoU-R13 | Width ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| PF (comparator) | U-Net++ / ResNet-34 | 5 to 9 | 148.0 | 1 | 0.365 | 0.844 | 0.894 / 0.799 | 0.503 | 0.612 | 1.00 |
| PF on gaint | as PF | 5 to 8 | as PF | 1 | 0.365 | 0.844 | 0.896 / 0.799 | 0.503 | 0.613 | 1.009 |
| HOUSE | as PF, plain fine-tune | 5, 6 | as PF | 1 | 0.382 | 0.850 | 0.897 / 0.807 | 0.522 | 0.609 | 1.11 |
| unet_r34_pf | U-Net / ResNet-34 | 5, 6 | 63.4 | 1 | 0.364 | 0.843 | 0.896 / 0.795 | 0.522 | 0.612 | 1.00 |
| hanifi_vgg16_unet_pf | U-Net / VGG-16 (Hanifi et al.) | 5, 6 | 199.0 | 1 | 0.349 | 0.838 | 0.882 / 0.798 | 0.498 | 0.610 | 0.96 |
| dlv3p_r34_pf | DeepLabV3+ / ResNet-34 | 5, 6 | 62.4 | 4 | 0.354 | 0.835 | 0.884 / 0.791 | 0.478 | 0.609 | 1.21 |
| ucf_dlv3_r50_pf | DeepLabV3 / ResNet-50 (UCF-EL's model) | 5, 6 | 326.4 | 8 | 0.287 | 0.767 | 0.809 / 0.729 | 0.497 | 0.574 | 1.23 |
| pratt_dlv3p_wcec | DeepLabV3+ / ResNet-34, the paper's weighted CE | 5, 6 | 62.4 | 4 | 0.258 | 0.751 | 0.648 / 0.892 | 0.506 | 0.604 | 3.05 |

- **No row beats PF or HOUSE** (E `ROWS1` section 3). Row minus PF, strict crack IoU at OP-W (E `ROWS1` section 2): unet_r34_pf 0.0000 [-0.0076, +0.0088]; hanifi_vgg16_unet_pf -0.0134 [-0.0244, -0.0040]; dlv3p_r34_pf -0.0242 [-0.0384, -0.0098]; ucf_dlv3_r50_pf -0.0967 [-0.1121, -0.0787]; pratt_dlv3p_wcec -0.0691 [-0.0851, -0.0517]. On inactive IoU no row is separated from PF.
- **HOUSE against PF** (E `W1C` section 3): strict crack IoU +0.0173 [+0.0107, +0.0241] at OP-A and +0.0110 [+0.0028, +0.0187] at OP-W; relF1@2 inside M. HOUSE draws cracks 11% wider and doubles the false crack px on crack-free cells (732 against 357). This is a screen flag (2 seeds), not a result.
- **Ruling** (D `W1C` section 3): PF stays the comparator of every arm; HOUSE is a table row of its own; an arm that claims an in-distribution crack gain is also printed against HOUSE.
- Limits (E `ROWS1` section 3): 2 seeds per row, so every row except PF is a screen read; one machine; pool cells only; the ucf row uses ImageNet weights (not COCO) and no auxiliary head; the pratt row uses the house augmentation with the paper's loss.
- **Planned or training, no numbers yet.** Tranche 2: segformer_mitb2_pf, hrnet_w18_unetpp_pf, skr01_pf_v11 (in build, not launched; E `log` 15 Nov 15:46). Wave 2a arms on gaint: rcs, ema_wise_posthoc, soft_band_jml, jml_hard, swad_const, encoder_spd, encoder_spd_ctrl (27 of 61 runs trained; E `migrate/HANDOVER.md` section 3; `log` 15 Nov 15:46). skr01_pf_v11 is a table row, not a candidate (D `log` 14 Nov 05:58).
- The rows of `draft` section 7 are legacy-split results under the old protocol. They are not CV5-G rows.

## 8. Unseen modules, deferred items, risks
### 8.1 The development instrument U-dev (stage B item B3; E `B3`; review E `RB`, as found 15 Nov 16:00)
| Read | Cells | Review | State |
|---|---|---|---|
| U1 leave-source-out, CSIR and BMRK | 114 and 50 held out | roots pass | runs prepared, not armed; whether the deciding read is pooled or per source is not fixed in writing |
| U2 synthetic half-cut views of pool cells | 1,064 views of 532 cells | **FAIL** | 4 degenerate views; the read tool cannot read these dumps; unusable until fixed and re-reviewed |
| U3 F51 | 51 | not part of B3 | dumps owed (stage A7) |
| U4 H36 crack-free cells; pool half-cells | 19; 943 label-free | lists pass | false alarms count only on the 19 labelled cells |
| U5 CSIR multi cells of P532 | 32 | pass with note | M on relF1@2 is 0.044 (gaint) and 0.065 (cv02): a guard and a descriptive stratum only |

- Status of B3 as a whole: **pending review.** `RB` is still being written and fails its sets item on U2.
- The check of the proxies against published E1 contrasts (R0) qualified no read as a crack primary and falsified none (E `B3` section 4; `RB` section 2).
- **Rule** (D `brief` 12; `W3` G15): development proxies never support a claim about E1; only the registered opening does.
- Labelling pack (D user, `log` 15 Nov 12:40; E `B3` section 6; `RB` section 3): 24 pool half-cut cells with model pre-labels for one pass by the user; development reads only, never training. It is a half-cut crack set, not a scuff set.
### 8.2 Deferred, with the reason (D `brief` 13)
- `rank_stability` (`T12` section 3: ties, rank intervals, which metric orders the table): until at least 8 rows have 2 seeds. 7 rows have them now (section 7).
- `t5_post_eval` (`T12` section 6) and `severity_external_elpvpower` (`T12` section 8): to the last week; the ELPVPower download awaits the user.
### 8.3 Risks (S)
- **Inactive stays under-powered:** M is 0.049 to 0.054 at 2 seeds (section 5.4); 34 module groups hold all inactive cells of the pool (E `draft` section 3.2).
- **No development read sees the stratum that holds 75% of E1 crack pixels** (E `W3` Y2). Every unseen-module claim waits for the one opening.
- **The comparator is not the best in-distribution model:** HOUSE is flagged above PF on strict crack IoU; PF was adopted for unseen modules, which CV5-G cannot test (E `W1C` section 3).
- **The suite is small:** 7 rows, 6 of them at 2 seeds, on one machine. One team built it on one dataset family (`draft` section 8).

## 9. v0.1 to v0.2: what changed and why
| # | Topic | v0.1 (12 Nov) | v0.2 (15 Nov) | Why, with the evidence |
|---|---|---|---|---|
| 1 | Split | frozen B6 folds, 4 straddling cells to be moved | cv5v2 (the 4 moved); 2 more duplicated cells found, split kept, final tables on 528 cells | E `SPL`; `dup_crossfold_v1.tsv`; D `log` 15 Nov 13:51 |
| 2 | Labels | v1 in use, v1.1 proposed | v1.1 in force; its training-side effect is within noise | D `log` 12 Nov 20:15; E `W1C` section 4 |
| 3 | Legacy test | continuity and final confirmation, one read per locked protocol | continuity only; 18 counted openings, none planned | E `TEST`; D `brief` 1 |
| 4 | E1 | one read per locked protocol | one registered opening near the end, at most 3 candidates (user to confirm) | D `HO5` L10 |
| 5 | Tolerance | 2 px by convention | 2 px, backed by distances between annotators | E `A4` |
| 6 | Centreline F1@2 | proposed, not measured | measured; not eligible, it rewards dilation | E `A2m` |
| 7 | Headline order | relF1@2 first (a recommendation) | unchanged; the probe gave no reproducible reason to change | E `A2m`; `RA` |
| 8 | Width | a flag, and a 0.05 guard on relP@2 | pass band 0.85 to 1.15 x baseline, pooled and per source; false-alarm and component guards with every row | D `W2` X4 and section 5 |
| 9 | Operating points | argmax plus one val-chosen crack bias | OP-A and OP-W decide; OP-F printed only (unstable under A/A); OP-C added, pending review | E `W1C` section 2; `B1`; D `HO5` L3 |
| 10 | Decision rule | seed rule plus paired bootstrap | margin M from an A/A read per machine; two-stage group bootstrap; 0 of 15 false promotions | E `A1`; `ROWS1` section 4 |
| 11 | Inactive | contrast SE 0.038 to 0.039 at 2 seeds (B6 folds) | SE 0.0245, M 0.049 / 0.054; no trained arm promoted on pooled inactive IoU at 2 seeds | E `A1` section 2; D `HO5` L4 |
| 12 | Entries | ensembles and test-time augmentation as separate entries | four entry classes; equal-cost comparator; source-metadata flag | D `HO5` L3; E `A2e`; D `log` 13 Nov 09:25 |
| 13 | Data tracks | none | main track (clear terms) and a labelled extra-data track | D user, `log` 15 Nov 12:40 |
| 14 | Cost and size | deployment track T4 | fairness record on every row; stride and head ceiling printed | D `W3` G16; E `A5`; `ROWS1` section 3 |
| 15 | Leakage | unlabelled pools minus the 7 train twins | one pool list of 6,424 cells; weights rule; teacher rule | E `POOL`; `A6`; D `W3` G14 |
| 16 | Governance | a per-track reporting list | info sheet, 10-item checklist, two ledgers, related-work table | D `T12` section 7; `W3` section 2 |
| 17 | Baselines | legacy-split rows | 7 CV5-G rows on cv02; PF the comparator, HOUSE a row of its own | E `ROWS1`; `W1C` section 3 |
| 18 | Unseen-module development | F51 and H36 reads | U-dev reads U1 to U5 (U2 failed its review) and a labelling pack | E `B3`; `RB` |
| 19 | Post-evaluation, severity, ranking | light track T5; ties not specified | deferred, with reasons | D `brief` 13 |

## 10. Open
Items without a ruling, or with a ruling that waits for something. Nothing below is decided.

| # | Item | State on 15 Nov | What closes it |
|---|---|---|---|
| 1 | OP-C (stage B1) | builder reports a pass; `RB` verdict unfilled; the inactive bias sits at the grid edge (+4.0) in all 45 PF fits (`B1` section 2d) | the finished `RB`; the lead's word on a wider grid, which would be a new variant |
| 2 | U-dev (stage B3) | U2 fails review; the U1 deciding read is not fixed in writing; no U-dev GPU job is armed; U3 dumps owed | the U2 fix and its re-review; a written U1 rule before the first U1 number |
| 3 | E1 opening | awaits the user's confirmation; the rule that names the candidates is a proposal (`W3` L10) built on U-dev reads, and R0 qualified none; label set and strata for scoring E1 are v0.1 proposals (`draft` 2.5 row 6, 3.5) | the user's confirmation; a registered protocol before the read |
| 4 | T3b, few-shot track inside E1 | the user said yes for the last week (`log` 12 Nov 20:15); no ruling in the brief; it trains on E1 labels, which the sealing rule of section 3.3 does not allow in development | a ruling on how T3b sits beside the one opening, and its registration |
| 5 | 528-cell scoring | no score-exclude option in the read tools; masked audit of the 357 pairs owed | the tool change and the audit, before any final table |
| 6 | Seeds of a table row | `brief` 6 says 5 seeds; `HO5` L6 accepted that a row whose 2-seed interval lies wholly below PF stays at 2 seeds with its rank interval | the lead says whether L6 still holds; the rank interval needs `rank_stability` |
| 7 | Tracks without a ruling | T2 label efficiency (no CV5-G run); the leave-one-source-out table of v0.1 (not run; U-dev has two sources only); latency for T4 (not measured); the split-variance probe of `T12` section 1 (not run: M covers seed noise only, not fold assignment) | a ruling each, or removal from the text |
| 8 | Release and terms | "lists and code only" plus one email to Pratt is a v0.1 recommendation (`draft` section 8 decision 6); no file lists which data and weights pass "clear terms": BenchmarkEL has no licence file, the ImageNet weights' licence field is "other" (`RR1` note 4), the SegFormer weights are unverified (`W3` U2) | a list of cleared data and weights; a release decision |
| 9 | Governance pieces | info sheet tool, related-work table and the audit rewrite of section 1 are not built; "with and without noisy cells" is in no read so far; guards G17, G19, G20 of `W3` section 6 are used by the builders, but no ruling makes them protocol text | the week-2 work of `W3` section 4 (E2); a ruling on G17, G19, G20 |
| 10 | Deferred analyses | `rank_stability`, `t5_post_eval`, `severity_external_elpvpower` (section 8.2) | 8 rows with 2 seeds; the last week; the user's OK for the download |

Contradictions found between the source files:
1. cv02 inactive margin: 0.049 (`A1` section 3, mean over 15 splits; `log` 15 Nov 12:50) against 0.050 (`W1C` section 2 table and `ROWS1` section 2 header, the one canonical split). This file uses 0.049, as the brief rules.
2. Seeds of a table row: `brief` 6 against `HO5` L6 (Open 6).
3. Stale statements. `benchmark/README.md` says 17 counted openings; `TEST` says 18. `benchmark/README.md` and `SPL` say cv5v2 has 0 groups cut across folds; `dup_crossfold_v1.tsv` lists two cells that sit in two folds each (true for the group file, stale as a leakage statement). The `LAB` header calls the use of v1.1 an open decision; `log` 12 Nov 20:15 records it as decided.
4. Pool cells left after rules 1 to 3: 6,696 (`POOL`) against 6,694 (`A6` section 3, option 2).
5. SDLE cells: 18 (`B1` section 1) against 17 in the pool (`A2e` section 2; `W2` section 5).
6. Crack-free cells: every read uses 303, the v1 count (`W1C` section 1; `W2` section 5), while `LAB` section 2 says 3 train cells lose all crack under v1.1. The reads do not say which mask defines "crack-free".
7. E1 description: `BRIEF.md` section 2 says 67 modules and 58 half-cut cells; `draft` section 3.3 counts 71 image ids and 62 half-cut cells (58 multi, 4 mono).
8. `B3` section 2 says U2 reproduces SHV1 exactly on the 54 val cells; `RB` section 1 finds that on disk it does not (a different random draw).
9. `brief` 5 and 12 treat the existence of `RB` as the end of "pending review"; the file exists but is unfinished (Open 1, 2).
10. Overtaken by a measurement, no conflict left: `W3` Y1 planned with an inactive SE of 0.038; `A1` measured 0.0245 on cv5v2.

## 11. Lead's rulings on the Open list and on the contradictions found (15 Nov 2026, 16:01 IST)
These close or narrow items of section 10; the text above is not rewritten until the stage B review is complete.
1. **Seeds of a table row (Open 6).** Ruling L6 stands and refines "5 seeds": a row whose 2-seed interval against PF lies wholly below 0 at OP-A and at OP-W stays at 2 seeds and is printed as "2 seeds" with that interval; every other row and every candidate gets 5 seeds. Rank intervals wait for `rank_stability`.
2. **T3b few-shot track on E1 (Open 4).** Allowed by the user (12 Nov) for the last week only. It runs only after the one registered E1 opening, as its own track marked `trained_on_e1`: K labelled E1 cells adapt the model, the remaining E1 cells are scored, and no T3b number enters the main table or supports a claim about unseen modules without labels.
3. **Inactive margin on cv02.** 0.049 (mean of the 15 two-seed splits, `results/stageA/A1.md`) is the value; 0.050 in the read tables is the one canonical split. gaint keeps 0.054 from its canonical split until the 4-seed calibration command in A1 section 4 is run.
4. **Tracks without a ruling (Open 7).** Label efficiency and latency are not part of v0.2 (latency is measured once per row in the last week; the fairness record already carries step time and GFLOPs). The leave-one-source-out table is the unseen-module instrument of section 8 and has its status. The split-variance probe is deferred; until it runs, every margin statement says "M covers seed noise, not the choice of folds".
5. **Crack-free cells.** Corrected 15 Nov (fix-round re-review): 303 is the v1.1 crack-free count (v1 gives 300); every read already defined crack-free by the scoring label set; 301 on 528 cells. The reads now print the definition and n. No number changes.
6. **Stale statements** in `benchmark/README.md`, `benchmark/splits/README.md` and the header of `benchmark/LABELS_V11.md` are corrected (18 openings; the two cross-fold cells; v1.1 decided).
7. **Still open, with the user:** what "clear terms" means for the main track, given that BenchmarkEL has no licence file and the ImageNet weights carry the licence tag "other" (Open 8); the confirmation of the E1 opening rule (Open 3).
8. **Stage B review complete (15 Nov, 16:08; `harness/REVIEW_STAGEB.md`).** This supersedes the "review not finished" wording of section 0 line 6, section 5.3, section 8.1 and Open 1 and 2. **OP-C is adopted** as the comparator for arms that shift class priors: `classbias_xfit` passed its pre-set rule on both machines (OP-C minus argmax mIoU-R13 +0.0137 [+0.0107, +0.0169] on gaint, +0.0126 [+0.0077, +0.0167] on cv02; crack IoU -0.0011, inactive IoU +0.0104; `results/stageB/B1_classbias_xfit.md`). It is an entry of class "decision layer". Whenever OP-C is used, gridline and splice IoU and their precision on cells without that class are printed beside mIoU-R13 (about a third of the gain is splice at precision 0.15 to 0.20). One wider-grid variant for the inactive bias is allowed (ledger count 2). **Unseen-module instrument:** the leave-source-out roots LOSO-2 (CSIR 114 held out; BMRK 50 held out) and the U4 / U5 lists pass; the U2 set failed its review and is in a fix round; no U-dev number supports any claim yet. **U1 deciding read**, fixed before any LOSO-2 run: the pooled 164 held-out cells, frontier read with width ratio and two-stage interval; per-source reads are printed and cannot decide alone; opposite signs of at least M in the two sources = "inconsistent".
9. **Fix round and split integrity (15 Nov, 17:58; `harness/REVIEW_STAGEB_FIX.md`, `results/stageB/SAMECELL_AUDIT.md`).** The U2 set is rebuilt and passes (`bench_udev/build_shvoof_v2`). The read tools have a score-exclude option; with the 4 known duplicate cells excluded every headline value moves by 0.0004 or less. The wider-grid class-bias variant failed its rule; OP-C stays variant 1 (ledger count 2). **The module groups of cv5v2 are incomplete:** a masked local-feature audit of all 30,974 same-source cross-fold pool pairs finds the same physical module under two image ids in different folds for at least 16 image-id pairs (60 pool cells; on ARTS images the printed serial numbers match, lead's check on the contact sheet), plus further same-cell candidates. The matcher misses featureless mono cells, so this is a lower bound. Until the module-identity audit over all image ids is done and ruled on: every number in this protocol is "on cv5v2 as built"; comparisons between arms stay valid (all arms share the split); absolute levels may be optimistic for the affected cells; the claim "every cell is predicted by a model that never saw its module" is not yet true for them. Section 10 item 6's wording on the crack-free count is superseded by item 5 above.
10. **Split integrity: audit done and ruled (15 Nov, 22:14; `results/stageC/SPLIT_INTEGRITY.md`, tool branch `bench_split` f966127).** Physical-module identity over all 700 image ids (printed serials on ARTS: 20 of 20 same-serial pairs also matched by pixels, 0 of 2,906 different-serial pairs; image-id level local-feature matching with every crop on disk): 561 physical modules; BMRK and SDLE not decidable. **cv5v2: 24 physical modules span two folds; 91 pool cells (ARTS 48, CFVS 32, CSIR 11; 22.7% of crack px) are held out while a cell of their module trains** (4 the same cell, 38 a neighbouring crop, 49 the same module without shared area); 4 more image-id pairs are open (8 cells). **E1: no link to any training image id and no matching cell** (highest count 7 inliers, noise level); testable for about a third of the image-id pairs (half-cut E1 ids and BMRK have no testable counterpart), so "unseen modules" is supported by pixel evidence, not proven. **Legacy test: 8 test cells are the same physical cell as a pool cell, 7 more are neighbouring crops, 19 share a module**: every legacy test number of the earlier openings carries that (continuity track only). Rulings of the lead: (a) every read of results on cv5v2 scores the **clean cells: `benchmark/splits/score_exclude_v2c.txt` (99 cells = the 91 plus the 8 of the open pairs), 433 cells**, and prints the 532-cell value beside it; this needs no retraining and each scored cell's physical module then has no cell in its training folds, as far as the audit can see. (b) Measured with the 91-cell list (441 cells): PF **0.347 strict crack IoU, 0.826 relF1@2, 0.502 to 0.505 inactive IoU, 0.606 mIoU-R13** (532 cells: 0.365 / 0.844 / 0.503 / 0.612); every arm drops by a similar amount; no contrast changes sign, no screen flag changes, the order of rows is the same (HOUSE minus PF +0.0183 against +0.0173); M stays 0.010 (inactive 0.055 to 0.061). (c) The excluded cells score higher than comparable clean cells (+0.07 crack IoU within source and cell type), which is leakage or easier cells or both; the bound on the headline is about 0.02; only models trained on a regrouped split can separate the two. (d) **The final table (5 seeds) is trained on a corrected split, cv5v3**: module identity v3 plus the open pairs plus the earlier links, minimal moves (the proposal moves 31 cells), built and reviewed before any 5-seed run, with PF and HOUSE re-run on it (about 50 GPU-hours beyond what the 5-seed stage costs anyway). Screens already run stay on cv5v2 with clean-cell scoring. (e) Pool list: `pool_t9_v2.txt` (4,949 cells) replaces `pool_t9.txt`: 1,475 pool cells sat in physical modules that hold labelled cells. (f) The leave-source-out roots are not affected (whole sources are held out).
11. **Corrected split cv5v3: built, reviewed, published (16 Nov, 01:04; `results/stageC/CV5V3_BUILD.md`, `harness/REVIEW_CV5V3.md`, code `bench_cv5v3` c417732).** Groups = cv5v2 groups, the physical modules of the audit, the four open image-id pairs, the earlier links, and the SDLE modules named in the stems (A1, A10, A11): 285 groups, none spans folds (lead's own recount: 304 physical modules, 0 spanning). Folds: a group that sat in one cv5v2 fold keeps it; a group that spanned folds goes to its majority fold, ties to the fold with fewer cells; 47 cells move. Held-out sizes 107 / 110 / 103 / 101 / 111. The balance rule is the narrowed one: crack cells (spread 4 across folds, 9 in cv5v2), inactive cells (7 against 8), the same three classes without training pixels in the same folds, no source or cell type missing from a training list. Costs accepted: SDLE cells are scored in folds 0, 2 and 4 only; fold sizes run from 101 to 111. Files: `benchmark/splits/cv5v3.json` (7a700b00), `cv5v3_groups.tsv` (d880a769); roots `/home/noob/work/bench_data_v3b`; every cv5v3 read passes `--groups .../bench_data_v3b/meta/cv5v3_groups.tsv`. **Clean cells on cv5v2: `benchmark/splits/score_exclude_v3.txt`, 116 excluded, 416 left** (the 99 of item 10 plus the 17 SDLE cells, whose modules sit in all five cv5v2 folds); these 416 cells keep their fold in cv5v3, so the same cells can be compared across the two splits. BMRK (50 pool cells) carries no module information in pixels or names: its grouping stays by image id, a stated limit. The final 5-seed table (PF, HOUSE and every row or arm that goes to 5 seeds) is trained and scored on cv5v3.

