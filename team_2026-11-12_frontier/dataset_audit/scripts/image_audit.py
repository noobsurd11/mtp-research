"""Axis g (image side) and the new part of axis c, on the 532 pool images (pixels; the mask is used only for the padding class
and the cell-gap geometry). Per image: exposure, clipping, grey levels, noise, sharpness, high-frequency power, 8 x 8 blockiness,
colour spread, padding, centre-cell size. Source separability: logistic regression and random forest, 5-fold CV grouped by cv5v3
group, balanced accuracy. Duplicates: grey-pixel md5 and a 64-bit DCT hash (Hamming <= 6) across cv5v3 groups, with NCC.
Overlapping windows: pool cells with a pool cell at an adjacent position of the same module image (cells.tsv).
Writes out/image_audit.txt, out/image_features.tsv, out/dup_hash_pairs.tsv. CPU only."""
from __future__ import annotations

import collections
import hashlib
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402
from scipy.fft import dctn  # noqa: E402

import common as C  # noqa: E402
import labels_audit as LA  # noqa: E402

SRC = ["ARTS", "BMRK", "CFVS", "CSIR", "SDLE"]
SCAL = ["mean", "std", "p1", "p99", "clip0", "clip255", "levels", "noise", "lapvar", "hf", "block", "colour", "pad", "cellw"]


def feats(stem):
    im = Image.open(C.IMAGES / f"{stem}.png")
    rgba = np.array(im.convert("RGB")).astype(np.int16)
    g = np.array(im.convert("L"), dtype=np.uint8)
    gt = C.mask_v11(stem)
    npad = gt != 7
    v = g[npad].astype(np.float32)
    f = {"stem": stem, "src": stem.split("_")[0]}
    f["mean"], f["std"] = float(v.mean()), float(v.std())
    f["p1"], f["p99"] = (float(x) for x in np.percentile(v, [1, 99]))
    f["clip0"], f["clip255"] = float((v <= 0).mean()), float((v >= 255).mean())
    f["levels"] = int(len(np.unique(v)))
    med = ndi.median_filter(g, 5).astype(np.float32)
    f["noise"] = float(1.4826 * np.median(np.abs(g.astype(np.float32) - med)[npad]))
    lap = ndi.laplace(g.astype(np.float32))
    f["lapvar"] = float(lap[ndi.binary_erosion(npad, iterations=3)].var())
    # spectrum on the central 192 x 192 crop (inside the cell for every source)
    c = g[160:352, 160:352].astype(np.float32)
    c = (c - c.mean()) * np.outer(np.hanning(192), np.hanning(192))
    P = np.abs(np.fft.fftshift(np.fft.fft2(c))) ** 2
    yy, xx = np.indices(P.shape)
    r = np.hypot(yy - 96, xx - 96) / 192.0
    tot = P[(r > 0.01) & (r <= 0.5)].sum()
    f["hf"] = float(P[(r > 0.25) & (r <= 0.5)].sum() / max(tot, 1e-9))
    edges = np.linspace(0.01, 0.5, 9)
    spec = [P[(r > edges[i]) & (r <= edges[i + 1])].sum() / max(tot, 1e-9) for i in range(8)]
    # 8 x 8 blockiness: mean |horizontal diff| on columns 7|8 boundaries over the mean on other columns (inside the cell crop)
    dx = np.abs(np.diff(g[160:352, 160:352].astype(np.float32), axis=1)).mean(0)
    idx = np.arange(160, 351)
    f["block"] = float(dx[(idx % 8) == 7].mean() / max(dx[(idx % 8) != 7].mean(), 1e-6))
    f["colour"] = float((rgba.max(-1) - rgba.min(-1))[npad].mean())
    f["pad"] = float(1 - npad.mean())
    (y0, y1, x0, x1), found = LA.central_rect(gt)
    f["cellw"] = float(min(y1 - y0, x1 - x0))
    hist = np.histogram(v, bins=16, range=(0, 256))[0] / len(v)
    # DCT hash
    small = np.array(Image.fromarray(g).resize((32, 32), Image.BILINEAR), dtype=np.float32)
    D = dctn(small, norm="ortho")[:8, :8].ravel()[1:]
    f["hash"] = (D > np.median(D)).astype(np.uint8)
    f["thumb"] = np.array(Image.fromarray(g).resize((128, 128), Image.BILINEAR), dtype=np.float32)
    f["md5"] = hashlib.md5(g.tobytes()).hexdigest()
    f["vec"] = np.array([f[k] for k in SCAL] + list(hist) + spec, np.float64)
    return f


