"""coach (14 Nov 2026): independent recompute of protocol_SKR2C v1's opening (E1 opening #7; same 50 test and 106 E1 cells as #5 / #6,
3rd look). Own code. Not used: the runner's readout (m2_rung call, s2c_d_boot.py) and the opening's scorers (s2c_e1_coprim.py,
s2c_guards.py, s2c_named_boot.py, s2_b5w_check.py). Reused: my earlier coach code (coach_thin rule1 / twoset / e1_agg / load_m0;
coach_s2 e1_vals / test_vals / g1 / g2 / b5_arm_w; coach_verify counts / metrics; coach_skr2e feats / metr / boot / cfree_px; the
feats / metr / boot of my coach_s2_boot.py 7ea26cfb, copied here verbatim because that file runs on import).

Verdict R (protocol 3a; house rule 1, /3, 5 v 5; singles s10-14, argmax m0 JSONs):
  7 co-primaries: test crack IoU, crack relF1@2, inactive IoU (two-set rule: all 50 + clean 49 without CSIR_00070_r8_c4); B5 comp
  recall at comp P >= 0.90 and relR@2 at relP@2 >= 0.90 (arm-pooled OP on val, grid -8.0 .. +12.0 step 0.1; two-set rule); E1 crack
  relF1@2 and E1 any-hit (106 cells, one set).
  Guards (seed means): G1 test inactive IoU d <= -0.015 in both sets; G2 test crack relP@2 d < -0.03 (all 50) or E1 crack px on the
  74 crack-free cells > 1.5 x the fresh SUPPF s10-14 mean (ruling 1).
  PASS: >= 1 co-primary BETTER, none WORSE, no guard tripped. FAIL: any WORSE or any guard tripped. Else n.d.
  Named claim condition 1: seed-aware two-stage bootstrap of E1 relF1@2 (71 clusters x seeds within arm, 2,000 draws, seed 0).
Verdict D (protocol 3b; 5-member ensembles, both at b 0):
  primaries: test crack IoU / relF1@2 / inactive IoU, paired image bootstrap (2,000, seed 0), all 50 + clean 49; pass = CI wholly
  above 0 in both sets, or in one with a same-sign estimate in the other; fail = CI wholly below 0 in either set. E1 crack relF1@2 and
  any-hit, 71-cluster bootstrap (2,000, seed 0). Guards at the b 0 pair (point estimates): G2a test relP@2 d < -0.03; G2b E1
  crack-free px > 1.5 x E-SUPPF'; G1t test inactive d <= -0.015 in both sets; G1e E1 inactive cluster CI wholly below 0.
  PASS: >= 1 primary passes, none fails, no guard trips. FAIL: any primary fails or any guard trips. Else n.d.
  "seed 0" CIs: a fresh numpy default_rng(0) per bootstrap, stems sorted, clusters sorted, one rng.integers(0, n, n) per resample:
  the same draws as Track M m1_analyze.boot / the pf2e cluster bootstrap, with my own metric code. A second stream
  (default_rng(12345), shared) is printed as a check that no verdict depends on the stream.
Combination (3a named claim, 3c, 7): 'combine'.
Fragility: leave-one-seed-out (10 drops, rule 1 /3 on 4 v 5), leave-one-cluster-out (E1 71 source images; test 48 / 47 modules).
Usage: python -B coach_s2c.py selftest              (opened files only: #5 s5-9 singles, #6 ensembles)
       python -B coach_s2c.py R OUT.json            (raw_r)
       python -B coach_s2c.py D OUT.json            (raw_d; --rjson R.json adds singles vs ensemble from R's per-run values)
       python -B coach_s2c.py combine R.json D.json"""
import json, re, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; T = HERE.parent.parent; RES = T / 'results'
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(T.parent / 'team_2026-10-29_features' / 'scripts'))
import coach_thin as ct      # rule1, twoset, e1_agg, load_m0
import coach_s2 as cs2       # e1_vals, test_vals, g1, g2, b5_arm_w
import coach_verify as cv    # counts, metrics (test primaries)
import coach_skr2e as ce     # feats, metr, boot, cfree_px, key

NC, CR, IN, NOISY, NB = 24, 14, 11, 'CSIR_00070_r8_c4', 2000
CTX = T.parent / 'team_2026-10-29_features' / 'scripts' / 'e1_context.tsv'
clu = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)
LAB = {'nd': 'n.d.', 'BETTER': 'BETTER', 'WORSE': 'WORSE'}
P = print


# ---------------------------------------------------------------- seed-aware two-stage bootstrap (coach_s2_boot.py 7ea26cfb, verbatim)
def sb_feats(c):
    C = np.asarray(c['conf'], float).reshape(NC, NC); x = np.asarray(c['crack_rel2'], float)
    n = sum(1 for sz, h in c['crack_cc']['gt'] if sz >= 20); h = sum(1 for sz, hh in c['crack_cc']['gt'] if sz >= 20 and hh >= 1)
    return [C[CR, CR], C[CR].sum(), C[:, CR].sum(), C[IN, IN], C[IN].sum(), C[:, IN].sum(), x[0], x[1], x[2], x[3], n, h]


def sb_metr(F):  # F (..., 12) summed
    ci = F[..., 0] / np.maximum(F[..., 1] + F[..., 2] - F[..., 0], 1); ii = F[..., 3] / np.maximum(F[..., 4] + F[..., 5] - F[..., 3], 1)
    rp = F[..., 6] / np.maximum(F[..., 7], 1); rr = F[..., 8] / np.maximum(F[..., 9], 1); rf = 2 * rp * rr / np.maximum(rp + rr, 1e-12)
    ah = F[..., 11] / np.maximum(F[..., 10], 1)
    return {'crack': ci, 'relF1': rf, 'inact': ii, 'anyhit': ah, 'relP': rp, 'relR': rr}


def sb_boot(X, inv, ncl, a, b, keys, B=2000, seed=20261102):
    rng = np.random.default_rng(seed); M = np.zeros((ncl, len(inv))); M[inv, np.arange(len(inv))] = 1
    pt = {k: sb_metr(X[b].sum(1))[k].mean() - sb_metr(X[a].sum(1))[k].mean() for k in keys}
    D = {k: [] for k in keys}
    for _ in range(B):
        w = np.bincount(rng.integers(0, ncl, ncl), minlength=ncl) @ M  # cell weights
        sa = rng.integers(0, 5, 5); sb = rng.integers(0, 5, 5)
        Fa = np.einsum('c,rcf->rf', w, X[a][sa]); Fb = np.einsum('c,rcf->rf', w, X[b][sb])
        ma, mb = sb_metr(Fa), sb_metr(Fb)
        for k in keys:
            D[k].append(mb[k].mean() - ma[k].mean())
    out = {}
    for k in keys:
        v = np.array(D[k]); out[k] = (pt[k], np.percentile(v, 2.5), np.percentile(v, 97.5), (v > 0).mean())
    return out


def sb_boot_n(XA, XB, inv, ncl, keys, B=2000, seed=0):
    """the same two-stage bootstrap for any number of runs per arm (leave-one-seed-out); with 5 v 5 it draws exactly as sb_boot."""
    rng = np.random.default_rng(seed); M = np.zeros((ncl, len(inv))); M[inv, np.arange(len(inv))] = 1; D = {k: [] for k in keys}
    for _ in range(B):
        w = np.bincount(rng.integers(0, ncl, ncl), minlength=ncl) @ M
        sa = rng.integers(0, len(XA), len(XA)); sb = rng.integers(0, len(XB), len(XB))
        ma, mb = sb_metr(np.einsum('c,rcf->rf', w, XA[sa])), sb_metr(np.einsum('c,rcf->rf', w, XB[sb]))
        for k in keys:
            D[k].append(mb[k].mean() - ma[k].mean())
    return {k: (float(sb_metr(XB.sum(1))[k].mean() - sb_metr(XA.sum(1))[k].mean()), float(np.percentile(D[k], 2.5)), float(np.percentile(D[k], 97.5)),
                float((np.array(D[k]) > 0).mean())) for k in keys}


def sb_load(MA, MB, split, keep):
    X = {}; stems = None
    for a, ms in (('A', MA), ('B', MB)):
        runs = []
        for d in ms:
            cs_ = d['cells'][split]; st = sorted(s for s in cs_ if keep(s)); stems = stems or st; assert st == stems
            runs.append(np.array([sb_feats(cs_[s]) for s in st]))
        X[a] = np.stack(runs)
    cl = np.array([clu(s) for s in stems]); u, inv = np.unique(cl, return_inverse=True)
    return X, inv, len(u), stems, list(u)


# ---------------------------------------------------------------- verdict R
PRIM = (('crack', 'test crack IoU'), ('relF1', 'test crack relF1@2'), ('inact', 'test inactive IoU'))


def test_metrics(M, keep, split='test'):
    return [cv.metrics(*cv.counts(d, keep, split)) for d in M]


def test_coprim(MA, MB, split='test'):
    """rule 1 per set + the two-set rule, for the 3 test co-primaries. Returns {key: {...}}."""
    out = {}
    va, vb = test_metrics(MA, lambda s: True, split), test_metrics(MB, lambda s: True, split)
    ca, cb = test_metrics(MA, lambda s: s != NOISY, split), test_metrics(MB, lambda s: s != NOISY, split)
    for k, _ in PRIM:
        ra = ct.rule1([m[k] for m in va], [m[k] for m in vb]); rc = ct.rule1([m[k] for m in ca], [m[k] for m in cb])
        out[k] = {'A_all': [m[k] for m in va], 'B_all': [m[k] for m in vb], 'A_clean': [m[k] for m in ca], 'B_clean': [m[k] for m in cb],
                  'all': ra, 'clean': rc, 'two': ct.twoset(ra, rc)}
    out['_desc'] = {k: (float(np.mean([m[k] for m in va])), float(np.mean([m[k] for m in vb]))) for k in ('cP', 'cR', 'relP', 'relR', 'mIoU_rob')}
    return out


def assemble_R(labels, guards):
    """protocol 3a, verbatim: PASS = >= 1 co-primary BETTER, none WORSE, no guard tripped; FAIL = any WORSE, or any guard tripped;
    else n.d. labels: {co-primary: BETTER | WORSE | nd}; guards: {name: bool tripped}."""
    better = [k for k, v in labels.items() if v == 'BETTER']; worse = [k for k, v in labels.items() if v == 'WORSE']; trip = [k for k, v in guards.items() if v]
    if worse or trip:
        return 'FAIL', better, worse, trip
    return ('PASS' if better else 'n.d.'), better, worse, trip


def pix(M, split, keep=lambda s: True):
    """per run: pred / GT crack px, crack px on crack-free cells and their count, any-hit, GT comps >= 20 px."""
    out = []
    for d in M:
        pred = gt = free = nfree = n = h = 0
        for s, x in d['cells'][split].items():
            if not keep(s):
                continue
            C = np.asarray(x['conf'], np.int64).reshape(NC, NC); pred += C[:, CR].sum(); gt += C[CR].sum()
            if C[CR].sum() == 0:
                free += C[:, CR].sum(); nfree += 1
            for sz, hit in x['crack_cc']['gt']:
                if sz >= 20:
                    n += 1; h += int(hit >= 1)
        out.append({'predGT': pred / max(gt, 1), 'free': int(free), 'nfree': nfree, 'anyhit': h / max(n, 1), 'ncomp': n})
    return out


