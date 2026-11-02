"""coach (2 Nov): independent recompute of protocol_B6 §4 (own code, numpy; not b6_verdict.py).
Input: the 20 <run>.b6.json files (b6_score.py --mode b6: cells['heldout'][stem] in m0 format), b6_folds.tsv (e2cafce1), b6_groups.tsv
(5ff33e20). Keys (arm, fold, seed) are parsed from the run name b6_{SUP,SUPPF}_f<k>_s<seed> and cross-checked with the file's fields.
Primary: per (arm, seed) pooled out-of-fold inactive IoU over the 532 cells = TP / (GT + PRED - TP) from conf (rows GT, cols pred,
argmax); delta = mean over seeds 5, 6 of PF - house. CI: two-stage paired bootstrap, 2,000 resamples, own RNG (seed 20261102):
(a) resample the 334 groups with replacement; (b) per (fold, arm) draw the seed from {5, 6}; pool counts per arm; delta* = PF - house.
95% percentile CI. PASS iff lo > 0 and delta >= 0.01; FAIL iff hi < 0; else n.d. Reported: one-stage CI (groups only, both seeds
kept, delta* = seed-mean PF - house), seed-pair deltas, crack IoU / relF1@2, per source, per fold, leave-top-3-groups-out (by
inactive px), twin groups (> 1 image id) vs rest, inactive component R / P (>= 20 px; found iff >= 50% covered; pred correct iff
any overlap), inactive FP on the zero-train-px classes in their held-out fold (belt_mark 19 / f0, rings 12 / f2, clamp 8 / f3).
Usage: python3 coach_b6.py run SCORES_DIR FOLDS_TSV GROUPS_TSV | python3 coach_b6.py selftest FOLDS_TSV GROUPS_TSV"""
import csv, json, re, sys, tempfile
from pathlib import Path
import numpy as np

NC, IN, CR, CMIN = 24, 11, 14, 20
ARMS, SEEDS, FOLDS = ('house', 'PF'), (5, 6), (0, 1, 2, 3, 4)
ZERO = {19: 0, 12: 2, 8: 3}


def rows(p):
    return list(csv.DictReader(open(p), delimiter='\t'))


def load(sdir, folds_tsv, groups_tsv):
    F = rows(folds_tsv); fold = {r['stem']: int(r['fold']) for r in F}; ipx = {r['stem']: int(r['inactive_px']) for r in F}
    G = rows(groups_tsv); grp = {r['stem']: r['phys_group'] for r in G}; img = {r['stem']: r['b6_module'] for r in G}
    assert len(fold) == 532 and set(grp) == set(fold)
    runs = {}
    for f in sorted(Path(sdir).glob('*.b6.json')):
        d = json.load(open(f)); m = re.fullmatch(r'b6_(SUP|SUPPF)_f(\d)_s(\d)', d['run'])
        assert m, d['run']; key = ('PF' if m.group(1) == 'SUPPF' else 'house', int(m.group(2)), int(m.group(3)))
        assert int(d['fold']) == key[1] and int(d['seed']) == key[2] and int(d['step']) == 20000, (f.name, d['fold'], d['seed'])
        cells = d['cells']['heldout']; assert set(cells) == {s for s, k in fold.items() if k == key[1]}, f.name
        assert key not in runs; runs[key] = cells
    assert len(runs) == 20, len(runs)
    for (a, k, s), cells in runs.items():
        for st, c in cells.items():
            C = np.asarray(c['conf']).reshape(NC, NC); assert C[IN].sum() == ipx[st], (a, k, s, st)
    return fold, grp, img, ipx, runs


def cstat(c):
    C = np.asarray(c['conf'], np.int64).reshape(NC, NC)
    gi = [g for g in c['inact_cc']['gt'] if g[0] >= CMIN]; pi = [p for p in c['inact_cc']['pr'] if p[0] >= CMIN]
    return {'in': np.array([C[IN, IN], C[:, IN].sum(), C[IN].sum()]), 'cr': np.array([C[CR, CR], C[:, CR].sum(), C[CR].sum()]),
            'rel': np.asarray(c['crack_rel2'], np.int64), 'icc': np.array([sum(g[1] >= 0.5 * g[0] for g in gi), len(gi), sum(p[1] > 0 for p in pi), len(pi)]),
            'zfp': {z: int(C[z, IN]) for z in ZERO}, 'zgt': {z: int(C[z].sum()) for z in ZERO}}


