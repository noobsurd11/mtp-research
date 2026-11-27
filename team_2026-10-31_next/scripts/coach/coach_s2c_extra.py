"""coach (14 Nov 2026): SKR2C extra readouts, written AFTER my verdict outputs (coach_s2c_R.txt / coach_s2c_D.txt, MD5_first) and after
the comparison with the runner. Reported / fragility lines only: they describe where the guard trips come from. No verdict, bar, set or
seed list is touched; nothing here feeds coach_s2c.py. Own code on the same per-cell files (raw_r m0 JSONs, raw_d E-*.json).
  1 per-seed values of the guard quantities (test inactive IoU and test crack relP@2, all 50 / clean 49), both arms
  2 the noisy cell CSIR_00070_r8_c4 per run: GT / predicted crack px and its share of the run's predicted crack px (Track M's noisy-cell line)
  3 G2's test relP@2 form on the clean 49 and without each seed; which seed / module drop removes each trip (from coach_s2c_R.json)
  4 seed-aware two-stage bootstrap (48 modules x seeds within arm, 2,000, seed 0): share of draws in which G1 / G2's relP arm trips
  5 test inactive: GT px per cell, concentration, per-cell IoU change (singles seed means; ensembles), leave-top-3-out
  6 D: image bootstrap (2,000, seed 0) share of draws in which G1t trips; val inactive of both ensembles and of the singles (val is not sealed)
  7 comparison aids: the 5-seed-mean image bootstrap redone with m2_rung's RNG stream; the 2,000 seed-0 draws of D's E1 any-hit
    (how many are below, at and above 0); opening_outputs.txt against the raw files
Usage: python -B coach_s2c_extra.py"""
import json, re, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; T = HERE.parent.parent; RES = T / 'results'
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(T.parent / 'team_2026-10-29_features' / 'scripts'))
import coach_thin as ct
import coach_verify as cv
import coach_skr2e as ce

NC, CR, IN, NOISY = 24, 14, 11, 'CSIR_00070_r8_c4'
clu = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)
raw = RES / 's2c/raw_r'; P = print
MA = [ct.load_m0(f'{raw}/m0/SUPPF/s2c_SUPPF_100pct_s{k}.json', 'e544133') for k in range(10, 15)]
MB = [ct.load_m0(f'{raw}/m0/SKR01/s2c_SKR01_100pct_s{k}.json', 'c9bbb02') for k in range(10, 15)]
Rj = json.load(open(RES / 's2c/coach_v/coach_s2c_R.json'))
met = lambda M, keep, split='test': [cv.metrics(*cv.counts(d, keep, split)) for d in M]
ALL, CLEAN = (lambda s: True), (lambda s: s != NOISY)

P('## 1. guard quantities per seed (s10..s14); singles, argmax')
for k, nm in (('inact', 'test inactive IoU'), ('relP', 'test crack relP@2'), ('crack', 'test crack IoU'), ('relF1', 'test crack relF1@2')):
    for sn, kp in (('all 50', ALL), ('clean 49', CLEAN)):
        a, b = [m[k] for m in met(MA, kp)], [m[k] for m in met(MB, kp)]
        P(f'  {nm:19s} {sn:8s} SUPPF {" ".join(f"{x:.4f}" for x in a)} (mean {np.mean(a):.4f}) | SKR01 {" ".join(f"{x:.4f}" for x in b)} (mean {np.mean(b):.4f}) | d {np.mean(b) - np.mean(a):+.4f}')

P(f'## 2. the noisy cell {NOISY} per run: GT crack px | predicted crack px | predicted crack px within 2 px of GT | share of the run\'s predicted crack px (test, all 50)')
for nm, M in (('SUPPF', MA), ('SKR01', MB)):
    rows = []
    for d in M:
        c = d['cells']['test'][NOISY]; C = np.asarray(c['conf'], np.int64).reshape(NC, NC); tot = sum(np.asarray(x['conf'], np.int64).reshape(NC, NC)[:, CR].sum() for x in d['cells']['test'].values())
        rows.append((int(C[CR].sum()), int(C[:, CR].sum()), int(c['crack_rel2'][0]), C[:, CR].sum() / tot, int(C[IN].sum()), int(C[:, IN].sum())))
    P(f'  {nm}: GT crack px {rows[0][0]} | predicted ' + ' '.join(str(r[1]) for r in rows) + ' | near GT ' + ' '.join(str(r[2]) for r in rows) + ' | share ' + ' '.join(f'{r[3]:.3f}' for r in rows)
      + f' | GT inactive px {rows[0][4]}, predicted inactive ' + ' '.join(str(r[5]) for r in rows))
