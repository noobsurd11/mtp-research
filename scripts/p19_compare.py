"""P19: compare our Hanifi 2025 reproduction runs with the paper (Table 2, Table 3, Fig. 3).

Paper values are transcribed from the authors' PDF (ORBilu IEA25_paper.pdf): Fig. 3 heatmaps read at 300 dpi, Tables 2-3 as printed.
Our runs: results/p19/raw/<arch>_s<seed>.json (from scripts_cv02/hanifi_run.py), release split 553/70/72, test set.
Usage: .venv/bin/python scripts/p19_compare.py --out results/p19/fig_p19_classiou.png | tee results/p19/p19_compare.txt
"""
import argparse, glob, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("--raw", default="results/p19/raw")
ap.add_argument("--out", required=True)
a = ap.parse_args()

M = ["resnet50_unet", "mobilenet_unet", "vgg_unet", "resnet50_segnet", "mobilenet_segnet", "vgg_segnet"]  # paper column order
LBL = dict(resnet50_unet="ResNet50-UNet", mobilenet_unet="MobileNet-UNet", vgg_unet="VGG16-UNet",
           resnet50_segnet="ResNet50-SegNet", mobilenet_segnet="MobileNet-SegNet", vgg_segnet="VGG16-SegNet")
FIG3 = {  # class: IoU per model in M order (paper Fig. 3)
    "crack rbn edge": [0, 0, 0, 0, 0, 0], "inactive": [.578, .504, .550, .529, .532, .592],
    "rings": [.047, .001, .285, .273, .000, .020], "material": [.386, .388, .316, .422, .389, .353],
    "crack": [.374, .249, .335, .266, .224, .319], "gridline": [.344, .301, .297, .320, .239, .295],
    "splice": [.178, .099, .159, .134, .139, .104], "dead cell": [.088, .000, .502, .112, .056, .373],
    "corrosion rbn": [.601, .632, .563, .604, .527, .609], "belt mark": [.036, .099, .293, .105, .028, .057],
    "edge dark": [.363, .357, .347, .360, .415, .458], "meas artifact": [0, 0, 0, 0, 0, 0],
    "scuff": [.623, .441, .532, .503, .525, .508], "corrosion cell": [.614, .580, .534, .558, .542, .580],
    "brightening": [.468, .512, .428, .424, .286, .343], "star": [.027, .019, .083, .099, .167, .004],
    "bckgnd": [.903, .903, .895, .911, .898, .893], "sp multi": [.783, .759, .751, .750, .737, .743],
    "sp mono": [.704, .688, .695, .710, .695, .692], "sp dogbone": [.545, .532, .555, .545, .517, .547],
    "ribbons": [.570, .611, .571, .619, .599, .577], "border": [.753, .760, .734, .752, .716, .769],
    "text": [.603, .419, .617, .335, .278, .594], "padding": [.994, .993, .993, .992, .985, .994],
    "busbars": [.470, .577, .579, .584, .395, .566], "frame edge": [.748, .758, .675, .698, .760, .719],
    "jbox": [.918, .658, .839, .748, .136, .556], "sp mono halfcut": [.186, .058, .057, .136, .088, .065]}
T3 = {"features": [.681, .642, .663, .648, .567, .642], "defects": [.295, .261, .326, .294, .254, .288],
      "29": [.488, .451, .494, .471, .410, .465], "fw": [.871, .871, .879, .885, .871, .879]}
T2 = {"params": [16356509, 6314461, 12336605, 14845085, 5540317, 11562461], "epochs": [27, 21, 30, 30, 23, 42],
      "runtime": ["22m54s", "16m21s", "27m41s", "24m9s", "16m58s", "36m31s"]}
DEF = ["crack rbn edge", "inactive", "rings", "material", "crack", "gridline", "splice", "dead cell", "corrosion rbn",
       "belt mark", "edge dark", "meas artifact", "scuff", "corrosion cell", "brightening", "star"]
FEAT = ["bckgnd", "sp multi", "sp mono", "sp dogbone", "ribbons", "border", "text", "padding", "busbars", "frame edge",
        "jbox", "sp mono halfcut"]  # clamp left out, as the paper

# check the transcription against Table 3 (features and defects means)
for i, m in enumerate(M):
    f, d = np.mean([FIG3[c][i] for c in FEAT]), np.mean([FIG3[c][i] for c in DEF])
    assert abs(f - T3["features"][i]) < 0.0015 and abs(d - T3["defects"][i]) < 0.0015, (m, f, d)
print("transcription check: Fig. 3 means reproduce Table 3 features/defects for all 6 models (|diff| < 0.0015)")
print("Table 3 '29 classes' vs Fig. 3 mean (28 classes, clamp out / 29 with clamp = 0):",
      ", ".join(f"{LBL[m]} {T3['29'][i]:.3f} vs {np.mean([FIG3[c][i] for c in FEAT + DEF]):.3f}/{sum(FIG3[c][i] for c in FEAT + DEF) / 29:.3f}"
                for i, m in enumerate(M)))

