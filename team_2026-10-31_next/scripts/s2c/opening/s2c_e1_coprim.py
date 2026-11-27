"""SKR2C (protocol_SKR2C §3a.3, E1 opening #7) = s2_e1_coprim.py 6e08c084 with: arms are seeds 10-14 (refs stay s5-9), every arm run
asserts 74 crack-free E1 cells and 296 GT components >= 20 px (prediction-independent), labels, and a reported 10-seed view for a ref
named <ARM>_s5-9 (s5-14 means; "5 of 10 seeds opened before"). Self-test verbatim. Original docstring follows.
SKR2 + HC2 E1 co-primaries (protocol_SKR2_HC2 v1.0.1 §3a.3 / §3b.2; E1 opening #5; E1 = second test set, pre-registered, read once).
DRAFT (runner's helper, 2 Nov 2026) for coach's review and FREEZE. CPU only, reads m0 per-cell JSONs (ext cells), no model, no image.
From hc_e1_coprim.py (5a8fbe89, frozen HC): relf1(), inact(), rule1() and the strata block kept verbatim; changed: arms are explicit
run lists (--arm NAME M0_DIR RUN x5, seeds 5..9 from the names), contrasts per arm (--contrast), the any-hit metric, E1 width readouts,
reference rows, the self-test.

Per run, all 106 ext117 cells pooled, argmax (default m0 JSONs, not tau). m0 cell fields (m0_audit d36f7438 / m0_audit_tau d77241bb
cell_stats(), read in the code): conf = bincount(gt * 24 + pred) over keep px, i.e. a 24x24 row-major GT x pred matrix; crack_rel2 =
[pred crack px within 2 px of GT crack, pred crack px, GT crack px within 2 px of pred, GT crack px] (keep px); crack_cc['gt'] = one
[size, hit] per 8-conn GT crack component in keep, hit = its px within 2 px (EDT) of a predicted crack px in keep.
  relF1    E1 crack relF1@2: thin_e1_relf1.py (98bcb979) relf1() verbatim: relP = sum c0 / sum c1, relR = sum c2 / sum c3, 2PR/(P+R).
  anyhit   E1 any-hit component recall (§3a.3): pooled list of crack_cc['gt'] over the 106 cells; #(size >= 20 and hit >= 1) / #(size >= 20)
           (= m0_analyze.agg cc_recany_20, asserted in the self-test).
  inactIoU E1 inactive IoU: Track M m0_analyze.agg (d5adbe6b, imported) ["iou"][11] on the pooled confusion.
Reported per run (never a verdict): relP@2, relR@2, pred / GT crack px (conf column 14 / row 14 sums over keep), crack px on the
crack-free cells (conf row 14 sum 0) and their count, number of GT components >= 20 px.
Contrasts (--contrast ARM METRIC ...; protocol §3: SKR01 relF1 anyhit, HC2 relF1 inactIoU) vs --base, rule 1 (/3), sd ddof 1:
  delta > max(0.01, 2*sqrt((sdA^2+sdB^2)/3)) BETTER, < -thr WORSE, else n.d. Every other metric of every arm is printed as reported.
Reference rows (--ref NAME M0_DIR RUN x5; already opened, NOT contrasts; protocol §4): HC p 0.35 (HC opening) and SKR w 1.0 (THIN
  opening, m0_audit_b3 files: if conf is 25x25 the 24x24 GT x pred block is used, as judge's skr2hc2_check; dropped px are counted).
Asserts (arms): step 20000, 106 ext cells, the same 106 stems in every run, conf 24x24, code_revision per arm (--rev NAME REV).
Strata (reported only, --ctx e1_context.tsv 12bd1385): 29 scuff+half-cut, 29 half-cut without scuff, 48 full, 58 half-cut, 77 other.
--selftest: on the opened SUPPF s5-9 (PF2) and HC s5-9 (HC opening) m0 files, per file (a) relF1 == relf1() extracted by ast from the
  frozen thin_e1_relf1.py, exact; (b) relF1 == m0_analyze.agg relF1, exact; (c) inactive IoU (agg) == the pooled-confusion formula of
  pf2_e1_extra.py (d404dd25), |d| <= 1e-12; (d) any-hit == agg cc_recany_20 and n == agg cc_n_20, exact; (e) pred / GT / crack-free px
  from conf == from crack_rel2, exact; (f) relF1 / relP / relR / inactIoU == the HC opening's e1_coprim.json (0c461952) per-run values,
  exact. Summary values checked against the opened numbers (protocol §3a.3, verify_hc.md, judge): SUPPF relF1 0.4202, any-hit 0.3811
  (per seed 0.399 / 0.355 / 0.429 / 0.365 / 0.358; 296 components per run), inactive IoU 0.2371; HC relF1 0.4338, inactive IoU 0.2369
  (= e1_coprim.json arm means, exact), any-hit 0.377. Prints booleans and only these expected-vs-got values. exit 0 iff all hold.
Usage: python s2_e1_coprim.py --arm SUPPF <pf2 post/m0> RUN x5 --arm SKR01 <s2 post/m0/SKR01> RUN x5 --arm HC2 <...> RUN x5 \
         --rev SUPPF e544133 --rev SKR01 c9bbb02 --rev HC2 <dep> --base SUPPF --contrast SKR01 relF1 anyhit --contrast HC2 relF1 inactIoU \
         [--ref HC <hc post/m0> RUN x5] [--ref SKRw1 <thin post/m0> RUN x5] --trackm DIR [--ctx e1_context.tsv] [--json OUT.json]
       python s2_e1_coprim.py --selftest --pf2-m0 DIR --hc-m0 DIR --hc-json e1_coprim.json --trackm DIR --thin thin_e1_relf1.py
"""
import argparse, ast, hashlib, json, math, sys
import numpy as np

