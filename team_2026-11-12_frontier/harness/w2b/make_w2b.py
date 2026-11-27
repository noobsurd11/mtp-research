"""Write the wave 2b queue files for gaint (bench_q format name|card|seed|data_root|gate_mib|cmd|extra) into OUT.
Usage: python make_w2b.py OUT DEPLOY_FULL_SHA
Queues (each OUT/<q>/{jobs.txt, MAXC[, dump/jobs.txt, dump/MAXC], launch.sh}; the lead copies OUT/<q> to
/home/noob/work/bq/<q> and runs the launch script, which only exports the pins and execs bench_setup.sh):
  w2b_smoke    3 smoke jobs, fold 0 seed 5, --exit_after_step 200 (rc 3 by design), MAXC 1, gate 11000, no dumps:
               PF (house_r34_unetpp_pf_v11, the same-conditions comparator), la_ce, layered_ci. Peak memory per job from
               gpumem.log; steps/s from the step-200 line of each train.log (pathfinder criterion 2).
  w2b_lcipath  layered_ci pathfinder (T10 spec arm 3): w2b_lcipath_f0_s5, 20k steps, then 3 dumps of fold 0 (decision
               card = layered_ci_replace, argmax24, layered_ci_union). MAXC 1.
  w2b_lace     la_ce screen: folds 0-4, seeds 5 and 6 (seed 5 block first), 10 runs, then 10 dumps. MAXC 2.
  w2b_lci      layered_ci screen: folds 0-4, seeds 5 and 6, 10 runs, then 30 dumps (10 layered, 10 argmax24, 10 union).
Dumps: canonical fp32 on cuda (W1-G / wave 2a settings), no --logp, into /home/noob/work/bench_dumps/w2b.
"""
import hashlib
import sys
from pathlib import Path

OUT, DEPLOY = Path(sys.argv[1]), sys.argv[2]
assert len(DEPLOY) == 40
REPO = "/home/noob/work/bench_wt_w2b"
PY = "/home/noob/work/el-fault-detection/.venv/bin/python"
ROOT = "/home/noob/work/bench_data/roots/cv5v2_v11_f{k}"
DUMPS = "/home/noob/work/bench_dumps/w2b"
GATE, DGATE = 11000, 6200
MAXH = 120
LACE, LCI, PF = "la_ce_pf_v11", "layered_ci_pf_v11", "house_r34_unetpp_pf_v11"


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def tline(n, c, s, k, extra=""):
    return f"{n}|bench/methods/{c}.yaml|{s}|{ROOT.format(k=k)}|{GATE}||{extra}"


def dline(n, c, s, k, decision=None):
    rid = n if decision is None else f"{n}.{decision}"
    dn = f"dump_{n}" + ("" if decision is None else f"_{decision}")
    dec = f" --decision {decision}" if decision else ""
    cmd = (f"{PY} -u scripts/bench_infer.py --run {REPO}/experiments/{n} --set cv5v2_f{k} --dumps {DUMPS} --method {c} "
           f"--card bench/methods/{c}.yaml --run-id {rid} --weights-key model{dec} --device cuda --precision fp32 "
           f"--threads 4 --workers 4 --batch 8 --bench-run {dn}")
    return f"{dn}|-|{s}|{ROOT.format(k=k)}|{DGATE}|{cmd}|"


Q = {}
Q["w2b_smoke"] = ([tline(f"smoke_w2b_{a}_f0_s5", c, 5, 0, "--exit_after_step 200")
                   for a, c in (("pf", PF), ("lace", LACE), ("lci", LCI))], None, 1,
                  "3 smoke jobs (--exit_after_step 200, rc 3 by design, MAXC 1, gate 11000); no dumps")
Q["w2b_lcipath"] = ([tline("w2b_lcipath_f0_s5", LCI, 5, 0)],
                    [dline("w2b_lcipath_f0_s5", LCI, 5, 0)] + [dline("w2b_lcipath_f0_s5", LCI, 5, 0, d)
                                                              for d in ("argmax24", "layered_ci_union")], 1,
                    "the layered_ci pathfinder (1 training job, 20k steps), then 3 fold-0 dumps")
runs = {a: [(f"w2b_{a}_f{k}_s{s}", c, s, k) for s in (5, 6) for k in range(5)] for a, c in (("lace", LACE), ("lci", LCI))}
Q["w2b_lace"] = ([tline(*r) for r in runs["lace"]], [dline(*r) for r in runs["lace"]], 2,
                 "10 la_ce training jobs (MAXC 2), then 10 held-out dumps (MAXC 1)")
Q["w2b_lci"] = ([tline(*r) for r in runs["lci"]],
                [dline(*r) for r in runs["lci"]] + [dline(*r, d) for d in ("argmax24", "layered_ci_union")
                                                    for r in runs["lci"]], 2,
                "10 layered_ci training jobs (MAXC 2), then 30 held-out dumps (layered, argmax24, union; MAXC 1)")

for q, (lines, dlines, maxc, note) in Q.items():
    d = OUT / q
    d.mkdir(parents=True, exist_ok=True)
    (d / "jobs.txt").write_text("\n".join(lines) + "\n")
    (d / "MAXC").write_text(f"{maxc}\n")
    if dlines:
        (d / "dump").mkdir(exist_ok=True)
        (d / "dump" / "jobs.txt").write_text("\n".join(dlines) + "\n")
        (d / "dump" / "MAXC").write_text("1\n")
    names = [l.split("|")[0] for l in lines + (dlines or [])]
    assert len(names) == len(set(names)), q
    ses = f"bench_q_{q}"
    env = (f"export Q=/home/noob/work/bq/{q} SES={ses} DEPLOY={DEPLOY} \\\n  JOBS_MD5={md5(d / 'jobs.txt')}"
           + (f" DJOBS_MD5={md5(d / 'dump' / 'jobs.txt')}" if dlines else "") + f" REPO={REPO} MAXH={MAXH}\n")
    (d / "launch.sh").write_text(
        "#!/bin/bash\n"
        f"# Wave 2b ({ses}): the lead runs this once, after the review of harness/LAUNCH_REQUEST_w2b.md.\n"
        f"# Arms /home/noob/work/bq/{q} in tmux {ses} from the bench_w2b worktree (REPO) at DEPLOY: {note}.\n"
        "# The queue shares the gpu_gate with every other queue (free >= gate, 120 s since any start) and waits while any\n"
        "# GPU process that is not its own holds > 1,024 MiB. bench_setup.sh refuses (nothing started) if the session\n"
        "# exists, the dir is armed or used, an md5 or HEAD differs, a tracked change exists, or any experiments/<job> exists.\n"
        + env + "exec bash $REPO/bench/q/bench_setup.sh\n")
    (d / "launch.sh").chmod(0o755)
    print(f"{q}: jobs {len(lines)} md5 {md5(d / 'jobs.txt')}" +
          (f"; dumps {len(dlines)} md5 {md5(d / 'dump' / 'jobs.txt')}" if dlines else "") +
          f"; launch.sh md5 {md5(d / 'launch.sh')}")
