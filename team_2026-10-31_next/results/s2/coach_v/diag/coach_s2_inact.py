# coach (2 Nov 21:5x): where does HC2 lose inactive? (reported; descriptive). Per test inactive cell and per E1 source image.
import json, re, numpy as np
NC, CR, IN = 24, 14, 11
PF = '/home/noob/work/el_f3/reports/pf2/post/m0'; S2 = '/home/noob/work/s2q/post/m0'; HCM = '/home/noob/work/el_hc/reports/hc/post/m0'
ARMS = {'SUPPF': [f'{PF}/pf2_SUPPF_100pct_s{k}.json' for k in range(5, 10)], 'HC': [f'{HCM}/hc_HC_100pct_s{k}.json' for k in range(5, 10)],
        'HC2': [f'{S2}/HC2/hc2_HCig_100pct_s{k}.json' for k in range(5, 10)], 'SKR01': [f'{S2}/SKR01/skr2_SKR01_100pct_s{k}.json' for k in range(5, 10)]}
ctx = {l.split('\t')[0]: l.strip().split('\t')[1:] for l in open('/home/noob/work/coach_v/bin/e1_context.tsv') if l.strip()}
clu = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)
D = {a: [json.load(open(p))['cells'] for p in ps] for a, ps in ARMS.items()}
def inv(cells, keep):
    C = sum(np.asarray(c['conf'], float).reshape(NC, NC) for s, c in cells.items() if keep(s))
    return C[IN, IN], C[IN].sum(), C[:, IN].sum(), C[IN, CR]
for split in ('test', 'ext'):
    st = sorted(D['SUPPF'][0][split]); grp = sorted(set(clu(s) for s in st)) if split == 'ext' else st
    key = (lambda g: (lambda s: clu(s) == g)) if split == 'ext' else (lambda g: (lambda s: s == g))
    rows = []
    for g in grp:
        gt = inv(D['SUPPF'][0][split], key(g))[1]
        if gt == 0: continue
        r = {}
        for a in ARMS:
            v = [inv(c[split], key(g)) for c in D[a]]
            r[a] = (np.mean([x[0] / max(x[1] + x[2] - x[0], 1) for x in v]), np.mean([x[2] for x in v]), np.mean([x[3] for x in v]))
        tag = ','.join(sorted(set(' '.join(ctx.get(s, ['?'])) for s in st if key(g)(s)))) if split == 'ext' else ''
        rows.append((gt, g, r, tag))
    rows.sort(key=lambda x: -x[0])
    print(f'## {split}: units with GT inactive px: {len(rows)}; per unit inactive IoU (seed mean) | pred inactive px | GT-inactive px predicted crack')
    for a in ('HC', 'HC2', 'SKR01'):
        d = np.array([r[a][0] - r['SUPPF'][0] for _, _, r, _ in rows]); print(f'   {a} - SUPPF: {int((d < 0).sum())} / {len(d)} units down; median {np.median(d):+.3f}')
    d = np.array([r['HC2'][0] - r['HC'][0] for _, _, r, _ in rows]); print(f'   HC2 - HC: {int((d < 0).sum())} / {len(d)} units down; median {np.median(d):+.3f}')
    for gt, g, r, tag in rows[:12]:
        print(f'   {g:22s} gt {int(gt):7d} | ' + ' | '.join(f'{a} {r[a][0]:.3f} pred {r[a][1]:7.0f} in->cr {r[a][2]:6.0f}' for a in ('SUPPF', 'HC', 'HC2')) + (f' | {tag}' if tag else ''))
