"""Q2/Q5: physical-module groups, cross-split leakage, raw vs '_output' session copies, and twin-cell mask agreement.

Twin module rule (from ucf_twins.py's distributions, checked visually in figs/ucf_twin_check.png):
  median refined NCC over shared cells >= 0.6, OR mean crack-mask IoU (128 px, 2 px dilation) >= 0.4 over >= 3 crack cells.
Modules are grouped by union-find. A cell's twins are the same cell index in the other modules of its group.
Mask agreement: twin pairs with refined NCC >= 0.8 (near-identical image, little real change), image b resized to
image a's size, translation from phase correlation, then per-class IoU and 2 px tolerance F1 between the masks.

Usage: python -I ucf_twins2.py <UCF root> <splits dir> <out dir> <figs dir>
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.registration import phase_cross_correlation

sys.path.insert(0, str(Path(__file__).parent))
from ucf_common import CLASSES, IGNORE, dump, load_split_list, pairs  # noqa: E402

root, sdir, od, figs = (Path(x) for x in sys.argv[1:5])
D = np.load(od / "ucf_refined_desc.npy")
rel = [(s, n, a) for s in ("train", "test") for n, a in pairs(root, s)]
relset = {n for _, n, _ in rel}
extra = sorted(p.name for p in (root / "Test_Images").iterdir() if p.name not in relset)
items = rel + [("extra", n, None) for n in extra]
pos = {n: i for i, (_, n, _) in enumerate(items)}


def key(n):
    m = re.match(r"^M(\d+)C(\d{3})\d{3}\.(jpg|png)$", n)
    if m:
        return ("M" + m[1] + ("p" if m[3] == "png" else ""), int(m[2]))
    m = re.match(r"^(.+?) TestName_(\d{8}_[\d.]+)(_output_\d+_\d+(_altered)?)?_C(\d+)\.jpg$", n)
    if m:
        return (f"{m[1]}|{m[2]}|{'output' if m[3] else 'raw'}", int(m[5]))
    return None


mods = collections.defaultdict(dict)
for i, (s, n, a) in enumerate(items):
    k = key(n)
    if k:
        mods[k[0]][k[1]] = i
mp = json.load(open(od / "ucf_module_pairs.json"))["module_pairs"]
TIER = sys.argv[5] if len(sys.argv) > 5 else "A"
tierA = [(p[0], p[1]) for p in mp if p[5] is not None and p[4] >= 3 and p[5] >= 0.4]
tierB = [(p[0], p[1]) for p in mp if p[3] >= 0.6]
twin_pairs = tierA if TIER == "A" else sorted(set(tierA) | set(tierB))
direct = collections.defaultdict(set)
for a, b in twin_pairs:
    direct[a].add(b); direct[b].add(a)
# named sessions: raw vs output of the same session are copies by construction; add if their median NCC is high
parent = {m: m for m in mods}


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


for a, b in twin_pairs:
    parent[find(a)] = find(b)
groups = collections.defaultdict(list)
for m in mods:
    groups[find(m)].append(m)
multi = {g: v for g, v in groups.items() if len(v) > 1}
res = {"twin_module_pairs": len(twin_pairs), "module_ids": len(mods), "physical_modules": len(groups),
       "groups_with_more_than_one_id": len(multi),
       "group_size_hist": dict(collections.Counter(len(v) for v in groups.values())),
       "example_groups": sorted(multi.values(), key=len, reverse=True)[:8]}
# raw vs output named sessions
ro = []
for m in mods:
    if m.endswith("|raw"):
        o = m[:-4] + "|output"
        if o in mods:
            common = set(mods[m]) & set(mods[o])
            ncc = [float(D[mods[m][c]] @ D[mods[o][c]]) for c in common]
            ri, oi = [mods[m][c] for c in sorted(mods[m])], [mods[o][c] for c in sorted(mods[o])]
            best = (D[ri] @ D[oi].T).max(1)
            ro.append({"session": m[:-4], "shared_cells": len(common), "median_ncc": float(np.median(ncc)),
                       "median_best_ncc_any_cell": float(np.median(best)),
                       "grouped": find(m) == find(o)})
res["raw_vs_output_sessions"] = ro

# twins of each released cell
split_of = {n: s for s, n, _ in items}
twins_of = {}
for i, (s, n, a) in enumerate(items):
    k = key(n)
    if not k:
        twins_of[n] = []
        continue
    tw = [items[mods[m][k[1]]][1] for m in direct[k[0]] if k[1] in mods[m]]  # direct evidence only, no chaining
    twins_of[n] = tw


def leak(names: list[str], against: set[str]) -> dict:
    hit = [n for n in names if any(t in against for t in twins_of.get(n, []))]
    return {"n": len(names), "with_twin_in_other_set": len(hit), "share": round(len(hit) / max(len(names), 1), 4)}


train = {n for s, n, _ in rel if s == "train"}
test = [n for s, n, _ in rel if s == "test"]
res["leak_test_vs_train"] = leak(test, train)
res["leak_test_vs_extra_pool"] = leak(test, set(extra))
for f in ("sl20_seed0", "sl5_seed0", "sl1_seed0", "val957_seed0"):
    names = load_split_list(sdir / f"{f}.txt")
    res[f"leak_{f}_vs_test"] = leak(names, set(test))
val = set(load_split_list(sdir / "val957_seed0.txt"))
res["leak_val957_vs_rest_of_train"] = leak(sorted(val), train - val)
res["extra_pool_twin_of_test"] = leak(extra, set(test))
res["extra_pool_twin_of_train"] = leak(extra, train)


# mask agreement on near-identical twins
def tol_f1(a, b, r=2):
    if not a.any() and not b.any():
        return None
    da, db = ndi.distance_transform_edt(~a), ndi.distance_transform_edt(~b)
    p = (db[a] <= r).mean() if a.any() else 0.0
    q = (da[b] <= r).mean() if b.any() else 0.0
    return 2 * p * q / (p + q) if p + q else 0.0


ann = {n: (s, a) for s, n, a in rel}
I = collections.Counter(); U = collections.Counter(); f1s = collections.defaultdict(list); npairs = 0
pair_ncc = []
examples = []
seen = set()
for n in sorted(ann):
    for t in twins_of[n]:
        if t not in ann or (t, n) in seen:
            continue
        seen.add((n, t))
        ncc = float(D[pos[n]] @ D[pos[t]])
        pair_ncc.append(ncc)
        if ncc < 0.8:
            continue
        sa, aa = ann[n]
        sb, ab = ann[t]
        ia = np.asarray(Image.open(root / "training/data" / sa / "images" / n).convert("L"), np.float32)
        ib = np.asarray(Image.open(root / "training/data" / sb / "images" / t).convert("L").resize(ia.shape[::-1], Image.BILINEAR), np.float32)
        ma = np.asarray(Image.open(root / "training/data" / sa / "annotations" / aa))
        mb = np.asarray(Image.open(root / "training/data" / sb / "annotations" / ab).resize(ia.shape[::-1], Image.NEAREST))
        sh, _, _ = phase_cross_correlation(ia, ib, upsample_factor=1)
        dy, dx = int(round(sh[0])), int(round(sh[1]))
        if abs(dy) > 15 or abs(dx) > 15:
            continue
        mb = np.roll(mb, (dy, dx), (0, 1))
        npairs += 1
        for c in (1, 2, 3, 4):
            a_, b_ = ma == c, mb == c
            I[c] += int((a_ & b_).sum()); U[c] += int((a_ | b_).sum())
            f = tol_f1(a_, b_)
            if f is not None:
                f1s[c].append(f)
        if len(examples) < 6 and (ma == 1).sum() > 500:
            examples.append((sa, n, aa, sb, t, ab, dy, dx, ncc))
res["twin_pair_ncc_quantiles"] = np.quantile(pair_ncc, [.1, .5, .9]).tolist() if pair_ncc else None
res["twin_pairs_released_both"] = len(pair_ncc)
res["mask_agreement_pairs_ncc_ge_0.8"] = npairs
res["mask_agreement_iou"] = {CLASSES[c]: round(I[c] / max(U[c], 1), 4) for c in (1, 2, 3, 4)}
res["mask_agreement_tolF1_2px_median"] = {CLASSES[c]: (round(float(np.median(v)), 3), len(v)) for c, v in f1s.items()}
res["tier"] = TIER
dump(res, od / f"ucf_twins_tier{TIER}.json")
dump({"examples": examples, "twins_of": twins_of}, od / f"ucf_twins_detail_tier{TIER}.json")
print(json.dumps({k: v for k, v in res.items() if k not in ("raw_vs_output_sessions", "example_groups")}, indent=1))
print("raw vs output:", ro)
