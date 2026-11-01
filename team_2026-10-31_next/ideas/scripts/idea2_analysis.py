"""calib idea 2: is E1 separated from train in intensity space, and does intensity explain the E1 failure? (E1 descriptive)
Inputs: intensity.tsv (calib_intensity.py), per-cell records of FINAL (el_metrics) for the failure link.
Outputs: text summary + 2 small figures.
  1. per set medians [IQR] of the stats;
  2. AUROC (Mann-Whitney) per stat for set X vs train, X in val, test, E1, rf, pool (test = in-domain reference);
  3. multivariate separability: L2 logistic regression on standardised stats, leave-one-module-out CV AUROC (E1 vs train; test vs train);
  4. house augmentation coverage: share of X cells whose (mean, sd) is reachable from some train cell by
     RandomBrightnessContrast(0.2, 0.2) (alpha in [0.8,1.2] on contrast, beta*255 in [-51,51] on brightness);
  5. module share of variance (ICC of cell mean) on the pool (many cells per module);
  6. link to failure: Spearman of per-cell crack relR@2 (FINAL, b +0.75) with the stats, E1 crack cells and val crack cells.
"""
import argparse
import json
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--tsv", required=True)
ap.add_argument("--rec", required=True, help="dir with FINAL.val.json / FINAL.ext.json records")
ap.add_argument("--out", required=True)
ap.add_argument("--figs")
ap.add_argument("--f51", required=True)
a = ap.parse_args()
rows = [l.rstrip("\n").split("\t") for l in open(a.tsv)]
hdr, rows = rows[0], rows[1:]
T = {k: [r[i] for r in rows] for i, k in enumerate(hdr)}
num = lambda k: np.array([float(x) if x not in ("", "None") else np.nan for x in T[k]])
F51L = [l.strip() for l in open(a.f51) if l.strip()]
SET = np.array(T["set"]); STEM = np.array(T["stem"]); MOD = np.array(T["module"]); CTX = np.array(T["ctx"])
STATS = ["c_mean", "c_sd", "c_p1", "c_p5", "c_p50", "c_p95", "c_p99", "c_contrast", "c_noise", "rows_dark", "cols_dark", "content_frac", "letterbox", "mean"]
X = {k: num(k) for k in STATS}
SETS = ["train", "val", "test", "ext", "rf", "pool"]
L = ["idea 2 (calib): intensity statistics per cell (grey 0-255, all px; PIL convert L as the house loader). E1 = ext, DESCRIPTIVE.", ""]


