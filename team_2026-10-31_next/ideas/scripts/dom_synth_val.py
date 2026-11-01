"""SHV1: frozen synthetic half-cut VAL set (domain, 31 Oct 2026). Every val cell (54) cut by the idea-5 simulator,
both halves -> 108 images. Geometry deterministic (no jitter): split the centre cell at its midline, insert a copy of
the image's own gap band (image + mask rows), rescale sx = 342/256, sy = 163/(128 + g) (pool half-cell medians;
CSIR_00300 excluded), crop 512 x 512 centred on the chosen half, clamped inside the source. Intensity: content px
linearly mapped to a (mean, sd) pair drawn, with ONE frozen seed, from the empirical pairs of the 1,008 pool half-cells
(ap_pool.tsv, content px by the F6 white rule). Images bilinear, masks nearest. Masks = house masks_escdd (24 classes;
the inserted gap carries the source's spacing labels: sp multi 1 / sp mono 2, as calib's _rf build (29->1, 24->2)).
Use: non-E1 selection/readout set (e.g. a half-cut crack bias). NEVER for E1 or test.
Usage: python -I dom_synth_val.py VAL_LIST IMG_DIR MASK_DIR POOL_AP_TSV OUTDIR SEED"""
import sys, os, csv, numpy as np
from PIL import Image
from scipy import ndimage as ndi
VAL, IMG, MSK, POOL, OUT, SEED = sys.argv[1:7]; SEED = int(SEED)
stems = sorted(l.strip() for l in open(VAL) if l.strip()); assert len(stems) == 54, len(stems)
pool = [(float(r['mean']), float(r['sd'])) for r in csv.DictReader(open(POOL), delimiter='\t')]; assert len(pool) == 1008, len(pool)
rng = np.random.default_rng(SEED)
for d in ('images', 'masks', 'ignore'): os.makedirs(f'{OUT}/{d}', exist_ok=True)
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
ctx = open(f'{OUT}/shv1_context.tsv', 'w')
ctx.write('name\tsrc_stem\thalf\tgap_found\tg\tsx\tsy\tpool_idx\tmean_t\tsd_t\tcrack_px\tinact_px\tsrc_crack_px\tsrc_inact_px\n')
names = []
for st in stems:
    I = np.asarray(Image.open(f'{IMG}/{st}.png').convert('L'), dtype=np.float64); M = np.asarray(Image.open(f'{MSK}/{st}.png')).astype(np.uint8)
    assert M.max() <= 23
    wr = np.mean(I >= 250, axis=1) > 0.98; wc = np.mean(I >= 250, axis=0) > 0.98; valid = (~wr[:, None]) & (~wc[None, :])
    (yt, at, bt, dt), (yb, ab, bb, db) = gap_rows(I, valid)
    found = int(dt > 0.08 and db > 0.08 and 200 < yb - yt < 310)
    if not found: yt, at, bt, yb = 128, 124, 132, 384
    ymid = int(round((yt + yb) / 2)); g = bt + 1 - at
    I2 = np.concatenate([I[:ymid], I[at:bt + 1], I[ymid:]], 0); M2 = np.concatenate([M[:ymid], M[at:bt + 1], M[ymid:]], 0)
    V2 = np.concatenate([valid[:ymid], valid[at:bt + 1], valid[ymid:]], 0) & (M2 != 7)
    sx, sy = 342 / 256, 163 / (128 + g)
    I3 = ndi.zoom(I2, (sy, sx), order=1); M3 = ndi.zoom(M2, (sy, sx), order=0); V3 = ndi.zoom(V2.astype(np.uint8), (sy, sx), order=0).astype(bool)
    for half in (0, 1):
        cy = ((yt + ymid) / 2 if half == 0 else (ymid + g + yb + g) / 2) * sy; cx = 256 * sx
        y0 = int(np.clip(round(cy - 256), 0, I3.shape[0] - 512)); x0 = int(np.clip(round(cx - 256), 0, I3.shape[1] - 512))
        O = I3[y0:y0 + 512, x0:x0 + 512].copy(); OM = M3[y0:y0 + 512, x0:x0 + 512]; OV = V3[y0:y0 + 512, x0:x0 + 512]
        k = int(rng.integers(len(pool))); mt, sdt = pool[k]
        v = O[OV]; O[OV] = (v - v.mean()) / max(v.std(), 1e-3) * sdt + mt
        name = f'{st}__h{half}'; names.append(name)
        Image.fromarray(np.clip(np.round(O), 0, 255).astype(np.uint8)).save(f'{OUT}/images/{name}.png')
        Image.fromarray(OM.astype(np.uint8)).save(f'{OUT}/masks/{name}.png')
        Image.fromarray(np.zeros((512, 512), np.uint8)).save(f'{OUT}/ignore/{name}.png')
        ctx.write(f'{name}\t{st}\t{half}\t{found}\t{g}\t{sx:.4f}\t{sy:.4f}\t{k}\t{mt:.2f}\t{sdt:.2f}\t{int((OM == 14).sum())}\t{int((OM == 11).sum())}\t{int((M == 14).sum())}\t{int((M == 11).sum())}\n')
ctx.close()
open(f'{OUT}/stems_eval.txt', 'w').write('\n'.join(names) + '\n')
print('wrote', len(names), 'images from', len(stems), 'val cells, seed', SEED)
