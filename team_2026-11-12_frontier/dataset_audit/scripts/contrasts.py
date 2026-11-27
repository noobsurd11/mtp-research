"""Axes d, e, f (statistics): levels and the four contrasts (X minus PF) under the label variants, two-stage group bootstrap;
fragility (greedy group removal); Kish effective n; error decomposition by model agreement. Reads out/pass_records.pkl.
Writes out/contrasts.txt, out/contrasts.json. CPU only."""
from __future__ import annotations

import json
import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import common as C  # noqa: E402

M_MARGIN = 0.010
B = 2000
ARMS = ["PF", "HOUSE", "HRNET", "SWADBN", "C3X"]


def metrics(x):
    """x: (..., 10) pooled counts -> dict of arrays: iou, relF1, relP, relR, iiou."""
    x = np.asarray(x, np.float64)
    tp, fp, fn, ph, pn, rh, rn, itp, ifp, ifn = np.moveaxis(x, -1, 0)
    P = ph / np.maximum(pn, 1)
    R = rh / np.maximum(rn, 1)
    return {"iou": tp / np.maximum(tp + fp + fn, 1), "relF1": 2 * P * R / np.maximum(P + R, 1e-12), "relP": P, "relR": R,
            "iiou": itp / np.maximum(itp + ifp + ifn, 1)}


def load():
    d = pickle.load(open(C.OUT / "pass_records.pkl", "rb"))
    stems = sorted(d["cells"])
    R = np.stack([d["cells"][s]["rec"] for s in stems]).astype(np.float64)   # cells, 26, var, 10
    g = C.groups(C.G3)
    fold = np.array([int(g[s]["fold"]) for s in stems])
    grp_names = sorted({g[s]["group"] for s in stems})
    gi = {n: i for i, n in enumerate(grp_names)}
    grp = np.array([gi[g[s]["group"]] for s in stems])
    return d, stems, R, fold, grp, d["meta"]["variants"]


def midx(meta_models, arm, seed):
    return [tuple(m) for m in meta_models].index((arm, seed))


def boot_contrast(R, fold, grp, models, a, b, var, keepcells=None, rng_seed=0):
    """Two-stage group bootstrap of arm a minus arm b, as the protocol: groups with replacement, then one seed per fold per arm."""
    rng = np.random.default_rng(rng_seed)
    nC = R.shape[0]
    kc = np.ones(nC, bool) if keepcells is None else keepcells
    ng = grp.max() + 1
    gsel = np.unique(grp[kc])
    mult = np.zeros((B, ng))
    for bb in range(B):
        draw = rng.choice(gsel, size=len(gsel), replace=True)
        mult[bb] = np.bincount(draw, minlength=ng)
    w = mult[:, grp] * kc[None]                                         # B x cells
    sa = rng.integers(0, 5, size=(B, 5))
    sb = rng.integers(0, 5, size=(B, 5))
    out = {}
    for arm, sel in ((a, sa), (b, sb)):
        tot = np.zeros((B, 10))
        for f in range(5):
            cf = fold == f
            for si, s in enumerate(C.SEEDS):
                S = w[:, cf] @ R[cf, midx(models, arm, s), var, :]          # B x 10
                tot += S * (sel[:, f] == si)[:, None]
        out[arm] = metrics(tot)
    # point: mean over seeds of pooled metric, a minus b
    pa = [metrics(R[kc, midx(models, a, s), var, :].sum(0)) for s in C.SEEDS]
    pb = [metrics(R[kc, midx(models, b, s), var, :].sum(0)) for s in C.SEEDS]
    res = {}
    for k in ("iou", "relF1", "iiou", "relP", "relR"):
        pt = np.mean([x[k] for x in pa]) - np.mean([x[k] for x in pb])
        dd = out[a][k] - out[b][k]
        lo, hi = np.percentile(dd, [2.5, 97.5])
        res[k] = (float(pt), float(lo), float(hi))
    return res


def level(R, models, arm, var, kc=None):
    kc = np.ones(R.shape[0], bool) if kc is None else kc
    v = [metrics(R[kc, midx(models, arm, s), var, :].sum(0)) for s in C.SEEDS]
    return {k: float(np.mean([x[k] for x in v])) for k in ("iou", "relF1", "relP", "relR", "iiou")}


def passes(t):
    return t[0] >= M_MARGIN and t[1] > 0


