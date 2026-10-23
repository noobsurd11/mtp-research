"""SK1 analysis (protocol team_2026-10-21/skcdf/protocol_v2.md sections 8-9): P8 rule-1 arithmetic and a paired
cell bootstrap for every SK1 contrast, in the four test-cell sets (all 50 / without the noisy cell / without the 7
twin test cells / without both), from E1 per-cell counts (results/e1/raw_v2), checked first against the re-score JSONs.
Also crack FP on the noisy cell per run. Final-step weights only (the re-score / E1 inputs are step 20,000).
Usage: .venv/bin/python scripts/sk1_analysis.py | tee results/sk1/sk1_cellsets.md
"""
import glob, json, os
import numpy as np

NOISY = "CSIR_00070_r8_c4"
TWINS = ["CFVS_00006_r5_c5", "CFVS_00033_r8_c4", "CFVS_00035_r8_c4", "CFVS_00042_r8_c4", "CFVS_00018_r4_c4",
         "CFVS_00027_r4_c4", "ARTS_00020_r5_c1"]
SETS = [("all 50", []), ("without noisy cell", [NOISY]), ("without 7 twins", TWINS), ("without both", TWINS + [NOISY])]
ARMS = {"A5c": ["p12_A_5pct_s0", "p12_A_5pct_s1", "p12_A_5pct_s2", "p13_A_5pct_s3", "p13_A_5pct_s4"],
        "AB5": [f"sk1_AB_5pct_s{i}" for i in range(5)],
        "BsD5": [f"sk1_BsD_5pct_s{i}" for i in range(5)],
        "BsDB5": [f"sk1_BsDB_5pct_s{i}" for i in range(5)],
        "BsDBn5": [f"sk1_BsDBn_5pct_s{i}" for i in range(5)],
        "BsD5(P17, full pool)": [f"p17_BsD_5pct_s{i}" for i in range(5)],
        "BsM5(P13, full pool)": [f"p13_BsM_5pct_s{i}" for i in range(5)]}
PAIRS = [("BsDB5", "BsD5", "rule 1, primary"), ("AB5", "A5c", "rule 2, secondary"), ("BsDB5", "BsDBn5", "rule 3, secondary"),
         ("BsDB5", "A5c", "descriptive"), ("BsD5", "A5c", "descriptive"),
         ("BsDBn5", "BsD5", "EXPLORATORY"),
         ("BsDBn5", "A5c", "exploratory")]
NAMES = ["crack IoU", "inactive IoU", "crack relF1@2", "crack relP@2"]
KEYS = ("crack_tp", "crack_gt", "crack_pred", "crack_p2_hit", "crack_r2_hit", "inact_tp", "inact_union")

E1 = {os.path.basename(f)[:-5]: json.load(open(f))["cells"]["test"] for f in glob.glob("results/e1/raw_v2/*_s[0-9].json")}
RS = {}
for d in ("results/p12/raw", "results/p13/raw", "results/p17/raw", "results/sk1/raw"):
    for f in glob.glob(os.path.join(d, "*_s[0-9].json")):
        for k, v in json.load(open(f)).items():
            if k.startswith("test/"):
                RS[k[5:]] = v["new_escdd"]
missing = [r for rs in ARMS.values() for r in rs if r not in E1 or r not in RS]
if missing:
    raise SystemExit(f"missing E1 or re-score JSONs: {missing}")
CELLS = sorted(E1[ARMS["A5c"][0]])
assert all(sorted(E1[r]) == CELLS for rs in ARMS.values() for r in rs) and len(CELLS) == 50
assert NOISY in CELLS and all(t in CELLS for t in TWINS)
C = {r: np.array([[E1[r][c].get(k, 0) for k in KEYS] for c in CELLS], dtype=np.float64) for rs in ARMS.values() for r in rs}


def metrics(t):  # t: (..., 7) summed counts
    ci = t[..., 0] / (t[..., 1] + t[..., 2] - t[..., 0])
    ii = t[..., 5] / t[..., 6]
    p, r = t[..., 3] / np.maximum(t[..., 2], 1), t[..., 4] / t[..., 1]
    return np.stack([ci, ii, 2 * p * r / (p + r), p], -1)


err = max(abs(metrics(C[r].sum(0))[j] - RS[r][c][m]) for rs in ARMS.values() for r in rs
          for j, (c, m) in enumerate((("crack", "iou"), ("inactive", "iou"), ("crack", "rel_f1_2"), ("crack", "rel_p2"))))
print(f"sanity: max |E1 pooled - re-score JSON| over all runs, 4 metrics = {err:.1e}\n")
print(f"Crack FP px on {NOISY} per run (E1 crack_pred - crack_tp):")
i_n = CELLS.index(NOISY)
for k, rs in ARMS.items():
    print(f"  {k:22s} " + ", ".join(f"s{r[-1]} {int(C[r][i_n, 2] - C[r][i_n, 0])}" for r in rs))

rng = np.random.default_rng(0)
B = 2000
for lab, drop in SETS:
    keep = np.array([c not in drop for c in CELLS])
    idx = np.flatnonzero(keep)
    boot = rng.integers(0, len(idx), size=(B, len(idx)))
    V = {k: np.array([metrics(C[r][keep].sum(0)) for r in rs]) for k, rs in ARMS.items()}
    BV = {k: np.mean([metrics(C[r][idx][boot].sum(1)) for r in rs], 0) for k, rs in ARMS.items()}  # (B, 4) seed-mean
    print(f"\n## {lab} ({keep.sum()} cells)\n\n| arm | seeds | " + " | ".join(NAMES) + " |\n|---|---|" + "---|" * len(NAMES))
    for k, v in V.items():
        print(f"| {k} | {len(v)} | " + " | ".join(f"{v[:, j].mean():.4f}±{v[:, j].std(ddof=1):.4f}" for j in range(4)) + " |")
    print("\n| contrast | role | " + " | ".join(NAMES[:3]) + " | rule-1 arithmetic | relP@2 Δ |\n|---|---|---|---|---|---|---|")
    for s, b, role in PAIRS:
        cells, sg = [], []
        for j in range(3):
            xa, xb = V[s][:, j], V[b][:, j]
            dl = xa.mean() - xb.mean()
            thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
            sg.append(1 if dl > thr else -1 if dl < -thr else 0)
            d = BV[s][:, j] - BV[b][:, j]
            lo, hi = np.percentile(d, [2.5, 97.5])
            cells.append(f"{dl:+.4f} ({thr:.4f}) [{lo:+.4f}, {hi:+.4f}]")
        w = "WORSE" if -1 in sg else "passes" if 1 in sg else "n.d."
        print(f"| {s} − {b} | {role.split(' (')[0]} | " + " | ".join(cells) + f" | {w} | {V[s][:, 3].mean() - V[b][:, 3].mean():+.4f} |")
print("\nCells: Δ (rule-1 threshold) [95% paired cell-bootstrap CI of the seed-mean Δ, 2,000 resamples, seed 0].")
