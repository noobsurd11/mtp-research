# P14 protocol: offset-tolerant supervision for thin labels (E2; directions row 1)

Locked 11 Oct 2026, ~13:45 IST, before any P14 run.

**Context:** the user asked for results within one day and left the GPU allocation to me.

**What I had seen:** P1–P13 as reported. No P14 run.

## Question
Human crack labels carry the same 1–2 px ambiguity as teacher pseudo-labels:
- old vs revised labels agree at 0.73–0.81 IoU, but 0.98 within 2 px (P3);
- crack pseudo-labels have 0.59 pixel-exact precision but 0.96 within 2 px (P5).

So does the tolerant rule that `tolerant_pl` applies to pseudo-labels also help when applied to human labels?
- (a) Does it make training on the noisier old labels closer to training on the revised labels?
- (b) Does it help on the revised labels themselves?

## Code
Commit `be67787` (branch `p14`; cv02 `/tmp/noob_el/el_p14`).

`loss.supervised=tol_dice` is `ce_dice` with its CE replaced by `TolerantPLLoss` applied to the ground truth:
- **Rare-class labels (crack 14, inactive 11):** credited if the class is predicted within R = 2 px.
- **Head-class pixels within 2 px of a rare label:** not scored.
- **Everything else:** plain CE.
- **Unchanged:** the normalisation and the pixel-exact Dice term.

At R = 0 it equals `ce_dice` (tested). 205 tests pass.

## Arms (cv02, 10% labels = 47 cells, split seed 0, seeds 0–2)
All use P6's L3 options verbatim (`supervised.yaml`, `smp_unetpp`, label-safe, batch 8, 20,000 steps, final weights). Each arm makes one change.

| Arm | Run names | Training labels | Loss |
|---|---|---|---|
| L3 (reference, P6) | `p6_L3_10pct` | revised (E-SCDD) | `ce_dice` |
| L3o | `p14_L3o_10pct` | old (`masks_coded`, 20211104) | `ce_dice` |
| L3To | `p14_L3To_10pct` | old | `tol_dice`, R = 2 |
| L3T | `p14_L3T_10pct` | revised | `tol_dice`, R = 2 |

**Scheduling:**
- one cv02 queue, chained after the P13 queue has launched, plus 5 minutes;
- at most 3 runs per GPU, and only on GPUs with < 1,000 MiB used.

**The P6 reference:** it ran at `824fab0`. The `ce_dice` path is unchanged in `be67787`; the diff adds only opt-in code.

## Metrics
Test cells, scored on the **revised** labels, as P8:
- **Primary:** crack IoU, inactive IoU, crack relF1@2.
- **Width check:** crack relP@2.
- **Secondary:** AP and bin-0 share; old-label scores; the per-cell E1 metrics.

## Decision rules
1. **Label-noise gap:** G = L3 − L3o on crack IoU and crack relF1@2.
   - The gap exists if it passes P8 rule-1 arithmetic: Δ > max(0.01, 2·√((sd²+sd²)/3)).
   - If no metric has a gap, rule 2 is void.
2. **Recovery:** on a metric with a gap, tolerance recovers label noise if:
   - L3To − L3o passes rule-1 arithmetic;
   - it is ≥ 0.5·G;
   - the relP@2 drop vs L3o is ≤ 0.05.
3. **Tolerance on revised labels:** L3T − L3 under P8 rule 1 (any primary passes, none worse), plus the width check.
4. **Robustness:** image bootstrap and leave-top-3-out on every contrast in rules 2 and 3. Inactive is reported with the 3-cell caveat (P6).

## Not claimed
- Tuning R.
- A tolerant Dice term.
- Other label fractions.
- Generality beyond this split.
