"""Label-side measures on the 532 pool cells (no predictions): axis b (width, fragmentation, placement against the image,
inactive conventions, class vocabulary, crop geometry), d (20211104 vs v1.1), e (class coverage), f (shift / width ceiling,
repeat-label agreement). Writes out/labels_audit.txt, out/labels_percell.tsv, out/repeat_pairs.tsv. CPU only."""
from __future__ import annotations

import collections
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402

import common as C  # noqa: E402

SRC = ["ARTS", "BMRK", "CFVS", "CSIR", "SDLE"]
SPACING = (1, 2, 3)
PAD = 7
NAMES = ["background", "sp_multi", "sp_mono", "sp_dogbone", "ribbons", "border", "text", "padding", "clamp", "busbars",
         "crack_rbn_edge", "inactive", "rings", "material", "crack", "gridline", "splice", "dead_cell", "corrosion", "belt_mark",
         "edge_dark", "frame_edge", "jbox", "meas_artifact"]


def central_rect(gt):
    """Bounds of the cell that holds the image centre, from rows / columns that are mostly cell-gap (spacing) px.
    Returns (y0, y1, x0, x1) inclusive and a flag 'gaps found'."""
    sp = np.isin(gt, SPACING)
    nonpad = gt != PAD
    ys, xs = np.nonzero(nonpad)
    if not len(ys):
        return (0, 511, 0, 511), False
    py0, py1, px0, px1 = ys.min(), ys.max(), xs.min(), xs.max()
    rowf = sp.sum(1) / np.maximum(nonpad.sum(1), 1)
    colf = sp.sum(0) / np.maximum(nonpad.sum(0), 1)
    gr = np.nonzero(rowf > 0.2)[0]
    gc = np.nonzero(colf > 0.2)[0]
    c = 256
    y0 = max([y for y in gr if y < c - 20], default=py0)
    y1 = min([y for y in gr if y > c + 20], default=py1)
    x0 = max([x for x in gc if x < c - 20], default=px0)
    x1 = min([x for x in gc if x > c + 20], default=px1)
    return (int(y0), int(y1), int(x0), int(x1)), bool(len(gr) or len(gc))


def width_stats(g):
    if not g.any():
        return 0, 0, 0, 0
    sk = C.skeletonize(g)
    lab, n = ndi.label(g, C.S8)
    sz = np.bincount(lab.ravel())[1:]
    return int(g.sum()), int(sk.sum()), int(n), int(sz[sz < 20].sum())


def profile(gr, g, gt, maxd=10):
    """Mean grey at rounded distance d from the label skeleton, on background / crack px only. Returns array or None."""
    sk = C.skeletonize(g)
    if sk.sum() < 30:
        return None
    d = np.rint(ndi.distance_transform_edt(~sk)).astype(int)
    ok = np.isin(gt, (0, 14)) & (d <= maxd)
    s = np.bincount(d[ok], weights=gr[ok].astype(np.float64), minlength=maxd + 1)
    n = np.bincount(d[ok], minlength=maxd + 1)
    if (n < 5).any():
        return None
    return s / n


def fwhm(p):
    """Full width at half depth of a trough profile p(d), baseline = mean of d 7..10."""
    base = p[7:11].mean()
    depth = base - p[0]
    if depth <= 0:
        return np.nan, depth
    half = base - depth / 2
    for i in range(1, len(p)):
        if p[i] >= half:
            f = (half - p[i - 1]) / max(p[i] - p[i - 1], 1e-9)
            return 2 * (i - 1 + f), depth
    return np.nan, depth


def iou(a, b):
    u = (a | b).sum()
    return (a & b).sum(), u


def shift(m, dy, dx):
    o = np.zeros_like(m)
    ys = slice(max(dy, 0), 512 + min(dy, 0)); yd = slice(max(-dy, 0), 512 + min(-dy, 0))
    xs = slice(max(dx, 0), 512 + min(dx, 0)); xd = slice(max(-dx, 0), 512 + min(-dx, 0))
    o[ys, xs] = m[yd, xd]
    return o


def rel(a, b):
    """relP@2 hits of a against b, |a|, relR@2 hits of b against a, |b|."""
    na, nb = a.sum(), b.sum()
    da = ndi.distance_transform_edt(~a) <= 2 if na else np.zeros_like(a)
    db = ndi.distance_transform_edt(~b) <= 2 if nb else np.zeros_like(b)
    return int((a & db).sum()), int(na), int((b & da).sum()), int(nb)


