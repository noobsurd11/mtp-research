"""evalx Q5: where the unseen-module gap is. E1 ext (106 cells) per source / per module; label-shape check;
power on ext with cell and module-cluster bootstrap. Reads Track M m0 + final JSONs (full confusion, relaxed@2,
components) and results/e1/raw_v2 (all arms, counts)."""
import json, glob, re, collections
import numpy as np
from common import load, pooled, ARMS

TM = '/home/yugma/mtp/research/team_2026-10-24_go/trackM/'
NC, CR, IN = 24, 14, 11
rng = np.random.default_rng(0)


def cellrec(c):
    C = np.array(c['conf']).reshape(NC, NC)
    r = c['crack_rel2']
    return dict(cgt=C[CR].sum(), cpr=C[:, CR].sum(), ctp=C[CR, CR], igt=C[IN].sum(), ipr=C[:, IN].sum(), itp=C[IN, IN],
                p2=r[0], pr=r[1], r2=r[2], g=r[3], cc=c['crack_cc'], icc=c['inact_cc'])


def loadtm(path, key=None, split='ext'):
    d = json.load(open(path))
    cells = d['cells'][split] if key is None else d[split][key]
    return {s: cellrec(v) for s, v in cells.items()}


A100 = [loadtm(f) for f in sorted(glob.glob(TM + 'm0/p6_L3_100pct_s*.json')) + sorted(glob.glob(TM + 'm0/p16_A_100pct_s*.json'))]
SX = [loadtm(f) for f in sorted(glob.glob(TM + 'm0/p16_Sx_100pct_s*.json'))]
FIN = loadtm(TM + 'final/final_cells.json', 'final_b0.75')
FIN0 = loadtm(TM + 'final/final_cells.json', 'final_b0')
A100t = [loadtm(f, split='test') for f in sorted(glob.glob(TM + 'm0/p6_L3_100pct_s*.json')) + sorted(glob.glob(TM + 'm0/p16_A_100pct_s*.json'))]
FINt = loadtm(TM + 'final/final_cells.json', 'final_b0.75', 'test')
cells = sorted(FIN)
src = lambda s: s.split('_')[0]
mod = lambda s: '_'.join(s.split('_')[:2])
print(f'ext cells {len(cells)}; sources {collections.Counter(map(src, cells))}; modules {len(set(map(mod, cells)))}')


def agg(R, cs):
    t = {k: sum(R[c][k] for c in cs) for k in ['cgt', 'cpr', 'ctp', 'igt', 'ipr', 'itp', 'p2', 'pr', 'r2', 'g']}
    o = {}
    o['ciou'] = t['ctp'] / max(t['cgt'] + t['cpr'] - t['ctp'], 1)
    o['crec'] = t['ctp'] / max(t['cgt'], 1)
    o['cprec'] = t['ctp'] / max(t['cpr'], 1)
    o['relR'] = t['r2'] / max(t['g'], 1)
    o['relP'] = t['p2'] / max(t['pr'], 1)
    o['relF1'] = 2 * o['relR'] * o['relP'] / max(o['relR'] + o['relP'], 1e-9)
    o['iiou'] = t['itp'] / max(t['igt'] + t['ipr'] - t['itp'], 1)
    o['irec'] = t['itp'] / max(t['igt'], 1)
    gg = [x for c in cs for x in R[c]['cc']['gt'] if x[0] >= 20]
    o['cc_rec'] = np.mean([x[1] >= 0.5 * x[0] for x in gg]) if gg else np.nan
    o['cc_n'] = len(gg)
    pp = [x for c in cs for x in R[c]['cc']['pr'] if x[0] >= 20]
    o['cc_prec'] = np.mean([x[1] > 0 for x in pp]) if pp else np.nan
    o['cgt'] = t['cgt']; o['igt'] = t['igt']
    return o


def mean_runs(RR, cs, k):
    return np.mean([agg(R, cs)[k] for R in RR])


print('\n# A. Test vs ext, crack (A100 = mean of 5 single models; FINAL = ensemble bias +0.75)')
for name, RR, cs in [('test A100', A100t, sorted(FINt)), ('test FINAL', [FINt], sorted(FINt)),
                     ('ext A100', A100, cells), ('ext Sx100', SX, cells), ('ext FINAL', [FIN], cells), ('ext FINAL b0', [FIN0], cells)]:
    a = {k: np.mean([agg(R, cs)[k] for R in RR]) for k in ['ciou', 'crec', 'cprec', 'relR', 'relP', 'relF1', 'cc_rec', 'cc_prec', 'iiou', 'irec']}
    print(name, ' '.join(f'{k} {v:.3f}' for k, v in a.items()))

print('\n# B. Ext per source')
for s in ['CSIR', 'BMRK']:
    cs = [c for c in cells if src(c) == s]
    nc = sum(FIN[c]['cgt'] > 0 for c in cs); ni = sum(FIN[c]['igt'] > 0 for c in cs)
    a = agg(FIN, cs); b = {k: mean_runs(A100, cs, k) for k in ['ciou', 'crec', 'relR', 'iiou']}
    print(f'{s} cells {len(cs)} crack_cells {nc} inact_cells {ni} crack_px {a["cgt"]} inact_px {a["igt"]} | A100 ciou {b["ciou"]:.3f} '
          f'crec {b["crec"]:.3f} relR {b["relR"]:.3f} iiou {b["iiou"]:.3f} | FINAL ciou {a["ciou"]:.3f} crec {a["crec"]:.3f} '
          f'relR {a["relR"]:.3f} cc_rec {a["cc_rec"]:.3f} (n {a["cc_n"]}) iiou {a["iiou"]:.3f} irec {a["irec"]:.3f}')

