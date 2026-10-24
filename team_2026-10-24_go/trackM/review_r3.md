# MC review of `protocol_r3.md` (encoder pilots on val, then the winner at 5 seeds)

MC, 24 Oct 2026. **Verdict: APPROVED, after fixes F1 to F3.** These are edits made before launch and logged in `log.md`. The 300-step smokes may run now.

## F1. Part B seed 0 equals the pilot
- Training is deterministic per machine. "All 5 seeds are run fresh" therefore re-creates the pilot exactly for seed 0, and that run was selected for its high val score.
- **Fix:** Part B uses seeds **1-5**. The comparator SUP100 uses 0-4. Seeds are not paired in rule 1, so this costs nothing.
- Alternatively, keep 0-4 and disclose that s0 is the selected pilot, but seeds 1-5 is cleaner.

## F2. The pass rule must match design §1 and C6
The same as review_r2 F1: pass on both sets, or pass on one with a same-sign n.d. on the other; worse on either set fails.

## F3. Name the source secondaries now (C's request, Track D `verify_probe.md`)
- BMRK crack recall, relR@2 and AP.
- CSIR and ARTS crack IoU.
- A per-source table for every primary.

The probe predicts a source trade (BMRK up, CSIR/ARTS down). A pooled n.d. must not hide it. AP needs per-pixel scores: if `m0_audit` stores only bands, add a per-source crack AP to the scorer before Part B, and use it on SUP100 too.

## Checks
- **Threshold arithmetic** (E): SUP100 val scores 0.6399, 0.6381, 0.6383, 0.6409, 0.6416 give mean 0.63976 and sd 0.00157, so the threshold is 0.6413. I will recompute the five scores from `m0/*.json` before the pilots finish.
- **Selection risk** (R): with 1 seed per pilot and a 1-sd bar, an encoder no better than R34 qualifies about 16% of the time, so about 40% across 3 candidates. Part B on fresh seeds is the protection, so this is acceptable. The selection score has no inactive. Agreed.
- **Recipe:** L3 for all encoders, no LR tuning. If ConvNeXt with Adam at 1e-3 under-trains, the result reads "at the L3 recipe", not "ConvNeXt is worse".
- **Two-change label** for P-cnxt: agreed.
- **1-channel input:** smp sums the first-conv RGB weights for `in_channels=1`. Confirm in the smoke that the `tu-convnext_tiny` stem gets the same treatment, by printing the stem weight shape.
- **Compute reporting:** params, FLOPs, GPU-h and peak memory. Agreed, and it goes into every claim.
- **No test for pilots:** agreed. Pilot JSONs must hold val only; if `m0_audit` scores test by default, add a `--sets val` switch, or delete the test cells before anyone reads them. I will check that the pilot JSONs carry no test key.
