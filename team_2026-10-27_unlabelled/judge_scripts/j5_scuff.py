# judge: independent check of evalx's E1 scuff claim, and how much scuff exists in our train/test (20221008 masks).
import json, glob, os, numpy as np
from PIL import Image
D='/home/yugma/mtp/datasets/BenchmarkEL_releases/dataset_20221008/'
F='/home/yugma/mtp/research/team_2026-10-24_go/trackM/final/final_cells.json'
SP='/home/yugma/mtp/datasets/splits_benchmark/'
msk={os.path.basename(p)[:-4]:p for p in glob.glob(D+'el_masks_*/*.png') if 'rgb' not in p}
def cnt(s,c):
    if s not in msk: return None
    m=np.array(Image.open(msk[s])); 
    return int((m==c).sum())
fin=json.load(open(F))
ext=fin['ext']['final_b0.75']
vals=set()
s0=list(ext)[0]; vals=np.unique(np.array(Image.open(msk[s0]))); print('mask values example', vals[:30])
rows=[]
for s in ext:
    C=np.array(ext[s]['conf']).reshape(24,24); g=C[14].sum(); tp=C[14,14]
    rows.append((s,cnt(s,25),cnt(s,14),g,tp))
for thr in [1,500]:
    a=[r for r in rows if r[3]>0 and r[1]>=thr]; b=[r for r in rows if r[3]>0 and r[1]<thr]
    G=sum(r[3] for r in rows)
    for name,x in [(f'scuff>={thr}',a),(f'scuff<{thr}',b)]:
        g=sum(r[3] for r in x); tp=sum(r[4] for r in x)
        print(f'E1 {name}: crack cells {len(x)}, crack px {g} ({g/G:.2f}), FINAL b0.75 recall {tp/g:.3f}')
print('E1 cells with any scuff', sum(1 for r in rows if r[1]), 'of', len(rows))
for split in ['train','test','val']:
    st=[os.path.basename(l.strip()).replace('.png','') for l in open(SP+split+'.txt') if l.strip()]
    sc=[(s,cnt(s,25)) for s in st]; miss=sum(1 for s,c in sc if c is None)
    w=[(s,c) for s,c in sc if c]
    wc=[s for s,c in w if (cnt(s,14) or 0)>0]
    print(f'{split}: {len(st)} cells, missing in release {miss}, cells with scuff {len(w)} (with crack too {len(wc)}), scuff px {sum(c for s,c in w)}', [s for s,_ in w][:8])
