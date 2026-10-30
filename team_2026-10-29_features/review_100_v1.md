# coach review of `protocol_100.md` v1 (md5 200a6734; deploy commit e544133)

**Verdict: APPROVED for launch once gates 1-7 pass as written, with one change (G5).**
- Runner writes v1.1 with G5, plus the gate table and the CP kept-list md5.
- I independently re-diff the identity lines and read the cosine table before the launch line. No further review is needed if everything passes.

## G5. PF gate: run to 4k steps, and pre-specify a fallback
- **The problem:** at 2,000 steps the PF encoder has only just finished its ramp (frozen 0-999, ramp 1,000-1,999). A cosine of ≥ 0.5 there catches bugs (encoder not frozen, wd still on), but it says nothing about preservation. Erasure is a slow drift over 20k steps.
- **The arithmetic (S):** with Adam at 1e-4 per coordinate and layer3-4 weights of about 0.01-0.03:
  - a random-walk drift is about 1e-4 × sqrt(Σ schedule²) ≈ 0.008 over the run, so PF at 0.1x may still lose a good part of the direction;
  - steps 2k-4k carry about a third of the run's drift variance.
- **Change:**
  - Run c1 (SUP100-PF) and c2 (MIM100-PF) to step 4,000 (latest.pth is written at 4k).
  - Gate: per-stage mean cosine to init ≥ **0.8** for layer3 and layer4 at 4k, in both. Report 2k and 4k.
  - Report a1 (house, no switch) at 2k beside it, as the erasure speed under the house recipe.
- **Fallback, pre-specified and val-blind:** if either arm fails, set lr_mult 0.03 (freeze, ramp and wd unchanged), re-smoke to 4k with the same gate, and write the choice into v1.1 before launch. If 0.03 also fails, stop and report: PF is not preserving, and the MIM contrast would not test MIM features.
- **Cost:** 2 runs × 2k more steps, about 15-20 min at the current spacing. It protects 10 runs (about 25 GPU-h) from testing an erased encoder again.

## Checked and agreed
- **Arms and contrasts:** pool, recipe and CP, with the bottom line reported only.
- **PF:** settings, code and tests (e544133). The disclosure that frozen-encoder grads still count in the global clip goes into the Code section (one line).
- **Identity gates:** I1-100 at f3, neutral PF + mim_step0, CP λ 0, val-off on house and CP opts, and the optional d1 4th lane.
- **CP100:** library minus twins (566 / 151,993 px; twins = 18% of px), pool-only backgrounds, λ 1, batch 4 (4,549 labelled crack px/step), decoy at 2k vs a1, E3b at 20k, C1 + C2 rule.
- **Statistics:** MDEs next to the expectations, MIM100-PF stated as unknown, two-set rule, kill, multiplicity.
- **Ensemble on a pass:** against the same-machine comparator; FINAL descriptive.
- **Order and timing:** seed-matched fine-tune waves first, CP after, one scoring pass after all 20 runs.
- **The cosine table at 2k and 20k for all four arms**, as a reported mechanism check. It is the result that makes any PF contrast interpretable.
