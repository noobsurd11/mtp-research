"""G-N7 inference cost of the approved E1 candidates (C1, C1-D4, C2, C3, E-PF). CPU or CUDA, one config per process.

Code under test (read only, imported, never edited): the clean worktree --code (default /home/noob/work/bench_wt_t3b,
commit cba7fbd): src/models/model_factory.build_model, scripts/bench_infer.inference_model_cfg (re-implemented 1:1 below,
because importing bench_infer runs its argparse), bench/tta.predict_tta (the deployed D4 path: 8 views run one after
the other, each on the whole batch; p = mean softmax over the views).
Weights: final full-pool checkpoints, read only: <ckroot>/fin_{hrnet_swad,pf}_v11_pool_s{5..9}/experiments/<run>/checkpoints/
slim.pth (or latest.pth). Readouts: C1 / C1-D4 / E-PF = PF 'model'; C2 / C3 = HRNet 'swad' (FINAL_RULE_ADDENDUM_1 item 5).
Inputs: random float32 tensors of the real shape (B, 1, 512, 512), values = (U(0,1) - 0.5) / 0.25 (the eval normalisation);
no image, label or prediction of any set is read.

Subcommands
  verify   strict load of every checkpoint found (step must be 20000), parameter counts, md5 of each file. JSON out.
  flops    torch.utils.flop_counter.FlopCounterMode at (1, 1, 512, 512) per architecture, and for one D4 cell via
           predict_tta (8 views). FlopCounterMode counts 2 FLOPs per multiply-add; here it counts aten.convolution only
           (BN, ReLU, upsampling, adds, softmax are not counted). GFLOPs = total / 1e9 (the convention of the 148.0 /
           218.0 figures in the cards); GMACs = total / 2e9 (what bench_rows1_io/probe/probe.py prints).
  time     one arm, one thread count, one batch size: warm-up, then timed batches. Per batch: wall time of the whole
           predict (all members, all views, softmax, view / member average) with time.perf_counter (CPU) or CUDA events +
           synchronize (GPU). Peak memory: CPU VmHWM - and VmRSS after model load; GPU torch.cuda.max_memory_allocated.

Arms (members x views):
  C1     PF s5, plain: softmax(model(x))                                1 x 1 = 1 forward per cell
  C1D4   PF s5, predict_tta d4                                          1 x 8 = 8
  C2     HRNet+SWAD s5, predict_tta d4                                  1 x 8 = 8
  C3     HRNet+SWAD s5..s9, mean over members of predict_tta d4         5 x 8 = 40
  EPF    PF s5..s9, mean over members of softmax(model(x))              5 x 1 = 5
  UPF / UHR  one plain forward + softmax of PF / HRNet (the unit cost)  1
  --views-batched (C1D4, C2, C3 only): the 8 D4 views of each cell go through the model in ONE forward of 8*B images
                  (not the deployed path; same maths up to float summation order).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

ARMS = {"C1": ("pf", 1, False), "C1D4": ("pf", 1, True), "C2": ("hrnet", 1, True), "C3": ("hrnet", 5, True),
        "EPF": ("pf", 5, False), "UPF": ("pf", 1, False), "UHR": ("hrnet", 1, False)}
RUN = {"pf": "fin_pf_v11_pool_s{s}", "hrnet": "fin_hrnet_swad_v11_pool_s{s}"}
KEY = {"pf": "model", "hrnet": "swad"}
SEEDS = (5, 6, 7, 8, 9)
WEIGHT_KEYS_NULL = ("encoder_weights", "backbone_weights")          # = scripts/bench_infer.py
WEIGHT_KEYS_DROP = ("encoder_init", "decoder_init", "encoder_weights_file")


def inference_model_cfg(mcfg: dict) -> dict:
    """1:1 copy of scripts/bench_infer.py inference_model_cfg (worktree cba7fbd)."""
    m = {k: v for k, v in mcfg.items() if k not in WEIGHT_KEYS_DROP}
    for k in WEIGHT_KEYS_NULL:
        if k in m or k == "encoder_weights":
            m[k] = None
    return m


def md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def ckpt_path(root: Path, arch: str, s: int) -> Path:
    r = RUN[arch].format(s=s)
    for base in (root / r / "experiments" / r / "checkpoints", root / "experiments" / r / "checkpoints"):
        for f in ("slim.pth", "latest.pth"):
            if (base / f).exists():
                return base / f
    raise FileNotFoundError(f"no slim.pth / latest.pth for {r} under {root}")


def proc_status() -> dict:
    out = {}
    try:
        for ln in Path("/proc/self/status").read_text().splitlines():
            if ln.startswith(("VmHWM", "VmRSS")):
                out[ln.split(":")[0]] = int(ln.split()[1]) / 1024.0   # MiB
    except OSError:
        pass
    return out


def env_info(torch, dev) -> dict:
    d = {"python": platform.python_version(), "torch": torch.__version__, "threads": torch.get_num_threads(),
         "interop_threads": torch.get_num_interop_threads(), "host": platform.node(), "device": str(dev),
         "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"), "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
         "nice": os.nice(0), "loadavg": os.getloadavg()}
    try:
        d["cpu"] = next(ln.split(":", 1)[1].strip() for ln in open("/proc/cpuinfo") if ln.startswith("model name"))
    except (OSError, StopIteration):
        d["cpu"] = platform.processor()
    if dev.type == "cuda":
        d.update(gpu=torch.cuda.get_device_name(dev), cuda=torch.version.cuda, cudnn=torch.backends.cudnn.version(),
                 tf32_matmul=torch.backends.cuda.matmul.allow_tf32, tf32_cudnn=torch.backends.cudnn.allow_tf32,
                 cudnn_deterministic=torch.backends.cudnn.deterministic, cudnn_benchmark=torch.backends.cudnn.benchmark)
    try:
        import segmentation_models_pytorch as smp
        import timm
        d.update(smp=smp.__version__, timm=timm.__version__)
    except Exception as e:  # noqa: BLE001
        d["smp_timm"] = repr(e)
    return d


def load_member(torch, build_model, root: Path, arch: str, s: int, dev, want_step=20000):
    p = ckpt_path(root, arch, s)
    st = torch.load(p, map_location="cpu", weights_only=False)
    step = int(st.get("step", -1))
    assert step == want_step, (str(p), step)
    m = build_model(inference_model_cfg(st["cfg"]["model"]))
    res = m.load_state_dict(st["models"][KEY[arch]], strict=True)
    keys = sorted(st["models"])
    del st
    return m.eval().to(dev), p, step, keys, res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["verify", "flops", "time"])
    ap.add_argument("--code", default="/home/noob/work/bench_wt_t3b")
    ap.add_argument("--ckroot", default="/mnt/nas/noob_el_archive/bench_relay/fin2")
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--arm", default="C2", choices=sorted(ARMS))
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--views-batched", action="store_true")
    ap.add_argument("--warmup", type=int, default=3, help="warm-up batches (not timed)")
    ap.add_argument("--cells", type=int, default=200, help="timed cells (rounded up to whole batches)")
    ap.add_argument("--max-seconds", type=float, default=0, help="stop timing after this many seconds (0 = no cap); "
                    "the number of cells actually timed is reported")
    ap.add_argument("--no-weights", action="store_true", help="random init (same compute); default loads checkpoints")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    sys.path.insert(0, str(Path(a.code).resolve()))
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    import torch
    torch.set_num_threads(a.threads)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass
    dev = torch.device(a.device)
    if dev.type == "cuda":   # canonical benchmark dump settings (scripts/bench_infer.py lines 148 to 152)
        torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
    from src.models.model_factory import build_model
    from bench import tta as TTA
    root = Path(a.ckroot)
    out = {"cmd": a.cmd, "args": vars(a), "env": env_info(torch, dev)}

    if a.cmd == "verify":
        rows = []
        for arch in ("pf", "hrnet"):
            for s in SEEDS:
                m, p, step, keys, res = load_member(torch, build_model, root, arch, s, torch.device("cpu"))
                n = sum(t.numel() for t in m.parameters())
                ne = sum(t.numel() for k, t in m.named_parameters() if k.startswith("encoder."))
                nb = sum(t.numel() for t in m.buffers())
                rows.append({"arch": arch, "seed": s, "file": str(p), "md5": md5(p), "step": step, "readout": KEY[arch],
                             "models_keys": keys, "strict_load": "ok (missing 0, unexpected 0)" if not res.missing_keys
                             and not res.unexpected_keys else repr(res), "params": n, "encoder_params": ne,
                             "buffers": nb, "class": type(m).__name__,
                             "encoder_class": type(getattr(m, "encoder", m)).__name__})
                print(json.dumps({k: rows[-1][k] for k in ("arch", "seed", "md5", "step", "strict_load", "params")}),
                      flush=True)
                del m
        out["checkpoints"] = rows

    elif a.cmd == "flops":
        from torch.utils.flop_counter import FlopCounterMode
        res = {}
        for arch in ("pf", "hrnet"):
            m, p, *_ = load_member(torch, build_model, root, arch, 5, torch.device("cpu"))
            x = torch.zeros(1, 1, 512, 512)
            fc = FlopCounterMode(display=False)
            with torch.no_grad(), fc:
                y = m(x)
            f1 = fc.get_total_flops()
            by_op = {str(k): int(v) for k, v in fc.get_flop_counts().get("Global", {}).items()}
            fc8 = FlopCounterMode(display=False)
            with torch.no_grad(), fc8:
                TTA.predict_tta(m, x, (1.0,), True)
            res[arch] = {"ckpt": str(p), "out_shape": list(y.shape), "flops_per_view": int(f1),
                         "GFLOPs_per_view": f1 / 1e9, "GMACs_per_view": f1 / 2e9,
                         "flops_one_cell_d4_predict_tta": int(fc8.get_total_flops()),
                         "d4_over_single_ratio": fc8.get_total_flops() / f1, "flops_by_op_per_view": by_op}
            print(arch, json.dumps({k: v for k, v in res[arch].items() if k != "flops_by_op_per_view"}), flush=True)
            del m
        out["flops"] = res

    else:
        arch, n_mem, d4 = ARMS[a.arm]
        if a.views_batched and not d4:
            sys.exit("--views-batched needs a D4 arm")
        mems = []
        for s in SEEDS[:n_mem]:
            if a.no_weights:
                cfg ={"pf": {"name": "smp_unetpp", "in_channels": 1, "num_classes": 24, "encoder_weights": None},
                       "hrnet": {"name": "bench_smp", "decoder": "unetplusplus", "encoder_name": "tu-hrnet_w18",
                                 "encoder_weights": None, "in_channels": 1, "num_classes": 24}}[arch]
                mems.append(build_model(cfg).eval().to(dev))
            else:
                mems.append(load_member(torch, build_model, root, arch, s, dev)[0])
        if dev.type == "cuda":
            torch.cuda.synchronize(dev)
            torch.cuda.reset_peak_memory_stats(dev)
            mem_load = torch.cuda.memory_allocated(dev) / 2**20
        rss_load = proc_status().get("VmRSS")
        g = torch.Generator().manual_seed(1234)
        x = ((torch.rand(a.batch, 1, 512, 512, generator=g) - 0.5) / 0.25).to(dev)

        def one_member(m, xx):
            if not d4:
                return torch.softmax(m(xx).float(), 1)
            if not a.views_batched:
                return TTA.predict_tta(m, xx, (1.0,), True)          # deployed: 8 forwards of B images
            B = xx.shape[0]
            lo = m(torch.cat([TTA.d4(xx, i) for i in range(TTA.N_D4)])).float()   # 1 forward of 8 B images
            acc = None
            for i in range(TTA.N_D4):
                pi = torch.softmax(TTA.d4_inv(lo[i * B:(i + 1) * B], i), 1)
                acc = pi if acc is None else acc + pi
            return acc / TTA.N_D4

        @torch.no_grad()
        def predict(xx):
            acc = None
            for m in mems:
                p = one_member(m, xx)
                acc = p if acc is None else acc + p
            return acc / len(mems)

        for _ in range(a.warmup):
            predict(x)
        if dev.type == "cuda":
            torch.cuda.synchronize(dev)
        n_batches = -(-a.cells // a.batch)
        times, t_all = [], time.perf_counter()
        for _ in range(n_batches):
            if dev.type == "cuda":
                e0, e1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
                e0.record()
                p = predict(x)
                e1.record()
                torch.cuda.synchronize(dev)
                times.append(e0.elapsed_time(e1) / 1000.0)
            else:
                t0 = time.perf_counter()
                p = predict(x)
                times.append(time.perf_counter() - t0)
            if a.max_seconds and time.perf_counter() - t_all > a.max_seconds:
                break
        assert tuple(p.shape) == (a.batch, 24, 512, 512) and torch.isfinite(p).all()
        q = statistics.quantiles(times, n=10) if len(times) >= 2 else [times[0]] * 9
        per_cell = [t / a.batch for t in times]
        qc = statistics.quantiles(per_cell, n=10) if len(per_cell) >= 2 else [per_cell[0]] * 9
        ps = proc_status()
        out["timing"] = {
            "arm": a.arm, "arch": arch, "members": n_mem, "views_per_member": 8 if d4 else 1,
            "forwards_per_cell": n_mem * (8 if d4 else 1), "views_batched": bool(a.views_batched), "batch": a.batch,
            "images_per_forward": a.batch * (8 if a.views_batched else 1), "warmup_batches": a.warmup,
            "timed_batches": len(times), "timed_cells": len(times) * a.batch, "weights": "random init" if a.no_weights
            else "checkpoints", "batch_s_median": statistics.median(times), "batch_s_p90": q[8],
            "batch_s_min": min(times), "batch_s_max": max(times),
            "cell_s_median": statistics.median(per_cell), "cell_s_p90": qc[8], "cell_s_mean": statistics.fmean(per_cell),
            "times_s": times,
            "cpu_rss_after_load_mib": rss_load, "cpu_peak_rss_mib": ps.get("VmHWM"),
        }
        if dev.type == "cuda":
            out["timing"].update(gpu_alloc_after_load_mib=mem_load,
                                 gpu_peak_alloc_mib=torch.cuda.max_memory_allocated(dev) / 2**20,
                                 gpu_peak_reserved_mib=torch.cuda.max_memory_reserved(dev) / 2**20)
        out["env"]["loadavg_end"] = os.getloadavg()
        print(json.dumps({k: v for k, v in out["timing"].items() if k != "times_s"}), flush=True)

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1, default=str) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