MD5 = {'m0_analyze.py': 'd5adbe6bfb84ce251f56ec7494a69663', 'thin_e1_relf1.py': '98bcb979cd49bc87e4b2f076961f4074',
       'e1_context.tsv': '12bd138523fccfc6be5b41df35d19147', 'hc_e1_coprim.json': '0c4619527288c63c0b4d25ab7c9d0930'}
NC, CR, IN, CMIN = 24, 14, 11, 20
METRICS = ('relF1', 'anyhit', 'inactIoU')
LAB = {'relF1': 'E1 crack relF1@2', 'anyhit': 'E1 any-hit comp recall', 'inactIoU': 'E1 inactive IoU'}

ap = argparse.ArgumentParser()
ap.add_argument('--arm', nargs='+', action='append', default=[], metavar='NAME M0 RUN')
ap.add_argument('--ref', nargs='+', action='append', default=[], metavar='NAME M0 RUN')
ap.add_argument('--rev', nargs=2, action='append', default=[], metavar=('NAME', 'REV'))
ap.add_argument('--contrast', nargs='+', action='append', default=[], metavar='ARM METRIC')
ap.add_argument('--base', default='SUPPF')
ap.add_argument('--trackm', required=True, help='dir holding Track M m0_analyze.py (md5 d5adbe6b)')
ap.add_argument('--thin', help='frozen thin_e1_relf1.py (md5 98bcb979), for --selftest')
ap.add_argument('--ctx', help='e1_context.tsv (md5 12bd1385): strata, reported only')
ap.add_argument('--json'); ap.add_argument('--selftest', action='store_true')
ap.add_argument('--pf2-m0'); ap.add_argument('--hc-m0'); ap.add_argument('--hc-json')
a = ap.parse_args()


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


assert md5(f'{a.trackm}/m0_analyze.py') == MD5['m0_analyze.py'], 'm0_analyze.py md5'
sys.path.insert(0, a.trackm)
from m0_analyze import agg  # noqa: E402


def relf1(cells):  # verbatim from thin_e1_relf1.py (98bcb979)
    r = np.sum([c['crack_rel2'] for c in cells.values()], 0).astype(float)
    p, q = r[0] / max(r[1], 1), r[2] / max(r[3], 1)
    return 2 * p * q / max(p + q, 1e-9), p, q


def inact(cells, keep=lambda s: True):
    return float(agg(cells, keep)['iou'][IN])


def anyhit(cells):  # protocol §3a.3: GT comps >= 20 px, any-hit iff hit >= 1, pooled over the given cells
    g = [c for e in cells.values() for c in e['crack_cc']['gt'] if c[0] >= CMIN]
    return (sum(c[1] >= 1 for c in g) / len(g) if g else float('nan')), len(g)


