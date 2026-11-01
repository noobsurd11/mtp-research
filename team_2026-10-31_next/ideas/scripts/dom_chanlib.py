"""Shared label-free channel computation for ideas 3/4 (same definitions as dom_channels.py)."""
import numpy as np
from scipy import ndimage as ndi
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
            n = den[dy % H2, dx % W2]
            if n < minov: continue
            v = num[dy % H2, dx % W2] / max(e[dy % H2, dx % W2], 1e-6)
            if v > best[0]: best = (v, (dx, dy))
    return best
def shifted(a, valid, dx, dy):
    H, W = a.shape; out = np.full(a.shape, np.nan)
    ys = slice(max(0, -dy), min(H, H - dy)); xs = slice(max(0, -dx), min(W, W - dx))
    yt = slice(max(0, dy), min(H, H + dy)); xt = slice(max(0, dx), min(W, W + dx))
    out[ys, xs] = np.where(valid, a, np.nan)[yt, xt]; return out
def notch(h, valid):
    F = np.fft.fft2(np.where(valid, h, 0)); mag = np.abs(F); lm = np.log(mag + 1e-6)
    bg = ndi.median_filter(lm, size=9, mode='wrap'); H, W = h.shape
    KY, KX = np.meshgrid(np.fft.fftfreq(H) * H, np.fft.fftfreq(W) * W, indexing='ij'); r = np.hypot(KX, KY)
    peak = (lm - bg > np.log(4.)) & (r > 4) & ((np.abs(KX) <= 2) | (np.abs(KY) <= 2))
    peak = ndi.binary_dilation(peak, iterations=1) & (r > 4)
    return np.real(np.fft.ifft2(np.where(peak, F * np.exp(bg - lm), F)))
def channels(I, valid):
    """Returns dict of label-free channel images (darker defect -> higher score), each z-scored over valid px."""
    hp = I - mgauss(I, valid, 8); num, den, e = autocorr(hp, valid); shifts = []
    for b in (best_shift(num, den, e, (180, 420), (-10, 10), 0.15 * valid.sum()), best_shift(num, den, e, (-10, 10), (120, 420), 0.15 * valid.sum())):
        if b[1] is not None and b[0] > 0.15: shifts.append(b[1])
    if len(shifts) == 2:
        (sx, sxy), (syx, sy) = shifts
        for sgn in (1, -1):
            bd = best_shift(num, den, e, (sx + sgn * syx - 10, sx + sgn * syx + 10), (sgn * sy + sxy - 10, sgn * sy + sxy + 10), 0.05 * valid.sum())
            if bd[1] is not None and bd[0] > 0.10: shifts.append(bd[1])
    Ln = I / np.maximum(mgauss(I, valid, 64), 1); sh, sl = [], []
    for (dx, dy) in shifts:
        for sg in (1, -1): sh.append(shifted(hp, valid, sg * dx, sg * dy)); sl.append(shifted(Ln, valid, sg * dx, sg * dy))
    if sh:
        ref = np.nanmedian(np.stack(sh), 0); refL = np.nanmedian(np.stack(sl), 0)
    else:
        ref = np.full(I.shape, np.nan); refL = ref.copy()
    has = ~np.isnan(ref)
    nr = np.where(has, hp - np.nan_to_num(ref), hp); nrL = np.where(has, Ln - np.nan_to_num(refL), Ln - np.median(Ln[valid]))
    fn = notch(hp, valid)
    rc = hp - np.nan_to_num(np.nanmedian(np.where(valid, hp, np.nan), axis=0, keepdims=True))
    rc = rc - np.nan_to_num(np.nanmedian(np.where(valid, rc, np.nan), axis=1, keepdims=True))
    S = {'raw': -I, 'hp': -hp, 'nr': -nr, 'nrL': -nrL, 'fn': -fn, 'rc': -rc}
    return {k: np.where(valid, zs(v, valid), 0.) for k, v in S.items()}, shifts