cl_ = [(int(np.asarray(d['cells']['test'][NOISY]['conf'], np.int64).reshape(NC, NC)[:, CR].sum())) for d in MB]
P(f'  SKR01 s13 predicts {cl_[3]} crack px on this one cell; the other 4 SKR01 runs {min(x for i, x in enumerate(cl_) if i != 3)} .. {max(x for i, x in enumerate(cl_) if i != 3)}')

P('## 3. where each trip sits (verdict sets and bars unchanged; these are leave-outs)')
a, b = [m['relP'] for m in met(MA, CLEAN)], [m['relP'] for m in met(MB, CLEAN)]
P(f'  G2 relP@2 form on the clean 49 (the guard is defined on all 50): {np.mean(b) - np.mean(a):+.4f} (bar < -0.03)')
drops = [('SUPPF', k) for k in range(10, 15)] + [('SKR01', k) for k in range(10, 15)]
g = Rj['loso']['guards']
for (arm, k), x in zip(drops, g):
    P(f'  without {arm} s{k}: G1 {x[0]:+.4f} / {x[1]:+.4f} {"TRIP" if x[2] else "ok"} | G2 relP@2 {x[3]:+.4f}, E1 crack-free x{x[4]:.3f} {"TRIP" if x[5] else "ok"} | verdict R {Rj["loso"]["verdict_per_drop"][drops.index((arm, k))]}')
gl = Rj['loco']['guards_test_loco']
P('  module drops (48) that remove a trip: G1: ' + (', '.join(f'{x[3]} ({x[0]:+.4f} / {x[1]:+.4f})' for x in gl if not (x[0] <= -0.015 and x[1] <= -0.015)) or 'none')
  + ' | G2 relP@2: ' + (', '.join(f'{x[3]} ({x[2]:+.4f})' for x in gl if not x[2] < -0.03) or 'none'))
both = [x[3] for x in gl if not (x[0] <= -0.015 and x[1] <= -0.015) and not x[2] < -0.03]
P(f'  module drops that remove both trips: {both or "none"}')

P('## 4. seed-aware two-stage bootstrap of the guard quantities (48 test modules x seeds within arm; 2,000 draws; seed 0)')
stems = sorted(MA[0]['cells']['test']); cl = np.array([clu(s) for s in stems]); u, inv = np.unique(cl, return_inverse=True); ncl = len(u); assert ncl == 48
def F(M):
    out = []
    for d in M:
        r = []
        for s in stems:
            c = d['cells']['test'][s]; C = np.asarray(c['conf'], float).reshape(NC, NC)
            r.append([C[IN, IN], C[IN].sum(), C[:, IN].sum(), c['crack_rel2'][0], c['crack_rel2'][1]])
        out.append(r)
    return np.array(out, float)
XA, XB = F(MA), F(MB); noisy = np.array([s == NOISY for s in stems]); Mx = np.zeros((ncl, len(stems))); Mx[inv, np.arange(len(stems))] = 1
def gq(X, w):
    S = np.einsum('c,rcf->rf', w, X); return (S[:, 0] / np.maximum(S[:, 1] + S[:, 2] - S[:, 0], 1)).mean(), (S[:, 3] / np.maximum(S[:, 4], 1)).mean()
rng = np.random.default_rng(0); D = []
for _ in range(2000):
    w = np.bincount(rng.integers(0, ncl, ncl), minlength=ncl) @ Mx; sa = rng.integers(0, 5, 5); sb = rng.integers(0, 5, 5); wc = w * (~noisy)
    ia, pa = gq(XA[sa], w); ib, pb = gq(XB[sb], w); ica, _ = gq(XA[sa], wc); icb, _ = gq(XB[sb], wc)
    D.append((ib - ia, icb - ica, pb - pa))
