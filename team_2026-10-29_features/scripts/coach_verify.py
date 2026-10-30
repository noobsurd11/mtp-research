"""coach verifier (29 Oct). Independent of runner's analysis code.
Input: per-cell JSONs in m0_audit format: {'run','step','code_revision'?, 'cells': {'test'|'val': {stem: {'conf': 24x24 (gt rows, pred cols), 'crack_rel2': [tpP, nP, tpR, nR]}}}}
Usage: python coach_verify.py --base a1.json,..,a5.json --arm b1.json,..,b5.json [--boot 2000]
Prints: rule 1 (verdict: house divisor 3, ssl_rules.py cmp; /n seeds shown as descriptive) on test crack IoU, crack relF1@2, inactive IoU (+ mIoU_rob, crack P/R descriptive)
on the four cell sets and per source; the two-set verdict (all, noNoisy); width flag; paired bootstrap; leave-top-3-out."""
import argparse, hashlib, json
import numpy as np

NC, CR, IN = 24, 14, 11
NOISY = 'CSIR_00070_r8_c4'
TWINS = {'CFVS_00006_r5_c5', 'CFVS_00033_r8_c4', 'CFVS_00035_r8_c4', 'CFVS_00042_r8_c4',
         'CFVS_00018_r4_c4', 'CFVS_00027_r4_c4', 'ARTS_00020_r5_c1'}
ROB = [0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21]  # test robust class list (Track M)
SETS = {'all': lambda s: True, 'noNoisy': lambda s: s != NOISY,
        'noTwins': lambda s: s not in TWINS, 'noBoth': lambda s: s != NOISY and s not in TWINS}
SRC = {q: (lambda q: lambda s: s.startswith(q))(q) for q in ['ARTS', 'BMRK', 'CFVS', 'CSIR']}
PRIM = ['crack', 'relF1', 'inact']
DESC = ['mIoU_rob', 'cP', 'cR', 'relP', 'relR']


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()[:10]


def counts(d, keep, split='test'):
    C = np.zeros((NC, NC)); x = np.zeros(4)
    for s, c in d['cells'][split].items():
        if keep(s):
            C += np.asarray(c['conf'], float).reshape(NC, NC); x += np.asarray(c['crack_rel2'], float)
    return C, x


def metrics(C, x):
    tp = np.diag(C); g = C.sum(1); p = C.sum(0)
    iou = np.where(g > 0, tp / np.maximum(g + p - tp, 1), np.nan)
    rp = x[0] / max(x[1], 1); rr = x[2] / max(x[3], 1)
    return {'crack': iou[CR], 'inact': iou[IN], 'relF1': 2 * rp * rr / max(rp + rr, 1e-12),
            'mIoU_rob': np.nanmean(iou[ROB]), 'cP': tp[CR] / max(p[CR], 1), 'cR': tp[CR] / max(g[CR], 1),
            'relP': rp, 'relR': rr}


