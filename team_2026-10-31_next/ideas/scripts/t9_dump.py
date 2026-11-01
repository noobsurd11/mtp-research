"""t9_dump (found, 31 Oct 2026): T9 per-panel AdaBN dumps (ideas/t9_prereg.md), in calib's npz format so that calib's
el_metrics.py `records --set rf` scores them unchanged. Model loading, input normalisation and margin maps are copied from
calib_dump.py (md5 4badccb4) without the --tt intensity modes; BN re-estimation follows D's d_infer.py bn_reestimate.
CPU only (run with CUDA_VISIBLE_DEVICES=""); reads the Hanifi _rf set only (no E1, no test, no val).

npz per target (member or ensemble): stems (n,), margin (n,512,512) f16, oth (n,512,512) u8, pc (n,512,512) f16, runs.
Modes:
  v0     source BN.                                  --img rf   : all 106 cells on the E-SCDD _rf images (self-check vs calib)
                                                     --img pool : eligible cells on their pool copies (T9's V0)
  hc     BN-HC as D (all BN from the 986 pool half-cells), half-cut eligible cells only, pool copies   -> {name}__V1
  panel  per module, all BN re-estimated from that module's pool cells (cumulative mean, train mode, no grad, batch 8)
         -> {name}__V2; the same pass with only encoder bn1 / layer1 / layer2 BN taken from the panel -> {name}__V3
Eligible = the _rf cell has a pool copy and its module has >= --min-sib pool cells (t9_prereg.md §2: 88 cells).
Usage: python t9_dump.py --code EL_F3 --out DIR --mode panel --group NAME RUN [RUN ...] [--group ...] --threads 8
"""
import argparse
import collections
import copy
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--group", nargs="+", action="append", required=True, help="NAME RUN [RUN ...]")
ap.add_argument("--mode", required=True, choices=["v0", "hc", "panel"])
ap.add_argument("--img", default="pool", choices=["pool", "rf"])
ap.add_argument("--rf", default="/home/noob/work/calib/data/rf")
ap.add_argument("--pool", default="/home/noob/work/el-fault-detection/data/unlabeled/images_512")
ap.add_argument("--hc-inv", default="/home/noob/work/sa-unetpp-ssl-el/data/unlabeled/_inventory.json")
ap.add_argument("--hc-list", default="/home/noob/work/el_f1/reports/f1/mim_pool_v11.txt")
ap.add_argument("--min-sib", type=int, default=20)
ap.add_argument("--bs", type=int, default=8)
ap.add_argument("--threads", type=int, default=8)
ap.add_argument("--limit-modules", type=int, default=0, help="smoke only")
a = ap.parse_args()
assert a.mode == "v0" or a.img == "pool", "BN variants score pool copies only (t9_prereg.md gate 1)"
assert not torch.cuda.is_available(), "T9 is CPU-only: run with CUDA_VISIBLE_DEVICES=''"
sys.path.insert(0, a.code)
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

CRACK = 14
SHALLOW = ("encoder.bn1", "encoder.layer1.", "encoder.layer2.")
torch.set_num_threads(a.threads)
OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)
RF, POOL = Path(a.rf), Path(a.pool)
mod = lambda s: "_".join(s.split("_")[:2])


def load(run):  # = calib_dump.load
    run = Path(run); cfg = load_config(run / "config_used.yaml")
    st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(st.get("step", -1)) == 20000, run
    mc = {k: v for k, v in cfg["model"].items() if k not in ("encoder_init", "decoder_init")}; mc["encoder_weights"] = None
    m = build_model(mc); m.load_state_dict(st["models"]["model"]); m.eval()
    return m


def x_of(path):  # = calib_dump.x_of with --tt none
    g = np.array(Image.open(path).convert("L"), np.uint8).astype(np.float32) / 255.0
    return torch.from_numpy((g - 0.5) / 0.25)[None, None]


def maps(p):  # = calib_dump.maps
    lq = torch.log(p + 1e-12)
    pc = lq[CRACK].clone()
    lq[CRACK] = -1e30
    mo, oth = lq.max(0)
    return (pc - mo).numpy().astype(np.float16), oth.numpy().astype(np.uint8), p[CRACK].numpy().astype(np.float16)


def bns(m):
    return [(n, x) for n, x in m.named_modules() if isinstance(x, torch.nn.modules.batchnorm._BatchNorm)]


@torch.no_grad()
def bn_estimate(m, paths):  # = d_infer.bn_reestimate (reset, cumulative average, train mode, no grad)
    m2 = copy.deepcopy(m)
    for _, x in bns(m2):
        x.reset_running_stats(); x.momentum = None
    m2.train()
    for i in range(0, len(paths), a.bs):
        m2(torch.cat([x_of(p) for p in paths[i:i + a.bs]]))
    m2.eval()
    return m2


def shallow_from(src, adapted):
    m3 = copy.deepcopy(src); sd = adapted.state_dict(); n = 0
    for name, x in bns(m3):
        if name.startswith(SHALLOW):
            for buf in ("running_mean", "running_var", "num_batches_tracked"):
                getattr(x, buf).copy_(sd[f"{name}.{buf}"])
            n += 1
    assert n > 0, "no shallow BN layer matched"
    return m3, n


