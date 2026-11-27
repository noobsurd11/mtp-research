#!/usr/bin/env python3
"""bench_release, 22 Nov 2026. Stage the lists-and-code release under release_v1/files/ (local only; nothing is uploaded).

Sources (read only): the team benchmark folder (T/benchmark) and git commit cba7fbd of the bench_t3b worktree (files are
read with `git show <commit>:<path>`, so the worktree is never touched). Every text file is passed through the sanitize
rules below; every substitution is written to staging/substitutions.tsv (file, rule, line, count). Sealed rows of the
cell table (role test or E1) keep only the identity columns of the code's own rule (bench/udev.py SAFE_COLS); the v1.1
manifests keep train and val rows only. No sealed value is printed: the script prints counts only.
Run: python3 -I stage.py   (refuses to run if files/ already holds anything except .git)
"""
import hashlib, json, os, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = HERE.parent
OUT = REL / "files"
TEAM = REL.parent.parent                       # team_2026-11-12_frontier
BM = TEAM / "benchmark"
WT = Path("/home/noob/work/bench_wt_t3b")       # read-only worktree
COMMIT = "cba7fbdf5df1579d6efb1168eb292e637bc9fad6"

# ---- sanitize rules: (name, regex, replacement), applied in order to every staged text file
RULES = [
    ("team_path", r"/home/yugma/mtp/research/team_2026-11-12_frontier", "./local/team"),
    ("home_work", r"/home/noob/work/", "./local/"),
    ("home_any", r"/home/[A-Za-z0-9_.-]+/", "./local_home/"),
    ("tmp_path", r"/tmp/noob_el", "./local_tmp/el"),
    ("nas_path", r"/mnt/nas/[^\s\"'`)]*", "<nas-path>"),
    ("user_tilde", r"~/mtp/", "<datasets-root>/"),
    ("host_A", r"gaint", "machA"),
    ("host_B", r"cv02", "machB"),
    ("gh_user", r"noobsurd11", "<user>"),
    ("user_1", r"\bnoob\b", "<user>"),
    ("user_2", r"\byugma\b", "<user>"),
    ("ipv4", r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])", "<ip>"),
    ("email", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "<email>"),
]
CRX = [(n, re.compile(r), s) for n, r, s in RULES]

SUBS = []        # (staged path, rule, line, count)
SAFE_COLS = ("stem", "source", "image_id", "position", "module_group", "cell_id", "n_images_of_cell", "cell_type",
             "label_source", "mask_version", "role", "bench_set", "rf_set", "in_unlabelled_pool")   # bench/udev.py l.33
SEALED_ROLES = ("test", "E1")


def git_show(path: str) -> bytes:
    return subprocess.run(["git", "-C", str(WT), "show", f"{COMMIT}:{path}"], check=True, capture_output=True).stdout


def sanitize(text: str, dest: str) -> str:
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        for name, rx, rep in CRX:
            line, n = rx.subn(rep, line)
            if n:
                SUBS.append((dest, name, i, n))
        out.append(line)
    return "\n".join(out)


def put(dest: str, data: bytes) -> None:
    p = OUT / dest
    p.parent.mkdir(parents=True, exist_ok=True)
    t = sanitize(data.decode("utf-8"), dest)
    p.write_text(t, encoding="utf-8")


