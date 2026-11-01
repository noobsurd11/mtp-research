"""Ideas 3 + 4 prototype: label-free extra channels, scored by how well GT defect px separate from background.
Channels (all per image, label-free):
  raw  : -I
  hp   : -(I - G8(I))                      high-pass baseline (masked Gaussian, sigma 8)
  nr   : -(hp(I) - median_k hp(I)(p+s_k))  in-crop neighbour reference: shifts s_k = cell pitch found by
                                           autocorrelation (x, y, both diagonals), refined +-10 px
  nrL  : as nr on I/G64(I) without hp      (region scale, for inactive)
  fn   : -notch(hp(I))                     Fourier notch: spectral peaks > 4x local median, near the axes
  rc   : -(hp - colmedian - rowmedian)     full-length line removal
Scores z-scored per image by median/MAD over content px. Pixel sets: content = not white letterbox and not
class 7. Positives crack 14 / inactive 11 / scuff 25. Negatives: all non-defect content px (classes 0-5, 9) and
'hard' = ribbons/busbars/spacing (1, 2, 3, 4, 9). Pooled histogram AUROC (2,000 bins on [-12, 12]) and per-cell
crack CNR = (median ring - median crack) / (1.4826 MAD ring), ring = dilate6 - dilate2 of crack, non-defect only.
Also: share of crack px whose reference positions are themselves crack (+-2 px) = reference contamination.
Usage: python -I dom_channels.py INDEX.tsv SET[,SET] OUT.json [max_cells]"""
import sys, csv, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
rows = [r for r in csv.DictReader(open(sys.argv[1]), delimiter='\t') if r['set'] in sys.argv[2].split(',') and r['mask']]
MAXN = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 9
import os
CT = os.environ.get('CTYPE')  # optional filter: prefix of ctype column, e.g. 'multi' or 'mono' or 'unknown'
if CT: rows = [r for r in rows if r.get('ctype', '').startswith(CT)]
SRC = os.environ.get('SRC')  # optional filter: source prefix (ARTS, CFVS, CSIR, BMRK, SDLE)
if SRC: rows = [r for r in rows if r['src'] == SRC]
rows = rows[:MAXN]
CH = ['raw', 'hp', 'nr', 'nrL', 'fn', 'rc']
NB = 2000; LO, HI = -12., 12.
def mgauss(a, valid, s):
    num = ndi.gaussian_filter(np.where(valid, a, 0.), s); den = ndi.gaussian_filter(valid.astype(float), s)
    return num / np.maximum(den, 1e-3)
def zs(x, valid):
    v = x[valid]; med = np.median(v); mad = 1.4826 * np.median(np.abs(v - med)) + 1e-6
    return (x - med) / mad
def autocorr(h, valid):
    H, W = h.shape; P = np.zeros((2 * H, 2 * W)); M = np.zeros((2 * H, 2 * W))
    P[:H, :W] = np.where(valid, h, 0); M[:H, :W] = valid
    F = np.fft.rfft2(P); G = np.fft.rfft2(M)
    num = np.fft.irfft2(F * np.conj(F), s=P.shape); den = np.fft.irfft2(G * np.conj(G), s=P.shape)
    e = np.fft.irfft2(np.fft.rfft2(P ** 2) * np.conj(G), s=P.shape)
    return num, den, e
def best_shift(num, den, e, dx_rng, dy_rng, minov):
    H2, W2 = num.shape; best = (-9, None)
    for dy in range(dy_rng[0], dy_rng[1] + 1):
        for dx in range(dx_rng[0], dx_rng[1] + 1):
            c = num[dy % H2, dx % W2]; n = den[dy % H2, dx % W2]
            if n < minov: continue
            v = c / max(e[dy % H2, dx % W2], 1e-6)  # normalised by energy in overlap
            if v > best[0]: best = (v, (dx, dy))
    return best
def shifted(a, valid, dx, dy):
    H, W = a.shape; out = np.full(a.shape, np.nan)
    ys = slice(max(0, -dy), min(H, H - dy)); xs = slice(max(0, -dx), min(W, W - dx))
    yt = slice(max(0, dy), min(H, H + dy)); xt = slice(max(0, dx), min(W, W + dx))
    src = np.where(valid, a, np.nan)
    out[ys, xs] = src[yt, xt]
    return out
