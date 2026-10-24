"""Track D inactive-edge re-score analysis (protocol team_2026-10-24_go/trackD/protocol_edge.md).

Reads results/trackD_edge/edge.json (per run, tau, per cell). Checks standard rows against results/sk1/la_sa_test.json
and results/al1/raw/*.json; prints per-arm standard vs banded, per-arm paired delta, the six contrasts (rule 1,
scripts/ssl_rules.py arithmetic) in four cell sets, per-source rows, band shares.
Usage: python scripts/trackD_edge_analysis.py > results/trackD_edge/analysis.txt
"""
import json
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent.parent / "results"
E = json.loads((R / "trackD_edge" / "edge.json").read_text())
LA = json.loads((R / "sk1" / "la_sa_test.json").read_text())
NOISY = "CSIR_00070_r8_c4"
TWINS = ["CFVS_00006_r5_c5", "CFVS_00033_r8_c4", "CFVS_00035_r8_c4", "CFVS_00042_r8_c4", "CFVS_00018_r4_c4",
         "CFVS_00027_r4_c4", "ARTS_00020_r5_c1"]
ARMS = {
    "A5c": ["p12_A_5pct_s0", "p12_A_5pct_s1", "p12_A_5pct_s2", "p13_A_5pct_s3", "p13_A_5pct_s4"],
    "BsM5": [f"p13_BsM_5pct_s{i}" for i in range(5)],
    "CsM5": [f"p13_CsM_5pct_s{i}" for i in range(5)],
    "BsD5": [f"p17_BsD_5pct_s{i}" for i in range(5)],
    **{f"al1_{a}": [f"al1_{a}_s{i}" for i in range(5)] for a in ("A5", "BsM5", "AL5", "ALd5", "ALdh5", "CPS5", "CPSm5")},
    "A10": [f"p6_L3_10pct_s{i}" for i in range(3)],
    "A50": [f"p16_A_50pct_s{i}" for i in range(5)],
    "A100": ["p6_L3_100pct_s0", "p6_L3_100pct_s1", "p6_L3_100pct_s2", "p16_A_100pct_s3", "p16_A_100pct_s4"],
}
CONTRASTS = [("BsM5", 0, "A5c", 0), ("CsM5", 0, "A5c", 0), ("BsD5", 0, "A5c", 0), ("BsM5", 1, "A5c", 1),
             ("al1_BsM5", 0, "al1_A5", 0), ("al1_AL5", 0, "al1_A5", 0)]
DESC = [("A10", 0, "A5c", 0), ("A100", 0, "A5c", 0)]
cells_all = sorted(next(iter(E.values()))["per_cell"])
assert len(cells_all) == 50 and NOISY in cells_all and all(t in cells_all for t in TWINS), [t for t in TWINS if t not in cells_all]
SETS = {"all 50": cells_all, "no noisy": [c for c in cells_all if c != NOISY],
        "no twins": [c for c in cells_all if c not in TWINS], "neither": [c for c in cells_all if c != NOISY and c not in TWINS]}
SRC = ["ARTS", "BMRK", "CFVS", "CSIR"]


def met(run, tau, cells, var):
    pc = E[f"{run}/tau{tau}"]["per_cell"]
    v = np.sum([pc[c][var] for c in cells], 0)
    tp, fp, fn, rtp, pp, rtg, g = v
    P, Rr = rtp / max(pp, 1), rtg / max(g, 1)
    return {"iou": tp / max(tp + fp + fn, 1), "recall": tp / max(tp + fn, 1), "precision": tp / max(tp + fp, 1),
            "relf1": 2 * P * Rr / max(P + Rr, 1e-9), "relp": P}


def arm(a, tau, cells, var, k):
    return np.array([met(r, tau, cells, var)[k] for r in ARMS[a]])


def rule(xb, xa):
    d = xb.mean() - xa.mean()
    thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    return d, thr, ("BETTER" if d > thr else "WORSE" if d < -thr else "n.d.")


# ---- checks
print("## Checks")
mx = 0.0
for a, runs in ARMS.items():
    for r in runs:
        for tau in (0, 1):
            x = E[f"{r}/tau{tau}"]
            assert x["step"] == 20000, (r, x["step"])
            m = met(r, tau, cells_all, "crack_std")
            inn = np.sum([v["inactive"] for v in x["per_cell"].values()], 0)
            iiou = inn[0] / max(inn.sum(), 1)
            ref = None
            if f"test/{r}/tau{tau}" in LA:
                ref = LA[f"test/{r}/tau{tau}"]["new_escdd"]
            elif tau == 0 and (R / "al1" / "raw" / f"{r}.json").exists():
                ref = json.loads((R / "al1" / "raw" / f"{r}.json").read_text())[f"test/{r}"]["new_escdd"]
            if ref is None:
                print(f"  no reference for {r} tau{tau}")
                continue
            d = max(abs(ref["crack"]["iou"] - m["iou"]), abs(ref["inactive"]["iou"] - iiou),
                    abs(ref["crack"]["rel_f1_2"] - m["relf1"]))
            mx = max(mx, d)
print(f"  max |diff| vs reference JSONs (crack IoU, inactive IoU, relF1@2): {mx:.2e}; all steps 20000")

