import numpy as np,os
exec(open('leak.py').read().split('rows=[]')[0])
tr={st:img(f'{O}/images_train_original/{st}.png') for st in ours['train']}
twins={'CFVS_00006_r5_c5','CFVS_00033_r8_c4','CFVS_00035_r8_c4','CFVS_00042_r8_c4','CFVS_00018_r4_c4','CFVS_00027_r4_c4','ARTS_00020_r5_c1'}
import collections as c
by=c.defaultdict(list)
for r,(sp,v) in ref.items():
  if sp!='test':continue
  src=r.split('_')[0]
  b=max((float(np.dot(v,w)/len(v)),t) for t,w in tr.items() if t.startswith(src))
  by[src].append((round(b[0],3),r,b[1],r in twins))
for s,l in by.items():
  l.sort(reverse=True); print(s,l[:6]); print('   median',np.median([x[0] for x in l]))
