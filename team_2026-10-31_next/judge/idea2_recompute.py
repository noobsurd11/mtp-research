#!/usr/bin/env python3
"""judge recompute for calib idea 2. (a,b) AUROC E1 vs train of content mean / sd from judge's own intensity_stats.tsv
(non-padding px; independent of calib_intensity.py). (d) Spearman of per-cell relR@2 (FINAL +0.75, calib records) with
content mean, E1 crack cells >= 20 px. (e) relF1@2 at each variant's own val-chosen OP-rel (max val relR@2 s.t. relP@2 >= 0.90,
ties smaller b) for FINAL none vs cellz/modz/cellhist on val and F51, and SUPPF5 seed mean. Own code."""
import csv, json, numpy as np
from scipy.stats import spearmanr
J = '/home/yugma/mtp/research/team_2026-10-31_next'
r = list(csv.DictReader(open(f'{J}/judge/out/intensity_stats.tsv'), delimiter='\t'))
def auroc(a, b):
    a, b = np.array(a), np.array(b); return ((a[:, None] > b[None, :]).sum() + 0.5 * (a[:, None] == b[None, :]).sum()) / (len(a) * len(b))
for k in ('mean', 'sd'):
    e = [float(x[k]) for x in r if x['set'] == 'e1']; t = [float(x[k]) for x in r if x['set'] == 'train']
    print(f'(a/b) content {k}: E1 median {np.median(e):.1f} vs train {np.median(t):.1f}; AUROC E1>train {auroc(e, t):.2f}')
mean = {x['stem']: float(x['mean']) for x in r if x['set'] == 'e1'}
d = json.load(open(f'{J}/ideas/calib_out/rec/FINAL.ext.json')); g = np.array(d['grid']); i = int(np.argmin(np.abs(g - 0.75)))
cs = [c for c, v in d['cells'].items() if v['n_gt'] >= 20]
rr = [d['cells'][c]['relr_tp'][i] / d['cells'][c]['n_gt'] for c in cs]
print(f'(d) E1 crack cells n={len(cs)}: Spearman relR@2 vs content mean {spearmanr(rr, [mean[c] for c in cs]).correlation:+.2f}')
F51 = [l.strip() for l in open(f'{J}/ideas/calib_out/F51.txt') if l.strip()]
def curves(d, cells):
    s = lambda k: np.array([d['cells'][c][k] for c in cells], float).sum(0)
    P = s('relp_tp') / np.maximum(s('pred'), 1); R = s('relr_tp') / sum(d['cells'][c]['n_gt'] for c in cells)
    return P, R, np.where(P + R > 0, 2 * P * R / np.maximum(P + R, 1e-9), 0)
def oprel(dv):
    P, R, F = curves(dv, list(dv['cells'])); g = np.array(dv['grid']); ok = np.where((P >= 0.90) & (g <= 12))[0]
    best = R[ok].max(); return int(min(ok[R[ok] == best], key=lambda j: g[j]))
def load(name, s, tt):
    p = f'{J}/ideas/calib_out/rec/{name}.{s}.json' if tt == 'none' else f'{J}/ideas/calib_out/rec_tt/{name.split("_m")[0]}__{tt}{"_m" + name.split("_m")[1] if "_m" in name else ""}.{s}.json'
    return json.load(open(p))
for tt in ('none', 'cellz', 'modz', 'cellhist'):
    out = []
    for name in (['FINAL'], [f'SUPPF5_m{k}' for k in range(5)]):
        vals = []
        for n in name:
            dv, dr = load(n, 'val', tt), load(n, 'rf', tt); i = oprel(dv)
            vals.append((curves(dv, list(dv['cells']))[2][i], curves(dr, F51)[2][i]))
        out.append(np.mean(vals, 0))
    print(f'(e) {tt:8s} FINAL val {out[0][0]:.3f} F51 {out[0][1]:.3f} | SUPPF5 val {out[1][0]:.3f} F51 {out[1][1]:.3f}')
