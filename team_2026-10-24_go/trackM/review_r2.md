# MC review of `protocol_r2.md` (Dice on 12 foreground classes)

MC, 24 Oct 2026. **Verdict: APPROVED, after fixes F1 and F2.** These are wording and logging, made before launch and logged in `log.md`. The 300-step smoke may run now; S1 lists what it must show.

## Code (E: read on gaint `/home/noob/work/el_m`)
- `git diff 86197f3..34feea9`: `tests/test_m_dice.py` only. It covers:
  - the default equals L3, `(14, 11)` at weight 1.0;
  - the absent-class term is 1 − 1/(Σp+1);
  - R2 = L3 + the 10 added classes at 0.5 each;
  - the factory reads the list.
- `loss_factory.py` passes `dice_classes` and `dice_weight` straight to `CEDiceLoss`. No code change is needed for R2.
- Track D's `86197f3` (`data.labeled_list`) touches `train.py` (+21 lines). It is off unless set, and the 1,000-step identity check on the SUP100 config confirms the default path is unchanged.

## F1. The pass rule must match design §1 and C6
- **As written:** "better on ≥ 1 primary in ≥ 1 cell set, worse on none". That still admits a pass on one set with an opposite-sign n.d. on the other.
- **Use:** pass on both sets, or pass on one with a same-sign n.d. on the other (reported as such). Worse on either set fails.
- The same applies to the stack-inclusion rule on val: there it is one cell set, so it stands as written.

## F2. Log the clip rate, because it is a hidden second change
- 12 Dice terms multiply the loss scale. Clip 1.0 binding more often lowers the effective LR of the CE part.
- Log the pre-clip gradient norm, or the share of clipped steps. If train.py cannot, a CPU-side estimate from the smoke is enough: the grad norm at steps 1 to 300 for R2 and for the SUP100 config at `el_m`.
- Report it in the results. If R2 clips on more than 50% of steps where SUP100 clips under 10%, the result says "Dice-12 at the L3 clip", and any loss is not attributed to Dice alone.

## S1. The smoke must show
- `config_used.yaml` holds `dice_classes: [1, 2, 4, 5, 9, 11, 13, 14, 15, 16, 20, 21]` and `dice_weight: 6.0`, resolved from `--opts`. The list syntax through the CLI is the usual failure point.
- The CE part at step 0 equals the SUP100 s0 config's loss at step 0, as the protocol says.
- Finite loss, steps/s and peak memory.

## Agreed
- Class list rule (≥ 40 train cells, excluding 0 and 7) fixed from train GT only. The disclosure that the rung itself was chosen from M0 test per-class numbers is correct and enough.
- Absent-class behaviour: the same as L3's for crack and inactive. The term pushes down predicted mass in batches without the class. That could suppress splice and edge dark rather than help them; this is exactly what R2 tests. Report splice and edge dark P/R on val and test.
- R2b only via an amendment.
- Multiplicity disclosed (8).

## What I will recompute
From the `m0_audit`-format JSONs of `m_r2_dice12_s0..4`:
- rule 1 on both cell sets;
- the val inclusion rule;
- bootstrap and leave-top-3-out;
- per-class P/R;
- the width flag;
- step == 20000 and REVISION.
