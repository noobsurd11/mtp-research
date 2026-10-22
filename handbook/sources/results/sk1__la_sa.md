# S-a: fixed logit adjustment (τ = 1) on existing P-series checkpoints (22 Oct 2026)

**Status:** CONFIRMED by the critic (agent 4): own-scorer recompute of the 23 checkpoints at 5% matches to 4 decimals (`team_2026-10-21/skcdf/review_v2.md` addendum, `verify_a4/sa_verify_a4.txt`). The critic sent the team-lead report.

**Setup**
- Protocol: `team_2026-10-21/skcdf/protocol_sa.md`, written before any S-a number.
- Inference only on cv02 GPU 5 (ledger row `sksa`), 22 Oct 19:35–20:02 IST, rc 0.
- Scorer: `scripts/rescore_logit_adjust.py` (gaint `96dd86a`): z_c − τ·log π_c, with π from each run's own labelled cells.
- Weights: final step 20,000; EMA teacher for SSL arms, model for supervised.

**Files**
- Run list (64 checkpoints): `sa_runs.txt`.
- LA JSONs: `la_sa_test.json` (τ 0, 1, plus the masked-absent variant), `la_sa_val.json` (τ 0, 0.5, 1, 2).
- Logs: `la_sa_test.log`, `la_sa_val.log`.
- Full tables: `la_sa_tables.md`, from `scripts/sk1_sa_analysis.py`.

**Checks**
- τ = 0 reproduces every P-series re-score JSON: max |diff| = 0 on crack and inactive IoU, AP and relF1@2, for all 64 runs.
- Per-cell sums equal the pooled values (max |diff| 0).
- 12 runs (20–50% arms) predict a class absent from their labelled cells on more than 0.1% of test pixels at τ = 1. Masking those classes changes crack and inactive IoU by at most 0.0001, so the unmasked numbers are reported.
- relF1@2 is computed on all 50 cells only. The LA output holds per-cell TP/FP/FN, not relaxed counts, so the reduced cell sets cover IoU only.
- **Seen before S-a:** A5c's LA effect was already measured in SK1 (same checkpoints). Its row is a re-run of a seen contrast and is not confirmatory. SK1's own BsD5 runs are not in S-a.

## 1. Free gain from LA τ = 1 per arm (test, all 50 cells)
Δ = X+LA − X, paired by checkpoint: mean ± sd [min, max], n(Δ > 0).

| Arm | n | crack IoU Δ | inactive IoU Δ | crack relF1@2 Δ | crack precision |
|---|---|---|---|---|---|
| A5c (seen) | 5 | +0.0154 ± 0.0016, 5/5 | +0.0106, 5/5 | +0.0089, 5/5 | 0.626 → 0.592 |
| Cs5 | 3 | +0.0206 ± 0.0069, 3/3 | +0.0223 | +0.0153 | 0.617 → 0.575 |
| CsM5 | 5 | +0.0199 ± 0.0038, 5/5 | +0.0206 | +0.0126 | 0.612 → 0.565 |
| BsM5 | 5 | +0.0233 ± 0.0056, 5/5 | +0.0217 | +0.0121 | 0.635 → **0.554** (−0.081, flag) |
| BsD5 (P17) | 5 | +0.0157 ± 0.0019, 5/5 | +0.0056 | +0.0079 | 0.616 → 0.588 |
| A10 | 3 | +0.0108 ± 0.0007, 3/3 | +0.0090 | +0.0044 | 0.643 → 0.606 |
| BsM10 (expl.) | 3 | +0.0122 ± 0.0014, 3/3 | +0.0174 | +0.0059 | 0.652 → **0.588** (−0.064, flag) |
| A20 | 5 | +0.0104 ± 0.0065, 4/5 | −0.0053 | +0.0001 | 0.688 → 0.658 |
| S20 | 5 | −0.0004 ± 0.0209, 3/5 | −0.0008 | −0.0147 | 0.576 → 0.533 |
| BsM20 (expl.) | 5 | +0.0013 ± 0.0312, 4/5 | −0.0031 | −0.0172 | 0.635 → 0.586 |
| A50 | 5 | +0.0061 ± 0.0047, 4/5 | −0.0133 (0/5) | +0.0038 | 0.597 → 0.578 |
| S50 | 5 | +0.0060 ± 0.0054, 4/5 | −0.0074 (0/5) | +0.0003 | 0.667 → 0.639 |
| A100 | 5 | −0.0016 ± 0.0036, 3/5 | −0.0001 | +0.0020 | 0.586 → 0.555 |
| Sx100 | 5 | −0.0013 ± 0.0034, 3/5 | −0.0013 | +0.0002 | 0.641 → 0.594 |

