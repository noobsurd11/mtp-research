"""SKR2E (protocol_SKR2E.md v1, locked 2 Nov 21:59, md5 cbc3e015): E-PF (pf2_SUPPF_100pct_s5..9, el_f3 e544133) vs E-SKR2
(skr2_SKR01_100pct_s5..9, el_thin c9bbb02), 5-member mean-softmax ensembles, final weights, TTA off. Inference only, gaint CPU
fp32 (nice 19, <= 8 threads). = pf2e_infer.py 272463d3 with only the protocol §6 changes (arms, per-arm REVISION, per-arm m0 gate
reference, union of b's, extra gates / checks, E1 aggregate sweep); same image read x_of, same Track M m_common.cell_stats
10f0d37c, same crack bias (log p, + b on crack, argmax; p(crack) renormalised), same D2 rule and width flag. Both arms are built
with ONE model code (--code = el_f3 e544133), strict state-dict load; every member's model config and state-dict keys / shapes are
asserted equal to pf2_SUPPF_100pct_s5's. Order (each step's file written before the next set is read):
  1. VAL GATES (skr2e_gate.txt; any failure exits 3 before the val decisions and before any test / E1 cell):
     (a) member s5 of each arm alone vs its opening m0 JSON (E-PF: PF2 m0; E-SKR2: s2q/post/m0/SKR01; GPU bf16), val pooled at
         b 0: crack IoU and relF1@2 |delta| <= 0.005, val any-hit component recall (GT comps >= 20 px with >= 1 px within 2 px
         of a prediction) |delta| <= 0.01;
     (b) each ensemble's val GT crack components >= 20 px == 125 exactly (prediction-independent).
  2. VAL sweep b in {0, 0.25, ..., 3} per ensemble; FINAL's rule D2 exactly as Track M m9_final.py (smallest b with val relR@2 >=
     0.90, used if its relP@2 >= 0.90, else the b with max val relF1@2; headline b = 0 if val crack (pixel) precision drops by >
     0.05 from b 0 to the chosen b). Decisions -> skr2e_val_decisions.json BEFORE any test / E1 inference.
     (c) E-PF decisions == PF2E's pf2e_val_decisions.json (bias and headline exact, precision drop |delta| <= 1e-9), else exit 4.
  3. E1 GT check from the masks alone (no model has seen an E1 image yet): E1 GT crack components >= 20 px == 296, else exit 5.
  4. TEST (50; plus test_noscuff as PF2E) and E1 (ext117, 106, its ignore masks): BOTH arms at the union U = {0, b_D2(E-PF),
     b_D2(E-SKR2)} (contains both headline b's). Outputs, m0 per-cell format: <out>/<E>.b<b>.json. E1 aggregate sweep (reported
     only, protocol §4 matched-volume line): per arm and per b in the D2 grid, E1 pooled pred / GT crack px, relF1@2, any-hit,
     crack px on crack-free cells -> skr2e_e1_sweep.json (aggregates only; no per-cell E1 file at b outside U).
  5. CHECKS (skr2e_checks.txt / .json): E-PF identity (every val / test / test_noscuff / ext cell at b 0 and b 1.5 == PF2E's
     E-PF.b0.json / E-PF.b1.5.json exactly; if not exact: disclosed, E-PF is taken from this run); any-hit self-test (E-PF b 0 E1
     any-hit from this run's cells == the sweep aggregate == the count from PF2E's E-PF.b0.json crack_cc). Exit 6 if the sweep and
     this run's cells disagree, or if the identity is exact and the PF2E count differs (a code fault); else 0.
Usage: python skr2e_infer.py --code EL_F3 --tm DIR_WITH_m_common --out OUT --epf 5 runs --eskr 5 runs --m0ref-pf PF2_M0_DIR
       --m0ref-skr S2_M0_SKR01_DIR --pf2e PF2E_OUT_DIR [--threads 8] [--gate-only]
"""
import argparse, hashlib, json, sys, time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True); ap.add_argument("--tm", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--epf", nargs=5, required=True); ap.add_argument("--eskr", nargs=5, required=True)
ap.add_argument("--m0ref-pf", required=True); ap.add_argument("--m0ref-skr", required=True); ap.add_argument("--pf2e", required=True)
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
REV = {"E-PF": "e544133", "E-SKR2": "c9bbb02"}
t0 = time.time()


def load(run):  # as d_infer.py 129edac4; + returns the model config and the state-dict key / shape map (strict load as before)
    run = Path(run); cfg = load_config(run / "config_used.yaml")
    st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(st.get("step", -1)) == 20000, run
    mc = {k: v for k, v in cfg["model"].items() if k not in ("encoder_init", "decoder_init")}; mc["encoder_weights"] = None
    m = build_model(mc); m.load_state_dict(st["models"]["model"], strict=True); m.eval()
    rv = run.parent.parent / "REVISION"
    shapes = {k: tuple(v.shape) for k, v in st["models"]["model"].items()}
    return m, {"run": run.name, "revision": rv.read_text().strip() if rv.exists() else "?", "mc": mc, "shapes": shapes}


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


def anyhit(cs):  # protocol_SKR2_HC2 §3a.3 = m0_analyze.agg cc_recany_20: GT crack comps >= 20 px with hit >= 1, pooled counts
    g = [c for v in cs.values() for c in v["crack_cc"]["gt"] if c[0] >= 20]
    return sum(1 for c in g if c[1] >= 1), len(g)


def e1agg(cs):  # E1 aggregate sweep row (aggregates only)
    C = sum(np.array(v["conf"], np.int64).reshape(NC, NC) for v in cs.values())
    cf = [np.array(v["conf"], np.int64).reshape(NC, NC) for v in cs.values() if np.array(v["conf"]).reshape(NC, NC)[CRACK].sum() == 0]
    h, n = anyhit(cs)
    return {"pred_px": int(C[:, CRACK].sum()), "gt_px": int(C[CRACK].sum()), "pred_over_gt": float(C[:, CRACK].sum() / max(C[CRACK].sum(), 1)),
            "relF1": summ(cs)["relF1"], "anyhit": h / max(n, 1), "anyhit_hits": h, "anyhit_n": n,
            "crack_free_cells": len(cf), "crack_free_px": int(sum(c[:, CRACK].sum() for c in cf))}


md5 = lambda f: hashlib.md5(open(f, "rb").read()).hexdigest()
canon = lambda x: json.loads(json.dumps(x))  # compare as written to / read from JSON (ints, floats, lists)
# one opening only: refuse to run the val decisions / test / E1 part twice into the same output dir
if not a.gate_only and ((OUT / "skr2e_val_decisions.json").exists() or list(OUT.glob("E-*.json"))):
    sys.exit(f"refusing: {OUT} already holds SKR2E decisions / outputs (E1 opening #6 is read once)")
assert md5(Path(a.tm) / "m_common.py").startswith("10f0d37c"), "m_common.py is not Track M's 10f0d37c"
assert [Path(r).name for r in a.epf] == [f"pf2_SUPPF_100pct_s{k}" for k in range(5, 10)], a.epf
assert [Path(r).name for r in a.eskr] == [f"skr2_SKR01_100pct_s{k}" for k in range(5, 10)], a.eskr
EPF = [load(r) for r in a.epf]; ESK = [load(r) for r in a.eskr]
assert all(m[1]["revision"] == REV["E-PF"] for m in EPF) and all(m[1]["revision"] == REV["E-SKR2"] for m in ESK), \
    [(m[1]["run"], m[1]["revision"]) for m in EPF + ESK]
ref_mc, ref_sh = EPF[0][1]["mc"], EPF[0][1]["shapes"]
for _, i in EPF + ESK:  # one architecture: same model config, same state-dict keys and shapes as pf2_SUPPF_100pct_s5
    assert i["mc"] == ref_mc, (i["run"], i["mc"], ref_mc)
    assert i["shapes"] == ref_sh, (i["run"], sorted(set(i["shapes"]) ^ set(ref_sh))[:5], [k for k in ref_sh if i["shapes"].get(k) != ref_sh[k]][:5])
meta = {"E-PF": [m[1]["run"] for m in EPF], "E-SKR2": [m[1]["run"] for m in ESK], "revision": REV, "model_code": f"{a.code} (el_f3 e544133)",
        "n_state_keys": len(ref_sh), "script_md5": md5(__file__), "m_common_md5": md5(Path(a.tm) / "m_common.py"),
        "ext_stems_md5": md5(Path(a.ext) / "stems_eval.txt"), "pf2e_decisions_md5": md5(Path(a.pf2e) / "pf2e_val_decisions.json"),
        "device": "cpu fp32", "threads": a.threads}
print(json.dumps(meta), flush=True)
ARMS = {"E-PF": [m for m, _ in EPF], "E-SKR2": [m for m, _ in ESK]}
M0REF = {"E-PF": (EPF, Path(a.m0ref_pf)), "E-SKR2": (ESK, Path(a.m0ref_skr))}
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
L, bad = ["SKR2E gates (a) member s5 of each arm alone, val pooled, b 0: gaint CPU fp32 vs its opening m0 JSON (GPU bf16); "
          "tolerance 0.005 (crack IoU, relF1@2), 0.01 (any-hit); (b) ensemble val GT crack comps >= 20 px == 125"], False
for k, (ms, rdir) in M0REF.items():
    r5 = ms[0][1]["run"]; ref = json.load(open(rdir / f"{r5}.json"))["cells"]["val"]
    me, rf = summ(gate_cells[k]), summ({s: ref[s] for s in val})
    for q in ("crack_iou", "relF1"):
        d = me[q] - rf[q]; bad |= abs(d) > 0.005; L.append(f"  (a) {k} {r5} {q}: {me[q]:.4f} (ref {rf[q]:.4f}, delta {d:+.4f})")
    (h1, n1), (h2, n2) = anyhit(gate_cells[k]), anyhit({s: ref[s] for s in val})
    d = h1 / max(n1, 1) - h2 / max(n2, 1); bad |= abs(d) > 0.01 or n1 != n2
    L.append(f"  (a) {k} {r5} val any-hit: {h1 / max(n1, 1):.4f} ({h1}/{n1}) (ref {h2 / max(n2, 1):.4f} ({h2}/{n2}), delta {d:+.4f})")
    ng = anyhit(sweep_cells[k][0.0])[1]; bad |= ng != 125
    L.append(f"  (b) {k} ensemble val GT crack comps >= 20 px: {ng} (expected 125)")
L.append("  -> " + ("FAIL: stop before the val decisions and any test / E1 cell" if bad else "within tolerance: proceed"))
(OUT / "skr2e_gate.txt").write_text("\n".join(L) + "\n"); print("\n".join(L), flush=True)
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
U = sorted({0.0, dec["E-PF"]["bias"], dec["E-SKR2"]["bias"]}); dec["union_b"] = U
(OUT / "skr2e_val_decisions.json").write_text(json.dumps(dec, indent=1))
print(f"val decisions written (md5 {md5(OUT / 'skr2e_val_decisions.json')}): " +
      "; ".join(f"{k} b {dec[k]['bias']} ({dec[k]['why']}), headline {dec[k]['headline_bias']}" for k in ARMS) + f"; union {U}", flush=True)
pd = json.load(open(Path(a.pf2e) / "pf2e_val_decisions.json"))["E-PF"]
dd = dec["E-PF"]["val_crack_precision_drop_at_bias"] - pd["val_crack_precision_drop_at_bias"]
cok = dec["E-PF"]["bias"] == pd["bias"] and dec["E-PF"]["headline_bias"] == pd["headline_bias"] and abs(dd) <= 1e-9
L = [f"  (c) E-PF val decisions vs PF2E pf2e_val_decisions.json: bias {dec['E-PF']['bias']} (PF2E {pd['bias']}), headline "
     f"{dec['E-PF']['headline_bias']} (PF2E {pd['headline_bias']}), drop {dec['E-PF']['val_crack_precision_drop_at_bias']:.10f} (PF2E "
     f"{pd['val_crack_precision_drop_at_bias']:.10f}, delta {dd:+.2e}) -> " + ("EQUAL: proceed" if cok else "DIFFERENT: stop before any test / E1 cell")]
with open(OUT / "skr2e_gate.txt", "a") as f:
    f.write("\n".join(L) + "\n")
print("\n".join(L), flush=True)
if not cok:
    sys.exit(4)

# ---- 3: E1 GT components from the masks alone (prediction-independent; before any model sees an E1 image)
test = sorted(l.strip() for l in open(D / "splits" / "test.txt") if l.strip())
test = [s for s in test if (D / "escdd_masks" / "test" / f"{s}.png").exists()]; assert len(test) == 50
ext = [l.strip() for l in open(Path(a.ext) / "stems_eval.txt") if l.strip()]; assert len(ext) == 106
EXTGT = {}
for s in ext:
    gt = np.array(Image.open(Path(a.ext) / "masks" / f"{s}.png")); keep = ~(np.array(Image.open(Path(a.ext) / "ignore" / f"{s}.png")) > 0)
    EXTGT[s] = (gt, keep)
ngt = sum(1 for s in ext for c in cell_stats(np.zeros_like(EXTGT[s][0]), EXTGT[s][0], EXTGT[s][1])["crack_cc"]["gt"] if c[0] >= 20)
L = [f"  E1 GT crack comps >= 20 px (masks + ignore only): {ngt} (expected 296) -> " + ("OK" if ngt == 296 else "MISMATCH: stop before any E1 inference")]
with open(OUT / "skr2e_gate.txt", "a") as f:
    f.write("\n".join(L) + "\n")
print("\n".join(L), flush=True)
if ngt != 296:
    sys.exit(5)

# ---- 4: TEST + E1, both arms at the union U; E1 aggregate sweep over the D2 grid
res = {k: {b: {"val": {s: sweep_cells[k][b][s] for s in val}, "test": {}, "test_noscuff": {}, "ext": {}} for b in U} for k in ARMS}
e1sw = {k: {b: {} for b in GRID} for k in ARMS}
with torch.no_grad():
    for sp, stems in (("test", test), ("ext", ext)):
        for s in stems:
            if sp == "test":
                img, gt, keep = D / "labeled" / "images" / f"{s}.png", np.array(Image.open(D / "escdd_masks" / "test" / f"{s}.png")), None
            else:
                img = Path(a.ext) / "images" / f"{s}.png"; gt, keep = EXTGT[s]
            x = x_of(img)
            for k, ms in ARMS.items():
                pe = sum(torch.softmax(m(x).float(), 1)[0] for m in ms) / len(ms)
                for b in (U if sp == "test" else GRID):
                    cs = stats(pe, gt, keep, b)
                    if sp == "ext":
                        e1sw[k][b][s] = cs
                    if b in U:
                        res[k][b][sp][s] = cs
                    if sp == "test" and s in SCUFF:
                        sc = np.array(Image.open(Path(a.raw_test) / f"{s}.png")) == 25
                        assert int(sc.sum()) == SCUFF[s] and int((gt[sc] == CRACK).sum()) == SCUFF[s]
                        res[k][b]["test_noscuff"][s] = stats(pe, gt, ~sc, b)
                    elif sp == "test":
                        res[k][b]["test_noscuff"][s] = res[k][b]["test"][s]
        print(f"{sp} done, {time.time() - t0:.0f} s", flush=True)
for k in ARMS:
    for b in U:
        f = OUT / f"{k}.b{b:g}.json"
        f.write_text(json.dumps({"run": k, "members": meta[k], "step": 20000, "code_revision": REV[k], "model_code_revision": "e544133",
                                 "bias": b, "chosen_bias": dec[k]["bias"], "headline_bias": dec[k]["headline_bias"], "cells": res[k][b]}))
sweep = {"note": "E1 aggregate sweep, reported only (protocol_SKR2E §4 matched-volume line); aggregates over the 106 E1 cells",
         **{k: {str(b): e1agg(e1sw[k][b]) for b in GRID} for k in ARMS}}
(OUT / "skr2e_e1_sweep.json").write_text(json.dumps(sweep, indent=1))
del e1sw
print(f"SKR2E inference done, {time.time() - t0:.0f} s; files: " + ", ".join(sorted(p.name for p in OUT.glob("E-*.json"))), flush=True)

# ---- 5: checks (E-PF identity vs PF2E; any-hit self-test)
chk, L, rc = {}, ["SKR2E checks"], 0
for b in (0.0, 1.5):
    pf = json.load(open(Path(a.pf2e) / f"E-PF.b{b:g}.json"))["cells"]; me = canon(res["E-PF"][b])
    for sp in ("val", "test", "test_noscuff", "ext"):
        diff = sorted(s for s in set(pf[sp]) | set(me[sp]) if pf[sp].get(s) != me[sp].get(s))
        chk[f"identity_b{b:g}_{sp}"] = {"cells": len(me[sp]), "pf2e_cells": len(pf[sp]), "differ": len(diff), "first": diff[:5]}
        L.append(f"  E-PF identity b {b:g} {sp}: {len(me[sp])} cells (PF2E {len(pf[sp])}), {len(diff)} differ" + (f" (first {diff[:3]})" if diff else ""))
exact = all(v["differ"] == 0 and v["cells"] == v["pf2e_cells"] for v in chk.values())
L.append("  -> E-PF identity " + ("EXACT: PF2E's E-PF files equal this run's" if exact else "NOT EXACT: disclosed; E-PF is taken from this run, PF2E's files are not used"))
h_me = anyhit(res["E-PF"][0.0]["ext"]); h_pf = anyhit(json.load(open(Path(a.pf2e) / "E-PF.b0.json"))["cells"]["ext"])
h_sw = (sweep["E-PF"]["0.0"]["anyhit_hits"], sweep["E-PF"]["0.0"]["anyhit_n"])
ok_sw, ok_pf = h_me == h_sw, h_me == h_pf
L.append(f"  any-hit self-test, E-PF b 0 E1: this run's cells {h_me[0]}/{h_me[1]}, sweep aggregate {h_sw[0]}/{h_sw[1]}, PF2E E-PF.b0.json "
         f"{h_pf[0]}/{h_pf[1]} -> sweep {'EQUAL' if ok_sw else 'DIFFERENT'}, PF2E {'EQUAL' if ok_pf else 'DIFFERENT'}")
if not ok_sw or (exact and not ok_pf):
    rc = 6; L.append("  -> any-hit self-test FAIL (code fault): exit 6")
chk.update({"identity_exact": exact, "anyhit_this_run": h_me, "anyhit_sweep": h_sw, "anyhit_pf2e": h_pf, "rc": rc})
(OUT / "skr2e_checks.json").write_text(json.dumps(chk, indent=1)); (OUT / "skr2e_checks.txt").write_text("\n".join(L) + "\n")
print("\n".join(L), flush=True)
sys.exit(rc)
