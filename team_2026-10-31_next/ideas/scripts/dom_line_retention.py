"""Idea 4 risk test: do periodic-removal channels erase cracks parallel to busbars/fingers?
Insert a 2-px dark line (depth 15 grey levels, linear, before any filtering) into crack-free VAL cells at the
centre, orientation vertical / horizontal / 30 deg / 60 deg, length 64 / 128 / 256 / 480 px. Retention = (mean channel
value on the line px with line - without line) / same for the hp baseline (1.0 = as visible as after a plain
high-pass). Channels from dom_chanlib (z-scored per image; the z-scaling is shared by computing it on the
line-free image). Usage: python -I dom_line_retention.py INDEX.tsv"""
import sys, csv, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, __import__('os').path.dirname(__file__))
from dom_chanlib import channels
rows = [r for r in csv.DictReader(open(sys.argv[1]), delimiter='\t') if r['set'] == 'val' and r['crack_px'] == '0' and r['inactive_px'] == '0'][:20]
res = {}
for r in rows:
    I = np.asarray(Image.open(r['img']).convert('L'), dtype=np.float64)
    wr = np.mean(I >= 250, axis=1) > 0.98; wc = np.mean(I >= 250, axis=0) > 0.98; valid = (~wr[:, None]) & (~wc[None, :])
    if valid.sum() < 200000: continue
    C0, _ = channels(I, valid)
    for ang in (90, 0, 30, 60):
        for L in (64, 128, 256, 480):
            im = Image.new('L', (512, 512), 0); d = ImageDraw.Draw(im); t = np.radians(ang)
            dx, dy = np.cos(t) * L / 2, -np.sin(t) * L / 2; d.line([(256 - dx, 256 - dy), (256 + dx, 256 + dy)], fill=255, width=2)
            ln = (np.asarray(im) > 0) & valid
            if ln.sum() < 20: continue
            C1, _ = channels(I - 15.0 * ln, valid)
            base = (C1['hp'][ln] - C0['hp'][ln]).mean()
            for ch in ('raw', 'nr', 'fn', 'rc'):
                res.setdefault((ch, ang, L), []).append((C1[ch][ln] - C0[ch][ln]).mean() / max(base, 1e-6))
print('cells', len(rows)); print('retention vs hp (median over cells); angle 90 = vertical, 0 = horizontal')
for ch in ('nr', 'fn', 'rc', 'raw'):
    for ang in (90, 0, 30, 60):
        print('%-3s ang %2d ' % (ch, ang) + '  '.join('L%-3d %.2f' % (L, np.median(res[(ch, ang, L)])) for L in (64, 128, 256, 480) if (ch, ang, L) in res))
