# P15 protocol: is related labelled EL data (UCF-EL) worth more as encoder pretraining? (E3; directions rows 3 and 5)

Locked 11 Oct 2026, ~13:45 IST, before any P15 fine-tuning run.

**Context:** the user asked for results within one day and left the GPU allocation to me.

**What I had seen:**
- P1–P13 as reported.
- The pretraining run below had started (12:50 IST) but had not finished. Its UCF score is not used for any decision.

## Question
P4 showed that pretrained features carry most of the crack/inactive signal:
- ImageNet ResNet-50 vs random: +0.30 crack AP;
- ImageNet ResNet-50 vs our own trained encoder: +0.08.

Does an encoder further trained on UCF-EL's 9,562 labelled EL cells beat the ImageNet encoder when fine-tuned on BenchmarkEL with few labels?

## Pretraining (one run, cv02)
- **Run:** `p15_ucf_pre_dlv3p_r34`, el_p13 `bac5264`.
- **Recipe:** `configs/ucf_deeplab.yaml`, i.e. the reproduced Fioresi recipe:
  - SGD 5e-3 poly, batch 16, 256 crop of the 295-px shorter side, CE with ignore 128;
  - 59,760 steps = 100 epochs; seed 0.
- **Encoder:** `model.encoder_name=resnet34` (ImageNet init).
- **Data:** `data.labeled_subset=full` (all 9,562 UCF train cells).
- **Why DeepLabV3+:** it evaluates at UCF's variable image sizes; UNet++ cannot. Its ResNet-34 encoder has the same 216 tensors as our UNet++ encoder (checked).

**Leakage check:**
- Method: `results/p15/dedup.py`; 64×64 grayscale, 8 flips and rotations, normalised correlation.
- Result: UCF train vs BenchmarkEL val + test. Maximum 0.79; none ≥ 0.90.

## Transfer
`model.encoder_init=<pretrained final model>` (commit `be67787`):
- copies all 216 encoder tensors;
- sums the first conv over its 3 input channels for our 1-channel model, as smp does for ImageNet;
- leaves the decoder freshly initialised.

## Arms (gaint, split seed 0, seeds 0–2; P6 L3 options verbatim plus `encoder_init`)
| Arm | Run names | Labels | Reference (gaint, same seeds and options, ImageNet encoder) |
|---|---|---|---|
| U5 | `p15_gU_5pct` | 5% (23) | P10 `p10_A_5pct` |
| U10 | `p15_gU_10pct` | 10% (47) | P12 `p12_gA_10pct` |

**Scheduling:**
- gaint worktree `el_p14` at `be67787`.
- Lane A (U5) starts when P12 gaint lane 2 is done; lane B (U10) when lane 1 is done.
- Each lane runs one job at a time.

## Metrics and rules
Primary, revised labels, test: crack IoU, inactive IoU, crack relF1@2.
1. **U helps:** U − reference under P8 rule 1 (any primary passes, none worse), plus the width check (relP@2 drop ≤ 0.05).
2. **Robustness:** image bootstrap and leave-top-3-out.
3. **Descriptive:**
   - gap closed against L3@100% (P6, cv02; cross-machine, descriptive only);
   - U5 vs supervised 10% on gaint (P12 gA10): does UCF pretraining stand in for doubling the labels?

## Not claimed
- MIM or self-supervised pretraining.
- Other UCF recipes.
- Freezing schedules.
- Tuning the pretraining length.
- Pooling with cv02 runs.
