"""evalx: montage of E1 cells from the 3 crack-heaviest modules + 2 high-recall modules: image | GT crack overlay (red)."""
import glob, os, sys
import numpy as np
from PIL import Image
D = '/home/yugma/mtp/datasets/BenchmarkEL_releases/dataset_20221008/'
mods = sys.argv[1].split(',')
out = sys.argv[2]
tiles = []
for m in mods:
    for f in sorted(glob.glob(D + 'el_images_*/' + m + '_*.png'))[:5]:
        s = os.path.basename(f)
        mk = [x for x in glob.glob(D + 'el_masks_*/' + s) if 'rgb' not in x]
        im = np.array(Image.open(f).convert('L').resize((256, 256)))
        mask = np.array(Image.open(mk[0]).resize((256, 256), Image.NEAREST)) == 14 if mk else np.zeros_like(im, bool)
        rgb = np.stack([im] * 3, -1).copy(); ov = rgb.copy(); ov[mask] = [255, 0, 0]
        tiles.append(np.concatenate([rgb, ov], 1))
rows = [np.concatenate(tiles[i:i + 3], 1) for i in range(0, len(tiles) - len(tiles) % 3, 3)]
if len(tiles) % 3:
    last = tiles[-(len(tiles) % 3):]; pad = [np.zeros_like(tiles[0])] * (3 - len(last))
    rows.append(np.concatenate(last + pad, 1))
Image.fromarray(np.concatenate(rows, 0)).save(out)
print(len(tiles), 'tiles ->', out)
