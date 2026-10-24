import os,re,glob,csv,json,numpy as np
from PIL import Image
from scipy import ndimage
E='/home/yugma/mtp/datasets/escdd_full'; O='/home/yugma/mtp/datasets/BenchmarkELimages/dataset_20211104'
S='/home/yugma/mtp/datasets/splits_benchmark'
ours={sp:[l.strip() for l in open(f'{S}/{sp}.txt') if l.strip()] for sp in ['train','val','test']}
all582=set(sum(ours.values(),[]))
pool=set(l.strip() for l in open(f'{S}/external_unlabeled.txt') if l.strip())
pool={os.path.splitext(os.path.basename(p))[0] for p in pool}
e1={r['stem']:r for r in csv.DictReader(open('/home/yugma/mtp/research/results/e1/ext117_manifest.csv'))}
syn=re.compile(r'^\d+-.+_rf$')
cand=[]
for sp in ['train','val','test']:
  for f in sorted(os.listdir(f'{E}/el_images_{sp}')):
    st=f[:-4]
    if syn.match(st) or st in all582: continue
    cand.append((st,sp))
def key(st):
  s=st.replace('_rf','');p=s.split('_');return p[0],p[1],'_'.join(p[2:])
def img(path):
  a=np.asarray(Image.open(path).convert('L').resize((128,128),Image.BILINEAR),np.float32)
  h=a-ndimage.gaussian_filter(a,3); h=(h-h.mean())/(h.std()+1e-6); return h.ravel()
ref={}
for sp in ['val','test']:
  for st in ours[sp]: ref[st]=(sp,img(f'{O}/images_{sp}/{st}.png'))
rows=[]
for st,sp in cand:
  m=np.asarray(Image.open(f'{E}/el_masks_{sp}/{st}.png'))
  src,mod,pos=key(st)
  h=img(f'{E}/el_images_{sp}/{st}.png')
  best=max(((float(np.dot(h,v[1])/len(h)),r) for r,v in ref.items() if r.split('_')[0]==src),default=(0,''))
  samepos=[r for r in ref if key(r)[0]==src and key(r)[2]==pos]
  samemod=[r for r in ref if key(r)[0]==src and key(r)[1]==mod]
  rows.append(dict(stem=st,escdd_split=sp,src=src,rf=st.endswith('_rf'),in_pool=st.replace('_rf','') in pool or st in pool,
    in_e1=st in e1, crack=int((m==14).sum()),inact=int((m==11).sum()),best_r=round(best[0],3),best_ref=best[1],
    best_ref_split=ref[best[1]][0] if best[1] else '',samepos=';'.join(samepos),samemod=';'.join(samemod)))
w=csv.DictWriter(open('cand.csv','w'),fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
import collections as c
print(len(rows),c.Counter((r['rf'],r['in_pool'],r['in_e1']) for r in rows))
print('crack cells',sum(r['crack']>0 for r in rows),'inact cells',sum(r['inact']>0 for r in rows))
for r in sorted(rows,key=lambda r:-r['best_r'])[:25]: print(r['stem'],r['src'],r['crack'],r['inact'],r['best_r'],r['best_ref'],r['best_ref_split'],'|pos',r['samepos'],'|mod',r['samemod'])
print('samemod hits',[ (r['stem'],r['samemod']) for r in rows if r['samemod']])
