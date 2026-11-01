"""Idea 5: appearance statistics of cells (real half-cuts, full cells, synthetic half-cuts). numpy/scipy/PIL only.
Per image: content box (white letterbox rule of ideas F6), cell pitch x/y (autocorrelation of the high-passed image,
x in [180,420], y in [120,420]), horizontal gap lines (row-profile minima spaced by pitch y): width at half depth
(px) and depth (1 - min/plateau); cut-edge asymmetry = (band below gap - band above gap)/plateau, 12-px bands;
busbar period (column-profile autocorrelation in [15,130] px); mean/sd/mean|Laplacian| of content;
with a mask: crack px, crack width (px / skeleton px), scuff px.
Usage: python -I dom_halfcut_stats.py LIST.tsv OUT.tsv   (LIST: group<TAB>img<TAB>mask-or-empty)"""
import sys, csv, numpy as np
from PIL import Image
from scipy import ndimage as ndi
def mgauss(a, valid, s):
    num = ndi.gaussian_filter(np.where(valid, a, 0.), s); den = ndi.gaussian_filter(valid.astype(float), s)
    return num / np.maximum(den, 1e-3)
def ac1(p):
    p = p - p.mean(); n = len(p); f = np.fft.rfft(p, 2 * n); a = np.fft.irfft(f * np.conj(f))[:n]
    return a / np.maximum(np.arange(n, 0, -1), 1) / max(a[0] / n, 1e-9)
def pitch2d(hp, valid, axis, lo, hi):
    # mean autocorrelation of rows (axis=1 -> x pitch) or columns (axis=0 -> y pitch) over valid lines
    lines = hp if axis == 1 else hp.T; vm = valid if axis == 1 else valid.T
    acs = [ac1(l[v]) for l, v in zip(lines, vm) if v.sum() > hi + 20]
    if len(acs) < 10: return np.nan, np.nan
    L = min(len(a) for a in acs); A = np.mean([a[:L] for a in acs], 0)
    if L <= lo + 2: return np.nan, np.nan
    seg = A[lo:min(hi, L - 1)]; k = int(np.argmax(seg)); return float(lo + k), float(seg[k])
def skel_len(m):
    try:
        from skimage.morphology import skeletonize; return int(skeletonize(m).sum())
    except ImportError:
        # fallback: thinning by iterated erosion count is not exact; use px / median distance-transform width
        dt = ndi.distance_transform_edt(m); return int(m.sum() / max(2 * np.median(dt[m]) if m.any() else 1, 1))
rows = [l.rstrip('\n').split('\t') for l in open(sys.argv[1]) if l.strip()]
out = csv.writer(open(sys.argv[2], 'w'), delimiter='\t')
out.writerow(['group', 'img', 'content_h', 'content_w', 'pitch_x', 'acx', 'pitch_y', 'acy', 'n_gaps', 'gap_w', 'gap_depth',
              'edge_asym', 'edge_asym_abs', 'pitch_y_short', 'acy_short', 'gap_spacings', 'gap_widths', 'gap_depths', 'bb_period', 'mean', 'sd', 'lap', 'crack_px', 'crack_w', 'scuff_px'])
for g, ip, mp in [(r + [''])[:3] for r in rows]:
    I = np.asarray(Image.open(ip).convert('L'), dtype=np.float64)
    wr = np.mean(I >= 250, axis=1) > 0.98; wc = np.mean(I >= 250, axis=0) > 0.98
    valid = (~wr[:, None]) & (~wc[None, :])
    ch, cw = int((~wr).sum()), int((~wc).sum())
    hp = I - mgauss(I, valid, 8)
    px, acx = pitch2d(hp, valid, 1, 180, 420); py, acy = pitch2d(hp, valid, 0, 120, 420)
    pys, acys = pitch2d(hp, valid, 0, 120, 220)   # short y pitch (one half-cell row)
    # horizontal gaps: row profile of raw intensity over content columns
    rp = np.array([I[y][valid[y]].mean() if valid[y].sum() > 50 else np.nan for y in range(I.shape[0])])
    gw, gd, ea, gy = [], [], [], []
    if np.isfinite(py) and np.isfinite(rp).sum() > 100:
        rs = ndi.uniform_filter1d(np.nan_to_num(rp, nan=np.nanmedian(rp)), 3)
        plateau = ndi.maximum_filter1d(ndi.median_filter(rs, 31), 60)
        cand = [y for y in range(8, len(rs) - 8) if rs[y] == rs[max(0, y - 50):y + 50].min()]
        for y in cand:
            pl = plateau[y]; depth = 1 - rs[y] / max(pl, 1)
            if depth < 0.08: continue
            half = rs[y] + 0.5 * (pl - rs[y]); a = y; b = y
            while a > 0 and rs[a] < half: a -= 1
            while b < len(rs) - 1 and rs[b] < half: b += 1
            gw.append(b - a); gd.append(depth); gy.append(y)
            if a - 14 >= 0 and b + 14 < len(rs):
                ea.append((rs[b + 2:b + 14].mean() - rs[a - 13:a - 1].mean()) / max(pl, 1))
    bbp = np.nan
    if np.isfinite(px):
        cp = np.array([hp[:, x][valid[:, x]].mean() if valid[:, x].sum() > 50 else 0 for x in range(I.shape[1])])
        a = ac1(cp[valid.any(0)]); seg = a[15:130]
        if len(seg) > 10: bbp = float(15 + np.argmax(seg))
    lap = np.abs(ndi.laplace(I))[valid].mean() if valid.any() else np.nan
    cr = cwid = sc = ''
    if mp:
        m = np.asarray(Image.open(mp)); c = m == 14; cr = int(c.sum()); sc = int((m == 25).sum())
        cwid = round(cr / max(skel_len(c), 1), 3) if cr >= 20 else ''
    out.writerow([g, ip, ch, cw, px, round(acx, 3) if np.isfinite(acx) else '', py, round(acy, 3) if np.isfinite(acy) else '',
                  len(gw), np.median(gw) if gw else '', round(float(np.median(gd)), 3) if gd else '',
                  round(float(np.median(ea)), 4) if ea else '', round(float(np.median(np.abs(ea))), 4) if ea else '',
                  pys, round(acys, 3) if np.isfinite(acys) else '', ','.join(str(int(b - a)) for a, b in zip(gy[:-1], gy[1:])),
                  ','.join(str(int(x)) for x in gw), ','.join('%.2f' % x for x in gd),
                  bbp, round(float(I[valid].mean()), 1), round(float(I[valid].std()), 1), round(float(lap), 2), cr, cwid, sc])
