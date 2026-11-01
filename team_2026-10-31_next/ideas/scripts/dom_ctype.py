"""Add cell type (mono/multi/multi_half_cells + ribbons_N) to the index, by module, from the HF manifest folder
(by ID; ID collisions across folders flagged 'ambig') and our pool meta. Usage: python -I dom_ctype.py IN.tsv OUT.tsv"""
import sys, csv, re, os, collections
H = os.path.expanduser('~')
rx = re.compile(r'^([A-Z]+)_(\d+)_r(\d+)_c(\d+)')
g = collections.defaultdict(set)
with open(H + '/mtp/research/team_2026-10-29_features/pool_large/out/manifest.tsv') as f:
    hd = f.readline().rstrip('\n').split('\t'); ifp = hd.index('file_path')
    for l in f:
        fp = l.rstrip('\n').split('\t')[ifp]; m = rx.match(os.path.basename(fp))
        if m: g[(m.group(1), int(m.group(2)))].add('/'.join(fp.split('/')[:2]))
rows = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
w = csv.DictWriter(open(sys.argv[2], 'w'), fieldnames=list(rows[0].keys()) + ['ctype'], delimiter='\t'); w.writeheader()
for r in rows:
    m = rx.match(r['stem']); t = 'unknown'
    if m:
        s = g.get((m.group(1), int(m.group(2))), set())
        t = next(iter(s)) if len(s) == 1 else ('ambig' if s else 'unknown')
    if r['halfcut'] == '1' and t == 'unknown': t = 'halfcut_unknown'
    r['ctype'] = t; w.writerow(r)
