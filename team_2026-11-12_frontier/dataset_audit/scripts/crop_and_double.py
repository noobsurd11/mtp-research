"""(1) The one double annotation (CFVS_00015_r7_c4 = CFVS_00016_r7_c4, pixel-identical images, both pool): label-vs-label agreement
on the headline metrics (strict crack IoU, relF1@2, inactive IoU, per-class IoU). (2) Crop effect: recall of v1.1 crack px by the
25-model consensus (>= 13 votes, within 2 px) inside vs outside the centre cell, and within 32 px of the image edge vs further in;
share of systematic misses (<= 5 of 25 models within 2 px) in each part. Writes out/crop_and_double.txt."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402

import common as C  # noqa: E402
import labels_audit as LA  # noqa: E402


def main():
    stems = C.pool_stems()
    pool = set(stems)
    L = []
    W = L.append
    a, b = "CFVS_00015_r7_c4", "CFVS_00016_r7_c4"
    C.guard(a, pool); C.guard(b, pool)
    ga, gb = C.mask_v11(a), C.mask_v11(b)
    assert (C.grey(a) == C.grey(b)).all()
    k = (ga != C.IGN) & (gb != C.IGN)
    W("# crop_and_double.txt")
    W(f"\n## f2. Double annotation {a} vs {b} (same pixels; two masks in the release)")
    ca, cb = (ga == 14) & k, (gb == 14) & k
    tp = (ca & cb).sum()
    W(f"crack px {ca.sum()} vs {cb.sum()}; strict crack IoU {tp / (ca | cb).sum():.4f}")
    ph, pn, rh, rn = LA.rel(ca, cb)
    P, R = ph / pn, rh / rn
    W(f"relP@2 (a against b) {P:.4f}, relR@2 {R:.4f}, relF1@2 {2 * P * R / (P + R):.4f}")
    ia, ib = (ga == 11) & k, (gb == 11) & k
    W(f"inactive px {ia.sum()} vs {ib.sum()}; inactive IoU {(ia & ib).sum() / max((ia | ib).sum(), 1):.4f}")
    W(f"share of all px with the same class in both masks {(ga[k] == gb[k]).mean():.4f}")
    cls = [c for c in range(24) if ((ga == c) | (gb == c)).any()]
    W("per-class IoU: " + ", ".join(f"{LA.NAMES[c]} {((ga == c) & (gb == c) & k).sum() / max(((ga == c) | (gb == c)).sum(), 1):.3f}" for c in cls))
    # crop effect
    W("\n## b6. Crop effect: consensus (>= 13 of 25) recall of v1.1 crack px within 2 px, by place in the window")
    acc = {k_: [0, 0, 0] for k_ in ("centre", "outside", "edge32", "inner")}
    for s in stems:
        gt = C.mask_v11(s)
        g = (gt == 14) & (gt != C.IGN)
        if not g.any():
            continue
        z = np.load(C.CACHE / "cons" / f"{s}.npz")
        cons = z["vc"] >= 13
        near = ndi.distance_transform_edt(~cons) <= 2 if cons.any() else np.zeros_like(g)
        sysm = z["ncov"] <= 5
        (y0, y1, x0, x1), _ = LA.central_rect(gt)
        cen = np.zeros_like(g); cen[y0:y1 + 1, x0:x1 + 1] = True
        edge = np.ones_like(g); edge[32:480, 32:480] = False
        for name, m in (("centre", cen), ("outside", ~cen), ("edge32", edge), ("inner", ~edge)):
            gg = g & m
            acc[name][0] += int(gg.sum()); acc[name][1] += int((gg & near).sum()); acc[name][2] += int((gg & sysm).sum())
    for name, (n, h, sm) in acc.items():
        W(f"{name}: crack px {n}, consensus recall@2 {h / max(n, 1):.4f}, share missed by >= 20 of 25 models {sm / max(n, 1):.4f}")
    open(C.OUT / "crop_and_double.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
