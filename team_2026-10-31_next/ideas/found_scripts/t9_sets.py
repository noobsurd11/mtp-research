import collections
from pathlib import Path
RF = Path("/home/noob/work/calib/data/rf"); POOL = Path("/home/noob/work/el-fault-detection/data/unlabeled/images_512")
SP = Path("/home/noob/work/el_f3/data/splits")
mod = lambda s: "_".join(s.split("_")[:2])
pool = [p.stem for p in POOL.glob("*.png")]; pm = collections.Counter(mod(p) for p in pool); ps = set(pool)
train_mods = {mod(l.strip()) for l in open(SP / "train.txt") if l.strip()}
rows = [l.rstrip("\n").split("\t") for l in open(RF / "rf_context.tsv") if l.strip()]
hdr, rows = rows[0], rows[1:]
H = {h: i for i, h in enumerate(hdr)}
groups = collections.defaultdict(list)
for r in rows:
    s = r[0]; hc = r[H["halfcut"]] == "1"; m = mod(s)
    g = "H36" if hc else ("F51" if m not in train_mods else "F19")
    groups[g].append((s, int(r[H["crack_px"]]), int(r[H["inact_px"]]), pm.get(m, 0), s[:-3] in ps, m))
for g in ("H36", "F51", "F19"):
    L = groups[g]
    ok = [x for x in L if x[3] >= 20 and x[4]]
    print(f"{g}: cells {len(L)}, crack>=20 cells {sum(1 for x in L if x[1]>=20)}, crack px {sum(x[1] for x in L)}, inact cells {sum(1 for x in L if x[2]>0)}, "
          f"modules {len({x[5] for x in L})}; with pool copy AND >=20 siblings: cells {len(ok)}, crack>=20 cells {sum(1 for x in ok if x[1]>=20)}, "
          f"crack px {sum(x[1] for x in ok)}, modules {len({x[5] for x in ok})}, crack modules {len({x[5] for x in ok if x[1]>=20})}")
    print("   no pool copy:", [x[0] for x in L if not x[4]])
