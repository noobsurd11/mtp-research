# Track M, M0: baseline audit of the existing 100% checkpoints (no training)

MD, 24 Oct 2026. Status: **draft for MC's recompute**. Not reported to team-lead as a finding until MC verifies it.
Inference only: cv02 GPU 7, tmux `m0audit`, 24 Oct 11:24 to 13:30 IST.

## 0. What was scored
- **Runs.**
  - SUP100 (the baseline to beat, 5 seeds): P6 `p6_L3_100pct_s0..2` (cv02 `el_p6`, REVISION `824fab0`) + P16 `p16_A_100pct_s3..4` (`el_p13`, `bac5264`). The same pool as P16's A100.
  - Context only, not a candidate baseline: P16 `p16_Sx_100pct_s0..4` (SSL, external pool, EMA teacher; `el_p16`, `d51b60f` per P16 Amendment 1, no REVISION file).
- **Scoring.**
  - Final weights at step 20,000 (asserted), argmax, bf16 autocast, batch 8: the P-series re-scorer path.
  - Masks: `escdd_masks` (val 54, test 50); ext 106 with its ignore mask.
- **Identity.** `p6_L3_100pct_s0` reproduces its P6 re-score JSON exactly: crack and inactive IoU and relF1@2, on test and val.
- **Outputs.**
  - Per cell: 24×24 confusion, crack relaxed counts at 2 px, crack and inactive connected components (8-conn) with hit counts, and p(crack) bands on GT crack and GT non-crack px.
  - Files: `trackM/m0/<run>.json` (MD5 = cv02 copies, `m0/md5_cv02.txt`), tables `m0/m0_tables.md`, val tuning `m0/m0_tune.json`.
  - Scripts: `scripts/m0_audit.py`, `m0_analyze.py`, `m0_tune.py`.
  - A first pass without asserts was killed after MC's code review; its files sit in cv02 `trackM/m0_v1/` and are unused.
- **Seeds.** Mean ± sd over the seeds of an arm. Each run's metric is computed first, then averaged.

## 1. Definitions, fixed before any number below was read (agreed with MC)
- **IoU per class:** pooled over the cells of a set.
- **mIoU_rob (decision mIoU):** mean IoU over the classes with GT in ≥ 3 of the 50 test cells. The list is fixed from all-50 test GT: **0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21** (13 classes).
  - `mIoU_rob_no07` drops background (0) and padding (7), which sit at 0.91 and 0.99.
  - In any subset (without the noisy cell, per source) the list stays fixed. A class with no GT in the subset becomes NaN and is named.
- **mIoU_fix:** the same, over all 15 test GT classes (adds busbars 9 and corrosion 18, 1 cell each).
- **mIoU24** (secondary): a class absent from GT but predicted scores 0. It is printed next to the FP px on absent classes.
- **Crack capture** (how "almost all cracks" is measured; §4):
  - pixel recall;
  - relaxed recall relR@2 (GT crack px within 2 px of a predicted crack px), with relaxed precision relP@2 always beside it;
  - component recall: GT crack components ≥ 20 px count as found if ≥ 50% of their px lie within 2 px of a prediction; component precision is the share of predicted components ≥ 20 px within 2 px of GT.
- **Inactive capture:** component recall for GT components ≥ 100 px found if ≥ 50% of their px are predicted inactive; precision as the share of predicted components ≥ 100 px touching GT.

## 2. Test, SUP100 (5 seeds)