def to24(cells):  # reference rows only: 25x25 m0_audit_b3 conf -> its 24x24 GT x pred block (judge's convention); dropped px counted
    out, drop = {}, 0
    for s, c in cells.items():
        n = math.isqrt(len(c['conf'])); assert n * n == len(c['conf']) and n in (24, 25), (s, len(c['conf']))
        M = np.asarray(c['conf'], np.int64).reshape(n, n)
        drop += int(M.sum() - M[:NC, :NC].sum())
        out[s] = dict(c, conf=M[:NC, :NC].ravel().tolist())
    return out, drop


def width(cells):  # reported: pred / GT crack px and crack-free px from conf (keep px)
    C = sum(np.asarray(c['conf'], np.int64).reshape(NC, NC) for c in cells.values())
    free = [s for s, c in cells.items() if np.asarray(c['conf'], np.int64).reshape(NC, NC)[CR].sum() == 0]
    fpx = int(sum(np.asarray(cells[s]['conf'], np.int64).reshape(NC, NC)[:, CR].sum() for s in free))
    return {'pred_px': int(C[:, CR].sum()), 'gt_px': int(C[CR].sum()), 'pred_over_gt': float(C[:, CR].sum() / max(C[CR].sum(), 1)),
            'crackfree_px': fpx, 'n_crackfree': len(free)}


def run_row(run, e):
    f, p, q = relf1(e); h, n = anyhit(e)
    return {'run': run, 'relF1': f, 'relP': p, 'relR': q, 'anyhit': h, 'n_comp20': n, 'inactIoU': inact(e), **width(e)}


if a.selftest:
    assert a.thin and md5(a.thin) == MD5['thin_e1_relf1.py'], 'thin_e1_relf1.py md5'
    assert a.hc_json and md5(a.hc_json) == MD5['hc_e1_coprim.json'], 'HC opening e1_coprim.json md5 != 0c461952'
    tree = ast.parse(open(a.thin).read())
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'relf1']
    assert len(fn) == 1, 'relf1 not found once in thin_e1_relf1.py'
    mod = ast.Module(body=[ast.Import(names=[ast.alias(name='numpy', asname='np')]), fn[0]], type_ignores=[])
    ns = {}; exec(compile(ast.fix_missing_locations(mod), a.thin, 'exec'), ns)
    HJ = json.load(open(a.hc_json))
    ok, R = True, {'SUPPF': [], 'HC': []}
    for arm, d, stem in (('SUPPF', a.pf2_m0, 'pf2_SUPPF_100pct_s'), ('HC', a.hc_m0, 'hc_HC_100pct_s')):
        ref = {x['run']: x for x in HJ['per_run'][arm]}
        for k in range(5, 10):
            f = f'{d}/{stem}{k}.json'; run = f'{stem}{k}'
            e = json.load(open(f))['cells']['ext']
            assert len(e) == 106, (f, len(e))
            C = np.zeros((NC, NC))
            for c in e.values():
                C += np.asarray(c['conf'], float).reshape(NC, NC)
            tp, g, p = np.diag(C), C.sum(1), C.sum(0)
            ref_in = tp[IN] / max(g[IN] + p[IN] - tp[IN], 1) if g[IN] > 0 else float('nan')  # pf2_e1_extra.py m()['inact']
            row = run_row(run, e); A = agg(e, lambda s: True); R[arm].append(row)
            rel = np.sum([c['crack_rel2'] for c in e.values()], 0)
            frel = sum(c['crack_rel2'][1] for c in e.values() if c['crack_rel2'][3] == 0)
            t = (row['relF1'] == ns['relf1'](e)[0], row['relF1'] == A['relF1'], abs(row['inactIoU'] - ref_in) <= 1e-12,
                 row['anyhit'] == A['cc_recany_20'] and row['n_comp20'] == A['cc_n_20'],
                 row['pred_px'] == rel[1] and row['gt_px'] == rel[3] and row['crackfree_px'] == frel,
                 all(row[m] == ref[run][m] for m in ('relF1', 'relP', 'relR', 'inactIoU')))
            ok &= all(t)
            print(f'selftest {run}: relF1 == thin relf1 {t[0]} | relF1 == agg relF1 {t[1]} | inactive IoU (agg) == pf2_e1_extra formula {t[2]} | '
                  f'any-hit == agg cc_recany_20 {t[3]} | px from conf == from crack_rel2 {t[4]} | == HC opening e1_coprim.json per run {t[5]}')
    mn = lambda arm, m: float(np.mean([x[m] for x in R[arm]]))
    chk = [('SUPPF E1 relF1@2 (protocol / verify_hc)', round(mn('SUPPF', 'relF1'), 4), 0.4202),
           ('SUPPF E1 any-hit (protocol §3a.3, judge)', round(mn('SUPPF', 'anyhit'), 4), 0.3811),
           ('SUPPF E1 any-hit per seed (judge)', [round(x['anyhit'], 3) for x in R['SUPPF']], [0.399, 0.355, 0.429, 0.365, 0.358]),
           ('SUPPF GT components >= 20 px per run (judge)', [x['n_comp20'] for x in R['SUPPF']], [296] * 5),
           ('SUPPF E1 inactive IoU (protocol / verify_hc)', round(mn('SUPPF', 'inactIoU'), 4), 0.2371),
           ('HC E1 relF1@2 (verify_hc)', round(mn('HC', 'relF1'), 4), 0.4338),
           ('HC E1 relF1@2 == e1_coprim.json arm mean (exact)', mn('HC', 'relF1') == HJ['arms']['HC']['relF1']['mean'], True),
           ('HC E1 inactive IoU (verify_hc)', round(mn('HC', 'inactIoU'), 4), 0.2369),
           ('HC E1 inactive IoU == e1_coprim.json arm mean (exact)', mn('HC', 'inactIoU') == HJ['arms']['HC']['inactIoU']['mean'], True),
           ('HC E1 any-hit (judge reference)', round(mn('HC', 'anyhit'), 3), 0.377)]
    for lab, got, exp in chk:
        ok &= got == exp
        print(f'selftest summary {lab}: expected {exp} got {got} -> {got == exp}')
    print('SELFTEST', 'PASS' if ok else 'FAIL', '(10 opened files: SUPPF s5-9, HC s5-9)')
    sys.exit(0 if ok else 1)

