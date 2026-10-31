"""D (inference only; d_prereg.md): FINAL vs BN-HC (routed / global) vs RN50-5 vs R34-5+RN50-5 [vs R34-10], val + E1 only.
CPU fp32 (FINAL itself was scored on a cv02 A6000 in bf16, so the cross-check against its val numbers is to a tolerance).
Ensembles are mean softmax; crack bias as Track M m9_final.score (log p, + bias on crack, renormalise); per cell
Track M m_common.cell_stats. No test cell is read.
Usage: python d_infer.py --code EL_F3 --tm DIR_WITH_m_common --out OUT --final R34 x5 --rn50 RN50 x5 [--sup10 SUPg x5]
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
ap.add_argument("--final", nargs=5, required=True)
ap.add_argument("--rn50", nargs=5)
ap.add_argument("--only-r34-10", action="store_true", help="after opening 1 (pre-registered): score FINAL and R34-10 only; no BN-HC, no RN50")
ap.add_argument("--sup10", nargs=5)
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


final = [load(r) for r in a.final]; rn50 = [load(r) for r in a.rn50] if (a.rn50 and not a.only_r34_10) else []
sup10 = [load(r) for r in a.sup10] if a.sup10 else []
assert not a.only_r34_10 or len(sup10) == 5, "--only-r34-10 needs --sup10"
meta = {"final": [x[1] for x in final], "rn50": [x[1] for x in rn50], "sup10": [x[1] for x in sup10]}
print(json.dumps(meta, indent=1), flush=True)
# coach (30 Oct): cross-check gate BEFORE any variant. FINAL val on this CPU vs the cv02 bf16 reference; stop if
# |delta| > 0.005 on val crack IoU or relF1@2 at bias 0 or +0.75. Variants are always compared with this CPU FINAL.
REF = {0.0: {"crack_iou": 0.435, "relF1": 0.8929}, 0.75: {"crack_iou": 0.4349, "relF1": 0.8968}}
_val = sorted(l.strip() for l in open(D / "splits" / "val.txt") if l.strip())
if not a.limit:
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
TAG = "_r34_10" if a.only_r34_10 else ""
json.dump(res, open(OUT / f"d_results{TAG}.json", "w"), indent=1)
json.dump({sp: {v: {str(b): c for b, c in d.items()} for v, d in vv.items()} for sp, vv in cells.items()}, open(OUT / f"d_cells{TAG}.json", "w"))
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
