"""arch A6 premise check: post-hoc cell gate on EXISTING per-cell records (el_metrics records format).

DESCRIPTIVE. CPU only, no model is run, no training. Reads ONLY *.val.json and *.rf.json record files
(val 54 cells; Hanifi _rf 106 after hygiene = F51 51 / H36 36 / F19 19 per found's t9_rf_sets.tsv).
No test record and no E1 (ext) record is opened: every path is listed explicitly below.

Rule (written before any number was computed; arch, 2 Nov 2026):
- Gate score g(cell) = record s['1'] = the largest crack margin in the cell's keep px at b = 0
  (margin = log p_crack - max_other log p; the record's proxy for "max p(crack)"). Sensitivity: s['20'].
- G1 threshold, per run, from that run's own val records only: t = min over val crack-positive cells
  (n_gt >= 20) of g, minus 1e-3. So every val positive passes (val cell recall 1.0 by construction).
- Gating: a cell with g < t keeps none of its predicted crack px (pred, tp, relp_tp, relr_tp -> 0 at every b);
  GT counts unchanged. Other classes are not rescored (crack metrics only).
- Pixel operating points, per run:
  (a) b = 0 (argmax);
  (b) b_rel on UNGATED val: max val relR@2 s.t. relP@2 >= 0.90 on OPGRID -4..+12 step 0.1, ties to the
      smaller b; unreachable -> max-precision b, flagged (calib's el_metrics rule);
  (c) b_rel re-chosen on GATED val (same rule, gate fixed first).
- Readouts per set (val, F51, H36; F19 reported): crack px on crack-free cells (n_gt == 0; FA px),
  crack-free cells with >= 20 crack px, pooled relR@2 / relP@2 / relF1@2, pooled crack IoU, pred / GT px,
  positive cells gated out (n_gt >= 20) and their GT px. Seed means; per-seed values in the json.
- Decomposition (val, b 0 and b_rel): off-GT predicted px (pred - relp_tp) on crack-free cells vs on
  crack cells. A cell gate can only remove the first part.
- Cell AUROC (positives n_gt >= 20, negatives n_gt == 0, ambiguous 1-19 excluded) for g = s1 and s20.
Nothing here chooses a model, a threshold for any protocol, or touches test / E1.
"""
import json, sys, hashlib
from pathlib import Path
import numpy as np

T = Path(__file__).resolve().parents[2]  # team_2026-10-31_next
REC_CALIB = T / "ideas/calib_out/rec"
REC_HC = T / "results/hc/raw/shv1/rec"
REC_PF2 = T / "results/pf2/raw/b5/rec"
REC_THIN = T / "results/thin/raw/b5/rec"
SETS_TSV = T / "ideas/found_scripts/t9_rf_sets.tsv"

def pth(d, name, s):
    assert s in ("val", "rf"), s
    p = d / f"{name}.{s}.json"
    assert p.name.endswith((".val.json", ".rf.json"))
    return p

# arm label -> list of (val path, rf path or None)
ARMS = {
    "SUPPF_s5-9 (syn_work CPU; val+rf)": [(pth(REC_HC, f"pf2_SUPPF_100pct_s{k}", "val"), pth(REC_HC, f"pf2_SUPPF_100pct_s{k}", "rf")) for k in range(5, 10)],
    "HC_s5-9 (syn_work CPU; val+rf)": [(pth(REC_HC, f"hc_HC_100pct_s{k}", "val"), pth(REC_HC, f"hc_HC_100pct_s{k}", "rf")) for k in range(5, 10)],
    "SUPPF_s0-4 (calib backfill CPU; val+rf)": [(pth(REC_CALIB, f"SUPPF5_m{k}", "val"), pth(REC_CALIB, f"SUPPF5_m{k}", "rf")) for k in range(5)],
    "SUPPF_s5-9 (PF2 b5 bf16; val only)": [(pth(REC_PF2, f"pf2_SUPPF_100pct_s{k}", "val"), None) for k in range(5, 10)],
    "SKR_w1_s5-9 (THIN b5 bf16; val only)": [(pth(REC_THIN, f"thin_SKR_100pct_s{k}", "val"), None) for k in range(5, 10)],
    "CLD_s5-9 (THIN b5 bf16; val only)": [(pth(REC_THIN, f"thin_CLD_100pct_s{k}", "val"), None) for k in range(5, 10)],
    "FINAL ens (calib backfill CPU; val+rf)": [(pth(REC_CALIB, "FINAL", "val"), pth(REC_CALIB, "FINAL", "rf"))],
}

rows = [l.rstrip("\n").split("\t") for l in open(SETS_TSV) if l.strip()]
RFSET = {r[0]: r[1] for r in rows[1:]}

