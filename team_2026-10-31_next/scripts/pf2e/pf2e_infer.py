"""PF2E (protocol_PF2E.md v1, locked 1 Nov 14:28): E-g (pf2_SUP_100pct_s5..9) vs E-PF (pf2_SUPPF_100pct_s5..9), 5-member
mean-softmax ensembles, final weights, TTA off. Inference only, gaint CPU fp32 (nice 19, <= 8 threads), as D's d_infer.py
(129edac4; same image read x_of, same Track M m_common.cell_stats 10f0d37c, same crack bias: log p, + b on crack, argmax; p(crack)
renormalised). Order (each step's file written before the next set is read):
  1. VAL GATE: member s5 of each arm alone vs its PF2-opening m0 JSON (GPU bf16), val pooled crack IoU and relF1@2 at b 0,
     |delta| <= 0.005, else exit 3 before any test / E1 cell (pf2e_gate.txt).
  2. VAL sweep b in {0, 0.25, ..., 3} per ensemble; FINAL's rule D2 exactly as Track M m9_final.py: the smallest b with val
     relR@2 >= 0.90, used if its relP@2 >= 0.90, else the b with max val relF1@2; headline b = 0 if val crack (pixel) precision
     drops by > 0.05 from b 0 to the chosen b. Decisions -> pf2e_val_decisions.json BEFORE any test / E1 inference.
  3. TEST (50; plus test_noscuff = the 236 raw class-25 px of ARTS_00047_r3_c1 / ARTS_00051_r3_c2 ignored, descriptive) and
     E1 (ext117, 106, its ignore masks) at b 0 and at each ensemble's chosen and headline b. Outputs, m0 per-cell format
     ({"run", "step", "code_revision", "bias", "cells": {"val", "test", "test_noscuff", "ext"}}): <out>/<E>.b<b>.json.
Usage: python pf2e_infer.py --code EL_F3 --tm DIR_WITH_m_common --out OUT --eg 5 runs --epf 5 runs --m0ref PF2_M0_DIR [--threads 8]
       [--gate-only]
"""
import argparse, hashlib, json, sys, time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True); ap.add_argument("--tm", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--eg", nargs=5, required=True); ap.add_argument("--epf", nargs=5, required=True); ap.add_argument("--m0ref", required=True)
ap.add_argument("--ext", default="/home/noob/work/el_f1/reports/f1/ext117")
ap.add_argument("--raw-test", default="/home/noob/work/el-fault-detection/data/escdd_masks/test")
ap.add_argument("--threads", type=int, default=8); ap.add_argument("--gate-only", action="store_true")
a = ap.parse_args()
sys.path.insert(0, a.code); sys.path.insert(0, a.tm)
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402
from m_common import NC, CRACK, cell_stats  # noqa: E402

torch.set_num_threads(a.threads)
OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)
D = Path(a.code) / "data"
GRID = [round(0.25 * i, 2) for i in range(13)]
SCUFF = {"ARTS_00047_r3_c1": 34, "ARTS_00051_r3_c2": 202}
t0 = time.time()


def load(run):  # as d_infer.py 129edac4
    run = Path(run); cfg = load_config(run / "config_used.yaml")
    st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(st.get("step", -1)) == 20000, run
    mc = {k: v for k, v in cfg["model"].items() if k not in ("encoder_init", "decoder_init")}; mc["encoder_weights"] = None
    m = build_model(mc); m.load_state_dict(st["models"]["model"]); m.eval()
    rv = run.parent.parent / "REVISION"
    return m, {"run": run.name, "revision": rv.read_text().strip() if rv.exists() else "?"}


def x_of(path):  # as d_infer.py 129edac4
    g = np.array(Image.open(path).convert("L"), np.float32) / 255.0
    return torch.from_numpy((g - 0.5) / 0.25)[None, None]


def stats(p, gt, keep, bias):  # as d_infer.py 129edac4
    lq = torch.log(p + 1e-12)
    if bias:
        lq[CRACK] += bias
    pc = (p[CRACK] if not bias else torch.softmax(lq, 0)[CRACK]).numpy()
    return cell_stats(lq.argmax(0).numpy(), gt, keep, pc)


