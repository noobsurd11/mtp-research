"""coach (2 Nov): independent recompute for protocol_SKR2_HC2's opening (E1 opening #5). Own code (not s2_* / el_metrics readouts).
Test primaries (two sets, tau 0 / 1) are done by coach_verify.py b0456b28 per arm; this file does the rest:
  A. E1 co-primaries from argmax m0 ext cells (106, pooled per run): crack relF1@2 (coach_thin.e1_agg), any-hit component recall
     (m0 crack_cc gt [size, hit]: size >= 20 and hit >= 1, hit = px within 2 px of a prediction), inactive IoU (e1_agg). Rule 1 /3
     per contrast: SKR01 -> relF1 + any-hit; HC2 -> relF1 + inactive. Reported: E1 relP / relR, pred / GT crack px, crack-free px.
  B. B5 on the wide grid (SKR01 co-primary; HC2 reported) from el_metrics_w records (grid read from each record): arm-pooled OP on
     val (max recall s.t. precision >= 0.90 over tenths in [grid min, 12]; ties smaller b; unreachable -> max precision, flagged);
     comp recall (v50 + b > 0, comps >= 20 px) and relR@2; test (50) and test_clean (49); rule 1 + two-set rule. Per-run OPs reported.
  C. Guards: G1 test inactive IoU d <= -0.015 in both sets (both arms); G2 (SKR01) test relP@2 d (all 50, argmax) < -0.03 or E1
     crack px on E1 crack-free cells (GT crack px 0) > 1.5 x SUPPF's (seed means); G3 (HC2) F51 crack AP 36-module bootstrap upper
     97.5 pct < 0 (own AP / own RNG, coach_hc).
  D. Mechanism (HC2; SKR01 context): SHV1 matched relR@2 at relP@2 >= 0.90, 5 seeds pooled (coach_hc.pooled); kill if < +0.05.
Usage: python -I coach_s2.py run S2_POST S2_SYNDUMP PF2_POST HC_POST HC_SYNDUMP RF RF_SETS E1CTX
       python -I coach_s2.py selftest PF2_POST HC_POST HC_SYNDUMP THIN_POST RF RF_SETS E1CTX"""
import json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coach_thin as ct  # rule1, twoset, e1_agg, load_m0
import coach_hc as ch    # pooled (SHV1), recs (narrow grid), hist, ap_of

SEEDS = [5, 6, 7, 8, 9]; CR, IN, NOISY = 14, 11, 'CSIR_00070_r8_c4'
R = lambda p: [f'{p}_100pct_s{k}' for k in SEEDS]


def m0s(d, runs, rev=None):
    return [ct.load_m0(f'{d}/{r}.json', rev) for r in runs]


# ---------- A. E1 ----------
def e1_vals(m):
    c = m['cells']['ext']; a = ct.e1_agg(c, lambda s: True)
    n = h = 0; pred = gt = free = 0
    for s, x in c.items():
        for sz, hit in x['crack_cc']['gt']:
            if sz >= 20:
                n += 1; h += int(hit >= 1)
        C = np.asarray(x['conf'], float).reshape(24, 24); pred += C[:, CR].sum(); gt += C[CR].sum()
        if C[CR].sum() == 0:
            free += C[:, CR].sum()
    return {'relF1': a['relF1'], 'inact': a['inact'], 'anyhit': h / max(n, 1), 'ncomp': n, 'relP': a['relP'], 'relR': a['relR'],
            'predGT': pred / max(gt, 1), 'free': free}


def e1_block(M, arms, base):
    V = {a: [e1_vals(m) for m in M[a]] for a in M}
    for a in M:
        print(f'  {a:6s} ' + ' | '.join(f'{k} {np.mean([v[k] for v in V[a]]):.4f}' for k in ('relF1', 'anyhit', 'inact', 'relP', 'relR', 'predGT'))
              + f' | crack-free px {np.mean([v["free"] for v in V[a]]):.0f} | comps {V[a][0]["ncomp"]}')
        print(f'         per seed relF1 ' + ' '.join(f'{v["relF1"]:.4f}' for v in V[a]) + ' | any-hit ' + ' '.join(f'{v["anyhit"]:.4f}' for v in V[a])
              + ' | inact ' + ' '.join(f'{v["inact"]:.4f}' for v in V[a]))
    out = {}
    for a, keys in arms.items():
        for k in keys:
            r = ct.rule1([v[k] for v in V[base]], [v[k] for v in V[a]]); out[(a, k)] = r
            print(f'  -> E1 {a} - {base} {k}: {r[0]:+.4f} (thr {r[1]:.4f}) {r[2]}')
    return V, out


