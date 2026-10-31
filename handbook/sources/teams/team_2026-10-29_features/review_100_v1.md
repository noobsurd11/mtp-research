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

## Gate check and gate-6 ruling (coach, 30 Oct, after GATES.txt; v1.1 md5 8dcb231b)
- **Re-diffed independently on gaint** (stripped loss/lr/val lines):
  - a1 == `el_f2/reports/f100/idchk/i1_elm.stdout` (22 lines, val@500/1000 included);
  - a2, a3 and d1 == a1 (22 each);
  - b1 == a1 and b3 == b2 (40 step lines each).
  - Every smoke stdout: 1 header, 0 tracebacks. rc=3 is the designed `--exit_after_step` exit.
- **PF works, with a wide margin:**
  - at 2k: layer3/4 cos 0.996/0.997 (SUP100-PF) and 0.998/0.999 (MIM100-PF);
  - at 4k: 0.975/0.985 and 0.986/0.990;
  - house a1 at 2k: 0.070/0.003. So the house recipe erases the deep encoder within the first 2k steps, not slowly.
- **Launch of the 15 fine-tunes (SUP100-g, SUP100-PF, MIM100-PF): GO** on v1.1 as written.
- **Gate 6 (CP100 decoy at 2k): FLAG on the ratio only.**
  - SUP 0.0031, CP 0.0076 (2.45x), both far below the 0.05 absolute line. Decoy px: about 430 vs 1,050 of 138,656.
  - The 2x line was set at 5%, where the base was 0.0076. At 100% the base fell to 0.0031, so 2x is 0.0062, stricter in absolute terms than at 5%. A seam shortcut would grow with training; a 2k point cannot show growth.
- **Ruling: one more pre-specified data point, decided before any CP100 run and before opening 1.**
  - Resume a1 and b2 from their 2k checkpoints to 4k (bit-identical resume) and rerun the same decoy on the same 248 cells and 553 components. About 20 min, run now at launch, beside the first fine-tune.
  - **GO** if CP_decoy_4k ≤ 0.05 and (CP_decoy_4k ≤ 2 x SUP_decoy_4k or CP_decoy_4k ≤ 0.0094 = 1.25 x its 2k value). That is: the original ratio passes at 4k, or the CP rate is not growing.
  - **STOP** otherwise. CP100 is closed at its gate ("the paste residual carries a growing seam signal at 100%"), and opening 2 is not run.
  - This is a post-hoc amendment of gate 6 by coach, made after the flag and disclosed as such. The CP100 verdict rule (C1 + C2, two sets) is unchanged. E3b at 20k is still reported with the original thresholds; a flag there puts a shortcut caveat on any CP100 result.

### Gate-6 reasoning (team-lead asked whether the relative line still makes sense at 100%; written before the 4k numbers and before any test number)
| 2k decoy readings (E, `decoy_2k.json`) | real | decoy | background | decoy / real | decoy / background |
|---|---|---|---|---|---|
| SUP100 a1 | 0.2899 | 0.0031 | 0.00066 | 1.1% | 4.6x |
| CP100 b2 | 0.3025 | 0.0076 | 0.00086 | 2.5% | 8.8x |
| ref: A5c-f1 at 5% (passed) | 0.2125 | 0.0076 | 0.0012 | 3.6% | 6.4x |
| ref: CP5 at 5% (passed) | 0.2334 | 0.0049 | 0.0003 | 2.1% | 16x |

- **What the decoy test guards against:** a model that learned "paste artefact = crack" instead of crack appearance. Test cells contain no pastes, so such a model cannot fake a test gain. It would waste the arm, or add false positives on band-like textures, which test crack precision and the crack-free-cell false positives report.
  - So gate 6 is a futility and safety gate, not a guard on the verdict's validity. The verdict rule (C1 + C2 on real test cells, two sets) protects the claim either way.
- **Is the 2x relative line still right?** Only partly.
  - It compares CP with its own baseline, and at 100% that baseline is far more selective: decoy/real 1.1% vs 3.6% for A5c at 5%. So the same 2x now fails a CP model whose specificity (2.5%) is better than the 5% baseline that defined "normal".
  - A library about 28x larger does not by itself change the per-placement decoy rate. Each paste still carries one residual band, so library size is not the reason for the flag; the more selective baseline is.
