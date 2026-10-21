"""Post hoc (21 Oct, data/decision.md D6): P18 contrasts with/without the 7 twin test cells and the noisy cell.
Agent 2. Pooled metrics from E1 per-cell counts (results/e1/raw_v2), sanity-checked against re-score JSONs.
Run from ~/mtp/research: .venv/bin/python team_2026-10-21/data/p18_twins.py"""
import glob, json, os
import numpy as np
E1 = {os.path.basename(f)[:-5]: json.load(open(f))["cells"]["test"] for f in glob.glob("results/e1/raw_v2/p*_s[0-9].json")}
RS = {}
for d in ("results/p6/raw", "results/p16/raw", "results/p18/raw"):
    for f in glob.glob(os.path.join(d, "p*_s[0-9].json")):
        for k, v in json.load(open(f)).items():
            if k.startswith("test/"): RS[k[5:]] = v["new_escdd"]
TW = ["CFVS_00006_r5_c5", "CFVS_00033_r8_c4", "CFVS_00035_r8_c4", "CFVS_00042_r8_c4", "CFVS_00018_r4_c4", "CFVS_00027_r4_c4", "ARTS_00020_r5_c1"]
NOISY = "CSIR_00070_r8_c4"
TRAIN_TW = ["CFVS_00003_r5_c5", "CFVS_00037_r8_c4", "CFVS_00032_r8_c4", "CFVS_00020_r4_c4", "CFVS_00022_r4_c4", "CFVS_00031_r4_c4", "ARTS_00081_r5_c1"]
def pooled(run, drop=()):
    c = [v for s, v in E1[run].items() if s not in drop]
    t = {k: sum(x.get(k, 0) for x in c) for k in ("crack_tp", "crack_gt", "crack_pred", "crack_p2_hit", "crack_r2_hit", "inact_tp", "inact_union")}
    p, r = t["crack_p2_hit"] / max(t["crack_pred"], 1), t["crack_r2_hit"] / t["crack_gt"]
    return np.array([t["crack_tp"] / (t["crack_gt"] + t["crack_pred"] - t["crack_tp"]), t["inact_tp"] / t["inact_union"], 2 * p * r / (p + r), p])
ARMS = {"A10": [f"p6_L3_10pct_s{i}" for i in range(3)], "BsM10": [f"p18_BsM_10pct_s{i}" for i in range(3)],
        "A20": [f"p6_L3_20pct_s{i}" for i in range(3)] + [f"p16_A_20pct_s{i}" for i in (3, 4)],
        "BsM20": [f"p18_BsM_20pct_s{i}" for i in range(5)]}
err = max(abs(pooled(r)[j] - RS[r][c][m]) for rs in ARMS.values() for r in rs
          for j, (c, m) in enumerate((("crack", "iou"), ("inactive", "iou"), ("crack", "rel_f1_2"), ("crack", "rel_p2"))))
print(f"sanity: max |E1 pooled - re-score| = {err:.1e}")
for frac in ("10pct", "20pct"):
    lab = set(open(os.path.expanduser(f"~/mtp/datasets/splits_benchmark/seed0/labeled_{frac}.txt")).read().split())
    unl = set(open(os.path.expanduser(f"~/mtp/datasets/splits_benchmark/seed0/unlabeled_{frac}.txt")).read().split())
    print(f"{frac} split seed 0: train twins labelled {sorted(t for t in TRAIN_TW if t in lab)}; unlabelled {sorted(t for t in TRAIN_TW if t in unl)}")
for drop, name in (((), "all 50"), (tuple(TW), "without 7 twins"), (tuple(TW) + (NOISY,), "without twins + noisy cell")):
    V = {k: np.array([pooled(r, drop) for r in rs]) for k, rs in ARMS.items()}
    print(f"\n## {name}")
    for k, v in V.items():
        print(f"  {k:6s} " + "  ".join(f"{v[:, j].mean():.3f}±{v[:, j].std(ddof=1):.3f}" for j in range(4)))
    for s, b in (("BsM10", "A10"), ("BsM20", "A20")):
        out, sg = [], []
        for j in range(3):
            xa, xb = V[s][:, j], V[b][:, j]; dl = xa.mean() - xb.mean()
            thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
            out.append(f"{dl:+.4f} ({thr:.4f})"); sg.append(1 if dl > thr else -1 if dl < -thr else 0)
        dp = V[s][:, 3].mean() - V[b][:, 3].mean()
        verdict = "passes" if any(x == 1 for x in sg) and not any(x == -1 for x in sg) else "fails"
        print(f"  {s} - {b}: crack IoU / inactive IoU / relF1@2 = " + " / ".join(out) + f"  -> {verdict} {sg}; relP@2 {dp:+.4f}")
