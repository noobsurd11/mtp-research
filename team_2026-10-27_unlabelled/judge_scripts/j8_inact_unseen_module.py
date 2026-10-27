# judge (post hoc, descriptive): SSL vs supervised inactive IoU/recall on clean test cells from seen vs unseen modules.
import json, glob, statistics as st, math, os
R='/home/yugma/mtp/research/results/e1/raw_v2/'
SP='/home/yugma/mtp/datasets/splits_benchmark/'
NOISY='CSIR_00070_r8_c4'
def mod(s): return '_'.join(s.split('_')[:2])
tm={mod(os.path.basename(l.strip()).replace('.png','')) for l in open(SP+'train.txt') if l.strip()}
def files(ps): return sorted(f for p in ps for f in glob.glob(R+p+'_s*.json'))
arms={'A100':['p6_L3_100pct','p16_A_100pct'],'Sx100':['p16_Sx_100pct'],'A50':['p16_A_50pct'],'S50':['p16_S_50pct'],'A20':['p6_L3_20pct','p16_A_20pct'],'S20':['p16_S_20pct'],'BsM20':['p18_BsM_20pct'],'L3_10':['p6_L3_10pct'],'BsM10':['p18_BsM_10pct'],'A5c':['p12_A_5pct','p13_A_5pct'],'BsM5':['p13_BsM_5pct']}
C={a:[json.load(open(f))['cells']['test'] for f in files(p)] for a,p in arms.items()}
keys=[k for k in C['A100'][0] if k!=NOISY]
G={'seen':[k for k in keys if mod(k) in tm],'unseen':[k for k in keys if mod(k) not in tm]}
for g,ks in G.items():
    gt=sum(C['A100'][0][k]['inact_gt'] for k in ks); n=sum(1 for k in ks if C['A100'][0][k]['inact_gt']>0)
    print(f'== {g}-module clean test cells: {len(ks)}, inactive cells {n}, inactive px {gt}')
    for A,B in [('A100','Sx100'),('A50','S50'),('A20','S20'),('A20','BsM20'),('L3_10','BsM10'),('A5c','BsM5')]:
        def pr(c):
            tp=sum(c[k]['inact_tp'] for k in ks); g_=sum(c[k]['inact_gt'] for k in ks); p=sum(c[k]['inact_pred'] for k in ks)
            return tp/(g_+p-tp), tp/g_
        a=[pr(c) for c in C[A]]; b=[pr(c) for c in C[B]]
        ai=[x[0] for x in a]; bi=[x[0] for x in b]
        thr=max(0.01,2*math.sqrt((st.stdev(ai)**2+st.stdev(bi)**2)/3)); d=st.mean(bi)-st.mean(ai)
        print(f'  {B}-{A}: IoU {st.mean(ai):.3f}->{st.mean(bi):.3f} d={d:+.3f} thr={thr:.3f} | recall {st.mean(x[1] for x in a):.3f}->{st.mean(x[1] for x in b):.3f}')
