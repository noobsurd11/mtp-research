# Sample montage: synthetic images next to their real base, and newly annotated (_rf) cells; crack red, inactive blue.
import os, sys, json, numpy as np
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ESC, OUTD = sys.argv[1], sys.argv[2]
inv = json.load(open(os.path.join(OUTD, 'out', 'inv_escdd.json')))
def ov(split, f):
    g = np.asarray(Image.open(os.path.join(ESC, f'el_images_{split}', f)).convert('L'), np.float32) / 255
    m = np.asarray(Image.open(os.path.join(ESC, f'el_masks_{split}', f))); rgb = np.stack([g] * 3, -1)
    rgb[m == 14] = [1, 0, 0]; rgb[m == 11] = 0.5 * rgb[m == 11] + 0.5 * np.array([0, 0.3, 1]); return g, rgb
rows = []
for base in ('CFVS_00114_r2_c5', 'CSIR_00067_r4_c3_rf', 'CSIR_00094_r3_c5_rf'):
    b = next(r for r in inv if r['file'] == base + '.png'); syn = [r for r in inv if r['kind'] == 'synthetic' and r['base'] == base]
    pick = [next(r for r in syn if r['cond'] == c) for c in ('crack', 'bckgnd') if any(r['cond'] == c for r in syn)]
    rows.append([(b, 'real base')] + [(r, f"synthetic ({r['cond']})") for r in pick])
rf = [r for r in inv if r['kind'] == 'real_rf' and r['counts'][14] > 0][:3]
rows.append([(r, 'new annotation (_rf)') for r in rf])
fig, ax = plt.subplots(len(rows), 6, figsize=(18, 3.2 * len(rows)))
for i, row in enumerate(rows):
    for j in range(3):
        for k in range(2): ax[i, 2 * j + k].axis('off')
        if j >= len(row): continue
        r, t = row[j]; g, o = ov(r['split'], r['file'])
        ax[i, 2 * j].imshow(g, cmap='gray', vmin=0, vmax=1); ax[i, 2 * j].set_title(f"{t}\n{r['file'][:34]}", fontsize=7)
        ax[i, 2 * j + 1].imshow(o); ax[i, 2 * j + 1].set_title('mask: crack red, inactive blue', fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(OUTD, 'escdd_samples.png'), dpi=80)
