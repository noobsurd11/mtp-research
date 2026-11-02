#!/usr/bin/env python3
"""judge skr2c_power (3 Nov 2026): rule-1 pass probability for a fresh-seed (5 v 5) SKR2 vs SUPPF replication, from opening #5's
per-arm seed sds and deltas (verify_skr2_hc2.md; SKR2E singles lines). Independent normal seeds; primaries treated as independent
(S, approximation; test crack IoU and relF1@2 are correlated in reality). rule 1: d > max(0.01, 2*sqrt((sA^2+sB^2)/3)) with SAMPLE sds;
BETTER on >= 1, WORSE on none. Shrink k scales every #5 delta (k 1 = #5 as observed; winner's curse argues k < 1)."""
import numpy as np
P = {  # name: (sd SUPPF, sd SKR2, #5 delta)
    'E1 relF1@2': (0.0272, 0.0135, 0.0364), 'E1 any-hit': (0.0320, 0.0318, 0.0439),
    'test crack IoU': (0.0048, 0.0031, 0.0091), 'test relF1@2': (0.0057, 0.0037, 0.0089), 'test inactive': (0.0209, 0.0109, 0.0099)}
rng = np.random.default_rng(20261103); N = 20000
for k in (1.0, 0.75, 0.5, 0.0):
    better = np.zeros((N, len(P)), bool); worse = np.zeros((N, len(P)), bool)
    for j, (sA, sB, d) in enumerate(P.values()):
        A = rng.normal(0, sA, (N, 5)); B = rng.normal(k * d, sB, (N, 5))
        dd = B.mean(1) - A.mean(1); thr = np.maximum(0.01, 2 * np.sqrt((A.std(1, ddof=1) ** 2 + B.std(1, ddof=1) ** 2) / 3))
        better[:, j] = dd > thr; worse[:, j] = dd < -thr
    ps = better.any(1) & ~worse.any(1)
    print(f'k {k:.2f}: P(PASS) {ps.mean():.3f} | per primary BETTER: ' + ', '.join(f'{n} {better[:, j].mean():.3f}' for j, n in enumerate(P))
          + f' | P(E1 relF1 BETTER) {better[:, 0].mean():.3f}')
