"""Quick look montage: rows of example cells with crack (red), inactive (blue), scuff (green) overlay.
Usage: python -I dom_montage.py INDEX.tsv OUT.png"""
import sys, csv, numpy as np
from PIL import Image
rows = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
def pick(f, n=4):
    v = [r for r in rows if f(r)]; v.sort(key=lambda r: -int(r['crack_px'])); return v[:n]
groups = [
    ('train CSIR', pick(lambda r: r['set'] == 'train' and r['src'] == 'CSIR')),
    ('train ARTS', pick(lambda r: r['set'] == 'train' and r['src'] == 'ARTS')),
    ('val CFVS/BMRK', pick(lambda r: r['set'] == 'val' and r['src'] in ('CFVS', 'BMRK'))),
    ('E1 halfcut', pick(lambda r: r['set'] == 'E1' and r['halfcut'] == '1')),
    ('rf halfcut', pick(lambda r: r['set'] == 'rf' and r['halfcut'] == '1')),
    ('E1 full', pick(lambda r: r['set'] == 'E1' and r['halfcut'] == '0')),
]
T = 256
M = Image.new('RGB', (8 * T, len(groups) * T), (255, 255, 255))
for i, (g, v) in enumerate(groups):
    for j, r in enumerate(v):
        a = np.asarray(Image.open(r['img']).convert('L'))
        rgb = np.stack([a] * 3, -1).copy(); o = rgb.copy()
        if r['mask']:
            m = np.asarray(Image.open(r['mask']))
            o[m == 14] = [255, 0, 0]; o[m == 11] = [0, 80, 255]; o[m == 25] = [0, 220, 0]
        M.paste(Image.fromarray(rgb).resize((T, T)), (2 * j * T, i * T))
        M.paste(Image.fromarray(o).resize((T, T)), ((2 * j + 1) * T, i * T))
        print(g, r['stem'], r['content_h'], r['content_w'], r['crack_px'], r['scuff_px'])
M.save(sys.argv[2])
