"""Track D labelset analysis (protocol team_2026-10-24_go/trackD/protocol_labelset.md §5-6, C's review notes).

Inputs (results/trackD_labelset/): d1_score.json (per run, tau, cell: crack std/band counts with relaxed@2, inactive),
d1_score_confusion.npz (per run/tau/cell 24x24), e1/<run>.json (E1 per-cell), ../../team_2026-10-24_go/trackD/draws/audit.json.
Rule: unit = draw (mean over its 3 seeds); thr = max(0.01, 2*sqrt(var_A/3 + var_B/3)) over draw-means.
Usage: python scripts/trackD_labelset_analysis.py > results/trackD_labelset/analysis.txt
"""
import json, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts_cv02"))
from e1_aggregate import arrays as e1_arrays, metrics as e1_metrics  # noqa: E402

D = ROOT / "results" / "trackD_labelset"
S = json.loads((D / "d1_score.json").read_text())
CONF = np.load(D / "d1_score_confusion.npz")
AUD = json.loads((ROOT / "team_2026-10-24_go" / "trackD" / "draws" / "audit.json").read_text())
ABS = json.loads((D / "absent_classes.json").read_text()) if (D / "absent_classes.json").exists() else {}  # from train logs
LA = json.loads((ROOT / "results" / "sk1" / "la_sa_test.json").read_text())
NOISY = "CSIR_00070_r8_c4"
TWINS = ["CFVS_00006_r5_c5", "CFVS_00033_r8_c4", "CFVS_00035_r8_c4", "CFVS_00042_r8_c4", "CFVS_00018_r4_c4",
         "CFVS_00027_r4_c4", "ARTS_00020_r5_c1"]
ARMS, DRAWS, SEEDS = ["R", "Tc", "Ts"], [0, 1, 2], [0, 1, 2]
RUN = lambda a, d, s: f"d1_{a}_d{d}_s{s}"
YARD = {"A5c": ["p12_A_5pct_s0", "p12_A_5pct_s1", "p12_A_5pct_s2", "p13_A_5pct_s3", "p13_A_5pct_s4"],
        "BsM5 (D7)": [f"al1_BsM5_s{i}" for i in range(5)], "L3 10%": [f"p6_L3_10pct_s{i}" for i in range(3)]}
CELLS = sorted(S[f"{RUN('R', 0, 0)}/tau0"]["per_cell"])
SETS = {"all 50": CELLS, "no noisy": [c for c in CELLS if c != NOISY], "no twins": [c for c in CELLS if c not in TWINS],
        "neither": [c for c in CELLS if c != NOISY and c not in TWINS]}
SRC = ["ARTS", "BMRK", "CFVS", "CSIR"]
PRIM = ["iou", "relf1", "recall"]
B = 2000


def agg(run, tau, cells, var="crack_std"):
    pc = S[f"{run}/tau{tau}"]["per_cell"]
    v = np.sum([pc[c][var] for c in cells], 0)
    tp, fp, fn, rtp, pp, rtg, g = v
    P, Rr = rtp / max(pp, 1), rtg / max(g, 1)
    i = np.sum([pc[c]["inactive"] for c in cells], 0)
    return {"iou": tp / max(tp + fp + fn, 1), "recall": tp / max(tp + fn, 1), "precision": tp / max(tp + fp, 1),
            "relf1": 2 * P * Rr / max(P + Rr, 1e-9), "relp": P, "relr": Rr, "inact_iou": i[0] / max(i.sum(), 1)}


def miou(run, tau, cells):
    c = sum(CONF[f"{run}/tau{tau}/{x}"] for x in cells).astype(np.float64)
    gt, pr, tp = c.sum(1), c.sum(0), np.diag(c)
    present = gt > 0
    return float(np.mean(tp[present] / (gt + pr - tp)[present])), int(present.sum())


def draw_means(arm, k, cells, tau=0):
    return np.array([np.mean([agg(RUN(arm, d, s), tau, cells)[k] for s in SEEDS]) for d in DRAWS])