def auroc(pos, neg):
    pos, neg = pos[~np.isnan(pos)], neg[~np.isnan(neg)]
    if not len(pos) or not len(neg):
        return np.nan
    a_ = np.concatenate([pos, neg]); _, inv, cnt = np.unique(a_, return_inverse=True, return_counts=True)
    rk = np.empty(len(a_)); rk[np.argsort(a_, kind="mergesort")] = np.arange(1, len(a_) + 1)
    rk = (np.bincount(inv, weights=rk) / cnt)[inv]
    return (rk[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


L.append("1. medians [p25, p75] per set")
for k in STATS:
    L.append(f"  {k:10s} " + " | ".join(f"{s} {np.nanmedian(X[k][SET == s]):.1f} [{np.nanpercentile(X[k][SET == s], 25):.1f}, {np.nanpercentile(X[k][SET == s], 75):.1f}]"
                                         for s in SETS if (SET == s).any()))
for s in ("ext", "rf", "pool"):
    for c in sorted(set(CTX[SET == s])):
        m = (SET == s) & (CTX == c)
        L.append(f"  {s}:{c or '-'} n={m.sum()}: c_mean {np.nanmedian(X['c_mean'][m]):.1f}, c_sd {np.nanmedian(X['c_sd'][m]):.1f}, c_contrast {np.nanmedian(X['c_contrast'][m]):.2f}, "
                 f"c_noise {np.nanmedian(X['c_noise'][m]):.2f}, rows_dark {np.nanmedian(X['rows_dark'][m]):.0f}, cols_dark {np.nanmedian(X['cols_dark'][m]):.0f}, "
                 f"letterbox {np.nanmean(X['letterbox'][m]):.2f}, content_frac {np.nanmedian(X['content_frac'][m]):.2f}")
L += ["", "2. AUROC per stat, set vs train (0.5 = same; |AUROC-0.5| > 0.25 = strongly separated). test = in-domain reference"]
for s in ("val", "test", "ext", "rf", "pool"):
    L.append(f"  {s:5s} " + "; ".join(f"{k} {auroc(X[k][SET == s], X[k][SET == 'train']):.2f}" for k in STATS))
for c in ("halfcut+scuff", "halfcut", "full", "full+scuff"):
    m = (SET == "ext") & (CTX == c)
    if m.any():
        L.append(f"  E1 {c} (n={m.sum()}) " + "; ".join(f"{k} {auroc(X[k][m], X[k][SET == 'train']):.2f}" for k in STATS))


def logit_cv(pos_mask, neg_mask, feats, lam=1.0):
    Z = np.stack([X[k] for k in feats], 1); y = np.r_[np.ones(pos_mask.sum()), np.zeros(neg_mask.sum())]
    Z = np.concatenate([Z[pos_mask], Z[neg_mask]]); grp = np.concatenate([MOD[pos_mask], MOD[neg_mask]])
    ok = ~np.isnan(Z).any(1); Z, y, grp = Z[ok], y[ok], grp[ok]
    sc = np.zeros(len(y))
    for g in np.unique(grp):
        te = grp == g; tr = ~te
        mu, sd = Z[tr].mean(0), Z[tr].std(0) + 1e-9
        A = np.c_[np.ones(tr.sum()), (Z[tr] - mu) / sd]; w = np.zeros(A.shape[1])
        for _ in range(50):  # Newton, L2 (not on intercept)
            p = 1 / (1 + np.exp(-A @ w)); Rg = np.diag(np.r_[0, np.full(A.shape[1] - 1, lam)])
            H = A.T @ (A * (p * (1 - p))[:, None]) + Rg; gr = A.T @ (p - y[tr]) + Rg @ w
            w -= np.linalg.solve(H, gr)
        sc[te] = np.c_[np.ones(te.sum()), (Z[te] - mu) / sd] @ w
    return auroc(sc[y == 1], sc[y == 0])


feats = ["c_mean", "c_sd", "c_p5", "c_p50", "c_p95", "c_contrast", "c_noise", "rows_dark", "cols_dark"]
L += ["", "3. multivariate separability (L2 logistic, leave-one-module-out CV AUROC, features " + ",".join(feats) + ")"]
for s in ("test", "val", "ext", "rf"):
    L.append(f"  {s} vs train: {logit_cv(SET == s, SET == 'train', feats):.3f}")
L.append(f"  ext vs train, brightness only (mean, p50): {logit_cv(SET == 'ext', SET == 'train', ['c_mean', 'c_p50']):.3f}; "
         f"contrast/noise only (c_sd, c_contrast, c_noise): {logit_cv(SET == 'ext', SET == 'train', ['c_sd', 'c_contrast', 'c_noise']):.3f}; "
         f"frame/structure only (content_frac, rows_dark, cols_dark): {logit_cv(SET == 'ext', SET == 'train', ['content_frac', 'rows_dark', 'cols_dark']):.3f}")
mfull = (SET == "ext") & np.isin(CTX, ["full", "full+scuff"])
L.append(f"  E1 full cells only vs train: {logit_cv(mfull, SET == 'train', feats):.3f}; brightness only {logit_cv(mfull, SET == 'train', ['c_mean', 'c_p50']):.3f}")
mrf = (SET == "rf") & np.isin(STEM, F51L)
L.append(f"  rf F51 vs train: {logit_cv(mrf, SET == 'train', feats):.3f}; brightness only {logit_cv(mrf, SET == 'train', ['c_mean', 'c_p50']):.3f}")

# 4. augmentation coverage
tm, ts = X["c_mean"][SET == "train"], X["c_sd"][SET == "train"]
L += ["", "4. house augmentation coverage: RandomBrightnessContrast(0.2, 0.2, p 0.4): out = alpha*x + beta*255, alpha in [0.8,1.2], beta in [-0.2,0.2]"]
for s in ("val", "test", "ext", "rf", "pool"):
    em, es = X["c_mean"][SET == s], X["c_sd"][SET == s]
    cov = []
    for m_, s_ in zip(em, es):
        al = s_ / np.maximum(ts, 1e-6); be = (m_ - al * tm) / 255
        cov.append(bool(np.any((al >= 0.8) & (al <= 1.2) & (be >= -0.2) & (be <= 0.2))))
    inr = np.mean((em >= np.percentile(tm, 1)) & (em <= np.percentile(tm, 99)) & (es >= np.percentile(ts, 1)) & (es <= np.percentile(ts, 99)))
    L.append(f"  {s}: reachable from a train cell under the jitter {np.mean(cov):.3f}; inside train [p1, p99] of mean and sd {inr:.3f}")

# 5. module share of cell-mean variance on the pool
L += ["", "5. module share of variance of the cell mean (one-way ANOVA ICC-like: between-module var / total), pool modules with >= 5 cells"]
for s in ("pool", "train", "ext", "rf"):
    m = SET == s
    mods = [g for g in np.unique(MOD[m]) if ((MOD == g) & m).sum() >= (5 if s == "pool" else 2)]
    if len(mods) < 3:
        continue
    vals = [X["c_mean"][(MOD == g) & m] for g in mods]
    allv = np.concatenate(vals); gm = np.array([v.mean() for v in vals]); n = np.array([len(v) for v in vals])
    between = np.sum(n * (gm - allv.mean()) ** 2) / len(allv); total = allv.var()
    L.append(f"  {s}: {len(mods)} modules, {len(allv)} cells: between-module share {between / total:.3f}; within-module sd {np.sqrt(np.mean([v.var() for v in vals])):.1f}, between-module sd {gm.std():.1f}")

# 6. link to failure
L += ["", "6. failure link: Spearman rho of per-cell crack relR@2 (FINAL, b +0.75) with intensity stats, crack cells (>= 20 GT px)"]


def spearman(x, y):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


for sp, sname in (("val", "val"), ("ext", "ext")):
    rec = json.load(open(Path(a.rec) / f"FINAL.{sp}.json"))["cells"]
    j = int(np.argmin(np.abs(np.array(json.load(open(Path(a.rec) / f"FINAL.{sp}.json"))["grid"]) - 0.75)))
    st = [s for s, c in rec.items() if c["n_gt"] >= 20]
    idx = {s: i for i, s in enumerate(STEM) if SET[i] == sname}
    y = np.array([rec[s]["relr_tp"][j] / rec[s]["n_gt"] for s in st])
    L.append(f"  {sp} (n={len(st)} crack cells, median relR {np.median(y):.2f}): " + "; ".join(f"{k} {spearman(X[k][[idx[s] for s in st]], y):+.2f}" for k in STATS))
    if sp == "ext":
        ctx = CTX[[idx[s] for s in st]]
        for c in sorted(set(ctx)):
            mm = ctx == c
            if mm.sum() >= 5:
                L.append(f"    E1 {c} (n={mm.sum()}): median relR {np.median(y[mm]):.2f}; content mean grey {np.nanmedian(X['c_mean'][[idx[s] for s in np.array(st)[mm]]]):.1f}")
Path(a.out).write_text("\n".join(L) + "\n"); print("\n".join(L))

if a.figs:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for s, c in (("pool", "#cccccc"), ("train", "#1f77b4"), ("test", "#17becf"), ("rf", "#9467bd"), ("ext", "#d62728")):
        m = SET == s
        ax[0].scatter(X["c_mean"][m], X["c_sd"][m], s=3 if s == "pool" else 9, c=c, label=f"{'E1' if s == 'ext' else s} ({m.sum()})", alpha=0.35 if s == "pool" else 0.8, lw=0)
        ax[1].scatter(X["c_p50"][m], X["c_contrast"][m], s=3 if s == "pool" else 9, c=c, alpha=0.35 if s == "pool" else 0.8, lw=0)
    ax[0].set_xlabel("cell content mean grey"); ax[0].set_ylabel("cell content sd"); ax[0].legend(fontsize=7, markerscale=2)
    ax[1].set_xlabel("cell content median grey"); ax[1].set_ylabel("content robust contrast (p95-p5)/p50")
    fig.suptitle("idea 2: per-cell intensity, train / test / Hanifi rf / E1 (descriptive) / pool", fontsize=9)
    fig.tight_layout(); Path(a.figs).mkdir(parents=True, exist_ok=True); fig.savefig(Path(a.figs) / "idea2_intensity.png", dpi=90)
