# P8 protocol: P7's arms on the base recipe that has label-efficiency headroom (L3)

Locked 10 Oct 2026, after P6 and before any P8 run. P7 (base L0) keeps running unchanged as locked.

## Why this exists (disclosed post-hoc choice)
P6 rule 2 selected L0 as P7's base. Rule 3, computed literally, then found L0 has no headroom: pooled AP −0.001 from 10% to 100% labels, so P7 is a pilot.

L3 (`smp_unetpp` resnet34 ImageNet + CE+Dice, label-safe) has a large gap, 10% → 100% labels (P6, `results/p6/README.md`):
- pooled AP +0.159;
- crack IoU +0.075;
- inactive IoU +0.135.

The base was chosen using P6 val+test results. The choice applies to every P8 arm equally, so it does not favour any arm. P8 asks the same question as P7 on this base.

## Fixed for all arms
P7's protocol verbatim except for the base:
- `model.name=smp_unetpp loss.supervised=ce_dice` (P6 L3).
- Revised masks; seed-0 split; 10% labels (47 images); unlabelled = 431 train images, labels hidden; batch 8 + 8.
- Mean Teacher EMA 0.999, weak teacher view, label-safe strong student view.
- λ: 0 for 2,000 steps, linear ramp over 2,000 steps to 1.0.
- 20,000 steps; seeds 0–2; cv02 RTX A6000, at most 3 runs per GPU.
- Code commit `0367079`, the same as P7.
- Evaluated weights: the EMA teacher (what `rescore_label_versions.py` picks for `mean_teacher`), identical for all arms.

## Arms
| Arm | Unlabelled loss |
|---|---|
| A (reference, no new runs) | P6 L3 10%: pure supervised pipeline |
| B | `confidence_ce`, t_pos 0.95 |
| C (proposed) | `tolerant_pl`, t_pos 0.95, rare = {crack, inactive}, R = 2 px |
| D (loss-off control) | arm C with λ_final = 0 |

## Metrics
P6 showed that AP on this base is dominated by unrankable pixels: 42% of GT crack and 65% of GT inactive score < 0.001. A pseudo-label loss can change that saturation without changing the segmentation. So the primary metrics for P8 are fixed now, before any run:
- **Primary:** test crack IoU, test inactive IoU, test crack relaxed F1@2. All use argmax and revised labels.
- **Secondary:**
  - crack and inactive AP, reported with the bin-0 share from `scripts_gaint/score_histograms.py`;
  - val;
  - old labels;
  - relaxed precision@2.

## Decision rules
1. **C helps** if mean(C) − mean(D) on any primary metric is > 0.01 and > 2·√((sd_C² + sd_D²)/3), with no primary metric worse by the same rule. B vs D uses the same rule.
2. **C beats B** under the same rule for C − B. If C helps but does not beat B, the claim is "a correct pseudo-label loss helps", not "tolerance helps".
3. **Width check:** if C's crack gain comes with crack relaxed precision@2 falling by > 0.05 against D, flag it as possible fattening.
4. **Headroom:** the gap SSL tries to close is L3@100% − D. It is reported as the share of the gap closed: (C − D) / (L3@100% − D), per primary metric.

## Not claimed
- Confirmation of P7. P7 and P8 are different bases.
- Any tuning of R, t_pos or λ.
- Results beyond this split and dataset.