def fragility(R, grp, models, a, b, var, key, kmax=60):
    """Greedy removal of whole groups, largest drop of the mean-over-seeds delta first. Returns (k_M, k_0, removed groups)."""
    ng = grp.max() + 1
    # per group pooled counts per seed per arm
    G = {}
    for arm in (a, b):
        G[arm] = np.stack([np.stack([R[grp == q, midx(models, arm, s), var, :].sum(0) for q in range(ng)]) for s in C.SEEDS])  # seeds, ng, 10
    alive = np.ones(ng, bool)

    def delta(mask):
        da = np.mean([metrics(G[a][si][mask].sum(0))[key] for si in range(5)])
        db = np.mean([metrics(G[b][si][mask].sum(0))[key] for si in range(5)])
        return da - db
    d0 = delta(alive)
    kM = k0 = None
    removed = []
    for k in range(1, kmax + 1):
        best, bq = None, None
        for q in np.nonzero(alive)[0]:
            m = alive.copy(); m[q] = False
            v = delta(m)
            if best is None or v < best:
                best, bq = v, q
        alive[bq] = False
        removed.append((int(bq), float(best)))
        if kM is None and best < M_MARGIN:
            kM = k
        if best <= 0:
            k0 = k
            break
    return d0, kM, k0, removed


def kish(w):
    w = np.asarray(w, np.float64)
    return float(w.sum() ** 2 / max((w ** 2).sum(), 1e-12))


