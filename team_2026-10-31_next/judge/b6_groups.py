#!/usr/bin/env python3
"""judge helper (1 Nov): physical-module groups for protocol_B6 from b6_audit.py outputs.
Edge rule (S, judge): same image id; OR same source + same (r, c) + different image id with
inactive-mask IoU >= 0.2 or crack-mask IoU >= 0.2 (defect geometry is cell-specific); OR, for CFVS
only (a time series of the same modules, decision.md D6), hp_r >= 0.90 at the same position.
Groups = connected components. Prints how much of the inactive pool sits in multi-image groups.
Usage: python b6_groups.py OUT_DIR"""
import sys, collections
OUT = sys.argv[1]
cells = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/b6_cells.tsv')][1:]
par = {}
def f(x):
    par.setdefault(x, x)
    while par[x] != x: par[x] = par[par[x]]; x = par[x]
    return x
def u(a, b): par[f(a)] = f(b)
mod = {c[0]: c[3] for c in cells}
for c in cells: f(c[3])
edges = []
for l in list(open(f'{OUT}/b6_neardup.tsv'))[1:]:
    r, a, asp, b, bsp, ia, ib, iiou, ca, cb, ciou = l.rstrip('\n').split('\t')
    r = float(r); iiou = float(iiou); ciou = float(ciou)
    same_pos = not a.startswith(('BMRK', 'SDLE'))
    if a.startswith(('BMRK', 'SDLE')): continue  # decision.md D6: BMRK/SDLE high scores are different cells (judge visual 1 Nov: BMRK_00222/01660 differ)
    hit = (iiou >= 0.2) or (ciou >= 0.2) or (a.startswith('CFVS') and r >= 0.90)
    if hit:
        edges.append((r, a, b, iiou, ciou)); u(mod[a], mod[b])
# decision.md D6 known twins / early stages (train+val only), added regardless of the screen
for a, b in [('CFVS_00032_r8_c4', 'CFVS_00037_r8_c4'), ('CFVS_00017_r4_c4', 'CFVS_00031_r4_c4'),
             ('CFVS_00009_r7_c4', 'CFVS_00012_r7_c4'), ('ARTS_00061_r1_c6', 'ARTS_00040_r1_c6')]:
    if a in mod and b in mod: u(mod[a], mod[b]); edges.append((None, a, b, None, None))
print('twin edges', len(edges))
grp = collections.defaultdict(list)
for c in cells: grp[f(c[3])].append(c)
multi = {g: v for g, v in grp.items() if len({c[3] for c in v}) > 1}
print('groups', len(grp), 'vs B6 modules', len({c[3] for c in cells}), '; multi-image groups', len(multi))
tot = sum(int(c[5]) for c in cells)
in_multi = sum(int(c[5]) for v in multi.values() for c in v)
print(f'inactive px in multi-image groups {in_multi} / {tot} = {in_multi/tot:.3f}; inactive cells',
      sum(int(c[5]) > 0 for v in multi.values() for c in v), '/', sum(int(c[5]) > 0 for c in cells))
print('largest groups (cells, images, inactive px, splits):')
for g, v in sorted(grp.items(), key=lambda kv: -len(kv[1]))[:8]:
    print(' ', len(v), len({c[3] for c in v}), sum(int(c[5]) for c in v), collections.Counter(c[1] for c in v), sorted({c[3] for c in v})[:8])
print('multi-image groups with inactive:')
for g, v in multi.items():
    ip = sum(int(c[5]) for c in v)
    if ip: print(' ', sorted({c[3] for c in v}), 'cells', len(v), 'inactive px', ip, dict(collections.Counter(c[1] for c in v)))
# power proxies: inactive px weight per group
w = collections.Counter()
for c in cells: w[f(c[3])] += int(c[5])
w = sorted([v for v in w.values() if v], reverse=True)
neff = sum(w) ** 2 / sum(v * v for v in w)
print('inactive groups', len(w), '; n_eff (px-weighted) %.1f' % neff, '; group top-3 share %.3f' % (sum(w[:3]) / sum(w)))
wm = collections.Counter()
for c in cells: wm[c[3]] += int(c[5])
wm = sorted([v for v in wm.values() if v], reverse=True)
print('  for comparison, B6 v0 key: inactive modules', len(wm), 'n_eff %.1f' % (sum(wm) ** 2 / sum(v * v for v in wm)))
with open(f'{OUT}/b6_groups.tsv', 'w') as fo:
    fo.write('stem\tsplit\tb6_module\tphys_group\tinactive_px\tcrack_px\n')
    for c in cells: fo.write(f'{c[0]}\t{c[1]}\t{c[3]}\t{f(c[3])}\t{c[5]}\t{c[6]}\n')
