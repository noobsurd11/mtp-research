import sys, os, csv
sys.path.insert(0,'/home/yugma/mtp/research/team_2026-11-12_frontier/dataset_audit/rater/scripts')
import build as B, rcommon as R, numpy as np
stems=R.C.pool_stems(); pool=set(stems); g3=R.C.groups(R.C.G3)
cands=B.supported_candidates(); cc={r['stem'] for r in cands}
cg={g3[s]['group'] for s in cc}
cal,used=B.select_calibration(stems,pool,cc)
print('calibration items whose cell shares a group with a rated cell:', sum(g3[c['stem']]['group'] in cg for c in cal), 'of', len(cal))
import collections; print(collections.Counter((c['cls'],c['plant']) for c in cal if g3[c['stem']]['group'] in cg))
print('cells in rated groups:', sum(g3[s]['group'] in cg for s in stems), 'rated groups', len(cg))
rows=list(csv.DictReader(open(R.C.OUT/'a_candidates.tsv'),delimiter='\t'))
uns=[r for r in rows if r['supported']=='0' and g3[r['stem']]['group'] not in cg and r['stem'] not in used]
print('unsupported candidates outside rated groups and calibration cells:', len(uns))
for i,r in enumerate(sorted(uns,key=lambda r:-int(r['px']))):
    print(i, r['stem'], r['type'], r['kind'], r['px'], r['z'], r['classes_under'], r['bbox_y0x0y1x1'])
out='/home/noob/work/bench_int_io/rater/explore/ex_panels'
sel=[r for r in sorted(uns,key=lambda r:-int(r['px'])) if r['type'] in ('MC','SC')][:6]
for i,r in enumerate(sel):
    d=R.load_cell(r['stem'],pool)
    R.render_panel(f'V{i}',d['grey'],(d['lab_crack'],d['lab_inact']),(d['con_crack'],d['con_inact']),[int(v) for v in r['bbox_y0x0y1x1'].split(',')],out_path=f'{out}/V{i}_{r["type"]}_{r["stem"]}_A=label.png',valid=d['valid'])
