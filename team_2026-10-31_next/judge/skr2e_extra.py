#!/usr/bin/env python3
"""judge skr2e_extra (2 Nov 2026): adversarial extras on the SKR2E pull (reported only; chooses nothing). Own code, numpy.
 (1) test bias share: E-PF test readouts at U b's, linear in pred/GT, at E-SKR2 b 0's test volume (coarse: test is stored at U only).
 (2) E1 from the aggregate sweep: equal-b gap and matched-volume gap at every grid b of E-SKR2; crack-free px at matched volume.
 (3) G2b ratio for every candidate E-SKR2 headline b on the grid vs E-PF b 0 (which headline b's would have tripped).
 (4) bootstrap CIs of the two guard statistics (test relP@2 delta: image boot; E1 crack-free px ratio: cluster boot), b 0 and headline.
 (5) any-hit image sign count at b 0 (exact two-sided sign test).
Usage: skr2e_extra.py OUT_DIR"""
import json, re, sys, math
from pathlib import Path
import numpy as np

D = Path(sys.argv[1]); CR = 14
MOD = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)
J = {(json.load(open(f))['run'], float(json.load(open(f))['bias'])): json.load(open(f))['cells'] for f in sorted(D.glob('E-*.b*.json'))}
U = sorted({b for _, b in J}); sw = json.load(open(D / 'skr2e_e1_sweep.json'))
P = {float(b): v for b, v in sw['E-PF'].items()}; S = {float(b): v for b, v in sw['E-SKR2'].items()}; G = sorted(P)
dec = json.load(open(D / 'skr2e_val_decisions.json')); hS = dec['E-SKR2']['headline_bias']; hP = dec['E-PF']['headline_bias']


def cm(c):
    m = np.asarray(c['conf'], np.int64); n = int(math.isqrt(m.size)); return m.reshape(n, n)


def tvec(cells, st):  # crack TP, FP, FN, rel2 (4), pred px, gt px
    out = []
    for s in st:
        m = cm(cells[s]); out.append([m[CR, CR], m[:, CR].sum() - m[CR, CR], m[CR, :].sum() - m[CR, CR], *cells[s]['crack_rel2'], m[:, CR].sum(), m[CR, :].sum()])
    return np.array(out, np.float64)


def tp(Sv):
    Pp, R = Sv[3] / Sv[4], Sv[5] / Sv[6]
    return dict(iou=Sv[0] / Sv[:3].sum(), relF1=2 * Pp * R / (Pp + R), relP=Pp, vol=Sv[7] / Sv[8])


test = sorted(J[('E-PF', 0.0)]['test']); ext = sorted(J[('E-PF', 0.0)]['ext'])
print('## (1) test bias share (all 50; E-PF stored at U only, so linear in pred/GT between U points; E-PF curve is concave in b, so the remaining gap is an upper bound)')
TP = {b: tp(tvec(J[('E-PF', b)]['test'], test).sum(0)) for b in U}; TS = tp(tvec(J[('E-SKR2', 0.0)]['test'], test).sum(0))
print('  E-PF: ' + ' | '.join(f'b{b:g} vol {TP[b]["vol"]:.3f} IoU {TP[b]["iou"]:.4f} relF1 {TP[b]["relF1"]:.4f} relP {TP[b]["relP"]:.4f}' for b in U))
print(f'  E-SKR2 b0: vol {TS["vol"]:.3f} IoU {TS["iou"]:.4f} relF1 {TS["relF1"]:.4f} relP {TS["relP"]:.4f}')
for i in range(len(U) - 1):
    a, b = U[i], U[i + 1]
    if TP[a]['vol'] <= TS['vol'] <= TP[b]['vol']:
        t = (TS['vol'] - TP[a]['vol']) / (TP[b]['vol'] - TP[a]['vol']); ip = lambda q: TP[a][q] + t * (TP[b][q] - TP[a][q])
        g0 = (TS['iou'] - TP[0.0]['iou'], TS['relF1'] - TP[0.0]['relF1'])
        print(f'  matched test volume: E-PF ~b {a + t * (b - a):.2f}: IoU {ip("iou"):.4f} relF1 {ip("relF1"):.4f} relP {ip("relP"):.4f} -> gap left IoU {TS["iou"] - ip("iou"):+.4f} '
              f'({(TS["iou"] - ip("iou")) / g0[0] * 100:.0f}% of {g0[0]:+.4f}), relF1 {TS["relF1"] - ip("relF1"):+.4f} ({(TS["relF1"] - ip("relF1")) / g0[1] * 100:.0f}% of {g0[1]:+.4f}); relP {TS["relP"] - ip("relP"):+.4f}')
print('\n## (2) E1 sweep: equal-b gap and matched-volume gap, E-SKR2 at each grid b (relF1 / any-hit / crack-free px)')
pv = [P[b]['pred_over_gt'] for b in G]
for b in G:
    r = S[b]['pred_over_gt']; eq = (S[b]['relF1'] - P[b]['relF1'], S[b]['anyhit'] - P[b]['anyhit'], S[b]['crack_free_px'] - P[b]['crack_free_px'])
    if pv[0] <= r <= pv[-1]:
        j = max(i for i in range(len(G) - 1) if pv[i] <= r); t = (r - pv[j]) / (pv[j + 1] - pv[j]); ip = lambda q: P[G[j]][q] + t * (P[G[j + 1]][q] - P[G[j]][q])
        mv = f'E-PF ~b {G[j] + t * 0.25:.2f}: {S[b]["relF1"] - ip("relF1"):+.4f} / {S[b]["anyhit"] - ip("anyhit"):+.4f} / {S[b]["crack_free_px"] - ip("crack_free_px"):+.0f}'
    else:
        mv = 'outside E-PF grid volume'
    print(f'  SKR2 b{b:g} (vol {r:.3f}): equal-b {eq[0]:+.4f} / {eq[1]:+.4f} / {eq[2]:+d} | matched volume {mv}')