# ---------------------------------------------------------------- cells
stems_all = [l.strip() for l in open(RF / "stems_eval.txt") if l.strip()]
assert len(stems_all) == 106
rows = [l.rstrip("\n").split("\t") for l in open(RF / "rf_context.tsv") if l.strip()]
H = {h: i for i, h in enumerate(rows[0])}
halfcut = {r[0]: r[H["halfcut"]] == "1" for r in rows[1:]}
pool_stems = sorted(p.stem for p in POOL.glob("*.png"))
assert len(pool_stems) == 11938, len(pool_stems)
pool_by_mod = collections.defaultdict(list)
for s in pool_stems:
    pool_by_mod[mod(s)].append(POOL / f"{s}.png")
eligible = [s for s in stems_all if (POOL / f"{s[:-3]}.png").exists() and len(pool_by_mod[mod(s)]) >= a.min_sib]
if a.mode == "v0" and a.img == "rf":
    cells = stems_all
elif a.mode == "hc":
    cells = [s for s in eligible if halfcut[s]]
else:
    cells = eligible
img_of = (lambda s: RF / "images" / f"{s}.png") if a.img == "rf" else (lambda s: POOL / f"{s[:-3]}.png")
mods = collections.OrderedDict()
for s in cells:
    mods.setdefault(mod(s), []).append(s)
if a.limit_modules:
    keep = list(mods)[: a.limit_modules]; mods = collections.OrderedDict((k, mods[k]) for k in keep); cells = [s for k in keep for s in mods[k]]
idx = {s: i for i, s in enumerate(cells)}
meta = {"mode": a.mode, "img": a.img, "n_cells": len(cells), "n_eligible": len(eligible), "min_sib": a.min_sib,
        "modules": {k: {"scored": v, "n_sib": len(pool_by_mod[k]),
                        "sib_md5": hashlib.md5("\n".join(str(p) for p in pool_by_mod[k]).encode()).hexdigest()[:8]} for k, v in mods.items()}}
if a.mode == "hc":
    inv = json.load(open(a.hc_inv))
    half = {Path(e["name"]).stem for e in inv if "half" in e.get("rel", "").lower()}
    hc_paths = [Path(a.code) / "data" / r.strip() for r in open(a.hc_list) if r.strip().startswith("unlabeled/") and Path(r.strip()).stem in half]
    assert len(hc_paths) == 986, len(hc_paths)
    meta["hc_n"] = len(hc_paths)
print(json.dumps({k: v for k, v in meta.items() if k != "modules"}), f"modules {len(mods)}", flush=True)

# ---------------------------------------------------------------- run
t0 = time.time()
for g in a.group:
    name, runs = g[0], g[1:]
    ms = [load(r) for r in runs]
    tags = {"v0": ["V0" if a.img == "pool" else "V0rf"], "hc": ["V1"], "panel": ["V2", "V3"]}[a.mode]
    n = len(cells)
    buf = {(t, j): (np.zeros((n, 512, 512), np.float16), np.zeros((n, 512, 512), np.uint8), np.zeros((n, 512, 512), np.float16))
           for t in tags for j in list(range(len(ms))) + ["ens"]}
    with torch.no_grad():
        hc_models = [bn_estimate(m, hc_paths) for m in ms] if a.mode == "hc" else None
        for k, (mname, sts) in enumerate(mods.items()):
            per = {t: {s: [] for s in sts} for t in tags}
            for j, m in enumerate(ms):
                if a.mode == "v0":
                    vm = {tags[0]: m}
                elif a.mode == "hc":
                    vm = {"V1": hc_models[j]}
                else:
                    m2 = bn_estimate(m, pool_by_mod[mname]); m3, nsh = shallow_from(m, m2)
                    vm = {"V2": m2, "V3": m3}
                for s in sts:
                    x = x_of(img_of(s))
                    for t, mm in vm.items():
                        p = torch.softmax(mm(x).float(), 1)[0]
                        per[t][s].append(p)
                        mg, oth, pc = maps(p); i = idx[s]
                        buf[(t, j)][0][i], buf[(t, j)][1][i], buf[(t, j)][2][i] = mg, oth, pc
            for t in tags:
                for s in sts:
                    mg, oth, pc = maps(sum(per[t][s]) / len(per[t][s])); i = idx[s]
                    buf[(t, "ens")][0][i], buf[(t, "ens")][1][i], buf[(t, "ens")][2][i] = mg, oth, pc
            print(f"[{time.time() - t0:.0f}s] {name} module {k + 1}/{len(mods)} {mname}: {len(sts)} cells, {len(pool_by_mod[mname])} sib", flush=True)
    for (t, j), (mg, oth, pc) in buf.items():
        tgt = f"{name}__{t}" + ("" if j == "ens" else f"_m{j}")
        np.savez(OUT / f"{tgt}.rf.npz", stems=np.array(cells), margin=mg, oth=oth, pc=pc,
                 runs=np.array(runs if j == "ens" else [runs[j]]))
    print(f"[{time.time() - t0:.0f}s] {name}: wrote {[f'{name}__{t}' for t in tags]} (+ members)", flush=True)
json.dump(meta, open(OUT / f"meta_{a.mode}_{a.img}.json", "w"), indent=1)
print(f"DONE {time.time() - t0:.0f}s", flush=True)
