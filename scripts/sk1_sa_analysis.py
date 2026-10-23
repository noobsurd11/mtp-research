"""S-a (team_2026-10-21/skcdf/protocol_sa.md): fixed logit adjustment tau = 1 on existing P-series checkpoints.
Rule 1 per arm (X+LA - X), and (SSL+LA) - (sup+LA) next to SSL - sup per fraction, in four test-cell sets from the
per-cell counts in la_sa_test.json (tau 0 rows checked against the re-score JSONs by the scorer; here the pooled
per-cell sums are also checked against the tau-0 pooled values).
Usage: .venv/bin/python scripts/sk1_sa_analysis.py | tee results/sk1/la_sa.md
"""
import json
import numpy as np

T = json.load(open("results/sk1/la_sa_test.json"))
V = json.load(open("results/sk1/la_sa_val.json"))
NOISY = "CSIR_00070_r8_c4"
TWINS = ["CFVS_00006_r5_c5", "CFVS_00033_r8_c4", "CFVS_00035_r8_c4", "CFVS_00042_r8_c4", "CFVS_00018_r4_c4",
         "CFVS_00027_r4_c4", "ARTS_00020_r5_c1"]
SETS = [("all 50", []), ("without noisy cell", [NOISY]), ("without 7 twins", TWINS), ("without both", TWINS + [NOISY])]
s = lambda p, n: [f"{p}_s{i}" for i in n]
ARMS = {
    "A5c": s("p12_A_5pct", range(3)) + s("p13_A_5pct", (3, 4)), "Cs5": s("p13_Cs_5pct", range(3)),
    "CsM5": s("p13_CsM_5pct", range(5)), "BsM5": s("p13_BsM_5pct", range(5)), "BsD5 (P17)": s("p17_BsD_5pct", range(5)),
    "A10": s("p6_L3_10pct", range(3)), "BsM10 (P18, expl.)": s("p18_BsM_10pct", range(3)),
    "A20": s("p6_L3_20pct", range(3)) + s("p16_A_20pct", (3, 4)), "S20": s("p16_S_20pct", range(5)),
    "BsM20 (P18, expl.)": s("p18_BsM_20pct", range(5)),
    "A50": s("p16_A_50pct", range(5)), "S50": s("p16_S_50pct", range(5)),
    "A100": s("p6_L3_100pct", range(3)) + s("p16_A_100pct", (3, 4)), "Sx100": s("p16_Sx_100pct", range(5))}
PAIRS = [("CsM5", "A5c"), ("BsM5", "A5c"), ("BsD5 (P17)", "A5c"), ("Cs5", "A5c"), ("BsM10 (P18, expl.)", "A10"),
         ("S20", "A20"), ("BsM20 (P18, expl.)", "A20"), ("S50", "A50"), ("Sx100", "A100")]
NM = ["crack IoU", "inactive IoU", "crack relF1@2"]


def cells(run, tau):
    return T[f"test/{run}/tau{tau}"]["per_cell"]


def pooled(run, tau, drop=()):
    c = np.array([v for k, v in cells(run, tau).items() if k not in drop], dtype=float)
    t = c.sum(0)  # crack tp fp fn, inactive tp fp fn
    ci, ii = t[0] / (t[0] + t[1] + t[2]), t[3] / (t[3] + t[4] + t[5])
    return ci, ii


def rel(run, tau):
    return T[f"test/{run}/tau{tau}"]["new_escdd"]["crack"]["rel_f1_2"]


def vals(run, tau, drop):  # relF1@2 only on all 50 (per-cell relaxed counts are not in the LA output)
    ci, ii = pooled(run, tau, drop)
    return [ci, ii, rel(run, tau) if not drop else np.nan]


def rule(xa, xb):
    xa, xb = np.asarray(xa), np.asarray(xb)
    if np.isnan(xa).all():
        return "–", 0
    dl = np.nanmean(xa) - np.nanmean(xb)
    thr = max(0.01, 2 * np.sqrt((np.nanstd(xa, ddof=1) ** 2 + np.nanstd(xb, ddof=1) ** 2) / 3))
    return f"{dl:+.4f} ({thr:.4f}){' >' if dl > thr else ' <' if dl < -thr else ''}", (1 if dl > thr else -1 if dl < -thr else 0)


