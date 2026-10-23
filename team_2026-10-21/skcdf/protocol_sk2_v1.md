# SK2 protocol v1: BsD5 without background pseudo-labels (S-b), 5% labels, 8 v 8 seeds

**Status: DROPPED, 22 Oct 2026.** The H-cm gate did not pass: probe (b) gives INCONCLUSIVE. True misses are 0.378 of GT crack (passes the ≥ 0.30 bar), but only 0.705 of them carry a confident-background PL (fails the ≥ 0.80 bar); see `second_opinion_a2.md`, "Probe (b) result". Not reviewed, not run. The code switch (`88a7e88`) stays opt-in and unused.

Former status: DRAFT for review (agent 4). User approval via team-lead (22 Oct) is **conditional**. Launch needs both:
1. **The H-cm gate.** The ALHVR critic's probe (b) supports H-cm by its locked thresholds (`second_opinion_a2.md` addendum, locked 22 Oct 19:33 IST):
   - on BsD5, true misses ≥ 30% of GT crack;
   - and ≥ 80% of true misses carry a confident-background pseudo-label.

   If the probe gives "refuted" or "inconclusive", **SK2 does not run.**
2. **`APPROVED` for launch** in `review_sk2_v1.md`.

**What I had seen when writing**
- All SK1 results.
- `diag_agent3.md`.
- `second_opinion_a2.md`.
- No probe (b) number. No S-a number except SK1's own BsD5/A5c LA rows.

Follows up an exploratory observation (SK1 BsDBn5: lower crack bin-0 and higher crack AP; its teacher had lost confident background pseudo-labels late in training).

## 1. Question
Does removing background from the confident pseudo-label set of the decoupled recipe make the unlabelled loss stop reinforcing confident crack misses? In other words: does it lower crack bin-0 and raise crack AP and crack IoU on test?

## 2. Hypothesis (H-cm, background-suppression half)
- **What H-cm says:** the ≥ 0.95 rule turns confident crack misses in unlabelled cells into background targets and reinforces them.
- **Prediction** (from `second_opinion_a2.md`, stated before any SK2 run): crack bin-0 ≤ 0.45 and crack AP ≥ 0.35. BsD5 is at 0.523 and 0.314.
- **Refutation:** a result near BsD5 refutes this half of H-cm.

## 3. Data
- D0 with D7 = yes: BenchmarkEL `20211104`, `masks_escdd`, split seed 0, 5% (23 labelled cells).
- The 448-cell unlabelled pool (7 twins excluded).
- Test 50 cells, val 54 cells.

## 4. Code
- Branch `sk1` on gaint, commit **`88a7e88`** on top of `96dd86a` (tests: `tests/test_sk2.py` 3, suite 225 pass, 3 skipped): opt-in `loss.pl_exclude_classes` (list, default `[]`) in `ConfidenceCELoss`.
  - Pixels whose teacher argmax is in the list are dropped from the confident mask.
  - Normalisation is unchanged: the masked CE sum is divided by all unlabelled pixels, as in `confidence_ce`.
  - Logging: `conf_frac` stays the share passing ≥ 0.95, so it is comparable with BsD5. A new field `used_frac` gives the share actually used after the exclusion. `pseudo_labels.csv` counts stay pre-exclusion.
- **Default `[]` must be bit-identical** to `0ea71df`. Unit test, plus a log-identity check on cv02: `sk1_BsD_5pct_s0` options, 2,500 steps, against `sk1_BsD_5pct_s0.stdout`, every field except time.
- Deployed by `git archive` to cv02 `/tmp/noob_el/el_sk2`, with `REVISION` and `data -> el_p7/data`. The D7 exclusion list is copied as in SK1.

## 5. Arms (cv02, 20,000 steps, final-step weights)
| Arm | Runs | Change | Seeds | Status |
|---|---|---|---|---|
| BsD5 | `sk1_BsD_5pct_s0..4` (SK1, 0ea71df) + `sk2_BsD_5pct_s5..7` (new code, exclusion off) | reference | 0–7 | s0–4 reused after the §4 identity check; s5–7 new |
| **BsDnb5** | `sk2_BsDnb_5pct_s0..7` | BsD5 + `loss.pl_exclude_classes=[0]` | 0–7 | new |
| A5c | P12 s0–2 + P13 s3–4 | supervised reference (descriptive only) | 0–4 | reused (SK1 checks) |

Option strings are SK1's BsD5 string (`scripts_cv02/sk1_queue_d7yes.spec`) plus the arm key. The spec is diffed by script.

New runs: 11. About 2.2 h each alone. At 2 per GPU on 4 free GPUs, about 5 h. GPUs are agreed with the ALHVR track in the ledger beforehand.

## 6. Metrics
- **Co-primaries (declared now): test crack IoU and test crack AP.** AP is binned pixel AP, as in the re-scorer.
- **Guard metrics:** test inactive IoU and crack relF1@2 (the other P-series primaries). Neither may be WORSE.
- **Key secondary:** crack bin-0 share (H-cm prediction); crack precision and recall; relP@2 (width check).
- **Secondary:**
  - val;
  - E1 per-cell on test and on the 106-cell extension, **including crack false alarm**;
  - the mechanism log: `conf_frac`, `used_frac`, pseudo-label class shares at 4k and 20k.

## 7. Decision rules (P8 rule-1 arithmetic, 8 v 8; threshold max(0.01, 2·√((sd_A²+sd_B²)/3)), as every P-series rule)
1. **Primary: BsDnb5 − BsD5.**
   - "Helps": BETTER on crack IoU or crack AP, and no WORSE on crack IoU, crack AP, inactive IoU or crack relF1@2.
   - "Harms": WORSE on any of these four.
   - Otherwise n.d.
2. **Prior-shift yardstick** (descriptive, required by S-a): BsDnb5 − (BsD5+LA τ=1) on the same metrics. A gain that LA τ = 1 already gives is reported as such.
3. **H-cm prediction check** (descriptive): BsDnb5 seed-mean crack bin-0 ≤ 0.45 and crack AP ≥ 0.35. Report met / not met.
4. **Width:** relP@2 drop > 0.05 vs BsD5 is flagged.
5. **Unseen-module cost:** E1 extension crack false alarm, BsDnb5 − BsD5 with bootstrap CI, is reported next to the verdict. An increase whose CI excludes 0 is stated in the verdict line.

- Contrast count: 1 primary + 4 descriptive. No multiplicity correction.

## 8. Robustness
- All four cell sets: all 50 / without `CSIR_00070_r8_c4` / without the 7 twins / without both.
- Paired cell bootstrap (2,000).
- Leave-top-3-out.
- Source split.
- Per-run crack FP on the noisy cell.

## 9. Selection and stopping
- No test or val selection; final-step weights.
- Crashes are resumed bitwise.
- No seed extension.

## 10. Pre-launch checks (after APPROVED and the gate)
- Unit tests.
- §4 identity check.
- Smoke: `smoke_BsDnb`, 300 steps, λ on from step 0, `loss.t_pos=0.0`. This shows that `used_frac` < `conf_frac` and that background is absent from the used set.
- Logs go to the critic before the queue.

## 11. Not claimed
- That background pseudo-labels are wrong in general.
- Other fractions or splits.
- Any reading of SK1's BsDBn5 beyond exploratory.
