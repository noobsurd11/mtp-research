# P9: external unlabelled pool (11,938 cells) on the L3 base, 10% labels. Results

Protocol: `protocols/P9_external_pool.md`, locked before any run (be69ace).

**Runs**
- 9 runs on cv02 (RTX A6000), 10 Oct 22:56 IST to 11 Oct 06:26 IST.
- Every run has rc = 0. All are 20,000 steps; the EMA teacher is evaluated.
- Code: commit `0367079`, the same as P8. Only `data.unlabeled_pool=external` differs.

**Files**
- `raw/`: re-score JSONs and `launch.log`.
- `p9_rules.txt`: `scripts/ssl_rules.py`, plus the bin-0 share.
- `per_image_test.txt`: the bootstrap, all cells and the source split.
- `fig_p9_bars.png`.
- `per_image.json` and `hist_revised.npz`.
- The whole set is reproduced by `bash scripts/post_ssl.sh p9 <gpu> 9`.

## Results
Test, revised labels, mean ± sd over seeds 0–2. P8 and P6 arms are repeated for reference.

| Arm | Pool | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|
| A: L3 10%, supervised (P6) | – | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| D (P8), loss off | 431 | 0.383±0.003 | 0.194±0.034 | 0.796±0.008 | 0.903±0.009 | 0.402±0.008 | 0.201±0.034 |
| C (P8), tolerant PL | 431 | 0.392±0.006 | 0.253±0.109 | 0.811±0.012 | 0.919±0.014 | 0.421±0.011 | 0.317±0.105 |
| **Dx**, loss off | 11,938 | 0.380±0.003 | 0.287±0.032 | 0.792±0.008 | 0.895±0.024 | 0.399±0.003 | 0.282±0.028 |
| **Bx**, hard PL (conf ≥ 0.95) | 11,938 | 0.389±0.010 | 0.347±0.054 | 0.801±0.013 | 0.914±0.015 | 0.423±0.009 | 0.363±0.064 |
| **Cx**, tolerant PL (proposed) | 11,938 | 0.384±0.007 | 0.344±0.023 | 0.799±0.009 | 0.893±0.017 | 0.419±0.004 | 0.364±0.019 |
| L3 100% (P6) | – | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

## Locked rules (primary: test crack IoU, inactive IoU, crack relF1@2)
Each cell shows the difference, then the threshold in brackets.

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| Cx − Dx (rule 1) | +0.004 (0.010) | **+0.056 (0.046)** | +0.007 (0.014) | **Cx helps (inactive IoU passes; nothing worse)** |
| Bx − Dx (rule 1) | +0.009 (0.012) | +0.060 (0.073) | +0.010 (0.017) | Bx does not help |
| Cx − Bx (rule 2) | −0.004 (0.014) | −0.004 (0.068) | −0.002 (0.018) | **Cx does not beat Bx** |

- **Rule 3, width:** crack relP@2, Cx − Dx = −0.003, so OK.
- **Rule 4, share of the gap (L3@100% − Dx) closed by Cx:**
  - crack IoU 5%;
  - inactive IoU 40%;
  - crack relF1@2 9%.
- **Rule 5, pool-size effect** (Cx − Dx) − (C − D):
  - crack IoU −0.005;
  - inactive IoU −0.003;
  - relF1@2 −0.007.
  - So the loss effect is the same with 431 or 11,938 unlabelled cells. The 28× larger pool does not amplify it.

