"""c3swad: job list of the merged cv02 queue that follows a frozen queue (MAXC 0), with the 25 swad_const runs.

Usage: c3swad_make_jobs.py <prev jobs.txt> <started names> <out jobs.txt> [--no-swad | --alternate]
  prev jobs.txt   the frozen queue's job list (c3all: md5 c58f610b726bec9bae9b302606c7bc03), fetched read-only from cv02
  started names   one name per line: every job of the frozen queue that has pids/<name>.gpu (read after MAXC 0 and the
                  settle wait); these lines are left out, all others are carried over byte for byte
  --no-swad       reorder only (no swad lines; such a list needs no new queue code)
  --alternate     the other order: swad and HRNet in turn by seed (swad s5, HRNet first seed left, swad s6, HRNet next,
                  swad s7, HRNet next, then the swad seeds left, then any HRNet left); not the default

Order (lead's ruling Q4, 17 Nov 09:35): PF first, then all swad seeds, then HRNet, then HOUSE; inside each arm seed,
then fold ascending. Reason: the registered HRNet read needs HOUSE s7 to s9, which end last in both orders, so swad
first moves the swad verdict earlier and nothing later.

swad line (cq.sh format with the 10th field of cq_c3swad.patch):
  c3s_swad_v11_f<k>_s<s>|bench/methods/swad_const_pf_v11.yaml|<s>|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f<k>|<k>|11000|5262|0||swad
  gate 11000 = the card's gate (cq.sh refuses less; measured gaint peak 7,154 MiB + 2,048 = 9,202); dump gate 5262 = the
  PF lines' (same network; measured cv02 dump peak 3,212 MiB + 2,048); logp 0; readouts field "swad".
Names c3s_* match neither running relay (^c3_ and ^c3h_).
Refuses: an unknown name pattern, a repeated name, a started name that is not in the list, an existing output file.
Prints a summary; exit 0 only if every check holds.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = "/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f{k}"
SWAD_CARD = "bench/methods/swad_const_pf_v11.yaml"
SEEDS, FOLDS = (5, 6, 7, 8, 9), (0, 1, 2, 3, 4)
ARMS = {
    "pf": re.compile(r"^c3_pf_v11_f([0-4])_s([5-9])$"),
    "house": re.compile(r"^c3_house_v11_f([0-4])_s([5-9])$"),
    "hrnet": re.compile(r"^c3h_hrnet_w18_unetpp_pf_f([0-4])_s([5-9])$"),
    "swad": re.compile(r"^c3s_swad_v11_f([0-4])_s([5-9])$"),
}


def swad_line(k: int, s: int) -> str:
    return f"c3s_swad_v11_f{k}_s{s}|{SWAD_CARD}|{s}|{ROOT.format(k=k)}|{k}|11000|5262|0||swad"


def classify(name: str):
    for arm, rx in ARMS.items():
        m = rx.match(name)
        if m:
            return arm, int(m.group(2)), int(m.group(1))
    sys.exit(f"REFUSED: unknown job name pattern: {name}")


def main() -> int:
    args = [a for a in sys.argv[1:] if a not in ("--no-swad", "--alternate")]
    no_swad = "--no-swad" in sys.argv[1:]
    swad_first = "--alternate" not in sys.argv[1:]
    if no_swad and not swad_first:
        sys.exit("REFUSED: --no-swad and --alternate together")
    if len(args) != 3:
        sys.exit(__doc__)
    prev, started_f, out = Path(args[0]), Path(args[1]), Path(args[2])
    if out.exists():
        sys.exit(f"REFUSED: {out} exists")
    lines = [ln for ln in prev.read_text().split("\n") if ln]
    names = [ln.split("|", 1)[0] for ln in lines]
    if len(set(names)) != len(names):
        sys.exit("REFUSED: repeated name in the previous list")
    started = [x.strip() for x in started_f.read_text().split("\n") if x.strip()]
    unknown = sorted(set(started) - set(names))
    if unknown:
        sys.exit(f"REFUSED: started names not in the previous list: {unknown[:5]}")
    left = {}                                             # arm -> {(seed, fold): line}
    for ln, n in zip(lines, names):
        arm, s, k = classify(n)
        if n not in set(started):
            left.setdefault(arm, {})[(s, k)] = ln
            f = ln.split("|")
            if int(f[2]) != s or int(f[4]) != k or f[3] != ROOT.format(k=k):
                sys.exit(f"REFUSED: seed, fold or root of {n} does not match its name")
    new_swad = []
    if not no_swad and "swad" not in {classify(n)[0] for n in names}:
        new_swad = [swad_line(k, s) for s in SEEDS for k in FOLDS]
        for ln in new_swad:
            arm, s, k = classify(ln.split("|", 1)[0])
            left.setdefault("swad", {})[(s, k)] = ln

    def block(arm, seed):
        return [left[arm][key] for key in sorted(left.get(arm, {})) if key[0] == seed]

    def seeds_of(arm):
        return sorted({s for s, _ in left.get(arm, {})})

    order, plan = [], []

    def add(arm, seed):
        b = block(arm, seed)
        if b:
            order.extend(b); plan.append(f"{arm} s{seed} ({len(b)})")

    for s in seeds_of("pf"):
        add("pf", s)
    sw, hr = seeds_of("swad"), seeds_of("hrnet")
    for i in range(0 if swad_first else 3):
        if i < len(sw):
            add("swad", sw[i])
        if i < len(hr):
            add("hrnet", hr[i])
    for s in (sw if swad_first else sw[3:]):
        add("swad", s)
    for s in (hr if swad_first else hr[3:]):
        add("hrnet", s)
    for s in seeds_of("house"):
        add("house", s)

    onames = [ln.split("|", 1)[0] for ln in order]
    carried = [ln for ln, n in zip(lines, names) if n not in set(started)]
    assert len(set(onames)) == len(onames), "repeated name in the output"
    assert sorted(order) == sorted(carried + new_swad), "output line set != carried lines + swad lines"
    assert not set(onames) & set(started), "a started job is in the output"
    for ln in order:                                      # field count: 9 fields for carried lines, 10 for swad lines
        assert ln.count("|") == (9 if ln.startswith("c3s_swad_") else 8), ln
    text = "".join(ln + "\n" for ln in order)
    out.write_text(text)
    md5 = hashlib.md5(text.encode()).hexdigest()
    cnt = {a: len(left.get(a, {})) for a in ARMS}
    print(f"previous list: {len(lines)} lines (md5 {hashlib.md5(prev.read_bytes()).hexdigest()}), started {len(started)}, carried over {len(carried)}")
    print(f"new swad lines: {len(new_swad)}; output: {len(order)} lines = pf {cnt['pf']}, swad {cnt['swad']}, hrnet {cnt['hrnet']}, house {cnt['house']}")
    print("order: " + ", ".join(plan))
    print(f"carried lines byte-identical to the previous list: {all(ln in set(lines) for ln in carried)}")
    print(f"wrote {out} md5 {md5}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
