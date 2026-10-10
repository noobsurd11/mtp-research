# P4 result: frozen-feature linear probe (protocol `protocols/P4_frozen_feature_probe.md`, locked in commit 855b130)

Run: 10 Oct 2026, gaint, `scripts_gaint/p4_feature_probe.py`, about 5 min in total. Raw data: `p4_feature_probe.json` and `.log`.
Setup: linear 24-class probe on 47 images (`labeled_10pct`, seed 0), old labels. Scores are pixel AP, mean of 2 probe seeds (seed spread ≤ 0.011).

| Encoder (frozen) | Crack AP, pooled, revised | Inactive AP, pooled, revised | Crack AP test old/rev | Crack AP val old/rev | Crack relaxed P@2 / R@2 |
|---|---|---|---|---|---|
| ResNet-50, random init | 0.029 | 0.097 | 0.039 / 0.045 | 0.010 / 0.014 | 0.28 / 0.02 |
| ResNet-50, ImageNet | 0.321 | **0.423** | 0.324 / 0.353 | 0.223 / 0.258 | 0.78 / 0.35 |
| ConvNeXt-T, ImageNet | **0.331** | 0.383 | 0.328 / 0.371 | 0.226 / 0.251 | 0.87 / 0.26 |
| DINOv2 ViT-S/14 | 0.183 | 0.384 | 0.175 / 0.197 | 0.122 / 0.155 | 0.50 / 0.13 |
| *ref.* our U-Net++ encoder, SL-100 (e2 + e3) | 0.244 | 0.266 | 0.246 / 0.281 | 0.137 / 0.175 | 0.80 / 0.27 |
| *ref.* full SL-10% model (not a probe) | – | – | 0.492 / 0.527 | 0.348 / 0.427 | – |

## Verdict against the locked rules (CONFIRMATORY)
1. **Rule 1 fires.** The best pretrained encoder beats random by +0.30 on crack AP and +0.33 on inactive AP, far above the +0.10 bar. Pretrained features carry the signal, so rows 3 and 6 (MIM pretraining, foundation teacher) stay.
2. **Rule 2 fires.** DINOv2 crack AP (0.183) is below ImageNet ResNet-50 (0.321). ViT-patch features are dropped for crack. For inactive, DINOv2 (0.384) is on par with the CNNs, so it is kept for region classes only.
3. **Rule 3 does not fire.**

## EXPLORATORY
- **Random baseline:** the random-init probe is close to degenerate (BN statistics at init), so it may understate a randomly initialised network trained end to end. Rule 1's margin is far too large for that to matter.
- **Crack:** convolutional stride-4/8 ImageNet features linearly separate crack better than our own supervised encoder's e2/e3, with high relaxed precision (0.78–0.87) and low recall.
- **Inactive:** ImageNet ResNet-50 features alone reach inactive AP 0.42.
- **Implications:** an ImageNet- or MIM-initialised CNN encoder for the deployable student, plus a CNN (not ViT) teacher for thin cracks.