def R_core(MA, MB, recA, runsA, recB, runsB, tag, quiet=False):
    """the 7 co-primaries, the guards and the verdict. MA / MB: loaded m0 dicts (base, arm). Returns a dict of plain numbers."""
    pr = (lambda *a: None) if quiet else P
    res = {'tag': tag}
    # A. test co-primaries
    tc = test_coprim(MA, MB); res['test'] = {}
    pr(f'## R.1 test co-primaries at argmax ({tag}); rule 1 /3; two-set rule (all 50, clean 49 without {NOISY})')
    for k, name in PRIM:
        r = tc[k]; res['test'][k] = {'A_all': r['A_all'], 'B_all': r['B_all'], 'A_clean': r['A_clean'], 'B_clean': r['B_clean'],
                                     'd_all': r['all'][0], 'thr_all': r['all'][1], 'lab_all': r['all'][2], 'd_clean': r['clean'][0], 'thr_clean': r['clean'][1],
                                     'lab_clean': r['clean'][2], 'two': r['two']}
        pr(f'  {name:20s} SUPPF {np.mean(r["A_all"]):.4f}±{np.std(r["A_all"], ddof=1):.4f} SKR01 {np.mean(r["B_all"]):.4f}±{np.std(r["B_all"], ddof=1):.4f} | all 50 {r["all"][0]:+.4f} '
           f'(thr {r["all"][1]:.4f}) {LAB[r["all"][2]]} | clean 49 {r["clean"][0]:+.4f} (thr {r["clean"][1]:.4f}) {LAB[r["clean"][2]]} | two-set {LAB[r["two"]]}')
        pr(f'      per seed all 50: SUPPF {" ".join(f"{x:.4f}" for x in r["A_all"])} | SKR01 {" ".join(f"{x:.4f}" for x in r["B_all"])}')
    res['test_desc'] = tc['_desc']
    # B. B5 wide grid
    BA, BB = cs2.b5_arm_w(recA, runsA), cs2.b5_arm_w(recB, runsB); res['b5'] = {'op': {'SUPPF': BA, 'SKR01': BB}}
    pr(f'## R.2 B5 on the wide grid; arm-pooled OP on val (max recall s.t. precision >= 0.90, tenths, ties smaller b)')
    for nm, B_ in (('SUPPF', BA), ('SKR01', BB)):
        pr(f'  {nm}: grid {B_["grid"]} pooled OP b_comp {B_["b_comp"]:+.1f} b_rel {B_["b_rel"]:+.1f} reachable {B_["reach"]}')
    assert BA['grid'] == BB['grid'] == (-8.0, 12.0, 202), (BA['grid'], BB['grid'])
    for k, name in (('compR', 'B5 comp recall @ comp P >= 0.90'), ('relR', 'B5 relR@2 @ relP@2 >= 0.90')):
        ra = ct.rule1(BA['test'][k], BB['test'][k]); rc = ct.rule1(BA['test_clean'][k], BB['test_clean'][k]); two = ct.twoset(ra, rc)
        prr = ct.rule1(BA['test'][k + '_run'], BB['test'][k + '_run'])
        res['b5'][k] = {'A_all': [float(x) for x in BA['test'][k]], 'B_all': [float(x) for x in BB['test'][k]], 'A_clean': [float(x) for x in BA['test_clean'][k]],
                        'B_clean': [float(x) for x in BB['test_clean'][k]], 'd_all': ra[0], 'thr_all': ra[1], 'lab_all': ra[2], 'd_clean': rc[0], 'thr_clean': rc[1],
                        'lab_clean': rc[2], 'two': two, 'perrun_d': prr[0], 'perrun_thr': prr[1], 'perrun_lab': prr[2],
                        'e1_desc': float(np.mean(BB['ext'][k]) - np.mean(BA['ext'][k]))}
        pr(f'  {name:32s} SUPPF {np.mean(BA["test"][k]):.4f}±{np.std(BA["test"][k], ddof=1):.4f} SKR01 {np.mean(BB["test"][k]):.4f}±{np.std(BB["test"][k], ddof=1):.4f} | all 50 {ra[0]:+.4f} '
           f'(thr {ra[1]:.4f}) {LAB[ra[2]]} | clean 49 {rc[0]:+.4f} (thr {rc[1]:.4f}) {LAB[rc[2]]} | two-set {LAB[two]} | per-run OP all 50 {prr[0]:+.4f} (thr {prr[1]:.4f}) '
           f'{LAB[prr[2]]} (reported) | E1 at the val OP {res["b5"][k]["e1_desc"]:+.4f} (descriptive)')
    for B_ in (BA, BB):
        for st in ('test', 'test_clean', 'ext'):
            B_[st] = {k: [float(x) for x in v] for k, v in B_[st].items()}
    # C. E1 co-primaries
    VA, VB = [cs2.e1_vals(m) for m in MA], [cs2.e1_vals(m) for m in MB]; res['e1'] = {}
    pr(f'## R.3 E1 co-primaries (106 cells pooled per run, argmax; one set)')
    for V in (VA, VB):
        assert all(v['ncomp'] == 296 for v in V), [v['ncomp'] for v in V]
    for k, name in (('relF1', 'E1 crack relF1@2'), ('anyhit', 'E1 any-hit comp recall')):
        r = ct.rule1([v[k] for v in VA], [v[k] for v in VB])
        res['e1'][k] = {'A': [float(v[k]) for v in VA], 'B': [float(v[k]) for v in VB], 'd': r[0], 'thr': r[1], 'lab': r[2]}
        pr(f'  {name:24s} SUPPF {np.mean([v[k] for v in VA]):.4f}±{np.std([v[k] for v in VA], ddof=1):.4f} SKR01 {np.mean([v[k] for v in VB]):.4f}±{np.std([v[k] for v in VB], ddof=1):.4f} '
           f'| d {r[0]:+.4f} (thr {r[1]:.4f}) {LAB[r[2]]}')
        pr(f'      per seed: SUPPF {" ".join(f"{v[k]:.4f}" for v in VA)} | SKR01 {" ".join(f"{v[k]:.4f}" for v in VB)}')
    res['e1_rep'] = {k: (float(np.mean([v[k] for v in VA])), float(np.mean([v[k] for v in VB]))) for k in ('inact', 'relP', 'relR', 'predGT', 'free')}
    res['e1_rep']['free_per_seed'] = ([int(v['free']) for v in VA], [int(v['free']) for v in VB])
    res['e1_rep']['inact_rule1'] = ct.rule1([v['inact'] for v in VA], [v['inact'] for v in VB])
    # D. guards
    MT = {'A': [cs2.test_vals(m) for m in MA], 'B': [cs2.test_vals(m) for m in MB]}; V = {'A': VA, 'B': VB}
    g1 = cs2.g1(MT, 'B', 'A'); g2 = cs2.g2(MT, V, 'B', 'A')
    fa, fb = float(np.mean([v['free'] for v in VA])), float(np.mean([v['free'] for v in VB]))
    nfree = {int(x['nfree']) for M_ in (MA, MB) for x in pix(M_, 'ext')}; assert nfree == {74}, nfree
    res['guards'] = {'G1': {'d_all': float(g1[0]), 'd_clean': float(g1[1]), 'bar': -0.015, 'trip': bool(g1[2])},
                     'G2': {'d_relP': float(g2[0]), 'bar_relP': -0.03, 'trip_relP': bool(g2[0] < -0.03), 'free_arm': fb, 'free_base': fa, 'ratio': float(g2[1]),
                            'bar_px': 1.5 * fa, 'trip_e1': bool(g2[1] > 1.5), 'trip': bool(g2[2]), 'fixed_bar_ref_px': 1.5 * 3931, 'arm_above_fixed_ref': bool(fb > 1.5 * 3931)}}
    pr(f'## R.4 guards (seed means)')
    pr(f'  G1 test inactive IoU d: all 50 {g1[0]:+.4f}, clean 49 {g1[1]:+.4f}; trip iff <= -0.015 in both sets -> {"TRIP" if g1[2] else "ok"}')
    pr(f'  G2 test crack relP@2 d (all 50) {g2[0]:+.4f}; trip iff < -0.03 -> {"TRIP" if g2[0] < -0.03 else "ok"}')
    pr(f'  G2 E1 crack px on the 74 crack-free cells: SKR01 {fb:.1f} vs fresh SUPPF {fa:.1f} = x{g2[1]:.3f}; bar 1.5 x {fa:.1f} = {1.5 * fa:.1f} px (ruling 1) -> '
       f'{"TRIP" if g2[1] > 1.5 else "ok"}   [reference line, decides nothing: fixed s5-9 bar 5,896 px; SKR01 mean above it: {fb > 1.5 * 3931}]')
    pr(f'      per seed crack-free px: SUPPF {res["e1_rep"]["free_per_seed"][0]} | SKR01 {res["e1_rep"]["free_per_seed"][1]}')
    # verdict
    labels = {name: tc[k]['two'] for k, name in PRIM}
    labels.update({'B5 comp recall @ comp P >= 0.90': res['b5']['compR']['two'], 'B5 relR@2 @ relP@2 >= 0.90': res['b5']['relR']['two'],
                   'E1 crack relF1@2': res['e1']['relF1']['lab'], 'E1 any-hit': res['e1']['anyhit']['lab']})
    assert len(labels) == 7
    v, better, worse, trip = assemble_R(labels, {'G1': res['guards']['G1']['trip'], 'G2': res['guards']['G2']['trip']})
    res.update({'labels': labels, 'verdict': v, 'better': better, 'worse': worse, 'trips': trip})
    pr(f'## VERDICT R ({tag}): {v} | BETTER: {better if better else "none"} | WORSE: {worse if worse else "none"} | guards tripped: {trip if trip else "none"}')
    pr('   labels: ' + '; '.join(f'{k} {LAB[x]}' for k, x in labels.items()))
    return res


def loso_R(MA, MB, recA, runsA, recB, runsB, full):
    """leave-one-seed-out: drop one run of one arm (10 drops); rule 1 /3 on 4 v 5; B5 OP kept at the 5-seed pooled OP."""
    P('## R fragility 1: leave-one-seed-out (10 drops; rule 1 /3 on 4 v 5; the B5 OP stays the 5-seed pooled OP)')
    tc = test_coprim(MA, MB); rows = {}
    VA, VB = [cs2.e1_vals(m) for m in MA], [cs2.e1_vals(m) for m in MB]
    b5 = full['b5']
    series = {}
    for k, name in PRIM:
        series[name] = (tc[k]['A_all'], tc[k]['B_all'], tc[k]['A_clean'], tc[k]['B_clean'])
    for k, name in (('compR', 'B5 comp recall @ comp P >= 0.90'), ('relR', 'B5 relR@2 @ relP@2 >= 0.90')):
        series[name] = (b5[k]['A_all'], b5[k]['B_all'], b5[k]['A_clean'], b5[k]['B_clean'])
    for k, name in (('relF1', 'E1 crack relF1@2'), ('anyhit', 'E1 any-hit')):
        series[name] = ([v[k] for v in VA], [v[k] for v in VB], None, None)
    MT = {'A': [cs2.test_vals(m) for m in MA], 'B': [cs2.test_vals(m) for m in MB]}
    drops = [('SUPPF', i) for i in range(5)] + [('SKR01', i) for i in range(5)]
    out = {}
    for name, (a, b, ac, bc) in series.items():
        labs, ds = [], []
        for arm, i in drops:
            sel = lambda v, who: [x for j, x in enumerate(v) if not (arm == who and j == i)]
            r = ct.rule1(sel(a, 'SUPPF'), sel(b, 'SKR01'))
            lab = r[2] if ac is None else ct.twoset(r, ct.rule1(sel(ac, 'SUPPF'), sel(bc, 'SKR01')))
            labs.append(lab); ds.append((r[0], r[1]))
        out[name] = {'labels': labs, 'd_minus_thr': [float(d - t) for d, t in ds], 'd': [float(d) for d, _ in ds]}
        P(f'  {name:32s} full {LAB[full["labels"][name]]:6s} | drops: BETTER {labs.count("BETTER")}, n.d. {labs.count("nd")}, WORSE {labs.count("WORSE")} of 10 | d (all 50 / E1) range '
          f'[{min(d for d, _ in ds):+.4f}, {max(d for d, _ in ds):+.4f}] | labels SUPPF-drops {" ".join(LAB[x] for x in labs[:5])} | SKR01-drops {" ".join(LAB[x] for x in labs[5:])}')
    gl = []
    for arm, i in drops:
        sel = lambda v, who: [x for j, x in enumerate(v) if not (arm == who and j == i)]
        mt = {'A': sel(MT['A'], 'SUPPF'), 'B': sel(MT['B'], 'SKR01')}; vv = {'A': sel(VA, 'SUPPF'), 'B': sel(VB, 'SKR01')}
        a1 = cs2.g1(mt, 'B', 'A'); a2 = cs2.g2(mt, vv, 'B', 'A'); gl.append((float(a1[0]), float(a1[1]), bool(a1[2]), float(a2[0]), float(a2[1]), bool(a2[2])))
    out['guards'] = gl
    P(f'  G1: trips in {sum(g[2] for g in gl)} of 10 drops; d all 50 range [{min(g[0] for g in gl):+.4f}, {max(g[0] for g in gl):+.4f}], clean [{min(g[1] for g in gl):+.4f}, {max(g[1] for g in gl):+.4f}]')
    P(f'  G2: trips in {sum(g[5] for g in gl)} of 10 drops; relP@2 d range [{min(g[3] for g in gl):+.4f}, {max(g[3] for g in gl):+.4f}]; E1 crack-free ratio range '
      f'[x{min(g[4] for g in gl):.3f}, x{max(g[4] for g in gl):.3f}]')
    # verdict per drop
    vd = []
    for q, (arm, i) in enumerate(drops):
        labels = {name: out[name]['labels'][q] for name in series}
        vd.append(assemble_R(labels, {'G1': gl[q][2], 'G2': gl[q][5]})[0])
    out['verdict_per_drop'] = vd
    P(f'  verdict R per drop (SUPPF s10..14, then SKR01 s10..14): {" ".join(vd)}  -> PASS {vd.count("PASS")}, n.d. {vd.count("n.d.")}, FAIL {vd.count("FAIL")} of 10')
    return out