print(f'  E-PF best E1 relF1 over the grid: {max(P[b]["relF1"] for b in G):.4f} at b {max(G, key=lambda b: P[b]["relF1"]):g} (vol {P[max(G, key=lambda b: P[b]["relF1"])]["pred_over_gt"]:.3f}); E-SKR2 b0 {S[0.0]["relF1"]:.4f} (vol {S[0.0]["pred_over_gt"]:.3f})')
print('\n## (3) G2b (E1 crack-free px vs E-PF b 0 = %d; bar x1.5 = %.0f) for every candidate E-SKR2 headline b on the grid' % (P[0.0]['crack_free_px'], 1.5 * P[0.0]['crack_free_px']))
print('  ' + ' '.join(f'{b:g}:x{S[b]["crack_free_px"] / P[0.0]["crack_free_px"]:.2f}{"T" if S[b]["crack_free_px"] > 1.5 * P[0.0]["crack_free_px"] else ""}' for b in G) + '   (T = trip)')
vs = {b: v for b, v in dec['E-SKR2']['sweep'].items()}
print('  E-SKR2 val D2 path: ' + ' '.join(f'{b}: relR {v["relR2"]:.4f} relP {v["relP2"]:.4f} drop {vs["0.0"]["crack_P"] - v["crack_P"]:+.4f}' for b, v in vs.items() if float(b) <= 1.25))
print('\n## (4) guard statistics with bootstrap CIs (2,000, seed 0): test relP@2 delta (image boot, all 50), E1 crack-free px ratio (71-cluster boot)')
for bP, bS, lab in ((0.0, 0.0, 'b 0'), (hP, hS, 'headline pair')):
    A, B = tvec(J[('E-PF', bP)]['test'], test), tvec(J[('E-SKR2', bS)]['test'], test); rng = np.random.default_rng(0); d = []
    for _ in range(2000):
        ix = rng.integers(0, len(test), len(test)); d.append(B[ix].sum(0)[3] / B[ix].sum(0)[4] - A[ix].sum(0)[3] / A[ix].sum(0)[4])
    full = B.sum(0)[3] / B.sum(0)[4] - A.sum(0)[3] / A.sum(0)[4]
    cf = lambda cells: np.array([cm(cells[s])[:, CR].sum() if cm(cells[s])[CR].sum() == 0 else 0 for s in ext], np.float64)
    fa, fb = cf(J[('E-PF', bP)]['ext']), cf(J[('E-SKR2', bS)]['ext']); gs = sorted({MOD(s) for s in ext}); lab_ = np.array([gs.index(MOD(s)) for s in ext])
    ca, cb = np.bincount(lab_, fa, len(gs)), np.bincount(lab_, fb, len(gs)); rng = np.random.default_rng(0); q = []
    for _ in range(2000):
        w = np.bincount(rng.integers(0, len(gs), len(gs)), minlength=len(gs)); q.append((w @ cb) / max(w @ ca, 1))
    print(f'  {lab} (E-PF b{bP:g}, E-SKR2 b{bS:g}): G2a relP@2 {full:+.4f} [{np.percentile(d, 2.5):+.4f}, {np.percentile(d, 97.5):+.4f}] P(< -0.03) {np.mean(np.array(d) < -0.03):.3f} | '
          f'G2b x{cb.sum() / ca.sum():.2f} [x{np.percentile(q, 2.5):.2f}, x{np.percentile(q, 97.5):.2f}] P(> 1.5) {np.mean(np.array(q) > 1.5):.3f}; '
          f'crack-free FA px by top clusters SKR2: ' + ', '.join(f'{gs[i]} {int(cb[i])} (PF {int(ca[i])})' for i in np.argsort(-cb)[:4]))
print('\n## (5) any-hit at b 0 by image')
h = lambda cells: {g: [0, 0] for g in sorted({MOD(s) for s in ext})}
HA, HB = h(None), h(None)
for s in ext:
    for H, k in ((HA, 'E-PF'), (HB, 'E-SKR2')):
        g = [e for e in J[(k, 0.0)]['ext'][s]['crack_cc']['gt'] if e[0] >= 20]; H[MOD(s)][0] += sum(1 for e in g if e[1] >= 1); H[MOD(s)][1] += len(g)
dd = [HB[g][0] - HA[g][0] for g in HA if HA[g][1] > 0]; npos, nneg = sum(x > 0 for x in dd), sum(x < 0 for x in dd)
p = sum(math.comb(npos + nneg, k) for k in range(0, min(npos, nneg) + 1)) * 2 / 2 ** (npos + nneg)
print(f'  images with GT comps {len(dd)}: SKR2 more hits in {npos}, fewer in {nneg}, equal {len(dd) - npos - nneg}; exact two-sided sign p {min(p, 1):.3f}')
