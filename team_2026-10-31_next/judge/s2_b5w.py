#!/usr/bin/env python3
"""judge s2_b5w (2 Nov 2026): own-code B5 on the wide grid for protocol_SKR2_HC2 §3a.2 + a width-robust E1 detection check.
Reads only the opening's calib-format records (rec_w/<run>.{val,test,ext}.json; gt_cc = [size, v50, vany]: found at b iff v50 + b > 0,
any-hit at b iff vany + b > 0). Imports no el_metrics / s2_* / coach code.
  OP rule (calib): on OPGRID b = -8.0..+12.0 step 0.1 (0.75 excluded), max val recall s.t. val precision >= 0.90, ties -> smaller b;
  unreachable -> max-precision b (ties -> smaller b), flagged. Arm-pooled OP = the 5 seeds' val cells pooled. Co-primaries
  (test, two-set rule): comp recall (GT comps >= 20 px found at >= 50%) at the comp OP (comp P = pred comps >= 20 px hitting GT-near
  / all pred comps >= 20 px), relR@2 at the rel OP. Rule 1 /3 vs base. Per-run OPs reported.
  Width check (descriptive): base arm's E1 curve over b (pooled 5 seeds): pred/GT crack px, any-hit, >= 50% found, crack px on E1
  GT-crack-free cells, relP@2; the test arm at b 0 placed on it (base at the b with equal E1 pred/GT, and at equal crack-free px).
Usage: s2_b5w.py --arm NAME RECDIR PREFIX [--arm ...] --base NAME
"""
import argparse, json, math
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('--arm', nargs=3, action='append', required=True)
ap.add_argument('--base', required=True)
ap.add_argument('--seeds', nargs='+', type=int, default=[5, 6, 7, 8, 9])
a = ap.parse_args()
NOISY = 'CSIR_00070_r8_c4'
R = {}
GRID = None
for name, d, pre in a.arm:
    R[name] = {}
    for st in ('val', 'test', 'ext'):
        L = []
        for k in a.seeds:
            j = json.load(open(f'{d}/{pre}_100pct_s{k}.{st}.json'))
            g = np.array(j['grid'], float)
            if GRID is None: GRID = g
            assert np.array_equal(g, GRID), (name, st, k)
            L.append(j['cells'])
        R[name][st] = L
    print(f'# {name}: {pre}_100pct_s{a.seeds}; val/test/ext cells {[len(R[name][s][0]) for s in ("val", "test", "ext")]}')
OPG = (GRID >= -8 - 1e-9) & (GRID <= 12 + 1e-9) & (np.abs(np.round(GRID * 10) - GRID * 10) < 1e-6)
print(f'# grid {len(GRID)} points {GRID[0]}..{GRID[-1]}, OP grid {OPG.sum()} points, 0.75 in grid {0.75 in GRID}')
i0 = int(np.argmin(np.abs(GRID)))
assert abs(GRID[i0]) < 1e-9


def cv(cellsets, keep=lambda s: True):
    cs = [c for cells in cellsets for s, c in cells.items() if keep(s)]
    S = lambda k: np.sum([np.asarray(c[k], np.int64) for c in cs], 0)
    pred, rp, rr = S('pred'), S('relp_tp'), S('relr_tp'); ng = sum(c['n_gt'] for c in cs)
    gc = [x for c in cs for x in c['gt_cc'] if x[0] >= 20]
    v50 = np.array([x[1] for x in gc]); vany = np.array([x[2] for x in gc])
    f50 = np.array([(v50 + b > 0).mean() for b in GRID]) if len(gc) else np.full(len(GRID), np.nan)
    fany = np.array([(vany + b > 0).mean() for b in GRID]) if len(gc) else np.full(len(GRID), np.nan)
    free = np.sum([np.asarray(c['pred'], np.int64) for c in cs if c['n_gt'] == 0], 0) if any(c['n_gt'] == 0 for c in cs) else np.zeros(len(GRID))
    dv = lambda x, y: np.where(y > 0, x / np.maximum(y, 1), np.nan)
    return dict(relP=dv(rp, pred), relR=rr / max(ng, 1), compR=f50, anyhit=fany, compP=dv(S('pc20_hit'), S('pc20_n')),
                predGT=pred / max(ng, 1), free=free, ngc=len(gc), ng=ng)


def op(c, rk, pk):
    cand = np.where(OPG)[0]
    P = np.nan_to_num(c[pk][cand], nan=-1)
    ok = cand[P >= 0.90]
    if len(ok):
        best = c[rk][ok].max(); j = min(i for i in ok if c[rk][i] == best); return j, True
    best = P.max(); j = min(i for i, p in zip(cand, P) if p == best); return j, False


