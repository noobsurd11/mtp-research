# Download BenchmarkEL release originals (no flip_/mirror_/rotate_ copies) from GitHub at a pinned tree; verify git blob sha1.
import json, os, sys, re, hashlib, urllib.request, urllib.parse, concurrent.futures as cf
TREE, OUT, REL = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(TREE)); sha = d['sha']
todo = [t for t in d['tree'] if t['type'] == 'blob' and t['path'].startswith(REL + '/')
        and not re.match(r'(flip|mirror|rotate)_', os.path.basename(t['path']))]
def get(t):
    p = os.path.join(OUT, t['path']); os.makedirs(os.path.dirname(p), exist_ok=True)
    if not os.path.exists(p):
        urllib.request.urlretrieve(f"https://raw.githubusercontent.com/TheMakiran/BenchmarkELimages/{sha}/{urllib.parse.quote(t['path'])}", p)
    b = open(p, 'rb').read()
    return t['path'], hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest() == t['sha']
with cf.ThreadPoolExecutor(16) as ex: res = list(ex.map(get, todo))
bad = [f for f, ok in res if not ok]
print('tree', sha, REL, 'files', len(res), 'bad', len(bad), bad[:5])
