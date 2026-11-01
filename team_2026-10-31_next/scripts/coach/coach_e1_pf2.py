"""coach (1 Nov): independent E1 co-primary + width-robust recompute for protocol_PF2 (own code; not runner's pf2_e1_extra / pf2_e1_width).
Input: m0 per-cell JSONs (cells['ext'][stem] = {'conf': 24x24 gt-rows / pred-cols, 'crack_rel2': [tpP, nP, tpR, nR], 'crack_cc': {'gt': [[size, hits]], 'pr': [[size, hits]]}}).
Usage: python coach_e1_pf2.py M0DIR E1CTX.tsv  (runs pf2_{SUP,SUPPF,RN50PF}_100pct_s5..9)
Prints per arm mean±sd and rule 1 (/3) for SUPPF-SUP (PF2) and RN50PF-SUPPF (RN): E1 crack recall, inactive IoU (co-primaries, PF2),
crack precision (flag if PF2 recall BETTER and precision drop > 0.05), crack IoU, relR@2, relP@2, relF1@2, comp recall (GT comps >= 20 px with
>= 50% px within 2 px of a prediction), comp precision (pred comps >= 20 px with >= 1 px within 2 px of GT); strata 29/77 and 58/48."""
import json, sys, os
import numpy as np
NC, CR, IN = 24, 14, 11
D, CTX = sys.argv[1], sys.argv[2]
ctx = {}
for l in open(CTX):
    f = l.rstrip('\n').split('\t')
    if len(f) >= 4:
        ctx[f[0]] = (f[2] == 'scuff=1', f[3] == 'halfcut=1')

def load(arm):
    out = []
    for k in range(5, 10):
        p = f'{D}/pf2_{arm}_100pct_s{k}.json'
        if not os.path.exists(p):
            return None
        d = json.load(open(p)); assert d['step'] == 20000, (p, d['step']); out.append(d)
    return out

def agg(d, keep):
    C = np.zeros((NC, NC)); x = np.zeros(4); gt = [0, 0]; pr = [0, 0]
    cells = d['cells']['ext']; assert len(cells) == 106
    for s, c in cells.items():
        if not keep(s):
            continue
        C += np.asarray(c['conf'], float).reshape(NC, NC); x += np.asarray(c['crack_rel2'], float)
        for sz, h in c['crack_cc']['gt']:
            if sz >= 20:
                gt[0] += 1; gt[1] += int(h >= 0.5 * sz)
        for sz, h in c['crack_cc']['pr']:
            if sz >= 20:
                pr[0] += 1; pr[1] += int(h >= 1)
    tp = np.diag(C); g = C.sum(1); p = C.sum(0)
    rp = x[0] / max(x[1], 1); rr = x[2] / max(x[3], 1)
    return {'cR': tp[CR] / max(g[CR], 1), 'cP': tp[CR] / max(p[CR], 1), 'crack': tp[CR] / max(g[CR] + p[CR] - tp[CR], 1),
            'inact': tp[IN] / max(g[IN] + p[IN] - tp[IN], 1), 'relR': rr, 'relP': rp, 'relF1': 2 * rp * rr / max(rp + rr, 1e-12),
            'compR': gt[1] / max(gt[0], 1), 'compP': pr[1] / max(pr[0], 1)}

def rule1(a, b):
    sd = lambda v: np.std(v, ddof=1)
    thr = max(0.01, 2 * np.sqrt((sd(a) ** 2 + sd(b) ** 2) / 3)); dl = np.mean(b) - np.mean(a)
    return dl, thr, ('BETTER' if dl > thr else 'WORSE' if dl < -thr else 'nd')

R = {a: load(a) for a in ['SUP', 'SUPPF', 'RN50PF']}
groups = [('E1 all 106', lambda s: True), ('scuff+halfcut 29', lambda s: ctx[s][0] and ctx[s][1]),
          ('other 77', lambda s: not (ctx[s][0] and ctx[s][1])), ('half-cut 58', lambda s: ctx[s][1]), ('full 48', lambda s: not ctx[s][1])]
KEYS = ['cR', 'inact', 'cP', 'crack', 'relR', 'relP', 'relF1', 'compR', 'compP']
for gname, keep in groups:
    print(f'## {gname}')
    vals = {a: ([agg(d, keep) for d in R[a]] if R[a] else None) for a in R}
    for a in R:
        if vals[a]:
            print(f'  {a:7s} ' + ' | '.join(f'{k} {np.mean([m[k] for m in vals[a]]):.4f}±{np.std([m[k] for m in vals[a]], ddof=1):.4f}' for k in KEYS))
    for name, A, B in [('PF2 SUPPF-SUP', 'SUP', 'SUPPF'), ('RN RN50PF-SUPPF', 'SUPPF', 'RN50PF')]:
        if vals[A] and vals[B]:
            print(f'  {name:16s} ' + ' | '.join('%s %+.4f(%.4f) %s' % ((k,) + rule1([m[k] for m in vals[A]], [m[k] for m in vals[B]])) for k in KEYS))
    if gname == 'E1 all 106' and vals['SUP'] and vals['SUPPF']:
        print('  per-seed PF2 co-primaries:')
        for a in ['SUP', 'SUPPF']:
            print(f'    {a:6s} cR ' + ' '.join(f'{m["cR"]:.4f}' for m in vals[a]) + ' | inact ' + ' '.join(f'{m["inact"]:.4f}' for m in vals[a]))
        dR = rule1([m['cR'] for m in vals['SUP']], [m['cR'] for m in vals['SUPPF']])
        dI = rule1([m['inact'] for m in vals['SUP']], [m['inact'] for m in vals['SUPPF']])
        dP = np.mean([m['cP'] for m in vals['SUPPF']]) - np.mean([m['cP'] for m in vals['SUP']])
        print(f'  PF2 E1 co-primaries: crack recall {dR[0]:+.4f} ({dR[1]:.4f}) {dR[2]} | inactive IoU {dI[0]:+.4f} ({dI[1]:.4f}) {dI[2]}'
              f' | precision flag: {"FLAG" if dR[2] == "BETTER" and dP < -0.05 else "ok"} (crack P {dP:+.4f})')
