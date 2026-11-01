#!/usr/bin/env python3
"""judge (1 Nov): THIN-B3 adversarial extras (descriptive; never a verdict). Own code on opening files.
A. Volume / width proxy: pred crack px / GT crack px (crack_rel2 c1 / c3) and pixel P vs relP@2 gap, test and E1;
   E1 relR@2 vs component recall (detection vs fattening).
B. B5 pooled-OP stability (SKR / CLD vs base): val pooled precision margin at the chosen b; leave-one-seed-out pooled OPs
   (contrast range over the 5 LOSO choices x the base's 5); test precision reached at the OP per arm (matched precision?).
C. B3: scuff_train_iou JSONs (scuff IoU, crack_on_scuff, p_scuff ratio), E1 'scuff' dicts in m0 ext cells (crack on scuff,
   scuff predicted), specificity: change of crack px ON scuff vs crack px OFF scuff in the same 38 cells and in the other cells.
Usage: thin_extra.py --arm NAME M0 PREFIX REC ... --base SUPPF [--b3 B3 --scuff-dir DIR --cmp-scuff-m0 DIR]
"""
import argparse, json, math, glob, os
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('--arm', nargs=4, action='append'); ap.add_argument('--base', required=True)
ap.add_argument('--seeds', nargs='+', type=int, default=[5, 6, 7, 8, 9])
ap.add_argument('--b3'); ap.add_argument('--scuff-dir'); ap.add_argument('--cmp-scuff-m0')
a = ap.parse_args()
ARM = {n: (d, p, r) for n, d, p, r in a.arm}
def m0(n, k): d, p, _ = ARM[n]; return json.load(open(f'{d}/{p}_{n}_100pct_s{k}.json'))
def rel(cells, keep=lambda s: True):
    return np.sum([c['crack_rel2'] for s, c in cells.items() if keep(s)], 0).astype(float)

print('## A. volume / width proxy (argmax): pred/GT crack px, relP@2 - pixel P gap (fattening shows as a larger gap), E1 relR@2 vs comp recall')
for st in ('test', 'ext'):
    for n in ARM:
        v, g, rr, cr = [], [], [], []
        for k in a.seeds:
            c = m0(n, k)['cells'][st]; r = rel(c)
            M = sum(np.asarray(x['conf'], np.int64).reshape(int(math.isqrt(len(x['conf']))), -1)[:24, :24] for x in c.values())
            P = M[14, 14] / max(M[:, 14].sum(), 1)
            v.append(r[1] / r[3]); g.append(r[0] / r[1] - P); rr.append(r[2] / r[3])
            gt = [x for cc in c.values() for x in cc['crack_cc']['gt'] if x[0] >= 20]
            cr.append(np.mean([x[1] >= math.ceil(0.5 * x[0]) for x in gt]))
        print(f'  {st:4s} {n:6s} pred/GT {np.mean(v):.3f} (sd {np.std(v, ddof=1):.3f}) | relP-P gap {np.mean(g):.3f} | relR@2 {np.mean(rr):.4f} | compR {np.mean(cr):.4f}')

