# P11: Mean Teacher with the supervised labelled view, at 10% labels on the L3 base. Results

Protocol: `protocols/P11_matched_pipeline.md`, locked before any run.

**Runs**
- 12 runs on cv02 (RTX A6000), 11 Oct 06:02–13:50 IST. Every run has rc = 0. All are 20,000 steps; the EMA teacher is evaluated.
- Code: commit `24590fb`, with `ssl.labeled_aug=supervised`. The labelled images get exactly the supervised arm's label-safe view.

**Files**
- `raw/`: re-score JSONs and `launch.log`.
- `p11_rules.txt`.
- `per_image_test.txt`: the bootstrap and source split.
- `fig_p11_bars.png`.
- `per_image.json` and `hist_revised.npz`.
- The whole set is reproduced by `bash scripts/post_ssl.sh p11 <gpu> 12`.

## Results
Test, revised labels, mean ± sd over seeds 0–2.

| Arm | Pool | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|
| A: L3 10%, supervised (P6) | – | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| D (P8): loss off, SSL labelled view | 431 | 0.383±0.003 | 0.194±0.034 | 0.796±0.008 | 0.903±0.009 | 0.402±0.008 | 0.201±0.034 |
| **Dm**: loss off, matched view | 431 | 0.389±0.002 | 0.295±0.023 | 0.809±0.004 | 0.907±0.010 | 0.395±0.002 | 0.300±0.018 |
| **Cm**: tolerant PL, matched view | 431 | **0.398±0.010** | **0.365±0.055** | **0.827±0.010** | 0.917±0.012 | 0.416±0.012 | 0.401±0.056 |
| **Dmx**: loss off, matched, external | 11,938 | 0.396±0.005 | 0.300±0.049 | 0.815±0.005 | 0.905±0.013 | 0.401±0.004 | 0.301±0.044 |
| **Cmx**: tolerant PL, matched, external | 11,938 | 0.398±0.009 | 0.355±0.038 | 0.819±0.010 | 0.910±0.010 | 0.413±0.010 | 0.398±0.035 |
| L3 100% (P6) | – | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

## Locked rules (primary: crack IoU, inactive IoU, crack relF1@2)
Each cell shows the difference, then the threshold in brackets.

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| Dm − A (rule 1, pipeline check) | −0.007 (0.010) | +0.000 (0.034) | −0.005 (0.010) | **no detectable handicap** |
| **Cm − Dm (rule 2)** | +0.009 (0.012) | **+0.071 (0.069)** | **+0.018 (0.013)** | **Cm helps** |
| Cmx − Dmx (rule 2) | +0.002 (0.013) | +0.054 (0.072) | +0.004 (0.013) | Cmx does not help |
| **Cm − A (rule 3)** | +0.002 (0.012) | **+0.071 (0.067)** | **+0.013 (0.012)** | **Cm beats supervised** (credited: rule 2 holds) |
| Cmx − A (rule 3) | +0.003 (0.011) | +0.061 (0.049) | +0.005 (0.012) | passes, **not credited** (rule 2 fails for Cmx) |

- **Width check:** relP@2 does not drop in any contrast (+0.000 to +0.010).
- **Gap closed** by Cm (vs L3@100% − A): crack IoU 3%, inactive IoU 53%, crack relF1@2 21%.

## Required robustness reporting
Image bootstrap: cells resampled, paired, 2,000 resamples. Test IoU.

| Contrast | Δ, all cells | Δ without top-3 | 95% CI | P(Δ>0) |
|---|---|---|---|---|
| Dm − A, crack | −0.007 | −0.010 | [−0.016, −0.001] | 0.01 |
| Dm − A, inactive | +0.000 | −0.042 | [−0.092, +0.083] | 0.48 |
| **Cm − Dm, crack** | +0.009 | +0.014 | **[+0.003, +0.016]** | 1.00 |
| **Cm − Dm, inactive** | +0.071 | **+0.070** | **[+0.020, +0.121]** | 1.00 |
| Cmx − Dmx, inactive | +0.054 | +0.014 | [+0.011, +0.074] | 0.99 |
| Cm − A, crack | +0.002 | +0.004 | [−0.004, +0.008] | 0.73 |
| Cm − A, inactive | +0.071 | +0.028 | [−0.009, +0.158] | 0.91 |
| Dm − D (P8), inactive | +0.101 | +0.035 | [+0.014, +0.188] | 1.00 |

