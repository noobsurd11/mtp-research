import os, numpy as np, collections
from PIL import Image
from scipy import ndimage as ndi
M=os.path.expanduser('~/mtp/research/team_2026-11-12_frontier/benchmark/out/masks_v11/masks')
SP=os.path.expanduser('~/mtp/datasets/splits_benchmark')
stems=[s.strip() for s in open(f'{SP}/train.txt') if s.strip()]
NONCELL=[1,2,3,5,6,7,8,21,22,255]
res=collections.defaultdict(list)
for s in stems:
    m=np.array(Image.open(f'{M}/{s}.png'))
    cell=~np.isin(m,NONCELL)
    lab,n=ndi.label(cell)
    if n==0: continue
    sz=ndi.sum(cell,lab,range(1,n+1)); k=int(np.argmax(sz))+1
    ys,xs=np.nonzero(lab==k)
    res[s[:4]].append((ys.max()-ys.min()+1, xs.max()-xs.min()+1, sz[k-1]))
for src,v in res.items():
    a=np.array(v); print(src,len(v),'median bbox h %d w %d, area %d px'%tuple(np.median(a,0)))
