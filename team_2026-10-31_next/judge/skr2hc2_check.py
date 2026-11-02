#!/usr/bin/env python3
"""judge skr2hc2_check (2 Nov 2026): numbers for the protocol_SKR2_HC2 v0.9 review (stdlib only; opened files only).
1. per-seed test inactive IoU, test relP@2 (argmax), E1 crack px on crack-free cells, E1 any-hit (GT comps >= 20 px, hit >= 1),
   for SUPPF s5-9 (PF2), HC s5-9, SKR w1.0 s5-9, CLD s5-9 (THIN): sds and null trip rates of G1 / G2.
2. HC opening records at b 0 (el_metrics format): inactive IoU per seed on val (V0), SHV1 (synval), F51, F19, H36 for SUPPF and HC.
Usage: python3 skr2hc2_check.py ROOT (team folder)"""
import json, math, sys
from statistics import mean, stdev
R = sys.argv[1]
RFSET = {}
for l in list(open(f'{R}/judge/out/rf_sets.tsv'))[1:]:
    x = l.rstrip('\n').split('\t'); RFSET.setdefault(x[1], set()).add(x[0])
M0 = {'SUPPF': (f'{R}/results/pf2/raw/m0', 'pf2'), 'HC': (f'{R}/results/hc/raw/m0', 'hc'),
      'SKR': (f'{R}/results/thin/raw/m0', 'thin'), 'CLD': (f'{R}/results/thin/raw/m0', 'thin')}
NC, CR, IN = 24, 14, 11


def conf(c):
    m = c['conf']; n = int(math.isqrt(len(m)))
    return [m[i * n:(i + 1) * n][:24] for i in range(24)]


def stats(cells, stems):
    tp = fp = fn = 0; rp = [0, 0, 0, 0]; free = 0; gc = []
    for s in stems:
        c = cells[s]; M = conf(c)
        tp += M[IN][IN]; fp += sum(M[r][IN] for r in range(24)) - M[IN][IN]; fn += sum(M[IN]) - M[IN][IN]
        rp = [a + b for a, b in zip(rp, c['crack_rel2'])]
        if sum(M[CR]) == 0:
            free += sum(M[r][CR] for r in range(24))
        gc += [g for g in c['crack_cc']['gt'] if g[0] >= 20]
    return dict(inact=tp / max(tp + fp + fn, 1), relP=rp[0] / max(rp[1], 1), free=free, anyhit=sum(g[1] >= 1 for g in gc) / max(len(gc), 1), ngc=len(gc))


V = {}
for arm, (d, p) in M0.items():
    rows = []
    for k in range(5, 10):
        c = json.load(open(f'{d}/{p}_{arm}_100pct_s{k}.json'))['cells']
        t = sorted(c['test']); tc = [s for s in t if s != 'CSIR_00070_r8_c4']; e = sorted(c['ext'])
        rows.append((stats(c['test'], t), stats(c['test'], tc), stats(c['ext'], e)))
    V[arm] = rows
    f = lambda i, k: [r[i][k] for r in rows]
    print(f"{arm:5s} test inact all {[round(x, 4) for x in f(0, 'inact')]} sd {stdev(f(0, 'inact')):.4f} | clean sd {stdev(f(1, 'inact')):.4f} | "
          f"test relP@2 mean {mean(f(0, 'relP')):.4f} sd {stdev(f(0, 'relP')):.4f} | E1 crack-free px {f(2, 'free')} mean {mean(f(2, 'free')):.0f} "
          f"| E1 any-hit {[round(x, 3) for x in f(2, 'anyhit')]} mean {mean(f(2, 'anyhit')):.4f} (comps {V[arm][0][2]['ngc']})")

Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
sA = stdev([r[0]['inact'] for r in V['SUPPF']])
for lab, sB in (('pooled SUPPF/HC sd', math.sqrt((sA ** 2 + stdev([r[0]['inact'] for r in V['HC']]) ** 2) / 2)), ('SUPPF sd both arms', sA)):
    se = sB * math.sqrt(2 / 5)
    print(f"G1 (d <= -0.015), {lab} {sB:.4f}: SE of d {se:.4f}; null trip {Phi(-0.015 / se):.3f}; power at -0.023 {Phi((0.023 - 0.015) / se):.3f}; at -0.030 {Phi((0.030 - 0.015) / se):.3f}")
fr = [r[2]['free'] for r in V['SUPPF']]
print(f"G2 E1 crack-free px: SUPPF per seed {fr} cv {stdev(fr) / mean(fr):.3f}; 1.5x bar {1.5 * mean(fr):.0f}; "
      f"approx null trip (normal, 5-seed mean, same sd) {1 - Phi((0.5 * mean(fr)) / (stdev(fr) / math.sqrt(5))):.4f}")
rp = [r[0]['relP'] for r in V['SUPPF']]
print(f"G2 test relP@2: SUPPF sd {stdev(rp):.4f}; SE of d {stdev(rp) * math.sqrt(2 / 5):.4f}; null trip at -0.03 {Phi(-0.03 / (stdev(rp) * math.sqrt(2 / 5))):.2e}")
for arm in ('HC', 'SKR', 'CLD'):
    d_all = mean(r[0]['inact'] for r in V[arm]) - mean(r[0]['inact'] for r in V['SUPPF'])
    d_cl = mean(r[1]['inact'] for r in V[arm]) - mean(r[1]['inact'] for r in V['SUPPF'])
    d_rp = mean(r[0]['relP'] for r in V[arm]) - mean(r[0]['relP'] for r in V['SUPPF'])
    x = mean(r[2]['free'] for r in V[arm]) / mean(fr)
    print(f"  {arm}: G1 d {d_all:+.4f} / {d_cl:+.4f} -> {'TRIP' if d_all <= -0.015 and d_cl <= -0.015 else 'ok'}; G2 relP d {d_rp:+.4f}, E1 free x{x:.2f} -> {'TRIP' if d_rp < -0.03 or x > 1.5 else 'ok'}")

print("\n## HC opening records, inactive IoU at b 0 per seed")
RS = f'{R}/results/hc/raw/shv1/rec'
def inact(cells, keep=None):
    tp = pr = gi = 0
    for s, c in cells.items():
        if keep is not None and s not in keep:
            continue
        tp += c['inact_tp'][J0]; pr += c['inact_pred'][J0]; gi += c['gt_inact']
    return tp / max(pr + gi - tp, 1)
for arm, pre in (('SUPPF', 'pf2_SUPPF'), ('HC', 'hc_HC')):
    out = {}
    for k in range(5, 10):
        for st in ('val', 'synval', 'rf'):
            d = json.load(open(f'{RS}/{pre}_100pct_s{k}.{st}.json'))
            J0 = min(range(len(d['grid'])), key=lambda i: abs(d['grid'][i]))
            if st == 'rf':
                for g in ('F51', 'F19', 'H36'):
                    out.setdefault(g, []).append(inact(d['cells'], RFSET[g]))
            else:
                out.setdefault(st, []).append(inact(d['cells']))
    print(arm, {k: ([round(x, 3) for x in v], round(mean(v), 4)) for k, v in out.items()})