# ---------- C. guards from m0 ----------
def test_vals(m):
    t = m['cells']['test']
    A = ct.e1_agg(t, lambda s: True); B = ct.e1_agg(t, lambda s: s != NOISY)
    return {'inact_all': A['inact'], 'inact_clean': B['inact'], 'relP_all': A['relP']}


def g1(MT, a, base):
    da = np.mean([v['inact_all'] for v in MT[a]]) - np.mean([v['inact_all'] for v in MT[base]])
    dc = np.mean([v['inact_clean'] for v in MT[a]]) - np.mean([v['inact_clean'] for v in MT[base]])
    return da, dc, (da <= -0.015 and dc <= -0.015)


def g2(MT, V, a, base):
    dr = np.mean([v['relP_all'] for v in MT[a]]) - np.mean([v['relP_all'] for v in MT[base]])
    x = np.mean([v['free'] for v in V[a]]) / np.mean([v['free'] for v in V[base]])
    return dr, x, (dr < -0.03 or x > 1.5)


# ---------- B. B5 wide ----------
def recw(path):
    d = json.load(open(path)); return np.asarray(d['grid'], float), d['cells']


def curves_w(cells, G):
    cs = list(cells.values())
    S = lambda k: np.sum([np.asarray(c[k], np.int64) for c in cs], 0)
    pred, rp, rr, n20, h20 = S('pred'), S('relp_tp'), S('relr_tp'), S('pc20_n'), S('pc20_hit')
    ng = sum(c['n_gt'] for c in cs)
    v50 = np.array([x[1] for c in cs for x in c['gt_cc'] if x[0] >= 20])
    dv = lambda a, b: np.where(b > 0, a / np.maximum(b, 1), np.nan)
    return {'relR': rr / max(ng, 1), 'relP': dv(rp, pred), 'compR': (v50[:, None] + G[None, :] > 0).mean(0) if len(v50) else np.full(len(G), np.nan),
            'compP': dv(h20, n20)}


def opj(G):
    return np.array([j for j, b in enumerate(G) if abs(round(b * 10) - b * 10) < 1e-6 and G.min() - 1e-9 <= b <= 12.0 + 1e-9])


def op_w(cv, rk, pk, J):
    Rv, Pv = cv[rk][J], np.nan_to_num(cv[pk][J], nan=-1)
    ok = np.where(Pv >= 0.90)[0]
    return (int(J[ok[np.argmax(Rv[ok])]]), True) if len(ok) else (int(J[np.argmax(Pv)]), False)


def b5_arm_w(recdir, runs):
    vals = [recw(f'{recdir}/{r}.val.json') for r in runs]; G = vals[0][0]
    assert all(np.array_equal(v[0], G) for v in vals); J = opj(G)
    pooled = {f'{i}:{s}': c for i, (_, v) in enumerate(vals) for s, c in v.items()}
    pc = curves_w(pooled, G); jc, okc = op_w(pc, 'compR', 'compP', J); jr, okr = op_w(pc, 'relR', 'relP', J)
    res = {'b_comp': float(G[jc]), 'b_rel': float(G[jr]), 'reach': okc and okr, 'grid': (float(G.min()), float(G.max()), len(G))}
    for st, sub in (('test', None), ('test_clean', NOISY), ('ext', None)):
        cR, rR, cRr, rRr = [], [], [], []
        for i, r in enumerate(runs):
            G2_, cells = recw(f'{recdir}/{r}.{"ext" if st == "ext" else "test"}.json'); assert np.array_equal(G2_, G)
            if sub:
                cells = {s: c for s, c in cells.items() if s != sub}
            tc = curves_w(cells, G); cR.append(tc['compR'][jc]); rR.append(tc['relR'][jr])
            vc = curves_w(vals[i][1], G); jcr, _ = op_w(vc, 'compR', 'compP', J); jrr, _ = op_w(vc, 'relR', 'relP', J)
            cRr.append(tc['compR'][jcr]); rRr.append(tc['relR'][jrr])
        res[st] = {'compR': cR, 'relR': rR, 'compR_run': cRr, 'relR_run': rRr}
    return res


