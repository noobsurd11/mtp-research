# Hanifi et al. 2025 (IEA/AIE, LNCS): 29-class EL segmentation with U-Net/SegNet
- **Citation.** Hanifi, Jafarnejad, Cormier, Frank. "Multi-class Semantic Segmentation of Photovoltaic Module Defects and Features: Towards Industrial Robotic Applications". IEA/AIE 2025, LNCS. doi 10.1007/978-981-96-8892-0_4.
- **Affiliations:** University of Luxembourg (SnT), SolarCleano. Same group as E-SCDD / PV-DDPM (note A09).
- **Read:** full text, 14 Oct 2026. The Research MCP had the record but no full text; the authors' copy is on ORBilu (`orbilu.uni.lu/handle/10993/65653`). Local: `papers/hanifi2025_ieaaie_multiclass_seg.pdf` (untracked).
- **Code:** `github.com/sntubix/pv-defect-segmentation` @ `506aa0b`, a keras_segmentation fork (TF 2.18, Keras 3.8).
- **Reproduced:** P19, `results/p19/README.md`.

## What it does
- Six models: {VGG16, MobileNet, ResNet50} × {U-Net, SegNet}, ImageNet encoders, 29 classes of BenchmarkEL/SCDD `20221008` (13 feature, 16 defect).
- **Data:** the 695 images re-split "after a comprehensive pixel-count analysis" into 551 / 67 / 77. Training uses "2,204 augmented frames" (551 × 4); the augmentation is not described. Neither split nor augmentation is in the repo.
- **Training:** weighted CE with hand-set class weights (Table 1, from class imbalance, detection difficulty and defect importance), Adam lr 0.001, batch 8, early stopping on val loss (patience 10). Input 416×608 in the code (not stated in the paper). RTX 4090, 16–37 min per model.
- **Metric:** per class, IoU pooled over the test images at the model's output resolution (208×304). The feature mean leaves out clamp (12 classes), the defect mean covers 16. Also frequency-weighted IoU.

## Results claimed (Table 3; one run per model)
| | ResNet50-UNet | MobileNet-UNet | VGG16-UNet | ResNet50-SegNet | MobileNet-SegNet | VGG16-SegNet |
|---|---|---|---|---|---|---|
| features | 0.681 | 0.642 | 0.663 | 0.648 | 0.567 | 0.642 |
| defects | 0.295 | 0.261 | 0.326 | 0.294 | 0.254 | 0.288 |
| 29 classes | 0.488 | 0.451 | 0.494 | 0.471 | 0.410 | 0.465 |
| FW IoU | 0.871 | 0.871 | 0.879 | 0.885 | 0.871 | 0.879 |

VGG16-UNet per class (Fig. 3): crack 0.335, inactive 0.550, gridline 0.297, dead cell 0.502 ("+0.129" over VGG16-SegNet, the abstract's rare-defect claim).

## Weaknesses
**Empirical (checked in P19):**
- The "29 classes" mean cannot be recomputed from Fig. 3 for any model (VGG16-UNet: 0.494 claimed; 0.471 over 28, 0.455 over 29).
- One run per model. The headline margin (VGG16-UNet over ResNet50-UNet, 0.031 on defects) is under 2 seed sd in our reproduction.
- The split and augmentation that produce the numbers are not released.

**Reader-inferred:**
- Class weights were set by hand, partly from "our experiments", with no stated held-out procedure.
- Resizing 512×512 cells to 416×608 distorts the aspect ratio. Scoring at 208×304 hides thin-structure errors.
- An absent class scores IoU 0 in the group means, so the means depend on which rare classes land in the test split.

## Relevance to us
- **A public, runnable 29-class baseline on `20221008`.** On the release split it gives VGG16-UNet crack ≈ 0.35, inactive ≈ 0.47 (pooled, 208×304).
- **Not comparable with our P-series numbers** (split, label set, resolution, metric). A like-for-like comparison needs one model run under both setups.
