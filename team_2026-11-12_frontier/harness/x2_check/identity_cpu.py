"""CPU bit-identity check of one training path (thin worktree): run N real training steps of a code root on CPU and record
everything that must match between two code roots.

The run is the real one minus the GPU: ``scripts/train.py``'s own builders (``apply_opts``, ``build_benchmark_data``,
``build_optimizer``), the model factory and the loss factory of ``--code``, and ``Trainer._train_step`` on the real
labelled stream (seed, stream 0, batch k = step k), fp32 (no autocast on CPU), ``num_workers`` 0 (a resume-mutable key:
the stream is a pure function of seed and step). After every step: the loss / loss_sup values (exact float repr), the
learning rate(s), the sha256 of every parameter and buffer, and the sha256 of the eval-mode logits on a fixed batch (the
stream's batch 0). Also seconds per step and, for Skeleton Recall runs, the tube count.

Usage (from anywhere; nothing is written inside --code):
  python identity_cpu.py --code /path/to/root --out rec.json --steps 3 --opts seed=0 data.labeled_fraction=1.0 ...
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--steps", type=int, default=3)
ap.add_argument("--threads", type=int, default=8)
ap.add_argument("--opts", nargs="*", default=[])
a = ap.parse_args()
ROOT = Path(a.code).resolve()
OUT = Path(a.out).resolve()
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

import torch  # noqa: E402

torch.set_num_threads(a.threads)
spec = importlib.util.spec_from_file_location("train_under_test", ROOT / "scripts" / "train.py")
train = importlib.util.module_from_spec(spec); spec.loader.exec_module(train)
from src.losses.loss_factory import build_losses  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.trainers.trainer import Trainer  # noqa: E402
from src.utils.config import load_config  # noqa: E402
from src.utils.seed import set_seed  # noqa: E402


def sha(t: torch.Tensor) -> str:
    return hashlib.sha256(t.detach().contiguous().cpu().numpy().tobytes()).hexdigest()[:16]


def state_hash(m: torch.nn.Module) -> str:
    h = hashlib.sha256()
    for k, v in m.state_dict().items():
        h.update(k.encode()); h.update(v.detach().contiguous().cpu().numpy().tobytes())
    return h.hexdigest()[:16]


def main() -> None:
    cfg = train.apply_opts(load_config("configs/supervised.yaml"), a.opts + ["training.num_workers=0"])
    seed = int(cfg["seed"])
    set_seed(seed, deterministic=cfg["training"].get("deterministic", True))
    dev = torch.device("cpu")
    method = cfg.get("method", "supervised")
    train.__dict__.get("check_thin_b3", lambda c, m: None)(cfg, method)  # thin worktree only
    data = train.build_benchmark_data(cfg, method, seed, float(cfg["data"]["labeled_fraction"]), False, dev, 0)
    torch.manual_seed(seed)
    model = build_model(cfg["model"]).to(dev)
    losses = build_losses(cfg["loss"], data["class_counts"])
    rec = {"code": str(ROOT), "opts": a.opts, "loss_class": type(losses["supervised"]).__name__,
           "n_params": sum(p.numel() for p in model.parameters()), "init_state": state_hash(model),
           "class_counts_sha": hashlib.sha256(bytes(str(list(map(int, data["class_counts"]))), "ascii")).hexdigest()[:16],
           "steps": []}
    with tempfile.TemporaryDirectory() as td:
        tr = Trainer(model=model, optimizer=train.build_optimizer(model, cfg), losses=losses,
                     labeled_loader=data["labeled_loader"], val_loader=None, test_loader=None, cfg=cfg, device=dev,
                     run_dir=Path(td) / "run", class_counts=data["class_counts"])
        fixed = next(data["labeled_loader"].iterate(0))
        rec["fixed_batch"] = {"stems": list(fixed["stem"]), "image": sha(fixed["image"]), "mask": sha(fixed["mask"]),
                              "keys": sorted(fixed)}
        it = data["labeled_loader"].iterate(0)
        for step in range(a.steps):
            t0 = time.perf_counter()
            out = tr._train_step(step, it, None)
            dt = time.perf_counter() - t0
            model.eval()
            with torch.no_grad():
                lg = model(fixed["image"])
            model.train()
            row = {"step": step + 1, "out": {k: repr(v) for k, v in out.items()},
                   "lr": [repr(g["lr"]) for g in tr.optimizer.param_groups], "state": state_hash(model),
                   "logits": sha(lg), "logits_shape": list(lg.shape), "sec": round(dt, 2)}
            if tr.thin_on if hasattr(tr, "thin_on") else False:
                row["thin"] = {k: repr(float(v)) for k, v in tr.sup_criterion.last_terms.items()}
            rec["steps"].append(row)
            print(json.dumps(row), flush=True)
    OUT.write_text(json.dumps(rec, indent=1))


if __name__ == "__main__":
    main()