def b5_contrast(Bb, Ba, name):
    out = {}
    for k in ('compR', 'relR'):
        ra = ct.rule1(Bb['test'][k], Ba['test'][k]); rc = ct.rule1(Bb['test_clean'][k], Ba['test_clean'][k])
        out[k] = (ra, rc, ct.twoset(ra, rc))
        pr = ct.rule1(Bb['test'][k + '_run'], Ba['test'][k + '_run'])
        print(f'  -> B5 {name} {k} @ P>=0.90, pooled OP: all {ra[0]:+.4f} (thr {ra[1]:.4f}) {ra[2]} | clean {rc[0]:+.4f} (thr {rc[1]:.4f}) {rc[2]} '
              f'| two-set {out[k][2]} | per-run OP all {pr[0]:+.4f} {pr[2]} (reported) | E1 (desc) {np.mean(Ba["ext"][k]) - np.mean(Bb["ext"][k]):+.4f}')
    return out


# ---------- F51 + SHV1 ----------
def f51(arms, rf, rfs, seed=20261101):
    from PIL import Image
    rows = [l.rstrip('\n').split('\t') for l in open(rfs) if l.strip()][1:]
    rfset = {r[0]: r[1] for r in rows}; module = {r[0]: r[3] for r in rows}
    H = {}
    for a, (dumpd, runs) in arms.items():
        for r in runs:
            z = np.load(f'{dumpd}/{r}.rf.npz'); H[r] = {}
            for i, s in enumerate(str(x) for x in z['stems']):
                if rfset[s] != 'F51':
                    continue
                gt = np.array(Image.open(f'{rf}/masks/{s}.png')); keep = ~(np.array(Image.open(f'{rf}/ignore/{s}.png')) > 0)
                H[r][s] = ch.hist(z['pc'][i], gt, keep)
    any_r = next(iter(H)); f = sorted(H[any_r]); mods = sorted({module[s] for s in f}); by = {m: [s for s in f if module[s] == m] for m in mods}
    assert len(f) == 51 and len(mods) == 36
    ap = lambda r, st: ch.ap_of(np.sum([H[r][s][0] for s in st], 0), np.sum([H[r][s][1] for s in st], 0))
    return ap, f, mods, by


