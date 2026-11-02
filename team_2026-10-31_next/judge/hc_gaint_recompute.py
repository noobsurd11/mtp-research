"""judge hc_gaint_recompute (2 Nov 2026): own-code recompute of protocol_HC v1.1 decision readouts that need the gaint dumps.
Imports nothing from a8_screen_score / el_metrics / calib_dump / hc_*. CPU only (numpy / scipy).
  f51  : F51 crack AP (1,000-bin, the rule; and fp16-exact), arm means over seeds, d = TEST - BASE; paired 36-module bootstrap
         (2,000, numpy default_rng(0), the a8_screen_score stream); HC guard FAIL iff 97.5% < 0. Extra: seed-aware two-stage bootstrap
         (modules + seeds drawn with replacement per arm), per seed, leave-one-crack-module-out, FA px on crack-free H36 / F51 at b 0.
  shv1 : per arm, cells pooled over seeds: relP@2 / relR@2 over GRID (-4..+12 step 0.1 + 0.75); matched relR@2 = max relR s.t.
         relP >= 0.90 (GRID incl. 0.75); oracle b = argmax relF1@2 on the OP grid (ties smaller b); relR@2 / relP@2 at b 0. Sets:
         V0 (val 54), SHV1 (108), SHV1-p (--shv1p list, 80). Mechanism: matched SHV1 relR@2 TEST - BASE vs +0.05.
Reads only val / rf / synval dumps and their masks; never test or E1.
Usage: python -B hc_gaint_recompute.py f51  --dump DIR --arm NAME RUN [RUN ..] --arm ... --test NAME --base NAME --out TXT
       python -B hc_gaint_recompute.py shv1 --dump-val DIR --dump-syn DIR --arm NAME RUN [..] --arm ... [--test N --base N] [--shv1p F] --out TXT
"""
import argparse
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["f51", "shv1"])
ap.add_argument("--dump"); ap.add_argument("--dump-val"); ap.add_argument("--dump-syn")
ap.add_argument("--arm", nargs="+", action="append", default=[])
ap.add_argument("--test"); ap.add_argument("--base")
ap.add_argument("--labeled", default="/home/noob/work/el-fault-detection/data/labeled")
ap.add_argument("--rf", default="/home/noob/work/calib/data/rf")
ap.add_argument("--rf-sets", default="/home/noob/work/found/t9/rf_sets.tsv")
ap.add_argument("--shv1", default="/home/noob/work/domain_scratch/shv1")
ap.add_argument("--shv1p", default="/home/noob/work/domain_scratch/out/shv1p_stems_eval.txt")
ap.add_argument("--forbid", nargs="*", default=["/home/noob/work/el_f8/data/splits/test.txt", "/home/noob/work/el_f1/reports/f1/ext117/stems.txt"])
ap.add_argument("--out", required=True)
a = ap.parse_args()
ARMS = {x[0]: x[1:] for x in a.arm}
LOG = open(a.out, "w")
CR, IN = 14, 11
OPB = np.round(np.arange(-40, 121) / 10.0, 1)
GRID = np.unique(np.concatenate([OPB, [0.75]]))
OPMASK = np.isin(GRID, OPB)
NCODE = 15361
OFFS = [(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3) if dy * dy + dx * dx <= 4]
FORB = set()
for f in a.forbid:
    FORB |= {l.strip() for l in open(f) if l.strip()}


def say(*x):
    s = " ".join(str(v) for v in x); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


def load(path):
    z = np.load(path); st = [str(s) for s in z["stems"]]
    assert not set(st) & FORB, f"FORBIDDEN stem in {path}"
    return z, st


def ap_hist(pos, neg):
    tp = np.cumsum(pos[::-1]).astype(float); fp = np.cumsum(neg[::-1]).astype(float); n = pos.sum()
    if n == 0:
        return float("nan")
    prec = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) > 0)
    return float(np.sum(prec * np.diff(np.concatenate([[0.0], tp / n]))))


def dil2(m):
    H, W = m.shape; p = np.full((H + 4, W + 4), -np.inf, np.float32); p[2:-2, 2:-2] = m
    out = np.full((H, W), -np.inf, np.float32)
    for dy, dx in OFFS:
        np.maximum(out, p[2 + dy:2 + dy + H, 2 + dx:2 + dx + W], out=out)
    return out


def rel_counts(args):
    m, g, k = args
    m = np.where(k, m, -np.inf).astype(np.float32); gc = (g == CR) & k; ng = int(gc.sum())
    near = (ndi.distance_transform_edt(~gc) <= 2) & k if ng else np.zeros(g.shape, bool)
    cnt = lambda s: len(s) - np.searchsorted(s, -GRID, side="right")
    return cnt(np.sort(m[k])), cnt(np.sort(m[near])), cnt(np.sort(dil2(m)[gc])), ng


