"""Idea 5 prototype: synthetic half-cut cells from labelled full cells (label-preserving).
Steps per source cell (512 crop, full-cell pitch ~256):
 1. find the centre cell's top/bottom gaps from the row profile (minima near 128 and 384; fallback 128/384) and the
    existing gap band (width at half depth) around the top gap;
 2. split the centre cell at its midline and insert a copy of the image's own gap band (image and mask rows), so
    the two halves are separated like half-cell rows (gap rows carry the source's spacing/ribbon labels);
 3. rescale anisotropically: sx = 342/256 * U(0.92, 1.08), sy = 163/(128 + g) * U(0.92, 1.08) (targets from the
    non-E1 Hanifi/pool half-cells; image bilinear, mask nearest);
 4. crop 512 x 512 centred on the top or bottom half (random); outside the source -> white 255 / mask padding 7.
No new busbars are drawn (source keeps 2-5 busbars; real half-cells have 9). Output: PNG image (L) + index mask.
Usage: python -I dom_synth_halfcut.py INDEX.tsv OUTDIR N_PER_CELL SEED [stem_filter_set=train] [ctype_prefix]"""
import sys, os, csv, numpy as np
from PIL import Image
from scipy import ndimage as ndi
rows = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
OUT = sys.argv[2]; NPC = int(sys.argv[3]); rng = np.random.default_rng(int(sys.argv[4]))
SET = sys.argv[5] if len(sys.argv) > 5 else 'train'; CT = sys.argv[6] if len(sys.argv) > 6 else ''
os.makedirs(OUT + '/images', exist_ok=True); os.makedirs(OUT + '/masks', exist_ok=True)
src = [r for r in rows if r['set'] == SET and r['mask'] and r.get('ctype', '').startswith(CT)]
def gap_rows(I, valid):
    rp = np.array([I[y][valid[y]].mean() if valid[y].sum() > 50 else np.nan for y in range(I.shape[0])])
    rp = np.nan_to_num(rp, nan=np.nanmedian(rp)); rs = ndi.uniform_filter1d(rp, 3)
    out = []
    for c in (128, 384):
        lo, hi = c - 45, c + 45; y = lo + int(np.argmin(rs[lo:hi]))
        pl = np.median(rs[max(0, y - 60):y + 60]); half = rs[y] + 0.5 * (pl - rs[y])
        a = y; b = y
        while a > 0 and rs[a] < half: a -= 1
        while b < len(rs) - 1 and rs[b] < half: b += 1
        depth = 1 - rs[y] / max(pl, 1)
        out.append((y, a, b, depth))
    return out
log = csv.writer(open(OUT + '/synth_log.tsv', 'w'), delimiter='\t')
log.writerow(['out', 'src', 'gap_found', 'g', 'sx', 'sy', 'half', 'crack_src', 'crack_out', 'inact_src', 'inact_out'])
k = 0
for r in src:
    I = np.asarray(Image.open(r['img']).convert('L'), dtype=np.float64); M = np.asarray(Image.open(r['mask'])).astype(np.uint8)
    if M.max() > 23:  # E-SCDD classes 24-29 -> our scheme (as P6): scuff/star/brightening/corrosion cell -> background,
        M = M.copy(); M[M == 24] = 2; M[M == 29] = 1; M[np.isin(M, [25, 26, 27, 28])] = 0   # disclosed simplification
    wr = np.mean(I >= 250, axis=1) > 0.98; wc = np.mean(I >= 250, axis=0) > 0.98
    valid = (~wr[:, None]) & (~wc[None, :])
    (yt, at, bt, dt), (yb, ab, bb, db) = gap_rows(I, valid)
    found = dt > 0.08 and db > 0.08 and 200 < yb - yt < 310
    if not found: yt, at, bt, yb = 128, 124, 132, 384
    ymid = int(round((yt + yb) / 2)); band = slice(at, bt + 1); g = bt + 1 - at
    for j in range(NPC):
        I2 = np.concatenate([I[:ymid], I[band], I[ymid:]], 0); M2 = np.concatenate([M[:ymid], M[band], M[ymid:]], 0)
        sx = 342 / 256 * rng.uniform(0.92, 1.08); sy = 163 / (128 + g) * rng.uniform(0.92, 1.08)
        I3 = ndi.zoom(I2, (sy, sx), order=1); M3 = ndi.zoom(M2, (sy, sx), order=0)
        half = int(rng.integers(2))  # 0 top half, 1 bottom half
        cy = ((yt + ymid) / 2 if half == 0 else (ymid + g + yb + g) / 2) * sy; cx = 256 * sx
        y0 = int(round(cy - 256)); x0 = int(round(cx - 256))
        O = np.full((512, 512), 255.0); OM = np.full((512, 512), 7, np.uint8)
        ys = slice(max(0, y0), min(I3.shape[0], y0 + 512)); xs = slice(max(0, x0), min(I3.shape[1], x0 + 512))
        O[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0] = I3[ys, xs]
        OM[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0] = M3[ys, xs]
        name = f'syn{k:05d}_{r["stem"]}_h{half}'
        Image.fromarray(np.clip(O, 0, 255).astype(np.uint8)).save(f'{OUT}/images/{name}.png')
        Image.fromarray(OM).save(f'{OUT}/masks/{name}.png')
        log.writerow([name, r['stem'], int(found), g, round(sx, 3), round(sy, 3), half, int((M == 14).sum()), int((OM == 14).sum()),
                      int((M == 11).sum()), int((OM == 11).sum())])
        k += 1
print('wrote', k, 'from', len(src), 'source cells')