D = np.array(D)
P(f'  G1: share of draws with inactive d <= -0.015 in both sets {np.mean((D[:, 0] <= -0.015) & (D[:, 1] <= -0.015)):.3f}; d all 50 95% interval [{np.percentile(D[:, 0], 2.5):+.4f}, {np.percentile(D[:, 0], 97.5):+.4f}], '
  f'clean [{np.percentile(D[:, 1], 2.5):+.4f}, {np.percentile(D[:, 1], 97.5):+.4f}]; share with d < 0 (all) {np.mean(D[:, 0] < 0):.3f}')
P(f'  G2 relP@2: share of draws with d < -0.03 {np.mean(D[:, 2] < -0.03):.3f}; 95% interval [{np.percentile(D[:, 2], 2.5):+.4f}, {np.percentile(D[:, 2], 97.5):+.4f}]; median {np.median(D[:, 2]):+.4f}')
P(f'  either guard trips in {np.mean(((D[:, 0] <= -0.015) & (D[:, 1] <= -0.015)) | (D[:, 2] < -0.03)):.3f} of the draws')

P('## 5. test inactive: where the loss sits')
gt = {s: int(np.asarray(MA[0]['cells']['test'][s]['conf'], np.int64).reshape(NC, NC)[IN].sum()) for s in stems}
ic = sorted((s for s in stems if gt[s] > 0), key=lambda s: -gt[s]); TI = sum(gt[s] for s in ic)
P(f'  GT inactive px {TI} in {len(ic)} of 50 cells ({len({clu(s) for s in ic})} modules); top 3 cells {sum(gt[s] for s in ic[:3]) / TI:.3f}, n_eff {TI ** 2 / sum(gt[s] ** 2 for s in ic):.1f} cells')
def cell_iou(d, s):
    C = np.asarray(d['cells']['test'][s]['conf'], float).reshape(NC, NC); den = C[IN].sum() + C[:, IN].sum() - C[IN, IN]; return C[IN, IN] / den if den > 0 else np.nan
rows = []
for s in ic:
    a_, b_ = np.nanmean([cell_iou(d, s) for d in MA]), np.nanmean([cell_iou(d, s) for d in MB]); rows.append((s, gt[s], a_, b_))
P(f'  singles, per-cell inactive IoU (seed means), cells with GT inactive: down in {sum(r[3] < r[2] for r in rows)} of {len(rows)}; median change {np.median([r[3] - r[2] for r in rows]):+.4f}')
for r in rows:
    P(f'    {r[0]:22s} GT px {r[1]:6d} ({r[1] / TI:.3f})  SUPPF {r[2]:.3f} -> SKR01 {r[3]:.3f} ({r[3] - r[2]:+.3f})')
def pooled(M, keep):
    return float(np.mean([m['inact'] for m in met(M, keep)]))
top3 = set(ic[:3]); P(f'  singles without the top-3 GT inactive cells {sorted(top3)}: d {pooled(MB, lambda s: s not in top3) - pooled(MA, lambda s: s not in top3):+.4f} (all) / '
                      f'{pooled(MB, lambda s: s not in top3 and s != NOISY) - pooled(MA, lambda s: s not in top3 and s != NOISY):+.4f} (clean)')
fp = lambda M: float(np.mean([sum(np.asarray(x['conf'], np.int64).reshape(NC, NC)[:, IN].sum() - np.asarray(x['conf'], np.int64).reshape(NC, NC)[IN, IN] for x in d['cells']['test'].values()) for d in M]))
tp = lambda M: float(np.mean([sum(np.asarray(x['conf'], np.int64).reshape(NC, NC)[IN, IN] for x in d['cells']['test'].values()) for d in M]))
P(f'  singles, test (all 50), seed means: inactive TP px {tp(MA):.0f} -> {tp(MB):.0f} of {TI} GT ({tp(MA) / TI:.3f} -> {tp(MB) / TI:.3f}); inactive predicted on other GT {fp(MA):.0f} -> {fp(MB):.0f}')
va, vb = [m['inact'] for m in met(MA, ALL, 'val')], [m['inact'] for m in met(MB, ALL, 'val')]; r = ct.rule1(va, vb)
P(f'  singles, val (54 cells; not a sealed set): inactive IoU {np.mean(va):.4f} -> {np.mean(vb):.4f}, d {r[0]:+.4f} (rule-1 thr {r[1]:.4f}); per seed SUPPF {" ".join(f"{x:.3f}" for x in va)} | SKR01 {" ".join(f"{x:.3f}" for x in vb)}')
e1a, e1b = [m['inact'] for m in met(MA, ALL, 'ext')], [m['inact'] for m in met(MB, ALL, 'ext')]
P(f'  singles, E1 (106): inactive IoU {np.mean(e1a):.4f} -> {np.mean(e1b):.4f} ({np.mean(e1b) - np.mean(e1a):+.4f}); per seed SUPPF {" ".join(f"{x:.3f}" for x in e1a)} | SKR01 {" ".join(f"{x:.3f}" for x in e1b)}')

