# P4 protocol: frozen-feature linear probe (locked before running, 10 Oct 2026)

**Question:** do frozen pretrained features carry crack and inactive information better than random features?
This decides whether the MIM-pretraining and foundation-teacher directions (`to_human/directions_2026-10-10.md`, rows 3 and 6) are worth 1–2 GPU-days.

## Encoders (all frozen, eval mode)
1. ResNet-50 with random initialisation (torch seed 0).
2. ImageNet ResNet-50 (torchvision `IMAGENET1K_V2`).
3. ImageNet ConvNeXt-Tiny (torchvision `IMAGENET1K_V1`).
4. DINOv2 ViT-S/14 (torch.hub `facebookresearch/dinov2`, `dinov2_vits14`).
5. Reference only, outside the decision rules: our supervised U-Net++ encoder from `experiments/sl_100pct_b8_s0` (`encode()` e2 + e3, final step). It was trained with labels on all 478 train images.

DINOv3 is skipped: its weights are gated behind a licence the user must accept.

## Features
- **CNNs:** the stride-4 and stride-8 stages.
  - ResNet: layer1 + layer2.
  - ConvNeXt: stages 0 + 1.
  - U-Net++: e2 + e3.
- **ViT-S/14:** patch tokens at a 518 px input (37 × 37).
- **Inputs:** the 512 px grayscale image replicated to 3 channels with ImageNet normalisation. The U-Net++ gets its own 1-channel normalisation (mean 0.5, sd 0.25).
- **Standardisation:** each channel is standardised with the mean and sd over the training images' cached features.

## Probe
- **Head:** a linear 1×1 conv per stage, logits upsampled bilinearly to 512 and summed, plus a bias. This is the same as a 1×1 conv on the upsampled concatenated features, because upsampling is linear.
- **Classes:** 24, trained with plain CE.
- **Training images:** BenchmarkEL seed-0 `labeled_10pct` (47 images) with their old (`20211104`) masks.
- **Optimisation:** Adam 1e-3, 2,000 steps, batch 8 sampled with replacement, no augmentation.
- **Seeds:** two probe-training seeds (0, 1); results are reported as their mean.

## Evaluation
- **Images:** official val (54) and test (50), each scored separately and pooled (104).
- **Classes:** crack (14) and inactive (11).
- **Metrics:** dataset-level pixel AP (1,000-bin, as `src/evaluation/threshold_free.py`); argmax IoU; relaxed F1 at 2 px.
- **Labels:** each against both the old masks and the revised E-SCDD masks (`data/escdd_masks/`).
- **Reference:** the SL-10% b8 s0 full model reaches crack AP 0.492 / 0.527 on test (old / revised) and 0.348 / 0.427 on val.

## Decision rules
The decision metric is AP on the pooled val+test set with revised labels, mean of the 2 probe seeds.
1. **Pretrained features carry the signal.** If the best pretrained encoder (2–4) reaches at least the random-init AP + 0.10 on crack or inactive, rows 3 and 6 stay.
2. **ViT patches and crack.** If DINOv2's crack AP is below ImageNet ResNet-50's, drop ViT-patch features for crack and keep them for region classes only.
3. **Downgrade.** If no pretrained encoder beats random by at least 0.05 AP on either class, downgrade rows 3 and 6.

Anything outside these rules is reported as EXPLORATORY.
