"""marker1 view tool (image only, no labels, no model output).
Usage: python3 m1_view.py <in.png> <outdir>
Writes: <stem>_box.txt (detected centre half-cell box), <stem>_L.png and <stem>_R.png
(left / right halves of the centre band + 8 px margin, 16 px overlap, autocontrast cutoff 1 %, 3x Lanczos)."""
import sys, os
from PIL import Image, ImageOps

def box_of(g):
    w, h = g.size; d = list(g.getdata())
    rows = [sum(d[y*w:(y+1)*w]) / w for y in range(h)]
    cols = [sum(d[y*w + x] for y in range(h)) / h for x in range(w)]
    amin = lambda v, lo, hi: min(range(lo, hi), key=lambda i: v[i])
    y0, y1 = amin(rows, 120, 231), amin(rows, 281, 401)
    x0, x1 = amin(cols, 30, 151), amin(cols, 361, 491)
    ok = (130 <= y1 - y0 <= 230) and (300 <= x1 - x0 <= 420)
    if not ok: x0, y0, x1, y1 = 85, 175, 427, 338
    return x0, y0, x1, y1, ok

def main(src, out):
    st = os.path.basename(src)[:-4]
    g = Image.open(src).convert('L')
    x0, y0, x1, y1, ok = box_of(g)
    open(os.path.join(out, st + '_box.txt'), 'w').write(f'{st}\t{x0}\t{y0}\t{x1}\t{y1}\t{int(ok)}\n')
    m = 8; X0, Y0, X1, Y1 = max(0, x0-m), max(0, y0-m), min(511, x1+m), min(511, y1+m)
    xm = (X0 + X1) // 2
    for tag, (a, b) in {'L': (X0, xm + 8), 'R': (xm - 8, X1)}.items():
        c = ImageOps.autocontrast(g.crop((a, Y0, b + 1, Y1 + 1)), cutoff=1)
        c = c.resize((c.width * 3, c.height * 3), Image.LANCZOS)
        c.save(os.path.join(out, f'{st}_{tag}.png'))
    print(st, x0, y0, x1, y1, ok)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
