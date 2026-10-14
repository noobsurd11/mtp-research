# P19 protocol: reproduce Hanifi et al. 2025 (IEA/AIE, LNCS), 29-class supervised segmentation

Locked 14 Oct 2026, before any P19 run. The user: "reproduce hanifi 2025, asap", then "wait, use the researchmcp connector to get the paper then, no presumptions" (14 Oct ~08:35 IST).

## Source
- Paper: Hanifi, Jafarnejad, Cormier, Frank. "Multi-class Semantic Segmentation of Photovoltaic Module Defects and Features: Towards Industrial Robotic Applications". IEA/AIE 2025, LNCS, doi 10.1007/978-981-96-8892-0_4. Research MCP found the record but no full text; the authors' copy is on ORBilu (`orbilu.uni.lu/bitstream/10993/65653/1/IEA25_paper.pdf`), saved locally as `papers/hanifi2025_ieaaie_multiclass_seg.pdf` (untracked).
- Code: `github.com/sntubix/pv-defect-segmentation` at `506aa0b` (a fork of keras_segmentation; Keras 3.8, TF 2.18, Python 3.10).

## What the paper and code fix
- Data: BenchmarkEL/SCDD `20221008`, 29 classes (13 feature, 16 defect, by the release CSV's `Class` column).
- Six models: {VGG16, MobileNet, ResNet50} × {U-Net, SegNet}, ImageNet encoders (keras_segmentation constructors).
- Loss: weighted categorical CE with the Table 1 weights (identical to `train_script.py`'s list).
- Adam, lr 0.001 (Keras default), batch 8, val batch 16, up to 65 epochs, steps/epoch = n_train // 8, val steps = n_val.
- Early stopping on val loss, patience 10, best weights restored. ModelCheckpoint on train accuracy (as the code).
- Input 416×608 (the code's config; the paper does not state it). Images read with `cv2.imread(..., 1)`, keras_segmentation preprocessing.
- Metric (their `evaluate`): per class, TP/FP/FN pooled over test images at the model's output resolution; IoU = TP/(TP+FP+FN+1e-12).
  - Mean IoU features = mean over 12 feature classes, clamp (8) left out (checked: Fig. 3 values give 0.663 for VGG16-UNet as in Table 3).
  - Mean IoU defects = mean over 16 defect classes (checked: 0.326).
  - Mean over 29 (code's `mean_IU`) and frequency-weighted IoU also reported. The paper's "29 classes" value (0.494) cannot be recomputed from its Fig. 3 (0.471 or 0.455); noted, not resolved.

## What is not available, and the user's choices (14 Oct)
| Gap | Paper | Choice |
|---|---|---|
| Split | 551 / 67 / 77, re-split "after a pixel-count analysis"; not released | **Release split 553 / 70 / 72** (the `20221008` folders, whose names `train_script.py` uses) |
| Augmentation | "2,204 augmented frames" (= 551 × 4), method not described | **Code as released: no augmentation** |
| Seeds | one run per model, none stated | **6 models × seed 0, plus VGG16-UNet seeds 1–2** (8 runs) |

Seeds set with `tf.keras.utils.set_random_seed(seed)` (the code sets none). GPU nondeterminism remains.

## Runs
cv02 (RTX A6000), one run per GPU, tmux `p19`, venv `/tmp/noob_el/hanifi/venv`, driver `scripts_cv02/hanifi_run.py` (= `train_script.py` without wandb logging and without prediction images; same model, loss, optimizer, callbacks, generator and evaluate call). wandb disabled; `KERAS_HOME` under `/tmp/noob_el/hanifi`.

## Smoke checks before lock (1 epoch; VGG16-UNet, MobileNet-SegNet, ResNet50-UNet; deleted after)
- ImageNet weights load: every encoder layer equals the weight file (10/10, 46/46, 86/86). cv02 could not download them (GitHub reset), so the files were fetched on the laptop and copied (MD5 equal).
- Trainable parameters equal Table 2 exactly: VGG16-UNet 12,336,605; MobileNet-SegNet 5,540,317; ResNet50-UNet 16,356,509.
- Our per-class TP/FP/FN path reproduces their `evaluate()` IoU (asserted in the driver).
- About 66 s per epoch (MobileNet-SegNet, A6000).

## Comparison (descriptive; no rule)
- Our numbers vs Table 3 and Fig. 3, per model: mean IoU features, defects, 29, FW IoU; per-class IoU (crack, inactive, gridline first).
- Checks: trainable parameter counts vs Table 2; epochs run vs Table 2.
- A reproduction "agrees" if our VGG16-UNet seed spread covers the paper's value; given the different split and no augmentation, differences are reported, not explained away.
- Our test set (72 cells) differs from theirs (77). Classes absent from our test get IoU 0 in their metric; listed.

## Not claimed
- An exact reproduction (split and augmentation unavailable).
- Any comparison with our P-series numbers (different split, labels, classes and metric).
