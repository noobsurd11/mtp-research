#!/usr/bin/env python3
"""judge skr2e_check (2 Nov 2026): inputs for the protocol_SKR2E v0.9 review; opened files only, no new read.
 (a) val only (selection set): singles' pooled val curves (rec_w, 5 seeds pooled) for SUPPF and SKR2 on FINAL's D2 grid b 0..3 step 0.25:
     relR@2, relP@2, pixel precision; smallest b with relR >= 0.90 and its pixel-precision drop from b 0 (width flag > 0.05).
 (b) E1 any-hit cluster structure (m0 SUPPF s5 GT comps >= 20 px; GT-only, prediction-independent): comps per source image (71),
     top-3 share, effective n; comps by stratum.
 (c) bias sensitivity of the ensemble readouts already opened in PF2E (E-PF b 0 vs b 1.5) are quoted from verify_pf2e, not recomputed.
Usage: skr2e_check.py RECW_SUPPF RECW_SKR2 M0_SUPPF"""
import json, sys, math
import numpy as np
rB, rS, m0 = sys.argv[1:4]
ctx = {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in open('/home/yugma/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv') if l.strip()}
for name, d, pre in (('SUPPF', rB, 'pf2_SUPPF'), ('SKR2', rS, 'skr2_SKR01')):
    J = [json.load(open(f'{d}/{pre}_100pct_s{k}.val.json')) for k in range(5, 10)]
    G = np.array(J[0]['grid'])
    cs = [c for j in J for c in j['cells'].values()]
    S = lambda k: np.sum([np.asarray(c[k], np.int64) for c in cs], 0)
    pred, tp, rp, rr = S('pred'), S('tp'), S('relp_tp'), S('relr_tp'); ng = sum(c['n_gt'] for c in cs)
    relR, relP, pP = rr / ng, rp / pred, tp / pred
    print(f'## (a) {name} singles, val pooled over 5 seeds (not an ensemble):')
    j0 = int(np.argmin(np.abs(G)))
    for b in np.arange(0, 3.01, 0.25):
        j = int(np.argmin(np.abs(G - b)))
        print(f'   b {G[j]:+.2f}: relR@2 {relR[j]:.4f} relP@2 {relP[j]:.4f} pixel P {pP[j]:.4f} drop {pP[j0] - pP[j]:+.4f}')
    ok = [b for b in np.arange(0, 3.01, 0.25) if relR[int(np.argmin(np.abs(G - b)))] >= 0.90]
    if ok:
        j = int(np.argmin(np.abs(G - ok[0]))); print(f'   smallest D2-grid b with relR >= 0.90: {ok[0]:.2f} (relP {relP[j]:.4f}; drop {pP[j0] - pP[j]:+.4f} -> flag {"TRIPS" if pP[j0] - pP[j] > 0.05 else "ok"})')
    else:
        print('   relR >= 0.90 not reached on 0..3')
cells = json.load(open(f'{m0}/pf2_SUPPF_100pct_s5.json'))['cells']['ext']
img = lambda s: '_'.join(s.split('_')[:2])
cnt = {}; strat = {}
for s, c in cells.items():
    n = sum(1 for g in c['crack_cc']['gt'] if g[0] >= 20)
    cnt[img(s)] = cnt.get(img(s), 0) + n
    k = 'scuff+halfcut' if ctx[s][1] == 'scuff_halfcut' else ('halfcut no-scuff' if ctx[s][3] == 'halfcut=1' else 'full')
    strat[k] = strat.get(k, 0) + n
v = np.array(sorted(cnt.values(), reverse=True)); tot = v.sum(); w = v / tot
print(f'\n## (b) E1 GT crack comps >= 20 px: {tot} in {len(cnt)} images ({(v > 0).sum()} with >= 1); top-3 images {v[:3].tolist()} share {v[:3].sum() / tot:.3f}; '
      f'top-10 share {v[:10].sum() / tot:.3f}; effective n images {1 / np.sum(w ** 2):.1f}; by stratum {strat}')
print('   top images: ' + ', '.join(f'{k} {n}' for k, n in sorted(cnt.items(), key=lambda x: -x[1])[:6]))