arms = {x[0]: (x[1], x[2:]) for x in a.arm}; refs = {x[0]: (x[1], x[2:]) for x in a.ref}
assert a.base in arms and len(arms) >= 2 and all(len(v[1]) == 5 for v in list(arms.values()) + list(refs.values())), 'need 5 runs per arm / ref'
assert all(r.endswith(f'_s{k}') for v in arms.values() for r, k in zip(v[1], range(10, 15))), 'arm runs must be s10..s14 in order'
assert all(r.endswith(f'_s{k}') for v in refs.values() for r, k in zip(v[1], range(5, 10))), 'ref runs must be s5..s9 in order'
contr = {x[0]: x[1:] for x in a.contrast}
assert set(contr) <= set(arms) - {a.base} and all(m in METRICS for v in contr.values() for m in v), contr
rev = dict(a.rev); R = {}; E = {}; stems = None; REFR = {}; DROP = {}
for name, (d, runs) in arms.items():
    R[name], E[name] = [], []
    for run in runs:
        j = json.load(open(f'{d}/{run}.json'))
        assert j['run'] == run and j['step'] == 20000, (name, run, j.get('run'), j['step'])
        if name in rev:
            assert j['code_revision'] == rev[name], (name, run, j['code_revision'])
        e = j['cells']['ext']; assert len(e) == 106, (name, run, len(e))
        assert all(len(c['conf']) == NC * NC for c in e.values()), (name, run, 'conf not 24x24')
        stems = stems or sorted(e); assert sorted(e) == stems, (name, run)
        R[name].append(run_row(run, e)); E[name].append(e)
        assert R[name][-1]['n_crackfree'] == 74 and R[name][-1]['n_comp20'] == 296, (name, run, 'E1 GT: 74 crack-free cells, 296 comps')
