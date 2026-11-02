#!/usr/bin/env python3
"""judge s2_extra (2 Nov 2026): adversarial extras for the SKR2+HC2 opening (descriptive; never a verdict). Own code.
 1. SKR2 E1 relF1@2 BETTER fragility (m0, argmax): leave-one-source-image-out (71 images) rule-1 re-check; leave-one-seed-out per arm
    (4 v 5 and 5 v 4, rule 1 /3 recomputed); per-image contribution to pooled relP/relR counts.
 2. Is SKR2's E1 gain a bias shift? (records rec_w, 5 seeds each): E1 relF1@2 over b for SUPPF and SKR2 (per run, then mean);
    SUPPF's best constant-b E1 relF1@2 (E1-oracle, descriptive, chooses nothing) vs SKR2 at b 0; and at b 0.75.
 3. HC2 SHV1 / val readouts from records (synval / val, 5 seeds pooled): matched relR@2 (max relR s.t. relP >= 0.90 over the
    grid incl. 0.75), relR / relP at b 0, inactive IoU at b 0; split SHV1 into views with / without GT inactive px.
Usage: s2_extra.py M0_SUPPF M0_SKR2 RECW_SUPPF RECW_SKR2 SHV_SUPPF SHV_HC SHV_HC2 [CTX]
"""
import json, math, sys
import numpy as np

m0B, m0S, rwB, rwS, shB, shH, shH2 = sys.argv[1:8]
SEEDS = [5, 6, 7, 8, 9]


