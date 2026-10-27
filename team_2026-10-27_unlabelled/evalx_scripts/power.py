"""evalx Q1: seed vs cell variance, rule-1 thresholds, minimum detectable effects, scaling with test size.
CPU only, reads results/e1/raw_v2 (per-cell counts; they reproduce the re-score exactly per results/p16/README.md)."""
import sys
import numpy as np
from common import ARMS, load, pooled, METRICS, subset

rng = np.random.default_rng(0)
B = 2000
SUBS = ['all', 'clean']
data = {a: load(a) for a in ARMS}
cells0 = data['A100'][0]
for a in data:
    assert data[a][0] == cells0, a

# fixed bootstrap index draws (paired across arms)
BOOT = rng.integers(0, len(cells0), size=(B, len(cells0)))


def boot_mean(X, idx_base):
    """bootstrap distribution of the seed-mean pooled metric, resampling cells within idx_base"""
    n = len(idx_base)
    out = {m: np.empty(B) for m in METRICS}
    single = {m: np.empty(B) for m in METRICS}
    for b in range(B):
        idx = idx_base[BOOT[b, :n] % n]
        p = pooled(X, idx)
        for m in METRICS:
            out[m][b] = p[m].mean()
            single[m][b] = p[m][0]
    return out, single


print('# 1. Per arm: mean, seed sd, cell-bootstrap sd (of the 5-seed mean, and of one run)')
print('arm subset metric n_seeds mean seed_sd cellboot_sd_mean cellboot_sd_single seed_share_single')
ARMSTAT = {}
BOOTS = {}
for a, (cells, X, names) in data.items():
    for s in SUBS:
        idx = subset(cells, s)
        p = pooled(X, idx)
        bm, bs = boot_mean(X, idx)
        BOOTS[(a, s)] = bm
        for m in METRICS:
            sd = p[m].std(ddof=1)
            csd = bm[m].std(); csd1 = bs[m].std()
            share = sd**2 / (sd**2 + csd1**2)
            ARMSTAT[(a, s, m)] = (p[m].mean(), sd, csd, len(names))
            print(f'{a} {s} {m} {len(names)} {p[m].mean():.4f} {sd:.4f} {csd:.4f} {csd1:.4f} {share:.2f}')

PAIRS = [('A100', 'Sx100'), ('A50', 'S50'), ('A20', 'S20'), ('A5c', 'BsM5'), ('A5c', 'CsM5'), ('A5c', 'BsD5'),
         ('al1_A5', 'al1_BsM5'), ('al1_A5', 'al1_AL5'), ('A20', 'BsM20'), ('L3_10', 'BsM10'),
         ('A50', 'A100'), ('A20', 'A50'), ('A5c', 'L3_10')]
print('\n# 2. Contrasts B - A: delta, rule-1 thr (code, /3), seed SE (true, n), paired cell-bootstrap sd and 95% CI, '
      'z_seed=delta/seedSE, z_cell=delta/cellsd, z_tot')
print('A B subset metric delta thr verdict seedSE cellSD ci_lo ci_hi P(d>0) seed_share_of_var')
PAIRSTAT = {}
for a, b in PAIRS:
    for s in SUBS:
        for m in METRICS:
            ma, sa, _, na = ARMSTAT[(a, s, m)]
            mb, sb, _, nb = ARMSTAT[(b, s, m)]
            d = mb - ma
            thr = max(0.01, 2 * np.sqrt((sa**2 + sb**2) / 3))
            v = 'BETTER' if d > thr else ('WORSE' if d < -thr else 'n.d.')
            se = np.sqrt(sa**2 / na + sb**2 / nb)
            bd = BOOTS[(b, s)][m] - BOOTS[(a, s)][m]
            csd = bd.std()
            lo, hi = np.percentile(bd, [2.5, 97.5])
            PAIRSTAT[(a, b, s, m)] = (d, thr, se, csd)
            print(f'{a} {b} {s} {m} {d:+.4f} {thr:.4f} {v} {se:.4f} {csd:.4f} {lo:+.4f} {hi:+.4f} '
                  f'{(bd > 0).mean():.3f} {se**2 / (se**2 + csd**2):.2f}')

