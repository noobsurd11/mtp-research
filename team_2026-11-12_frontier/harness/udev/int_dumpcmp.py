"""integrator udev: compare two bench_infer dump folders file by file (md5). Cell files must be byte-identical; for the
manifest / run files that name the code, prints which top-level JSON keys differ (no values).
Usage: int_dumpcmp.py <dir_a> <dir_b>; prints one line, rc 0 if every cell file is identical."""
import hashlib
import json
import sys
from pathlib import Path

a, b = Path(sys.argv[1]), Path(sys.argv[2])
fa = {p.relative_to(a): p for p in a.rglob("*") if p.is_file()}
fb = {p.relative_to(b): p for p in b.rglob("*") if p.is_file()}
md5 = lambda p: hashlib.md5(p.read_bytes()).hexdigest()  # noqa: E731
cells = sorted(k for k in fa if k.suffix == ".npz")
same = sum(1 for k in cells if k in fb and md5(fa[k]) == md5(fb[k]))
only = sorted(set(map(str, fa)) ^ set(map(str, fb)))
meta = []
for k in sorted(k for k in fa if k.suffix != ".npz"):
    if k not in fb:
        continue
    if md5(fa[k]) == md5(fb[k]):
        meta.append(f"{k}: same")
        continue
    try:
        ja, jb = json.loads(fa[k].read_text()), json.loads(fb[k].read_text())
        keys = sorted(x for x in set(ja) | set(jb) if ja.get(x) != jb.get(x))
        meta.append(f"{k}: keys differ {keys}")
    except Exception:  # noqa: BLE001
        meta.append(f"{k}: differs (not json)")
ok = bool(cells) and same == len(cells) and not [x for x in only if x.endswith(".npz")]
print(f"{'IDENTICAL' if ok else 'DIFF'} cell files {same} of {len(cells)} byte-identical; files only on one side {len(only)}; "
      f"other files: {'; '.join(meta)}")
sys.exit(0 if ok else 1)
