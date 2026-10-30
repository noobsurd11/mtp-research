# Protocol R1: post hoc layer on the SUP100 checkpoints (TTA, 5-seed ensemble, crack operating point)

MD, 24 Oct 2026. Status: **APPROVED by MC** (review_r1.md) after fix F1 (pass rule aligned with design §1/C6), applied 24 Oct. Inference only; no training.

## What I had seen when writing this
- M0 (`baseline.md`, APPROVED):
  - all test and val numbers of the 5 SUP100 checkpoints at plain argmax;
  - val-only numbers for TTA, ensembles, LA and bias (`m0_tune.json`).
- No test number for TTA, an ensemble or a bias exists. The choices below follow from val numbers already seen, so they are disclosed as **val-informed**, as the rules require.

## Question
On the existing 100% checkpoints, how much do the following add on test:
- (a) dihedral-8 TTA;
- (b) averaging the 5 seeds;
- (c) a crack operating point chosen on val?

The answer sets the R1 layer that the final model re-applies with the same frozen rules.

## Fixed
- **Checkpoints:** SUP100 = `p6_L3_100pct_s0..2` (cv02 `el_p6`) and `p16_A_100pct_s3..4` (`el_p13`), final weights at step 20,000 (asserted).
- **Code:** `trackM/scripts/m1_r1.py` + `m_common.py` (the M0 scoring helpers, unchanged), run with `--code /tmp/noob_el/el_m` (`86197f3`, identity-checked).
- **Masks:** escdd val 54 and test 50.
- **Inference:** bf16 autocast, batch 8.
- **TTA:** the 8 dihedral transforms (rot90 × h-flip). They are exact pixel permutations on square 512 cells, hence label-safe. The 8 softmax outputs are averaged after inverting each transform.
- **Ensemble:** the mean of the 5 softmax maps (plain), or of the 5 TTA maps.
- **Argmax** of the log of the averaged probabilities.
- **Crack bias:** b added to log p(crack) before argmax. It changes the argmax of every class, and all of them are scored.

## Decision rules fixed now (applied by the script on val before test is computed)
- **D1 (TTA on the ensemble):**
  - Compute the val score, the mean of val crack IoU, val relF1@2 and val mIoU_rob (val list 0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 15, 16, 21), for the plain ensemble and for the TTA ensemble.
  - The R1 model is the TTA ensemble if its score is higher, else the plain ensemble.
  - Val inactive is not used.
- **D2 (crack operating point, MC C3):**
  - Grid b ∈ {0, 0.25, ..., 3.0}, applied to the R1 model on val.
  - Choose the smallest b with val relR@2 ≥ 0.90, if its val relP@2 is ≥ 0.90. Otherwise choose the b with the highest val relF1@2.
  - The choice is written to `r1_val_decisions.json` before any test inference.
- **Test then computes only:**
  - per-seed plain and TTA;
  - ensemble plain and TTA;
  - the 5 leave-one-out 4-member ensembles (plain);
  - the R1 model at its chosen b.

  No other test variant is computed.

## Contrasts and verdicts
Primaries: crack IoU, inactive IoU, crack relF1@2, mIoU_rob (13-class test list). Each is computed on all 50 cells and without `CSIR_00070_r8_c4`.

| # | Contrast | Verdict method |
|---|---|---|
| R1a | TTA − plain, same 5 checkpoints (5 v 5) | Rule 1 (P8), per primary, both cell sets. **Pass** = rule 1 passes on both sets, or passes on one and is n.d. with the same sign on the other; **worse** on any primary in either set fails (design §1, C6). Also paired per-seed differences (mean, min, max, n > 0) and the paired image bootstrap |
| R1b | ensemble (plain) − mean single seed (plain) | Paired image bootstrap, 2,000 resamples (seed 0): 95% CI and P(Δ > 0), per primary, both cell sets. **Read on the without-noisy set** (C2). Spread: the 5 LOO ensembles. **Pass** = the CI excludes 0 (above) on at least one primary on both sets, or on one set with the same-sign point estimate on the other; any primary whose CI lies wholly below 0 on either set fails |
| R1a×b | TTA ensemble − plain ensemble | Bootstrap as R1b; descriptive (D1 already chose on val) |
| R1c | R1 model at b − R1 model at 0 | **Descriptive only** (C3): report the change in crack P, R, IoU, relP@2, relR@2, relF1@2, crack component recall/precision, inactive IoU and mIoU_rob |

- **Multiplicity:** 2 verdict contrasts × 4 primaries × 2 cell sets = 16 tests, no correction (house practice), disclosed.
- **Width flag (R4):** a crack relP@2 drop > 0.05, or a crack or inactive precision drop > 0.05, is flagged on R1a and R1b.

## Reporting (every contrast)
- Cell sets:
  - all 50;
  - without the noisy cell;
  - without the 7 twins;
  - without both.
- Per source (CFVS, BMRK, ARTS, CSIR, SDLE), with the FP px of subset-absent classes.
- Per-class IoU / P / R for the 13 robust classes.
- The crack capture measures of baseline §4 (relR@2, relP@2, component recall and precision) on all 50 and without the noisy cell, always with precision.
- Noisy-cell check: crack and border px predicted on `CSIR_00070_r8_c4`, plain vs TTA vs ensemble.
- Compute: 8× inference for TTA, 5× for the ensemble, 40× for both, against one plain forward. Training cost of the ensemble: 5 runs (already paid).

## Identity check
The script's `single_plain/<run>` cells must equal M0's per-cell confusion matrices for the same checkpoints (`trackM/m0/<run>.json`), test and val, max |diff| = 0. If they differ, nothing is reported.

## Compute and logistics
- cv02 GPU 7 (Track M lane), tmux `=r1`, about 20-30 min. Ledger row before launch.
- Outputs: cv02 `/tmp/noob_el/trackM/r1/`, relayed to `trackM/r1/` with MD5.

## Not claimed
- That the ensemble is a better *training recipe*. It is 5 models.
- That R1c's operating point is better: it moves along the precision/recall curve.
- Any statement on unseen modules. E1 ext is not scored here; the final protocol scores it once.
