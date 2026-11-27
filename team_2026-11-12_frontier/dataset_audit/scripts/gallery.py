"""Local gallery (never published): sheets of 4 candidates, one row each: full cell with the box | zoom | zoom + v1.1 label |
zoom + 25-model consensus. Colours: label crack red, label inactive blue, ignore grey; consensus crack (>= 13 of 25) yellow,
consensus inactive cyan; candidate outline magenta. Selection fixed in PLAN.md: the largest candidates per type
(MC 10, SC 8, MI 5, SI 7 = 30) and the 10 lowest-softmin cells (whole cell). Writes out/gallery/sheet_XX.png + index.tsv."""
from __future__ import annotations

import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402

import common as C  # noqa: E402

TILE = 256
PER_TYPE = {"MC": 10, "SC": 8, "MI": 5, "SI": 7}


def overlay(gr, layers):
    rgb = np.stack([gr] * 3, -1).astype(np.float32)
    for m, col, a in layers:
        rgb[m] = (1 - a) * rgb[m] + a * np.array(col, np.float32)
    return rgb.clip(0, 255).astype(np.uint8)


def outline(m):
    return m & ~ndi.binary_erosion(m, np.ones((3, 3), bool))


def row(stem, bbox, title, pool):
    C.guard(stem, pool)
    gr = C.grey(stem)
    gt = C.mask_v11(stem)
    z = np.load(C.CACHE / "cons" / f"{stem}.npz")
    vc, vi, ign = z["vc"], z["vi"], z["ign"]
    if bbox is None:
        y0, x0, y1, x1 = 0, 0, 511, 511
    else:
        y0, x0, y1, x1 = bbox
        cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
        h = max(y1 - y0 + 24, x1 - x0 + 24, 72) // 2
        y0, y1 = max(cy - h, 0), min(cy + h, 511)
        x0, x1 = max(cx - h, 0), min(cx + h, 511)
    cand = outline(ign)
    full = overlay(gr, [(cand, (255, 0, 255), 1.0)])
    fi = Image.fromarray(full).resize((TILE, TILE), Image.BILINEAR)
    dr = ImageDraw.Draw(fi)
    s = TILE / 512
    dr.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], outline=(0, 255, 0))
    sl = (slice(y0, y1 + 1), slice(x0, x1 + 1))
    zg = gr[sl]
    lab = overlay(zg, [(gt[sl] == C.CRACK, (255, 0, 0), 0.6), (gt[sl] == C.INACT, (0, 80, 255), 0.4),
                       (gt[sl] == C.IGN, (128, 128, 128), 0.6), (cand[sl], (255, 0, 255), 1.0)])
    con = overlay(zg, [(vc[sl] >= 13, (255, 230, 0), 0.6), (vi[sl] >= 13, (0, 230, 230), 0.4), (cand[sl], (255, 0, 255), 1.0)])
    tiles = [fi] + [Image.fromarray(a).resize((TILE, TILE), Image.NEAREST) for a in (np.stack([zg] * 3, -1), lab, con)]
    r = Image.new("RGB", (4 * TILE + 30, TILE + 18), (20, 20, 20))
    for i, t in enumerate(tiles):
        r.paste(t, (i * (TILE + 10), 18))
    ImageDraw.Draw(r).text((4, 3), title, fill=(255, 255, 255))
    return r


def main():
    d = pickle.load(open(C.OUT / "pass_records.pkl", "rb"))
    cells = d["cells"]
    pool = set(C.pool_stems())
    sel = []
    for t, n in PER_TYPE.items():
        r = sorted([(s, c) for s in cells for c in cells[s]["cands"] if c["type"] == t], key=lambda x: -x[1]["px"])[:n]
        sel += [(s, c["bbox"], f"{t} {c['kind']} {s} px {c['px']} votes {c['meanV']:.1f}/25 z {c['z']:.2f} repl {int(c['repl'])}")
                for s, c in r]
    low = sorted(cells, key=lambda s: min(cells[s]["softmin_c"], cells[s]["softmin_i"]))[:10]
    sel += [(s, None, f"LOWSOFTMIN {s} crack {cells[s]['softmin_c']:.3f} inact {cells[s]['softmin_i']:.3f}") for s in low]
    out = C.OUT / "gallery"
    os.makedirs(out, exist_ok=True)
    with open(out / "index.tsv", "w") as f:
        f.write("sheet\trow\tstem\tbbox\ttitle\n")
        for k in range(0, len(sel), 4):
            rows = [row(s, b, t, pool) for s, b, t in sel[k:k + 4]]
            sh = Image.new("RGB", (rows[0].width, sum(r.height for r in rows)), (0, 0, 0))
            y = 0
            for r in rows:
                sh.paste(r, (0, y)); y += r.height
            name = f"sheet_{k // 4:02d}.png"
            sh.save(out / name)
            for i, (s, b, t) in enumerate(sel[k:k + 4]):
                f.write(f"{name}\t{i}\t{s}\t{b}\t{t}\n")
    print(len(sel), "rows")


if __name__ == "__main__":
    main()