**How to read the one pass.** The effect is the same size as in P8:
- Cx − Dx inactive is +0.056, against P8's C − D of +0.059.
- It passes here because the seed spread is smaller (Cx sd 0.023 against C's 0.109). P8's seed-0 collapse does not recur with the external pool.
- So the pass reflects lower variance, not a larger effect.

## Required robustness reporting
Image bootstrap: cells resampled, averaged over seeds, 2,000 resamples.

| Contrast | Δ, all cells | Δ without top-3 | 95% CI | P(Δ>0) |
|---|---|---|---|---|
| Cx − Dx, crack | +0.004 | +0.008 | [−0.003, +0.014] | 0.88 |
| **Cx − Dx, inactive** | **+0.056** | **+0.026** | **[−0.013, +0.117]** | 0.95 |
| Bx − Dx, crack | +0.009 | +0.009 | [+0.002, +0.016] | 1.00 |
| Bx − Dx, inactive | +0.060 | +0.010 | [−0.017, +0.119] | 0.95 |
| Cx − Bx, crack | −0.004 | −0.001 | [−0.009, +0.001] | 0.06 |
| Cx − Bx, inactive | −0.004 | +0.017 | [−0.028, +0.032] | 0.39 |

- **The rule-1 pass is not robust to the choice of test cells.**
  - The CI on Cx − Dx inactive covers 0.
  - Without the 3 largest inactive test cells, the gain halves to +0.026.
  - The pass rests on seeds; the bootstrap rests on test cells. This contrast passes the first and not the second.
- Hard PL's crack edge over Dx (+0.009) is consistent across cells but below the locked threshold.

**Source split** (`per_image_test.txt`):
- The pool is 77% CSIR and 23% ARTS. Test has 21 CSIR+ARTS cells and 29 cells from other sources.
- Cx − Dx crack IoU: CSIR+ARTS −0.003 [−0.019, +0.023]; other sources +0.006 [−0.002, +0.016].
- So there is **no in-source benefit** on crack.
- The CSIR+ARTS test cells have almost no inactive pixels: the top 3 cells hold 100%. The inactive split is therefore not informative.

## Exploratory
**1. Swapping the pool changes the loss-off control.** With λ = 0, the unlabelled pool affects training only through:
- BatchNorm statistics: student forward over 8 labelled + 8 unlabelled images;
- the data streams.

Even so, Dx − D (P8):
- inactive IoU +0.094 [+0.003, +0.179]; +0.024 without the top-3 cells;
- crack IoU −0.003 [−0.010, +0.003].

Dx's inactive score (0.287) is back at supervised A's (0.294). P8's pipeline handicap on inactive (D − A = −0.101) therefore depends on what shares the BatchNorm batch, not only on the labelled view. P11 isolates the view. A BatchNorm-only control was not run.

**2. The external pool slightly hurts crack on its own sources.** Cx − C (P8): crack IoU −0.007 [−0.015, −0.000] overall, and −0.019 [−0.041, −0.003] on the CSIR+ARTS test cells. Dx − D on CSIR+ARTS shows the same pattern: −0.012 [−0.032, −0.001].
- A plausible reading is that the external CSIR/ARTS cells differ in capture or preprocessing from the benchmark's own cells of the same source. This is untested.

**3. Bin-0 share** (GT pixels scored < 0.001, test):

| Arm | crack | inactive |
|---|---|---|
| D (P8) | 0.419 | 0.758 |
| C (P8) | 0.400 | 0.627 |
| Dx | 0.418 | 0.648 |
| Bx | 0.394 | 0.512 |
| Cx | 0.392 | 0.517 |

- With the external pool, both pseudo-label arms reduce inactive saturation against Dx by about 0.13. That fits their higher inactive IoU and AP.

**4. Rare-class pseudo-label share during training (`rare_frac` in the logs).**
- **Cx:** the share of unlabelled pixels with a rare-class pseudo-target rises over training, from about 0.001 at step 3,000 to 0.006–0.014 at step 20,000.
- **P8's C:** it stays flat at about 0.003.
- So the external pool gives the teacher many more confident defect pixels. This is consistent with CSIR/ARTS production cells carrying more defects. Not tested.

## Reading
- **Locked result:** with the 11,938-cell external pool at 10% labels on L3, tolerant pseudo-labels pass the locked rule against their loss-off control on inactive IoU (+0.056); crack shows no difference.
- **Three qualifications:**
  - It is the same effect size as P8, now with less seed noise.
  - It is not robust to resampling the test cells, because 3 cells drive it.
  - Tolerance does not beat hard pseudo-labels here (Cx − Bx ≈ 0). The P7 advantage of tolerant over hard pseudo-labels (on L0) does not carry over to L3 with this pool.
- **A larger pool does not amplify the loss effect** (rule 5 ≈ 0).
- **Against plain supervised training** (exploratory; not a P9 rule): Cx − A is crack IoU −0.011, inactive IoU +0.049, relF1@2 −0.015. So SSL has not beaten supervised L3 at 10% labels on crack.
- **For the mid-term:** the unlabelled loss gives a consistent but fragile inactive gain of about +0.06 IoU over its control in both pools. The SSL pipeline costs crack about 0.01–0.015 IoU against supervised training. P11 tests whether the matched pipeline removes that cost.

## Caveats
- One split; 3 seeds; 50 test cells.
- Inactive: only 4 of the 47 labelled cells contain it (`results/p10/labelled_set_counts.txt`). 3 test cells hold 59% of its pixels.
- The P8 arms in the comparisons ran with the same code and seeds but in a different launch batch. Co-location affects speed only, because training is deterministic.