def rule1(a, b, div=None):
    sd = lambda v: np.std(v, ddof=1)
    div = div or 3  # verdict: house divisor 3 (team-lead ruling 29 Oct); pass div=n for the descriptive /n line
    thr = max(0.01, 2 * np.sqrt((sd(a) ** 2 + sd(b) ** 2) / div))
    dl = np.mean(b) - np.mean(a)
    return dl, thr, ('BETTER' if dl > thr else 'WORSE' if dl < -thr else 'nd')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base'); ap.add_argument('--arm'); ap.add_argument('--boot', type=int, default=2000)
    ap.add_argument('--e1ctx', default=None, help='scripts/e1_context.tsv: E1 (ext) secondary, split scuff_halfcut / other')
    a = ap.parse_args()
    fb, fa = a.base.split(','), a.arm.split(',')
    B = [json.load(open(f)) for f in fb]; A = [json.load(open(f)) for f in fa]
    print('base', [(d['run'], d.get('step'), d.get('code_revision', '?')[:8], md5(f)) for d, f in zip(B, fb)])
    print('arm ', [(d['run'], d.get('step'), d.get('code_revision', '?')[:8], md5(f)) for d, f in zip(A, fa)])
    bad = [d['run'] for d in A + B if d.get('step') != 20000]
    print('STEP CHECK', 'OK' if not bad else f'FAIL {bad}')
    stems = sorted(B[0]['cells']['test'])
    assert all(sorted(d['cells']['test']) == stems for d in A + B) and len(stems) == 50, 'test cell sets differ'

    verdict = {}
    for sn, f in list(SETS.items()) + list(SRC.items()):
        mb = [metrics(*counts(d, f)) for d in B]; ma = [metrics(*counts(d, f)) for d in A]
        row = []
        for k in PRIM + DESC:
            xa = [m[k] for m in mb]; xb = [m[k] for m in ma]
            dl, thr, v = rule1(xa, xb)
            _, thrn, vn = rule1(xa, xb, min(len(xa), len(xb)))
            if sn in SETS and k in PRIM:
                verdict[(sn, k)] = (dl, v)
            row.append(f'{k} {np.mean(xa):.4f}>{np.mean(xb):.4f} {dl:+.4f}({thr:.4f}){"" if k in DESC else " " + v + f" [/n {thrn:.4f} {vn}]"}')
        print(f'TEST {sn:8s} ' + ' | '.join(row))
        if sn in ('all', 'noNoisy'):
            drp = np.mean([m['relP'] for m in ma]) - np.mean([m['relP'] for m in mb])
            print(f'   width relP@2 {drp:+.4f}', 'FLAG' if drp < -0.05 else 'ok')

    # two-set verdict (all, noNoisy = clean co-primary): pass on both, or pass on one with same-sign nd on the other;
    # worse on either verdict set fails the arm.
    better, worse = [], []
    for k in PRIM:
        (d1, v1), (d2, v2) = verdict[('all', k)], verdict[('noNoisy', k)]
        if 'WORSE' in (v1, v2):
            worse.append(k)
        elif (v1 == 'BETTER' and (v2 == 'BETTER' or (v2 == 'nd' and d2 > 0))) or \
             (v2 == 'BETTER' and v1 == 'nd' and d1 > 0):
            better.append(k)
    print('VERDICT', 'BETTER' if better and not worse else 'WORSE' if worse else 'nd',
          f'better={better} worse={worse}')

    # E1 (ext, 106 cells): secondary, descriptive only (rule-1 arithmetic shown, never a verdict)
    if a.e1ctx and all('ext' in d['cells'] for d in A + B):
        ctx = dict(l.split('\t')[:2] for l in open(a.e1ctx) if l.strip())
        ext = sorted(B[0]['cells']['ext'])
        assert len(ext) == 106 and set(ext) <= set(ctx), 'E1 cell list mismatch'
        for gname, keep in [('E1 all', lambda s: True), ('E1 scuff_halfcut', lambda s: ctx[s] == 'scuff_halfcut'),
                            ('E1 other', lambda s: ctx[s] == 'other')]:
            mb = [metrics(*counts(d, keep, 'ext')) for d in B]; ma = [metrics(*counts(d, keep, 'ext')) for d in A]
            print(f'{gname:17s} ' + ' | '.join(
                f'{k} {np.mean([m[k] for m in mb]):.4f}>{np.mean([m[k] for m in ma]):.4f} %+.4f(%.4f) %s' % rule1([m[k] for m in mb], [m[k] for m in ma])
                for k in ['cR', 'crack', 'relR', 'inact']) + '  [descriptive]')
    elif a.e1ctx:
        print('E1: ext cells missing in some JSON')

    # paired image bootstrap of arm mean - base mean (pooled per run), and leave-top-3-out by GT area
    def stack(D):
        return (np.stack([[np.asarray(d['cells']['test'][s]['conf'], float).reshape(NC, NC) for s in stems] for d in D]),
                np.stack([[np.asarray(d['cells']['test'][s]['crack_rel2'], float) for s in stems] for d in D]))
    CB, XB = stack(B); CA, XA = stack(A)

    def mean_m(C, X, idx):
        out = [metrics(C[r, idx].sum(0), X[r, idx].sum(0)) for r in range(C.shape[0])]
        return np.array([np.mean([o[k] for o in out]) for k in PRIM])
    rng = np.random.default_rng(0)
    for sn in ('all', 'noNoisy'):
        idx0 = np.array([i for i, s in enumerate(stems) if SETS[sn](s)])
        pt = mean_m(CA, XA, idx0) - mean_m(CB, XB, idx0)
        D = np.array([mean_m(CA, XA, i) - mean_m(CB, XB, i) for i in (rng.choice(idx0, len(idx0)) for _ in range(a.boot))])
        print(f'BOOT {sn:6s} ' + ' | '.join(f'{k} {pt[j]:+.4f} [{np.nanpercentile(D[:, j], 2.5):+.4f},{np.nanpercentile(D[:, j], 97.5):+.4f}] P>0 {np.mean(D[:, j] > 0):.2f}' for j, k in enumerate(PRIM)))
        for j, (k, cl) in enumerate([('crack', CR), ('relF1', CR), ('inact', IN)]):
            gt = CB[0][:, cl, :].sum(1); top = set(np.argsort(-gt)[:3])
            keep = np.array([i for i in idx0 if i not in top])
            print(f'   top3-out {k} {(mean_m(CA, XA, keep) - mean_m(CB, XB, keep))[j]:+.4f}')


if __name__ == '__main__':
    main()
