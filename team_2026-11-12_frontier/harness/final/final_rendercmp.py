"""final package: compare the jobs_rendered.txt of a render-only run of F's cq.sh on cv02 with the lines the job list must give.

Two independent checks, both must pass (prints 'render compare: 0 FAIL' at the end, rc 0; else the failing items, rc 1):
 1. Templates (cq.sh of F, 012e8e3f): for every job line of --jobs, the expected rendered line(s), built here:
      full-pool training  '<n>|<P> -u scripts/train.py --config <card config> --opts <bench.cards opts --seed --run-name --data-root>'
                          and NO dump line (the full-pool root has no held-out set)
      dump-only           'dump_<n>|<P> -u scripts/bench_infer.py --run <src> --set cv5v3_f<k> --dumps <B>/dumps --method <card name>
                          --card <card> --run-id <n> --weights-key <key> --tta <mode> --device cuda --precision fp32 --threads 4
                          --workers 4 --batch 8 --forbidden <DATA>/meta/forbidden_v1.txt --bench-run dump_<n>' and NO training line
    The opts come from bench.cards of --repo (F's tree; cards byte-equal to the deploy's). The rendered set must equal the
    expected set exactly (no extra, no missing line).
 2. Semantics, read off the rendered text alone: 85 lines = 10 training + 75 dump lines; no '--logp', no '--opening', no
    sealed set name; every dump line's --set is cv5v3_f<fold of its job>, its --run is the job's --dumpof dir, its --run-id is
    the job name, its --tta d4, its --weights-key the job's key; every training line holds seed=<s>, run_name=<n> and
    data.root=<pool root>; no rendered line names a fin_ job as a dump.
--df maps the full-pool root of the job list to the one the render used (the render smoke builds its own DATA_F).

  python final_rendercmp.py --jobs jobs_fin.txt --rendered rendered.txt --b /tmp/noob_el/bench_821dfad [--df OLD=NEW]
      [--repo /home/noob/work/bench_wt_fin] [--p /tmp/noob_el/el-fault-detection/.venv/bin/python] [--data /tmp/noob_el/bench_data]
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

SEALED = ("test50", "e1_106", "legacy_test", "ext117", "--opening", "--logp")


def card_get(repo: str, card: str, key: str) -> str:
    code = "import sys, yaml; c = yaml.safe_load(open(sys.argv[1]))\nfor k in sys.argv[2].split('.'): c = c[k]\nprint(c)"
    return subprocess.run([sys.executable, "-c", code, card, key], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def card_opts(repo: str, card: str, seed: str, name: str, root: str) -> str:
    r = subprocess.run([sys.executable, "-m", "bench.cards", "opts", card, "--seed", seed, "--run-name", name, "--data-root", root],
                       cwd=repo, capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--rendered", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--df", default=None, help="OLD=NEW: the full-pool root path of the list and the one the render used")
    ap.add_argument("--repo", default="/home/noob/work/bench_wt_fin")
    ap.add_argument("--p", default="/tmp/noob_el/el-fault-detection/.venv/bin/python")
    ap.add_argument("--data", default="/tmp/noob_el/bench_data")
    a = ap.parse_args()
    old, new = (a.df.split("=", 1) if a.df else (None, None))
    jobs = [ln.rstrip("\n") for ln in open(a.jobs) if ln.strip()]
    if old:
        jobs = [ln.replace(old, new) for ln in jobs]
    rend = [ln.rstrip("\n") for ln in open(a.rendered) if ln.strip()]
    fails = []
    exp, meta = [], {}
    cache = {}
    for j in jobs:
        f = (j.split("|") + [""] * 10)[:10]
        n, card, seed, root, fold, gate, dgate, logp, extra, ro = f
        if card not in cache:
            cache[card] = (card_get(a.repo, card, "config"), card_get(a.repo, card, "name"))
        cfg, method = cache[card]
        if extra.startswith("--dumpof "):
            w = extra.split()
            assert len(w) == 6 and w[0] == "--dumpof" and w[2] == "--key" and w[4] == "--tta", j
            src, key, mode = w[1], w[3], w[5]
            exp.append(f"dump_{n}|{a.p} -u scripts/bench_infer.py --run {src} --set cv5v3_f{fold} --dumps {a.b}/dumps --method {method} "
                       f"--card {card} --run-id {n} --weights-key {key} --tta {mode} --device cuda --precision fp32 --threads 4 "
                       f"--workers 4 --batch 8{' --logp' if logp == '1' else ''} --forbidden {a.data}/meta/forbidden_v1.txt --bench-run dump_{n}")
            meta[f"dump_{n}"] = ("dump", fold, src, n, key, mode)
        else:
            assert extra == "" and root.endswith("/roots/pool532_v11"), f"only full-pool training lines are expected: {j}"
            exp.append(f"{n}|{a.p} -u scripts/train.py --config {cfg} --opts {card_opts(a.repo, card, seed, n, root)}")
            meta[n] = ("train", seed, root, n)
    # 1. templates
    E, R = set(exp), set(rend)
    for x in sorted(E - R):
        fails.append(f"template: expected line not rendered: {x[:200]}")
    for x in sorted(R - E):
        fails.append(f"template: rendered line not expected: {x[:200]}")
    if len(rend) != len(R):
        fails.append(f"template: {len(rend) - len(R)} duplicate rendered lines")
    # 2. semantics of the rendered text alone
    nt = sum(1 for x in rend if not x.startswith("dump_"))
    nd = sum(1 for x in rend if x.startswith("dump_"))
    if (len(rend), nt, nd) != (85, 10, 75):
        fails.append(f"semantics: {len(rend)} lines, {nt} training, {nd} dump (expected 85, 10, 75)")
    for x in rend:
        name, cmd = x.split("|", 1)
        if any(t in cmd for t in SEALED):
            fails.append(f"semantics: sealed token in {name}")
        m = meta.get(name)
        if m is None:
            fails.append(f"semantics: {name} is no job of the list")
            continue
        if m[0] == "dump":
            _, fold, src, n, key, mode = m
            want = {"--set": f"cv5v3_f{fold}", "--run": src, "--run-id": n, "--weights-key": key, "--tta": mode}
            toks = cmd.split()
            for k, v in want.items():
                got = toks[toks.index(k) + 1] if k in toks else None
                if got != v:
                    fails.append(f"semantics: {name} {k} {got!r}, expected {v!r}")
            if "scripts/train.py" in cmd:
                fails.append(f"semantics: {name} trains")
        else:
            _, seed, root, n = m
            for t in (f"seed={seed}", f"run_name={n}", f"data.root={root}"):
                if f" {t} " not in f" {cmd} ":
                    fails.append(f"semantics: {name} lacks {t}")
            if "bench_infer" in cmd:
                fails.append(f"semantics: {name} dumps")
    if any(x.startswith("dump_fin_") for x in rend):
        fails.append("semantics: a full-pool job has a dump line")
    for x in fails[:40]:
        print("FAIL", x)
    print(f"render compare: {len(fails)} FAIL ({len(rend)} rendered lines: {nt} training, {nd} dump; {len(exp)} expected)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
