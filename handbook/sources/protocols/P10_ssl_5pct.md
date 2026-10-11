# P10 protocol: SSL at 5% labels on the L3 base, in-domain and external pools

Locked 10 Oct 2026, ~23:05 IST, before any P10 run. The user approved overnight SSL runs on all resources ("go for p9 then, we need to focus on the SSL as well, night long").

## Why this exists
At 10% labels, interim P8 shows no detectable gain from the unlabelled loss.

Semi-supervised gains usually grow as labels shrink. P10 halves the labels to 23 cells, the committed `seed0/labeled_5pct.txt`, where the label gap should be larger. It crosses that with the two unlabelled pools:
- in-domain: 455 hidden-label training cells;
- external: 11,938 cells, as in P9.

The question was chosen after seeing interim P7/P8 numbers. That is disclosed here. It applies equally to every P10 arm.

## Fixed for all arms
P8's protocol verbatim, except `data.labeled_fraction=0.05`. That means:
- code commit `0367079` (cv02 `/tmp/noob_el/el_p7`);
- L3 base `model.name=smp_unetpp loss.supervised=ce_dice`;
- label-safe views;
- revised masks; seed-0 split; batch 8 + 8;
- λ: 0 for 2,000 steps, ramp over 2,000 to 1.0;
- 20,000 steps; seeds 0–2;
- EMA teacher evaluated.

## Arms
| Arm | Unlabelled loss | Pool | Hardware |
|---|---|---|---|
| A5 (reference only) | none: supervised pipeline, P6 L3 options at 5% | – | gaint (RTX PRO 4500), so not used in any rule |
| D5 | `tolerant_pl`, λ_final = 0 | in-domain (455) | cv02 |
| C5 | `tolerant_pl`, R = 2 px | in-domain (455) | cv02 |
| Dx5 | `tolerant_pl`, λ_final = 0 | external (11,938) | cv02 |
| Cx5 | `tolerant_pl`, R = 2 px | external (11,938) | cv02 |

There is no hard-pseudo-label arm. P8/P9 carry the "C beats B" question. Compute goes to the label-budget and pool axes.

## Metrics
As P8:
- **Primary:** test crack IoU, inactive IoU, crack relaxed F1@2, at argmax with revised labels.
- **Secondary:** AP with bin-0 share, val, relaxed precision@2.

## Decision rules
1. **C5 helps** if mean(C5) − mean(D5) on any primary metric is > 0.01 and > 2·√((sd²+sd²)/3), with no primary metric worse by the same rule. **Cx5 helps** uses the same rule against Dx5.
2. **Width check:** if a crack gain comes with crack relaxed precision@2 falling by > 0.05 against the matching D arm, flag it.
3. **Gap closed:** (C − D) / (L3@100% − D), per primary metric, with P6's L3@100% (cv02).
4. **Label-budget interaction (secondary):** (C5 − D5) against P8's (C − D) at 10%, and (Cx5 − Dx5) against P9's (Cx − Dx).

## Required robustness reporting
- The image bootstrap and leave-top-3-cells-out check on every rule-1 contrast.
- The P9 source split (CSIR+ARTS test cells against the rest) for the external-pool contrast.
- How many of the 23 labelled cells contain any inactive pixels. Inactive results at 5% may rest on very few labelled examples.

## Not claimed
- Tuning of R, t_pos or λ.
- Results beyond this split and dataset.
- Any A5-against-cv02 comparison beyond a descriptive label curve: A5 runs on different hardware.

## Amendment, 10 Oct ~23:10 IST, before any B5 run (no P10 results seen)
- **New arm B5:** `confidence_ce`, t_pos 0.95, in-domain pool, seeds 0–2, cv02. It fills the third slot on GPUs 0–2.
- **Rule:** C5 beats B5 is tested with the rule-1 test applied to C5 − B5. If C5 helps but does not beat B5, the claim is "pseudo-labels help at 5%", not "tolerance helps".
