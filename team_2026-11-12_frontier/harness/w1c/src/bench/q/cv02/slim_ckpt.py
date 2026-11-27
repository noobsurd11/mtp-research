"""Slim checkpoint for the relay: <run>/checkpoints/latest.pth -> <run>/checkpoints/slim.pth holding only
{format, step, cfg, models, slim_of} (no optimizer, scheduler, scaler, rng, trainer state). CPU only.
bench_infer.py reads only st["step"] and st["models"][key], so slim.pth (renamed latest.pth) can be dumped again on gaint.
Asserts step == cfg training.total_steps (or --expect-step) and that every models.* tensor is unchanged in the written file.
Refuses to overwrite. Prints one line: "slim <run> step <n> keys <models keys> latest_md5 <md5> slim_md5 <md5>".
Usage: CUDA_VISIBLE_DEVICES= python bench/q/cv02/slim_ckpt.py --run <run dir> [--expect-step N]
"""
import argparse
import hashlib
import os
import sys
from pathlib import Path

import torch


def md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--expect-step", type=int, default=None)
    a = ap.parse_args()
    torch.set_num_threads(2)
    run = Path(a.run)
    src, dst = run / "checkpoints" / "latest.pth", run / "checkpoints" / "slim.pth"
    if dst.exists():
        sys.exit(f"refuse: {dst} exists")
    st = torch.load(src, map_location="cpu", weights_only=False)
    want = a.expect_step if a.expect_step is not None else int(st["cfg"]["training"]["total_steps"])
    assert int(st["step"]) == want, (int(st["step"]), want)
    lm = md5(src)
    slim = {"format": st.get("format"), "step": int(st["step"]), "cfg": st["cfg"], "models": st["models"],
            "slim_of": {"file": "latest.pth", "md5": lm}}
    tmp = dst.with_suffix(".pth.tmp")
    torch.save(slim, tmp)
    back = torch.load(tmp, map_location="cpu", weights_only=False)
    assert back["step"] == slim["step"] and set(back["models"]) == set(st["models"])
    for k, sd in st["models"].items():
        assert set(back["models"][k]) == set(sd), k
        for n, t in sd.items():
            assert torch.equal(back["models"][k][n], t), (k, n)
    os.replace(tmp, dst)
    print(f"slim {run.name} step {slim['step']} keys {sorted(st['models'])} latest_md5 {lm} slim_md5 {md5(dst)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
