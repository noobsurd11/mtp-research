"""MC: aggregate runs into arms, rule 1, paired image bootstrap. Independent of MD's code.
python mc_agg.py --arm A=f1.json,f2.json [--arm B=...] [--split test] [--contrast B-A]"""
import argparse,json,numpy as np,sys,os
sys.path.insert(0,os.path.dirname(__file__))
from mc_score import pool,met,SETS,NC
ap=argparse.ArgumentParser();ap.add_argument('--arm',action='append');ap.add_argument('--split',default='test')
ap.add_argument('--contrast',action='append',default=[]);ap.add_argument('--boot',type=int,default=2000)
a=ap.parse_args()
KEYS=['crack_iou','crack_P','crack_R','inact_iou','inact_P','inact_R','relF1','relP2','relR2','miou_gt','miou_gt_nobgpad','miou24']
arms={};cells={}
for s in a.arm:
    n,fs=s.split('=');arms[n]=[json.load(open(f))['cells'][a.split] for f in fs.split(',')]
ref=next(iter(arms.values()))[0];gtcls=pool(ref,lambda s:True)[0].sum(1)>0
stems=sorted(ref)
def armstat(runs,f):
    v={k:[] for k in KEYS};ious=[]
    for c in runs:
        C,r=pool(c,f);m=met(C,r,gtcls)
        for k in KEYS:v[k].append(m[k])
        ious.append(m['iou'])
    return v,np.array(ious)
for n,runs in arms.items():
    print(f'== {n} ({len(runs)} runs, {a.split})')
    for sn,f in SETS.items():
        v,_=armstat(runs,f)
        print(f'  {sn:8s} '+' '.join(f'{k} {np.mean(v[k]):.4f}±{np.std(v[k],ddof=1) if len(runs)>1 else 0:.4f}' for k in ['crack_iou','crack_P','crack_R','inact_iou','inact_P','inact_R','relF1','miou_gt','miou_gt_nobgpad','miou24']))
    _,I=armstat(runs,SETS['all'])
    print('  per-class IoU mean:',' '.join(f'{c}:{np.nanmean(I[:,c]):.3f}' for c in range(NC) if gtcls[c]))
def rule1(xa,xb):
    sd=lambda x:np.std(x,ddof=1)
    thr=max(0.01,2*np.sqrt((sd(xa)**2+sd(xb)**2)/3));d=np.mean(xb)-np.mean(xa)
    return d,thr,('BETTER' if d>thr else 'WORSE' if d<-thr else 'n.d.')
rng=np.random.default_rng(0)
for con in a.contrast:
    B,A=con.split('-')
    print(f'== {con}')
    for sn,f in SETS.items():
        va,_=armstat(arms[A],f);vb,_=armstat(arms[B],f)
        print(f'  {sn:8s} '+' | '.join('%s %+.4f (%.4f) %s'%((k,)+rule1(va[k],vb[k])) for k in ['crack_iou','inact_iou','relF1','miou_gt','crack_R','crack_P']))
    # paired bootstrap over test cells, pooled IoU per run then arm mean
    def conf_cells(runs):
        return np.stack([np.stack([np.array(c[s]['conf'],float).reshape(NC,NC) for s in stems]) for c in runs])
    CA,CB=conf_cells(arms[A]),conf_cells(arms[B])
    def iou_c(C,cl):
        tp=C[...,cl,cl];g=C[...,cl,:].sum(-1);p=C[...,:,cl].sum(-1);return tp/np.maximum(g+p-tp,1)
    out={'crack':[],'inact':[]}
    for _ in range(a.boot):
        idx=rng.integers(0,len(stems),len(stems))
        sa=CA[:,idx].sum(1);sb=CB[:,idx].sum(1)
        out['crack'].append(iou_c(sb,14).mean()-iou_c(sa,14).mean());out['inact'].append(iou_c(sb,11).mean()-iou_c(sa,11).mean())
    for k,v in out.items(): print(f'  boot {k}: CI [{np.percentile(v,2.5):+.4f}, {np.percentile(v,97.5):+.4f}] P(>0) {np.mean(np.array(v)>0):.3f}')
