"""Idea 3 premise: same-module neighbour files available per cell, by set.
Sources: our labelled 582 + E1 106 + Hanifi 117 (index), our 11,938 pool (external_unlabeled_meta.csv),
HF large pool (manifest.tsv, by ID only; not downloaded). Usage: python -I dom_neigh_count.py INDEX.tsv"""
import sys, csv, re, os, collections, numpy as np
H = os.path.expanduser('~')
idx = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
rx = re.compile(r'^([A-Z]+)_(\d+)_r(\d+)_c(\d+)')
def modkey(st):
    m = rx.match(st); return (m.group(1), int(m.group(2))) if m else None
lab = collections.defaultdict(set)
for r in idx:
    k = modkey(r['stem'])
    if k: lab[k].add(r['stem'].replace('_rf', ''))
pool = collections.defaultdict(set); pool_grp = {}
for r in csv.DictReader(open(H + '/mtp/datasets/splits_benchmark/external_unlabeled_meta.csv')):
    k = modkey(r['stem'])
    if k: pool[k].add(r['stem']); pool_grp.setdefault(k, set()).add(r['group'])
hf = collections.defaultdict(set); hf_grp = {}
with open(H + '/mtp/research/team_2026-10-29_features/pool_large/out/manifest.tsv') as f:
    hd = f.readline().rstrip('\n').split('\t')
    ist = hd.index('stem') if 'stem' in hd else None
    ifp = hd.index('file_path') if 'file_path' in hd else None
    for l in f:
        p = l.rstrip('\n').split('\t')
        st = p[ist] if ist is not None else os.path.basename(p[ifp])[:-4]
        k = modkey(st)
        if k:
            hf[k].add(st)
            if ifp is not None: hf_grp.setdefault(k, set()).add('/'.join(p[ifp].split('/')[:2]))
print('HF header', hd[:6])
def q(a):
    a = np.array(a); return 'n %d | 0 nb %d (%.0f%%) | >=3 nb %d (%.0f%%) | >=8 nb %d (%.0f%%) | median %.0f' % (
        len(a), (a == 0).sum(), 100 * (a == 0).mean(), (a >= 3).sum(), 100 * (a >= 3).mean(), (a >= 8).sum(), 100 * (a >= 8).mean(), np.median(a))
for s in ['train', 'val', 'test', 'E1', 'rf']:
    rr = [r for r in idx if r['set'] == s]
    nogrid = [r for r in rr if not modkey(r['stem'])]
    A, B, C = [], [], []
    for r in rr:
        k = modkey(r['stem'])
        if not k: A.append(0); B.append(0); C.append(0); continue
        st = r['stem'].replace('_rf', '')
        a = lab[k] - {st}; b = a | (pool[k] - {st}); c = b | (hf[k] - {st})
        A.append(len(a)); B.append(len(b)); C.append(len(c))
    print(f'== {s}: {len(rr)} cells, {len(nogrid)} without a row/col grid ID ({collections.Counter(r["src"] for r in nogrid)})')
    print('  labelled sets only     ', q(A)); print('  + our 11,938 pool      ', q(B)); print('  + HF 159k (by ID)      ', q(C))
# E1 half-cut vs other
for hc in ('1', '0'):
    rr = [r for r in idx if r['set'] == 'E1' and r['halfcut'] == hc]
    A = [len(lab[modkey(r['stem'])] - {r['stem']}) if modkey(r['stem']) else 0 for r in rr]
    C = [len((lab[modkey(r['stem'])] | pool[modkey(r['stem'])] | hf[modkey(r['stem'])]) - {r['stem']}) if modkey(r['stem']) else 0 for r in rr]
    print(f'E1 halfcut={hc}: labelled-only', q(A), '|| all sources', q(C))
