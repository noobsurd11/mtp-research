# P8: tolerant pseudo-labels on the L3 base (Experiment 2). Results

Protocol: `protocols/P8_tolerant_pl_on_l3.md`, locked before any run (da3d941). The base was chosen post hoc; this is disclosed there.

**Runs**
- 9 runs on cv02 (RTX A6000), 10 Oct 2026, 17:15–23:53 IST.
- Every run has rc = 0. All are 20,000 steps; the EMA teacher is evaluated.
- Code: commit `0367079`.

**Files**
- `raw/`: re-score JSONs.
- `p8_rules.txt`: `scripts/p78_rules.py`, plus the bin-0 share.
- `per_image_test.txt`: the bootstrap.
- `fig_p8_bars.png`.
- `per_image.json` and `hist_revised.npz`: read-only scoring on cv02.
- `per_image_student.json`: student weights; exploratory 3.
- The whole set is reproduced by `bash scripts/post_p78.sh p8 <gpu>`.

## Results
Test, revised labels, mean ± sd over seeds 0–2.

| Arm | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|
| A: L3 10%, supervised (P6) | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| D: Mean Teacher, loss off | 0.383±0.003 | 0.194±0.034 | 0.796±0.008 | 0.903±0.009 | 0.402±0.008 | 0.201±0.034 |
| B: hard PL (conf ≥ 0.95) | 0.389±0.007 | 0.219±0.081 | 0.806±0.015 | 0.934±0.011 | 0.430±0.011 | 0.297±0.050 |
| C: tolerant PL (proposed) | 0.392±0.006 | 0.253±0.109 | 0.811±0.012 | 0.919±0.014 | 0.421±0.011 | 0.317±0.105 |
| L3 100% (P6) | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

## Locked rules (primary: test crack IoU, inactive IoU, crack relF1@2)
Each cell shows the difference, then the threshold in brackets.

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| C − D | +0.009 (0.010) | +0.059 (0.132) | +0.015 (0.017) | **C does not help (no primary passes)** |
| B − D | +0.007 (0.010) | +0.026 (0.102) | +0.010 (0.020) | **B does not help** |
| C − B | +0.003 (0.010) | +0.033 (0.157) | +0.005 (0.023) | **C does not beat B** |

- Width check: crack relP@2, C − D = +0.017, so OK.
- Rule 4, share of the gap (L3@100% − D) closed by C:
  - crack IoU 10%;
  - inactive IoU 25%;
  - crack relF1@2 18%.
- Rule 4, the same for B: 8% / 11% / 13%.
- Every difference is within the rule-1 thresholds, so these shares are descriptive only.

## Exploratory
**1. Across test cells, C − D is small but consistent. Across seeds, it is not separable.**
Image bootstrap: cells resampled, averaged over seeds.

| Contrast | Δ, all cells | Δ without top-3 | 95% CI | P(Δ>0) |
|---|---|---|---|---|
| C − D, crack | +0.009 | +0.009 | [+0.002, +0.015] | 0.99 |
| C − D, inactive | +0.059 | +0.052 | [+0.020, +0.109] | 1.00 |
| B − D, crack | +0.007 | +0.006 | [−0.001, +0.013] | 0.96 |
| C − B, inactive | +0.033 | +0.032 | [−0.005, +0.095] | 0.93 |
| **D − A, crack** | **−0.013** | −0.021 | **[−0.028, −0.001]** | 0.01 |
| **D − A, inactive** | **−0.101** | −0.077 | **[−0.171, −0.031]** | 0.00 |

- The inactive seed spread is large. C's seed 0 and D's seed 0 both collapse on inactive (IoU 0.13 and 0.15), with the same seed and with or without the loss. So that variance is training noise on the few inactive cells, not an effect of the loss.

**2. The SSL pipeline with the loss switched off is worse than plain supervised training on L3.** D − A is robust to the choice of cells (table above).
- C recovers part of this, but ends where A is: C − A = −0.004 crack IoU, −0.041 inactive IoU, −0.003 relF1@2.
- On L0 (P7) the same D was not worse than A: crack IoU +0.036.

**3. The cause is not the EMA teacher.** Student weights scored the same way (`per_image_student.json`, test IoU):

| Run set | Weights | crack IoU | inactive IoU |
|---|---|---|---|
| P8 D | student | 0.383 | 0.189 |
| P8 D | teacher | 0.383 | 0.194 |
| P8 C | student | 0.391 | 0.249 |
| P8 C | teacher | 0.392 | 0.253 |

What remains differs between D and A in the training path:
- **Labelled view.** Mean Teacher's label-safe "strong" view uses brightness/contrast ±0.25 with p = 0.8, plus Gaussian noise with p = 0.3. The supervised label-safe pipeline uses ±0.2 with p = 0.4 and no noise.
- **BatchNorm.** Statistics are computed over 8 labelled + 8 unlabelled images in one student forward pass.
- **Data streams.** The random streams differ.

P8 cannot separate these. Candidate next step: a pipeline-matched control, with the supervised label-safe view for labelled images and separate forward passes. It should equal A before any SSL gain is credited.

**4. Bin-0 share** (GT pixels scored < 0.001, test):

| Arm | crack | inactive |
|---|---|---|
| A (P6) | 0.422 | 0.648 |
| D | 0.419 | 0.758 |
| B | 0.397 | 0.632 |
| C | 0.400 | 0.627 |

- On L3, pseudo-labels slightly *reduce* saturation against D. This is the opposite of L0 (P7).
- D is more saturated on inactive than A, which is consistent with point 2.

## Reading
With 431 in-domain unlabelled cells at 10% labels on L3, no unlabelled loss passes the locked rule against its loss-off control.
- Tolerant PL's edge over D is small: +0.009 crack IoU. It is consistent across test cells but not separable from seed noise.
- A larger problem is that the Mean Teacher pipeline itself costs about −0.013 crack IoU and −0.10 inactive IoU against plain supervised training. The pseudo-label loss only wins that back.
- For the mid-term: no SSL gain on this split. The specific obstacle is identified: the pipeline's labelled view and batch mixing, not the EMA teacher.

P9 (12k external pool) and P10 (5% labels) test the other two levers. Both use the same D-type control.

## Caveats
- One split; 3 seeds; 50 test cells.
- Inactive is dominated by 3 test cells (59% of GT pixels) and by seed collapse.
- Base chosen post hoc (disclosed in the protocol).