| cells | n | crack IoU | crack P | crack R | relP@2 | relR@2 | relF1@2 | inactive IoU | inact P | inact R | mIoU_rob | mIoU_rob no 0/7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all 50 | 50 | 0.435±0.078 | 0.586 | 0.637 | 0.853 | 0.824 | 0.828±0.105 | 0.436±0.013 | 0.631 | 0.584 | 0.547±0.016 | 0.473±0.018 |
| without noisy cell | 49 | 0.474±0.002 | 0.644 | 0.642 | 0.938 | 0.830 | 0.881±0.004 | 0.449±0.014 | 0.631 | 0.610 | 0.580±0.011 | 0.511±0.013 |
| without 7 twins | 43 | 0.361±0.087 | 0.535 | 0.543 | 0.809 | 0.736 | 0.752±0.140 | 0.412±0.013 | 0.641 | 0.536 | 0.539±0.016 | 0.464±0.018 |
| without both | 42 | 0.405±0.004 | 0.607 | 0.550 | 0.918 | 0.745 | 0.822±0.006 | 0.428±0.013 | 0.641 | 0.563 | 0.575±0.011 | 0.504±0.013 |

Per seed, all 50:
- crack IoU: 0.472, 0.471, 0.470, **0.297 (A100 s3)**, 0.467;
- mIoU_rob: 0.540, 0.535, 0.546, 0.574, 0.537.

Without the noisy cell:
- crack IoU: 0.475, 0.474, 0.473, 0.477, 0.470;
- mIoU_rob: 0.576, 0.571, 0.584, 0.598, 0.573.

