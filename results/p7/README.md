# P7: tolerant pseudo-labels on the L0 base (Experiment 2, pilot). Results

Protocol: `protocols/P7_tolerant_pl_pilot.md`, locked before any run.

**Runs**
- 9 runs on cv02 (RTX A6000), 10 Oct 2026, 15:34–23:13 IST.
- Every run has rc = 0. All are 20,000 steps; the EMA teacher is evaluated.
- Code: commit `0367079`.
- Scoring: `scripts/rescore_label_versions.py` on test (50) and val (54).

**Files**
- `raw/`: re-score JSONs.
- `p7_rules.txt`: `scripts/p78_rules.py`, plus the bin-0 share.
- `per_image_test.txt`: `scripts/per_image_analysis.py`.
- `fig_p7_bars.png`: `scripts/p78_figure.py`.
- `per_image.json` and `hist_revised.npz`: read-only scoring on cv02.
- The whole set is reproduced by `bash scripts/post_p78.sh p7 <gpu>`.

**Status: PILOT.** P6 rule 3 found no label headroom on L0: pooled AP −0.001 from 10% to 100% labels. Under P7 rule 4, nothing here is a confirmatory claim about SSL.

## Results
Test, revised labels, mean ± sd over seeds 0–2.

| Arm | crack AP | inactive AP | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 |
|---|---|---|---|---|---|---|
| A: L0 10%, supervised (P6) | 0.553±0.015 | 0.621±0.003 | 0.319±0.051 | 0.439±0.015 | 0.746±0.078 | 0.690±0.126 |
| D: Mean Teacher, loss off | 0.551±0.004 | 0.618±0.004 | 0.355±0.006 | 0.453±0.001 | 0.782±0.007 | 0.788±0.018 |
| B: hard PL (conf ≥ 0.95) | 0.527±0.004 | 0.521±0.015 | 0.359±0.003 | 0.381±0.022 | 0.768±0.007 | 0.848±0.005 |
| C: tolerant PL (proposed) | 0.551±0.001 | 0.585±0.005 | 0.363±0.004 | 0.437±0.007 | 0.790±0.003 | 0.819±0.006 |
| L0 100% (P6) | 0.545±0.003 | 0.612±0.006 | 0.337±0.004 | 0.391±0.008 | 0.782±0.008 | 0.744±0.010 |

## Locked rules (primary: test crack AP and inactive AP)
| Contrast | crack AP | inactive AP | Verdict |
|---|---|---|---|
| C − D | +0.000 (n.d.) | −0.032 (worse) | **C does not help** |
| B − D | −0.024 (worse) | −0.097 (worse) | **B does not help; it hurts both** |
| C − B | +0.024 (better) | +0.064 (better) | **C beats B** |

- Width check: crack relP@2, C − D = +0.031. C predicts thinner cracks, not fatter ones.
- Rule 4: pilot (see above).

## Exploratory
**1. Robustness to the choice of test cells** (image bootstrap and leave-top-3-out; `per_image_test.txt`, test IoU):

| Contrast | Δ, all cells | Δ without top-3 | 95% CI | P(Δ>0) |
|---|---|---|---|---|
| C − D, crack | +0.007 | +0.011 | [−0.001, +0.018] | 0.94 |
| C − D, inactive | −0.016 | +0.050 | [−0.063, +0.059] | 0.31 |
| B − D, inactive | −0.072 | +0.001 | [−0.135, +0.018] | 0.06 |
| C − B, inactive | +0.056 | +0.049 | [+0.022, +0.086] | 1.00 |
| D − A, crack | +0.036 | +0.035 | [−0.013, +0.085] | 0.75 |

- The only robust contrast is **C over B on inactive**: tolerant routing avoids the damage that hard pseudo-labels do.
- The C − D crack effect is tiny (+0.007) and is not claimed.

**2. Pseudo-labels push defect pixels to "certain background".** Bin-0 share is the share of GT pixels scored < 0.001 on test:

| Arm | crack | inactive |
|---|---|---|
| D | 0.061 | 0.205 |
| C | 0.088 | 0.284 |
| B | 0.129 | 0.354 |

- The order is D < C < B for both classes.
- A plausible mechanism is confirmation bias. Where the teacher misses a defect, the confident-background pseudo-label trains the student to be certain it is background.
- B applies that pressure everywhere. C exempts a 2-px band around rare-class targets, so it does less damage.
- This matches the AP losses above: B < C < D on inactive AP.

**3. D − A** (EMA teacher plus P7's label-safe views, no unlabelled loss) is about +0.036 crack IoU. That is the same order as P6's L1 − L0 label-safe gain (+0.048). The unlabelled loss adds nothing on top.

## Reading
On L0 at 10% labels, the unlabelled loss gives no measurable gain:
- hard pseudo-labels hurt, mostly inactive;
- tolerant pseudo-labels are close to neutral: inactive AP drops, crack AP is unchanged.

This is the expected outcome for a base with no label headroom (P6 rule 3). The one positive, robust finding is about *how* to use pseudo-labels: routing rare classes through a tolerant target is clearly less harmful than hard confidence thresholding (C − B inactive IoU +0.056, CI [+0.022, +0.086]).

## Caveats
- Pilot (no headroom).
- One split; 3 seeds; 50 test cells.
- Inactive is dominated by 3 test cells (59% of GT pixels).
- AP saturates (see bin-0 share), so AP differences partly reflect ranking, not segmentation.
