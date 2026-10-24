import json,numpy as np
from mc_score import NC,TWINS,NOISY
R=json.load(open('../r1/r1_cells.json'));DEC=json.load(open('../r1/r1_val_decisions.json'))
RUNS=R['runs'];ROB=[0,1,2,4,5,7,11,13,14,15,16,20,21];VL=[0,1,2,4,5,7,9,11,13,14,15,16,21]
# 1 identity
mx=0
for r in RUNS:
  m0=json.load(open('../m0/%s.json'%r))['cells']
  for sp in ['val','test']:
    for s,c in R[sp]['single_plain/'+r].items(): mx=max(mx,np.abs(np.array(c['conf'])-np.array(m0[sp][s]['conf'])).max())
print('identity max|diff|',mx)
def M(cells,keep,cls):
  C=np.zeros((NC,NC));x=np.zeros(4)
  for s,c in cells.items():
    if keep(s): C+=np.array(c['conf']).reshape(NC,NC);x+=c['crack_rel2']
  tp=np.diag(C);g=C.sum(1);p=C.sum(0);iou=np.where(g>0,tp/np.maximum(g+p-tp,1),np.nan)
  rp=x[0]/max(x[1],1);rr=x[2]/max(x[3],1)
  return dict(crack=iou[14],inact=iou[11],relF1=2*rp*rr/max(rp+rr,1e-12),miou=np.nanmean(iou[cls]),cP=tp[14]/p[14],cR=tp[14]/g[14],relP=rp,relR=rr,iP=tp[11]/p[11])
A=lambda s:True;N=lambda s:s!=NOISY
# 2 val decisions
v=R['val'];sc=lambda m:np.mean([m['crack'],m['relF1'],m['miou']])
print('val score ens_plain %.4f ens_tta %.4f'%(sc(M(v['ens_plain'],A,VL)),sc(M(v['ens_tta'],A,VL))),'dec',DEC['use_tta_on_ensemble'],DEC['crack_bias'],DEC['why'])
sw=DEC['sweep'];print('sweep relR/relP:',{k:(round(x['relR2'],3),round(x['relP2'],3),round(x['relF1'],4)) for k,x in sw.items()})
m=M(v['r1_final_bias0.75'],A,VL);print('val r1_final relR %.4f relP %.4f relF1 %.4f  vs sweep0.75 %.4f %.4f'%(m['relR'],m['relP'],m['relF1'],sw['0.75']['relR2'],sw['0.75']['relP2']))
# 3 R1a rule1
t=R['test'];K=['crack','inact','relF1','miou','cP','iP','relP']
def rule1(a,b):
  sd=lambda x:np.std(x,ddof=1);thr=max(0.01,2*np.sqrt((sd(a)**2+sd(b)**2)/3));d=np.mean(b)-np.mean(a);return d,thr,('BETTER' if d>thr else 'WORSE' if d<-thr else 'nd')
for nm,f in [('all',A),('noNoisy',N)]:
  P=[M(t['single_plain/'+r],f,ROB) for r in RUNS];T=[M(t['single_tta/'+r],f,ROB) for r in RUNS]
  print('R1a',nm,' | '.join('%s %+.4f (%.4f) %s'%((k,)+rule1([x[k] for x in P],[x[k] for x in T])) for k in K[:4]),
        '| paired crack diffs',np.round([T[i]['crack']-P[i]['crack'] for i in range(5)],4),' prec dC %+.3f dI %+.3f'%(np.mean([x['cP'] for x in T])-np.mean([x['cP'] for x in P]),np.mean([x['iP'] for x in T])-np.mean([x['iP'] for x in P])))
# 4 R1b bootstrap
stems=sorted(t['ens_plain'])
def cm(cells): return np.stack([np.array(cells[s]['conf'],float).reshape(NC,NC) for s in stems]),np.stack([np.array(cells[s]['crack_rel2'],float) for s in stems])
Es,Er=cm(t['ens_plain']);S=[cm(t['single_plain/'+r]) for r in RUNS]
def met(C,x):
  tp=np.diag(C);g=C.sum(1);p=C.sum(0);iou=np.where(g>0,tp/np.maximum(g+p-tp,1),np.nan)
  rp=x[0]/max(x[1],1);rr=x[2]/max(x[3],1);return np.array([iou[14],iou[11],2*rp*rr/max(rp+rr,1e-12),np.nanmean(iou[ROB])])
rng=np.random.default_rng(0)
for nm,keep in [('all',np.ones(len(stems),bool)),('noNoisy',np.array([s!=NOISY for s in stems]))]:
  idx0=np.where(keep)[0];pt=met(Es[idx0].sum(0),Er[idx0].sum(0))-np.mean([met(C[idx0].sum(0),x[idx0].sum(0)) for C,x in S],0)
  D=[]
  for _ in range(2000):
    i=rng.choice(idx0,len(idx0));D.append(met(Es[i].sum(0),Er[i].sum(0))-np.mean([met(C[i].sum(0),x[i].sum(0)) for C,x in S],0))
  D=np.array(D);print('R1b',nm,' '.join('%s %+.4f [%+.4f,%+.4f]'%(k,pt[j],np.nanpercentile(D[:,j],2.5),np.nanpercentile(D[:,j],97.5)) for j,k in enumerate(['crack','inact','relF1','miou'])))
  loo=[met(*[a[idx0].sum(0) for a in cm(t['loo_plain/-'+r])]) for r in RUNS];print('   LOO crack',np.round([l[0] for l in loo],4),'single mean',np.round(np.mean([met(C[idx0].sum(0),x[idx0].sum(0)) for C,x in S],0),4),'ens',np.round(met(Es[idx0].sum(0),Er[idx0].sum(0)),4))
# 5 R1c
for nm,f in [('all',A),('noNoisy',N)]:
  a=M(t['ens_plain'],f,ROB);b=M(t['r1_final_bias0.75'],f,ROB)
  print('R1c',nm,' '.join('%s %.4f->%.4f'%(k,a[k],b[k]) for k in ['crack','cP','cR','relP','relR','relF1','inact','miou']))
c=t['r1_final_bias0.75'][NOISY]['conf'];c0=t['ens_plain'][NOISY]['conf']
print('noisy cell crack px pred: ens',int(np.array(c0).reshape(24,24)[:,14].sum()),'r1c',int(np.array(c).reshape(24,24)[:,14].sum()),' border ens',int(np.array(c0).reshape(24,24)[:,5].sum()))
for r in RUNS:
  for k in ['single_plain/','single_tta/']: print('  ',k+r,'noisy crack px',int(np.array(t[k+r][NOISY]['conf']).reshape(24,24)[:,14].sum()),'border',int(np.array(t[k+r][NOISY]['conf']).reshape(24,24)[:,5].sum()))
