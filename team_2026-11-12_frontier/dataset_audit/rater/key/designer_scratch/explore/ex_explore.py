import sys, os, csv
sys.path.insert(0,'/home/yugma/mtp/research/team_2026-11-12_frontier/dataset_audit/rater/scripts')
import build as B, rcommon as R, numpy as np
stems=R.C.pool_stems(); pool=set(stems)
cands=B.supported_candidates(); cc={r['stem'] for r in cands}
cal,used=B.select_calibration(stems,pool,cc)
rows=list(csv.DictReader(open(R.C.OUT/'a_candidates.tsv'),delimiter='\t'))
uns=[r for r in rows if r['supported']=='0' and r['stem'] not in cc and r['stem'] not in used]
print(len(uns))
out='/home/noob/work/bench_int_io/rater/explore/ex_panels'; os.makedirs(out,exist_ok=True)
for i,r in enumerate(sorted(uns,key=lambda r:-int(r['px']))[:40]):
    print(i, r['stem'], r['type'], r['kind'], r['px'], r['z'], r['classes_under'], r['bbox_y0x0y1x1'])
sel=[r for r in sorted(uns,key=lambda r:-int(r['px'])) if r['type'] in ('MC','SC')][:6]
for i,r in enumerate(sel):
    d=R.load_cell(r['stem'],pool)
    R.render_panel(f'U{i}',d['grey'],(d['lab_crack'],d['lab_inact']),(d['con_crack'],d['con_inact']),[int(v) for v in r['bbox_y0x0y1x1'].split(',')],out_path=f'{out}/U{i}_{r["type"]}_A=label.png',valid=d['valid'])
