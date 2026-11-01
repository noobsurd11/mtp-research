"""Label-free half-cut cell detector (domain, 31 Oct 2026), rule R1, pre-stated in team log 31 Oct before any number.
Image only (PIL 'L'); no mask, no label. Content = rows/cols not >= 98% white (px >= 250). hp = I - masked Gaussian
(sigma 8) over content. Mean autocorrelation of hp over content rows (x lags) and columns (y lags), each line
normalised by its lag-0 energy and overlap length; lines need > hi + 20 content px.
  px, acx = argmax / max over x lags 180..420;  py, acy = same over y lags 180..420
  pxs, pys = argmax over short lags 120..220 (reported only)
R1: half-cut iff (300 <= px <= 400 and acx >= 0.10) or (300 <= py <= 400 and acy >= 0.10); else full.
Physical basis (non-E1): full-cell pitch 256 px in all labelled sources; pool/Hanifi half-cell long pitch 342 px.
Usage: python -I dom_halfcut_detector.py LIST.tsv OUT.tsv [workers]   (LIST: group<TAB>image_path)"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
P = dict(lo=180, hi=420, slo=120, shi=220, band=(300, 400), acmin=0.10, sigma=8, white=250, whitefrac=0.98)
def _ac1(p):
    p = p - p.mean(); n = len(p); f = np.fft.rfft(p, 2 * n); a = np.fft.irfft(f * np.conj(f))[:n]
    return a / np.maximum(np.arange(n, 0, -1), 1) / max(a[0] / n, 1e-9)
def _pitch(hp, valid, lo, hi):
    acs = [_ac1(l[v]) for l, v in zip(hp, valid) if v.sum() > hi + 20]
    if len(acs) < 10: return float('nan'), float('nan')
    L = min(len(a) for a in acs); A = np.mean([a[:L] for a in acs], 0)
    if L <= lo + 2: return float('nan'), float('nan')
    seg = A[lo:min(hi, L - 1) + 1]; k = int(np.argmax(seg)); return float(lo + k), float(seg[k])
def features(img_path):
    I = np.asarray(Image.open(img_path).convert('L'), dtype=np.float64)
    wr = np.mean(I >= P['white'], axis=1) > P['whitefrac']; wc = np.mean(I >= P['white'], axis=0) > P['whitefrac']
    valid = (~wr[:, None]) & (~wc[None, :])
    num = ndi.gaussian_filter(np.where(valid, I, 0.), P['sigma']); den = ndi.gaussian_filter(valid.astype(float), P['sigma'])
    hp = I - num / np.maximum(den, 1e-3)
    px, acx = _pitch(hp, valid, P['lo'], P['hi']); py, acy = _pitch(hp.T, valid.T, P['lo'], P['hi'])
    pxs, _ = _pitch(hp, valid, P['slo'], P['shi']); pys, _ = _pitch(hp.T, valid.T, P['slo'], P['shi'])
    return dict(content_h=int((~wr).sum()), content_w=int((~wc).sum()), px=px, acx=acx, py=py, acy=acy, pxs=pxs, pys=pys)
def rule(f):
    b0, b1 = P['band']
    land = np.isfinite(f['px']) and b0 <= f['px'] <= b1 and f['acx'] >= P['acmin']
    port = np.isfinite(f['py']) and b0 <= f['py'] <= b1 and f['acy'] >= P['acmin']
    return int(land or port), ('landscape' if land else ('portrait' if port else ''))
def _one(row):
    g, p = row; f = features(p); h, why = rule(f); return g, p, f, h, why
if __name__ == '__main__':
    rows = [tuple(l.rstrip('\n').split('\t')[:2]) for l in open(sys.argv[1]) if l.strip()]
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    if W > 1:
        from multiprocessing import Pool
        with Pool(W) as pool: res = pool.map(_one, rows, chunksize=16)
    else:
        res = [_one(r) for r in rows]
    with open(sys.argv[2], 'w') as o:
        o.write('group\timg\tcontent_h\tcontent_w\tpx\tacx\tpy\tacy\tpxs\tpys\thalfcut\twhy\n')
        for g, p, f, h, why in res:
            o.write(f"{g}\t{p}\t{f['content_h']}\t{f['content_w']}\t{f['px']}\t{f['acx']:.4f}\t{f['py']}\t{f['acy']:.4f}\t{f['pxs']}\t{f['pys']}\t{h}\t{why}\n")
