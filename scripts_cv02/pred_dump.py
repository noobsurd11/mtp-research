"""Read-only: argmax predictions of given runs on given test cells (final weights; teacher for Mean Teacher runs), saved with
the raw image and the revised (E-SCDD) mask, for qualitative figures. Run from a cv02 code root (e.g. /tmp/noob_el/el_p13):
python pred_dump.py --runs ... --stems ... --out preds.npz"""
import argparse, sys
from pathlib import Path
import numpy as np, torch
from PIL import Image
ROOT = Path.cwd(); sys.path.insert(0, str(ROOT))
from src.data.augmentations import get_weak_augmentation
from src.data.benchmark_el import BenchmarkELDataset
from src.models.model_factory import build_model
from src.utils.config import load_config
ap = argparse.ArgumentParser(); ap.add_argument("--runs", nargs="+"); ap.add_argument("--stems", nargs="+"); ap.add_argument("--out")
a = ap.parse_args(); dev = torch.device("cuda"); D = ROOT / "data"; out = {}
for s in a.stems:
    out[f"img/{s}"] = np.array(Image.open(D / "labeled" / "images" / f"{s}.png"))
    out[f"gt/{s}"] = np.array(Image.open(D / "escdd_masks" / "test" / f"{s}.png"))
for run in a.runs:
    cfg = load_config(ROOT / "experiments" / run / "config_used.yaml"); d = cfg["data"]
    ds = BenchmarkELDataset(D / "labeled" / "images", D / "labeled" / "masks_coded", a.stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    st = torch.load(ROOT / "experiments" / run / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
    key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
    m = build_model(cfg["model"]).to(dev); m.load_state_dict(st["models"][key]); m.eval()
    for i, s in enumerate(a.stems):
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            out[f"pred/{run}/{s}"] = m(ds[i]["image"][None].to(dev)).float().argmax(1)[0].cpu().numpy().astype(np.uint8)
    print(run, key, flush=True); del m; torch.cuda.empty_cache()
np.savez_compressed(a.out, **out); print("wrote", a.out)
