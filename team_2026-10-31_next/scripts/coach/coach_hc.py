"""coach (1 Nov, respawned session): independent recompute of protocol_HC v1.1's opening (E1 opening #3). Own code, not hc_e1_coprim /
hc_shv1_read / hc_f51 / el_metrics' readout. Test primaries (two sets, tau 0 / 1) are done by coach_verify.py b0456b28 (coach's own).
  A. E1 co-primaries: crack relF1@2 and inactive IoU, all 106 ext cells pooled per run from the argmax m0 JSONs (coach_thin.e1_agg:
     relF1 from summed crack_rel2, inactive IoU from the summed confusion), rule 1 (/3) HC s5-9 vs SUPPF s5-9 (PF2's opening m0, reused);
     strata and width-robust keys reported.
  B. SHV1 mechanism from the el_metrics records (rec/<run>.{val,synval}.json; per grid b counts): per arm the per-cell counts of the 5
     seeds are summed; relP@2(b) = relp_tp / pred, relR@2(b) = relr_tp / n_gt; matched relR@2 = max relR over the full record grid
     (-4.0..12.0 step 0.1 + 0.75) with relP >= 0.90; oracle b = argmax relF1@2 over -4.0..12.0 step 0.1 (ties smaller b). Sets V0 (val
     54), SHV1 (108), SHV1-p (80, stem list). Mechanism: HC - SUPPF matched SHV1 relR@2 < +0.05 -> FAILED.
  C. F51 harm guard from the rf dumps (pc): 1,000-bin crack AP per run (as coach_a8 2da944cd), arm means, paired bootstrap over F51's
     36 modules (2,000, own RNG seed 20261101); FAIL iff the 97.5th percentile of HC - SUPPF < 0. Reported: per-run b_rel (val records)
     and crack px on crack-free H36 / F51 cells at b_rel.
Usage: python -I coach_hc.py selftest CAL_REC_DIR CAL_REC_SHV1_DIR
       python -I coach_hc.py run HC_POST PF2_POST REC_DIR DUMP_DIR RF_DIR RF_SETS E1CTX SHV1P_LIST"""
import json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coach_thin as ct  # rule1, e1_agg, load_m0 (coach's own, 7562d97f)

SEEDS = [5, 6, 7, 8, 9]
HC = [f'hc_HC_100pct_s{k}' for k in SEEDS]; SP = [f'pf2_SUPPF_100pct_s{k}' for k in SEEDS]
GRID = ct.GRID; OPJ = ct.OPJ; CR, NB = 14, 1000


def recs(path):
    d = json.load(open(path)); assert d['grid'] == list(GRID), path
    return d['cells']


def pooled(cell_dicts, keep=None):
    cs = [c for cells in cell_dicts for s, c in cells.items() if keep is None or s in keep]
    S = lambda k: np.sum([np.asarray(c[k], np.int64) for c in cs], 0)
    pred, rp, rr, tp = S('pred'), S('relp_tp'), S('relr_tp'), S('tp'); ng = sum(c['n_gt'] for c in cs)
    P = np.where(pred > 0, rp / np.maximum(pred, 1), np.nan); R = rr / max(ng, 1)
    F = np.where((P + R) > 0, 2 * P * R / np.maximum(P + R, 1e-12), 0.0)
    ok = np.where(np.nan_to_num(P, nan=-1) >= 0.90)[0]
    matched = float(R[ok].max()) if len(ok) else float('nan')
    jo = int(OPJ[np.argmax(np.nan_to_num(F[OPJ], nan=-1))])
    j0 = int(np.where(np.isclose(GRID, 0.0))[0][0])
    return {'matched': matched, 'oracle_b': float(GRID[jo]), 'relR0': float(R[j0]), 'relP0': float(P[j0]), 'pixR0': float(tp[j0] / max(ng, 1)),
            'n_cells': len(cs), 'n_gt': int(ng)}


