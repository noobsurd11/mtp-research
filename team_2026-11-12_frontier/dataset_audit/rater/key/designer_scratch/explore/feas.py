import sys, csv, collections, pickle
sys.path.insert(0,'/home/yugma/mtp/research/team_2026-11-12_frontier/dataset_audit/scripts')
import common as C, numpy as np
from scipy import ndimage as ndi
rows=list(csv.DictReader(open(C.OUT/'a_candidates.tsv'),delimiter='\t'))
supcells={r['stem'] for r in rows if r['supported']=='1'}
anycells={r['stem'] for r in rows}
stems=C.pool_stems(); pool=set(stems)
crack=[]; inact=[]
for s in stems:
    gt=C.mask_v11(s); z=np.load(C.CACHE/'cons'/f'{s}.npz')
    vc,vi,ncov,ign=z['vc'],z['vi'],z['ncov'],z['ign']
    keep=gt!=255; valid=keep&(gt!=7)
    g=(gt==14)&keep; gi=(gt==11)&keep
    if not g.any(): continue
    gry=C.grey(s)
    lg,n=ndi.label(g,C.S8)
    excl=g|(vc>=13)
    for i in range(1,n+1):
        comp=lg==i; m=int(comp.sum())
        if m<40: continue
        a25=float((ncov[comp]>=25).mean()); a23=float((ncov[comp]>=23).mean())
        zz=C.contrast_z(gry,comp,excl,valid)
        crack.append((s,m,a25,a23,zz, s in supcells, s in anycells))
    if gi.any():
        li,ni=ndi.label(gi,C.S8)
        for i in range(1,ni+1):
            comp=li==i; m=int(comp.sum())
            if m<200: continue
            v20=float((vi[comp]>=20).mean()); v25=float((vi[comp]>=25).mean())
            zz=C.contrast_z(gry,comp,gi|(vi>=13),valid)
            inact.append((s,m,v20,v25,zz,s in supcells, s in anycells))
def summ(L, f):
    sel=[x for x in L if f(x)]
    return len(sel), len({x[0] for x in sel}), collections.Counter(x[0].split('_')[0] for x in {x[0]:x for x in sel}.values())
print('crack comps>=40', len(crack))
for thr in (25,23):
    k=2 if thr==25 else 3
    print(thr, 'not supcell, a>=0.95, z<=-1', summ(crack, lambda x: x[k]>=0.95 and x[4]<=-1 and not x[5]))
    print(thr, 'no cand cell, a>=0.95, z<=-1', summ(crack, lambda x: x[k]>=0.95 and x[4]<=-1 and not x[6]))
print('inact comps>=200', len(inact))
for k,name in ((2,'v20'),(3,'v25')):
    for frac in (0.9,0.8):
        print(name,frac,'not supcell z<=-1', summ(inact, lambda x: x[k]>=frac and x[4]<=-1 and not x[5]))
        print(name,frac,'no cand cell z<=-1', summ(inact, lambda x: x[k]>=frac and x[4]<=-1 and not x[6]))
pickle.dump((crack,inact),open('/home/noob/work/bench_int_io/rater/explore/feas.pkl','wb'))
