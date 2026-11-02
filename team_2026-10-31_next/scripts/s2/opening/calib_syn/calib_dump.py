"""calib (31 Oct): read-only margin dump for idea 1 (calibration) and idea 7 (scorer). CPU fp32; test cells only with --opening.

Per model (and per group ensemble = mean softmax, as m9_final / d_infer), per cell set, writes one npz:
  stems  (n,)          cell stems in order
  margin (n,512,512)   float16, m = log(p_crack+1e-12) - max_{k!=crack} log(p_k+1e-12); crack predicted at bias b iff m + b > 0
  oth    (n,512,512)   uint8, argmax over the 23 non-crack classes (the prediction wherever crack is not predicted)
  pc     (n,512,512)   float16, p(crack) (ensemble: mean softmax)
Sets: val (54), ext (E1, 106, ext117), rf (Hanifi _rf, 106 after hygiene); test (50) ONLY with --opening <protocol> at a
pre-registered opening (the calib backfill never passes it).
Usage: python calib_dump.py --code EL_F3 --out OUT --group NAME RUN [RUN ...] [--group ...] --sets val ext rf --threads 8
"""
import argparse
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
ap.add_argument("--sets", nargs="+", default=["val", "ext", "rf"], choices=["val", "ext", "rf", "test", "synval"])
ap.add_argument("--synval", default="/home/noob/work/domain_scratch/shv1", help="domain's frozen synthetic half-cut val (SHV1: images/, masks/, ignore/, stems_eval.txt, MANIFEST.md5)")
ap.add_argument("--synval-manifest", default="63dd5469cc4eeaf21025e98669d635e3", help="md5 of SHV1's MANIFEST.md5; verified with every file before reading ('' = no check, sensitivity runs only)")
ap.add_argument("--opening", default="", help="REQUIRED to include 'test': the protocol name whose pre-registered opening this is (e.g. protocol_PF2)")
ap.add_argument("--ext", default="/home/noob/work/el_f1/reports/f1/ext117")
ap.add_argument("--rf", default="/home/noob/work/calib/data/rf")
ap.add_argument("--threads", type=int, default=8)
ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"], help="cuda: bf16 autocast, batch --batch, as m0_audit (exact self-check); runner only, behind the GPU gate")
ap.add_argument("--batch", type=int, default=8)
ap.add_argument("--no-members", action="store_true", help="write only the group ensemble, not each member")
ap.add_argument("--tt", default="none", choices=["none", "cellz", "cellhist", "modz"],
                help="idea 2 test-time intensity mapping into the train distribution (diagnostic): cellz = per-cell affine to train mean/sd; "
                     "cellhist = per-cell histogram matching to the pooled train histogram; modz = per-module affine (module stats over the set's cells)")
ap.add_argument("--ref", default="/home/noob/work/calib/out/train_ref.npz", help="train reference: mean, sd, cdf (256)")
a = ap.parse_args()
assert "test" not in a.sets or a.opening, "test cells only at a pre-registered protocol opening: pass --opening <protocol>"
sys.path.insert(0, a.code)
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

CRACK = 14
torch.set_num_threads(a.threads)
if a.device == "cuda":
    torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False
OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)
D = Path(a.code) / "data"


def load(run):
    run = Path(run); cfg = load_config(run / "config_used.yaml")
    st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(st.get("step", -1)) == 20000, run
    mc = {k: v for k, v in cfg["model"].items() if k not in ("encoder_init", "decoder_init")}; mc["encoder_weights"] = None
    m = build_model(mc); m.load_state_dict(st["models"]["model"]); m.eval()
    return m.to(a.device)


REF = np.load(a.ref) if a.tt != "none" else None
MODSTAT = {}


def content(u8):
    """F6 letterbox rule: rows/cols with >= 98% px >= 250 are frame; the mapping touches content px only."""
    wr = np.mean(u8 >= 250, axis=1) > 0.98; wc = np.mean(u8 >= 250, axis=0) > 0.98
    return (~wr[:, None]) & (~wc[None, :])


def tt_map(u8, stem):
    """Map a uint8 cell's CONTENT px into the train content intensity distribution (float grey 0..255), as stated in --tt.
    Frame (white letterbox) px are left unchanged."""
    g = u8.astype(np.float32); cm = content(u8)
    if cm.sum() < 1000:
        return g
    out = g.copy(); v = g[cm]
    if a.tt == "cellz":
        out[cm] = np.clip((v - v.mean()) / max(v.std(), 1e-3) * float(REF["sd"]) + float(REF["mean"]), 0, 255)
    elif a.tt == "modz":
        mu, sd = MODSTAT["_".join(stem.split("_")[:2])]
        out[cm] = np.clip((v - mu) / max(sd, 1e-3) * float(REF["sd"]) + float(REF["mean"]), 0, 255)
    elif a.tt == "cellhist":
        h = np.bincount(u8[cm], minlength=256).astype(np.float64); c = np.cumsum(h) / h.sum()
        rc = np.maximum.accumulate(np.asarray(REF["cdf"], np.float64) + np.arange(256) * 1e-12)  # strictly increasing for interp
        lut = np.interp(c, rc, np.arange(256))  # source content quantile -> train content grey level
        out[cm] = lut[u8[cm]]
    return out


