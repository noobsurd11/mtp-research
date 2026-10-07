"""Q6 near-duplicates (DCT perceptual hash + pixel correlation), label fragmentation per image, visible vs label width.

usage: python -I dups_fragments.py <dataset_20211104 dir> <out dir>
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402
from scipy.fft import dctn  # noqa: E402

from common import CRACK, INACTIVE, SPLIT_DIRS, load_mask, parse_name, stems  # noqa: E402

SQ = np.ones((3, 3), bool)


def phash(path: Path) -> tuple[np.ndarray, np.ndarray]:
    im = Image.open(path).convert("L")
    small = np.asarray(im.resize((32, 32), Image.Resampling.LANCZOS), dtype=np.float64)
    d = dctn(small, norm="ortho")[:8, :8]
    h = (d > np.median(d[1:].ravel() if False else d.ravel()[1:])).ravel()
    thumb = np.asarray(im.resize((64, 64), Image.Resampling.BILINEAR), dtype=np.float64).ravel()
    thumb = (thumb - thumb.mean()) / (thumb.std() + 1e-9)
    return h, thumb


def main() -> None:
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    keys, hashes, thumbs = [], [], []
    for split in ("train", "val", "test"):
        for s in stems(root, split):
            h, t = phash(root / SPLIT_DIRS[split][0] / f"{s}.png")
            keys.append((split, s))
            hashes.append(h)
            thumbs.append(t)
    H = np.array(hashes, dtype=np.uint8)
    Tm = np.array(thumbs)
    ham = (H[:, None, :] != H[None, :, :]).sum(-1)
    corr = Tm @ Tm.T / Tm.shape[1]
    n = len(keys)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if ham[i, j] <= 10 or corr[i, j] >= 0.95:
                pairs.append(dict(a=f"{keys[i][0]}/{keys[i][1]}", b=f"{keys[j][0]}/{keys[j][1]}",
                                  ham=int(ham[i, j]), corr=round(float(corr[i, j]), 4),
                                  cross_split=keys[i][0] != keys[j][0]))
    pairs.sort(key=lambda p: (-p["corr"], p["ham"]))
    # nearest neighbour correlation of every val/test image to train
    tr = [i for i, k in enumerate(keys) if k[0] == "train"]
    nn = {}
    for sp in ("val", "test"):
        idx = [i for i, k in enumerate(keys) if k[0] == sp]
        best = corr[np.ix_(idx, tr)].max(1)
        nn[sp] = dict(percentiles=np.percentile(best, [50, 90, 100]).round(4).tolist(),
                      n_ge_0p95=int((best >= 0.95).sum()), n_ge_0p9=int((best >= 0.9).sum()))
    # ---- fragmentation per image ----
    frag = defaultdict(list)
    frag_rows = []
    for split in ("train", "val", "test"):
        for s in stems(root, split):
            m = load_mask(root, split, s)
            cr = m == CRACK
            if not cr.any():
                continue
            lab, k = ndi.label(cr, SQ)
            sizes = ndi.sum(cr, lab, index=np.arange(1, k + 1))
            small_px = float(sizes[sizes <= 10].sum())
            ina_d = ndi.binary_dilation(m == INACTIVE, SQ, iterations=2)
            in_ina = float((cr & ina_d).sum())
            r = dict(split=split, stem=s, src=parse_name(s)[0], crack_px=int(cr.sum()), n_comp=int(k),
                     frac_px_in_comp_le10=small_px / cr.sum(), frac_crack_px_in_or_at_inactive=in_ina / cr.sum())
            frag_rows.append(r)
            frag[split].append(r)
    fsum = {}
    for sp, rows in frag.items():
        fr = np.array([r["frac_px_in_comp_le10"] for r in rows])
        px = np.array([r["crack_px"] for r in rows], float)
        ina = np.array([r["frac_crack_px_in_or_at_inactive"] for r in rows])
        fsum[sp] = dict(n_crack_images=len(rows), n_fragmented_ge30pct=int((fr >= 0.3).sum()),
                        n_fragmented_ge10pct=int((fr >= 0.1).sum()),
                        crack_px_share_in_fragmented_ge30pct_images=float(px[fr >= 0.3].sum() / px.sum()),
                        crack_px_share_in_or_at_inactive=float((ina * px).sum() / px.sum()),
                        fragmented_images=[r["stem"] for r in rows if r["frac_px_in_comp_le10"] >= 0.3])
    # ---- visible width vs label width from the label-centred mean profiles ----
    ac = json.load(open(out / "annotation_consistency.json"))
    T = np.array(ac["profile_T"])
    fwhm = {}
    for k, v in ac["mean_profile_label_centred"].items():
        v = np.array(v)
        base = np.mean(v[np.abs(T) >= 4])
        mn = v.min()
        half = base - (base - mn) / 2
        below = T[v <= half]
        fwhm[k] = dict(depth=float((base - mn) / base), fwhm_px=float(below.max() - below.min()) if len(below) else None,
                       min_at=float(T[np.argmin(v)]))
    res = dict(near_duplicate_pairs=pairs[:60], n_pairs=len(pairs),
               n_cross_split_pairs=sum(p["cross_split"] for p in pairs),
               nn_corr_to_train=nn, fragmentation=fsum, visible_dip_fwhm=fwhm)
    with open(out / "dups_fragments.json", "w") as f:
        json.dump(res, f, indent=1)
    with open(out / "fragmentation_rows.json", "w") as f:
        json.dump(frag_rows, f)
    print("pairs", len(pairs), "cross-split", res["n_cross_split_pairs"])
    for p in pairs[:25]:
        print("  ", p)
    print("nn corr to train", nn)
    for sp, d in fsum.items():
        print(sp, {k: v for k, v in d.items() if k != "fragmented_images"}, d["fragmented_images"][:12])
    for k, v in sorted(fwhm.items()):
        print("fwhm", k, v)


if __name__ == "__main__":
    main()