def seed_vals(arm, k, cells, tau=0):
    return np.array([agg(RUN(arm, d, s), tau, cells)[k] for d in DRAWS for s in SEEDS])


def rule_draw(b, a):
    d = b.mean() - a.mean(); thr = max(0.01, 2 * np.sqrt(a.var(ddof=1) / 3 + b.var(ddof=1) / 3))
    return d, thr, ("BETTER" if d > thr else "WORSE" if d < -thr else "n.d.")


def rule_seed(b, a):
    d = b.mean() - a.mean(); thr = max(0.01, 2 * np.sqrt((a.std(ddof=1) ** 2 + b.std(ddof=1) ** 2) / 3))
    return d, thr, ("BETTER" if d > thr else "WORSE" if d < -thr else "n.d.")


def verdict(vs):
    better = any(v == "BETTER" for v in vs); worse = any(v == "WORSE" for v in vs)
    return "BETTER" if better and not worse else "WORSE" if worse and not better else ("MIXED" if better else "n.d.")


# ---- checks
print("## Checks")
mx, steps = 0.0, set()
for a in ARMS:
    for d in DRAWS:
        for s in SEEDS:
            r = RUN(a, d, s); steps.add(S[f"{r}/tau0"]["step"])
            ref = json.loads((D / "rescore" / f"{r}.json").read_text())[f"test/{r}"]["new_escdd"]
            m = agg(r, 0, CELLS)
            mx = max(mx, abs(ref["crack"]["iou"] - m["iou"]), abs(ref["crack"]["rel_f1_2"] - m["relf1"]), abs(ref["inactive"]["iou"] - m["inact_iou"]))
for y, runs in YARD.items():
    for r in runs:
        if f"test/{r}/tau0" in LA:
            mx = max(mx, abs(LA[f"test/{r}/tau0"]["new_escdd"]["crack"]["iou"] - agg(r, 0, CELLS)["iou"]))
print(f"  max |diff| vs lane re-score JSONs / la_sa_test.json: {mx:.2e}; steps {sorted(steps)}")

# ---- draws
print("\n## Draws (added 12 cells): crack cells, crack px, inactive cells / px, shares test position, absent classes in the 35")
for a in ARMS:
    for d in DRAWS:
        x = AUD["draws"][f"{a}_d{d}"]; ad = x["added_summary"]
        absent = ABS.get(f"{a}_d{d}", "?")
        print(f"  {a}_d{d}: +{ad['crack_cells']} crack cells, +{ad['crack_px']} px, +{ad['inactive_cells']} inactive cells / {ad['inactive_px']} px, "
              f"absent {absent}, test-pos {x['added_sharing_test_pos']}, BMRK/ARTS crack cells {ad['by_source'].get('BMRK', {}).get('crack_cells', 0)}/"
              f"{ad['by_source'].get('ARTS', {}).get('crack_cells', 0)}")

# ---- per-run table and draw means
print("\n## Per draw, all 50 (mean of 3 seeds): crack IoU / relF1@2 / recall / relP@2 / inactive IoU / mIoU(24)")
for a in ARMS:
    for d in DRAWS:
        rs = [RUN(a, d, s) for s in SEEDS]
        ms = [agg(r, 0, CELLS) for r in rs]; mi = [miou(r, 0, CELLS)[0] for r in rs]
        fpn = [S[f"{r}/tau0"]["per_cell"][NOISY]["crack_std"][1] for r in rs]
        print(f"  {a}_d{d}: " + " / ".join(f"{np.mean([m[k] for m in ms]):.4f}" for k in ("iou", "relf1", "recall", "relp", "inact_iou"))
              + f" / {np.mean(mi):.4f} | seeds IoU {[round(m['iou'], 4) for m in ms]} | noisy-cell crack FP {fpn}")

print("\n## Arms (9 runs; draw-mean sd) and yardsticks, all 50")
for a in ARMS:
    print(f"  {a}: " + ", ".join(f"{k} {draw_means(a, k, CELLS).mean():.4f} (draw sd {draw_means(a, k, CELLS).std(ddof=1):.4f})" for k in PRIM + ["relp", "inact_iou"])
          + f", mIoU {np.mean([miou(RUN(a, d, s), 0, CELLS)[0] for d in DRAWS for s in SEEDS]):.4f}")
    print(f"  {a}+LA: " + ", ".join(f"{k} {np.mean([agg(RUN(a, d, s), 1, CELLS)[k] for d in DRAWS for s in SEEDS]):.4f}" for k in PRIM + ["relp"]))
