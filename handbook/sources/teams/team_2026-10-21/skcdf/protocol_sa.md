# S-a: pre-registered fixed logit adjustment (τ = 1) on existing P-series checkpoints (inference only)

**Status**
- Approved by the user via team-lead, 22 Oct 2026 ("go" on the critics' proposals).
- Written by agent 3 before any S-a number is computed.
- Critic: agent 4, who recomputes the results.

**What I had seen**
- SK1's τ = 1 effect on SK1 BsD5 (+0.0126 crack IoU) and A5c (+0.0154 crack IoU).
- A5c (P12 s0–2, P13 s3–4) was in that SK1 measurement, so its S-a row is a re-run of a seen contrast and is labelled so.
- No other checkpoint has been scored with LA.

## Question
Does a fixed logit bias, applied to the final weights of recipes we already have, raise test crack IoU, inactive IoU or crack relF1@2?

How large is that free gain compared with the gains claimed for SSL? It becomes the yardstick for any claimed crack gain.

## Method (fixed now)
- **Score function:** `scripts/rescore_logit_adjust.py` (gaint `96dd86a`, reviewed): z_c − τ·log π_c, with τ = 1.
  - π_c is the class pixel frequency in the run's own labelled cells (its `labeled_fraction`, split seed 0, `masks_escdd`; train.txt at 100%).
  - Classes with no labelled pixel get the smallest non-zero π.
  - τ = 0 must reproduce each run's re-score JSON (checked in the script).
- **Weights:** final step 20,000 only (EMA teacher for SSL, model for supervised); weak view, bf16; test 50 cells, revised masks.
- **No τ tuning:** τ = 1 is the only test value. Val is scored at τ ∈ {0, 0.5, 1, 2} for description only.

## Checkpoints (cv02, all existing; reached by read-only symlinks in `el_sk1/experiments`)
| Group | Runs | Seeds |
|---|---|---|
| 5% | P13 A5c (`p12_A` s0–2 + `p13_A` s3–4); P13 Cs5, CsM5, BsM5; P17 BsD5 | 5 / 3 / 5 / 5 / 5 |
| 10% | P6 L3 10% (A10); P18 BsM10 | 3 / 3 |
| 20% | A20 (P6 L3 20% s0–2 + P16 A20 s3–4); P16 S20; P18 BsM20 | 5 / 5 / 5 |
| 50% | P16 A50; P16 S50 | 5 / 5 |
| 100% | A100 (P6 L3 100% s0–2 + P16 A100 s3–4); P16 Sx100 | 5 / 5 |

## Rules (descriptive yardstick; no SSL verdict changes)
1. **Per arm: X+LA − X.** P8 rule-1 arithmetic on the three primaries (seed-level threshold, as every P-series rule). Paired per-checkpoint mean and sd of Δ are also reported.
   - Flag when crack precision drops > 0.05 or crack relP@2 drops > 0.05.
2. **Per fraction: (SSL+LA) − (sup+LA), next to SSL − sup.** Does the SSL gain survive when both arms get the free bias?
   - 5%: BsM5, CsM5, BsD5 vs A5c.
   - 10%: BsM10 vs A10.
   - 20%: S20, BsM20 vs A20.
   - 50%: S50 vs A50.
   - 100%: Sx100 vs A100.
   - P18 rows are exploratory, as in P18.
3. **Robustness:** all four cell sets (all 50 / without CSIR_00070_r8_c4 / without the 7 twins / without both) from the per-cell counts the script writes.

## Not claimed
- That LA is a method contribution.
- Anything about τ ≠ 1 on test.
- Any change to locked P-series verdicts.
