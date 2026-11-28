"""x4 step 2: compare the positive-control reads with the recorded c3x read. Prints IDENTICAL / DIFF with counts.
(a) vs /home/noob/work/bench_reads/c3x/read/read.json, both cell blocks: contrasts COMBO - PF and COMBO_SWAD - PF (every
    field), A/A, M, summary / per_seed / choices of PF, COMBO, COMBO_SWAD, crackfree; and the verdict lines that c3x_verdict.py
    writes for these two arms against PF, against the recorded verdict.txt.
(b) M equals (a)'s M in both blocks; 2-seed contrasts printed.
(c) OP-A point deltas of PFX - COMBO equal minus (b)'s COMBO_SWAD - PF (same dumps, same seeds 5, 6).
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c3x_verdict as cv  # noqa: E402

R = Path("/home/noob/work/bench_reads")
REC = json.loads((R / "c3x/read/read.json").read_text())
A = json.loads((R / "x4_posctl_a/read/read.json").read_text())
B = json.loads((R / "x4_posctl_b/read/read.json").read_text())
C = json.loads((R / "x4_posctl_c/read/read.json").read_text())
ARMS = ("PF", "COMBO", "COMBO_SWAD")


def leaves(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f"{p}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f"{p}[{i}]")
    else:
        yield p, x


def same(a, b):
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b


def cmp(name, x, y):
    lx, ly = dict(leaves(x)), dict(leaves(y))
    keys = set(lx) | set(ly)
    nd = sum(1 for k in keys if k not in lx or k not in ly or not same(lx[k], ly[k]))
    print(f"{'IDENTICAL' if nd == 0 else 'DIFF'}\t{name}\t{len(keys)} values, {nd} differ")
    return nd == 0


ok = True
print("== (a) 5 seeds against the recorded c3x read")
for blk in ("", "x416"):
    r, a = (REC, A) if not blk else (REC[blk], A[blk])
    t = blk or "532"
    for c in ("COMBO - PF", "COMBO_SWAD - PF"):
        ok &= cmp(f"{t} contrast {c}", r["contrasts"][c], a["contrasts"][c])
    for k in ("aa", "M", "crackfree"):
        ok &= cmp(f"{t} {k}", r.get(k), a.get(k))
    for arm in ARMS:
        ok &= cmp(f"{t} summary {arm}", r["summary"][arm], a["summary"][arm])
        ok &= cmp(f"{t} per_seed {arm}", r["per_seed"][arm], a["per_seed"][arm])
        ok &= cmp(f"{t} choices {arm}", {k: v for k, v in r["choices"].items() if k.split("|")[0] == arm},
                  {k: v for k, v in a["choices"].items() if k.split("|")[0] == arm})
rec_lines = set((R / "c3x/verdict.txt").read_text().splitlines())
cv.BASE = "PF"
n = miss = 0
for arm in ("COMBO", "COMBO_SWAD"):
    for tag, D in (("532 cells", A), ("416 clean cells", A["x416"])):
        for okk, text in cv.headline(D, arm, tag):
            n += 1; miss += (("PASS" if okk else "FAIL") + "\t" + text) not in rec_lines
        for okk, kind, lab, text in cv.guards(D, arm, tag):
            n += 1; miss += (("PASS" if okk else "FAIL") + "\t" + text) not in rec_lines
print(f"{'IDENTICAL' if miss == 0 else 'DIFF'}\tverdict lines (headline + guards, COMBO and COMBO_SWAD vs PF): {n} lines, {miss} not in the recorded verdict.txt")
ok &= miss == 0
v = A["contrasts"]["COMBO - PF"]["OP-A"]["metrics"]["relF1_2"]
print(f"(a) COMBO - PF relF1@2, 532, OP-A, 5 seeds: {v['delta']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}] (recorded +0.0154 [+0.0065, +0.0260])")
v = A["contrasts"]["COMBO_SWAD - PF"]["OP-A"]["metrics"]["relF1_2"]
print(f"(a) COMBO_SWAD - PF relF1@2, 532, OP-A, 5 seeds: {v['delta']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}] (recorded +0.0166 [+0.0082, +0.0263])")

print("== (b) 2 seeds (5, 6)")
for blk in ("", "x416"):
    a, b = (A, B) if not blk else (A[blk], B[blk])
    ok &= cmp(f"{blk or '532'} M of PFAA 5,6 v 7,8 = M of (a)", a["M"], b["M"])
for blk, D in (("532", B), ("416", B["x416"])):
    for c in ("COMBO - PF", "COMBO_SWAD - PF"):
        for op in ("OP-A", "OP-W"):
            v = D["contrasts"][c][op]["metrics"]["relF1_2"]
            print(f"(b) {c} relF1@2, {blk}, {op}, seeds 5, 6: {v['delta']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}], M {D['M']['relF1_2']:.4f}")

print("== (c) x4 read form: PFX (= PF s5, s6) - COMBO (= COMBO_SWAD s5, s6), base COMBO")
nd = nt = 0
for blk in ("", "x416"):
    b, c = (B, C) if not blk else (B[blk], C[blk])
    for k, vb in b["contrasts"]["COMBO_SWAD - PF"]["OP-A"]["metrics"].items():
        vc = c["contrasts"]["PFX - COMBO"]["OP-A"]["metrics"][k]
        nt += 1
        if not (vb["delta"] is None and vc["delta"] is None) and not (
                vb["delta"] is not None and vc["delta"] is not None and abs(vb["delta"] + vc["delta"]) <= 1e-12):
            nd += 1
print(f"{'IDENTICAL' if nd == 0 else 'DIFF'}\t(c) OP-A point deltas = minus (b): {nt} values, {nd} differ")
ok &= nd == 0
for blk, D in (("532", C), ("416", C["x416"])):
    for op in ("OP-A", "OP-W"):
        v = D["contrasts"]["PFX - COMBO"][op]["metrics"]["relF1_2"]
        print(f"(c) PFX - COMBO relF1@2, {blk}, {op}: {v['delta']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}], M {D['M']['relF1_2']:.4f}")
print("POSITIVE CONTROL: " + ("IDENTICAL" if ok else "DIFF"))
sys.exit(0 if ok else 1)