for name, (d, runs) in refs.items():
    REFR[name], DROP[name] = [], []
    for run in runs:
        j = json.load(open(f'{d}/{run}.json')); assert j['step'] == 20000 and len(j['cells']['ext']) == 106, (name, run)
        e, dr = to24(j['cells']['ext']); assert sorted(e) == stems, (name, run)
        REFR[name].append(run_row(run, e)); DROP[name].append(dr)


def rule1(xb, xa):
    xa, xb = np.asarray(xa, float), np.asarray(xb, float)
    d = xb.mean() - xa.mean(); thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    return {'delta': float(d), 'thr': float(thr), 'reading': 'BETTER' if d > thr else ('WORSE' if d < -thr else 'n.d.')}


ms = lambda v: f'{np.mean(v):.4f}±{np.std(v, ddof=1):.4f}'
KEYS = ('relF1', 'relP', 'relR', 'anyhit', 'inactIoU', 'pred_over_gt', 'crackfree_px')
out = {'label': 'protocol_SKR2C §3a.3 E1 co-primaries (E1 opening #7; same 106 E1 cells, 3rd look); all 106 cells pooled per run, argmax; rule 1 (/3)',
       'base': a.base, 'contrasts': contr, 'per_run': R, 'arms': {}, 'rule1': {}, 'reported_deltas': {}, 'refs_not_contrasts': {},
       'strata_reported_only': {}, 'md5': {'m0_analyze.py': MD5['m0_analyze.py'], 'this_file': md5(__file__)}}
L = ['## E1 co-primaries (protocol_SKR2C §3a.3; same 106 E1 cells as #5 / #6, 3rd look), all 106 cells pooled per run, argmax; seeds 10-14']
for name in R:
    out['arms'][name] = {m: {'mean': float(np.mean([x[m] for x in R[name]])), 'sd': float(np.std([x[m] for x in R[name]], ddof=1))} for m in KEYS}
    for m in METRICS:
        v = [x[m] for x in R[name]]
        L.append(f'{name:6s} {LAB[m]:23s} ' + ' '.join(f'{x:.4f}' for x in v) + f' | mean {np.mean(v):.4f} sd {np.std(v, ddof=1):.4f}'
                 + ('' if name == a.base or m in contr.get(name, ()) else '  (reported)'))
    L.append(f'{name:6s} (reported) relP@2 / relR@2 ' + ' '.join(f"{x['relP']:.4f}/{x['relR']:.4f}" for x in R[name])
             + ' | pred/GT crack px ' + ' '.join(f"{x['pred_over_gt']:.3f}" for x in R[name])
             + f" | crack px on {R[name][0]['n_crackfree']} crack-free cells " + ' '.join(str(x['crackfree_px']) for x in R[name])
             + f" | comps >= 20 px {R[name][0]['n_comp20']}")
L.append(f'\n## rule 1 (/3) vs {a.base}: delta > max(0.01, 2*sqrt((sdA^2+sdB^2)/3)) BETTER, < -thr WORSE, else n.d.')
for name in R:
    if name == a.base:
        continue
    out['rule1'][name], out['reported_deltas'][name] = {}, {}
    for m in METRICS:
        xa, xb = [x[m] for x in R[a.base]], [x[m] for x in R[name]]
        r = rule1(xb, xa)
        if m in contr.get(name, ()):
            out['rule1'][name][m] = r
            L.append(f"{name} - {a.base} | CO-PRIMARY {LAB[m]} | {name} {ms(xb)} | {a.base} {ms(xa)} | delta {r['delta']:+.4f} | thr {r['thr']:.4f} | {r['reading']}")
        else:
            out['reported_deltas'][name][m] = r
            L.append(f"{name} - {a.base} | (reported, not a co-primary) {LAB[m]} | delta {r['delta']:+.4f} | thr {r['thr']:.4f}")
    for m in ('relP', 'relR', 'pred_over_gt', 'crackfree_px'):
        out['reported_deltas'][name][m] = float(np.mean([x[m] for x in R[name]]) - np.mean([x[m] for x in R[a.base]]))
    L.append(f"{name} - {a.base} | (reported, next to any-hit) E1 relP@2 {out['reported_deltas'][name]['relP']:+.4f} relR@2 "
             f"{out['reported_deltas'][name]['relR']:+.4f} pred/GT {out['reported_deltas'][name]['pred_over_gt']:+.3f} crack-free px x"
             f"{np.mean([x['crackfree_px'] for x in R[name]]) / max(np.mean([x['crackfree_px'] for x in R[a.base]]), 1e-9):.2f}")
