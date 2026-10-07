"""Verify near-duplicate pairs at full resolution (image + mask) and measure per-point visible crack width.

usage: python -I verify_dups_width.py <dataset_20211104 dir> <out dir>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402
from skimage.morphology import skeletonize  # noqa: E402

from annotation_consistency import tangents  # noqa: E402
from common import CRACK, load_image, load_mask, parse_name, stems  # noqa: E402

SQ = np.ones((3, 3), bool)
RNG = np.random.default_rng(2)


def main() -> None:
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    d = json.load(open(out / "dups_fragments.json"))
    rows = []
    for p in d["near_duplicate_pairs"]:
        if p["corr"] < 0.98:
            continue
        (sa, a), (sb, b) = p["a"].split("/"), p["b"].split("/")
        ia, ib = load_image(root, sa, a), load_image(root, sb, b)
        ma, mb = load_mask(root, sa, a), load_mask(root, sb, b)
        mad = float(np.abs(ia - ib).mean())
        same_px = float(np.mean(ia == ib))
        mask_agree = float(np.mean(ma == mb))
        crack_iou = float(((ma == CRACK) & (mb == CRACK)).sum() / max(1, ((ma == CRACK) | (mb == CRACK)).sum()))
        rows.append(dict(a=p["a"], b=p["b"], corr=p["corr"], mad=round(mad, 2), identical_px_frac=round(same_px, 4),
                         mask_agreement=round(mask_agree, 4), crack_iou_between_masks=round(crack_iou, 3),
                         cross_split=p["cross_split"]))
    rows.sort(key=lambda r: r["mad"])
    # ---- per-point visible width, unsmoothed, aligned at the local minimum ----
    T = np.arange(-6, 6.0001, 0.25)
    widths, label_w = [], []
    by_src = {}
    for split in ("train", "val", "test"):
        for s in stems(root, split):
            m = load_mask(root, split, s)
            cr = m == CRACK
            if cr.sum() < 30:
                continue
            img = load_image(root, split, s)
            lab, n = ndi.label(cr, SQ)
            sizes = ndi.sum(cr, lab, index=np.arange(1, n + 1))
            sk = skeletonize(cr) & np.isin(lab, 1 + np.nonzero(sizes >= 15)[0])
            ys, xs = np.nonzero(sk)
            if len(ys) == 0:
                continue
            k = RNG.choice(len(ys), min(60, len(ys)), replace=False)
            ys, xs = ys[k], xs[k]
            tg = tangents(skeletonize(cr), lab, ys, xs)
            ok = ~np.isnan(tg[:, 0])
            ys, xs, tg = ys[ok], xs[ok], tg[ok]
            nrm = np.stack([-tg[:, 1], tg[:, 0]], 1)
            cy = ys[:, None] + T[None, :] * nrm[:, 0:1]
            cx = xs[:, None] + T[None, :] * nrm[:, 1:2]
            pr = ndi.map_coordinates(img, [cy.ravel(), cx.ravel()], order=1, mode="nearest").reshape(cy.shape)
            lp = ndi.map_coordinates(cr.astype(float), [cy.ravel(), cx.ravel()], order=1, mode="nearest").reshape(cy.shape)
            src = parse_name(s)[0]
            for prof, lprof in zip(pr, lp):
                search = np.abs(T) <= 3
                j = np.nonzero(search)[0][np.argmin(prof[search])]
                base = np.median(np.concatenate([prof[:6], prof[-6:]]))
                depth = base - prof[j]
                if depth <= 0.05 * base:
                    continue
                half = base - depth / 2
                # walk out from the minimum to the half-depth crossings
                l = j
                while l > 0 and prof[l] < half:
                    l -= 1
                r = j
                while r < len(T) - 1 and prof[r] < half:
                    r += 1
                if l == 0 or r == len(T) - 1:
                    continue
                w = (r - l) * 0.25
                widths.append(w)
                lw = float((lprof >= 0.5).sum() * 0.25)
                label_w.append(lw)
                by_src.setdefault(src, ([], []))
                by_src[src][0].append(w)
                by_src[src][1].append(lw)
    widths, label_w = np.array(widths), np.array(label_w)
    wres = dict(n_points=len(widths), visible_fwhm_percentiles=np.percentile(widths, [25, 50, 75]).tolist(),
                label_width_percentiles=np.percentile(label_w, [25, 50, 75]).tolist(),
                frac_visible_wider_than_label_by_ge1px=float(np.mean(widths - label_w >= 1)),
                by_source={k: dict(n=len(v[0]), visible_median=float(np.median(v[0])), label_median=float(np.median(v[1])))
                           for k, v in sorted(by_src.items())})
    res = dict(verified_pairs=rows, width=wres)
    with open(out / "verify_dups_width.json", "w") as f:
        json.dump(res, f, indent=1)
    for r in rows[:20]:
        print(r)
    print(json.dumps(wres, indent=1))


if __name__ == "__main__":
    main()