print('\n# C. Ext per module (modules with crack GT), sorted by crack px; FINAL recall/relR@2, A100 mean recall')
M = collections.defaultdict(list)
for c in cells:
    M[mod(c)].append(c)
rows = []
tot = sum(FIN[c]['cgt'] for c in cells)
for m, cs in M.items():
    g = sum(FIN[c]['cgt'] for c in cs)
    if g == 0:
        continue
    a = agg(FIN, cs)
    rows.append((g, m, len(cs), sum(FIN[c]['cgt'] > 0 for c in cs), a['crec'], a['relR'], mean_runs(A100, cs, 'crec'), a['cc_rec'], a['cc_n']))
rows.sort(reverse=True)
cum = 0
for g, m, n, ncr, r, rr, ra, ccr, ccn in rows:
    cum += g
    print(f'{m} cells {n} crack_cells {ncr} crack_px {g} share {g / tot:.3f} cum {cum / tot:.3f} | FINAL rec {r:.3f} relR {rr:.3f} '
          f'cc_rec {ccr:.2f} (n {ccn}) | A100 rec {ra:.3f}')
print(f'modules with crack {len(rows)}; total crack px {tot}; top-3 module share {sum(r[0] for r in rows[:3]) / tot:.3f}; '
      f'top-5 {sum(r[0] for r in rows[:5]) / tot:.3f}')
nmod_in = sum(1 for m, cs in M.items() if sum(FIN[c]['igt'] for c in cs) > 0)
itot = sum(FIN[c]['igt'] for c in cells)
irows = sorted([(sum(FIN[c]['igt'] for c in cs), m) for m, cs in M.items() if sum(FIN[c]['igt'] for c in cs) > 0], reverse=True)
print(f'inactive: modules {nmod_in}, cells {sum(FIN[c]["igt"] > 0 for c in cells)}, px {itot}, top-3 module share {sum(r[0] for r in irows[:3]) / max(itot, 1):.3f}')

print('\n# D. Label shape: GT crack components, test vs ext (FINAL file; GT is the same for every model)')
for name, R in [('test', FINt), ('ext', FIN)]:
    sz = np.array([x[0] for c in R for x in R[c]['cc']['gt']])
    px = sz.sum()
    print(f'{name}: comps {len(sz)}, px {px}, median comp {np.median(sz):.0f}, comps<20px {np.mean(sz < 20):.2f} '
          f'holding {sz[sz < 20].sum() / px:.3f} of px, comps<5px {np.mean(sz < 5):.2f}; cells with crack {sum(R[c]["cgt"] > 0 for c in R)}; '
          f'median crack px per crack cell {np.median([R[c]["cgt"] for c in R if R[c]["cgt"] > 0]):.0f}')
# width proxy from raw_v2 (crack_len_gt = skeleton px)
for split in ['test', 'ext']:
    js = json.load(open('/home/yugma/mtp/research/results/e1/raw_v2/p6_L3_100pct_s0.json'))['cells'][split]
    g = sum(v.get('crack_gt', 0) for v in js.values()); L = sum(v.get('crack_len_gt', 0) for v in js.values())
    ws = [v['crack_gt'] / v['crack_len_gt'] for v in js.values() if v.get('crack_len_gt', 0) >= 20]
    print(f'{split}: crack px / skeleton px = {g}/{L} = {g / max(L, 1):.2f}; per-cell median {np.median(ws) if ws else float("nan"):.2f}')

print('\n# E. Power on ext: seed sd, rule-1 thr (5v5), cell-bootstrap and module-cluster-bootstrap sd of the contrast')
PAIRS = [('A100', 'Sx100'), ('A50', 'S50'), ('A20', 'S20'), ('A5c', 'BsM5'), ('A5c', 'CsM5'), ('L3_10', 'BsM10'), ('A20', 'BsM20')]
D = {a: load(a, 'ext') for a in set(x for p in PAIRS for x in p)}
ec = D['A100'][0]
mods = sorted(set(map(mod, ec)))
midx = {m: np.array([i for i, c in enumerate(ec) if mod(c) == m]) for m in mods}
Bc = rng.integers(0, len(ec), size=(2000, len(ec)))
Bm = [np.concatenate([midx[mods[j]] for j in rng.integers(0, len(mods), len(mods))]) for _ in range(2000)]
for a, b in PAIRS:
    XA, XB = D[a][1], D[b][1]
    for m in ['crack_iou', 'crack_rec', 'inact_iou']:
        pa, pb = pooled(XA)[m], pooled(XB)[m]
        d = pb.mean() - pa.mean(); sa, sb = pa.std(ddof=1), pb.std(ddof=1)
        thr = max(0.01, 2 * np.sqrt((sa**2 + sb**2) / 3))
        bc = np.array([pooled(XB, i)[m].mean() - pooled(XA, i)[m].mean() for i in Bc])
        bm = np.array([pooled(XB, i)[m].mean() - pooled(XA, i)[m].mean() for i in Bm])
        print(f'{b}-{a} {m}: A {pa.mean():.3f} B {pb.mean():.3f} d {d:+.4f} thr {thr:.4f} seedsd {sa:.4f}/{sb:.4f} '
              f'cellCI [{np.percentile(bc, 2.5):+.4f},{np.percentile(bc, 97.5):+.4f}] sd {bc.std():.4f} '
              f'moduleCI [{np.percentile(bm, 2.5):+.4f},{np.percentile(bm, 97.5):+.4f}] sd {bm.std():.4f}')
