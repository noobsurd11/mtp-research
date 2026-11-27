"""SKR2C named claim, condition 1 (protocol_SKR2C §3a 'Named claim, two tiers'; §6 stage 2): seed-aware two-stage bootstrap of E1 crack
relF1@2 on the 10 fresh singles at b 0 (argmax m0 per-cell files from R's pass 4), 2,000 draws, RNG seed 0, 71 module clusters asserted;
condition 1 holds iff the 95% CI is wholly above 0. Also reported (§4, never a verdict): the same bootstrap of each test co-primary (crack
IoU, relF1@2, inactive IoU; all 50 / clean 49) and of E1 any-hit / inactive / relP@2 / relR@2.
New file, pattern of coach's coach_s2_boot.py 7ea26cfb (results/s2/coach_v/diag/): feats / metr / boot verbatim; load() takes the run
lists from the command line instead of fixed paths; one pair (SKR01 - SUPPF). CPU, numpy only.
  Stage 1: draw clusters (test: modules; E1: source images) with replacement, same draw for both arms (paired over cells).
  Stage 2: draw 5 runs with replacement per arm, independently. Metric pooled per drawn run on the drawn cells; arm = mean of drawn runs.
--selftest: on the opened #5 files (PF2 m0 pf2_SUPPF s5-9, S2 m0 skr2_SKR01 s5-9) with coach's RNG 20261102, the three 'SKR01 - SUPPF'
  lines must equal coach's boot.txt lines exactly (test all 50, test clean 49, E1 106). Prints booleans only. exit 0 iff all equal.
Usage: python s2c_named_boot.py --base SUPPF M0 RUN x5 --arm SKR01 M0 RUN x5 [--seed 0] [--json OUT]
       python s2c_named_boot.py --selftest --base SUPPF PF2_M0 RUN x5 --arm SKR01 S2_M0 RUN x5 --ref-txt boot.txt
"""
import argparse, hashlib, json, re, sys
import numpy as np

NC, CR, IN, NOISY = 24, 14, 11, 'CSIR_00070_r8_c4'
ap = argparse.ArgumentParser()
ap.add_argument('--base', nargs=7, required=True, metavar='NAME_M0_RUNx5')
ap.add_argument('--arm', nargs=7, required=True, metavar='NAME_M0_RUNx5')
ap.add_argument('--seed', type=int, default=0); ap.add_argument('--n', type=int, default=2000); ap.add_argument('--json')
ap.add_argument('--selftest', action='store_true'); ap.add_argument('--ref-txt')
a = ap.parse_args()
ARMS = {x[0]: [f'{x[1]}/{r}.json' for r in x[2:]] for x in (a.base, a.arm)}
A_, B_ = a.base[0], a.arm[0]
clu = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)


def feats(c):  # coach_s2_boot.py 7ea26cfb, verbatim
    C = np.asarray(c['conf'], float).reshape(NC, NC); x = np.asarray(c['crack_rel2'], float)
    n = sum(1 for sz, h in c['crack_cc']['gt'] if sz >= 20); h = sum(1 for sz, hh in c['crack_cc']['gt'] if sz >= 20 and hh >= 1)
    return [C[CR, CR], C[CR].sum(), C[:, CR].sum(), C[IN, IN], C[IN].sum(), C[:, IN].sum(), x[0], x[1], x[2], x[3], n, h]


def metr(F):  # F (..., 12) summed  (verbatim)
    ci = F[..., 0] / np.maximum(F[..., 1] + F[..., 2] - F[..., 0], 1); ii = F[..., 3] / np.maximum(F[..., 4] + F[..., 5] - F[..., 3], 1)
    rp = F[..., 6] / np.maximum(F[..., 7], 1); rr = F[..., 8] / np.maximum(F[..., 9], 1); rf = 2 * rp * rr / np.maximum(rp + rr, 1e-12)
    ah = F[..., 11] / np.maximum(F[..., 10], 1)
    return {'crack': ci, 'relF1': rf, 'inact': ii, 'anyhit': ah, 'relP': rp, 'relR': rr}


