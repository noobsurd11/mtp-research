# AL1 v2: independent recompute by agent 2 (23 Oct 06:55 IST)

## Checks
- **Raw files:**
  - 35 re-score JSONs in `results/al1/raw/`; MD5 identical to the cv02 originals in `el_alhvr/reports/al1/` (35/35).
  - Every entry is at step 20,000, n = 50, weights `model` (network A), or `teacher` for BsM5.
  - cv02 stdouts: 35/35 reach step 20000/20000, one "Run:" header each, 0 Traceback. `launch.log`: 35 "trained … rc=0".
- **Scorer:** my own pooling of the E1 per-cell counts (`results/e1/raw_v2/al1_*`). Max |E1 pooled − re-score JSON| = 0.0 over 35 runs × 4 metrics.
- **A5 vs old A5c** (P12 s0–2, P13 s3–4): identical per seed on crack IoU, inactive IoU, relF1@2 and relP@2. So the new commit reproduces P12/P13 exactly.
- **Rule 1:** recomputed for P, S1, S2, the four S3 contrasts, S4, S6, S5 and ref. The Δ and the threshold match `results.md` §2 to 4 decimals in all four cell sets, and every verdict matches.
- **Paired cell bootstrap** (2,000 resamples, seed 0), own code. It matches results.md:

  | Contrast | crack IoU | inactive IoU | relF1@2 |
  |---|---|---|---|
  | AL5 − A5 | [−0.0287, −0.0065] | [−0.1906, −0.0750] | [−0.0536, −0.0118] |
  | CPSm5 − CPS5 | [−0.0075, +0.0030] | [−0.0317, −0.0001] | [−0.0124, +0.0086] |
  | CPS5 − A5 | [−0.0012, +0.0084] | [+0.0076, +0.1411] | [−0.0007, +0.0152] |

- **Noisy-cell crack FP per run:** matches results.md §4. ALdh5 s0 has 7,236 px; every other run has ≤ 397.

## Verdict: CONFIRMED
**P: AL5 − A5 is WORSE on all three primaries in all four cell sets:** crack −0.0169 (0.0131), inactive −0.1324 (0.0761), relF1@2 −0.0312 (0.0216).

## Added by the critic (not in results.md)
**Inactive precision and recall** (test only, seed means, from the re-score JSONs). *Corrected 23 Oct: the first version averaged test and val by mistake; trainer 1b caught it, and I re-checked it on test only.*

| Arm | Precision | Recall |
|---|---|---|
| A5 | 0.771 | 0.276 |
| AL5 | 0.827 | 0.124 |
| ALd5 | 0.790 | 0.108 |
| ALdh5 | 0.799 | 0.154 |
| CPS5 | 0.649 | 0.400 |
| CPSm5 | 0.620 | 0.389 |
| BsM5 | 0.746 | 0.444 |

- The ALHVR-family arms more than halve inactive recall (0.276 to 0.108–0.154), with precision about unchanged or slightly up.
- The CPS arms and BsM5 raise recall 1.4–1.6×.
- Reading: DTCT is sufficient for the harm (ALd5 is as bad as AL5). CE to the partner's argmax (CPS) does not harm. So the loss form on Ω2/Ω3 (sharpened-MSE plus entropy minimisation) suppresses the minority class. This is untested by a one-change arm.

## H-cm predictions (review_v2 addendum 4, written before any AL1 score was opened)
1. **Crack gain no larger than +0.024:** held (−0.0169).
2. **AL5 crack bin-0 within ±0.03 of A5's:** held, just (0.596 vs 0.569, +0.027).
3. **S1 n.d. or worse on crack:** held (−0.0025, n.d.).
4. **Inactive gains larger than crack gains:** held. CPS5 gives +0.074 inactive vs +0.003 crack; BsM5 +0.132 vs +0.027.

Caveat: these predictions were weak. They would also follow from "ALHVR does not help". The damage to inactive was **not** predicted.