def notch(h, valid):
    F = np.fft.fft2(np.where(valid, h, 0)); mag = np.abs(F); lm = np.log(mag + 1e-6)
    bg = ndi.median_filter(lm, size=9, mode='wrap')
    H, W = h.shape; ky = np.fft.fftfreq(H) * H; kx = np.fft.fftfreq(W) * W
    KY, KX = np.meshgrid(ky, kx, indexing='ij'); r = np.hypot(KX, KY)
    peak = (lm - bg > np.log(4.)) & (r > 4) & ((np.abs(KX) <= 2) | (np.abs(KY) <= 2))
    peak = ndi.binary_dilation(peak, iterations=1) & (r > 4)
    F2 = np.where(peak, F * np.exp(bg - lm), F)
    return np.real(np.fft.ifft2(F2)), int(peak.sum())
def orient_axis(mask):
    # per crack px: True if local orientation within 15 deg of an image axis (structure tensor of smoothed mask)
    m = ndi.gaussian_filter(mask.astype(float), 2)
    gy, gx = np.gradient(m)
    jxx = ndi.gaussian_filter(gx * gx, 3); jyy = ndi.gaussian_filter(gy * gy, 3); jxy = ndi.gaussian_filter(gx * gy, 3)
    th = 0.5 * np.arctan2(2 * jxy, jxx - jyy)  # gradient direction; line is perpendicular, axis test symmetric
    d = np.degrees(np.abs(th)) % 90
    return (d < 15) | (d > 75)
hist = {ch: {k: np.zeros(NB) for k in ['crack', 'inactive', 'scuff', 'neg', 'hard', 'crack_ax', 'crack_ob']} for ch in CH}
cnr = {ch: [] for ch in CH}; percell = []
contam = {'crack_px': 0, 'ref_crack': 0, 'ref_anydefect': 0, 'n_refs': []}
pitch_log = []
for i, r in enumerate(rows):
    I = np.asarray(Image.open(r['img']).convert('L'), dtype=np.float64)
    m = np.asarray(Image.open(r['mask']))
    white_r = np.mean(I >= 250, axis=1) > 0.98; white_c = np.mean(I >= 250, axis=0) > 0.98
    valid = (~white_r[:, None]) & (~white_c[None, :]) & (m != 7)
    if valid.sum() < 5000: continue
    hp = I - mgauss(I, valid, 8)
    num, den, e = autocorr(hp, valid)
    ch_, cw_ = valid.any(1).sum(), valid.any(0).sum()
    shifts = []
    bx = best_shift(num, den, e, (180, 420), (-10, 10), 0.15 * valid.sum())
    by = best_shift(num, den, e, (-10, 10), (120, 420), 0.15 * valid.sum())
    for b in (bx, by):
        if b[1] is not None and b[0] > 0.15: shifts.append(b[1])
    if len(shifts) == 2:
        (sx, sxy), (syx, sy) = shifts
        for sgn in (1, -1):
            bd = best_shift(num, den, e, (sx + sgn * syx - 10, sx + sgn * syx + 10), (sgn * sy + sxy - 10, sgn * sy + sxy + 10), 0.05 * valid.sum())
            if bd[1] is not None and bd[0] > 0.10: shifts.append(bd[1])
    pitch_log.append({'stem': r['stem'], 'shifts': shifts, 'corr': [round(float(bx[0]), 3), round(float(by[0]), 3)]})
    stack_hp, stack_L, stack_m = [], [], []
    Ln = I / np.maximum(mgauss(I, valid, 64), 1)
    for (dx, dy) in shifts:
        for sg in (1, -1):
            stack_hp.append(shifted(hp, valid, sg * dx, sg * dy)); stack_L.append(shifted(Ln, valid, sg * dx, sg * dy))
            stack_m.append(shifted(m.astype(float), valid, sg * dx, sg * dy))
    if stack_hp:
        ref = np.nanmedian(np.stack(stack_hp), 0); refL = np.nanmedian(np.stack(stack_L), 0)
        nref = np.sum(~np.isnan(np.stack(stack_hp)), 0)
    else:
        ref = np.full(I.shape, np.nan); refL = ref.copy(); nref = np.zeros(I.shape)
    has_ref = ~np.isnan(ref)
    nr = np.where(has_ref, hp - np.nan_to_num(ref), hp)      # fall back to hp where no reference exists
    nrL = np.where(has_ref, Ln - np.nan_to_num(refL), Ln - np.median(Ln[valid]))
    fn, npk = notch(hp, valid)
    rc = hp - np.median(np.where(valid, hp, np.nan), axis=0, keepdims=True).__array__()
    rc = np.nan_to_num(rc); rc = rc - np.nan_to_num(np.nanmedian(np.where(valid, rc, np.nan), axis=1, keepdims=True))
    S = {'raw': -I, 'hp': -hp, 'nr': -nr, 'nrL': -nrL, 'fn': -fn, 'rc': -rc}
    crack = (m == 14) & valid; inac = (m == 11) & valid; scuff = (m == 25) & valid
    negm = np.isin(m, [0, 1, 2, 3, 4, 5, 9]) & valid; hard = np.isin(m, [1, 2, 3, 4, 9]) & valid
    if crack.any():
        ax = orient_axis(crack); cax = crack & ax; cob = crack & ~ax
        ring = ndi.binary_dilation(crack, iterations=6) & ~ndi.binary_dilation(crack, iterations=2) & negm
    pc = {'stem': r['stem'], 'set': r['set'], 'crack_px': int(crack.sum()), 'inactive_px': int(inac.sum()), 'scuff_px': int(scuff.sum()),
          'n_shifts': len(shifts), 'ref_cover': round(float(has_ref[valid].mean()), 3), 'notch_bins': npk}
    for ch in CH:
        z = np.clip(zs(S[ch], valid), LO, HI - 1e-9); b = ((z - LO) / (HI - LO) * NB).astype(int)
        for k, mk in [('crack', crack), ('inactive', inac), ('scuff', scuff), ('neg', negm), ('hard', hard)] + (
                [('crack_ax', cax), ('crack_ob', cob)] if crack.any() else []):
            if mk.any(): hist[ch][k] += np.bincount(b[mk], minlength=NB)
        if crack.sum() >= 20 and ring.sum() >= 20:
            zr = z[ring]; mr = np.median(zr); c = (np.median(z[crack]) - mr) / (1.4826 * np.median(np.abs(zr - mr)) + 1e-6)
            cnr[ch].append(float(c)); pc['cnr_' + ch] = round(float(c), 3)
    if crack.any() and stack_m:
        sm = np.stack(stack_m); dil = np.stack([ndi.binary_dilation(np.nan_to_num(s) == 14, iterations=2) for s in sm])
        avail = ~np.isnan(sm)
        contam['crack_px'] += int(crack.sum())
        contam['ref_crack'] += int(((dil & avail).any(0) & crack).sum())
        dd = np.isin(np.nan_to_num(sm, nan=-1), [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23, 25])
        contam['ref_anydefect'] += int(((dd & avail).any(0) & crack).sum())
        contam['n_refs'].append(float(np.median(nref[crack])))
    percell.append(pc)
    if i % 50 == 0: print(i, r['stem'], shifts, file=sys.stderr)
