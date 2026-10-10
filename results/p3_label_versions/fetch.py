import json, os, sys, urllib.request, concurrent.futures as cf
SP, LOCAL = sys.argv[1], sys.argv[2]
d = json.load(urllib.request.urlopen("https://huggingface.co/api/datasets/snt-ubix/escdd"))
fs = [s['rfilename'] for s in d['siblings'] if s['rfilename'].startswith('el_')]
local = {}
for split, sub in [('train','masks_coded_train_original'),('val','masks_coded_val'),('test','masks_coded_test')]:
    for n in os.listdir(os.path.join(LOCAL, sub)): local[n] = split
esc = {}
for f in fs:
    kind, split = f.split('/')[0].split('_')[1], f.split('/')[0].split('_')[2]
    esc.setdefault(os.path.basename(f), {})[kind] = (split, f)
over = [n for n in esc if n in local]
print('escdd images', sum(1 for v in esc.values() if 'images' in v), 'local', len(local), 'overlap', len(over))
moved = [(n, local[n], esc[n]['masks'][0]) for n in over if local[n] != esc[n]['masks'][0]]
print('split changes', len(moved), moved[:8])
todo = [esc[n]['masks'][1] for n in over] + [esc[n]['images'][1] for n in over]
out = os.path.join(SP, 'escdd_data')
def get(f):
    p = os.path.join(out, f)
    if os.path.exists(p): return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    urllib.request.urlretrieve("https://huggingface.co/datasets/snt-ubix/escdd/resolve/main/" + f, p)
with cf.ThreadPoolExecutor(16) as ex: list(ex.map(get, todo))
json.dump({'over': over, 'local_split': local, 'esc': esc}, open(os.path.join(SP, 'escdd_code', 'index.json'), 'w'))
print('downloaded', len(todo))
