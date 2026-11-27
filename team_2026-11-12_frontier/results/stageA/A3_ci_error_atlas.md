# A3 ci_error_atlas (shared piece S2): one inactive and weak-class error atlas (builder A3, 14 Nov 2026)

Spec: `cards/T10_rare_classes_spec.md` section A0. Critic: `cards/WAVE3_REVIEW.md` Y4 (one atlas; interval, leave-top-3-groups-out and region counts on every gate; each team's threshold), gin_ipa verdict (P-GIN part (d)), guard G20, Y8 (W1-G explores, W1-C1 confirms). Lead: L4 (Y1 inactive policy) accepted.
Tags: E = measured by the tool, S = my judgement.

## 1. Reading rule (written at 05:31 IST, before the tool was run on any real dump; the first real run started 05:33)

### 1.1 Instrument
- Input: out-of-fold PF v1.1 dumps (`house_r34_unetpp_pf_v11`, cv5v2, folds 0 to 4, every seed of the arm), held-out strict v1.1 masks with ignore px excluded everywhere; images only for P-GIN (d). Only the 532 pool cells; sealed stems refused.
- P = the dump's `pred` (OP-A). Seed-mean pbar = mean over seeds of exp(logp), used only in part (e).
- Every share = pooled px (or region) counts, point = seed mean of pooled counts. Each carries: 95% two-stage group bootstrap interval (330 groups of cv5v2_groups.tsv, then one seed per fold; B = 2000, seed 0); a leave-top-3-groups-out value (lt3: the 3 groups with most GT px of the class the share reads; inactive for the inactive gates, crack for P-GIN, the class itself for G-bias); a region-count value (share of error-bearing components whose largest error bucket is in the gate's set; missed / false regions counted as regions); per-source and per-fold values (G20, BMRK row).
- **Y4 rule applied to every gate:** a gate opens only if it holds on all cells AND without the top 3 groups. Holds on all cells but not without the top 3: "LEAD DECIDES". Intervals and region counts are printed beside the point; they are not decision inputs unless a rule below says so (only P-GIN (d)).
- Definitions fixed where a spec leaves room (S): T6 "region-miss" = FN px in GT inactive components >= 100 px with coverage < 0.2 (FN px in smaller components count in the denominator only); T6 "false region" = predicted inactive component >= 100 px with < 10% of its px within 3 px of GT inactive. T8 C3 (a) = FN px in GT components >= 100 px with coverage < 0.5; (c) = FP px in predicted components with < 10% of px on GT inactive (= T10's spurious components, any size); (b) = all other FN + FP px. T10 seed mean = mean over seeds of pooled counts. Region recall = GT components >= 100 px with coverage >= 0.5; region precision = predicted components >= 100 px that are not spurious.

### 1.2 Gates and what each outcome decides (thresholds as each team wrote them)
| Gate | Owner | Rule (point, seed mean) | Outcome decides |
|---|---|---|---|
| G-rules | T10 arm 1 | share of GT inactive components (>= 100 px) with GT crack within 5 px < 0.97 -> d = 10, else d = 5 | rule-a variant; GT only |
| P-rules R-a | T10 arm 1 pre-check (part d) | R-a deletes >= 3% of predicted inactive px AND precision of the deleted px <= 0.40 | build the R-a variant (2 h) or drop it |
| P-rules R-b | same | R-b adds >= 3% of predicted inactive px AND precision of the added px >= 0.50 | build R-b or drop it |
| G-layer | T10 arm 3 layered_ci | (FN-overlap + FP-on-crack + FN-crackadj + FP-crackadj) >= 25% of inactive error px, OR O1 + O5 >= +0.04 inactive IoU | opens layered_ci (still behind its own union-proxy gate, critic fix 3) |
| G-paste | T10 arm 4, merged paste arm | FN-missed >= 35% of inactive FN px AND < 50% of FN-missed px in FL-candidate components | opens the merged paste arm (then its CPU pre-check) |
| G-refine | T10 parked inact_refiner | FN-boundary + FP-boundary >= 40% of error px AND O4 >= +0.05 | reopens inact_refiner |
| G-bias | T10 arm 2 | in-sample single-class oracle gain >= +0.05 on gridline or splice | sets arm 2's expectation; closes nothing. If no weak class gains >= +0.02: "decision-limited share small", la_ce stays closed |
| T6 gate 1 | T6 vfm_ctx_r34_pf | BUILD if region-miss share of FN >= 0.5 OR false-region share of FP >= 0.5; PARK if both < 0.3; else LEAD DECIDES | vfm_ctx gate 1 (gate 2, late fusion, follows only on BUILD) |
| T8 C3 | T8 ucf_partial_joint | (b) found-region boundary share > 0.70 of FN + FP px -> "expect a null", said before any screen | expectation for the UCF arm |
| UCF step B | T8, WAVE3 verdict fix (2) | missed (a) + false (c) regions >= 30% of inactive error px | step B (6.5 build h) may be built if C4 also does not predict a null |
| G-sam | T13 sam_prompt_refine | FN-boundary + FP-boundary + FN-interior + FP-spurious >= 30% of inactive error px | P-SAM pre-check may run; else "dominant errors are missed regions or the crack overlap" |
| C-BMRK | T8 elpv_bmrk_negatives (DROPPED, parked by the critic) | pass if BMRK crack-free cells with >= 50 predicted crack px >= 20%, or BMRK inactive FP > FN with precision < 0.5, or BMRK relP@2 lowest source by >= 0.05 | record only; the arm stays parked (no module ids in ELPV) |
| ICL readability | T13 icl_oof_probe (DROPPED, parked) | >= 8 PF-missed GT inactive regions | record only |
| P-GIN (d) | T7 gin_ipa | PF OOF crack relR@2 of cells in the top decile of histogram shape (p50 - p5) / (p95 - p5) on content px (GT != padding 7) minus the rest; top decile = shape >= p90 over the 532 pool cells. DEFICIT = point < 0 AND 95% interval wholly below 0 AND lt3 < 0 (S: the critic gave no threshold; I fix this one now). Point < 0 with interval below 0 but lt3 >= 0: LEAD DECIDES. Anything else: NO DEFICIT | NO DEFICIT: "the photometric half of gin_ipa has no support here", stated before the screen. Per source and within-source deciles printed, not decision inputs |
| D2 pointer | critic plan D2 | O2 (paste oracle) against O1 + O5 (layered oracle), point | which trained inactive arm, among those whose gate opens, is built first |

### 1.3 Label-issue list (part (e))
Positive control on W1-C3 (PF on v1 masks, scored on v1 masks, seeds 5 and 6): per cell crack softmin (temperature 0.1) of the seed-mean p_crack over the cell's v1 GT crack px, ranked over all pool cells with v1 crack. PASS only if all 7 control cells rank in the worst 10%: `BMRK_00031_cell0091` (v1 crack 1,560 px) and the 6 train cells whose v1 crack px v1.1 turned to scuff ignore (`ARTS_00051_r6_c2`, `CSIR_00092_r11_c5`, `CSIR_00117_r8_c4`, `CSIR_00155_r5_c5`, `CSIR_00161_r4_c6`, `CSIR_00176_r5_c2`; masks_v11 CHANGES.tsv; the star cell `CFVS_00024_r3_c3` is not a scuff cell). FAIL: the label-issue list is not published (counts only). Agreement with the B1 audit's 9 inactive-FL cells is printed as agreement, not truth.

### 1.4 Not decided here
Y1: no inactive arm is screened on pooled inactive IoU; this atlas only orders and gates. Y8: a W1-G (gaint) outcome is called a result only after the unchanged script reproduces it on W1-C1 (cv02, seeds 5 to 9).

## 2. Runs (E)
- Tool: bench_a **8e0c17e** (`bench/atlas.py` 73520377, `scripts/bench_atlas.py` 29798ae8, `tests/test_bench_atlas.py` 17 tests; full pytest 505 passed, 4 skipped). CPU only, 7 or 8 workers, about 1 min per run.
- W1-G (gaint, seeds 5, 6, 10 runs, 532 cells): `/home/noob/work/bench_reads/stageA/atlas/w1g_s56/` (summary.txt afad9391, gates.json 4a68e6d2, plus buckets.tsv, cells.tsv, regions_gt.tsv, regions_pred.tsv, control_crack_softmin.tsv). Run manifests and input md5s are at the top of summary.txt.
- W1-C1 (cv02, seeds 5 to 9, 25 runs; the Y8 confirmation, same command and commit): `.../atlas/w1c1_s5-9/` (summary.txt b503eace, gates.json 837f1342).
- Positive control: W1-C3 (PF on v1 masks, seeds 5, 6, 10 runs) scored on v1 masks, in both runs.
- Sanity (E): W1-G inactive IoU 0.498, precision 0.767; by source CFVS 0.552, BMRK 0.469, CSIR 0.161, ARTS 0. Same values as the reviewed first read (W1G_FIRST_READ.md).
- Reading the table below: point [95% interval] (lt3 = without the top 3 inactive groups CFVS_00009, CFVS_00114, CFVS_00146), then rc = region-count share. W1-G first, W1-C1 after the slash.

## 3. Gates: numbers and outcomes (E numbers; outcome = the rule in 1.2)
| Gate | W1-G (seeds 5, 6) | W1-C1 (seeds 5 to 9) | Outcome |
|---|---|---|---|
| G-rules | GT crack within 5 px of 99.6% of GT inactive regions (285 regions), lt3 1.000 | 0.996 | **d = 5** (both) |
| P-rules R-a (d = 5) | deletes 0.1% of predicted inactive px [0.0, 0.5%] (264 px, 3 components), precision 0.004 | 0.6%, precision 0.055 | **FAIL: R-a dropped** (both) |
| P-rules R-b | adds 0.6% [0.3, 1.0%] (1,279 px), precision 0.517 [0.227, 0.770], lt3 0.385 | 0.5%, precision 0.468 | **FAIL: R-b dropped** (both) |
| G-layer | overlap + crack-adjacent share 0.370 [0.257, 0.482], lt3 0.321, rc 0.638; O1 + O5 0.153 [0.118, 0.178], lt3 0.131 | 0.366, lt3 0.319, rc 0.617; O1 + O5 0.151 | **OPEN** (both, both conditions, lt3 holds) |
| G-paste | FN-missed share 0.378 [0.197, 0.574], lt3 0.473, rc 0.206; FL share of FN-missed 0.660 [0.370, 0.985], lt3 0.735, rc 0.788 | 0.393, lt3 0.481; FL share 0.627 | **CLOSED** (both; condition 1 holds, condition 2 fails; see 4.2) |
| G-refine | boundary share 0.058 [0.037, 0.080]; O4 0.025 [0.018, 0.031] | 0.059; O4 0.025 | **CLOSED** (both) |
| G-bias | in-sample oracle gain: gridline +0.061 [0.047, 0.074] (best b +1.00), splice +0.086 [0.058, 0.120] (b +1.75); material +0.011, edge_dark +0.003 | gridline +0.059, splice +0.070 | **MET** (both): arm 2 keeps its expectation; la_ce not closed by this |
| T6 gate 1 | region-miss share of FN 0.496 [0.322, 0.671], lt3 0.551, rc 0.223; false-region share of FP 0.337 [0.126, 0.618], lt3 0.439, rc 0.127 | 0.528 [0.346, 0.683], lt3 0.582, rc 0.220; 0.384, lt3 0.494 | W1-G **LEAD DECIDES** (in the band; BUILD without top 3); W1-C1 **BUILD**. Not reproduced under Y8: **LEAD DECIDES** |
| T8 C3 | (a) regions < 50% covered 0.542 [0.353, 0.723] of FN + FP px, (c) false regions 0.108, (b) found-region boundary 0.350 [0.191, 0.520], lt3 0.331, rc 0.695 | (a) 0.482, (c) 0.137, (b) 0.381, rc 0.681 | **NO NULL EXPECTED** (both) |
| UCF step B (atlas part) | missed + false regions 0.650 [0.480, 0.809], lt3 0.669, rc 0.305 | 0.619, lt3 0.637, rc 0.319 | **OPEN** (both); step B still waits for C4 |
| G-sam | boundary + interior + spurious 0.342 [0.215, 0.472], lt3 0.336, rc 0.212 | 0.347, lt3 0.353, rc 0.242 | **OPEN** (both) at px; by region count it is below 0.30 (S: note for the lead) |
| C-BMRK (arm parked) | crack-free BMRK cells with >= 50 crack px 5% ; BMRK inactive FP - FN = -15,441 px, precision 0.984; BMRK relP@2 0.901 vs lowest other 0.887 (CFVS) | 5%, -13,125, 0.984, gap -0.014 | **PARK** (record only) |
| ICL readability (arm parked) | 85 missed GT inactive regions (seed mean), lt3 55 | 81.8 | READABLE (record only) |
| P-GIN (d) | top-decile shape (>= 0.7875; 54 cells, 21 with crack) relR@2 0.879 vs rest 0.787: delta **+0.092 [-0.048, +0.186]**, lt3 +0.114. Within-source deciles +0.098; BMRK +0.161, CFVS +0.073, CSIR +0.257, ARTS not readable (1 cell) | +0.099 [-0.032, +0.195]; BMRK +0.184, CFVS +0.085, CSIR +0.257 | **NO DEFICIT** (both): the photometric half of gin_ipa has no support here |
| D2 pointer | O2 (paste) 0.148 [0.066, 0.261]; O1 + O5 (layered) 0.153 | 0.149; 0.151 | only G-layer opens: **layered_ci** is the atlas's trained inactive arm (still after A1 part (e), Y1) |


## 4. Other atlas parts (E unless marked S)
### 4.1 (a) Where the inactive error sits (W1-G, seed mean; FN 117,797 px, FP 50,765 px)
- FN: overlap (predicted crack) 0.201, missed regions 0.378, crack-adjacent 0.100, boundary 0.056, interior holes 0.264. FP: on GT crack 0.408, spurious components 0.332, crack-adjacent 0.123, boundary 0.060, other 0.077.
- Oracles (inactive IoU 0.498): O1 overlap +0.108 [0.079, 0.127], O2 missed regions +0.148 [0.066, 0.261], O3 spurious +0.028, O4 boundary +0.025, O5 crack-adjacent +0.045. Region recall (>= 50% covered) 0.600, any-hit 0.702, region precision (>= 100 px) 0.829; 85 of 285 GT regions missed.
- Spurious FP sit next to predicted crack (16,403 of 16,864 px within 5 px of a predicted crack component).
- 25.5% of region-miss px are in cells whose max p_inact < 0.1 ("blind"). Region-miss px are predicted background (0.81) or crack (0.12).
- G20 by source: CFVS errors are mostly at the crack overlap (G-layer share 0.471, O1 + O5 0.177); ARTS and CSIR errors are almost all missed regions (G-paste share 0.960 and 0.824; region recall 0 and 0.148); BMRK mixed (G-layer 0.179, G-paste 0.296), BMRK false regions 0. By fold, inactive IoU 0.31 (fold 0) to 0.65 (fold 4). Full per-source intervals and fold values: summary.txt.
- S: missed regions are few but large (px share 0.38, region share 0.21). Shares by px and by region disagree for every inactive gate; the gates are written in px.

### 4.2 Rule usability (S, for the lead; thresholds unchanged)
- G-paste condition 2 counts FN-missed px in FL-candidate components (part (e) CoCo < 0.05). The part (e) positive control FAILED (4.4), so the score it uses is not trusted by the spec's own test. Under the written rule G-paste is CLOSED. If the lead sets condition 2 aside, condition 1 holds on both machines and without the top 3 groups (0.378 / 0.393, lt3 0.47 / 0.48), but only 21% of the error-bearing regions are missed regions. I leave this to the lead.
- T6 gate 1 sits on its 0.5 line (0.496 / 0.528; per seed 0.33 to 0.49 on W1-C1). Seed noise is larger than the distance to the threshold.

### 4.3 (b) Crack at the overlap (W1-G)
15.9% of GT crack px lie within 2 px of GT inactive. There 41% are predicted crack, 34% inactive, 22% background; relR@2 0.626 against 0.828 elsewhere. 14.4% of all crack FN px are predicted inactive. S: crack loses px to inactive at the overlap, so an inactive gain there can cost crack; layered_ci's crack guards must be read at OP-A and OP-W.

### 4.4 (c) Weak classes (W1-G)
| Class | IoU | comps >= 20 px missed | error px within 2 px of the class boundary | FN margin median (share < -6 nats) | oracle gain |
|---|---|---|---|---|---|
| material | 0.391 | 0.617 | 0.228 | -7.25 (0.60) | +0.011 |
| gridline | 0.301 | 0.326 | 0.832 | -1.50 (0.08) | +0.061 |
| splice | 0.025 | 0.906 | 0.966 | -4.50 (0.33) | +0.086 |
| edge_dark | 0.625 | 0.055 | 0.416 | -3.25 (0.39) | +0.003 |
FN go to background for all four (0.82 to 0.98). S: gridline and splice are decision-limited (near the boundary, small margins), material is not reachable by a bias (60% of FN below -6 nats).

### 4.5 (e) Label quality and the positive control
- Control (W1-C3, v1 masks; 232 crack cells ranked; worst 10% = rank <= 24): **FAIL**. In: BMRK_00031_cell0091 (rank 1), CSIR_00161_r4_c6 (4), CSIR_00155_r5_c5 (8), CSIR_00117_r8_c4 (12). Out: CSIR_00092_r11_c5 (45), CSIR_00176_r5_c2 (213), ARTS_00051_r6_c2 (229).
- S: the two worst misses are cells whose whole v1 crack is scuff (47 px each). A model trained on v1 learned scuff-as-crack from the other scuff cells and agrees with the wrong label, so a self-agreement score cannot flag a convention error the model shares.
- **The label-issue list is not published** (label_issues_t10.tsv not written). Counts only (W1-G): inactive FL 67 components in 21 cells (6 of the B1 audit's 9 inactive-FL cells among them), inactive ML 1, material FL 283 / ML 7, gridline FL 626, splice FL 74, edge_dark FL 23 / ML 4. The parked ignore arm stays parked.

## 5. What this decides (outcome under the rule; W1-G explored, W1-C1 confirmed unless stated)
1. **ci_rules_posthoc (B2): both variants fail the arm 1 pre-check** on both machines. Rule a would delete 0.1 to 0.6% of predicted inactive px; rule b would add 0.5 to 0.6%. Not built (2 build h saved). G-rules: d = 5.
2. **layered_ci: G-layer OPEN** (0.37 of inactive error at the crack overlap or crack-adjacent; O1 + O5 = +0.15). Its union-proxy clause (critic fix 3) is met by O1 + O5 >= 0.04. It is the atlas's choice for D2, still behind A1 part (e) (Y1).
3. **Merged paste arm: G-paste CLOSED** under the written rule (the FL clause), with the caveat in 4.2 for the lead.
4. **inact_refiner stays parked** (G-refine closed).
5. **classbias_xfit: G-bias met** (gridline +0.06, splice +0.07 to +0.09 in-sample, optimistic).
6. **vfm_ctx gate 1: LEAD DECIDES** (on the 0.5 line; W1-G in band, W1-C1 BUILD).
7. **ucf_partial_joint: C3 expects no null; the step-B atlas condition is met** (0.62 to 0.65 of inactive error is missed or false regions). Step B still waits for C4 and the build order.
8. **sam_prompt_refine: G-sam OPEN at px** (0.34 to 0.35); P-SAM may run. By region count 0.21 to 0.24.
9. **gin_ipa: P-GIN (d) NO DEFICIT.** Cells with the most E1-like histogram shape have higher, not lower, crack relR@2 (+0.09 to +0.10, interval includes 0, no source negative). Said before any screen: the photometric half of gin_ipa has no support in P532. S caveat: only 12 pool cells (2 with crack) reach shape >= 0.84, the E1 half-cut median (idea 11), so this cannot speak for E1's extreme shapes.
10. C-BMRK: PARK, ICL readable: record only (both arms parked by the critic).

## 6. Not run yet, and the exact command
- **W1-G 4 seeds (5 to 8)**, when the W1-G2 dumps exist (`ls -d /home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11/w1g_pf_v11_f*_s[78]/cv5v2_f*/manifest.json | wc -l` = 10), about 1 min:
```
tmux has-session -t "=bench_a_atlas4" 2>/dev/null || tmux new-session -d -s bench_a_atlas4 'cd /home/noob/work/bench_wt_a && git checkout -q 8e0c17e -- bench/atlas.py scripts/bench_atlas.py && CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python scripts/bench_atlas.py --arm PF=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11:"w1g_pf_v11_f[0-4]_s[5-8]" --labels v11 --control PFV1=/home/noob/work/bench_reads/stageA/links/w1c/house_r34_unetpp_pf:"w1c3_pf_v1_f[0-4]_s[56]" --control-labels v1 --workers 8 --out /home/noob/work/bench_reads/stageA/atlas/w1g_s5-8 > /home/noob/work/bench_reads/stageA/logs/A3_atlas_w1g_s5-8.log 2>&1'
```
  (The `git checkout ... 8e0c17e --` only pins the two files if a later builder changed them; drop it if bench_a HEAD still holds 8e0c17e's versions.) Read the gates block of `w1g_s5-8/summary.txt` against section 3; nothing else changes.
- F51 / H36 inactive: not read by design (G20, Y1: 4 and 3 cells, in no promotion rule).
