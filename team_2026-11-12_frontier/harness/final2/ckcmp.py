"""Compare two training-state files (latest.pth) or two metrics.json files; print only PATHS that differ, never values.
  python ckcmp.py pth A B [--allow regex ...]     python ckcmp.py json A B [--allow regex ...]
Counts tensors compared per top-level key; rc 0 iff every differing path matches an --allow regex."""
import json
import re
import sys

import numpy as np
import torch


def walk(a, b, path, out, cnt):
    if isinstance(a, torch.Tensor) or isinstance(b, torch.Tensor):
        cnt[path.split("/")[1] if "/" in path else path] = cnt.get(path.split("/")[1] if "/" in path else path, 0) + 1
        if not (isinstance(a, torch.Tensor) and isinstance(b, torch.Tensor) and a.dtype == b.dtype and a.shape == b.shape
                and torch.equal(a, b)):
            out.append(path)
        return
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        if not (isinstance(a, np.ndarray) and isinstance(b, np.ndarray) and np.array_equal(a, b)):
            out.append(path)
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                out.append(f"{path}/{k}(missing in {'A' if k not in a else 'B'})")
            else:
                walk(a[k], b[k], f"{path}/{k}", out, cnt)
        return
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            out.append(f"{path}(len {len(a)} vs {len(b)})")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", out, cnt)
        return
    if isinstance(a, float) and isinstance(b, float) and a != a and b != b:
        return
    if a != b:
        out.append(path)


def main():
    kind, A, B = sys.argv[1:4]
    allow = [re.compile(x) for i, x in enumerate(sys.argv[4:]) if sys.argv[4 + i - 1] == "--allow" and i > 0] if False else []
    args = sys.argv[4:]
    allow = [re.compile(args[i + 1]) for i in range(len(args)) if args[i] == "--allow"]
    if kind == "pth":
        a = torch.load(A, map_location="cpu", weights_only=False)
        b = torch.load(B, map_location="cpu", weights_only=False)
    else:
        a, b = json.load(open(A)), json.load(open(B))
    out, cnt = [], {}
    walk(a, b, "", out, cnt)
    bad = [p for p in out if not any(r.search(p) for r in allow)]
    ok = [p for p in out if any(r.search(p) for r in allow)]
    if kind == "pth":
        print(f"step A {a.get('step')} B {b.get('step')}; models keys A {sorted(a['models'])} B {sorted(b['models'])}")
        print("tensors compared per top-level key: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())))
    print(f"differing paths: {len(out)} ({len(ok)} allowed, {len(bad)} not allowed)")
    for p in ok[:15]:
        print(f"  allowed: {p}")
    for p in bad[:30]:
        print(f"  NOT ALLOWED: {p}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
