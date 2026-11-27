"""c3base checklist item 6 (own code, not make_jobs.py): rebuild the 50 expected job lines for both queues from the rule in
LAUNCH_REQUEST_c3base.md section 5 and compare with the files; print names / order / roots / gates / experiments checks.
Usage: c3_rv_jobs.py <cv02 jobs.txt copy> <gaint jobs.txt> <gaint dump/jobs.txt>"""
import hashlib
import os
import sys

cv, gt, gd = sys.argv[1:4]
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()  # noqa: E731
want = [(f"c3_{t}_v11_f{k}_s{s}", c, s, k) for s in range(5, 10)
        for t, c in (("pf", "house_r34_unetpp_pf_v11"), ("house", "house_r34_unetpp_v11")) for k in range(5)]
ecv = [f"{n}|bench/methods/{c}.yaml|{s}|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f{k}|{k}|9000|5262|1|" for n, c, s, k in want]
egt = [f"{n}|bench/methods/{c}.yaml|{s}|/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f{k}|9000||" for n, c, s, k in want]
egd = [f"dump_{n}|-|{s}|/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f{k}|6200|/home/noob/work/el-fault-detection/.venv/bin/python"
       f" -u scripts/bench_infer.py --run /home/noob/work/bench_wt_final/experiments/{n} --set cv5v3_f{k} --dumps "
       f"/home/noob/work/bench_c3base/dumps --method {c} --card bench/methods/{c}.yaml --run-id {n} --device cuda --precision "
       f"fp32 --threads 4 --workers 4 --batch 8 --logp --bench-run dump_{n}|" for n, c, s, k in want]
bad = 0
for tag, p, e in (("cv02", cv, ecv), ("gaint", gt, egt), ("gaint dump", gd, egd)):
    got = open(p).read().splitlines()
    same = got == e
    bad += not same
    print(f"{tag}: {p} md5 {md5(p)} lines {len(got)} names unique {len({x.split('|')[0] for x in got}) == len(got)} "
          f"= expected (order incl.) {same}")
seeds = [int(x.split("|")[2]) for x in open(cv).read().splitlines()]
print("seed-major:", seeds == sorted(seeds), "| per seed", {s: seeds.count(s) for s in sorted(set(seeds))},
      "| sealed words", sum(w in open(p).read() for p in (cv, gt, gd) for w in ("test50", "e1_106")))
ex = [n for n, *_ in want if os.path.exists(f"/home/noob/work/bench_wt_final/experiments/{n}")
      or os.path.exists(f"/home/noob/work/bench_wt_final/experiments/{n}.stdout")]
print("gaint experiments/<name> existing:", len(ex), "| gaint dump dir exists:", os.path.exists("/home/noob/work/bench_c3base"))
print("RESULT", "PASS" if not bad and not ex else "FAIL")
