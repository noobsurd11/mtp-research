import sys
sys.path.insert(0,'/home/yugma/mtp/research/team_2026-11-12_frontier/dataset_audit/rater/scripts')
import build as B, rcommon as R, numpy as np
from scipy import ndimage as ndi
stems=R.C.pool_stems(); pool=set(stems); g3=R.C.groups(R.C.G3)
cc={r['stem'] for r in B.supported_candidates()}; rg={g3[s]['group'] for s in cc}
cal,used=B.select_calibration(stems,pool,cc,rg)
free=[s for s in stems if s not in used and s not in cc and g3[s]['group'] not in rg]
print('free cells',len(free))
for s in free:
    d=R.load_cell(s,pool)
    if d['lab_inact'].any():
        li,n=ndi.label(d['lab_inact'],R.C.S8)
        for i in range(1,n+1):
            I=li==i; m=int(I.sum())
            if m<150: continue
            bb=R.bbox_of(I); e=max(bb[2]-bb[0],bb[3]-bb[1])+1
            z=B.zc(d,I,d['lab_inact']|d['con_inact'])
            print('INACT',s,m,e,round(float((d['vi'][I]>=13).mean()),2),round(z,2),B.window_clean(d,bb))
    if d['lab_crack'].any():
        for mc in (23,20):
            k=len(B.crack_clean_comps(d,mc))
            if k: print('CRACK',s,mc,k); break
