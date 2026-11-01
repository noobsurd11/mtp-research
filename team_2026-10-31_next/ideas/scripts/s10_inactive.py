"""s10_inactive (found, 31 Oct 2026): idea 10 S10-inactive (ideas/s10_prereg.md). SAM2.1 Hiera-T inactive masks prompted by the
model vs the model's own inactive masks, against Pratt (masks_escdd) labels on B1's A50 out-of-fold train cells. CPU only.
Stages (each run with CUDA_VISIBLE_DEVICES=""):
  model  (el-fault-detection venv): A50 5-seed mean-softmax argmax; inactive = class 11; prompts = per 8-conn component >= 100 px:
         bounding box + deepest interior point (max EDT). Writes model.npz (packed masks) + prompts.json.
  sam    (venv_sam2): SAM2ImagePredictor per cell; per prompt box + point, multimask, keep the highest predicted-IoU mask; union per cell.
         Writes sam.npz.
  score  (either venv): per-cell IoU and boundary F1 at 2 px for (a) model, (a2) model restricted to its prompted components
         (>= 100 px; judge A1), (b) SAM, (c) a AND b; pooled IoU; paired cell bootstrap vs the better of a / a2.
No test, no E1, no _rf. No training, no checkpoint written.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

assert os.environ.get("CUDA_VISIBLE_DEVICES") == "", "S10 is CPU-only: run with CUDA_VISIBLE_DEVICES=''"
INACT, MINPX = 11, 100
ap = argparse.ArgumentParser()
ap.add_argument("stage", choices=["model", "sam", "score"])
ap.add_argument("--code", default="/home/noob/work/el_f3")
ap.add_argument("--runs", nargs=5)
ap.add_argument("--labeled", default="/home/noob/work/el_f3/data/splits/seed0/labeled_50pct.txt")
ap.add_argument("--ckpt", default="/home/noob/work/weights/sam2.1_hiera_tiny.pt")
ap.add_argument("--cfg", default="configs/sam2.1/sam2.1_hiera_t.yaml")
ap.add_argument("--out", required=True)
ap.add_argument("--threads", type=int, default=8)
ap.add_argument("--boot", type=int, default=2000)
a = ap.parse_args()
OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)
D = Path(a.code) / "data"


def cell_lists():
    tr = [l.strip() for l in open(D / "splits" / "train.txt") if l.strip()]
    lab = {l.strip() for l in open(a.labeled) if l.strip()}
    oof = [s for s in tr if s not in lab]
    val = sorted(l.strip() for l in open(D / "splits" / "val.txt") if l.strip())
    assert len(oof) == 239 and len(val) == 54, (len(oof), len(val))
    return {"oof": oof, "val": val}


def img_u8(stem):
    return np.array(Image.open(D / "labeled" / "images" / f"{stem}.png").convert("L"), np.uint8)


def gt_inact(stem):
    return np.array(Image.open(D / "labeled" / "masks_escdd" / f"{stem}.png")) == INACT


if a.stage == "model":
    import torch
    from scipy import ndimage as ndi
    sys.path.insert(0, a.code)
    from src.models.model_factory import build_model  # noqa: E402
    from src.utils.config import load_config  # noqa: E402
    torch.set_num_threads(a.threads)

    def load(run):  # as calib_dump / b1_audit: final weights, models["model"]
        run = Path(run); cfg = load_config(run / "config_used.yaml")
        st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
        assert int(st.get("step", -1)) == 20000, run
        mc = {k: v for k, v in cfg["model"].items() if k not in ("encoder_init", "decoder_init")}; mc["encoder_weights"] = None
        m = build_model(mc); m.load_state_dict(st["models"]["model"]); m.eval()
        return m
    md5 = {r: hashlib.md5(open(Path(r) / "checkpoints" / "latest.pth", "rb").read()).hexdigest() for r in a.runs}
    ms = [load(r) for r in a.runs]
    C = cell_lists(); masks, prompts, t0 = {}, {}, time.time()
    with torch.no_grad():
        for sp, stems in C.items():
            for s in stems:
                x = torch.from_numpy((img_u8(s).astype(np.float32) / 255.0 - 0.5) / 0.25)[None, None]
                p = sum(torch.softmax(m(x).float(), 1)[0] for m in ms) / len(ms)
                mk = (p.argmax(0) == INACT).numpy()
                masks[s] = np.packbits(mk)
                lab, n = ndi.label(mk, np.ones((3, 3)))
                pr = []
                for i, sl in enumerate(ndi.find_objects(lab), 1):
                    comp = lab == i
                    if comp.sum() < MINPX:
                        continue
                    ys, xs = np.where(comp)
                    dt = ndi.distance_transform_edt(comp); yy, xx = np.unravel_index(int(dt.argmax()), dt.shape)
                    pr.append({"box": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())], "pt": [int(xx), int(yy)], "px": int(comp.sum())})
                prompts[s] = pr
    np.savez_compressed(OUT / "model.npz", **{s: v for s, v in masks.items()})
    json.dump({"runs": a.runs, "md5": md5, "cells": C, "prompts": prompts}, open(OUT / "prompts.json", "w"))
    print(f"model stage done {time.time() - t0:.0f}s; cells {sum(len(v) for v in C.values())}; prompts {sum(len(v) for v in prompts.values())}")

elif a.stage == "sam":
    import torch
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    torch.set_num_threads(a.threads)
    J = json.load(open(OUT / "prompts.json"))
    pred = SAM2ImagePredictor(build_sam2(a.cfg, a.ckpt, device="cpu"))
    out, t0, n = {}, time.time(), 0
    with torch.no_grad():
        for sp, stems in J["cells"].items():
            for s in stems:
                u = np.zeros((512, 512), bool)
                if J["prompts"][s]:
                    pred.set_image(np.stack([img_u8(s)] * 3, -1))
                    for q in J["prompts"][s]:
                        mk, sc, _ = pred.predict(point_coords=np.array([q["pt"]], np.float32), point_labels=np.array([1]),
                                                 box=np.array(q["box"], np.float32), multimask_output=True)
                        u |= mk[int(np.argmax(sc))].astype(bool); n += 1
                out[s] = np.packbits(u)
    np.savez_compressed(OUT / "sam.npz", **out)
    json.dump({"ckpt": a.ckpt, "ckpt_md5": hashlib.md5(open(a.ckpt, "rb").read()).hexdigest(), "cfg": a.cfg, "n_prompts": n,
               "seconds": round(time.time() - t0)}, open(OUT / "sam_meta.json", "w"))
    print(f"sam stage done {time.time() - t0:.0f}s; prompts {n}")

else:
    from scipy import ndimage as ndi
    J = json.load(open(OUT / "prompts.json")); Mz = np.load(OUT / "model.npz"); Sz = np.load(OUT / "sam.npz")
    unpack = lambda z, s: np.unpackbits(z[s])[: 512 * 512].reshape(512, 512).astype(bool)

    def bf1(p, g):
        bp = p & ~ndi.binary_erosion(p); bg = g & ~ndi.binary_erosion(g)
        if not bp.any() and not bg.any():
            return float("nan")
        dg = ndi.distance_transform_edt(~bg) if bg.any() else np.full(g.shape, np.inf)
        dp = ndi.distance_transform_edt(~bp) if bp.any() else np.full(g.shape, np.inf)
        P = float((dg[bp] <= 2).mean()) if bp.any() else 0.0; R = float((dp[bg] <= 2).mean()) if bg.any() else 0.0
        return 2 * P * R / (P + R) if P + R else 0.0
    res = {}
    for sp, stems in J["cells"].items():
        rows = {}
        for s in stems:
            g = gt_inact(s); A = unpack(Mz, s); B = unpack(Sz, s); Cc = A & B
            lab, n = ndi.label(A, np.ones((3, 3)))
            sz = np.bincount(lab.ravel(), minlength=n + 1); keep = np.where(sz >= MINPX)[0]; keep = keep[keep > 0]
            A2 = np.isin(lab, keep)  # judge A1: the model mask restricted to the prompted (>= 100 px) components
            rows[s] = {v: [int((m & g).sum()), int(m.sum()), int(g.sum()), bf1(m, g)] for v, m in (("a", A), ("a2", A2), ("b", B), ("c", Cc))}
        V = ("a", "a2", "b", "c")
        pooled = {v: (lambda t: t[0] / max(t[1] + t[2] - t[0], 1))(np.sum([rows[s][v][:3] for s in stems], 0)) for v in V}
        ref = "a" if pooled["a"] >= pooled["a2"] else "a2"  # judge A1: reference = max(IoU(a), IoU(a2)), fixed on the full set
        st = list(stems); rng = np.random.default_rng(0); boot = {"b": [], "c": []}
        T = {v: np.array([rows[s][v][:3] for s in st]) for v in V}
        iou = lambda t: t[0] / max(t[1] + t[2] - t[0], 1)
        for _ in range(a.boot):
            idx = rng.integers(0, len(st), len(st))
            ir = iou(T[ref][idx].sum(0))
            for v in "bc":
                boot[v].append(iou(T[v][idx].sum(0)) - ir)
        inact_cells = [s for s in st if rows[s]["a"][2] > 0]
        res[sp] = {"n_cells": len(st), "n_gt_inactive_cells": len(inact_cells), "gt_inactive_px": int(T["a"][:, 2].sum()),
                   "pooled_iou": {v: round(float(pooled[v]), 4) for v in V}, "ref": ref,
                   "d_pooled_vs_ref": {v: round(float(pooled[v] - pooled[ref]), 4) for v in "bc"},
                   "boot_lo95": {v: round(float(np.percentile(boot[v], 2.5)), 4) for v in "bc"},
                   "boot_hi95": {v: round(float(np.percentile(boot[v], 97.5)), 4) for v in "bc"},
                   "per_cell_iou_gt_cells": {s: {v: round(rows[s][v][0] / max(rows[s][v][1] + rows[s][v][2] - rows[s][v][0], 1), 4) for v in V} for s in inact_cells},
                   "mean_boundary_f1_gt_cells": {v: round(float(np.nanmean([rows[s][v][3] for s in inact_cells])), 4) if inact_cells else None for v in V},
                   "pred_px_on_cells_without_gt": {v: int(sum(rows[s][v][1] for s in st if rows[s]["a"][2] == 0)) for v in V}}
    o = res["oof"]
    res["rule"] = {v: {"ref": o["ref"], "d_vs_ref>=0.05": o["d_pooled_vs_ref"][v] >= 0.05, "boot_lo>0": o["boot_lo95"][v] > 0,
                       "pass": o["d_pooled_vs_ref"][v] >= 0.05 and o["boot_lo95"][v] > 0} for v in "bc"}
    res["S10_pass"] = any(res["rule"][v]["pass"] for v in "bc")
    json.dump(res, open(OUT / "s10_result.json", "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("rule", "S10_pass")}, indent=1))
