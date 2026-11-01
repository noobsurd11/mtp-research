"""coach (1 Nov, successor session): independent recompute for protocol_thin_b3's opening (own code; not runner's
thin_e1_relf1.py, not calib's el_metrics summary). Test primaries (crack IoU / relF1@2 / inactive IoU, two sets) are done by
team_2026-10-29_features/scripts/coach_verify.py (coach's own); this file does the rest:
  A. E1 co-primary: crack relF1@2, all 106 ext cells pooled per run (sum of crack_rel2 = [pred near GT, pred, GT near pred, GT]),
     argmax m0 JSONs, rule 1 (/3) vs SUPPF (PF2's opening m0, seeds 5-9); E1 reported: relR/relP, crack R/P/IoU, comp R/P, inactive,
     strata 29/77 and 58/48.
  B. B5 co-primaries from calib's per-cell records (rec/<run>.<set>.json: per grid b counts), recomputed here from the raw counts:
     OP = max val recall s.t. val precision >= 0.90 on b in -4.0..+12.0 step 0.1 (ties smaller b; none -> max precision, flagged),
     arm-pooled (val counts of all 5 seeds) and per run; test (all 50), test_clean (no CSIR_00070_r8_c4), ext. Rule 1 (/3) and the
     two-set rule for SKR / CLD (B3 reported). Speck guard (all-size comp precision, speck share) at each OP.
  C. B3: train scuff readout (scuff_train_iou JSONs, CPU fp32), E1 crack-on-scuff (m0 ext 'scuff' dicts) vs the comparator.
Usage: python coach_thin.py run   THIN_RAW PF2_RAW E1CTX     (THIN_RAW = own pull of el_thin/reports/thin/post; PF2_RAW = own PF2 pull)
       python coach_thin.py selftest PF2_RAW E1CTX            (B5 on PF2's SUP / SUPPF / RN50PF records -> compare with coach_v/b5_pf2.txt)
"""
import json, os, sys
import numpy as np

NC, CR, IN = 24, 14, 11
NOISY = 'CSIR_00070_r8_c4'
SEEDS = [5, 6, 7, 8, 9]
GRID = np.unique(np.round(np.concatenate([np.arange(-40, 121) / 10.0, [0.75]]), 2))
OPJ = np.array([j for j, b in enumerate(GRID) if abs(round(b * 10) - b * 10) < 1e-6])  # -4.0..12.0 step 0.1 (0.75 excluded)


