"""x4 kd (builder kd): read_x4.py b012ccfb with ONE change: --writers, an allowlist of dump writers (exact
"<script> <md5>" strings) replacing the single-writer check, so that derived dumps (bench_ens_infer.py ensembles) and
the COMBO D4 dumps (bench_infer.py 32e0b67c, queue fin) can enter one read beside the plain COMBO dumps (bench_infer.py
afd91642). Everything else (frozen tool, groups, exclude, manifest checks, one GPU model) is unchanged.

x4: read of screening arms on cv5v3 (gaint CPU). A thin driver around the reviewed read tool, which it does not change:
bench_wt_final at 89b9ea5, scripts/bench_read_w1.py fdb56b78 (the c3x read tool), groups cv5v3_groups.tsv d880a769 (285
groups), score_exclude_v3.txt 6d48dfbd (416 clean cells), 2,000 draws, two-stage group bootstrap, OP-A and OP-W.
The rule printer is x4_verdict.py (headline and guard functions imported unchanged from c3x_verdict.py faa2a961).

Usage (gaint, CPU only; run inside tmux, nice 19):
  python read_x4.py --out /home/noob/work/bench_reads/x4_<tag> --base COMBO \
     --arm 'COMBO=<dump dir template with {k} {s}>:5,6:swad' --arm 'X=<template>:5,6:<weights key>' \
     --arm 'PFAA=<template>:5,6,7,8:model' --aa PFAA:5,6:7,8 --pair COMBO=X [--cache DIR] [--verdict X] [--show]
  Templates: the dump folder of one run (the folder that holds cv5v3_f<k>/manifest.json), with {k} = fold, {s} = seed.
  Default x4 arms: see x4_arms.sh (COMBO = c3x swad readout seeds 5, 6; PFAA = c3_pf_v11 seeds 5 to 8 for M only).
Refuses (nothing written, the output folder not created) unless: the read tree is at 89b9ea5 with no tracked change and the
tool, groups and exclude files have their md5; every arm has folds 0 to 4 for each of its seeds; every manifest names
run_id = folder name, fold, seed, weights key, step 20000, set cv5v3_f<k>, fp32, set_kind open; one GPU model and one
writer (bench_infer.py md5) over all dumps; a dump under /home/noob/work/bench_relay/<q>/<run>/ has <q>/.ok/<run>.
Sealed sets cannot enter: only cv5v3_f<k> sets pass the manifest check (and the tool refuses non-CV sets itself).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

RT = Path("/home/noob/work/bench_wt_final")
REV = "89b9ea5a12a37a87c16c4868cc4adf00794a7610"
TOOL_MD5 = "fdb56b78"
XCL = Path("/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/score_exclude_v3.txt"); XCL_MD5 = "6d48dfbd"
G3 = Path("/home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv"); G3_MD5 = "d880a769"
PY = "/home/noob/work/el-fault-detection/.venv/bin/python"
HERE = Path(__file__).resolve().parent
RELAY = Path("/home/noob/work/bench_relay")


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def git(*a) -> str:
    return subprocess.run(["git", "-C", str(RT), *a], capture_output=True, text=True).stdout.strip()


def parse_arm(spec: str):
    name, rest = spec.split("=", 1)
    tmpl, seeds, key = rest.rsplit(":", 2)
    return name, tmpl, [int(x) for x in seeds.split(",")], key


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--arm", action="append", required=True)
    ap.add_argument("--pair", action="append", required=True)
    ap.add_argument("--aa", required=True)
    ap.add_argument("--cache", default=None)
    ap.add_argument("--verdict", default=None, help="comma list of arms judged against --base (default: the B of every pair)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--writers", action="append", default=None, help="allowed writer strings (exact manifest 'writer')")
    ap.add_argument("--stage", default="")
    ap.add_argument("--show", action="store_true", help="print the tool command and exit (nothing checked or written)")
    a = ap.parse_args()
    out = Path(a.out)
    arms = [parse_arm(s) for s in a.arm]
    names = [n for n, *_ in arms]
    assert a.base in names, f"base {a.base} is not an arm"
    links = out / "links" / "elbench1"
    cmd = [PY, "scripts/bench_read_w1.py"]
    for n, *_ in arms:
        cmd += ["--arm", f"{n}={links / n}:.*"]
    for p in a.pair:
        cmd += ["--pair", p]
    cmd += ["--labels", "v11", "--workers", str(a.workers), "--cache", str(a.cache or out / "cache"), "--baseline", a.base,
            "--aa", a.aa, "--groups", str(G3), "--score-exclude", str(XCL), "--out", str(out / "read")]
    if a.show:
        print(" ".join(cmd)); return 0
    # ---- checks before anything is written
    bad = []
    if git("rev-parse", "HEAD") != REV:
        bad.append(f"{RT} not at {REV[:7]}")
    if git("status", "--porcelain", "-uno"):
        bad.append(f"tracked changes in {RT}")
    for p, m in ((RT / "scripts/bench_read_w1.py", TOOL_MD5), (XCL, XCL_MD5), (G3, G3_MD5)):
        if md5(p)[:8] != m:
            bad.append(f"{p} md5 {md5(p)[:8]} != {m}")
    if out.exists():
        bad.append(f"output folder exists: {out}")
    rows, dev, wr = [], set(), set()
    for n, tmpl, seeds, key in arms:
        for s in seeds:
            for k in range(5):
                d = Path(tmpl.format(k=k, s=s))
                mf = d / f"cv5v3_f{k}" / "manifest.json"
                if not mf.is_file():
                    bad.append(f"{n}: missing {mf}"); continue
                try:
                    rel = d.relative_to(RELAY)
                    q, run = rel.parts[0], rel.parts[1]
                    if not (RELAY / q / ".ok" / run).exists():
                        bad.append(f"{n}: {RELAY / q / '.ok' / run} missing (not relayed)")
                except ValueError:
                    pass
                m = json.loads(mf.read_text())
                want = {"run_id": d.name, "fold": k, "seed": s, "weights_key": key, "step": 20000, "set": f"cv5v3_f{k}",
                        "precision": "fp32", "set_kind": "open"}
                bad += [f"{d}: {x} = {m.get(x)!r}, expected {v!r}" for x, v in want.items() if m.get(x) != v]
                dev.add(str(m.get("device"))); wr.add(str(m.get("writer")))
                rows.append((n, s, k, str(d), m.get("train_code_revision"), md5(mf)[:8]))
    if len(dev) != 1 or any("cpu" in x.lower() for x in dev):
        bad.append(f"devices over all dumps: {sorted(dev)} (one GPU model expected)")
    allowed = set(a.writers or [])
    if (len(wr) != 1 and not allowed) or (allowed and not wr <= allowed):
        bad.append(f"writers over all dumps: {sorted(wr)} (allowed: {sorted(allowed) or 'one bench_infer.py'})")
    print(f"read_x4 check: {len(rows)} dumps, arms {names}, device {sorted(dev)}, writer {sorted(wr)}: {'OK' if not bad else 'FAIL'}")
    if bad:
        for b in bad[:30]:
            print("  " + b)
        print("REFUSED: nothing written"); return 1
    for n, s, k, d, rev, mm in rows:
        (links / n).mkdir(parents=True, exist_ok=True)
        os.symlink(d, links / n / Path(d).name)
    (out / "expected_dumps.tsv").write_text("arm\tseed\tfold\tdump_dir\ttrain_code_revision\tmanifest_md5\n" +
                                            "".join("\t".join(map(str, r)) + "\n" for r in rows))
    (out / "command.txt").write_text(" ".join(cmd) + "\n")
    env = dict(os.environ, CUDA_VISIBLE_DEVICES="", OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    print(f"command (cwd {RT}, nice 19): {' '.join(cmd)}", flush=True)
    rc = subprocess.run(["nice", "-n", "19", *cmd], cwd=RT, env=env).returncode
    print(f"read rc={rc}", flush=True)
    if rc != 0:
        return rc
    vs = a.verdict or ",".join(p.split("=", 1)[1] for p in a.pair if p.split("=", 1)[0] == a.base)
    if vs:
        rc = subprocess.run([PY, str(HERE.parent.parent / "x4_verdict.py"), "--read", str(out), "--base", a.base, "--arms", vs,
                             "--out", str(out / "verdict.txt")] + (["--stage", a.stage] if a.stage else [])).returncode
        print(f"verdict rc={rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