def run(post, syndump, pf2, hcp, hcsyn, rf, rfs, ctxf):
    print('## A. E1 co-primaries (106, argmax, pooled per run; rule 1 /3)')
    M = {'SUPPF': m0s(f'{pf2}/m0', R('pf2_SUPPF'), 'e544133'), 'SKR01': m0s(f'{post}/m0/SKR01', R('skr2_SKR01'), 'c9bbb02'),
         'HC2': m0s(f'{post}/m0/HC2', R('hc2_HCig'), '0405151')}
    V, E1 = e1_block(M, {'SKR01': ('relF1', 'anyhit'), 'HC2': ('relF1', 'inact')}, 'SUPPF')
    print('## C. guards')
    MT = {a: [test_vals(m) for m in M[a]] for a in M}
    G = {}
    for a in ('SKR01', 'HC2'):
        G[(a, 'G1')] = g1(MT, a, 'SUPPF'); d = G[(a, 'G1')]
        print(f'  G1 {a}: test inactive d all {d[0]:+.4f} / clean {d[1]:+.4f} -> {"TRIP" if d[2] else "ok"}')
    G[('SKR01', 'G2')] = g2(MT, V, 'SKR01', 'SUPPF'); d = G[('SKR01', 'G2')]
    print(f'  G2 SKR01: test relP@2 d {d[0]:+.4f} (trip < -0.03); E1 crack-free px x{d[1]:.2f} (trip > 1.5; SUPPF mean {np.mean([v["free"] for v in V["SUPPF"]]):.0f}) -> {"TRIP" if d[2] else "ok"}')
    print('## B. B5 wide grid')
    B = {a: b5_arm_w(f'{post}/b5/{a}/rec_w', R(p)) for a, p in (('SUPPF', 'pf2_SUPPF'), ('SKR01', 'skr2_SKR01'), ('HC2', 'hc2_HCig'))}
    for a in B:
        print(f'  {a}: grid {B[a]["grid"]} pooled OP b_comp {B[a]["b_comp"]:+.1f} b_rel {B[a]["b_rel"]:+.1f} reachable {B[a]["reach"]}')
    B5 = {a: b5_contrast(B['SUPPF'], B[a], f'{a}-SUPPF' + ('' if a == 'SKR01' else ' (reported)')) for a in ('SKR01', 'HC2')}
    print('## D. F51 (G3 for HC2; reported for SKR01) + SHV1 mechanism')
    ap, f, mods, by = f51({'SUPPF': (hcsyn, R('pf2_SUPPF')), 'SKR01': (syndump, R('skr2_SKR01')), 'HC2': (syndump, R('hc2_HCig'))}, rf, rfs)
    rng = np.random.default_rng(20261101); draws = [[s for i in rng.integers(0, 36, 36) for s in by[mods[i]]] for _ in range(2000)]
    for a, p in (('SKR01', 'skr2_SKR01'), ('HC2', 'hc2_HCig')):
        d = np.mean([ap(r, f) for r in R(p)]) - np.mean([ap(r, f) for r in R('pf2_SUPPF')])
        bs = [np.mean([ap(r, st) for r in R(p)]) - np.mean([ap(r, st) for r in R('pf2_SUPPF')]) for st in draws]
        lo, hi = np.percentile(bs, [2.5, 97.5]); G[(a, 'G3')] = (d, lo, hi, hi < 0)
        print(f'  F51 {a} - SUPPF crack AP {d:+.4f} boot [{lo:+.4f}, {hi:+.4f}] (own RNG)' + (f' -> G3 {"TRIP" if hi < 0 else "ok"}' if a == 'HC2' else ' (reported)'))
    sp = set(l.strip() for l in open('/home/noob/work/domain_scratch/out/shv1p_stems_eval.txt') if l.strip())
    mech = {}
    for a, d, p in (('SUPPF', f'{hcp}/shv1/rec', 'pf2_SUPPF'), ('SKR01', f'{post}/shv1/rec', 'skr2_SKR01'), ('HC2', f'{post}/shv1/rec', 'hc2_HCig')):
        mech[a] = {st: ch.pooled([ch.recs(f'{d}/{r}.{ "synval" if st != "V0" else "val"}.json') for r in R(p)], sp if st == 'SHV1p' else None) for st in ('V0', 'SHV1', 'SHV1p')}
        print(f'  {a}: matched relR@2 V0 / SHV1 / SHV1-p {mech[a]["V0"]["matched"]:.4f} / {mech[a]["SHV1"]["matched"]:.4f} / {mech[a]["SHV1p"]["matched"]:.4f}; '
              f'oracle b V0 / SHV1 {mech[a]["V0"]["oracle_b"]:+.1f} / {mech[a]["SHV1"]["oracle_b"]:+.1f}')
    gm = mech['HC2']['SHV1']['matched'] - mech['SUPPF']['SHV1']['matched']
    print(f'  -> mechanism HC2 - SUPPF {gm:+.4f} (kill < +0.05): {"PASSED" if gm >= 0.05 else "FAILED"}; SKR01 (context) {mech["SKR01"]["SHV1"]["matched"] - mech["SUPPF"]["SHV1"]["matched"]:+.4f}')
    print('## SUMMARY (test co-primaries from coach_verify files)')
    for a in ('SKR01', 'HC2'):
        e = [f'E1 {k} {E1[(a, k)][0]:+.4f} {E1[(a, k)][2]}' for (aa, k) in E1 if aa == a]
        b = [f'B5 {k} {B5[a][k][2]}' for k in ('compR', 'relR')] if a == 'SKR01' else []
        g = [f'{gg} {"TRIP" if G[(a, gg)][-1] else "ok"}' for gg in ('G1', 'G2', 'G3') if (a, gg) in G and not (a == 'SKR01' and gg == 'G3')]
        print(f'  {a}: ' + ' | '.join(e + b + g) + (f' | mechanism {gm:+.4f}' if a == 'HC2' else ''))


