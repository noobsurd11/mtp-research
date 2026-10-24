import json,numpy as np,sys
from mc_score import pool,met,SETS,NC
M='../m0/';runs={'A100':['p6_L3_100pct_s0','p6_L3_100pct_s1','p6_L3_100pct_s2','p16_A_100pct_s3','p16_A_100pct_s4'],
 'Sx100':['p16_Sx_100pct_s%d'%i for i in range(5)]}
D={r:json.load(open(M+r+'.json')) for v in runs.values() for r in v}
for split in ['test','val','ext']:
  ref=D['p6_L3_100pct_s0']['cells'][split]
  ncell=np.zeros(NC)
  for s,c in ref.items(): ncell+=np.array(c['conf']).reshape(NC,NC).sum(1)>0
  gt=ncell>0; rob=ncell>=3 if split=='test' else None
  if split=='test': ROB=rob; print('robust classes',np.where(ROB)[0].tolist())
  for arm,rs in runs.items():
    print(f'== {arm} {split}')
    for sn in ['all','noNoisy','noTwins','noBoth','CFVS','BMRK','ARTS','CSIR']:
      if split!='test' and sn!='all': continue
      vals={}
      for r in rs:
        C,rr=pool(D[r]['cells'][split],SETS[sn]);m=met(C,rr,gt)
        iou=m['iou'];m['miou_rob']=np.nanmean(np.where(ROB,iou,np.nan)) 
        for k in ['crack_iou','crack_P','crack_R','relR2','relF1','inact_iou','inact_P','inact_R','miou_gt','miou_rob']: vals.setdefault(k,[]).append(m[k])
      print(f'  {sn:8s}'+' '.join(f'{k} {np.mean(v):.3f}±{np.std(v,ddof=1):.3f}' for k,v in vals.items()))
# p-bands on test GT crack, pooled cells, mean over runs
for arm,rs in runs.items():
  for split in ['test','ext']:
    B=[];N=[]
    for r in rs:
      cc=D[r]['cells'][split];b=np.sum([c['crack_pband_gt'] for c in cc.values()],0);n=np.sum([c['crack_pband_neg'] for c in cc.values()],0)
      B.append(b/b.sum());N.append(n)
    print(arm,split,'GT-crack share by p band <.001,.001-.1,.1-.5,.5-.95,>=.95:',np.round(np.mean(B,0),3),' neg px in middle bands',np.mean(N,0)[1:4].round(0))