def loco_R(MA, MB, full):
    """leave-one-cluster-out for the m0-based co-primaries and guards: E1 (71 source images) and test (48 modules; rule 1 /3, two-set)."""
    P('## R fragility 2: leave-one-cluster-out (E1: 71 source images; test: 48 modules); rule 1 /3 recomputed on the remaining cells')
    out = {}
    ext = sorted(MA[0]['cells']['ext']); cl = sorted({clu(s) for s in ext}); assert len(cl) == 71
    for k, name in (('relF1', 'E1 crack relF1@2'), ('anyhit', 'E1 any-hit')):
        labs, ds = [], []
        for c in cl:
            def val(m):
                e = {s: x for s, x in m['cells']['ext'].items() if clu(s) != c}
                if k == 'relF1':
                    return ct.e1_agg(e, lambda s: True)['relF1']
                g = [x for v in e.values() for x in v['crack_cc']['gt'] if x[0] >= 20]; return sum(x[1] >= 1 for x in g) / max(len(g), 1)
            r = ct.rule1([val(m) for m in MA], [val(m) for m in MB]); labs.append(r[2]); ds.append((r[0], r[1], c))
        out[name] = {'labels': labs, 'rows': [(float(d), float(t), c) for d, t, c in ds]}
        ch = [f'{c} ({d:+.4f} vs thr {t:.4f})' for (d, t, c), l in zip(ds, labs) if l != full['labels'][name]]
        P(f'  {name:24s} full {LAB[full["labels"][name]]:6s} | drops: BETTER {labs.count("BETTER")}, n.d. {labs.count("nd")}, WORSE {labs.count("WORSE")} of 71 | d range '
          f'[{min(d for d, _, _ in ds):+.4f}, {max(d for d, _, _ in ds):+.4f}] | min (d - thr) {min(d - t for d, t, _ in ds):+.4f}, max {max(d - t for d, t, _ in ds):+.4f}'
          + (f' | label changes when dropping: {"; ".join(ch)}' if ch else ''))
    free = []
    for c in cl:
        fa = np.mean([sum(np.asarray(x['conf'], np.int64).reshape(NC, NC)[:, CR].sum() for s, x in m['cells']['ext'].items() if clu(s) != c and np.asarray(x['conf'], np.int64).reshape(NC, NC)[CR].sum() == 0) for m in MA])
        fb = np.mean([sum(np.asarray(x['conf'], np.int64).reshape(NC, NC)[:, CR].sum() for s, x in m['cells']['ext'].items() if clu(s) != c and np.asarray(x['conf'], np.int64).reshape(NC, NC)[CR].sum() == 0) for m in MB])
        free.append(float(fb / fa))
    out['G2_e1_ratio_range'] = (min(free), max(free))
    P(f'  G2 E1 crack-free ratio over the 71 drops: [x{min(free):.3f}, x{max(free):.3f}] (trip > 1.5: {sum(x > 1.5 for x in free)} drops)')
    test = sorted(MA[0]['cells']['test']); tcl = sorted({clu(s) for s in test}); assert len(tcl) == 48
    for k, name in PRIM:
        labs, ds = [], []
        for c in tcl:
            ra = ct.rule1([m[k] for m in test_metrics(MA, lambda s: clu(s) != c)], [m[k] for m in test_metrics(MB, lambda s: clu(s) != c)])
            rc = ct.rule1([m[k] for m in test_metrics(MA, lambda s: clu(s) != c and s != NOISY)], [m[k] for m in test_metrics(MB, lambda s: clu(s) != c and s != NOISY)])
            labs.append(ct.twoset(ra, rc)); ds.append((ra[0], ra[1], c))
        out[name] = {'labels': labs, 'rows': [(float(d), float(t), c) for d, t, c in ds]}
        ch = [f'{c} ({d:+.4f} vs thr {t:.4f})' for (d, t, c), l in zip(ds, labs) if l != full['labels'][name]]
        P(f'  {name:24s} full {LAB[full["labels"][name]]:6s} | drops (two-set label): BETTER {labs.count("BETTER")}, n.d. {labs.count("nd")}, WORSE {labs.count("WORSE")} of 48 | d (all) range '
          f'[{min(d for d, _, _ in ds):+.4f}, {max(d for d, _, _ in ds):+.4f}]' + (f' | label changes when dropping: {"; ".join(ch)}' if ch else ''))
    g = []
    for c in tcl:
        d1 = np.mean([m['inact'] for m in test_metrics(MB, lambda s: clu(s) != c)]) - np.mean([m['inact'] for m in test_metrics(MA, lambda s: clu(s) != c)])
        d2 = np.mean([m['inact'] for m in test_metrics(MB, lambda s: clu(s) != c and s != NOISY)]) - np.mean([m['inact'] for m in test_metrics(MA, lambda s: clu(s) != c and s != NOISY)])
        d3 = np.mean([m['relP'] for m in test_metrics(MB, lambda s: clu(s) != c)]) - np.mean([m['relP'] for m in test_metrics(MA, lambda s: clu(s) != c)])
        g.append((float(d1), float(d2), float(d3), c))
    out['guards_test_loco'] = g
    P(f'  G1 over the 48 module drops: d all 50 range [{min(x[0] for x in g):+.4f}, {max(x[0] for x in g):+.4f}], clean [{min(x[1] for x in g):+.4f}, {max(x[1] for x in g):+.4f}]; '
      f'trips (<= -0.015 in both) in {sum(x[0] <= -0.015 and x[1] <= -0.015 for x in g)} drops' + ''.join(f'; {x[3]}' for x in g if x[0] <= -0.015 and x[1] <= -0.015))
    P(f'  G2 relP@2 d over the 48 module drops: [{min(x[2] for x in g):+.4f}, {max(x[2] for x in g):+.4f}]; trips (< -0.03) in {sum(x[2] < -0.03 for x in g)} drops')
    return out


def named_boot(MA, MB, seed=0, quiet=False):
    """named claim condition 1 (seed 0) + the same bootstrap of each test co-primary (protocol 4, reported) + stream checks."""
    pr = (lambda *a: None) if quiet else P
    out = {}
    for split, name, keep, nexp in (('test', 'test all 50', lambda s: True, 48), ('test', 'test clean 49', lambda s: s != NOISY, 47), ('ext', 'E1 106', lambda s: True, 71)):
        X, inv, ncl, stems, _ = sb_load(MA, MB, split, keep); assert ncl == nexp, (name, ncl)
        keys = ['crack', 'relF1', 'inact'] if split == 'test' else ['relF1', 'anyhit', 'inact', 'relP', 'relR']
        r = sb_boot(X, inv, ncl, 'A', 'B', keys, B=NB, seed=seed); out[name] = {k: [float(x) for x in v] for k, v in r.items()}
        pr(f'  {name}: {len(stems)} cells, {ncl} clusters; seed-aware two-stage bootstrap, 2,000, RNG seed {seed}' + ('' if split == 'ext' else '   [reported only]'))
        pr('    SKR01 - SUPPF: ' + ' | '.join(f'{k} {v[0]:+.4f} [{v[1]:+.4f}, {v[2]:+.4f}] P>0 {v[3]:.3f}' for k, v in r.items()))
    return out


def R_reported(MA, MB, raw, full):
    P('\n## R reported items (protocol 4; never change a verdict)')
    out = {}
    ctx = {l.split('\t')[0]: l.rstrip('\n').split('\t')[1:] for l in open(CTX) if l.strip()}
    ext = sorted(MA[0]['cells']['ext']); assert set(ext) == set(ctx)
    # width / crack-free px
    P('  width and crack-free px (seed means; SUPPF -> SKR01):')
    for split, n in (('test', 50), ('ext', 106)):
        a, b = pix(MA, split), pix(MB, split)
        ma, mb = test_metrics(MA, lambda s: True, split), test_metrics(MB, lambda s: True, split)
        f = lambda k, m: float(np.mean([x[k] for x in m]))
        out[f'width_{split}'] = {'predGT': (f('predGT', a), f('predGT', b)), 'relP': (f('relP', ma), f('relP', mb)), 'relR': (f('relR', ma), f('relR', mb)), 'cP': (f('cP', ma), f('cP', mb)),
                                 'cR': (f('cR', ma), f('cR', mb)), 'anyhit': (f('anyhit', a), f('anyhit', b)), 'free': (f('free', a), f('free', b)), 'nfree': a[0]['nfree'], 'ncomp': a[0]['ncomp']}
        w = out[f'width_{split}']
        P(f'    {"test (50)" if split == "test" else "E1 (106)"}: pred / GT crack px {w["predGT"][0]:.3f} -> {w["predGT"][1]:.3f} | relP@2 {w["relP"][0]:.4f} -> {w["relP"][1]:.4f} | relR@2 {w["relR"][0]:.4f} -> '
          f'{w["relR"][1]:.4f} | pixel P {w["cP"][0]:.4f} -> {w["cP"][1]:.4f} | pixel R {w["cR"][0]:.4f} -> {w["cR"][1]:.4f} | any-hit {w["anyhit"][0]:.4f} -> {w["anyhit"][1]:.4f} (n {w["ncomp"]}) | '
          f'crack px on the {w["nfree"]} crack-free cells {w["free"][0]:.0f} -> {w["free"][1]:.0f}')
    P(f'    E1 inactive IoU (reported; not a co-primary here): {full["e1_rep"]["inact"][0]:.4f} -> {full["e1_rep"]["inact"][1]:.4f}, rule-1 arithmetic '
      f'{full["e1_rep"]["inact_rule1"][0]:+.4f} (thr {full["e1_rep"]["inact_rule1"][1]:.4f})')
    # E1 strata
    ST = {'scuff + half-cut (29)': lambda s: ctx[s][1] == 'scuff=1' and ctx[s][2] == 'halfcut=1', 'half-cut without scuff (29)': lambda s: ctx[s][1] == 'scuff=0' and ctx[s][2] == 'halfcut=1',
          'full (48)': lambda s: ctx[s][2] == 'halfcut=0', 'half-cut (58)': lambda s: ctx[s][2] == 'halfcut=1', 'other (77)': lambda s: not (ctx[s][1] == 'scuff=1' and ctx[s][2] == 'halfcut=1')}
    P('  E1 strata (seed means ± sd; SUPPF -> SKR01): relF1@2 | any-hit | inactive IoU')
    out['strata'] = {}
    for g, keep in ST.items():
        n = sum(keep(s) for s in ext); assert str(n) in g, (g, n)
        def vals(M):
            r = []
            for m in M:
                e = {s: x for s, x in m['cells']['ext'].items() if keep(s)}; a_ = ct.e1_agg(e, lambda s: True)
                cc = [x for v in e.values() for x in v['crack_cc']['gt'] if x[0] >= 20]
                r.append((a_['relF1'], sum(x[1] >= 1 for x in cc) / len(cc) if cc else float('nan'), a_['inact'], len(cc)))
            return np.array(r)
        a, b = vals(MA), vals(MB); out['strata'][g] = {'A': a.mean(0).tolist(), 'B': b.mean(0).tolist()}
        P(f'    {g:28s} relF1@2 {a[:, 0].mean():.4f}±{a[:, 0].std(ddof=1):.4f} -> {b[:, 0].mean():.4f}±{b[:, 0].std(ddof=1):.4f} | any-hit {a[:, 1].mean():.4f} -> {b[:, 1].mean():.4f} (comps {int(a[0, 3])}) | '
          f'inactive {a[:, 2].mean():.4f} -> {b[:, 2].mean():.4f}')
    # per source test
    P('  per source, test (seed means; SUPPF -> SKR01; descriptive, no labels):')
    out['source'] = {}
    for so in ('ARTS', 'BMRK', 'CFVS', 'CSIR'):
        a, b = test_metrics(MA, lambda s: s.startswith(so)), test_metrics(MB, lambda s: s.startswith(so)); n = sum(s.startswith(so) for s in MA[0]['cells']['test'])
        f = lambda k, m: float(np.nanmean([x[k] for x in m])); out['source'][so] = {k: (f(k, a), f(k, b)) for k in ('crack', 'relF1', 'inact')}
        P(f'    {so} (n {n}): crack IoU {f("crack", a):.4f} -> {f("crack", b):.4f} ({f("crack", b) - f("crack", a):+.4f}) | relF1@2 {f("relF1", a):.4f} -> {f("relF1", b):.4f} | inactive IoU {f("inact", a):.4f} -> {f("inact", b):.4f}')
    # four cell sets
    P('  four test cell sets (rule-1 arithmetic; all 50 and clean 49 are the verdict sets; the twin sets are reported):')
    for sn, keep in cv.SETS.items():
        a, b = test_metrics(MA, keep), test_metrics(MB, keep)
        P(f'    {sn:8s} ' + ' | '.join('%s %+.4f (thr %.4f) %s' % ((k,) + tuple(x if i < 2 else LAB[x] for i, x in enumerate(ct.rule1([m[k] for m in a], [m[k] for m in b])))) for k in ('crack', 'relF1', 'inact')))
    # LA tau 1, scuff-ignored
    for lab, suf, sub in (('LA tau 1', '.tau1', 'm0'), ('scuff-ignored test', '.scuffign', 'm0_scuffign')):
        A = [json.load(open(f'{raw}/{sub}/SUPPF/s2c_SUPPF_100pct_s{k}{suf}.json')) for k in range(10, 15)]
        B = [json.load(open(f'{raw}/{sub}/SKR01/s2c_SKR01_100pct_s{k}{suf}.json')) for k in range(10, 15)]
        assert all(d['step'] == 20000 and len(d['cells']['test']) == 50 for d in A + B)
        tc = test_coprim(A, B); out[lab] = {k: (tc[k]['all'][0], tc[k]['all'][1], tc[k]['all'][2], tc[k]['clean'][0], tc[k]['clean'][1], tc[k]['clean'][2], tc[k]['two']) for k, _ in PRIM}
        P(f'  {lab} (rule-1 arithmetic, reported): ' + ' | '.join(f'{name} all {tc[k]["all"][0]:+.4f} (thr {tc[k]["all"][1]:.4f}) {LAB[tc[k]["all"][2]]}, clean {tc[k]["clean"][0]:+.4f} '
                                                                 f'(thr {tc[k]["clean"][1]:.4f}) {LAB[tc[k]["clean"][2]]}' for k, name in PRIM))
        if suf == '.scuffign':
            sc = A[0].get('scuffign', {}); P(f'      scuff-ignored cells (px set to ignore): {sc}; identical to the default m0 test cells elsewhere: '
                                             f'{all(A[i]["cells"]["test"][s] == MA[i]["cells"]["test"][s] for i in range(5) for s in A[i]["cells"]["test"] if s not in sc)}')
    # paired image bootstrap of the seed means (as my coach_verify; reported)
    stems = sorted(MA[0]['cells']['test'])
    def stack(D):
        return (np.stack([[np.asarray(d['cells']['test'][s]['conf'], float).reshape(NC, NC) for s in stems] for d in D]),
                np.stack([[np.asarray(d['cells']['test'][s]['crack_rel2'], float) for s in stems] for d in D]))
    CB, XB = stack(MA); CA, XA = stack(MB)
    def mean_m(C, X, idx):
        o = [cv.metrics(C[r, idx].sum(0), X[r, idx].sum(0)) for r in range(C.shape[0])]; return np.array([np.mean([q[k] for q in o]) for k in ('crack', 'relF1', 'inact')])
    rng = np.random.default_rng(0); out['imgboot'] = {}
    for sn in ('all', 'noNoisy'):
        idx0 = np.array([i for i, s in enumerate(stems) if cv.SETS[sn](s)]); pt = mean_m(CA, XA, idx0) - mean_m(CB, XB, idx0)
        D = np.array([mean_m(CA, XA, i) - mean_m(CB, XB, i) for i in (rng.choice(idx0, len(idx0)) for _ in range(NB))])
        out['imgboot'][sn] = [(float(pt[j]), float(np.nanpercentile(D[:, j], 2.5)), float(np.nanpercentile(D[:, j], 97.5))) for j in range(3)]
        P(f'  paired image bootstrap of the 5-seed means, fixed models ({sn}; 2,000; reported): ' + ' | '.join(
            f'{k} {pt[j]:+.4f} [{np.nanpercentile(D[:, j], 2.5):+.4f}, {np.nanpercentile(D[:, j], 97.5):+.4f}] P>0 {np.mean(D[:, j] > 0):.2f}' for j, k in enumerate(('crack', 'relF1', 'inact'))))
    # references: #5 rows and the 10-seed view
    PF, S2 = RES / 'pf2/raw/m0', RES / 's2/raw/m0/SKR01'
    OA = [ct.load_m0(f'{PF}/pf2_SUPPF_100pct_s{k}.json', 'e544133') for k in range(5, 10)]; OB = [ct.load_m0(f'{S2}/skr2_SKR01_100pct_s{k}.json', 'c9bbb02') for k in range(5, 10)]
    P('  references (already opened; not contrasts): #5 single means s5-9, this opening s10-14, and the 10-seed view s5-14 ("5 of 10 seeds opened before")')
    out['ten'] = {}
    def allv(M):
        t = test_metrics(M, lambda s: True); tcn = test_metrics(M, lambda s: s != NOISY); e = [cs2.e1_vals(m) for m in M]
        return {'test crack IoU': [m['crack'] for m in t], 'test relF1@2': [m['relF1'] for m in t], 'test inactive IoU': [m['inact'] for m in t], 'clean crack IoU': [m['crack'] for m in tcn],
                'E1 relF1@2': [v['relF1'] for v in e], 'E1 any-hit': [v['anyhit'] for v in e], 'E1 crack-free px': [v['free'] for v in e], 'E1 inactive IoU': [v['inact'] for v in e]}
    a5, b5_, a10, b10 = allv(OA), allv(OB), allv(MA), allv(MB)
    for k in a5:
        d5 = np.mean(b5_[k]) - np.mean(a5[k]); d10 = np.mean(b10[k]) - np.mean(a10[k]); dall = np.mean(b5_[k] + b10[k]) - np.mean(a5[k] + a10[k])
        r10 = ct.rule1(a5[k] + a10[k], b5_[k] + b10[k])
        out['ten'][k] = {'s5_9': (float(np.mean(a5[k])), float(np.mean(b5_[k])), float(d5)), 's10_14': (float(np.mean(a10[k])), float(np.mean(b10[k])), float(d10)),
                         's5_14': (float(np.mean(a5[k] + a10[k])), float(np.mean(b5_[k] + b10[k])), float(dall)), 'sd10': (float(np.std(a5[k] + a10[k], ddof=1)), float(np.std(b5_[k] + b10[k], ddof=1)))}
        fm = '.0f' if 'px' in k else '.4f'
        P(f'    {k:18s} s5-9 {np.mean(a5[k]):{fm}} -> {np.mean(b5_[k]):{fm}} ({d5:+{fm}}) | s10-14 {np.mean(a10[k]):{fm}} -> {np.mean(b10[k]):{fm}} ({d10:+{fm}}) | s5-14 {np.mean(a5[k] + a10[k]):{fm}} -> '
          f'{np.mean(b5_[k] + b10[k]):{fm}} ({dall:+{fm}}; sd over 10 seeds {np.std(a5[k] + a10[k], ddof=1):{fm}} / {np.std(b5_[k] + b10[k], ddof=1):{fm}}; rule-1 /3 arithmetic on 10 v 10: thr {r10[1]:{fm}}, descriptive)')
    P('    FINAL (cv02, R34 5-seed ensemble, b +0.75) clean-test crack IoU 0.492: descriptive only (other machine and commits).')
    return out