def auroc(p, n):
    # P(score_pos > score_neg) from histograms (ties half)
    p = p / max(p.sum(), 1); n = n / max(n.sum(), 1); cn = np.cumsum(n) - n
    return float(np.sum(p * (cn + 0.5 * n)))
res = {'n_cells': len(percell), 'sets': sys.argv[2], 'ctype': CT, 'src': SRC, 'auroc': {}, 'cnr_median': {}, 'contam': {}, 'pitch': pitch_log[:5]}
for ch in CH:
    res['auroc'][ch] = {f'{pk}_vs_{nk}': round(auroc(hist[ch][pk], hist[ch][nk]), 4)
                        for pk in ['crack', 'inactive', 'scuff', 'crack_ax', 'crack_ob'] for nk in ['neg', 'hard'] if hist[ch][pk].sum() > 0}
    if hist[ch]['scuff'].sum() > 0 and hist[ch]['crack'].sum() > 0:
        res['auroc'][ch]['crack_vs_scuff'] = round(auroc(hist[ch]['crack'], hist[ch]['scuff']), 4)
    res['cnr_median'][ch] = round(float(np.median(cnr[ch])), 3) if cnr[ch] else None
    res['n_px'] = {k: int(v.sum()) for k, v in hist['raw'].items()}
res['cnr_n'] = len(cnr['raw'])
if contam['crack_px']:
    res['contam'] = {'crack_px': contam['crack_px'], 'ref_is_crack_share': round(contam['ref_crack'] / contam['crack_px'], 4),
                     'ref_any_defect_share': round(contam['ref_anydefect'] / contam['crack_px'], 4),
                     'median_refs_at_crack': float(np.median(contam['n_refs']))}
res['shift_count'] = {k: sum(1 for p in percell if p['n_shifts'] == k) for k in range(5)}
res['percell'] = percell
json.dump(res, open(sys.argv[3], 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ('percell', 'pitch')}, indent=1))
