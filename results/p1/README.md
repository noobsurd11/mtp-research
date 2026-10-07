# P1 result: overfit check (can the model fit crack on its own training images?)

Run: 8 Oct 2026, 00:46–01:52 IST, gaint, `scripts/overfit_check.py --arm {A..E}` (copy in `scripts_gaint/`).
Protocol: `protocols/P1_overfit_check.md`, locked before running.
Raw data: `arm_*.json`, `logs/`, overlays `overlay_<arm>_<image>.png` (panels: image | crack TP green, FP red, FN blue | inactive TP cyan, FP magenta, FN yellow).

## Setup

- **Images:** 10 train images that contain crack, the first 10 (sorted) of `labeled_10pct` seed 0: ARTS ×4, BMRK ×2, CFVS ×4. One is from the `CFVS_00114` module, which has dotted labels.
- **Training:** batch 8 with replacement, 3,000 steps (about 2,400 passes per image), Adam 1e-3 constant after a 200-step warm-up.
- **Model:** the SL-run model.
- **Scoring:** on the same 10 images, evaluation transform.
- **Arm D, attempt 1:** ran out of memory while sharing the GPU and was rerun alone; the protocol is unchanged and the failed log is kept.

## Final numbers (step 3,000, one run per arm; replicates of B and D are running)

| Arm | Setting | Crack IoU | P | R | AP | relaxed F1 1 px / 2 px | Inactive IoU | Inactive AP |
|---|---|---:|---:|---:|---:|---|---:|---:|
| A | weighted CE, no aug, bf16 | 0.612 | 0.618 | 0.985 | 0.929 | 0.938 / 0.981 | 0.979 | 1.000 |
| B | plain CE, no aug, bf16 | 0.677 | 0.811 | 0.804 | 0.884 | 0.942 / 0.962 | 0.956 | 0.998 |
| C | plain CE + soft Dice, no aug, bf16 | **0.861** | 0.942 | 0.909 | 0.953 | 0.970 / 0.971 | 0.985 | 0.997 |
| D | plain CE, no aug, fp32 | 0.605 | 0.792 | 0.719 | 0.838 | 0.898 / 0.928 | 0.913 | 0.995 |
| E | weighted CE, **training augmentation**, bf16 | **0.381** | 0.426 | 0.782 | 0.587 | 0.743 / 0.848 | 0.751 | 0.973 |
| (original `sl_10pct_b8_s0`, 20k steps, aug, its 47 images) | | 0.325 | 0.33 | 0.95 | 0.64 | | 0.881 | 0.99 |

All arms were still improving at step 3,000 except E (full trajectories in the JSONs).

## Against the locked decision rules

| Hypothesis | Rule | Measured | Verdict |
|---|---|---|---|
| H4 pipeline bug, misalignment | step-0 overlay or exact comparison | loader mask identical to the raw PNG in 10/10 images; image difference 4e-6 | **Refuted**: no image/mask misalignment |
| H4 pipeline bug, bf16 | \|D − B\| > 0.05 | 0.072, but fp32 (D) is the *lower* one, and D's curve is B's delayed by about 500 steps | **Rule fires; reading open.** The direction is the opposite of a bf16 defect. Replicates (B, D seeds 1–2) are running |
| H1 operating point (class weights) | B ≥ 0.8 and A < 0.6 with A's AP ≥ 0.9 | B 0.677, A 0.612, A's AP 0.929 | **Not met as written.** Partial support: at equal settings weighting costs precision (0.62 vs 0.81) with AP still high. Weights dilate predictions, but they are not the main cap |
| H2 augmentation | A's AP high and E's AP low | A 0.929 vs E 0.587; IoU 0.612 vs 0.381 | **Met.** Augmentation is the largest single factor. E's profile matches the original run's training-set profile |
| H3 label inconsistency caps fitting | B < 0.6 with high relaxed IoU | B 0.677; C reaches 0.861 | **Refuted as a cap on fitting.** A fixed annotation can be memorised to 0.86 at the pixel level |

**No locked prediction:** CE + soft Dice (arm C) fits crack far better than CE alone: 0.861 vs 0.677, precision 0.94.

## What this answers

"Trained on 47 images, tested on the same 47, crack IoU 0.3, something is wrong":
- **It is not a code or data bug.** Masks are aligned exactly, and the same network fits crack to 0.86 with a different loss and no augmentation.
- **It is the training recipe.**
  - **Augmentation (biggest factor):** blur kernels of 3–7 px and ±5° rotations applied to labels a median 1.75 px wide.
  - **Loss:** plain or weighted CE learns a 0.2%-pixel thin class slowly. Weighting adds dilation. In E the model fills dark cracked regions with crack instead of tracing lines (see `overlay_E_CFVS_00031_r4_c4.png`).
- **Generalisation has a separate ceiling.** The labels themselves agree only about 0.26 IoU between two annotations of the same image (`data_analysis/`, one solid pair).

## What it does not answer (careful)

- **Fitting is not generalisation.** Less augmentation or a Dice term may or may not help on held-out images. That needs held-out evaluation with tolerance-aware metrics.
- **Small sample.** One run per arm (B and D replicates pending), 10 images, 3,000 steps, not converged.

## Implications to discuss (interpretation)

1. Revisit augmentation for thin structures (blur strength, how the mask is interpolated under rotation) before any further comparison.
2. Overlap or skeleton losses (Dice, Tversky, clDice, Skeleton Recall) are worth a held-out test. They are cheap and directly target the measured failure.
3. Any SSL comparison sits on this supervised recipe. Fix the recipe first, or SSL is measured on a broken base.