**Reading:**
- **The loss effect is robust.** Cm − Dm holds over test cells on both classes, and the inactive gain survives leaving out the 3 largest inactive cells (+0.070). It holds in both source groups (crack on CSIR+ARTS +0.022 [+0.015, +0.033]; inactive on CFVS/BMRK/SDLE +0.073 [+0.016, +0.127]). This is the first unlabelled-loss effect in P7–P12 that survives both the seed rule and the cell bootstrap.
- **SSL vs supervised is a seed-level pass only.**
  - Cm − A passes the locked seed rule, but its inactive gain is not robust over test cells (CI covers 0; +0.028 without the top 3).
  - Crack IoU is level.
  - The relF1@2 pass is narrow (+0.013 against a threshold of 0.012).
- **The matched view removed most of P8's handicap.** The P8 loss-off control lost 0.10 inactive IoU through the labelled view (Dm − D: +0.101).
- **A small crack handicap remains.** Dm − A = −0.007 [−0.016, −0.001], consistent with BatchNorm mixing. So about 0.007 of Cm's crack gain over Dm only offsets it. P13's separate forward removes this channel.

**Bin-0 share** (GT px scored < 0.001, test):

| Arm | crack | inactive |
|---|---|---|
| Dm | 0.429 | 0.653 |
| Cm | 0.402 | 0.508 |
| Dmx | 0.419 | 0.639 |
| Cmx | 0.404 | 0.531 |

As in P8–P10, pseudo-labels de-saturate inactive. Dmx ≈ Dm shows that, with the matched view, the external pool no longer moves the loss-off control as it did in P9.

## Caveats
- One split; 3 seeds; 50 test cells.
- Inactive: 4 of the 47 labelled cells contain it.
- The P6 reference ran in a different launch batch (training is deterministic per machine).
- The relF1@2 bootstrap is in E1 (`results/e1`), not here.

## E1 addendum (11 Oct, after the locked analysis)
Per-cell task metrics and the relF1@2 bootstrap, from `results/e1/e1_p11.md` (definitions: `results/e1/README.md`). Paired image bootstrap, 2,000 resamples. Test = 50 cells; ext = 106 extension cells from unseen modules.

| Contrast | Set | crack relF1@2 (pooled) | crack tolF1 (per cell) | crack false alarm | inactive cell IoU |
|---|---|---|---|---|---|
| Cm − Dm | test | **+0.018 [+0.010, +0.032]** | **+0.039 [+0.015, +0.067]** | 0 vs 0 | **+0.076 [+0.014, +0.172]** |
| Cm − A | test | **+0.013 [+0.005, +0.024]** | **+0.036 [+0.014, +0.061]** | 0 vs 0 | +0.028 [−0.005, +0.072] |
| Cm − Dm | ext | +0.012 [−0.018, +0.044] | **+0.035 [+0.009, +0.063]** | **+0.122 [+0.063, +0.191]** (worse) | +0.020 [−0.068, +0.120] |
| Cm − A | ext | −0.013 [−0.047, +0.021] | +0.012 [−0.017, +0.043] | **+0.113 [+0.049, +0.186]** (worse) | **+0.071 [+0.001, +0.166]** |
| Cmx − A | ext | +0.020 [−0.030, +0.065] | +0.021 [−0.013, +0.058] | **+0.068 [+0.004, +0.135]** (worse) | **+0.218 [+0.072, +0.367]** |

- **The relF1@2 part of rule 3 is robust over test cells** (Cm − A: CI excludes 0), unlike the inactive IoU part.
- **On unseen modules, Cm raises crack false alarms.** The share of crack-free extension cells with ≥ 50 predicted crack px rises from 0.13 (A) to 0.24 (Cm). On the test set no arm has any.
- **Cmx improves inactive on unseen modules** (cell IoU +0.22, pooled IoU +0.085 [+0.009, +0.225]), as P9's Cx did. Only 1 of the 106 extension cells comes from a module that has cells in the external pool, so this is not a module leak.
- These contrasts were not in the locked rules. They are descriptive.
