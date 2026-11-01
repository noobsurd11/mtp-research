"""Figure: Hanifi _rf half-cut crack cells (non-E1): image | GT crack red, scuff/ignore green | FINAL (+0.75) crack.
Usage: python -I dom_rf_fig.py DUMP.npz CALIB_RF_DIR OUT.png [n]"""
import sys, csv, numpy as np
from PIL import Image
z = np.load(sys.argv[1]); RF = sys.argv[2]; N = int(sys.argv[4]) if len(sys.argv) > 4 else 8
ctx = {r['stem']: r for r in csv.DictReader(open(RF + '/rf_context.tsv'), delimiter='\t')}
st = [str(s) for s in z['stems']]
sel = sorted([i for i, s in enumerate(st) if ctx[s]['halfcut'] == '1' and int(ctx[s]['crack_px']) >= 20], key=lambda i: -int(ctx[st[i]]['crack_px']))[:N]
T = 256; M = Image.new('RGB', (3 * T, len(sel) * T), (255, 255, 255))
for r, i in enumerate(sel):
    a = np.asarray(Image.open(f'{RF}/images/{st[i]}.png').convert('L')); m = np.asarray(Image.open(f'{RF}/masks/{st[i]}.png'))
    ig = np.asarray(Image.open(f'{RF}/ignore/{st[i]}.png')) > 0; p = z['margin'][i].astype(np.float32) + 0.75 > 0
    rgb = np.stack([a] * 3, -1); g = rgb.copy(); g[ig] = [0, 200, 0]; g[m == 14] = [255, 0, 0]; q = rgb.copy(); q[p] = [255, 0, 255]
    for c, im in enumerate([rgb, g, q]): M.paste(Image.fromarray(im).resize((T, T)), (c * T, r * T))
M.save(sys.argv[3])
