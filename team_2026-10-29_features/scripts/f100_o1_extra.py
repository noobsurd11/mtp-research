"""protocol_100 opening 1, reported-only extras from the m0 per-cell JSONs (default argmax, final weights):
(1) E1 (ext 106) crack recall / crack IoU / inactive IoU per arm, split scuff_halfcut vs other (scripts/e1_context.tsv col 2);
(2) predicted crack px on crack-free cells (GT crack row sum 0) for test / val / ext, per arm (mean over 5 seeds, sum over cells).
Pooled confusion over the cells of a group, per seed; arm value = mean of 5 seeds (sd shown). Descriptive only."""
import json, sys
import numpy as np

NC, CR, IN = 24, 14, 11
D = sys.argv[1]; CTX = sys.argv[2]
ctx = dict(l.rstrip('\n').split('\t')[:2] for l in open(CTX) if l.strip())
# optional ARM=DIR pairs after the two positional args (opening 2: SUP=<opening1 m0> CP=<opening2 m0>); default: 3 arms in D
PAIRS = dict(x.split('=', 1) for x in sys.argv[3:])
ARMS = list(PAIRS) if PAIRS else ['SUP', 'SUPPF', 'MIMPF']


def load(arm):
    d = PAIRS.get(arm, D)
    return [json.load(open(f'{d}/f3_{arm}_100pct_s{k}.json')) for k in range(5)]


def grp(d, keep, split):
    C = np.zeros((NC, NC))
    for s, c in d['cells'][split].items():
        if keep(s):
            C += np.asarray(c['conf'], float).reshape(NC, NC)
    return C


def m(C):
    tp = np.diag(C); g = C.sum(1); p = C.sum(0)
    iou = lambda k: tp[k] / max(g[k] + p[k] - tp[k], 1) if g[k] > 0 else float('nan')
    return {'cR': tp[CR] / max(g[CR], 1), 'crack': iou(CR), 'inact': iou(IN)}


R = {a: load(a) for a in ARMS}
for a in ARMS:
    assert all(d['step'] == 20000 and d['code_revision'] == 'e544133' for d in R[a]), a
ext = sorted(R[ARMS[0]][0]['cells']['ext'])
assert len(ext) == 106 and set(ext) <= set(ctx)
groups = [('E1 all 106', lambda s: True), ('E1 scuff_halfcut', lambda s: ctx[s] == 'scuff_halfcut'),
          ('E1 other', lambda s: ctx[s] == 'other')]
print('## E1 (ext), mean±sd over 5 seeds: group | n | arm | crack recall | crack IoU | inactive IoU')
for gname, keep in groups:
    n = sum(keep(s) for s in ext)
    for a in ARMS:
        v = [m(grp(d, keep, 'ext')) for d in R[a]]
        print(f'{gname:17s} | {n:3d} | {a:5s} | ' + ' | '.join(
            f"{np.mean([x[k] for x in v]):.3f}±{np.std([x[k] for x in v], ddof=1):.3f}" for k in ['cR', 'crack', 'inact']))
print('\n## predicted crack px on crack-free cells (GT crack 0), sum over cells, mean±sd over 5 seeds; cells with any crack px (mean)')
for split in ['test', 'val', 'ext']:
    for a in ARMS:
        px, nz = [], []
        for d in R[a]:
            cf = [np.asarray(c['conf'], float).reshape(NC, NC) for c in d['cells'][split].values()]
            cf = [C for C in cf if C[CR].sum() == 0]
            px.append(sum(C[:, CR].sum() for C in cf)); nz.append(sum(C[:, CR].sum() > 0 for C in cf))
        print(f'{split:4s} | crack-free cells {len(cf):3d} | {a:5s} | px {np.mean(px):9.1f}±{np.std(px, ddof=1):8.1f} | cells with crack px {np.mean(nz):5.1f}')
