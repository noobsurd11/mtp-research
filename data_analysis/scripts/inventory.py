"""Q1 + Q6(modules) + Q7: class inventory, sources, shift, module sharing, class-weight operating point.

usage: python -I inventory.py <dataset_20211104 dir> <splits dir> <out dir>
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

from common import (BG, CRACK, INACTIVE, NUM_CLASSES, PADDING, class_kinds, class_names, load_image,  # noqa: E402
                    load_mask, parse_name, read_list, stems)


def ce_weights(counts: np.ndarray, cap_ratio: float = 10.0) -> np.ndarray:
    present = counts > 0
    w = np.zeros(NUM_CLASSES)
    freq = counts[present] / counts.sum()
    ww = 1.0 / np.sqrt(freq)
    ww = np.minimum(ww, cap_ratio * np.median(ww))
    w[present] = ww / ww.mean()
    return w


def main() -> None:
    root, splits_dir, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    names, kinds = class_names(root), class_kinds(root)
    per_image = {}
    for split in ("train", "val", "test"):
        for s in stems(root, split):
            m = load_mask(root, split, s)
            im = load_image(root, split, s)
            if m.max() >= NUM_CLASSES:
                raise ValueError(f"{split}/{s}: mask value {m.max()}")
            cnt = np.bincount(m.ravel(), minlength=NUM_CLASSES)
            cell = (m != PADDING)
            src, mod = parse_name(s)
            per_image[(split, s)] = dict(
                counts=cnt, src=src, mod=mod, shape=m.shape, img_dtype=str(im.dtype),
                mean=float(im[cell].mean()), sd=float(im[cell].std()),
                p5=float(np.percentile(im[cell], 5)), p95=float(np.percentile(im[cell], 95)))

    res: dict = {"class_names": names, "class_kinds": kinds}
    shapes = Counter(v["shape"] for v in per_image.values())
    res["shapes"] = {str(k): c for k, c in shapes.items()}

    # ---- per split class inventory ----
    inv = {}
    for split in ("train", "val", "test"):
        items = [v for (sp, _), v in per_image.items() if sp == split]
        tot = np.sum([v["counts"] for v in items], axis=0)
        pres = np.sum([v["counts"] > 0 for v in items], axis=0)
        inv[split] = dict(n_images=len(items), pixels=tot.tolist(), share=(tot / tot.sum()).tolist(),
                          images_with=pres.tolist(), absent=[names[c] for c in range(NUM_CLASSES) if tot[c] == 0])
        crack_imgs = [v for v in items if v["counts"][CRACK] > 0]
        inact_imgs = [v for v in items if v["counts"][INACTIVE] > 0]
        both = [v for v in items if v["counts"][CRACK] > 0 and v["counts"][INACTIVE] > 0]
        inv[split]["crack_images"] = len(crack_imgs)
        inv[split]["inactive_images"] = len(inact_imgs)
        inv[split]["crack_and_inactive"] = len(both)
        inv[split]["inactive_without_crack"] = len(inact_imgs) - len(both)
        inv[split]["sources"] = dict(Counter(v["src"] for v in items))
        inv[split]["crack_images_by_source"] = dict(Counter(v["src"] for v in crack_imgs))
        cp = np.array([v["counts"][CRACK] for v in crack_imgs])
        inv[split]["crack_px_per_crack_image"] = dict(median=float(np.median(cp)), mean=float(cp.mean()),
                                                      p10=float(np.percentile(cp, 10)), p90=float(np.percentile(cp, 90)))
        ip = np.array([v["counts"][INACTIVE] for v in inact_imgs]) if inact_imgs else np.array([0])
        inv[split]["inactive_px_per_inactive_image"] = dict(median=float(np.median(ip)), mean=float(ip.mean()))
        sds = np.array([v["sd"] for v in items])
        means = np.array([v["mean"] for v in items])
        inv[split]["intensity_sd_median"] = float(np.median(sds))
        inv[split]["intensity_mean_median"] = float(np.median(means))
        by_src = defaultdict(list)
        for v in items:
            by_src[v["src"]].append(v)
        inv[split]["by_source"] = {
            k: dict(n=len(vs), sd_median=float(np.median([v["sd"] for v in vs])),
                    mean_median=float(np.median([v["mean"] for v in vs])),
                    crack_frac=float(np.mean([v["counts"][CRACK] > 0 for v in vs])))
            for k, vs in sorted(by_src.items())}
    res["inventory"] = inv

    # ---- module sharing across splits ----
    mods = {sp: {v["mod"] for (s2, _), v in per_image.items() if s2 == sp} for sp in ("train", "val", "test")}
    res["modules"] = {sp: len(m) for sp, m in mods.items()}
    for sp in ("val", "test"):
        shared = [s for (s2, s), v in per_image.items() if s2 == sp and v["mod"] in mods["train"]]
        res[f"{sp}_images_from_train_modules"] = len(shared)
    res["val_test_shared_modules"] = len(mods["val"] & mods["test"])

    # ---- class weights for labelled subsets (seed 0) ----
    train_counts = {s: v["counts"] for (sp, s), v in per_image.items() if sp == "train"}
    subsets = {"100pct": read_list(splits_dir / "train.txt")}
    for p in ("50", "20", "10", "5", "2"):
        f = splits_dir / "seed0" / f"labeled_{p}pct.txt"
        if f.exists():
            subsets[f"{p}pct"] = read_list(f)
    wres = {}
    for tag, sl in subsets.items():
        missing = [s for s in sl if s not in train_counts]
        if missing:
            raise ValueError(f"{tag}: {len(missing)} stems not in train_original, e.g. {missing[:3]}")
        counts = np.sum([train_counts[s] for s in sl], axis=0).astype(np.float64)
        w = ce_weights(counts)
        share = counts / counts.sum()
        loss_mass = w * share
        loss_mass = loss_mass / loss_mass.sum()
        thr = w[BG] / (w[BG] + w[CRACK]) if w[CRACK] > 0 else float("nan")
        wres[tag] = dict(
            n_images=len(sl), weights=[round(x, 4) for x in w.tolist()],
            zero_weight_classes=[names[c] for c in range(NUM_CLASSES) if w[c] == 0],
            bg_weight=float(w[BG]), crack_weight=float(w[CRACK]), inactive_weight=float(w[INACTIVE]),
            padding_weight=float(w[PADDING]),
            crack_to_bg_ratio=float(w[CRACK] / w[BG]),
            p_crack_threshold_vs_bg=float(thr),
            capped_classes=[names[c] for c in range(NUM_CLASSES)
                            if counts[c] > 0 and abs(w[c] - w[counts > 0].max()) < 1e-9],
            pixel_share={names[c]: float(share[c]) for c in range(NUM_CLASSES)},
            loss_mass_share={names[c]: float(loss_mass[c]) for c in range(NUM_CLASSES)},
            crack_images=int(sum(train_counts[s][CRACK] > 0 for s in sl)),
            inactive_images=int(sum(train_counts[s][INACTIVE] > 0 for s in sl)),
        )
    res["class_weights_seed0"] = wres

    with open(out / "inventory.json", "w") as f:
        json.dump(res, f, indent=1)
    # compact printout
    print("shapes", res["shapes"])
    for sp in ("train", "val", "test"):
        d = inv[sp]
        print(f"\n== {sp}: n={d['n_images']} crack_imgs={d['crack_images']} inactive_imgs={d['inactive_images']} "
              f"both={d['crack_and_inactive']} inactive_wo_crack={d['inactive_without_crack']}")
        print("  sources", d["sources"], " crack by source", d["crack_images_by_source"])
        print("  absent:", d["absent"])
        print("  crack px:", d["pixels"][CRACK], "share %.4f%%" % (100 * d["share"][CRACK]),
              " inactive px:", d["pixels"][INACTIVE], " bg %.1f%% pad %.1f%%" % (100 * d["share"][BG], 100 * d["share"][PADDING]))
        print("  crack px/crack img", d["crack_px_per_crack_image"], " sd median %.1f mean median %.1f" % (
            d["intensity_sd_median"], d["intensity_mean_median"]))
        print("  by source", d["by_source"])
    print("\nmodules", res["modules"], "val from train modules", res["val_images_from_train_modules"],
          "test from train modules", res["test_images_from_train_modules"], "val&test shared modules",
          res["val_test_shared_modules"])
    print("\nper-class pixels / images (train | val | test):")
    for c in range(NUM_CLASSES):
        print(f"  {c:2d} {names[c]:14s} {kinds[c]:7s} " + " | ".join(
            f"{inv[sp]['pixels'][c]:>10d} px {inv[sp]['images_with'][c]:>3d} im" for sp in ("train", "val", "test")))
    for tag, d in wres.items():
        print(f"\nweights {tag} (n={d['n_images']}): bg {d['bg_weight']:.4f} crack {d['crack_weight']:.4f} "
              f"inactive {d['inactive_weight']:.4f} padding {d['padding_weight']:.4f} crack/bg {d['crack_to_bg_ratio']:.1f} "
              f"p_crack thr {d['p_crack_threshold_vs_bg']:.4f} zero-w {len(d['zero_weight_classes'])} capped {d['capped_classes']}")
        lm = sorted(d["loss_mass_share"].items(), key=lambda x: -x[1])[:8]
        print("  loss-mass share top:", ", ".join(f"{k} {v:.3f}" for k, v in lm))


if __name__ == "__main__":
    main()
