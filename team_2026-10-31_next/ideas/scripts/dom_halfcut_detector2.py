"""Label-free half-cut detector, features v2 (domain, 31 Oct 2026). Developed AFTER rule R1 failed its FP target
(dom_halfcut_detector.py, team log). Image only (PIL 'L'). Content = F6 white rule; hp = I - masked Gaussian sigma 8.
Mean autocorrelation over content rows (x) / columns (y), each line normalised by lag-0 energy and overlap; a line
contributes at lag L only if its content length >= L + 40 (so narrow edge/corner crops still count).
Features per axis a in {x, y}: F_a = max A_a over lags 240..272 (full-cell pitch), H_a = max over 300..400 (half-cell
long pitch) and its argmax hp_a, S_a = max over 140..190 (half-cell row pitch), and the line counts behind them.
Rule R2 (delta fixed on the DEV split only, see dom_halfcut_rule2.py): landscape iff H_x - F_x >= delta and H_x >= 0.10;
portrait iff H_y - F_y >= delta and H_y >= 0.10.
Usage: python -I dom_halfcut_detector2.py LIST.tsv OUT.tsv [workers]"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
P = dict(full=(240, 272), half=(300, 400), row=(140, 190), margin=40, sigma=8, white=250, whitefrac=0.98)
def _ac_lines(hp, valid):
    maxlag = P['half'][1] + 1; S = np.zeros(maxlag); N = np.zeros(maxlag)
    for l, v in zip(hp, valid):
        x = l[v]; n = len(x)
        if n < P['full'][0] + P['margin']: continue
        x = x - x.mean(); f = np.fft.rfft(x, 2 * n); a = np.fft.irfft(f * np.conj(f))[:n]
        a = a / np.maximum(np.arange(n, 0, -1), 1) / max(a[0] / n, 1e-9)
        L = min(maxlag, n - P['margin'])
        if L <= 0: continue
        S[:L] += a[:L]; N[:L] += 1
    return np.where(N >= 10, S / np.maximum(N, 1), np.nan), N
def _win(A, w):
    seg = A[w[0]:w[1] + 1]
    if np.all(np.isnan(seg)): return float('nan'), float('nan')
    k = int(np.nanargmax(seg)); return float(seg[k]), float(w[0] + k)
def features(p):
    I = np.asarray(Image.open(p).convert('L'), dtype=np.float64)
    wr = np.mean(I >= P['white'], axis=1) > P['whitefrac']; wc = np.mean(I >= P['white'], axis=0) > P['whitefrac']
    valid = (~wr[:, None]) & (~wc[None, :])
    num = ndi.gaussian_filter(np.where(valid, I, 0.), P['sigma']); den = ndi.gaussian_filter(valid.astype(float), P['sigma'])
    hp = I - num / np.maximum(den, 1e-3); out = dict(content_h=int((~wr).sum()), content_w=int((~wc).sum()))
    for ax, (h, v) in (('x', (hp, valid)), ('y', (hp.T, valid.T))):
        A, N = _ac_lines(h, v)
        F, _ = _win(A, P['full']); H, hl = _win(A, P['half']); Srow, sl = _win(A, P['row'])
        out.update({f'F_{ax}': F, f'H_{ax}': H, f'hp_{ax}': hl, f'S_{ax}': Srow, f'sp_{ax}': sl,
                    f'nH_{ax}': int(N[P['half'][0]]) if len(N) > P['half'][0] else 0})
    return out
def rule(f, delta, hmin=0.10):
    def ok(ax):
        F, H = f[f'F_{ax}'], f[f'H_{ax}']
        if not np.isfinite(H): return False
        F = F if np.isfinite(F) else 0.0
        return (H - F >= delta) and (H >= hmin)
    l, p = ok('x'), ok('y'); return int(l or p), ('landscape' if l else ('portrait' if p else ''))
KEYS = ['content_h', 'content_w', 'F_x', 'H_x', 'hp_x', 'S_x', 'sp_x', 'nH_x', 'F_y', 'H_y', 'hp_y', 'S_y', 'sp_y', 'nH_y']
def _one(row):
    g, p = row; return g, p, features(p)
if __name__ == '__main__':
    rows = [tuple(l.rstrip('\n').split('\t')[:2]) for l in open(sys.argv[1]) if l.strip()]
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    if W > 1:
        from multiprocessing import Pool
        with Pool(W) as pool: res = pool.map(_one, rows, chunksize=16)
    else:
        res = [_one(r) for r in rows]
    with open(sys.argv[2], 'w') as o:
        o.write('group\timg\t' + '\t'.join(KEYS) + '\n')
        for g, p, f in res: o.write(f'{g}\t{p}\t' + '\t'.join(str(round(f[k], 4)) if isinstance(f[k], float) else str(f[k]) for k in KEYS) + '\n')
