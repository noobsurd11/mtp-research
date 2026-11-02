#!/usr/bin/env python3
"""judge b6_recompute (2 Nov 2026, respawned judge): own-code recompute of protocol_B6 v1.0.2 from the 20 <run>.b6.json files.
Imports no b6_verdict / coach code. numpy only.
 I. integrity: 20 files = {SUP, SUPPF} x fold 0-4 x seed 5, 6, run name <-> file's arm / fold / seed <-> runner's jobs line (data.root =
    b6_root_<fold>); cell set == fold k (b6_folds.tsv) == root test.txt == val.txt; root train.txt == the other 4 folds (no overlap);
    0 forbidden stems (test + E1) in any held-out or train list; phys groups never split across folds; each (arm, seed) covers 532
    cells once; GT guard (conf row sums for inactive / crack == b6_folds.tsv px); one scorer md5 / device / code revision; step 20000.
 II. primary: pooled OOF inactive IoU per (arm, seed); d = mean over seeds PF - mean house; two-stage bootstrap (groups with
    replacement, then one seed per (fold, arm)); one-stage (groups only, seed means); PASS iff lo > 0 and d >= 0.01, FAIL iff hi < 0.
    Power: normal approx with the bootstrap SE of d (PASS ~ d_hat > 1.96 SE and >= 0.01).
 III. zero-train-px classes: per fold, classes with 0 GT px in the fold's train list (= other 4 folds) but > 0 in held-out; for
    belt_mark 19 / rings 12 / clamp 8 (and any other), GT px of that class predicted inactive (conf[c, 11]) per arm / seed, and the
    share of all inactive FP px they make; inactive IoU with those cells' FP removed.
 IV. reported: per seed pair, per fold, per source, crack IoU / relF1@2, inactive comp recall (any-hit, >= 50%) / precision (inact_cc),
    leave-top-3-groups-out, twin (multi-image) groups vs the rest.
Usage: b6_recompute.py --scores DIR --folds TSV --groups TSV --forbidden TXT --roots DIR --jobs b6_jobs.txt
"""
import argparse, glob, json, math, os, re
import numpy as np

ap = argparse.ArgumentParser()
for k in ('scores', 'folds', 'groups', 'forbidden', 'roots', 'jobs'):
    ap.add_argument('--' + k, required=True)
ap.add_argument('--nboot', type=int, default=2000)
a = ap.parse_args()
IN, CR = 11, 14
CLS = {8: 'clamp', 12: 'rings', 19: 'belt_mark'}
bad = []
ok = lambda c, m: c or bad.append(m)

rows = [l.rstrip('\n').split('\t') for l in open(a.folds)]
hdr = rows[0]; F = {r[0]: dict(zip(hdr, r)) for r in rows[1:]}
fold = {s: int(F[s]['fold']) for s in F}
G = {r[0]: r[3] for r in [l.rstrip('\n').split('\t') for l in open(a.groups)][1:]}
MOD = {r[0]: r[2] for r in [l.rstrip('\n').split('\t') for l in open(a.groups)][1:]}
forb = {l.strip() for l in open(a.forbidden) if l.strip()}
ok(len(fold) == 532, 'folds != 532'); ok(set(G) == set(fold), 'groups stems != folds stems')
ok(all(F[s]['phys_group'] == G[s] for s in fold), 'folds phys_group != judge groups')
gfold = {}
for s in fold:
    gfold.setdefault(G[s], set()).add(fold[s])
ok(all(len(v) == 1 for v in gfold.values()), 'a group is split across folds')
ok(not (set(fold) & forb), 'forbidden stem in folds')
rd = lambda p: [l.strip() for l in open(p) if l.strip()]
for k in range(5):
    R = f'{a.roots}/b6_root_{k}'
    tr, va, te = rd(f'{R}/train.txt'), rd(f'{R}/val.txt'), rd(f'{R}/test.txt')
    fk = {s for s in fold if fold[s] == k}
    ok(va == te and set(te) == fk and len(te) == len(fk), f'root {k}: held-out != fold {k}')
    ok(set(tr) == set(fold) - fk and len(tr) == len(set(tr)), f'root {k}: train != other folds')
    ok(not (set(tr) & set(te)), f'root {k}: train/held-out overlap'); ok(not ((set(tr) | set(te)) & forb), f'root {k}: forbidden stem')