def load(p):
    d = json.load(open(p))
    g = np.array(d["grid"], dtype=float)
    return d, g

def opgrid_idx(g):
    # OPGRID = -4..+12 step 0.1 (exclude the inserted +0.75 diagnostic point)
    return [i for i, b in enumerate(g) if abs(round(b * 10) - b * 10) < 1e-6]

def arrs(cells, stems, keepmask=None):
    """sum arrays over stems; keepmask[stem] False -> crack pred zeroed."""
    pred = tp = rp = rr = 0
    ngt = 0
    for s in stems:
        c = cells[s]
        ngt += c["n_gt"]
        if keepmask is not None and not keepmask[s]:
            continue
        pred = pred + np.array(c["pred"], dtype=np.int64)
        tp = tp + np.array(c["tp"], dtype=np.int64)
        rp = rp + np.array(c["relp_tp"], dtype=np.int64)
        rr = rr + np.array(c["relr_tp"], dtype=np.int64)
    return pred, tp, rp, rr, ngt

def metrics_at(cells, stems, i, keep=None):
    n = len(next(iter(cells.values()))["pred"])
    z = np.zeros(n, dtype=np.int64)
    pred, tp, rp, rr, ngt = arrs(cells, stems, keep)
    pred = pred if isinstance(pred, np.ndarray) else z
    tp = tp if isinstance(tp, np.ndarray) else z
    rp = rp if isinstance(rp, np.ndarray) else z
    rr = rr if isinstance(rr, np.ndarray) else z
    relP = rp[i] / pred[i] if pred[i] else float("nan")
    relR = rr[i] / ngt if ngt else float("nan")
    relF = 2 * relP * relR / (relP + relR) if (relP == relP and relR == relR and relP + relR) else float("nan")
    iou = tp[i] / (pred[i] + ngt - tp[i]) if (pred[i] + ngt - tp[i]) else float("nan")
    fa = 0; fa_cells = 0; off_neg = 0; off_pos = 0
    for s in stems:
        c = cells[s]
        if keep is not None and not keep[s]:
            continue
        pr = c["pred"][i]
        if c["n_gt"] == 0:
            fa += pr; fa_cells += int(pr >= 20); off_neg += pr - c["relp_tp"][i]
        else:
            off_pos += pr - c["relp_tp"][i]
    return dict(relR=relR, relP=relP, relF=relF, iou=iou, fa_px=fa, fa_cells=fa_cells,
                pred_gt=(pred[i] / ngt if ngt else float("nan")), off_neg=off_neg, off_pos=off_pos)

def choose_brel(cells, stems, g, keep=None):
    idx = opgrid_idx(g)
    pred, tp, rp, rr, ngt = arrs(cells, stems, keep)
    best = None; bestp = None
    for i in idx:
        P = rp[i] / pred[i] if pred[i] else 0.0
        R = rr[i] / ngt
        if bestp is None or P > bestp[0] + 1e-15:
            bestp = (P, i)
        if P >= 0.90 and (best is None or R > best[0] + 1e-15):
            best = (R, i)
    if best is not None:
        return best[1], True
    return bestp[1], False

def auroc(scores_pos, scores_neg):
    if not scores_pos or not scores_neg:
        return float("nan")
    tot = 0.0
    for a in scores_pos:
        for b in scores_neg:
            tot += 1.0 if a > b else (0.5 if a == b else 0.0)
    return tot / (len(scores_pos) * len(scores_neg))

