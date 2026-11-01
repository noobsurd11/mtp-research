"""calib idea 2: per-cell intensity statistics (read-only, CPU, single thread). Images are read as the house loader does
(PIL convert("L"), uint8). No labels are used except the padding class (7) when a mask exists, to report stats on the
non-padding area as well.
Per cell: mean, sd, p1, p5, p25, p50, p75, p95, p99 (all px); same on non-padding px when a mask exists; robust contrast
(p95-p5)/p50; noise = 1.4826*MAD of (img - 5x5 median); dark-line counts: prominent minima of the row and column mean
profiles (busbar / cut-line proxy, prominence >= 8 grey levels, distance >= 20 px).
Sets: train, val, test (image stats only), ext (E1), rf (Hanifi _rf, hygiene 106), pool (11,938 external, image only).
Output TSV: set, stem, module, half(pool inventory or E1/rf context), stats...
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.signal import find_peaks

ap = argparse.ArgumentParser()
ap.add_argument("--code", default="/home/noob/work/el_f3")
ap.add_argument("--ext", default="/home/noob/work/el_f1/reports/f1/ext117")
ap.add_argument("--rf", default="/home/noob/work/calib/data/rf")
ap.add_argument("--pool-root", default="/home/noob/work/el-fault-detection/data")
ap.add_argument("--inventory", default="/home/noob/work/sa-unetpp-ssl-el/data/unlabeled/_inventory.json")
ap.add_argument("--out", required=True)
ap.add_argument("--sets", nargs="+", default=["train", "val", "test", "ext", "rf", "pool"])
ap.add_argument("--ref-out", help="write the train reference (pooled mean, sd, 256-bin cdf over train CONTENT px: letterbox rule, non-padding) for calib_dump --tt")
a = ap.parse_args()
D = Path(a.code) / "data"
Q = [1, 5, 25, 50, 75, 95, 99]


def module(stem):
    return "_".join(stem.split("_")[:2])


def dark_lines(prof):
    pk, _ = find_peaks(-prof, prominence=8, distance=20)
    return len(pk)


def content_mask(img):
    """F6 letterbox rule (team_2026-10-27_unlabelled/ideas.md): a row/col is white if >= 98% of its px are >= 250."""
    wr = np.mean(img >= 250, axis=1) > 0.98; wc = np.mean(img >= 250, axis=0) > 0.98
    return (~wr[:, None]) & (~wc[None, :])


def stats(img, nonpad):
    x = img.astype(np.float32)
    q = np.percentile(x, Q)
    o = {"mean": float(x.mean()), "sd": float(x.std())}
    o.update({f"p{k}": float(v) for k, v in zip(Q, q)})
    o["contrast"] = float((q[5] - q[1]) / max(q[3], 1.0))
    r = x - ndi.median_filter(x, 5)
    o["noise"] = float(1.4826 * np.median(np.abs(r - np.median(r))))
    o["rows_dark"], o["cols_dark"] = dark_lines(x.mean(1)), dark_lines(x.mean(0))
    cm = content_mask(img)
    if nonpad is not None:
        cm = cm & nonpad
    ys, xs = np.where(content_mask(img))
    o["content_frac"] = float(cm.mean())
    o["letterbox"] = int(len(ys) > 0 and (xs.max() - xs.min() + 1) / max(ys.max() - ys.min() + 1, 1) >= 1.6 and (ys.max() - ys.min() + 1) <= 360)
    if cm.sum() > 1000:
        y = x[cm]; qq = np.percentile(y, Q)
        o.update({"c_mean": float(y.mean()), "c_sd": float(y.std())})
        o.update({f"c_p{k}": float(v) for k, v in zip(Q, qq)})
        o["c_contrast"] = float((qq[5] - qq[1]) / max(qq[3], 1.0))
        er = ndi.binary_erosion(cm, iterations=3)
        if er.sum() > 500:
            rr = r[er]; o["c_noise"] = float(1.4826 * np.median(np.abs(rr - np.median(rr))))
    if nonpad is not None and nonpad.sum() > 1000:
        y = x[nonpad]; qq = np.percentile(y, Q)
        o.update({"np_mean": float(y.mean()), "np_sd": float(y.std()), "np_p5": float(qq[1]), "np_p50": float(qq[3]), "np_p95": float(qq[5]),
                  "np_frac": float(nonpad.mean())})
    return o


def items():
    if any(s in a.sets for s in ("train", "val", "test")):
        for sp in ("train", "val", "test"):
            if sp not in a.sets:
                continue
            for s in sorted(l.strip() for l in open(D / "splits" / f"{sp}.txt") if l.strip()):
                yield sp, s, D / "labeled" / "images" / f"{s}.png", D / "labeled" / "masks_escdd" / f"{s}.png", ""
    ctx = {}
    for l in open(Path(a.code) / "reports" / "d" / "e1_context.tsv"):
        f = l.rstrip("\n").split("\t")
        if len(f) >= 4:
            ctx[f[0]] = ("halfcut" if f[3] == "halfcut=1" else "full") + ("+scuff" if f[2] == "scuff=1" else "")
    if "ext" in a.sets:
        for s in (l.strip() for l in open(Path(a.ext) / "stems_eval.txt") if l.strip()):
            yield "ext", s, Path(a.ext) / "images" / f"{s}.png", Path(a.ext) / "masks" / f"{s}.png", ctx.get(s, "")
    if "rf" in a.sets:
        rc = {}
        for i, l in enumerate(open(Path(a.rf) / "rf_context.tsv")):
            f = l.rstrip("\n").split("\t")
            if i:
                rc[f[0]] = ("halfcut" if f[5] == "1" else "full") + ("+scuff" if f[6] == "1" else "")
        for s in (l.strip() for l in open(Path(a.rf) / "stems_eval.txt") if l.strip()):
            yield "rf", s, Path(a.rf) / "images" / f"{s}.png", Path(a.rf) / "masks" / f"{s}.png", rc.get(s, "")
    if "pool" in a.sets:
        inv = json.load(open(a.inventory))
        half = {Path(e["name"]).stem for e in inv if "half" in e.get("rel", "").lower()}
        for s in (l.strip() for l in open(D / "splits" / "external_unlabeled.txt") if l.strip()):
            p = Path(a.pool_root) / "unlabeled" / "images_512" / f"{s}.png"
            yield "pool", s, p, None, "halfcut" if s in half else "full"


rows = []
H = np.zeros(256, np.float64)
for sp, s, img, msk, cx in items():
    im = np.array(Image.open(img).convert("L"), np.uint8)
    if sp == "train":  # train reference on content px (letterbox rule + non-padding), as the test-time mapping uses
        cm_ = content_mask(im)
        if msk is not None and Path(msk).exists():
            mm_ = np.array(Image.open(msk)); cm_ &= (mm_ != 7) & (mm_ != 255)
        H += np.bincount(im[cm_].ravel(), minlength=256)
    npd = None
    if msk is not None and Path(msk).exists():
        m = np.array(Image.open(msk)); npd = (m != 7) & (m != 255)
    o = stats(im, npd)
    rows.append({"set": sp, "stem": s, "module": module(s), "ctx": cx, "h": im.shape[0], "w": im.shape[1], **o})
keys = list(dict.fromkeys(k for r in rows for k in r))
with open(a.out, "w") as f:
    f.write("\t".join(keys) + "\n")
    for r in rows:
        f.write("\t".join(f"{r[k]:.4f}" if isinstance(r.get(k), float) else str(r.get(k, "")) for k in keys) + "\n")
print("rows", len(rows))
if a.ref_out and H.sum():
    v = np.arange(256); mu = (H * v).sum() / H.sum(); sd = np.sqrt((H * (v - mu) ** 2).sum() / H.sum())
    np.savez(a.ref_out, mean=mu, sd=sd, cdf=np.cumsum(H) / H.sum(), hist=H)
    print("train ref", mu, sd)
