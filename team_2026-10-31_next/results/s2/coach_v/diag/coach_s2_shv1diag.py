# coach (2 Nov 21:3x): HC2 SHV1 diagnostic (descriptive, val-derived, non-E1, no verdict role).
# Why is SHV1 relP@2 >= 0.90 unreachable for HC2? Split SHV1 cells by GT inactive (gt_inact > 0) and pool 5 seeds per arm.
import json, sys, numpy as np
HCP = '/home/noob/work/el_hc/reports/hc/post/shv1/rec'; S2 = '/home/noob/work/s2q/post/shv1/rec'
ARMS = {'SUPPF': (HCP, 'pf2_SUPPF'), 'HC': (HCP, 'hc_HC'), 'HC2': (S2, 'hc2_HCig'), 'SKR01': (S2, 'skr2_SKR01')}
def load(d, p, st):
    out = []
    for k in range(5, 10):
        j = json.load(open(f'{d}/{p}_100pct_s{k}.{st}.json')); out.append((j['grid'], j['cells']))
    return out
def pool(runs, sel):
    G = np.array(runs[0][0]); cs = [c for g, cells in runs for s, c in cells.items() if sel(s, c)]
    S = lambda k: np.sum([np.asarray(c[k], np.int64) for c in cs], 0)
    pred, rp, rr = S('pred'), S('relp_tp'), S('relr_tp'); ng = sum(c['n_gt'] for c in cs)
    ip, it = S('inact_pred'), S('inact_tp'); gi = sum(c['gt_inact'] for c in cs)
    P = np.where(pred > 0, rp / np.maximum(pred, 1), np.nan); R = rr / max(ng, 1)
    ok = np.where(np.nan_to_num(P, nan=-1) >= 0.90)[0]; j0 = int(np.argmin(np.abs(G)))
    jm = int(np.nanargmax(P)) if np.isfinite(P).any() else 0
    iou0 = it[j0] / max(ip[j0] + gi - it[j0], 1)
    return dict(n=len(cs), ng=ng, gi=gi, matched=(R[ok].max() if len(ok) else np.nan), maxP=np.nanmax(P), b_maxP=G[jm], R_at_maxP=R[jm],
                P0=P[j0], R0=R[j0], pred0=pred[j0], fp0=pred[j0] - rp[j0], ipred0=ip[j0], iou0=iou0)
SEL = {'all': lambda s, c: True, 'inact-bearing (gt_inact>0)': lambda s, c: c['gt_inact'] > 0, 'no GT inactive': lambda s, c: c['gt_inact'] == 0}
for st in ('synval', 'val'):
    print(f'## {st} (pooled 5 seeds per arm; grid -4..+12; b0 = grid point nearest 0)')
    R = {a: load(d, p, st) for a, (d, p) in ARMS.items()}
    for name, f in SEL.items():
        print(f' -- {name}')
        for a in ARMS:
            r = pool(R[a], f)
            print(f'   {a:5s} cells {r["n"]:3d} ngt {r["ng"]:7d} gt_inact {r["gi"]:8d} | matched relR {r["matched"]:.4f} | max relP {r["maxP"]:.4f} at b {r["b_maxP"]:+.1f} (relR {r["R_at_maxP"]:.4f})'
                  f' | b0 relP {r["P0"]:.4f} relR {r["R0"]:.4f} pred {r["pred0"]:8d} off-GT(2px) {r["fp0"]:8d} | inact pred b0 {r["ipred0"]:8d} IoU {r["iou0"]:.4f}')
