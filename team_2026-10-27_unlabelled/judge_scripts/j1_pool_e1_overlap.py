# judge: how many E1-ext modules have cells in the 11,938 external pool, and in our 582 labelled cells
import csv, re, os, glob
P='/home/yugma/mtp/datasets/splits_benchmark/external_unlabeled_meta.csv'
M='/home/yugma/mtp/research/results/e1/ext117_manifest.csv'
def mod(stem):
    # CSIR_00070_r8_c4 -> CSIR_00070 ; BMRK_01502_cell2156 -> BMRK_01502
    return '_'.join(stem.split('_')[:2])
pool=[r['stem'] for r in csv.DictReader(open(P))]
pm={}
for s in pool: pm[mod(s)]=pm.get(mod(s),0)+1
ext=[r for r in csv.DictReader(open(M)) if r['in_external_pool']=='0']
print('E1 cells', len(ext))
em={}
for r in ext: em.setdefault(mod(r['stem']),[]).append(r)
print('E1 modules', len(em))
inpool=[m for m in em if m in pm]
print('E1 modules with >=1 pool cell', len(inpool), 'E1 cells in those modules', sum(len(em[m]) for m in inpool))
print('pool cells from E1 modules', sum(pm[m] for m in inpool))
crk=[r for r in ext if int(r['crack_px'])>0]; ina=[r for r in ext if int(r['inactive_px'])>0]
print('E1 crack cells', len(crk), 'in pool-modules', sum(mod(r['stem']) in pm for r in crk))
print('E1 inactive cells', len(ina), 'in pool-modules', sum(mod(r['stem']) in pm for r in ina))
# labelled 582
lab=set()
for f in ['train','val','test']:
    for p in glob.glob(f'/home/yugma/mtp/datasets/splits_benchmark/{f}*.txt'):
        pass
import itertools
sp='/home/yugma/mtp/datasets/splits_benchmark/'
print(sorted(os.listdir(sp))[:30])
