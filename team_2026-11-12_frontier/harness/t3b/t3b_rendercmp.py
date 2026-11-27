"""T3b render check (t3b_queue.sh render / render2; pattern of harness/final/final_rendercmp.py and opening_rendercmp.py):
the jobs_rendered.txt of a render-only run of K's cq.sh must equal the lines built here, and the semantics must hold.
Prints 'render compare: 0 FAIL' (rc 0) or the failures (rc 1).
--kind train (queue t3b, 33 lines):
  template '<n>|<P> -u scripts/train.py --config <card config> --opts <bench.cards opts --seed --run-name --data-root>' per
  line (opts from bench.cards of --repo = K's tree; the cards are byte-equal to the deploy's) and NO dump line;
  semantics: 33 training lines (30 t3b_{all,half}_f<k>_s<s>, 3 t3b_deploy_s<s>), seeds 5 to 7, data.root = the job's T3b root
  (fold roots end _f<fold>), no bench_infer, no '--opening', no '--logp', no sealed set name.
--kind repair (a registered repair queue bench_q/t3brep<R>, review round 1 N1): T3b training lines of the 33, each with extra
  '' (fresh re-run) or '--resume' (template '<n>|<P> -u scripts/train.py --resume --config ... --opts ...'); semantics as train,
  the number of lines = the job list's.
--kind dump (queue t3bopen, SEALED, 30 lines):
  template 'dump_<n>|<P> -u scripts/bench_infer.py --run <KB>/experiments/<run> --set e1t3b_f<k> --opening e1_open9_t3b
  --dumps <KB>/dumps --method <card name> --card <card> --run-id <n> --weights-key swad --tta d4 --device cuda --precision
  fp32 --threads 4 --workers 4 --batch 8 --forbidden <DATA>/meta/forbidden_v1.txt --bench-run dump_<n>' and NO training line;
  semantics: 30 dump lines, --set e1t3b_f<fold of the job>, run = a fold model of the same fold and seed (never t3b_deploy),
  key swad, tta d4, no '--logp' / '--ens-member', no e1_106 / test50.
--dt OLD=NEW maps the T3b root dir of the list to the one the render used (the render smoke builds its own).
Usage: python t3b_rendercmp.py --kind train|repair|dump --jobs J --rendered R --b <KB> [--dt OLD=NEW] [--repo <K worktree>]
         [--p <cv02 python>] [--data <DATA>]
"""
import argparse
import os
import re
import subprocess
import sys

OPENING = "e1_open9_t3b"
SEEDS = {"5", "6", "7"}


