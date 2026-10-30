"""coach (30 Oct): file checks for an f2 arm before coach_verify.py (generalises coach_mim5_checks.py).
Usage: python -I coach_f2_checks.py <raw dir> <rev prefix> <run> [<run> ...]
Per run: m0 default / tau0 / tau1 JSONs; step 20000, weights 'model', code_revision prefix; cells val 54 / test 50 / ext 106
with the same stems as the A5c-f1 files (results/mim5/coach_raw); tau0 == default; pooled test crack IoU, relF1@2,
inactive IoU from m0 cells == the run's rescore JSON (new_escdd), and tau1 cells == la.json tau1."""
import json, os, sys
import numpy as np

NC, CR, IN = 24, 14, 11
raw, rev, RUNS = sys.argv[1], sys.argv[2], sys.argv[3:]
REF = json.load(open('results/mim5/coach_raw/m0/f1_A_5pct_s0.json'))['cells']
ref = {k: sorted(REF[k]) for k in ('val', 'test', 'ext')}
bad = []


def pooled(cells):
    C = np.zeros((NC, NC)); x = np.zeros(4)
    for c in cells.values():
        C += np.asarray(c['conf'], float).reshape(NC, NC); x += np.asarray(c['crack_rel2'], float)
    tp = np.diag(C); g = C.sum(1); p = C.sum(0)
    iou = tp / np.maximum(g + p - tp, 1)
    rp, rr = x[0] / max(x[1], 1), x[2] / max(x[3], 1)
    return np.array([iou[CR], 2 * rp * rr / max(rp + rr, 1e-12), iou[IN]])


la = json.load(open(os.path.join(raw, 'la.json'))) if os.path.exists(os.path.join(raw, 'la.json')) else {}
for r in RUNS:
    D = {}
    for tag, fn in (('def', f'{r}.json'), ('tau0', f'{r}.tau0.json'), ('tau1', f'{r}.tau1.json')):
        f = os.path.join(raw, 'm0', fn)
        if not os.path.exists(f):
            bad.append(f'{r} missing {fn}'); continue
        d = json.load(open(f)); D[tag] = d
        if d.get('step') != 20000 or d.get('weights') != 'model': bad.append(f'{fn} step {d.get("step")} weights {d.get("weights")}')
        if not str(d.get('code_revision', '')).startswith(rev): bad.append(f'{fn} rev {d.get("code_revision")}')
        if {k: sorted(d['cells'].get(k, {})) for k in ('val', 'test', 'ext')} != ref: bad.append(f'{fn} stems differ from A5c-f1')
    if 'def' in D and 'tau0' in D and D['def']['cells'] != D['tau0']['cells']:
        bad.append(f'{r} tau0 != default')
    rf = os.path.join(raw, 'rescore', f'{r}.json')
    if 'def' in D and os.path.exists(rf):
        v = json.load(open(rf))[f'test/{r}']['new_escdd']
        dif = np.abs(pooled(D['def']['cells']['test']) - [v['crack']['iou'], v['crack']['rel_f1_2'], v['inactive']['iou']]).max()
        print(f'{r} m0-vs-rescore max|diff| {dif:.2e}', 'OK' if dif < 1e-4 else 'MISMATCH')
        if dif >= 1e-4: bad.append(f'{r} m0 vs rescore {dif:.4f}')
    else:
        bad.append(f'{r} no rescore json')
    k = f'test/{r}/tau1'
    if 'tau1' in D and k in la:
        v = la[k]['new_escdd']
        dif = np.abs(pooled(D['tau1']['cells']['test']) - [v['crack']['iou'], v['crack']['rel_f1_2'], v['inactive']['iou']]).max()
        print(f'{r} tau1-vs-la max|diff| {dif:.2e}', 'OK' if dif < 1e-4 else 'MISMATCH')
        if dif >= 1e-4: bad.append(f'{r} tau1 vs la {dif:.4f}')
    else:
        bad.append(f'{r} no la tau1')
print('FILE CHECKS', 'OK' if not bad else 'FAIL')
for b in bad: print('  ', b)
