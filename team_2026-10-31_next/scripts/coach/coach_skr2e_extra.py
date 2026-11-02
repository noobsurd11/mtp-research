"""coach (2 Nov): SKR2E reported readouts (protocol_SKR2E §4; never change the verdict). Own code on the per-cell JSONs, reusing
only coach_skr2e.py's feats / metr / boot. Descriptive E1 reads inside opening #6.
- val: the decisions-file sweep at b in U re-summed from the val cells of the b-files;
- pairs: (1, 1) = E-PF at E-SKR2's headline b; (1.5, 1) = each D2 b; (1.5, 1.5); point estimates + own CIs;
- width: pred / GT crack px, pixel P / R, relP / relR on test and E1; crack-free px on test / E1 / val, per arm per b;
- any-hit: per stratum (scuff + half-cut 29 / half-cut no scuff 29 / full 48 / other 77), per image (top 3 / top 10 by GT comps),
  where the extra hits sit; leave-top-3-images-out and leave-one-cluster-out for E1 relF1@2 and any-hit (b 0 pair);
- matched volume: E-PF on the E1 aggregate sweep at E-SKR2 b 0's pred / GT (linear in b), E1-oracle, chooses nothing;
- E1 inactive: GT px by image, leave-top-3-out delta.
Usage: python coach_skr2e_extra.py OUT_DIR E1_CONTEXT_TSV"""
import json, sys
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from coach_skr2e import feats, metr, boot, key, NC, CR, IN, NOISY, NAMES

D = Path(sys.argv[1]); CX = {l.split('\t')[0]: l.rstrip('\n').split('\t')[1:] for l in open(sys.argv[2])}
U = [0.0, 1.0, 1.5]; A = ('E-PF', 'E-SKR2')
J = {(k, b): json.load(open(D / f'{k}.b{b:g}.json'))['cells'] for k in A for b in U}
dec = json.load(open(D / 'skr2e_val_decisions.json')); sw = json.load(open(D / 'skr2e_e1_sweep.json'))
pr = print


def px(cells, stems):
    C = sum(np.asarray(cells[s]['conf'], np.int64).reshape(NC, NC) for s in stems)
    return int(C[CR].sum()), int(C[:, CR].sum()), int(C[CR, CR])


def cfree(cells):
    n = p = 0
    for c in cells.values():
        M = np.asarray(c['conf'], np.int64).reshape(NC, NC)
        if M[CR].sum() == 0: n += 1; p += int(M[:, CR].sum())
    return n, p


def hits(cells, stems):
    h = n = 0
    for s in stems:
        for g in cells[s]['crack_cc']['gt']:
            if g[0] >= 20: n += 1; h += g[1] >= 1
    return h, n


pr('## val sweep entries at b in U, re-summed from the b-files val cells (crack IoU / crack P / relP@2 / relR@2 / relF1@2 / inactive)')
for k in A:
    for b in U:
        st = sorted(J[(k, b)]['val']); C, R, H = feats(J[(k, b)]['val'], st); m = metr(C.sum(0), R.sum(0), H.sum(0))
        g, p, tp = px(J[(k, b)]['val'], st); rr = R.sum(0)[2] / R.sum(0)[3]
        mine = [m[0], tp / p, m[4], rr, m[1], m[2]]; ref = dec[k]['sweep'][str(b)]
        refv = [ref['crack_iou'], ref['crack_P'], ref['relP2'], ref['relR2'], ref['relF1'], ref['inact_iou']]
        pr(f'  {k} b {b}: ' + ' / '.join(f'{x:.4f}' for x in mine) + f'  max|diff| vs file {max(abs(a - c) for a, c in zip(mine, refv)):.1e}')

pr('\n## reported pairs (E-PF b, E-SKR2 b): test all 50 / clean 49 and E1; own CIs (default_rng(777))')
rng = np.random.default_rng(777)
for pa, pb, tag in ((1.0, 1.0, 'E-PF at E-SKR2 headline b'), (1.5, 1.0, 'each at its D2 b'), (1.5, 1.5, 'both at E-PF D2 b'), (0.0, 1.5, 'reported')):
    pr(f'  pair ({pa}, {pb}) [{tag}; reported, not a verdict]')
    for sn, kp in (('all 50', lambda s: True), ('clean 49', lambda s: s != NOISY)):
        st = sorted(s for s in J[('E-PF', pa)]['test'] if kp(s))
        f, lo, hi = boot(feats(J[('E-PF', pa)]['test'], st), feats(J[('E-SKR2', pb)]['test'], st), [np.array([i]) for i in range(len(st))], rng)
        pr(f'    test {sn:8s} ' + ' | '.join(f'{NAMES[i]} {f[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}]' for i in (0, 1, 2)) + f' | relP@2 {f[4]:+.4f}')
    st = sorted(J[('E-PF', pa)]['ext']); cl = sorted({key(s) for s in st}); gr = [np.array([i for i, s in enumerate(st) if key(s) == c]) for c in cl]
    f, lo, hi = boot(feats(J[('E-PF', pa)]['ext'], st), feats(J[('E-SKR2', pb)]['ext'], st), gr, rng)
    pr(f'    E1 ' + ' | '.join(f'{NAMES[i]} {f[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}]' for i in (1, 3, 2)))
    na, ca = cfree(J[('E-PF', pa)]['ext']); nb, cb = cfree(J[('E-SKR2', pb)]['ext'])
    pr(f'    G2a-form relP@2 (all 50) {"see test line"}; G2b-form E1 crack-free px {cb} vs {ca} (x{cb / max(ca, 1):.2f})')

