"""Track M, M0 baseline audit: read-only inference on existing checkpoints, all 24 classes.

Per run (final weights, latest.pth; teacher for Mean Teacher runs) and per cell set (val 54, test 50, ext 106):
  - 24x24 confusion matrix per cell (rows GT, cols prediction), argmax, bf16 autocast as the P-series re-scorer;
  - crack relaxed counts at 2 px per cell;
  - crack and inactive connected components (8-conn) of GT and prediction, with their hit counts.
On val only, also dihedral-8 TTA (mean softmax), and the val log-probabilities are saved (fp16) for val-only tuning.
Test and ext get plain argmax only: no tuned variant is evaluated on them here.

Usage (cv02): python m0_audit.py --code /tmp/noob_el/el_p13 --out <dir> --runs <run dir> ...
"""
from __future__ import annotations

import argparse, json, os, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--ext", default="/tmp/noob_el/ext117")
ap.add_argument("--runs", nargs="+", required=True)
ap.add_argument("--no-logits", action="store_true")
ap.add_argument("--sets", nargs="+", default=["val", "test", "ext"], help="cell sets to score (R3 pilots: val only)")
a = ap.parse_args()
CODE = Path(a.code).resolve()
sys.path.insert(0, str(CODE))
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np  # noqa: E402
import torch  # noqa: E402
from PIL import Image  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

NC, CRACK, INACT = 24, 14, 11
DEV = torch.device("cuda")
DATA = CODE / "data"
S8 = np.ones((3, 3), bool)


def comps(gt_m: np.ndarray, pr_m: np.ndarray, near_pr: np.ndarray | None, near_gt: np.ndarray | None):
    """GT components: [size, hit] where hit = px of the component covered (by pred, or within 2 px of pred if near_pr).
    Pred components: [size, hit] with hit = px overlapping GT (or within 2 px of GT if near_gt)."""
    out = {}
    lg, ng = ndi.label(gt_m, S8)
    cov = near_pr if near_pr is not None else pr_m
    if ng:
        sz = np.bincount(lg.ravel(), minlength=ng + 1)[1:]
        ht = np.bincount(lg[cov].ravel(), minlength=ng + 1)[1:]
        out["gt"] = np.stack([sz, ht], 1).tolist()
    else:
        out["gt"] = []
    lp, npc = ndi.label(pr_m, S8)
    cov = near_gt if near_gt is not None else gt_m
    if npc:
        sz = np.bincount(lp.ravel(), minlength=npc + 1)[1:]
        ht = np.bincount(lp[cov].ravel(), minlength=npc + 1)[1:]
        out["pr"] = np.stack([sz, ht], 1).tolist()
    else:
        out["pr"] = []
    return out


BANDS = [0, 0.001, 0.1, 0.5, 0.95, 1.0001]


def cell_stats(pred: np.ndarray, gt: np.ndarray, keep: np.ndarray | None, pc: np.ndarray | None = None) -> dict:
    k = np.ones_like(gt, bool) if keep is None else keep
    assert gt[k].max() < NC and pred.max() < NC, "label id out of range"
    conf = np.bincount(gt[k].astype(np.int64) * NC + pred[k], minlength=NC * NC)
    g, p = (gt == CRACK) & k, (pred == CRACK) & k
    dg = ndi.distance_transform_edt(~g) if g.any() else np.full(g.shape, np.inf)
    dp = ndi.distance_transform_edt(~p) if p.any() else np.full(g.shape, np.inf)
    rel = [int((dg[p] <= 2).sum()), int(p.sum()), int((dp[g] <= 2).sum()), int(g.sum())]
    o = {"conf": conf.tolist(), "crack_rel2": rel,
         "crack_cc": comps(g, p, (dp <= 2) & k, (dg <= 2) & k)}
    gi, pi = (gt == INACT) & k, (pred == INACT) & k
    o["inact_cc"] = comps(gi, pi, None, None)
    if pc is not None:  # p(crack) bands on GT crack px and on GT non-crack px
        o["crack_pband_gt"] = np.histogram(pc[g], BANDS)[0].tolist()
        o["crack_pband_neg"] = np.histogram(pc[k & ~g], BANDS)[0].tolist()
        b = np.clip((pc * 1000).astype(int), 0, 999)  # 1,000-bin histograms as the P-series binned AP (per source AP)
        o["crack_h1000_pos"] = np.bincount(b[g], minlength=1000).tolist()
        o["crack_h1000_neg"] = np.bincount(b[k & ~g], minlength=1000).tolist()
    return o


