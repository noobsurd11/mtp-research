#!/usr/bin/env python3
"""judge recompute for calib idea 1, from calib's per-cell records (calib_out/rec/*.json), own aggregation code.
relP@2 = sum relp_tp / sum pred; relR@2 = sum relr_tp / sum n_gt; relF1 = harmonic mean. Pooled over the cells of a set.
Seed arms (X_m0..m4): per-seed metric, then mean. E1 rows descriptive only."""
import json, re, numpy as np, sys
R = '/home/yugma/mtp/research/team_2026-10-31_next/ideas/calib_out/rec'
ctx = {l.split('\t')[0]: l.strip().split('\t')[1] for l in open('/home/yugma/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv')}
F51 = [l.strip() for l in open('/home/yugma/mtp/research/team_2026-10-31_next/ideas/calib_out/F51.txt') if l.strip()]
def load(t, s): return json.load(open(f'{R}/{t}.{s}.json'))
def arr(d, cells, k): return np.array([d['cells'][c][k] for c in cells], float)
def curves(d, cells):
    pred = arr(d, cells, 'pred').sum(0); rp = arr(d, cells, 'relp_tp').sum(0); rr = arr(d, cells, 'relr_tp').sum(0)
    ngt = sum(d['cells'][c]['n_gt'] for c in cells)
    P = np.where(pred > 0, rp / np.maximum(pred, 1), np.nan); Rr = rr / max(ngt, 1)
    F = np.where((P + Rr) > 0, 2 * P * Rr / (P + Rr), 0)
    return P, Rr, np.nan_to_num(F)
def module(s):
    s = re.sub(r'_rf$', '', s); m = re.match(r'^(.*)_r\d+_c\d+$', s); return m.group(1) if m else s
fin = {s: load('FINAL', s) for s in ('val', 'ext', 'rf')}
g = np.array(fin['val']['grid']); i075 = int(np.argmin(np.abs(g - 0.75))); i0 = int(np.argmin(np.abs(g)))
E = list(fin['ext']['cells']); sh = [c for c in E if ctx[c] == 'scuff_halfcut']; ot = [c for c in E if ctx[c] != 'scuff_halfcut']
sets = {'val': (fin['val'], list(fin['val']['cells'])), 'E1': (fin['ext'], E), 'other77': (fin['ext'], ot), 'sh29': (fin['ext'], sh), 'F51': (fin['rf'], F51)}
print('FINAL matched precision: max relR@2 s.t. relP@2 >= x')
for name, (d, cells) in sets.items():
    P, Rr, F = curves(d, cells)
    row = []
    for x in (0.9, 0.8, 0.7, 0.6):
        ok = P >= x; row.append(f'{Rr[ok].max():.3f}' if ok.any() else 'n/r')
    print(f'  {name:8s} n={len(cells):3d}  ' + '  '.join(row) + f'   relF1 dep(+0.75) {F[i075]:.3f} oracle {F.max():.3f} at b {g[F.argmax()]:+.1f}')
# 2-stratum oracle on E1 (FINAL): one b for sh29, one for other77, pooled relF1
d = fin['ext']
def pooled_at(bidx_by_cell, cells):
    pred = sum(d['cells'][c]['pred'][bidx_by_cell[c]] for c in cells); rp = sum(d['cells'][c]['relp_tp'][bidx_by_cell[c]] for c in cells)
    rr = sum(d['cells'][c]['relr_tp'][bidx_by_cell[c]] for c in cells); ngt = sum(d['cells'][c]['n_gt'] for c in cells)
    P = rp / max(pred, 1); Rr = rr / max(ngt, 1); return 2 * P * Rr / max(P + Rr, 1e-9)
SH = arr(d, sh, 'pred').sum(0), arr(d, sh, 'relp_tp').sum(0), arr(d, sh, 'relr_tp').sum(0)
OT = arr(d, ot, 'pred').sum(0), arr(d, ot, 'relp_tp').sum(0), arr(d, ot, 'relr_tp').sum(0)
ngt = sum(d['cells'][c]['n_gt'] for c in E)
best = (0, None)
for i in range(len(g)):
    pred = SH[0][i] + OT[0]; rp = SH[1][i] + OT[1]; rr = SH[2][i] + OT[2]
    P = rp / np.maximum(pred, 1); Rr = rr / ngt; F = 2 * P * Rr / np.maximum(P + Rr, 1e-9)
    j = int(F.argmax())
    if F[j] > best[0]: best = (F[j], (g[i], g[j]))
