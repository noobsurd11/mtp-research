"""judge hc_extra (2 Nov 2026): answers to coach's HC verify questions (descriptive; own code on opening files).
1. F51 / H36 false alarms at each run's val b_rel (own OP from the val records: max relR@2 s.t. relP@2 >= 0.90 on -4..+12 step 0.1,
   ties smaller b) and at b 0: per seed, per-cell concentration (cells with >= 20 FA px, top-cell share), seed medians.
2. F51 width at b_rel and b 0 on the 12 crack cells: pred/GT px, pixel P / R, relP@2 / relR@2.
3. Test inactive IoU: seed-aware two-stage bootstrap (48 test modules with replacement + 5 seeds with replacement per arm; 2,000, seed 0).
4. E1 half-cut-without-scuff: any-hit / >= 50% component counts per seed (GT comps >= 20 px), pred/GT per seed.
Usage: python hc_extra.py REC_DIR HC_M0 PF2_M0 RF_SETS E1_CTX"""
import json, math, sys
import numpy as np

REC, HM, PM, SETS, CTX = sys.argv[1:6]
HC = [f"hc_HC_100pct_s{k}" for k in range(5, 10)]; SP = [f"pf2_SUPPF_100pct_s{k}" for k in range(5, 10)]
rows = [l.rstrip("\n").split("\t") for l in open(SETS) if l.strip()][1:]
SET = {r[0]: r[1] for r in rows}
J = lambda r, s: json.load(open(f"{REC}/{r}.{s}.json"))


def op(cells, grid):
    S = lambda k: np.sum([np.asarray(c[k], np.int64) for c in cells.values()], 0)
    pred, rp, rr = S("pred"), S("relp_tp"), S("relr_tp"); ng = sum(c["n_gt"] for c in cells.values())
    P = np.where(pred > 0, rp / np.maximum(pred, 1), np.nan); R = rr / ng
    opg = np.where((grid >= -4 - 1e-9) & (grid <= 12 + 1e-9) & (np.abs(np.round(grid * 10) - grid * 10) < 1e-6))[0]
    ok = opg[np.nan_to_num(P[opg], nan=-1) >= 0.90]
    return int(ok[np.argmax(R[ok])]) if len(ok) else int(opg[np.argmax(np.nan_to_num(P[opg], nan=-1))])


print("## 1-2. _rf false alarms and F51 width (own b_rel from val records)")
agg = {}
for arm, runs in (("SUPPF", SP), ("HC", HC)):
    for r in runs:
        v = J(r, "val"); grid = np.asarray(v["grid"], float); j = op(v["cells"], grid); j0 = int(np.argmin(np.abs(grid)))
        rf = J(r, "rf")["cells"]
        line = f"{arm:5s} {r:20s} b_rel {grid[j]:+.1f}"
        for st in ("H36", "F51"):
            free = [s for s in rf if SET[s] == st and rf[s]["n_gt"] == 0]
            fa = sorted([rf[s]["pred"][j] for s in free], reverse=True); fa0 = sum(rf[s]["pred"][j0] for s in free)
            line += f" | {st} FA b_rel {sum(fa):5d} (cells>=20px {sum(x >= 20 for x in fa)}, top cell {fa[0] / max(sum(fa), 1):.2f}) b0 {fa0:4d}"
            agg.setdefault((arm, st), []).append(sum(fa))
        cr = [s for s in rf if SET[s] == "F51" and rf[s]["n_gt"] >= 20]
        for jj, lab in ((j, "b_rel"), (j0, "b0")):
            pred = sum(rf[s]["pred"][jj] for s in cr); tp = sum(rf[s]["tp"][jj] for s in cr); ng = sum(rf[s]["n_gt"] for s in cr)
            rp = sum(rf[s]["relp_tp"][jj] for s in cr); rr = sum(rf[s]["relr_tp"][jj] for s in cr)
            line += f" | F51 crack cells {lab}: pred/GT {pred / ng:.3f} pxP {tp / max(pred, 1):.3f} pxR {tp / ng:.3f} relP {rp / max(pred, 1):.3f} relR {rr / ng:.3f}"
            agg.setdefault((arm, "w_" + lab), []).append((pred / ng, tp / max(pred, 1), tp / ng, rp / max(pred, 1), rr / ng))
        print(line)
for st in ("H36", "F51"):
    a, b = np.array(agg[("SUPPF", st)]), np.array(agg[("HC", st)])
    print(f"{st} FA at b_rel: mean SUPPF {a.mean():.1f} HC {b.mean():.1f} (x{a.mean() / max(b.mean(), 1e-9):.1f}); median {np.median(a):.0f} vs {np.median(b):.0f} "
          f"(x{np.median(a) / max(np.median(b), 1e-9):.1f}); max HC {b.max():.0f} vs min SUPPF {a.min():.0f}")