def md5b(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


def main() -> None:
    if any(x.name != ".git" for x in OUT.iterdir()):
        sys.exit(f"{OUT} is not empty; remove the staged files first")
    src_md5 = {}

    # 1. code from the commit
    code = ["bench/__init__.py", "bench/cellmeta.py", "bench/classbias.py", "bench/crossfit_op.py", "bench/cv5v3.py",
            "bench/donottrain.py", "bench/dumpfmt.py", "bench/headres.py", "bench/m0core.py", "bench/placement.py",
            "bench/public_metrics.py", "bench/score_ext.py", "bench/sets.py", "bench/skel.py", "bench/udev.py",
            "bench/w1read.py", "bench/postproc/__init__.py", "bench/postproc/hysteresis.py", "bench/postproc/src_calib.py",
            "scripts/bench_score.py", "scripts/bench_read_w1.py", "scripts/bench_open_read.py", "scripts/bench_make_cv5v3.py"]
    sets_lists = ["celltypes.tsv", "do_not_train.txt", "e1_106_stems.txt", "e1t3b_f0.txt", "e1t3b_f1.txt", "e1t3b_f2.txt",
                  "e1t3b_f3.txt", "e1t3b_f4.txt", "f51.txt", "h36.txt", "masks_v0_pool532.md5"]
    for c in code:
        b = git_show(c); src_md5[f"code/{c}"] = (f"git {COMMIT[:7]}:{c}", md5b(b)); put(f"code/{c}", b)
    for s in sets_lists:
        c = f"bench/sets/{s}"
        b = git_show(c); src_md5[f"code/{c}"] = (f"git {COMMIT[:7]}:{c}", md5b(b)); put(f"code/{c}", b)

    # 2. benchmark build scripts (team folder)
    for s in ("make_masks_v11.py", "corpus_build.py", "groups_folds.py", "make_splits.py", "make_cells_table.py"):
        b = (BM / "scripts" / s).read_bytes(); src_md5[f"code/benchmark_scripts/{s}"] = (f"benchmark/scripts/{s}", md5b(b))
        put(f"code/benchmark_scripts/{s}", b)

    # 3. split, group and exclusion lists
    for s in ("cv5v3.json", "cv5v3_groups.tsv", "cv5v3_check.txt", "cv5v3_proposal.tsv", "cv5v2.json", "cv5v2_groups.tsv",
              "cv5v2_check.txt", "cv5v2_vs_b6.tsv", "legacy.json", "forbidden_v1.txt", "dup_crossfold_v1.tsv",
              "score_exclude_v2.txt", "score_exclude_v2c.txt", "score_exclude_v3.txt", "module_identity_v3.tsv",
              "pool532_manifest.tsv", "pool_t9_v2.txt"):
        b = (BM / "splits" / s).read_bytes(); src_md5[f"lists/{s}"] = (f"benchmark/splits/{s}", md5b(b)); put(f"lists/{s}", b)

    # 4. cell table: sealed rows reduced to SAFE_COLS (values never printed)
    b = (BM / "cells.tsv").read_bytes(); src_md5["lists/cells.tsv"] = ("benchmark/cells.tsv", md5b(b))
    rows = [l.split("\t") for l in b.decode().rstrip("\n").split("\n")]
    hdr = rows[0]; ir = hdr.index("role"); keep = [h in SAFE_COLS for h in hdr]
    n_sealed = n_blank = 0
    for r in rows[1:]:
        assert len(r) == len(hdr)
        if r[ir] in SEALED_ROLES:
            n_sealed += 1
            for j, k in enumerate(keep):
                if not k and r[j] != "":
                    r[j] = ""; n_blank += 1
    put("lists/cells.tsv", ("\n".join("\t".join(r) for r in rows) + "\n").encode())
    print(f"cells.tsv: {len(rows) - 1} rows, {n_sealed} sealed rows reduced to {sum(keep)} identity columns, {n_blank} values blanked")
    b = (BM / "CELLS_README.md").read_bytes(); src_md5["lists/CELLS_README.md"] = ("benchmark/CELLS_README.md", md5b(b))
    put("lists/CELLS_README.md", b)

    # 5. v1.1 manifests: train + val rows only
    for s, d in (("MANIFEST.tsv", "MANIFEST_pool532.tsv"), ("CHANGES.tsv", "CHANGES_pool532.tsv")):
        b = (BM / "out" / "masks_v11" / s).read_bytes(); src_md5[f"lists/labels_v11/{d}"] = (f"benchmark/out/masks_v11/{s}", md5b(b))
        L = b.decode().rstrip("\n").split("\n"); h = L[0].split("\t"); isp = h.index("legacy_split")
        kept = [L[0]] + [l for l in L[1:] if l.split("\t")[isp] in ("train", "val")]
        put(f"lists/labels_v11/{d}", ("\n".join(kept) + "\n").encode())
        print(f"{s}: kept {len(kept) - 1} of {len(L) - 1} rows (train + val)")

    json.dump({k: list(v) for k, v in sorted(src_md5.items())}, open(HERE / "sources.json", "w"), indent=1)
    with open(HERE / "substitutions.tsv", "w") as f:
        f.write("staged_path\trule\tline\tcount\n")
        for t in SUBS:
            f.write("\t".join(map(str, t)) + "\n")
    print(f"staged {len(src_md5)} files; {len(SUBS)} substituted lines, {sum(t[3] for t in SUBS)} substitutions")


if __name__ == "__main__":
    main()
