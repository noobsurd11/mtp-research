#!/usr/bin/env python3
"""judge helper (1 Nov): protocol_B6 v0 data audit. Read-only, CPU, local copies of el_f3 data
(train/val lists md5 842f27c4 / 9dcccf00 = splits_benchmark; masks = el_f3 labeled/masks_escdd).
1. B6 module key (source + image id) -> modules, inactive cells / px, top-k concentration.
2. Cross-image near-duplicate scan: same source, same (r, c) position, different image id;
   128-px high-pass correlation (agent 4's 21 Oct screen) + inactive / crack mask IoU.
Usage: python b6_audit.py DATA_DIR OUT_DIR"""
import os, re, sys, itertools, collections
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

D, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
rd = lambda p: [l.strip() for l in open(p) if l.strip()]
split = {s: 'train' for s in rd(f'{D}/train.txt')}
split.update({s: 'val' for s in rd(f'{D}/val.txt')})
test = set(rd(f'{D}/test.txt'))

def key(stem):
    m = re.match(r'^(.*)_r(\d+)_c(\d+)$', stem)
    if m: return m.group(1), (int(m.group(2)), int(m.group(3)))
    m = re.match(r'^(.*?)[_-]cell(\d+)$', stem)
    if m: return m.group(1), None
    return stem, None

rows = []
for s, sp in sorted(split.items()):
    mk = np.array(Image.open(f'{D}/masks_escdd/{s}.png'))
    if mk.ndim == 3: mk = mk[..., 0]
    mod, pos = key(s)
    rows.append(dict(stem=s, split=sp, src=s[:4], module=mod, pos=pos,
                     inact=int((mk == 11).sum()), crack=int((mk == 14).sum()), shape=mk.shape))
with open(f'{OUT}/b6_cells.tsv', 'w') as f:
    f.write('stem\tsplit\tsource\tmodule\tpos\tinactive_px\tcrack_px\n')
    for r in rows: f.write(f"{r['stem']}\t{r['split']}\t{r['src']}\t{r['module']}\t{r['pos']}\t{r['inact']}\t{r['crack']}\n")

print('cells', len(rows), 'shapes', collections.Counter(r['shape'] for r in rows).most_common(3))
mods = collections.defaultdict(list)
for r in rows: mods[r['module']].append(r)
print('B6 modules (source+image id):', len(mods))
print('per source: cells / modules / inactive cells / inactive px / crack cells')
for src in sorted({r['src'] for r in rows}):
    rr = [r for r in rows if r['src'] == src]
    print(f"  {src}: {len(rr)} / {len({r['module'] for r in rr})} / {sum(r['inact']>0 for r in rr)} / "
          f"{sum(r['inact'] for r in rr)} / {sum(r['crack']>0 for r in rr)}")
inr = sorted([r for r in rows if r['inact'] > 0], key=lambda r: -r['inact'])
tot = sum(r['inact'] for r in inr)
print(f'inactive cells {len(inr)} (train {sum(r["split"]=="train" for r in inr)}, val {sum(r["split"]=="val" for r in inr)}); px {tot}')
for k in (1, 3, 5, 10):
    print(f'  top-{k} share {sum(r["inact"] for r in inr[:k]) / tot:.3f}')
im_mods = collections.Counter(r['module'] for r in inr)
print('inactive modules', len(im_mods), '; modules with >=2 inactive cells', sum(v >= 2 for v in im_mods.values()))
mpx = collections.Counter()
for r in inr: mpx[r['module']] += r['inact']
print('  module top-3 share', round(sum(v for _, v in mpx.most_common(3)) / tot, 3), mpx.most_common(5))
print('  small inactive cells (<500 px):', sum(r['inact'] < 500 for r in inr))
print('top 12 inactive cells:')
for r in inr[:12]: print(f"  {r['stem']} {r['split']} {r['inact']}")

# 2. near-duplicate scan, same source and position, different image id
def hp(stem):
    a = np.asarray(Image.open(f'{D}/images/{stem}.png').convert('L'), dtype=np.float32)
    a = np.asarray(Image.fromarray(a).resize((128, 128), Image.BILINEAR), dtype=np.float32)
    h = a - ndi.gaussian_filter(a, 4)
    h = (h - h.mean()) / (h.std() + 1e-6)
    return h.ravel()
bypos = collections.defaultdict(list)
for r in rows:
    if r['pos'] is not None: bypos[(r['src'], r['pos'])].append(r)
cache, pairs = {}, []
for k, rr in bypos.items():
    for a, b in itertools.combinations(rr, 2):
        if a['module'] == b['module']: continue
        for x in (a, b):
            if x['stem'] not in cache: cache[x['stem']] = hp(x['stem'])
        c = float(np.dot(cache[a['stem']], cache[b['stem']]) / cache[a['stem']].size)
        pairs.append((c, a, b))
# also BMRK / SDLE (no position): all pairs within source
for src in ('BMRK', 'SDLE'):
    rr = [r for r in rows if r['src'] == src]
    for a, b in itertools.combinations(rr, 2):
        for x in (a, b):
            if x['stem'] not in cache: cache[x['stem']] = hp(x['stem'])
        c = float(np.dot(cache[a['stem']], cache[b['stem']]) / cache[a['stem']].size)
        pairs.append((c, a, b))
pairs.sort(key=lambda t: -t[0])

def miou(a, b, cls):
    ma = np.array(Image.open(f'{D}/masks_escdd/{a}.png')); mb = np.array(Image.open(f'{D}/masks_escdd/{b}.png'))
    if ma.ndim == 3: ma, mb = ma[..., 0], mb[..., 0]
    if ma.shape != mb.shape: return float('nan')
    A, B = ma == cls, mb == cls
    u = (A | B).sum()
    return float((A & B).sum() / u) if u else float('nan')
with open(f'{OUT}/b6_neardup.tsv', 'w') as f:
    f.write('hp_r\ta\ta_split\tb\tb_split\tinact_a\tinact_b\tinact_iou\tcrack_a\tcrack_b\tcrack_iou\n')
    for c, a, b in pairs:
        if c < 0.5: break
        f.write(f"{c:.3f}\t{a['stem']}\t{a['split']}\t{b['stem']}\t{b['split']}\t{a['inact']}\t{b['inact']}\t"
                f"{miou(a['stem'], b['stem'], 11):.3f}\t{a['crack']}\t{b['crack']}\t{miou(a['stem'], b['stem'], 14):.3f}\n")
print('pairs scanned', len(pairs), '; hp_r>=0.8:', sum(c >= 0.8 for c, _, _ in pairs), '; >=0.7:', sum(c >= 0.7 for c, _, _ in pairs))
