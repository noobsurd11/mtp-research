# Idea 7 + B5: cell-level and operating-point metrics (scorer for PF2 and later protocols)

calib, 31 Oct 2026, v1. Tags: E measured (file path), R literature (Research MCP id), S judgement. E1, val and `_rf` rows are descriptive. No test cell was read.

**Status:**
- Definitions agreed with coach: v0 + A1-A5, filed as `idea7_metrics_defs.md`, the code-level restatement of protocol_PF2 §4.1-4.2 (authoritative).
- Scorer, dump and hook are freeze candidates, accepted by coach and copied by runner to `el_f3/reports/pf2/post_extra/calib/`.
- Final freeze follows runner's GPU bf16 smoke (~22:00).
- Reported in PF2; co-primary in THIN-B3.

**Verdict (S): PASS, already in protocol.** Two cautions from the backfill (§5.2):
1. The component operating point (b_comp) wanders across seeds (sd of b 1.1-2.8). relR@2 at relP@2 ≥ 0.90 is the steadier of the two.
2. The A4 self-check passes only if the opening dump reproduces m0's bf16 numerics. A CPU fallback at 0.0005 would refuse every single run.

## 0. Deliverable
| file | md5 | role |
|---|---|---|
| `scripts/el_metrics.py` | 6e73ff11 (adds coach's `--tol-profile exact|cpu`, OP grid to +12 + edge flag, `--pooled-val` arm-level OP, E1 oracle readout) | scorer: `records` (per-cell counts over the bias grid; b = 0 self-check vs m0, refuses on FAIL), `selfcheck`, `summary` (val-chosen OPs; refuses unless self-checks PASS; `--exclude` for the clean set) |
| `scripts/calib_dump.py` | c172717e | read-only margin dump; CPU fp32 or `--device cuda` bf16 batch 8; test only with `--opening <protocol>` |
| `scripts/pf2_b5_hook.sh` | e06dfc5f | opening hook: dump → records + self-check → summaries (test, test_clean, ext); env DEVICE=cuda (default) or cpu |
| `scripts/pf2_b5_pooled.sh` | 873591ff | arm-level pooled OP summaries |
| `scripts/test_el_metrics.py` | 9fd7293a | unit tests vs Track M `cell_stats`, incl. pooled OP vs brute force |
| `scripts/idea7_backfill.py` | 77e31969 | this backfill |
| `idea7_metrics_defs.md` | - | definitions + A1-A5 + CLI sequence |

## 1. Definitions (summary; full text in `idea7_metrics_defs.md`)
- **Knob:** crack logit bias b on log p (house mechanism, FINAL's +0.75). Crack is predicted iff margin m + b > 0, with m = log p_crack − max_{k≠crack} log p_k.
  - OP grid: −4.0 .. +8.0, step 0.1.
  - Diagnostic grid: −4 .. +12 plus +0.75.
- **OPs, per run, on val only:**
  - b_comp = max val component recall s.t. val component precision ≥ 0.90.
  - b_rel = max val relR@2 s.t. val relP@2 ≥ 0.90.
  - Ties go to the smaller b. Unreachable → max-precision b, flagged (A2).
  - Applied unchanged to test and E1 (E1 descriptive, A5).
- **Components:** Track M (`cc_rec50_20`, `cc_prec_20`). Recall counts GT components ≥ 20 px with ≥ 50% of px within 2 px. Precision counts predicted components ≥ 20 px with ≥ 1 px within 2 px.
  - A1 speck guard: precision over all predicted components, and the share of crack px in components < 20 px.
- **relR@2 / relP@2:** pooled, as the house re-scorer.
- **Cell level (reported):**
  - positive = ≥ 20 GT crack px; 1-19 = ambiguous (excluded, counted); flag = ≥ 20 predicted px;
  - AUROC on s20 (the 20th-largest margin, so flag(b) ⇔ s20 + b > 0).
  - N = 20 because no val or E1 cell has 1-54 GT px (E), so any N in 1-50 gives the same positives. It is also the component floor and the 27 Oct definition.
  - Test has 2 crack-free cells, so test gives cell recall only.
- **Inactive area % error:** |A_pred − A_gt| × 100 per cell, with area = keep px with GT ≠ 7. MAE over all cells, over GT-inactive cells (≥ 0.5%) and over the rest; signed mean.

## 2. Validation (E)
- **Unit test vs Track M `m_common.cell_stats`:** 12 synthetic cells, with and without ignore masks, b ∈ {−1.5, 0, 0.75, 2}.
  - Checked: crack and inactive predicted/TP, rel2 counts, GT components found, predicted components ≥ 20 and hits, all components and hits, speck px, cell flag.
  - Result: **0 mismatches** (`scripts/test_el_metrics.py`).
- **Real data:** FINAL val/E1 records (CPU fp32) reproduce D's `d_checks/d_cells.json` (CPU fp32). At b 0, |Δ| = 0 on all six pooled metrics; at b +0.75, 2 px of 50,481.
- **judge checks (seed means; records vs o1_extra / m0):**
  - E1 crack recall at b 0: SUP100-PF 0.2133 / 0.2133, SUP100-g 0.1689 / 0.1687;
  - scuff + half-cut 29: 0.1522 / 0.1521 and 0.0939 / 0.0941;
  - val: 0.5961 / 0.5960 and 0.6503 / 0.6504.
- **CLI gating (A4):** tested on a synthetic val set.
  - PASS → records written.
  - FAIL → nothing written, exit 4.
  - Summary refuses FAIL, MISSING, and UNCHECKED without `--allow-unchecked`.

## 3. Prior tries in the repo
- 27 Oct `eval.md` §3 (evalx) first proposed component recall at component precision ≥ 0.90 and relR@2 at relP@2 ≥ 0.90. It also gave FINAL's E1 cell-level numbers (`cell_detect.py`: positive ≥ 20 px, flag ≥ 50 px; 24/32 found, 16/74 false alarms).
- `review_suggestions_2026-10-30.md` item 5: "Metrics DO NOW"; not adopted until now.
- Track M R1 / FINAL: bias +0.75 by max val relF1@2, "because no bias reached val relR@2 ≥ 0.90 at relP@2 ≥ 0.90" (`trackM/results_final.md`).
- Runner's `pf2_e1_width.py` (PF2 §3b) reports E1 relR@2 and component R/P at argmax via Track M `agg`. That is the same component rule at b = 0, so it is consistent with this scorer.
- New here: exact b sweep, per-run val OPs, cell-level AUROC, inactive-area error.

## 4. Literature (R)
- Metrics Reloaded (doi:10.1038/s41592-023-02151-z) and the pitfalls companion (doi:10.1038/s41592-023-02150-0) recommend:
  - matching the metric to the domain question: object / instance-level detection for "find every object", not only pixel overlap;
  - fixing operating points on held-out data, never on the test set.
- Mixed-supervision defect work reports image-level detection AP (doi:10.1016/j.compind.2021.103459). EL anomaly detection reports cell-level F1 (doi:10.1016/j.solener.2023.04.059). Cell level is the industry unit. (Both returned by Research MCP, `team_2026-10-27_unlabelled/lit.md`.)

## 5. Backfill: protocol_100 arms + FINAL (descriptive; val, E1, `_rf` F51; no test)
E: `calib_out/idea7_backfill.txt` / `.json` (md5 6316d265 for the txt), from the per-cell records `calib_out/rec/` (MANIFEST 856faa7d).
- OPs: per run, on that run's own val.
- Cell metrics at b = 0.
- Inactive error in percentage points.
- Mean (sd) over 5 seeds; FINAL is one ensemble (its cell numbers at +0.75 are in the txt).
- CPU fp32 records (§5.2).

### 5.1 Tables
**val (54 cells; 125 GT components ≥ 20 px; 23 crack / 31 crack-free cells)**
| arm | compR@OPc | compP@OPc | compP_all@OPc | relR@OPr | relP@OPr | cell R b0 | cell FA b0 | cell AUROC | inact MAE | inact MAE, inact cells |
|---|---|---|---|---|---|---|---|---|---|---|
| SUP100-g | 0.818 (0.021) | 0.923 | 0.753 | 0.868 (0.005) | 0.901 | 0.957 | 0.052 | 0.994 | 0.069 | 0.830 |
| SUP100-PF | 0.846 (0.023) | 0.912 | 0.723 | 0.876 (0.009) | 0.900 | 0.974 | 0.013 | 0.997 | 0.049 | 0.679 |
| MIM100-PF | 0.821 (0.016) | 0.917 | 0.752 | 0.866 (0.005) | 0.901 | 0.974 | 0.058 | 0.997 | 0.055 | 0.753 |
| CP100 | 0.797 (0.034) | 0.913 | 0.797 | 0.864 (0.010) | 0.900 | 0.983 | 0.097 | 0.990 | 0.065 | 0.717 |
| FINAL | 0.864 | 0.904 | 0.722 | 0.892 | 0.902 | 0.957 | 0.032 | 0.996 | 0.070 | 0.836 |

**E1 all (106 cells; 296 components; 32 / 74 cells), descriptive**
| arm | compR@OPc | compP@OPc | compP_all@OPc | relR@OPr | relP@OPr | cell R b0 | cell FA b0 | cell AUROC | inact MAE | inact MAE, inact cells |
|---|---|---|---|---|---|---|---|---|---|---|
| SUP100-g | 0.164 (0.056) | 0.503 | 0.265 | 0.318 (0.044) | 0.525 | 0.850 | 0.314 | 0.869 | 0.182 | 0.937 |
| SUP100-PF | 0.309 (0.067) | 0.450 | 0.235 | 0.426 (0.040) | 0.480 | 0.863 | 0.257 | 0.889 | 0.097 | 0.382 |
| MIM100-PF | 0.281 (0.035) | 0.440 | 0.219 | 0.420 (0.020) | 0.440 | 0.912 | 0.346 | 0.894 | 0.170 | 0.533 |
| CP100 | 0.167 (0.027) | 0.543 | 0.285 | 0.352 (0.018) | 0.527 | 0.887 | 0.308 | 0.877 | 0.169 | 0.773 |
| FINAL | 0.270 | 0.421 | 0.241 | 0.368 | 0.534 | 0.781 | 0.189 | 0.893 | 0.169 | 0.792 |

**E1 scuff + half-cut 29 (274 components; 20 / 9 cells), descriptive**
| arm | compR@OPc | relR@OPr | relP@OPr | cell R b0 | cell FA b0 | cell AUROC | inact MAE, inact cells |
|---|---|---|---|---|---|---|---|
| SUP100-g | 0.126 (0.059) | 0.202 (0.056) | 0.623 | 0.830 | 0.578 | 0.782 | 0.888 |
| SUP100-PF | 0.271 (0.070) | 0.316 (0.043) | 0.611 | 0.830 | 0.400 | 0.856 | 0.300 |
| MIM100-PF | 0.240 (0.034) | 0.320 (0.021) | 0.570 | 0.910 | 0.556 | 0.872 | 0.408 |
| CP100 | 0.133 (0.026) | 0.238 (0.019) | 0.649 | 0.900 | 0.533 | 0.828 | 0.716 |
| FINAL | 0.226 | 0.244 | 0.657 | 0.750 | 0.333 | 0.794 | 0.730 |

**`_rf` F51 (51 unseen-module full cells; 43 components; 12 / 34 / 5 ambiguous)**
| arm | compR@OPc | compP@OPc | relR@OPr | relP@OPr | cell R b0 | cell FA b0 | cell AUROC | inact MAE, inact cells |
|---|---|---|---|---|---|---|---|---|
| SUP100-g | 0.679 (0.030) | 0.667 | 0.851 (0.004) | 0.808 | 0.567 | 0.129 | 0.662 | 2.261 |
| SUP100-PF | 0.674 (0.023) | 0.771 | 0.845 (0.009) | 0.781 | 0.450 | 0.047 | 0.704 | 2.330 |
| MIM100-PF | 0.623 (0.030) | 0.705 | 0.841 (0.008) | 0.738 | 0.417 | 0.059 | 0.662 | 2.489 |
| CP100 | 0.670 (0.025) | 0.761 | 0.848 (0.015) | 0.835 | 0.533 | 0.118 | 0.663 | 2.273 |
| FINAL | 0.721 | 0.565 | 0.870 | 0.840 | 0.583 | 0.059 | 0.650 | 2.302 |

**Readings (S; descriptive, not verdicts):**
- **Cell level tells the "usefulness" story Om expected, on val.** All arms flag 96-98% of crack cells with 1-10% false alarms, AUROC ≥ 0.99. On E1 they flag 78-91% of crack cells (pixel crack recall 0.17-0.21), but at 19-35% false alarms.
- **SUP100-PF vs SUP100-g:**
  - E1 component recall at the val OP: 0.164 → 0.309.
  - E1 inactive-area MAE on inactive cells: 0.94 → 0.38 pp.
  - E1 cell false alarms: 0.31 → 0.26.
  - On val: cell false alarms 0.052 → 0.013, inactive MAE 0.069 → 0.049.
  - This agrees with the protocol_100 E1 readings and adds that PF also lowers false alarms. Part of PF's E1 recall gain comes from its higher val-chosen b (idea 1 §1).
- **F51 cell recall (0.42-0.58) and AUROC (0.65-0.70) are low** while relR@2 is 0.84-0.87. Pixel-weighted relR@2 is dominated by a few long cracks; the 12 F51 crack cells include short SAM-labelled cracks that models miss or that are label specks (S).

### 5.2 Cautions for the protocols (E)
1. **b_comp wanders across seeds** (per-run val choice):
   - SUP100-g −1.2 / −1.1 / 2.8 / −0.4 / 2.9; SUP100-PF 7.5 / 3.9 / 2.3 / 1.4 / 7.1; MIM100-PF 2.8 / 4.9 / 1.0 / 5.0 / 4.3; CP100 0.6 / −1.6 / 0.1 / −1.9 / 0.1.
   - Cause: val component precision (≥ 20 px) is flat around 0.90 and moves in steps of about 1/130. The ≥ 20 px floor leaves new specks out of it, so precision stays near 0.90 as b rises.
   - Effect: val compR@OPc sd 0.016-0.034 and E1 sd 0.03-0.07, against 0.005-0.010 and 0.02-0.04 for relR@OPr.
   - b_rel is steadier: SUP100-g 1.8 / 0.6 / 2.5 / 1.9 / 1.7; SUP100-PF 5.2 / 2.9 / 4.3 / 3.2 / 3.3.
   - S: in THIN-B3, where both are co-primary, the component one will have the wider rule-1 threshold.
   - **Coach's fix (31 Oct):** an arm-level pooled OP (one b per arm on the pooled 5-seed val), used for THIN-B3's co-primaries.
   - E on the backfill: component-recall seed sd SUP100-g val 0.021 → 0.018, E1 0.056 → 0.041; SUP100-PF val 0.023 → 0.015, E1 0.067 → 0.048. Means unchanged within 0.02.
   - A1's `compP_all` falls to 0.58-0.83 on val at b_comp: below the floor, the val-chosen b admits many small false components.
2. **Arms differ in their OPs:** PF arms sit at higher b (b_rel about 3.8-4.3 vs 1.2-1.7). PF is less crack-confident, as on test (recall down, precision up at argmax). The val OP removes that difference by design.
3. **Numerics (A4):** CPU fp32 records vs the opening m0 JSONs (GPU bf16) at b = 0, 20 single runs.
   - val median / max |Δ|: crack IoU 0.0003 / 0.0008, relR@2 0.0007 / 0.0023, inactive IoU 0.0011 / 0.0061, component recall 0 / 0.008 (1 of 125), component precision 0.0012 / 0.0145.
   - 0/20 runs pass all six at 0.0005.
   - So the opening dump must be GPU bf16, matching m0. Runner smokes it ~22:00.
   - **Coach ruling** (protocol_PF2 §4.1): if the smoke is not exact, ALL runs of ALL arms are dumped on CPU and checked with profile `cpu` (pixel metrics and inactive IoU ≤ 0.01; components ≤ 0.025).
   - All 40 backfill run x set checks pass that profile. Implemented as `--tol-profile`, el_metrics 83666f9e.
4. **Grid edge (judge item 1, E):** 2 of 20 backfill runs chose b_comp within 0.5 of the old OP-grid edge (+8.0): SUP100-PF s0 7.5, s4 7.1. No b_rel did (max 5.2).
   - Coach widened the OP grid to +12, flagging b ≥ 11.5 as edge. None of the backfill runs or pooled OPs reaches it.

## 6. Cost, kill, protocol
- **Cost:** no GPU training.
  - Per run, one read-only pass over val + test + E1: GPU bf16 ~1-2 GB (estimate; runner measures), or CPU ~0.27 s per cell at 8 threads.
  - Records ~10 s per 106 cells with 8 processes.
  - Backfill: 25 models x 266 cells, 32 min CPU + 8 min records.
- **Kill:** none (not a method). It drops from co-primary only if coach judges the OP unusable. The b_comp spread (§5.2) is the thing to watch.
- **Protocol:** done. PF2 §4.1-4.2 (reported); THIN-B3 co-primary; md5s frozen after the smoke.

---

## judge verdict (31 Oct 2026, 14:48 IST from date; report md5 6996d3b6 as reviewed)

**Verdict: PASS (already in protocol).** The scorer is validated, and the backfill reproduces.

### What I reproduced (E)
Own code on calib's records (`judge/idea7_recompute.py`, md5 e283bd50).
- **Per-run val b_rel** (max val relR@2 at relP@2 ≥ 0.90, ties to the smaller b, OP grid −4 to +8):
  - SUP5 1.8 / 0.6 / 2.5 / 1.9 / 1.7;
  - SUPPF5 5.2 / 2.9 / 4.3 / 3.2 / 3.3.
- **Readouts at those operating points:**
  - val relR@OPr 0.868 (0.005) and 0.876 (0.009);
  - E1 relR@OPr 0.318 and 0.426; sh29 0.202 and 0.316.
- **Cell level, val, b 0:** recall 0.957 / 0.974, FA 0.052 / 0.013, AUROC (s20) 0.994 / 0.997. E1 cell FA 0.314 / 0.257.
- **All exact.**

### For coach (protocol items, S)
1. **Grid edge.**
   - SUPPF5's b_comp reaches 7.5 and 7.1 against an OP-grid edge of 8.0, and b_rel's edge is the same.
   - Report how many runs choose b within 0.5 of the edge.
   - If the grid edge binds for any PF2 / THIN-B3 run, widen it before the opening. Never after.
2. **b_comp instability:** seed sd 1.1 to 2.8 against 0.3 to 1.0 for b_rel (calib's own §5.2).
   - In THIN-B3, where component recall at component precision ≥ 0.90 is a co-primary, this will inflate its rule-1 threshold, or let the OP choice decide the verdict.
   - Before THIN-B3 locks, coach should either:
     - stabilise the choice (for example, choose b_comp on a smoothed val component-precision curve, or on the ensemble), or
     - keep relR@2 at relP@2 ≥ 0.90 as the co-primary and report component recall.
3. **Numerics:** agreed that the opening dump must be GPU bf16 to pass the 0.0005 self-check. The fallback tolerance is coach's call. It must be set before the opening and stated in the protocol.
4. **F51 cell metrics** (recall 0.42 to 0.58, AUROC 0.65 to 0.70, while relR@2 is 0.84 to 0.87) reflect short or speckled Hanifi crack labels.
   - Use F51 pixel-pooled metrics, not cell-level metrics, for any `_rf` decision (idea 8 screen, T9). Both already do.

### Tags
- E: backfill rows reproduced.
- R: Metrics Reloaded ids not re-checked (they were returned in earlier team work).
- S: items 1 and 2.
