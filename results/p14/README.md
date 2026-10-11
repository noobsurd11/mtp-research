# P14: offset-tolerant supervised loss (R = 2 px), 10% labels (47 cells), old vs revised masks. Results

Protocol: `protocols/P14_tolerant_supervision.md`, locked before any run.

**Runs**
- cv02 (RTX A6000): 9 runs, 11 Oct 14:42–19:34 IST. All 18 train/rescore steps have rc = 0. All runs are 20,000 steps and use final weights.
- Code: commit `be67787` (branch `p14`). The reference L3 is P6 `p6_L3_10pct` (`824fab0`); its `ce_dice` path is unchanged.

**Files**
- `raw/`: re-score JSONs and `launch.log`.
- `p14_rules.txt`.
- `per_image_test.txt`: bootstrap and source split.
- `fig_p14_bars.png`.
- `per_image.json` and `hist_revised.npz`.
- E1 per-cell metrics: `../e1/e1_p14.md`.
- Reproduce with `bash scripts/post_ssl.sh p14 <gpu> 9`.

## Results
Test cells, scored on revised labels; mean ± sd over seeds 0–2.

| Arm | Train labels | Loss | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|---|
| **L3o** | old | CE+Dice | 0.314±0.009 | 0.309±0.054 | 0.733±0.009 | 0.895±0.006 | 0.324±0.007 | 0.317±0.054 |
| **L3To** | old | tolerant | 0.310±0.009 | 0.319±0.003 | 0.728±0.005 | 0.921±0.003 | 0.300±0.011 | 0.311±0.009 |
| L3 (P6) | revised | CE+Dice | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| **L3T** | revised | tolerant | 0.398±0.005 | **0.331±0.016** | 0.816±0.007 | 0.907±0.008 | 0.380±0.006 | 0.336±0.021 |
| L3 100% (P6) | revised | CE+Dice | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

## Locked rules
Each cell gives the difference, then the threshold in brackets.

| Rule | Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|---|
| 1. label-noise gap G | L3 − L3o | **+0.082** (0.011) | −0.015 (0.066) | **+0.081** (0.011) | gap exists on crack IoU and relF1@2 |
| 2. recovery | L3To − L3o | −0.004 (0.015) | +0.010 (0.063) | −0.005 (0.012) | **fails**: 0% of G recovered; ≥ 50% (+0.041) was needed. relP@2 rises by 0.027, so no width flag |
| 3. tolerance on revised labels | L3T − L3 | +0.003 (0.010) | **+0.037** (0.028) | +0.002 (0.010) | **passes** on inactive IoU, none worse. Width check relP@2 −0.003: ok |

## Robustness (rule 4)
Image bootstrap over the 50 test cells, 2,000 resamples.

| Contrast | Class | Δ | Without top-3 cells | 95% CI | P(Δ > 0) |
|---|---|---|---|---|---|
| L3 − L3o | crack | +0.082 | +0.100 | [+0.046, +0.129] | 1.00 |
| L3To − L3o | crack | −0.003 | −0.001 | [−0.013, +0.006] | 0.22 |
| L3T − L3 | crack | +0.003 | +0.006 | [−0.003, +0.010] | 0.82 |
| L3T − L3 | inactive | +0.037 | +0.028 | [−0.016, +0.093] | 0.88 |

- **The label-noise gap is robust.**
  - It survives removal of the top-3 cells.
  - It holds in both source groups: CSIR/ARTS +0.197 [+0.080, +0.241]; CFVS/BMRK/SDLE +0.062 [+0.030, +0.112].
- **The rule-3 inactive gain is not robust over cells.** Its CI includes 0.
  - The top-3 test cells hold 59% of inactive GT pixels.
  - CSIR/ARTS: all the inactive pixels are in 3 cells; without them the Δ is 0.000.
  - CFVS/BMRK/SDLE: +0.030 [−0.024, +0.092], and +0.008 without the top 3.

## Secondary
- **Tolerance lowers crack AP and pushes more crack GT pixels to near-zero scores. Argmax IoU does not change.**

  | | crack AP | crack bin-0 share |
  |---|---|---|
  | L3 → L3T | 0.400 → 0.380 | 0.422 → 0.441 |
  | L3o → L3To | 0.324 → 0.300 | 0.550 → 0.595 |

  The tolerant rule credits a crack prediction anywhere within 2 px, so the exact GT pixel is pushed less.
- **Scored on the old labels, the revised-label model is still better.**

  | Model | crack IoU (old labels) | crack relF1@2 (old labels) |
  |---|---|---|
  | L3 | 0.351±0.001 | 0.791±0.003 |
  | L3o | 0.332±0.004 | 0.758±0.006 |

  So the gap is not only "trained on the label version it is scored on".
- **Validation agrees in direction:**
  - L3T − L3 val inactive IoU 0.336 vs 0.300; val crack 0.319 vs 0.318.
  - L3To val inactive 0.214 vs L3o 0.293, opposite to its test sign.

## E1 per-cell metrics (secondary; `../e1/e1_p14.md`)

**Test**
| Contrast | Metric | Δ | 95% CI |
|---|---|---|---|
| L3To − L3o | crack tolF1 | −0.041 | [−0.066, −0.020] |
| L3To − L3o | crack length error | +0.079 | [+0.011, +0.153] |
| L3T − L3 | inactive cell IoU | +0.025 | [−0.020, +0.077] |
| L3T − L3 | crack tolF1 | +0.010 | [−0.003, +0.023] |

On old labels, tolerance makes per-cell crack detection worse.

**Unseen-module extension, 106 cells**
| Contrast | Metric | Δ | 95% CI |
|---|---|---|---|
| L3 − L3o | crack IoU | +0.030 | [+0.012, +0.048] |
| L3 − L3o | crack relF1@2 | +0.068 | [+0.021, +0.110] |
| L3T − L3 | inactive cell IoU | +0.088 | [+0.005, +0.193] |
| L3T − L3 | crack false alarm | +0.041 | [−0.008, +0.091] |

- The label revision transfers to modules we never trained on.
- L3T's direction matches tolerant pseudo-labels in P11/P12: inactive improves and crack false alarms rise.

## Reading
- **(a) No.** The tolerant loss does not make old-label training closer to revised-label training.
  - The gap is large (+0.082 crack IoU) and robust.
  - Tolerance recovers none of it, so the old-vs-revised difference is not a 1–2 px offset that tolerance can absorb.
- **(b) Passes the locked rule on inactive IoU (+0.037), but the result is weak.**
  - It is not robust over test cells: the CI includes 0, and it rests on the 3-cell caveat.
  - Crack argmax metrics are unchanged.
  - Crack AP is lower (−0.020).

Not claimed: tuning R, a tolerant Dice term, other label fractions, or other splits.