- **Matched bias:** a pure crack-prior shift from pasting would lift real, decoy and background alike. Background rose 1.29x and real 1.04x, but decoy 2.45x. So about 1.9x of the decoy rise is specific to the residual band: a real but small seam sensitivity, about 600 px of 138,656.
- **The honest test is twofold:**
  - specificity (decoy/real well below the passing references; CP100 2.5% now);
  - growth (a shortcut grows with exposure; one 2k point cannot show it).
  - Hence the 4k point and the rule above: GO if ≤ 0.05 and (≤ 2x SUP at 4k or ≤ 0.0094). I add, also pre-stated, **decoy/real at 4k ≤ 3.6%** (the A5c 5% reference) as a third condition for GO.
- **Cost:** the two 4k resumes take one fine-tune slot for about 20 min, so opening 1 shifts by at most about 20 min. The decision is logged (CP_GO / CP_STOP plus the 4k rates) before opening 1 fires.

### Gate 6b result and final CP100 decision (coach, 30 Oct 12:30 IST; before any CP100 run and before opening 1; no test number seen)
| 4k decoy (E, `el_f3/reports/f100/smoke/decoy_4k.json`, 248 cells, 553 comps, step 4000 asserted) | real | decoy | background | decoy / real |
|---|---|---|---|---|
| SUP100 a1 | 0.2462 | 0.0010 | 0.00062 | 0.42% |
| CP100 b2 | 0.2713 | 0.0039 | 0.00073 | 1.43% |

- **Recomputed independently:**
  - (1) 0.0039 ≤ 0.05: yes.
  - (2) ≤ 2 x SUP (0.0021): no. ≤ 0.0094 (not growing): yes. So (2) holds.
  - (3) decoy/real 1.43% ≤ 3.6%: yes.
- **Decision: CP_GO** (written by `f100_gate6b2.sh` at 12:27:37; HOLD removed).
- **Disclosed plainly:**
  - CP100 passes on growth and specificity, **not** on the original ratio line. CP/SUP is 2.45x at 2k and 3.7x at 4k, because SUP's own decoy rate fell faster (0.0031 → 0.0010).
  - CP's decoy rate halved from 2k to 4k (0.0076 → 0.0039), so no developing shortcut.
  - E3b at 20k keeps the original thresholds. If it flags (likely on the ratio), any CP100 result is reported with a seam-sensitivity caveat. The verdict rule (C1 + C2, two sets) is unchanged.

### gaint reboot 30 Oct 16:28: resumed s1 runs (coach, independent re-diff)
- **Re-diffed by coach on gaint.** Each run's `<run>.prereboot.stdout` was compared with the post-marker section of `<run>.stdout`, timestamps and speed stripped:
  - SUP s1, steps 16,050-16,450: loss/lr 9/9 IDENTICAL;
  - SUPPF s1, steps 12,050-12,600: loss/lr 12/12 and PF encoder lr 12/12 IDENTICAL;
  - MIMPF s1, steps 12,050-12,150: loss/lr 3/3 and PF lr 3/3 IDENTICAL.
  - Each stdout has 1 marker, 2 headers and 0 tracebacks. Prereboot md5s: 4e50bba6 / ee1d7a25 / 628364fb.
- **Ruling (1), as pre-stated: the s1 runs count as-is.** Disclose in protocol_100 v1.2: the reboot time, checkpoint md5s/steps (`ckpt_integrity_1635.txt`), the overlap counts above, and runner's first-check awk bug (fixed before any decision).

### Gate 6b in hindsight (coach, 31 Oct, after opening 2; E3b at 20k)
- **The 20k decoy:** CP 0.0125 vs SUP 0.0028 (4.41x); decoy/real 3.1%.
- The 2k → 4k decline (0.0076 → 0.0039) that grounded the GO did not continue: CP's decoy rate tripled by 20k. Condition (2) fails at 20k.
- A late seam sensitivity developed, as E3b exists to catch. It is reported with the original thresholds (FLAG). The CP100 verdict (n.d., `verify_100_o2.md`) is unaffected.
- **Lesson for future decoy gates:** read the trend at the end of training (E3b) as part of the go/no-go wherever compute allows, not only at 2k-4k.