iou = lambda t: t[0] / max(t[2] + t[1] - t[0], 1)


def relf1(r):
    p, q = r[0] / max(r[1], 1), r[2] / max(r[3], 1); return 2 * p * q / max(p + q, 1e-12)


def analyse(fold, grp, img, ipx, runs, B=2000, seed=20261102, quiet=False):
    S = {k: {st: cstat(c) for st, c in v.items()} for k, v in runs.items()}
    cell_of = lambda a, s: {st: S[(a, fold[st], s)][st] for st in fold}
    CS = {(a, s): cell_of(a, s) for a in ARMS for s in SEEDS}
    pool = lambda a, s, stems, key='in': np.sum([CS[(a, s)][st][key] for st in stems], 0)
    allst = sorted(fold)
    I = {(a, s): iou(pool(a, s, allst)) for a in ARMS for s in SEEDS}
    delta = np.mean([I[('PF', s)] for s in SEEDS]) - np.mean([I[('house', s)] for s in SEEDS])
    gl = sorted(set(grp.values())); gi = {g: i for i, g in enumerate(gl)}; ng = len(gl)
    gfold = np.zeros(ng, int); cnt = np.zeros((2, 2, ng, 3), np.int64)
    for st in allst:
        g = gi[grp[st]]; gfold[g] = fold[st]
        for ai, a in enumerate(ARMS):
            for si, s in enumerate(SEEDS):
                cnt[ai, si, g] += CS[(a, s)][st]['in']
    rng = np.random.default_rng(seed); two, one = [], []
    for _ in range(B):
        mult = np.bincount(rng.integers(0, ng, ng), minlength=ng)
        sd = rng.integers(0, 2, (5, 2))  # (fold, arm)
        tot = [np.einsum('g,gk->k', mult, cnt[ai, sd[gfold, ai], np.arange(ng)]) for ai in range(2)]
        two.append(iou(tot[1]) - iou(tot[0]))
        per = [[iou(np.einsum('g,gk->k', mult, cnt[ai, si])) for si in range(2)] for ai in range(2)]
        one.append(np.mean(per[1]) - np.mean(per[0]))
    lo, hi = np.percentile(two, [2.5, 97.5]); lo1, hi1 = np.percentile(one, [2.5, 97.5])
    verdict = 'PASS' if (lo > 0 and delta >= 0.01) else ('FAIL' if hi < 0 else 'n.d.')
    res = {'I': {f'{a}_s{s}': round(v, 4) for (a, s), v in I.items()}, 'delta': delta, 'ci2': (lo, hi), 'ci1': (lo1, hi1), 'verdict': verdict}
    if quiet:
        return res
    print(f'## primary: pooled OOF inactive IoU (532 cells): ' + ' '.join(f'{a} s{s} {I[(a, s)]:.4f}' for a in ARMS for s in SEEDS))
    print(f'  delta (PF - house, seed means) {delta:+.4f}; two-stage CI [{lo:+.4f}, {hi:+.4f}] (own RNG, 2,000) -> **{verdict}** '
          f'(PASS iff lo > 0 and delta >= 0.01; FAIL iff hi < 0)')
    print(f'  [reported] one-stage CI [{lo1:+.4f}, {hi1:+.4f}]; seed-pair deltas s5 {I[("PF", 5)] - I[("house", 5)]:+.4f}, s6 {I[("PF", 6)] - I[("house", 6)]:+.4f}')
    cr = {k: np.mean([iou(pool('PF', s, allst, 'cr')) for s in SEEDS]) - np.mean([iou(pool('house', s, allst, 'cr')) for s in SEEDS]) for k in [0]}
    rf = np.mean([relf1(pool('PF', s, allst, 'rel')) for s in SEEDS]) - np.mean([relf1(pool('house', s, allst, 'rel')) for s in SEEDS])
    print(f'  [reported] crack IoU delta {cr[0]:+.4f}; crack relF1@2 delta {rf:+.4f}')
    ic = {a: np.mean([pool(a, s, allst, 'icc') for s in SEEDS], 0) for a in ARMS}
    print('  [reported] inactive comp R / P: ' + ' | '.join(f'{a} {ic[a][0] / max(ic[a][1], 1):.3f} / {ic[a][2] / max(ic[a][3], 1):.3f}' for a in ARMS))
    sub = lambda keep: np.mean([iou(pool('PF', s, [x for x in allst if keep(x)])) for s in SEEDS]) - np.mean([iou(pool('house', s, [x for x in allst if keep(x)])) for s in SEEDS])
    print('  [reported] per source: ' + ' | '.join(f'{q} {sub(lambda x, q=q: x.startswith(q)):+.4f}' for q in ('ARTS', 'BMRK', 'CFVS', 'CSIR', 'SDLE')
                                                    if any(x.startswith(q) and ipx[x] > 0 for x in allst)))
    print('  [reported] per fold (delta, PF / house seed means): ' + ' | '.join(
        f'f{k} {sub(lambda x, k=k: fold[x] == k):+.4f}' for k in FOLDS))
    gpx = {}
    for st in allst:
        gpx[grp[st]] = gpx.get(grp[st], 0) + ipx[st]
    top3 = sorted(gpx, key=lambda g: -gpx[g])[:3]
    print(f'  [reported] leave-top-3-groups-out ({", ".join(top3)}): {sub(lambda x: grp[x] not in top3):+.4f}')
    twins = {g for g in gpx if len({img[x] for x in allst if grp[x] == g}) > 1}
    print(f'  [reported] twin groups ({len(twins)}): {sub(lambda x: grp[x] in twins):+.4f} | rest {sub(lambda x: grp[x] not in twins):+.4f}')
    for z, k in ZERO.items():
        st_k = [x for x in allst if fold[x] == k]
        v = {(a, s): sum(CS[(a, s)][x]['zfp'][z] for x in st_k) for a in ARMS for s in SEEDS}
        gt = sum(CS[('house', 5)][x]['zgt'][z] for x in st_k)
        print(f'  [reported] class {z} (fold {k}, GT px {gt}): inactive predicted on it: ' + ' '.join(f'{a} s{s} {v[(a, s)]}' for a in ARMS for s in SEEDS))
    return res


