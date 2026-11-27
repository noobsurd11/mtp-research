"""SKR2C verdict D inference (protocol_SKR2C §3b, §4, §6 stage 2; rulings_s2c_stage2.md 5 / 6): E-SUPPF' (s2c_SUPPF_100pct_s10..14, el_f3
e544133) vs E-SKR2' (s2c_SKR01_100pct_s10..14, el_thin c9bbb02), 5-member mean-softmax ensembles, final weights, TTA off, gaint CPU fp32
(nice 19, <= 8 threads). = skr2e_infer.py 5ba3c597 with only these changes: arms / run names (s10-14; --val-only: the opened s5-9
members); gate (a) for EACH of the 10 members vs its R-opening m0 JSON; no gate (c) and no E-PF identity check; one verdict pair at a
shared b 0 (the D2 b and width flag are written as reported, val only); b_mv chosen on val before any test / E1 read; per-cell files for
both arms at b 0 and for E-SKR2' at b_mv; E1 aggregate sweep on -1.5 .. 3 step 0.25; real-split md5 asserts; an image-read log; the
--val-only identity mode (ruling 5). Same image read x_of, same Track M m_common.cell_stats 10f0d37c, same crack bias (log p, + b on crack,
argmax; p(crack) renormalised), same D2 rule and width flag. Both arms are built with ONE model code (--code = el_f3 e544133), strict
state-dict load; every member's model config and state-dict keys / shapes are asserted equal to the first E-SUPPF member's.
Order (each step's file written before the next set is read):
  1. VAL GATES (s2c_d_gate.txt; any failure exits 3 before the val decisions and before any test / E1 cell):
     (a) EACH member of each arm alone vs its R-opening m0 JSON (GPU bf16), val pooled at b 0: crack IoU and relF1@2 |delta| <= 0.005,
         val any-hit component recall |delta| <= 0.01 with equal component counts;
     (b) each ensemble's val GT crack components >= 20 px == 125 exactly (prediction-independent).
  2. VAL sweeps: D2 grid b in {0, 0.25, ..., 3} per ensemble (FINAL's rule D2 exactly as skr2e; reported only); b_mv grid -1.50 .. +0.50
     step 0.05 for E-SKR2': b_mv = the b whose val crack pred / GT (pooled conf, keep px) is nearest E-SUPPF''s at b 0; ties: the b nearer
     0, then the smaller b (ruling 6). Decisions -> s2c_d_val_decisions.json BEFORE any test / E1 inference.
     --val-only (ruling 5; opened s5-9 members, E-PF / E-SKR2 = #6's arms): compare with #6 (--id-ref = SKR2E out): gate (a) lines of the
     s5 members == #6's skr2e_gate.txt lines; every val cell at b 0 / 1 / 1.5 == #6's E-*.b*.json val cells; D2 sweep, bias, headline and
     drop == #6's skr2e_val_decisions.json; every image read is a val stem (asserted from the read log). Then exit (0 iff all equal; 7
     if not). No test or E1 file is opened in this mode.
  3. E1 GT check from the masks alone (no model has seen an E1 image yet): E1 GT crack components >= 20 px == 296, else exit 5.
  4. TEST (50; plus test_noscuff as SKR2E) and E1 (ext117, 106, its ignore masks): E-SUPPF' at b 0, E-SKR2' at b 0 and b_mv. Outputs, m0
     per-cell format: <out>/<E>.b<b>.json. E1 aggregate sweep (reported only): per arm and per b in -1.5 .. 3 step 0.25, E1 pooled pred /
     GT crack px, relF1@2, any-hit, crack px on crack-free cells -> s2c_d_e1_sweep.json (aggregates only).
  5. CHECKS (s2c_d_checks.txt / .json): any-hit self-test per arm (b 0 E1 any-hit from this run's cells == the sweep aggregate); every
     test / E1 stem read == the real lists. Exit 6 if not; else 0.
Usage: python s2c_d_infer.py --code EL_F3 --tm DIR_WITH_m_common --out OUT --esup 5 runs --eskr 5 runs --m0ref-sup DIR --m0ref-skr DIR
       [--threads 8] [--val-only --id-ref SKR2E_OUT]
"""
import argparse, hashlib, json, sys, time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True); ap.add_argument("--tm", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--esup", nargs=5, required=True); ap.add_argument("--eskr", nargs=5, required=True)
ap.add_argument("--m0ref-sup", required=True); ap.add_argument("--m0ref-skr", required=True)
ap.add_argument("--ext", default="/home/noob/work/el_f1/reports/f1/ext117")
ap.add_argument("--raw-test", default="/home/noob/work/el-fault-detection/data/escdd_masks/test")
ap.add_argument("--threads", type=int, default=8); ap.add_argument("--val-only", action="store_true"); ap.add_argument("--id-ref")
a = ap.parse_args()
sys.path.insert(0, a.code); sys.path.insert(0, a.tm)
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402
from m_common import NC, CRACK, cell_stats  # noqa: E402

torch.set_num_threads(a.threads)
OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)
D = Path(a.code) / "data"
GRID = [round(0.25 * i, 2) for i in range(13)]
BMV = [round(-1.5 + 0.05 * i, 2) + 0.0 for i in range(41)]
EGRID = [round(-1.5 + 0.25 * i, 2) + 0.0 for i in range(19)]
SCUFF = {"ARTS_00047_r3_c1": 34, "ARTS_00051_r3_c2": 202}
KS, KK = ("E-PF", "E-SKR2") if a.val_only else ("E-SUPPF", "E-SKR2")
REV = {KS: "e544133", KK: "c9bbb02"}
TEST_MD5, VAL_MD5, EXT_MD5 = "a31fad14fa27ee28e2a2319b8976aba3", "9dcccf00662dfca750f0b46628f8d5bb", "5266806b559f74bcf9eae167bb076b95"
READS = []  # (set, stem) of every image / mask read
t0 = time.time()


