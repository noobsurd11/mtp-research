"""coach (30 Oct): CP5 extras, independent of runner's code. Usage: python -I coach_cp5_extra.py <cp5 raw dir>
1) crack-claim rule (protocol_cp5): C1 BETTER on crack IoU or relF1@2 AND C2 BETTER on the same primary, worse on none,
   two-set rule (all + noNoisy), read from coach_verify outputs results/cp5/coach/verify_tau0.txt (C1) and verify_tau1.txt (C2);
2) predicted crack px on cells with no GT crack (test / val / ext), both arms, tau 0 and 1, from m0 confusions;
3) E3b decoy on final checkpoints (decoy_final.json), flag CP mean > 2x A5c-f1 mean or > 0.05 (reported)."""
import json, os, re, sys
import numpy as np

NC, CR = 24, 14
raw = sys.argv[1]; AM = 'results/mim5/coach_raw/m0'


def verdict(path):
    t = open(path).read()
    m = re.search(r"VERDICT (\S+) better=(\[.*?\]) worse=(\[.*?\])", t)
    return m.group(1), eval(m.group(2)), eval(m.group(3))


v1, b1, w1 = verdict('results/cp5/coach/verify_tau0.txt'); v2, b2, w2 = verdict('results/cp5/coach/verify_tau1.txt')
same = [k for k in ('crack', 'relF1') if k in b1 and k in b2]
claim = bool(same) and not w1 and not w2
print(f'C1 {v1} better={b1} worse={w1} | C2 {v2} better={b2} worse={w2} -> crack claim {"YES on " + str(same) if claim else "NO"}')
wf = re.findall(r'width relP@2 ([+-][0-9.]+) (\S+)', open('results/cp5/coach/verify_tau0.txt').read())
print('C1 width flag (all, noNoisy):', wf)

for split in ('test', 'val', 'ext'):
    for tau in ('', '.tau1'):
        row = []
        for lab, d, pfx in (('A5c-f1', AM, 'f1_A_5pct'), ('CP5', os.path.join(raw, 'm0'), 'f2_CP_5pct')):
            px = []
            for k in range(5):
                cells = json.load(open(f'{d}/{pfx}_s{k}{tau}.json'))['cells'][split]
                n = 0; fp = 0
                for c in cells.values():
                    C = np.asarray(c['conf'], float).reshape(NC, NC)
                    if C[CR].sum() == 0: n += 1; fp += C[:, CR].sum()
                px.append(int(fp))
            row.append(f'{lab} mean {np.mean(px):.0f} {px}')
        print(f'crack-free {split:4s} (n={n}) tau{1 if tau else 0}: ' + ' | '.join(row))

f = os.path.join(raw, 'decoy_final.json')
if os.path.exists(f):
    r = json.load(open(f))['runs']
    assert all(v['step'] == 20000 for v in r.values())
    A = [r[f'f1_A_5pct_s{k}'] for k in range(5)]; C = [r[f'f2_CP_5pct_s{k}'] for k in range(5)]
    for key in ('real', 'decoy', 'background'):
        print(f'E3b {key:10s} A5c-f1 {np.mean([a[key] for a in A]):.4f} | CP5 {np.mean([c[key] for c in C]):.4f}')
    ma, mc = np.mean([a['decoy'] for a in A]), np.mean([c['decoy'] for c in C])
    print('E3b decoy flag (CP > 2x A or > 0.05):', 'FLAG' if mc > 2 * ma or mc > 0.05 else 'no flag')
else:
    print('decoy_final.json missing')
