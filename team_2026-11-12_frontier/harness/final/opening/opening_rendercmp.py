"""Render check of the sealed-opening queue (opening_queue.sh render; pattern of harness/final/final_rendercmp.py):
every line cq.sh of G rendered (Q/jobs_rendered.txt) must equal the template built here from the job line, and the semantics
must hold. Prints 'render compare: 0 FAIL' or the failures; rc 1 on any failure.
Template per job line name|card|seed|root|0|gate|dgate|logp|--dumpof <run> --key <key> --tta <mode> --set <set>:
  dump_<name>|<PC> -u scripts/bench_infer.py --run <run> --set <set> --opening <opening of set> --dumps <B>/dumps --method <card
  name> --card <card> --run-id <name> --weights-key <key> --tta <mode> --device cuda --precision fp32 --threads 4 --workers 4
  --batch 8[ --logp --ens-member] --forbidden /tmp/noob_el/bench_data/meta/forbidden_v1.txt --bench-run dump_<name>
Semantics: exactly one rendered line per job, all of them dumps (no training command); the opening is e1_open8_final for
e1_106 and t50_open19_final for test50; --logp appears only with --ens-member and only on e1_106 C1 / C2 lines; C2 lines
take key swad with d4, C1 lines key model with none, C1-D4 lines key model with d4; the run dir is F2B's (the fin2 resume
deploy, /tmp/noob_el/bench_9967d59).
Usage: opening_rendercmp.py --jobs jobs.txt --rendered rendered.txt --b <GB> [--pc <cv02 python>]
"""
import argparse
import sys

OPEN = {"e1_106": "e1_open8_final", "test50": "t50_open19_final"}
METHOD = {"bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml": "hrnet_w18_unetpp_swad_const_pf_v11",
          "bench/methods/house_r34_unetpp_pf_v11.yaml": "house_r34_unetpp_pf_v11"}
EXP = "/tmp/noob_el/bench_9967d59/experiments/"   # F2B: the full-pool runs after the fin2 resume (REVIEW_FIN2 N3)
FORB = "/tmp/noob_el/bench_data/meta/forbidden_v1.txt"


def template(line: str, B: str, PC: str) -> tuple[str, str]:
    name, card, seed, root, fold, gate, dgate, logp, extra = line.split("|")
    w = extra.split()
    assert len(w) == 8 and w[0::2] == ["--dumpof", "--key", "--tta", "--set"], extra
    run, key, mode, st = w[1], w[3], w[5], w[7]
    cmd = (f"{PC} -u scripts/bench_infer.py --run {run} --set {st} --opening {OPEN[st]} --dumps {B}/dumps "
           f"--method {METHOD[card]} --card {card} --run-id {name} --weights-key {key} --tta {mode} --device cuda "
           f"--precision fp32 --threads 4 --workers 4 --batch 8{' --logp --ens-member' if logp == '1' else ''} "
           f"--forbidden {FORB} --bench-run dump_{name}")
    return f"dump_{name}", cmd


def semantics(line: str) -> list[str]:
    name, card, seed, root, fold, gate, dgate, logp, extra = line.split("|")
    w = extra.split()
    run, key, mode, st = w[1], w[3], w[5], w[7]
    bad = []
    if not run.startswith(EXP) or not name.startswith(run[len(EXP):] + "."):
        bad.append("run dir / name")
    if root != "/tmp/noob_el/bench_data_fin/roots/pool532_v11" or fold != "0":
        bad.append("root / fold")
    if not run.endswith(f"_s{seed}"):
        bad.append("seed")
    kind = ("C2" if run[len(EXP):].startswith("fin_hrnet_swad_v11_pool_") else
            "C1D4" if mode == "d4" else "C1")
    want = {"C2": ("swad", "d4"), "C1": ("model", "none"), "C1D4": ("model", "d4")}[kind]
    if (key, mode) != want:
        bad.append(f"{kind} key / mode {key} {mode}")
    if (logp == "1") != (st == "e1_106" and kind in ("C1", "C2")):
        bad.append("logp")
    if not name.endswith("." + st):
        bad.append("name / set")
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--rendered", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--pc", default="/tmp/noob_el/el-fault-detection/.venv/bin/python")
    a = ap.parse_args(argv)
    jobs = [l.rstrip("\n") for l in open(a.jobs) if l.strip()]
    rend = [l.rstrip("\n") for l in open(a.rendered) if l.strip()]
    fails = []
    got = {}
    for l in rend:
        k, v = l.split("|", 1)
        if k in got:
            fails.append(f"rendered twice: {k}")
        got[k] = v
    if len(rend) != len(jobs):
        fails.append(f"{len(rend)} rendered lines for {len(jobs)} jobs")
    for l in rend:
        if "scripts/train.py" in l:
            fails.append(f"training command rendered: {l[:80]}")
    for j in jobs:
        try:
            k, want = template(j, a.b, a.pc)
        except Exception as e:  # noqa: BLE001
            fails.append(f"bad job line {j[:80]}: {e}")
            continue
        if got.get(k) != want:
            fails.append(f"{k}: rendered line differs from the template")
        fails += [f"{k}: {b}" for b in semantics(j)]
    n_logp = sum(1 for v in got.values() if " --logp --ens-member " in v)
    n_e1 = sum(1 for j in jobs if j.split("|")[0].endswith(".e1_106"))
    print(f"jobs {len(jobs)} (e1_106 {n_e1}, test50 {len(jobs) - n_e1}); rendered {len(rend)}; ensemble members with logp {n_logp}")
    for f in fails:
        print("FAIL " + f)
    print(f"render compare: {len(fails)} FAIL")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
