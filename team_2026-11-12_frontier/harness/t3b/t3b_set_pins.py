"""Builder's tool: write the pins of the T3b package into its scripts (re-runnable; regex on the pin lines).
Pins: K (full commit) and its tree; t3b_make_jobs.py, T3B_RULE.md, diskguard8.sh, t3b_rendercmp.py md5s; K's bench_infer.py md5;
PINS (md5 of the deployed files t3b_queue.sh checks on cv02) and DW (the CODE.md5 diff of the deploy of K against the deploy
of F2, computed from git archives exactly as c3_deploy.sh writes CODE.md5).
Usage: python t3b_set_pins.py <K commit> [--rule-only]
"""
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

H = Path(__file__).resolve().parent
REPO = "/home/noob/work/bench_wt_t3b"
F2 = "9967d59abaab03cef83c1e3014840b2359ef45d7"
PIN_FILES = ["bench/q/cv02/cq.sh", "bench/q/cv02/cq_setup.sh", "bench/q/cv02/cq_gpumem.sh", "bench/q/cv02/cvcard.py",
             "bench/q/cv02/slim_ckpt.py", "bench/q/bench_lib.sh", "scripts/train.py", "scripts/bench_infer.py", "bench/tta.py",
             "bench/sets.py", "bench/dumpfmt.py", "bench/cards.py", "src/trainers/weight_avg.py", "src/data/benchmark_el.py",
             "bench/sets/e1_106_stems.txt"] + [f"bench/sets/e1t3b_f{k}.txt" for k in range(5)] + [
             "bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml", "bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml"]


def md5b(b):
    return hashlib.md5(b).hexdigest()


def md5(p):
    return md5b(Path(p).read_bytes())


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, check=True).stdout


def code_md5(commit, d):
    subprocess.run(f"git -C {REPO} archive {commit} | tar -x -C {d} && echo {commit} > {d}/REVISION", shell=True, check=True)
    out = {}
    for p in sorted(Path(d).rglob("*")):
        if p.is_file() and not p.is_symlink():
            out[str(p.relative_to(d))] = md5(p)
    return out


def sub(path, pat, rep, flags=0):
    s = Path(path).read_text()
    s2, n = re.subn(pat, rep, s, flags=flags)
    assert n == 1, f"{path}: pattern {pat!r} matched {n} times"
    Path(path).write_text(s2)


def main(argv):
    k = git("rev-parse", f"{argv[0]}^{{commit}}").strip()
    tree = git("rev-parse", f"{k}^{{tree}}").strip()
    rule = md5(H / "T3B_RULE.md") if (H / "T3B_RULE.md").exists() else "__RULE_MD5__"
    if "--rule-only" in argv:
        sub(H / "t3b_register.sh", r"^RULE_PIN=\S+$", f"RULE_PIN={rule}", re.M)
        print(f"RULE_PIN {rule}")
        return
    with tempfile.TemporaryDirectory(dir="/home/noob/work/bench_int_io") as t:
        a, b = Path(t) / "f2", Path(t) / "k"
        a.mkdir(); b.mkdir()
        fa, fb = code_md5(F2, a), code_md5(k, b)
        pins = "\n".join(f"{fb[p]}  {p}" for p in PIN_FILES)
        winf = fb["scripts/bench_infer.py"]
    fa.pop("REVISION"); fb.pop("REVISION")
    dw = sorted([f"<{p}" for p in fa if fb.get(p) != fa[p]] + [f">{p}" for p in fb if fa.get(p) != fb[p]])
    dw = " ".join(dw) + " "
    sub(H / "t3b_queue.sh", r"^KC=\S+; F2C=", f"KC={k}; F2C=", re.M)
    sub(H / "t3b_queue.sh", r'\[ "\$GUARD8_MD5" = \S+ \]', f'[ "$GUARD8_MD5" = {md5(H / "diskguard8.sh")} ]')
    sub(H / "t3b_queue.sh", r'(t3b_rendercmp\.py \| cut -c1-32\)" = )\S+( \])', rf'\g<1>{md5(H / "t3b_rendercmp.py")}\g<2>')
    sub(H / "t3b_queue.sh", r'^PINS="[^"]*"$', f'PINS="{pins}"', re.M)
    sub(H / "t3b_queue.sh", r'^DW="[^"]*"$', f'DW="{dw}"', re.M)
    sub(H / "t3b_relay.sh", r"^KC=\S+; KB=", f"KC={k}; KB=", re.M)
    sub(H / "run_t3b_read.sh", r"^K=\S+; F2=", f"K={k}; F2=", re.M)
    sub(H / "run_t3b_read.sh", r'^W_K="bench_infer\.py \S+"; W_G=', f'W_K="bench_infer.py {winf}"; W_G=', re.M)
    # the register last: it pins the md5s of the scripts above (review round 1 B2)
    names = ["run_t3b_read.sh", "t3b_verdict.py", "t3b_queue.sh", "t3b_relay.sh", "t3b_rendercmp.py", "diskguard8.sh", "t3b_label_precheck.py"]
    sp = " ".join(f"{n}={md5(H / n)}" for n in names)
    sub(H / "t3b_register.sh", r"^RULE_PIN=\S+$", f"RULE_PIN={rule}", re.M)
    sub(H / "t3b_register.sh", r"^MAKE_MD5=\S+$", f"MAKE_MD5={md5(H / 't3b_make_jobs.py')}", re.M)
    sub(H / "t3b_register.sh", r"^K=\$\{K:-[^}]+\}; K_TREE=\S+$", f"K=${{K:-{k}}}; K_TREE={tree}", re.M)
    sub(H / "t3b_register.sh", r'^SCRIPT_PINS="[^"]*"$', f'SCRIPT_PINS="{sp}"', re.M)
    print(f"K {k} tree {tree}; rule {rule}; make {md5(H / 't3b_make_jobs.py')}; guard8 {md5(H / 'diskguard8.sh')}; "
          f"rendercmp {md5(H / 't3b_rendercmp.py')}; bench_infer(K) {winf}; DW {len(dw.split())} entries")
    print("scripts " + sp)


if __name__ == "__main__":
    main(sys.argv[1:])
