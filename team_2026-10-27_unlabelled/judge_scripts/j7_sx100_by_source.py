# judge: does Sx100 (external CSIR/ARTS pool) help on the test cells whose source IS in the pool? (clean test, seed means)
import json, glob, statistics as st, math
R='/home/yugma/mtp/research/results/e1/raw_v2/'
NOISY='CSIR_00070_r8_c4'
def files(ps): return sorted(f for p in ps for f in glob.glob(R+p+'_s*.json'))
def pooled(c,keys,cls):
    tp=sum(c[k][cls+'_tp'] for k in keys); g=sum(c[k][cls+'_gt'] for k in keys); p=sum(c[k][cls+'_pred'] for k in keys)
    return (tp/(g+p-tp) if g+p-tp else float('nan'), tp/g if g else float('nan'))
arms={'A100':['p6_L3_100pct','p16_A_100pct'],'Sx100':['p16_Sx_100pct'],'A50':['p16_A_50pct'],'S50':['p16_S_50pct'],'A20':['p6_L3_20pct','p16_A_20pct'],'BsM20':['p18_BsM_20pct'],'S20':['p16_S_20pct']}
C={a:[json.load(open(f))['cells']['test'] for f in files(p)] for a,p in arms.items()}
keys=[k for k in C['A100'][0] if k!=NOISY]
groups={'pool sources (CSIR+ARTS)':[k for k in keys if k[:4] in ('CSIR','ARTS')],'non-pool (CFVS+BMRK+SDLE)':[k for k in keys if k[:4] not in ('CSIR','ARTS')]}
for g,ks in groups.items():
    print(f'== {g}: {len(ks)} cells')
    for A,B in [('A100','Sx100'),('A50','S50'),('A20','S20'),('A20','BsM20')]:
        for cls in ['crack','inact']:
            a=[pooled(c,ks,cls) for c in C[A]]; b=[pooled(c,ks,cls) for c in C[B]]
            ai=[x[0] for x in a]; bi=[x[0] for x in b]
            if any(math.isnan(x) for x in ai+bi): print(f'  {B}-{A} {cls}: no GT'); continue
            thr=max(0.01,2*math.sqrt((st.stdev(ai)**2+st.stdev(bi)**2)/3)); d=st.mean(bi)-st.mean(ai)
            print(f'  {B}-{A} {cls}: IoU {st.mean(ai):.3f}->{st.mean(bi):.3f} d={d:+.4f} thr={thr:.4f} | recall {st.mean(x[1] for x in a):.3f}->{st.mean(x[1] for x in b):.3f}')
