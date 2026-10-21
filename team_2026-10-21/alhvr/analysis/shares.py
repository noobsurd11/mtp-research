"""Activity / routing watch from AL1 training logs (protocol_v2 §7). Usage: python shares.py <experiments dir> <lo> <hi> [runs...]
Two-network runs: mean share_a (= λ·L_u/L_sup), gshare_a, region fractions, disagreement over logged steps in [lo, hi].
BsM5 runs: mean λ·loss_con/loss_sup."""
import re, sys, glob, os
d, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
runs = sys.argv[4:] or sorted(os.path.basename(p)[:-7] for p in glob.glob(f"{d}/al1_*.stdout"))
kv = re.compile(r"(\w+)=([-0-9.e+naif]+)")
for r in runs:
    rows, gs = [], []
    for line in open(f"{d}/{r}.stdout"):
        m = re.search(r"trainer — step (\d+)/20000  (.*)", line)
        if m and lo <= int(m.group(1)) <= hi:
            rows.append({k: float(v) for k, v in kv.findall(m.group(2))})
        g = re.search(r"grad share @ step (\d+)  .*gshare_a=([-0-9.e+naif]+)", line)
        if g and lo <= int(g.group(1)) <= hi:
            gs.append(float(g.group(2)))
    if not rows:
        print(f"{r:16s} no rows in [{lo},{hi}]"); continue
    mean = lambda k: sum(x[k] for x in rows) / len(rows)
    last = max(int(x.get("step", 0)) for x in rows) if rows and "step" in rows[0] else None
    if "share_a" in rows[0]:
        r23 = sum(x["frac_r2a"] + x["frac_r2b"] + x["frac_r3"] for x in rows) / len(rows)
        print(f"{r:16s} n={len(rows):3d} lambda={mean('lambda'):.3f} share_a={mean('share_a'):.4f} gshare_a={sum(gs)/len(gs) if gs else float('nan'):.3f} "
              f"sup_a={mean('sup_a'):.4f} frac_r2+r3={r23:.4f} r3={mean('frac_r3'):.4f} disagree={mean('disagree'):.4f} gamma={mean('gamma'):.4f}")
    else:
        sh = sum(x["lambda"] * x["loss_con"] / x["loss_sup"] for x in rows) / len(rows)
        print(f"{r:16s} n={len(rows):3d} lambda={mean('lambda'):.3f} share={sh:.4f} conf_frac={mean('conf_frac'):.4f} loss_sup={mean('loss_sup'):.4f}")
