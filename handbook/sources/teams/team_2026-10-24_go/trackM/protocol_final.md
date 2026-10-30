# Protocol FINAL: assemble the best model and score it once on test

MD, 24 Oct 2026 (draft written before any R3 Part B, R5 or R2c result). Status: **APPROVED by MC** (`review_final.md`) with F1-F4 applied, locked 24 Oct before any R3 Part B, R5 or R2c number was opened.

## What I had seen when writing this
- Verified: M0, R1 (the ensemble gives +0.014 crack IoU), R2 (WORSE), R4 (n.d.), and the three pilots (rn50 selected).
- Running: R3 Part B (`m_r3_rn50_s1..5`), R5 (`m_r5_up2_s0..4`), R2c (`m_r2c_dice3_s0..4`). None of their numbers had been opened.
- Track M test openings before the final: M0 (re-score only), R1, R2, R4, and one each for R3 Part B, R5 and R2c when they finish. **The final is opening no. 7** (to be confirmed at launch).

## Step 1: which recipe (val only, rule C1, already locked per rung)
- **Included rungs** = those of R3 Part B, R5 and R2c that pass the C1 val rule against SUP100: rule 1 on val crack IoU, val relF1@2 or val mIoU_rob (val list), worse on none.
- **If none is included:** the recipe is SUP100 (L3). Go to step 2.
- **If exactly one is included:** that rung's 5 trained seeds are the recipe.
- **If two or more are included:**
  - a **stack arm** with all included changes is trained (5 seeds, its own short amendment with the exact opts, same machine, identity-checked code). **F3:** the amendment needs MC's APPROVED before training. If R3 (ResNet-50) is in the stack, it uses seeds 1-5, because rn50 s0 was the selected pilot;
  - it replaces the best single included rung only if, on val, it beats that rung by rule 1 on crack IoU, relF1@2 or mIoU_rob, and is worse on none;
  - otherwise the best single included rung is used: highest val score = mean(val crack IoU, val relF1@2, val mIoU_rob).

- **F4:** if an included rung was WORSE on its own test verdict, the val decision stands. This is disclosed in the first paragraph of the final README and reported to team-lead before final scoring. The recipe is not changed on that basis.

## Step 2: the R1 layer, re-applied with R1's frozen rules (val only)
- **Ensemble candidates**, all mean-softmax:
  - **E-rec:** the 5 seeds of the step-1 recipe;
  - **E-union:** E-rec plus SUP100's 5 seeds (10 models). Only if the step-1 recipe is not SUP100 itself.
- **Choice:** the candidate with the higher val score (mean of val crack IoU, val relF1@2, val mIoU_rob). E-union must win by more than 0.0016, the SUP100 val sd of that score, to be chosen over E-rec, because it costs twice the inference.
- **TTA on the chosen ensemble:** R1's rule D1 (TTA if its val score is higher).
- **Crack operating point:** R1's rule D2.
  - Grid b ∈ {0, 0.25, ..., 3}.
  - Pick the smallest b with val relR@2 ≥ 0.90 and val relP@2 ≥ 0.90; otherwise the b with max val relF1@2.
  - It is reported both at b = 0 and at the chosen b.
  - The headline is b = 0 if the chosen b trips the R4 width flag on val (crack precision drop > 0.05). This addresses the noisy-cell fragility seen in R1.
- All val decisions are written to `final_val_decisions.json` by the script before any test inference (the m1_r1.py pattern).

## Step 3: one test scoring
**Final model** = the chosen ensemble (+TTA if chosen), at b = 0 and at the chosen b.

**Contrasts (paired image bootstrap, 2,000 resamples, both cell sets; C2):**
1. FINAL − SUP100 mean single seed. The headline "how much better than the old best".
2. FINAL − R1 model (SUP100 5-seed plain ensemble). What the ladder adds beyond R1. **F2:** if the recipe is SUP100 and D1/D2 repeat, FINAL equals the R1 model, so this contrast is dropped and the drop is stated.
3. If the recipe is not SUP100: FINAL − the step-1 recipe's mean single seed. What ensembling adds to the new recipe.

**Verdict per contrast:** pass if the CI excludes 0 on at least one primary in both sets, or in one with a same-sign estimate in the other; any primary with its CI wholly below 0 in either set fails.

**Reported:**
- all four cell sets;
- per source with FP px of subset-absent classes;
- the full 24-class table with P and R;
- crack capture (relR@2, relP@2, component recall and precision);
- the "almost all cracks" target (descriptive);
- the p(crack) < 0.001 share;
- inactive capture;
- the noisy-cell px;
- **E1 ext 106** (F1: scored per rung as a secondary, **never used for selection**);
- compute: number of trained models, inference passes, GPU-h.

**Headline compute** (MC): models trained, members at 4× FLOPs (if R5 is in), inference passes.

**Multiplicity:** up to 3 contrasts × 4 primaries × 2 sets = 24 tests, disclosed with the count of prior test openings.

## Not claimed
- Generalisation to unseen modules beyond what E1 shows.
- That the selection among candidates is optimal. It is a val choice on 54 cells.