jobs = {}
for l in open(a.jobs):
    if l.strip():
        t = l.rstrip('\n').split('|'); jobs[t[0]] = t
        m = re.search(r'data\.root=\S*b6_root_(\d)', t[4]); ok(m and int(m.group(1)) == int(t[3]), f'jobs {t[0]}: data.root fold')
        ok(('encoder_pf' in t[4]) == (t[2] == 'SUPPF'), f'jobs {t[0]}: PF opts vs arm')
ok(len(jobs) == 20, 'jobs != 20 lines')

files = sorted(glob.glob(f'{a.scores}/*.b6.json'))
ok(len(files) == 20, f'{len(files)} score files')
RUN = {}
meta_keys = set()
for f in files:
    j = json.load(open(f))
    name = os.path.basename(f)[:-len('.b6.json')]
    m = re.fullmatch(r'b6_(SUP|SUPPF)_f(\d)_s(\d)', name); ok(m is not None, f'bad run name {name}')
    arm, fk, sd = m.group(1), int(m.group(2)), int(m.group(3))
    cells = j['cells']['heldout'] if 'heldout' in j.get('cells', {}) else j['cells']
    meta = {k: v for k, v in j.items() if k != 'cells'}; meta_keys |= set(meta)
    RUN[(arm, fk, sd)] = dict(name=name, cells=cells, meta=meta)
    ok(name in jobs and jobs[name][2] == arm and int(jobs[name][3]) == fk and int(jobs[name][1]) == sd, f'{name}: jobs mismatch')
    ok(set(cells) == {s for s in fold if fold[s] == fk}, f'{name}: cell set != fold {fk}')
    ok(not (set(cells) & forb), f'{name}: forbidden stem')
    for key, want in (('fold', fk), ('seed', sd)):
        if key in meta: ok(int(meta[key]) == want, f'{name}: meta {key} {meta[key]} != {want}')
    if 'arm' in meta: ok(str(meta['arm']).lower() in ({'pf', 'suppf'} if arm == 'SUPPF' else {'house', 'sup'}), f'{name}: meta arm {meta["arm"]}')
    if 'step' in meta: ok(int(meta['step']) == 20000, f'{name}: step {meta["step"]}')
ok(set(RUN) == {(x, f, s) for x in ('SUP', 'SUPPF') for f in range(5) for s in (5, 6)}, 'missing (arm, fold, seed)')
for key in ('scorer_md5', 'device', 'code_revision'):
    vals = {str(r['meta'].get(key)) for r in RUN.values()}
    print(f'# meta {key}: {sorted(vals)}'); ok(len(vals) == 1, f'{key} not unique')
print(f'# meta keys seen: {sorted(meta_keys)}')
if bad:
    raise SystemExit('INTEGRITY: FAIL (before any number) ' + '; '.join(bad[:10]))


def Cm(c):
    m = np.asarray(c['conf'], np.int64); n = math.isqrt(m.size); return m.reshape(n, n)[:24, :24]


ST = sorted(fold)
CONF = {(x, s): np.stack([Cm(RUN[(x, fold[st], s)]['cells'][st]) for st in ST]) for x in ('SUP', 'SUPPF') for s in (5, 6)}  # cells x 24 x 24
for st_i, st in enumerate(ST):
    g = CONF[('SUP', 5)][st_i]
    ok(int(g[IN].sum()) == int(F[st]['inactive_px']) and int(g[CR].sum()) == int(F[st]['crack_px']), f'GT guard {st}')
    for key in CONF:
        ok(np.array_equal(CONF[key][st_i].sum(1), g.sum(1)), f'GT rows differ across runs {st}')
print('INTEGRITY: ' + ('ALL CHECKS PASS' if not bad else 'FAIL ' + '; '.join(bad[:10])))

