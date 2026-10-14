# P19: reproduction of Hanifi et al. 2025 (IEA/AIE, LNCS), 29-class supervised segmentation. Results

Protocol: `protocols/P19_hanifi2025_reproduction.md`, locked 14 Oct before any run (`8655bd6`; smoke excepted). The user: "reproduce hanifi 2025, asap", then "use the researchmcp connector to get the paper then, no presumptions"; the split, augmentation and scope were the user's choices (14 Oct).

**Source**
- Paper: Hanifi, Jafarnejad, Cormier, Frank, "Multi-class Semantic Segmentation of Photovoltaic Module Defects and Features: Towards Industrial Robotic Applications", IEA/AIE 2025, LNCS, doi 10.1007/978-981-96-8892-0_4.
  - Research MCP had the record but no full text; the authors' copy came from ORBilu (`papers/hanifi2025_ieaaie_multiclass_seg.pdf`, untracked).
- Code: `github.com/sntubix/pv-defect-segmentation` @ `506aa0b` (keras_segmentation fork), run unchanged through `scripts_cv02/hanifi_run.py`, which is `train_script.py` without wandb logging and prediction images.

**Runs**
- cv02 (RTX A6000), Python 3.10, TF 2.18, Keras 3.8 (the authors' versions), tmux `p19`, 14 Oct 08:58–09:31 IST. All 8 rc = 0.
- 6 models at seed 0, plus VGG16-UNet seeds 1–2.
- Setup:
  - data: BenchmarkEL `20221008` with the release split (553 / 70 / 72), no augmentation, input 416×608;
  - training: weighted CE with the Table 1 weights, Adam lr 0.001, batch 8, early stopping on val loss (patience 10, best weights restored);
  - scoring: their `evaluate()` on test.
- Checks:
  - the ImageNet weights loaded (every encoder layer equals the weight file);
  - trainable parameters equal the paper's Table 2 for all 6 models;
  - our per-class TP/FP/FN reproduce their `evaluate()` (asserted).

**Differences from the paper that cannot be removed** (the user's choices, protocol table):
- **Split:** theirs is a 551 / 67 / 77 re-split, not released.
- **Augmentation:** they trained on 2,204 frames (= 551 × 4) with an undescribed augmentation.
- **Test classes:** our 72-cell test set has no dead cell, belt mark, sp mono halfcut, crack rbn edge, meas artifact or clamp.
  - Their metric scores an absent class as IoU 0.
  - The paper's VGG16-UNet scored 0.502 on dead cell and 0.293 on belt mark.

**Files:** `raw/` (result JSONs with per-class and per-image TP/FP/FN on val and test, epoch histories, `launch.log`), `p19_compare.txt` (all tables), `fig_p19_classiou.png` (per-class IoU, ours vs paper). Reproduce with `.venv/bin/python scripts/p19_compare.py --out results/p19/fig_p19_classiou.png`.

## Results (test, release split; their metric: IoU pooled over test images at the 208×304 output)

### Headline model, VGG16-UNet (3 seeds) vs the paper (1 run)
| | ours | paper |
|---|---|---|
| mean IoU, 12 feature classes | 0.678 ± 0.020 | 0.663 |
| mean IoU, 16 defect classes | 0.246 ± 0.018 | 0.326 |
| mean IoU, 29 classes | 0.416 ± 0.015 | 0.494 |
| frequency-weighted IoU | 0.884 ± 0.011 | 0.879 |
| defect mean over the 12 defect classes in our test | 0.328 ± 0.024 | 0.369 (same 12, from Fig. 3) |
| feature mean over the 11 feature classes in our test | 0.740 ± 0.021 | 0.719 (same 11) |
| **crack** | **0.352 ± 0.008** | 0.335 |
| **inactive** | **0.469 ± 0.032** | 0.550 |
| **gridline** | **0.316 ± 0.028** | 0.297 |

Per seed, crack / inactive / gridline: s0 0.350 / 0.490 / 0.291; s1 0.345 / 0.432 / 0.310; s2 0.361 / 0.484 / 0.347.

### All six models (seed 0 except VGG16-UNet)
| Model | features (12) ours / paper | defects (16) ours / paper | defects, 12 present ours / paper | crack ours / paper | inactive ours / paper | epochs ours / paper |
|---|---|---|---|---|---|---|
| ResNet50-UNet | 0.676 / 0.681 | 0.230 / 0.295 | 0.307 / 0.384 | 0.363 / 0.374 | 0.318 / 0.578 | 34 / 27 |
| MobileNet-UNet | 0.666 / 0.642 | 0.265 / 0.261 | 0.353 / 0.340 | 0.323 / 0.249 | 0.491 / 0.504 | 22 / 21 |
| VGG16-UNet (3 seeds) | 0.678 / 0.663 | 0.246 / 0.326 | 0.328 / 0.369 | 0.352 / 0.335 | 0.469 / 0.550 | 51, 38, 41 / 30 |
| ResNet50-SegNet | 0.620 / 0.648 | 0.211 / 0.294 | 0.282 / 0.374 | 0.203 / 0.266 | 0.289 / 0.529 | 29 / 30 |
| MobileNet-SegNet | 0.607 / 0.567 | 0.221 / 0.254 | 0.295 / 0.332 | 0.184 / 0.224 | 0.437 / 0.532 | 32 / 23 |
| VGG16-SegNet | 0.549 / 0.642 | 0.176 / 0.288 | 0.234 / 0.349 | 0.201 / 0.319 | 0.383 / 0.592 | 45 / 42 |

Per-class tables for all 29 classes: `p19_compare.txt`.

### What reproduces and what does not
- **Reproduces:**
  - The feature means: ours are within about ±0.03 of the paper for the U-Nets.
  - Crack and gridline IoU for VGG16-UNet: ours are slightly higher (crack 0.352 ± 0.008 vs 0.335).
  - The frequency-weighted IoU (0.87–0.89).
  - U-Net above SegNet on defects for every encoder (ours, 12 present classes: 0.307 / 0.353 / 0.328 vs 0.282 / 0.295 / 0.234).
  - The trainable parameter counts, exactly.
- **Lower in ours:**
  - **The 16-class defect mean (0.246 vs 0.326).** Most of this gap is a test-set artefact: dead cell and belt mark are absent from our test, so they score 0 here, against 0.502 and 0.293 in the paper. Over the 12 defect classes present in both, the gap is 0.328 vs 0.369. Half of that comes from **rings** (ours 0.017, paper 0.285; 1,626 GT px in our test).
  - **Inactive** (0.469 ± 0.032 vs 0.550). Our test has 9 inactive cells.
- **Not reproduced:**
  - **The paper's model ranking.** In ours, MobileNet-UNet (0.353) is level with VGG16-UNet (0.328 ± 0.024) on present-class defects. The paper's headline margin (VGG16-UNet over the next model, 0.031 on the 16-class defect mean) is under 2 seed sd here (VGG16-UNet sd 0.018), so its ranking (VGG16-UNet best) is not established by one run per model.
  - **The paper's "29 classes" mean** (0.494 for VGG16-UNet) cannot be recomputed from its own Fig. 3 (0.471 with 28 classes, 0.455 with 29), for any of the 6 models. Ours is reported as their code computes it (mean over all 29, absent = 0).
- **Training length:** ours runs longer than the paper's Table 2 for most models (e.g. VGG16-UNet 38–51 vs 30 epochs). This is expected: without the 4× offline augmentation each of our epochs has a quarter of their steps.

### Validation (70 cells), VGG16-UNet
Features / defects / 29: 0.638 / 0.250 / 0.402 (s0), 0.629 / 0.229 / 0.387 (s1), 0.624 / 0.251 / 0.397 (s2).

## Reading
- With the released code, the release split and no augmentation, VGG16-UNet matches the paper on features and on crack and gridline. It is lower on inactive. The group means are lower mainly because our test set lacks two defect classes that the paper's test set had. The model ranking does not hold beyond seed noise.
- **For our thesis:** this gives a reproduced, public 29-class baseline on `20221008`: crack about 0.35 IoU, pooled at 208×304, on the release test split.
  - **It is not comparable with our P-series numbers:** they use a different split (our 50 test cells), a 3-class-relevant label set (`masks_escdd` on 582 cells), full-resolution scoring, and a different recipe.
  - **A like-for-like comparison would need either:**
    - Hanifi's VGG16-UNet trained on our split and scored with our metric; or
    - our L3 model trained on the release split.
  - Neither was run.

## Not claimed
- An exact reproduction (the split and augmentation are unavailable).
- Any comparison with our P-series numbers.
- An architecture ranking: one seed per model except VGG16-UNet.
