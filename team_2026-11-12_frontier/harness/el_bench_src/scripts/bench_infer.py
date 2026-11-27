"""elbench inference: one harness run (config_used.yaml + checkpoints/latest.pth) on one named cell set -> per-cell dumps.

Predict path = b6_score.py 981b5f29 `predict` (= m0_audit d36f7438): eval transform (resize + normalise), batch 8 in the
set's order, DataLoader workers 4, logits concatenated, argmax and torch.softmax on the concatenated float logits.
  --device cpu  --precision fp32 : no autocast (b6 CPU check path)
  --device cuda --precision bf16 : torch.autocast("cuda", bfloat16), logits .float() (m0 / b6 GPU path; legacy identity only)
  --device cuda --precision fp32 : no autocast, TF32 off (canonical benchmark dumps)
Margin / oth = calib_dump c172717e `maps` (log(p + 1e-12), crack masked to -1e30, max over the rest).
Model = the run's config with pretrained-weight keys nulled (weights come from the checkpoint; m0 drops encoder_init and
sets encoder_weights None), built by this repo's src/models/model_factory.py.

Guards: sealed sets (test50, e1_106) need --opening; open sets must hold no stem of the forbidden list (md5 pinned) and
no stem of the run's own <data.root>/splits/train.txt; latest.pth step must equal --expect-step (default: the config's
training.total_steps); refuses to write into an existing set directory.

Usage: python scripts/bench_infer.py --run <run dir> --set val54 --dumps <root> --method <card name> [--card <yaml>]
         [--device cpu --precision fp32 --threads 4] [--run-id NAME] [--opening PROTOCOL] [--logp] [--bench-run JOB]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--run", required=True)
ap.add_argument("--set", required=True)
ap.add_argument("--dumps", required=True)
ap.add_argument("--bench", default="elbench1")
ap.add_argument("--method", required=True)
ap.add_argument("--run-id", default=None)
ap.add_argument("--card", default=None)
ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
ap.add_argument("--precision", default="fp32", choices=["fp32", "bf16"])
ap.add_argument("--batch", type=int, default=8)
ap.add_argument("--workers", type=int, default=4)
ap.add_argument("--threads", type=int, default=int(os.environ.get("OMP_NUM_THREADS", "8")))
ap.add_argument("--weights-key", default="auto", choices=["auto", "model", "ema", "teacher"])
ap.add_argument("--expect-step", type=int, default=None)
ap.add_argument("--opening", default=None)
ap.add_argument("--forbidden", default="/home/noob/work/b6/b6_forbidden.txt")
ap.add_argument("--logp", action="store_true", help="also store float16 log-probabilities (24 x 512 x 512); open sets only")
ap.add_argument("--bench-run", default=None, help="queue job name: verify token for bench_q / bench_guard; printed as "
                "'BENCH_START: run=<name>' before anything else (the queue's start check)")
a = ap.parse_args()
if a.bench_run:
    print(f"BENCH_START: run={a.bench_run}", flush=True)
if a.device == "cpu" and a.precision == "bf16":
    sys.exit("bf16 is the GPU legacy path only")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np  # noqa: E402
import torch  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from bench import cards, dumpfmt, sets  # noqa: E402
from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

CRACK, INACT = 14, 11
FORBIDDEN_MD5 = "9bb4d919fc16b5b394ce6d71f53903a6"
WEIGHT_KEYS_NULL = ("encoder_weights", "backbone_weights")
WEIGHT_KEYS_DROP = ("encoder_init", "decoder_init", "encoder_weights_file")


def inference_model_cfg(mcfg: dict) -> dict:
    m = {k: v for k, v in mcfg.items() if k not in WEIGHT_KEYS_DROP}
    for k in WEIGHT_KEYS_NULL:
        if k in m or k == "encoder_weights":
            m[k] = None
    return m


def maps(p: torch.Tensor):
    """calib_dump c172717e `maps`, on one cell's (24, H, W) float32 probabilities."""
    lq = torch.log(p + 1e-12)
    pc = lq[CRACK].clone()
    lq[CRACK] = -1e30
    mo, oth = lq.max(0)
    return (pc - mo).numpy().astype(np.float16), oth.numpy().astype(np.uint8)


