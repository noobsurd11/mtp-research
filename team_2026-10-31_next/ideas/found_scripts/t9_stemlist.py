import collections
from pathlib import Path
RF = Path("/home/noob/work/calib/data/rf"); POOL = Path("/home/noob/work/el-fault-detection/data/unlabeled/images_512")
mod = lambda s: "_".join(s.split("_")[:2])
pool = [p.stem for p in POOL.glob("*.png")]; pm = collections.Counter(mod(p) for p in pool); ps = set(pool)
tm = {mod(l.strip()) for l in open("/home/noob/work/el_f3/data/splits/train.txt") if l.strip()}
rows = [l.rstrip("\n").split("\t") for l in open(RF / "rf_context.tsv") if l.strip()]; H = {h: i for i, h in enumerate(rows[0])}
out = ["stem\tset\teligible\tmodule\tn_pool_module\thas_pool_copy\tcrack_px"]
for r in rows[1:]:
    s = r[0]; hc = r[H["halfcut"]] == "1"; m = mod(s)
    g = "H36" if hc else ("F51" if m not in tm else "F19")
    el = int(s[:-3] in ps and pm.get(m, 0) >= 20)
    out.append(f"{s}\t{g}\t{el}\t{m}\t{pm.get(m, 0)}\t{int(s[:-3] in ps)}\t{r[H['crack_px']]}")
open("/home/noob/work/found/t9/rf_sets.tsv", "w").write("\n".join(out) + "\n")
print(len(out) - 1, collections.Counter(l.split("\t")[1] for l in out[1:]), "eligible", sum(int(l.split("\t")[2]) for l in out[1:]))
