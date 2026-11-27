# Figures F1, F3, F4, F7, F8, F9, F18, F21 (fig_maker_B, 23 Nov 2026)

Built from pool cells and result files only. No E1 or test50 image, mask, label, prediction or dump was opened. O4 ruling
(coordinator, 23 Nov): no E1 or test50 pictures now; E1 examples may come later, after the T3b read, as a separate task.

- **Files per figure:** `F<n>.pdf` (vector; images embedded at native resolution, checked with `pdfimages -list`),
  `F<n>.png` (200 dpi), `F<n>_data.csv` (plotted values or cell ids with sources).
- **Scripts:** `src/make_F<n>.py`, shared helpers `src/figB_common.py`, sealed check `src/check_sealed_B.py`.
  Run with the house venv, `PYTHONDONTWRITEBYTECODE=1`, `CUDA_VISIBLE_DEVICES=` empty, `nice -n 10`.
- **Read logs:** `src/logs_B/readlog_F<n>.tsv`, one line per file read. Check result: `src/logs_B/sealed_check.txt`.
- **Overlay colours (Okabe-Ito, colour-blind safe), the same in every image figure:**
  - crack (class 14): vermillion #D55E00, opaque; drawn with a 1 px (3 x 3) dilation in full-cell panels so it stays visible.
    F7 crops are not dilated.
  - inactive (class 11): blue #0072B2 at a 45% tint.
  - boxes (centre cell, candidate region): yellow #F0E442, dashed.
- **No figure titles** (lead ruling, 23 Nov): no figure carries a suptitle or figure-level header text. The captions
  below carry that text. Panel letters, short panel headings and column headers stay.
- **Figure text** (lead ruling, 23 Nov): no file names, line numbers or table ids appear on any figure; sources are in
  this file and the data CSVs. "user" is not used on figures (F8 says "ruling" and "decision").
- **Font:** base 9 pt to match fig_maker_A (was 8 pt); every explicit size in the scripts scales by 9/8 through
  `figB_common.fs()`, so annotation text is about 5.5 to 7.3 pt. Figures are 7.0 in wide (fig_maker_A uses 15 cm = 5.9 in),
  so at text width they print at about 0.84 x these sizes.
- **Pool guard:** P532 = the union of the cv5v3 held-out folds. It must equal `pool532_manifest.tsv`, contain no stem of
  `forbidden_v1.txt` or the `legacy.json` sealed sets, and have no `cells.tsv` bench_set of test50 or e1_106.
  Every path is refused if it contains test50, e1_106, /e1/ or _e1.