# ---------- II. primary
def tfn(C):  # (..., 24, 24) -> tp, fp, fn for inactive
    tp = C[..., IN, IN]; return np.stack([tp, C[..., :, IN].sum(-1) - tp, C[..., IN, :].sum(-1) - tp], -1)


iou = lambda t: t[..., 0] / np.maximum(t.sum(-1), 1)
T = {k: tfn(v) for k, v in CONF.items()}  # cells x 3
I = {k: iou(v.sum(0)) for k, v in T.items()}
d = (I[('SUPPF', 5)] + I[('SUPPF', 6)]) / 2 - (I[('SUP', 5)] + I[('SUP', 6)]) / 2
print('\n## primary: pooled OOF inactive IoU (532 cells)')
print('   ' + ' | '.join(f'{x} s{s} {I[(x, s)]:.4f}' for x in ('SUP', 'SUPPF') for s in (5, 6)))
print(f'   d (mean over seeds PF - house) {d:+.4f} | seed pairs: s5 {I[("SUPPF", 5)] - I[("SUP", 5)]:+.4f}, s6 {I[("SUPPF", 6)] - I[("SUP", 6)]:+.4f}; '
      f'cross pairs s5-s6 {I[("SUPPF", 5)] - I[("SUP", 6)]:+.4f}, s6-s5 {I[("SUPPF", 6)] - I[("SUP", 5)]:+.4f}; seed spread house {abs(I[("SUP", 5)] - I[("SUP", 6)]):.4f} PF {abs(I[("SUPPF", 5)] - I[("SUPPF", 6)]):.4f}')
groups = sorted({G[s] for s in ST}); gi = np.array([groups.index(G[s]) for s in ST]); fo = np.array([fold[s] for s in ST])
# per (group) per (arm, seed) counts; groups live in one fold
GT_ = {k: np.stack([v[gi == j].sum(0) for j in range(len(groups))]) for k, v in T.items()}  # groups x 3
gfo = np.array([fo[gi == j][0] for j in range(len(groups))])
rng = np.random.default_rng(20261103)
two, one = np.empty(a.nboot), np.empty(a.nboot)
for b in range(a.nboot):
    w = np.bincount(rng.integers(0, len(groups), len(groups)), minlength=len(groups)).astype(float)
    pick = {(x, f): (5, 6)[rng.integers(0, 2)] for f in range(5) for x in ('SUP', 'SUPPF')}
    arm_t = {}
    for x in ('SUP', 'SUPPF'):
        t = np.zeros(3)
        for f in range(5):
            m = gfo == f; t += (w[m, None] * GT_[(x, pick[(x, f)])][m]).sum(0)
        arm_t[x] = t
    two[b] = iou(arm_t['SUPPF']) - iou(arm_t['SUP'])
    one[b] = np.mean([iou(w @ GT_[('SUPPF', s)]) for s in (5, 6)]) - np.mean([iou(w @ GT_[('SUP', s)]) for s in (5, 6)])
lo, hi = np.percentile(two, [2.5, 97.5]); se = two.std(ddof=1)
v = 'PASS' if (lo > 0 and d >= 0.01) else ('FAIL' if hi < 0 else 'n.d.')
print(f'   two-stage ({a.nboot}, groups {len(groups)} + seed per (fold, arm); rng 20261103): CI [{lo:+.4f}, {hi:+.4f}] P(d*<0) {np.mean(two < 0):.3f} SE {se:.4f} -> {v}')
print(f'   one-stage (groups only, seed means): CI [{np.percentile(one, 2.5):+.4f}, {np.percentile(one, 97.5):+.4f}] SE {one.std(ddof=1):.4f}')
from math import erf, sqrt
Phi = lambda z: 0.5 * (1 + erf(z / sqrt(2)))
for sd_ in (se, 0.020):
    pw = lambda delta: 1 - Phi((max(1.96 * sd_, 0.01) - delta) / sd_)
    print(f'   power (normal approx, SE {sd_:.4f}): P(PASS | true d) at +0.017 {pw(0.017):.2f}, +0.03 {pw(0.03):.2f}, +0.05 {pw(0.05):.2f}; 80% needs d ~ {(1.96 + 0.8416) * sd_:+.3f}'
          f' | P(FAIL | d=0) {Phi(-1.96):.3f}; minimum detectable at the observed SE: CI half-width {1.96 * sd_:.3f}')

