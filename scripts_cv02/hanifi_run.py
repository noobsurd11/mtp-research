"""P19: Hanifi et al. 2025 (IEA/AIE) reproduction driver.

Mirrors pv-defect-segmentation@506aa0b keras_segmentation/train_script.py: same model constructors (416x608, 29 classes),
weighted CE with the Table 1 weights, Adam (Keras default lr 0.001), batch 8 / val batch 16, 65 epochs max,
steps/epoch = n_train // 8, val steps = n_val, ModelCheckpoint(monitor="accuracy"), EarlyStopping(val_loss, patience 10,
restore best), then their evaluate() on test. Dropped: wandb logging (disabled), prediction images, confusion-matrix plot.
Added: a seed, a JSON with their metrics plus per-class TP/FP/FN (same predict + get_segmentation_array path) on val and test.
Usage: python hanifi_run.py --arch vgg_unet --seed 0 --repo <pv-defect-segmentation> --data <dir with dataset_20221008> --out <dir>
"""
import argparse, json, os, sys, time

ap = argparse.ArgumentParser()
ap.add_argument("--arch", required=True, choices=["vgg_unet", "mobilenet_unet", "resnet50_unet",
                                                  "vgg_segnet", "mobilenet_segnet", "resnet50_segnet"])
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--repo", required=True)
ap.add_argument("--data", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--epochs", type=int, default=65)
a = ap.parse_args()
sys.path.insert(0, a.repo)
os.environ.setdefault("WANDB_MODE", "disabled")

import numpy as np
import pandas as pd
import tensorflow as tf
import wandb
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras_segmentation.models.unet import vgg_unet, mobilenet_unet, resnet50_unet
from keras_segmentation.models.segnet import vgg_segnet, mobilenet_segnet, resnet50_segnet
from keras_segmentation.predict import predict
from keras_segmentation.data_utils.data_loader import get_pairs_from_paths, get_segmentation_array

for d in tf.config.experimental.list_physical_devices("GPU"):
    tf.config.experimental.set_memory_growth(d, True)
tf.keras.utils.set_random_seed(a.seed)
wandb.init(mode="disabled")  # their evaluate() calls wandb.log

D = os.path.join(a.data, "dataset_20221008")
tr_i, tr_a = os.path.join(D, "el_images_train"), os.path.join(D, "el_masks_train")
va_i, va_a = os.path.join(D, "el_images_val"), os.path.join(D, "el_masks_val")
te_i, te_a = os.path.join(D, "el_images_test"), os.path.join(D, "el_masks_test")
df = pd.read_csv(os.path.join(D, "ListOfClassesAndColorCodes_20221008.csv"))
names, groups = df["Desc"].str.strip().tolist(), df["Class"].tolist()

class_weights = [0.8, 3.0, 3.0, 6.0, 5.0, 2.0, 4.0, 0.7, 4.0, 6.0, 10.0, 5.0, 9.0, 4.0, 7.0, 5.0, 7.0, 7.0, 6.0, 6.0,
                 3.0, 2.0, 8.0, 9.0, 8.0, 6.0, 5.0, 5.0, 7.0]  # train_script.py, = paper Table 1
H, W, NC, BS, VBS = 416, 608, 29, 8, 16
ctor = dict(vgg_unet=vgg_unet, mobilenet_unet=mobilenet_unet, resnet50_unet=resnet50_unet,
            vgg_segnet=vgg_segnet, mobilenet_segnet=mobilenet_segnet, resnet50_segnet=resnet50_segnet)[a.arch]
model = ctor(n_classes=NC, input_height=H, input_width=W)

# Check the ImageNet weights really loaded (their load_weights uses skip_mismatch=True, which would skip silently).
import glob, h5py
wf = [f for f in glob.glob(os.path.join(os.environ.get("KERAS_HOME", os.path.expanduser("~/.keras")), "datasets", "*.h5"))
      if f.split("/")[-1].split("_")[0] == {"vgg": "vgg16", "mobilenet": "mobilenet", "resnet50": "resnet50"}[a.arch.split("_")[0]]]
with h5py.File(wf[0], "r") as f:
    g = f["model_weights"] if "model_weights" in f else f
    match = tot = 0
    for L in model.layers:
        if L.weights and L.name in g:
            arrs = [np.asarray(g[L.name][n]) for n in g[L.name].attrs["weight_names"]]
            tot += 1
            match += int(len(arrs) == len(L.get_weights()) and all(np.array_equal(x, y) for x, y in zip(arrs, L.get_weights())))
print(f"pretrained check ({os.path.basename(wf[0])}): {match}/{tot} encoder layers equal the ImageNet file", flush=True)
assert tot > 0 and match == tot, "ImageNet weights not loaded"

os.makedirs(a.out, exist_ok=True)
ck = os.path.join(a.out, "checkpoint/")
os.makedirs(ck, exist_ok=True)
info = dict(arch=a.arch, seed=a.seed, input=[H, W], n_classes=NC, batch=BS, val_batch=VBS, max_epochs=a.epochs,
            n_train=len(os.listdir(tr_i)), n_val=len(os.listdir(va_i)), n_test=len(os.listdir(te_i)),
            total_params=int(model.count_params()),
            trainable_params=int(np.sum([tf.keras.backend.count_params(w) for w in model.trainable_weights])))
print(json.dumps(info), flush=True)


class EpochLog(tf.keras.callbacks.Callback):
    def __init__(self):
        super().__init__(); self.rows = []; self.t0 = time.time()

    def on_epoch_end(self, epoch, logs=None):
        r = {"epoch": epoch + 1, "sec": round(time.time() - self.t0, 1), **{k: float(v) for k, v in (logs or {}).items()}}
        self.rows.append(r); print(json.dumps(r), flush=True)
        json.dump(self.rows, open(os.path.join(a.out, "history.json"), "w"), indent=1)


hist = EpochLog()
es = EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True)
callbacks = [hist, ModelCheckpoint(filepath=os.path.join(ck, "best_model.keras"), monitor="accuracy", save_best_only=True,
                                   save_weights_only=False, save_freq="epoch", verbose=1), es]
