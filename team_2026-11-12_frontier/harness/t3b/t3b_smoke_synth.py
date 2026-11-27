"""SYNTHETIC data for the T3b smokes (never a sealed image, mask or prediction). Only the E1 stem LIST is real.
  ext DIR                      a fake ext117: stems_eval.txt (the real list bytes), random images, masks (values 0 to 23 with
                               crack lines in exactly 32 cells, so 74 are crack-free as in E1; inactive blocks, gridlines),
                               ignore maps (a small block of 255, never on a crack line)
  runs DEPLOY REVISION ROOTMAP RELAY NAMES...
                               tiny random U-Net++ runs DEPLOY/experiments/<name> (config_used.yaml with the seed of the name
                               and data.root from ROOTMAP '<name prefix>=<root>' pairs, comma separated; latest.pth step 20000
                               with keys model and swad), DEPLOY/REVISION, and RELAY/<name>/runs/<name>/LATEST.md5
  units DEPLOY NAME...         the cv02 side of finished training runs as cq.sh leaves them (review round 1 B1 smokes):
                               experiments/<n>/checkpoints/slim.pth (random bytes), runs/<n>/LATEST.md5 (md5 of latest.pth),
                               runs/<n>/RUN.md5 (config_used.yaml, slim.pth, LATEST.md5); the run dir must exist
Usage: python t3b_smoke_synth.py ext DIR | runs DEPLOY REVISION ROOTMAP RELAY NAME... | units DEPLOY NAME...
"""
import hashlib
import re
import sys
from pathlib import Path

import numpy as np

E1_LIST = Path("/home/yugma/mtp/research/team_2026-11-12_frontier/harness/t3b/lists/e1_106_stems.txt")
MODEL = {"name": "unetpp", "in_channels": 1, "num_classes": 24, "start_filters": 2, "dropout_rate": 0.0, "input_size": 512}


def ext(d: Path):
    from PIL import Image
    rng = np.random.default_rng(11)
    for s in ("images", "masks", "ignore"):
        (d / s).mkdir(parents=True)
    (d / "stems_eval.txt").write_bytes(E1_LIST.read_bytes())
    stems = [l.strip() for l in open(E1_LIST) if l.strip()]
    crack = set(rng.choice(len(stems), 32, replace=False).tolist())
    for i, st in enumerate(stems):
        Image.fromarray(rng.integers(0, 256, (512, 512), dtype=np.uint8)).save(d / "images" / f"{st}.png")
        m = np.zeros((512, 512), np.uint8); m[:, :40] = 7; m[200:210, :] = 4
        if i in crack:
            r = int(rng.integers(50, 440)); m[r:r + 2, 60:400] = 14
        if rng.random() < 0.1:
            m[300:400, 300:400] = 11
        if rng.random() < 0.5:
            m[100:103, :] = 15
        ig = np.zeros((512, 512), np.uint8)
        if rng.random() < 0.5:
            ig[450:470, 450:470] = 255
        Image.fromarray(m).save(d / "masks" / f"{st}.png"); Image.fromarray(ig).save(d / "ignore" / f"{st}.png")
    print(f"synthetic ext117 in {d}: 106 cells")


def runs(dep: Path, rev: str, rootmap: str, relay: Path, names):
    import torch
    import yaml
    sys.path.insert(0, "/home/noob/work/bench_wt_t3b")
    from src.models.model_factory import build_model
    roots = dict(x.split("=", 1) for x in rootmap.split(","))
    (dep / "experiments").mkdir(parents=True, exist_ok=True)
    (dep / "REVISION").write_text(rev + "\n")
    for n in names:
        seed = int(re.search(r"_s(\d+)$", n).group(1))
        root = next(v for k, v in roots.items() if n.startswith(k))
        run = dep / "experiments" / n
        (run / "checkpoints").mkdir(parents=True)
        cfg = {"seed": seed, "method": "supervised", "model": MODEL, "training": {"total_steps": 20000},
               "data": {"root": root, "input_size": 512, "mean": [0.5], "std": [0.25]}}
        (run / "config_used.yaml").write_text(yaml.safe_dump(cfg))
        torch.manual_seed(seed * 7 + len(n))
        m = build_model(MODEL)
        with torch.no_grad():
            m.output_conv.weight.mul_(1000.0)
            m.output_conv.bias.copy_(torch.randn(24) * 50.0)
        torch.save({"step": 20000, "models": {"model": m.state_dict(), "swad": m.state_dict()}}, run / "checkpoints" / "latest.pth")
        h = hashlib.md5((run / "checkpoints" / "latest.pth").read_bytes()).hexdigest()
        rl = relay / n / "runs" / n
        rl.mkdir(parents=True)
        (rl / "LATEST.md5").write_text(f"{h}  experiments/{n}/checkpoints/latest.pth\n")
    print(f"{len(names)} tiny runs in {dep} (REVISION {rev[:7]}), LATEST.md5 in {relay}")


def units(dep: Path, names):
    import os
    for n in names:
        e = dep / "experiments" / n
        assert (e / "config_used.yaml").is_file() and (e / "checkpoints" / "latest.pth").is_file(), n
        (e / "checkpoints" / "slim.pth").write_bytes(os.urandom(4096))
        r = dep / "runs" / n
        r.mkdir(parents=True, exist_ok=True)
        h = hashlib.md5((e / "checkpoints" / "latest.pth").read_bytes()).hexdigest()
        (r / "LATEST.md5").write_text(f"{h}  experiments/{n}/checkpoints/latest.pth\n")
        rows = [f"experiments/{n}/config_used.yaml", f"experiments/{n}/checkpoints/slim.pth", f"runs/{n}/LATEST.md5"]
        (r / "RUN.md5").write_text("".join(f"{hashlib.md5((dep / x).read_bytes()).hexdigest()}  {x}\n" for x in rows))
    print(f"{len(names)} training units (slim, LATEST.md5, RUN.md5) in {dep}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "ext":
        ext(Path(a[1]))
    elif a[0] == "runs":
        runs(Path(a[1]), a[2], a[3], Path(a[4]), a[5:])
    elif a[0] == "units":
        units(Path(a[1]), a[2:])
    else:
        sys.exit("ext | runs")
