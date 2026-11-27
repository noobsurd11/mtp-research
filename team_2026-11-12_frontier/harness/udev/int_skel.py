"""integrator udev: Skeleton Recall term on the trainer's real path for N CPU steps (pattern of the rows2 reviewer's
rv_skel.py, threads from OMP_NUM_THREADS). Prints per step only booleans and counts: loss class, term present / finite / > 0,
tube px > 0, tube px on ignore (255) px, any non-finite loss. No loss value is printed.
Usage: int_skel.py <repo> <steps> <opts...>"""
import importlib.util
import math
import os
import sys
import tempfile
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
ROOT = Path(sys.argv[1]).resolve()
N = int(sys.argv[2])
OPTS = sys.argv[3:]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
import torch  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "1")))
spec = importlib.util.spec_from_file_location("t", ROOT / "scripts" / "train.py")
train = importlib.util.module_from_spec(spec)
spec.loader.exec_module(train)
from src.losses.loss_factory import build_losses  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.trainers.trainer import Trainer  # noqa: E402
from src.utils.config import load_config  # noqa: E402
from src.utils.seed import set_seed  # noqa: E402

cfg = train.apply_opts(load_config("configs/supervised.yaml"), OPTS + ["training.num_workers=0"])
seed = int(cfg["seed"])
set_seed(seed, deterministic=True)
dev = torch.device("cpu")
train.__dict__.get("check_thin_b3", lambda c, m: None)(cfg, "supervised")
data = train.build_benchmark_data(cfg, "supervised", seed, float(cfg["data"]["labeled_fraction"]), False, dev, 0)
torch.manual_seed(seed)
model = build_model(cfg["model"])
losses = build_losses(cfg["loss"], data["class_counts"])
print("data root", cfg["data"].get("root", cfg["data"].get("data_root")), "loss class", type(losses["supervised"]).__name__,
      "srec_weight", getattr(losses["supervised"], "srec_weight", None), flush=True)
with tempfile.TemporaryDirectory() as td:
    tr = Trainer(model=model, optimizer=train.build_optimizer(model, cfg), losses=losses, labeled_loader=data["labeled_loader"],
                 val_loader=None, test_loader=None, cfg=cfg, device=dev, run_dir=Path(td) / "run", class_counts=data["class_counts"])
    print("trainer thin_on", getattr(tr, "thin_on", None), flush=True)
    chk = data["labeled_loader"].iterate(0)
    it = data["labeled_loader"].iterate(0)
    nonfinite = 0
    for s in range(N):
        b = next(chk)
        tube = b.get("skel_tube")
        tpx = int(tube.sum()) if tube is not None else -1
        ign = int(((tube > 0) & (b["mask"] == 255)).sum()) if tube is not None else -1
        crack = bool((b["mask"] == 14).sum() > 0)
        out = tr._train_step(s, it, None)
        lv = out.get("loss") if isinstance(out, dict) else None
        fin_loss = (lv is None) or math.isfinite(float(lv))
        nonfinite += int(not fin_loss)
        lt = getattr(tr.sup_criterion, "last_terms", {}) or {}
        v = lt.get("loss_srec")
        print(f"step {s + 1}: batch has crack px {crack} tube px>0 {tpx > 0} tube px on ignore {ign} | srec term present "
              f"{v is not None} finite {bool(torch.isfinite(v)) if v is not None else None} >0 "
              f"{bool(v > 0) if v is not None else None} | total loss finite {fin_loss if lv is not None else 'n/a'}", flush=True)
    print(f"non-finite total loss steps: {nonfinite} of {N}", flush=True)
