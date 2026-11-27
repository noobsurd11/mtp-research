"""integrator c3base: the 50 job lines of the cv5v3 baselines, seed-major (seed 5: PF f0-f4, HOUSE f0-f4; then seeds 6, 7, 8, 9).
Usage: make_jobs.py cv02 <out jobs.txt>            (cq.sh format: name|card|seed|root|fold|gate|dump_gate|logp|extra)
       make_jobs.py gaint <out jobs.txt> <out dump jobs.txt>   (bench_q format: name|card|seed|root|gate|cmd|extra)
Gates: cv02 training 9,000 = card gate (measured wave 1 peak on cv02 5,740 MiB + 2,048 = 7,788 is below it and cq.sh refuses a
gate below the card's), cv02 dump 3,214 + 2,048 = 5,262 (measured W1-C dump peak, --logp); gaint 9,000 / 6,200 as W1-G and udev
(gaint peaks 6,830 + 2,048 = 8,878 -> card gate; W1-G dumps with logp 4,098 + 2,048 = 6,146 -> 6,200)."""
import sys

ARMS = (("pf", "house_r34_unetpp_pf_v11"), ("house", "house_r34_unetpp_v11"))
SEEDS, FOLDS = (5, 6, 7, 8, 9), (0, 1, 2, 3, 4)
PY = "/home/noob/work/el-fault-detection/.venv/bin/python"
GREPO, GDUMPS = "/home/noob/work/bench_wt_final", "/home/noob/work/bench_c3base/dumps"


def tuples():
    for s in SEEDS:
        for tag, card in ARMS:
            for k in FOLDS:
                yield f"c3_{tag}_v11_f{k}_s{s}", card, s, k


def main():
    mode = sys.argv[1]
    lines, dlines = [], []
    for name, card, s, k in tuples():
        c = f"bench/methods/{card}.yaml"
        if mode == "cv02":
            lines.append(f"{name}|{c}|{s}|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f{k}|{k}|9000|5262|1|")
        else:
            root = f"/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f{k}"
            lines.append(f"{name}|{c}|{s}|{root}|9000||")
            dlines.append(f"dump_{name}|-|{s}|{root}|6200|{PY} -u scripts/bench_infer.py --run {GREPO}/experiments/{name} "
                          f"--set cv5v3_f{k} --dumps {GDUMPS} --method {card} --card {c} --run-id {name} --device cuda "
                          f"--precision fp32 --threads 4 --workers 4 --batch 8 --logp --bench-run dump_{name}|")
    assert len(lines) == 50 and len({ln.split('|')[0] for ln in lines}) == 50
    open(sys.argv[2], "w").write("".join(x + "\n" for x in lines))
    if mode == "gaint":
        open(sys.argv[3], "w").write("".join(x + "\n" for x in dlines))


if __name__ == "__main__":
    main()
