# MC review of `design.md` (v1)

MC, 24 Oct 2026. **Verdict: CHANGES.** One substantive change (C1) and six smaller ones. Wave 0 (the identity check and switch smokes, under 1,000 steps) may start now. No rung launches until `protocol_rN.md` is APPROVED.

## C1 (substantive). Rung inclusion is decided on test: a selection leak
§2.7 and §5: "winners are then stacked", with winners defined by each rung's test verdict. The final model would then be chosen by test results across 4 to 8 contrasts × 4 metrics × 2 cell sets. That is tuning on test at the recipe level, the same failure as best-val checkpoints, one level up. The team README says "val for every choice".

**Required:**
1. **Inclusion rule on val.** A rung enters the stack if, on val, it is better than the comparator by rule 1 on at least one of val crack IoU, val relF1@2 or val mIoU_rob (val robust list), and worse on none. Val inactive is reported, but it neither includes nor excludes (6 cells).
2. **Test per rung is still scored and reported** under the locked rule, as the confirmatory verdict for that rung. It does not decide inclusion.
3. **If val and test disagree** (val includes, test says worse, or the reverse), it is reported. The val decision stands for the stack, and the disagreement goes to team-lead.
4. **Final protocol:** the stacked recipe plus the R1 layer is scored once on test, against SUP100 (rule 1, both cell sets) and against the best single rung. Disclose in it how many test openings preceded it. E1 ext (106) is reported as the untouched secondary.

## C2. R1b (the ensemble) has no seed replicates; rule 1 does not apply as written
A 5-seed ensemble is one model, so rule 1 has no sd for it.

**Required:**
- The verdict for R1b is the **paired image bootstrap** (2,000 resamples) of ensemble minus the mean single seed, on both cell sets.
- Descriptive spread: the 5 leave-one-out 4-member ensembles.
- Expect the all-50 gain to be inflated: averaging removes s3's noisy-cell failure. Read R1b on the without-noisy set.
- R1a (TTA on vs off, the same 5 checkpoints) can use rule 1. Also report the paired per-seed differences, which are more sensitive.

## C3. R1c operating point: accepted, with a fixed grid
- The rule in §7.2 is accepted.
- Grid: crack bias from 0 to +3 in steps of 0.25, applied to the crack logit only. Fix it in protocol_r1.
- Val metric for the R1c choice: the R1a/R1b model it is applied to (the ensemble, if R1b is used).
- On test, report what the bias costs in crack precision, crack IoU and mIoU_rob. A crack bias also changes the argmax of the other classes.
- The R1c outcome is **descriptive** (an operating point, not a better model). It is never a rule-1 "better".

## C4. R3 pilots: accepted as val selection, with these fixes
- **Pilot score:** the mean of val crack IoU, val relF1@2 and val mIoU_rob. **Inactive is excluded** (6 cells).
- **Threshold:** "beats R34 by > 1 seed sd" uses the SUP100 val sd of that score, over 5 seeds. Compute and fix it in the protocol before the pilots run.
- **Recipe:** the L3 recipe (Adam 1e-3, wd 1e-4, cosine) is kept for every encoder. If a candidate looks under-trained or diverges, report it as "at the L3 recipe". No LR tuning inside this rung; that would be another rung with its own val grid.
- **ConvNeXt on a U-Net decoder** is two changes. Allowed only labelled as such. If it wins, the claim is "encoder + decoder".
- **Compute:** report params, FLOPs per step, GPU-h and peak memory per candidate.
- **Scope:** the R3 pilots go in their own `protocol_r3.md`. R2 is a separate protocol.

## C5. R2 (Dice on all classes): state how Dice treats classes absent from a batch
- **The risk:** splice (16), edge dark (20) and other rare classes are absent from most batches of 8. If the Dice implementation gives an absent class a loss of 1, or a term that pushes predictions to zero, it penalises any prediction of that class. If it masks absent classes, the term is active only on the few batches that contain them.
- **Required:**
  - Name the implementation and its absent-class behaviour, and show it in a unit test.
  - Fix the class list from train GT now.
  - Report per-class IoU, P and R for all 13 robust classes on val and test.
- R2b as the fallback is fine. It is a separate arm, so it needs its own amendment before it runs.

## C6. The pass rule across the two cell sets
- Accepted, with one addition: **"worse" on either cell set fails the rung.**
- Multiplicity: 4 primaries × 2 cell sets. Disclose the count per protocol (handbook 07 §5). No correction is applied, per house practice.

## C7. The identity check and the code base
- Wave 0 is accepted. Requirements:
  - match the stdout losses of `p16_A_100pct_s3` for 1,000 steps exactly;
  - record REVISION;
  - confirm that Track D's `data.labeled_list` is off by default (a diff of the config path).
- Any new switch (R2 dice_classes, R4 labelled list at fraction 1.0, R5 upsampling) must default to bit-identical behaviour, with a unit test.
- I will read the diff in the gaint worktree `el_m` before approving the first protocol that uses it.

## Rulings on §7
1. **mIoU_rob as a fourth primary:** accepted.
2. **R1c rule:** accepted, with C3.
3. **R1 now as its own locked protocol:** yes. It costs about 1 GPU-h and gives a verified number early. The final re-applies the same frozen rules to the new checkpoints.
4. **R3 pilots, 1 seed each, chosen on val:** accepted, with C4.

## Other notes
- §6 "what the user can expect" is speculation. It stays out of anything sent to the user until a result exists.
- R4: fine as ranked. Its protocol needs the class mapping and histograms (data_addendum §5).
- R5: fine. Labels are upsampled with nearest-neighbour and scored at 512 after pooling the logits back. State the pooling (average of the logits).
- R7, R8, R9 and the "not proposed" list: agreed.
