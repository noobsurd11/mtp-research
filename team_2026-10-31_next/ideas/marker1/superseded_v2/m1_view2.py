"""marker1 view tool v2 (prereg v2): image only; no labels, no model output, no filters.
Usage: python3 m1_view2.py <in.png> <outdir> [quadrant]
  default: V2 = whole 512 crop, no contrast change, 2x Lanczos -> <id>_V2.png (1024 x 1024)
  quadrant in {TL, TR, BL, BR, C}: V3 = 288 x 288 tile (TL/TR/BL/BR corners, C centred), autocontrast cutoff 0.5 %, 3x Lanczos -> <id>_V3<q>.png"""
import sys, os
from PIL import Image, ImageOps
T = {'TL': (0, 0), 'TR': (224, 0), 'BL': (0, 224), 'BR': (224, 224), 'C': (112, 112)}
def main(src, out, q=None):
    i = os.path.basename(src).rsplit('.', 1)[0]
    g = Image.open(src).convert('L')
    if q is None:
        v = g.resize((g.width * 2, g.height * 2), Image.LANCZOS)
        p = os.path.join(out, i + '_V2.png')
    else:
        x, y = T[q]; c = ImageOps.autocontrast(g.crop((x, y, x + 288, y + 288)), cutoff=0.5)
        v = c.resize((864, 864), Image.LANCZOS); p = os.path.join(out, f'{i}_V3{q}.png')
    v.save(p); print(p)
if __name__ == '__main__':
    main(*sys.argv[1:4])