@torch.no_grad()
def predict(m, img_dir: Path, stems: list[str], cfg: dict, dev: torch.device) -> torch.Tensor:
    d = cfg["data"]
    ds = BenchmarkELDataset(img_dir, None, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    plain, got = [], []
    for b in DataLoader(ds, batch_size=a.batch, shuffle=False, num_workers=a.workers):
        x = b["image"].to(dev)
        if a.precision == "bf16":
            with torch.autocast("cuda", dtype=torch.bfloat16):
                lg = m(x).float()
        else:
            lg = m(x).float()
        plain.append(lg.cpu())
        got += list(b["stem"])
    assert got == stems, "stem order"
    return torch.cat(plain)


def git_head(p: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(p), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def main() -> None:
    t0 = time.time()
    torch.set_num_threads(a.threads)
    torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False
    if a.device == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
    dev = torch.device(a.device)
    run = Path(a.run).resolve()
    run_id = a.run_id or run.name
    S = sets.resolve(a.set, a.opening)
    if a.logp and S["kind"] == "sealed":
        sys.exit("--logp is for open sets only")
    out_dir = dumpfmt.cell_path(a.dumps, a.bench, a.method, run_id, a.set, "x").parent
    if out_dir.exists():
        sys.exit(f"refuse: {out_dir} exists")
    cfg = load_config(run / "config_used.yaml")
    card = cards.load_card(a.card) if a.card else None
    # ---- list guards
    if S["kind"] == "open":
        assert dumpfmt.md5_file(a.forbidden) == FORBIDDEN_MD5, "forbidden list md5"
        fb = set(load_split(Path(a.forbidden)))
        assert not set(S["stems"]) & fb, "open set holds a sealed (test / E1) stem"
    droot = Path(cfg["data"]["root"])
    if not droot.is_absolute():
        droot = run.parent.parent / droot
    train_list = droot / "splits" / "train.txt"
    assert train_list.exists(), f"cannot check train overlap: {train_list} missing"
    tr = load_split(train_list)
    assert not set(S["stems"]) & set(tr), "the set overlaps the run's training cells"
    # ---- weights
    wpath = run / "checkpoints" / "latest.pth"   # final weights; best.pth is never read
    st = torch.load(wpath, map_location="cpu", weights_only=False)
    step = int(st.get("step", -1))
    want = a.expect_step if a.expect_step is not None else int(cfg["training"]["total_steps"])
    assert step == want, (run, step, want)
    key = a.weights_key
    if key == "auto":
        key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else \
            (card["weights_key"] if card else "model")
    assert key in st["models"], (key, list(st["models"]))
    m = build_model(inference_model_cfg(cfg["model"])).to(dev)
    m.load_state_dict(st["models"][key])
    m.eval()
    del st
    # ---- inference (m0 / b6 predict) and maps
    lg = predict(m, S["images"], S["stems"], cfg, dev)
    pred = lg.argmax(1).numpy().astype(np.uint8)
    if len(S["stems"]) <= 128:
        p = torch.softmax(lg, 1)                     # as m0 / b6: one softmax over the concatenated logits
    else:
        p = torch.cat([torch.softmax(c, 1) for c in torch.split(lg, 64)])
    cells = {}
    for i, s in enumerate(S["stems"]):
        mg, oth = maps(p[i])
        logp = torch.log(p[i] + 1e-12).numpy().astype(np.float16) if a.logp else None
        cells[s] = dumpfmt.write_cell(out_dir / f"{s}.npz", pred[i], oth, mg, p[i, CRACK].numpy(),
                                      p[i, INACT].numpy(), logp)
    fold = int(a.set.rsplit("_f", 1)[1]) if a.set.startswith("cv") else None
    rv = run.parent.parent / "REVISION"
    meta = {"bench": a.bench, "method": a.method, "run_id": run_id, "seed": int(cfg["seed"]),
            "split_def": str(droot), "split_md5": dumpfmt.md5_file(train_list), "fold": fold, "set": a.set,
            "stems_md5": sets.stems_md5(S["stems"]), "code_repo": str(ROOT), "code_commit": git_head(ROOT),
            "train_code_revision": rv.read_text().strip() if rv.exists() else "unknown",
            "checkpoint": str(wpath), "checkpoint_md5": dumpfmt.md5_file(wpath), "step": step, "weights_key": key,
            "device": torch.cuda.get_device_name(0) if a.device == "cuda" else "cpu", "precision": a.precision,
            "threads": a.threads, "batch": a.batch, "tta": False,
            "decision_rule": card["decision_rule"] if card else "argmax24",
            "card": a.card, "card_md5": dumpfmt.md5_file(a.card) if a.card else None,
            "writer": f"bench_infer.py {dumpfmt.md5_file(__file__)}", "set_kind": S["kind"], "opening": a.opening,
            "list_file": S["list_file"], "list_md5": S["list_md5"], "config_md5": dumpfmt.md5_file(run / "config_used.yaml")}
    dumpfmt.write_manifest(out_dir, meta, cells)
    ties = sum(c["ties"] for c in cells.values())
    mb = sum(c["bytes"] for c in cells.values()) / 2**20
    print(f"dumped {run_id} {a.set}: {len(cells)} cells, {mb:.1f} MiB, ties {ties}, key {key}, step {step}, "
          f"{a.device}/{a.precision}, {time.time() - t0:.0f}s -> {out_dir}", flush=True)


if __name__ == "__main__":
    main()
