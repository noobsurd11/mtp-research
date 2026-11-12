"""Montage of cellreg overlays for visual QA (pick1 Amendment 4). usage: python -I overlay_montage.py <run_dir> <modality el|ir> <out.png> [cols]
IR overlays are cropped to the registered grid +- 1 cell and upscaled; EL overlays cropped to the grid +- 0.3 cell."""
import glob, json, os, sys
from PIL import Image, ImageDraw
d, mod, out = sys.argv[1:4]; cols = int(sys.argv[4]) if len(sys.argv) > 4 else 3
tiles = []
for f in sorted(glob.glob(os.path.join(d, f"*_{mod}_overlay.png"))):
    name = os.path.basename(f).replace(f"_{mod}_overlay.png", "")
    reg = json.load(open(os.path.join(d, name + "_reg.json")))
    q = reg["modalities"][mod]["qa"]; meta = reg["modalities"][mod]["meta"]
    im = Image.open(f).convert("RGB")
    H, W = meta["shape"][:2]; sx, sy = im.size[0] / W, im.size[1] / H
    xs = [p[0] for p in q["grid_corners"]]; ys = [p[1] for p in q["grid_corners"]]
    pad = q["cell_side_px"] * (1.0 if mod == "ir" else 0.3)
    box = (max(0, (min(xs) - pad) * sx), max(0, (min(ys) - pad) * sy), min(im.size[0], (max(xs) + pad) * sx), min(im.size[1], (max(ys) + pad) * sy))
    c = im.crop(tuple(int(v) for v in box))
    tw = 900
    c = c.resize((tw, max(1, int(c.size[1] * tw / c.size[0]))), Image.NEAREST if mod == "ir" else Image.BILINEAR)
    lab = Image.new("RGB", (tw, 28), "white"); ImageDraw.Draw(lab).text((5, 6), f"{name}  {mod}  rms {q['res_rms_pct_cell']:.2f}%  fallback {q['lines_fallback']}", fill="black")
    t = Image.new("RGB", (tw, c.size[1] + 28), "white"); t.paste(lab, (0, 0)); t.paste(c, (0, 28)); tiles.append(t)
rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
Wt = cols * 900; Ht = sum(max(t.size[1] for t in r) for r in rows)
M = Image.new("RGB", (Wt, Ht), "white"); y = 0
for r in rows:
    for k, t in enumerate(r): M.paste(t, (k * 900, y))
    y += max(t.size[1] for t in r)
M.save(out); print(out, M.size, len(tiles))
