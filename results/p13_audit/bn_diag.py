"""Post-hoc BatchNorm diagnostic for the SSL handicap (no training; weights frozen).

For each run (final-step weights from checkpoints/latest.pth: the EMA teacher for mean_teacher runs, the model
otherwise), the BN running statistics are evaluated as trained ("orig") and after recomputation (cumulative average,
one pass, eval transform, batch 8, fixed order) from
  own   - the run's own labelled images (the labelled subset of its config),
  train - all 478 BenchmarkEL train images (in-domain, clean).
Test (50 cells) is scored against the E-SCDD revised masks with rescore_label_versions.score (argmax IoU, relF1@2).

Usage: python bn_diag.py --code /tmp/noob_el/el_p7 --out out.json --runs <run dir> ...
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--runs", nargs="+", required=True)
a = ap.parse_args()
CODE = Path(a.code).resolve()
RUNS = [Path(r).resolve() for r in a.runs]
OUT = Path(a.out).resolve()
sys.path.insert(0, str(CODE))
sys.path.insert(0, str(CODE / "scripts"))
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np  # noqa: E402
import torch  # noqa: E402
from PIL import Image  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

import rescore_label_versions as R  # noqa: E402  (chdir to CODE)
from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.class_info import CRACK_CLASS, INACTIVE_CLASS  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

DEV = torch.device("cuda")
SPL = CODE / "data" / "splits"


def bns(m):
    return [x for x in m.modules() if isinstance(x, torch.nn.modules.batchnorm._BatchNorm)]


def weak(cfg):
    d = cfg["data"]
    return get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"])


@torch.no_grad()
def recal(m, stems, cfg):
    for b in bns(m):
        b.reset_running_stats()
        b.momentum = None
    m.eval()
    for b in bns(m):
        b.train()
    order = [stems[i] for i in np.random.default_rng(0).permutation(len(stems))]
    for bt in DataLoader(BenchmarkELDataset(R.IMG, None, order, weak(cfg)), batch_size=8, shuffle=False, num_workers=4):
        with torch.autocast("cuda", dtype=torch.bfloat16):
            m(bt["image"].to(DEV))
    m.eval()


@torch.no_grad()
def score(m, dl, new):
    probs = {CRACK_CLASS: [], INACTIVE_CLASS: []}
    preds = []
    for b in dl:
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lg = m(b["image"].to(DEV)).float()
        sm = torch.softmax(lg, 1)
        for c in probs:
            probs[c] += list(sm[:, c].cpu().numpy())
        preds += list(lg.argmax(1).cpu().numpy())
    return {n: R.score(probs[c], preds, new, c) for n, c in (("crack", CRACK_CLASS), ("inactive", INACTIVE_CLASS))}


def main():
    torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False
    test = sorted(load_split(SPL / "test.txt"))
    test = [s for s in test if (R.NEW / "test" / f"{s}.png").exists()]
    new = [np.array(Image.open(R.NEW / "test" / f"{s}.png")) for s in test]
    train = load_split(SPL / "train.txt")
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    for run in RUNS:
        if run.name in res:
            continue
        t0 = time.time()
        cfg = load_config(run / "config_used.yaml")
        d = cfg["data"]
        frac = float(d.get("labeled_fraction", 1.0))
        ss = int(d.get("split_seed", cfg["seed"]))
        own = load_split(SPL / "train.txt") if frac >= 1 else load_split(SPL / f"seed{ss}" / f"labeled_{round(frac * 100)}pct.txt")
        st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
        key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
        sd = st["models"][key]
        dl = DataLoader(BenchmarkELDataset(R.IMG, R.MSK, test, weak(cfg)), batch_size=8, shuffle=False, num_workers=4)
        out = {"weights": key, "step": int(st.get("step", -1)), "n_own": len(own)}
        for src, stems in (("orig", None), ("own", own), ("train", train)):
            m = build_model(cfg["model"]).to(DEV)
            m.load_state_dict(sd)
            m.eval()
            if stems is not None:
                recal(m, stems, cfg)
            out[src] = score(m, dl, new)
            del m
        res[run.name] = out
        OUT.write_text(json.dumps(res, indent=1))
        print(f"{run.name:22s} " + "  ".join(
            f"{s}: {out[s]['crack']['iou']:.3f}/{out[s]['inactive']['iou']:.3f}/{out[s]['crack']['rel_f1_2']:.3f}"
            for s in ("orig", "own", "train")) + f"  ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
