"""QA overlays with 1 px full grids (pick1 v2 QA criterion 6). usage: python -I qa_overlay.py <run_dir> <out_dir>
IR upscaled x8 (nearest); EL resized to ~1800 px wide; grid = homography of the 4 grid_corners applied to a uniform canonical grid."""
import glob, json, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cellreg
d, od = sys.argv[1:3]; os.makedirs(od, exist_ok=True)
def homog(src, dst):
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y, -u], [0, 0, 0, x, y, 1, -v * x, -v * y, -v]]
    _, _, Vt = np.linalg.svd(np.array(A, float)); return Vt[-1].reshape(3, 3)
def app(H, p):
    q = H @ np.array([p[0], p[1], 1.0]); return q[:2] / q[2]
for f in sorted(glob.glob(os.path.join(d, "*_reg.json"))):
    R = json.load(open(f))
    for mod in ("el", "ir"):
        M = R["modalities"][mod]; q = M["qa"]
        img = cellreg.read_nef_preview(M["path"]) if M["path"].upper().endswith(".NEF") else cellreg.read_matrix_txt(M["path"])
        img = np.asarray(img[0] if isinstance(img, tuple) else img, float)
        G = np.array(q["grid_corners"], float)
        gw = np.linalg.norm(G[1] - G[0]); gh = np.linalg.norm(G[3] - G[0])
        nr, nc = q["rows"], q["cols"]
        nx, ny = (max(nr, nc), min(nr, nc)) if gw >= gh else (min(nr, nc), max(nr, nc))
        H = homog([(0, 0), (nx, 0), (nx, ny), (0, ny)], G)
        lo, hi = np.nanpercentile(img, [1, 99.5]); g8 = np.clip((img - lo) / (hi - lo + 1e-9) * 255, 0, 255)
        g8 = np.nan_to_num(g8).astype(np.uint8)
        pad = 1.0
        xs, ys = G[:, 0], G[:, 1]; cs = max(gw / nx, gh / ny)
        x0, y0 = int(max(0, xs.min() - pad * cs)), int(max(0, ys.min() - pad * cs))
        x1, y1 = int(min(img.shape[1], xs.max() + pad * cs)), int(min(img.shape[0], ys.max() + pad * cs))
        crop = Image.fromarray(g8[y0:y1, x0:x1]).convert("RGB")
        k = 8.0 if mod == "ir" else 1800.0 / crop.size[0]
        crop = crop.resize((int(crop.size[0] * k), int(crop.size[1] * k)), Image.NEAREST if mod == "ir" else Image.BILINEAR)
        dr = ImageDraw.Draw(crop)
        sc = lambda p: ((p[0] - x0) * k, (p[1] - y0) * k)
        for i in range(ny + 1):
            dr.line([sc(app(H, (0, i))), sc(app(H, (nx, i)))], fill=(255, 0, 0), width=1)
        for j in range(nx + 1):
            dr.line([sc(app(H, (j, 0))), sc(app(H, (j, ny)))], fill=(255, 0, 0), width=1)
        Q = np.array(q["quad"], float)
        dr.line([sc(p) for p in list(Q) + [Q[0]]], fill=(0, 200, 255), width=1)
        crop.save(os.path.join(od, f"{R['module']}_{mod}_qa.png"))
print(od)