**Rule-1 arithmetic for X+LA − X** (seed-level threshold; per arm in `la_sa_tables.md`):
- **Crack IoU passes at 5% for every arm:** A5c, Cs5, CsM5, BsM5, BsD5. It also passes for A10.
- **20%:** passes only without the noisy cell (A20, S20). S20 and BsM20 carry noisy-cell seeds with sd up to 0.04.
- **50% and 100%:** n.d.
- **Inactive IoU and relF1@2:** n.d. everywhere except Cs5's relF1@2.
- **Precision flags (> 0.05 drop):** BsM5 (−0.081) and BsM10 (−0.064). No other arm.

## 2. Yardstick: does the SSL crack gain survive a free bias on the supervised arm?
Δ (threshold), all 50 cells, crack IoU / inactive IoU / crack relF1@2; ">" means past the threshold.

| Contrast | SSL − sup | (SSL+LA) − (sup+LA) | **SSL (no LA) − (sup+LA)** |
|---|---|---|---|
| CsM5 − A5c | +0.0137 / +0.117 > / +0.033 > | +0.018 > / +0.127 > / +0.037 > | **−0.0017** / +0.106 > / +0.024 |
| BsM5 − A5c | +0.0289 > / +0.107 > / +0.045 > | +0.037 > / +0.118 > / +0.048 > | **+0.0135 (0.0159)** / +0.096 > / +0.036 > |
| BsD5 (P17) − A5c | +0.0232 > / +0.117 > / +0.037 > | +0.024 > / +0.112 > / +0.036 > | **+0.0079 (0.0108)** / +0.107 > / +0.028 > |
| Cs5 − A5c | +0.004 / +0.105 > / +0.018 | +0.009 / +0.117 > / +0.024 > | −0.012 / +0.095 > / +0.009 |
| BsM10 − A10 (expl.) | +0.012 / +0.132 > / +0.013 | +0.014 > / +0.141 > / +0.015 | +0.002 / +0.123 > / +0.009 |
| S20 − A20 | −0.040 / +0.029 / −0.070 | −0.051 / +0.034 / −0.085 | −0.050 / +0.034 / −0.070 |
| BsM20 − A20 (expl.) | −0.006 / +0.060 > / −0.018 | −0.015 / +0.063 > / −0.035 | −0.016 / +0.066 > / −0.018 |
| S50 − A50 | +0.039 / +0.006 / +0.053 | +0.039 / +0.012 / +0.050 | +0.033 / +0.019 / +0.049 |
| Sx100 − A100 | +0.028 / +0.003 / +0.040 | +0.028 / +0.002 / +0.038 | +0.030 / +0.003 / +0.038 |

The four cell sets are in `la_sa_tables.md`. The pattern is the same in each:
- **Without the twins,** every SSL − (A5c+LA) crack difference is between −0.014 and +0.004 at 5%, n.d.
- **Without the noisy cell,** the 20% rows stop being dominated by the noisy-cell seeds.

## 3. Reading (interpretation)
- **A fixed prior shift is worth +0.015 to +0.023 crack IoU at 5% labels, +0.011 to +0.012 at 10%, about +0.010 at 20% (A20; without the noisy cell also S20 and BsM20), and about 0 at 50–100%.**
  - The free gain shrinks as labels grow, as expected if the head's crack prior is the bottleneck at low label counts.
  - Inactive gains are small and turn slightly negative from 20% up.
- **The crack-IoU gain claimed for SSL at 5% is the same size as what a free logit bias gives the supervised model:**
  - BsM5 +0.0135, BsD5 +0.008 and CsM5 −0.002 against A5c+LA, all n.d.
  - The inactive gains (+0.10 to +0.12) and most relF1@2 gains survive.
- **LA adds to SSL rather than replacing it:** (SSL+LA) − (sup+LA) still passes on crack for BsM5, BsD5 and CsM5.
  - Any crack claim should therefore be stated against base+LA, as agent 2 proposed.
  - The BsM arms pay the largest precision cost under LA (BsM5 −0.081).
- **Limits:**
  - τ = 1 was fixed after seeing SK1's LA rows. It is the theoretical value, not tuned on test.
  - Val (description only): crack IoU rises from τ = 0 to τ = 1 in every 5–20% arm. At 50–100% it is flat. τ = 2 collapses val crack IoU from 20% up (e.g. A50 0.377 → 0.195).
  - One split.
  - **relF1@2 in the reduced cell sets** comes from the critic's scorer, which keeps relaxed counts (`verify_a4/sa_verify_a4.txt`). Without the 7 twins:
    - BsM5 − (A5c+LA): relF1@2 +0.028 (0.029), n.d.;
    - BsD5 − (A5c+LA): relF1@2 +0.024 (0.023), passes;
    - Cs5 − (A5c+LA): crack IoU −0.023 (0.014), WORSE.