def card_get(repo, card, key):
    code = "import sys, yaml; c = yaml.safe_load(open(sys.argv[1]))\nfor k in sys.argv[2].split('.'): c = c[k]\nprint(c)"
    return subprocess.run([sys.executable, "-c", code, card, key], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def card_opts(repo, card, seed, name, root):
    r = subprocess.run([sys.executable, "-m", "bench.cards", "opts", card, "--seed", seed, "--run-name", name, "--data-root", root],
                       cwd=repo, capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, choices=("train", "repair", "dump"))
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--rendered", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--dt", default=None)
    ap.add_argument("--repo", default="/home/noob/work/bench_wt_t3b")
    ap.add_argument("--p", default="/tmp/noob_el/el-fault-detection/.venv/bin/python")
    ap.add_argument("--data", default="/tmp/noob_el/bench_data")
    a = ap.parse_args(argv)
    jobs = [l.rstrip("\n") for l in open(a.jobs) if l.strip()]
    if a.dt:
        old, new = a.dt.split("=", 1)
        jobs = [l.replace(old, new) for l in jobs]
    rend = [l.rstrip("\n") for l in open(a.rendered) if l.strip()]
    fails, exp, meta, cache = [], [], {}, {}
    for j in jobs:
        n, card, seed, root, fold, gate, dgate, logp, extra, ro = (j.split("|") + [""] * 10)[:10]
        if card not in cache:
            cache[card] = (card_get(a.repo, card, "config"), card_get(a.repo, card, "name"))
        cfg, method = cache[card]
        if a.kind in ("train", "repair"):
            assert (extra == "" or (a.kind == "repair" and extra == "--resume")) and ro == "swad" and logp == "0", f"not a T3b training line: {j}"
            exp.append(f"{n}|{a.p} -u scripts/train.py {extra + ' ' if extra else ''}--config {cfg} --opts {card_opts(a.repo, card, seed, n, root)}")
            meta[n] = (seed, root, fold)
        else:
            w = extra.split()
            assert len(w) == 8 and w[0::2] == ["--dumpof", "--key", "--tta", "--set"] and logp == "0" and not ro, f"not a T3b dump line: {j}"
            src, key, mode, st = w[1], w[3], w[5], w[7]
            exp.append(f"dump_{n}|{a.p} -u scripts/bench_infer.py --run {src} --set {st} --opening {OPENING} --dumps {a.b}/dumps "
                       f"--method {method} --card {card} --run-id {n} --weights-key {key} --tta {mode} --device cuda --precision fp32 "
                       f"--threads 4 --workers 4 --batch 8 --forbidden {a.data}/meta/forbidden_v1.txt --bench-run dump_{n}")
            meta[f"dump_{n}"] = (seed, root, fold, src, n)
    E, R = set(exp), set(rend)
    fails += [f"template: expected line not rendered: {x[:160]}" for x in sorted(E - R)]
    fails += [f"template: rendered line not expected: {x[:160]}" for x in sorted(R - E)]
    if len(rend) != len(R):
        fails.append(f"template: {len(rend) - len(R)} duplicate rendered lines")
    want_n = {"train": 33, "dump": 30, "repair": len(jobs)}[a.kind]
    if len(rend) != want_n:
        fails.append(f"semantics: {len(rend)} rendered lines, {want_n} expected")
    for x in rend:
        name, cmd = x.split("|", 1)
        toks = cmd.split()
        m = meta.get(name)
        if m is None:
            fails.append(f"semantics: {name} is no job of the list")
            continue
        for t in ("--logp", "--ens-member", "e1_106", "test50"):
            if t in toks or f"--set {t}" in cmd:
                fails.append(f"semantics: {name} holds {t}")
        if a.kind in ("train", "repair"):
            seed, root, fold = m
            if not cmd.startswith(f"{a.p} -u scripts/train.py ") or "bench_infer" in cmd or "--opening" in toks:
                fails.append(f"semantics: {name} is not a training command")
            ok = (re.fullmatch(rf"t3b_(all|half)_f{fold}_s{seed}", name) and root.endswith(f"/roots/t3b_{name.split('_')[1]}_f{fold}")) or \
                 (re.fullmatch(rf"t3b_deploy_s{seed}", name) and fold == "0" and root.endswith("/roots/t3b_deploy"))
            if not ok or seed not in SEEDS:
                fails.append(f"semantics: {name} name / seed / root / fold")
            for t in (f"seed={seed}", f"run_name={name}", f"data.root={root}"):
                if t not in toks:
                    fails.append(f"semantics: {name} lacks {t}")
        else:
            seed, root, fold, src, n = m
            want = {"--set": f"e1t3b_f{fold}", "--opening": OPENING, "--run": src, "--run-id": n, "--weights-key": "swad", "--tta": "d4"}
            for k, v in want.items():
                got = toks[toks.index(k) + 1] if k in toks else None
                if got != v:
                    fails.append(f"semantics: {name} {k} {got!r}, expected {v!r}")
            run = src.rsplit("/", 1)[1]
            if not re.fullmatch(rf"t3b_(all|half)_f{fold}_s{seed}", run) or not root.endswith(f"/roots/t3b_{run.split('_')[1]}_f{fold}") \
                    or seed not in SEEDS or not src.startswith(f"{a.b}/experiments/"):
                fails.append(f"semantics: {name} run / root / seed / fold")
            if "scripts/train.py" in cmd:
                fails.append(f"semantics: {name} trains")
    for f in fails[:40]:
        print("FAIL " + f)
    print(f"render compare: {len(fails)} FAIL ({len(rend)} rendered {a.kind} lines; {len(exp)} expected)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
