"""c3x: job list of the cv02 queue c3x: the 25 runs of the combination HRNet-W18 U-Net++ + swad_const on cv5v3
(lead's ruling C1, 17 Nov 2026). No other line. The list does not depend on any other queue.

Usage: c3x_make_jobs.py <out jobs.txt> [--gate MIB] [--dump-gate MIB] [--logp 0|1]

Line (cq.sh format of 852ed5c, 10 fields; the 10th = the further readout key, as the swad lines of c3all3):
  c3x_hrnet_swad_v11_f<k>_s<s>|bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml|<s>|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f<k>|<k>|11000|6200|0||swad
  gate 11000      = the card's gate (cq.sh refuses less). Basis: HRNet PF peak 8,430 MiB on cv02 (card hrnet_w18_unetpp_pf_v11)
                    + the averaged copies; expected peak 8,650 to 8,760; + 2,048 = at most 10,808. --gate raises it when
                    the GPU smoke shows a higher peak (peak + 2,048); a value below 11000 is refused.
  dump gate 6200  = the dump gate of the HRNet lines of c3all3 (the dump loads one state dict of the same network).
                    A value below 6200 is refused.
  logp 0          = as the swad lines (two dumps per run; the read never uses logp).
  readouts "swad" = second dump <name>.swad from the state dict swad; the first dump is the card's weights_key swad_bn.
Order: seed 5 to 9, inside a seed fold 0 to 4 (as every arm of c3all3), so the seeds finish in turn.
Names c3x_* match none of the relay patterns ^c3_ , ^c3h_ , ^c3s_ , ^r2_ (checked).
Refuses: an existing output file, a gate below the floors, a name that matches a running relay's pattern.
Prints a summary; exit 0 only if every check holds.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = "/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f{k}"
CARD = "bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml"
SEEDS, FOLDS = (5, 6, 7, 8, 9), (0, 1, 2, 3, 4)
GATE_MIN, DGATE_MIN = 11000, 6200
NAME_RX = re.compile(r"^c3x_hrnet_swad_v11_f([0-4])_s([5-9])$")
OTHER_RELAYS = (r"^c3_", r"^c3h_", r"^c3s_", r"^r2_")


def line(k: int, s: int, gate: int, dgate: int, logp: int) -> str:
    return f"c3x_hrnet_swad_v11_f{k}_s{s}|{CARD}|{s}|{ROOT.format(k=k)}|{k}|{gate}|{dgate}|{logp}||swad"


def main() -> int:
    a = sys.argv[1:]
    opt = {"--gate": GATE_MIN, "--dump-gate": DGATE_MIN, "--logp": 0}
    pos = []
    i = 0
    while i < len(a):
        if a[i] in opt:
            if i + 1 >= len(a) or not a[i + 1].isdigit():
                sys.exit(f"REFUSED: {a[i]} needs a whole number")
            opt[a[i]] = int(a[i + 1]); i += 2
        elif a[i].startswith("--"):
            sys.exit(f"REFUSED: unknown option {a[i]}")
        else:
            pos.append(a[i]); i += 1
    if len(pos) != 1:
        sys.exit(__doc__)
    gate, dgate, logp = opt["--gate"], opt["--dump-gate"], opt["--logp"]
    if gate < GATE_MIN:
        sys.exit(f"REFUSED: gate {gate} is below the card's gate {GATE_MIN}")
    if dgate < DGATE_MIN:
        sys.exit(f"REFUSED: dump gate {dgate} is below {DGATE_MIN}")
    if logp not in (0, 1):
        sys.exit("REFUSED: --logp must be 0 or 1")
    out = Path(pos[0])
    if out.exists():
        sys.exit(f"REFUSED: {out} exists")
    lines = [line(k, s, gate, dgate, logp) for s in SEEDS for k in FOLDS]
    names = [ln.split("|", 1)[0] for ln in lines]
    assert len(lines) == 25 and len(set(names)) == 25
    for ln, n in zip(lines, names):
        m = NAME_RX.match(n)
        f = ln.split("|")
        assert m and len(f) == 10, ln
        assert int(f[2]) == int(m.group(2)) and int(f[4]) == int(m.group(1)) and f[3] == ROOT.format(k=int(m.group(1))), ln
        assert f[1] == CARD and f[8] == "" and f[9] == "swad", ln
        hit = [rx for rx in OTHER_RELAYS if re.search(rx, n)]
        if hit:
            sys.exit(f"REFUSED: {n} matches the relay pattern {hit[0]}")
    assert sorted({int(ln.split('|')[2]) for ln in lines}) == list(SEEDS)
    assert all(sorted(int(ln.split("|")[4]) for ln in lines if int(ln.split("|")[2]) == s) == list(FOLDS) for s in SEEDS)
    text = "".join(ln + "\n" for ln in lines)
    out.write_text(text)
    print(f"c3x list: {len(lines)} lines, seeds {SEEDS[0]} to {SEEDS[-1]} x folds {FOLDS[0]} to {FOLDS[-1]}, card {CARD}")
    print(f"gate {gate} MiB, dump gate {dgate} MiB, logp {logp}, further readout swad; first line: {lines[0]}")
    print(f"wrote {out} md5 {hashlib.md5(text.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