L.append('(E1 part only. Verdict R also needs the test co-primaries (two-set rule), B5 and the guards.)')
if REFR:
    L.append('\n## reference rows (already opened; NOT contrasts; protocol §4)')
    for name, rows in REFR.items():
        out['refs_not_contrasts'][name] = {'per_run': rows, 'conf_px_dropped_25to24': DROP[name],
                                           'mean': {m: float(np.mean([x[m] for x in rows])) for m in KEYS}}
        L.append(f'{name:6s} ' + ' | '.join(f'{LAB.get(m, m)} {ms([x[m] for x in rows])}' for m in KEYS)
                 + (f' | 25x25 conf: px outside the 24x24 block {sum(DROP[name])}' if any(DROP[name]) else ''))
    TV = [(n, n.rsplit('_s5-9', 1)[0]) for n in REFR if n.endswith('_s5-9') and n.rsplit('_s5-9', 1)[0] in R]
    if TV:
        L.append('\n## 10-seed view (REPORTED ONLY; s5-14 single means; 5 of 10 seeds opened before)')
        for n, arm in TV:
            rows = REFR[n] + R[arm]; out.setdefault('ten_seed_view_reported', {})[arm] = {m: float(np.mean([x[m] for x in rows])) for m in KEYS}
            L.append(f'{arm:6s} s5-14 ' + ' | '.join(f'{LAB.get(m, m)} {ms([x[m] for x in rows])}' for m in KEYS))
if a.ctx:
    assert md5(a.ctx) == MD5['e1_context.tsv'], 'e1_context.tsv md5'
    rows = [l.rstrip('\n').split('\t') for l in open(a.ctx) if l.strip()]
    cx = {r[0]: dict(x.split('=') for x in r[2:4]) for r in rows}; c2 = {r[0]: r[1] for r in rows}
    assert set(stems) <= set(cx)
    n_sh = sum(cx[s]['scuff'] == '1' and cx[s]['halfcut'] == '1' for s in stems)
    assert n_sh == sum(c2[s] == 'scuff_halfcut' for s in stems), 'e1_context col 2 vs scuff/halfcut columns'
    assert (n_sh, sum(cx[s]['halfcut'] == '1' for s in stems)) == (29, 58), 'strata sizes (29 scuff+half-cut, 58 half-cut)'
    G = {'scuff+half-cut': lambda s: cx[s]['scuff'] == '1' and cx[s]['halfcut'] == '1',
         'half-cut without scuff': lambda s: cx[s]['scuff'] == '0' and cx[s]['halfcut'] == '1',
         'full': lambda s: cx[s]['halfcut'] == '0', 'half-cut': lambda s: cx[s]['halfcut'] == '1',
         'other (not scuff+half-cut)': lambda s: not (cx[s]['scuff'] == '1' and cx[s]['halfcut'] == '1')}
    L.append('\n## E1 strata (REPORTED ONLY, never a verdict; protocol §4): group | n | arm | relF1@2 mean±sd | inactive IoU mean±sd | any-hit mean±sd')
    for g, keep in G.items():
        st = [s for s in stems if keep(s)]; out['strata_reported_only'][g] = {'n': len(st)}
        for name in R:
            vf = [relf1({s: e[s] for s in st})[0] for e in E[name]]; vi = [inact(e, keep) for e in E[name]]
            vh = [anyhit({s: e[s] for s in st})[0] for e in E[name]]
            out['strata_reported_only'][g][name] = {'relF1': vf, 'inactIoU': vi, 'anyhit': vh}
            L.append(f'{g:27s} | {len(st):3d} | {name:6s} | {np.mean(vf):.4f}±{np.std(vf, ddof=1):.4f} | {np.nanmean(vi):.4f}±{np.nanstd(vi, ddof=1):.4f}'
                     f' | {np.nanmean(vh):.4f}±{np.nanstd(vh, ddof=1):.4f}')
print('\n'.join(L))
if a.json:
    json.dump(out, open(a.json, 'w'), indent=1)