def rule(xa, xb):
    xa, xb = np.asarray(xa, float), np.asarray(xb, float); d = xb.mean() - xa.mean()
    thr = max(0.01, 2 * math.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    return d, thr, 'BETTER' if d > thr else ('WORSE' if d < -thr else 'n.d.')


# ---- 1. LOIO / LOSO on E1 relF1@2
def m0(d, pre):
    return [json.load(open(f'{d}/{pre}_100pct_s{k}.json'))['cells']['ext'] for k in SEEDS]


A = {'SUPPF': m0(m0B, 'pf2_SUPPF'), 'SKR2': m0(m0S, 'skr2_SKR01')}
st = sorted(A['SUPPF'][0]); img = sorted({'_'.join(s.split('_')[:2]) for s in st})
R2 = {n: np.array([[r[s]['crack_rel2'] for s in st] for r in v], float) for n, v in A.items()}  # seeds x cells x 4
ii = np.array([img.index('_'.join(s.split('_')[:2])) for s in st])


def f1(t):
    P, R = t[..., 0] / np.maximum(t[..., 1], 1), t[..., 2] / np.maximum(t[..., 3], 1); return 2 * P * R / np.maximum(P + R, 1e-12)


full = rule(f1(R2['SUPPF'].sum(1)), f1(R2['SKR2'].sum(1)))
print(f'## 1. SKR2 E1 relF1@2: d {full[0]:+.4f} thr {full[1]:.4f} {full[2]}; per-seed SUPPF ' + ' '.join(f'{x:.4f}' for x in f1(R2["SUPPF"].sum(1)))
      + ' SKR2 ' + ' '.join(f'{x:.4f}' for x in f1(R2['SKR2'].sum(1))))
res = []
for j, im in enumerate(img):
    k = ii != j
    d, thr, v = rule(f1(R2['SUPPF'][:, k].sum(1)), f1(R2['SKR2'][:, k].sum(1)))
    gt = R2['SUPPF'][0, ii == j, 3].sum()
    res.append((d - thr, d, thr, v, im, gt))
res.sort()
nb = sum(r[3] == 'BETTER' for r in res)
print(f'leave-one-image-out ({len(img)} images): BETTER kept in {nb}/{len(img)}; n.d. in {len(img) - nb}; margin (d - thr) min {res[0][0]:+.4f} median {np.median([r[0] for r in res]):+.4f}')
for r in res[:8]:
    print(f'   drop {r[4]:12s} (GT crack px/run {r[5]:7.0f}): d {r[1]:+.4f} thr {r[2]:.4f} {r[3]}')
for n_drop, who in (('SUPPF', 'base'), ('SKR2', 'test')):
    out = []
    for q in range(5):
        k = [i for i in range(5) if i != q]
        a_ = f1(R2['SUPPF'].sum(1)); b_ = f1(R2['SKR2'].sum(1))
        if n_drop == 'SUPPF': a_ = a_[k]
        else: b_ = b_[k]
        d, thr, v = rule(a_, b_); out.append(f's{SEEDS[q]} {d:+.4f}/{thr:.4f} {v}')
    print(f'leave-one-seed-out of {n_drop}: ' + ' | '.join(out))
# per-image contribution: d relF1 when only image j is changed from SUPPF counts to SKR2 counts (seed-pooled), top movers
pB, pS = R2['SUPPF'].sum(0), R2['SKR2'].sum(0)
base = f1(pB.sum(0)); mov = []
for j, im in enumerate(img):
    t = pB.sum(0) - pB[ii == j].sum(0) + pS[ii == j].sum(0); mov.append((f1(t) - base, im, pB[ii == j, 3].sum() / 5))
mov.sort(reverse=True)
print('per-image swap contribution to seed-pooled d relF1 (top 6 / bottom 3): ' + ', '.join(f'{m[1]} {m[0]:+.4f} (GT {m[2]:.0f})' for m in mov[:6])
      + ' ... ' + ', '.join(f'{m[1]} {m[0]:+.4f}' for m in mov[-3:]) + f'; sum of all {sum(m[0] for m in mov):+.4f} vs pooled {f1(pS.sum(0)) - base:+.4f}')
pos = sorted([m[0] for m in mov], reverse=True)
print(f'   images with + contribution {sum(m[0] > 0 for m in mov)}, - {sum(m[0] < 0 for m in mov)}; top-3 share of positive sum {sum(pos[:3]) / max(sum(p for p in pos if p > 0), 1e-12):.2f}')

# ---- 2. bias-shift oracle on E1 (records)
def recw(d, pre, s):
    return [json.load(open(f'{d}/{pre}_100pct_s{k}.{s}.json')) for k in SEEDS]


def curve_rel(cells):
    cs = list(cells.values())
    S = lambda key: np.sum([np.asarray(c[key], np.int64) for c in cs], 0)
    pred, rp, rr = S('pred'), S('relp_tp'), S('relr_tp'); ng = sum(c['n_gt'] for c in cs)
    P = rp / np.maximum(pred, 1); R = rr / max(ng, 1)
    return 2 * P * R / np.maximum(P + R, 1e-12), P, R


EB, ES = recw(rwB, 'pf2_SUPPF', 'ext'), recw(rwS, 'skr2_SKR01', 'ext')
G = np.array(EB[0]['grid']); i0 = int(np.argmin(np.abs(G))); i75 = int(np.argmin(np.abs(G - 0.75)))
FB = np.array([curve_rel(j['cells'])[0] for j in EB]); FS = np.array([curve_rel(j['cells'])[0] for j in ES])
mB, mS = FB.mean(0), FS.mean(0)
jb = int(np.argmax(mB)); js = int(np.argmax(mS))
print(f'\n## 2. E1 relF1@2 vs constant bias b (records; mean of per-run values; E1-oracle = descriptive, chooses nothing)')
print(f'SUPPF b 0 {mB[i0]:.4f}, b 0.75 {mB[i75]:.4f}, best b {G[jb]:+.1f} {mB[jb]:.4f} | SKR2 b 0 {mS[i0]:.4f}, b 0.75 {mS[i75]:.4f}, best b {G[js]:+.1f} {mS[js]:.4f}')
print(f'SKR2 b 0 - SUPPF best-b {mS[i0] - mB[jb]:+.4f} ; SKR2 best - SUPPF best {mS[js] - mB[jb]:+.4f} ; rule 1 at each arm\'s E1-best b: '
      + '{:+.4f} thr {:.4f} {}'.format(*rule(FB[:, jb], FS[:, js])))
for b in (-1, 0, 0.5, 1, 1.5, 2, 3, 4):
    j = int(np.argmin(np.abs(G - b)))
    print(f'   b {G[j]:+.1f}: SUPPF {mB[j]:.4f}  SKR2 {mS[j]:.4f}  d {mS[j] - mB[j]:+.4f} (thr {rule(FB[:, j], FS[:, j])[1]:.4f} {rule(FB[:, j], FS[:, j])[2]})')

# ---- 3. SHV1 / val from records
def sh(d, pre, s):
    return [json.load(open(f'{d}/{pre}_100pct_s{k}.{s}.json'))['cells'] for k in SEEDS]


def rd(cellsets, keep=lambda s, c: True):
    cs = [c for cells in cellsets for s, c in cells.items() if keep(s, c)]
    S = lambda key: np.sum([np.asarray(c[key], np.int64) for c in cs], 0)
    pred, rp, rr = S('pred'), S('relp_tp'), S('relr_tp'); ng = sum(int(c['n_gt']) for c in cs)
    ip, it = S('inact_pred'), S('inact_tp'); gi = sum(int(c['gt_inact']) for c in cs)
    P = rp / np.maximum(pred, 1); R = rr / max(ng, 1)
    ok = P >= 0.90
    return dict(matched=R[ok].max() if ok.any() else np.nan, R0=R[i0s], P0=P[i0s], I0=it[i0s] / max(ip[i0s] + gi - it[i0s], 1), n=len(cs) // len(cellsets),
                offgt0=(pred[i0s] - rp[i0s]) / len(cellsets), gi=gi // len(cellsets))


G2 = np.array(json.load(open(f'{shB}/pf2_SUPPF_100pct_s5.synval.json'))['grid']); i0s = int(np.argmin(np.abs(G2)))
print(f'\n## 3. records-based SHV1 (synval 108) / val (54) readouts, 5 seeds pooled per arm (grid {G2[0]}..{G2[-1]}, {len(G2)} pts)')
ARM = {'SUPPF': (shB, 'pf2_SUPPF'), 'HC': (shH, 'hc_HC'), 'HC2': (shH2, 'hc2_HCig')}
D = {n: {s: sh(d, p, s) for s in ('synval', 'val')} for n, (d, p) in ARM.items()}
for s in ('synval', 'val'):
    for lab, kp in (('all', lambda st, c: True), ('views with GT inactive', lambda st, c: int(c['gt_inact']) > 0),
                    ('views without GT inactive', lambda st, c: int(c['gt_inact']) == 0)):
        r = {n: rd(D[n][s], kp) for n in ARM}
        print(f'-- {s} {lab} (n {r["SUPPF"]["n"]}, GT inactive px/run {r["SUPPF"]["gi"]}): ' + ' | '.join(
            f'{n} matched {r[n]["matched"]:.4f} relR0 {r[n]["R0"]:.4f} relP0 {r[n]["P0"]:.4f} inact0 {r[n]["I0"]:.4f} offGT0/run {r[n]["offgt0"]:.0f}' for n in ARM))
    rr = {n: [rd([c]) for c in D[n][s]] for n in ARM}
    print(f'   per seed matched: ' + ' | '.join(f'{n} ' + ' '.join(f'{x["matched"]:.3f}' for x in rr[n]) for n in ARM)
          + '\n   per seed inact0: ' + ' | '.join(f'{n} ' + ' '.join(f'{x["I0"]:.3f}' for x in rr[n]) for n in ARM))
r = {n: rd(D[n]['synval']) for n in ARM}
print(f'mechanism (records): HC2 - SUPPF matched SHV1 relR@2 {r["HC2"]["matched"] - r["SUPPF"]["matched"]:+.4f} (kill < +0.05); HC - SUPPF {r["HC"]["matched"] - r["SUPPF"]["matched"]:+.4f}')
