# MC review of `protocol_final.md` (assemble the best model, score once)

MC, 24 Oct 2026. **Verdict: APPROVED with F1 to F4.** These are wording or scope edits, logged before any Part B, R5 or R2c number is opened. The protocol is locked at that point; no re-review is needed unless the stack branch triggers (F3).

## What is right
- Recipe choice by the per-rung C1 val rule, fixed in advance.
- E-union needs a pre-set margin (0.0016) to beat E-rec.
- TTA and the bias come from R1's frozen D1/D2.
- The width-flag fallback for the headline bias.
- Val decisions are written before test.
- The paired bootstrap is used for single-ensemble contrasts (C2).
- The opening count is disclosed.

## F1. E1 is not "untouched"
- E1 ext was scored and reported for M0, R2 and R4 (and will be for R3B, R5 and R2c). What is true is that it **was never used for any selection.**
- Reword it as "E1 ext, never used for selection; scored per rung as a secondary and once for the final model".

## F2. Contrast 2 when the recipe is SUP100
- If step 1 yields SUP100, and D1/D2 repeat R1's choices, FINAL equals the R1 model and contrast 2 is identically 0.
- In that case drop contrast 2 and say so. Contrast 1 then repeats R1b, which is already verified.

## F3. The stack amendment needs MC approval before training
- Two or more included rungs trigger a stack arm. Its amendment (opts, code, identity check, seeds) needs APPROVED like any rung.
- **Seeds for the stack arm:** use 0-4 if none of its components was chosen with a seed-0 pilot. If R3 is in the stack, rn50 seed 0 was the selected pilot, so use **seeds 1-5**, the same as Part B.

## F4. Disclose val/test disagreement of included rungs
- If a rung enters on val but its own test verdict was WORSE, the val decision stands (C1). The final README must then state this in its first paragraph, and team-lead is told before final scoring.
- This is a disclosure, not a veto; changing the recipe because of it would be selection on test.

## Notes
- **Compute in the headline:** number of trained models, any 4x-FLOP members (R5) and inference passes. "Best model" claims carry this.
- **Per-source and the noisy-cell px:** listed. Agreed.
- **I will recompute:**
  - every final number from the per-cell outputs;
  - D1/D2 and the E-union choice from the stored val cells;
  - the bootstrap with my own code.
