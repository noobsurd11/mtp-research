"""SHV1-c: SHV1 images whose source val cell passes a protocol_HC source rule. rule_c (coach v0.1): gap found AND band
width g <= 20 AND no class-7 px in the inserted band rows. rule_p (domain proposal): gap found AND g <= 20 AND band
class-7 fraction < 0.4 (excludes single-cell crops only, keeps module-edge cells with side margins). Same gap code as dom_synth_val.py. Reads only val images/masks and the
frozen shv1_context.tsv; no model output. Usage: python -I dom_shv1_subset.py VAL_LIST IMG_DIR MASK_DIR SHV1_CONTEXT OUT"""
import sys, csv, numpy as np
from PIL import Image
from scipy import ndimage as ndi
VAL, IMG, MSK, CTX, OUT = sys.argv[1:6]
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
ok = {}
for st in sorted(l.strip() for l in open(VAL) if l.strip()):
    I = np.asarray(Image.open(f'{IMG}/{st}.png').convert('L'), dtype=np.float64); M = np.asarray(Image.open(f'{MSK}/{st}.png'))
    wr = np.mean(I >= 250, axis=1) > 0.98; wc = np.mean(I >= 250, axis=0) > 0.98; valid = (~wr[:, None]) & (~wc[None, :])
    (yt, at, bt, dt), (yb, ab, bb, db) = gap_rows(I, valid)
    found = dt > 0.08 and db > 0.08 and 200 < yb - yt < 310
    g = bt + 1 - at; pf = float((M[at:bt + 1] == 7).mean()); pad = pf > 0
    ok[st] = (found, g, pad, found and g <= 20 and not pad, pf, found and g <= 20 and pf < 0.4)
rows = list(csv.DictReader(open(CTX), delimiter='\t'))
with open(OUT, 'w') as o:
    o.write('name\tsrc_stem\tgap_found\tg\tpad_in_band\tband_pad_frac\trule_c_pass\trule_p_pass\tcrack_px\tinact_px\n')
    for r in rows:
        f, g, pad, p, pf, pp = ok[r['src_stem']]
        o.write(f"{r['name']}\t{r['src_stem']}\t{int(f)}\t{g}\t{int(pad)}\t{pf:.3f}\t{int(p)}\t{int(pp)}\t{r['crack_px']}\t{r['inact_px']}\n")
for j, nm in ((3, 'rule_c'), (5, 'rule_p')):
  print(nm, 'SHV1 images', len(rows), 'passing', sum(ok[r['src_stem']][j] for r in rows), '| val cells passing', sum(v[j] for v in ok.values()), 'of', len(ok),
      '| crack images (>=20 px) passing', sum(1 for r in rows if ok[r['src_stem']][j] and int(r['crack_px']) >= 20),
      '| inactive images passing', sum(1 for r in rows if ok[r['src_stem']][j] and int(r['inact_px']) > 0))
