"""Ideas 3/4: linear probe. Does a channel add crack / inactive information beyond a multi-scale local filter
bank on the raw image (which a CNN can learn anyway)? Features per channel (z-scored image X): X, and for sigma in
1, 2, 4, 8: G_sigma X, Hessian eigenvalues (sigma^2-normalised), gradient magnitude (17). Raw control 'raw+':
extra raw scales 16, 32 (25 features). L2 logistic regression (scipy L-BFGS, standardised features), trained on
TRAIN cells (sampled px: up to 400 positives + 600 random content px per cell), evaluated on all content px of VAL
(and Hanifi half-cuts) by pooled histogram AP and AUROC. No E1, no test.
Usage: python -I dom_probe.py INDEX.tsv OUT.json"""
import sys, csv, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi, optimize
sys.path.insert(0, __import__('os').path.dirname(__file__))
from dom_chanlib import channels
rows = [r for r in csv.DictReader(open(sys.argv[1]), delimiter='\t') if r['mask']]
rng = np.random.default_rng(0)
def hess_feats(X, sig):
    out = [X]
    for s in sig:
        G = ndi.gaussian_filter(X, s); gy, gx = np.gradient(G); gyy, gyx = np.gradient(gy); gxy, gxx = np.gradient(gx)
        tr = (gxx + gyy) * s * s; dt = np.sqrt(((gxx - gyy) * s * s) ** 2 + 4 * (gxy * s * s) ** 2)
        out += [G, 0.5 * (tr + dt), 0.5 * (tr - dt), np.hypot(gx, gy) * s]
    return out
CH = ['nr', 'nrL', 'fn', 'rc']
def feats(I, valid):
    C, _ = channels(I, valid)
    F = {'raw': hess_feats(C['raw'], (1, 2, 4, 8))}
    F['raw+'] = F['raw'] + hess_feats(C['raw'], (16, 32))[1:]
    for c in CH: F[c] = hess_feats(C[c], (1, 2, 4, 8))
    return {k: np.stack(v, -1) for k, v in F.items()}
SETS = {'raw': ['raw'], 'raw+': ['raw+'], **{f'raw+{c}': ['raw', c] for c in CH}, 'raw+all': ['raw'] + CH}
def load(r):
    I = np.asarray(Image.open(r['img']).convert('L'), dtype=np.float64); m = np.asarray(Image.open(r['mask']))
    wr = np.mean(I >= 250, axis=1) > 0.98; wc = np.mean(I >= 250, axis=0) > 0.98
    return I, m, (~wr[:, None]) & (~wc[None, :]) & (m != 7)
Xtr = {k: [] for k in SETS}; Ytr = {'crack': [], 'inactive': []}
for i, r in enumerate([r for r in rows if r['set'] == 'train']):
    I, m, valid = load(r); F = feats(I, valid)
    idx = []
    for cls in (14, 11):
        p = np.flatnonzero((m == cls).ravel() & valid.ravel())
        if len(p): idx.append(rng.choice(p, min(400, len(p)), replace=False))
    v = np.flatnonzero(valid.ravel()); idx.append(rng.choice(v, 600, replace=False)); idx = np.concatenate(idx)
    for k, parts in SETS.items(): Xtr[k].append(np.concatenate([F[p].reshape(-1, F[p].shape[-1])[idx] for p in parts], 1))
    Ytr['crack'].append(m.ravel()[idx] == 14); Ytr['inactive'].append(m.ravel()[idx] == 11)
    if i % 100 == 0: print('train', i, file=sys.stderr)
Ytr = {k: np.concatenate(v) for k, v in Ytr.items()}
def fit(X, y, lam=1e-3):
    mu, sd = X.mean(0), X.std(0) + 1e-6; Z = (X - mu) / sd; Z1 = np.c_[Z, np.ones(len(Z))]; yy = y.astype(float)
    w0 = np.zeros(Z1.shape[1]); wpos = 0.5 / max(yy.mean(), 1e-6); wneg = 0.5 / max(1 - yy.mean(), 1e-6); sw = np.where(yy > 0, wpos, wneg)
    def f(w):
        t = Z1 @ w; l = np.logaddexp(0, t) - yy * t; g = Z1.T @ (sw * (1 / (1 + np.exp(-t)) - yy)) / len(yy)
        return (sw * l).mean() + lam * (w[:-1] ** 2).sum(), g + 2 * lam * np.r_[w[:-1], 0]
    w = optimize.minimize(f, w0, jac=True, method='L-BFGS-B', options={'maxiter': 500}).x
    return mu, sd, w
models = {(k, c): fit(np.concatenate(Xtr[k]), Ytr[c]) for k in SETS for c in ('crack', 'inactive')}
print('fitted', len(models), file=sys.stderr)
NB = 4000
def ap_auc(hp, hn):
    tp = np.cumsum(hp[::-1]); fp = np.cumsum(hn[::-1]); P = hp.sum()
    prec = tp / np.maximum(tp + fp, 1); rec = tp / max(P, 1)
    ap = float(np.sum(np.diff(np.r_[0, rec]) * prec))
    cn = np.cumsum(hn) - hn; auc = float(np.sum(hp / max(P, 1) * (cn + 0.5 * hn)) / max(hn.sum(), 1))
    return round(ap, 4), round(auc, 4)
res = {}
for evset, filt in (('val', lambda r: r['set'] == 'val'), ('rf_half', lambda r: r['set'] == 'rf' and r['halfcut'] == '1'),
                    ('rf_full', lambda r: r['set'] == 'rf' and r['halfcut'] == '0')):
    H = {(k, c): (np.zeros(NB), np.zeros(NB)) for k in SETS for c in ('crack', 'inactive')}
    for r in [r for r in rows if filt(r)]:
        I, m, valid = load(r); F = feats(I, valid); ign = np.isin(m, [25, 26, 27, 28]); ev = valid & ~ign
        for k, parts in SETS.items():
            X = np.concatenate([F[p][ev] for p in parts], 1)
            for c, cls in (('crack', 14), ('inactive', 11)):
                mu, sd, w = models[(k, c)]; t = ((X - mu) / sd) @ w[:-1] + w[-1]
                b = np.clip(((t + 20) / 40 * NB).astype(int), 0, NB - 1); y = m[ev] == cls
                H[(k, c)][0][:] += np.bincount(b[y], minlength=NB); H[(k, c)][1][:] += np.bincount(b[~y], minlength=NB)
    res[evset] = {f'{k}|{c}': ap_auc(*H[(k, c)]) for (k, c) in H}
    print(evset, json.dumps(res[evset]))
json.dump(res, open(sys.argv[2], 'w'), indent=1)
