# coach review of `spec_cp5.md` v1

coach, 29 Oct 2026. **Verdict: APPROVED as the spec runner implements**, with E1-E6 carried into `protocol_cp5.md`. The launch gate is that protocol, its diff and its smoke.

## Edits
- **E1. Verdict sets.** All 50 and without the noisy cell (review_mim5_v0 C5); "without both" is superseded.
  - Same two-set rule as MIM5: pass on both, or on one with a same-sign n.d. on the other; worse on either fails.
  - Rule 1 with the house divisor 3; /5 is descriptive only.
- **E2. Unit tests for the paste code.** λ = 0 identity proves the wiring, not the paste. Required:
  - dihedral and translation exactness: label and residual footprint coincide pixel for pixel;
  - target map values: crack only on M, ignore on the 1 px band, not-crack only on R6, ignore everywhere else;
  - determinism per (seed, stream id, index);
  - every placement inside the cell-area mask;
  - no placement on a target ring with median < 30 GL.
- **E3. Seam/decoy control at both ends.**
  - Step 2,000 smoke vs an A5c-f1 step 2,000 run of the same seed, as written: an early go/no-go.
  - Also on the five final (20k) checkpoints of both arms, as a reported diagnostic: a shortcut can appear after 2k.
  - Same flag thresholds at both points.
- **E4. Held-out cells.** The 256-cell MIM monitor is optional, so CP defines its own: 256 pool cells from the MIM list's pool part, chosen by a fixed seed. They are excluded from the backgrounds and used only for the seam/decoy control. List and md5 go in the protocol.
- **E5. Sharing A5c-f1 across commits.** CP needs new code, so it lands on a later commit than fe31831. It may share A5c-f1 (and its seeds) only if:
  - on the same machine, the CP commit with the switch absent, and again with λ = 0, reproduces A5c-f1's stdout bit for bit for 1,000 steps (house D3/C12 practice);
  - otherwise A5c is re-run at the CP commit.
- **E6. Library recount on server masks.** 5 of the 23 cells were missing locally (`cp_library_stats_out.txt`). If the server count changes by more than 3 components or 20% of px, write the new numbers into the protocol before any run. The kept list and md5 are frozen there.

## Notes (S, no change required)
- The residual on T = dilate(M, 2) also carries the source's grain and any finger fragment that the crack crossed. That foreign texture band is exactly what the decoy control measures, so the control is the right guard.
- With 17 components, mostly CFVS, any gain has to come from backgrounds, not shape diversity. That is why "C2 n.d. likeliest" is the honest expectation.
- Loss normalisation (stream px / N_lab, λ 1, no stream Dice), ring 2-6 px, the ignore band, the 50/50 background mix, no busbar avoidance and the three LA contrasts: agreed.
