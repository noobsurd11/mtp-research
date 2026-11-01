"""THIN-B3 E1 co-primary (protocol_thin_b3.md §4, user decision 31 Oct: E1 = second test set, pre-registered, read once):
E1 crack relF1@2, all 106 ext117 cells pooled per run, argmax (default m0 per-cell JSONs), rule 1 (/3) vs SUP100-PF.
Successor of pf2_e1_extra.py (d404dd25) for this one metric: same JSON inputs, same per-run pooling (sum of the per-cell
crack_rel2 counts [pred near GT, pred, GT near pred, GT], relP = c0/c1, relR = c2/c3, relF1 = 2PR/(P+R)), equal to Track M
m0_analyze.agg's relF1 (self-test below). Per arm: --arm NAME M0_DIR PREFIX (files PREFIX_NAME_100pct_sK.json, K in --seeds).
Asserts: step 20000, 106 ext cells, the same 106 stems in every run, code_revision as given per arm (--rev NAME REV).
Usage: python thin_e1_relf1.py --arm SUPPF <pf2 m0> pf2 --arm SKR <thin m0> thin ... --rev SUPPF e544133 --rev SKR <deploy> \
         --base SUPPF [--seeds 5 6 7 8 9]
       python thin_e1_relf1.py --selftest <m0 dir> (opening-1 f3_ runs: compares with m0_analyze.agg relF1 on ext, all 106)
"""
import argparse, json, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('--arm', nargs=3, action='append', metavar=('NAME', 'M0', 'PREFIX'))
ap.add_argument('--rev', nargs=2, action='append', default=[], metavar=('NAME', 'REV'))
ap.add_argument('--base', default='SUPPF'); ap.add_argument('--seeds', nargs='+', type=int, default=[5, 6, 7, 8, 9])
ap.add_argument('--selftest')
a = ap.parse_args()


def relf1(cells):
    r = np.sum([c['crack_rel2'] for c in cells.values()], 0).astype(float)
    p, q = r[0] / max(r[1], 1), r[2] / max(r[3], 1)
    return 2 * p * q / max(p + q, 1e-9), p, q


if a.selftest:
    sys.path.insert(0, '/home/yugma/mtp/research/team_2026-10-24_go/trackM/scripts')
    from m0_analyze import agg
    ok = True
    for arm in ['SUP', 'SUPPF', 'MIMPF']:
        for k in range(5):
            c = json.load(open(f'{a.selftest}/f3_{arm}_100pct_s{k}.json'))['cells']['ext']
            mine, ref = relf1(c)[0], agg(c, lambda s: True)['relF1']
            ok &= mine == ref
    print('selftest: relF1 equals Track M m0_analyze.agg relF1 on all 15 opening-1 runs (ext, 106 cells):', ok)
    sys.exit(0 if ok else 1)

rev = dict(a.rev); R = {}; stems = None
for name, d, pre in a.arm:
    vals = []
    for k in a.seeds:
        j = json.load(open(f'{d}/{pre}_{name}_100pct_s{k}.json'))
        assert j['step'] == 20000, (name, k, j['step'])
        if name in rev:
            assert j['code_revision'] == rev[name], (name, k, j['code_revision'])
        e = j['cells']['ext']; assert len(e) == 106, (name, k, len(e))
        stems = stems or sorted(e); assert sorted(e) == stems, (name, k)
        vals.append(relf1(e))
    R[name] = vals
print(f'## E1 crack relF1@2 (co-primary), all 106 cells pooled per run, argmax; seeds {a.seeds}')
for name in R:
    v = R[name]
    print(f"{name:6s} relF1 " + ' '.join(f'{x[0]:.4f}' for x in v) + f" | mean {np.mean([x[0] for x in v]):.4f} sd {np.std([x[0] for x in v], ddof=1):.4f}"
          + " | relP " + ' '.join(f'{x[1]:.4f}' for x in v) + " | relR " + ' '.join(f'{x[2]:.4f}' for x in v))
print(f'\n## rule 1 (/3) vs {a.base}: delta > max(0.01, 2*sqrt((sdA^2+sdB^2)/3)) BETTER, < -thr WORSE, else n.d.')
xa = np.array([x[0] for x in R[a.base]])
for name in R:
    if name == a.base:
        continue
    xb = np.array([x[0] for x in R[name]])
    d = xb.mean() - xa.mean(); thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    print(f'{name} - {a.base} | E1 relF1@2 | {name} {xb.mean():.4f}±{xb.std(ddof=1):.4f} | {a.base} {xa.mean():.4f}±{xa.std(ddof=1):.4f} | '
          f'delta {d:+.4f} | thr {thr:.4f} | {"BETTER" if d > thr else ("WORSE" if d < -thr else "n.d.")}')
