# P12 protocol: pipeline-matched SSL at 5% labels (cv02), a cv02 supervised 5% reference, and a gaint replication

Locked 11 Oct 2026, ~02:00 IST, before any P12 run. This is part of the overnight SSL work the user approved on 10 Oct ("night long works ... use all resources ... cv02, gaint all of them").

What I had seen when locking:
- No P9, P10 (cv02) or P11 result. All of those runs were still training.
- P10's gaint supervised reference A5: test crack IoU 0.298±0.005, inactive IoU 0.277±0.055, crack relF1@2 0.708±0.012. This is disclosed. It motivates the 5% setting (large label headroom against P6 A10 at 0.396 crack IoU). It applies equally to every P12 arm.

## Why this exists
- **P10's pipeline is handicapped.** P10 tests SSL at 5% labels, but on the P8-style Mean Teacher pipeline. Its labelled images get the SSL "strong" view. At 10% labels that pipeline with the loss off (D) was below plain supervised training: crack IoU −0.013, inactive IoU −0.10 (P8).
- **P12 crosses P10 and P11.** P11 removes that handicap at 10% (`ssl.labeled_aug=supervised`). P12 applies the same matched pipeline at 5%, where the label gap is largest.
- **P10's A5 can't enter a rule.** It ran on gaint (different hardware), so it cannot be compared with cv02 arms. P12 adds a supervised A5 on cv02, so "SSL beats supervised at 5%" can be tested on matched hardware.
- **gaint replication.** gaint is idle after its P10 references (~04:00). It runs fresh seeds of the key in-domain contrast. Those runs are hardware-matched to gaint's own A5.

## Fixed for all SSL arms
P11's protocol verbatim, except `data.labeled_fraction=0.05`:
- **Labels:** the committed `seed0/labeled_5pct.txt`, 23 cells. The in-domain pool is the other 455 training cells.
- **Code:** commit `24590fb`, `ssl.labeled_aug=supervised`.
- **Base:** L3 (`model.name=smp_unetpp loss.supervised=ce_dice`), label-safe.
- **Data:** revised masks; split seed 0.
- **Training:** batch 8 + 8; λ 0 for 2,000 steps, then a ramp over 2,000 to its final value; 20,000 steps; EMA teacher evaluated; `OMP_NUM_THREADS=4`.

Supervised runs use P6's L3 options verbatim (`configs/supervised.yaml`, label-safe, `ce_dice`, `smp_unetpp`, batch 8, 20,000 steps). The supervised code path is unchanged between P6's commit `824fab0` and `24590fb`. A diff shows additions only: SSL augmentations, the `tolerant_pl` loss and the opt-in labelled-view switch.

## Arms
| Arm | Run names | Unlabelled loss | Pool | Seeds | Hardware |
|---|---|---|---|---|---|
| A5c | `p12_A_5pct` | none (supervised) | – | 0–2 | cv02 |
| Dm5 | `p12_Dm_5pct` | `tolerant_pl`, λ_final = 0 | in-domain (455) | 0–2 | cv02 |
| Cm5 | `p12_Cm_5pct` | `tolerant_pl`, R = 2 px | in-domain (455) | 0–2 | cv02 |
| Dmx5 | `p12_Dmx_5pct` | `tolerant_pl`, λ_final = 0 | external (11,938) | 0–2 | cv02 |
| Cmx5 | `p12_Cmx_5pct` | `tolerant_pl`, R = 2 px | external (11,938) | 0–2 | cv02 |
| gDm5 | `p12_gDm_5pct` | `tolerant_pl`, λ_final = 0 | in-domain (455) | 3–5 | gaint |
| gCm5 | `p12_gCm_5pct` | `tolerant_pl`, R = 2 px | in-domain (455) | 3–5 | gaint |
| gA10 | `p12_gA_10pct` | none (supervised, 10%) | – | 0–2 | gaint |

The gaint SSL arms use fresh seeds 3–5. They are never pooled with the cv02 seeds.

**Scheduling**
- **cv02:**
  - Runs start only after the P11 queue has launched all its runs, plus 5 minutes so GPU memory registers. This avoids the earlier queue race.
  - At most 3 runs per GPU, and only on a GPU with < 1000 MiB used, so never on another user's GPU.
  - A5c is queued after the SSL arms.
- **gaint:**
  - Two sequential lanes. They start after all six P10 gaint references are rescored.
  - Each run waits until the GPU has < 20,000 MiB used.
  - Lane 1: gDm5 s3, s4, s5, then gA10 s0, s2. Lane 2: gCm5 s3, s4, s5, then gA10 s1.
- Training is deterministic per machine, so co-location affects speed only.

## Metrics
As P8/P11:
- **Primary:** test crack IoU, inactive IoU, crack relaxed F1@2. All use argmax and revised labels.
- **Secondary:** AP with bin-0 share, val, relaxed precision@2.

## Decision rules (all on cv02 unless stated)
1. **Pipeline check at 5% (descriptive):** Dm5 − A5c and Dm5 − D5 (P10), with the image bootstrap.
2. **Cm5 helps** if Cm5 − Dm5 passes P8 rule 1 (> 0.01 and > 2·√((sd²+sd²)/3) on any primary, no primary worse). **Cmx5 helps** uses the same rule against Dmx5.
3. **SSL beats supervised at 5%:** Cm5 − A5c and Cmx5 − A5c under the same rule. Credited only if rule 2 also holds for that arm.
4. **Width check:** crack relaxed precision@2 drop > 0.05 against the matching Dm arm is flagged.
5. **Gap closed:** (C − A5c) / (L3@100% − A5c), per primary metric, with P6's L3@100%.
6. **gaint replication (descriptive):** gCm5 − gDm5, and gCm5 − A5 (P10's gaint reference, same hardware), reported with the same arithmetic.
   - A cv02 claim from rule 2 or 3 is called **replicated** if the gaint contrast has the same sign, and at least half the size, on each metric that passed.
   - The gaint runs never rescue a cv02 rule that failed.
7. **Calibration (descriptive):** gA10 − P6 L3 10% (cv02) on the primaries. This says how far gaint's references (P10 A5/A50, gaint A5 in rule 6) can be read next to cv02 numbers.

## Required robustness reporting
- The image bootstrap and leave-top-3-out check on every rule-2/3 contrast.
- The P9 source split for the external-pool arms.
- The inactive count among the 23 labelled cells (shared with P10).

## Not claimed
- Pooling cv02 and gaint seeds.
- Separating BatchNorm mixing from data streams.
- Tuning of R, t_pos, λ or augmentation.
- Results beyond this split and dataset.
