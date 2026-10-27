# judge: E1 ext inactive: per-cell GT share and per-arm recall per cell (seed means); leave-top-cell-out pooled IoU
import json, glob, statistics as st
R='/home/yugma/mtp/research/results/e1/raw_v2/'
arms={'A100':['p6_L3_100pct','p16_A_100pct'],'Sx100':['p16_Sx_100pct'],'A50':['p16_A_50pct'],'S50':['p16_S_50pct'],
      'A20':['p6_L3_20pct','p16_A_20pct'],'S20':['p16_S_20pct'],'BsM20':['p18_BsM_20pct'],'L3_10':['p6_L3_10pct'],'BsM10':['p18_BsM_10pct'],
      'A5':['al1_A5'],'BsM5':['al1_BsM5'],'A5c':['p12_A_5pct','p13_A_5pct'],'CsM5':['p13_CsM_5pct']}
def files(ps): return sorted(f for p in ps for f in glob.glob(R+p+'_s*.json'))
ref=json.load(open(files(arms['A100'])[0]))['cells']['ext']
gt={k:v['inact_gt'] for k,v in ref.items() if v['inact_gt']>0}
tot=sum(gt.values())
print('E1 inactive cells',len(gt),'px',tot)
for k,v in sorted(gt.items(),key=lambda x:-x[1]): print(f'  {k:28s} {v:7d} {v/tot:.2f}')
def pooled(c,drop=()):
    tp=sum(v['inact_tp'] for k,v in c.items() if k not in drop); g=sum(v['inact_gt'] for k,v in c.items() if k not in drop); p=sum(v['inact_pred'] for k,v in c.items() if k not in drop)
    return tp/(g+p-tp) if g+p-tp else float('nan')
top=[k for k,_ in sorted(gt.items(),key=lambda x:-x[1])[:3]]
print('\narm   n  pooledIoU  noTop1  noTop3   FPpx_on_noGT_cells   recall_per_cell(seed-mean, sorted by GT)')
for a,ps in arms.items():
    fs=files(ps); cs=[json.load(open(f))['cells']['ext'] for f in fs]
    iou=st.mean(pooled(c) for c in cs); i1=st.mean(pooled(c,top[:1]) for c in cs); i3=st.mean(pooled(c,top) for c in cs)
    fp=st.mean(sum(v['inact_pred'] for k,v in c.items() if v['inact_gt']==0) for c in cs)
    rec=[st.mean(c[k]['inact_tp']/gt[k] for c in cs) for k,_ in sorted(gt.items(),key=lambda x:-x[1])]
    print(f'{a:6s} {len(fs)} {iou:.3f} {i1:.3f} {i3:.3f} {fp:9.0f}  '+' '.join(f'{r:.2f}' for r in rec))
