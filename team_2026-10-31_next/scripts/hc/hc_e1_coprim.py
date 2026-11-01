"""HC E1 co-primaries (protocol_HC.md v1.1 §4; E1 opening #3; user policy 31 Oct: E1 = second test set, pre-registered, read once).
DRAFT (runner's helper, 1 Nov 2026) for coach's review and FREEZE. CPU only, reads m0 per-cell JSONs, no model, no image.

Co-primaries, per run, all 106 ext117 cells pooled, argmax (default m0 JSONs, not tau):
  E1 crack relF1@2 : thin_e1_relf1.py (98bcb979) relf1(), copied verbatim below: sum of the per-cell crack_rel2 counts
                     [pred near GT, pred, GT near pred, GT]; relP = c0/c1, relR = c2/c3, relF1 = 2PR/(P+R).
  E1 inactive IoU  : Track M m0_analyze.agg (d5adbe6b, imported from --trackm) ["iou"][11] on the pooled 24x24 confusion.
Per arm mean +- sd (ddof 1) over --seeds; rule 1 (/3): delta > max(0.01, 2*sqrt((sdA^2+sdB^2)/3)) BETTER, < -thr WORSE, else n.d.
Arms: --arm NAME M0_DIR PREFIX, files M0_DIR/PREFIX_NAME_100pct_sK.json (HC from the HC opening's m0 dir, prefix hc; SUPPF from PF2's
opening m0 dir, prefix pf2, reused unchanged). Asserts: step 20000, 106 ext cells, the same 106 stems in every run, code_revision per
arm (--rev NAME REV). Reported only (never a verdict): strata from --ctx (e1_context.tsv 12bd1385): 29 scuff+half-cut, 29 half-cut
without scuff, 48 full, 58 half-cut, 77 other.
--selftest FILE ...: on given m0 JSONs (ext cells) checks, per file, (a) relF1 here == relf1() extracted by ast from the frozen
thin_e1_relf1.py (--thin, md5 asserted), exact; (b) relF1 here == m0_analyze.agg relF1, exact (thin's own self-test); (c) inactive IoU
here (agg) == the pooled-confusion formula of pf2_e1_extra.py (d404dd25, PF2's E1 co-primary code), |d| <= 1e-12. Prints booleans
only (no metric value), exit 0 iff all hold.
Usage: python hc_e1_coprim.py --arm SUPPF <pf2 post/m0> pf2 --arm HC <hc post/m0> hc --rev SUPPF e544133 --rev HC c2e6973 \
         --base SUPPF --trackm DIR [--ctx e1_context.tsv] [--json OUT.json]
       python hc_e1_coprim.py --selftest F.json ... --trackm DIR --thin thin_e1_relf1.py
"""
import argparse, ast, hashlib, json, sys
import numpy as np

MD5 = {'m0_analyze.py': 'd5adbe6bfb84ce251f56ec7494a69663', 'thin_e1_relf1.py': '98bcb979cd49bc87e4b2f076961f4074',
       'e1_context.tsv': '12bd138523fccfc6be5b41df35d19147'}
NC, CR, IN = 24, 14, 11

ap = argparse.ArgumentParser()
ap.add_argument('--arm', nargs=3, action='append', default=[], metavar=('NAME', 'M0', 'PREFIX'))
ap.add_argument('--rev', nargs=2, action='append', default=[], metavar=('NAME', 'REV'))
ap.add_argument('--base', default='SUPPF'); ap.add_argument('--seeds', nargs='+', type=int, default=[5, 6, 7, 8, 9])
ap.add_argument('--trackm', required=True, help='dir holding Track M m0_analyze.py (md5 d5adbe6b)')
ap.add_argument('--thin', help='frozen thin_e1_relf1.py (md5 98bcb979), for --selftest')
ap.add_argument('--ctx', help='e1_context.tsv (md5 12bd1385): strata, reported only')
ap.add_argument('--json'); ap.add_argument('--selftest', nargs='+')
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


if a.selftest:
    assert a.thin and md5(a.thin) == MD5['thin_e1_relf1.py'], 'thin_e1_relf1.py md5'
    tree = ast.parse(open(a.thin).read())
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'relf1']
    assert len(fn) == 1, 'relf1 not found once in thin_e1_relf1.py'
    mod = ast.Module(body=[ast.Import(names=[ast.alias(name='numpy', asname='np')]), fn[0]], type_ignores=[])
    ns = {}; exec(compile(ast.fix_missing_locations(mod), a.thin, 'exec'), ns)
    ok = True
    for f in a.selftest:
        e = json.load(open(f))['cells']['ext']
        assert len(e) == 106, (f, len(e))
        C = np.zeros((NC, NC))
        for c in e.values():
            C += np.asarray(c['conf'], float).reshape(NC, NC)
        tp, g, p = np.diag(C), C.sum(1), C.sum(0)
        ref_in = tp[IN] / max(g[IN] + p[IN] - tp[IN], 1) if g[IN] > 0 else float('nan')  # pf2_e1_extra.py m()['inact']
        mine_f, mine_i = relf1(e)[0], inact(e)
        t = (mine_f == ns['relf1'](e)[0], mine_f == agg(e, lambda s: True)['relF1'], abs(mine_i - ref_in) <= 1e-12)
        ok &= all(t)
        print(f'selftest {f.split("/")[-1]}: relF1 == thin relf1 {t[0]} | relF1 == agg relF1 {t[1]} | inactive IoU (agg) == pf2_e1_extra formula {t[2]}')
    print('SELFTEST', 'PASS' if ok else 'FAIL', f'({len(a.selftest)} files)')
    sys.exit(0 if ok else 1)

