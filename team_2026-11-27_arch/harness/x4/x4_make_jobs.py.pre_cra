"""x4: card list -> jobs.tsv for the cv02 queue (cq.sh of the x4 commit, 10-field lines), md5 pinned.

Usage (gaint):
  python x4_make_jobs.py --out jobs.tsv [--repo /home/noob/work/bench_wt_x4] [--seeds 5,6] [--folds 0,1,2,3,4]
      [--dump-gate 6200] [--extra '--exit_after_step N'] CARD[=SHORT][@PEAK_MIB] [CARD...]
  CARD   bench/methods/<m>.yaml in --repo (the x4 worktree; the cv02 deploy of the same commit holds the same file).
  SHORT  run-name stem: runs are named <prefix>_<SHORT>_f<k>_s<s> (prefix x4, or smoke_x4 with --extra); default = card name.
  PEAK   measured training peak on cv02 in MiB. Job gate = max(card memory.gate_mib, PEAK + 2,048). Without @PEAK the card's
         memory.peak_mib is used; if that is null too, the list is refused (measure first: a 300-step memory smoke).
--commit C (x4 shared queue, cq_x4.sh): the card is read from commit C (git show C:<card>, also its cv02 variant) and the
  line gets an 11th field = C (the job trains in cv02 /tmp/noob_el/bench_<C 7 hex>, which must be deployed).
Line: name|card|seed|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f<k>|k|gate|dump gate|0||<readouts>[|<commit>]
  readouts (10th field) = 'swad' when the card has a readout with weights_key swad and its own weights_key is not swad: the
  queue then dumps <name> (card weights_key) and <name>.swad; the x4 comparator is COMBO's swad readout.
  logp 0. Roots: cv5v3 v1.1, held-out fold = val = test (open cells only; no sealed set is ever dumped by cq.sh).
Order: seed, then fold. Refuses: an existing output, an unknown card, a name collision, a name outside [a-z0-9_], an --extra
other than '--exit_after_step N' (smoke_x4_* jobs only; cq.sh runs no dump for them).
Measured (E, cv02 c3x gpumem.log, all 25 runs): COMBO card peak 9,386 MiB -> gate 11,434 MiB.
"""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = "/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f{k}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--repo", default="/home/noob/work/bench_wt_x4")
    ap.add_argument("--seeds", default="5,6")
    ap.add_argument("--folds", default="0,1,2,3,4")
    ap.add_argument("--dump-gate", type=int, default=6200)
    ap.add_argument("--extra", default="")
    ap.add_argument("--commit", default="", help="full commit of the job's deploy (11th field; cq_x4.sh queues)")
    ap.add_argument("cards", nargs="+")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        sys.exit(f"REFUSED: {out} exists")
    if a.commit and not re.fullmatch(r"[0-9a-f]{40}", a.commit):
        sys.exit("REFUSED: --commit must be a full 40-hex commit")
    if a.extra and not re.fullmatch(r"--exit_after_step [0-9]+", a.extra):
        sys.exit("REFUSED: --extra may only be '--exit_after_step N'")
    prefix = "smoke_x4" if a.extra else "x4"
    seeds = [int(x) for x in a.seeds.split(",")]
    folds = [int(x) for x in a.folds.split(",")]
    assert set(folds) <= set(range(5)) and seeds, (folds, seeds)
    lines, meta = [], []
    for spec in a.cards:
        m = re.fullmatch(r"([^=@]+)(?:=([a-z0-9_]+))?(?:@([0-9]+))?", spec)
        if not m:
            sys.exit(f"REFUSED: bad card spec {spec!r}")
        card, short, peak = m.group(1), m.group(2), m.group(3)
        p = Path(a.repo) / card
        if not card.startswith("bench/methods/"):
            sys.exit(f"REFUSED: {card} is not under bench/methods/")
        if a.commit:
            def show(path):
                r = subprocess.run(["git", "-C", a.repo, "show", f"{a.commit}:{path}"], capture_output=True)
                if r.returncode:
                    sys.exit(f"REFUSED: {path} not in commit {a.commit[:7]}")
                return r.stdout
            raw = show(card); show("bench/methods_cv02/" + p.name)
        else:
            if not p.is_file():
                sys.exit(f"REFUSED: {card} is not a card file under {a.repo}/bench/methods/")
            if not (Path(a.repo) / "bench/methods_cv02" / p.name).is_file():
                sys.exit(f"REFUSED: no cv02 variant bench/methods_cv02/{p.name}")
            raw = p.read_bytes()
        c = yaml.safe_load(raw.decode())
        short = short or c["name"]
        mem = c.get("memory") or {}
        peak = int(peak) if peak else mem.get("peak_mib")
        if peak is None:
            sys.exit(f"REFUSED: {card}: no measured peak (give CARD@PEAK_MIB from a memory smoke on cv02)")
        gate = max(int(mem.get("gate_mib") or 0), int(peak) + 2048)
        keys = [r.get("weights_key") for r in (c.get("readouts") or [])]
        ro = "swad" if ("swad" in keys and c.get("weights_key") != "swad") else ""
        md5 = hashlib.md5(raw).hexdigest()
        meta.append(f"# card {card}{'@' + a.commit[:7] if a.commit else ''} md5 {md5} name {c['name']} weights_key {c.get('weights_key')} peak {peak} gate {gate} readouts '{ro}'")
        for s in seeds:
            for k in folds:
                n = f"{prefix}_{short}_f{k}_s{s}"
                if not re.fullmatch(r"[a-z0-9_]+", n):
                    sys.exit(f"REFUSED: run name {n} not [a-z0-9_]")
                lines.append(f"{n}|{card}|{s}|{ROOT.format(k=k)}|{k}|{gate}|{a.dump_gate}|0|{a.extra}|{'' if a.extra else ro}" + (f"|{a.commit}" if a.commit else ""))
    names = [ln.split("|", 1)[0] for ln in lines]
    if len(set(names)) != len(names):
        sys.exit("REFUSED: duplicate run names")
    text = "".join(ln + "\n" for ln in lines)
    out.write_text(text)
    h = hashlib.md5(text.encode()).hexdigest()
    Path(str(out) + ".md5").write_text(f"{h}  {out.name}\n" + "\n".join(meta) + "\n")
    print("\n".join(meta))
    print(f"wrote {out}: {len(lines)} lines, md5 {h}; first line: {lines[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
