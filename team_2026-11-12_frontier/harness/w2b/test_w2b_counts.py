"""Reproduction test of w2b_counts.py against the reviewed read tool (w2b builder). Runs w2b_counts on the finished
wave 2a read folder (/home/noob/work/bench_reads/w2a, read 17 Nov 08:36, results already published in results/W2A_READ.md)
and checks, without printing any number: (1) its R5 (inactive IoU), R3 (inactive precision) and R1 (region recall) point
values for PF and RCS equal bench_read_w1's summary values (OP-A, all cells) to 6e-7 (6 dp printed); (2) its PF=RCS contrast on R5 has
the same delta, 2.5% and 97.5% bounds as bench_read_w1's PF=RCS inact_iou contrast at OP-A (same draw order, seed 0).
Prints PASS / FAIL per item. Usage: python test_w2b_counts.py <scratch dir>
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RD = Path("/home/noob/work/bench_reads/w2a")
out = Path(sys.argv[1]) / "w2b_counts_test.txt"
assert not out.exists(), out
subprocess.run([sys.executable, str(HERE / "w2b_counts.py"), "--read", str(RD), "--pair", "PF=RCS", "--out", str(out)],
               check=True, stdout=subprocess.DEVNULL)
L = out.read_text().splitlines()
hdr = L[1].split("\t")
pts = {l.split("\t")[0]: dict(zip(hdr[2:], map(float, l.split("\t")[2:]))) for l in L[2:] if l and "\t" in l and
       l.split("\t")[0] in ("PF", "RCS", "PFAA", "RAWBN", "EMA", "JMLHARD", "SWADBN")}
doc = json.loads((RD / "read" / "read.json").read_text())
ok_all = True
for arm in ("PF", "RCS"):
    s = doc["summary"][arm]["OP-A"]["all"]
    for mine, theirs in (("R5_inact_iou", "inact_iou"), ("R3_inact_prec", "inact_prec"), ("R1_region_recall", "in_cc_rec50")):
        ok = abs(pts[arm][mine] - s[theirs]["mean"]) < 6e-7
        ok_all &= ok
        print(f"point {arm} {mine} = read tool {theirs}: {'PASS' if ok else 'FAIL'}")
ci = doc["contrasts"]["RCS - PF"]["OP-A"]["metrics"]["inact_iou"]     # read.json: contrasts["B - A"][op]["metrics"]
row = [l for l in L if l.startswith("R5_inact_iou\t") and "[" in l][0]
d, lo, hi = row.split("\t")[1].replace("[", "").replace("]", "").replace(",", "").split()[:3]
ok = abs(float(d) - ci["delta"]) < 5e-5 and abs(float(lo) - ci["lo"]) < 5e-5 and abs(float(hi) - ci["hi"]) < 5e-5
ok_all &= ok
print(f"contrast PF=RCS R5 delta and 95% bounds = read tool inact_iou (4 dp): {'PASS' if ok else 'FAIL'}")
print("W2B_COUNTS TEST " + ("PASS" if ok_all else "FAIL"))
