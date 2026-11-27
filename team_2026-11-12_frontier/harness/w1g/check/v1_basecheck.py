"""W1-G item 2 (builder, 13 Nov): decoded-array check of gaint's real masks_escdd against the local v1 rebuild.
Reads MANIFEST.tsv of benchmark/out/masks_v11 (v1_pixmd5 = md5 of the raw uint8 512x512 array of the local rebuild of
masks_escdd, make_masks_v11.py 4467261c) and decodes <labeled>/masks_escdd/<stem>.png for the 582 stems (same rmask as
the script: first channel if 3-D, shape 512x512, uint8). Prints counts only. Optional: --strict DIR (v1.1 strict pngs)
and --v11 DIR (v1.1 pngs) are decoded and checked against the manifest's v11 columns; --pool pool532_manifest.tsv checks
the image file md5s against <labeled>/images. CPU, numpy + PIL. Run with python -I.
"""
import argparse, hashlib, sys
import numpy as np
from PIL import Image
ap = argparse.ArgumentParser()
ap.add_argument('--manifest', required=True); ap.add_argument('--labeled', required=True)
ap.add_argument('--v11'); ap.add_argument('--strict'); ap.add_argument('--pool')
a = ap.parse_args()
def rmask(p):
    m = np.array(Image.open(p))
    if m.ndim == 3: m = m[..., 0]
    assert m.shape == (512, 512), (p, m.shape)
    return m.astype(np.uint8)
def pmd5(x): return hashlib.md5(np.ascontiguousarray(x, dtype=np.uint8).tobytes()).hexdigest()
rows = [l.rstrip('\n').split('\t') for l in open(a.manifest) if l.strip()]
h = rows[0]; rows = [dict(zip(h, r)) for r in rows[1:]]
assert len(rows) == 582 and len({r['stem'] for r in rows}) == 582
bad = [r['stem'] for r in rows if pmd5(rmask(f"{a.labeled}/masks_escdd/{r['stem']}.png")) != r['v1_pixmd5']]
print(f"BASE v1 rebuild vs real masks_escdd: {582 - len(bad)} of 582 cells IDENTICAL, {len(bad)} DIFF {bad[:5]}")
rc = 1 if bad else 0
for opt, col in (('v11', 'v11_pixmd5'), ('strict', 'v11_strict_pixmd5')):
    d = getattr(a, opt)
    if d:
        b = [r['stem'] for r in rows if pmd5(rmask(f"{d}/{r['stem']}.png")) != r[col]]
        print(f"{opt} pngs vs manifest {col}: {582 - len(b)} of 582 IDENTICAL, {len(b)} DIFF {b[:5]}"); rc |= bool(b)
if a.pool:
    pr = [l.rstrip('\n').split('\t') for l in open(a.pool) if l.strip()][1:]
    b = [s for s, _, fm, _ in pr if hashlib.md5(open(f"{a.labeled}/images/{s}.png", 'rb').read()).hexdigest() != fm]
    print(f"pool532 image file md5 vs labeled/images: {len(pr) - len(b)} of {len(pr)} IDENTICAL, {len(b)} DIFF {b[:5]}"); rc |= bool(b)
sys.exit(rc)
