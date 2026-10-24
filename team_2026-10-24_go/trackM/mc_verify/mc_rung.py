"""MC rung verifier. python mc_rung.py --base f1,..,f5 --arm g1,..,g5 [--name R2]
Rule 1 on 4 primaries x {all, noNoisy}; val inclusion (crack, relF1, mIoU_rob val list); width flags;
paired image bootstrap (arm mean - base mean of pooled per-run IoU), leave-top-3-out; per source; per class."""
import argparse,json,numpy as np
from mc_score import NC,TWINS,NOISY
ap=argparse.ArgumentParser();ap.add_argument('--base');ap.add_argument('--arm');ap.add_argument('--boot',type=int,default=2000)
a=ap.parse_args()
TL=[0,1,2,4,5,7,11,13,14,15,16,20,21];VL=[0,1,2,4,5,7,9,11,13,14,15,16,21]
L=lambda s:[json.load(open(f)) for f in s.split(',')]
B,A=L(a.base),L(a.arm)
for d in A: assert d.get('step',20000)==20000,(d['run'],d.get('step'))
print('arm runs',[ (d['run'],d.get('code_revision')) for d in A])
def met(cells,keep,cls):
  C=np.zeros((NC,NC));x=np.zeros(4)
  for s,c in cells.items():
    if keep(s): C+=np.array(c['conf']).reshape(NC,NC);x+=c['crack_rel2']
  tp=np.diag(C);g=C.sum(1);p=C.sum(0);iou=np.where(g>0,tp/np.maximum(g+p-tp,1),np.nan)
  rp=x[0]/max(x[1],1);rr=x[2]/max(x[3],1)
  return dict(crack=iou[14],inact=iou[11],relF1=2*rp*rr/max(rp+rr,1e-12),miou=np.nanmean(iou[cls]),cP=tp[14]/max(p[14],1),cR=tp[14]/max(g[14],1),
              iP=tp[11]/max(p[11],1),iR=tp[11]/max(g[11],1),relP=rp,relR=rr,iou=iou,P=tp/np.maximum(p,1),R=tp/np.maximum(g,1))
def r1(xa,xb):
  sd=lambda x:np.std(x,ddof=1);thr=max(0.01,2*np.sqrt((sd(xa)**2+sd(xb)**2)/3));d=np.mean(xb)-np.mean(xa)
  return d,thr,('BETTER' if d>thr else 'WORSE' if d<-thr else 'nd')
SETS={'all':lambda s:True,'noNoisy':lambda s:s!=NOISY,'noTwins':lambda s:s not in TWINS,'noBoth':lambda s:s!=NOISY and s not in TWINS}
for q in ['CFVS','BMRK','ARTS','CSIR']: SETS[q]=(lambda q:lambda s:s.startswith(q))(q)
PR=['crack','inact','relF1','miou']
for sn,f in SETS.items():
  mb=[met(d['cells']['test'],f,TL) for d in B];ma=[met(d['cells']['test'],f,TL) for d in A]
  print(f'TEST {sn:8s}',' | '.join('%s %.4f->%.4f %+.4f(%.4f) %s'%((k,np.mean([m[k] for m in mb]),np.mean([m[k] for m in ma]))+r1([m[k] for m in mb],[m[k] for m in ma])) for k in PR))
  if sn in('all','noNoisy'):
    print('   width: dcP %+.3f diP %+.3f drelP %+.3f | cR %+.3f relR %+.3f iR %+.3f'%tuple(np.mean([m[k] for m in ma])-np.mean([m[k] for m in mb]) for k in ['cP','iP','relP','cR','relR','iR']))
# val inclusion
mb=[met(d['cells']['val'],SETS['all'],VL) for d in B];ma=[met(d['cells']['val'],SETS['all'],VL) for d in A]
print('VAL incl',' | '.join('%s %+.4f(%.4f) %s'%((k,)+r1([m[k] for m in mb],[m[k] for m in ma])) for k in ['crack','relF1','miou','inact']))
# per class test noNoisy
mb=[met(d['cells']['test'],SETS['noNoisy'],TL) for d in B];ma=[met(d['cells']['test'],SETS['noNoisy'],TL) for d in A]
print('per-class IoU/P/R noNoisy base->arm:')
for c in TL+[9,18]: print('  %2d IoU %.3f->%.3f P %.3f->%.3f R %.3f->%.3f'%(c,np.nanmean([m['iou'][c] for m in mb]),np.nanmean([m['iou'][c] for m in ma]),np.mean([m['P'][c] for m in mb]),np.mean([m['P'][c] for m in ma]),np.mean([m['R'][c] for m in mb]),np.mean([m['R'][c] for m in ma])))
# bootstrap + top3
stems=sorted(B[0]['cells']['test'])
def stack(D): return np.stack([[np.array(d['cells']['test'][s]['conf'],float).reshape(NC,NC) for s in stems] for d in D]),np.stack([[d['cells']['test'][s]['crack_rel2'] for s in stems] for d in D]).astype(float)
CB,XB=stack(B);CA,XA=stack(A)
def v(C,X):
  C=C.sum(1);X=X.sum(1);tp=np.einsum('rii->ri',C);g=C.sum(2);p=C.sum(1);iou=np.where(g>0,tp/np.maximum(g+p-tp,1),np.nan)
  rp=X[:,0]/np.maximum(X[:,1],1);rr=X[:,2]/np.maximum(X[:,3],1)
  return np.stack([iou[:,14],iou[:,11],2*rp*rr/np.maximum(rp+rr,1e-12),np.nanmean(iou[:,TL],1)],1).mean(0)
rng=np.random.default_rng(0)
for sn in ['all','noNoisy']:
  idx0=np.array([i for i,s in enumerate(stems) if SETS[sn](s)])
  pt=v(CA[:,idx0],XA[:,idx0])-v(CB[:,idx0],XB[:,idx0]);D=[]
  for _ in range(a.boot):
    i=rng.choice(idx0,len(idx0));D.append(v(CA[:,i],XA[:,i])-v(CB[:,i],XB[:,i]))
  D=np.array(D);print('BOOT',sn,' '.join('%s %+.4f [%+.4f,%+.4f] P>0 %.2f'%(k,pt[j],np.nanpercentile(D[:,j],2.5),np.nanpercentile(D[:,j],97.5),np.mean(D[:,j]>0)) for j,k in enumerate(PR)))
  for j,(k,cl) in enumerate([('crack',14),('inact',11)]):
    gt=CB[0][:, cl,:].sum(1);top=set(np.argsort(-gt)[:3]);keep=np.array([i for i in idx0 if i not in top])
    print('   top3-out',k,'%+.4f'%(v(CA[:,keep],XA[:,keep])-v(CB[:,keep],XB[:,keep]))[j])
