# P17 protocol: SKCDF-style decoupled decoder on the BsM5 recipe, 5% labels

Locked 13 Oct 2026, ~02:00 IST, before any P17 run (smoke excepted). The user's go: "go with ur calls" (13 Oct ~01:45 IST), on the plan sent just before it.

## Question
P13 BsM5 (hard pseudo-labels ≥ 0.95, separate BN, CutMix) beats the supervised A5c at 5% on all three primaries: crack IoU +0.036, inactive IoU +0.113, crack relF1@2 +0.052 (`results/p13/README.md`, secondary, 3 seeds; seeds 3–4 added by P13 Amendment 2).

Does that gain need the decoder to fit pseudo-labels, or does it enter through the encoder?

## Source of the idea
SKCDF (Zhang et al., CVPR 2025, `literature/pdfs/skcdf_cvpr2025/`), Sec. 3.1, "data flow decoupling":
- the labelled decoder is trained on labelled data only;
- an unlabelled decoder is trained on pseudo-labels only;
- both share the encoder, which learns from both;
- the unlabelled decoder follows the labelled one by a parameter EMA, ω = 0.99 (their Eq. 6).

Their ablation (Synapse, 20% labels) credits decoupling with +12.74 average Dice over their pseudo-labelling baseline, out of +19.61 for the full method.

**Taken:** the decoupling only. **Not taken:** the semantic knowledge complementarity module (cross-attention), the auxiliary balanced heads, their optimizer, λ_u = 10, pseudo-labels from the student's own labelled decoder, and inference through the unlabelled decoder as the primary. Name in all write-ups: "SKCDF-style decoupling", never "SKCDF".

## Code
- Commit `f2f20d3` (branch `p17` on gaint, worktree `/home/noob/work/el_p17`), = P13's `bac5264` plus one opt-in switch:
  - `ssl.decouple_decoder=true`: the student's unlabelled forward (strong view, CutMix, BN running stats frozen as in P13) goes encoder → `decoder_u` → `head_u`, deep copies of the labelled decoder and head made at step 0. The labelled decoder and head get no gradient from the unlabelled loss.
  - After every step: `decoder_u ← ω · decoder_u + (1 − ω) · decoder`, parameters only, ω = `ssl.decouple_ema` = 0.99. `decoder_u` keeps its own BN statistics.
  - `decoder_u` has its own optimizer (same type and settings), scheduler (same schedule) and gradient clip (same norm). All are checkpointed in `latest.pth`.
  - Pseudo-labels still come from the EMA teacher (encoder + labelled decoder). Validation and test use the teacher, as in P13.
  - Default off: the P13 step is unchanged.
- Tests: `tests/test_ssl_split.py` (+6): at λ = 0 the decoupled student equals the supervised run bitwise; the unlabelled loss reaches the encoder and `decoder_u` only; the EMA transfer; checkpoint contents; argument checks. Full suite: 203 pass, 7 skipped (gaint CPU).
- Deployed to cv02 `/tmp/noob_el/el_p17` by `git archive f2f20d3` (`REVISION`), `data` symlinked to `el_p7/data`, the same venv as P13.

## Arm
| Arm | Run names | Recipe | Labels | Seeds | Hardware |
|---|---|---|---|---|---|
| **BsD5** | `p17_BsD_5pct_s<k>` | BsM5 options verbatim + `ssl.decouple_decoder=true` | 5% (23 cells), split seed 0 | 0–4 | cv02, GPUs 3–7, one run per GPU |

**References (cv02, existing or running):** BsM5 seeds 0–4 (P13 + Amendment 2, `bac5264`), A5c seeds 0–4 (P12 + P13).

## Built-in pipeline check
λ = 0 for the first 2,000 steps, so until step 2,000 BsD5 seed k is the same computation as BsM5 seed k. The logged losses at steps 50 to 2,000 must match `p13_BsM_5pct_s<k>/train.log` (4 significant digits). A mismatch stops the analysis until explained.

## Metrics
As P13:
- **Primary:** test crack IoU, inactive IoU, crack relF1@2 (argmax, revised labels), from the re-score of the EMA teacher's final weights.
- **Secondary:** AP, relaxed precision@2, E1 per-cell metrics on the 106-cell extension.
- **Secondary decoder (descriptive):** student encoder + `decoder_u`, `test_final_secondary` in `metrics.json` (SKCDF's inference path).

## Decision rules (cv02, 5 vs 5 seeds, P8 rule 1: Δ > max(0.01, 2·√((sd_A² + sd_B²)/3)) on a primary, no primary worse)
1. **Primary: BsD5 − BsM5.**
   - Worse by the rule on any primary: the gain needs the labelled decoder to fit pseudo-labels.
   - Better by the rule: keeping pseudo-labels out of the labelled decoder helps on EL.
   - n.d. on all three: any decoder share of the BsM5 gain is below the detection threshold (reported with the threshold, as a fraction of the BsM5 − A5c gain).
2. **Secondary: BsD5 − A5c** (SSL beats supervised with the decoupled recipe).
3. **Descriptive:** `decoder_u` path vs the teacher path on test.
4. **Width check:** relP@2 drop > 0.05 against BsM5 is flagged.

## Required robustness reporting
- Image bootstrap (2,000 resamples) and leave-top-3-out on rules 1 and 2.
- With and without test cell `CSIR_00070_r8_c4`, labelled post hoc (as P16).
- Per-seed `rare_frac` at steps 4,000 and 20,000 (collapse watch).

## Not claimed
- SKCDF itself, or any comparison with its published numbers.
- Tuning of ω, λ or anything else.
- Other label fractions, the external pool, gaint replication, results beyond split seed 0.