t0 = time.time()
model.train(train_images=tr_i, train_annotations=tr_a, val_images=va_i, val_annotations=va_a, validate=True,
            checkpoints_path=ck, epochs=a.epochs, batch_size=BS, val_batch_size=VBS,
            steps_per_epoch=len(os.listdir(tr_i)) // BS, val_steps_per_epoch=len(os.listdir(va_i)),
            callbacks=callbacks, class_weights=class_weights)
info["train_sec"] = round(time.time() - t0, 1)
info["epochs_run"] = len(hist.rows)
info["best_epoch_val_loss"] = int(es.best_epoch + 1) if hasattr(es, "best_epoch") else None
model.save_weights(os.path.join(ck, "final_restored.weights.h5"))

res = {"info": info}
for split, ii, aa in (("val", va_i, va_a), ("test", te_i, te_a)):
    ev = model.evaluate_segmentation(inp_images_dir=ii, annotations_dir=aa)  # their metric, unchanged
    tp, fp, fn, npx = (np.zeros(NC) for _ in range(4))
    per_img = {}
    for p in get_pairs_from_paths(ii, aa):
        im, an = p[0], p[1]
        pr = predict(model, im).flatten()
        gt = get_segmentation_array(an, NC, model.output_width, model.output_height, no_reshape=True).argmax(-1).flatten()
        c = {}
        for k in range(NC):
            t, f, n = int(np.sum((pr == k) & (gt == k))), int(np.sum((pr == k) & (gt != k))), int(np.sum((pr != k) & (gt == k)))
            tp[k] += t; fp[k] += f; fn[k] += n; npx[k] += t + n
            if t + f + n:
                c[k] = [t, f, n]
        per_img[os.path.basename(im)] = c
    iou = tp / (tp + fp + fn + 1e-12)
    assert np.allclose(iou, ev["class_wise_IU"]), "count path disagrees with their evaluate()"
    feat = [k for k in range(NC) if groups[k] == "feature" and k != 8]  # clamp (8) left out, as the paper
    dfc = [k for k in range(NC) if groups[k] == "defect"]
    res[split] = {"class_iou": {names[k]: float(iou[k]) for k in range(NC)},
                  "mean_iou_features_12": float(iou[feat].mean()), "mean_iou_defects_16": float(iou[dfc].mean()),
                  "mean_iou_29": float(ev["mean_IU"]), "fw_iou": float(ev["frequency_weighted_IU"]),
                  "class_median_iou": {names[int(k)]: float(v) for k, v in ev["class_wise_median_IU"].items()},
                  "gt_px": {names[k]: int(npx[k]) for k in range(NC)},
                  "tp": tp.astype(int).tolist(), "fp": fp.astype(int).tolist(), "fn": fn.astype(int).tolist(),
                  "per_image_counts": per_img}
    print(split, json.dumps({k: res[split][k] for k in ("mean_iou_features_12", "mean_iou_defects_16", "mean_iou_29", "fw_iou")}), flush=True)
json.dump(res, open(os.path.join(a.out, "result.json"), "w"))
print("DONE", a.arch, a.seed, flush=True)