# 3. MDE table. Seed sd: pooled over the 5-seed arms of one regime. Cell SD of a contrast: median paired-bootstrap sd
# over that regime's contrasts. MDEs:
#  thr       = rule-1 threshold at 5v5 (code divisor 3); a true effect equal to it is detected ~50% of the time.
#  rule1_80  = true effect detected by rule 1 with 80% prob (seed noise only): thr + 0.842*SE_seed(5v5).
#  gen_80    = two-sided 5% test, 80% power, seed + cell variance: 2.80*sqrt(SE_seed^2 + SD_cell^2).
REG = {'100%': (['A100', 'Sx100'], [('A100', 'Sx100')]),
       '50%': (['A50', 'S50'], [('A50', 'S50')]),
       '20%': (['A20', 'S20', 'BsM20'], [('A20', 'S20'), ('A20', 'BsM20')]),
       '5%': (['A5c', 'BsM5', 'CsM5', 'BsD5', 'al1_A5', 'al1_BsM5', 'al1_AL5', 'al1_CPS5'],
              [('A5c', 'BsM5'), ('A5c', 'CsM5'), ('A5c', 'BsD5'), ('al1_A5', 'al1_BsM5'), ('al1_A5', 'al1_AL5')])}
print('\n# 3. MDE, 5 v 5 seeds, 50 test cells')
print('regime subset metric seed_sd(pooled) thr rule1_80 cell_sd gen_80')
MDE = {}
for r, (arms, prs) in REG.items():
    for s in SUBS:
        for m in METRICS:
            sds = [ARMSTAT[(a, s, m)][1] for a in arms]
            sd = np.sqrt(np.mean(np.square(sds)))
            thr = max(0.01, 2 * np.sqrt(2 * sd**2 / 3))
            se = sd * np.sqrt(2 / 5)
            r80 = thr + 0.842 * se
            csd = np.median([PAIRSTAT[(a, b, s, m)][3] for a, b in prs])
            g80 = 2.80 * np.sqrt(se**2 + csd**2)
            MDE[(r, s, m)] = (sd, thr, r80, csd, g80)
            print(f'{r} {s} {m} {sd:.4f} {thr:.4f} {r80:.4f} {csd:.4f} {g80:.4f}')

# 4. Scaling with test size. Seed sd of a single run's pooled metric on random cell subsets of size n (no
# replacement), and the paired bootstrap sd of a contrast on those subsets; fit var = a + b/n and extrapolate.
print('\n# 4. Scaling with number of test cells (clean subset). seed var = a + b/n fit; cell sd ~ c/sqrt(n)')
ns = [15, 25, 35, 49]
for r, (arms, prs) in [('100%', REG['100%']), ('5%', REG['5%'])]:
    a0, b0 = prs[0]
    cells, XA, _ = data[a0]; _, XB, _ = data[b0]
    clean = subset(cells, 'clean')
    for m in METRICS:
        sv, cv = [], []
        for n in ns:
            v1, v2 = [], []
            for t in range(300):
                idx = rng.choice(clean, n, replace=False)
                pa, pb = pooled(XA, idx)[m], pooled(XB, idx)[m]
                v1.append((pa.var(ddof=1) + pb.var(ddof=1)) / 2)
                # one bootstrap-resample variance proxy of delta: resample within idx
                bi = idx[rng.integers(0, n, size=(60, n))]
                ds = [pooled(XB, bb)[m].mean() - pooled(XA, bb)[m].mean() for bb in bi]
                v2.append(np.var(ds))
            sv.append(np.nanmean(v1)); cv.append(np.nanmean(v2))
        A = np.vstack([np.ones(len(ns)), 1 / np.array(ns)]).T
        coef_s = np.linalg.lstsq(A, np.array(sv), rcond=None)[0]
        coef_c = np.linalg.lstsq(A, np.array(cv), rcond=None)[0]
        line = []
        for N in [50, 100, 150, 250]:
            vs = max(coef_s[0] + coef_s[1] / N, 1e-12); vc = max(coef_c[0] + coef_c[1] / N, 1e-12)
            se = np.sqrt(2 * vs / 5)
            thr = max(0.01, 2 * np.sqrt(2 * vs / 3))
            g80 = 2.80 * np.sqrt(se**2 + vc)
            line.append(f'N={N}: seed_sd {np.sqrt(vs):.4f} thr {thr:.4f} cell_sd {np.sqrt(vc):.4f} gen80 {g80:.4f}')
        print(f'{r} {a0}-{b0} {m} | ' + ' | '.join(line))
        print(f'    raw seed var by n {dict(zip(ns, np.round(np.sqrt(sv), 4)))}  cell sd by n {dict(zip(ns, np.round(np.sqrt(cv), 4)))}')
