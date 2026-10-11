# P10: SSL at 5% labels (23 cells) on the L3 base, in-domain and external pools. Results

Protocol: `protocols/P10_ssl_5pct.md`, locked before any run (9a85958). The amendment adding B5 (bf745e0) was made before any B5 run.

**Runs**
- 15 runs on cv02 (RTX A6000), 10 Oct 22:57 IST to 11 Oct 07:34 IST.
- 6 supervised references on gaint (RTX PRO 4500), 10 Oct 22:58 IST to 11 Oct 03:57 IST.
- Every run has rc = 0. All are 20,000 steps; the EMA teacher is evaluated for SSL arms.
- Code: commit `0367079`.

**Files**
- `raw/`: re-score JSONs; `launch.log` (cv02) and `launch_gaint.log`.
- `p10_rules.txt`: the rules and the bin-0 share.
- `per_image_test.txt`: the bootstrap and the source split.
- `fig_p10_bars.png`.
- `per_image.json` and `hist_revised.npz`: cv02 arms.
- `labelled_set_counts.txt`: the required inactive count.
- The whole set is reproduced by `bash scripts/post_ssl.sh p10 <gpu> 15`.

## Results
Test, revised labels, mean ± sd over seeds 0–2.

| Arm | Pool | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|
| A5: supervised (gaint, reference only) | – | 0.298±0.005 | 0.277±0.055 | 0.708±0.012 | 0.890±0.014 | 0.282±0.003 | 0.270±0.050 |
| D5, loss off | 455 | 0.243±0.005 | 0.243±0.006 | 0.629±0.014 | 0.855±0.030 | 0.232±0.009 | 0.251±0.008 |
| B5, hard PL | 455 | 0.247±0.104 | 0.238±0.204 | 0.618±0.177 | 0.898±0.019 | 0.284±0.098 | 0.272±0.221 |
| C5, tolerant PL | 455 | 0.246±0.090 | 0.250±0.194 | 0.630±0.162 | 0.887±0.011 | 0.262±0.085 | 0.307±0.155 |
| Dx5, loss off | 11,938 | 0.275±0.005 | 0.198±0.021 | 0.683±0.005 | 0.848±0.001 | 0.266±0.003 | 0.197±0.017 |
| Cx5, tolerant PL | 11,938 | 0.263±0.012 | 0.288±0.017 | 0.656±0.020 | 0.783±0.054 | 0.264±0.016 | 0.310±0.039 |

Supervised label curve (descriptive; 5% and 50% ran on gaint, the rest on cv02):

| Labels | crack IoU | inactive IoU |
|---|---|---|
| 5% | 0.298 | 0.277 |
| 10% | 0.396 | 0.294 |
| 20% | 0.398 | 0.347 |
| 50% | 0.437 | 0.427 |
| 100% | 0.471 | 0.429 |

## Locked rules (primary: test crack IoU, inactive IoU, crack relF1@2)
Each cell shows the difference, then the threshold in brackets.

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| C5 − D5 (rule 1) | +0.003 (0.104) | +0.007 (0.224) | +0.001 (0.188) | **C5 does not help** |
| Cx5 − Dx5 (rule 1) | −0.012 (0.014) | **+0.090 (0.031)** | **−0.027 (0.024), worse** | **Cx5 does not help** (a primary is worse) |
| B5 − D5 (amendment) | +0.005 (0.120) | −0.005 (0.236) | −0.011 (0.205) | B5 does not help |
| C5 − B5 (amendment) | −0.002 (0.159) | +0.012 (0.325) | +0.012 (0.277) | C5 does not beat B5 |

- **Rule 2, width check:** Cx5 − Dx5 crack relP@2 = −0.065, **flagged as possible fattening**. The other contrasts are OK.
- **Rule 3, share of the gap closed** (against L3@100%):
  - C5: 1% / 4% / 0%.
  - Cx5: −6% / 39% / −14%.
- **Rule 4, label-budget interaction** (secondary). The loss effect at 5% minus the effect at 10%:
  - (C5 − D5) − (C − D, P8): crack IoU −0.006, inactive −0.052, relF1@2 −0.014.
  - (Cx5 − Dx5) − (Cx − Dx, P9): −0.016 / +0.034 / −0.035.
  - So the loss effect did not grow when labels were halved.

**Required counts.** Inactive is present in **2 of the 23** labelled cells (20,517 px). Crack is in 9 of 23. See `labelled_set_counts.txt`.

## Required robustness reporting
Image bootstrap: cells resampled, averaged over seeds, 2,000 resamples.

| Contrast | Δ, all cells | Δ without top-3 | 95% CI | P(Δ>0) |
|---|---|---|---|---|
| C5 − D5, crack | +0.003 | +0.003 | [−0.012, +0.016] | 0.66 |
| C5 − D5, inactive | +0.007 | +0.036 | [−0.048, +0.086] | 0.61 |
| C5 − B5, inactive | +0.012 | +0.037 | [−0.033, +0.071] | 0.63 |
| **Cx5 − Dx5, crack** | **−0.012** | −0.017 | **[−0.026, −0.001]** | 0.01 |
| Cx5 − Dx5, inactive | +0.090 | **+0.003** | [−0.019, +0.157] | 0.95 |

