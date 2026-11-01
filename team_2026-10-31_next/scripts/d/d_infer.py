"""D (inference only; d_prereg.md): FINAL vs BN-HC (routed / global) vs RN50-5 vs R34-5+RN50-5 [vs R34-10], val + E1 only.
CPU fp32 (FINAL itself was scored on a cv02 A6000 in bf16, so the cross-check against its val numbers is to a tolerance).
Ensembles are mean softmax; crack bias as Track M m9_final.score (log p, + bias on crack, renormalise); per cell
Track M m_common.cell_stats. No test cell is read.
Usage: python d_infer.py --code EL_F3 --tm DIR_WITH_m_common --out OUT --final R34 x5 --rn50 RN50 x5 [--sup10 SUPg x5]
v3 (runner, 1 Nov; protocol_PF2 §3c RN named secondary, pre-registered): --pf2-rn --suppf SUPPF x5 --rn50pf RN50PF x5 --m0ref DIR
  scores only the two 5-member mean-softmax ensembles SUPPF_5 (comparator) and RN50PF_5 on val + E1 (no test, no BN-HC, no FINAL);
  gate before any E1 read: SUPPF s5 alone on CPU fp32 vs its PF2-opening m0 JSON (GPU bf16), val pooled crack IoU and relF1@2 at
  bias 0, |delta| <= 0.005, else stop. Read at bias +0.75 as D: RN50PF_5 - SUPPF_5. Outputs *_pf2_rn.
  python d_infer.py --pf2-rn --code EL_F3 --tm DIR --out OUT --suppf ... --rn50pf ... --m0ref EL_F3/reports/pf2/post/m0 --threads 8
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--tm", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--final", nargs=5)
ap.add_argument("--rn50", nargs=5)
ap.add_argument("--only-r34-10", action="store_true", help="after opening 1 (pre-registered): score FINAL and R34-10 only; no BN-HC, no RN50")
ap.add_argument("--sup10", nargs=5)
ap.add_argument("--pf2-rn", action="store_true", help="v3: PF2's RN named secondary: SUPPF_5 vs RN50PF_5 ensembles only")
ap.add_argument("--suppf", nargs=5); ap.add_argument("--rn50pf", nargs=5); ap.add_argument("--m0ref")
ap.add_argument("--gate-only", action="store_true", help="v3 dry check: load the 10 models, run the val gate, exit before any E1 cell is read")
ap.add_argument("--ext", default="/home/noob/work/el_f1/reports/f1/ext117")
ap.add_argument("--e1ctx", default="/home/noob/work/el_f3/reports/d/e1_context.tsv")
ap.add_argument("--threads", type=int, default=16)
ap.add_argument("--limit", type=int, default=0)
a = ap.parse_args()
sys.path.insert(0, a.code); sys.path.insert(0, a.tm)
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402
from m_common import NC, CRACK, cell_stats  # noqa: E402

torch.set_num_threads(a.threads)
OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)
D = Path(a.code) / "data"
VL = [0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 15, 16, 21]
BIASES = (0.0, 0.75)
t0 = time.time()


def load(run):
    run = Path(run); cfg = load_config(run / "config_used.yaml")
    st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(st.get("step", -1)) == 20000, run
    mc = {k: v for k, v in cfg["model"].items() if k not in ("encoder_init", "decoder_init")}; mc["encoder_weights"] = None
    m = build_model(mc); m.load_state_dict(st["models"]["model"]); m.eval()
    return m, {"run": str(run), "encoder": cfg["model"].get("encoder_name", cfg["model"].get("encoder")), "name": cfg["model"].get("name"),
               "revision": (run.parent.parent / "REVISION").read_text().strip()[:7] if (run.parent.parent / "REVISION").exists() else "?"}


def x_of(path):
    g = np.array(Image.open(path).convert("L"), np.float32) / 255.0
    return torch.from_numpy((g - 0.5) / 0.25)[None, None]


@torch.no_grad()
def bn_reestimate(m, paths, bs=8):
    import copy
    m2 = copy.deepcopy(m)
    for mod in m2.modules():
        if isinstance(mod, torch.nn.modules.batchnorm._BatchNorm):
            mod.reset_running_stats(); mod.momentum = None
    m2.train()
    for i in range(0, len(paths), bs):
        m2(torch.cat([x_of(p) for p in paths[i:i + bs]]))
    m2.eval()
    return m2


assert a.pf2_rn or a.final, "--final is required unless --pf2-rn"
if a.pf2_rn:  # v3: the two PF2 ensembles; "final" holds SUPPF_5 (the comparator), "rn50" RN50PF_5
    assert a.suppf and a.rn50pf and a.m0ref and not (a.only_r34_10 or a.sup10)
    final = [load(r) for r in a.suppf]; rn50 = [load(r) for r in a.rn50pf]; sup10 = []
    meta = {"suppf": [x[1] for x in final], "rn50pf": [x[1] for x in rn50]}
else:
    final = [load(r) for r in a.final]; rn50 = [load(r) for r in a.rn50] if (a.rn50 and not a.only_r34_10) else []
    sup10 = [load(r) for r in a.sup10] if a.sup10 else []
    assert not a.only_r34_10 or len(sup10) == 5, "--only-r34-10 needs --sup10"
    meta = {"final": [x[1] for x in final], "rn50": [x[1] for x in rn50], "sup10": [x[1] for x in sup10]}
print(json.dumps(meta, indent=1), flush=True)
# coach (30 Oct): cross-check gate BEFORE any variant. FINAL val on this CPU vs the cv02 bf16 reference; stop if
# |delta| > 0.005 on val crack IoU or relF1@2 at bias 0 or +0.75. Variants are always compared with this CPU FINAL.
REF = {0.0: {"crack_iou": 0.435, "relF1": 0.8929}, 0.75: {"crack_iou": 0.4349, "relF1": 0.8968}}
_val = sorted(l.strip() for l in open(D / "splits" / "val.txt") if l.strip())
if a.pf2_rn and not a.limit:  # v3 gate: SUPPF s5 alone, CPU fp32 vs its PF2-opening m0 JSON (GPU bf16), val, bias 0
    r5 = Path(a.suppf[0]).name; ref5 = json.load(open(Path(a.m0ref) / f"{r5}.json"))["cells"]["val"]; mine5 = {}
    with torch.no_grad():
        for s_ in _val:
            x_ = x_of(D / "labeled" / "images" / f"{s_}.png"); g_ = np.array(Image.open(D / "escdd_masks" / "val" / f"{s_}.png"))
            p_ = torch.softmax(final[0][0](x_).float(), 1)[0]
            mine5[s_] = cell_stats(torch.log(p_ + 1e-12).argmax(0).numpy(), g_, None, p_[CRACK].numpy())
    def _pool(cs):
        C_ = sum(np.array(v["conf"], np.int64).reshape(NC, NC) for v in cs.values()); tp_ = np.diag(C_).astype(float)
        den_ = C_.sum(1) + C_.sum(0) - tp_; rel_ = np.sum([v["crack_rel2"] for v in cs.values()], 0)
        rP_, rR_ = rel_[0] / max(rel_[1], 1), rel_[2] / max(rel_[3], 1)
        return {"crack_iou": tp_[CRACK] / max(den_[CRACK], 1), "relF1": 2 * rP_ * rR_ / max(rP_ + rR_, 1e-9)}
    me5, rf5 = _pool(mine5), _pool({s_: ref5[s_] for s_ in _val}); _bad = False
    _lines = [f"v3 gate: {r5} alone, val, bias 0: gaint CPU fp32 vs its PF2-opening m0 JSON (GPU bf16); tolerance 0.005:"]
    for k_ in me5:
        d_ = me5[k_] - rf5[k_]; _bad |= abs(d_) > 0.005; _lines.append(f"  {k_}: {me5[k_]:.4f} (ref {rf5[k_]:.4f}, delta {d_:+.4f})")
    _lines.append("  -> " + ("FAIL: stop before any E1 read" if _bad else "within tolerance: proceed"))
    (OUT / "d_crosscheck_pf2_rn.txt").write_text("\n".join(_lines) + "\n"); print("\n".join(_lines), flush=True)
    if _bad:
        sys.exit(3)
    if a.gate_only:
        print("gate-only: stopping before any E1 cell", flush=True); sys.exit(0)
if not a.limit and not a.pf2_rn:
    _ck = {0.0: {}, 0.75: {}}
    with torch.no_grad():
        for s_ in _val:
            x_ = x_of(D / "labeled" / "images" / f"{s_}.png"); g_ = np.array(Image.open(D / "escdd_masks" / "val" / f"{s_}.png"))
            p_ = sum(torch.softmax(m(x_).float(), 1)[0] for m, _ in final) / len(final)
            for b_ in (0.0, 0.75):
                lq_ = torch.log(p_ + 1e-12)
                if b_:
                    lq_[CRACK] += b_
                pc_ = (p_[CRACK] if not b_ else torch.softmax(lq_, 0)[CRACK]).numpy()
                _ck[b_][s_] = cell_stats(lq_.argmax(0).numpy(), g_, None, pc_)
    _lines, _bad = ["cross-check gate, FINAL val (gaint CPU fp32 vs cv02 A6000 bf16 reference; tolerance 0.005):"], False
    for b_ in (0.0, 0.75):
        C_ = sum(np.array(v["conf"], np.int64).reshape(NC, NC) for v in _ck[b_].values())
        tp_ = np.diag(C_).astype(float); den_ = C_.sum(1) + C_.sum(0) - tp_
        rel_ = np.sum([v["crack_rel2"] for v in _ck[b_].values()], 0); rP_, rR_ = rel_[0] / max(rel_[1], 1), rel_[2] / max(rel_[3], 1)
        me_ = {"crack_iou": tp_[CRACK] / max(den_[CRACK], 1), "relF1": 2 * rP_ * rR_ / max(rP_ + rR_, 1e-9)}
        for k_ in me_:
            d_ = me_[k_] - REF[b_][k_]; _bad |= abs(d_) > 0.005
            _lines.append(f"  b{b_} {k_}: {me_[k_]:.4f} (ref {REF[b_][k_]:.4f}, delta {d_:+.4f})")
    _lines.append("  -> " + ("FAIL: |delta| > 0.005; D stops before any variant is scored" if _bad else "within tolerance: proceed"))
    (OUT / "d_crosscheck.txt").write_text("\n".join(_lines) + "\n"); print("\n".join(_lines), flush=True)
    if _bad:
        (OUT / "d_report.txt").write_text("\n".join(_lines) + "\nD stopped at the cross-check gate (coach); no variant scored.\n")
        sys.exit(3)
if a.pf2_rn:  # v3: no BN-HC
    bnhc = []
else:
    inv = json.load(open("/home/noob/work/sa-unetpp-ssl-el/data/unlabeled/_inventory.json"))
    half = {Path(e["name"]).stem for e in inv if "half" in e.get("rel", "").lower()}
    pool = [r.strip() for r in open("/home/noob/work/el_f1/reports/f1/mim_pool_v11.txt") if r.strip().startswith("unlabeled/")]
    hc_paths = [D / r for r in pool if Path(r).stem in half]
    assert len(hc_paths) == 986, len(hc_paths)
    if a.limit:  # smoke only
        hc_paths = hc_paths[:16]
    bnhc = [] if a.only_r34_10 else [bn_reestimate(m, hc_paths) for m, _ in final]
    print(f"BN re-estimated on {len(hc_paths)} pool half-cells, {time.time() - t0:.0f} s", flush=True)

ctx = {r[0]: {"scuff": r[2] == "scuff=1", "halfcut": r[3] == "halfcut=1"} for r in (l.rstrip("\n").split("\t") for l in open(a.e1ctx) if l.strip())}
val = sorted(l.strip() for l in open(D / "splits" / "val.txt") if l.strip())
ext = [l.strip() for l in open(Path(a.ext) / "stems_eval.txt") if l.strip()]
assert len(val) == 54 and len(ext) == 106 and set(ext) == set(ctx)
if a.limit:
    val, ext = val[:a.limit], ext[:a.limit]
VARS = ["FINAL", "R34_10"] if a.only_r34_10 else (["FINAL", "BNHC_routed", "BNHC_global", "RN50_5", "R34_5+RN50_5"] + (["R34_10"] if sup10 else []))
if a.pf2_rn:  # v3: "FINAL" slot = SUPPF_5 (comparator), "RN50_5" slot = RN50PF_5; renamed in the outputs
    VARS = ["FINAL", "RN50_5"]
cells = {sp: {v: {b: {} for b in BIASES} for v in VARS} for sp in ("val", "ext")}


def stats(p, gt, keep, bias):
    lq = torch.log(p + 1e-12)
    if bias:
        lq[CRACK] += bias
    pc = (p[CRACK] if not bias else torch.softmax(lq, 0)[CRACK]).numpy()
    return cell_stats(lq.argmax(0).numpy(), gt, keep, pc)


with torch.no_grad():
    for sp, stems in (("val", val), ("ext", ext)):
        for s in stems:
            if sp == "val":
                img, gt, keep = D / "labeled" / "images" / f"{s}.png", np.array(Image.open(D / "escdd_masks" / "val" / f"{s}.png")), None
            else:
                img = Path(a.ext) / "images" / f"{s}.png"; gt = np.array(Image.open(Path(a.ext) / "masks" / f"{s}.png"))
                keep = ~(np.array(Image.open(Path(a.ext) / "ignore" / f"{s}.png")) > 0)
            x = x_of(img)
            sm = lambda ms: sum(torch.softmax(m(x).float(), 1)[0] for m in ms) / len(ms)
            pf = sm([m for m, _ in final])
            if a.only_r34_10:
                P = {"FINAL": pf}
            elif a.pf2_rn:
                P = {"FINAL": pf, "RN50_5": sm([m for m, _ in rn50])}
            else:
                pr = sm([m for m, _ in rn50]); pb = sm(bnhc)
                hc = sp == "ext" and ctx[s]["halfcut"]
                P = {"FINAL": pf, "BNHC_routed": pb if hc else pf, "BNHC_global": pb, "RN50_5": pr, "R34_5+RN50_5": (pf + pr) / 2}
            if sup10:
                P["R34_10"] = (pf + sm([m for m, _ in sup10])) / 2
            for v, p in P.items():
                for b in BIASES:
                    cells[sp][v][b][s] = stats(p, gt, keep, b)
        print(f"{sp} done, {time.time() - t0:.0f} s", flush=True)


def summ(cs, cls=VL):
    C = sum(np.array(v["conf"], np.int64).reshape(NC, NC) for v in cs.values())
    tp = np.diag(C).astype(float); g = C.sum(1); p = C.sum(0); den = g + p - tp
    iou = np.where(den > 0, tp / np.maximum(den, 1), np.nan)
    rel = np.sum([v["crack_rel2"] for v in cs.values()], 0)
    rP, rR = rel[0] / max(rel[1], 1), rel[2] / max(rel[3], 1)
    return {"crack_iou": float(iou[CRACK]), "crack_P": float(tp[CRACK] / max(p[CRACK], 1)), "crack_R": float(tp[CRACK] / max(g[CRACK], 1)),
            "relP2": float(rP), "relR2": float(rR), "relF1": float(2 * rP * rR / max(rP + rR, 1e-9)),
            "miou_rob": float(np.nanmean([iou[c] for c in cls if g[c] > 0])), "inact_iou": float(iou[11]), "gt_crack_px": int(g[CRACK])}


def crackfree_px(cs):
    out = 0
    for v in cs.values():
        C = np.array(v["conf"], np.int64).reshape(NC, NC)
        if C[CRACK].sum() == 0:
            out += int(C[:, CRACK].sum())
    return out


grp = {"target_scuff_halfcut29": lambda s: ctx[s]["scuff"] and ctx[s]["halfcut"],
       "halfcut_noscuff29": lambda s: (not ctx[s]["scuff"]) and ctx[s]["halfcut"],
       "full48": lambda s: not ctx[s]["halfcut"]}
res = {"meta": meta, "val": {}, "ext": {}}
for v in VARS:
    for b in BIASES:
        k = f"{v}@b{b}"
        res["val"][k] = summ(cells["val"][v][b])
        e = cells["ext"][v][b]
        r = summ(e); r["crackfree_cells"] = sum(1 for c in e.values() if np.array(c["conf"]).reshape(NC, NC)[CRACK].sum() == 0)
        r["crack_px_on_crackfree"] = crackfree_px(e)
        for gname, f in grp.items():
            sub = {s: c for s, c in e.items() if f(s)}
            r[f"recall_{gname}"] = summ(sub)["crack_R"] if sub else float("nan"); r[f"n_{gname}"] = len(sub)
        res["ext"][k] = r
TAG = "_r34_10" if a.only_r34_10 else ("_pf2_rn" if a.pf2_rn else "")
if a.pf2_rn:  # v3: rename the slots for the outputs (SUPPF_5 = comparator, RN50PF_5)
    REN = {"FINAL": "SUPPF_5", "RN50_5": "RN50PF_5"}
    res = {"meta": meta, **{sp: {k.replace(k.split("@")[0], REN[k.split("@")[0]]): v for k, v in res[sp].items()} for sp in ("val", "ext")}}
    cells = {sp: {REN[v]: d for v, d in vv.items()} for sp, vv in cells.items()}
json.dump(res, open(OUT / f"d_results{TAG}.json", "w"), indent=1)
json.dump({sp: {v: {str(b): c for b, c in d.items()} for v, d in vv.items()} for sp, vv in cells.items()}, open(OUT / f"d_cells{TAG}.json", "w"))
if a.pf2_rn:  # v3 report: RN50PF_5 - SUPPF_5 at bias +0.75 (as D), descriptive; val as the sanity read; no test
    F = res["ext"]["SUPPF_5@b0.75"]; Fv = res["val"]["SUPPF_5@b0.75"]; e = res["ext"]["RN50PF_5@b0.75"]; vv = res["val"]["RN50PF_5@b0.75"]
    L = ["PF2 RN named secondary (protocol_PF2 §3c; descriptive; computed after opening #1 on the same models): 5-member mean-softmax",
         "ensembles, crack bias +0.75 (D's rule); CPU fp32; val + E1 only.", (OUT / "d_crosscheck_pf2_rn.txt").read_text().rstrip()]
    for name, x, xv in (("SUPPF_5", F, Fv), ("RN50PF_5", e, vv)):
        L.append(f"  {name}: E1 scuff+half-cut (29) recall {x['recall_target_scuff_halfcut29']:.3f}; half-cut no-scuff (29) {x['recall_halfcut_noscuff29']:.3f}; "
                 f"full (48) {x['recall_full48']:.3f}; E1 crack P {x['crack_P']:.3f}, R {x['crack_R']:.3f}, IoU {x['crack_iou']:.3f}; crack px on "
                 f"{x['crackfree_cells']} crack-free E1 cells {x['crack_px_on_crackfree']}; E1 inact IoU {x['inact_iou']:.3f} | val crack IoU {xv['crack_iou']:.4f}, "
                 f"relF1@2 {xv['relF1']:.4f}, inact IoU {xv['inact_iou']:.4f}")
    L.append(f"  RN50PF_5 - SUPPF_5: target recall {e['recall_target_scuff_halfcut29'] - F['recall_target_scuff_halfcut29']:+.3f}; must-not-hurt "
             f"{e['recall_halfcut_noscuff29'] - F['recall_halfcut_noscuff29']:+.3f}; full48 {e['recall_full48'] - F['recall_full48']:+.3f}; E1 crack P "
             f"{e['crack_P'] - F['crack_P']:+.3f}; crack px on crack-free {e['crack_px_on_crackfree'] - F['crack_px_on_crackfree']:+d}; val relF1@2 {vv['relF1'] - Fv['relF1']:+.4f}")
    (OUT / f"d_report{TAG}.txt").write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"total {time.time() - t0:.0f} s")
    sys.exit(0)
ref = {0.0: {"crack_iou": 0.435, "relF1": 0.8929, "inact_iou": 0.424}, 0.75: {"crack_iou": 0.4349, "relF1": 0.8968, "inact_iou": 0.4287}}
L = ["cross-check, FINAL val (cv02 A6000 bf16 reference vs gaint CPU fp32):"]
for b in BIASES:
    me = res["val"][f"FINAL@b{b}"]
    L.append(f"  b{b}: " + ", ".join(f"{k} {me[k]:.4f} (ref {ref[b][k]:.4f}, d {me[k] - ref[b][k]:+.4f})" for k in ref[b]))
L.append("pre-registered read (bias +0.75, variant - FINAL; kill unless some variant gains >= +0.05 on the target recall at E1 crack-precision cost < 0.05):")
F = res["ext"]["FINAL@b0.75"]; Fv = res["val"]["FINAL@b0.75"]; alive = []
for v in VARS[1:]:
    e = res["ext"][f"{v}@b0.75"]; vv = res["val"][f"{v}@b0.75"]
    dt = e["recall_target_scuff_halfcut29"] - F["recall_target_scuff_halfcut29"]; dP = F["crack_P"] - e["crack_P"]
    ok = dt >= 0.05 and dP < 0.05; alive += [v] if ok else []
    L.append(f"  {v}: target recall {e['recall_target_scuff_halfcut29']:.3f} ({dt:+.3f}); must-not-hurt {e['recall_halfcut_noscuff29']:.3f} "
             f"({e['recall_halfcut_noscuff29'] - F['recall_halfcut_noscuff29']:+.3f}); full48 {e['recall_full48']:.3f}; E1 crack P {e['crack_P']:.3f} "
             f"(cost {dP:+.3f}); crack px on {e['crackfree_cells']} crack-free E1 cells {e['crack_px_on_crackfree']} (FINAL {F['crack_px_on_crackfree']}); "
             f"E1 inact IoU {e['inact_iou']:.3f}; val relF1 drop {Fv['relF1'] - vv['relF1']:+.4f} -> {'passes the read' if ok else 'no'}")
L.append(f"FINAL@b0.75 E1: target recall {F['recall_target_scuff_halfcut29']:.3f}, must-not-hurt {F['recall_halfcut_noscuff29']:.3f}, full48 {F['recall_full48']:.3f}, P {F['crack_P']:.3f}")
L.append("verdict (descriptive): " + (f"variants passing the read: {alive}" if alive else "KILL (no variant gains >= +0.05 at precision cost < 0.05)"))
(OUT / f"d_report{TAG}.txt").write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"total {time.time() - t0:.0f} s")
