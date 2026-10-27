"""evalx Q3b: does the goal metric (crack component recall/precision, inactive region recall) show an Sx100 - A100
difference that IoU missed? Track M m0 JSONs (5 v 5), clean test cells and E1 ext; paired cell bootstrap."""
import json, glob
import numpy as np
TM = '/home/yugma/mtp/research/team_2026-10-24_go/trackM/'
NOISY = 'CSIR_00070_r8_c4'
rng = np.random.default_rng(0)
def ld(f, split): return json.load(open(f))['cells'][split]
for split in ['test', 'ext']:
    A = [ld(f, split) for f in sorted(glob.glob(TM + 'm0/p6_L3_100pct_s*.json')) + sorted(glob.glob(TM + 'm0/p16_A_100pct_s*.json'))]
    S = [ld(f, split) for f in sorted(glob.glob(TM + 'm0/p16_Sx_100pct_s*.json'))]
    cells = [c for c in sorted(A[0]) if c != NOISY]
    def per_cell(R):
        # per run, per cell: [crack comps found, crack comps, pred comps hitting, pred comps, inact regions found, inact regions]
        out = []
        for r in R:
            row = []
            for c in cells:
                g = [x for x in r[c]['crack_cc']['gt'] if x[0] >= 20]; p = [x for x in r[c]['crack_cc']['pr'] if x[0] >= 20]
                gi = [x for x in r[c]['inact_cc']['gt'] if x[0] >= 100]
                row.append([sum(x[1] >= 0.5 * x[0] for x in g), len(g), sum(x[1] > 0 for x in p), len(p),
                            sum(x[1] >= 0.5 * x[0] for x in gi), len(gi)])
            out.append(row)
        return np.array(out, float)  # run, cell, 6
    XA, XS = per_cell(A), per_cell(S)
    def met(X, idx=None):
        s = X[:, idx].sum(1) if idx is not None else X.sum(1)
        return np.stack([s[:, 0] / np.maximum(s[:, 1], 1), s[:, 2] / np.maximum(s[:, 3], 1), s[:, 4] / np.maximum(s[:, 5], 1)], 1)
    ma, ms = met(XA), met(XS)
    B = rng.integers(0, len(cells), size=(2000, len(cells)))
    bd = np.array([met(XS, b).mean(0) - met(XA, b).mean(0) for b in B])
    names = ['crack comp recall', 'crack comp precision', 'inactive region recall']
    print(f'== {split} ({len(cells)} cells; GT crack comps {int(XA[0, :, 1].sum())}, inactive regions {int(XA[0, :, 5].sum())})')
    for k, n in enumerate(names):
        sa, ss = ma[:, k].std(ddof=1), ms[:, k].std(ddof=1)
        d = ms[:, k].mean() - ma[:, k].mean(); thr = max(0.01, 2 * np.sqrt((sa**2 + ss**2) / 3))
        lo, hi = np.nanpercentile(bd[:, k], [2.5, 97.5])
        print(f'{n}: A100 {ma[:, k].mean():.3f}+-{sa:.3f} Sx100 {ms[:, k].mean():.3f}+-{ss:.3f} d {d:+.4f} thr {thr:.4f} cellCI [{lo:+.4f},{hi:+.4f}]')