for lab in ("b_rel", "b0"):
    a, b = np.mean(agg[("SUPPF", "w_" + lab)], 0), np.mean(agg[("HC", "w_" + lab)], 0)
    print(f"F51 crack cells at {lab} (seed means) pred/GT / pxP / pxR / relP / relR: SUPPF {np.round(a, 3).tolist()} HC {np.round(b, 3).tolist()}")

print("\n## 3. test inactive IoU, seed-aware two-stage bootstrap (modules + seeds)")
IN, CR = 11, 14
def m0(d, p, a, k):
    return json.load(open(f"{d}/{p}_{a}_100pct_s{k}.json"))["cells"]
A = {"SUPPF": [m0(PM, "pf2", "SUPPF", k) for k in range(5, 10)], "HC": [m0(HM, "hc", "HC", k) for k in range(5, 10)]}
st = sorted(A["SUPPF"][0]["test"])
def cm(c):
    m = np.asarray(c["conf"], np.int64); n = math.isqrt(m.size); return m.reshape(n, n)[:24, :24]
def tfn(c, k):
    m = cm(c); return np.array([m[k, k], m[:, k].sum() - m[k, k], m[k].sum() - m[k, k]], float)
mods = sorted({"_".join(s.split("_")[:2]) for s in st}); mi = np.array([mods.index("_".join(s.split("_")[:2])) for s in st])
for k, lab in ((IN, "inactive"), (CR, "crack")):
    X = {a: np.stack([np.stack([tfn(r["test"][s], k) for s in st]) for r in v]) for a, v in A.items()}  # seeds x cells x 3
    M = {a: np.stack([X[a][:, mi == j].sum(1) for j in range(len(mods))], 1) for a in X}  # seeds x mods x 3
    iou = lambda t: t[..., 0] / np.maximum(t.sum(-1), 1)
    d0 = iou(M["HC"].sum(1)).mean() - iou(M["SUPPF"].sum(1)).mean()
    rng = np.random.default_rng(0); bs = []
    for _ in range(2000):
        w = np.bincount(rng.integers(0, len(mods), len(mods)), minlength=len(mods)).astype(float)
        sa, sb = rng.integers(0, 5, 5), rng.integers(0, 5, 5)
        bs.append(iou(np.einsum("m,smk->sk", w, M["HC"][sa])).mean() - iou(np.einsum("m,smk->sk", w, M["SUPPF"][sb])).mean())
    bs = np.array(bs)
    print(f"test {lab} IoU: d (seed-mean) {d0:+.4f}; two-stage 95% [{np.percentile(bs, 2.5):+.4f}, {np.percentile(bs, 97.5):+.4f}] P(d*<0) {np.mean(bs < 0):.3f}")
    if k == CR:
        P = {a: [X[a][i, :, 0].sum() / max(X[a][i, :, 0].sum() + X[a][i, :, 1].sum(), 1) for i in range(5)] for a in X}
        R = {a: [X[a][i, :, 0].sum() / max(X[a][i, :, 0].sum() + X[a][i, :, 2].sum(), 1) for i in range(5)] for a in X}
        V = {a: [(X[a][i, :, 0].sum() + X[a][i, :, 1].sum()) / max(X[a][i, :, 0].sum() + X[a][i, :, 2].sum(), 1) for i in range(5)] for a in X}
        print(f"  test crack pxP SUPPF {np.mean(P['SUPPF']):.4f} HC {np.mean(P['HC']):.4f} | pxR {np.mean(R['SUPPF']):.4f} {np.mean(R['HC']):.4f} | pred/GT {np.mean(V['SUPPF']):.3f} {np.mean(V['HC']):.3f}")

print("\n## 4. E1 half-cut without scuff: GT comps >= 20 px, per seed")
ctx = {l.split("\t")[0]: l.rstrip("\n").split("\t") for l in open(CTX) if l.strip()}
hs = [s for s in ctx if ctx[s][3] == "halfcut=1" and ctx[s][1] != "scuff_halfcut"]
for a in ("SUPPF", "HC"):
    out = []
    for r in A[a]:
        gc = [g for s in hs for g in r["ext"][s]["crack_cc"]["gt"] if g[0] >= 20]
        M = sum(cm(r["ext"][s]) for s in hs)
        out.append(f"anyhit {sum(g[1] >= 1 for g in gc)}/{len(gc)} half {sum(g[1] >= math.ceil(0.5 * g[0]) for g in gc)} pred/GT {M[:, CR].sum() / max(M[CR].sum(), 1):.2f}")
    print(f"{a}: " + " | ".join(out))