# ---- band shares
gt = sum(v["crack_std"][6] for v in E["p12_A_5pct_s0/tau0"]["per_cell"].values())
gtb = sum(v["gt_crack_in_band"] for v in E["p12_A_5pct_s0/tau0"]["per_cell"].values())
print(f"\n## Band: test GT crack px {gt}, inside the 2-px inactive band {gtb} ({gtb / gt:.3f})")
for s in SRC:
    cs = [c for c in cells_all if c.startswith(s)]
    g1 = sum(E["p12_A_5pct_s0/tau0"]["per_cell"][c]["crack_std"][6] for c in cs)
    g2 = sum(E["p12_A_5pct_s0/tau0"]["per_cell"][c]["gt_crack_in_band"] for c in cs)
    print(f"  {s}: {g2} of {g1} ({g2 / max(g1, 1):.3f})")

# ---- per arm
print("\n## Per arm, all 50, mean ± sd over seeds (tau 0 unless +LA)")
print("| arm | n | crack IoU std | banded | Δ paired (n>0) | relF1@2 std | banded | recall std | banded | recall in band | pred crack px in band |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
rows = [(a, 0) for a in ARMS] + [("A5c", 1), ("BsM5", 1)]
for a, tau in rows:
    s, b = arm(a, tau, cells_all, "crack_std", "iou"), arm(a, tau, cells_all, "crack_band", "iou")
    fs, fb = arm(a, tau, cells_all, "crack_std", "relf1"), arm(a, tau, cells_all, "crack_band", "relf1")
    rs, rb = arm(a, tau, cells_all, "crack_std", "recall"), arm(a, tau, cells_all, "crack_band", "recall")
    # recall inside band: tp_in = tp_std - tp_band ; gt_in = gt_std - gt_band
    rin, pin = [], []
    for r in ARMS[a]:
        pc = E[f"{r}/tau{tau}"]["per_cell"].values()
        tps = sum(v["crack_std"][0] for v in pc); tpb = sum(v["crack_band"][0] for v in pc)
        gs = sum(v["crack_std"][6] for v in pc); gb = sum(v["crack_band"][6] for v in pc)
        rin.append((tps - tpb) / max(gs - gb, 1)); pin.append(sum(v["pred_crack_in_band"] for v in pc))
    d = b - s
    print(f"| {a}{'+LA' if tau else ''} | {len(s)} | {s.mean():.4f}±{s.std(ddof=1):.4f} | {b.mean():.4f}±{b.std(ddof=1):.4f} | "
          f"{d.mean():+.4f}±{d.std(ddof=1):.4f} ({(d > 0).sum()}/{len(d)}) | {fs.mean():.4f} | {fb.mean():.4f} | {rs.mean():.3f} | {rb.mean():.3f} | "
          f"{np.mean(rin):.3f} | {np.mean(pin):.0f} |")

# ---- contrasts
for name, cl in [("CONTRASTS (rule 1)", CONTRASTS), ("DESCRIPTIVE", DESC)]:
    print(f"\n## {name}: Δ (thr) verdict, standard vs banded")
    for sname, cells in SETS.items():
        print(f"\n### {sname} ({len(cells)} cells)")
        print("| contrast | metric | standard | banded | sign flip past thr |")
        print("|---|---|---|---|---|")
        for b_, tb, a_, ta in cl:
            lab = f"{b_}{'+LA' if tb else ''} − {a_}{'+LA' if ta else ''}"
            for k in ("iou", "relf1", "recall"):
                ds = rule(arm(b_, tb, cells, "crack_std", k), arm(a_, ta, cells, "crack_std", k))
                db = rule(arm(b_, tb, cells, "crack_band", k), arm(a_, ta, cells, "crack_band", k))
                flip = "YES" if (np.sign(ds[0]) != np.sign(db[0]) and abs(db[0]) > db[1]) else "no"
                print(f"| {lab} | {k} | {ds[0]:+.4f} ({ds[1]:.4f}) {ds[2]} | {db[0]:+.4f} ({db[1]:.4f}) {db[2]} | {flip} |")

# ---- per source
print("\n## Per source, crack IoU std → banded (seed means, tau 0), descriptive")
print("| arm | " + " | ".join(SRC) + " |")
print("|---|" + "---|" * len(SRC))
for a in ARMS:
    out = []
    for s in SRC:
        cs = [c for c in cells_all if c.startswith(s)]
        out.append(f"{arm(a, 0, cs, 'crack_std', 'iou').mean():.3f} → {arm(a, 0, cs, 'crack_band', 'iou').mean():.3f}")
    print(f"| {a} | " + " | ".join(out) + " |")
print("\n## Per source contrasts, crack IoU (rule-1 arithmetic, descriptive)")
for s in SRC:
    cs = [c for c in cells_all if c.startswith(s)]
    for b_, tb, a_, ta in CONTRASTS:
        ds = rule(arm(b_, tb, cs, "crack_std", "iou"), arm(a_, ta, cs, "crack_std", "iou"))
        db = rule(arm(b_, tb, cs, "crack_band", "iou"), arm(a_, ta, cs, "crack_band", "iou"))
        print(f"  {s} {b_}{'+LA' if tb else ''} − {a_}{'+LA' if ta else ''}: std {ds[0]:+.4f} ({ds[1]:.4f}) {ds[2]}; band {db[0]:+.4f} ({db[1]:.4f}) {db[2]}")
