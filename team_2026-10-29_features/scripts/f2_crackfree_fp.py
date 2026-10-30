"""Crack px predicted on cells with no GT crack (coach request for CP5; test is the requested line, val and ext106 added
because only 2 of 50 test cells are crack-free), per run, two arms, tau 0 and tau 1.
From m0 per-cell confusions (rows GT, cols prediction, valid px only; class 14 = crack). CPU only.
Usage: python f2_crackfree_fp.py --a <dir> <prefix> --b <dir> <prefix> --labels A5c-f1 CP5 --out out.json
"""
import argparse
import json

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--a", nargs=2, required=True)
ap.add_argument("--b", nargs=2, required=True)
ap.add_argument("--labels", nargs=2, default=["A5c-f1", "CP5"])
ap.add_argument("--out", required=True)
a = ap.parse_args()
res = {}
SETS = ("test", "val", "ext")
for lab, (d, pre) in zip(a.labels, (a.a, a.b)):
    for t in ("", ".tau1"):
        for k in range(5):
            r = f"{pre}_s{k}"
            allc = json.load(open(f"{d}/{r}{t}.json"))["cells"]
            for st in SETS:
                cells = allc[st]
                cf = {s: np.array(v["conf"]).reshape(24, 24) for s, v in cells.items()}
                free = [s for s, c in cf.items() if c[14].sum() == 0]
                px = {s: int(cf[s][:, 14].sum()) for s in free}
                res[f"{st}/{r}{t or '.tau0'}"] = {"arm": lab, "set": st, "n_cells": len(cells), "n_crackfree_cells": len(free),
                                                  "crack_px": sum(px.values()),
                                                  "cells_with_crack_px": sum(v > 0 for v in px.values()), "per_cell": px}
json.dump(res, open(a.out, "w"), indent=1)
for st in SETS:
    for t in (".tau0", ".tau1"):
        for lab in a.labels:
            v = [res[k] for k in sorted(res) if k.startswith(st + "/") and k.endswith(t) and res[k]["arm"] == lab]
            print(f"{st:4s} {lab:7s}{t}: crack-free cells {v[0]['n_crackfree_cells']}/{v[0]['n_cells']}; crack px per run "
                  f"{[x['crack_px'] for x in v]} (mean {np.mean([x['crack_px'] for x in v]):.0f}); "
                  f"cells with any crack px {[x['cells_with_crack_px'] for x in v]}")
