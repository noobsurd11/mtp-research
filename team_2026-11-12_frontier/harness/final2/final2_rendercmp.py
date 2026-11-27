"""fin2: compare jobs_rendered.txt of a render-only run of F2's cq.sh with what the 10 resume lines must give.
Template (cq.sh of F2): '<n>|<P> -u scripts/train.py --resume --config <card config> --opts <bench.cards opts --seed --run-name
--data-root>' and nothing else (full-pool root: no dump line). Semantics on the rendered text alone: 10 lines, each with
' --resume ', seed=<s>, run_name=<n>, data.root=<pool root>; no bench_infer, no --logp, no --opening, no sealed name.
Prints 'render compare: 0 FAIL' and rc 0, else the failing items and rc 1.

  python final2_rendercmp.py --jobs jobs_fin2.txt --rendered rendered.txt [--repo /home/noob/work/bench_wt_fin2]
      [--p /tmp/noob_el/el-fault-detection/.venv/bin/python]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

SEALED = ("test50", "e1_106", "legacy_test", "ext117", "--opening", "--logp", "bench_infer")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--rendered", required=True)
    ap.add_argument("--repo", default="/home/noob/work/bench_wt_fin2")
    ap.add_argument("--p", default="/tmp/noob_el/el-fault-detection/.venv/bin/python")
    a = ap.parse_args()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    jobs = [ln.rstrip("\n").split("|") for ln in open(a.jobs) if ln.strip()]
    rend = [ln.rstrip("\n") for ln in open(a.rendered) if ln.strip()]
    exp, fails = [], []
    for f in jobs:
        n, card, seed, root, extra = f[0], f[1], f[2], f[3], f[8]
        assert extra == "--resume" and root.endswith("/roots/pool532_v11"), f
        cfg = subprocess.run([sys.executable, "-c", "import sys, yaml; print(yaml.safe_load(open(sys.argv[1]))['config'])", card],
                             cwd=a.repo, capture_output=True, text=True, check=True, env=env).stdout.strip()
        r = subprocess.run([sys.executable, "-m", "bench.cards", "opts", card, "--seed", seed, "--run-name", n, "--data-root", root],
                           cwd=a.repo, capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stderr
        exp.append(f"{n}|{a.p} -u scripts/train.py --resume --config {cfg} --opts {r.stdout.strip()}")
        x = next((ln for ln in rend if ln.startswith(n + "|")), None)
        if x is None:
            fails.append(f"semantics: no rendered line for {n}")
            continue
        for t in (" --resume ", f" seed={seed} ", f" run_name={n} ", f" data.root={root} "):
            if t not in x + " ":
                fails.append(f"semantics: {n} lacks '{t.strip()}'")
    for x in sorted(set(exp) - set(rend)):
        fails.append(f"template: expected line not rendered: {x[:160]}")
    for x in sorted(set(rend) - set(exp)):
        fails.append(f"template: rendered line not expected: {x[:160]}")
    if len(rend) != 10 or any(ln.startswith("dump_") for ln in rend):
        fails.append(f"semantics: {len(rend)} rendered lines (10 training lines, no dump line expected)")
    fails += [f"semantics: sealed or dump token in {ln.split('|', 1)[0]}" for ln in rend if any(t in ln for t in SEALED)]
    for x in fails[:30]:
        print("FAIL", x)
    print(f"render compare: {len(fails)} FAIL ({len(rend)} rendered lines; {len(exp)} expected)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
