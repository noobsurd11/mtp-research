"""G-N7: observed wall time of cv02 dump-only jobs, from local read-only copies of two cv02 queue logs.
Inputs : raw/cv02_logs/{open,fin}_launch.log (copied with `ssh -n -a -o BatchMode=yes cv02@10.8.1.106 cat ...`).
Output : raw/wall_jobs.tsv (one row per dump job) and raw/wall_summary.tsv (per queue x arm x set).
Per job: start = 'start dump_<job> on GPU g' line, end = 'dumped dump_<job> rc=0' line (log time stamps, 1 s resolution).
cells = RUN.md5 file count - 1 (one manifest per dump dir; E1 107 files = 106 cells, test50 51 = 50).
Context per job (from the same log): our other jobs running at start (any GPU), our jobs on the same GPU, the last
'another user > 4096 MiB' memory reported for that GPU in the 120 s before start (the queue logs other users only above
4096 MiB, so 0 means 'not above 4096 MiB', not 'idle'), and 'free MiB' at start.
Arm labels: hrnet_swad *.swad.tta_d4 = C2 member (C3 = 5 of them); pf plain = C1 (E-PF = 5 of them); pf *.tta_d4 = C1-D4;
hrnet *.swad_bn.tta_d4 = swad_bn readout (information only, not a candidate). No prediction file is read.
"""
import re
import statistics as st
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
TS = re.compile(r"^\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\] (.*)$")


def t(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def arm_of(job):
    if "hrnet_swad" in job:
        return "C2_member" if ".swad.tta_d4" in job else ("swad_bn_D4(info)" if ".swad_bn.tta_d4" in job else "hrnet_other")
    if "_pf_" in job:
        return "C1_D4" if ".tta_d4" in job else "C1"
    return "other"


def set_of(job, q):
    if job.endswith(".e1_106"):
        return "e1_106"
    if job.endswith(".test50"):
        return "test50"
    return "cv5_fold_oof" if q == "fin" else "?"


def parse(q):
    lines = (HERE / "raw" / "cv02_logs" / f"{q}_launch.log").read_text().splitlines()
    ev = []
    for ln in lines:
        m = TS.match(ln)
        if m:
            ev.append((t(m.group(1)), m.group(2)))
    jobs, running, other_mem = {}, {}, {}   # running: name -> gpu (ours, trainings and dumps)
    for ts, msg in ev:
        m = re.match(r"lane GPU (\d+): another user > 4096 MiB: (.*)$", msg)
        if m:
            mib = sum(int(x) for x in re.findall(r":(\d+)MiB", m.group(2)))
            other_mem[int(m.group(1))] = (ts, mib)
            continue
        m = re.match(r"start (\S+) on GPU (\d+) \((?:card [^,]+, seed \d+, root \S+, gate \d+; )?free (\d+) MiB", msg)
        if m:
            name, g, free = m.group(1), int(m.group(2)), int(m.group(3))
            if name.startswith("dump_"):
                job = name[len("dump_"):]
                om = other_mem.get(g)
                jobs[job] = dict(queue=q, job=job, arm=arm_of(job), set=set_of(job, q), gpu=g, start=ts, free_mib=free,
                                 ours_running_any=len(running), ours_same_gpu=sum(1 for v in running.values() if v == g),
                                 other_user_mib_120s=(om[1] if om and (ts - om[0]).total_seconds() <= 120 else 0))
            running[name] = g
            continue
        m = re.match(r"dumped dump_(\S+) rc=(\d+)", msg)
        if m:
            job = m.group(1)
            jobs[job]["end"], jobs[job]["rc"] = ts, int(m.group(2))
            running.pop("dump_" + job, None)
            continue
        m = re.match(r"(?:trained|done|no dump for) ([^\s:]+)", msg)
        if m and not m.group(1).startswith("dump_"):
            running.pop(m.group(1), None)
            continue
        m = re.match(r"RUN\.md5 (\S+) rc=\d+: (\d+) files", msg)
        if m and m.group(1) in jobs:
            jobs[m.group(1)]["cells"] = int(m.group(2)) - 1
    return list(jobs.values())


def main():
    rows = parse("open") + parse("fin")
    cols = ["queue", "job", "arm", "set", "gpu", "start", "end", "wall_s", "cells", "s_per_cell", "rc", "free_mib",
            "ours_running_any", "ours_same_gpu", "other_user_mib_120s"]
    out = ["\t".join(cols)]
    for r in rows:
        r["wall_s"] = int((r["end"] - r["start"]).total_seconds())
        r["s_per_cell"] = round(r["wall_s"] / r["cells"], 3)
        out.append("\t".join(str(r[c]) for c in cols))
    (HERE / "raw" / "wall_jobs.tsv").write_text("\n".join(out) + "\n")
    groups = {}
    for r in rows:
        groups.setdefault((r["queue"], r["arm"], r["set"]), []).append(r)
    sc = ["queue", "arm", "set", "jobs", "cells_per_job", "wall_s_median", "wall_s_min", "wall_s_max", "s_per_cell_median",
          "s_per_cell_min", "s_per_cell_max", "jobs_with_other_user_gt4096MiB_on_gpu", "jobs_sharing_gpu_with_our_job"]
    so = ["\t".join(sc)]
    for k, g in sorted(groups.items()):
        w = [r["wall_s"] for r in g]
        s = [r["s_per_cell"] for r in g]
        cells = sorted({r["cells"] for r in g})
        so.append("\t".join(map(str, [*k, len(g), ",".join(map(str, cells)), st.median(w), min(w), max(w),
                                      round(st.median(s), 3), min(s), max(s),
                                      sum(r["other_user_mib_120s"] > 0 for r in g), sum(r["ours_same_gpu"] > 0 for r in g)])))
    (HERE / "raw" / "wall_summary.tsv").write_text("\n".join(so) + "\n")
    print("\n".join(so))
    return 0


if __name__ == "__main__":
    sys.exit(main())