def selftest(cal, cals):
    fin = pooled([recs(f'{cal}/FINAL.val.json')]); fis = pooled([recs(f'{cals}/FINAL.synval.json')])
    sv = pooled([recs(f'{cal}/SUPPF5_m{i}.val.json') for i in range(5)]); ss = pooled([recs(f'{cals}/SUPPF5_m{i}.synval.json') for i in range(5)])
    print(f'FINAL V0 oracle b {fin["oracle_b"]:+.1f} matched {fin["matched"]:.3f} | SHV1 oracle b {fis["oracle_b"]:+.1f} matched {fis["matched"]:.3f}')
    print(f'SUPPF s0-4 pooled V0 oracle b {sv["oracle_b"]:+.1f} matched {sv["matched"]:.3f} | SHV1 oracle b {ss["oracle_b"]:+.1f} matched {ss["matched"]:.3f}')
    exp = [(fin['oracle_b'], 1.1), (fis['oracle_b'], 1.5), (sv['oracle_b'], 2.9), (ss['oracle_b'], 3.8)]
    expm = [(fin['matched'], 0.892), (fis['matched'], 0.730), (sv['matched'], 0.876), (ss['matched'], 0.694)]
    ok = all(abs(a - b) < 1e-6 for a, b in exp) and all(abs(a - b) < 0.0005 for a, b in expm)
    print('SELFTEST', 'PASS (routing pre-check values reproduced)' if ok else 'FAIL')
    return ok


def hist(pc, gt, keep):
    bins = np.clip((pc.astype(np.float64) * NB).astype(np.int64), 0, NB - 1)
    pos = (gt == CR) & keep; neg = keep & ~pos
    return np.bincount(bins[pos], minlength=NB), np.bincount(bins[neg], minlength=NB)


def ap_of(pos, neg):
    tp = np.cumsum(pos[::-1]).astype(float); fp = np.cumsum(neg[::-1]).astype(float); tot = pos.sum()
    if tot == 0:
        return float('nan')
    prec = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) > 0)
    return float(np.sum(prec * np.diff(np.concatenate([[0.0], tp / tot]))))