def main():
    d, stems, R, fold, grp, VAR = load()
    models = d["meta"]["models"]
    lines = []
    J = {}
    P = lines.append
    P("# contrasts.txt (dataset_audit, axes d, e, f). 532 pool cells, cv5v3 out-of-fold, argmax, 25 models (5 recipes x seeds 5-9).")
    P("# two-stage group bootstrap: 285 cv5v3 groups, then one seed per fold per arm; B = 2000; rng 0. M = 0.010.")
    # levels
    P("\n## Levels (mean over 5 seeds of the pooled metric), per label variant")
    P("variant | arm | strict crack IoU | relF1@2 | relP@2 | relR@2 | inactive IoU")
    J["levels"] = {}
    for vi, v in enumerate(VAR):
        for arm in ARMS:
            L = level(R, models, arm, vi)
            J["levels"][f"{v}|{arm}"] = L
            P(f"{v} | {arm} | {L['iou']:.4f} | {L['relF1']:.4f} | {L['relP']:.4f} | {L['relR']:.4f} | {L['iiou']:.4f}")
        cons = metrics(R[:, -1, vi, :].sum(0))
        J["levels"][f"{v}|CONS25"] = {k: float(x) for k, x in cons.items()}
        P(f"{v} | CONS25 (>= 13 of 25 vote) | {cons['iou']:.4f} | {cons['relF1']:.4f} | {cons['relP']:.4f} | {cons['relR']:.4f} | {cons['iiou']:.4f}")
    # contrasts
    P("\n## Contrasts X minus PF per label variant: point [95% CI]; PASS = delta >= M and low end > 0")
    P("variant | contrast | strict crack IoU | relF1@2 | inactive IoU")
    J["contrasts"] = {}
    for vi, v in enumerate(VAR):
        for arm in ARMS[1:]:
            r = boot_contrast(R, fold, grp, models, arm, "PF", vi)
            J["contrasts"][f"{v}|{arm}-PF"] = r
            f = lambda t: f"{t[0]:+.4f} [{t[1]:+.4f}, {t[2]:+.4f}] {'PASS' if passes(t) else '-'}"
            P(f"{v} | {arm}-PF | {f(r['iou'])} | {f(r['relF1'])} | {f(r['iiou'])}")
    # sensitivity summary
    P("\n## Sensitivity of each contrast to the label variant (point shift against v11; flag if |shift| >= 0.005 or PASS changes)")
    for arm in ARMS[1:]:
        base = J["contrasts"][f"v11|{arm}-PF"]
        for v in VAR[1:]:
            r = J["contrasts"][f"{v}|{arm}-PF"]
            for k in ("iou", "relF1", "iiou"):
                sh = r[k][0] - base[k][0]
                fl = abs(sh) >= 0.005 or passes(r[k]) != passes(base[k])
                sign = np.sign(r[k][0]) != np.sign(base[k][0])
                P(f"{arm}-PF | {v} | {k} | shift {sh:+.4f} | pass {passes(base[k])}->{passes(r[k])} | sign change {bool(sign)} | {'FLAG' if fl else 'ok'}")
    # fragility
    P("\n## Fragility on v11 (greedy removal of whole cv5v3 groups; k_M = groups until delta < M, k_0 = until delta <= 0)")
    J["fragility"] = {}
    gnames = sorted({C.groups(C.G3)[s]["group"] for s in stems})
    vi0 = list(VAR).index("v11")
    for arm in ARMS[1:]:
        for key in ("relF1", "iou"):
            d0, kM, k0, rem = fragility(R, grp, models, arm, "PF", vi0, key)
            J["fragility"][f"{arm}-PF|{key}"] = {"d0": d0, "kM": kM, "k0": k0, "removed": [(gnames[q], v) for q, v in rem]}
            P(f"{arm}-PF {key}: delta {d0:+.4f}; k_M {kM}; k_0 {k0}; first groups: " +
              ", ".join(f"{gnames[q]} ({v:+.4f})" for q, v in rem[:6]))
    # Kish effective n
    P("\n## Effective sample size over cv5v3 groups (Kish n_eff = (sum w)^2 / sum w^2)")
    ng = grp.max() + 1
    gcr = np.bincount(grp, weights=R[:, 0, vi0, 6], minlength=ng)         # GT crack px per group (relR_n)
    gin = np.bincount(grp, weights=R[:, 0, vi0, 7] + R[:, 0, vi0, 9], minlength=ng)   # GT inactive px = tp + fn
    ccr = np.bincount(grp, weights=(R[:, 0, vi0, 6] > 0), minlength=ng)
    cin = np.bincount(grp, weights=((R[:, 0, vi0, 7] + R[:, 0, vi0, 9]) > 0), minlength=ng)
    J["neff"] = {"groups": int(ng), "crack_groups": int((gcr > 0).sum()), "crack_cells": int(ccr.sum()), "crack_neff": kish(gcr),
                 "inact_groups": int((gin > 0).sum()), "inact_cells": int(cin.sum()), "inact_neff": kish(gin),
                 "crack_top5_share": float(np.sort(gcr)[::-1][:5].sum() / gcr.sum()),
                 "inact_top3_share": float(np.sort(gin)[::-1][:3].sum() / gin.sum()),
                 "inact_top5_share": float(np.sort(gin)[::-1][:5].sum() / gin.sum())}
    for k, v in J["neff"].items():
        P(f"{k}: {v:.3f}" if isinstance(v, float) else f"{k}: {v}")
    # error decomposition
    P("\n## Error decomposition (v11): each model's missed GT crack px (relR@2) and false crack px (relP@2), by how many of the 25")
    P("## models make the same call within 2 px. 'systematic' = >= 20 of 25 agree on the error, 'variable' = 6..19, 'own' = <= 5.")
    E = np.stack([d["cells"][s]["errdec"] for s in stems]).sum(0).astype(np.float64)   # 25 x 12
    cols = d["meta"]["errdec_cols"]
    J["errdec"] = {}
    for arm in ARMS + ["ALL"]:
        rows = [i for i, m in enumerate(models) if (m[0] == arm or arm == "ALL")]
        e = E[rows].sum(0)
        fn, fp = e[0:3].sum(), e[3:6].sum()
        ifn, ifp = e[8:10].sum(), e[10:12].sum()
        r = {"fn_sys": e[0] / fn, "fn_var": e[1] / fn, "fn_own": e[2] / fn, "fp_sys": e[3] / fp, "fp_var": e[4] / fp, "fp_own": e[5] / fp,
             "fn_in_cand": e[6] / fn, "fp_in_cand": e[7] / fp, "ifn_sys": e[8] / max(ifn, 1), "ifp_sys": e[10] / max(ifp, 1),
             "fn_px_per_model": fn / len(rows), "fp_px_per_model": fp / len(rows)}
        J["errdec"][arm] = {k: float(v) for k, v in r.items()}
        P(f"{arm}: missed px/model {r['fn_px_per_model']:.0f}: systematic {r['fn_sys']:.3f}, variable {r['fn_var']:.3f}, own {r['fn_own']:.3f}, "
          f"in candidates {r['fn_in_cand']:.3f} | false px/model {r['fp_px_per_model']:.0f}: systematic {r['fp_sys']:.3f}, variable "
          f"{r['fp_var']:.3f}, own {r['fp_own']:.3f}, in candidates {r['fp_in_cand']:.3f} | inactive missed systematic {r['ifn_sys']:.3f}, "
          f"false systematic {r['ifp_sys']:.3f}")
    open(C.OUT / "contrasts.txt", "w").write("\n".join(lines) + "\n")
    json.dump(J, open(C.OUT / "contrasts.json", "w"), indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