def run_R(out_json):
    raw = RES / 's2c/raw_r'
    runsA = [f's2c_SUPPF_100pct_s{k}' for k in range(10, 15)]; runsB = [f's2c_SKR01_100pct_s{k}' for k in range(10, 15)]
    MA = [ct.load_m0(f'{raw}/m0/SUPPF/{r}.json', 'e544133') for r in runsA]; MB = [ct.load_m0(f'{raw}/m0/SKR01/{r}.json', 'c9bbb02') for r in runsB]
    assert [m['run'] for m in MA] == runsA and [m['run'] for m in MB] == runsB
    assert all(sorted(m['cells']['test']) == sorted(MA[0]['cells']['test']) and sorted(m['cells']['ext']) == sorted(MA[0]['cells']['ext']) for m in MA + MB)
    assert all(len(c['conf']) == 576 for m in MA + MB for sp in ('test', 'ext') for c in m['cells'][sp].values())
    P('# coach recompute, verdict R of protocol_SKR2C (E1 opening #7; same 50 test and 106 E1 cells as #5 / #6, 3rd look); singles s10-14, argmax m0 JSONs')
    P(f'# inputs: {raw}/m0/{{SUPPF,SKR01}}/<run>.json (step 20000; code_revision e544133 / c9bbb02 asserted), {raw}/b5/{{SUPPF,SKR01}}/rec_w')
    full = R_core(MA, MB, f'{raw}/b5/SUPPF/rec_w', runsA, f'{raw}/b5/SKR01/rec_w', runsB, 'fresh seeds 10-14, SKR01 - SUPPF')
    P('\n## R.5 named claim, condition 1 (protocol 3a): seed-aware two-stage bootstrap (seeds within arm x clusters), 2,000 draws, seed 0')
    nb = named_boot(MA, MB, 0); e1 = nb['E1 106']['relF1']; c1 = bool(e1[1] > 0)
    P(f'  CONDITION 1: 95% CI of E1 crack relF1@2 = [{e1[1]:+.4f}, {e1[2]:+.4f}] (estimate {e1[0]:+.4f}); wholly above 0: {c1}')
    X, inv, ncl, stems, cl = sb_load(MA, MB, 'ext', lambda s: True)
    chk = sb_boot_n(X['A'], X['B'], inv, ncl, ['relF1'], NB, 0)['relF1']; assert abs(chk[1] - e1[1]) < 1e-12 and abs(chk[2] - e1[2]) < 1e-12
    lows = []
    for sd in list(range(1, 21)) + [20261102]:
        r = sb_boot_n(X['A'], X['B'], inv, ncl, ['relF1'], NB, sd)['relF1']; lows.append((sd, r[1], r[2], r[3]))
    P(f'  stream check (not the registered CI): seeds 1..20 and 20261102: lower bound range [{min(x[1] for x in lows):+.4f}, {max(x[1] for x in lows):+.4f}], upper '
      f'[{min(x[2] for x in lows):+.4f}, {max(x[2] for x in lows):+.4f}]; lower bound > 0 in {sum(x[1] > 0 for x in lows)} of {len(lows)} streams; P(d > 0) range '
      f'[{min(x[3] for x in lows):.3f}, {max(x[3] for x in lows):.3f}]')
    r20 = sb_boot_n(X['A'], X['B'], inv, ncl, ['relF1', 'anyhit'], 20000, 0)
    P(f'  20,000 draws, seed 0 (not the registered CI): relF1@2 [{r20["relF1"][1]:+.4f}, {r20["relF1"][2]:+.4f}] P>0 {r20["relF1"][3]:.4f}; any-hit [{r20["anyhit"][1]:+.4f}, {r20["anyhit"][2]:+.4f}]')
    # leave-one-seed-out and leave-one-cluster-out of condition 1
    ls = []
    for arm in ('A', 'B'):
        for i in range(5):
            XA = X['A'][[j for j in range(5) if not (arm == 'A' and j == i)]]; XB = X['B'][[j for j in range(5) if not (arm == 'B' and j == i)]]
            ls.append(sb_boot_n(XA, XB, inv, ncl, ['relF1'], NB, 0)['relF1'])
    P(f'  condition 1 under leave-one-seed-out (10 drops; 4 v 5, seed 0): CI above 0 in {sum(x[1] > 0 for x in ls)} of 10; lower bounds '
      + ' '.join(f'{x[1]:+.4f}' for x in ls) + f' (SUPPF s10..14, then SKR01 s10..14); estimates {min(x[0] for x in ls):+.4f} .. {max(x[0] for x in ls):+.4f}')
    lc = []
    for ci in range(ncl):
        keepc = np.array([j for j in range(len(inv)) if inv[j] != ci]); u2, inv2 = np.unique(inv[keepc], return_inverse=True)
        lc.append(sb_boot_n(X['A'][:, keepc], X['B'][:, keepc], inv2, len(u2), ['relF1'], NB, 0)['relF1'] + (cl[ci],))
    flip = [f'{x[4]} ([{x[1]:+.4f}, {x[2]:+.4f}])' for x in lc if (x[1] > 0) != c1]
    P(f'  condition 1 under leave-one-cluster-out (71 drops; seed 0): CI above 0 in {sum(x[1] > 0 for x in lc)} of 71; lower bound range [{min(x[1] for x in lc):+.4f}, {max(x[1] for x in lc):+.4f}]'
      + (f'; outcome changes when dropping: {"; ".join(flip)}' if flip else '; no drop changes the outcome'))
    P('')
    lo = loso_R(MA, MB, f'{raw}/b5/SUPPF/rec_w', runsA, f'{raw}/b5/SKR01/rec_w', runsB, full)
    lc2 = loco_R(MA, MB, full)
    rep = R_reported(MA, MB, raw, full)
    full.update({'named': nb, 'cond1': c1, 'cond1_ci': [e1[0], e1[1], e1[2], e1[3]], 'cond1_streams': lows, 'cond1_loso': ls, 'cond1_loco_n_above': int(sum(x[1] > 0 for x in lc)),
                 'cond1_loco_range': [min(x[1] for x in lc), max(x[1] for x in lc)], 'loso': lo, 'loco': lc2, 'reported': rep})
    json.dump(full, open(out_json, 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))


# ---------------------------------------------------------------- verdict D
DN = ce.NAMES  # ['crack IoU', 'relF1@2', 'inactive IoU', 'any-hit', 'relP@2']


def d_boot(JA, JB, split, keep, cluster, rng):
    st = sorted(s for s in JA[split] if keep(s)); assert sorted(s for s in JB[split] if keep(s)) == st
    if cluster:
        cl = sorted({ce.key(s) for s in st}); groups = [np.array([i for i, s in enumerate(st) if ce.key(s) == c]) for c in cl]
    else:
        groups = [np.array([i]) for i in range(len(st))]
    full, lo, hi = ce.boot(ce.feats(JA[split], st), ce.feats(JB[split], st), groups, rng)
    return full, lo, hi, len(groups), st


