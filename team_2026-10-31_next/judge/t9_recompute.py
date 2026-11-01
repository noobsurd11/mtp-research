"""judge recompute of T9 (run on gaint, CPU, 1 thread). Own code on found's per-cell records.
P = rf_sets F51 & eligible (36). Pixel PR per grid b (pooled tp/pred/n_gt). AP over [0, R_common], R_common = min(max recall
of V, V0) on P; step-wise in order of increasing recall. FA px = predicted crack px on crack-free cells at the family's OP
(FINAL +0.75; SUPPF5 1.4 from t9_result.json), sets H36 (half-cut, crack-free) and P (crack-free)."""
import json, csv, numpy as np, re
T = '/home/noob/work/found/t9'
rows = list(csv.DictReader(open(f'{T}/rf_sets.tsv'), delimiter='\t'))
Pset = [r['stem'] for r in rows if r['set'] == 'F51' and r['eligible'] == '1']
H36 = [r['stem'] for r in rows if r['set'] == 'H36']
mod = {r['stem']: r['module'] for r in rows}
print('P cells', len(Pset), 'modules', len(set(mod[s] for s in Pset)), 'H36', len(H36))
def L(f, v): return json.load(open(f'{T}/rec/{f}__{v}.rf.json'))
def pr(d, cells):
    tp = np.array([d['cells'][c]['tp'] for c in cells], float).sum(0); pred = np.array([d['cells'][c]['pred'] for c in cells], float).sum(0)
    ngt = sum(d['cells'][c]['n_gt'] for c in cells); return tp / np.maximum(pred, 1), tp / max(ngt, 1)
def ap(P, R, cap):
    o = np.argsort(R, kind='stable'); out = prev = 0.0
    for i in o:
        r = min(R[i], cap)
        if r > prev: out += P[i] * (r - prev); prev = r
    return out
for fam, op in (('FINAL', 0.75), ('SUPPF5', 1.4)):
    d0 = L(fam, 'V0'); g = np.array(d0['grid']); io = int(np.argmin(np.abs(g - op)))
    P0, R0 = pr(d0, Pset)
    fa = lambda d, cells: int(sum(d['cells'][c]['pred'][io] for c in cells if d['cells'][c]['n_gt'] == 0))
    for v in ('V2', 'V3'):
        d = L(fam, v); P1, R1 = pr(d, Pset); rc = min(R1.max(), R0.max())
        dAP = ap(P1, R1, rc) - ap(P0, R0, rc)
        # per-module sign on crack modules
        cm = sorted(set(mod[s] for s in Pset if d0['cells'][s]['n_gt'] > 0)); up = 0
        for m in cm:
            cs = [s for s in Pset if mod[s] == m]; a, b = pr(d0, cs), pr(d, cs); r = min(a[1].max(), b[1].max())
            up += ap(*b, r) > ap(*a, r)
        print(f'{fam} {v}: R_common {rc:.2f} dAP(P) {dAP:+.3f} | sign {up}/{len(cm)} | H36 FA px {fa(d0, H36)} -> {fa(d, H36)} | P FA px {fa(d0, Pset)} -> {fa(d, Pset)}')