def rd(path, sp, stem):  # every image / mask read goes through here and is logged (set, stem)
    READS.append((sp, stem)); return Image.open(path)


def load(run):  # as d_infer.py 129edac4; + returns the model config and the state-dict key / shape map (strict load as before)
    run = Path(run); cfg = load_config(run / "config_used.yaml")
    st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(st.get("step", -1)) == 20000, run
    mc = {k: v for k, v in cfg["model"].items() if k not in ("encoder_init", "decoder_init")}; mc["encoder_weights"] = None
    m = build_model(mc); m.load_state_dict(st["models"]["model"], strict=True); m.eval()
    rv = run.parent.parent / "REVISION"
    shapes = {k: tuple(v.shape) for k, v in st["models"]["model"].items()}
    return m, {"run": run.name, "revision": rv.read_text().strip() if rv.exists() else "?", "mc": mc, "shapes": shapes}


def x_of(path, sp, stem):  # as d_infer.py 129edac4 (+ read log)
    g = np.array(rd(path, sp, stem).convert("L"), np.float32) / 255.0
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


def vol(cs):  # val crack pred / GT px (pooled conf over keep px): the b_mv matching quantity
    C = sum(np.array(v["conf"], np.int64).reshape(NC, NC) for v in cs.values())
    return float(C[:, CRACK].sum() / max(C[CRACK].sum(), 1))


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
if (OUT / "s2c_d_val_decisions.json").exists() or list(OUT.glob("E-*.json")):
    sys.exit(f"refusing: {OUT} already holds D decisions / outputs (E1 opening #7 is read once)")