pr('\n## width per arm per b: test (all 50) and E1 (106): pred / GT crack px, pixel P / R, relP@2 / relR@2; crack-free px test / E1 / val')
for k in A:
    for b in U:
        row = []
        for sp in ('test', 'ext'):
            c = J[(k, b)][sp]; st = sorted(c); g, p, tp = px(c, st); R = feats(c, st)[1].sum(0)
            row.append(f'{sp} pred/GT {p / g:.3f} P {tp / p:.3f} R {tp / g:.3f} relP {R[0] / R[1]:.3f} relR {R[2] / R[3]:.3f}')
        cf = [cfree(J[(k, b)][sp]) for sp in ('test', 'ext', 'val')]
        pr(f'  {k} b {b}: ' + ' | '.join(row) + ' | crack-free px ' + ' / '.join(f'{p} ({n})' for n, p in cf))

ST = {'scuff+half-cut 29': lambda s: CX[s][1] == 'scuff=1' and CX[s][2] == 'halfcut=1',
      'half-cut no scuff 29': lambda s: CX[s][1] == 'scuff=0' and CX[s][2] == 'halfcut=1',
      'full 48': lambda s: CX[s][2] == 'halfcut=0', 'other 77': lambda s: not (CX[s][1] == 'scuff=1' and CX[s][2] == 'halfcut=1')}
ext = sorted(J[('E-PF', 0.0)]['ext']); assert set(ext) == set(CX) and len(ext) == 106
pr('\n## E1 any-hit per stratum (hits / GT comps >= 20 px), relF1@2, inactive IoU, pred / GT')
for b_pf, b_sk in ((0.0, 0.0), (0.0, 1.0)):
    pr(f'  pair ({b_pf}, {b_sk})')
    for sn, f in ST.items():
        st = [s for s in ext if f(s)]; row = []
        for k, b in (('E-PF', b_pf), ('E-SKR2', b_sk)):
            c = J[(k, b)]['ext']; h, n = hits(c, st); m = metr(*(x.sum(0) for x in feats(c, st))); g, p, _ = px(c, st)
            row.append(f'{k} {h}/{n} relF1 {m[1]:.4f} inact {m[2]:.4f} pred/GT {p / max(g, 1):.3f}')
        pr(f'    {sn:21s} ' + ' | '.join(row))

pr('\n## any-hit by source image (cluster), b 0 pair and headline pair: GT comps, E-PF b0 / E-SKR2 b0 / E-SKR2 b1 hits')
cl = sorted({key(s) for s in ext}); per = []
for c in cl:
    st = [s for s in ext if key(s) == c]; n = hits(J[('E-PF', 0.0)]['ext'], st)[1]
    if n: per.append((n, c, hits(J[('E-PF', 0.0)]['ext'], st)[0], hits(J[('E-SKR2', 0.0)]['ext'], st)[0], hits(J[('E-SKR2', 1.0)]['ext'], st)[0],
                      sum(ST['scuff+half-cut 29'](s) for s in st), len(st)))
per.sort(reverse=True); N = sum(p[0] for p in per)
pr(f'  {len(per)} images hold GT comps; N {N}; top 3 {sum(p[0] for p in per[:3]) / N:.2f}; top 10 {sum(p[0] for p in per[:10]) / N:.2f}; '
   f'n_eff {N ** 2 / sum(p[0] ** 2 for p in per):.1f}')
for p in per:
    pr(f'    {p[1]:18s} comps {p[0]:3d}  hits PF0 {p[2]:3d} SK0 {p[3]:3d} SK1 {p[4]:3d}  (+{p[3] - p[2]} / +{p[4] - p[2]})  cells {p[6]} (scuff+hc {p[5]})')
d0 = sum(p[3] - p[2] for p in per); d1 = sum(p[4] - p[2] for p in per)
top3 = [p[1] for p in per[:3]]
pr(f'  extra hits: b 0 pair +{d0} (top-3 images {sum(p[3] - p[2] for p in per[:3])}); headline pair +{d1} (top-3 images {sum(p[4] - p[2] for p in per[:3])})')

pr('\n## E1 robustness at the b 0 pair: leave-top-3-images-out (by GT crack comps; by GT inactive px) and leave-one-cluster-out')
def e1d(st, b_sk=0.0):
    a = metr(*(x.sum(0) for x in feats(J[('E-PF', 0.0)]['ext'], st))); b = metr(*(x.sum(0) for x in feats(J[('E-SKR2', b_sk)]['ext'], st)))
    return b - a
