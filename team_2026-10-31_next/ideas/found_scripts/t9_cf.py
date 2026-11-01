import collections
from pathlib import Path
RF = Path("/home/noob/work/calib/data/rf"); POOL = Path("/home/noob/work/el-fault-detection/data/unlabeled/images_512")
mod = lambda s: "_".join(s.split("_")[:2])
pool = [p.stem for p in POOL.glob("*.png")]; pm = collections.Counter(mod(p) for p in pool); ps = set(pool)
tm = {mod(l.strip()) for l in open("/home/noob/work/el_f3/data/splits/train.txt") if l.strip()}
rows = [l.rstrip("\n").split("\t") for l in open(RF / "rf_context.tsv") if l.strip()]; H = {h: i for i, h in enumerate(rows[0])}
for g, sel in (("H36", lambda r: r[H["halfcut"]] == "1"), ("P", lambda r: r[H["halfcut"]] != "1" and mod(r[0]) not in tm), ("F19", lambda r: r[H["halfcut"]] != "1" and mod(r[0]) in tm)):
    L = [r for r in rows[1:] if sel(r) and r[0][:-3] in ps and pm.get(mod(r[0]), 0) >= 20]
    cp = [int(r[H["crack_px"]]) for r in L]
    print(g, "eligible", len(L), "crack px == 0:", sum(1 for c in cp if c == 0), "1-19 px:", sum(1 for c in cp if 0 < c < 20), ">=20:", sum(1 for c in cp if c >= 20), "sibling imgs:", sum(pm[m] for m in {mod(r[0]) for r in L}))
