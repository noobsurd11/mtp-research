"""Track M (protocol_r2 F2): summarise logged pre-clip grad norm and clip rate from training stdout logs.
Usage: python m_gradnorm.py <stdout> ...   -> per run: mean grad_norm and clip rate over steps 1-2k, 2k-10k, 10k-20k, all.
"""
import re, sys
import numpy as np

pat = re.compile(r"step (\d+)/20000 .*grad_norm=([0-9.e+-]+)\s+clipped=([0-9.e+-]+)")
print("run | phase | mean grad_norm | clip rate | windows")
for f in sys.argv[1:]:
    rows = [(int(m.group(1)), float(m.group(2)), float(m.group(3))) for m in map(pat.search, open(f)) if m]
    a = np.array(rows) if rows else np.zeros((0, 3))
    for nm, lo, hi in (("1-2k", 0, 2000), ("2k-10k", 2000, 10000), ("10k-20k", 10000, 20000), ("all", 0, 20000)):
        k = (a[:, 0] > lo) & (a[:, 0] <= hi) if len(a) else np.zeros(0, bool)
        if k.any():
            print(f"{f.split('/')[-1]} | {nm} | {a[k, 1].mean():.3f} | {a[k, 2].mean():.3f} | {int(k.sum())}")