full = e1d(ext)
pr(f'  all 106: relF1@2 {full[1]:+.4f} any-hit {full[3]:+.4f} inactive {full[2]:+.4f}')
st = [s for s in ext if key(s) not in top3]; d = e1d(st)
pr(f'  without top-3 crack images {top3} ({106 - len(st)} cells): relF1@2 {d[1]:+.4f} any-hit {d[3]:+.4f} inactive {d[2]:+.4f}')
ig = {}
for s in ext:
    ig[key(s)] = ig.get(key(s), 0) + int(np.asarray(J[('E-PF', 0.0)]['ext'][s]['conf'], np.int64).reshape(NC, NC)[IN].sum())
it = sorted(((v, c) for c, v in ig.items() if v), reverse=True); TI = sum(v for v, _ in it)
st = [s for s in ext if key(s) not in [c for _, c in it[:3]]]; d = e1d(st)
pr(f'  inactive GT px {TI} in {len(it)} images, top 3 {sum(v for v, _ in it[:3]) / TI:.2f}, n_eff {TI ** 2 / sum(v * v for v, _ in it):.1f}; '
   f'without top-3 inactive images {[c for _, c in it[:3]]}: relF1@2 {d[1]:+.4f} any-hit {d[3]:+.4f} inactive {d[2]:+.4f}')
lo = [e1d([s for s in ext if key(s) != c]) for c in cl]
for i, nm in ((1, 'relF1@2'), (3, 'any-hit'), (2, 'inactive')):
    v = [x[i] for x in lo]; pr(f'  leave-one-cluster-out (71) {nm}: [{min(v):+.4f}, {max(v):+.4f}]')

pr('\n## matched volume (E1 aggregate sweep; E1-oracle, descriptive, chooses nothing)')
sp = {k: {float(b): v for b, v in sw[k].items()} for k in A}; g = sorted(sp['E-PF'])
t = sp['E-SKR2'][0.0]['pred_over_gt']; pv = [sp['E-PF'][b]['pred_over_gt'] for b in g]
assert all(x < y for x, y in zip(pv, pv[1:])), 'E-PF pred/GT not monotone'
i = next(j for j in range(len(g) - 1) if pv[j] <= t <= pv[j + 1]); w = (t - pv[i]) / (pv[i + 1] - pv[i]); bm = g[i] + w * (g[i + 1] - g[i])
li = lambda f: sp['E-PF'][g[i]][f] + w * (sp['E-PF'][g[i + 1]][f] - sp['E-PF'][g[i]][f])
pr(f'  E-SKR2 b 0 pred/GT {t:.4f}, relF1 {sp["E-SKR2"][0.0]["relF1"]:.4f}, any-hit {sp["E-SKR2"][0.0]["anyhit"]:.4f}, crack-free px {sp["E-SKR2"][0.0]["crack_free_px"]}')
pr(f'  E-PF at matched b {bm:.3f}: relF1 {li("relF1"):.4f}, any-hit {li("anyhit"):.4f}, crack-free px {li("crack_free_px"):.0f}')
pr(f'  E1 relF1@2 delta {sp["E-SKR2"][0.0]["relF1"] - sp["E-PF"][0.0]["relF1"]:+.4f} at b 0 -> {sp["E-SKR2"][0.0]["relF1"] - li("relF1"):+.4f} at matched volume '
   f'(bias share {(li("relF1") - sp["E-PF"][0.0]["relF1"]) / (sp["E-SKR2"][0.0]["relF1"] - sp["E-PF"][0.0]["relF1"]):.0%})')
pr(f'  E1 any-hit delta {sp["E-SKR2"][0.0]["anyhit"] - sp["E-PF"][0.0]["anyhit"]:+.4f} at b 0 -> {sp["E-SKR2"][0.0]["anyhit"] - li("anyhit"):+.4f} at matched volume '
   f'(bias share {(li("anyhit") - sp["E-PF"][0.0]["anyhit"]) / (sp["E-SKR2"][0.0]["anyhit"] - sp["E-PF"][0.0]["anyhit"]):.0%})')
pr('  full sweep (b: E-PF pred/GT relF1 any-hit cfree | E-SKR2 pred/GT relF1 any-hit cfree)')
for b in g:
    pr(f'    {b:4.2f}: ' + ' | '.join(f'{sp[k][b]["pred_over_gt"]:.3f} {sp[k][b]["relF1"]:.4f} {sp[k][b]["anyhit_hits"]:3d} {sp[k][b]["crack_free_px"]:5d}' for k in A))
for k in A:
    for b in U:
        assert sp[k][b]['anyhit_hits'] == hits(J[(k, b)]['ext'], ext)[0] and sp[k][b]['crack_free_px'] == cfree(J[(k, b)]['ext'])[1]
pr('  sweep at b in U = per-cell files (any-hit hits, crack-free px): EQUAL')
