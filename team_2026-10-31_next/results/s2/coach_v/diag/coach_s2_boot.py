# coach (2 Nov 21:4x): seed-aware two-stage bootstrap (reported, protocol_SKR2_HC2 §4; judge's convention). Own code, numpy only.
# Stage 1: draw clusters (test: 48 modules; E1: source images) with replacement, same draw for both arms (paired over cells).
# Stage 2: draw 5 runs with replacement per arm, independently. Metric pooled per drawn run on the drawn cells; arm = mean of drawn runs.
import json, re, sys, numpy as np
NC, CR, IN, NOISY = 24, 14, 11, 'CSIR_00070_r8_c4'
PF = '/home/noob/work/el_f3/reports/pf2/post/m0'; S2 = '/home/noob/work/s2q/post/m0'; HCM = '/home/noob/work/el_hc/reports/hc/post/m0'
ARMS = {'SUPPF': [f'{PF}/pf2_SUPPF_100pct_s{k}.json' for k in range(5, 10)],
        'SKR01': [f'{S2}/SKR01/skr2_SKR01_100pct_s{k}.json' for k in range(5, 10)],
        'HC2': [f'{S2}/HC2/hc2_HCig_100pct_s{k}.json' for k in range(5, 10)],
        'HC': [f'{HCM}/hc_HC_100pct_s{k}.json' for k in range(5, 10)]}
clu = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)
def feats(c):
    C = np.asarray(c['conf'], float).reshape(NC, NC); x = np.asarray(c['crack_rel2'], float)
    n = sum(1 for sz, h in c['crack_cc']['gt'] if sz >= 20); h = sum(1 for sz, hh in c['crack_cc']['gt'] if sz >= 20 and hh >= 1)
    return [C[CR, CR], C[CR].sum(), C[:, CR].sum(), C[IN, IN], C[IN].sum(), C[:, IN].sum(), x[0], x[1], x[2], x[3], n, h]
def metr(F):  # F (..., 12) summed
    ci = F[..., 0] / np.maximum(F[..., 1] + F[..., 2] - F[..., 0], 1); ii = F[..., 3] / np.maximum(F[..., 4] + F[..., 5] - F[..., 3], 1)
    rp = F[..., 6] / np.maximum(F[..., 7], 1); rr = F[..., 8] / np.maximum(F[..., 9], 1); rf = 2 * rp * rr / np.maximum(rp + rr, 1e-12)
    ah = F[..., 11] / np.maximum(F[..., 10], 1)
    return {'crack': ci, 'relF1': rf, 'inact': ii, 'anyhit': ah, 'relP': rp, 'relR': rr}
def load(split, keep):
    X = {}; stems = None
    for a, ps in ARMS.items():
        runs = []
        for p in ps:
            d = json.load(open(p)); assert d['step'] == 20000; cs = d['cells'][split]
            st = sorted(s for s in cs if keep(s)); stems = stems or st; assert st == stems, p
            runs.append(np.array([feats(cs[s]) for s in st]))
        X[a] = np.stack(runs)  # (5, ncell, 12)
    cl = np.array([clu(s) for s in stems]); u, inv = np.unique(cl, return_inverse=True)
    return X, inv, len(u), len(stems)
def boot(X, inv, ncl, a, b, keys, B=2000, seed=20261102):
    rng = np.random.default_rng(seed); M = np.zeros((ncl, len(inv))); M[inv, np.arange(len(inv))] = 1
    pt = {k: metr(X[b].sum(1))[k].mean() - metr(X[a].sum(1))[k].mean() for k in keys}
    D = {k: [] for k in keys}
    for _ in range(B):
        w = np.bincount(rng.integers(0, ncl, ncl), minlength=ncl) @ M  # cell weights
        sa = rng.integers(0, 5, 5); sb = rng.integers(0, 5, 5)
        Fa = np.einsum('c,rcf->rf', w, X[a][sa]); Fb = np.einsum('c,rcf->rf', w, X[b][sb])
        ma, mb = metr(Fa), metr(Fb)
        for k in keys:
            D[k].append(mb[k].mean() - ma[k].mean())
    out = {}
    for k in keys:
        v = np.array(D[k]); out[k] = (pt[k], np.percentile(v, 2.5), np.percentile(v, 97.5), (v > 0).mean())
    return out
for split, name, keep in (('test', 'test all 50', lambda s: True), ('test', 'test clean 49', lambda s: s != NOISY), ('ext', 'E1 106', lambda s: True)):
    X, inv, ncl, n = load(split, keep)
    keys = ['crack', 'relF1', 'inact'] if split == 'test' else ['relF1', 'anyhit', 'inact', 'relP', 'relR']
    print(f'## {name}: {n} cells, {ncl} clusters; seed-aware two-stage bootstrap, 2,000, RNG 20261102')
    for a, b in (('SUPPF', 'SKR01'), ('SUPPF', 'HC2'), ('HC', 'HC2')):
        r = boot(X, inv, ncl, a, b, keys)
        print(f'  {b} - {a}: ' + ' | '.join(f'{k} {v[0]:+.4f} [{v[1]:+.4f}, {v[2]:+.4f}] P>0 {v[3]:.2f}' for k, v in r.items()))