assert a.arm and a.base in [x[0] for x in a.arm], 'need --arm for the base and the test arm'
rev = dict(a.rev); R = {}; stems = None; E = {}
for name, d, pre in a.arm:
    R[name], E[name] = [], []
    for k in a.seeds:
        j = json.load(open(f'{d}/{pre}_{name}_100pct_s{k}.json'))
        assert j['step'] == 20000, (name, k, j['step'])
        if name in rev:
            assert j['code_revision'] == rev[name], (name, k, j['code_revision'])
        e = j['cells']['ext']; assert len(e) == 106, (name, k, len(e))
        stems = stems or sorted(e); assert sorted(e) == stems, (name, k)
        f, p, q = relf1(e)
        R[name].append({'run': f'{pre}_{name}_100pct_s{k}', 'relF1': f, 'relP': p, 'relR': q, 'inactIoU': inact(e)})
        E[name].append(e)


def rule1(xb, xa):
    xa, xb = np.asarray(xa, float), np.asarray(xb, float)
    d = xb.mean() - xa.mean(); thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    return {'delta': float(d), 'thr': float(thr), 'reading': 'BETTER' if d > thr else ('WORSE' if d < -thr else 'n.d.')}


out = {'label': 'protocol_HC §4 E1 co-primaries (E1 opening #3); all 106 cells pooled per run, argmax; rule 1 (/3)',
       'seeds': a.seeds, 'base': a.base, 'per_run': R, 'arms': {}, 'rule1': {}, 'strata_reported_only': {},
       'md5': {'m0_analyze.py': MD5['m0_analyze.py'], 'this_file': md5(__file__)}}
L = [f'## E1 co-primaries (protocol_HC §4), all 106 cells pooled per run, argmax; seeds {a.seeds}']
for name in R:
    out['arms'][name] = {m: {'mean': float(np.mean([x[m] for x in R[name]])), 'sd': float(np.std([x[m] for x in R[name]], ddof=1))}
                         for m in ('relF1', 'relP', 'relR', 'inactIoU')}
    for m, lab in (('relF1', 'E1 crack relF1@2'), ('inactIoU', 'E1 inactive IoU')):
        v = [x[m] for x in R[name]]
        L.append(f'{name:6s} {lab:17s} ' + ' '.join(f'{x:.4f}' for x in v) + f' | mean {np.mean(v):.4f} sd {np.std(v, ddof=1):.4f}')
    L.append(f'{name:6s} (relP@2 / relR@2, reported) ' + ' '.join(f"{x['relP']:.4f}/{x['relR']:.4f}" for x in R[name]))
L.append(f'\n## rule 1 (/3) vs {a.base}: delta > max(0.01, 2*sqrt((sdA^2+sdB^2)/3)) BETTER, < -thr WORSE, else n.d.')
for name in R:
    if name == a.base:
        continue
    out['rule1'][name] = {}
    for m, lab in (('relF1', 'E1 crack relF1@2'), ('inactIoU', 'E1 inactive IoU')):
        xa, xb = [x[m] for x in R[a.base]], [x[m] for x in R[name]]
        r = rule1(xb, xa); out['rule1'][name][m] = r
        L.append(f'{name} - {a.base} | {lab} | {name} {np.mean(xb):.4f}±{np.std(xb, ddof=1):.4f} | {a.base} {np.mean(xa):.4f}±{np.std(xa, ddof=1):.4f} | '
                 f"delta {r['delta']:+.4f} | thr {r['thr']:.4f} | {r['reading']}")
L.append('(E1 part only. The HC PASS also needs the test co-primaries under the two-set rule: protocol_HC §4.)')
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
    L.append('\n## E1 strata (REPORTED ONLY, never a verdict; protocol_HC §6): group | n | arm | relF1@2 mean±sd | inactive IoU mean±sd')
    for g, keep in G.items():
        st = [s for s in stems if keep(s)]; out['strata_reported_only'][g] = {'n': len(st)}
        for name in R:
            vf = [relf1({s: e[s] for s in st})[0] for e in E[name]]; vi = [inact(e, keep) for e in E[name]]
            out['strata_reported_only'][g][name] = {'relF1': vf, 'inactIoU': vi}
            L.append(f'{g:27s} | {len(st):3d} | {name:6s} | {np.mean(vf):.4f}±{np.std(vf, ddof=1):.4f} | {np.nanmean(vi):.4f}±{np.nanstd(vi, ddof=1):.4f}')
print('\n'.join(L))
if a.json:
    json.dump(out, open(a.json, 'w'), indent=1)