def d_pair(JA, JB, la, lb, tag, quiet=False, verdict_line=True):
    """one pair: test primaries (two sets), E1 primaries, guards, verdict D per protocol 3b. CIs: fresh default_rng(0) per bootstrap
    (= the registered seed-0 draws); second stream default_rng(12345) shared, as a check."""
    pr = (lambda *a: None) if quiet else P
    res = {'tag': tag, 'test': {}, 'e1': {}}
    rng2 = np.random.default_rng(12345); rows = {}; rows2 = {}
    for sn, kp in (('all 50', lambda s: True), ('clean 49', lambda s: s != NOISY)):
        full, lo, hi, n, st = d_boot(JA, JB, 'test', kp, False, np.random.default_rng(0)); rows[sn] = (full, lo, hi)
        f2, lo2, hi2, _, _ = d_boot(JA, JB, 'test', kp, False, rng2); rows2[sn] = (f2, lo2, hi2)
        a = ce.metr(*(x.sum(0) for x in ce.feats(JA['test'], st))); b = ce.metr(*(x.sum(0) for x in ce.feats(JB['test'], st)))
        res['test'][sn] = {DN[i]: {'A': float(a[i]), 'B': float(b[i]), 'd': float(full[i]), 'lo': float(lo[i]), 'hi': float(hi[i]), 'lo2': float(lo2[i]), 'hi2': float(hi2[i])} for i in range(5)}
        pr(f'  test {sn:8s} (n {n}) ' + ' | '.join(f'{DN[i]} {a[i]:.4f} -> {b[i]:.4f} = {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}] (stream 2 [{lo2[i]:+.4f}, {hi2[i]:+.4f}])' for i in (0, 1, 2))
           + f' | relP@2 {a[4]:.4f} -> {b[4]:.4f} = {full[4]:+.4f}')
    def tv(rows):
        fail = [DN[i] for i in (0, 1, 2) if any(rows[s][2][i] < 0 for s in rows)]
        pas = [DN[i] for i in (0, 1, 2) if all(rows[s][1][i] > 0 for s in rows) or (any(rows[s][1][i] > 0 for s in rows) and all(rows[s][0][i] > 0 for s in rows))]
        return pas, fail
    pas, fail = tv(rows); pas2, fail2 = tv(rows2)
    full, lo, hi, ncl, st = d_boot(JA, JB, 'ext', lambda s: True, True, np.random.default_rng(0)); assert ncl == 71 and len(st) == 106
    f2, lo2, hi2, _, _ = d_boot(JA, JB, 'ext', lambda s: True, True, rng2)
    FA, FB = ce.feats(JA['ext'], st), ce.feats(JB['ext'], st); assert FA[2][:, 1].sum() == 296 == FB[2][:, 1].sum()
    a = ce.metr(*(x.sum(0) for x in FA)); b = ce.metr(*(x.sum(0) for x in FB))
    res['e1'] = {DN[i]: {'A': float(a[i]), 'B': float(b[i]), 'd': float(full[i]), 'lo': float(lo[i]), 'hi': float(hi[i]), 'lo2': float(lo2[i]), 'hi2': float(hi2[i])} for i in range(5)}
    res['e1']['anyhit_counts'] = (int(FA[2][:, 0].sum()), int(FB[2][:, 0].sum()), 296)
    pr(f'  E1 (106 cells, 71 clusters) ' + ' | '.join(f'{DN[i]} {a[i]:.4f} -> {b[i]:.4f} = {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}] (stream 2 [{lo2[i]:+.4f}, {hi2[i]:+.4f}])' for i in (1, 3, 2))
       + f' | any-hit {la} {FA[2][:, 0].sum()}/296, {lb} {FB[2][:, 0].sum()}/296')
    e_pass = [('E1 crack relF1@2', 1), ('E1 any-hit', 3)]
    epas = [n for n, i in e_pass if lo[i] > 0]; efail = [n for n, i in e_pass if hi[i] < 0]
    epas2 = [n for n, i in e_pass if lo2[i] > 0]; efail2 = [n for n, i in e_pass if hi2[i] < 0]
    na, pa = ce.cfree_px(JA['ext']); nb_, pb = ce.cfree_px(JB['ext']); assert na == nb_ == 74
    G = {'G2a test relP@2 d < -0.03': (bool(rows['all 50'][0][4] < -0.03), float(rows['all 50'][0][4])),
         f'G2b E1 crack-free px > 1.5 x {la}': (bool(pb > 1.5 * pa), (int(pb), int(pa), float(pb / max(pa, 1)), 1.5 * pa)),
         'G1t test inactive d <= -0.015 in both sets': (bool(rows['all 50'][0][2] <= -0.015 and rows['clean 49'][0][2] <= -0.015), (float(rows['all 50'][0][2]), float(rows['clean 49'][0][2]))),
         'G1e E1 inactive cluster CI wholly below 0': (bool(hi[2] < 0), (float(full[2]), float(lo[2]), float(hi[2])))}
    pr(f'  guards: G2a test relP@2 d (all 50) {rows["all 50"][0][4]:+.4f} (trip < -0.03) {"TRIP" if G["G2a test relP@2 d < -0.03"][0] else "ok"} | G2b E1 crack px on the 74 crack-free cells {lb} {pb} vs {la} {pa} '
       f'(x{pb / max(pa, 1):.3f}; bar {1.5 * pa:.0f}) {"TRIP" if pb > 1.5 * pa else "ok"} | G1t test inactive d {rows["all 50"][0][2]:+.4f} / {rows["clean 49"][0][2]:+.4f} (trip <= -0.015 in both) '
       f'{"TRIP" if G["G1t test inactive d <= -0.015 in both sets"][0] else "ok"} | G1e E1 inactive {full[2]:+.4f} [{lo[2]:+.4f}, {hi[2]:+.4f}] (trip: CI below 0) {"TRIP" if hi[2] < 0 else "ok"}')
    trips = [g for g, (t, _) in G.items() if t]
    car = [f'test {n}' for n in pas] + epas; pf = [f'test {n}' for n in fail] + efail
    V = 'FAIL' if (pf or trips) else ('PASS' if car else 'n.d.')
    car2 = [f'test {n}' for n in pas2] + epas2; pf2 = [f'test {n}' for n in fail2] + efail2
    V2 = 'FAIL' if (pf2 or trips or hi2[2] < 0) else ('PASS' if car2 else 'n.d.')
    near = [f'test {s} {DN[i]}' for s in rows for i in (0, 1, 2) if min(abs(rows[s][1][i]), abs(rows[s][2][i])) < 0.002] + [f'E1 {DN[i]}' for i in (1, 3, 2) if min(abs(lo[i]), abs(hi[i])) < 0.002]
    res.update({'verdict': V, 'carriers': car, 'primary_fails': pf, 'trips': trips, 'guards': {g: {'trip': t, 'detail': d} for g, (t, d) in G.items()}, 'verdict_stream2': V2, 'carriers_stream2': car2,
                'near_zero_bounds': near, 'e1_relF1_primary_passes': bool(lo[1] > 0), 'cfree': (int(pa), int(pb))})
    if verdict_line:
        pr(f'## VERDICT D ({tag}): {V} | passing primaries: {car if car else "none"} | failing primaries: {pf if pf else "none"} | guard trips: {trips if trips else "none"}')
        pr(f'   second RNG stream: {V2}, passing {car2 if car2 else "none"}' + (f' | bounds within 0.002 of 0 (seed-0 CIs): {near}' if near else ' | no bound within 0.002 of 0'))
    else:
        pr(f'  ({tag}; not a verdict) CIs above 0: {car if car else "none"}; CIs below 0: {pf if pf else "none"}; guard-form trips: {trips if trips else "none"}')
    return res


def d_wording(res):
    """protocol 3b fixed wording."""
    L = []; car = res['carriers']
    if res['verdict'] == 'PASS':
        L.append(f'VERDICT D PASS, carried by: {", ".join(car)}.')
        if set(car) <= {'test crack IoU', 'test relF1@2', 'E1 any-hit'}:
            L.append('carried by argmax readouts that were mostly volume on seeds 5-9 (SKR2E §3a); see the matched-volume lines (§4).')
        if not any(c.startswith('E1') for c in car):
            L.append("SKR2's E1 gain is not replicated at ensemble level.")
    elif res['verdict'] == 'FAIL':
        L.append(f'VERDICT D FAIL: ' + '; '.join(([f'primary fails: {", ".join(res["primary_fails"])}'] if res['primary_fails'] else []) + ([f'guard trips: {", ".join(res["trips"])}'] if res['trips'] else [])) + '.')
        if not res['primary_fails'] and res['trips'] and all(t.startswith(('G1t', 'G1e')) for t in res['trips']):
            L.append("inactive guard alone: D's G1t null false-FAIL ~8%; with R's G1 ~9-15%, ~15% combined that a true null keeps SUP100-PF through an inactive guard alone (protocol 3c, judge L2).")
    else:
        L.append('VERDICT D n.d.; the SUP100-PF ensemble stays (protocol 3c).')
    if 'E1 any-hit' in car:
        L.append('(every any-hit line carries the per-image concentration line: see D reported, E1 concentration.)')
    return L


