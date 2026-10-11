# Download every file of HF snt-ubix/escdd at a pinned revision and verify sizes and LFS sha256.
import json, os, sys, hashlib, urllib.request, urllib.parse, concurrent.futures as cf
API, OUT = sys.argv[1], sys.argv[2]
d = json.load(open(API)); rev = d['sha']
def get(s):
    f = s['rfilename']; p = os.path.join(OUT, f)
    os.makedirs(os.path.dirname(p) or OUT, exist_ok=True)
    if not os.path.exists(p) or os.path.getsize(p) != s.get('size'):
        urllib.request.urlretrieve(f"https://huggingface.co/datasets/snt-ubix/escdd/resolve/{rev}/{urllib.parse.quote(f)}", p)
    b = open(p, 'rb').read(); ok = len(b) == s.get('size')
    if 'lfs' in s: ok &= hashlib.sha256(b).hexdigest() == s['lfs']['sha256']
    return f, ok
with cf.ThreadPoolExecutor(16) as ex: res = list(ex.map(get, d['siblings']))
bad = [f for f, ok in res if not ok]
print('rev', rev, 'files', len(res), 'bad', len(bad), bad[:5])
