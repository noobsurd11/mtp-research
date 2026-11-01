"""PF2 successor of team_2026-10-29_features/scripts/f100_o1_extra.py (md5 45b03c2f). With no environment variables set the
output is byte-identical to the original (checked on protocol_100 opening 1, o1_extra.txt). Environment:
  PREFIX (default f3), SEEDS (default "0 1 2 3 4"): run files {PREFIX}_{ARM}_100pct_s{K}.json;
  EXTRA=1: after the original output, (3) E1 crack precision and the E1 strata of protocol_PF2.md section 4.4 (58 half-cut vs
  48 full, 29 scuff+half-cut vs 77 other), and (4) the per-seed values of the PF2 E1 co-primaries (E1 crack recall, E1 inactive
  IoU, all 106 cells pooled per run) with rule 1 (/3) for given contrasts CONTRASTS="B-A ..." (default "SUPPF-SUP RN50PF-SUPPF").
Original docstring follows.
protocol_100 opening 1, reported-only extras from the m0 per-cell JSONs (default argmax, final weights):
(1) E1 (ext 106) crack recall / crack IoU / inactive IoU per arm, split scuff_halfcut vs other (scripts/e1_context.tsv col 2);
(2) predicted crack px on crack-free cells (GT crack row sum 0) for test / val / ext, per arm (mean over 5 seeds, sum over cells).
Pooled confusion over the cells of a group, per seed; arm value = mean of 5 seeds (sd shown). Descriptive only."""
import json, os, sys
import numpy as np

NC, CR, IN = 24, 14, 11
D = sys.argv[1]; CTX = sys.argv[2]
ctx = dict(l.rstrip('\n').split('\t')[:2] for l in open(CTX) if l.strip())
# optional ARM=DIR pairs after the two positional args (opening 2: SUP=<opening1 m0> CP=<opening2 m0>); default: 3 arms in D
PAIRS = dict(x.split('=', 1) for x in sys.argv[3:])
ARMS = list(PAIRS) if PAIRS else ['SUP', 'SUPPF', 'MIMPF']


PREFIX = os.environ.get('PREFIX', 'f3'); SEEDS = [int(k) for k in os.environ.get('SEEDS', '0 1 2 3 4').split()]


def load(arm):
    d = PAIRS.get(arm, D)
    return [json.load(open(f'{d}/{PREFIX}_{arm}_100pct_s{k}.json')) for k in SEEDS]


def grp(d, keep, split):
    C = np.zeros((NC, NC))
    for s, c in d['cells'][split].items():
        if keep(s):
            C += np.asarray(c['conf'], float).reshape(NC, NC)
    return C


def m(C):
    tp = np.diag(C); g = C.sum(1); p = C.sum(0)
    iou = lambda k: tp[k] / max(g[k] + p[k] - tp[k], 1) if g[k] > 0 else float('nan')
    return {'cR': tp[CR] / max(g[CR], 1), 'crack': iou(CR), 'inact': iou(IN), 'cP': tp[CR] / max(p[CR], 1)}


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

if os.environ.get('EXTRA') == '1':
    ctx4 = {l.split('\t')[0]: dict(x.split('=') for x in l.rstrip('\n').split('\t')[2:4]) for l in open(CTX) if l.strip()}
    g2 = [('E1 all 106', lambda s: True), ('E1 half-cut', lambda s: ctx4[s]['halfcut'] == '1'),
          ('E1 full', lambda s: ctx4[s]['halfcut'] == '0'), ('E1 scuff_halfcut', lambda s: ctx[s] == 'scuff_halfcut'),
          ('E1 other', lambda s: ctx[s] == 'other')]
    print(f'\n## (3) E1 strata, mean±sd over {len(SEEDS)} seeds (reported, not tested): group | n | arm | crack recall | crack precision | crack IoU | inactive IoU')
    for gname, keep in g2:
        n = sum(keep(s) for s in ext)
        for a in ARMS:
            v = [m(grp(d, keep, 'ext')) for d in R[a]]
            print(f'{gname:17s} | {n:3d} | {a:6s} | ' + ' | '.join(
                f"{np.mean([x[k] for x in v]):.4f}±{np.std([x[k] for x in v], ddof=1):.4f}" for k in ['cR', 'cP', 'crack', 'inact']))
    print(f'\n## (4) E1 co-primaries per seed (all 106 cells pooled per run; seeds {SEEDS}) and rule 1 (/3)')
    per = {a: [m(grp(d, lambda s: True, 'ext')) for d in R[a]] for a in ARMS}
    for a in ARMS:
        print(f"{a:6s} crack recall " + ' '.join(f"{x['cR']:.4f}" for x in per[a]) + " | inactive IoU " + ' '.join(f"{x['inact']:.4f}" for x in per[a])
              + " | crack precision " + ' '.join(f"{x['cP']:.4f}" for x in per[a]))
    for c in os.environ.get('CONTRASTS', 'SUPPF-SUP RN50PF-SUPPF').split():
        b, a = c.split('-')
        if a not in per or b not in per:
            continue
        for k, lab in [('cR', 'E1 crack recall'), ('inact', 'E1 inactive IoU'), ('cP', 'E1 crack precision (flag only)')]:
            xa = np.array([x[k] for x in per[a]]); xb = np.array([x[k] for x in per[b]])
            dlt = xb.mean() - xa.mean(); thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
            v = 'BETTER' if dlt > thr else ('WORSE' if dlt < -thr else 'n.d.')
            print(f'{b} - {a} | {lab:31s} | {b} {xb.mean():.4f}±{xb.std(ddof=1):.4f} | {a} {xa.mean():.4f}±{xa.std(ddof=1):.4f} | delta {dlt:+.4f} | thr {thr:.4f} | {v}')
