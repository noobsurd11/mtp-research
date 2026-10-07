"""Q2 crack geometry + Q3 IoU ceiling under 1-2 px jitter + Q5 inactive regions.

usage: python -I geometry_ceiling.py <dataset_20211104 dir> <out dir>
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402
from skimage.morphology import skeletonize  # noqa: E402

from common import BG, CRACK, CRACK_RBN_EDGE, INACTIVE, load_image, load_mask, parse_name, stems  # noqa: E402

SQ = np.ones((3, 3), bool)
CROSS = ndi.generate_binary_structure(2, 1)


def shift(a: np.ndarray, dy: int, dx: int) -> np.ndarray:
    out = np.zeros_like(a)
    H, W = a.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = a[ys, xs]
    return out


PERTURB = {
    "shift1_mean4": [(1, 0), (-1, 0), (0, 1), (0, -1)],
    "shift1_diag": [(1, 1)],
    "shift2_mean4": [(2, 0), (-2, 0), (0, 2), (0, -2)],
}


def perturbations(gt: np.ndarray) -> dict[str, list[np.ndarray]]:
    out = {k: [shift(gt, dy, dx) for dy, dx in v] for k, v in PERTURB.items()}
    out["dilate1_sq"] = [ndi.binary_dilation(gt, SQ)]
    out["dilate1_cross"] = [ndi.binary_dilation(gt, CROSS)]
    out["dilate2_sq"] = [ndi.binary_dilation(gt, SQ, iterations=2)]
    out["erode1_cross"] = [ndi.binary_erosion(gt, CROSS)]
    return out


def component_stats(mask: np.ndarray, img: np.ndarray) -> list[dict]:
    lab, n = ndi.label(mask, SQ)
    if n == 0:
        return []
    edt = ndi.distance_transform_edt(mask)
    sk = skeletonize(mask)
    rows = []
    objs = ndi.find_objects(lab)
    for i, sl in enumerate(objs, start=1):
        comp = lab[sl] == i
        skc = sk[sl] & comp
        area = int(comp.sum())
        L = int(skc.sum())
        if L == 0:
            L = 1
        d = edt[sl][skc] if skc.any() else edt[sl][comp]
        local_w = 2 * d - 1
        ys, xs = np.nonzero(skc if skc.sum() >= 2 else comp)
        if len(ys) >= 2:
            cov = np.cov(np.vstack([xs, ys]))
            evals, evecs = np.linalg.eigh(cov)
            v = evecs[:, -1]
            ang = float(np.degrees(np.arctan2(v[1], v[0])) % 180)
            elong = float(np.sqrt(evals[-1] / max(evals[0], 1e-6)))
        else:
            ang, elong = float("nan"), float("nan")
        rows.append(dict(area=area, skel_len=L, width_area_over_len=area / L,
                         width_edt_median=float(np.median(local_w)), width_edt_max=float(local_w.max()),
                         frac_skel_w_le1=float(np.mean(local_w <= 1)), frac_skel_w_le3=float(np.mean(local_w <= 3)),
                         angle=ang, elong=elong))
    return rows


def main() -> None:
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    res: dict = {}
    for split in ("train", "val", "test"):
        inter = defaultdict(float)
        union = defaultdict(float)
        per_img_iou = defaultdict(list)
        comps, comps_rbn, per_image = [], [], []
        inact_comps = []
        for s in stems(root, split):
            m = load_mask(root, split, s)
            src, _ = parse_name(s)
            for cls, tag in ((CRACK, "crack"), (INACTIVE, "inactive")):
                gt = m == cls
                if not gt.any():
                    continue
                for k, preds in perturbations(gt).items():
                    for p in preds:
                        i_, u_ = float((gt & p).sum()), float((gt | p).sum())
                        inter[(tag, k)] += i_ / len(preds)
                        union[(tag, k)] += u_ / len(preds)
                        per_img_iou[(tag, k)].append(i_ / u_ / len(preds) if u_ else np.nan)
            crack = m == CRACK
            if crack.any():
                img = load_image(root, split, s)
                cs = component_stats(crack, img)
                for c in cs:
                    c["src"], c["stem"] = src, s
                comps += cs
                skel = skeletonize(crack)
                edt = ndi.distance_transform_edt(crack)
                lw = 2 * edt[skel] - 1
                per_image.append(dict(stem=s, src=src, n_comp=len(cs), crack_px=int(crack.sum()),
                                      skel_px=int(skel.sum()), w_median=float(np.median(lw)) if lw.size else np.nan))
            rbn = m == CRACK_RBN_EDGE
            if rbn.any():
                comps_rbn += component_stats(rbn, None)
            ina = m == INACTIVE
            if ina.any():
                img = load_image(root, split, s)
                lab, n = ndi.label(ina, SQ)
                cell = np.isin(m, [BG, 1, 2])  # cell surface + spacing classes, used for the ring
                crack_d = ndi.binary_dilation(crack, SQ, iterations=3) if crack.any() else np.zeros_like(crack)
                for i in range(1, n + 1):
                    comp = lab == i
                    ring = ndi.binary_dilation(comp, SQ, iterations=15) & ~ndi.binary_dilation(comp, SQ, iterations=5)
                    ring &= (m == BG)
                    crack_inside = float((crack & ndi.binary_dilation(comp, SQ, iterations=1)).sum())
                    inact_comps.append(dict(
                        stem=s, area=int(comp.sum()), touches_crack=bool((comp & crack_d).any()),
                        crack_px_inside_or_adjacent=crack_inside,
                        mean_in=float(img[comp].mean()), mean_ring=float(img[ring].mean()) if ring.any() else np.nan,
                        ratio=float(img[comp].mean() / img[ring].mean()) if ring.any() and img[ring].mean() > 0 else np.nan))
                del cell
        ceil = {}
        for (tag, k), v in inter.items():
            ceil.setdefault(tag, {})[k] = dict(dataset_iou=v / union[(tag, k)],
                                                per_image_median=float(np.nanmedian(per_img_iou[(tag, k)])),
                                                per_image_mean=float(np.nanmean(per_img_iou[(tag, k)])))
        A = lambda key, rows=comps: np.array([r[key] for r in rows], float)  # noqa: E731
        area = A("area")
        geo = {}
        if comps:
            wts = area / area.sum()
            geo = dict(
                n_components=len(comps), n_images=len(per_image),
                comps_per_image_median=float(np.median([p["n_comp"] for p in per_image])),
                comp_area_median=float(np.median(area)), comp_area_p90=float(np.percentile(area, 90)),
                comp_len_median=float(np.median(A("skel_len"))), comp_len_p90=float(np.percentile(A("skel_len"), 90)),
                width_area_over_len_median=float(np.median(A("width_area_over_len"))),
                width_area_over_len_pixelweighted=float(np.sum(wts * A("width_area_over_len"))),
                width_edt_median_of_medians=float(np.median(A("width_edt_median"))),
                frac_components_tiny_lt20px=float(np.mean(area < 20)),
                frac_crack_pixels_in_tiny_lt20px=float(area[area < 20].sum() / area.sum()),
                orientation_hist_deg=np.histogram(A("angle")[~np.isnan(A("angle"))], bins=[0, 10, 35, 55, 80, 100, 125, 145, 170, 180])[0].tolist(),
                image_skel_width_median_dist=np.percentile([p["w_median"] for p in per_image], [10, 25, 50, 75, 90]).tolist(),
            )
            by_src = defaultdict(list)
            for c in comps:
                by_src[c["src"]].append(c)
            geo["by_source"] = {k: dict(n=len(v), width_area_over_len_median=float(np.median([c["width_area_over_len"] for c in v])),
                                        comp_len_median=float(np.median([c["skel_len"] for c in v])))
                                for k, v in sorted(by_src.items())}
        res[split] = dict(iou_ceiling=ceil, crack_geometry=geo,
                          crack_rbn_edge=dict(n_components=len(comps_rbn),
                                              area=[c["area"] for c in comps_rbn],
                                              width=[round(c["width_area_over_len"], 2) for c in comps_rbn]),
                          inactive=dict(
                              n_components=len(inact_comps),
                              area_percentiles=np.percentile([c["area"] for c in inact_comps], [10, 50, 90]).tolist() if inact_comps else [],
                              frac_touching_crack=float(np.mean([c["touches_crack"] for c in inact_comps])) if inact_comps else np.nan,
                              intensity_ratio_in_over_ring_percentiles=np.nanpercentile([c["ratio"] for c in inact_comps], [10, 50, 90]).tolist() if inact_comps else [],
                              frac_area_with_ratio_gt_0p8=float(np.nansum([c["area"] for c in inact_comps if c["ratio"] > 0.8]) / max(1, sum(c["area"] for c in inact_comps)))))
        with open(out / f"components_{split}.json", "w") as f:
            json.dump(dict(cracks=comps, inactive=inact_comps, per_image=per_image), f)
    with open(out / "geometry_ceiling.json", "w") as f:
        json.dump(res, f, indent=1)
    for split, d in res.items():
        print(f"\n== {split}")
        for tag, kk in d["iou_ceiling"].items():
            print(f"  IoU ceiling {tag}: " + "  ".join(f"{k} {v['dataset_iou']:.3f} (img-med {v['per_image_median']:.3f})" for k, v in kk.items()))
        g = d["crack_geometry"]
        print("  crack geometry:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in g.items() if k != "by_source"})
        print("  by source:", g.get("by_source"))
        print("  crack_rbn_edge:", d["crack_rbn_edge"])
        print("  inactive:", d["inactive"])


if __name__ == "__main__":
    main()