for y, runs in YARD.items():
    for tau in (0, 1):
        ms = [agg(r, tau, CELLS) for r in runs]
        print(f"  {y}{'+LA' if tau else ''} ({len(runs)}): " + ", ".join(f"{k} {np.mean([m[k] for m in ms]):.4f}" for k in PRIM + ["relp", "inact_iou"])
              + (f", mIoU {np.mean([miou(r, 0, CELLS)[0] for r in runs]):.4f}" if tau == 0 else ""))

# ---- primary contrasts
CON = [("Ts", "Tc", "PRIMARY 1"), ("Tc", "R", "PRIMARY 2"), ("Ts", "R", "secondary")]
for sname, cells in SETS.items():
    print(f"\n## Contrasts, {sname} ({len(cells)} cells): draw-level rule (seed-level 9 v 9 descriptive)")
    for b, a, lab in CON:
        vs, line = [], []
        for k in PRIM:
            dl = rule_draw(draw_means(b, k, cells), draw_means(a, k, cells)); vs.append(dl[2])
            sl = rule_seed(seed_vals(b, k, cells), seed_vals(a, k, cells))
            line.append(f"{k} {dl[0]:+.4f} ({dl[1]:.4f}) {dl[2]} [seed {sl[1]:.4f} {sl[2]}]")
        rp = draw_means(b, "relp", cells).mean() - draw_means(a, "relp", cells).mean()
        print(f"  {lab} {b} − {a}: {verdict(vs)} | " + "; ".join(line) + f" | relP@2 Δ {rp:+.4f}{' FLAG' if rp < -0.05 else ''}")

# ---- bootstrap (all 50, paired)
print(f"\n## Paired cell bootstrap, all 50, {B} resamples: Δ [95% CI] (P(Δ>0)) over arm means of 9 runs")
rng = np.random.default_rng(0); boots = rng.integers(0, len(CELLS), size=(B, len(CELLS)))
arr = {}
for a in ARMS:
    for d in DRAWS:
        for s in SEEDS:
            pc = S[f"{RUN(a, d, s)}/tau0"]["per_cell"]
            arr[RUN(a, d, s)] = np.array([pc[c]["crack_std"] for c in CELLS], np.float64)


def bm(x, k):
    tp, fp, fn, rtp, pp, rtg, g = x.T
    if k == "iou": return tp / np.maximum(tp + fp + fn, 1)
    if k == "recall": return tp / np.maximum(tp + fn, 1)
    P, Rr = rtp / np.maximum(pp, 1), rtg / np.maximum(g, 1)
    return 2 * P * Rr / np.maximum(P + Rr, 1e-9)


sums = {r: x[boots].sum(1) for r, x in arr.items()}  # (B, 7)
for b, a, lab in CON:
    out = []
    for k in PRIM:
        db = np.mean([bm(sums[RUN(b, d, s)], k) for d in DRAWS for s in SEEDS], 0) - np.mean([bm(sums[RUN(a, d, s)], k) for d in DRAWS for s in SEEDS], 0)
        lo, hi = np.percentile(db, [2.5, 97.5])
        d0 = np.mean([agg(RUN(b, d, s), 0, CELLS)[k] for d in DRAWS for s in SEEDS]) - np.mean([agg(RUN(a, d, s), 0, CELLS)[k] for d in DRAWS for s in SEEDS])
        out.append(f"{k} {d0:+.4f} [{lo:+.4f}, {hi:+.4f}] ({(db > 0).mean():.2f})")
    print(f"  {b} − {a}: " + "; ".join(out))

