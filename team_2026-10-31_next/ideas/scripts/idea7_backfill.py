"""calib idea 7: descriptive backfill of the el_metrics metrics for the protocol_100 arms (+ FINAL), val + E1 (+ Hanifi rf) only.
NO TEST CELL is read (no test records exist). Operating points come from each run's own val records.
Usage: python idea7_backfill.py --rec DIR --ctx e1_context.tsv --out OUT.txt [--json OUT.json]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import el_metrics as E  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--rec", required=True)
ap.add_argument("--ctx", required=True)
ap.add_argument("--f51", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--json")
ap.add_argument("--arms", nargs="+", default=["SUP5", "SUPPF5", "MIMPF5", "CP5", "FINAL"])
a = ap.parse_args()
R = Path(a.rec)
ctx = {f[0]: (f[2] == "scuff=1", f[3] == "halfcut=1") for f in (l.rstrip("\n").split("\t") for l in open(a.ctx)) if len(f) >= 4}
SUBS = {"val": {"val": None}, "ext": {"E1": None, "E1 sh29": [s for s in ctx if ctx[s][0] and ctx[s][1]], "E1 other77": [s for s in ctx if not (ctx[s][0] and ctx[s][1])]},
        "rf": {"rf": None, "rf F51": [l.strip() for l in open(a.f51) if l.strip()]}}
KEYS = [("comp_recall_at_opc", "compR@OPc"), ("comp_prec_at_opc", "compP@OPc"), ("relR_at_opr", "relR@OPr"), ("relP_at_opr", "relP@OPr"),
        ("cell_deployed.recall", "cellR"), ("cell_deployed.fa_rate", "cellFA"), ("cell_deployed.precision", "cellP"), ("cell_deployed.auroc", "cellAUROC"),
        ("inactive_area_err.mae_all", "inactMAE%"), ("inactive_area_err.mae_inactive_cells", "inactMAE%(inact cells)"),
        ("at_deployed.IoU", "crackIoU@dep"), ("at_deployed.relR", "relR@dep"), ("op_comp.b", "b_OPc"), ("op_rel.b", "b_OPr")]


def get(d, k):
    for p in k.split("."):
        d = d[p]
    return d


out, L = {}, ["idea 7 backfill (calib, descriptive; val + E1 + Hanifi rf only, no test). Per-run OPs chosen on that run's val.",
              "cell metrics at the deployed b (0 single runs, +0.75 FINAL); cell positive = GT crack >= 20 px; flag = >= 20 px predicted.",
              "mean (sd) over seeds; FINAL = one ensemble.", ""]
for arm in a.arms:
    ms = [f.name.split(".")[0] for f in sorted(R.glob(f"{arm}_m*.val.json"))] if arm != "FINAL" else ["FINAL"]
    for m in ms:
        V = json.load(open(R / f"{m}.val.json"))
        bdep = 0.75 if arm == "FINAL" else 0.0
        for sp, subs in SUBS.items():
            p = R / f"{m}.{sp}.json"
            if not p.exists():
                continue
            T = V if sp == "val" else json.load(open(p))
            for sn, st in subs.items():
                s = E.summarize(V, T, bdep, st)
                out.setdefault(arm, {}).setdefault(sn, []).append({"member": m, "runs": T.get("runs"), **s})
    for sn in [x for v in SUBS.values() for x in v]:
        rs = out.get(arm, {}).get(sn, [])
        if not rs:
            continue
        parts = []
        for k, lab in KEYS:
            v = np.array([get(r, k) for r in rs], float)
            parts.append(f"{lab} {np.nanmean(v):.3f}" + (f"({np.nanstd(v, ddof=1):.3f})" if len(v) > 1 else ""))
        nn = rs[0]["cell_deployed"]
        L.append(f"{arm:7s} {sn:10s} n={rs[0]['n_cells']} comps={rs[0]['gt_comp20']} cells+/-/amb={nn['n_pos']}/{nn['n_neg']}/{nn['n_ambiguous']}: " + "; ".join(parts))
    L.append("")
# descriptive contrasts on E1 / val (no rule verdict: E1 is descriptive and val is the selection set)
L.append("descriptive contrasts (mean difference, seeds; NOT a rule-1 verdict):")
for A, B in (("SUPPF5", "SUP5"), ("MIMPF5", "SUPPF5"), ("CP5", "SUP5")):
    for sn in ("val", "E1", "E1 sh29", "E1 other77", "rf", "rf F51"):
        ra, rb = out.get(A, {}).get(sn), out.get(B, {}).get(sn)
        if not ra or not rb:
            continue
        d = []
        for k, lab in KEYS[:10]:
            va, vb = np.array([get(r, k) for r in ra], float), np.array([get(r, k) for r in rb], float)
            d.append(f"{lab} {np.nanmean(va) - np.nanmean(vb):+.3f}")
        L.append(f"  {A} - {B} [{sn}]: " + "; ".join(d))
# self-check of these CPU fp32 records vs the openings' m0 JSONs (GPU bf16), b = 0, val and E1 (coach A4 tolerance 0.0005)
L += ["", "self-check: CPU fp32 records vs the opening m0 JSONs (GPU bf16) at b = 0; max |delta| over crack IoU, relP@2, relR@2, inactive IoU, comp R / P"]
F100 = Path("/home/yugma/mtp/research/team_2026-10-29_features/results/f100")
DC = json.load(open("/home/yugma/mtp/research/team_2026-10-29_features/d_checks/d_cells.json"))
for arm in a.arms:
    ms = [f.name.split(".")[0] for f in sorted(R.glob(f"{arm}_m*.val.json"))] if arm != "FINAL" else ["FINAL"]
    for m in ms:
        for sp in ("val", "ext"):
            p = R / f"{m}.{sp}.json"
            if not p.exists():
                continue
            rec = json.load(open(p))
            if arm == "FINAL":
                ref, src = DC[sp]["FINAL"]["0.0"], "d_cells (CPU fp32)"
            else:
                run = Path(rec["runs"][0]).name
                f = next((F100 / o / "raw" / "m0" / f"{run}.json" for o in ("opening1", "opening2") if (F100 / o / "raw" / "m0" / f"{run}.json").exists()), None)
                if f is None:
                    continue
                ref, src = json.load(open(f))["cells"][sp], f"{f.parent.parent.parent.name} m0 (GPU bf16) {run}"
            ok, LL = E.selfcheck(rec, ref)
            d = max(abs(float(x.split("delta ")[1].split()[0])) for x in LL if "nan" not in x.split("delta ")[1])
            L.append(f"  {m:10s} {sp}: {'PASS' if ok else 'FAIL'} max|delta| {d:.5f} vs {src}")
Path(a.out).write_text("\n".join(L) + "\n")
if a.json:
    json.dump(out, open(a.json, "w"))
print("\n".join(L))