P('## 6. D: the G1t trip')
rd = RES / 's2c/raw_d'; A = json.load(open(rd / 'E-SUPPF.b0.json'))['cells']; B = json.load(open(rd / 'E-SKR2.b0.json'))['cells']
st = sorted(A['test']); FA, FB = ce.feats(A['test'], st), ce.feats(B['test'], st); nz = np.array([s != NOISY for s in st])
rng = np.random.default_rng(0); Dd = []
for _ in range(2000):
    ix = rng.integers(0, len(st), len(st)); ixc = ix[nz[ix]]
    da = ce.metr(*(x[ix].sum(0) for x in FB)) - ce.metr(*(x[ix].sum(0) for x in FA)); dc = ce.metr(*(x[ixc].sum(0) for x in FB)) - ce.metr(*(x[ixc].sum(0) for x in FA))
    Dd.append((da[2], dc[2], da[4]))
Dd = np.array(Dd)
P(f'  paired image bootstrap (2,000, seed 0; the clean set = the same draw without the noisy cell): share of draws with inactive d <= -0.015 in both sets {np.nanmean((Dd[:, 0] <= -0.015) & (Dd[:, 1] <= -0.015)):.3f}; '
  f'share with d < 0 (all) {np.nanmean(Dd[:, 0] < 0):.3f}; G2a relP@2 share < -0.03 {np.nanmean(Dd[:, 2] < -0.03):.3f}')
rows = []
for s in ic:
    def ci(c):
        C = np.asarray(c[s]['conf'], float).reshape(NC, NC); den = C[IN].sum() + C[:, IN].sum() - C[IN, IN]; return C[IN, IN] / den if den > 0 else np.nan
    rows.append((s, gt[s], ci(A['test']), ci(B['test'])))
P(f'  ensembles, per-cell inactive IoU, cells with GT inactive: down in {sum(r[3] < r[2] for r in rows)} of {len(rows)}; median change {np.median([r[3] - r[2] for r in rows]):+.4f}')
for r in rows:
    P(f'    {r[0]:22s} GT px {r[1]:6d}  E-SUPPF {r[2]:.3f} -> E-SKR2 {r[3]:.3f} ({r[3] - r[2]:+.3f})')
mm = lambda c, stl: ce.metr(*(x.sum(0) for x in ce.feats(c, stl)))
s3 = [s for s in st if s not in top3]; P(f'  ensembles without the top-3 GT inactive cells: d {mm(B["test"], s3)[2] - mm(A["test"], s3)[2]:+.4f} (all) / '
                                           f'{mm(B["test"], [s for s in s3 if s != NOISY])[2] - mm(A["test"], [s for s in s3 if s != NOISY])[2]:+.4f} (clean)')
C_ = lambda c: sum(np.asarray(v['conf'], np.int64).reshape(NC, NC) for v in c.values())
ca, cb = C_(A['test']), C_(B['test'])
P(f'  ensembles, test (all 50): inactive TP px {ca[IN, IN]} -> {cb[IN, IN]} of {ca[IN].sum()} GT; inactive predicted on other GT {ca[:, IN].sum() - ca[IN, IN]} -> {cb[:, IN].sum() - cb[IN, IN]}; '
  f'GT inactive predicted as background (0) {ca[IN, 0]} -> {cb[IN, 0]}, as crack (14) {ca[IN, CR]} -> {cb[IN, CR]}')
