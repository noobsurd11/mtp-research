"""coach (29 Oct, respawn): MIM5 file checks before coach_verify.py. Independent of runner's analysis code.
Usage: python -I coach_mim5_checks.py <raw dir = results/mim5/raw>
Checks per run (A5c-f1 s0-4, MIM5 s0-4): m0 default / tau0 / tau1 JSONs exist; step 20000; code_revision 603e0d5;
cells val 54 / test 50 / ext 106, same stems in every file; tau0 cells == default cells (own check);
cross-check: test crack IoU, crack relF1@2, inactive IoU pooled from m0 cells vs the run's rescore JSON (new_escdd)."""
import json, os, sys
import numpy as np

NC, CR, IN = 24, 14, 11
raw = sys.argv[1]
RUNS = [f'f1_{a}_5pct_s{k}' for a in ('A', 'MIM') for k in range(5)]
bad = []


def pooled(cells):
    C = np.zeros((NC, NC)); x = np.zeros(4)
    for c in cells.values():
        C += np.asarray(c['conf'], float).reshape(NC, NC); x += np.asarray(c['crack_rel2'], float)
    tp = np.diag(C); g = C.sum(1); p = C.sum(0)
    iou = tp / np.maximum(g + p - tp, 1)
    rp, rr = x[0] / max(x[1], 1), x[2] / max(x[3], 1)
    return iou[CR], 2 * rp * rr / max(rp + rr, 1e-12), iou[IN]


ref = None
for r in RUNS:
    D = {}
    for tag, fn in (('def', f'{r}.json'), ('tau0', f'{r}.tau0.json'), ('tau1', f'{r}.tau1.json')):
        f = os.path.join(raw, 'm0', fn)
        if not os.path.exists(f):
            bad.append(f'{r} missing {fn}'); continue
        d = json.load(open(f)); D[tag] = d
        if d.get('step') != 20000 or d.get('weights') != 'model': bad.append(f'{fn} step {d.get("step")} weights {d.get("weights")}')
        if not str(d.get('code_revision', '')).startswith('603e0d5'): bad.append(f'{fn} rev {d.get("code_revision")}')
        n = {k: len(d['cells'].get(k, {})) for k in ('val', 'test', 'ext')}
        if n != {'val': 54, 'test': 50, 'ext': 106}: bad.append(f'{fn} cells {n}')
        stems = {k: sorted(d['cells'].get(k, {})) for k in ('val', 'test', 'ext')}
        ref = ref or stems
        if stems != ref: bad.append(f'{fn} stems differ')
    if 'def' in D and 'tau0' in D and D['def']['cells'] != D['tau0']['cells']:
        bad.append(f'{r} tau0 != default')
    rf = os.path.join(raw, 'rescore', f'{r}.json')
    if 'def' in D and os.path.exists(rf):
        v = json.load(open(rf))[f'test/{r}']['new_escdd']
        mine = pooled(D['def']['cells']['test'])
        theirs = (v['crack']['iou'], v['crack']['rel_f1_2'], v['inactive']['iou'])
        dif = max(abs(a - b) for a, b in zip(mine, theirs))
        print(f'{r} m0-vs-rescore max|diff| {dif:.5f}', 'OK' if dif < 1e-4 else 'MISMATCH')
        if dif >= 1e-4: bad.append(f'{r} m0 vs rescore {dif:.4f}')
    else:
        bad.append(f'{r} no rescore json')
print('FILE CHECKS', 'OK' if not bad else 'FAIL')
for b in bad: print('  ', b)