def dihedral(x: torch.Tensor, i: int, inv: bool = False) -> torch.Tensor:
    r, f = i % 4, i // 4
    if not inv:
        x = torch.rot90(x, r, (2, 3))
        return torch.flip(x, (3,)) if f else x
    if f:
        x = torch.flip(x, (3,))
    return torch.rot90(x, -r, (2, 3))


@torch.no_grad()
def predict(m, img_dir: Path, stems: list[str], cfg: dict, tta: bool):
    d = cfg["data"]
    ds = BenchmarkELDataset(img_dir, None, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    plain, tlp, got = [], [], []
    for b in DataLoader(ds, batch_size=8, shuffle=False, num_workers=4):
        x = b["image"].to(DEV)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lg = m(x).float()
        plain.append(lg.cpu())
        got += list(b["stem"])
        if tta:
            pr = torch.zeros_like(lg)
            for i in range(8):
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    li = m(dihedral(x, i)).float()
                pr += torch.softmax(dihedral(li, i, inv=True), 1)
            tlp.append(torch.log(pr / 8 + 1e-12).cpu())
    assert got == stems, "stem order"
    plain = torch.cat(plain)
    return plain, (torch.cat(tlp) if tta else None)


def main() -> None:
    torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    sets = {}
    for sp in ("val", "test"):
        st = sorted(load_split(DATA / "splits" / f"{sp}.txt"))
        st = [s for s in st if (DATA / "escdd_masks" / sp / f"{s}.png").exists()]
        assert len(st) == {"val": 54, "test": 50}[sp], (sp, len(st))
        sets[sp] = (DATA / "labeled" / "images", st, [np.array(Image.open(DATA / "escdd_masks" / sp / f"{s}.png")) for s in st], [None] * len(st))
    ext_dir = Path(a.ext)
    ext = [l.strip() for l in open(ext_dir / "stems_eval.txt") if l.strip()]
    assert len(ext) == 106, len(ext)
    sets["ext"] = (ext_dir / "images", ext, [np.array(Image.open(ext_dir / "masks" / f"{s}.png")) for s in ext],
                   [~(np.array(Image.open(ext_dir / "ignore" / f"{s}.png")) > 0) for s in ext])
    if not (out / "val_gt.npy").exists():
        np.save(out / "val_gt.npy", np.stack(sets["val"][2]).astype(np.uint8))
        (out / "val_stems.txt").write_text("\n".join(sets["val"][1]) + "\n")
    for run in map(Path, a.runs):
        f = out / f"{run.name}.json"
        # pilots (val only) must never carry test cells: the sets dict is filtered below and recorded here
        if f.exists():
            print("skip", run.name); continue
        t0 = time.time()
        cfg = load_config(run / "config_used.yaml")
        st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
        key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
        mcfg = {k: v for k, v in cfg["model"].items() if k != "encoder_init"}
        mcfg["encoder_weights"] = None
        m = build_model(mcfg).to(DEV); m.load_state_dict(st["models"][key]); m.eval()
        res = {"run": run.name, "weights": key, "step": int(st.get("step", -1)), "cells": {}, "sets_scored": list(a.sets)}
        assert res["step"] == 20000, (run, res["step"])
        rv = run.parent.parent / "REVISION"
        res["code_revision"] = rv.read_text().strip() if rv.exists() else "none (see protocol)"
        for name, (img_dir, stems, gts, keeps) in sets.items():
            if name not in a.sets:
                continue
            tta = name == "val"
            lg, tlp = predict(m, img_dir, stems, cfg, tta)
            pred = lg.argmax(1).numpy()
            pcr = torch.softmax(lg, 1)[:, CRACK].numpy()
            res["cells"][name] = {s: cell_stats(p, g, k, c) for s, p, g, k, c in zip(stems, pred, gts, keeps, pcr)}
            if tta:
                tp = tlp.argmax(1).numpy()
                tpc = tlp[:, CRACK].exp().numpy()
                res["cells"]["val_tta"] = {s: cell_stats(p, g, k, c) for s, p, g, k, c in zip(stems, tp, gts, keeps, tpc)}
                if not a.no_logits:
                    np.save(out / f"{run.name}.val_logp.npy", torch.log_softmax(lg, 1).half().numpy())
                    np.save(out / f"{run.name}.val_tta_logp.npy", tlp.half().numpy())
        f.write_text(json.dumps(res))
        print(f"{run.name:24s} {key:7s} step {res['step']} ({time.time() - t0:.0f}s)", flush=True)
        del m; torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