if all(r != '-' for _, _, r in ARM.values()):
    GRID = None
    def L(n, k, st): _, p, r = ARM[n]; return json.load(open(f'{r}/{p}_{n}_100pct_s{k}.{st}.json'))
    def curves(cs):
        S = lambda key: np.sum([np.asarray(c[key], np.int64) for c in cs], 0)
        pred, rp, rr = S('pred'), S('relp_tp'), S('relr_tp'); ng = sum(c['n_gt'] for c in cs)
        gc = [x for c in cs for x in c['gt_cc'] if x[0] >= 20]
        f = np.array([[x[1] + b > 0 for b in GRID] for x in gc])
        dv = lambda x, y: np.where(y > 0, x / np.maximum(y, 1), np.nan)
        return dict(relP=dv(rp, pred), relR=dv(rr, np.full_like(rr, ng)), compR=f.mean(0), compP=dv(S('pc20_hit'), S('pc20_n')))
    def op(cv, rk, pk):
        ok = np.where(OPG & (np.nan_to_num(cv[pk], nan=-1) >= 0.90))[0]
        if not len(ok):  # unreachable: calib's frozen rule = max-precision b, ties to the smaller b (flagged by the caller's printout of val P)
            cand = np.where(OPG)[0]; bp = np.nanmax(cv[pk][cand]); return min([j for j in cand if cv[pk][j] == bp], key=lambda j: GRID[j])
        b = np.nanmax(cv[rk][ok]); return min([j for j in ok if cv[rk][j] == b], key=lambda j: GRID[j])
    V, T = {}, {}
    for n in ARM:
        for k in a.seeds:
            v = L(n, k, 'val'); V[n, k] = list(v['cells'].values()); T[n, k] = L(n, k, 'test')['cells']
            if GRID is None:
                GRID = np.array(v['grid'], float); OPG = (GRID >= -4 - 1e-9) & (GRID <= 12 + 1e-9) & (np.abs(np.round(GRID * 10) - GRID * 10) < 1e-6)
    print('\n## B. B5 pooled-OP stability')
    for rk, pk in (('compR', 'compP'), ('relR', 'relP')):
        for n in ARM:
            cv = curves([c for k in a.seeds for c in V[n, k]]); j = op(cv, rk, pk)
            tP = [curves(list(T[n, k].values()))[pk][j] for k in a.seeds]; tR = [curves(list(T[n, k].values()))[rk][j] for k in a.seeds]
            lo = [op(curves([c for kk in a.seeds if kk != k for c in V[n, kk]]), rk, pk) for k in a.seeds]
            # val precision margin: how far above 0.90 at j and at the next larger-recall b (j-1)
            print(f'  {rk}@{pk}>=0.90 {n:6s}: b {GRID[j]:.1f} | val {pk} {cv[pk][j]:.4f} {rk} {cv[rk][j]:.4f} | val {pk} at b+0.1 / b-0.1: '
                  f'{cv[pk][j + 1] if j + 1 < len(GRID) else np.nan:.4f} / {cv[pk][j - 1]:.4f} | LOSO b ' + '/'.join(f'{GRID[x]:.1f}' if x is not None else 'NA' for x in lo)
                  + f' | test {pk} at b {np.mean(tP):.4f} (seeds ' + ' '.join(f'{x:.3f}' for x in tP) + f') test {rk} {np.mean(tR):.4f}')
        # LOSO contrast range: each arm's OP re-chosen with one of its seeds left out; test values of all 5 seeds at that b
        for n in ARM:
            if n == a.base: continue
            ds = []
            for kb in a.seeds:
                jb = op(curves([c for kk in a.seeds if kk != kb for c in V[a.base, kk]]), rk, pk)
                for kn in a.seeds:
                    jn = op(curves([c for kk in a.seeds if kk != kn for c in V[n, kk]]), rk, pk)
                    xb = [curves(list(T[a.base, k].values()))[rk][jb] for k in a.seeds]
                    xn = [curves(list(T[n, k].values()))[rk][jn] for k in a.seeds]
                    d = np.mean(xn) - np.mean(xb); thr = max(0.01, 2 * math.sqrt((np.var(xb, ddof=1) + np.var(xn, ddof=1)) / 3))
                    ds.append((d, thr))
            dd = np.array(ds)
            print(f'  LOSO {rk} {n}-{a.base} (test all 50): delta min {dd[:, 0].min():+.4f} median {np.median(dd[:, 0]):+.4f} max {dd[:, 0].max():+.4f}; '
                  f'BETTER in {(dd[:, 0] > dd[:, 1]).sum()}/25, WORSE in {(dd[:, 0] < -dd[:, 1]).sum()}/25')

if a.b3:
    print('\n## C. B3 scuff')
    if a.scuff_dir:
        for f in sorted(glob.glob(f'{a.scuff_dir}/*.json')):
            j = json.load(open(f)); j.pop('cells', None)
            print('  ', os.path.basename(f), {k: (round(v, 6) if isinstance(v, float) else v) for k, v in j.items() if k in
                  ('step', 'scuff_px', 'crack_on_scuff', 'scuff_iou', 'tp', 'fp', 'fn', 'p_scuff_on_scuff_mean', 'p_scuff_other_mean', 'p_scuff_ratio', 'p_scuff_on_scuff_p90')})
    def sc(cells):
        on = sum(c['scuff']['crack_on_scuff'] for c in cells.values() if c.get('scuff'))
        spx = sum(c['scuff']['scuff_px'] for c in cells.values() if c.get('scuff'))
        sp = sum(c['scuff'].get('scuffpred_px', 0) for c in cells.values() if c.get('scuff'))
        spon = sum(c['scuff'].get('scuffpred_on_scuff', 0) for c in cells.values() if c.get('scuff'))
        sc_cells = [s for s, c in cells.items() if c.get('scuff') and c['scuff']['scuff_px'] > 0]
        pred_sc = sum(c['crack_rel2'][1] for s, c in cells.items() if s in sc_cells)
        pred_other = sum(c['crack_rel2'][1] for s, c in cells.items() if s not in sc_cells)
        return on, spx, sp, spon, len(sc_cells), pred_sc - on, pred_other
    rows = {}
    for n, src in ((a.b3, None), (a.base, a.cmp_scuff_m0)):
        rr = []
        for k in a.seeds:
            c = json.load(open(f'{src}/pf2_{n}_100pct_s{k}.json'))['cells']['ext'] if src else m0(n, k)['cells']['ext']
            rr.append(sc(c))
        rows[n] = np.array(rr, float)
        r = rows[n].mean(0)
        print(f'  E1 {n:6s}: crack on scuff px {r[0]:.0f} of {r[1]:.0f} scuff px ({r[4]:.0f} cells) | scuff predicted px {r[2]:.0f} (on GT scuff {r[3]:.0f}) | '
              f'crack px off-scuff in scuff cells {r[5]:.0f} | crack px in other E1 cells {r[6]:.0f}')
    b, s = rows[a.b3].mean(0), rows[a.base].mean(0)
    print(f'  B3 vs {a.base}: crack-on-scuff {100 * (b[0] / s[0] - 1):+.1f}% | off-scuff crack px in scuff cells {100 * (b[5] / s[5] - 1):+.1f}% | '
          f'crack px in other cells {100 * (b[6] / s[6] - 1):+.1f}%  (specific only if the first is clearly below the other two)')
    print('  per-seed crack-on-scuff B3 ' + ' '.join(f'{x:.0f}' for x in rows[a.b3][:, 0]) + f' | {a.base} ' + ' '.join(f'{x:.0f}' for x in rows[a.base][:, 0]))
