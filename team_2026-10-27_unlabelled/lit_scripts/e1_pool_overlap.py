# lit, 27 Oct: do the E1 unseen-module cells share modules with the external unlabelled pool?
# Module id = first two '_' fields of the stem (e.g. CSIR_00300). Run: python3 -I e1_pool_overlap.py
import csv, os
H = os.path.expanduser('~/mtp')
e1 = [r for r in csv.DictReader(open(f'{H}/research/results/e1/ext117_manifest.csv')) if r['in_external_pool'] == '0']
pool = [r['stem'] for r in csv.DictReader(open(f'{H}/datasets/splits_benchmark/external_unlabeled_meta.csv'))]
mod = lambda s: '_'.join(s.split('_')[:2])
pm = {}
for s in pool:
    pm[mod(s)] = pm.get(mod(s), 0) + 1
em = sorted(set(mod(r['stem']) for r in e1))
hit = [m for m in em if m in pm]
print('E1 cells', len(e1), 'E1 module ids', len(em), 'with pool cells', len(hit), 'pool cells there', sum(pm[m] for m in hit))
ce = [r for r in e1 if int(r['crack_px']) > 0]
print('E1 crack cells', len(ce), 'in pool-covered modules', sum(mod(r['stem']) in pm for r in ce))
