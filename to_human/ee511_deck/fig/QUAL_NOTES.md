# Qualitative figures for the EE511 talk (25 Nov 2026, v2)

Files (2400 px wide, 150 dpi, white background): `qual_pool_methods.png` (2400 x 1830), `qual_e1_final.png` (2400 x 3297),
`qual_e1_fewshot.png` (2400 x 3297). Script `src/qual_make.py` (gaint copy `/home/noob/work/ee511_qual/qual_make.py`, log
`run_v2.log`, outputs `out/`, row data `out/qual_notes.json`, local copy `src/qual_notes.json`). Run on gaint CPU (nice 10,
CUDA_VISIBLE_DEVICES empty); writes only under `/home/noob/work/ee511_qual/`. cv02 was read only (listing, grep).

## Selection rule v2 (reviewer constraint, written here before rendering v2)
F21's rule on the per-cell mean gain over all available seeds:
- per-cell crack relF1@2 = frozen per-cell formula (metrics_v02 cell_values = F21 f1cell) on the crack_rel2 counts of the
  benchmark's own per-cell records; mean over all available seeds per arm;
- candidates = cells with >= 20 scored GT crack px (the frozen per-cell eligibility, MIN_GT_CELL = 20; pool figure: clean cells
  only, score_exclude_v3 removed, as F21);
- sort by (gain, stem id), n candidates; picks: median = index floor(0.50 (n - 1)), 25th percentile = floor(0.25 (n - 1)),
  failure = the lowest gain (largest loss) not already picked; a 4th row (Q2, Q3) = 90th percentile floor(0.90 (n - 1));
- panels show seed 5 of every arm.
Arms and gain per figure:
- Q1 (pool, split cv5v2, out-of-fold): gain = Ours (PF U-Net++ on cv5v2, w1c1_pf_v11, seeds 5 to 9) minus the mean of Hanifi,
  UCF-EL and Pratt (rows1, seeds 5 and 6 each). 3 rows: median, 25th percentile, largest loss.
- Q2 (E1): gain = C2 minus C1, seeds 5 to 9, all 106 E1 cells. 4 rows: 90th percentile, median, 25th percentile, largest loss.
- Q3 (E1): gain = ALL (out-of-fold: t3b_all_f{k} on e1t3b_f{k}, the fold that held the cell out) minus ZS (C2), seeds 5 to 7,
  all 106 E1 cells. 4 rows: 90th percentile, median, 25th percentile, largest loss.
Note: v1 of these figures (rule 90th / 75th / 50th percentile, >= 50 px, Q2 and Q3 stratified by cell type) was rendered and
viewed before this rule was set by the reviewer; v2 replaces it and applies the rule above mechanically.

## Common conventions
- Drawing (as F21): crack #D55E00 opaque, 1 px dilated (3 x 3); inactive #0072B2 at 45% tint; labels and predictions drawn on
  scored (non-ignore) px only; OP-A = argmax (`pred`). Whole 512 x 512 canvas, no crop; padding (image 255 where the label is
  class 7) shown light grey and every panel framed, so padded half-cut cells read as such.
- Prediction panels: line 1 = relF1@2 of seed 5 (the shown map), line 2 = mean over the arm's available seeds (the ranking value).
- Checks (all pass): pooled relF1@2 from the same records equals the read levels (Q1 PF 0.844 over 5 seeds, Hanifi 0.838, UCF
  0.767, Pratt 0.751; Q2 C1 0.447, C2 0.490; Q3 ZS 0.488, ALL 0.709); for every shown panel the counts recomputed from the drawn
  map equal the record's counts exactly.

## Q1 `qual_pool_methods.png`: pool cells, out-of-fold, split cv5v2, seed 5 (190 candidates)
| Row | Cell (cv5v2 fold) | GT crack px | Gain | Ours s5 / mean(5) | Hanifi s5 / mean(2) | UCF-EL s5 / mean(2) | Pratt s5 / mean(2) |
|---|---|---|---|---|---|---|---|
| median gain | CSIR_00203_r3_c3 (f3) | 1234 | +0.048 | 0.948 / 0.963 | 0.958 / 0.960 | 0.936 / 0.937 | 0.865 / 0.848 |
| 25th pct gain | CSIR_00177_r8_c4 (f4) | 62 | +0.013 | 0.784 / 0.897 | 0.960 / 0.980 | 0.912 / 0.874 | 0.799 / 0.798 |
| largest loss | ARTS_00073_r7_c3 (f0) | 77 | -0.527 | 0.851 / 0.170 | 0.842 / 0.855 | 0.595 / 0.504 | 0.746 / 0.733 |

