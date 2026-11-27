"""Write the wave 2a queue files (gaint, bench_q format name|card|seed|data_root|gate_mib|cmd|extra) into OUT.
Usage: python make_w2a.py OUT DEPLOY_FULL_SHA
OUT/w2a/{jobs.txt, MAXC, dump/jobs.txt, dump/MAXC, launch_w2a.sh}, OUT/w2a_smoke/{jobs.txt, MAXC, launch_w2a_smoke.sh}."""
import hashlib
import sys
from pathlib import Path

OUT, DEPLOY = Path(sys.argv[1]), sys.argv[2]
assert len(DEPLOY) == 40
REPO = "/home/noob/work/bench_wt_w2"
PY = "/home/noob/work/el-fault-detection/.venv/bin/python"
ROOT = "/home/noob/work/bench_data/roots/cv5v2_v11_f{k}"
DUMPS = "/home/noob/work/bench_dumps/w2a"
GATE, DGATE = 11000, 6200
MAXH = 120  # lifetime (h) of the gpumem logger and guard (bench_setup passes it through, commit c57508e); training is about 50 h
# (short name, card, readout keys to dump: primary first, then the card's other readouts in reading order)
ARMS = [
    ("rcs", "rcs_pf_v11", ["model"]),
    ("ema", "ema_wise_posthoc_pf_v11", ["ema_9998_bn", "raw_bn", "model", "ema_999_bn", "ema_9998", "ema_999"]),
    ("softband", "soft_band_jml", ["model"]),
    ("jmlhard", "jml_hard", ["model"]),
    ("swad", "swad_const_pf_v11", ["swad_bn", "model", "raw_bn", "swad", "ema_9998_bn", "ema_9998"]),
    ("spd", "encoder_spd_pf_v11", ["model"]),
]
CTRL = ("spdctrl", "encoder_spd_ctrl_pf_v11", ["model"])  # fold 0, seed 5 only (spec control), right after spd seed 5


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


runs = []  # (run name, card, seed, fold, keys)
for seed in (5, 6):
    for short, card, keys in ARMS:
        for k in range(5):
            runs.append((f"w2a_{short}_f{k}_s{seed}", card, seed, k, keys))
        if seed == 5 and short == "spd":
            runs.append((f"w2a_{CTRL[0]}_f0_s5", CTRL[1], 5, 0, CTRL[2]))

q = OUT / "w2a"
(q / "dump").mkdir(parents=True, exist_ok=True)
lines = [f"{n}|bench/methods/{c}.yaml|{s}|{ROOT.format(k=k)}|{GATE}||" for n, c, s, k, _ in runs]
(q / "jobs.txt").write_text("\n".join(lines) + "\n")
(q / "MAXC").write_text("3\n")


def dline(n, c, s, k, key):
    rid = n if key == "model" else f"{n}.{key}"
    dn = f"dump_{n}" + ("" if key == "model" else f"_{key}")
    cmd = (f"{PY} -u scripts/bench_infer.py --run {REPO}/experiments/{n} --set cv5v2_f{k} --dumps {DUMPS} --method {c} "
           f"--card bench/methods/{c}.yaml --run-id {rid} --weights-key {key} --device cuda --precision fp32 --threads 4 "
           f"--workers 4 --batch 8 --bench-run {dn}")
    return f"{dn}|-|{s}|{ROOT.format(k=k)}|{DGATE}|{cmd}|"


# dump order: the primary key(s) of every run (training order), then the other readouts (training order, card order)
# (ema: primary contrast ema_9998_bn - raw_bn, so raw_bn joins the first block)
NFIRST = {"ema_wise_posthoc_pf_v11": 2}
dl = [dline(n, c, s, k, key) for n, c, s, k, keys in runs for key in keys[:NFIRST.get(c, 1)]]
dl += [dline(n, c, s, k, key) for n, c, s, k, keys in runs for key in keys[NFIRST.get(c, 1):]]
(q / "dump" / "jobs.txt").write_text("\n".join(dl) + "\n")
(q / "dump" / "MAXC").write_text("1\n")

sm = OUT / "w2a_smoke"
sm.mkdir(parents=True, exist_ok=True)
smoke = [f"smoke_w2a_{short}_f0_s5|bench/methods/{c}.yaml|5|{ROOT.format(k=0)}|{GATE}||--exit_after_step 50"
         for short, c, _ in ARMS]
(sm / "jobs.txt").write_text("\n".join(smoke) + "\n")
(sm / "MAXC").write_text("1\n")

for d, ses, script, dump, note in [
        (q, "bench_q_w2a", "launch_w2a.sh", True,
         f"{len(lines)} training jobs (MAXC 3, gate {GATE}), then {len(dl)} held-out dumps (MAXC 1, gate {DGATE})"),
        (sm, "bench_q_w2a_smoke", "launch_w2a_smoke.sh", False,
         f"{len(smoke)} smoke jobs (--exit_after_step 50, rc 3 by design, MAXC 1, gate {GATE}); no dumps")]:
    env = (f"export Q={d.as_posix().replace(str(OUT), '/home/noob/work/bq')} SES={ses} DEPLOY={DEPLOY} \\\n"
           f"  JOBS_MD5={md5(d / 'jobs.txt')}" + (f" DJOBS_MD5={md5(d / 'dump' / 'jobs.txt')}" if dump else "")
           + f" REPO={REPO} MAXH={MAXH}\n")
    (d / script).write_text(
        "#!/bin/bash\n"
        f"# Wave 2a ({ses}): the reviewer runs this once, after the checklist in harness/LAUNCH_REQUEST_w2a.md passes.\n"
        f"# Arms {d.name} in tmux {ses} from the bench_w2 worktree (REPO) at DEPLOY: {note}.\n"
        "# The queue shares the gpu_gate with every other queue (free >= gate, 120 s since any start) and waits while any\n"
        "# GPU process that is not its own holds > 1,024 MiB (W1-G), so arming it while W1-G runs is safe.\n"
        "# bench_setup.sh refuses (nothing started) if the session exists, this dir is armed or used, an md5 or HEAD differs,\n"
        "# a tracked change exists, or any experiments/<job> exists. MAXH: logger and guard lifetime in h (default 24 is too short).\n"
        + env + "exec bash $REPO/bench/q/bench_setup.sh\n")
    (d / script).chmod(0o755)
print(f"training {len(lines)} md5 {md5(q / 'jobs.txt')}; dumps {len(dl)} md5 {md5(q / 'dump' / 'jobs.txt')}; "
      f"smoke {len(smoke)} md5 {md5(sm / 'jobs.txt')}")