# ======================================================================= f51
if a.mode == "f51":
    rows = [l.rstrip("\n").split("\t") for l in open(a.rf_sets) if l.strip()][1:]
    SET = {r[0]: r[1] for r in rows}; MOD = {r[0]: r[3] for r in rows}
    code_val = np.arange(NCODE, dtype=np.uint16).view(np.float16).astype(np.float32)
    bin_of = np.clip((code_val * 1000).astype(int), 0, 999)
    GT = {}
    H, FA0 = {}, {}
    for arm, runs in ARMS.items():
        for r in runs:
            z, st = load(Path(a.dump) / f"{r}.rf.npz"); assert len(st) == 106 and all(s in SET for s in st)
            codes = z["pc"].view(np.uint16); assert int(codes.max()) < NCODE
            mg = z["margin"]; H[r] = {}; FA0[r] = {"H36": 0, "F51": 0}
            for i, s in enumerate(st):
                if s not in GT:
                    GT[s] = (np.array(Image.open(Path(a.rf) / "masks" / f"{s}.png")), ~(np.array(Image.open(Path(a.rf) / "ignore" / f"{s}.png")) > 0))
                g, k = GT[s]; t = (g == CR) & k
                H[r][s] = (np.bincount(codes[i][t], minlength=NCODE), np.bincount(codes[i][k & ~t], minlength=NCODE), int(t.sum()))
                if SET[s] in FA0[r] and int(t.sum()) == 0:
                    FA0[r][SET[s]] += int(((mg[i].astype(np.float32) > 0) & k).sum())
            del z
    F51 = [s for s in SET if SET[s] == "F51"]; mods = sorted({MOD[s] for s in F51}); by = {m: [s for s in F51 if MOD[s] == m] for m in mods}
    ngt = {s: H[next(iter(H))][s][2] for s in F51}

    def ap_of(r, stems, binned=True):
        P = np.sum([H[r][s][0] for s in stems], 0); N = np.sum([H[r][s][1] for s in stems], 0)
        if binned:
            P, N = np.bincount(bin_of, P, 1000), np.bincount(bin_of, N, 1000)
        return ap_hist(P, N)
    T, B = ARMS[a.test], ARMS[a.base]
    say(f"F51 cells {len(F51)} modules {len(mods)} crack cells {sum(ngt[s] >= 20 for s in F51)} crack px {sum(ngt.values())}")
    for r in T + B:
        say(f"{r}: F51 AP 1000-bin {ap_of(r, F51):.6f} fp16 {ap_of(r, F51, False):.6f} | FA px at b 0: H36 {FA0[r]['H36']} F51 {FA0[r]['F51']}")
    for binned, nm in ((True, "1000-bin"), (False, "fp16-exact")):
        d = np.mean([ap_of(r, F51, binned) for r in T]) - np.mean([ap_of(r, F51, binned) for r in B])
        MH = {r: (np.stack([np.sum([H[r][s][0] for s in by[m]], 0) for m in mods]).astype(float),
                  np.stack([np.sum([H[r][s][1] for s in by[m]], 0) for m in mods]).astype(float)) for r in T + B}
        if binned:
            MH = {r: (np.stack([np.bincount(bin_of, p, 1000) for p in P]), np.stack([np.bincount(bin_of, n, 1000) for n in N])) for r, (P, N) in MH.items()}
        f = lambda r, c: ap_hist(c @ MH[r][0], c @ MH[r][1])
        rng = np.random.default_rng(0); bs = []
        for _ in range(2000):
            c = np.bincount(rng.integers(0, len(mods), len(mods)), minlength=len(mods)).astype(float)
            bs.append(np.mean([f(r, c) for r in T]) - np.mean([f(r, c) for r in B]))
        bs = np.array(bs)
        say(f"{nm}: d {a.test}-{a.base} {d:+.4f} | module boot (seed 0) 2.5% {np.percentile(bs, 2.5):+.4f} 97.5% {np.percentile(bs, 97.5):+.4f} "
            f"P(d*<0) {np.mean(bs < 0):.3f} | HC guard (FAIL iff 97.5% < 0): {'FAIL' if np.percentile(bs, 97.5) < 0 else 'pass'}")
        if binned:
            rng = np.random.default_rng(0); rs = np.random.default_rng(1); b2 = []
            for _ in range(2000):
                c = np.bincount(rng.integers(0, len(mods), len(mods)), minlength=len(mods)).astype(float)
                b2.append(np.mean([f(T[i], c) for i in rs.integers(0, len(T), len(T))]) - np.mean([f(B[i], c) for i in rs.integers(0, len(B), len(B))]))
            say(f"two-stage (modules + seeds with replacement): 2.5% {np.percentile(b2, 2.5):+.4f} 97.5% {np.percentile(b2, 97.5):+.4f}")
    cm = [m for m in mods if any(ngt[s] >= 20 for s in by[m])]
    for m in cm:
        rest = [s for s in F51 if MOD[s] != m]
        dm = np.mean([ap_of(r, by[m]) for r in T]) - np.mean([ap_of(r, by[m]) for r in B])
        dl = np.mean([ap_of(r, rest) for r in T]) - np.mean([ap_of(r, rest) for r in B])
        say(f"  {m}: crack px {sum(ngt[s] for s in by[m])} module dAP {dm:+.4f} | F51 without it d {dl:+.4f}")
    say("DONE")

