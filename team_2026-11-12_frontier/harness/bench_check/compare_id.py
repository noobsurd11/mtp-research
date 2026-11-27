"""Compare two identity_cpu.py records. Prints IDENTICAL or DIFF with counts only (no values).
Ignored: 'code' and per-step 'sec'. 'opts' must be equal (same arm)."""
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
diffs = []
def walk(x, y, path):
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y)):
            if k in ("code", "sec"):
                continue
            if k not in x or k not in y:
                diffs.append(path + "/" + k + " (missing)"); continue
            walk(x[k], y[k], path + "/" + k)
    elif isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            diffs.append(path + " (length)"); return
        for i, (u, v) in enumerate(zip(x, y)):
            walk(u, v, f"{path}[{i}]")
    elif x != y:
        diffs.append(path)
walk(a, b, "")
nsteps = len(a.get("steps", []))
if diffs:
    print(f"DIFF {len(diffs)} fields (steps {nsteps}); first paths: {diffs[:5]}")
    sys.exit(1)
print(f"IDENTICAL ({nsteps} steps, all fields except code / sec)")
