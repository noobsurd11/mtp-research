import json,numpy as np
from mc_score import pool,SETS,NC
M='../m0/';RS=['p6_L3_100pct_s0','p6_L3_100pct_s1','p6_L3_100pct_s2','p16_A_100pct_s3','p16_A_100pct_s4']
D={r:json.load(open(M+r+'.json')) for r in RS}
ROB=[0,1,2,4,5,7,11,13,14,15,16,20,21]
def ious(C):
    tp=np.diag(C);g=C.sum(1);p=C.sum(0);return np.where(g>0,tp/np.maximum(g+p-tp,1),np.nan),tp/np.maximum(p,1),tp/np.maximum(g,1)
def mrob(C,no07=False):
    i=ious(C)[0];L=[c for c in ROB if not(no07 and c in(0,7))];return np.nanmean(i[L])
print('per seed mIoU_rob all/noNoisy:',[ (round(mrob(pool(D[r]['cells']['test'],SETS['all'])[0]),3),round(mrob(pool(D[r]['cells']['test'],SETS['noNoisy'])[0]),3)) for r in RS])
for sn in ['all','noNoisy','noTwins','noBoth','ARTS','BMRK','CFVS','CSIR']:
    v=[mrob(pool(D[r]['cells']['test'],SETS[sn])[0]) for r in RS];w=[mrob(pool(D[r]['cells']['test'],SETS[sn])[0],True) for r in RS]
    rp=[];rr=[]
    for r in RS:
        _,x=pool(D[r]['cells']['test'],SETS[sn]);rp.append(x[0]/x[1]);rr.append(x[2]/x[3])
    print(f'{sn:8s} mIoU_rob {np.mean(v):.3f}±{np.std(v,ddof=1):.3f} no07 {np.mean(w):.3f}  relP2 {np.mean(rp):.3f} relR2 {np.mean(rr):.3f}')
# per class all 50
I=np.array([ious(pool(D[r]['cells']['test'],SETS['all'])[0])[0] for r in RS])
print('per-class IoU:',{c:round(float(np.nanmean(I[:,c])),3) for c in range(NC) if not np.all(np.isnan(I[:,c]))})
# components
def comp(sn,key='crack_cc',minsz=20,frac=0.5):
    out=[];prec=[]
    for r in RS:
        f=0;n=0;pf=0;pn=0
        for s,c in D[r]['cells']['test'].items():
            if not SETS[sn](s):continue
            for sz,h in c[key]['gt']:
                if sz>=minsz: n+=1;f+=h>=frac*sz
            for sz,h in c[key]['pr']:
                if sz>=minsz: pn+=1;pf+=h>0
        out.append(f/n);prec.append(pf/pn)
    return np.mean(out),np.mean(prec)
for sn in ['all','noNoisy','noBoth']: print(sn,'crack comp rec/prec',np.round(comp(sn),3),'inact comp',np.round(comp(sn,'inact_cc',100),3))
# val tta single model
for k in ['val','val_tta']:
    C=[pool(D[r]['cells'][k],SETS['all'])[0] for r in RS];print(k,'crack',round(np.mean([ious(c)[0][14] for c in C]),3),'inact',round(np.mean([ious(c)[0][11] for c in C]),3))
