# P2 — Does the SemiCE consistency term actually move the student?

Status: LOCKED, not run (2026-10-08 00:15 IST). Needs approval for compute on gaint (read-only use of an existing checkpoint).

## Why
Mean Teacher on BenchmarkEL with λ = 1.5 equals its λ = 0 control (paired −0.000 ± 0.024). Code reading
(`src/losses/semi_ce.py`, `src/data/class_info.py:121-144`) shows the consistency loss is not standard Mean Teacher:
- per-class binary cross-entropy applied to the logits of a softmax network;
- "confident" sets chosen on **raw logits**: positive if `teacher_logit[c] > 0.5·freq[c]` (≈ 0.001 for crack),
  negative if `teacher_logit[c] < −0.5·(1 − freq[c])` (≈ −0.5);
- averaged over all active (pixel, class) pairs.
Softmax is invariant to adding a constant to all logits of a pixel, so these sets have no fixed meaning, and a large part
of the gradient may fall along that invariant direction (pushing all logits up or down together), which changes nothing.

## Hypothesis
SemiCE as implemented gives little gradient that changes class decisions. Prediction: the share of its logit-gradient
along the per-pixel class-mean direction is large (> 0.5), and/or its parameter-gradient norm is small next to the
supervised term (< 0.1×), and/or the positive sets are incoherent (many pixels with 0 or ≥ 2 positive classes).

## Measurements
On `experiments/mt_20pct_s0` final weights (student and EMA teacher from `latest.pth`), 40 training batches built exactly
as in training (labelled strong view + unlabelled strong/weak views), forward and backward only, no optimizer step:
1. λ·loss_con / loss_sup (values).
2. ‖∇θ loss_sup‖, ‖∇θ λ·loss_con‖, cosine between them.
3. Logit-gradient of loss_con: fraction of its squared norm in the per-pixel class-mean (softmax-invariant) direction.
4. Positive and negative sets: per-class share of pixels flagged positive; share of pixels with 0, 1, ≥ 2 positive classes;
   share of active pairs that are negative.
5. Reference: standard pseudo-label CE (teacher argmax where teacher max-prob ≥ 0.95, weight 1): same norms and cosine.
6. Also from `train.log`: logged λ·loss_con / loss_sup over steps.

## Caveat
At the final step the learning rate is about 0, so student ≈ teacher and magnitudes are a lower bound. The structural
quantities (3, 4) do not depend on that. If the result is borderline, re-run MT to step 5,000 and log 2–4 every 250 steps.

## Decision rule
Offset share > 0.5, or ‖λ∇ loss_con‖ < 0.1 ‖∇ loss_sup‖, or > 20% of unlabelled pixels with ≥ 2 positive classes →
SemiCE as implemented is not a valid consistency loss, and every MT result with it (BenchmarkEL, UCF-EL on cv02,
the external-pool queue) says nothing about Mean Teacher itself.