# ---- per source
print("\n## Per source (all 50): crack recall / IoU, arm means of draw-means; contrasts with draw-level arithmetic (descriptive)")
for src in SRC:
    cs = [c for c in CELLS if c.startswith(src)]
    row = [f"{a} {draw_means(a, 'recall', cs).mean():.3f} / {draw_means(a, 'iou', cs).mean():.3f}" for a in ARMS]
    ys = [f"{y} {np.mean([agg(r, 0, cs)['recall'] for r in runs]):.3f} / {np.mean([agg(r, 0, cs)['iou'] for r in runs]):.3f}" for y, runs in YARD.items()]
    print(f"  {src} ({len(cs)} cells): " + "; ".join(row + ys))
    for b, a, lab in CON:
        r_ = rule_draw(draw_means(b, "recall", cs), draw_means(a, "recall", cs)); i_ = rule_draw(draw_means(b, "iou", cs), draw_means(a, "iou", cs))
        print(f"    {b} − {a}: recall {r_[0]:+.4f} ({r_[1]:.4f}) {r_[2]}; IoU {i_[0]:+.4f} ({i_[1]:.4f}) {i_[2]}")

# ---- kill check
cs_b = [c for c in CELLS if c.startswith("BMRK")]; cs_a = [c for c in CELLS if c.startswith("ARTS")]
mv = {f"{b}-{a} {n}": draw_means(b, "recall", cs).mean() - draw_means(a, "recall", cs).mean() for b, a, _ in CON[:2] for n, cs in (("BMRK", cs_b), ("ARTS", cs_a))}
print("\n## Kill inputs: BMRK / ARTS recall moves:", {k: round(v, 4) for k, v in mv.items()})

# ---- regression on added crack px
x = np.array([AUD["draws"][f"{a}_d{d}"]["added_summary"]["crack_px"] for a in ARMS for d in DRAWS], float)
y = np.array([draw_means(a, "iou", CELLS)[d] for a in ARMS for d in DRAWS])
sl, ic = np.polyfit(x, y, 1); r = np.corrcoef(x, y)[0, 1]
print(f"\n## Descriptive regression, 9 draw-means: crack IoU = {ic:.4f} + {sl * 1e4:.4f} per 10k added crack px (r = {r:.2f})")
xi = np.array([AUD["draws"][f"{a}_d{d}"]["added_summary"]["inactive_px"] for a in ARMS for d in DRAWS], float)
yi = np.array([draw_means(a, "inact_iou", CELLS)[d] for a in ARMS for d in DRAWS])
print(f"   inactive IoU vs added inactive px: r = {np.corrcoef(xi, yi)[0, 1]:.2f}; per draw: " + ", ".join(f"{a}_d{d} {yi[i]:.3f}" for i, (a, d) in enumerate([(a, d) for a in ARMS for d in DRAWS])))

# ---- E1
e1 = D / "e1"
if e1.is_dir():
    print("\n## E1 extension (106 cells): crack false alarm / tolF1, arm means over 9 runs")
    for a in ARMS:
        vals = []
        for d in DRAWS:
            for s in SEEDS:
                j = json.loads((e1 / f"{RUN(a, d, s)}.json").read_text())["cells"]["ext"]
                st = sorted(j); mm = e1_metrics(e1_arrays(j, st), np.arange(len(st)))
                vals.append((mm["crack_false_alarm"], mm["crack_tolF1"]))
        v = np.array(vals)
        print(f"  {a}: false alarm {v[:, 0].mean():.3f}, tolF1 {v[:, 1].mean():.3f}")

# ---- all-class mIoU (24 classes; mean over classes present in test GT), draw-level arithmetic, descriptive
dmi = {a: np.array([np.mean([miou(RUN(a, d, s), 0, CELLS)[0] for s in SEEDS]) for d in DRAWS]) for a in ARMS}
print(f"\n## All-class mIoU (classes present in test GT: {miou(RUN('R', 0, 0), 0, CELLS)[1]}), draw-means:", {a: v.round(4).tolist() for a, v in dmi.items()})
for b, a, lab in CON:
    r_ = rule_draw(dmi[b], dmi[a])
    print(f"  {b} − {a}: {r_[0]:+.4f} ({r_[1]:.4f}) {r_[2]}")
