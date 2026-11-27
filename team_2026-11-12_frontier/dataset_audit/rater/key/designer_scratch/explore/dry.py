import sys, time, collections
sys.path.insert(0,'/home/yugma/mtp/research/team_2026-11-12_frontier/dataset_audit/rater/scripts')
import build as B, rcommon as R
t=time.time()
stems=R.C.pool_stems(); pool=set(stems)
cands=B.supported_candidates(); cc={r['stem'] for r in cands}
g3=R.C.groups(R.C.G3); cal,used=B.select_calibration(stems,pool,cc,{g3[s]["group"] for s in cc})
print(len(cal), len(used), f'{time.time()-t:.0f}s')
print(collections.Counter((c['cls'],c['plant'],c['side']) for c in cal))
print(collections.Counter((c['cls'],c['stem'].split('_')[0]) for c in cal))
print(collections.Counter(c['stem'] for c in cal).most_common(3))
import numpy as np
for c in cal:
    b=c['bbox']; print(c['cls'],c['plant'],c['side'], max(b[2]-b[0],b[3]-b[1])+1, {k:(round(float(v),2) if isinstance(v,float) else v) for k,v in c.items() if k in ('z_comp','z_seg','z_shift','v','area','len_px','seg_px','min_cov','seg_mode')})
