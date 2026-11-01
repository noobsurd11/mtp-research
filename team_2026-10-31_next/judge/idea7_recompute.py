#!/usr/bin/env python3
"""judge recompute for calib idea 7 backfill: per-run val OP b_rel (max val relR@2 s.t. relP@2 >= 0.90, ties -> smaller b,
OP grid -4..+8), E1 / sh29 relR@2 at that b; cell recall / FA at b 0 (positive >= 20 GT px, flag >= 20 pred px); cell AUROC on s20.
Own code on calib's records. Descriptive."""
import json, numpy as np
R = '/home/yugma/mtp/research/team_2026-10-31_next/ideas/calib_out/rec'
ctx = {l.split('\t')[0]: l.strip().split('\t')[1] for l in open('/home/yugma/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv')}
def L(t, s): return json.load(open(f'{R}/{t}.{s}.json'))
def pooled(d, cells, k): return np.array([d['cells'][c][k] for c in cells], float).sum(0)
def auroc(pos, neg):
    pos, neg = np.array(pos), np.array(neg); return ((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg))
for arm in ('SUP5', 'SUPPF5'):
    rows = []
    for m in range(5):
        v, e = L(f'{arm}_m{m}', 'val'), L(f'{arm}_m{m}', 'ext'); g = np.array(v['grid'])
        vc = list(v['cells']); P = pooled(v, vc, 'relp_tp') / np.maximum(pooled(v, vc, 'pred'), 1); Rr = pooled(v, vc, 'relr_tp') / sum(v['cells'][c]['n_gt'] for c in vc)
        ok = (P >= 0.90) & (g <= 8.0) & (g >= -4.0)
        idx = np.where(ok)[0]; best = idx[np.argmax(Rr[idx])] if len(idx) else int(np.argmax(P))
        cand = idx[Rr[idx] == Rr[best]] if len(idx) else [best]; i = int(min(cand, key=lambda j: g[j]))
        ec = list(e['cells']); sh = [c for c in ec if ctx[c] == 'scuff_halfcut']
        rE = pooled(e, ec, 'relr_tp')[i] / sum(e['cells'][c]['n_gt'] for c in ec); rS = pooled(e, sh, 'relr_tp')[i] / sum(e['cells'][c]['n_gt'] for c in sh)
        i0 = int(np.argmin(np.abs(g)))
        pos = [c for c in vc if v['cells'][c]['n_gt'] >= 20]; neg = [c for c in vc if v['cells'][c]['n_gt'] == 0]
        cR = np.mean([v['cells'][c]['pred'][i0] >= 20 for c in pos]); cFA = np.mean([v['cells'][c]['pred'][i0] >= 20 for c in neg])
        au = auroc([v['cells'][c]['s']['20'] for c in pos], [v['cells'][c]['s']['20'] for c in neg])
        epos = [c for c in ec if e['cells'][c]['n_gt'] >= 20]; eneg = [c for c in ec if e['cells'][c]['n_gt'] == 0]
        eFA = np.mean([e['cells'][c]['pred'][i0] >= 20 for c in eneg])
        rows.append((g[i], Rr[i], rE, rS, cR, cFA, au, eFA))
    a = np.array(rows)
    print(f'{arm}: b_rel ' + '/'.join(f'{x:.1f}' for x in a[:, 0]) + f' | val relR@OPr {a[:,1].mean():.3f} ({a[:,1].std(ddof=1):.3f}) | E1 relR@OPr {a[:,2].mean():.3f} | sh29 {a[:,3].mean():.3f} | val cellR b0 {a[:,4].mean():.3f} FA {a[:,5].mean():.3f} AUROC {a[:,6].mean():.3f} | E1 cellFA b0 {a[:,7].mean():.3f}')