assert md5(Path(a.tm) / "m_common.py").startswith("10f0d37c"), "m_common.py is not Track M's 10f0d37c"
assert md5(D / "splits" / "val.txt") == VAL_MD5 and md5(D / "splits" / "test.txt") == TEST_MD5, "real splits md5 (val 9dcccf00, test a31fad14)"
assert md5(Path(a.ext) / "stems_eval.txt") == EXT_MD5, "ext117 stems_eval.txt md5 (5266806b)"
if a.val_only:  # ruling 5: the opened s5-9 members only (#6's arms)
    assert [Path(r).name for r in a.esup] == [f"pf2_SUPPF_100pct_s{k}" for k in range(5, 10)], a.esup
    assert [Path(r).name for r in a.eskr] == [f"skr2_SKR01_100pct_s{k}" for k in range(5, 10)], a.eskr
    assert a.id_ref, "--val-only needs --id-ref (SKR2E out)"
else:
    assert [Path(r).name for r in a.esup] == [f"s2c_SUPPF_100pct_s{k}" for k in range(10, 15)], a.esup
    assert [Path(r).name for r in a.eskr] == [f"s2c_SKR01_100pct_s{k}" for k in range(10, 15)], a.eskr
ESU = [load(r) for r in a.esup]; ESK = [load(r) for r in a.eskr]
assert all(m[1]["revision"] == REV[KS] for m in ESU) and all(m[1]["revision"] == REV[KK] for m in ESK), \
    [(m[1]["run"], m[1]["revision"]) for m in ESU + ESK]
ref_mc, ref_sh = ESU[0][1]["mc"], ESU[0][1]["shapes"]
for _, i in ESU + ESK:  # one architecture: same model config, same state-dict keys and shapes as the first E-SUPPF member
    assert i["mc"] == ref_mc, (i["run"], i["mc"], ref_mc)
    assert i["shapes"] == ref_sh, (i["run"], sorted(set(i["shapes"]) ^ set(ref_sh))[:5], [k for k in ref_sh if i["shapes"].get(k) != ref_sh[k]][:5])
meta = {KS: [m[1]["run"] for m in ESU], KK: [m[1]["run"] for m in ESK], "revision": REV, "model_code": f"{a.code} (el_f3 e544133)",
        "n_state_keys": len(ref_sh), "script_md5": md5(__file__), "m_common_md5": md5(Path(a.tm) / "m_common.py"),
        "ext_stems_md5": md5(Path(a.ext) / "stems_eval.txt"), "val_md5": VAL_MD5, "test_md5": TEST_MD5, "mode": "val-only identity" if a.val_only else "opening",
        "device": "cpu fp32", "threads": a.threads}
print(json.dumps(meta), flush=True)
ARMS = {KS: [m for m, _ in ESU], KK: [m for m, _ in ESK]}
M0REF = {KS: (ESU, Path(a.m0ref_sup)), KK: (ESK, Path(a.m0ref_skr))}
VG = {KS: GRID, KK: sorted(set(GRID) | set(BMV))}
val = sorted(l.strip() for l in open(D / "splits" / "val.txt") if l.strip()); assert len(val) == 54

# ---- 1 + 2: VAL (gate members, ensemble sweeps) in one pass over val
gate_cells = {k: [{} for _ in ARMS[k]] for k in ARMS}; sweep_cells = {k: {b: {} for b in VG[k]} for k in ARMS}
with torch.no_grad():
    for s in val:
        x = x_of(D / "labeled" / "images" / f"{s}.png", "val", s); gt = np.array(rd(D / "escdd_masks" / "val" / f"{s}.png", "val", s))
        for k, ms in ARMS.items():
            P = [torch.softmax(m(x).float(), 1)[0] for m in ms]
            for i in range(len(P)):
                gate_cells[k][i][s] = stats(P[i], gt, None, 0.0)
            pe = sum(P) / len(P)
            for b in VG[k]:
                sweep_cells[k][b][s] = stats(pe, gt, None, b)
print(f"val done, {time.time() - t0:.0f} s", flush=True)
L, bad = [f"SKR2C D gates (a) each member of each arm alone, val pooled, b 0: gaint CPU fp32 vs its R-opening m0 JSON (GPU bf16); "
          "tolerance 0.005 (crack IoU, relF1@2), 0.01 (any-hit); (b) ensemble val GT crack comps >= 20 px == 125"], False
