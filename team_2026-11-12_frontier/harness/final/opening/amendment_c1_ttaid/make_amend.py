"""AMENDMENT C1 ttaid (AMENDMENT_C1_TTAID.md; NOT applied unless a C1 plain dump of the opening failed closed).
Writes IO/amend/jobs.txt (one `--tta id` line per failed C1 plain job, named <run>.ttaid.<set>, same card, seed, root, gates and
logp) and IO/amend/AMEND.txt (failed names, the amendment list md5, the base registration md5) + AMEND.md5; read-only.
Usage: python make_amend.py --io /home/noob/work/bench_open_io --failed <job name> [--failed ...]
Refuses: IO/amend exists; a failed name not in IO/jobs.txt, or not a C1 plain line (key model, --tta none)."""
import argparse
import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--io", required=True)
    ap.add_argument("--failed", action="append", required=True)
    a = ap.parse_args(argv)
    io = Path(a.io)
    out = io / "amend"
    if out.exists():
        sys.exit(f"refuse: {out} exists")
    jobs = {l.split("|", 1)[0]: l.rstrip("\n") for l in open(io / "jobs.txt") if l.strip()}
    reg = (io / "REGISTERED.md5").read_text().strip()
    lines = []
    for n in a.failed:
        if n not in jobs:
            sys.exit(f"refuse: {n} is not in {io / 'jobs.txt'}")
        f = jobs[n].split("|")
        w = f[8].split()
        if not (w[0::2] == ["--dumpof", "--key", "--tta", "--set"] and w[3] == "model" and w[5] == "none"
                and w[1].rsplit("/", 1)[1].startswith("fin_pf_v11_pool_s")):
            sys.exit(f"refuse: {n} is not a C1 plain line")
        run, st = w[1].rsplit("/", 1)[1], w[7]
        w[5] = "id"
        f[0] = f"{run}.ttaid.{st}"
        f[8] = " ".join(w)
        lines.append("|".join(f))
    out.mkdir()
    jt = "".join(l + "\n" for l in lines)
    (out / "jobs.txt").write_text(jt)
    jm = hashlib.md5(jt.encode()).hexdigest()
    rec = ("amendment C1 ttaid of E1 opening #8 / test50 opening #19 (OPENING_RULE section 2 contingency), made "
           f"{datetime.now():%Y-%m-%d %H:%M:%S} by {os.environ.get('USER', '?')}\n"
           + "".join(f"failed {n}\n" for n in a.failed) + f"amend_jobs {jm} {len(lines)} lines\nregistered_base {reg}\n")
    (out / "AMEND.txt").write_text(rec)
    (out / "AMEND.md5").write_text(hashlib.md5(rec.encode()).hexdigest() + "\n")
    for p in out.iterdir():
        p.chmod(0o444)
    print(rec + f"AMEND.txt md5 {hashlib.md5(rec.encode()).hexdigest()} (log it in both ledgers before anything runs)")


if __name__ == "__main__":
    main()