# ---------- III. zero-train-px classes
print('\n## zero-train-px classes (GT px per fold from conf rows; train = other 4 folds)')
gtc = CONF[('SUP', 5)].sum(2)  # cells x 24 GT px per class
per_fold = np.stack([gtc[fo == f].sum(0) for f in range(5)])  # 5 x 24
zero = []
for f in range(5):
    trainpx = per_fold.sum(0) - per_fold[f]
    for c in range(24):
        if trainpx[c] == 0 and per_fold[f, c] > 0:
            zero.append((f, c))
print('   (fold, class, held-out GT px, n cells): ' + ', '.join(f'(f{f}, {c} {CLS.get(c, "")}, {per_fold[f, c]}, {(gtc[fo == f, c] > 0).sum()})' for f, c in zero))
for f, c in zero:
    m = (fo == f) & (gtc[:, c] > 0)
    line = f'   fold {f} class {c} {CLS.get(c, "")}: GT px {gtc[m, c].sum()} in {m.sum()} cells; predicted as inactive: '
    for x in ('SUP', 'SUPPF'):
        for s in (5, 6):
            C = CONF[(x, s)][m]; px = C[:, c, IN].sum(); fpall = (CONF[(x, s)][:, :, IN].sum() - CONF[(x, s)][:, IN, IN].sum())
            top = np.argsort(-C[:, c, :].sum(0))[:3]
            line += f'{x} s{s} {px} ({px / max(gtc[m, c].sum(), 1):.2f} of class px; {px / max(fpall, 1):.3f} of all inactive FP; top pred {list(map(int, top))}) | '
    print(line)
# inactive IoU with the zero-train-class cells' FP removed (descriptive)
mask_z = np.zeros(len(ST), bool)
for f, c in zero:
    mask_z |= (fo == f) & (gtc[:, c] > 0)
Iz = {k: iou(v[~mask_z].sum(0)) for k, v in T.items()}
dz = (Iz[('SUPPF', 5)] + Iz[('SUPPF', 6)]) / 2 - (Iz[('SUP', 5)] + Iz[('SUP', 6)]) / 2
print(f'   without the {mask_z.sum()} zero-train-class cells: ' + ' '.join(f'{x} s{s} {Iz[(x, s)]:.4f}' for x in ('SUP', 'SUPPF') for s in (5, 6)) + f' | d {dz:+.4f} (all {d:+.4f})')

# ---------- IV. reported
print('\n## reported')
def crack(C, cells):
    tp = C[..., CR, CR].sum(); return tp / max(C[..., :, CR].sum() + C[..., CR, :].sum() - tp, 1)
for f in range(5):
    m = fo == f
    print(f'   fold {f} ({m.sum()} cells, GT inact px {T[("SUP", 5)][m].sum(0)[[0, 2]].sum()}): ' + ' '.join(f'{x} s{s} {iou(T[(x, s)][m].sum(0)):.4f}' for x in ('SUP', 'SUPPF') for s in (5, 6))
          + f' | d {np.mean([iou(T[("SUPPF", s)][m].sum(0)) for s in (5, 6)]) - np.mean([iou(T[("SUP", s)][m].sum(0)) for s in (5, 6)]):+.4f}')
src = np.array([s.split('_')[0] for s in ST])
for so in sorted(set(src)):
    m = src == so; gpx = T[('SUP', 5)][m].sum(0)[[0, 2]].sum()
    if gpx == 0: continue
    print(f'   source {so} (GT inact px {gpx}): d {np.mean([iou(T[("SUPPF", s)][m].sum(0)) for s in (5, 6)]) - np.mean([iou(T[("SUP", s)][m].sum(0)) for s in (5, 6)]):+.4f} '
          + ' '.join(f'{x} {np.mean([iou(T[(x, s)][m].sum(0)) for s in (5, 6)]):.4f}' for x in ('SUP', 'SUPPF')))
