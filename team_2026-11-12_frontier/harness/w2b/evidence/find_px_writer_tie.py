import sys
sys.path.insert(0, "/home/noob/work/bench_w2b_io/new_5995379")
import torch, numpy as np
from torch.utils.data import DataLoader
from src.models.model_factory import build_model
from src.utils.config import load_config
from src.data.benchmark_el import BenchmarkELDataset
from src.data.augmentations import get_weak_augmentation
from bench import sets
torch.set_num_threads(8)
run = "/home/noob/work/bench_w2b_io/repro/repro_pf_f0"
cfg = load_config(f"{run}/config_used.yaml")
mc = {k: v for k, v in cfg["model"].items()}; mc["encoder_weights"] = None
m = build_model(mc); st = torch.load(f"{run}/checkpoints/latest.pth", map_location="cpu", weights_only=False)
m.load_state_dict(st["models"]["model"]); m.eval()
S = sets.resolve("cv5v2_f0", None)
d = cfg["data"]
ds = BenchmarkELDataset(S["images"], None, S["stems"], get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
lgs = []
with torch.no_grad():
    for b in DataLoader(ds, batch_size=8, shuffle=False, num_workers=2):
        lgs.append(m(b["image"]).float())
lg = torch.cat(lgs); p = torch.softmax(lg, 1)
for i in range(lg.shape[0]):
    pred = lg[i].argmax(0)
    lq = torch.log(p[i] + 1e-12); pc = lq[14].clone(); lq[14] = -1e30; mo, oth = lq.max(0)
    mg = (pc - mo).numpy().astype(np.float16).astype(np.float32)
    implied = np.where(mg > 0, 14, oth.numpy())
    bad = (implied != pred.numpy()) & (np.abs(mg) >= 1e-3)
    if bad.any():
        y, x = np.argwhere(bad)[0]
        print("cell", S["stems"][i], "px", y, x, "pred", int(pred[y, x]), "oth", int(oth[y, x]), "m", float(mg[y, x]))
        v = lg[i, :, y, x]; order = v.argsort(descending=True)[:4]
        print(" top logits", [(int(c), float(v[c])) for c in order])
        print(" p", [(int(c), float(p[i, c, y, x])) for c in order], "log(p+1e-12)", [(int(c), float(torch.log(p[i, c, y, x] + 1e-12))) for c in order])
        break
