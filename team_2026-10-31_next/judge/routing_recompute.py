#!/usr/bin/env python3
"""judge recompute of calib's routing pre-check (SHV1 primary). Own code on calib's records.
Oracle b = argmax pooled relF1@2 (ties smaller b) on grid -4..+12. SUPPF5 pooled = counts summed over m0..m4.
G = F_SHV1(b_SHV1) - F_SHV1(b_V0). G_cf: my own 2 folds over source val cells (seed 0, stratified crack yes/no) - folds differ
from calib's by construction, so agreement in sign/size is the check, not equality."""
import json, numpy as np
C = '/home/yugma/mtp/research/team_2026-10-31_next/ideas/calib_out'
def L(p): return json.load(open(p))
def counts(ds, cells=None):
    out = None
    for d in ds:
        cs = cells if cells is not None else list(d['cells'])
        a = np.array([[d['cells'][c]['pred'], d['cells'][c]['relp_tp'], d['cells'][c]['relr_tp']] for c in cs], float).sum(0)
        ngt = sum(d['cells'][c]['n_gt'] for c in cs)
        out = (a, ngt) if out is None else (out[0] + a, out[1] + ngt)
    return out
def curve(cnt):
    a, ngt = cnt; P = a[1] / np.maximum(a[0], 1); R = a[2] / max(ngt, 1); return P, R, np.where(P + R > 0, 2 * P * R / np.maximum(P + R, 1e-9), 0)
def ob(F, g): 
    m = F.max(); return int(min(np.where(F == m)[0], key=lambda j: g[j]))
for name, v0, sh in (('FINAL', [L(f'{C}/rec/FINAL.val.json')], [L(f'{C}/rec_shv1/FINAL.synval.json')]),
                     ('SUPPF5 pooled', [L(f'{C}/rec/SUPPF5_m{k}.val.json') for k in range(5)], [L(f'{C}/rec_shv1/SUPPF5_m{k}.synval.json') for k in range(5)])):
    g = np.array(v0[0]['grid']); assert g.tolist() == sh[0]['grid']
    _, _, F0 = curve(counts(v0)); P1, R1, F1 = curve(counts(sh)); i0 = ob(F0, g); i1 = ob(F1, g)
    G = F1[i1] - F1[i0]
    P0, R0, _ = curve(counts(v0))
    mp = lambda P, R: R[P >= 0.90].max() if (P >= 0.90).any() else float('nan')
    # cross-fit folds over source cells
    cells = list(sh[0]['cells']); src = sorted(set(c.split('__')[0] for c in cells))
    crack = {s: any(sh[0]['cells'][c]['n_gt'] >= 20 for c in cells if c.startswith(s + '__')) for s in src}
    rng = np.random.default_rng(0); fold = {}
    for grp in (True, False):
        ss = [s for s in src if crack[s] == grp]; rng.shuffle(ss)
        for k, s in enumerate(ss): fold[s] = k % 2
    Gcf = []
    for f in (0, 1):
        A = [c for c in cells if fold[c.split('__')[0]] == f]; B = [c for c in cells if fold[c.split('__')[0]] != f]
        _, _, FA = curve(counts(sh, A)); _, _, FB = curve(counts(sh, B)); iA = ob(FA, g)
        Gcf.append(FB[iA] - FB[i0])
    print(f'{name}: b_V0 {g[i0]:+.1f} b_SHV1 {g[i1]:+.1f} db {g[i1]-g[i0]:+.1f} | G {G:+.3f} | G_cf {np.mean(Gcf):+.3f} (folds {Gcf[0]:+.3f}/{Gcf[1]:+.3f}) | max relR@relP>=0.90 V0 {mp(P0,R0):.3f} SHV1 {mp(P1,R1):.3f}')
