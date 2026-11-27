"""Compare two dump folders cell by cell (w2b builder). Prints IDENTICAL or DIFF with counts only (no values).
Arrays: every key of every cell must be equal (dtype, shape, bytes). Manifest: equal except the fields that name the
code or the time (code_repo, code_commit, writer, written, card, card_md5, cells: per-file md5s of the compressed npz
differ by zip timestamps). Usage: python dump_compare.py <set dir A> <set dir B>
"""
import json
import sys
from pathlib import Path

import numpy as np

A, B = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, sys.argv[3] if len(sys.argv) > 3 else "/home/noob/work/bench_wt_w2b")
from bench import dumpfmt  # noqa: E402

fa, fb = sorted(p.name for p in A.glob("*.npz")), sorted(p.name for p in B.glob("*.npz"))
diffs = []
if fa != fb:
    diffs.append(f"cell lists differ ({len(fa)} vs {len(fb)})")
nk = 0
for f in sorted(set(fa) & set(fb)):
    a, b = dumpfmt.read_cell(A / f), dumpfmt.read_cell(B / f)
    if set(a) != set(b):
        diffs.append(f"{f}: keys"); continue
    for k in a:
        nk += 1
        if a[k].dtype != b[k].dtype or a[k].shape != b[k].shape or a[k].tobytes() != b[k].tobytes():
            diffs.append(f"{f}:{k}")
ma, mb = (json.loads((d / "manifest.json").read_text()) for d in (A, B))
SKIP = {"code_repo", "code_commit", "writer", "written", "card", "card_md5", "cells", "bytes_total"}
ARR = __import__("os").environ.get("ARRAYS_ONLY") == "1"   # two different runs / readouts: compare the arrays only
mk = sorted(k for k in set(ma) | set(mb) if k not in SKIP and ma.get(k, "<absent>") != mb.get(k, "<absent>"))
if mk and not ARR:
    diffs.append(f"manifest fields {mk}")
if diffs:
    print(f"DIFF {len(diffs)} ({len(fa)} cells, {nk} arrays); first: {diffs[:5]}")
    sys.exit(1)
print(f"IDENTICAL ({len(fa)} cells, {nk} arrays; " + ("arrays only; manifests not compared" if ARR else
      f"manifest equal except {sorted(SKIP)}") + ")")
