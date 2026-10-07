"""Figures for Q4: crack overlays (24 images), mean normal profiles, unlabelled-line candidates; refined registration.

usage: python -I figures.py <dataset_20211104 dir> <out dir> <figs dir>
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402

from common import CRACK, INACTIVE, RIBBONS, load_image, load_mask, parse_name, stems  # noqa: E402

SQ = np.ones((3, 3), bool)
RNG = np.random.default_rng(1)


def outline(mask: np.ndarray) -> np.ndarray:
    return mask & ~ndi.binary_erosion(mask, SQ, border_value=0)


def overlay_rgb(img: np.ndarray, m: np.ndarray, fill: bool = False) -> np.ndarray:
    g = np.clip(img / 255.0, 0, 1)
    rgb = np.stack([g, g, g], -1)
    cr = m == CRACK
    ina = outline(m == INACTIVE)
    if fill:
        rgb[cr] = [1.0, 0.1, 0.1]
    else:
        rgb[cr] = 0.45 * rgb[cr] + 0.55 * np.array([1.0, 0.1, 0.1])
    rgb[ina] = [1.0, 0.85, 0.0]
    return rgb


def crack_overlays(root: Path, figs: Path) -> list[str]:
    per = defaultdict(list)
    for split in ("train", "val", "test"):
        for s in stems(root, split):
            m = load_mask(root, split, s)
            if (m == CRACK).sum() >= 60:
                per[(split, parse_name(s)[0])].append(s)
    want = {"test": 8, "val": 6, "train": 10}
    chosen = []
    for split, k in want.items():
        keys = sorted(kk for kk in per if kk[0] == split)
        i = 0
        while sum(1 for c in chosen if c[0] == split) < k and any(per[kk] for kk in keys):
            kk = keys[i % len(keys)]
            if per[kk]:
                s = per[kk].pop(RNG.integers(len(per[kk])))
                chosen.append((split, s))
            i += 1
    names = []
    for f in range(4):
        rows = chosen[f * 6:(f + 1) * 6]
        fig, ax = plt.subplots(len(rows), 4, figsize=(16, 4 * len(rows)))
        for r, (split, s) in enumerate(rows):
            img, m = load_image(root, split, s), load_mask(root, split, s)
            cr = m == CRACK
            lab, n = ndi.label(cr, SQ)
            sizes = ndi.sum(cr, lab, index=np.arange(1, n + 1))
            big = int(np.argmax(sizes)) + 1
            ys, xs = np.nonzero(lab == big)
            k = RNG.integers(len(ys))
            cy, cx = int(np.clip(ys[k], 40, 471)), int(np.clip(xs[k], 40, 471))
            crop = (slice(cy - 40, cy + 40), slice(cx - 40, cx + 40))
            ax[r, 0].imshow(img, cmap="gray", vmin=0, vmax=255)
            ax[r, 0].add_patch(plt.Rectangle((cx - 40, cy - 40), 80, 80, fill=False, ec="cyan", lw=1))
            ax[r, 0].set_title(f"{split}/{s}", fontsize=8)
            ax[r, 1].imshow(overlay_rgb(img, m))
            ax[r, 1].set_title("crack (red), inactive outline (yellow)", fontsize=8)
            ax[r, 2].imshow(img[crop], cmap="gray", interpolation="nearest")
            ax[r, 2].set_title("zoom 80x80 raw", fontsize=8)
            zo = overlay_rgb(img[crop], m[crop])
            ax[r, 3].imshow(zo, interpolation="nearest")
            ax[r, 3].set_title("zoom + crack label", fontsize=8)
            for a in ax[r]:
                a.axis("off")
        plt.tight_layout()
        name = f"crack_overlays_{f + 1}.png"
        plt.savefig(figs / name, dpi=60)
        plt.close(fig)
        names.append(name)
    with open(figs / "crack_overlays_index.json", "w") as fh:
        json.dump(chosen, fh)
    return names


def profile_fig(out: Path, figs: Path) -> None:
    res = json.load(open(out / "annotation_consistency.json"))
    T = np.array(res["profile_T"])
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    for k, v in sorted(res["mean_profile_label_centred"].items()):
        ax[0].plot(T, v, label=k, lw=1)
    ax[0].axvline(0, color="k", lw=0.5)
    ax[0].set_xlabel("offset along normal from label skeleton (px)")
    ax[0].set_ylabel("intensity / far-field")
    ax[0].legend(fontsize=6, ncol=2)
    ax[0].set_title("mean intensity profile across labelled cracks")
    # offset histograms are recomputed from summaries only (bars)
    s = res["profile_offsets_all"]
    nul = res["null_random_bg_offsets"]
    xs = ["<=0.5", "<=1", "<=2"]
    ax[1].bar(np.arange(3) - 0.2, [s["abs_offset_le0p5"], s["abs_offset_le1"], s["abs_offset_le2"]], 0.4, label="label skeleton")
    ax[1].bar(np.arange(3) + 0.2, [nul["abs_le0p5"], nul["abs_le1"], nul["abs_le2"]], 0.4, label="random bg points (null)")
    ax[1].set_xticks(range(3), xs)
    ax[1].set_ylabel("fraction of points")
    ax[1].set_title("|offset| of darkest pixel from label (search ±4 px)")
    ax[1].legend()
    plt.tight_layout()
    plt.savefig(figs / "crack_normal_profiles.png", dpi=80)
    plt.close(fig)


def candidate_fig(root: Path, out: Path, figs: Path) -> None:
    cands = [c for c in json.load(open(out / "line_candidates.json")) if not c["axis_aligned"]][:30]
    fig, ax = plt.subplots(5, 12, figsize=(24, 10.5))
    for i, c in enumerate(cands):
        img, m = load_image(root, c["split"], c["stem"]), load_mask(root, c["split"], c["stem"])
        y0, y1, x0, x1 = c["bbox"]
        cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
        h = max(y1 - y0, x1 - x0) // 2 + 12
        h = max(h, 30)
        sl = (slice(max(0, cy - h), min(512, cy + h)), slice(max(0, cx - h), min(512, cx + h)))
        a = ax[(i // 6), (i % 6) * 2]
        b = ax[(i // 6), (i % 6) * 2 + 1]
        a.imshow(img[sl], cmap="gray", interpolation="nearest")
        a.set_title(f"#{i} {c['split']}/{c['stem'][:22]}", fontsize=6)
        rgb = overlay_rgb(img[sl], m[sl])
        box = np.zeros(img.shape, bool)
        box[y0:y1, x0:x1] = True
        rgb[outline(box)[sl]] = [0.0, 1.0, 1.0]
        b.imshow(rgb, interpolation="nearest")
        b.set_title(f"len {c['length']} ang {c['angle']:.0f}", fontsize=6)
        a.axis("off")
        b.axis("off")
    for j in range(len(cands), 30):
        ax[(j // 6), (j % 6) * 2].axis("off")
        ax[(j // 6), (j % 6) * 2 + 1].axis("off")
    plt.tight_layout()
    plt.savefig(figs / "unlabelled_line_candidates.png", dpi=60)
    plt.close(fig)


def refined_registration(root: Path, out: Path) -> dict:
    """Ribbons are vertical: optimal horizontal shift only, separately for the left and right image halves."""
    rows = []
    for split in ("train", "val", "test"):
        for s in stems(root, split):
            m = load_mask(root, split, s)
            rb = m == RIBBONS
            if rb.sum() < 200:
                continue
            img = ndi.gaussian_filter(load_image(root, split, s), 0.7)
            # keep only vertical ribbon pixels (vertical run >= 7 px)
            vert = ndi.binary_opening(rb, np.ones((7, 1), bool))
            res = {}
            for half, xs_ in (("left", slice(0, 256)), ("right", slice(256, 512))):
                mk = np.zeros_like(vert)
                mk[:, xs_] = vert[:, xs_]
                if mk.sum() < 100:
                    continue
                ys, xs = np.nonzero(mk)
                vals = []
                for dx in np.arange(-3, 3.01, 0.25):
                    vals.append(ndi.map_coordinates(img, [ys.astype(float), xs + dx], order=1, mode="nearest").mean())
                d = np.arange(-3, 3.01, 0.25)[int(np.argmin(vals))]
                res[half] = float(d)
            rows.append(dict(split=split, stem=s, src=parse_name(s)[0], **res))
    out_d = {}
    for key in ("left", "right"):
        v = np.array([r[key] for r in rows if key in r])
        out_d[key] = dict(n=len(v), mean=float(v.mean()), median=float(np.median(v)),
                          frac_abs_le_0p25=float(np.mean(np.abs(v) <= 0.25)), frac_abs_le_0p5=float(np.mean(np.abs(v) <= 0.5)),
                          frac_abs_ge_1=float(np.mean(np.abs(v) >= 1)))
    by_src = defaultdict(list)
    for r in rows:
        for key in ("left", "right"):
            if key in r:
                by_src[r["src"]].append(r[key])
    out_d["by_source_mean"] = {k: float(np.mean(v)) for k, v in sorted(by_src.items())}
    both = [(r["left"], r["right"]) for r in rows if "left" in r and "right" in r]
    out_d["left_minus_right_mean"] = float(np.mean([a - b for a, b in both])) if both else None
    with open(out / "ribbon_registration.json", "w") as f:
        json.dump(dict(summary=out_d, rows=rows), f)
    return out_d


def main() -> None:
    root, out, figs = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    figs.mkdir(parents=True, exist_ok=True)
    print(crack_overlays(root, figs))
    profile_fig(out, figs)
    candidate_fig(root, out, figs)
    print(json.dumps(refined_registration(root, out), indent=1))


if __name__ == "__main__":
    main()
