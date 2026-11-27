import sys, collections
sys.path.insert(0,'/home/yugma/mtp/research/team_2026-11-12_frontier/dataset_audit/rater/scripts')
import build as B, rcommon as R, numpy as np
from scipy import ndimage as ndi
stems=R.C.pool_stems(); pool=set(stems)
cc={r['stem'] for r in B.supported_candidates()}
why=collections.Counter(); ext=[]
for s in stems:
    if s in cc: continue
    d=R.load_cell(s,pool)
    if not d['lab_crack'].any(): continue
    for K,z in B.crack_clean_comps(d):
        bb=R.bbox_of(K); e=max(bb[2]-bb[0],bb[3]-bb[1])+1; ext.append(e)
        if e>90: why['ext>90']+=1; continue
        yx=np.argwhere(K).astype(float); w,V=np.linalg.eigh(np.cov((yx-yx.mean(0)).T)); nrm=V[:,0]
        for sg in (1,-1):
            v=(int(round(sg*8*nrm[0])),int(round(sg*8*nrm[1])))
            Kc=d['con_crack']&ndi.binary_dilation(K,structure=R.disc(4))
            KS,KcS=B.shift_mask(K,v),B.shift_mask(Kc,v)
            if KS is None or KcS is None: why['oob']+=1; continue
            halo=ndi.binary_dilation(K,structure=R.disc(6))
            rest_l=d['lab_crack']&~K; rest_c=d['con_crack']&~Kc; both=KS|KcS
            if B.dist_to(rest_l)[both].min()<5: why['near other label crack']+=1; continue
            if B.dist_to((d['vc']>=2)&~halo)[both].min()<5: why['near votes']+=1; continue
            if B.dist_to(rest_c)[both].min()<5: why['near other cons crack']+=1; continue
            if B.dist_to(d['lab_inact']|d['con_inact'])[both].min()<3: why['near inactive']+=1; continue
            if not np.isin(d['gt'][KS],R.ALLOWED_PLACE).all(): why['class '+str(sorted(set(np.unique(d['gt'][KS]))-{0,9}))]+=1; continue
            z2=B.zc(d,KS,d['lab_crack']|d['con_crack'])
            if not z2>-0.5: why['dark at shift']+=1; continue
            if not B.window_clean(d,R.bbox_of(K|KS)): why['window ign']+=1; continue
            why['OK']+=1
print(why); print(np.percentile(ext,[10,25,50,75,90]))
