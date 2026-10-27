"""Half-cut cells: E1 vs E-SCDD _rf (pool frame). Crack width (px / skeleton px), content box, and the
dominant period of the column/row intensity profile (grid repeat) as a scale proxy. Usage: halfcut_scale.py <montage.png>"""
import sys, glob, os, numpy as np, json
from PIL import Image
from skimage.morphology import skeletonize
R = os.path.expanduser('~/mtp/datasets/escdd_full')
d = json.load(open('/home/yugma/mtp/research/team_2026-10-24_go/trackM/final/final_cells.json'))
ext = set(d['ext']['final_b0.75'])
def period(prof):
    p = prof - np.convolve(prof, np.ones(31) / 31, mode='same'); p = p[20:-20]
    f = np.abs(np.fft.rfft(p - p.mean())); fr = np.fft.rfftfreq(len(p))
    ok = (fr > 1 / 300) & (fr < 1 / 15); return 1 / fr[ok][np.argmax(f[ok])]
rows = {'E1': [], 'rf': []}
for mp in glob.glob(R + '/el_masks_*/*.png'):
    st = os.path.basename(mp)[:-4]
    if st[0].isdigit(): continue
    grp = 'E1' if st in ext else ('rf' if st.endswith('_rf') else None)
    if grp is None: continue
    m = np.asarray(Image.open(mp))
    if not (m == 29).any(): continue
    ip = mp.replace('el_masks_', 'el_images_'); a = np.asarray(Image.open(ip).convert('L'), dtype=np.float32)
    keep_r = np.mean(a >= 250, axis=1) <= 0.98; keep_c = np.mean(a >= 250, axis=0) <= 0.98
    c = a[keep_r][:, keep_c]
    cr = m == 14; n = cr.sum(); w = n / max(skeletonize(cr).sum(), 1) if n >= 20 else np.nan
    rows[grp].append((st, c.shape[0], c.shape[1], period(c.mean(0)), period(c.mean(1)), n, w, ip, mp))
for g, v in rows.items():
    a = np.array([r[1:7] for r in v], dtype=float)
    print(g, len(v), 'content h/w median', np.median(a[:, 0]), np.median(a[:, 1]), '| col period median %.1f, row period median %.1f' % (np.median(a[:, 2]), np.median(a[:, 3])),
          '| crack cells', int((a[:, 4] >= 20).sum()), 'width median %.2f' % np.nanmedian(a[:, 5]))
# montage: 4 E1 and 4 rf half-cut crack cells, native, with crack overlay
T = 256; M = Image.new('RGB', (4 * T * 2, 2 * T), (255, 255, 255))
for i, g in enumerate(['E1', 'rf']):
    v = sorted([r for r in rows[g] if r[5] >= 100], key=lambda r: -r[5])[:4]
    for j, r in enumerate(v):
        a = np.asarray(Image.open(r[7]).convert('L')); m = np.asarray(Image.open(r[8])) == 14
        rgb = np.stack([a, a, a], -1).copy(); rgb2 = rgb.copy(); rgb2[m] = [255, 0, 0]
        M.paste(Image.fromarray(rgb).resize((T, T)), (2 * j * T, i * T)); M.paste(Image.fromarray(rgb2).resize((T, T)), ((2 * j + 1) * T, i * T))
M.save(sys.argv[1])