def selftest(folds_tsv, groups_tsv):
    F = rows(folds_tsv); rng = np.random.default_rng(1); ok = True
    def fake(dirp, gain=0.0):
        for a in ARMS:
            for s in SEEDS:
                for k in FOLDS:
                    cells = {}
                    for r in F:
                        if int(r['fold']) != k:
                            continue
                        C = np.zeros((NC, NC), np.int64); g = int(r['inactive_px'])
                        frac = 0.5 + (gain if a == 'PF' else 0.0)
                        tp = int(round(g * frac)); C[IN, IN] = tp; C[IN, 0] = g - tp; C[0, IN] = int(g * 0.2)
                        C[0, 0] = 262144 - C.sum()
                        cells[r['stem']] = {'conf': C.ravel().tolist(), 'crack_rel2': [0, 0, 0, 0], 'crack_cc': {'gt': [], 'pr': []}, 'inact_cc': {'gt': [], 'pr': []}}
                    name = f'b6_{"SUPPF" if a == "PF" else "SUP"}_f{k}_s{s}'
                    json.dump({'run': name, 'fold': k, 'seed': s, 'step': 20000, 'cells': {'heldout': cells}}, open(f'{dirp}/{name}.b6.json', 'w'))
    for gain, exp in ((0.0, 'n.d.'), (0.1, 'PASS'), (-0.1, 'FAIL')):
        with tempfile.TemporaryDirectory() as d:
            fake(d, gain); r = analyse(*load(d, folds_tsv, groups_tsv), B=300, quiet=True)
            tot = sum(int(x['inactive_px']) for x in F)
            hand = (lambda f: sum(round(int(x['inactive_px']) * f) for x in F) / (tot + sum(int(int(x['inactive_px']) * 0.2) for x in F)))
            h = hand(0.5 + gain) - hand(0.5)
            p = r['verdict'] == exp and abs(r['delta'] - h) < 1e-9 and (gain != 0 or r['ci2'] == (0.0, 0.0))
            ok &= p; print(f'  selftest gain {gain:+.1f}: delta {r["delta"]:+.6f} (hand {h:+.6f}) CI {tuple(round(x, 4) for x in r["ci2"])} {r["verdict"]} (exp {exp}) -> {"ok" if p else "FAIL"}')
    print('SELFTEST', 'PASS' if ok else 'FAIL'); return ok


if __name__ == '__main__':
    if sys.argv[1] == 'selftest':
        sys.exit(0 if selftest(sys.argv[2], sys.argv[3]) else 1)
    analyse(*load(sys.argv[2], sys.argv[3], sys.argv[4]))