def load(split, keep):  # coach's load(), run lists from the command line; + 5 runs per arm and 20000 steps asserted
    X = {}; stems = None
    for arm, ps in ARMS.items():
        runs = []; assert len(ps) == 5, (arm, len(ps))
        for p in ps:
            d = json.load(open(p)); assert d['step'] == 20000; cs = d['cells'][split]
            st = sorted(s for s in cs if keep(s)); stems = stems or st; assert st == stems, p
            runs.append(np.array([feats(cs[s]) for s in st]))
        X[arm] = np.stack(runs)  # (5, ncell, 12)
    cl = np.array([clu(s) for s in stems]); u, inv = np.unique(cl, return_inverse=True)
    return X, inv, len(u), len(stems)


def boot(X, inv, ncl, a, b, keys, B=2000, seed=20261102):  # verbatim
    rng = np.random.default_rng(seed); M = np.zeros((ncl, len(inv))); M[inv, np.arange(len(inv))] = 1
    pt = {k: metr(X[b].sum(1))[k].mean() - metr(X[a].sum(1))[k].mean() for k in keys}
    D = {k: [] for k in keys}
    for _ in range(B):
        w = np.bincount(rng.integers(0, ncl, ncl), minlength=ncl) @ M  # cell weights
        sa = rng.integers(0, 5, 5); sb = rng.integers(0, 5, 5)
        Fa = np.einsum('c,rcf->rf', w, X[a][sa]); Fb = np.einsum('c,rcf->rf', w, X[b][sb])
        ma, mb = metr(Fa), metr(Fb)
        for k in keys:
            D[k].append(mb[k].mean() - ma[k].mean())
    out = {}
    for k in keys:
        v = np.array(D[k]); out[k] = (pt[k], np.percentile(v, 2.5), np.percentile(v, 97.5), (v > 0).mean())
    return out


SPLITS = (('test', 'test all 50', lambda s: True, 48), ('test', 'test clean 49', lambda s: s != NOISY, 47), ('ext', 'E1 106', lambda s: True, 71))
seed = 20261102 if a.selftest else a.seed
lines, res = [], {}
for split, name, keep, ncl_exp in SPLITS:
    X, inv, ncl, n = load(split, keep); assert ncl == ncl_exp, (name, ncl)
    keys = ['crack', 'relF1', 'inact'] if split == 'test' else ['relF1', 'anyhit', 'inact', 'relP', 'relR']
    r = boot(X, inv, ncl, A_, B_, keys, B=a.n, seed=seed); res[name] = {k: [float(x) for x in v] for k, v in r.items()}
    head = f'## {name}: {n} cells, {ncl} clusters; seed-aware two-stage bootstrap, {a.n:,}, RNG {seed}'
    line = f'  {B_} - {A_}: ' + ' | '.join(f'{k} {v[0]:+.4f} [{v[1]:+.4f}, {v[2]:+.4f}] P>0 {v[3]:.2f}' for k, v in r.items())
    lines.append((head, line))
if a.selftest:
    ref = open(a.ref_txt).read().split('\n'); ok = True
    for head, line in lines:
        t = head in ref and line in ref and ref.index(line) > ref.index(head)
        ok &= t; print(f'selftest {head.split(":")[0][3:]}: header and SKR01 - SUPPF line == coach boot.txt (md5 {hashlib.md5(open(a.ref_txt, "rb").read()).hexdigest()[:8]}) {t}')
    print('SELFTEST', 'PASS' if ok else 'FAIL', '(opened #5 files: SUPPF s5-9, SKR01 s5-9; RNG 20261102)')
    sys.exit(0 if ok else 1)
e1 = res['E1 106']['relF1']; c1 = bool(e1[1] > 0)
for head, line in lines:
    print(head + ('  [test rows: REPORTED ONLY, protocol §4]' if head.startswith('## test') else '')); print(line)
print(f'\nNAMED CLAIM condition 1 (protocol_SKR2C §3a): seed-aware 95% CI of E1 crack relF1@2 ({B_} - {A_}, fresh singles s10-14, b 0, '
      f'2,000 draws, seed {seed}, 71 clusters) wholly above 0: {c1}')
print('(The claim also needs D\'s E1 relF1@2 primary to pass and neither R nor D to be FAIL; same 106 E1 cells, 3rd look.)')
if a.json:
    json.dump({'label': 'protocol_SKR2C §3a named claim condition 1 (+ §4 reported rows)', 'seed': seed, 'n': a.n, 'pair': f'{B_} - {A_}',
               'runs': ARMS, 'rows': res, 'condition1_ci_above_0': c1,
               'this_file_md5': hashlib.md5(open(__file__, 'rb').read()).hexdigest()}, open(a.json, 'w'), indent=1)