for k, (ms, rdir) in M0REF.items():
    for i, (_, info) in enumerate(ms):
        r5 = info["run"]; ref = json.load(open(rdir / f"{r5}.json"))["cells"]["val"]
        me, rf = summ(gate_cells[k][i]), summ({s: ref[s] for s in val})
        for q in ("crack_iou", "relF1"):
            d = me[q] - rf[q]; bad |= abs(d) > 0.005; L.append(f"  (a) {k} {r5} {q}: {me[q]:.4f} (ref {rf[q]:.4f}, delta {d:+.4f})")
        (h1, n1), (h2, n2) = anyhit(gate_cells[k][i]), anyhit({s: ref[s] for s in val})
        d = h1 / max(n1, 1) - h2 / max(n2, 1); bad |= abs(d) > 0.01 or n1 != n2
        L.append(f"  (a) {k} {r5} val any-hit: {h1 / max(n1, 1):.4f} ({h1}/{n1}) (ref {h2 / max(n2, 1):.4f} ({h2}/{n2}), delta {d:+.4f})")
    ng = anyhit(sweep_cells[k][0.0])[1]; bad |= ng != 125
    L.append(f"  (b) {k} ensemble val GT crack comps >= 20 px: {ng} (expected 125)")
L.append("  -> " + ("FAIL: stop before the val decisions and any test / E1 cell" if bad else "within tolerance: proceed"))
(OUT / "s2c_d_gate.txt").write_text("\n".join(L) + "\n"); print("\n".join(L), flush=True)
if bad:
    sys.exit(3)
dec = {"rule": "FINAL D2 (Track M m9_final.py): smallest b in 0..3 step 0.25 with val relR@2 >= 0.90, used if its relP@2 >= 0.90, "
               "else max val relF1@2; headline b 0 if val crack precision drops by > 0.05 from b 0 to the chosen b (SKR2C: REPORTED ONLY; "
               "the verdict pair is b 0 for both arms)", "meta": meta}
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
tgt = vol(sweep_cells[KS][0.0]); vk = {b: vol(sweep_cells[KK][b]) for b in BMV}
b_mv = min(BMV, key=lambda b: (abs(vk[b] - tgt), abs(b), b))
dec["b_mv"] = {"rule": "b on -1.50 .. +0.50 step 0.05 (val only) where E-SKR2' val crack pred / GT is nearest E-SUPPF''s at b 0; ties: nearer 0, "
                       "then smaller b (ruling 6)", "b_mv": b_mv, "target_val_pred_over_gt": tgt, "val_pred_over_gt_at_b_mv": vk[b_mv],
               "val_pred_over_gt_grid": {str(b): v for b, v in vk.items()}}
WB = {KS: [0.0], KK: sorted({0.0, b_mv})}; dec["written_b"] = WB
(OUT / "s2c_d_val_decisions.json").write_text(json.dumps(dec, indent=1))
print(f"val decisions written (md5 {md5(OUT / 's2c_d_val_decisions.json')}): " +
      "; ".join(f"{k} D2 b {dec[k]['bias']} ({dec[k]['why']}), headline {dec[k]['headline_bias']} (reported)" for k in ARMS)
      + f"; b_mv {b_mv}; written b {WB}", flush=True)