print(f'FINAL E1 2-stratum oracle (b_sh29, b_other77) = {best[1]}: pooled relF1 {best[0]:.3f}')
# seed arms: dep (b 0) and global oracle on E1, sh29
for arm in ('SUPPF5', 'SUP5'):
    out = {k: [] for k in ('E1dep', 'E1orc', 'shdep', 'shorc', 'valdep')}
    for m in range(5):
        dv = load(f'{arm}_m{m}', 'ext'); vv = load(f'{arm}_m{m}', 'val')
        _, _, F = curves(dv, E); out['E1dep'].append(F[i0]); out['E1orc'].append(F.max())
        _, _, F = curves(dv, sh); out['shdep'].append(F[i0]); out['shorc'].append(F.max())
        _, _, F = curves(vv, list(vv['cells'])); out['valdep'].append(F[i0])
    print(f'{arm}: ' + ' '.join(f'{k} {np.mean(v):.3f}' for k, v in out.items()))
# A0 and A1 on F51 (FINAL): A0 = max val relR s.t. val relP >= 0.90; A1 = per module, smallest b whose predicted-crack area fraction >= val's at A0
Pv, Rv, Fv = curves(fin['val'], list(fin['val']['cells']))
ok = Pv >= 0.90; iA0 = int(np.where(ok)[0][np.argmax(Rv[ok])]) if ok.any() else int(np.argmax(Pv))
vcells = list(fin['val']['cells'])
vfrac = arr(fin['val'], vcells, 'pred').sum(0)[iA0] / sum(fin['val']['cells'][c]['area'] for c in vcells)
dr = fin['rf']; mods = {}
for c in F51: mods.setdefault(module(c), []).append(c)
bidx = {}
for mname, cs in mods.items():
    pr = arr(dr, cs, 'pred').sum(0); ar = sum(dr['cells'][c]['area'] for c in cs); fr = pr / ar
    idx = np.where(fr >= vfrac)[0]; k = int(idx[0]) if len(idx) else len(g) - 1
    for c in cs: bidx[c] = k
def fa(dd, cells, bi):
    cf = [c for c in cells if dd['cells'][c]['n_gt'] == 0]
    return np.mean([dd['cells'][c]['pred'][bi[c]] >= 20 for c in cf]), len(cf)
A0idx = {c: iA0 for c in F51}
d = dr
print(f'FINAL A0 b={g[iA0]:+.2f} (val frac {vfrac:.5f}); F51 relF1 A0 {pooled_at(A0idx, F51):.3f} FA {fa(dr, F51, A0idx)[0]:.3f} | A1 {pooled_at(bidx, F51):.3f} FA {fa(dr, F51, bidx)[0]:.3f} (crack-free cells {fa(dr, F51, bidx)[1]})')
# deployable routing split: half-cut (58) vs full (48), cell type only (no scuff info); FINAL and seed arms
ctx3 = {l.split('\t')[0]: l.strip().split('\t')[3] for l in open('/home/yugma/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv')}
def two_stratum(d, A, B):
    a = [arr(d, A, k).sum(0) for k in ('pred', 'relp_tp', 'relr_tp')]; b = [arr(d, B, k).sum(0) for k in ('pred', 'relp_tp', 'relr_tp')]
    ngt = sum(d['cells'][c]['n_gt'] for c in A + B); best = (0, None)
    for i in range(len(g)):
        P = (a[1][i] + b[1]) / np.maximum(a[0][i] + b[0], 1); Rr = (a[2][i] + b[2]) / ngt; F = 2 * P * Rr / np.maximum(P + Rr, 1e-9)
        j = int(F.argmax())
        if F[j] > best[0]: best = (F[j], (round(float(g[i]), 1), round(float(g[j]), 1)))
    return best
HC = [c for c in E if ctx3[c] == 'halfcut=1']; FU = [c for c in E if ctx3[c] == 'halfcut=0']
print('FINAL E1 2-stratum oracle, half-cut vs full (b_hc, b_full):', two_stratum(fin['ext'], HC, FU))
for arm in ('SUPPF5', 'SUP5'):
    v = [two_stratum(load(f'{arm}_m{m}', 'ext'), HC, FU)[0] for m in range(5)]
    print(f'{arm} E1 2-stratum (hc/full) oracle relF1 mean {np.mean(v):.3f}')
