"""Diagnostic (read-only): crack prediction on one test cell for given runs, bf16 vs fp32, plus probability stats.
Run from a code worktree root: python diag_csir70.py --runs ... --out DIR"""
import argparse, os, sys
from pathlib import Path
import numpy as np, torch
from PIL import Image
ROOT = Path.cwd(); sys.path.insert(0, str(ROOT))
from src.data.augmentations import get_weak_augmentation
from src.data.benchmark_el import BenchmarkELDataset
from src.data.class_info import CRACK_CLASS
from src.models.model_factory import build_model
from src.utils.config import load_config
ap = argparse.ArgumentParser(); ap.add_argument("--runs", nargs="+"); ap.add_argument("--out"); ap.add_argument("--stem", default="CSIR_00070_r8_c4")
a = ap.parse_args(); dev = torch.device("cuda"); D = ROOT / "data"
os.makedirs(a.out, exist_ok=True)
g = np.array(Image.open(D / "escdd_masks" / "test" / f"{a.stem}.png"))
for run in a.runs:
    cfg = load_config(ROOT / "experiments" / run / "config_used.yaml"); d = cfg["data"]
    ds = BenchmarkELDataset(D / "labeled" / "images", D / "labeled" / "masks_coded", [a.stem], get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    st = torch.load(ROOT / "experiments" / run / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
    key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
    m = build_model(cfg["model"]).to(dev); m.load_state_dict(st["models"][key]); m.eval()
    x = ds[0]["image"][None].to(dev)
    with torch.no_grad():
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lb = m(x).float()
        lf = m(x).float()
    for name, lg in (("bf16", lb), ("fp32", lf)):
        pr = lg.softmax(1)[0]; am = lg.argmax(1)[0].cpu().numpy(); pc = pr[CRACK_CLASS].cpu().numpy()
        fp = int(((am == CRACK_CLASS) & (g != CRACK_CLASS)).sum())
        q = np.quantile(pc[am == CRACK_CLASS], [0.1, 0.5, 0.9]) if (am == CRACK_CLASS).any() else [np.nan] * 3
        print(f"{run} {key} {name}: crack pred px {(am == CRACK_CLASS).sum()}, fp {fp}, p(crack) on predicted crack q10/50/90 {q[0]:.2f}/{q[1]:.2f}/{q[2]:.2f}, px with p(crack)>0.3 {(pc > 0.3).sum()}", flush=True)
        if name == "bf16":
            Image.fromarray((pc * 255).astype(np.uint8)).save(f"{a.out}/{run}_pcrack.png")
    del m; torch.cuda.empty_cache()
