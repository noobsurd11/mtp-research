"""coach (1 Nov): independent recompute of the A8 screen GO rule (protocol_A8screen §3) from the frozen scoring pass's dumps and
el_metrics records (a8_score.sh 75a57c9c: work/dump/<run>.{val,rf}.npz, out/rec/<run>.{val,rf}.json). Own code; same metric
definitions as the pre-registered rule, own module-bootstrap RNG (so the bound differs slightly from a8_screen_score by design).
  crack AP: pooled per run over a set's cells; p(crack) from the dump binned into 1,000 equal bins on [0, 1]; precision / recall
            swept from the top bin down; AP = sum of precision x recall increment (step integral).
  F51 bootstrap: resample F51 modules (rf_sets column 4) with replacement; per resample, seed-mean AP(A8) - seed-mean AP(A8c),
            each run's AP on the pooled cells of the drawn modules (multiset); 2,000 draws; 2.5th percentile.
  b_rel: per run on its val record, max relR@2 s.t. relP@2 >= 0.90 on b in -4.0..+12.0 step 0.1 (ties smaller b; none -> max relP).
  FA: crack px predicted at b_rel on the crack-free (n_gt == 0, keep-masked) cells of H36 / F51 (records); seed mean per arm;
      term passes iff A8 <= max(1.5 x A8c, A8c + 200).
Usage: python coach_a8.py A8_SCORE_OUT_DIR(v1) RF_DIR RF_SETS_TSV EL_F8_CODE"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image

V, RF, RFS, CODE = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
ARMS = {'A8': ['f8_A8_4k_s0', 'f8_A8_4k_s1'], 'A8c': ['f8_A8c_4k_s0', 'f8_A8c_4k_s1']}
CR, NB = 14, 1000
GRID = np.unique(np.round(np.concatenate([np.arange(-40, 121) / 10.0, [0.75]]), 2))
OPJ = np.array([j for j, b in enumerate(GRID) if abs(round(b * 10) - b * 10) < 1e-6])
rows = [l.rstrip('\n').split('\t') for l in open(RFS) if l.strip()][1:]
rfset = {r[0]: r[1] for r in rows}; module = {r[0]: r[3] for r in rows}


def hist(pc, gt, keep):
    bins = np.minimum((pc.astype(np.float64) * NB).astype(np.int64), NB - 1); bins = np.maximum(bins, 0)
    pos = (gt == CR) & keep; neg = keep & ~pos
    return np.bincount(bins[pos], minlength=NB), np.bincount(bins[neg], minlength=NB), int(pos.sum())


def ap_of(pos, neg):
    tp = np.cumsum(pos[::-1]).astype(float); fp = np.cumsum(neg[::-1]).astype(float)
    tot = pos.sum()
    if tot == 0:
        return float('nan')
    prec = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) > 0)
    rec = tp / tot
    return float(np.sum(prec * np.diff(np.concatenate([[0.0], rec]))))


H, sets, FA, BREL = {}, None, {}, {}
for runs in ARMS.values():
    for r in runs:
        H[r] = {}
        for sp in ('val', 'rf'):
            z = np.load(V / 'work' / 'dump' / f'{r}.{sp}.npz'); st = [str(s) for s in z['stems']]
            for i, s in enumerate(st):
                if sp == 'val':
                    gt = np.array(Image.open(CODE / 'data' / 'labeled' / 'masks_escdd' / f'{s}.png')); keep = np.ones(gt.shape, bool)
                else:
                    gt = np.array(Image.open(RF / 'masks' / f'{s}.png')); keep = ~(np.array(Image.open(RF / 'ignore' / f'{s}.png')) > 0)
                H[r][s] = hist(z['pc'][i], gt, keep)
            if sp == 'val':
                vst = st
            elif sets is None:
                sets = {g: [s for s in st if rfset[s] == g] for g in ('F51', 'H36', 'F19')}
        vr = json.load(open(V / 'out' / 'rec' / f'{r}.val.json'))['cells']
        S = lambda k: np.sum([np.asarray(c[k], np.int64) for c in vr.values()], 0)
        pred, rp, rr = S('pred'), S('relp_tp'), S('relr_tp'); ng = sum(c['n_gt'] for c in vr.values())
        relP = np.where(pred > 0, rp / np.maximum(pred, 1), -1.0)[OPJ]; relR = (rr / max(ng, 1))[OPJ]
        ok = np.where(relP >= 0.90)[0]
        j = int(OPJ[ok[np.argmax(relR[ok])]]) if len(ok) else int(OPJ[np.argmax(relP)])
        BREL[r] = (float(GRID[j]), bool(len(ok)))
        rf = json.load(open(V / 'out' / 'rec' / f'{r}.rf.json'))['cells']
        FA[r] = {g: float(sum(rf[s]['pred'][j] for s in sets[g] if rf[s]['n_gt'] == 0)) for g in ('H36', 'F51')}
sets['val'] = vst
ap = lambda r, st: ap_of(np.sum([H[r][s][0] for s in st], 0), np.sum([H[r][s][1] for s in st], 0))
print('## per run: crack AP (1,000 bins) | b_rel (reachable) | FA px on crack-free H36 / F51 at b_rel')
M = {}
for arm, runs in ARMS.items():
    for r in runs:
        print(f'  {r:14s} ' + ' '.join(f'{k} {ap(r, sets[k]):.4f}' for k in ('F51', 'val', 'H36', 'F19')) + f' | b_rel {BREL[r][0]:+.1f} ({BREL[r][1]}) | FA H36 {FA[r]["H36"]:.0f} F51 {FA[r]["F51"]:.0f}')
    M[arm] = {k: float(np.mean([ap(r, sets[k]) for r in runs])) for k in ('F51', 'val', 'F19')}
    M[arm].update({f'FA_{g}': float(np.mean([FA[r][g] for r in runs])) for g in ('H36', 'F51')})
    print(f'  {arm} mean: ' + json.dumps({k: round(v, 4) for k, v in M[arm].items()}))
mods = sorted({module[s] for s in sets['F51']}); by = {m: [s for s in sets['F51'] if module[s] == m] for m in mods}
assert len(mods) == 36 and len(sets['F51']) == 51, (len(mods), len(sets['F51']))
rng = np.random.default_rng(20261101); bs = []
for _ in range(2000):
    st = [s for i in rng.integers(0, len(mods), len(mods)) for s in by[mods[i]]]
    bs.append(np.mean([ap(r, st) for r in ARMS['A8']]) - np.mean([ap(r, st) for r in ARMS['A8c']]))
lo, hi = np.percentile(bs, [2.5, 97.5])
d51 = M['A8']['F51'] - M['A8c']['F51']; dv = M['A8']['val'] - M['A8c']['val']
bnd = lambda x: max(1.5 * x, x + 200)
t = {'1a F51 dAP > 0': (round(d51, 4), d51 > 0), '1b F51 module-boot LB > 0 (own RNG)': (round(float(lo), 4), lo > 0),
     '2 val dAP >= -0.02': (round(dv, 4), dv >= -0.02),
     '3 FA H36': ((M['A8']['FA_H36'], M['A8c']['FA_H36']), M['A8']['FA_H36'] <= bnd(M['A8c']['FA_H36'])),
     '3 FA F51': ((M['A8']['FA_F51'], M['A8c']['FA_F51']), M['A8']['FA_F51'] <= bnd(M['A8c']['FA_F51']))}
print('## GO-rule terms (seed means)')
for k, v in t.items():
    print(f'  {k}: {v[0]} -> {"pass" if v[1] else "FAIL"}')
print(f'  F51 module bootstrap 95% [{lo:+.4f}, {hi:+.4f}] (2,000, own RNG)')
print('## coach GO:', all(v[1] for v in t.values()))
