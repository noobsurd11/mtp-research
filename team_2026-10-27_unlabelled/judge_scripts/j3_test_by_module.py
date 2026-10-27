# judge: within the 50-cell test, crack/inactive IoU and recall for cells whose module has train cells vs not.
# Uses Track M final_cells.json (24x24 confusion per cell, rows=GT, cols=pred assumed; checked by sums).
import json, statistics as st
F='/home/yugma/mtp/research/team_2026-10-24_go/trackM/final/final_cells.json'
SP='/home/yugma/mtp/datasets/splits_benchmark/'
def mod(s): return '_'.join(s.split('_')[:2])
train=[l.strip() for l in open(SP+'train.txt') if l.strip()]
tm={mod(s) for s in train}
d=json.load(open(F)); t=d['test']
print('test keys', list(t.keys()))
NOISY='CSIR_00070_r8_c4'
def stats(cells, cls, keys):
    tp=fp=fn=0
    for k in keys:
        c=cells[k]['conf']; n=24
        tp+=c[cls*n+cls]; g=sum(c[cls*n+j] for j in range(n)); p=sum(c[i*n+cls] for i in range(n))
        fn+=g-c[cls*n+cls]; fp+=p-c[cls*n+cls]
    return tp/(tp+fp+fn) if tp+fp+fn else float('nan'), tp/(tp+fn) if tp+fn else float('nan'), tp+fn
for arm in ['final_b0','final_b0.75']+[k for k in t if k.startswith('rec_single')]:
    cells=t[arm]; keys=[k for k in cells if k!=NOISY]
    seen=[k for k in keys if mod(k) in tm]; unseen=[k for k in keys if mod(k) not in tm]
    out=[]
    for name,ks in [('seen-mod',seen),('unseen-mod',unseen)]:
        ci,cr,cg=stats(cells,14,ks); ii,ir,ig=stats(cells,11,ks)
        out.append(f'{name} n={len(ks)} crackIoU={ci:.3f} R={cr:.3f} gt={cg} | inactIoU={ii:.3f} R={ir:.3f} gt={ig}')
    print(arm, ' || '.join(out))
# E1 for comparison
e=d['ext']; print('ext keys', list(e.keys())[:6])
for arm in ['final_b0','final_b0.75']:
    if arm in e:
        cells=e[arm]; keys=list(cells)
        ci,cr,cg=stats(cells,14,keys); print('E1',arm,f'crackIoU={ci:.3f} R={cr:.3f} gt={cg}')
# per-source in unseen-mod test
from collections import Counter
cells=t['final_b0']; keys=[k for k in cells if k!=NOISY]
print('unseen-mod by source', Counter(k.split('_')[0] for k in keys if mod(k) not in tm), 'seen-mod', Counter(k.split('_')[0] for k in keys if mod(k) in tm))
