"""found, 1 Nov 2026: compare the step lines ('step N/T loss=... lr=...') and 'PF encoder lr=... at step N' lines of two
training stdouts for steps <= MAX (timestamps and steps_per_sec stripped). Reads only those two line types (never any
TEST / val block). Usage: python stepcmp.py A.stdout B.stdout MAX"""
import re
import sys

STEP = re.compile(r"step (\d+)/\d+\s+(.*?)\s+steps_per_sec=")
PF = re.compile(r"PF encoder lr=(\S+) at step (\d+)")


def parse(path, mx):
    st, pf = {}, {}
    for line in open(path, errors="replace"):
        m = STEP.search(line)
        if m and int(m.group(1)) <= mx:
            st[int(m.group(1))] = m.group(2)
            continue
        m = PF.search(line)
        if m and int(m.group(2)) <= mx:
            pf[int(m.group(2))] = m.group(1)
    return st, pf


a, b, mx = sys.argv[1], sys.argv[2], int(sys.argv[3])
(sa, pa), (sb, pb) = parse(a, mx), parse(b, mx)
ks, kp = sorted(set(sa) & set(sb)), sorted(set(pa) & set(pb))
ds = [k for k in ks if sa[k] != sb[k]]
dp = [k for k in kp if pa[k] != pb[k]]
print(f"step lines: A {len(sa)} B {len(sb)} common {len(ks)} differ {len(ds)}"
      + (f" first {ds[0]}: A '{sa[ds[0]]}' B '{sb[ds[0]]}'" if ds else ""))
print(f"PF lr lines: A {len(pa)} B {len(pb)} common {len(kp)} differ {len(dp)}"
      + (f" first {dp[0]}: A {pa[dp[0]]} B {pb[dp[0]]}" if dp else ""))
print("IDENTICAL" if not ds and not dp and len(ks) == len(sa) == len(sb) and len(kp) == len(pa) == len(pb) else "DIFFER")
