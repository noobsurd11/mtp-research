"""scout, 29 Oct: crack-component library stats for spec_cp5.md (CPU, local E-SCDD masks, read-only).
For the 5% labelled cells (seed0 labeled_5pct.txt) and, for reference, the 471 non-twin train cells:
component counts/sizes (8-conn, >= 20 px), bbox extent, ring overlap with inactive/padding/frame/border/busbar,
crack contrast (ring median - crack median, grey levels) and ring robust sd.
Usage: .venv/bin/python cp_library_stats.py"""
import os, numpy as np
from PIL import Image
from scipy import ndimage as ndi

R = os.path.expanduser('~/mtp/datasets/escdd_full')
S = os.path.expanduser('~/mtp/datasets/splits_benchmark')
TWINS = {'CFVS_00003_r5_c5', 'CFVS_00037_r8_c4', 'CFVS_00032_r8_c4', 'CFVS_00020_r4_c4',
         'CFVS_00022_r4_c4', 'CFVS_00031_r4_c4', 'ARTS_00081_r5_c1'}
CRACK, INACT, PAD, BORDER, BUS, FRAME = 14, 11, 7, 5, 9, 21
K8 = np.ones((3, 3), bool)


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


import glob
MP = {os.path.basename(p)[:-4]: p for p in glob.glob(R + '/el_masks_*/*.png') if not os.path.basename(p)[0].isdigit()}
IP = {os.path.basename(p)[:-4]: p for p in glob.glob(R + '/el_images_*/*.png') if not os.path.basename(p)[0].isdigit()}


def load(stem):
    if stem not in MP or stem not in IP:
        return None, None
    m = np.asarray(Image.open(MP[stem]))
    im = np.asarray(Image.open(IP[stem]).convert('L'))
    return im, m


def stats(stems, tag):
    rows, cells_with, px_tot, n_px = [], 0, 0, 0
    shapes = set()
    for st in stems:
        im, m = load(st)
        if m is None:
            print('  missing E-SCDD mask/image:', st); continue
        shapes.add(im.shape)
        n_px += m.size
        c = m == CRACK
        px_tot += int(c.sum())
        lab, n = ndi.label(c, structure=K8)
        if n == 0:
            continue
        cells_with += 1
        for i, sl in enumerate(ndi.find_objects(lab), 1):
            comp = lab == i
            a = int(comp.sum())
            if a < 20:
                continue
            d1 = ndi.binary_dilation(comp, disk(1))
            d8 = ndi.binary_dilation(comp, disk(8))
            ring = d8 & ~d1
            rv = m[ring]
            ext = max(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start)
            g_ring, g_crack = im[ring & ~c].astype(float), im[comp].astype(float)
            contrast = np.median(g_ring) - np.median(g_crack) if g_ring.size else np.nan
            mad = 1.4826 * np.median(np.abs(g_ring - np.median(g_ring))) if g_ring.size else np.nan
            rows.append(dict(stem=st, src=st.split('_')[0], px=a, ext=ext,
                             f_inact=float((rv == INACT).mean()), f_pad=float(np.isin(rv, [PAD, FRAME, BORDER]).mean()),
                             f_bus=float((rv == BUS).mean()), contrast=contrast, ring_sd=mad))
    print(f'== {tag}: {len(stems)} cells, {cells_with} with crack, crack px {px_tot} ({100 * px_tot / n_px:.3f}% of px), shapes {shapes}')
    if not rows:
        return
    px = np.array([r['px'] for r in rows]); ext = np.array([r['ext'] for r in rows])
    con = np.array([r['contrast'] for r in rows]); sd = np.array([r['ring_sd'] for r in rows])
    fi = np.array([r['f_inact'] for r in rows]); fp = np.array([r['f_pad'] for r in rows]); fb = np.array([r['f_bus'] for r in rows])
    keep = (fi <= 0.2) & (fp == 0)
    print(f'components >= 20 px: {len(rows)}; px median {np.median(px):.0f} p10 {np.percentile(px, 10):.0f} p90 {np.percentile(px, 90):.0f} max {px.max()}')
    print(f'bbox extent (px) median {np.median(ext):.0f} p90 {np.percentile(ext, 90):.0f} max {ext.max()}')
    print(f'ring touches inactive >20%: {(fi > 0.2).sum()}; touches padding/frame/border: {(fp > 0).sum()}; ring on busbar >0: {(fb > 0).sum()}')
    print(f'kept (inactive <= 20%, no padding/frame/border in ring): {keep.sum()} comps, {px[keep].sum()} px, from {len(set(r["stem"] for r, k in zip(rows, keep) if k))} cells')
    print(f'crack contrast (ring median - crack median, GL): median {np.nanmedian(con):.1f} p10 {np.nanpercentile(con, 10):.1f} p90 {np.nanpercentile(con, 90):.1f}; ring robust sd median {np.nanmedian(sd):.1f}; contrast/sd median {np.nanmedian(con / sd):.2f}')
    by = {}
    for r, k in zip(rows, keep):
        b = by.setdefault(r['src'], [0, 0, 0, []])
        b[0] += 1; b[1] += int(k); b[2] += r['px'] * int(k); b[3].append(r['contrast'])
    for s, (n, nk, pk, cl) in sorted(by.items()):
        print(f'  {s}: comps {n}, kept {nk}, kept px {pk}, contrast median {np.nanmedian(cl):.1f} GL')


if __name__ == '__main__':
    five = [l.strip() for l in open(f'{S}/seed0/labeled_5pct.txt') if l.strip()]
    train = [l.strip() for l in open(f'{S}/train.txt') if l.strip() and l.strip() not in TWINS]
    stats(five, '5% labelled (seed0)')
    stats(train, 'train minus 7 twins (100%)')
