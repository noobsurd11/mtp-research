"""T3b job lists (T3B_RULE.md sections 3 to 5, 9): cq.sh lines of commit K for the two cv02 queues.
  queue t3b (training, open mode; 33 lines):
    t3b_<arm>_f<k>_s<s>  arm all | half, k 0..4, seeds 5, 6, 7 (30 fold models); root DATA_T/roots/t3b_<arm>_f<k>, fold k
    t3b_deploy_s<s>      seeds 5, 6, 7 (3 deployable models, never scored on E1); root DATA_T/roots/t3b_deploy, fold 0
    card = the C2 card hrnet_w18_unetpp_swad_const_pf_v11 (fin's C2 lines: gate 11510, dump gate 6200, logp 0, 10th field
    'swad' = slim keeps swad_bn + swad); the chain makes no dump (in-sample monitor).
  queue t3bopen (sealed dump-only, Q/SEALED e1t3b_f0..4 at opening e1_open9_t3b; 30 lines, made after t3b ends):
    t3b_<arm>_f<k>_s<s>.swad.tta_d4.e1t3b_f<k> = --dumpof KB/experiments/t3b_<arm>_f<k>_s<s> --key swad --tta d4
    --set e1t3b_f<k> (the fold model's own held-out cells only; logp 0)
Order: seeds outer, then arm (all, half), then fold; the 3 deployable trainings last. Refuses an existing output.
Usage: python t3b_make_jobs.py --k <full commit K> --train OUT_TRAIN --dump OUT_DUMP
"""
import argparse
import re
import sys
from pathlib import Path

DT = "/tmp/noob_el/bench_data_t3b/roots"
CARD = "bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml"
GATE, DGATE = 11510, 6200
SEEDS = (5, 6, 7)
ARMS = ("all", "half")
K = 5


def train_lines() -> list[str]:
    out = []
    for s in SEEDS:
        for arm in ARMS:
            for k in range(K):
                out.append(f"t3b_{arm}_f{k}_s{s}|{CARD}|{s}|{DT}/t3b_{arm}_f{k}|{k}|{GATE}|{DGATE}|0||swad")
    for s in SEEDS:
        out.append(f"t3b_deploy_s{s}|{CARD}|{s}|{DT}/t3b_deploy|0|{GATE}|{DGATE}|0||swad")
    return out


def dump_lines(kb: str) -> list[str]:
    out = []
    for s in SEEDS:
        for arm in ARMS:
            for k in range(K):
                run = f"t3b_{arm}_f{k}_s{s}"
                out.append(f"{run}.swad.tta_d4.e1t3b_f{k}|{CARD}|{s}|{DT}/t3b_{arm}_f{k}|{k}|{GATE}|{DGATE}|0|"
                           f"--dumpof {kb}/experiments/{run} --key swad --tta d4 --set e1t3b_f{k}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", required=True)
    ap.add_argument("--train", required=True)
    ap.add_argument("--dump", required=True)
    a = ap.parse_args(argv)
    assert re.fullmatch(r"[0-9a-f]{40}", a.k), "K must be a full commit"
    for p in (a.train, a.dump):
        if Path(p).exists():
            sys.exit(f"refuse: {p} exists")
    kb = f"/tmp/noob_el/bench_{a.k[:7]}"
    T, D = train_lines(), dump_lines(kb)
    tn = [l.split("|", 1)[0] for l in T]
    dn = [l.split("|", 1)[0] for l in D]
    assert len(T) == len(set(tn)) == 33 and len(D) == len(set(dn)) == 30
    for l in T:
        f = l.split("|")
        assert len(f) == 10 and f[7] == "0" and f[8] == "" and f[9] == "swad"
        assert f[3].endswith(f"t3b_deploy") if f[0].startswith("t3b_deploy_") else f[3].endswith(f"_f{f[4]}")
    for l in D:
        f = l.split("|")
        w = f[8].split()
        assert len(f) == 9 and f[7] == "0" and len(w) == 8 and w[0::2] == ["--dumpof", "--key", "--tta", "--set"]
        run = w[1].rsplit("/", 1)[1]
        assert f[0] == f"{run}.swad.tta_d4.{w[7]}" and w[7] == f"e1t3b_f{f[4]}" and f[3].endswith(f"_f{f[4]}") and run in tn
        assert w[3] == "swad" and w[5] == "d4" and not run.startswith("t3b_deploy")
    Path(a.train).write_text("".join(l + "\n" for l in T))
    Path(a.dump).write_text("".join(l + "\n" for l in D))
    print(f"wrote {a.train}: {len(T)} training lines (30 fold models, 3 deployable); {a.dump}: {len(D)} sealed dump lines "
          f"(--dumpof {kb}/experiments)")


if __name__ == "__main__":
    main()