if a.val_only:  # ---- ruling 5: identity vs #6 (SKR2E), val only; no test or E1 file is opened in this mode
    R6 = Path(a.id_ref); L = ["SKR2C D val-only identity vs #6 (SKR2E out) on the opened s5-9 members"]; good = True
    g6 = (R6 / "skr2e_gate.txt").read_text().split("\n"); mine = (OUT / "s2c_d_gate.txt").read_text().split("\n")
    for k, pre in ((KS, "pf2_SUPPF_100pct_s5"), (KK, "skr2_SKR01_100pct_s5")):
        want = [l for l in g6 if l.startswith(f"  (a) {k} {pre} ") or l.startswith(f"  (b) {k} ")]
        got = [l for l in mine if l.startswith(f"  (a) {k} {pre} ") or l.startswith(f"  (b) {k} ")]
        t = len(want) == 4 and got == want; good &= t; L.append(f"  gate (a) s5 + (b) lines of {k} == #6 skr2e_gate.txt: {t} ({len(got)} / {len(want)} lines)")
    for k in ARMS:
        for b in (0.0, 1.0, 1.5):
            f6 = R6 / f"{k}.b{b:g}.json"
            if not f6.exists():
                continue
            c6 = json.load(open(f6))["cells"]["val"]; me = canon(sweep_cells[k][b])
            diff = sorted(s for s in set(c6) | set(me) if c6.get(s) != me.get(s))
            t = not diff and len(me) == len(c6) == 54; good &= t
            L.append(f"  val cells {k} b {b:g}: {len(me)} cells (#6 {len(c6)}), {len(diff)} differ -> {t}")
    d6 = json.load(open(R6 / "skr2e_val_decisions.json"))
    for k in ARMS:
        sw_eq = canon(dec[k]["sweep"]) == d6[k]["sweep"]; dd = dec[k]["val_crack_precision_drop_at_bias"] - d6[k]["val_crack_precision_drop_at_bias"]
        t = sw_eq and dec[k]["bias"] == d6[k]["bias"] and dec[k]["headline_bias"] == d6[k]["headline_bias"] and abs(dd) <= 1e-9; good &= t
        L.append(f"  val decisions {k}: D2 sweep (13 b) == #6 {sw_eq}; bias / headline / drop == #6 {t} (drop delta {dd:+.2e})")
    sets_read = sorted({sp for sp, _ in READS}); stems_read = sorted({s for _, s in READS})
    t = sets_read == ["val"] and stems_read == val; good &= t
    L.append(f"  image / mask reads: {len(READS)} reads, sets {sets_read}, {len(stems_read)} stems == the 54 val stems: {t} (no test / E1 file opened)")
    L.append("IDENTITY " + ("PASS" if good else "FAIL"))
    (OUT / "s2c_d_identity.txt").write_text("\n".join(L) + "\n"); print("\n".join(L), flush=True)
    sys.exit(0 if good else 7)

# ---- 3: E1 GT components from the masks alone (prediction-independent; before any model sees an E1 image)
test = sorted(l.strip() for l in open(D / "splits" / "test.txt") if l.strip())
test = [s for s in test if (D / "escdd_masks" / "test" / f"{s}.png").exists()]; assert len(test) == 50
ext = [l.strip() for l in open(Path(a.ext) / "stems_eval.txt") if l.strip()]; assert len(ext) == 106
EXTGT = {}
for s in ext:
    gt = np.array(rd(Path(a.ext) / "masks" / f"{s}.png", "ext", s)); keep = ~(np.array(rd(Path(a.ext) / "ignore" / f"{s}.png", "ext", s)) > 0)
    EXTGT[s] = (gt, keep)
ngt = sum(1 for s in ext for c in cell_stats(np.zeros_like(EXTGT[s][0]), EXTGT[s][0], EXTGT[s][1])["crack_cc"]["gt"] if c[0] >= 20)
L = [f"  E1 GT crack comps >= 20 px (masks + ignore only): {ngt} (expected 296) -> " + ("OK" if ngt == 296 else "MISMATCH: stop before any E1 inference")]
with open(OUT / "s2c_d_gate.txt", "a") as f:
    f.write("\n".join(L) + "\n")
print("\n".join(L), flush=True)
if ngt != 296:
    sys.exit(5)

