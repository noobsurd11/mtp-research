"""evalx: sensitivity of the scuff split to the scuff-px threshold (FINAL b0.75, E1 ext crack cells)."""
import json, glob
import numpy as np
from PIL import Image
D = '/home/yugma/mtp/datasets/BenchmarkEL_releases/dataset_20221008/'
fin = json.load(open('/home/yugma/mtp/research/team_2026-10-24_go/trackM/final/final_cells.json'))['ext']['final_b0.75']
sc = {}
for s in fin:
    f = [x for x in glob.glob(D + 'el_masks_*/' + s + '.png') if 'rgb' not in x]
    sc[s] = int((np.array(Image.open(f[0])) == 25).sum()) if f else 0
cr = {s: np.array(fin[s]['conf']).reshape(24, 24) for s in fin}
crack = [s for s in fin if cr[s][14].sum() > 0]
for t in [1, 500, 2000, 5000]:
    for lab, keep in [(f'scuff>={t}', lambda s: sc[s] >= t), (f'scuff<{t}', lambda s: sc[s] < t)]:
        cs = [s for s in crack if keep(s)]
        g = sum(cr[s][14].sum() for s in cs); tp = sum(cr[s][14, 14] for s in cs)
        print(f'{lab}: crack cells {len(cs)}, crack px {g}, FINAL recall {tp / max(g, 1):.3f}')
print('scuff px in crack cells:', sorted(sc[s] for s in crack))
