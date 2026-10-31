"""B2 v2 (coach final rule 30 Oct): dark px exclude consensus classes 1-9, 21, 22, dead_cell 17 and inactive 11; a component is
dropped if it lies within 6 px of the consensus-structural / frame mask (classes 1-9, 21, 22: inter-cell gaps, frame edges);
kept only if thin (minor-axis sd sqrt(l2) <= 2.5 px) and elongated (> 10); >= 20 px. --halfonly: the 986 half-cells.
B2 mining, step 1 (coach, 30 Oct; no labels, no training): per-cell proposer features, CPU, resumable (jsonl).
Models: 5 run dirs, final weights (step 20,000 asserted), mean softmax, fp32, 512 native, no TTA.
Per cell:
  a      predicted crack px (mean p_crack > 0.5)
  b_px   largest 8-connected predicted crack component, px
  b_len  its length: equivalent-ellipse major axis 4*sqrt(lambda1) of the pixel covariance (runner's stand-in for skeleton
         length: no skimage on gaint; disclosed)
  c      elongated dark streak px: 8-connected components (>= 20 px) of {grey < median - 20 GL, and the consensus class is
         not a structural 'feature' class (1-9, 21, 22: spacing, ribbons, border, text, padding, clamp, busbars, frame,
         jbox; runner's addition so busbars / gaps / ribbons do not dominate)} with elongation sqrt(l1 / (l2 + 1/12)) > 10;
         the median is over px whose consensus is not padding / frame / border (7, 21, 5)
Modes: --pool (the pool part of mim_pool_v11, half-cut flag from the unlabelled inventory) or --cells LIST --img-dir DIR
(train validation with out-of-fold models; positives = raw E-SCDD scuff 25 present).
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from scipy import ndimage

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--runs", nargs=5, required=True)
ap.add_argument("--out", required=True, help="jsonl (appended; done stems skipped)")
ap.add_argument("--pool", action="store_true")
ap.add_argument("--cells", help="stem list (validation mode)")
ap.add_argument("--img-dir")
ap.add_argument("--threads", type=int, default=20)
ap.add_argument("--halfonly", action="store_true")
ap.add_argument("--max-minor-sd", type=float, default=2.5)
ap.add_argument("--near", type=int, default=6)
a = ap.parse_args()
sys.path.insert(0, a.code)
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

torch.set_num_threads(a.threads)
D = Path(a.code) / "data"
S8 = np.ones((3, 3), bool)
STRUCT = np.array([c in (1, 2, 3, 4, 5, 6, 7, 8, 9, 21, 22, 17, 11) for c in range(24)])  # v2: + dead_cell 17, inactive 11
GEOM = np.array([c in (1, 2, 3, 4, 5, 6, 7, 8, 9, 21, 22) for c in range(24)])  # v2: structural / frame mask for the 6 px rule
DISKN = (lambda r: (lambda y, x: (x * x + y * y) <= r * r)(*np.ogrid[-r:r + 1, -r:r + 1]))
NOMED = np.array([c in (5, 7, 21) for c in range(24)])
RAW = Path("/home/noob/work/el-fault-detection/data/escdd_masks/train")

if a.pool:
    inv = json.load(open("/home/noob/work/sa-unetpp-ssl-el/data/unlabeled/_inventory.json"))
    half = {Path(e["name"]).stem for e in inv if "half" in e.get("rel", "").lower()}
    rels = [r.strip() for r in open("/home/noob/work/el_f1/reports/f1/mim_pool_v11.txt") if r.strip().startswith("unlabeled/")]
    cells = [(Path(r).stem, D / r) for r in rels]
    if a.halfonly:
        cells = [c for c in cells if c[0] in half]
        assert len(cells) == 986, len(cells)
else:
    half = set()
    cells = [(s.strip(), Path(a.img_dir) / f"{s.strip()}.png") for s in open(a.cells) if s.strip()]
out = Path(a.out); done = set()
if out.exists():
    done = {json.loads(l)["stem"] for l in open(out) if l.strip()}
models = []
for r in a.runs:
    r = Path(r); st = torch.load(r / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(st["step"]) == 20000, (r, st["step"])
    mc = {k: v for k, v in load_config(r / "config_used.yaml")["model"].items() if k not in ("encoder_init", "decoder_init")}
    mc["encoder_weights"] = None
    m = build_model(mc); m.load_state_dict(st["models"]["model"]); m.eval(); models.append(m)
todo = [c for c in cells if c[0] not in done]
print(f"{len(cells)} cells, {len(done)} done, {len(todo)} to do; half-cut in set: {sum(c[0] in half for c in cells)}", flush=True)


def moments(ys, xs):
    cy, cx = ys.mean(), xs.mean()
    cov = np.cov(np.stack([ys - cy, xs - cx])) if len(ys) > 1 else np.zeros((2, 2))
    l2, l1 = np.linalg.eigvalsh(cov)
    return max(l1, 0.0), max(l2, 0.0)


t0 = time.time()
with open(out, "a") as fo:
    for i, (stem, p) in enumerate(todo):
        g = np.array(Image.open(p).convert("L"))
        xt = torch.from_numpy((g.astype(np.float32) / 255.0 - 0.5) / 0.25)[None, None]
        with torch.no_grad():
            pm = torch.stack([torch.softmax(m(xt).float(), 1)[0] for m in models]).mean(0).numpy()
        cons = pm.argmax(0); pc = pm[14] > 0.5
        lb, n = ndimage.label(pc, S8)
        b_px = b_len = 0
        if n:
            sz = np.bincount(lb.ravel())[1:]; k = int(sz.argmax()) + 1; b_px = int(sz[k - 1])
            ys, xs = np.nonzero(lb == k); l1, _ = moments(ys.astype(float), xs.astype(float)); b_len = float(4 * np.sqrt(l1))
        med = float(np.median(g[~NOMED[cons]])) if (~NOMED[cons]).any() else float(np.median(g))
        dark = (g < med - 20) & ~STRUCT[cons]
        near = ndimage.binary_dilation(GEOM[cons], DISKN(a.near))   # v2: within 6 px of gaps / frame
        lb2, n2 = ndimage.label(dark, S8)
        c = nc = 0
        if n2:
            objs = ndimage.find_objects(lb2)
            for j, sl in enumerate(objs, 1):
                cm = lb2[sl] == j; ys, xs = np.nonzero(cm)
                if len(ys) < 20 or near[sl][cm].any():                        # v2: drop components within 6 px of gaps / frame
                    continue
                l1, l2 = moments(ys.astype(float), xs.astype(float))
                if np.sqrt(l1 / (l2 + 1 / 12)) > 10 and np.sqrt(l2) <= a.max_minor_sd:   # v2: thin (minor-axis sd <= 2.5 px)
                    c += len(ys); nc += 1
        rec = {"stem": stem, "source": stem.split("_")[0], "module": "_".join(stem.split("_")[:2]), "halfcut": stem in half,
               "a": int(pc.sum()), "b_px": b_px, "b_len": round(b_len, 1), "c": int(c), "c_comps": nc, "median": med}
        if not a.pool:
            rp = RAW / f"{stem}.png"
            rec["scuff_px"] = int((np.array(Image.open(rp)) == 25).sum()) if rp.exists() else -1
        fo.write(json.dumps(rec) + "\n"); fo.flush()
        if (i + 1) % 200 == 0:
            el = time.time() - t0
            print(f"  {i + 1}/{len(todo)} cells, {el:.0f} s, eta {el / (i + 1) * (len(todo) - i - 1) / 60:.0f} min", flush=True)
print(f"done {time.time() - t0:.0f} s")