def selftest(pf2, hcp, hcsyn, thin, rf, rfs, ctxf):
    ok = True
    M = {'SUPPF': m0s(f'{pf2}/m0', R('pf2_SUPPF'), 'e544133'), 'HC': m0s(f'{hcp}/m0', R('hc_HC'), 'c2e6973'),
         'SKR': m0s(f'{thin}/m0', R('thin_SKR'), 'c9bbb02'), 'CLD': m0s(f'{thin}/m0', R('thin_CLD'), 'c9bbb02')}
    V = {a: [e1_vals(m) for m in M[a]] for a in M}; MT = {a: [test_vals(m) for m in M[a]] for a in M}
    mv = lambda a, k: np.mean([v[k] for v in V[a]])
    chk = [('SUPPF relF1', mv('SUPPF', 'relF1'), 0.4202, 5e-5), ('SUPPF anyhit', mv('SUPPF', 'anyhit'), 0.3811, 5e-5), ('SUPPF inact', mv('SUPPF', 'inact'), 0.2371, 5e-5),
           ('HC relF1', mv('HC', 'relF1'), 0.4338, 5e-5), ('HC anyhit', mv('HC', 'anyhit'), 0.377, 5e-4), ('HC inact', mv('HC', 'inact'), 0.2369, 5e-5),
           ('SKR anyhit', mv('SKR', 'anyhit'), 0.523, 5e-4), ('SUPPF free', mv('SUPPF', 'free'), 3931, 0.6)]
    for a, (e_all, e_cl) in (('HC', (-0.0228, -0.0230)), ('SKR', (-0.0170, -0.0161)), ('CLD', (-0.0114, -0.0106))):
        d = g1(MT, a, 'SUPPF'); chk += [(f'{a} G1 all', d[0], e_all, 5e-5), (f'{a} G1 clean', d[1], e_cl, 5e-5)]
    for a, (er, ex) in (('SKR', (-0.0702, 2.40)), ('CLD', (-0.0186, 1.53))):
        d = g2(MT, V, a, 'SUPPF'); chk += [(f'{a} G2 relP', d[0], er, 5e-5), (f'{a} G2 ratio', d[1], ex, 5e-3)]
    for name, got, exp, tol in chk:
        p = abs(got - exp) <= tol; ok &= p
        print(f'  {name}: {got:.4f} vs {exp} -> {"ok" if p else "MISMATCH"}')
    Bs, Bk = b5_arm_w(f'{pf2}/b5/rec', R('pf2_SUPPF')), b5_arm_w(f'{thin}/b5/rec', R('thin_SKR'))
    Bc = b5_arm_w(f'{thin}/b5/rec', R('thin_CLD'))
    o = b5_contrast(Bs, Bk, 'SKR-SUPPF (selftest, narrow grid)'); oc = b5_contrast(Bs, Bc, 'CLD-SUPPF (selftest)')
    for name, got, exp in (('SKR compR all', o['compR'][0][0], 0.0413), ('SKR compR clean', o['compR'][1][0], 0.0417), ('CLD relR all', oc['relR'][0][0], -0.0374),
                           ('CLD relR clean', oc['relR'][1][0], -0.0376)):
        p = abs(got - exp) <= 5e-5; ok &= p; print(f'  {name}: {got:+.4f} vs {exp:+.4f} -> {"ok" if p else "MISMATCH"}')
    ap, f, mods, by = f51({'SUPPF': (hcsyn, R('pf2_SUPPF')), 'HC': (hcsyn, R('hc_HC'))}, rf, rfs)
    d = np.mean([ap(r, f) for r in R('hc_HC')]) - np.mean([ap(r, f) for r in R('pf2_SUPPF')])
    p = abs(d - 0.0669) <= 5e-5; ok &= p; print(f'  F51 HC - SUPPF {d:+.4f} vs +0.0669 -> {"ok" if p else "MISMATCH"}')
    print('SELFTEST', 'PASS' if ok else 'FAIL')
    return ok


if __name__ == '__main__':
    if sys.argv[1] == 'selftest':
        sys.exit(0 if selftest(*sys.argv[2:9]) else 1)
    run(*sys.argv[2:10])
