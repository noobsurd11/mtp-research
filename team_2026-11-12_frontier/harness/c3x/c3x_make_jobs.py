"""c3x: the jobs.txt of the cv02 queue c3x = the 25 runs of HRNet-W18 U-Net++ + swad_const on cv5v3 (lead's rulings C1, C5,
Q1 of 17 Nov 2026). No other line; the list does not depend on any other queue. (Built new; the 17:11 draft in draft_1711/
had a --logp and a --dump-gate option, both removed: logp 0 and dump gate 6200 are ruled.)

Usage: python c3x_make_jobs.py <out jobs.txt> [--gate MIB]

Line (cq.sh format of 852ed5c, 10 fields; the 10th = the further readout key, as the 25 swad lines of c3all3):
  c3x_hrnet_swad_v11_f<k>_s<s>|bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml|<s>|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f<k>|<k>|<gate>|6200|0||swad
  gate      the lead's ruling of 17 Nov 2026 17:35: job gate = max(11000, P + 2,048), P = the highest gaint peak of the new card
            over the memory and the path smoke (the RULE line of smoke/c3x_smoke_check.py); pass it as --gate (c3x_queue.sh
            build always passes it and checks it against that line). 11000 = the card's memory.gate_mib (cq.sh refuses a lower
            job gate) and the default here; below 11000: refused.
  dump gate 6200 (ruling C5) = the dump gate of every HRNet line of c3all3 (the dump loads one HRNet state dict; same code).
  logp 0    (ruling Q1) as the swad lines: two dumps per run; the read never uses logp.
  readout   'swad': second dump <name>.swad (weights key swad); the first dump is the card's weights_key swad_bn.
Order: seed 5 to 9, inside a seed fold 0 to 4 (as every arm of c3all3), so seeds finish in turn.
Names c3x_* match none of the relay patterns in use (^c3_, ^c3h_, ^c3s_, ^r2_); checked.
Refuses: an existing output file, a gate below 11000 or not a whole number, any other argument.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = "/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f{k}"
CARD = "bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml"
SEEDS, FOLDS = (5, 6, 7, 8, 9), (0, 1, 2, 3, 4)
GATE_MIN, DGATE, LOGP, RO = 11000, 6200, 0, "swad"
NAME_RX = re.compile(r"^c3x_hrnet_swad_v11_f([0-4])_s([5-9])$")
OTHER_RELAYS = (r"^c3_", r"^c3h_", r"^c3s_", r"^r2_")


def line(k: int, s: int, gate: int) -> str:
    return f"c3x_hrnet_swad_v11_f{k}_s{s}|{CARD}|{s}|{ROOT.format(k=k)}|{k}|{gate}|{DGATE}|{LOGP}||{RO}"


def main(argv) -> int:
    gate, pos, i = GATE_MIN, [], 0
    while i < len(argv):
        if argv[i] == "--gate":
            if i + 1 >= len(argv) or not argv[i + 1].isdigit():
                sys.exit("REFUSED: --gate needs a whole number of MiB")
            gate = int(argv[i + 1]); i += 2
        elif argv[i].startswith("-"):
            sys.exit(f"REFUSED: unknown option {argv[i]}")
        else:
            pos.append(argv[i]); i += 1
    if len(pos) != 1:
        sys.exit(__doc__)
    if gate < GATE_MIN:
        sys.exit(f"REFUSED: gate {gate} is below the card's gate {GATE_MIN}")
    out = Path(pos[0])
    if out.exists():
        sys.exit(f"REFUSED: {out} exists")
    lines = [line(k, s, gate) for s in SEEDS for k in FOLDS]
    names = [ln.split("|", 1)[0] for ln in lines]
    assert len(lines) == 25 and len(set(names)) == 25
    for ln, n in zip(lines, names):
        m = NAME_RX.match(n)
        f = ln.split("|")
        assert m and len(f) == 10, ln
        assert int(f[2]) == int(m.group(2)) and int(f[4]) == int(m.group(1)) and f[3] == ROOT.format(k=int(m.group(1))), ln
        assert f[1] == CARD and f[5] == str(gate) and f[6] == "6200" and f[7] == "0" and f[8] == "" and f[9] == "swad", ln
        hit = [rx for rx in OTHER_RELAYS if re.search(rx, n)]
        if hit:
            sys.exit(f"REFUSED: {n} matches the relay pattern {hit[0]}")
    assert sorted({int(ln.split("|")[2]) for ln in lines}) == list(SEEDS)
    assert all(sorted(int(ln.split("|")[4]) for ln in lines if int(ln.split("|")[2]) == s) == list(FOLDS) for s in SEEDS)
    text = "".join(ln + "\n" for ln in lines)
    out.write_text(text)
    print(f"c3x list: {len(lines)} lines, seeds {SEEDS[0]} to {SEEDS[-1]} x folds {FOLDS[0]} to {FOLDS[-1]}, card {CARD}")
    print(f"gate {gate} MiB, dump gate {DGATE} MiB, logp {LOGP}, further readout {RO}; first line: {lines[0]}")
    print(f"wrote {out} md5 {hashlib.md5(text.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
