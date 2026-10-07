# P1 — Overfit check: why can't crack be fitted on training images?

Status: LOCKED, not run (2026-10-08 00:15 IST). Needs approval for compute on gaint.

## Question
Supervised U-Net++ (`sl_10pct_b8_s0`) trained 20,000 steps at batch 8 on 47 labelled images (about 3,400 passes per image)
scores crack IoU 0.325 (P 0.33, R 0.95, AP 0.64) on those same 47 images, while inactive reaches 0.88
(`reports/fit_vs_generalise.md`). A 5M-parameter network should memorise 47 images. What caps crack?

## Hypotheses and what each predicts
| ID | Hypothesis | Prediction if true |
|---|---|---|
| H1 | Operating point: √-inverse-frequency class weights make "crack" the cheaper error, so predictions are dilated | Arm B (plain CE, no aug) memorises: crack IoU ≥ 0.8. Arm A (weighted, no aug) has high AP (≥ 0.9) but precision < 0.6 |
| H2 | Augmentation (±5° rotation, blur, noise) stops memorisation of 2–3 px lines | Arm E (weighted, standard aug) stays near IoU 0.3–0.4 and AP < 0.8; arm A clearly higher AP |
| H3 | Labels are inconsistent at the 1–2 px level | Even arm B plateaus below about 0.6 crack IoU while inactive > 0.9; relaxed (1–2 px) IoU much higher than strict |
| H4 | Pipeline bug (bf16 numerics, image/mask misalignment, model output path) | Arm D (fp32) differs materially from arm B; or every arm fails including inactive; or step-0 overlays show misalignment |

These are not exclusive. The design separates them.

## Step 0 (no training)
Load 3 crack images through `BenchmarkELDataset` with no augmentation and overlay mask on image; also overlay the raw
PNG mask on the raw image. Confirm the two agree pixel for pixel.

## Arms
Common: 10 train images that contain crack (taken from `labeled_10pct` seed 0, listed in the report), batch 8,
3,000 steps, Adam lr 1e-3, 200-step warm-up then constant (no cosine, to isolate), weight decay 1e-4, grad clip 1,
model exactly as in the SL runs (U-Net++ 32 filters, dropout 0.2), training seed 0.

| Arm | Loss | Augmentation | Precision |
|---|---|---|---|
| A | weighted CE (weights of the 10% subset, as SL-10) | none | bf16 autocast |
| B | plain CE | none | bf16 |
| C | plain CE + soft Dice (crack, inactive) | none | bf16 |
| D | plain CE | none | fp32 |
| E | weighted CE | standard training augmentation | bf16 |

## Measurements (every 500 steps, eval mode, the same 10 images, no augmentation)
Crack and inactive: IoU, precision, recall, pixel AP; relaxed precision/recall at 1 px and 2 px (Euclidean).
Loss values. Final: overlays for 3 images per arm (TP/FP/FN colours).

## Decision rules
- B ≥ 0.8 and A < 0.6 with A's AP ≥ 0.9 → H1. The class weights are the cap; fix the loss/operating point.
- A's AP high and E's AP low → H2. Augmentation geometry must be reconsidered for thin lines.
- B < 0.6 with high relaxed IoU → H3. Strict IoU is measuring label jitter; switch the crack metric to tolerance-aware.
- D ≠ B by more than 0.05, or step 0 misaligned → H4. Fix the pipeline before anything else.
