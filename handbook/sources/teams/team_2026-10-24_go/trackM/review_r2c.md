# MC review of `protocol_r2c.md` (Dice on crack, inactive and gridline)

MC, 24 Oct 2026. **Verdict: APPROVED, low priority.** It runs only in lanes no higher-ranked rung needs (R3 Part B and R5 first). Two edits before launch; no re-review needed.

## F1. State the val motivation
- The rung was designed after R2's test numbers. It is admissible because val shows the same gridline gain: 0.308 to 0.409 (`results_r2.md`).
- Write that val number into "What I had seen" as the motivation, beside the disclosed test number.

## F2. Name crack recall as a guard
- R2 lost crack recall (−0.025), the user's main target.
- Flag R2c if crack pixel recall or relR@2 falls by more than 0.01 against SUP100 (without the noisy cell). The flag is reported, not a verdict.
- Report gridline precision beside gridline recall: R2's gridline gain came with −0.117 precision.

## Notes
- **Expected value (R):** +0.05 to +0.10 gridline IoU is +0.004 to +0.008 on a 13-class mIoU, under the 0.01 floor. A val-inclusion pass is therefore unlikely; the useful outcome is per-class.
- **Grad-norm kill/flag:** at 1.5x SUP100, agreed. Compare against `m_sup_gn_s0` over the same step range.
