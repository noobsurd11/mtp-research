# Our training masks (masks_escdd copy) vs E-SCDD; pool pixel check; candidate enlarged test sets; mirror extras; colour check.
import os, sys, json, numpy as np, collections as C
from PIL import Image
ESC, MIR, OURS_ESCDD, POOL_IMGS, SPL, OUTD = sys.argv[1:7]
X = json.load(open(os.path.join(OUTD, 'out', 'xref.json'))); inv = {r['file']: r for r in json.load(open(os.path.join(OUTD, 'out', 'inv_escdd.json')))}
ours = {l.strip(): s for s in ('train', 'val', 'test') for l in open(os.path.join(SPL, f'{s}.txt'))}
L = lambda p: np.array(Image.open(p))
res = {}
# 9. masks_escdd vs escdd
byst = {x['stem']: x for x in X if x['kind'] == 'real' and x.get('r1104')}
T = C.Counter(); same = 0; px = C.defaultdict(lambda: [0, 0, 0, 0]); only_remap = []
for st, s in ours.items():
    me = L(os.path.join(OURS_ESCDD, st + '.png'))
    if st not in byst: continue
    mE = L(os.path.join(ESC, f"el_masks_{byst[st]['split']}", st + '.png'))
    a = px[s]; a[0] += int((me == 14).sum()); a[1] += int((mE == 14).sum()); a[2] += int((me == 11).sum()); a[3] += int((mE == 11).sum())
    if (me == 14).any() != (mE == 14).any(): only_remap.append((s, st, int((me == 14).sum())))
    if (me == mE).all(): same += 1; continue
    d = me != mE; pr, n = np.unique(np.stack([mE[d], me[d]], 1), axis=0, return_counts=True)
    for p, k in zip(pr, n): T[f'{p[0]}->{p[1]}'] += int(k)
res['masks_escdd'] = dict(same=same, n=len(byst), trans=dict(T), px=dict(px), crack_only_via_remap=only_remap,
    crack_cells={s: sum(int((L(os.path.join(OURS_ESCDD, st + '.png')) == 14).any()) for st, ss in ours.items() if ss == s) for s in ('train', 'val', 'test')})
# 8. pool pixel check
pc = []
for x in X:
    if x['kind'] != 'real_rf' or not x['in_pool']: continue
    a = np.asarray(Image.open(os.path.join(ESC, f"el_images_{x['split']}", x['stem'] + '_rf.png')).convert('L'), np.float32)
    b = np.asarray(Image.open(os.path.join(POOL_IMGS, x['stem'] + '.png')).convert('L'), np.float32)
    best = max(((float(np.corrcoef(a.ravel(), (np.rot90(b, k)[:, ::-1] if fl else np.rot90(b, k)).ravel())[0, 1]), k, fl) for k in range(4) for fl in (0, 1)))
    pc.append(dict(stem=x['stem'], r=best[0], rot=best[1], flip=best[2], mad=float(np.abs(a - (np.rot90(b, best[1])[:, ::-1] if best[2] else np.rot90(b, best[1]))).mean())))
res['pool_check'] = dict(n=len(pc), r_min=min(p['r'] for p in pc), hist=np.histogram([p['r'] for p in pc], [-1, 0.95, 0.99, 0.999, 1.01])[0].tolist(), transforms=C.Counter((p['rot'], p['flip']) for p in pc).most_common())
# 8. candidate enlarged test sets
test_cells = [(int((m == 11).sum()), int((m == 14).sum())) for m in (L(os.path.join(OURS_ESCDD, st + '.png')) for st, s in ours.items() if s == 'test')]
G = C.defaultdict(list)
for x in X:
    if x['kind'] == 'synthetic' or x.get('r1104'): continue
    g = 'E1' if x['in_ext117'] and not x['in_pool'] else ('rfnp' if not x['in_pool'] else 'pool')
    G[g].append((inv[x['file']]['counts'][11], inv[x['file']]['counts'][14]))
def rep(cells):
    i = sorted([c[0] for c in cells if c[0]], reverse=True); k = sorted([c[1] for c in cells if c[1]], reverse=True)
    return dict(cells=len(cells), inactive_cells=len(i), inactive_px=sum(i), inactive_top3=round(sum(i[:3]) / sum(i), 3), crack_cells=len(k), crack_px=sum(k), crack_top3=round(sum(k[:3]) / sum(k), 3))
res['enlarged_test'] = {'ours': rep(test_cells), 'A': rep(test_cells + G['E1'] + G['rfnp']), 'B': rep(test_cells + G['E1'] + G['rfnp'] + G['pool'])}
# mirror extras: masks in removed_padding still containing padding
mp = {}
for s in ('train', 'val', 'test'):
    d = os.path.join(MIR, f'el_masks_{s}', 'removed_padding'); fs = [f for f in os.listdir(d) if f.endswith('.png')]
    mp[s] = [len(fs), sum(int((L(os.path.join(d, f)) == 7).any()) for f in fs)]
res['mirror_masks_with_padding'] = mp
# colour: max channel spread over non-grey images
cs = [r['rgb_maxdiff'] for r in inv.values() if (r['rgb_maxdiff'] or 0) > 0]
res['non_grey'] = dict(n=len(cs), max_spread=max(cs), median=float(np.median(cs)))
json.dump(res, open(os.path.join(OUTD, 'out', 'ours_vs_escdd.json'), 'w'), default=str)
print(json.dumps({k: v for k, v in res.items()}, default=str)[:3000])