def ncc(a, b):
    a = a - a.mean(); b = b - b.mean()
    return float((a * b).sum() / max(np.sqrt((a * a).sum() * (b * b).sum()), 1e-9))


def main():
    import multiprocessing as mp
    stems = C.pool_stems()
    pool = set(stems)
    for s in stems:
        C.guard(s, pool)
    with mp.get_context("fork").Pool(8) as Pp:
        F = Pp.map(feats, stems, chunksize=4)
    g3 = C.groups(C.G3)
    L = []
    W = L.append
    W("# image_audit.txt (dataset_audit; 532 pool images; grey = PIL convert('L') of the RGBA file, as the loader)")
    W("\n## g1. Per-source image statistics (median over images; non-padding px)")
    W("source | n | " + " | ".join(SCAL))
    for so in SRC:
        ff = [f for f in F if f["src"] == so]
        W(f"{so} | {len(ff)} | " + " | ".join(f"{np.median([f[k] for f in ff]):.4g}" for k in SCAL))
    W("(mean/std/p1/p99 grey; clip0/clip255 share of px at 0 / 255; levels = grey levels used; noise = robust sigma (P16 rule); "
      "lapvar = Laplacian variance; hf = share of spectral power above 0.25 cycles/px in the central 192 px; block = 8x8 boundary "
      "diff ratio (1 = no JPEG grid); colour = mean RGB spread; pad = padding share; cellw = centre-cell size px)")
    for so in SRC:
        ff = [f for f in F if f["src"] == so]
        W(f"{so}: images with clip255 > 1%: {sum(f['clip255'] > 0.01 for f in ff)}; clip0 > 1%: {sum(f['clip0'] > 0.01 for f in ff)}; "
          f"noise > 10: {sum(f['noise'] > 10 for f in ff)}; block > 1.10: {sum(f['block'] > 1.10 for f in ff)}; colour > 2: "
          f"{sum(f['colour'] > 2 for f in ff)}; p99 < 128 (under-exposed): {sum(f['p99'] < 128 for f in ff)}; "
          f"centre cell px min/median/max {min(f['cellw'] for f in ff):.0f}/{np.median([f['cellw'] for f in ff]):.0f}/{max(f['cellw'] for f in ff):.0f}")
    # separability
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import balanced_accuracy_score, confusion_matrix
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    X = np.stack([f["vec"] for f in F])
    y = np.array([f["src"] for f in F])
    grp = np.array([g3[f["stem"]]["group"] for f in F])
    nS = len(SCAL)
    sets = {"all features": slice(None), "no padding / cell size": [i for i in range(X.shape[1]) if i not in (SCAL.index("pad"), SCAL.index("cellw"))],
            "grey histogram only (16)": list(range(nS, nS + 16)), "spectrum only (8 bins + hf)": list(range(nS + 16, nS + 24)) + [SCAL.index("hf")],
            "noise, sharpness, blockiness only": [SCAL.index(k) for k in ("noise", "lapvar", "hf", "block", "levels")]}
    W("\n## g2. Source separability: balanced accuracy, 5-fold CV grouped by cv5v3 group (chance 0.20; majority-class accuracy "
      f"{max(collections.Counter(y).values()) / len(y):.3f})")
    gkf = GroupKFold(n_splits=5)
    for name, cols in sets.items():
        Xs = X[:, cols]
        res = []
        for mname, mk in (("logreg", lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, C=1.0))),
                          ("forest", lambda: RandomForestClassifier(n_estimators=300, random_state=0, n_jobs=4))):
            pred = np.empty(len(y), dtype=object)
            for tr, te in gkf.split(Xs, y, grp):
                m = mk().fit(Xs[tr], y[tr])
                pred[te] = m.predict(Xs[te])
            res.append((mname, balanced_accuracy_score(y, pred.astype(str)), pred))
        W(f"{name}: logreg {res[0][1]:.3f}; forest {res[1][1]:.3f}")
        if name == "noise, sharpness, blockiness only":
            cm = confusion_matrix(y, res[1][2].astype(str), labels=SRC)
            W("  forest confusion (rows true " + ",".join(SRC) + "): " + "; ".join(" ".join(map(str, r)) for r in cm))
    # prevalence per source
    W("\n## g3. Defect prevalence per source (pool, v1.1; P(class | source) = share of images with the class)")
    for so in SRC:
        ss = [s for s in stems if s.startswith(so)]
        cr = sum(1 for s in ss if (C.mask_v11(s) == 14).any())
        ia = sum(1 for s in ss if (C.mask_v11(s) == 11).any())
        W(f"{so}: n {len(ss)}; crack {cr / len(ss):.3f}; inactive {ia / len(ss):.3f}")
    # duplicates
    W("\n## c1. Exact and near duplicates inside the pool")
    md = collections.defaultdict(list)
    for f in F:
        md[f["md5"]].append(f["stem"])
    ex = [v for v in md.values() if len(v) > 1]
    W(f"exact duplicates (grey-pixel md5): {len(ex)} sets: {ex}")
    H = np.stack([f["hash"] for f in F])
    T = [f["thumb"] for f in F]
    pairs = []
    for i in range(len(F)):
        d = (H[i + 1:] != H[i]).sum(1)
        for j in np.nonzero(d <= 6)[0] + i + 1:
            pairs.append((F[i]["stem"], F[j]["stem"], int(d[j - i - 1]), ncc(T[i], T[j]), g3[F[i]["stem"]]["group"] == g3[F[j]["stem"]]["group"]))
    cross = [p for p in pairs if not p[4]]
    W(f"pairs with DCT-hash Hamming <= 6: {len(pairs)}; across cv5v3 groups: {len(cross)}; of these with thumbnail NCC >= 0.9: "
      f"{sum(p[3] >= 0.9 for p in cross)}; by source: {dict(collections.Counter(p[0].split('_')[0] for p in cross))}")
    with open(C.OUT / "dup_hash_pairs.tsv", "w") as fo:
        fo.write("a\tb\thamming\tncc_thumb128\tsame_cv5v3_group\n")
        for p in sorted(pairs, key=lambda p: (p[4], -p[3])):
            fo.write(f"{p[0]}\t{p[1]}\t{p[2]}\t{p[3]:.4f}\t{int(p[4])}\n")
    # overlapping windows
    rows = [l.rstrip("\n").split("\t") for l in open(C.BENCH / "cells.tsv")]
    h = rows[0]
    cel = {r[0]: dict(zip(h, r)) for r in rows[1:] if r[0] in pool}       # pool rows only; sealed rows dropped unread
    pos = {}
    for s, r in cel.items():
        if r["position"] not in ("-", ""):
            rr, cc = r["position"].split("_")
            pos[s] = (r["image_id"], int(rr[1:]), int(cc[1:]))
    by_img = collections.defaultdict(list)
    for s, (im, rr, cc) in pos.items():
        by_img[im].append((s, rr, cc))
    adj = set()
    npairs = 0
    for im, lst in by_img.items():
        for a in range(len(lst)):
            for b in range(a + 1, len(lst)):
                if max(abs(lst[a][1] - lst[b][1]), abs(lst[a][2] - lst[b][2])) == 1:
                    adj.add(lst[a][0]); adj.add(lst[b][0]); npairs += 1
    crack_adj = sum(int(cel[s]["crack_px_v11"] or 0) for s in adj)
    crack_all = sum(int(cel[s]["crack_px_v11"] or 0) for s in cel)
    W(f"\n## c2. Overlapping windows: pool cells with another pool cell at an adjacent position (Chebyshev 1) of the same module image")
    W(f"adjacent pairs {npairs}; cells involved {len(adj)} of {len(pos)} with a position; their v1.1 crack px {crack_adj} of {crack_all} "
      f"({crack_adj / max(crack_all, 1):.3f})")
    open(C.OUT / "image_audit.txt", "w").write("\n".join(L) + "\n")
    with open(C.OUT / "image_features.tsv", "w") as fo:
        fo.write("stem\tsrc\t" + "\t".join(SCAL) + "\n")
        for f in F:
            fo.write(f"{f['stem']}\t{f['src']}\t" + "\t".join(f"{f[k]:.5g}" for k in SCAL) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