L3 100% alone (P6 s0–2, the handbook's "0.471" baseline): crack 0.471±0.001, inactive 0.429±0.011, relF1@2 0.876±0.003, mIoU_rob 0.541±0.005 (0.577 without the noisy cell).

### 2.1 The noisy cell decides all-class mIoU (MC's finding, confirmed here)
- `CSIR_00070_r8_c4` costs mIoU_rob 0.033 on average (0.547 → 0.580), against crack IoU 0.039 for the one seed that fails on it and about 0.003 for the others.
- On that cell SUP100 predicts on average:
  - 156,897 px of border;
  - 54,369 px of background;
  - 15,099 px of crack;
  - 4,604 px of corrosion;
  - nearly all of the 18,616 px of "text", a class absent from test.
- Without the cell: border IoU 0.438 → 0.692 and corrosion 0.656 → 0.755. The FP px on absent classes drop from 18,723 to 106.
- **Consequence for design:** every mIoU contrast is run under rule 1 both with and without this cell. A rung that only makes the model robust to this one cell would move all-50 mIoU by up to +0.03 without changing anything else.

### 2.2 Per class (test, SUP100)
| class | GT px | GT cells | IoU all 50 | P | R | IoU without noisy | P | R |
|---|---|---|---|---|---|---|---|---|
| 0 background | 8,506,124 | 50 | 0.907±0.006 | 0.954 | 0.948 | 0.926 | 0.955 | 0.968 |
| 1 sp_multi | 169,861 | 14 | 0.720±0.019 | 0.892 | 0.789 | 0.803 | 0.906 | 0.876 |
| 2 sp_mono | 297,693 | 24 | 0.732±0.010 | 0.833 | 0.859 | 0.740 | 0.842 | 0.859 |
| 4 ribbons | 582,670 | 50 | 0.632±0.006 | 0.817 | 0.737 | 0.647 | 0.817 | 0.757 |
| 5 border | 185,327 | 24 | 0.438±0.159 | 0.479 | 0.840 | 0.692 | 0.796 | 0.840 |
| 7 padding | 2,827,416 | 24 | 0.994±0.001 | 0.994 | 1.000 | 0.994 | 0.994 | 1.000 |
| 9 busbars | 2,315 | **1** | 0.416±0.076 | 0.515 | 0.687 | 0.420 | 0.519 | 0.687 |
| 11 inactive | 92,125 | 16 | 0.436±0.013 | 0.631 | 0.584 | 0.449 | 0.631 | 0.610 |
| 13 material | 83,724 | 11 | 0.411±0.009 | 0.604 | 0.564 | 0.411 | 0.604 | 0.564 |
| 14 crack | 92,074 | 48 | 0.435±0.078 | 0.586 | 0.637 | 0.474 | 0.644 | 0.642 |
| 15 gridline | 127,869 | 45 | **0.278±0.011** | 0.656 | **0.326** | 0.283 | 0.680 | 0.326 |
| 16 splice | 4,031 | 4 | **0.000±0.000** | – (none predicted) | 0.000 | 0.000 | – | 0.000 |
| 18 corrosion | 10,527 | **1** | 0.656±0.220 | 0.738 | 0.870 | 0.755 | 0.852 | 0.870 |
| 20 edge_dark | 20,504 | 3 | 0.305±0.094 | 0.565 | 0.394 | 0.306 | 0.568 | 0.394 |
| 21 frame_edge | 104,940 | 8 | 0.817±0.020 | 0.975 | 0.835 | 0.817 | 0.975 | 0.835 |

- Absent from test GT, still predicted (mean px, all 50): text 18,616 (on the noisy cell), sp_dogbone 106, dead_cell 1.
- Absent from test GT and never predicted: 8 clamp, 10 crack_rbn_edge, 12 rings, 19 belt_mark, 22 jbox, 23 meas_artifact.
- Bold = flags: 1-cell classes (9, 18), and the two weakest robust classes: gridline (recall 0.33) and splice (never predicted).

## 3. Per source (test, SUP100 seed means)
| source | cells | crack IoU | crack R | relR@2 | relP@2 | inact IoU | inact R | mIoU_rob |
|---|---|---|---|---|---|---|---|---|
| ARTS | 13 | 0.456 | 0.560 | 0.809 | 0.990 | 0.000 (no inactive GT) | – | 0.530 |
| BMRK | 10 | **0.379** | **0.516** | **0.745** | 0.865 | **0.324** | 0.386 | 0.576 |
| CFVS | 18 | 0.522 | 0.700 | 0.872 | 0.960 | 0.578 | 0.959 | 0.659 |
| CFVS without twins | 12 | 0.397 | 0.523 | 0.681 | 0.955 | 0.582 | 0.971 | 0.659 |
| CSIR | 8 | 0.379 | 0.640 | 0.796 | 0.800 | 0.380 | 0.394 | 0.455 |
| CSIR without noisy cell | 7 | 0.475 | 0.684 | 0.846 | 0.962 | 0.707 | 0.752 | 0.589 |
| SDLE | 1 | 0.031 | 0.032 | 0.065 | 0.200 | – | – | 0.577 |

- At 100% labels the weak sources are BMRK and CFVS-without-twins on crack, and BMRK on inactive (recall 0.39 vs 0.96 on CFVS).
- ARTS crack recovered with labels: 0.133 at 5% (handbook C0.6) → 0.456 here.
- "ARTS inactive 0.000" is 0 GT and 0 predicted inactive px (IoU 0/0). The code prints 0; it should read NaN and does not enter mIoU_rob.

## 4. "Almost all cracks": where crack stands (test, SUP100)
| measure | all 50 | without noisy | without both |
|---|---|---|---|
| pixel recall | 0.637 | 0.642 | 0.550 |
| relR@2 (px within 2 px of a prediction) | 0.824 | 0.830 | 0.745 |
| relP@2 | 0.853 | 0.938 | 0.918 |
| components ≥ 20 px found (≥ 50% within 2 px) | 0.790 | 0.798 | 0.738 |
| components ≥ 20 px touched at all | 0.885 | 0.892 | 0.859 |
| component precision (pred comps ≥ 20 px near GT) | 0.837 | 0.924 | 0.936 |
| inactive components ≥ 100 px found | 0.757 | 0.773 | 0.688 |

**p(crack) on GT crack px:**

| band | < 0.001 | 0.001–0.1 | 0.1–0.5 | 0.5–0.95 | ≥ 0.95 |
|---|---|---|---|---|---|
| test, SUP100 | 0.189 | 0.116 | 0.060 | 0.105 | 0.530 |
| val, SUP100 | 0.185 | 0.110 | 0.061 | 0.107 | 0.537 |
| ext, SUP100 | **0.704** | 0.083 | 0.036 | 0.050 | 0.127 |

- At 100% labels, 28% of GT crack sits in the middle band (5% labels: 8%, C0.5), so operating-point changes have more room here.
- About 19% of GT crack is a confident miss (< 0.001). Only the model itself can fix that.

**Proposed target** (for design.md; MC to rule): "almost all cracks" = test, without the noisy cell:
- relR@2 ≥ 0.90 at relP@2 ≥ 0.90;
- crack component recall ≥ 0.90;
- crack IoU not below the baseline by more than rule 1.

Baseline: relR@2 0.830 at relP@2 0.938, component recall 0.798.

## 5. Unseen modules (ext 106, SUP100; secondary)
| | crack IoU | crack P | crack R | relR@2 | inactive IoU | inact R | mIoU_rob (ext list) |
|---|---|---|---|---|---|---|---|
| SUP100 | 0.148±0.007 | 0.466 | **0.178** | 0.300 | 0.064±0.014 | 0.185 | 0.411±0.013 |
| L3 100% (P6, 3 seeds) | 0.152 | 0.485 | 0.181 | 0.306 | 0.071 | 0.174 | 0.416 |

- 70% of ext GT crack scores below 0.001. On unseen modules the model does not see the cracks at all (recognition, not calibration).
- No threshold rung can fix this.
- It reproduces handbook 11's 0.152 for L3 100%.

## 6. Val only: what post hoc operating points give (no test touched)
SUP100 seed means on val (54 cells). In `m0_tune`, mIoU is over val's 17 GT classes (not the robust list).

| variant | crack IoU | crack P | crack R | relP@2 | relR@2 | relF1@2 | inact IoU | inact P | inact R | mIoU (val GT) |
|---|---|---|---|---|---|---|---|---|---|---|
| plain argmax | 0.423 | 0.550 | 0.646 | 0.914 | 0.850 | 0.881 | 0.411 | 0.500 | 0.701 | 0.511 |
| TTA dihedral-8 | **0.433** | 0.559 | 0.657 | 0.927 | 0.853 | 0.888 | 0.453 | 0.524 | 0.769 | 0.516 |
| LA τ 0.25 / 0.5 / 1.0 | 0.422 / 0.418 / 0.420 | 0.525 / 0.503 / 0.518 | 0.682 / 0.714 / 0.691 | | 0.863 / 0.873 / 0.861 | 0.882 / 0.881 / 0.882 | 0.408 / 0.406 / 0.414 | | | 0.529 / 0.516 / 0.434 |
| crack bias +1 / +2 / +3 | 0.423 / 0.421 / 0.417 | 0.531 / 0.512 / 0.494 | 0.675 / 0.702 / 0.728 | 0.904 / 0.894 / 0.882 | 0.861 / 0.871 / 0.880 | 0.882 / 0.882 / 0.881 | | | | |
| 24-class bias, in-sample | 0.420 | 0.530 | 0.673 | 0.899 | 0.861 | 0.879 | 0.423 | 0.550 | 0.657 | 0.535 |
| 24-class bias, 2-fold cross-fit | 0.421 | 0.525 | 0.679 | 0.899 | 0.863 | 0.880 | 0.416 | 0.531 | 0.660 | **0.528** |
| TTA + 24-class bias, cross-fit | 0.433 | 0.536 | 0.694 | 0.912 | 0.870 | 0.890 | 0.506 | 0.692 | 0.652 | **0.544** |
| 5-seed ensemble (mean softmax) | **0.435** | 0.563 | 0.656 | 0.928 | 0.860 | **0.893** | 0.424 | 0.511 | 0.714 | 0.522 |
| ensemble + TTA | 0.436 | 0.562 | 0.660 | 0.930 | 0.851 | 0.889 | 0.456 | 0.528 | 0.768 | 0.521 |
| ensemble + crack bias +1 | 0.434 | 0.520 | 0.723 | 0.898 | **0.895** | 0.897 | | | | |
| ensemble + crack bias +2 | 0.419 | 0.476 | 0.779 | 0.859 | **0.923** | 0.890 | | | | |
| ensemble + TTA + 24-class bias, cross-fit | 0.433 | 0.544 | 0.678 | 0.918 | 0.860 | 0.888 | 0.544 | 0.734 | 0.678 | **0.552** |
| context: Sx100 5-seed ensemble | 0.438 | 0.569 | 0.655 | 0.934 | 0.863 | 0.897 | 0.478 | 0.553 | 0.779 | 0.522 |

Readings (val, 54 cells; inactive is 6 cells, 3 of them hold 89%):
1. **TTA:**
   - single model: +0.010 crack IoU (seed sd 0.002), +0.007 relF1, +0.005 mIoU;
   - cost: 8× inference, no training.
   - Its inactive +0.04 rests on 6 cells.
   - Noisy-cell effect: not measurable on val; to be checked on test at the TTA rung.
2. **Ensembling 5 existing seeds:** +0.012 crack IoU and +0.012 relF1@2 over the single-seed mean. TTA adds nothing on top of the ensemble for crack.
   - Cost: 5× training (already paid for these 5 checkpoints) and 5× inference.
3. **Crack bias trades precision for recall at flat IoU:**
   - crack IoU stays at 0.42 from bias −1 to +2;
   - on the ensemble, crack bias +1 reaches relR@2 0.895 at relP@2 0.898.
   - So the recall target in §4 is about one bias step away on val. It is a choice of operating point, not a better model.
4. **LA** (τ ≥ 0.5) does not help crack IoU, and it hurts mIoU at τ ≥ 0.75. It agrees with S-a (A100 +LA crack −0.0016). Not a rung.
5. **24-class bias:**
   - fitted on val, it is worth +0.017 mIoU after cross-fit (in-sample +0.024; about 30% of the in-sample gain is val overfitting);
   - with TTA, +0.033;
   - it comes mostly from rare classes (mean in-sample biases: splice +2.4, belt_mark +1.8, edge_dark +1.7, inactive −3.0).
   - Per-fold gains are not yet broken out; MC's rule (b) needs them before any inactive bias is adopted.
   - The cross-fit groups CFVS by cell position, others by module ID.

## 7. Where the headroom is (reading)
1. **Crack recall is decided at two levels.**
   - About 28% of GT crack is in the middle probability band: operating point, TTA and ensembles move it.
   - About 19% is a confident miss, concentrated in BMRK (relR@2 0.745) and CFVS-without-twins (0.681). Only a better model reaches it: backbone, resolution, data.
2. **Inactive:** precision 0.63, recall 0.61 (test, without the noisy cell). BMRK inactive recall 0.39. Val cannot tune inactive (6 cells).
3. **Other classes, by mIoU leverage:**
   - gridline 0.278 (recall 0.326; 45 cells; the largest robust-class deficit);
   - splice 0.000 (4 cells; never predicted);
   - edge_dark 0.31 (3 cells), material 0.41 (11 cells), border 0.69 (without the noisy cell).

   Today's loss puts Dice only on crack and inactive. These classes get CE alone, which favours the head classes. A rung that extends Dice to all classes (`loss.dice_classes`, config only) is the cheapest mIoU lever.
4. **The noisy cell** is worth +0.033 mIoU_rob and up to 0.18 crack IoU for one seed in five. Rule 1 on both cell sets is required. A model or TTA that is robust to it is a real but narrow gain.
5. **Unseen modules:** crack recall 0.18, 70% confident miss. Out of reach for anything but data or representation. Secondary.

## 8. Not done / open
- Per-fold breakdown of the 24-class bias (MC rule b), before any bias goes into a rung.
- No test number for any tuned variant (TTA, ensemble, bias). Those are rungs with locked protocols.
- Bootstrap CIs: none here. The baseline needs none; each contrast gets them.
