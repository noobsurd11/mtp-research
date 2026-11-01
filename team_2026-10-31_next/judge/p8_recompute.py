"""judge recompute of found's P8 probe F51 crack AP from per-cell histograms (run on gaint, el venv, CPU 1 thread).
Assumes per-cell 'crack' holds [pos_hist, neg_hist] over equal probability bins (checked by printing shapes).
AP = step-wise precision x delta-recall over bins in descending score order; pooled over F51 cells; mean of seeds."""
import numpy as np, json
d = json.loads(str(np.load('/home/noob/work/found/p8/run1/percell_hists.npz')['data']))
F51 = set(open('/home/noob/work/calib/data/rf/F51.txt').read().split()) if False else None
k0 = next(iter(d)); c0 = next(iter(d[k0].values()))
print('crack field type/len:', type(c0['crack']).__name__, [len(x) for x in c0['crack']] if isinstance(c0['crack'], list) else c0['crack'].keys())
sets = sorted(set(v['set'] for v in d[k0].values())); print('sets:', sets)
def ap(pos, neg):
    pos = np.asarray(pos, float)[::-1]; neg = np.asarray(neg, float)[::-1]
    tp = np.cumsum(pos); fp = np.cumsum(neg); P = tp / np.maximum(tp + fp, 1); R = tp / max(pos.sum(), 1)
    return float(np.sum(P * np.diff(np.concatenate([[0], R]))))
res = {}
for run, cells in d.items():
    enc = run.split('/')[0]
    for st in sets:
        cs = [v for v in cells.values() if v['set'] == st]
        pos = np.sum([np.asarray(v['crack']['pos'], float) for v in cs], 0); neg = np.sum([np.asarray(v['crack']['neg'], float) for v in cs], 0)
        res.setdefault((enc, st), []).append(ap(pos, neg))
for (enc, st), v in sorted(res.items()):
    if 'F51' in st or st.lower().startswith('f51') or st == 'val': print(f'{enc:28s} {st:8s} AP mean {np.mean(v):.3f}  seeds ' + ' '.join(f'{x:.3f}' for x in v))
