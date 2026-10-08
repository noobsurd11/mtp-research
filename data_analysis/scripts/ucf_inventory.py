"""Q1 inventory: per official split and per our subsets — sizes, families, class pixels (native and at shorter side 295),
image presence, co-occurrence, ignore share, VIA fine-class presence (crack subtypes), train vs test shift.

Usage: python -I ucf_inventory.py <UCF root> <splits dir> <out.json>
"""

from __future__ import annotations

import collections
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from ucf_common import CLASSES, IGNORE, dump, load_split_list, pairs  # noqa: E402

root, sdir, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
rel = {s: dict(pairs(root, s)) for s in ("train", "test")}
split_of = {n: s for s in rel for n in rel[s]}
rows = collections.defaultdict(list)
for r in csv.DictReader(open(root / "AnnotationsCombined.csv", newline="")):
    rows[r["filename"]].append(r)


def family(n: str) -> str:
    m = re.match(r"^M(\d+)C\d+\.(jpg|png)$", n)
    if m:
        return "M9000-series png" if n.endswith(".png") else "M-series jpg"
    return "named sessions (Bent/Control/Flat)"


def module(n: str) -> str:
    m = re.match(r"^M(\d+)C", n)
    if m:
        return "M" + m[1]
    m = re.match(r"^(.+?) TestName_(\d{8}_[\d.]+)", n)
    return m[2] if m else n


per = {}
for s in rel:
    for n, a in rel[s].items():
        m = np.asarray(Image.open(root / "training" / "data" / s / "annotations" / a))
        h, w = m.shape
        k = 295 / min(h, w)
        m295 = np.asarray(Image.fromarray(m).resize((round(w * k), round(h * k)), Image.NEAREST))
        fine = collections.Counter(json.loads(r["region_attributes"]).get("Defect_Class") for r in rows[n]
                                   if r["region_attributes"] not in ("", "{}"))
        per[n] = {"split": s, "h": h, "w": w, "family": family(n), "module": module(n),
                  "px": [int((m == c).sum()) for c in range(5)] + [int((m == IGNORE).sum())],
                  "px295": [int((m295 == c).sum()) for c in range(5)] + [int((m295 == IGNORE).sum())],
                  "fine": dict(fine)}

sets = {"train": [n for n in per if per[n]["split"] == "train"], "test": [n for n in per if per[n]["split"] == "test"]}
for f in ("sl20_seed0", "sl5_seed0", "sl1_seed0", "val957_seed0"):
    sets[f] = load_split_list(sdir / f"{f}.txt")
names6 = CLASSES + ["ignore128"]
res = {"sets": {}}
for k, ns in sets.items():
    P = np.array([per[n]["px"] for n in ns], np.int64)
    P295 = np.array([per[n]["px295"] for n in ns], np.int64)
    pres = (P > 0)
    fine = collections.Counter()
    for n in ns:
        for c in per[n]["fine"]:
            fine[c] += 1
    sig = collections.Counter("+".join(CLASSES[c] for c in range(1, 5) if pres[i, c]) or "none" for i in range(len(ns)))
    sizes = collections.Counter(f'{min(per[n]["h"], per[n]["w"]) // 50 * 50}' for n in ns)
    res["sets"][k] = {
        "n": len(ns),
        "families": dict(collections.Counter(per[n]["family"] for n in ns)),
        "n_modules": len({per[n]["module"] for n in ns}),
        "shorter_side_buckets": dict(sorted(sizes.items())),
        "pixel_share_native": {names6[c]: round(P[:, c].sum() / P.sum(), 5) for c in range(6)},
        "pixel_share_295": {names6[c]: round(P295[:, c].sum() / P295.sum(), 5) for c in range(6)},
        "pixels_295": {names6[c]: int(P295[:, c].sum()) for c in range(6)},
        "images_with": {names6[c]: int(pres[:, c].sum()) for c in range(1, 6)},
        "images_with_share": {names6[c]: round(pres[:, c].mean(), 4) for c in range(1, 6)},
        "signatures": dict(sig.most_common()),
        "fine_class_images": dict(fine.most_common()),
        "crack_px_per_crack_image_295_median": float(np.median(P295[pres[:, 1], 1])) if pres[:, 1].any() else None,
    }
# co-occurrence (train): P(class b present | class a present)
P = np.array([per[n]["px"] for n in sets["train"]]) > 0
res["train_cooccurrence_P_b_given_a"] = {CLASSES[a]: {CLASSES[b]: round(float((P[:, a] & P[:, b]).sum() / max(P[:, a].sum(), 1)), 3)
                                                      for b in range(1, 5)} for a in range(1, 5)}
# crack subtype share of crack pixels per split, via CSV region areas is approximate; use per-image dominant subtype
for s in ("train", "test"):
    sub = collections.Counter()
    for n in sets[s]:
        f = per[n]["fine"]
        for c in ("Crack_Closed", "Crack_Resistive", "Crack_Isolated"):
            if c in f:
                sub[c] += f[c]
    res[f"{s}_crack_subtype_regions"] = dict(sub)
dump({"per_image": per}, out.with_name("ucf_per_image.json"))
dump(res, out)
for k, v in res["sets"].items():
    print(k, v["n"], v["n_modules"], v["families"], "\n  share295", v["pixel_share_295"], "\n  imgs", v["images_with"], "\n  fine", v["fine_class_images"])
print(json.dumps(res["train_cooccurrence_P_b_given_a"]), res["train_crack_subtype_regions"], res["test_crack_subtype_regions"])
