"""x4 step 4 identity check: the logged training values of the first N steps of two runs (stdout 'step S/T' lines and the
'PF encoder' lines). Prints only IDENTICAL / DIFF with counts, the first differing step and the largest relative
difference (no loss values). steps_per_sec and timestamps are not compared.
Usage (on cv02, nothing written): python3 - A.stdout B.stdout N < x4_idcheck.py
"""
import re
import sys

a_path, b_path, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
STEP = re.compile(r"step (\d+)/(\d+)\s+(.*)$")


def rows(path):
    out, other = {}, []
    for line in open(path, errors="replace"):
        m = STEP.search(line)
        if m and " INFO " in line and "loss=" in line:
            s = int(m.group(1))
            if s <= N:
                kv = dict(x.split("=", 1) for x in m.group(3).split() if "=" in x)
                kv.pop("steps_per_sec", None)
                out[s] = (int(m.group(2)), kv)
        elif "PF encoder" in line:
            mm = re.search(r"at step (\d+)", line)
            if mm and int(mm.group(1)) <= N:
                other.append(line.split(" — ", 1)[-1].strip())
    return out, other


A, Ao = rows(a_path)
B, Bo = rows(b_path)
steps = sorted(set(A) | set(B))
miss = [s for s in steps if s not in A or s not in B]
nd, first, nval, rel = 0, None, 0, 0.0
for s in steps:
    if s in miss:
        continue
    (ta, ka), (tb, kb) = A[s], B[s]
    if ta != tb or set(ka) != set(kb):
        nd += 1; first = first or s; continue
    for k in ka:
        nval += 1
        if ka[k] != kb[k]:
            nd += 1; first = first or s
            try:
                x, y = float(ka[k]), float(kb[k])
                rel = max(rel, abs(x - y) / max(abs(x), abs(y), 1e-12))
            except ValueError:
                pass
print(f"steps <= {N}: {len(A)} lines in A, {len(B)} in B, {len(miss)} steps in one file only; {nval} values compared "
      f"(loss, loss_sup, loss_con, lambda, lr), {nd} differ; first differing step {first}; max relative difference {rel:.2e}")
po = "IDENTICAL" if Ao == Bo else "DIFF"
print(f"PF encoder lines <= step {N}: {len(Ao)} in A, {len(Bo)} in B: {po}")
ok = nd == 0 and not miss and len(A) > 0 and Ao == Bo
print("IDENTITY: " + ("IDENTICAL" if ok else "DIFF"))
sys.exit(0 if ok else 1)