def summ(cs):  # pooled, as Track M m9_final.summ (crack / inactive / relaxed)
    C = sum(np.array(v["conf"], np.int64).reshape(NC, NC) for v in cs.values())
    tp = np.diag(C).astype(float); g = C.sum(1); p = C.sum(0); den = g + p - tp
    rel = np.sum([v["crack_rel2"] for v in cs.values()], 0); rP, rR = rel[0] / max(rel[1], 1), rel[2] / max(rel[3], 1)
    return {"crack_iou": float(tp[CRACK] / max(den[CRACK], 1)), "crack_P": float(tp[CRACK] / max(p[CRACK], 1)),
            "relP2": float(rP), "relR2": float(rR), "relF1": float(2 * rP * rR / max(rP + rR, 1e-9)), "inact_iou": float(tp[11] / max(den[11], 1))}


md5 = lambda f: hashlib.md5(open(f, "rb").read()).hexdigest()
# one opening only: refuse to run the val decisions / test / E1 part twice into the same output dir
if not a.gate_only and ((OUT / "pf2e_val_decisions.json").exists() or list(OUT.glob("E-*.json"))):
    sys.exit(f"refusing: {OUT} already holds PF2E decisions / outputs (E1 opening #4 is read once)")
assert md5(Path(a.tm) / "m_common.py").startswith("10f0d37c"), "m_common.py is not Track M's 10f0d37c"
assert [Path(r).name for r in a.eg] == [f"pf2_SUP_100pct_s{k}" for k in range(5, 10)], a.eg
assert [Path(r).name for r in a.epf] == [f"pf2_SUPPF_100pct_s{k}" for k in range(5, 10)], a.epf
EG = [load(r) for r in a.eg]; EPF = [load(r) for r in a.epf]
assert all(m[1]["revision"] == "e544133" for m in EG + EPF)
meta = {"E-g": [m[1]["run"] for m in EG], "E-PF": [m[1]["run"] for m in EPF], "script_md5": md5(__file__), "m_common_md5": md5(Path(a.tm) / "m_common.py"),
        "ext_stems_md5": md5(Path(a.ext) / "stems_eval.txt"), "device": "cpu fp32", "threads": a.threads}
print(json.dumps(meta), flush=True)
ARMS = {"E-g": [m for m, _ in EG], "E-PF": [m for m, _ in EPF]}
val = sorted(l.strip() for l in open(D / "splits" / "val.txt") if l.strip()); assert len(val) == 54

# ---- 1 + 2: VAL (gate members, ensemble sweep) in one pass over val
gate_cells = {k: {} for k in ARMS}; sweep_cells = {k: {b: {} for b in GRID} for k in ARMS}
with torch.no_grad():
    for s in val:
        x = x_of(D / "labeled" / "images" / f"{s}.png"); gt = np.array(Image.open(D / "escdd_masks" / "val" / f"{s}.png"))
        for k, ms in ARMS.items():
            P = [torch.softmax(m(x).float(), 1)[0] for m in ms]
            gate_cells[k][s] = stats(P[0], gt, None, 0.0)
            pe = sum(P) / len(P)
            for b in GRID:
                sweep_cells[k][b][s] = stats(pe, gt, None, b)
print(f"val done, {time.time() - t0:.0f} s", flush=True)
L, bad = ["PF2E gate: member s5 of each arm alone, val pooled, b 0: gaint CPU fp32 vs its PF2-opening m0 JSON (GPU bf16); tolerance 0.005"], False
for k, ms in (("E-g", EG), ("E-PF", EPF)):
    r5 = ms[0][1]["run"]; ref = json.load(open(Path(a.m0ref) / f"{r5}.json"))["cells"]["val"]
    me, rf = summ(gate_cells[k]), summ({s: ref[s] for s in val})
    for q in ("crack_iou", "relF1"):
        d = me[q] - rf[q]; bad |= abs(d) > 0.005; L.append(f"  {k} {r5} {q}: {me[q]:.4f} (ref {rf[q]:.4f}, delta {d:+.4f})")
L.append("  -> " + ("FAIL: stop before any test / E1 cell" if bad else "within tolerance: proceed"))
(OUT / "pf2e_gate.txt").write_text("\n".join(L) + "\n"); print("\n".join(L), flush=True)
if bad:
    sys.exit(3)
