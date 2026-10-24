import csv,os,numpy as np
from PIL import Image
from scipy import ndimage
E='/home/yugma/mtp/datasets/escdd_full'
def find(st):
  for sp in ['train','val','test']:
    p=f'{E}/el_images_{sp}/{st}.png'
    if os.path.exists(p): return p
  for sp in ['train','val','test']:
    p=f'/home/yugma/mtp/datasets/BenchmarkEL_releases/dataset_20221008/el_images_{sp}/{st}.png'
    if os.path.exists(p): return p
def img(p):
  a=np.asarray(Image.open(p).convert('L').resize((128,128),Image.BILINEAR),np.float32)
  h=a-ndimage.gaussian_filter(a,3);h=(h-h.mean())/(h.std()+1e-6);return h.ravel()
el=[l.split('\t')[0] for l in open('/home/yugma/mtp/research/team_2026-10-24_go/trackM/mc_data/escdd_extra_train_eligible.tsv').read().split('\n')[1:] if l]
e1=[r['stem'] for r in csv.DictReader(open('/home/yugma/mtp/research/results/e1/ext117_manifest.csv')) if r['in_external_pool']=='0']
A={s:img(find(s)) for s in el};B={s:img(find(s)) for s in e1 if find(s)}
print('missing e1',len(e1)-len(B))
X=np.stack(list(A.values()));Y=np.stack(list(B.values()));R=X@Y.T/X.shape[1]
ka=list(A);kb=list(B)
idx=np.dstack(np.unravel_index(np.argsort(-R.ravel())[:15],R.shape))[0]
for i,j in idx: print(round(R[i,j],3),ka[i],kb[j])
print('E1 cells with max r>=0.93:',sum(R.max(0)>=0.93),' >=0.9:',sum(R.max(0)>=0.9))