def d_reported(J, dec, sw, la, lb, bmv, rjson=None):
    P('\n## D reported items (protocol 4; never change a verdict)')
    out = {}
    ctx = {l.split('\t')[0]: l.rstrip('\n').split('\t')[1:] for l in open(CTX) if l.strip()}
    A, B = J[(la, 0.0)], J[(lb, 0.0)]; ext = sorted(A['ext']); assert set(ext) == set(ctx)
    def px(cells, stems):
        C = sum(np.asarray(cells[s]['conf'], np.int64).reshape(NC, NC) for s in stems); return int(C[CR].sum()), int(C[:, CR].sum()), int(C[CR, CR])
    def hits(cells, stems):
        h = n = 0
        for s in stems:
            for g in cells[s]['crack_cc']['gt']:
                if g[0] >= 20:
                    n += 1; h += int(g[1] >= 1)
        return h, n
    def mm(cells, stems):
        return ce.metr(*(x.sum(0) for x in ce.feats(cells, stems)))
    # val decisions re-derived
    P('  val decisions (reported; val only):')
    GRID = [round(0.25 * i, 2) for i in range(13)]
    for k in (la, lb):
        s_ = {float(b): v for b, v in dec[k]['sweep'].items()}; ok = [b for b in GRID if s_[b]['relR2'] >= 0.90]
        bias = ok[0] if ok and s_[ok[0]]['relP2'] >= 0.90 else max(GRID, key=lambda b: s_[b]['relF1']); width = s_[0.0]['crack_P'] - s_[bias]['crack_P']
        assert bias == dec[k]['bias'] and abs(width - dec[k]['val_crack_precision_drop_at_bias']) < 1e-12 and (0.0 if width > 0.05 else bias) == dec[k]['headline_bias']
        st = sorted(J[(k, 0.0)]['val']); m = mm(J[(k, 0.0)]['val'], st); g, p, tp = px(J[(k, 0.0)]['val'], st)
        dmax = max(abs(m[0] - s_[0.0]['crack_iou']), abs(tp / p - s_[0.0]['crack_P']), abs(m[4] - s_[0.0]['relP2']), abs(m[1] - s_[0.0]['relF1']), abs(m[2] - s_[0.0]['inact_iou']))
        out[f'val_{k}'] = {'d2': bias, 'drop': width, 'flag': bool(width > 0.05), 'relR_at': s_[bias]['relR2'], 'relP_at': s_[bias]['relP2'], 'val_b0': {x: s_[0.0][x] for x in s_[0.0]}}
        P(f'    {k}: D2 b {bias} (val relR@2 {s_[bias]["relR2"]:.4f}, relP@2 {s_[bias]["relP2"]:.4f}); val crack precision drop {width:+.4f}; width flag {"ON" if width > 0.05 else "off"} '
          f'(reported only); = decisions file; sweep entry at b 0 re-summed from the val cells: max |diff| {dmax:.1e}')
    gv = {float(b): v for b, v in dec['b_mv']['val_pred_over_gt_grid'].items()}; tgt = dec['b_mv']['target_val_pred_over_gt']
    BMV = [round(-1.5 + 0.05 * i, 2) + 0.0 for i in range(41)]; assert sorted(gv) == sorted(BMV)
    mine = min(BMV, key=lambda b: (abs(gv[b] - tgt), abs(b), b)); assert mine == bmv == dec['b_mv']['b_mv'], (mine, bmv)
    va = px(A['val'], sorted(A['val'])); vb0 = px(B['val'], sorted(B['val'])); vbm = px(J[(lb, bmv)]['val'], sorted(J[(lb, bmv)]['val']))
    assert abs(va[1] / va[0] - tgt) < 1e-12 and abs(vbm[1] / vbm[0] - gv[bmv]) < 1e-12 and abs(vb0[1] / vb0[0] - gv[0.0]) < 1e-12
    srt = sorted(BMV, key=lambda b: (abs(gv[b] - tgt), abs(b), b))
    out['bmv'] = {'b_mv': bmv, 'target': tgt, 'at_bmv': gv[bmv], 'at_b0': gv[0.0], 'second': (srt[1], gv[srt[1]])}
    P(f'    b_mv {bmv}: val crack pred / GT of {lb} {gv[bmv]:.4f} vs {la} at b 0 {tgt:.4f} (at b 0 {lb} has {gv[0.0]:.4f}); next nearest b {srt[1]} ({gv[srt[1]]:.4f}); re-derived from the stored grid and '
          f're-summed from the val cells of the three files: equal')
    # b_mv pair
    P(f'  matched val volume pair (reported, not a verdict): {la} b 0 vs {lb} b_mv {bmv}')
    out['bmv_pair'] = d_pair(A, J[(lb, bmv)], la, lb, f'reported pair {la} b 0 vs {lb} b_mv {bmv}', verdict_line=False)
    # width
    P('  width (b 0 pair and b_mv): pred / GT crack px, pixel P / R, relP@2 / relR@2; crack px on crack-free cells test / E1 / val')
    out['width'] = {}
    for k, b in ((la, 0.0), (lb, 0.0), (lb, bmv)):
        row = []; out['width'][f'{k} b {b}'] = {}
        for sp in ('test', 'ext'):
            c = J[(k, b)][sp]; st = sorted(c); g, p, tp = px(c, st); R_ = ce.feats(c, st)[1].sum(0); h, n = hits(c, st)
            out['width'][f'{k} b {b}'][sp] = {'predGT': p / g, 'P': tp / p, 'R': tp / g, 'relP': R_[0] / R_[1], 'relR': R_[2] / R_[3], 'anyhit': (h, n)}
            row.append(f'{sp} pred/GT {p / g:.3f} P {tp / p:.3f} R {tp / g:.3f} relP {R_[0] / R_[1]:.4f} relR {R_[2] / R_[3]:.4f} any-hit {h}/{n}')
        cf = [ce.cfree_px(J[(k, b)][sp]) for sp in ('test', 'ext', 'val')]; out['width'][f'{k} b {b}']['cfree'] = cf
        P(f'    {k} b {b}: ' + ' | '.join(row) + ' | crack-free px ' + ' / '.join(f'{p} ({n} cells)' for n, p in cf))
    # four test sets, noscuff, per source
    P('  four test cell sets and test_noscuff (b 0 pair; seed-0 image bootstrap):')
    out['sets'] = {}
    for sn, kp in cv.SETS.items():
        full, lo, hi, n, _ = d_boot(A, B, 'test', kp, False, np.random.default_rng(0)); out['sets'][sn] = [(float(full[i]), float(lo[i]), float(hi[i])) for i in (0, 1, 2)]
        P(f'    {sn:8s} (n {n}) ' + ' | '.join(f'{DN[i]} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}]' for i in (0, 1, 2)))
    for sn, kp in (('all 50', lambda s: True), ('clean 49', lambda s: s != NOISY)):
        full, lo, hi, n, _ = d_boot(A, B, 'test_noscuff', kp, False, np.random.default_rng(0)); out['sets']['noscuff ' + sn] = [(float(full[i]), float(lo[i]), float(hi[i])) for i in (0, 1, 2)]
        P(f'    test_noscuff {sn} (n {n}) ' + ' | '.join(f'{DN[i]} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}]' for i in (0, 1, 2)))
    P('  per source, test (b 0 pair):')
    out['source'] = {}
    for so in ('ARTS', 'BMRK', 'CFVS', 'CSIR'):
        st = sorted(s for s in A['test'] if s.startswith(so)); a, b = mm(A['test'], st), mm(B['test'], st); out['source'][so] = (a[:3].tolist(), b[:3].tolist())
        P(f'    {so} (n {len(st)}): crack IoU {a[0]:.4f} -> {b[0]:.4f} ({b[0] - a[0]:+.4f}) | relF1@2 {a[1]:.4f} -> {b[1]:.4f} | inactive IoU {a[2]:.4f} -> {b[2]:.4f}')
    # E1 strata
    ST = {'scuff + half-cut (29)': lambda s: ctx[s][1] == 'scuff=1' and ctx[s][2] == 'halfcut=1', 'half-cut without scuff (29)': lambda s: ctx[s][1] == 'scuff=0' and ctx[s][2] == 'halfcut=1',
          'full (48)': lambda s: ctx[s][2] == 'halfcut=0', 'other (77)': lambda s: not (ctx[s][1] == 'scuff=1' and ctx[s][2] == 'halfcut=1')}
    P('  E1 strata (b 0 pair): any-hit hits / comps, relF1@2, inactive IoU, pred / GT')
    out['strata'] = {}
    for sn, f in ST.items():
        st = [s for s in ext if f(s)]; assert str(len(st)) in sn; row = []; out['strata'][sn] = {}
        for k, c in ((la, A['ext']), (lb, B['ext'])):
            h, n = hits(c, st); m = mm(c, st); g, p, _ = px(c, st); out['strata'][sn][k] = {'hits': h, 'n': n, 'relF1': float(m[1]), 'inact': float(m[2]), 'predGT': p / max(g, 1)}
            row.append(f'{k} {h}/{n} relF1 {m[1]:.4f} inact {m[2]:.4f} pred/GT {p / max(g, 1):.3f}')
        P(f'    {sn:28s} ' + ' | '.join(row))
    # concentration
    cl = sorted({ce.key(s) for s in ext}); per = []
    for c in cl:
        st = [s for s in ext if ce.key(s) == c]; n = hits(A['ext'], st)[1]
        if n:
            per.append((n, c, hits(A['ext'], st)[0], hits(B['ext'], st)[0], hits(J[(lb, bmv)]['ext'], st)[0], sum(ST['scuff + half-cut (29)'](s) for s in st), len(st)))
    per.sort(reverse=True); N = sum(p[0] for p in per); gains = [(p[3] - p[2], p[1]) for p in per if p[3] != p[2]]
    pos = sorted((g for g in gains if g[0] > 0), reverse=True); neg = [g for g in gains if g[0] < 0]; tot = sum(g[0] for g in gains)
    out['conc'] = {'n_images': len(per), 'N': N, 'top3': sum(p[0] for p in per[:3]) / N, 'top10': sum(p[0] for p in per[:10]) / N, 'n_eff': N ** 2 / sum(p[0] ** 2 for p in per),
                   'gain_total': tot, 'gain_pos': pos, 'gain_neg': neg, 'gain_n_eff': (sum(g[0] for g in pos) ** 2 / sum(g[0] ** 2 for g in pos)) if pos else 0.0,
                   'in_scuff_hc': (hits(A['ext'], [s for s in ext if ST['scuff + half-cut (29)'](s)]), hits(B['ext'], [s for s in ext if ST['scuff + half-cut (29)'](s)]))}
    P(f'  E1 any-hit concentration (per-image line): {len(per)} of 71 images hold the {N} GT comps >= 20 px; top 3 images {out["conc"]["top3"]:.2f}, top 10 {out["conc"]["top10"]:.2f}, n_eff {out["conc"]["n_eff"]:.1f}; '
      f'{out["conc"]["in_scuff_hc"][0][1]} comps in the 29 scuff + half-cut cells')
    P(f'    b 0 pair: net extra hits {tot:+d}; images up {len(pos)} ({", ".join(f"{c} +{g}" for g, c in pos)}); images down {len(neg)} ({", ".join(f"{c} {g}" for g, c in neg)}); '
      f'n_eff of the positive part {out["conc"]["gain_n_eff"]:.1f} images; scuff + half-cut cells {out["conc"]["in_scuff_hc"][0][0]} -> {out["conc"]["in_scuff_hc"][1][0]} of {out["conc"]["in_scuff_hc"][0][1]}')
    for p in per[:10]:
        P(f'      {p[1]:18s} comps {p[0]:3d}  hits {la} b0 {p[2]:3d} | {lb} b0 {p[3]:3d} | {lb} b_mv {p[4]:3d}   cells {p[6]} (scuff+hc {p[5]})')
    def e1d(st, kb=0.0):
        return mm(J[(lb, kb)]['ext'], st) - mm(A['ext'], st)
    fulld = e1d(ext); top3 = [p[1] for p in per[:3]]
    ig = {}
    for s in ext:
        ig[ce.key(s)] = ig.get(ce.key(s), 0) + int(np.asarray(A['ext'][s]['conf'], np.int64).reshape(NC, NC)[IN].sum())
    it = sorted(((v, c) for c, v in ig.items() if v), reverse=True); TI = sum(v for v, _ in it)
    d3 = e1d([s for s in ext if ce.key(s) not in top3]); di = e1d([s for s in ext if ce.key(s) not in [c for _, c in it[:3]]])
    lo_ = [e1d([s for s in ext if ce.key(s) != c]) for c in cl]
    out['robust'] = {'full': fulld.tolist(), 'no_top3_crack': d3.tolist(), 'no_top3_inact': di.tolist(), 'inact_px': TI, 'inact_images': len(it), 'inact_top3': sum(v for v, _ in it[:3]) / TI,
                     'inact_n_eff': TI ** 2 / sum(v * v for v, _ in it), 'loco': {DN[i]: (float(min(x[i] for x in lo_)), float(max(x[i] for x in lo_))) for i in (1, 3, 2)}}
    P(f'  E1 robustness (b 0 pair): all 106 relF1@2 {fulld[1]:+.4f} any-hit {fulld[3]:+.4f} inactive {fulld[2]:+.4f} | without the top-3 crack-comp images {top3}: relF1@2 {d3[1]:+.4f} any-hit {d3[3]:+.4f} '
      f'inactive {d3[2]:+.4f}')
    P(f'    E1 GT inactive px {TI} in {len(it)} images, top 3 {out["robust"]["inact_top3"]:.3f} ({[c for _, c in it[:3]]}), n_eff {out["robust"]["inact_n_eff"]:.1f}; without them: relF1@2 {di[1]:+.4f} any-hit {di[3]:+.4f} inactive {di[2]:+.4f}')
    P('    leave-one-cluster-out (71 drops), point estimates: ' + ' | '.join(f'{DN[i]} [{min(x[i] for x in lo_):+.4f}, {max(x[i] for x in lo_):+.4f}]' for i in (1, 3, 2)))
    # E1 sweep + matched volume
    sp = {k: {float(b): v for b, v in sw[k].items()} for k in (la, lb)}; g = sorted(sp[la]); assert g == [round(-1.5 + 0.25 * i, 2) for i in range(19)]
    for k in (la, lb):
        c = J[(k, 0.0)]['ext']; assert sp[k][0.0]['anyhit_hits'] == hits(c, ext)[0] and sp[k][0.0]['crack_free_px'] == ce.cfree_px(c)[1] and abs(sp[k][0.0]['relF1'] - mm(c, ext)[1]) < 1e-9
    P('  E1 aggregate sweep (-1.5 .. 3, step 0.25; E1-oracle, descriptive, chooses nothing); sweep entries at b 0 == the per-cell files (any-hit hits, crack-free px, relF1@2)')
    P('    b: ' + f'{la} pred/GT relF1 any-hit-hits crack-free px | {lb} the same | relF1 d at equal b')
    out['sweep'] = {}
    for b in g:
        out['sweep'][b] = {k: (sp[k][b]['pred_over_gt'], sp[k][b]['relF1'], sp[k][b]['anyhit_hits'], sp[k][b]['crack_free_px']) for k in (la, lb)}
        P(f'    {b:5.2f}: ' + ' | '.join(f'{sp[k][b]["pred_over_gt"]:.3f} {sp[k][b]["relF1"]:.4f} {sp[k][b]["anyhit_hits"]:3d} {sp[k][b]["crack_free_px"]:5d}' for k in (la, lb)) + f' | {sp[lb][b]["relF1"] - sp[la][b]["relF1"]:+.4f}')
    t = sp[lb][0.0]['pred_over_gt']; pv = [sp[la][b]['pred_over_gt'] for b in g]
    if all(x < y for x, y in zip(pv, pv[1:])) and pv[0] <= t <= pv[-1]:
        i = max(j for j in range(len(g) - 1) if pv[j] <= t); w = (t - pv[i]) / (pv[i + 1] - pv[i]); bm = g[i] + w * (g[i + 1] - g[i])
        li = lambda f: sp[la][g[i]][f] + w * (sp[la][g[i + 1]][f] - sp[la][g[i]][f])
        d0f, d0a = sp[lb][0.0]['relF1'] - sp[la][0.0]['relF1'], sp[lb][0.0]['anyhit'] - sp[la][0.0]['anyhit']
        out['matched_e1'] = {'b': bm, 'relF1_d0': d0f, 'relF1_dm': sp[lb][0.0]['relF1'] - li('relF1'), 'anyhit_d0': d0a, 'anyhit_dm': sp[lb][0.0]['anyhit'] - li('anyhit'), 'cfree': (sp[lb][0.0]['crack_free_px'], li('crack_free_px'))}
        P(f'  E1 matched volume: {lb} b 0 pred/GT {t:.4f}; {la} reaches it at b {bm:.3f} (linear between {g[i]:g} and {g[i + 1]:g}): relF1@2 d {d0f:+.4f} at b 0 -> {sp[lb][0.0]["relF1"] - li("relF1"):+.4f} at matched volume'
          + (f' (bias share {(li("relF1") - sp[la][0.0]["relF1"]) / d0f:.0%})' if abs(d0f) > 1e-9 else '') + f'; any-hit d {d0a:+.4f} -> {sp[lb][0.0]["anyhit"] - li("anyhit"):+.4f}'
          + (f' (bias share {(li("anyhit") - sp[la][0.0]["anyhit"]) / d0a:.0%})' if abs(d0a) > 1e-9 else '') + f'; crack-free px {sp[lb][0.0]["crack_free_px"]} vs {li("crack_free_px"):.0f}')
    else:
        P(f'  E1 matched volume: not computed ({la} pred/GT not monotone on the grid, or the target is outside its range)')
    # singles vs ensemble
    if rjson:
        Rj = json.load(open(rjson)); P('  singles (R, s10-14 means ± sd, argmax) vs ensemble (b 0), descriptive:')
        for k, key, arm in ((la, 'A', 'SUPPF'), (lb, 'B', 'SKR01')):
            c = J[(k, 0.0)]; t_ = mm(c['test'], sorted(c['test'])); tcn = mm(c['test'], sorted(s for s in c['test'] if s != NOISY)); e_ = mm(c['ext'], ext)
            f = lambda v: f'{np.mean(v):.4f} ± {np.std(v, ddof=1):.4f}'
            P(f'    {k}: test crack IoU {t_[0]:.4f} vs {f(Rj["test"]["crack"][key + "_all"])} | test relF1@2 {t_[1]:.4f} vs {f(Rj["test"]["relF1"][key + "_all"])} | test inactive {t_[2]:.4f} vs {f(Rj["test"]["inact"][key + "_all"])} '
              f'| clean crack IoU {tcn[0]:.4f} vs {f(Rj["test"]["crack"][key + "_clean"])} | E1 relF1@2 {e_[1]:.4f} vs {f(Rj["e1"]["relF1"][key])} | E1 any-hit {e_[3]:.4f} vs {f(Rj["e1"]["anyhit"][key])} '
              f'| E1 inactive {e_[2]:.4f} vs {Rj["e1_rep"]["inact"][0 if key == "A" else 1]:.4f}')
        P('    FINAL (cv02, R34 5-seed ensemble, b +0.75) clean-test crack IoU 0.492: descriptive only (other machine and commits).')
    return out