if a.gate_only:
    print("gate-only: stopping before the val decisions and any test / E1 cell", flush=True); sys.exit(0)
dec = {"rule": "FINAL D2 (Track M m9_final.py): smallest b in 0..3 step 0.25 with val relR@2 >= 0.90, used if its relP@2 >= 0.90, "
               "else max val relF1@2; headline b 0 if val crack precision drops by > 0.05 from b 0 to the chosen b", "meta": meta}
for k in ARMS:
    sw = {b: summ(sweep_cells[k][b]) for b in GRID}
    ok = [b for b in GRID if sw[b]["relR2"] >= 0.90]
    if ok and sw[ok[0]]["relP2"] >= 0.90:
        bias, why = ok[0], "smallest bias with val relR@2 >= 0.90 and relP@2 >= 0.90"
    else:
        bias = max(GRID, key=lambda b: sw[b]["relF1"]); why = "max val relF1@2"
    width = sw[0.0]["crack_P"] - sw[bias]["crack_P"]
    dec[k] = {"bias": bias, "why": why, "val_crack_precision_drop_at_bias": width, "headline_bias": 0.0 if width > 0.05 else bias,
              "sweep": {str(b): v for b, v in sw.items()}}
(OUT / "pf2e_val_decisions.json").write_text(json.dumps(dec, indent=1))
print(f"val decisions written (md5 {md5(OUT / 'pf2e_val_decisions.json')}): " +
      "; ".join(f"{k} b {dec[k]['bias']} ({dec[k]['why']}), headline {dec[k]['headline_bias']}" for k in ARMS), flush=True)

# ---- 3: TEST + E1 at b 0 and at each ensemble's chosen / headline b
BS = {k: sorted({0.0, dec[k]["bias"], dec[k]["headline_bias"]}) for k in ARMS}
res = {k: {b: {"val": {s: sweep_cells[k][b][s] for s in val}, "test": {}, "test_noscuff": {}, "ext": {}} for b in BS[k]} for k in ARMS}
test = sorted(l.strip() for l in open(D / "splits" / "test.txt") if l.strip())
test = [s for s in test if (D / "escdd_masks" / "test" / f"{s}.png").exists()]; assert len(test) == 50
ext = [l.strip() for l in open(Path(a.ext) / "stems_eval.txt") if l.strip()]; assert len(ext) == 106
with torch.no_grad():
    for sp, stems in (("test", test), ("ext", ext)):
        for s in stems:
            if sp == "test":
                img, gt, keep = D / "labeled" / "images" / f"{s}.png", np.array(Image.open(D / "escdd_masks" / "test" / f"{s}.png")), None
            else:
                img = Path(a.ext) / "images" / f"{s}.png"; gt = np.array(Image.open(Path(a.ext) / "masks" / f"{s}.png"))
                keep = ~(np.array(Image.open(Path(a.ext) / "ignore" / f"{s}.png")) > 0)
            x = x_of(img)
            for k, ms in ARMS.items():
                pe = sum(torch.softmax(m(x).float(), 1)[0] for m in ms) / len(ms)
                for b in BS[k]:
                    res[k][b][sp][s] = stats(pe, gt, keep, b)
                    if sp == "test" and s in SCUFF:
                        sc = np.array(Image.open(Path(a.raw_test) / f"{s}.png")) == 25
                        assert int(sc.sum()) == SCUFF[s] and int((gt[sc] == CRACK).sum()) == SCUFF[s]
                        res[k][b]["test_noscuff"][s] = stats(pe, gt, ~sc, b)
                    elif sp == "test":
                        res[k][b]["test_noscuff"][s] = res[k][b]["test"][s]
        print(f"{sp} done, {time.time() - t0:.0f} s", flush=True)
for k in ARMS:
    for b in BS[k]:
        f = OUT / f"{k}.b{b:g}.json"
        f.write_text(json.dumps({"run": k, "members": meta[k], "step": 20000, "code_revision": "e544133", "bias": b,
                                 "chosen_bias": dec[k]["bias"], "headline_bias": dec[k]["headline_bias"], "cells": res[k][b]}))
print(f"PF2E inference done, {time.time() - t0:.0f} s; files: " + ", ".join(sorted(p.name for p in OUT.glob("E-*.json"))), flush=True)