Sources:
- Ours = PF on cv5v2 (same split and seed as the rows): `/home/noob/work/bench_relay/w1c/w1c1_pf_v11_f{k}_s5/dumps/elbench1/house_r34_unetpp_pf_v11/w1c1_pf_v11_f{k}_s5/cv5v2_f{k}/<stem>.npz`.
- Hanifi / UCF-EL / Pratt: no dumps exist anywhere (gaint relay and NAS keep only checkpoints; the cv02 dump folders
  `/tmp/noob_el/bench_52e3f14/dumps/elbench1/{hanifi_vgg16_unet_pf_v11,ucf_dlv3_r50_pf_v11,pratt_dlv3p_wcec_v11}` are empty).
  Seed-5 CPU re-dump (fp32, argmax, bench_infer predict path, code `/home/noob/work/bench_wt_w2`) from
  `/home/noob/work/bench_relay/rows1/r1_<row>_f{k}_s5/experiments/r1_<row>_f{k}_s5/checkpoints/slim.pth` (step 20000), written to
  `/home/noob/work/ee511_qual/redump/r1_<row>_f{k}_s5/cv5v2_f{k}/<stem>.npz` (+ manifest.json). Counts equal the rows1 read
  records exactly for all 9 panels.
- Ranking records: `/home/noob/work/bench_reads/rows1/cache/<arm>/<run>/rec_argmax_*.json` (labels v1.1).

Caption: Rows chosen by rule (median, 25th percentile and largest loss of the per-cell relF1@2 gain of Ours over three published models; pool cells, out-of-fold, seed 5): on typical cells every model finds the crack, Pratt's weighted loss draws it too wide, and the loss row is a small crack our seed 5 finds but most of our seeds miss.

## Q2 `qual_e1_final.png`: E1, baseline C1 vs final C2, seed 5 (32 candidates)
| Row | Cell | Type | GT crack px | Gain (5 seeds) | C1 s5 / mean | C2 s5 / mean |
|---|---|---|---|---|---|---|
| 90th pct gain | CSIR_00345_r5_c6 | full | 874 | +0.143 | 0.576 / 0.505 | 0.637 / 0.648 |
| median gain | CSIR_01633_r8_c5 | half-cut | 367 | +0.017 | 0.975 / 0.941 | 0.965 / 0.958 |
| 25th pct gain | CSIR_01717_r18_c5 | half-cut + scuff | 2029 | -0.044 | 0.256 / 0.278 | 0.192 / 0.234 |
| largest loss | BMRK_01515_cell2169 | full | 55 | -0.184 | 0.000 / 0.184 | 0.000 / 0.000 |

Sources: C1 = `/mnt/nas/noob_el_archive/bench_relay/open/fin_pf_v11_pool_s5.e1_106/dumps/elbench1/house_r34_unetpp_pf_v11/fin_pf_v11_pool_s5.e1_106/e1_106/<stem>.npz`;
C2 = `/mnt/nas/noob_el_archive/bench_relay/open/fin_hrnet_swad_v11_pool_s5.swad.tta_d4.e1_106/dumps/elbench1/hrnet_w18_unetpp_swad_const_pf_v11/fin_hrnet_swad_v11_pool_s5.swad.tta_d4.e1_106/e1_106/<stem>.npz`.
Ranking records: `/home/noob/work/bench_reads/open_final/records/set/<run>.json` (seeds 5 to 9). Images, labels, ignore:
`/home/noob/work/el_f1/reports/f1/ext117/{images,masks,ignore}` (the files the opening read used). Cell type from
`/home/noob/work/bench_reads/t3b_open9/subsets/{full,halfcut,hard}.txt`.

Caption: E1 illustration after the registered read; decides nothing. Rows chosen by rule (90th percentile, median, 25th percentile and largest loss of the per-cell relF1@2 gain of Final over Baseline, seed 5): Final scores higher on a full cell, most cells change little, and cracks along dark scuff streaks stay hard for both.

