# judge: seed-level rule 1 on E1 ext (and test) pooled crack / inactive IoU from per-cell counts
import json, glob, math, statistics as st, sys
R='/home/yugma/mtp/research/results/e1/raw_v2/'
def runs(prefix):
    return sorted(glob.glob(R+prefix+'_s*.json'))
def pooled(f, split, cls):
    c=json.load(open(f))['cells'][split]
    tp=sum(v[cls+'_tp'] for v in c.values()); g=sum(v[cls+'_gt'] for v in c.values()); p=sum(v[cls+'_pred'] for v in c.values())
    return tp/(g+p-tp) if g+p-tp>0 else float('nan'), tp/g if g else float('nan')
def arm(prefixes, split, cls):
    fs=[f for p in prefixes for f in runs(p)]
    return [pooled(f,split,cls) for f in fs], fs
def rule(a,b):
    sa=st.stdev(a) if len(a)>1 else 0; sb=st.stdev(b) if len(b)>1 else 0
    n=min(len(a),len(b)); thr=max(0.01, 2*math.sqrt((sa**2+sb**2)/3))
    d=st.mean(b)-st.mean(a); v='BETTER' if d>thr else ('WORSE' if d<-thr else 'n.d.')
    return d,thr,v
pairs=[('A50 vs S50',['p16_A_50pct'],['p16_S_50pct']),
       ('A20 vs S20',['p6_L3_20pct','p16_A_20pct'],['p16_S_20pct']),
       ('A100 vs Sx100',['p6_L3_100pct','p16_A_100pct'],['p16_Sx_100pct']),
       ('A20 vs BsM20',['p6_L3_20pct','p16_A_20pct'],['p18_BsM_20pct']),
       ('L3_10 vs BsM10',['p6_L3_10pct'],['p18_BsM_10pct']),
       ('A5(al1) vs BsM5(al1)',['al1_A5'],['al1_BsM5']),
       ('A5c vs CsM5',['p12_A_5pct','p13_A_5pct'],['p13_CsM_5pct']),
]
for split in ['test','ext']:
  for cls in ['crack','inact']:
    print(f'== {split} {cls} pooled IoU (recall) ==')
    for name,A,B in pairs:
        a,fa=arm(A,split,cls); b,fb=arm(B,split,cls)
        ai=[x[0] for x in a]; bi=[x[0] for x in b]
        d,thr,v=rule(ai,bi)
        print(f'{name:22s} nA={len(ai)} nB={len(bi)} A={st.mean(ai):.3f} B={st.mean(bi):.3f} d={d:+.4f} thr={thr:.4f} {v}  recA={st.mean(x[1] for x in a):.3f} recB={st.mean(x[1] for x in b):.3f}')