def per_cell(stem):
    gt = C.mask_v11(stem)
    old = C.mask_old(stem)
    gr = C.grey(stem)
    keep = gt != C.IGN
    g = (gt == C.CRACK) & keep
    gi = (gt == C.INACT) & keep
    go = (old == C.CRACK) & keep
    gio = (old == C.INACT) & keep
    r = {"stem": stem, "src": stem.split("_")[0]}
    r["area"], r["sklen"], r["ncomp"], r["speck"] = width_stats(g)
    r["area_o"], r["sklen_o"], r["ncomp_o"], r["speck_o"] = width_stats(go)
    r["prof"] = profile(gr, g, gt) if r["sklen"] >= 30 else None
    # label version
    r["chg_any"] = int(((old != gt) & keep).sum())
    r["chg_crack"] = int((go ^ g).sum())
    r["chg_inact"] = int((gio ^ gi).sum())
    r["crack_o"], r["crack_n"], r["inact_o"], r["inact_n"] = int(go.sum()), int(g.sum()), int(gio.sum()), int(gi.sum())
    # crop geometry
    (y0, y1, x0, x1), found = central_rect(gt)
    cen = np.zeros_like(g); cen[y0:y1 + 1, x0:x1 + 1] = True
    nonpad = (gt != PAD)
    r["cen_share"] = float(cen.sum() / max(nonpad.sum(), 1))
    r["gaps_found"] = found
    r["crack_out"] = int((g & ~cen).sum())
    r["inact_out"] = int((gi & ~cen).sum())
    r["pad_share"] = float((gt == PAD).mean())
    # inactive conventions: crack px inside inactive (>= 70% of non-crack px in the 9 x 9 window inactive), boundary crack share
    if gi.sum() >= 100:
        nc = (~g & keep).astype(np.float32)
        fi = ndi.uniform_filter(gi.astype(np.float32), 9) / np.maximum(ndi.uniform_filter(nc, 9), 1e-6)
        r["crack_in_inact"] = int((g & (fi >= 0.7)).sum())
        bd = gi & ~ndi.binary_erosion(gi, np.ones((3, 3), bool))
        dg = ndi.distance_transform_edt(~g) if g.any() else np.full(g.shape, np.inf)
        r["inact_bd"] = int(bd.sum())
        r["inact_bd_crack"] = int((bd & (dg <= 2)).sum())
    else:
        r["crack_in_inact"] = r["inact_bd"] = r["inact_bd_crack"] = 0
    # classes present
    r["classes"] = np.bincount(gt[keep].astype(np.int64), minlength=24)[:24]
    # ceilings: 1-px and 2-px shifts, skeleton and 3-px redraw against the label
    if g.sum():
        s = {}
        for k in (1, 2):
            a = 0; u = 0
            for dy, dx in [(-k, 0), (k, 0), (0, -k), (0, k), (-k, -k), (-k, k), (k, -k), (k, k)]:
                aa, uu = iou(g, shift(g, dy, dx) & keep)
                a += aa; u += uu
            s[f"sh{k}"] = (a / 8, u / 8)
        sk = C.skeletonize(g) & keep
        w3 = ndi.binary_dilation(sk, np.ones((3, 3), bool)) & keep
        s["skel"] = iou(g, sk)
        s["w3"] = iou(g, w3)
        r["ceil"] = s
    else:
        r["ceil"] = None
    return r