## Q3 `qual_e1_fewshot.png`: E1, zero-shot C2 vs few-shot ALL (out-of-fold), seed 5 (32 candidates)
| Row | Cell (T3b fold) | Type | GT crack px | Gain (3 seeds) | ZS s5 / mean | ALL s5 / mean |
|---|---|---|---|---|---|---|
| 90th pct gain | CSIR_02026_r16_c1 (f4) | half-cut + scuff | 1079 | +0.588 | 0.000 / 0.153 | 0.784 / 0.740 |
| median gain | CSIR_01717_r19_c5 (f0) | half-cut + scuff | 1694 | +0.072 | 0.696 / 0.696 | 0.761 / 0.768 |
| 25th pct gain | CSIR_01633_r8_c5 (f2) | half-cut | 367 | -0.023 | 0.965 / 0.963 | 0.939 / 0.941 |
| largest loss | CSIR_02136_r7_c6 (f1) | half-cut | 412 | -0.817 | 0.703 / 0.817 | 0.000 / 0.000 |

Out-of-fold check: each ALL map is from `t3b_all_f{k}_s5` on its held-out set `e1t3b_f{k}` (dump manifest run_id and set
asserted); each cell is in the registered held-out list `/home/noob/work/bench_t3b_io/reg/lists/e1t3b_f{k}.txt` and in fold k of
`t3b_folds.tsv` (folds by image id); ALL f{k} trains on pool532 + the E1 cells outside fold k (T3B_RULE.md section 3), and
bench_infer refused any overlap with the run's train list at dump time. The run's train.txt (cv02 `/tmp/noob_el/bench_data_t3b/`)
no longer exists, so it was not re-read.
Sources: ZS = the C2 dumps above (seed 5). ALL = `/mnt/nas/noob_el_archive/bench_relay/t3bopen/t3b_all_f{k}_s5.swad.tta_d4.e1t3b_f{k}/dumps/elbench1/hrnet_w18_unetpp_swad_const_pf_v11/t3b_all_f{k}_s5.swad.tta_d4.e1t3b_f{k}/e1t3b_f{k}/<stem>.npz`.
Ranking records: `/home/noob/work/bench_reads/t3b_open9/records/{zs,oof}/` (ZS records equal the opening #8 records cell for cell).

Caption: E1 illustration after the registered read; decides nothing. Rows chosen by rule (90th percentile, median, 25th percentile and largest loss of the per-cell relF1@2 gain of Few-shot over Zero-shot, out-of-fold, seed 5): fine-tuning finds cracks along scuff streaks that zero-shot misses, leaves easy cells unchanged, and in the worst cell drops a crack at a busbar.

## Caveats
- Q1 is split cv5v2 (rows tranche 1; 2 seeds per literature row, 5 for Ours) while the final model used cv5v3; Ours in Q1 is
  the PF baseline (U-Net++ / ResNet-34), not the final HRNet recipe. The literature rows are our re-implementations under our
  recipe (deviations in ROWS1_READ.md). The literature panels are CPU re-dumps (exact match to the read's counts).
- Q1 loss row: Ours seed 5 scores 0.85 on that cell but its 5-seed mean is 0.17, so the shown seed looks better than the rank.
- Q2 loss row: both seed-5 maps score 0.00 (a 55 px crack at the corner of a BMRK cell); the loss is in other C1 seeds.
- The same half-cut cell CSIR_01633_r8_c5 appears in Q2 (median) and Q3 (25th percentile); both picks follow the rule.
- E1 labels are drawn about 1.5 x wider than pool labels (T3b verdict note).
- Q2 and Q3 are portrait (2400 x 3297); on a 16:9 slide they are height-limited.

## Landscape versions (layout only; same cells, rule and scores)
`qual_e1_final_wide.png` and `qual_e1_fewshot_wide.png` (2400 x 1170): 2 x 2 grid of the 4 examples in rule order (90th
percentile top-left, median top-right, 25th percentile bottom-left, largest loss bottom-right); each example = Image | Ground
truth | model A | model B; under each prediction "relF1@2 <seed 5> (mean <over seeds>)" in Liberation Sans Narrow (13.5 pt, the
largest size that fits one panel); footer "Maps: seed 5; mean over seeds ... E1 illustration after the registered read; decides
nothing." Script `src/qual_wide.py` (imports qual_make.py; same score asserts and out-of-fold check).