sv = sorted(A['val']); P(f'  ensembles, val (54 cells; not sealed): inactive IoU {mm(A["val"], sv)[2]:.4f} -> {mm(B["val"], sv)[2]:.4f} ({mm(B["val"], sv)[2] - mm(A["val"], sv)[2]:+.4f}); crack IoU '
                         f'{mm(A["val"], sv)[0]:.4f} -> {mm(B["val"], sv)[0]:.4f}; relF1@2 {mm(A["val"], sv)[1]:.4f} -> {mm(B["val"], sv)[1]:.4f}')
P(f'  noisy cell, ensembles: predicted crack px E-SUPPF {int(np.asarray(A["test"][NOISY]["conf"], np.int64).reshape(NC, NC)[:, CR].sum())}, E-SKR2 {int(np.asarray(B["test"][NOISY]["conf"], np.int64).reshape(NC, NC)[:, CR].sum())}')

P('## 7. comparison aids (after reading the runner\'s files)')
stems_t = sorted(MA[0]['cells']['test'])
def stack(D_):
    return (np.stack([[np.asarray(d['cells']['test'][s]['conf'], float).reshape(NC, NC) for s in stems_t] for d in D_]),
            np.stack([[np.asarray(d['cells']['test'][s]['crack_rel2'], float) for s in stems_t] for d in D_]))
CB, XB_ = stack(MA); CA, XA_ = stack(MB)
def mean_m(C, X, idx):
    o = [cv.metrics(C[r, idx].sum(0), X[r, idx].sum(0)) for r in range(C.shape[0])]; return np.array([np.mean([q[k] for q in o]) for k in ('crack', 'relF1', 'inact')])
for sn in ('all', 'noNoisy'):
    rng = np.random.default_rng(0); idx0 = np.array([i for i, s in enumerate(stems_t) if cv.SETS[sn](s)])
    Dm = np.array([mean_m(CA, XA_, idx0[i]) - mean_m(CB, XB_, idx0[i]) for i in (rng.integers(0, len(idx0), len(idx0)) for _ in range(2000))])
    P(f'  paired image bootstrap of the 5-seed means with a fresh default_rng(0) per set and rng.integers draws (= m2_rung\'s stream), {sn}: ' + ' | '.join(
        f'{k} [{np.nanpercentile(Dm[:, j], 2.5):+.4f}, {np.nanpercentile(Dm[:, j], 97.5):+.4f}] P>0 {np.mean(Dm[:, j] > 0):.2f}' for j, k in enumerate(('crack', 'relF1', 'inact'))))
ext = sorted(A['ext']); cls = sorted({ce.key(s) for s in ext}); groups = [np.array([i for i, s in enumerate(ext) if ce.key(s) == c]) for c in cls]
FA2, FB2 = ce.feats(A['ext'], ext), ce.feats(B['ext'], ext); rng = np.random.default_rng(0); ah = []
for _ in range(2000):
    ix = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
    ah.append(ce.metr(*(x[ix].sum(0) for x in FB2))[3] - ce.metr(*(x[ix].sum(0) for x in FA2))[3])
ah = np.array(ah)
P(f'  D E1 any-hit, the 2,000 seed-0 cluster draws: d < 0 in {int((ah < 0).sum())}, d == 0 in {int((ah == 0).sum())}, d > 0 in {int((ah > 0).sum())}; 2.5th percentile {np.percentile(ah, 2.5)!r}; '
  f'sorted draws no. 50 / 51 (the percentile sits between them): {np.sort(ah)[49]!r} / {np.sort(ah)[50]!r}')
import hashlib
oo = open(RES / 's2c/local/opening_outputs.txt').read().split('\n'); bad = []; n = 0
for i, l in enumerate(oo):
    q = re.match(r'^=================== (D )?(\S+) \(([0-9a-f]{8})\)$', l)
    if q:
        f = (RES / 's2c/raw_d' if q.group(1) else raw) / q.group(2); n += 1; body = open(f).read()
        j = i + 1; k = j
        while k < len(oo) and not oo[k].startswith('==================='):
            k += 1
        got = '\n'.join(oo[j:k]).rstrip('\n'); ok = hashlib.md5(open(f, 'rb').read()).hexdigest()[:8] == q.group(3) and got == body.rstrip('\n')
        if not ok:
            bad.append(q.group(2))
P(f'  opening_outputs.txt: {n} collected files; md5 tag and text equal to the raw file for all: {not bad}' + (f' (differs: {bad})' if bad else ''))