def main():
    import multiprocessing as mp
    stems = C.pool_stems()
    pool = set(stems)
    for s in stems:
        C.guard(s, pool)
    with mp.get_context("fork").Pool(8) as P:
        R = P.map(per_cell, stems, chunksize=4)
    g3 = C.groups(C.G3)
    L = []
    W = L.append
    W("# labels_audit.txt (dataset_audit; label-side, 532 pool cells, v1.1 unless stated; old = BenchmarkEL 20211104)")
    # ---- b: width
    W("\n## b1. Crack label width = crack px / skeleton px (bench/skel.py); pooled per source and median of cells with >= 50 skeleton px")
    W("source | crack cells | pooled width v1.1 | median cell width v1.1 | pooled width 20211104 | comps per 100 skeleton px | share of crack px in comps < 20 px")
    widths, labs = [], []
    for so in SRC + ["ALL"]:
        rr = [r for r in R if (r["src"] == so or so == "ALL") and r["area"] > 0]
        if not rr:
            continue
        A = sum(r["area"] for r in rr); Lk = sum(r["sklen"] for r in rr)
        Ao = sum(r["area_o"] for r in rr); Lo = sum(r["sklen_o"] for r in rr)
        cw = [r["area"] / r["sklen"] for r in rr if r["sklen"] >= 50]
        if so != "ALL":
            widths += cw; labs += [so] * len(cw)
        W(f"{so} | {len(rr)} | {A / Lk:.3f} | {np.median(cw) if cw else float('nan'):.3f} | {Ao / max(Lo, 1):.3f} | "
          f"{100 * sum(r['ncomp'] for r in rr) / Lk:.2f} | {sum(r['speck'] for r in rr) / A:.4f}")
    w = np.array(widths); lb = np.array(labs)
    sst = ((w - w.mean()) ** 2).sum()
    ssb = sum(((lb == so).sum() * (w[lb == so].mean() - w.mean()) ** 2) for so in set(labs))
    W(f"eta^2 (share of the variance of per-cell label width explained by source; cells with >= 50 skeleton px, n {len(w)}): {ssb / sst:.3f}")
    # Kruskal-Wallis without scipy.stats dependency issues
    from scipy.stats import kruskal
    W(f"Kruskal-Wallis across sources: H {kruskal(*[w[lb == so] for so in sorted(set(labs))]).statistic:.1f}, "
      f"p {kruskal(*[w[lb == so] for so in sorted(set(labs))]).pvalue:.2e}")
    # ---- b: placement against the image
    W("\n## b2. Dark trough under the crack label: mean grey vs distance from the label skeleton (bg and crack px), cells averaged")
    W("source | cells | trough FWHM px (pooled profile) | label width px (pooled) | label / trough | median per-cell FWHM | trough depth (grey)")
    for so in SRC + ["ALL"]:
        pp = [r["prof"] for r in R if (r["src"] == so or so == "ALL") and r["prof"] is not None]
        if len(pp) < 3:
            continue
        pn = np.array([p - p[7:11].mean() for p in pp])
        prof = pn.mean(0) + 100
        fw, dep = fwhm(prof)
        cf = [fwhm(p)[0] for p in pp]
        rr = [r for r in R if (r["src"] == so or so == "ALL") and r["area"] > 0]
        lw = sum(r["area"] for r in rr) / sum(r["sklen"] for r in rr)
        W(f"{so} | {len(pp)} | {fw:.2f} | {lw:.2f} | {lw / fw:.2f} | {np.nanmedian(cf):.2f} | {dep:.1f}   profile d0..10: "
          + " ".join(f"{x - 100:+.1f}" for x in prof))
    # ---- b: inactive conventions
    W("\n## b3. Inactive conventions (cells with >= 100 inactive px)")
    W("source | inactive cells | share of inactive boundary px within 2 px of a crack label | cells with >= 20 crack px inside inactive | crack px inside inactive")
    for so in SRC + ["ALL"]:
        rr = [r for r in R if (r["src"] == so or so == "ALL") and r["inact_n"] >= 100]
        if not rr:
            continue
        bd = sum(r["inact_bd"] for r in rr); bc = sum(r["inact_bd_crack"] for r in rr)
        per = [r["inact_bd_crack"] / max(r["inact_bd"], 1) for r in rr]
        W(f"{so} | {len(rr)} | {bc / max(bd, 1):.3f} (per cell min {min(per):.2f}, median {np.median(per):.2f}, max {max(per):.2f}) | "
          f"{sum(r['crack_in_inact'] >= 20 for r in rr)} | {sum(r['crack_in_inact'] for r in rr)}")
    # ---- b: class vocabulary
    W("\n## b4. Cells per class per source (v1.1, pool); '*' = class in one source only")
    W("class | " + " | ".join(SRC) + " | groups (cv5v3) | px")
    cls_groups = collections.defaultdict(set)
    for r in R:
        for c in np.nonzero(r["classes"])[0]:
            cls_groups[c].add(g3[r["stem"]]["group"])
    for c in range(24):
        cnt = [sum(1 for r in R if r["src"] == so and r["classes"][c] > 0) for so in SRC]
        px = sum(int(r["classes"][c]) for r in R)
        star = "*" if sum(1 for x in cnt if x) == 1 else ""
        W(f"{c} {NAMES[c]}{star} | " + " | ".join(map(str, cnt)) + f" | {len(cls_groups[c])} | {px}")
    W("classes with < 10 cv5v3 groups (pooled IoU not measurable at this size): " +
      ", ".join(f"{NAMES[c]} ({len(cls_groups[c])})" for c in range(24) if len(cls_groups[c]) < 10))
    # ---- b5 crop geometry
    W("\n## b5. Crop geometry: the cell that holds the image centre, bounded by rows / columns that are > 20% cell-gap px")
    W("source | cells | cells with gap lines found | median share of non-padding px inside the centre cell | crack px outside the centre cell | inactive px outside | median padding share")
    for so in SRC + ["ALL"]:
        rr = [r for r in R if r["src"] == so or so == "ALL"]
        cr = sum(r["crack_n"] for r in rr); co = sum(r["crack_out"] for r in rr)
        ir = sum(r["inact_n"] for r in rr); io = sum(r["inact_out"] for r in rr)
        W(f"{so} | {len(rr)} | {sum(r['gaps_found'] for r in rr)} | {np.median([r['cen_share'] for r in rr]):.3f} | "
          f"{co} of {cr} ({co / max(cr, 1):.3f}) | {io} of {ir} ({io / max(ir, 1):.3f}) | {np.median([r['pad_share'] for r in rr]):.3f}")
    nb = sum(1 for r in R if r["crack_n"] > 0 and r["crack_out"] == r["crack_n"])
    W(f"crack cells whose every crack px lies outside the centre cell: {nb} of {sum(1 for r in R if r['crack_n'] > 0)}")
    nbi = sum(1 for r in R if r["inact_n"] > 0 and r["inact_out"] == r["inact_n"])
    W(f"inactive cells whose every inactive px lies outside the centre cell: {nbi} of {sum(1 for r in R if r['inact_n'] > 0)}")
    # ---- d: label version
    W("\n## d. Label version 20211104 -> v1.1 on the pool (v1.1 ignore px excluded)")
    for so in SRC + ["ALL"]:
        rr = [r for r in R if r["src"] == so or so == "ALL"]
        W(f"{so}: cells with any px changed {sum(r['chg_any'] > 0 for r in rr)} of {len(rr)}; crack px changed (xor) {sum(r['chg_crack'] for r in rr)}; "
          f"crack px {sum(r['crack_o'] for r in rr)} -> {sum(r['crack_n'] for r in rr)}; cells whose crack px differ {sum(r['chg_crack'] > 0 for r in rr)}; "
          f"crack cells {sum(r['crack_o'] > 0 for r in rr)} -> {sum(r['crack_n'] > 0 for r in rr)}; crack comps {sum(r['ncomp_o'] for r in rr)} -> "
          f"{sum(r['ncomp'] for r in rr)}; inactive px changed {sum(r['chg_inact'] for r in rr)}; inactive px {sum(r['inact_o'] for r in rr)} -> "
          f"{sum(r['inact_n'] for r in rr)}; any-class px changed {sum(r['chg_any'] for r in rr)}")
    # ---- f: ceilings
    W("\n## f1. Strict crack IoU of the v1.1 label against itself moved or redrawn (pooled over the 229 crack cells; mean of 8 directions)")
    cc = [r["ceil"] for r in R if r["ceil"] is not None]
    for k in ("sh1", "sh2", "skel", "w3"):
        a = sum(c[k][0] for c in cc); u = sum(c[k][1] for c in cc)
        W(f"{k}: IoU {a / u:.4f}")
    for so in SRC:
        cs = [r["ceil"] for r in R if r["ceil"] is not None and r["src"] == so]
        if cs:
            W(f"  {so}: shift 1 px {sum(c['sh1'][0] for c in cs) / sum(c['sh1'][1] for c in cs):.3f}; "
              f"skeleton {sum(c['skel'][0] for c in cs) / sum(c['skel'][1] for c in cs):.3f}; "
              f"3-px redraw {sum(c['w3'][0] for c in cs) / sum(c['w3'][1] for c in cs):.3f}")
    open(C.OUT / "labels_audit.txt", "w").write("\n".join(L) + "\n")
    with open(C.OUT / "labels_percell.tsv", "w") as f:
        keys = ["stem", "src", "area", "sklen", "ncomp", "speck", "area_o", "sklen_o", "ncomp_o", "chg_any", "chg_crack", "chg_inact",
                "crack_o", "crack_n", "inact_o", "inact_n", "cen_share", "gaps_found", "crack_out", "inact_out", "pad_share",
                "crack_in_inact", "inact_bd", "inact_bd_crack"]
        f.write("\t".join(keys) + "\n")
        for r in R:
            f.write("\t".join(f"{r[k]:.4f}" if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