R = {}
for f in sorted(glob.glob(os.path.join(a.raw, "*_s[0-9].json"))):
    k = os.path.basename(f)[:-5]; R[k] = json.load(open(f))
runs = {m: sorted(k for k in R if k.rsplit("_s", 1)[0] == m) for m in M}
gt = R[next(iter(R))]["test"]["gt_px"]
absent = [c for c in FEAT + DEF if gt[c] == 0]
print(f"\nour test (release split, {R[next(iter(R))]['info']['n_test']} cells): classes absent = {absent}")
DEFp, FEATp = [c for c in DEF if c not in absent], [c for c in FEAT if c not in absent]

print("\n## Runs (ours vs paper Table 2)")
print("| model | seed | trainable params (paper) | epochs run (paper) | best val-loss epoch | train min (paper) |\n|---|---|---|---|---|---|")
for i, m in enumerate(M):
    for k in runs[m]:
        I = R[k]["info"]
        print(f"| {LBL[m]} | {I['seed']} | {I['trainable_params']:,} ({T2['params'][i]:,}) | {I['epochs_run']} ({T2['epochs'][i]}) | "
              f"{I.get('best_epoch_val_loss')} | {I['train_sec'] / 60:.1f} ({T2['runtime'][i]}) |")


def stat(m, fn):
    v = np.array([fn(R[k]["test"]) for k in runs[m]])
    return v.mean(), (v.std(ddof=1) if len(v) > 1 else float("nan")), len(v)


def fmt(m, fn):
    mu, sd, n = stat(m, fn)
    return f"{mu:.3f}" + (f"±{sd:.3f}" if n > 1 else "")


print("\n## Table 3: ours (test, release split) vs paper")
print("| model | features (12) ours / paper | defects (16) ours / paper | 29 ours / paper | FW IoU ours / paper |\n|---|---|---|---|---|")
for i, m in enumerate(M):
    if runs[m]:
        print(f"| {LBL[m]} (n={len(runs[m])}) | {fmt(m, lambda t: t['mean_iou_features_12'])} / {T3['features'][i]:.3f} | "
              f"{fmt(m, lambda t: t['mean_iou_defects_16'])} / {T3['defects'][i]:.3f} | {fmt(m, lambda t: t['mean_iou_29'])} / {T3['29'][i]:.3f} | "
              f"{fmt(m, lambda t: t['fw_iou'])} / {T3['fw'][i]:.3f} |")

print(f"\n## Same means over classes present in our test only ({len(FEATp)} feature, {len(DEFp)} defect), ours vs paper's Fig. 3 on the same classes")
print("| model | features ours / paper | defects ours / paper |\n|---|---|---|")
for i, m in enumerate(M):
    if runs[m]:
        print(f"| {LBL[m]} | {fmt(m, lambda t: np.mean([t['class_iou'][c] for c in FEATp]))} / {np.mean([FIG3[c][i] for c in FEATp]):.3f} | "
              f"{fmt(m, lambda t: np.mean([t['class_iou'][c] for c in DEFp]))} / {np.mean([FIG3[c][i] for c in DEFp]):.3f} |")

print("\n## Per class, test IoU: ours / paper (Fig. 3). VGG16-UNet ours = mean±sd over seeds")
print("| class | group | test GT px | " + " | ".join(LBL[m] for m in M) + " |\n|---|---|---|" + "---|" * len(M))
for c in DEF + FEAT + ["clamp"]:
    cells = []
    for i, m in enumerate(M):
        o = fmt(m, lambda t: t["class_iou"][c]) if runs[m] else "–"
        cells.append(f"{o} / {FIG3[c][i]:.3f}" if c in FIG3 else o)
    print(f"| {c} | {'defect' if c in DEF else 'feature'} | {gt[c]:,} | " + " | ".join(cells) + " |")

# figure: ours vs paper per class, all models
fig, axs = plt.subplots(1, 2, figsize=(12, 5.5))
for ax, cls, title in ((axs[0], DEFp, "defect classes present in our test"), (axs[1], FEATp, "feature classes present in our test")):
    for i, m in enumerate(M):
        if not runs[m]:
            continue
        x = [FIG3[c][i] for c in cls]; y = [stat(m, lambda t: t["class_iou"][c])[0] for c in cls]
        ax.scatter(x, y, s=18, label=LBL[m])
        if m == "vgg_unet":
            for c, xx, yy in zip(cls, x, y):
                ax.annotate(c, (xx, yy), fontsize=6, alpha=0.8)
    ax.plot([0, 1], [0, 1], "k--", lw=0.8); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("paper (Fig. 3, their 77-cell test)"); ax.set_ylabel("ours (release 72-cell test)"); ax.set_title(title, fontsize=9)
    ax.grid(alpha=0.3)
axs[0].legend(fontsize=7)
fig.suptitle("P19: Hanifi 2025 reproduction, per-class test IoU (release split, no augmentation; labels on VGG16-UNet points)", fontsize=10)
fig.tight_layout(); fig.savefig(a.out, dpi=150)
print("\nwrote", a.out)