cr = {k: crack(v, None) for k, v in CONF.items()}
def rel(x, s):
    r = np.sum([RUN[(x, fold[st], s)]['cells'][st]['crack_rel2'] for st in ST], 0).astype(float)
    P, R = r[0] / max(r[1], 1), r[2] / max(r[3], 1); return 2 * P * R / max(P + R, 1e-12)
print('   crack IoU ' + ' '.join(f'{k[0]} s{k[1]} {v:.4f}' for k, v in cr.items()) + f' | d {np.mean([cr[("SUPPF", s)] for s in (5, 6)]) - np.mean([cr[("SUP", s)] for s in (5, 6)]):+.4f}')
rf = {(x, s): rel(x, s) for x in ('SUP', 'SUPPF') for s in (5, 6)}
print('   crack relF1@2 ' + ' '.join(f'{k[0]} s{k[1]} {v:.4f}' for k, v in rf.items()) + f' | d {np.mean([rf[("SUPPF", s)] for s in (5, 6)]) - np.mean([rf[("SUP", s)] for s in (5, 6)]):+.4f}')
for x in ('SUP', 'SUPPF'):
    for s in (5, 6):
        gc = [g for st in ST for g in RUN[(x, fold[st], s)]['cells'][st]['inact_cc']['gt']]
        pc = [p for st in ST for p in RUN[(x, fold[st], s)]['cells'][st]['inact_cc']['pr']]
        print(f'   inact_cc {x} s{s}: GT comps {len(gc)} any-hit {np.mean([g[1] >= 1 for g in gc]):.3f} >=50% {np.mean([g[1] >= math.ceil(0.5 * g[0]) for g in gc]):.3f} | '
              f'pred comps {len(pc)} precision (hit >= 1) {np.mean([p[1] >= 1 for p in pc]) if pc else float("nan"):.3f}')
gpx = np.array([(GT_[('SUP', 5)][j, 0] + GT_[('SUP', 5)][j, 2]) for j in range(len(groups))])
top3 = np.argsort(-gpx)[:3]; keep = np.ones(len(groups), bool); keep[top3] = False
dl = np.mean([iou(GT_[('SUPPF', s)][keep].sum(0)) for s in (5, 6)]) - np.mean([iou(GT_[('SUP', s)][keep].sum(0)) for s in (5, 6)])
print(f'   top-3 groups by inactive px {[groups[j] for j in top3]} share {gpx[top3].sum() / gpx.sum():.3f}; leave-top-3-groups-out d {dl:+.4f}')
for j in top3:
    print(f'     {groups[j]} (fold {gfo[j]}, GT {gpx[j]}): ' + ' '.join(f'{x} s{s} {iou(GT_[(x, s)][j]):.3f}' for x in ('SUP', 'SUPPF') for s in (5, 6)))
twin = np.array([len({MOD[s] for s in ST if G[s] == g}) > 1 for g in groups])
for lab, m in (('twin (multi-image) groups', twin), ('other groups', ~twin)):
    print(f'   {lab} ({m.sum()} groups, GT inact px {gpx[m].sum()} = {gpx[m].sum() / gpx.sum():.3f}): d {np.mean([iou(GT_[("SUPPF", s)][m].sum(0)) for s in (5, 6)]) - np.mean([iou(GT_[("SUP", s)][m].sum(0)) for s in (5, 6)]):+.4f} '
          + ' '.join(f'{x} {np.mean([iou(GT_[(x, s)][m].sum(0)) for s in (5, 6)]):.4f}' for x in ('SUP', 'SUPPF')))
w_eff = gpx / gpx.sum(); print(f'   effective n groups (1/sum w^2, inactive px) {1 / np.sum(w_eff ** 2):.1f}; groups with inactive {int((gpx > 0).sum())}')
