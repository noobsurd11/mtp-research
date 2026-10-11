# P2 result: SemiCE gradient probe on `mt_20pct_s0` (final weights)

Run: 8 Oct 2026, 00:44 IST, gaint, `scripts/probe_semice_gradient.py --run experiments/mt_20pct_s0 --batches 40`.
Raw output: `p2_semice_mt_20pct_s0.json` (copy of gaint `reports/probes/`). Protocol: `protocols/P2_semice_gradient_probe.md`.

## Against the locked predictions

| Prediction (from the protocol) | Measured (40 batches, mean ± sd) | Verdict |
|---|---|---|
| Share of the loss_con logit-gradient along the per-pixel class-mean (softmax-invariant) direction > 0.5 | **0.041 ± 0.009** | **Refuted.** The gradient is not wasted on a common shift |
| ‖∇θ λ·loss_con‖ < 0.1 ‖∇θ loss_sup‖ | **0.25 ± 0.35** (per batch from 0.02 to 1.93) | **Not met.** The term is not negligible in size |
| > 20% of unlabelled pixels with ≥ 2 positive classes | **100%** of pixels | **Met, strongly** |

The decision rule fires on the third criterion. SemiCE as implemented is not a valid consistency loss: at every unlabelled
pixel its target says several classes are present at once.

## What the positive sets contain (raw-logit thresholds `t_pos = 0.5·freq`, `t_neg = 0.5·(1 − freq)`)

| Class | t_pos | Unlabelled pixels flagged positive | Flagged negative |
|---|---:|---:|---:|
| background | 0.330 | 98.9% | 1.0% |
| padding | 0.105 | 92.1% | 7.3% |
| crack | 0.0013 | **20.3%** (true crack is about 0.19% of pixels) | 78.6% |
| inactive | 0.0010 | 2.9% | 96.8% |

- The teacher's argmax class is always in the positive set, but so is at least one other class.
- 76% of active (pixel, class) pairs are negative.
- The teacher's mean raw logit is −4.5, so whether a pixel counts as "positive crack" depends on whether one logit lies a hair above 0.
- The gradient is nearly orthogonal to the supervised gradient: cosine 0.07 ± 0.40.
- The value ratio λ·loss_con / loss_sup in `train.log` sits at 0.10–0.15 from step 3,000 to the end, so the term was active, at a constant relative size, throughout training.

## Reading (inferred)

- The null result "MT λ = 1.5 equals λ = 0" is **not** caused by a missing or vanishing gradient, as I had expected.
- The gradient is real. But its target pushes background, padding and (on a fifth of pixels) crack up at the same time, so it does not encode the teacher's prediction. Its net effect on the final metrics is about zero, as measured by the loss-off control.
- So every MT result run with this loss (BenchmarkEL 20%, the external-pool queue, UCF-EL on cv02) tests this loss, not Mean Teacher.

## Side finding that matters for a rare-class method (measured)

- A standard pseudo-label rule (teacher max-prob ≥ 0.95) covers 77% of unlabelled pixels. Of those confident pixels:
  - background 66.7%;
  - padding 22.8%;
  - **crack 0.024%** (about 8× under its labelled share of about 0.19%);
  - inactive 0.042%.
- In other words, a correctly implemented confidence-thresholded loss would teach almost nothing about the rare classes.
- This is the rare-class problem in SSL, measured on our data. It fits the literature (DARS, DHC: confident sets are biased toward head classes).

## Caveats

- Final weights: the learning rate is 0, the student is about equal to the teacher (argmax disagreement 3.4% of pixels), and the model is evaluated in train mode.
- The structural findings (positive sets, offset share) do not depend on this. Magnitudes earlier in training come only from the logged loss values.
