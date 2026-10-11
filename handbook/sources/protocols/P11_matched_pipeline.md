# P11 protocol: SSL on a pipeline-matched Mean Teacher (L3 base, 10% labels, in-domain and external pools)

Locked 11 Oct 2026, ~00:15 IST, before any P11 run. This is part of the overnight SSL work the user approved on 10 Oct ("night long works ... use all resources"). The runs are queued to start when P9/P10 free cv02 GPUs.

## Why this exists (post hoc; disclosed)
P8 found that the loss-off Mean Teacher control D is *below* plain supervised L3 (A):
- crack IoU −0.013, image-bootstrap CI [−0.028, −0.001];
- inactive IoU −0.101, CI [−0.171, −0.031].

The student scores the same as the EMA teacher, so the teacher is not the cause.

What remains differs in the training path:
1. **Labelled view.** The SSL label-safe "strong" view uses jitter ±0.25 with p = 0.8, plus Gaussian noise with p = 0.3. The supervised label-safe view uses ±0.2 with p = 0.4 and no noise.
2. **BatchNorm.** Statistics are taken over 8 labelled + 8 unlabelled images in one forward pass.
3. **Data streams.** The random streams differ.

P11 removes difference 1 with the opt-in switch `ssl.labeled_aug=supervised` (commit `24590fb`). The switch:
- feeds labelled images through exactly the supervised arm's `get_labelsafe_augmentation`;
- leaves the unlabelled two-view pipeline unchanged;
- has unit tests and a CPU smoke run.

Then, on a pipeline-matched base, P11 asks whether the unlabelled loss beats **plain supervised training**, not just a handicapped control.

## Fixed for all arms
P8's protocol verbatim, plus `ssl.labeled_aug=supervised`. That means:
- **Code:** commit `24590fb`. It equals `0367079` except for this opt-in switch and its tests. cv02 path: `/tmp/noob_el/el_p11` (data symlinked from `el_p7`).
- **Base:** L3, `model.name=smp_unetpp loss.supervised=ce_dice`, label-safe.
- **Labels:** revised masks; seed-0 split; 10% labels (47 images).
- **Training:** batch 8 + 8; λ ramp as P8; 20,000 steps; seeds 0–2; EMA teacher evaluated.
- **Hardware:** cv02 RTX A6000, at most 3 runs per GPU. `OMP_NUM_THREADS=4` to limit CPU contention on the shared machine; this affects speed only.

## Arms
| Arm | Unlabelled loss | Pool |
|---|---|---|
| A (reference, no new runs) | P6 L3 10%, supervised | – |
| Dm | `tolerant_pl`, λ_final = 0 | in-domain (431) |
| Cm | `tolerant_pl`, R = 2 px | in-domain (431) |
| Dmx | `tolerant_pl`, λ_final = 0 | external (11,938) |
| Cmx | `tolerant_pl`, R = 2 px | external (11,938) |

## Metrics
As P8:
- **Primary:** test crack IoU, inactive IoU, crack relaxed F1@2. All use argmax and revised labels.
- **Secondary:** AP with bin-0 share, val, relaxed precision@2.

## Decision rules
1. **Pipeline check (descriptive, not a gate):** Dm − A on the primaries, with the image bootstrap.
   - Dm ≈ A (|Δ| within the rule-1 threshold, and the bootstrap CI covering 0 for crack) means the labelled view explains P8's D < A.
   - Otherwise BatchNorm/batch composition remains a candidate.
2. **Cm helps** if Cm − Dm passes P8 rule 1 (> 0.01 and > 2·SE on any primary, no primary worse). **Cmx helps** uses the same rule against Dmx.
3. **SSL beats supervised:** Cm − A and Cmx − A under the same rule. This is the claim the thesis needs. It is only credited if rule 2 also holds for that arm.
4. **Width check:** crack relaxed precision@2 drop > 0.05 against the matching D arm is flagged.
5. **Gap closed:** (C − A) / (L3@100% − A), per primary metric.

## Required robustness reporting
- The image bootstrap and leave-top-3-out check on every rule-2/3 contrast.
- The P9 source split for the external-pool arms.

## Not claimed
- Separating BatchNorm mixing from the data-stream difference.
- Tuning of R, t_pos, λ or augmentation strength.
- Results beyond this split and dataset.