def d_fragility(A, B, res):
    P('\n## D fragility: leave-one-out with the seed-0 CI recomputed (test: leave-one-image-out, both sets; E1: leave-one-cluster-out, 71)')
    out = {}
    test = sorted(A['test']); TR = {}
    for s0 in test:
        TR[s0] = {sn: d_boot(A, B, 'test', kp, False, np.random.default_rng(0))[:3] for sn, kp in (('all', lambda s, s0=s0: s != s0), ('clean', lambda s, s0=s0: s != s0 and s != NOISY))}
    for i, nm in ((0, 'crack IoU'), (1, 'relF1@2'), (2, 'inactive IoU')):
        st = {'pass': 0, 'fail': 0, 'nd': 0}; chg = []
        full_pass = f'test {nm}' in res['carriers']; full_fail = f'test {nm}' in res['primary_fails']
        for s0 in test:
            rows = {sn: (TR[s0][sn][0][i], TR[s0][sn][1][i], TR[s0][sn][2][i]) for sn in ('all', 'clean')}
            fail = any(r[2] < 0 for r in rows.values()); pas = (not fail) and (all(r[1] > 0 for r in rows.values()) or (any(r[1] > 0 for r in rows.values()) and all(r[0] > 0 for r in rows.values())))
            st['fail' if fail else 'pass' if pas else 'nd'] += 1
            if pas != full_pass or fail != full_fail:
                chg.append(f'{s0} (all {rows["all"][0]:+.4f} [{rows["all"][1]:+.4f}, {rows["all"][2]:+.4f}])')
        out[f'test {nm}'] = {'counts': st, 'changes': chg}
        P(f'  test {nm:13s}: full {"pass" if full_pass else "fail" if full_fail else "n.d."} | 50 image drops: pass {st["pass"]}, n.d. {st["nd"]}, fail {st["fail"]}' + (f' | changes when dropping: {"; ".join(chg)}' if chg else ''))
    ext = sorted(A['ext']); cl = sorted({ce.key(s) for s in ext})
    ER = {c: d_boot(A, B, 'ext', lambda s, c=c: ce.key(s) != c, True, np.random.default_rng(0))[:3] for c in cl}
    for i, nm in ((1, 'E1 crack relF1@2'), (3, 'E1 any-hit'), (2, 'E1 inactive IoU (G1e)')):
        st = {'pass': 0, 'fail': 0, 'nd': 0}; chg = []; los = []
        full_state = 'pass' if res['e1'][DN[i]]['lo'] > 0 else 'fail' if res['e1'][DN[i]]['hi'] < 0 else 'nd'
        for c in cl:
            f_, lo, hi = ER[c]; state = 'pass' if lo[i] > 0 else 'fail' if hi[i] < 0 else 'nd'
            st[state] += 1; los.append((float(f_[i]), float(lo[i]), float(hi[i])))
            if state != full_state:
                chg.append(f'{c} ({f_[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}])')
        out[nm] = {'counts': st, 'changes': chg, 'est_range': (min(x[0] for x in los), max(x[0] for x in los)), 'lo_range': (min(x[1] for x in los), max(x[1] for x in los)), 'hi_range': (min(x[2] for x in los), max(x[2] for x in los))}
        P(f'  {nm:22s}: full {"CI above 0" if full_state == "pass" else "CI below 0" if full_state == "fail" else "CI spans 0"} | 71 cluster drops: above 0 {st["pass"]}, spans 0 {st["nd"]}, below 0 {st["fail"]} | '
          f'estimate range [{min(x[0] for x in los):+.4f}, {max(x[0] for x in los):+.4f}], lower bound range [{min(x[1] for x in los):+.4f}, {max(x[1] for x in los):+.4f}], upper [{min(x[2] for x in los):+.4f}, {max(x[2] for x in los):+.4f}]'
          + (f' | changes when dropping: {"; ".join(chg)}' if chg else ''))
    # guards under leave-one-out (point estimates)
    g2a = []; g1t = []
    for s0 in test:
        st1 = [s for s in test if s != s0]; d = ce.metr(*(x.sum(0) for x in ce.feats(B['test'], st1))) - ce.metr(*(x.sum(0) for x in ce.feats(A['test'], st1)))
        st2 = [s for s in st1 if s != NOISY]; d2 = ce.metr(*(x.sum(0) for x in ce.feats(B['test'], st2))) - ce.metr(*(x.sum(0) for x in ce.feats(A['test'], st2)))
        g2a.append(float(d[4])); g1t.append((float(d[2]), float(d2[2]), s0))
    g2b = []
    for c in cl:
        pa = sum(int(np.asarray(v['conf'], np.int64).reshape(NC, NC)[:, CR].sum()) for s, v in A['ext'].items() if ce.key(s) != c and np.asarray(v['conf'], np.int64).reshape(NC, NC)[CR].sum() == 0)
        pb = sum(int(np.asarray(v['conf'], np.int64).reshape(NC, NC)[:, CR].sum()) for s, v in B['ext'].items() if ce.key(s) != c and np.asarray(v['conf'], np.int64).reshape(NC, NC)[CR].sum() == 0)
        g2b.append(pb / max(pa, 1))
    out['guards'] = {'G2a': (min(g2a), max(g2a)), 'G2b': (min(g2b), max(g2b)), 'G1t_all': (min(x[0] for x in g1t), max(x[0] for x in g1t)), 'G1t_clean': (min(x[1] for x in g1t), max(x[1] for x in g1t)),
                     'G1t_trips': [x[2] for x in g1t if x[0] <= -0.015 and x[1] <= -0.015], 'G1t_n_trip': sum(x[0] <= -0.015 and x[1] <= -0.015 for x in g1t)}
    P(f'  guards, point estimates under leave-one-out: G2a relP@2 d [{min(g2a):+.4f}, {max(g2a):+.4f}] (trips {sum(x < -0.03 for x in g2a)} of 50) | G2b ratio [x{min(g2b):.3f}, x{max(g2b):.3f}] (trips {sum(x > 1.5 for x in g2b)} of 71) | '
      f'G1t inactive d all [{min(x[0] for x in g1t):+.4f}, {max(x[0] for x in g1t):+.4f}], clean [{min(x[1] for x in g1t):+.4f}, {max(x[1] for x in g1t):+.4f}] (trips {out["guards"]["G1t_n_trip"]} of 50'
      + (': ' + ', '.join(out['guards']['G1t_trips']) if out['guards']['G1t_trips'] else '') + ')')
    return out


def run_D(out_json, rjson=None):
    raw = RES / 's2c/raw_d'; la, lb = 'E-SUPPF', 'E-SKR2'
    dec = json.load(open(raw / 's2c_d_val_decisions.json')); sw = json.load(open(raw / 's2c_d_e1_sweep.json')); bmv = dec['b_mv']['b_mv']
    assert dec['written_b'] == {la: [0.0], lb: sorted({0.0, bmv})}, dec['written_b']
    Jf = {(k, b): json.load(open(raw / f'{k}.b{b:g}.json')) for k in (la, lb) for b in dec['written_b'][k]}
    for (k, b), j in Jf.items():
        arm = 'SUPPF' if k == la else 'SKR01'
        assert j['step'] == 20000 and j['bias'] == b and [re.search(r's2c_\w+_100pct_s\d+', x).group(0) for x in j['members']] == [f's2c_{arm}_100pct_s{q}' for q in range(10, 15)], (k, b)
        assert {sp: len(v) for sp, v in j['cells'].items()} == {'val': 54, 'test': 50, 'test_noscuff': 50, 'ext': 106}
    J = {kb: j['cells'] for kb, j in Jf.items()}
    P("# coach recompute, verdict D of protocol_SKR2C (E1 opening #7; same 50 test and 106 E1 cells as #5 / #6, 3rd look); 5-member ensembles E-SUPPF' / E-SKR2' (s10-14), both at b 0")
    P(f'# inputs: {raw}/E-SUPPF.b0.json, E-SKR2.b0.json, E-SKR2.b{bmv:g}.json, s2c_d_val_decisions.json, s2c_d_e1_sweep.json')
    P('## D.1 verdict pair: both ensembles at b 0 (CIs: 2,000 resamples, fresh default_rng(0) per bootstrap = the registered seed-0 draws; "stream 2" = default_rng(12345))')
    res = d_pair(J[(la, 0.0)], J[(lb, 0.0)], la, lb, "E-SKR2' - E-SUPPF', b 0 / b 0")
    P('## D.2 fixed wording (protocol 3b)')
    for l in d_wording(res):
        P('  ' + l)
    P(f'  named claim condition 2 (D\'s E1 relF1@2 primary passes): {res["e1_relF1_primary_passes"]}')
    rep = d_reported(J, dec, sw, la, lb, bmv, rjson)
    fr = d_fragility(J[(la, 0.0)], J[(lb, 0.0)], res)
    res.update({'reported': rep, 'fragility': fr, 'b_mv': bmv, 'wording': d_wording(res)})
    json.dump(res, open(out_json, 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))


# ---------------------------------------------------------------- combination (3a named claim, 3c, 7)
def combine(rj, dj):
    R = json.load(open(rj)); D = json.load(open(dj))
    P('# coach: named-claim tier (3a), combination (3c) and the handbook line (7), from my own R and D outputs')
    c1, c2, c3 = bool(R['cond1']), bool(D['e1_relF1_primary_passes']), (R['verdict'] != 'FAIL' and D['verdict'] != 'FAIL')
    P(f'verdict R: {R["verdict"]} (BETTER: {R["better"] or "none"}; WORSE: {R["worse"] or "none"}; guards: {R["trips"] or "none"})')
    P(f'verdict D: {D["verdict"]} (passing: {D["carriers"] or "none"}; failing: {D["primary_fails"] or "none"}; guards: {D["trips"] or "none"})')
    P(f'named claim (3a): condition 1 seed-aware CI above 0: {c1} ([{R["cond1_ci"][1]:+.4f}, {R["cond1_ci"][2]:+.4f}]); condition 2 D E1 relF1@2 primary passes: {c2} '
      f'([{D["e1"]["relF1@2"]["lo"]:+.4f}, {D["e1"]["relF1@2"]["hi"]:+.4f}]); condition 3 neither R nor D is FAIL: {c3}')
    rl = LAB[R['labels']['E1 crack relF1@2']]
    if c1 and c2 and c3:
        tier = "\"SKR2's E1 crack relF1@2 gain REPLICATED on fresh seeds (seed-aware; same 106 E1 cells, 3rd look)\" HOLDS"
    elif c2 and not c1:
        tier = '"the fresh-seed ensemble pair differs on E1 relF1@2 (fixed-model CI; seed noise not included); replication at recipe level not shown"'
    else:
        tier = ('REPLICATED does not hold (' + ', '.join(f'condition {i} {"holds" if c else "fails"}' for i, c in ((1, c1), (2, c2), (3, c3)))
                + '). The protocol fixes wording only for "all three hold" and for "only D\'s ensemble CI passes"; this case has no fixed line: replication not shown.')
    P(f'  tier: {tier}')
    P(f"  R's rule-1 label for E1 relF1@2 (reported next to it): {rl} ({R['e1']['relF1']['d']:+.4f}, thr {R['e1']['relF1']['thr']:.4f})")
    vol = {'test crack IoU', 'test crack relF1@2', 'test relF1@2', 'E1 any-hit'}
    if R['verdict'] == 'PASS' and D['verdict'] == 'PASS':
        both_vol = set(R['better']) <= vol and set(D['carriers']) <= vol
        P("3c: R PASS and D PASS -> E-SKR2' at b 0 is recommended as the deployable candidate over E-SUPPF' (section 7)." + (' Both PASSes rest only on volume-sensitive carriers: the sentence carries the '
          'volume wording (3b) and the b_mv matched-val-volume result (4).' if both_vol else ''))
    elif R['verdict'] == 'FAIL' or D['verdict'] == 'FAIL':
        why = []
        if R['verdict'] == 'FAIL':
            why.append('R: ' + ', '.join(R['worse'] + R['trips']))
        if D['verdict'] == 'FAIL':
            why.append('D: ' + ', '.join(D['primary_fails'] + D['trips']))
        inact_only = (R['verdict'] != 'FAIL' or (not R['worse'] and R['trips'] == ['G1'])) and (D['verdict'] != 'FAIL' or (not D['primary_fails'] and all(t.startswith(('G1t', 'G1e')) for t in D['trips'])))
        P("3c: R FAIL or D FAIL -> the SUP100-PF ensemble stays (#6's E-PF at b 0). Caused by: " + '; '.join(why) + '.' + (" An inactive guard alone caused it: null false-FAIL R's G1 ~9-15% (S2 W1), D's G1t ~8%; "
          'combined, ~15% that a true null keeps SUP100-PF through an inactive guard alone (judge L2).' if inact_only else ''))
    else:
        P('3c: otherwise -> reported as is (each verdict with its carriers); the SUP100-PF ensemble stays. Coach does not recommend a switch; the user decides.')
    P(f'      R {R["verdict"]}' + (f' carried by {R["better"]}' if R['better'] else '') + f'; D {D["verdict"]}' + (f' carried by {D["carriers"]}' if D['carriers'] else ''))
    return {'c1': c1, 'c2': c2, 'c3': c3}