def rule1(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    thr = max(0.01, 2 * np.sqrt((a.std(ddof=1) ** 2 + b.std(ddof=1) ** 2) / 3)); d = b.mean() - a.mean()
    return d, thr, ('BETTER' if d > thr else 'WORSE' if d < -thr else 'nd')


def twoset(r_all, r_clean):
    (d1, _, v1), (d2, _, v2) = r_all, r_clean
    if 'WORSE' in (v1, v2):
        return 'WORSE'
    if (v1 == 'BETTER' and (v2 == 'BETTER' or (v2 == 'nd' and d2 > 0))) or (v2 == 'BETTER' and v1 == 'nd' and d1 > 0):
        return 'BETTER'
    return 'nd'


def fmt(r):
    return f'{r[0]:+.4f} (thr {r[1]:.4f}) {r[2]}'


# ---------- A. E1 from m0 per-cell JSONs ----------
def e1_agg(cells, keep):
    C = np.zeros((NC, NC)); x = np.zeros(4); gt = [0, 0]; pr = [0, 0]
    for s, c in cells.items():
        if not keep(s):
            continue
        C += np.asarray(c['conf'], float).reshape(NC, NC); x += np.asarray(c['crack_rel2'], float)
        for sz, h in c['crack_cc']['gt']:
            if sz >= 20:
                gt[0] += 1; gt[1] += int(h >= 0.5 * sz)
        for sz, h in c['crack_cc']['pr']:
            if sz >= 20:
                pr[0] += 1; pr[1] += int(h >= 1)
    tp = np.diag(C); g = C.sum(1); p = C.sum(0)
    rp = x[0] / max(x[1], 1); rr = x[2] / max(x[3], 1)
    return {'relF1': 2 * rp * rr / max(rp + rr, 1e-12), 'relR': rr, 'relP': rp, 'cR': tp[CR] / max(g[CR], 1),
            'cP': tp[CR] / max(p[CR], 1), 'crack': tp[CR] / max(g[CR] + p[CR] - tp[CR], 1),
            'inact': tp[IN] / max(g[IN] + p[IN] - tp[IN], 1), 'compR': gt[1] / max(gt[0], 1), 'compP': pr[1] / max(pr[0], 1)}


def load_m0(path, rev=None):
    d = json.load(open(path)); assert d['step'] == 20000, (path, d['step'])
    if rev:
        assert str(d.get('code_revision', '')).startswith(rev), (path, d.get('code_revision'))
    assert len(d['cells']['ext']) == 106 and len(d['cells']['test']) == 50 and len(d['cells']['val']) == 54, path
    return d


# ---------- B. B5 from calib's records (own curves) ----------
def curves(cells):
    cs = list(cells.values())
    S = lambda k: np.sum([np.asarray(c[k], np.int64) for c in cs], 0)
    pred, rp, rr, n20, h20, pn, ph, sp = S('pred'), S('relp_tp'), S('relr_tp'), S('pc20_n'), S('pc20_hit'), S('pc_n'), S('pc_hit'), S('speck_px')
    ng = sum(c['n_gt'] for c in cs)
    v50 = np.array([x[1] for c in cs for x in c['gt_cc'] if x[0] >= 20])
    found = (v50[:, None] + GRID[None, :] > 0).mean(0) if len(v50) else np.full(len(GRID), np.nan)
    dv = lambda a, b: np.where(b > 0, a / np.maximum(b, 1), np.nan)
    return {'relR': rr / max(ng, 1), 'relP': dv(rp, pred), 'compR': found, 'compP': dv(h20, n20),
            'compP_all': dv(ph, pn), 'speck': dv(sp, pred), 'ncomp': len(v50)}


def op(cv, rk, pk):
    R, P = cv[rk][OPJ], np.nan_to_num(cv[pk][OPJ], nan=-1)
    ok = np.where(P >= 0.90)[0]
    if len(ok):
        i = ok[np.argmax(R[ok])]; return int(OPJ[i]), True
    return int(OPJ[np.argmax(P)]), False


def rec(raw, run, st):
    d = json.load(open(f'{raw}/b5/rec/{run}.{st}.json')); assert d['set'] == st and d['grid'] == list(GRID), (run, st)
    return d['cells']


def b5_arm(raw, runs, label):
    """per-run and arm-pooled OPs; returns {mode: {set: {'compR': [...], 'relR': [...], ...}}}"""
    vals = [rec(raw, r, 'val') for r in runs]
    tgt = {st: [rec(raw, r, st) for r in runs] for st in ('test', 'ext')}
    pooled = {}
    for i, v in enumerate(vals):
        pooled.update({f'{i}:{s}': c for s, c in v.items()})
    pc = curves(pooled)
    jpc, okc = op(pc, 'compR', 'compP'); jpr, okr = op(pc, 'relR', 'relP')
    out = {}
    for mode in ('per-run', 'pooled'):
        out[mode] = {}
        for st, sub in (('test', None), ('test_clean', NOISY), ('ext', None)):
            res = {k: [] for k in ('compR', 'compP', 'relR', 'relP', 'b_comp', 'b_rel', 'reach', 'edge', 'compP_all_c', 'speck_c', 'compP_all_r', 'speck_r')}
            for i, r in enumerate(runs):
                if mode == 'pooled':
                    jc, oc, jr, orr = jpc, okc, jpr, okr
                else:
                    vc = curves(vals[i]); jc, oc = op(vc, 'compR', 'compP'); jr, orr = op(vc, 'relR', 'relP')
                cells = tgt['ext' if st == 'ext' else 'test'][i]
                if sub:
                    cells = {s: c for s, c in cells.items() if s != sub}
                tc = curves(cells)
                res['compR'].append(tc['compR'][jc]); res['compP'].append(tc['compP'][jc])
                res['relR'].append(tc['relR'][jr]); res['relP'].append(tc['relP'][jr])
                res['b_comp'].append(GRID[jc]); res['b_rel'].append(GRID[jr]); res['reach'].append(oc and orr)
                res['edge'].append(GRID[jc] >= 11.5 or GRID[jr] >= 11.5)
                res['compP_all_c'].append(tc['compP_all'][jc]); res['speck_c'].append(tc['speck'][jc])
                res['compP_all_r'].append(tc['compP_all'][jr]); res['speck_r'].append(tc['speck'][jr])
            out[mode][st] = res
    return out


def b5_print(arms, base, contrasts, coprim_arms):
    verdict = {}
    for mode in ('per-run', 'pooled'):
        for st in ('test', 'test_clean', 'ext'):
            print(f'## B5 {mode} OP | {st}')
            for a, R in arms.items():
                r = R[mode][st]
                print(f'  {a:7s} compR@P.90 {np.mean(r["compR"]):.4f}±{np.std(r["compR"], ddof=1):.4f} (compP {np.nanmean(r["compP"]):.4f}) | '
                      f'relR@relP.90 {np.mean(r["relR"]):.4f}±{np.std(r["relR"], ddof=1):.4f} (relP {np.nanmean(r["relP"]):.4f}) | '
                      f'b_comp {[round(float(x), 1) for x in r["b_comp"]]} b_rel {[round(float(x), 1) for x in r["b_rel"]]} '
                      f'reachable {all(r["reach"])} edge {any(r["edge"])} | speck guard opc compP_all {np.nanmean(r["compP_all_c"]):.3f} '
                      f'speck {np.nanmean(r["speck_c"]):.4f}; opr compP_all {np.nanmean(r["compP_all_r"]):.3f} speck {np.nanmean(r["speck_r"]):.4f}')
            for name, A, B in contrasts:
                ra, rb = arms[A][mode][st], arms[B][mode][st]
                c, rl = rule1(ra['compR'], rb['compR']), rule1(ra['relR'], rb['relR'])
                verdict[(name, mode, st)] = (c, rl)
                print(f'  {name:12s} compR {fmt(c)} | relR {fmt(rl)}' + ('' if st != 'ext' else '  [E1: descriptive]'))
    print('## B5 co-primaries, two-set rule at the ARM-POOLED OP (protocol_thin_b3 §4)')
    out = {}
    for name, A, B in contrasts:
        if B not in coprim_arms:
            continue
        c = twoset(verdict[(name, 'pooled', 'test')][0], verdict[(name, 'pooled', 'test_clean')][0])
        r = twoset(verdict[(name, 'pooled', 'test')][1], verdict[(name, 'pooled', 'test_clean')][1])
        out[name] = (c, r)
        print(f'  {name:12s} comp recall @ compP>=0.90: {c} | relR@2 @ relP@2>=0.90: {r}')
    return out


def selftest(pf2raw, ctx):
    arms = {a: b5_arm(pf2raw, [f'pf2_{a}_100pct_s{k}' for k in SEEDS], a) for a in ('SUP', 'SUPPF', 'RN50PF')}
    b5_print(arms, 'SUP', [('PF2', 'SUP', 'SUPPF'), ('RN', 'SUPPF', 'RN50PF')], [])
    m0 = {a: [load_m0(f'{pf2raw}/m0/pf2_{a}_100pct_s{k}.json') for k in SEEDS] for a in ('SUP', 'SUPPF')}
    v = {a: [e1_agg(d['cells']['ext'], lambda s: True) for d in m0[a]] for a in m0}
    print('## E1 relF1@2 selftest (PF2 SUPPF - SUP):', fmt(rule1([x['relF1'] for x in v['SUP']], [x['relF1'] for x in v['SUPPF']])),
          '| SUPPF', ' '.join(f'{x["relF1"]:.4f}' for x in v['SUPPF']))


def run(thinraw, pf2raw, ctxf, rev):
    ctx = {}
    for l in open(ctxf):
        f = l.rstrip('\n').split('\t')
        if len(f) >= 4:
            ctx[f[0]] = (f[2] == 'scuff=1', f[3] == 'halfcut=1')
    ARMS = ['SKR', 'CLD', 'B3']
    m0 = {'SUPPF': [load_m0(f'{pf2raw}/m0/pf2_SUPPF_100pct_s{k}.json', 'e544133') for k in SEEDS]}
    for a in ARMS:
        m0[a] = [load_m0(f'{thinraw}/m0/thin_{a}_100pct_s{k}.json', rev) for k in SEEDS]
    stems = sorted(m0['SUPPF'][0]['cells']['ext'])
    assert all(sorted(d['cells']['ext']) == stems for v in m0.values() for d in v)
    assert set(stems) == set(ctx), 'E1 ctx mismatch'
    # A. E1
    groups = [('E1 all 106', lambda s: True), ('scuff+halfcut 29', lambda s: ctx[s][0] and ctx[s][1]),
              ('other 77', lambda s: not (ctx[s][0] and ctx[s][1])), ('half-cut 58', lambda s: ctx[s][1]), ('full 48', lambda s: not ctx[s][1])]
    KEYS = ['relF1', 'relR', 'relP', 'cR', 'cP', 'crack', 'compR', 'compP', 'inact']
    e1v = {}
    for gname, keep in groups:
        print(f'## {gname}' + ('' if gname == 'E1 all 106' else ' [descriptive]'))
        vals = {a: [e1_agg(d['cells']['ext'], keep) for d in m0[a]] for a in m0}
        for a in m0:
            print(f'  {a:6s} ' + ' | '.join(f'{k} {np.mean([m[k] for m in vals[a]]):.4f}±{np.std([m[k] for m in vals[a]], ddof=1):.4f}' for k in KEYS))
        for a in ARMS:
            print(f'  {a}-SUPPF ' + ' | '.join('%s %+.4f(%.4f) %s' % ((k,) + rule1([m[k] for m in vals['SUPPF']], [m[k] for m in vals[a]])) for k in KEYS))
        if gname == 'E1 all 106':
            e1v = vals
    print('## E1 CO-PRIMARY: crack relF1@2, all 106, argmax, rule 1 (/3) vs SUPPF (one set)')
    for a in ['SUPPF'] + ARMS:
        print(f'  {a:6s} per seed ' + ' '.join(f'{m["relF1"]:.4f}' for m in e1v[a]))
    E1 = {}
    for a in ARMS:
        E1[a] = rule1([m['relF1'] for m in e1v['SUPPF']], [m['relF1'] for m in e1v[a]])
        print(f'  {a}-SUPPF E1 relF1@2 {fmt(E1[a])}')
    # B. B5
    arms = {'SUPPF': b5_arm(pf2raw, [f'pf2_SUPPF_100pct_s{k}' for k in SEEDS], 'SUPPF')}
    for a in ARMS:
        arms[a] = b5_arm(thinraw, [f'thin_{a}_100pct_s{k}' for k in SEEDS], a)
    B5 = b5_print(arms, 'SUPPF', [(f'{a}-SUPPF', 'SUPPF', a) for a in ARMS], ['SKR', 'CLD'])
    # C. B3 scuff
    print('## B3 train scuff readout (scuff_train_iou, CPU fp32, 12 train cells, step 20000)')
    sti = {}
    for k in SEEDS:
        for n in (f'thin_B3_100pct_s{k}', f'pf2_SUPPF_100pct_s{k}'):
            p = f'{thinraw}/scuff_train_iou/{n}.json'
            if os.path.exists(p):
                sti[n] = json.load(open(p)); assert sti[n]['step'] == 20000 and sti[n]['n_cells'] == 12 and sti[n]['scuff_px'] == 3246, n
    if len(sti) == 10:
        iou = [sti[f'thin_B3_100pct_s{k}']['scuff_iou'] for k in SEEDS]
        print('  B3 scuff IoU per seed ' + ' '.join(f'{x:.4f}' for x in iou) + f' | mean {np.mean(iou):.4f} -> '
              + ('"scuff class not learned; the arm\'s effect is the relabelling of 649 train crack px" (pre-stated, mean < 0.10)' if np.mean(iou) < 0.10 else 'learned (mean >= 0.10)'))
        for key in ('scuff_precision', 'scuff_recall', 'p_scuff_on_scuff_mean', 'p_scuff_other_mean', 'p_scuff_ratio', 'share_scuff_px_p_gt_0_1'):
            print(f'  B3 {key} ' + ' '.join(f'{sti[f"thin_B3_100pct_s{k}"][key]:.4g}' for k in SEEDS))
        cb = [sti[f'thin_B3_100pct_s{k}']['crack_on_scuff'] for k in SEEDS]; cs = [sti[f'pf2_SUPPF_100pct_s{k}']['crack_on_scuff'] for k in SEEDS]
        print(f'  train crack-on-scuff px (of 3,246): B3 {cb} mean {np.mean(cb):.1f} | SUPPF {cs} mean {np.mean(cs):.1f} | ratio {np.mean(cb) / max(np.mean(cs), 1e-9):.3f}')
        for k in SEEDS:
            print(f'  s{k} gt_scuff_predicted_as B3 {sti[f"thin_B3_100pct_s{k}"]["gt_scuff_predicted_as"]} | SUPPF {sti[f"pf2_SUPPF_100pct_s{k}"]["gt_scuff_predicted_as"]}')
    else:
        print(f'  scuff_train_iou incomplete: {len(sti)} of 10 files')
    print('## B3 E1 crack-on-scuff (m0_audit_b3 --ext-scuff; whole image; descriptive)')
    def sc(cells):
        t = {'scuff_px': 0, 'crack_on_scuff': 0, 'scuffpred_on_scuff': 0, 'scuffpred_px': 0, 'n_scuff_cells': 0}
        for c in cells.values():
            s = c['scuff']
            for k in ('scuff_px', 'crack_on_scuff', 'scuffpred_on_scuff', 'scuffpred_px'):
                t[k] += s[k]
            t['n_scuff_cells'] += int(s['scuff_px'] > 0)
        return t
    cmpd = f'{thinraw}/m0_comparator_scuff'
    rows = {'B3': [sc(d['cells']['ext']) for d in m0['B3']]}
    if all(os.path.exists(f'{cmpd}/pf2_SUPPF_100pct_s{k}.json') for k in SEEDS):
        rows['SUPPF'] = [sc(json.load(open(f'{cmpd}/pf2_SUPPF_100pct_s{k}.json'))['cells']['ext']) for k in SEEDS]
    for a in ('SKR', 'CLD'):
        if 'scuff' in next(iter(m0[a][0]['cells']['ext'].values())):
            rows[a] = [sc(d['cells']['ext']) for d in m0[a]]
    for a, rr in rows.items():
        print(f'  {a:6s} scuff px {rr[0]["scuff_px"]} in {rr[0]["n_scuff_cells"]} cells | crack_on_scuff per seed {[x["crack_on_scuff"] for x in rr]} '
              f'mean {np.mean([x["crack_on_scuff"] for x in rr]):.1f} | scuffpred_on_scuff {[x["scuffpred_on_scuff"] for x in rr]} | scuffpred_px {[x["scuffpred_px"] for x in rr]}')
    if 'SUPPF' in rows:
        mb, ms = np.mean([x['crack_on_scuff'] for x in rows['B3']]), np.mean([x['crack_on_scuff'] for x in rows['SUPPF']])
        print(f'  B3 vs SUPPF E1 crack-on-scuff: {ms:.1f} -> {mb:.1f} ({(mb / ms - 1) * 100:+.1f}%; pre-stated expectation -20% to -60%)')
    # summary
    print('## SUMMARY (test primaries two-set: from coach_verify.py files; here E1 + B5)')
    for a in ARMS:
        print(f'  {a}: E1 relF1@2 {E1[a][2]}' + (f' | B5 compR {B5[a + "-SUPPF"][0]} relR {B5[a + "-SUPPF"][1]}' if a in ('SKR', 'CLD') else ''))


if __name__ == '__main__':
    if sys.argv[1] == 'selftest':
        selftest(sys.argv[2], sys.argv[3])
    else:
        run(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else None)
