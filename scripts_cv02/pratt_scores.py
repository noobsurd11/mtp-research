"""Read-only: per-image TP/FP/FN for crack (14), gridline (15) and inactive (11) on the 50 test cells, against the old
(20211104, masks_coded) and revised (E-SCDD) labels, for Pratt-convention medians (per image, then median over images).
Final weights; teacher for Mean Teacher runs; argmax; bf16 as the re-score. Imports and data from --code.
Usage: python pratt_scores.py --code /tmp/noob_el/el_p13 --runs <run dir> ... --out pratt.json"""
import argparse, json, sys
from pathlib import Path
import numpy as np, torch
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument("--code"); ap.add_argument("--runs", nargs="+"); ap.add_argument("--out")
a = ap.parse_args(); ROOT = Path(a.code).resolve(); sys.path.insert(0, str(ROOT))
from torch.utils.data import DataLoader
from src.data.augmentations import get_weak_augmentation
from src.data.benchmark_el import BenchmarkELDataset
from src.data.splits import load_split
from src.models.model_factory import build_model
from src.utils.config import load_config
D = ROOT / "data"; dev = torch.device("cuda"); C = (14, 15, 11)
stems = [s for s in sorted(load_split(D / "splits" / "test.txt")) if (D / "escdd_masks" / "test" / f"{s}.png").exists()]
new = [np.array(Image.open(D / "escdd_masks" / "test" / f"{s}.png")) for s in stems]
res = {}
for rd in map(Path, a.runs):
    cfg = load_config(rd / "config_used.yaml"); d = cfg["data"]
    ds = BenchmarkELDataset(D / "labeled" / "images", D / "labeled" / "masks_coded", stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    st = torch.load(rd / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
    key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
    m = build_model(cfg["model"]).to(dev); m.load_state_dict(st["models"][key]); m.eval()
    out = {"old": {}, "new": {}}; i = 0
    for b in DataLoader(ds, batch_size=8, shuffle=False, num_workers=2):
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            pr = m(b["image"].to(dev)).float().argmax(1).cpu().numpy()
        for p, o, s in zip(pr, b["mask"].numpy(), b["stem"]):
            for lab, g in (("old", o), ("new", new[i])):
                out[lab][s] = [[int(((p == c) & (g == c)).sum()), int(((p == c) & (g != c)).sum()), int(((p != c) & (g == c)).sum())] for c in C]
            i += 1
    res[rd.name] = {"weights": key, **out}; print(rd.name, key, flush=True)
    del m; torch.cuda.empty_cache()
Path(a.out).write_text(json.dumps(res)); print("wrote", a.out)