# ======================================================================= shv1
else:
    sv = Path(a.shv1); ig = (sv / "ignore").is_dir()
    p80 = {l.strip() for l in open(a.shv1p) if l.strip()} if a.shv1p else set()
    GTC = {}

    def gt(set_, s):
        if (set_, s) not in GTC:
            if set_ == "val":
                g = np.array(Image.open(Path(a.labeled) / "masks_escdd" / f"{s}.png")); k = np.ones(g.shape, bool)
            else:
                g = np.array(Image.open(sv / "masks" / f"{s}.png")); k = ~(np.array(Image.open(sv / "ignore" / f"{s}.png")) > 0) if ig else np.ones(g.shape, bool)
            GTC[(set_, s)] = (g, k)
        return GTC[(set_, s)]
    C = {}
    for arm, runs in ARMS.items():
        for r in runs:
            for set_, d in (("val", a.dump_val), ("synval", a.dump_syn)):
                z, st = load(Path(d) / f"{r}.{set_}.npz"); assert len(st) == {"val": 54, "synval": 108}[set_], (r, set_, len(st))
                mg = z["margin"]
                with Pool(8) as p:
                    out = p.map(rel_counts, [(mg[i].astype(np.float32), *gt(set_, s)) for i, s in enumerate(st)], chunksize=2)
                C[(r, set_)] = dict(zip(st, out)); del z, mg
            say(f"loaded {r}")

    def curve(runs, set_, keep=None):
        pr = rp = rr = 0; ng = 0
        for r in runs:
            for s, (a0, a1, a2, n) in C[(r, set_)].items():
                if keep is None or s in keep:
                    pr = pr + a0; rp = rp + a1; rr = rr + a2; ng += n
        P = np.where(pr > 0, rp / np.maximum(pr, 1), np.nan); R = rr / max(ng, 1)
        F = np.where((P + R) > 0, 2 * P * R / np.maximum(P + R, 1e-12), 0.0)
        ok = np.nan_to_num(P, nan=-1) >= 0.90
        matched = float(np.max(R[ok])) if ok.any() else float("nan")
        jo = np.where(OPMASK)[0]; jb = int(jo[np.argmax(np.nan_to_num(F[jo], nan=-1))])
        j0 = int(np.where(GRID == 0.0)[0][0])
        return {"matched": matched, "oracle_b": float(GRID[jb]), "relR_b0": float(R[j0]), "relP_b0": float(P[j0])}
    res = {}
    for arm, runs in ARMS.items():
        res[arm] = {"V0": curve(runs, "val"), "SHV1": curve(runs, "synval"), "SHV1p": curve(runs, "synval", p80) if p80 else None}
        for k, v in res[arm].items():
            if v:
                say(f"{arm} {k}: matched relR@2 (relP>=0.90, GRID incl 0.75) {v['matched']:.4f} | oracle b {v['oracle_b']:+.1f} | relR@2 b0 {v['relR_b0']:.4f} relP@2 b0 {v['relP_b0']:.4f}")
        say(f"{arm}: bias gap (oracle b SHV1 - V0) {res[arm]['SHV1']['oracle_b'] - res[arm]['V0']['oracle_b']:+.1f}")
        for r in runs:
            say(f"  {r}: SHV1 matched {curve([r], 'synval')['matched']:.4f} V0 matched {curve([r], 'val')['matched']:.4f}")
    if a.test and a.base:
        d = res[a.test]["SHV1"]["matched"] - res[a.base]["SHV1"]["matched"]
        say(f"MECHANISM: matched SHV1 relR@2 {a.test} - {a.base} = {d:+.4f} (kill if < +0.05): {'FAILED' if d < 0.05 else 'held'}")
        if p80:
            say(f"  SHV1-p: {res[a.test]['SHV1p']['matched'] - res[a.base]['SHV1p']['matched']:+.4f}; V0: {res[a.test]['V0']['matched'] - res[a.base]['V0']['matched']:+.4f}")
    say("DONE")
