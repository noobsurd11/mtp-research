"""Idea 5 diagnostic: deterministic half-cut transforms of VAL cells, to test whether the current model's crack
recall survives (a) inserting a half-cut gap, (b) the half-cell scale, (c) both, (d) both + intensity matched to
pool half-cells (content mean 154, sd 24: medians of 1,008 pool half-cells), (e) (d) + Gaussian blur sigma 0.8
(pool |Laplacian| 2.8 vs train 6-11). Same geometry code as dom_synth_halfcut.py, without jitter; crop clamped
inside the source (no white bands). Both halves of the centre cell -> 2 images per cell for V1-V5; V0 = original.
Usage: python -I dom_synth_variants.py INDEX.tsv OUTDIR"""
import sys, os, csv, numpy as np
from PIL import Image
from scipy import ndimage as ndi
rows = [r for r in csv.DictReader(open(sys.argv[1]), delimiter='\t') if r['set'] == 'val']
OUT = sys.argv[2]
for d in ('images', 'masks'): os.makedirs(f'{OUT}/{d}', exist_ok=True)
def gap_rows(I, valid):
    rp = np.array([I[y][valid[y]].mean() if valid[y].sum() > 50 else np.nan for y in range(I.shape[0])])
    rp = np.nan_to_num(rp, nan=np.nanmedian(rp)); rs = ndi.uniform_filter1d(rp, 3); out = []
    for c in (128, 384):
        lo, hi = c - 45, c + 45; y = lo + int(np.argmin(rs[lo:hi])); pl = np.median(rs[max(0, y - 60):y + 60])
        half = rs[y] + 0.5 * (pl - rs[y]); a = y; b = y
        while a > 0 and rs[a] < half: a -= 1
        while b < len(rs) - 1 and rs[b] < half: b += 1
        out.append((y, a, b, 1 - rs[y] / max(pl, 1)))
    return out
def make(I, M, valid, gap, scale, half):
    (yt, at, bt, dt), (yb, ab, bb, db) = gap_rows(I, valid)
    if not (dt > 0.08 and db > 0.08 and 200 < yb - yt < 310): yt, at, bt, yb = 128, 124, 132, 384
    ymid = int(round((yt + yb) / 2)); g = (bt + 1 - at) if gap else 0
    if gap:
        I2 = np.concatenate([I[:ymid], I[at:bt + 1], I[ymid:]], 0); M2 = np.concatenate([M[:ymid], M[at:bt + 1], M[ymid:]], 0)
        V2 = np.concatenate([valid[:ymid], valid[at:bt + 1], valid[ymid:]], 0)
    else:
        I2, M2, V2 = I, M, valid
    sx, sy = (342 / 256, 163 / (128 + g)) if scale else (1.0, 1.0)
    I3 = ndi.zoom(I2, (sy, sx), order=1) if scale else I2; M3 = ndi.zoom(M2, (sy, sx), order=0) if scale else M2
    V3 = ndi.zoom(V2.astype(np.uint8), (sy, sx), order=0).astype(bool) if scale else V2
    cy = ((yt + ymid) / 2 if half == 0 else (ymid + g + yb + g) / 2) * sy; cx = 256 * sx
    y0 = int(np.clip(round(cy - 256), 0, I3.shape[0] - 512)); x0 = int(np.clip(round(cx - 256), 0, I3.shape[1] - 512))
    return I3[y0:y0 + 512, x0:x0 + 512], M3[y0:y0 + 512, x0:x0 + 512], V3[y0:y0 + 512, x0:x0 + 512]
def appear(O, V, blur):
    v = O[V]; O2 = O.copy(); O2[V] = (v - v.mean()) / max(v.std(), 1e-3) * 24 + 154
    if blur: O2 = np.where(V, ndi.gaussian_filter(O2, 0.8), O2)
    return np.clip(O2, 0, 255)
lst = open(f'{OUT}/list.tsv', 'w')
for r in rows:
    I = np.asarray(Image.open(r['img']).convert('L'), dtype=np.float64); M = np.asarray(Image.open(r['mask'])).astype(np.uint8)
    M = M.copy(); M[M == 24] = 2; M[M == 29] = 1; M[np.isin(M, [25, 26, 27, 28])] = 0
    wr = np.mean(I >= 250, axis=1) > 0.98; wc = np.mean(I >= 250, axis=0) > 0.98; valid = (~wr[:, None]) & (~wc[None, :])
    outs = [('V0', I, M, valid)]
    for half in (0, 1):
        for vn, gap, sc in (('V1', 1, 0), ('V2', 0, 1), ('V3', 1, 1)):
            O, OM, OV = make(I, M, valid, gap, sc, half); outs.append((f'{vn}h{half}', O, OM, OV))
        O, OM, OV = make(I, M, valid, 1, 1, half)
        outs.append((f'V4h{half}', appear(O, OV, False), OM, OV)); outs.append((f'V5h{half}', appear(O, OV, True), OM, OV))
    for vn, O, OM, OV in outs:
        name = f'{r["stem"]}__{vn}'
        Image.fromarray(np.clip(O, 0, 255).astype(np.uint8)).save(f'{OUT}/images/{name}.png'); Image.fromarray(OM.astype(np.uint8)).save(f'{OUT}/masks/{name}.png')
        lst.write(f'{name}\t{vn[:2]}\t{r["stem"]}\n')
lst.close()
