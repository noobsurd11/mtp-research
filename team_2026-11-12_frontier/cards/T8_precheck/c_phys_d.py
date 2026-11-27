# T8 pre-check C-PHY and C-INT (P532 only: legacy train + val; never test/E1)
import sys, os, numpy as np
from PIL import Image
from scipy import ndimage as ndi
B=os.path.expanduser('~/mtp/datasets/BenchmarkELimages/dataset_20211104')
M=os.path.expanduser('~/mtp/research/team_2026-11-12_frontier/benchmark/out/masks_v11/masks')
SP=os.path.expanduser('~/mtp/datasets/splits_benchmark')
stems=[(s.strip(),'train') for s in open(f'{SP}/train.txt') if s.strip()]+[(s.strip(),'val') for s in open(f'{SP}/val.txt') if s.strip()]
NONCELL={1,2,3,4,5,6,7,8,9,21,22,255}
rows=[]
st=np.ones((3,3),bool)
for s,sp in stems:
    m=np.array(Image.open(f'{M}/{s}.png'))
    d='images_train_original' if sp=='train' else 'images_val'
    im=np.array(Image.open(f'{B}/{d}/{s}.png').convert('L')).astype(float)
    crack=m==14; ina=m==11; coll=(m==4)|(m==9)
    src=s[:4]
    act=m==0
    rec={'stem':s,'src':src,'crack':int(crack.sum()),'ina':int(ina.sum()),'coll':int(coll.sum())}
    if ina.sum()>0 and act.sum()>500:
        rec['ratio']=float(np.median(im[ina])/max(np.median(im[act]),1e-6))
    if crack.sum()>=20 and coll.sum()>0:
        cell=~np.isin(m,list(NONCELL))
        cd=ndi.binary_dilation(crack,st,iterations=int(os.environ.get("DIL","1")))
        free=cell & ~cd
        lab,n=ndi.label(free)
        touchc=ndi.binary_dilation(cd,st,iterations=1)
        touchb=ndi.binary_dilation(coll,st,iterations=2)
        iso=np.zeros_like(crack)
        for k in range(1,n+1):
            comp=lab==k
            if (comp&touchc).any() and not (comp&touchb).any() and comp.sum()>=50:
                iso|=comp
        rec['iso']=int(iso.sum()); rec['cellpx']=int(cell.sum())
        if ina.sum()>0:
            inter=(iso&ina).sum(); rec['iou']=float(inter/((iso|ina).sum())); rec['rec']=float(inter/ina.sum()); rec['prec']=float(inter/max(iso.sum(),1))
    rows.append(rec)
import json
json.dump(rows,open(sys.argv[1],'w'))
ina=[r for r in rows if r['ina']>0]
print('P532 cells',len(rows),'inactive cells',len(ina))
rat=[r['ratio'] for r in ina if 'ratio' in r]
print('inactive/active median intensity ratio: median %.3f IQR %.3f-%.3f n=%d'%(np.median(rat),*np.percentile(rat,[25,75]),len(rat)))
for src in ['ARTS','CFVS','CSIR','BMRK']:
    rr=[r['ratio'] for r in ina if 'ratio' in r and r['src']==src]
    if rr: print('  ',src,len(rr),'median %.3f'%np.median(rr))
ev=[r for r in ina if 'iou' in r]
print('inactive cells evaluable by rule (crack>=20 & ribbon/busbar present):',len(ev))
if ev:
    I=sum((r['rec']*r['ina']) for r in ev); A=sum(r['ina'] for r in ev); P=sum(r['iso'] for r in ev)
    print('  pooled recall of inactive px by isolation rule %.3f, pooled precision %.3f'%(I/A, I/max(P,1)))
    print('  per-cell IoU median %.3f; cells with IoU>=0.5: %d'%(np.median([r['iou'] for r in ev]), sum(r['iou']>=0.5 for r in ev)))
    print('  cells where rule finds any isolated area: %d'%sum(r['iso']>0 for r in ev))
co=[r for r in rows if r['ina']==0 and 'iso' in r]
fire=[r for r in co if r['iso']>=0.005*r['cellpx']]
print('crack cells without inactive, evaluable:',len(co),'; rule isolates >=0.5%% of cell area in %d'%len(fire))
from collections import Counter
print('  by source',Counter(r['src'] for r in fire), 'of', Counter(r['src'] for r in co))
print('  isolated area share (median among firing) %.3f'%(np.median([r['iso']/r['cellpx'] for r in fire]) if fire else 0))