def x_of(path, stem=None):
    u8 = np.array(Image.open(path).convert("L"), np.uint8)
    g = (tt_map(u8, stem) if a.tt != "none" else u8.astype(np.float32)) / 255.0
    return torch.from_numpy((g - 0.5) / 0.25)[None, None]


def verify_manifest(root, want):
    """The MANIFEST.md5 file's own md5 must equal `want`, and every file it lists must match (as md5sum -c)."""
    import hashlib
    md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
    mf = Path(root) / "MANIFEST.md5"
    assert md5(mf) == want, f"synval MANIFEST md5 {md5(mf)} != {want}"
    n = 0
    for line in open(mf):
        if line.strip():
            h, f = line.split(None, 1); f = f.strip()
            assert md5(Path(root) / f) == h, f"synval file changed: {f}"; n += 1
    print(f"synval MANIFEST {want[:8]} OK ({n} files)", flush=True)


def cells(sp):
    if sp == "synval":  # PF2 §13: domain's frozen synthetic half-cut val (SHV1), both halves of each val cell
        root = Path(a.synval)
        if a.synval_manifest:
            verify_manifest(root, a.synval_manifest)
        st = [l.strip() for l in open(root / "stems_eval.txt") if l.strip()]
        assert len(st) == 108, ("synval", len(st))
        return [(s, root / "images" / f"{s}.png") for s in st]
    if sp in ("val", "test"):
        st = sorted(l.strip() for l in open(D / "splits" / f"{sp}.txt") if l.strip())
        assert len(st) == {"val": 54, "test": 50}[sp]
        return [(s, D / "labeled" / "images" / f"{s}.png") for s in st]
    root = Path(a.ext if sp == "ext" else a.rf)
    st = [l.strip() for l in open(root / "stems_eval.txt") if l.strip()]
    assert len(st) == 106, (sp, len(st))
    return [(s, root / "images" / f"{s}.png") for s in st]


def maps(p):
    lq = torch.log(p + 1e-12)
    pc = lq[CRACK].clone()
    lq[CRACK] = -1e30
    mo, oth = lq.max(0)
    return (pc - mo).numpy().astype(np.float16), oth.numpy().astype(np.uint8), p[CRACK].numpy().astype(np.float16)


t0 = time.time()
for g in a.group:
    name, runs = g[0], g[1:]
    if a.tt != "none":
        name = f"{name}__{a.tt}"
    ms = [load(r) for r in runs]
    print(f"[{time.time() - t0:.0f}s] group {name}: {len(ms)} models: {runs}", flush=True)
    for sp in a.sets:
        cs = cells(sp)
        if a.tt == "modz":  # module stats over the set's own cells of that module (label-free)
            acc = {}
            for s_, img_ in cs:
                u8_ = np.array(Image.open(img_).convert("L"), np.uint8)
                acc.setdefault("_".join(s_.split("_")[:2]), []).append(u8_[content(u8_)].astype(np.float64))
            MODSTAT.clear(); MODSTAT.update({k: (float(np.concatenate(v).mean()), float(np.concatenate(v).std())) for k, v in acc.items()})
        targets = ([f"{name}_m{i}" for i in range(len(ms))] if (len(ms) > 1 and not a.no_members) else []) + [name]
        if all((OUT / f"{t}.{sp}.npz").exists() for t in targets):
            print("skip", name, sp); continue
        buf = {t: (np.zeros((len(cs), 512, 512), np.float16), np.zeros((len(cs), 512, 512), np.uint8), np.zeros((len(cs), 512, 512), np.float16)) for t in targets}
        with torch.no_grad():
            B = a.batch if a.device == "cuda" else 1
            for i0 in range(0, len(cs), B):
                chunk = cs[i0:i0 + B]
                x = torch.cat([x_of(img, s) for s, img in chunk]).to(a.device)
                if a.device == "cuda":  # as m0_audit.predict: bf16 autocast, logits to float
                    with torch.autocast("cuda", dtype=torch.bfloat16):
                        lgs = [m(x) for m in ms]
                    ps = [torch.softmax(lg.float(), 1).cpu() for lg in lgs]
                else:
                    ps = [torch.softmax(m(x).float(), 1) for m in ms]
                for k_, (s, img) in enumerate(chunk):
                    i = i0 + k_
                    outs = {name: sum(p[k_] for p in ps) / len(ps)}
                    if len(ms) > 1 and not a.no_members:
                        outs.update({f"{name}_m{j}": p[k_] for j, p in enumerate(ps)})
                    for t, p in outs.items():
                        mg, oth, pc = maps(p)
                        buf[t][0][i], buf[t][1][i], buf[t][2][i] = mg, oth, pc
        for t, (mg, oth, pc) in buf.items():
            np.savez(OUT / f"{t}.{sp}.npz", stems=np.array([s for s, _ in cs]), margin=mg, oth=oth, pc=pc,
                     runs=np.array(runs if t == name else [runs[int(t.rsplit("_m", 1)[1])]]))
        print(f"[{time.time() - t0:.0f}s] {name} {sp}: {len(cs)} cells -> {targets}", flush=True)
print(f"DONE {time.time() - t0:.0f}s", flush=True)