def rule(xa, xb):
    xa, xb = np.asarray(xa, float), np.asarray(xb, float); d = xb.mean() - xa.mean()
    thr = max(0.01, 2 * math.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    return d, thr, 'BETTER' if d > thr else ('WORSE' if d < -thr else 'n.d.')


SETS = (('test50', 'test', lambda s: True), ('test49', 'test', lambda s: s != NOISY), ('E1', 'ext', lambda s: True))
OUT = {}
for n in R:
    pv = cv(R[n]['val']); jc, rc = op(pv, 'compR', 'compP'); jr, rr_ = op(pv, 'relR', 'relP')
    per = [(op(cv([R[n]['val'][i]]), 'compR', 'compP'), op(cv([R[n]['val'][i]]), 'relR', 'relP')) for i in range(len(a.seeds))]
    OUT[n] = dict(bc=GRID[jc], br=GRID[jr], reach=(rc, rr_), per=[(GRID[x[0][0]], x[0][1], GRID[x[1][0]], x[1][1]) for x in per])
    for lab, st, kp in SETS:
        for mode in ('pooled', 'perrun'):
            vals = []
            for i in range(len(a.seeds)):
                c = cv([R[n][st][i]], kp)
                jc_, jr_ = (jc, jr) if mode == 'pooled' else (per[i][0][0], per[i][1][0])
                vals.append((c['compR'][jc_], c['compP'][jc_], c['relR'][jr_], c['relP'][jr_]))
            OUT[n][(lab, mode)] = np.array(vals)
    print(f'{n}: pooled OP b_comp {OUT[n]["bc"]:+.1f} b_rel {OUT[n]["br"]:+.1f} reachable {OUT[n]["reach"]} | val pooled compP {pv["compP"][jc]:.4f} '
          f'compR {pv["compR"][jc]:.4f} relP {pv["relP"][jr]:.4f} relR {pv["relR"][jr]:.4f} | per-run b_comp '
          + '/'.join(f'{x[0]:+.1f}{"" if x[1] else "U"}' for x in OUT[n]['per']) + ' b_rel ' + '/'.join(f'{x[2]:+.1f}{"" if x[3] else "U"}' for x in OUT[n]['per']))
B = a.base
print('\n## B5 co-primaries (arm-pooled OP; per run at that OP; rule 1 vs base) and per-run OPs (reported)')
for lab, _, _ in SETS:
    for mode in ('pooled', 'perrun'):
        for k, (iv, ip, nm, pn) in {'comp': (0, 1, 'compR', 'compP'), 'rel': (2, 3, 'relR@2', 'relP@2')}.items():
            line = f'{mode:6s} {lab:6s} {nm:7s}: ' + ' | '.join(f'{n} {OUT[n][(lab, mode)][:, iv].mean():.4f} ({pn} {OUT[n][(lab, mode)][:, ip].mean():.3f})' for n in R)
            for n in R:
                if n != B:
                    d, thr, v = rule(OUT[B][(lab, mode)][:, iv], OUT[n][(lab, mode)][:, iv]); line += f' || {n}-{B} {d:+.4f} thr {thr:.4f} {v}'
            print(line)
            if mode == 'pooled' and lab.startswith('test'):
                for n in R:
                    print(f'     per-seed {n}: ' + ' '.join(f'{x:.4f}' for x in OUT[n][(lab, mode)][:, iv]))

print('\n## width-robust E1 detection (descriptive; records, 5 seeds pooled per arm)')
E = {n: cv(R[n]['ext']) for n in R}
for n in R:
    print(f'{n} at b 0: E1 pred/GT {E[n]["predGT"][i0]:.4f} any-hit {E[n]["anyhit"][i0]:.4f} >=50% {E[n]["compR"][i0]:.4f} relP@2 {E[n]["relP"][i0]:.4f} '
          f'relR@2 {E[n]["relR"][i0]:.4f} crack-free px/run {E[n]["free"][i0] / len(a.seeds):.0f} (GT comps {E[n]["ngc"]}, GT px {E[n]["ng"]})')
cb = E[B]
print(f'{B} E1 curve (b: pred/GT any-hit >=50% free/run relP):')
for b in (-2, -1, 0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8):
    j = int(np.argmin(np.abs(GRID - b)))
    print(f'   b {GRID[j]:+.1f}: {cb["predGT"][j]:.4f} {cb["anyhit"][j]:.4f} {cb["compR"][j]:.4f} {cb["free"][j] / len(a.seeds):7.0f} {cb["relP"][j]:.4f}')
for n in R:
    if n == B: continue
    t = E[n]
    j = int(np.argmin(np.abs(cb['predGT'] - t['predGT'][i0])))
    jf = int(np.argmin(np.abs(cb['free'] - t['free'][i0])))
    print(f'{n} b 0 vs {B} at equal E1 pred/GT (b {GRID[j]:+.1f}, pred/GT {cb["predGT"][j]:.4f}): any-hit {t["anyhit"][i0]:.4f} vs {cb["anyhit"][j]:.4f} '
          f'(d {t["anyhit"][i0] - cb["anyhit"][j]:+.4f}), >=50% {t["compR"][i0]:.4f} vs {cb["compR"][j]:.4f}, relP@2 {t["relP"][i0]:.4f} vs {cb["relP"][j]:.4f}, '
          f'crack-free px/run {t["free"][i0] / len(a.seeds):.0f} vs {cb["free"][j] / len(a.seeds):.0f}')
    print(f'   vs {B} at equal crack-free px (b {GRID[jf]:+.1f}): any-hit {t["anyhit"][i0]:.4f} vs {cb["anyhit"][jf]:.4f} (d {t["anyhit"][i0] - cb["anyhit"][jf]:+.4f}), '
          f'pred/GT {t["predGT"][i0]:.4f} vs {cb["predGT"][jf]:.4f}')
    # per seed: each test-arm seed at b 0 vs each base seed at the b matching that seed-pair's pred/GT (mean over pairs)
    ds = []
    for i in range(len(a.seeds)):
        ti = cv([R[n]['ext'][i]])
        for q in range(len(a.seeds)):
            bq = cv([R[B]['ext'][q]]); jj = int(np.argmin(np.abs(bq['predGT'] - ti['predGT'][i0])))
            ds.append(ti['anyhit'][i0] - bq['anyhit'][jj])
    ds = np.array(ds)
    print(f'   seed-pair matched-volume any-hit d: mean {ds.mean():+.4f}, {np.mean(ds > 0):.2f} of 25 pairs > 0, min {ds.min():+.4f} max {ds.max():+.4f}')