def run(post, pf2, recd, dumpd, rfd, rfs, ctxf, shv1p):
    from PIL import Image
    # ---------- A. E1 ----------
    ctx = {}
    for l in open(ctxf):
        f = l.rstrip('\n').split('\t')
        if len(f) >= 4:
            ctx[f[0]] = (f[2] == 'scuff=1', f[3] == 'halfcut=1')
    m0 = {'SUPPF': [ct.load_m0(f'{pf2}/m0/{r}.json', 'e544133') for r in SP], 'HC': [ct.load_m0(f'{post}/m0/{r}.json', 'c2e6973') for r in HC]}
    stems = sorted(m0['SUPPF'][0]['cells']['ext'])
    assert all(sorted(d['cells']['ext']) == stems for v in m0.values() for d in v) and set(stems) == set(ctx) and len(stems) == 106
    groups = [('E1 all 106', lambda s: True), ('scuff+halfcut 29', lambda s: ctx[s][0] and ctx[s][1]),
              ('halfcut no scuff 29', lambda s: ctx[s][1] and not ctx[s][0]), ('full 48', lambda s: not ctx[s][1]),
              ('half-cut 58', lambda s: ctx[s][1]), ('other 77', lambda s: not (ctx[s][0] and ctx[s][1]))]
    KEYS = ['relF1', 'inact', 'relR', 'relP', 'cR', 'cP', 'crack', 'compR', 'compP']
    out = {}
    for gname, keep in groups:
        n = sum(keep(s) for s in stems)
        print(f'## {gname} (n {n})' + ('' if gname == 'E1 all 106' else ' [reported]'))
        vals = {a: [ct.e1_agg(d['cells']['ext'], keep) for d in m0[a]] for a in m0}
        for a in m0:
            print(f'  {a:5s} ' + ' | '.join(f'{k} {np.mean([m[k] for m in vals[a]]):.4f}±{np.std([m[k] for m in vals[a]], ddof=1):.4f}' for k in KEYS))
        print('  HC-SUPPF ' + ' | '.join('%s %+.4f(%.4f) %s' % ((k,) + ct.rule1([m[k] for m in vals['SUPPF']], [m[k] for m in vals['HC']])) for k in KEYS))
        if gname == 'E1 all 106':
            out['E1'] = vals
    print('## E1 CO-PRIMARIES (all 106, argmax, rule 1 /3, HC - SUPPF, one set)')
    e1v = {}
    for k in ('relF1', 'inact'):
        for a in ('SUPPF', 'HC'):
            print(f'  {k} {a:5s} per seed ' + ' '.join(f'{m[k]:.4f}' for m in out['E1'][a]))
        e1v[k] = ct.rule1([m[k] for m in out['E1']['SUPPF']], [m[k] for m in out['E1']['HC']])
        print(f'  -> E1 {k}: {e1v[k][0]:+.4f} (thr {e1v[k][1]:.4f}) {e1v[k][2]}')
    # crack-free E1 px (reported): crack predicted on the 74 crack-free cells (GT row 14 sum 0)
    for a in ('SUPPF', 'HC'):
        cf = []
        for d in m0[a]:
            t = 0
            for s, c in d['cells']['ext'].items():
                C = np.asarray(c['conf'], float).reshape(24, 24)
                if C[CR].sum() == 0:
                    t += C[:, CR].sum()
            cf.append(t)
        print(f'  [reported] E1 crack px on crack-free cells {a}: mean {np.mean(cf):.0f} per seed ' + ' '.join(f'{x:.0f}' for x in cf))
    # ---------- B. SHV1 ----------
    sp = set(l.strip() for l in open(shv1p) if l.strip()); assert len(sp) == 80
    print('## SHV1 MECHANISM (records, 5 seeds pooled per arm; matched = max relR@2 at relP@2 >= 0.90 over the full grid)')
    M = {}
    for a, runs in (('SUPPF', SP), ('HC', HC)):
        V0 = [recs(f'{recd}/{r}.val.json') for r in runs]; SY = [recs(f'{recd}/{r}.synval.json') for r in runs]
        assert all(len(c) == 54 for c in V0) and all(len(c) == 108 for c in SY) and sp <= set(SY[0])
        M[a] = {'V0': pooled(V0), 'SHV1': pooled(SY), 'SHV1p': pooled(SY, sp)}
        for st in ('V0', 'SHV1', 'SHV1p'):
            print(f'  {a:5s} {st:5s} ' + json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in M[a][st].items()}))
        print(f'  {a:5s} oracle-b gap SHV1 - V0 {M[a]["SHV1"]["oracle_b"] - M[a]["V0"]["oracle_b"]:+.1f}; per seed matched SHV1 '
              + ' '.join(f'{pooled([c])["matched"]:.3f}' for c in SY))
    g = M['HC']['SHV1']['matched'] - M['SUPPF']['SHV1']['matched']
    print(f'  -> mechanism: HC - SUPPF matched SHV1 relR@2 {g:+.4f} (kill if < +0.05): {"PASSED" if g >= 0.05 else "FAILED"}')
    print(f'  [reported] SHV1-p {M["HC"]["SHV1p"]["matched"] - M["SUPPF"]["SHV1p"]["matched"]:+.4f}; V0 {M["HC"]["V0"]["matched"] - M["SUPPF"]["V0"]["matched"]:+.4f}; '
          f'SHV1 relR@2 at b 0 {M["HC"]["SHV1"]["relR0"] - M["SUPPF"]["SHV1"]["relR0"]:+.4f}')
    # ---------- C. F51 ----------
    rows = [l.rstrip('\n').split('\t') for l in open(rfs) if l.strip()][1:]
    rfset = {r[0]: r[1] for r in rows}; module = {r[0]: r[3] for r in rows}
    H, FA, BR = {}, {}, {}
    for r in SP + HC:
        z = np.load(f'{dumpd}/{r}.rf.npz'); st = [str(s) for s in z['stems']]; H[r] = {}
        for i, s in enumerate(st):
            gt = np.array(Image.open(f'{rfd}/masks/{s}.png')); keep = ~(np.array(Image.open(f'{rfd}/ignore/{s}.png')) > 0)
            H[r][s] = hist(z['pc'][i], gt, keep)
        vr = recs(f'{recd}/{r}.val.json'); cs = list(vr.values())
        Sx = lambda k: np.sum([np.asarray(c[k], np.int64) for c in cs], 0)
        pred, rp, rr = Sx('pred'), Sx('relp_tp'), Sx('relr_tp'); ng = sum(c['n_gt'] for c in cs)
        relP = np.where(pred > 0, rp / np.maximum(pred, 1), -1.0)[OPJ]; relR = (rr / max(ng, 1))[OPJ]
        ok = np.where(relP >= 0.90)[0]; j = int(OPJ[ok[np.argmax(relR[ok])]]) if len(ok) else int(OPJ[np.argmax(relP)])
        BR[r] = (float(GRID[j]), bool(len(ok)))
        rf = recs(f'{recd}/{r}.rf.json')
        FA[r] = {gs: float(sum(rf[s]['pred'][j] for s in rf if rfset[s] == gs and rf[s]['n_gt'] == 0)) for gs in ('H36', 'F51')}
    f51 = sorted(s for s in H[SP[0]] if rfset[s] == 'F51'); mods = sorted({module[s] for s in f51}); by = {m: [s for s in f51 if module[s] == m] for m in mods}
    assert len(f51) == 51 and len(mods) == 36
    ap = lambda r, st: ap_of(np.sum([H[r][s][0] for s in st], 0), np.sum([H[r][s][1] for s in st], 0))
    print('## F51 HARM GUARD (1,000-bin crack AP; FAIL iff 97.5th pct of HC - SUPPF < 0)')
    for a, runs in (('SUPPF', SP), ('HC', HC)):
        print(f'  {a:5s} F51 AP per seed ' + ' '.join(f'{ap(r, f51):.4f}' for r in runs) + f' mean {np.mean([ap(r, f51) for r in runs]):.4f}'
              + ' | b_rel ' + ' '.join(f'{BR[r][0]:+.1f}{"" if BR[r][1] else "*"}' for r in runs)
              + f' | FA@b_rel H36 {np.mean([FA[r]["H36"] for r in runs]):.0f} F51 {np.mean([FA[r]["F51"] for r in runs]):.0f}')
    d = np.mean([ap(r, f51) for r in HC]) - np.mean([ap(r, f51) for r in SP])
    rng = np.random.default_rng(20261101); bs = []
    for _ in range(2000):
        st = [s for i in rng.integers(0, len(mods), len(mods)) for s in by[mods[i]]]
        bs.append(np.mean([ap(r, st) for r in HC]) - np.mean([ap(r, st) for r in SP]))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f'  -> F51 AP HC - SUPPF {d:+.4f}, module bootstrap 95% [{lo:+.4f}, {hi:+.4f}] (own RNG): guard {"FAIL" if hi < 0 else "passed"}')
    print('## SUMMARY: E1 relF1@2 %+.4f %s | E1 inactive IoU %+.4f %s | mechanism %+.4f %s | F51 guard hi %+.4f %s'
          % (e1v['relF1'][0], e1v['relF1'][2], e1v['inact'][0], e1v['inact'][2], g, 'PASSED' if g >= 0.05 else 'FAILED', hi, 'FAIL' if hi < 0 else 'passed'))


if __name__ == '__main__':
    if sys.argv[1] == 'selftest':
        sys.exit(0 if selftest(sys.argv[2], sys.argv[3]) else 1)
    run(*sys.argv[2:10])
