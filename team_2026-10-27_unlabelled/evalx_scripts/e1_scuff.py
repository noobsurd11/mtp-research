"""evalx Q5b: E1 crack recall in cells that contain classes ignored by E1 (25 scuff, 26 corrosion cell, 27 brightening,
28 star) vs cells without. Flags from results/e1/raw_v2 ext 'ignored_px'; class identity from 20221008 masks."""
import json, glob
import numpy as np
from PIL import Image
R = '/home/yugma/mtp/research/results/e1/raw_v2/'
D = '/home/yugma/mtp/datasets/BenchmarkEL_releases/dataset_20221008/'
TM = '/home/yugma/mtp/research/team_2026-10-24_go/trackM/'
ref = json.load(open(R + 'p6_L3_100pct_s0.json'))['cells']['ext']
cls = {}
for s in ref:
    f = [x for x in glob.glob(D + 'el_masks_*/' + s + '.png') if 'rgb' not in x]
    m = np.array(Image.open(f[0])) if f else None
    cls[s] = {int(c): int((m == c).sum()) for c in (25, 26, 27, 28)} if m is not None else None
ign = {s: ref[s].get('ignored_px', 0) > 0 for s in ref}
crack = {s: ref[s]['crack_gt'] for s in ref}
def runs(p): return [json.load(open(f))['cells']['ext'] for f in sorted(glob.glob(R + p + '_s*.json'))]
fin = json.load(open(TM + 'final/final_cells.json'))['ext']['final_b0.75']
def fin_counts(s):
    C = np.array(fin[s]['conf']).reshape(24, 24); return C[14, 14], C[14].sum(), C[:, 14].sum()
for grp, keep in [('cells with ignored class', lambda s: ign[s]), ('cells without', lambda s: not ign[s])]:
    cs = [s for s in ref if keep(s)]
    nc = sum(crack[s] > 0 for s in cs); g = sum(crack[s] for s in cs)
    which = {}
    for s in cs:
        if cls[s]:
            for c, v in cls[s].items():
                if v: which[c] = which.get(c, 0) + 1
    line = f'{grp}: cells {len(cs)}, crack cells {nc}, crack px {g} ({g / sum(crack.values()):.2f} of ext crack), ignored classes by cell count {which}'
    for name, p in [('A100', ['p6_L3_100pct', 'p16_A_100pct']), ('Sx100', ['p16_Sx_100pct']), ('A50', ['p16_A_50pct']), ('S50', ['p16_S_50pct'])]:
        rr = [r for q in p for r in runs(q)]
        rec = np.mean([sum(r[s]['crack_tp'] for s in cs) / max(g, 1) for r in rr])
        iou = np.mean([sum(r[s]['crack_tp'] for s in cs) / max(sum(r[s]['crack_gt'] + r[s]['crack_pred'] - r[s]['crack_tp'] for s in cs), 1) for r in rr])
        poi = np.mean([sum(r[s].get('crack_pred_on_ignored', 0) for s in cs) for r in rr])
        line += f' | {name} rec {rec:.3f} IoU {iou:.3f} pred-on-ignored {poi:.0f}'
    tp = sum(fin_counts(s)[0] for s in cs); gg = sum(fin_counts(s)[1] for s in cs); pp = sum(fin_counts(s)[2] for s in cs)
    line += f' | FINAL rec {tp / max(gg, 1):.3f} IoU {tp / max(gg + pp - tp, 1):.3f}'
    print(line)
print('total ignored px in ext', sum(ref[s].get('ignored_px', 0) for s in ref), 'cells', sum(ign.values()))

print('\n# split by scuff (class 25) present, among crack cells')
for grp, keep in [('scuff >= 500 px', lambda s: cls[s] and cls[s][25] >= 500), ('scuff < 500 px', lambda s: not (cls[s] and cls[s][25] >= 500))]:
    cs = [s for s in ref if keep(s) and crack[s] > 0]
    g = sum(crack[s] for s in cs)
    mods = sorted(set('_'.join(s.split('_')[:2]) for s in cs))
    line = f'{grp}: crack cells {len(cs)} in {len(mods)} modules, crack px {g} ({g / sum(crack.values()):.2f})'
    for name, p in [('A100', ['p6_L3_100pct', 'p16_A_100pct']), ('Sx100', ['p16_Sx_100pct']), ('A50', ['p16_A_50pct']), ('S50', ['p16_S_50pct']), ('A20', ['p6_L3_20pct', 'p16_A_20pct']), ('BsM20', ['p18_BsM_20pct'])]:
        rr = [r for q in p for r in runs(q)]
        rec = np.mean([sum(r[s]['crack_tp'] for s in cs) / max(g, 1) for r in rr])
        iou = np.mean([sum(r[s]['crack_tp'] for s in cs) / max(sum(r[s]['crack_gt'] + r[s]['crack_pred'] - r[s]['crack_tp'] for s in cs), 1) for r in rr])
        line += f' | {name} rec {rec:.3f} IoU {iou:.3f}'
    tp = sum(fin_counts(s)[0] for s in cs); gg = sum(fin_counts(s)[1] for s in cs); pp = sum(fin_counts(s)[2] for s in cs)
    rel = [fin[s]['crack_rel2'] for s in cs]; rR = sum(x[2] for x in rel) / max(sum(x[3] for x in rel), 1)
    gc = [c for s in cs for c in fin[s]['crack_cc']['gt'] if c[0] >= 20]
    line += f' | FINAL rec {tp / max(gg, 1):.3f} IoU {tp / max(gg + pp - tp, 1):.3f} relR@2 {rR:.3f} cc_rec {np.mean([c[1] >= 0.5 * c[0] for c in gc]):.3f} (n {len(gc)})'
    print(line)