err = max(abs(pooled(r, 0)[0] - T[f"test/{r}/tau0"]["new_escdd"]["crack"]["iou"]) for rs in ARMS.values() for r in rs)
print(f"sanity: per-cell pooled crack IoU vs scorer pooled (tau 0), max |diff| = {err:.1e}")
print("tau-0 check vs P-series re-score JSONs, max |diff| = %.1e" % max(v.get("check_max_abs_diff", 0) for v in T.values()))
print("absent-class predicted share at tau 1, max = %.5f" % max(v["absent_pred_share"] for k, v in T.items() if k.endswith("tau1")))

for lab, drop in SETS:
    print(f"\n## {lab}\n\n| arm | n | crack IoU | +LA | inactive IoU | +LA | crack relF1@2 | +LA | crack P → +LA | rule 1, X+LA − X |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for k, rs in ARMS.items():
        a = np.array([vals(r, 0, drop) for r in rs]); b = np.array([vals(r, 1, drop) for r in rs])
        P0 = np.mean([T[f"test/{r}/tau0"]["new_escdd"]["crack"]["precision"] for r in rs])
        P1 = np.mean([T[f"test/{r}/tau1"]["new_escdd"]["crack"]["precision"] for r in rs])
        rr = [rule(b[:, j], a[:, j])[0] for j in range(3)]
        cellsx = []
        for j in range(3):
            cellsx += [f"{np.nanmean(a[:, j]):.4f}" if not np.isnan(a[:, j]).all() else "–",
                       f"{np.nanmean(b[:, j]):.4f}" if not np.isnan(b[:, j]).all() else "–"]
        print(f"| {k} | {len(rs)} | " + " | ".join(cellsx) + f" | {P0:.3f} → {P1:.3f} | " + " / ".join(rr) + " |")
    print("\n| contrast | SSL − sup (no LA) | (SSL+LA) − (sup+LA) | SSL (no LA) − (sup+LA) |\n|---|---|---|---|")
    for x, y in PAIRS:
        A0 = np.array([vals(r, 0, drop) for r in ARMS[x]]); A1 = np.array([vals(r, 1, drop) for r in ARMS[x]])
        B0 = np.array([vals(r, 0, drop) for r in ARMS[y]]); B1 = np.array([vals(r, 1, drop) for r in ARMS[y]])
        f = lambda P, Q: " / ".join(rule(P[:, j], Q[:, j])[0] for j in range(3))
        print(f"| {x} − {y} | {f(A0, B0)} | {f(A1, B1)} | {f(A0, B1)} |")
print("\nCells: Δ (rule-1 threshold), '>' / '<' = beyond threshold. Order crack IoU / inactive IoU / crack relF1@2 "
      "(relF1@2 only on all 50 cells).")
print("\n## Val (description only): crack IoU mean over seeds at tau 0 / 0.5 / 1 / 2")
for k, rs in ARMS.items():
    print(f"- {k}: " + " / ".join(f"{np.mean([V[f'val/{r}/tau{t}']['new_escdd']['crack']['iou'] for r in rs]):.4f}" for t in ("0", "0.5", "1", "2")))

print("\n## Paired by checkpoint (all 50 cells): Δ = X+LA − X per checkpoint; mean, sd, min, max, n(Δ > 0)")
print("\n| arm | n | crack IoU Δ | inactive IoU Δ | crack relF1@2 Δ |\n|---|---|---|---|---|")
for k, rs in ARMS.items():
    d = np.array([[a - b for a, b in zip(vals(r, 1, ()), vals(r, 0, ()))] for r in rs])
    print(f"| {k} | {len(rs)} | " + " | ".join(
        f"{d[:, j].mean():+.4f} ± {d[:, j].std(ddof=1):.4f} [{d[:, j].min():+.4f}, {d[:, j].max():+.4f}] {int((d[:, j] > 0).sum())}/{len(rs)}"
        for j in range(3)) + " |")
mx = [(k, v["absent_pred_share"]) for k, v in T.items() if k.endswith("tau1") and v["absent_pred_share"] > 0.001]
print(f"\nRuns with absent-class share > 0.1% at tau 1: {len(mx)}; max |masked - unmasked| crack/inactive IoU = "
      + "%.4f" % max(max(abs(T[k + '_maskabsent']['new_escdd'][c]['iou'] - T[k]['new_escdd'][c]['iou']) for c in ('crack', 'inactive')) for k, _ in mx))