def one_run(vp, rp_, score_key):
    dv, gv = load(vp)
    cv = dv["cells"]; vst = sorted(cv)
    out = {"val_path": str(vp.relative_to(T)), "rf_path": str(rp_.relative_to(T)) if rp_ else None}
    pos = [s for s in vst if cv[s]["n_gt"] >= 20]
    t = min(cv[s]["s"][score_key] for s in pos) - 1e-3
    out["t"] = t
    keep_v = {s: cv[s]["s"][score_key] >= t for s in vst}
    out["val_neg_gated"] = sum(1 for s in vst if cv[s]["n_gt"] == 0 and not keep_v[s])
    out["val_neg"] = sum(1 for s in vst if cv[s]["n_gt"] == 0)
    i0 = int(np.argmin(np.abs(gv - 0.0)))
    ib, reach = choose_brel(cv, vst, gv)
    ibg, reachg = choose_brel(cv, vst, gv, keep_v)
    out["b_rel"] = (float(gv[ib]), reach); out["b_rel_gated"] = (float(gv[ibg]), reachg)
    sets = {"val": (cv, vst, gv)}
    if rp_ is not None:
        dr, gr = load(rp_)
        assert list(gr) == list(gv)
        cr = dr["cells"]
        for name in ("F51", "H36", "F19"):
            sets[name] = (cr, sorted(s for s in cr if RFSET.get(s) == name), gr)
    res = {}
    for name, (cells, stems, g) in sets.items():
        keep = {s: cells[s]["s"][score_key] >= t for s in stems}
        r = {}
        for lab, i, k in (("b0", i0, None), ("b0_gate", i0, keep), ("brel", ib, None), ("brel_gate", ib, keep),
                          ("brelG_gate", ibg, keep)):
            r[lab] = metrics_at(cells, stems, i, k)
        posc = [s for s in stems if cells[s]["n_gt"] >= 20]
        negc = [s for s in stems if cells[s]["n_gt"] == 0]
        r["n_cells"] = len(stems); r["n_pos"] = len(posc); r["n_neg"] = len(negc)
        r["pos_gated"] = sum(1 for s in posc if not keep[s])
        r["pos_gated_gtpx"] = int(sum(cells[s]["n_gt"] for s in posc if not keep[s]))
        r["gt_px"] = int(sum(cells[s]["n_gt"] for s in stems))
        r["neg_gated"] = sum(1 for s in negc if not keep[s])
        r["auroc_s1"] = auroc([cells[s]["s"]["1"] for s in posc], [cells[s]["s"]["1"] for s in negc])
        r["auroc_s20"] = auroc([cells[s]["s"]["20"] for s in posc], [cells[s]["s"]["20"] for s in negc])
        res[name] = r
    out["sets"] = res
    return out

def mean(xs):
    xs = [x for x in xs if x == x]
    return sum(xs) / len(xs) if xs else float("nan")

def main():
    score_key = sys.argv[1] if len(sys.argv) > 1 else "1"
    allres = {}
    lines = [f"a6_gate.py md5 {hashlib.md5(open(__file__, 'rb').read()).hexdigest()[:8]}  gate score s{score_key}  (DESCRIPTIVE; val + _rf only)"]
    for arm, runs in ARMS.items():
        R = [one_run(v, r, score_key) for v, r in runs]
        allres[arm] = R
        lines.append(f"\n## {arm}  (n runs {len(R)})")
        lines.append("  t per run: " + " ".join(f"{x['t']:.2f}" for x in R)
                     + " | b_rel ungated: " + " ".join(f"{x['b_rel'][0]:+.1f}{'' if x['b_rel'][1] else '!'}" for x in R)
                     + " | b_rel gated: " + " ".join(f"{x['b_rel_gated'][0]:+.1f}{'' if x['b_rel_gated'][1] else '!'}" for x in R)
                     + "  (! = unreachable, max-precision b)")
        lines.append("  val crack-free cells gated out per run: " + " ".join(f"{x['val_neg_gated']}/{x['val_neg']}" for x in R))
        for sname in R[0]["sets"]:
            S = [x["sets"][sname] for x in R]
            lines.append(f"  [{sname}] cells {S[0]['n_cells']} pos {S[0]['n_pos']} neg {S[0]['n_neg']} GT px {S[0]['gt_px']}"
                         f" | AUROC s1 {mean([s['auroc_s1'] for s in S]):.3f} s20 {mean([s['auroc_s20'] for s in S]):.3f}"
                         f" | pos gated {mean([s['pos_gated'] for s in S]):.1f} ({mean([s['pos_gated_gtpx'] for s in S]):.0f} GT px)"
                         f" | neg gated {mean([s['neg_gated'] for s in S]):.1f}/{S[0]['n_neg']}")
            for lab in ("b0", "b0_gate", "brel", "brel_gate", "brelG_gate"):
                M = [s[lab] for s in S]
                lines.append(f"    {lab:11s} relR {mean([m['relR'] for m in M]):.4f} relP {mean([m['relP'] for m in M]):.4f}"
                             f" relF1 {mean([m['relF'] for m in M]):.4f} IoU {mean([m['iou'] for m in M]):.4f}"
                             f" pred/GT {mean([m['pred_gt'] for m in M]):.3f} FApx {mean([m['fa_px'] for m in M]):8.1f}"
                             f" FAcells {mean([m['fa_cells'] for m in M]):4.1f} offGT negcells {mean([m['off_neg'] for m in M]):8.1f}"
                             f" offGT poscells {mean([m['off_pos'] for m in M]):8.1f}")
    od = T / "ideas/arch_out"
    (od / f"a6_gate_s{score_key}.txt").write_text("\n".join(lines) + "\n")
    json.dump(allres, open(od / f"a6_gate_s{score_key}.json", "w"), indent=1, default=float)
    print("\n".join(lines))

if __name__ == "__main__":
    main()