# ---------------------------------------------------------------- self-test on opened files (#5 singles s5-9, #6 ensembles)
def selftest():
    ok = True
    def chk(name, got, exp, tol=5e-5):
        nonlocal ok
        p = (abs(got - exp) <= tol) if isinstance(exp, float) else (got == exp); ok &= bool(p)
        print(f'  {name}: {got if not isinstance(got, float) else format(got, "+.4f")} vs {exp if not isinstance(exp, float) else format(exp, "+.4f")} -> {"ok" if p else "MISMATCH"}')
    PF, S2 = RES / 'pf2/raw/m0', RES / 's2/raw/m0/SKR01'
    rA = [f'pf2_SUPPF_100pct_s{k}' for k in range(5, 10)]; rB = [f'skr2_SKR01_100pct_s{k}' for k in range(5, 10)]
    MA = [ct.load_m0(f'{PF}/{r}.json', 'e544133') for r in rA]; MB = [ct.load_m0(f'{S2}/{r}.json', 'c9bbb02') for r in rB]
    print('## selftest R on the opened #5 files (SUPPF s5-9, SKR01 s5-9); expected = verify_skr2_hc2.md / results/s2/coach_v')
    R = R_core(MA, MB, str(RES / 's2/raw/b5/SUPPF/rec_w'), rA, str(RES / 's2/raw/b5/SKR01/rec_w'), rB, 'selftest #5', quiet=True)
    for k, e in (('crack', (0.0091, 0.0100, 0.0088, 0.0100)), ('relF1', (0.0089, 0.0100, 0.0085, 0.0100)), ('inact', (0.0099, 0.0272, 0.0102, 0.0285))):
        t = R['test'][k]; chk(f'test {k} d all', float(t['d_all']), e[0]); chk(f'test {k} thr all', float(t['thr_all']), e[1]); chk(f'test {k} d clean', float(t['d_clean']), e[2]); chk(f'test {k} thr clean', float(t['thr_clean']), e[3])
        chk(f'test {k} two-set', t['two'], 'nd')
    for k, e in (('compR', (0.0169, 0.0290, 0.0171, 0.0293)), ('relR', (0.0094, 0.0177, 0.0094, 0.0177))):
        t = R['b5'][k]; chk(f'B5 {k} d all', float(t['d_all']), e[0]); chk(f'B5 {k} thr all', float(t['thr_all']), e[1]); chk(f'B5 {k} d clean', float(t['d_clean']), e[2]); chk(f'B5 {k} thr clean', float(t['thr_clean']), e[3])
    chk('B5 OPs SUPPF b_comp / b_rel, SKR01 b_comp / b_rel', tuple(round(R['b5']['op'][a_][k_], 1) for a_ in ('SUPPF', 'SKR01') for k_ in ('b_comp', 'b_rel')), (3.9, 3.9, 4.8, 2.7))
    chk('E1 relF1 d', float(R['e1']['relF1']['d']), 0.0364); chk('E1 relF1 thr', float(R['e1']['relF1']['thr']), 0.0351); chk('E1 relF1 label', R['e1']['relF1']['lab'], 'BETTER')
    chk('E1 any-hit d', float(R['e1']['anyhit']['d']), 0.0439); chk('E1 any-hit thr', float(R['e1']['anyhit']['thr']), 0.0521); chk('E1 any-hit label', R['e1']['anyhit']['lab'], 'nd')
    chk('G1 d all', R['guards']['G1']['d_all'], 0.0099); chk('G1 d clean', R['guards']['G1']['d_clean'], 0.0102); chk('G2 relP d', R['guards']['G2']['d_relP'], -0.0121)
    chk('G2 crack-free px SKR01 / SUPPF', (round(R['guards']['G2']['free_arm']), round(R['guards']['G2']['free_base'])), (3819, 3931)); chk('G2 ratio', R['guards']['G2']['ratio'], 0.97, 5e-3)
    chk('verdict R on #5', (R['verdict'], R['better'], R['worse'], R['trips']), ('PASS', ['E1 crack relF1@2'], [], []))
    X, inv, ncl, stems, cl = sb_load(MA, MB, 'ext', lambda s: True)
    r = sb_boot(X, inv, ncl, 'A', 'B', ['relF1', 'anyhit'], seed=20261102)
    chk('seed-aware boot E1 relF1 lo (RNG 20261102; boot.txt)', float(r['relF1'][1]), 0.0038); chk('seed-aware boot E1 relF1 hi', float(r['relF1'][2]), 0.0756)
    chk('seed-aware boot E1 any-hit lo', float(r['anyhit'][1]), -0.0057); chk('seed-aware boot E1 any-hit hi', float(r['anyhit'][2]), 0.1029)
    r2 = sb_boot_n(X['A'], X['B'], inv, ncl, ['relF1'], NB, 20261102)['relF1']; chk('sb_boot_n == sb_boot (5 v 5, same draws)', (round(r2[1], 12), round(r2[2], 12)), (round(float(r['relF1'][1]), 12), round(float(r['relF1'][2]), 12)))
    Xt, invt, nclt, _, _ = sb_load(MA, MB, 'test', lambda s: True); rt = sb_boot(Xt, invt, nclt, 'A', 'B', ['crack', 'relF1', 'inact'], seed=20261102)
    chk('test clusters', nclt, 48); chk('seed-aware boot test crack lo', float(rt['crack'][1]), 0.0006); chk('seed-aware boot test crack hi', float(rt['crack'][2]), 0.0194)
    chk('seed-aware boot test inact lo', float(rt['inact'][1]), -0.0168); chk('seed-aware boot test inact hi', float(rt['inact'][2]), 0.0410)
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        lo = loso_R(MA, MB, str(RES / 's2/raw/b5/SUPPF/rec_w'), rA, str(RES / 's2/raw/b5/SKR01/rec_w'), rB, R); lc = loco_R(MA, MB, R)
    chk('leave-one-seed-out E1 relF1 BETTER count (verify_skr2_hc2: 5 of 10)', lo['E1 crack relF1@2']['labels'].count('BETTER'), 5)
    chk('leave-one-image-out E1 relF1 BETTER count (judge: 65 of 71)', lc['E1 crack relF1@2']['labels'].count('BETTER'), 65)
    print('## selftest D on the opened #6 files (E-PF b 0 vs E-SKR2 b 0); expected = runner seed-0 CIs in verify_skr2e.md')
    D6 = RES / 'skr2e/raw'; A = json.load(open(D6 / 'E-PF.b0.json'))['cells']; B = json.load(open(D6 / 'E-SKR2.b0.json'))['cells']
    d = d_pair(A, B, 'E-PF', 'E-SKR2', 'selftest #6 b 0 pair', quiet=True)
    for sn, e in (('all 50', {'crack IoU': (0.0102, 0.0031, 0.0197), 'relF1@2': (0.0104, 0.0016, 0.0232), 'inactive IoU': (0.0050, -0.0090, 0.0280)}),
                  ('clean 49', {'crack IoU': (0.0101, 0.0031, 0.0188), 'relF1@2': (0.0103, 0.0017, 0.0231), 'inactive IoU': (0.0055, -0.0104, 0.0317)})):
        for k, v in e.items():
            t = d['test'][sn][k]; chk(f'#6 test {sn} {k} d', t['d'], v[0]); chk(f'#6 test {sn} {k} lo (seed 0)', t['lo'], v[1]); chk(f'#6 test {sn} {k} hi (seed 0)', t['hi'], v[2])
    for k, v in {'relF1@2': (0.0353, 0.0102, 0.0613), 'any-hit': (0.0676, 0.0253, 0.1282), 'inactive IoU': (-0.0418, -0.0545, 0.0123)}.items():
        t = d['e1'][k]; chk(f'#6 E1 {k} d', t['d'], v[0]); chk(f'#6 E1 {k} lo (seed 0)', t['lo'], v[1]); chk(f'#6 E1 {k} hi (seed 0)', t['hi'], v[2])
    for k, v in {('all 50', 'crack IoU'): (0.0031, 0.0193), ('clean 49', 'crack IoU'): (0.0029, 0.0192), ('all 50', 'relF1@2'): (0.0017, 0.0241)}.items():
        t = d['test'][k[0]][k[1]]; chk(f'#6 test {k[0]} {k[1]} stream-2 CI (= my #6 coach CI)', (round(t['lo2'], 4), round(t['hi2'], 4)), v)
    chk('#6 E1 any-hit counts', d['e1']['anyhit_counts'], (102, 122, 296)); chk('#6 G2a relP d', d['guards']['G2a test relP@2 d < -0.03']['detail'], -0.0110)
    chk('#6 crack-free px E-PF / E-SKR2', d['cfree'], (2528, 2673)); chk('#6 G1t', tuple(round(x, 4) for x in d['guards']['G1t test inactive d <= -0.015 in both sets']['detail']), (0.0050, 0.0055))
    chk('#6 verdict at the b 0 pair alone (no headline pair here)', (d['verdict'], d['carriers'], d['trips']), ('PASS', ['test crack IoU', 'test relF1@2', 'E1 crack relF1@2', 'E1 any-hit'], []))
    w = d_wording({'verdict': 'PASS', 'carriers': ['test crack IoU'], 'primary_fails': [], 'trips': []}); chk('wording: test-only PASS has 3 lines (carriers, volume, not replicated)', len(w), 3)
    w = d_wording({'verdict': 'FAIL', 'carriers': [], 'primary_fails': [], 'trips': ['G1t test inactive d <= -0.015 in both sets']}); chk('wording: G1t-only FAIL has 2 lines (cause, ~15%)', len(w), 2)
    chk('assemble_R: WORSE beats BETTER', assemble_R({'a': 'BETTER', 'b': 'WORSE'}, {'G1': False})[0], 'FAIL'); chk('assemble_R: guard trip fails a BETTER', assemble_R({'a': 'BETTER'}, {'G1': True})[0], 'FAIL')
    chk('assemble_R: none BETTER -> n.d.', assemble_R({'a': 'nd'}, {'G1': False, 'G2': False})[0], 'n.d.'); chk('assemble_R: one BETTER -> PASS', assemble_R({'a': 'BETTER', 'b': 'nd'}, {'G1': False, 'G2': False})[0], 'PASS')
    chk('two-set rule: BETTER + same-sign n.d. -> BETTER', ct.twoset((0.02, 0.01, 'BETTER'), (0.009, 0.01, 'nd')), 'BETTER'); chk('two-set rule: BETTER + opposite-sign n.d. -> n.d.', ct.twoset((0.02, 0.01, 'BETTER'), (-0.001, 0.01, 'nd')), 'nd')
    chk('two-set rule: WORSE in one set -> WORSE', ct.twoset((0.02, 0.01, 'BETTER'), (-0.02, 0.01, 'WORSE')), 'WORSE')
    print('SELFTEST', 'PASS' if ok else 'FAIL'); return ok


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'selftest':
        sys.exit(0 if selftest() else 1)
    elif mode == 'R':
        run_R(sys.argv[2])
    elif mode == 'D':
        run_D(sys.argv[2], sys.argv[sys.argv.index('--rjson') + 1] if '--rjson' in sys.argv else None)
    elif mode == 'combine':
        combine(sys.argv[2], sys.argv[3])
