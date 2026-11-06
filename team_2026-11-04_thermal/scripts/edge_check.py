"""Numeric edge check (pick1 v2 QA criterion 5). usage: python -I edge_check.py <run_dir> <out.tsv>
Edge offset per side = registered grid edge (grid_corners) minus module outline edge (quad), in cell sides, positive = grid inside the outline.
Fail if |offset - set median for that side and modality| > 0.25 cell. Reads reg.json only."""
import glob, json, os, sys
import numpy as np
d, out = sys.argv[1:3]
rows = []
for f in sorted(glob.glob(os.path.join(d, "*_reg.json"))):
    R = json.load(open(f))
    for mod in ("el", "ir"):
        q = R["modalities"][mod]["qa"]
        Q = np.array(q["quad"], float); G = np.array(q["grid_corners"], float)   # TL, TR, BR, BL (image x, y)
        gw = np.mean([np.linalg.norm(G[1] - G[0]), np.linalg.norm(G[2] - G[3])])
        gh = np.mean([np.linalg.norm(G[3] - G[0]), np.linalg.norm(G[2] - G[1])])
        nr, nc = q["rows"], q["cols"]
        nx, ny = (max(nr, nc), min(nr, nc)) if gw >= gh else (min(nr, nc), max(nr, nc))
        cw, ch = gw / nx, gh / ny
        off = {"top": (np.mean(G[[0, 1], 1]) - np.mean(Q[[0, 1], 1])) / ch,
               "bottom": (np.mean(Q[[3, 2], 1]) - np.mean(G[[3, 2], 1])) / ch,
               "left": (np.mean(G[[0, 3], 0]) - np.mean(Q[[0, 3], 0])) / cw,
               "right": (np.mean(Q[[1, 2], 0]) - np.mean(G[[1, 2], 0])) / cw}
        rows.append((R["module"], mod, off))
med = {}
for mod in ("el", "ir"):
    for side in ("top", "bottom", "left", "right"):
        med[(mod, side)] = float(np.median([o[side] for m, md, o in rows if md == mod]))
with open(out, "w") as f:
    f.write("module\tmodality\ttop\tbottom\tleft\tright\tmax_dev\tedge_call\n")
    for m, mod, o in rows:
        dev = {s: o[s] - med[(mod, s)] for s in o}
        mx = max(dev.values(), key=abs)
        f.write("\t".join([m, mod] + ["%+.3f" % o[s] for s in ("top", "bottom", "left", "right")] + ["%+.3f" % mx, "FAIL" if abs(mx) > 0.25 else "ok"]) + "\n")
    f.write("# set medians (cell sides): " + "; ".join("%s %s %+.3f" % (k[0], k[1], v) for k, v in med.items()) + "\n")
print(out)
