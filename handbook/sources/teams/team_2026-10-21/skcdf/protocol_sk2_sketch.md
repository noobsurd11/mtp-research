# SK2 sketches (NOT a protocol, NOT for launch): candidate follow-ups after the SK1 null (agent 3, 22 Oct 2026)

**Status:** for the critics' diagnosis (`null_diagnosis.md`) and the user's decision via team-lead. Nothing here is approved. No training launches without the user's approval. Every sketch would need a full protocol, a review and `APPROVED`.

**Common to all sketches**
- Data D0 with D7 = yes (448-cell pool), cv02, 20,000 steps, final-step weights.
- Reported on the four cell sets.
- Rule 1.
- References reused only after an identity check.

## S-a. Pre-registered logit adjustment on existing checkpoints (no training) [critic's recommendation (a)]
- **Question.** Does a fixed logit bias (τ = 1, π from each run's labelled cells, fixed now) raise test crack IoU for the recipes we already have?
- **Arms:** existing final checkpoints. LA vs no-LA on the same checkpoint, paired by seed:
  - P13 A5c, BsM5, CsM5;
  - P17 BsD5;
  - SK1 BsD5 and A5c (already measured: +0.0126 and +0.0154 crack IoU, which makes them exploratory here);
  - P18 BsM10, BsM20;
  - P16 / P6 references at 10, 20, 50 and 100%.
- **Rule.** P8 rule 1 on the three primaries, paired by checkpoint, plus a precision floor: a crack precision drop of more than 0.05 is flagged.
  - The SK1 pair is excluded from the confirmatory set because it was seen.
- **Cost:** inference only, about 1 h on one cv02 GPU.
- **Risk:** τ was fixed after SK1. Still, it is the theoretical value, not tuned on test, and the val grid showed a monotone gain to τ = 2.

## S-b. BsD5 without background pseudo-labels (critic: low priority)
- **Question.** Does removing background from the main confident pseudo-labels raise crack AP / IoU on its own? This would test the confound in BsDBn5 (D1: no background pseudo-labels late in training).
- **Arm.** BsD5 + `loss.pl_exclude_classes=[0]`: a new opt-in switch in `confidence_ce`. Background pixels are dropped from the confident mask; normalisation is unchanged, i.e. divided by all pixels.
  - One change versus BsD5.
- **Seeds:** 8 (BsD5 s5–7 added for 8 vs 8). The expected crack IoU effect is at the 5-seed floor.
- **Metrics.** Crack IoU and crack AP as co-primaries, declared before the runs. The other P-series primaries are secondary.
- **Comparisons:**
  - against BsD5;
  - against BsD5+LA τ=1, descriptive;
  - E1 extension crack false alarm, which must be reported because of BsDBn5's +0.105.
- **Label.** "Follows up an exploratory observation (SK1 BsDBn5)."
- **Cost:** 3 BsD5 + 8 new runs ≈ 11 runs, about 7 h on 4 GPUs.
- **Caveat.** BsDBn5 lost background only after about 14k (D1). A whole-run exclusion is a stronger intervention than what BsDBn5 had. A variant that excludes background only after 14k would match it, but needs a schedule switch, which is a second design choice.

## S-c. ABSH without overwriting the evaluated head (mechanism test; only if the critics judge D2 worth testing)
- **Question.** Is SK1's null caused by the late collapse of the evaluated head onto the balanced head (D2)? If the balanced head trains, but the transfer main_l ← aux_l is turned off, does the evaluated head keep its labelled fit while the shared encoder still gets the balanced-loss gradient?
- **Arm.** BsDB5 or BsDBn5 with `absh.transfer_main_l=false` (new switch).
  - The H step into the labelled main head is skipped.
  - The D step and main_u ← aux_u stay.
  - One change versus the SK1 arm.
- **Seeds:** 5, against the existing SK1 arm and BsD5.
- **Expected if D2 is right:**
  - final loss_sup back near BsD5's 0.023;
  - confident background back to about 0.69;
  - crack IoU not below BsD5.
  - If crack AP / bin-0 still improve, the encoder-side effect of balancing is real.
- **Caveat.** This departs further from SKCDF: its main head is meant to learn from the balanced head. It would be "an ABSH-derived variant", not SKCDF.
- **Cost:** 5 runs, about 3 h on 5 GPUs.

## My ranking (for the critics; the user decides)
1. **S-a:** cheap, no training, and directly useful for the thesis: is a free prior shift as good as an SSL tweak?
2. **S-c**, only if the diagnosis concludes the head-collapse mechanism is the main story; it tests that mechanism directly.
3. **S-b:** low, for the critic's four reasons.
