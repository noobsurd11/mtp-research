"""Shape test of w2b_verdict.py on REAL tool outputs (w2b builder, 17 Nov 2026). Mechanics only: the finished wave 2a
read (/home/noob/work/bench_reads/w2a, published in results/W2A_READ.md) stands in for a w2b read, with its arms renamed
(RCS -> LACE / LCI / LCIARG, PF -> PF and PFC); w2b_counts.py is run on it for 532 and 416 cells. Checks only that the
verdict tool reads the real read.json (contrasts, M, x416, summary per source) and the real w2b_counts JSON without a
key error and prints every element line and one VERDICT line. Prints no number. Usage: python w2b_verdict_shape_test.py <scratch dir>
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w2b_verdict as W  # noqa: E402

RD = Path("/home/noob/work/bench_reads/w2a")
X = "/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/score_exclude_v3.txt"
tmp = Path(sys.argv[1])
assert not (tmp / "c532.txt").exists()
for tag, extra in (("c532", []), ("c416", ["--exclude", X])):
    subprocess.run([sys.executable, str(HERE / "w2b_counts.py"), "--read", str(RD), "--pair", "PF=RCS", "--pair", "RAWBN=EMA:paired",
                    "--classes", "0,1,2,4,5,7,11,13,14,15,16,20,21", "--boot", "200", *extra, "--out", str(tmp / f"{tag}.txt")],
                   check=True, stdout=subprocess.DEVNULL)
doc = json.loads((RD / "read" / "read.json").read_text())


def rename_doc(d, arm):
    c = d["contrasts"]["RCS - PF"]
    s = d["summary"]
    return {"M": d["M"], "contrasts": {f"{arm} - PFC": c, f"{arm} - PF": c}, "summary": {"PF": s["PF"], arm: s["RCS"]}}


def rename_counts(j, arm):
    p = j["points"]
    out = {"excluded": j["excluded"], "points": {"PF": p["PF"], "PFC": p["PF"], arm: p["RCS"], "LCIARG": p["PF"]},
           "contrasts": {f"{arm} - PFC": j["contrasts"]["RCS - PF"], "LCI - LCIARG": j["contrasts"]["EMA - RAWBN"]}}
    return out


ok_all = True
c5, c4 = (json.loads((tmp / f"{t}.txt.json").read_text()) for t in ("c532", "c416"))
for arm, fn, want in (("LACE", W.verdict_lace, ("P1 532", "P2 416", "G1 relF1_2 OP-W", "G5 px on cells without class")),
                      ("LCI", W.verdict_lci, ("L1 416", "L6 mechanism", "L7 width CSIR", "L7 false crack px"))):
    d = rename_doc(doc, arm)
    d["x416"] = rename_doc(doc["x416"], arm)
    v = fn(d, rename_counts(c5, arm), rename_counts(c4, arm))
    ok = all(w in v.res for w in want) and v.lines[-1].startswith("VERDICT ") and sum(l.startswith("VERDICT") for l in v.lines) == 1
    ok_all &= ok
    print(f"{'OK  ' if ok else 'FAIL'} {arm}: {len(v.res)} element lines, one VERDICT line, real read.json / counts JSON shapes read")
print("SHAPE TEST " + ("PASS" if ok_all else "FAIL"))
sys.exit(0 if ok_all else 1)
