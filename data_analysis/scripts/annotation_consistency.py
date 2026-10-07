"""Q4 annotation consistency: contrast, normal-profile offsets, global registration, unlabelled dark lines.

usage: python -I annotation_consistency.py <dataset_20211104 dir> <out dir>
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402
from skimage.filters import sato  # noqa: E402
from skimage.morphology import skeletonize  # noqa: E402

from common import BG, CRACK, INACTIVE, RIBBONS, load_image, load_mask, parse_name, stems  # noqa: E402

SQ = np.ones((3, 3), bool)
T = np.arange(-5, 5.0001, 0.25)
SEARCH = np.abs(T) <= 4
RNG = np.random.default_rng(0)


def tangents(skel: np.ndarray, lab: np.ndarray, ys: np.ndarray, xs: np.ndarray, r: int = 3) -> np.ndarray:
    """Unit tangent (dy, dx) per skeleton point from PCA of same-component skeleton points within radius r."""
    H, W = skel.shape
    out = np.full((len(ys), 2), np.nan)
    for i, (y, x) in enumerate(zip(ys, xs)):
        y0, y1, x0, x1 = max(0, y - r), min(H, y + r + 1), max(0, x - r), min(W, x + r + 1)
        win = skel[y0:y1, x0:x1] & (lab[y0:y1, x0:x1] == lab[y, x])
        py, px = np.nonzero(win)
        if len(py) < 4:
            continue
        c = np.cov(np.vstack([py, px]).astype(float))
        ev, evec = np.linalg.eigh(c)
        if ev[-1] < 2 * max(ev[0], 1e-9):  # not line-like (junction / blob)
            continue
        out[i] = evec[:, -1]
    return out


def profiles(img_s: np.ndarray, ys, xs, nrm) -> np.ndarray:
    """Intensity along the normal at offsets T, bilinear."""
    cy = ys[:, None] + T[None, :] * nrm[:, 0:1]
    cx = xs[:, None] + T[None, :] * nrm[:, 1:2]
    return ndi.map_coordinates(img_s, [cy.ravel(), cx.ravel()], order=1, mode="nearest").reshape(cy.shape)


def best_shift(img: np.ndarray, mask: np.ndarray, r: int = 3) -> tuple[int, int, float]:
    """Shift (dy, dx) of the mask that minimises mean image intensity under it (dark structures)."""
    best = (0, 0, np.inf)
    ys, xs = np.nonzero(mask)
    H, W = img.shape
    vals = {}
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            yy, xx = ys + dy, xs + dx
            ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
            v = float(img[yy[ok], xx[ok]].mean())
            vals[(dy, dx)] = v
            if v < best[2]:
                best = (dy, dx, v)
    sharp = vals[(0, 0)] - best[2]
    return best[0], best[1], sharp


def main() -> None:
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    comp_rows, point_rows, reg_rows, cand_rows = [], [], [], []
    null_offsets = []
    agg_prof_label = defaultdict(lambda: np.zeros(len(T)))
    agg_prof_n = defaultdict(int)
    for split in ("train", "val", "test"):
        for s in stems(root, split):
            m = load_mask(root, split, s)
            img = load_image(root, split, s)
            src, _ = parse_name(s)
            crack = m == CRACK
            img_s = ndi.gaussian_filter(img, 0.7)
            # ---- global registration: crack mask and ribbons mask ----
            for cls, tag in ((CRACK, "crack"), (RIBBONS, "ribbons")):
                mk = m == cls
                if mk.sum() >= 50:
                    dy, dx, sharp = best_shift(img_s, mk)
                    reg_rows.append(dict(split=split, stem=s, src=src, cls=tag, dy=dy, dx=dx, sharp=sharp,
                                         n=int(mk.sum())))
            if not crack.any():
                continue
            lab, n = ndi.label(crack, SQ)
            bgmask = m == BG
            # ---- (a) contrast per component ----
            for i, sl in enumerate(ndi.find_objects(lab), start=1):
                comp = lab == i
                area = int(comp.sum())
                if area < 10:
                    continue
                ring = ndi.binary_dilation(comp, SQ, iterations=4) & ~ndi.binary_dilation(comp, SQ, iterations=1)
                ring &= bgmask & ~crack
                if ring.sum() < 10:
                    continue
                cm, rm = float(img[comp].mean()), float(img[ring].mean())
                comp_rows.append(dict(split=split, stem=s, src=src, area=area, crack_mean=cm, ring_mean=rm,
                                      ring_sd=float(img[ring].std()),
                                      rel_dark=(rm - cm) / max(rm, 1e-6), z=(rm - cm) / max(float(img[ring].std()), 1e-6)))
            # ---- (b) normal-profile offsets on skeleton points ----
            skel = skeletonize(crack)
            sizes = ndi.sum(crack, lab, index=np.arange(1, n + 1))
            big = np.isin(lab, 1 + np.nonzero(sizes >= 15)[0]) & skel
            ys, xs = np.nonzero(big)
            if len(ys) > 400:  # subsample per image to keep balance across images
                k = RNG.choice(len(ys), 400, replace=False)
                ys, xs = ys[k], xs[k]
            if len(ys):
                tg = tangents(skel, lab, ys, xs)
                ok = ~np.isnan(tg[:, 0])
                ys, xs, tg = ys[ok], xs[ok], tg[ok]
                nrm = np.stack([-tg[:, 1], tg[:, 0]], 1)
                pr = profiles(img_s, ys.astype(float), xs.astype(float), nrm)
                ps = pr[:, SEARCH]
                j = np.argmin(ps, 1)
                tstar = T[SEARCH][j]
                far = pr[:, np.abs(T) >= 4].mean(1)
                depth = (far - ps.min(1)) / np.maximum(far, 1e-6)
                center = pr[:, np.argmin(np.abs(T))]
                depth_label = (far - center) / np.maximum(far, 1e-6)
                for a, b, c, d, e, f, g in zip(tstar, nrm[:, 0], nrm[:, 1], depth, depth_label, ys, xs):
                    point_rows.append((split, src, float(a), float(b), float(c), float(d), float(e)))
                norm_pr = pr / np.maximum(far[:, None], 1e-6)
                agg_prof_label[(split, src)] += norm_pr.sum(0)
                agg_prof_n[(split, src)] += len(norm_pr)
                # null: random background points, random directions, same image
                bys, bxs = np.nonzero(bgmask & ~ndi.binary_dilation(crack, SQ, iterations=6))
                if len(bys):
                    k = RNG.choice(len(bys), min(100, len(bys)), replace=False)
                    th = RNG.uniform(0, np.pi, len(k))
                    nn = np.stack([np.sin(th), np.cos(th)], 1)
                    prn = profiles(img_s, bys[k].astype(float), bxs[k].astype(float), nn)
                    null_offsets += T[SEARCH][np.argmin(prn[:, SEARCH], 1)].tolist()
            # ---- (c) unlabelled dark line candidates ----
            cellbg = bgmask & ~ndi.binary_dilation(m != BG, SQ, iterations=3)  # away from every labelled non-bg class
            far_from_crack = ~ndi.binary_dilation(crack, SQ, iterations=6)
            resp = sato(img, sigmas=[1, 1.5], black_ridges=True)
            ref = np.percentile(resp[bgmask], 99.5) if bgmask.any() else 1.0
            cand = (resp > 0.5 * ref) & cellbg & far_from_crack
            cl, cn = ndi.label(cand, SQ)
            for i, sl in enumerate(ndi.find_objects(cl), start=1):
                comp = cl[sl] == i
                skl = skeletonize(comp)
                L = int(skl.sum())
                if L < 30:
                    continue
                py, px = np.nonzero(skl)
                c = np.cov(np.vstack([px, py]).astype(float))
                ev, evec = np.linalg.eigh(c)
                ang = float(np.degrees(np.arctan2(evec[1, -1], evec[0, -1])) % 180)
                axis = min(ang % 90, 90 - ang % 90) < 8
                yy, xx = py.mean() + sl[0].start, px.mean() + sl[1].start
                cand_rows.append(dict(split=split, stem=s, src=src, length=L, angle=ang, axis_aligned=bool(axis),
                                      mean_resp=float(resp[sl][comp].mean() / ref), cy=float(yy), cx=float(xx),
                                      bbox=[sl[0].start, sl[0].stop, sl[1].start, sl[1].stop]))
    # ---- summaries ----
    res = {}
    P = np.array([(r[2], r[3], r[4], r[5], r[6]) for r in point_rows])
    splits = np.array([r[0] for r in point_rows])
    srcs = np.array([r[1] for r in point_rows])

    def summ(mask) -> dict:
        t, ny, nx, dep, dlab = P[mask].T
        vis = dep > 0.03
        a = np.abs(t)
        sy, sx = t * ny, t * nx
        return dict(n_points=int(mask.sum()), frac_visible_dip_gt3pct=float(vis.mean()),
                    abs_offset_le0p5=float(np.mean(a[vis] <= 0.5)), abs_offset_le1=float(np.mean(a[vis] <= 1.0)),
                    abs_offset_le2=float(np.mean(a[vis] <= 2.0)), abs_offset_gt2=float(np.mean(a[vis] > 2.0)),
                    mean_shift_dy=float(sy[vis].mean()), mean_shift_dx=float(sx[vis].mean()),
                    median_depth_at_min=float(np.median(dep)), median_depth_at_label=float(np.median(dlab)))
    res["profile_offsets_all"] = summ(np.ones(len(P), bool))
    res["profile_offsets_by_split"] = {sp: summ(splits == sp) for sp in ("train", "val", "test")}
    res["profile_offsets_by_source"] = {sc: summ(srcs == sc) for sc in sorted(set(srcs))}
    nul = np.abs(np.array(null_offsets))
    res["null_random_bg_offsets"] = dict(n=len(nul), abs_le0p5=float(np.mean(nul <= 0.5)), abs_le1=float(np.mean(nul <= 1)),
                                         abs_le2=float(np.mean(nul <= 2)))
    res["mean_profile_label_centred"] = {f"{k[0]}/{k[1]}": (agg_prof_label[k] / agg_prof_n[k]).round(4).tolist()
                                         for k in agg_prof_label}
    res["profile_T"] = T.tolist()
    C = comp_rows
    rel = np.array([c["rel_dark"] for c in C])
    area = np.array([c["area"] for c in C], float)
    res["contrast_components_ge10px"] = dict(
        n=len(C), rel_dark_percentiles=np.percentile(rel, [5, 10, 25, 50, 75, 90]).tolist(),
        frac_rel_dark_lt_0p02=float(np.mean(rel < 0.02)), frac_brighter_than_ring=float(np.mean(rel < 0)),
        pixelweighted_frac_lt_0p02=float(area[rel < 0.02].sum() / area.sum()),
        by_split={sp: dict(n=int(sum(c["split"] == sp for c in C)),
                           median=float(np.median([c["rel_dark"] for c in C if c["split"] == sp])),
                           frac_lt_0p02=float(np.mean([c["rel_dark"] < 0.02 for c in C if c["split"] == sp])))
                  for sp in ("train", "val", "test")},
        by_source={sc: dict(n=int(sum(c["src"] == sc for c in C)),
                            median=float(np.median([c["rel_dark"] for c in C if c["src"] == sc])),
                            frac_lt_0p02=float(np.mean([c["rel_dark"] < 0.02 for c in C if c["src"] == sc])))
                   for sc in sorted({c["src"] for c in C})})
    reg = defaultdict(list)
    for r in reg_rows:
        reg[r["cls"]].append(r)
    res["global_registration"] = {}
    for cls, rows in reg.items():
        dy = np.array([r["dy"] for r in rows])
        dx = np.array([r["dx"] for r in rows])
        res["global_registration"][cls] = dict(
            n_images=len(rows), frac_best_at_00=float(np.mean((dy == 0) & (dx == 0))),
            frac_within_1=float(np.mean((np.abs(dy) <= 1) & (np.abs(dx) <= 1))),
            mean_dy=float(dy.mean()), mean_dx=float(dx.mean()),
            hist=dict(sorted({f"{a},{b}": int(np.sum((dy == a) & (dx == b))) for a, b in set(zip(dy.tolist(), dx.tolist()))}.items(),
                             key=lambda kv: -kv[1])[:10]),
            by_source={sc: dict(n=sum(r["src"] == sc for r in rows),
                                frac_00=float(np.mean([(r["dy"], r["dx"]) == (0, 0) for r in rows if r["src"] == sc])),
                                mean_dy=float(np.mean([r["dy"] for r in rows if r["src"] == sc])),
                                mean_dx=float(np.mean([r["dx"] for r in rows if r["src"] == sc])))
                       for sc in sorted({r["src"] for r in rows})})
    cand_rows.sort(key=lambda r: -r["length"] * r["mean_resp"])
    nonaxis = [r for r in cand_rows if not r["axis_aligned"]]
    res["unlabelled_line_candidates"] = dict(
        n_total=len(cand_rows), n_non_axis=len(nonaxis),
        images_with_non_axis_candidate={sp: len({r["stem"] for r in nonaxis if r["split"] == sp}) for sp in ("train", "val", "test")},
        top=nonaxis[:40])
    with open(out / "annotation_consistency.json", "w") as f:
        json.dump(res, f, indent=1)
    with open(out / "registration_rows.json", "w") as f:
        json.dump(reg_rows, f)
    with open(out / "line_candidates.json", "w") as f:
        json.dump(cand_rows, f)
    for k in ("profile_offsets_all", "profile_offsets_by_split", "profile_offsets_by_source", "null_random_bg_offsets",
              "contrast_components_ge10px", "global_registration"):
        print(f"\n{k}: {json.dumps(res[k], indent=None)[:2500]}")
    print("\ncandidates:", {k: v for k, v in res["unlabelled_line_candidates"].items() if k != "top"})


if __name__ == "__main__":
    main()
