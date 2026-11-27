import sys, os
sys.path.insert(0,'/home/yugma/mtp/research/team_2026-11-12_frontier/dataset_audit/rater/scripts')
import build as B, rcommon as R
stems=R.C.pool_stems(); pool=set(stems)
cands=B.supported_candidates(); cc={r['stem'] for r in cands}
cal,used=B.select_calibration(stems,pool,cc)
out='/home/noob/work/bench_int_io/rater/explore/test_panels'; os.makedirs(out,exist_ok=True)
pick=[c for c in cal if (c['cls'],c['plant'],c['side']) in {('crack','SHIFT','L'),('crack','DEL','C'),('inact','FAKE','L'),('crack','FAKE','C'),('inact','DEL','L')}]
seen=set(); sel=[]
for c in pick:
    k=(c['cls'],c['plant'],c['side'])
    if k in seen: continue
    seen.add(k); sel.append(c)
for i,c in enumerate(sel):
    c['set']='cal'
    d=R.load_cell(c['stem'],pool); lab,con=B.overlays_for(c,d)
    R.render_panel(f'T{i}',d['grey'],lab,con,c['bbox'],valid=d['valid'],out_path=f'{out}/T{i}_{c["cls"]}_{c["plant"]}_{c["side"]}_A=label.png')
    print(i,c['cls'],c['plant'],c['side'],c['stem'])