# ---- 4: TEST + E1: E-SUPPF' at b 0, E-SKR2' at b 0 and b_mv; E1 aggregate sweep over EGRID
res = {k: {b: {"val": {s: sweep_cells[k][b][s] for s in val}, "test": {}, "test_noscuff": {}, "ext": {}} for b in WB[k]} for k in ARMS}
e1sw = {k: {b: {} for b in EGRID} for k in ARMS}
with torch.no_grad():
    for sp, stems in (("test", test), ("ext", ext)):
        for s in stems:
            if sp == "test":
                img, gt, keep = D / "labeled" / "images" / f"{s}.png", np.array(rd(D / "escdd_masks" / "test" / f"{s}.png", "test", s)), None
            else:
                img = Path(a.ext) / "images" / f"{s}.png"; gt, keep = EXTGT[s]
            x = x_of(img, sp, s)
            for k, ms in ARMS.items():
                pe = sum(torch.softmax(m(x).float(), 1)[0] for m in ms) / len(ms)
                for b in (WB[k] if sp == "test" else sorted(set(EGRID) | set(WB[k]))):
                    cs = stats(pe, gt, keep, b)
                    if sp == "ext" and b in EGRID:
                        e1sw[k][b][s] = cs
                    if b in WB[k]:
                        res[k][b][sp][s] = cs
                    if sp == "test" and s in SCUFF:
                        sc = np.array(rd(Path(a.raw_test) / f"{s}.png", "test", s)) == 25
                        assert int(sc.sum()) == SCUFF[s] and int((gt[sc] == CRACK).sum()) == SCUFF[s]
                        res[k][b]["test_noscuff"][s] = stats(pe, gt, ~sc, b)
                    elif sp == "test":
                        res[k][b]["test_noscuff"][s] = res[k][b]["test"][s]
        print(f"{sp} done, {time.time() - t0:.0f} s", flush=True)
for k in ARMS:
    for b in WB[k]:
        f = OUT / f"{k}.b{b:g}.json"
        f.write_text(json.dumps({"run": k, "members": meta[k], "step": 20000, "code_revision": REV[k], "model_code_revision": "e544133",
                                 "bias": b, "d2_bias_reported": dec[k]["bias"], "b_mv": b_mv, "cells": res[k][b]}))
sweep = {"note": "E1 aggregate sweep, reported only (protocol_SKR2C §4); aggregates over the 106 E1 cells; b -1.5 .. 3 step 0.25",
         **{k: {str(b): e1agg(e1sw[k][b]) for b in EGRID} for k in ARMS}}
(OUT / "s2c_d_e1_sweep.json").write_text(json.dumps(sweep, indent=1))
del e1sw
print(f"SKR2C D inference done, {time.time() - t0:.0f} s; files: " + ", ".join(sorted(p.name for p in OUT.glob("E-*.json"))), flush=True)

# ---- 5: checks (any-hit self-test per arm; stems read == the real lists)
chk, L, rc = {}, ["SKR2C D checks"], 0
for k in ARMS:
    h_me = anyhit(res[k][0.0]["ext"]); h_sw = (sweep[k]["0.0"]["anyhit_hits"], sweep[k]["0.0"]["anyhit_n"]); ok_sw = h_me == h_sw
    chk[f"anyhit_{k}"] = {"this_run": h_me, "sweep": h_sw, "equal": ok_sw}
    L.append(f"  any-hit self-test, {k} b 0 E1: this run's cells {h_me[0]}/{h_me[1]}, sweep aggregate {h_sw[0]}/{h_sw[1]} -> {'EQUAL' if ok_sw else 'DIFFERENT'}")
    if not ok_sw:
        rc = 6
for sp, want in (("val", val), ("test", test), ("ext", sorted(ext))):
    got = sorted({s for q, s in READS if q == sp}); t = got == sorted(want)
    chk[f"reads_{sp}"] = {"stems": len(got), "equal_real_list": t}
    L.append(f"  {sp} stems read: {len(got)} == real list ({len(want)}): {t}")
    if not t:
        rc = 6
if rc:
    L.append("  -> check FAIL (code fault): exit 6")
chk["rc"] = rc
(OUT / "s2c_d_checks.json").write_text(json.dumps(chk, indent=1)); (OUT / "s2c_d_checks.txt").write_text("\n".join(L) + "\n")
print("\n".join(L), flush=True)
sys.exit(rc)