## F1. One pool cell per source
- **Label:** fig:F1. **Chapter:** 2 (2.2 classes and sources).
- **Caption:** One P532 pool cell from each of the five sources, with the v1.1 labels: crack in vermillion (#D55E00, drawn
  1 px dilated) and inactive in blue (#0072B2, 45% tint). ARTS, CFVS and CSIR images are windows of about 3 x 3 cells; BMRK
  and SDLE are single cells on white padding. Cells were chosen by a fixed rule (median crack size), not by eye. The release's one double-annotated image is
  excluded.
- **Sources:**
  - `benchmark/cells.tsv`: columns source, crack_px_v11 and inactive_px_v1. Inactive is unchanged in v1.1 (LABELS_V11.md section 2).
  - images: `/home/noob/work/el-fault-detection/data/labeled/images/<stem>.png`
  - masks: `benchmark/out/masks_v11/masks/<stem>.png`
- **Selection rule:**
  - Per source, the candidates are pool cells with crack_px_v11 > 0 and inactive_px_v1 > 0.
  - SDLE has no such cell, so its candidates need crack only.
  - Lead ruling, 23 Nov: cells flagged dup_image in cells.tsv are removed from the candidates before the rule. These are
    CFVS_00015_r7_c4 and CFVS_00016_r7_c4, the release's one double annotation (same pixels, two masks).
  - Sort by (crack_px_v11, stem) and take index (n - 1) // 2.
  - The script asserts that the mask's crack px equal the cells.tsv value.
- **Cells:**

  | Source | Stem | Fold | Crack px | Inactive px | Candidates |
  |---|---|---|---|---|---|
  | ARTS | ARTS_00073_r4_c1 | 0 | 65 | 769 | 2 |
  | BMRK | BMRK_00222_cell0882 | 2 | 1920 | 12221 | 6 |
  | CFVS | CFVS_00031_r5_c5 | 3 | 2483 | 2588 | 27 |
  | CSIR | CSIR_00055_r6_c3 | 2 | 1346 | 3956 | 11 |
  | SDLE | SDLE_00849_A11-DH3000-500h-PT-cell24 | 4 | 197 | 0 | 2 (crack only) |

- **Skipped cell:** the first version picked CFVS_00016_r7_c4 (crack 2423 px, inactive 13977 px, 29 candidates).
  - Reason: it is one half of the release's double annotation (cells.tsv flags dup_image;mask_copy_near).
  - Its twin CFVS_00015_r7_c4 is excluded with it, so the rule cannot land on the same pixels.
  - With 27 candidates left, the rule gives CFVS_00031_r5_c5 (no cells.tsv flag). The other four sources are unchanged.
- **Notes:** the ARTS crack is small: 65 px, and the source has only 2 candidates.

## F3. The 3 x 3 window
- **Label:** fig:F3. **Chapter:** 4 (4.5, audit finding F3).
- **Caption:**
  - (a to c) One P532 pool cell each from ARTS, CFVS and CSIR, with v1.1 crack (vermillion #D55E00, 1 px dilated) and
    inactive (blue #0072B2) labels. The dashed yellow box (#F0E442) is the centre cell found by the audit's rule.
  - (d) The share of v1.1 crack px (vermillion) and inactive px (blue) that lies outside the centre cell: 57% of crack px and
    71% of inactive px over all 532 pool cells. "ALL" includes the single-cell BMRK and SDLE images, whose shares are 0.
- **Sources:**
  - centre-cell rule: `central_rect`, copied verbatim from `dataset_audit/scripts/labels_audit.py` (md5 f0214464).
  - selection: per-cell table `dataset_audit/out/labels_percell.tsv`.
  - panel d values: `dataset_audit/out/labels_audit.txt` section b5 (the source of REPORT.md F3).
  - images and v1.1 masks as for F1.
- **Selection rule:**
  - Per source, the candidates are rows with gaps_found True and crack_n >= 200.
  - Pick the cell whose crack_out / crack_n is closest to the source's pooled share in b5 (ARTS 0.678, CFVS 0.624,
    CSIR 0.721). Ties go by stem.
  - The script recomputes the box and the outside count and asserts that both equal labels_percell.tsv.
- **Cells:**

  | Source | Stem | Crack px outside / all | Candidates |
  |---|---|---|---|
  | ARTS | ARTS_00152_r9_c5 | 344 / 664 | 25 |
  | CFVS | CFVS_00032_r8_c4 | 657 / 1077 | 86 |
  | CSIR | CSIR_00086_r10_c5 | 787 / 1104 | 41 |

  - Panel d, outside share for crack / inactive: ARTS 0.678 / 1.000, CFVS 0.624 / 0.788, CSIR 0.721 / 0.781,
    ALL 0.574 / 0.706.
- **Notes:**
  - The ARTS pick is the closest cell, but its share is 0.518. Single-cell shares cluster near 0 or 1.
  - CFVS_00032_r8_c4 carries the cells.tsv flag twin_train_d7.
  - None of the three picks has inactive px, so panels a to c show crack only. Inactive appears in panel d.
  - `out/gallery/check_centre_cell.png` was viewed but not reused. It uses red and green.

## F4. Sets and splits
- **Label:** fig:F4. **Chapter:** 4 (4.1).
- **Caption:** Cell sets and splits. The labelled corpus holds 816 real cells (787 physical cells, 463 module groups). The
  development pool P532 (legacy train 478 + val 54) is split twice:
  - cv5v2 (2-seed screens): 330 groups. It held a module leak of 24 modules (91 cells).
  - cv5v3 (5-seed rows and the CV5 TTA read): 285 groups, none spans folds; 47 cells moved. The 416 clean cells are read
    beside all 532.

  The bars give held-out fold sizes. The sealed sets are E1 (106 cells, 71 image-id clusters, 101 CSIR cells, 62 half-cut)
  and test50 (50 cells, continuity only). The 167 forbidden stems may enter no training list.
- **Sources:**
  - TT T1, T2, T17. Each phrase used is asserted verbatim against THESIS_TABLES.md.
  - `benchmark/cells.tsv` bench_set counts, re-counted and asserted: pool 532, test50 50, e1_106 106, aux_ext11 11,
    aux_rf117 117; sum 816.
  - "5 BMRK" E1 cells: TT T16b (BMRK stratum, 5 cells).
- **Selection rule:** not applicable (schematic).
- **Notes:** ext117 = E1 106 + aux_ext11 11, as in the forbidden entry of cv5v3.json.

## F7. Label-error candidates with rater verdicts
- **Label:** fig:F7. **Chapter:** 4 (4.5, audit F5 and the AI-rater check).
- **Caption:**
  - Six label-error candidates from the dataset audit (P532 pool cells), with the verdicts of three AI raters
    (rater/RESULT.md, pre-registered). Left block: crack candidates. Right block: inactive candidates. Rows: majority label
    error, model error, ambiguous.
  - The text under each example gives the class, the majority verdict, the candidate type and size, the stem and the three
    raters' verdicts.
  - Each example shows the image window, the v1.1 label, and the 25-model out-of-fold vote: pixels predicted by at least 13
    of 25 cv5v3 models (PF, HOUSE, HRNET, SWADBN, C3X x seeds 5 to 9).
  - Crack is vermillion (#D55E00), inactive is blue (#0072B2, 45% tint), and the candidate region is the dashed yellow box
    (#F0E442).
  - Raters are runs of one model (consistency, not independent reliability). For crack, about a quarter of candidates are
    label errors: corrected share 0.244 [0.105, 0.436].
- **Sources:**
  - `dataset_audit/rater/out/candidate_verdicts.tsv`: id, stem, type, px, bbox, r1 to r3, majority.
  - `dataset_audit/cache/cons/<stem>.npz`: vote maps vc and vi.
  - v1.1 masks and images as for F1.
  - Window rule: `rater/scripts/rcommon.py` crop_window, copied (side = clip(extent + 48, 96, 288)).
  - Consensus threshold: 13 (CONS_T in rcommon.py).
- **Selection rule:** for each class (crack, inact) and each majority verdict (label_error, model_error, ambiguous), take the
  candidate with the largest px. Ties go by id.
- **Cells:**

  | Class, verdict | Id | Stem | Type | px | Candidates in group |
  |---|---|---|---|---|---|
  | crack, label error | L4FAE | CSIR_00094_r16_c5 | SC | 1024 | 18 |
  | crack, model error | VCJWE | CSIR_00070_r7_c2 | SC | 219 | 11 |
  | crack, ambiguous | 94EJU | CSIR_00090_r3_c5 | SC | 604 | 46 |
  | inactive, label error | RRWDR | CFVS_00046_r8_c4 | MI | 3186 | 10 |
  | inactive, model error | RCME7 | BMRK_01660_cell0398 | SI | 3627 | 30 |
  | inactive, ambiguous | ENFPC | CFVS_00126_r5_c3 | MI | 2044 | 5 |

- **Notes:**
  - The figure has no block headers (titles ruling). Each example's text starts with its class.
  - CSIR_00070_r7_c2 is flagged noisy in cells.tsv.
  - CFVS_00046_r8_c4 is flagged mask_copy_near.
  - The raw rater panels (`rater/panels/`) were not reused. They use red, blue and green, and hide which annotation is the label.

## F8. Timeline of beliefs, 7 Oct to 21 Nov
- **Label:** fig:F8. **Chapter:** 5.
- **Caption:** What the project believed, and what the evidence said, from 7 Oct to 21 Nov 2026. Rows are in date order and
  not to scale. Markers give the lane: legacy-split SSL and recipe work (sky blue circles), registered E1 openings (vermillion
  diamonds), benchmark protocol (green squares). Legacy-split rows are not comparable with chapters 7 and 8.
- **Sources:**
  - handbook 11 (H11) timeline table l515 to l520, claim rows 17 and 18 (l90, l91), and l25 (for the dates 16 to 18 Nov).
  - TT T21 (P16, Track M, encoder audit rows), T17 (#1 to #8), T1, T2, T6, T7a.
  - log.md l224 (relF1@2 decides) and l291 (T3b; E1 becomes training data).
  - cv5v3.json "created": "2026-11-15".
  - FINAL_TTA_READ.md l5 (time of the TTA read).
- **Check:** each row's key phrase is asserted verbatim against its file; H11 and log line numbers are asserted.
  F8_data.csv lists each row with its file, pointer and the snippet.
- **Selection rule:** dated events named in the sources OUTLINE lists, plus four protocol-era rows from TT. The choice of
  rows is a judgement (S).

## F9. Protocol flow
- **Label:** fig:F9. **Chapter:** 6.
- **Caption:** The protocol's path from idea to claim:
  1. A 2-seed screen on cv5v2. A pass is a promotion, never a result.
  2. A 5-seed row on cv5v3. A gain counts only if delta >= M and the 95% interval is above 0 at OP-A and OP-W, with the
     guards passing.
  3. A registered E1 opening, with candidates and rule frozen before any sealed dump.

  The lower boxes give the outcomes this project recorded. CV5 numbers of the C2 recipe are selection-biased. The E1 result
  is for the recipe averaged over seeds 5 to 9, at OP-A only; 101 of 106 cells are CSIR, and the full cells carry it.
- **Sources:**
  - P02 l7 to l19, l116 to l118.
  - TT T4 (rules, MDE), T6, T7a, T8, T16a.
  - Every number and quoted rule is asserted verbatim against THESIS_TABLES.md or PROTOCOL_v0.2.md. F9_data.csv lists them.
- **Selection rule:** not applicable. The screen examples are the T16a arms with a printed relF1@2 value.
- **Note:** The "532 and 416 both decide" condition is the v1.0 addition stated in TT T4. The rest is the v0.2 wording.

## F18. Severity
- **Label:** fig:F18. **Chapter:** 10 (10.1, 10.2).
- **Caption:**
  - (a) Predicted against labelled inactive area fraction a (derived region: inactive plus enclosed crack, % of non-padding
    px) on the 532 P532 pool cells.
    - Predictions: PF, cv5v2 out of fold (each cell predicted by the fold model that did not train on it), cv02, seeds 5
      to 9. Not cv5v3.
    - Predicted value = mean over seeds. Symlog axes; dashed line y = x.
    - 467 cells sit at (0, 0).
    - Pooled: MAE 0.1224 pp [0.0663, 0.1879], kappa 0.7815, sensitivity at 0.5% 0.7316.
  - (b, c) ELPVPower S137 rows (129 used, 8 dropped by the automatic check): relative power loss L = 1 - Pmpp / Pref against
    predicted inactive area A (cell equivalents) and against predicted crack length C (skeleton px). PF v1.1 seed 5, 5-fold
    ensemble.
    - rho_A +0.873 [+0.803, +0.914], rho_C +0.885 [+0.832, +0.915], D = -0.013. Pre-registered outcome: NULL.
    - Within type: T3 rho_A +0.930. T1 and T2 near 0.
  - Colours: sources and module types use Okabe-Ito colours with distinct markers.
  - Not validated on unseen modules, half-cut cells or the final model.
- **Sources:**
  - `/home/noob/work/bench_reads/severity/S1/cv02/cells/PF/w1c1_pf_v11_f*_s*_*.json` (25 files, per-cell a in %).
  - `.../S1/cv02/cells/gt_cddf394e4614.json` (GT a; its keys are asserted to equal P532).
  - `.../S1/cv02/post_eval.txt` (pooled values).
  - `/home/noob/work/bench_reads/severity/S3/stats/rows_summary.tsv` (A, C, L, type per row).
  - `.../S3/stats/stats.txt` (rho values).
  - The definitions come from results/severity/S1_POST_EVAL.md section 1.2 and S3_ELPVPOWER.md l22, l29.
- **Selection rule:** all pool cells, and all 129 used rows.
- **Notes:**
  - The 467 count at (0, 0) is computed here from the per-cell files, not copied.
  - Panel a is the C1 recipe (PF) on cv5v2, not the final model (gap G-N11).
  - No ELPVPower image is shown.

## F21. Qualitative CV5 examples
- **Label:** fig:F21. **Chapter:** 7.
- **Caption:**
  - Pool cells, out of fold (cv5v3); selection-biased recipe. Columns: image, v1.1 label, PF (C1 recipe) and the C2 recipe
    (HRNet-W18 U-Net++ with SWAD, swad readout, plus D4 TTA; CS_D4). Both predictions are seed 5, OP-A (argmax).
  - Rows were chosen by a fixed rule from the 190 clean crack cells:
    - the median and the 25th percentile of the per-cell C2 gain in relF1@2 over PF (mean over seeds 5 to 9);
    - one failure: the largest loss of the C2 recipe against PF on the 5-seed mean relF1@2, ties broken by stem order.
  - Crack is vermillion (#D55E00, 1 px dilated) and inactive is blue (#0072B2, 45% tint).
  - The swad readout was chosen on these cells, so C2 numbers here are selection-biased. E1 is the unbiased test.
- **Sources:**
  - PF dumps: `/home/noob/work/bench_relay/c3base/c3_pf_v11_f{k}_s{s}/dumps/elbench1/house_r34_unetpp_pf_v11/c3_pf_v11_f{k}_s{s}/cv5v3_f{k}/<stem>.npz`
  - CS_D4 dumps (queue fin, FINAL_TTA_READ.md l4): `/home/noob/work/bench_relay/fin/c3x_hrnet_swad_v11_f{k}_s{s}.swad.tta_d4/dumps/elbench1/hrnet_w18_unetpp_swad_const_pf_v11/<run>/cv5v3_f{k}/<stem>.npz`
  - Labels: v1.1 masks, with keep = not ignore.
  - Counts: `src/logs_B/F21_percell_counts.tsv`.
- **Per-cell relF1@2:** the frozen per-cell formula (bench_wt_final bench/metrics_v02.py cell_values, md5 2f95427d; counts
  as score_ext.rel_counts, md5 75ae55e9).
  - The script asserts that the pooled levels reproduce T5: PF 0.8463 and CS_D4 0.8684 (532 cells, OP-A, mean over seeds).
    Both reproduced exactly.
- **Selection rule (fixed in the script before any per-cell value existed):**
  - Candidates: the 416 clean cells (score_exclude_v3.txt removed) with >= 20 v1.1 GT crack px. n = 190.
  - Gain = CS_D4 mean - PF mean over seeds 5 to 9. Sort by (gain, stem).
  - Median: index floor(0.5 (n - 1)) = 94. 25th percentile: index floor(0.25 (n - 1)) = 47.
  - Failure (lead ruling, 23 Nov): the largest loss of the C2 recipe against PF on the 5-seed mean relF1@2, i.e. the
    lowest gain among the 190 candidates. Ties go by stem order, skipping cells already picked.
  - The first version used "lowest C2 mean relF1@2". It picked ARTS_00009_r4_c1, where both arms are at 0. That rule is
    replaced.
- **Cells:**

  | Pick | Stem | Fold | GT crack px | PF mean | C2 mean | Gain |
  |---|---|---|---|---|---|---|
  | median gain | CSIR_00177_r8_c4 | 4 | 62 | 0.9759 | 0.9902 | +0.0143 |
  | 25th percentile | CSIR_00203_r3_c3 | 3 | 1234 | 0.9667 | 0.9688 | +0.0022 |
  | failure | BMRK_01234_cell2068 | 1 | 226 | 0.6826 | 0.3484 | -0.3342 |

- **Notes:**
  - The failure pick has no tie: the next-largest losses are CSIR_00090_r4_c4 (-0.2038) and BMRK_02285_cell1383 (-0.1429).
    BMRK_01234_cell2068 has no cells.tsv flag.
  - Seed-5 values in the failure panels: PF 0.7326, C2 0.3994.
  - The median-gain cell has only 62 GT crack px.
  - The figure has no title; the scope text "pool cells, out of fold; selection-biased recipe" is in the caption only.
  - F21_data.csv gives all 532 cells with per-arm values and the picks.

## Not done, or open
- **O4:** no E1 or test50 example in any figure (coordinator ruling, 23 Nov). E1 examples may follow after the T3b read,
  as a separate task.
- **F18:** shows PF, not the final model. No severity read of C2 exists (G-N11).
- **Lead rulings applied, 23 Nov:**
  - F1 excludes the double annotation.
  - F21 uses the largest-loss failure rule.
  - No figure titles: F21's title line and F7's two block headers were removed.
- **F8:** row choice is a judgement. It is not a complete history.
- **Style:** base 9 pt at 7.0 in width; included at a 15 cm text width the text prints at about 0.84 x. Making the
  widths 15 cm would need a further relayout of F4, F8 and F9; not done.
