# judge: cross-tab of E1 crack cells by scuff (class 25, 20221008 mask), half-cut multi (class 29, E-SCDD mask),
# and letterbox (white rows in image). FINAL b0.75 recall per group. Train counts of class 29 too.
import json, glob, os, numpy as np
from PIL import Image
D='/home/yugma/mtp/datasets/BenchmarkEL_releases/dataset_20221008/'
E=os.path.expanduser('~/mtp/datasets/escdd_full/')
F='/home/yugma/mtp/research/team_2026-10-24_go/trackM/final/final_cells.json'
m20={os.path.basename(p)[:-4]:p for p in glob.glob(D+'el_masks_*/*.png') if 'rgb' not in p}
i20={os.path.basename(p)[:-4]:p for p in glob.glob(D+'el_images_*/*.png')}
mes={os.path.basename(p)[:-4]:p for p in glob.glob(E+'el_masks_*/*.png')}
fin=json.load(open(F))['ext']['final_b0.75']
def letterbox(s):
    a=np.asarray(Image.open(i20[s]).convert('L')).astype(float)
    rows=(a.mean(1)>245).sum(); return rows>=32
groups={}
tot=0
for s,v in fin.items():
    C=np.array(v['conf']).reshape(24,24); g=C[14].sum(); tp=C[14,14]
    if g<20: continue
    m=np.array(Image.open(m20[s])); sc=(m==25).sum()>=500
    hc= s in mes and (np.array(Image.open(mes[s]))==29).any()
    lb=letterbox(s)
    k=(f'scuff={int(sc)}',f'halfcut={int(hc)}',f'letterbox={int(lb)}')
    a=groups.setdefault(k,[0,0,0]); a[0]+=1; a[1]+=g; a[2]+=tp; tot+=g
for k,(n,g,tp) in sorted(groups.items()):
    print(k, f'cells {n} crack px {g} ({g/tot:.2f}) recall {tp/g:.3f}')
# class 29 and letterbox in train
SP='/home/yugma/mtp/datasets/splits_benchmark/'
tr=[os.path.basename(l.strip()).replace('.png','') for l in open(SP+'train.txt') if l.strip()]
n29=sum(1 for s in tr if s in mes and (np.array(Image.open(mes[s]))==29).any())
nlb=sum(1 for s in tr if s in i20 and letterbox(s))
print('train cells with class 29:', n29, '| train cells letterboxed (>=32 white rows, 20221008 image):', nlb, '| train in E-SCDD', sum(s in mes for s in tr))