- With the external pool, tolerant PL is **robustly worse on crack** and predicts fatter cracks: relP@2 falls from 0.85 to 0.78, and seed 2 reaches 0.73.
- Its inactive gain disappears without the 3 largest inactive test cells.
- **Source split: the crack loss sits on the pool's own sources.** Cx5 − Dx5 crack IoU:
  - CSIR+ARTS test cells (21): **−0.065 [−0.092, −0.026]**;
  - other sources (29): −0.001 [−0.010, +0.007].

  P9 showed the same direction at 10% (Cx − C on CSIR+ARTS, −0.019).
  - Pseudo-labels learned on the external CSIR/ARTS cells therefore hurt crack on benchmark cells of the *same* sources.
  - A plausible reading: those production cells differ from the benchmark's in capture or preprocessing, and the teacher's crack pseudo-labels on them are wide or wrong. This matches the precision drop. Untested.
- In-domain C5 − D5 shows no source pattern: crack −0.008 on CSIR+ARTS, +0.005 on the rest, both CIs covering 0.

## Exploratory
**1. One seed collapses in both pseudo-label arms on the in-domain pool.** Per seed, test IoU (crack / inactive):

| Seed | D5 | B5 | C5 | Cx5 |
|---|---|---|---|---|
| 0 | 0.238 / 0.238 | 0.302 / 0.369 | 0.294 / 0.358 | 0.253 / 0.303 |
| 1 | 0.247 / 0.241 | 0.313 / 0.341 | 0.302 / 0.366 | 0.275 / 0.270 |
| 2 | 0.244 / 0.249 | **0.128 / 0.003** | **0.142 / 0.027** | 0.261 / 0.292 |

- Seed 2 collapses under **both** hard and tolerant pseudo-labels, but not under the same seed's loss-off control or with the external pool. That points to the seed's in-domain data stream and early teacher, not to either loss.
- In C5's training log, the share of unlabelled pixels with a rare-class pseudo-target (`rare_frac`) stays at 0.001–0.002 from step 4,000 in seed 2, against 0.007–0.009 in seeds 0–1.
  - The teacher stops predicting defects, and the student is trained toward "all background". This is confirmation-bias collapse, visible during training without any labels.
  - B5 does not log this quantity.
- At 10% (P8), the same aggregate signal did *not* separate C's inactive-only collapse in seed 0. A per-class version would be needed.
- **Healthy seeds only (0–1; post hoc, not a rule):**
  - B5 and C5 average about crack 0.30 and inactive 0.36. That is about +0.06 crack and +0.12 inactive over D5.
  - On crack this is level with supervised A5 (0.298); on inactive it is above A5 (0.277; gaint).
  - This is the most favourable SSL reading so far. It describes what pseudo-labels do *when they do not collapse*. It is not a claim.

**2. The P8-style Mean Teacher pipeline is far below supervised at 5%.**
- D5 − A5: crack IoU −0.055, relF1@2 −0.079. At 10% it was −0.013 (P8). Cross-hardware, descriptive.
- Swapping the unlabelled pool again moves the loss-off control: Dx5 − D5 = crack +0.032, inactive −0.045.
- With λ = 0 that can only act through BatchNorm statistics and the data streams. This motivates P12's matched pipeline at 5%.

**3. Bin-0 share** (GT pixels scored < 0.001, test):

| Arm | crack | inactive |
|---|---|---|
| D5 | 0.636 | 0.699 |
| B5 | 0.572 | 0.629 |
| C5 | 0.597 | 0.608 |
| Dx5 | 0.576 | 0.746 |
| Cx5 | 0.555 | 0.504 |

- Saturation is much higher than at 10% (P8 D: 0.419 / 0.758). Pseudo-label arms reduce it, as on L3 at 10%.

## Reading
- **Locked result:** at 5% labels on the P8-style pipeline, no unlabelled loss passes against its loss-off control.
  - In-domain pool: both pseudo-label arms are dominated by a same-seed collapse (sd ≈ 0.1).
  - External pool: tolerant PL gains inactive but loses crack, robustly, with wider crack predictions. The locked rule fails it.
  - That crack loss is concentrated on test cells from the pool's own sources (CSIR+ARTS, −0.065). The external pool is not a safe source of crack pseudo-labels.
- **Not confirmed:** the expectation that SSL helps more as labels shrink. The loss effect at 5% is no larger than at 10%.
- **What to carry forward:**
  - When pseudo-labelling does not collapse (2 of 3 seeds, in-domain), it lifts the handicapped control to about supervised level on crack and above it on inactive.
  - The pipeline itself (D5 vs A5) is the larger problem at 5%.
  - P12 tests both on a matched pipeline with a cv02 supervised reference.
  - Collapse is a concrete, detectable failure mode, a candidate target for the proposed method: rare-class-aware pseudo-label quotas or thresholds.

## Caveats
- One split; 3 seeds; 50 test cells.
- Inactive has 2 labelled examples at 5%. 3 test cells hold 59% of its test pixels.
- A5 and A50 ran on different hardware. They are reference only (P12 adds a cv02 A5).
- The healthy-seed reading is post hoc.
