"""Job list of the sealed-set opening (OPENING_RULE.md sections 2 and 9): dump-only lines of the fin full-pool runs for cq.sh
of G in a sealed-opening queue (Q/SEALED). Usage: python opening_make_jobs.py --c1d4 yes|no OUT
  E1 (e1_106, opening e1_open8_final):  C2 = fin_hrnet_swad_v11_pool_s<s>.swad.tta_d4.e1_106 (key swad, d4, logp 1: C3 members)
                                         C1 = fin_pf_v11_pool_s<s>.e1_106 (key model, plain, logp 1: E-PF members)
                                         C1-D4 = fin_pf_v11_pool_s<s>.tta_d4.e1_106 (key model, d4, logp 0), only with --c1d4 yes
  test50 (opening t50_open19_final):     the same three kinds with .test50, logp 0 everywhere
Seeds 5 to 9. Order: E1 C2, E1 C1, (E1 C1-D4), test50 C2, test50 C1, (test50 C1-D4). Refuses an existing OUT.
Asserts: distinct names, each name = '<run>.' ... '.<set>', exactly the expected count, no field outside the template.
"""
import argparse
import sys
from pathlib import Path

EXP = "/tmp/noob_el/bench_9967d59/experiments"   # F2B: the full-pool runs after the fin2 resume (REVIEW_FIN2 N3)
ROOT = "/tmp/noob_el/bench_data_fin/roots/pool532_v11"
CARD_X = "bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml"
CARD_P = "bench/methods/house_r34_unetpp_pf_v11.yaml"
GATE_X, GATE_P, DGATE = 11510, 9000, 6200            # fin's gates (LAUNCH_REQUEST_final.md section 3)
SEEDS = (5, 6, 7, 8, 9)
SETS = {"e1_106": "e1_open8_final", "test50": "t50_open19_final"}


def lines(c1d4: bool) -> list[str]:
    out = []
    for st in SETS:
        lp = 1 if st == "e1_106" else 0
        kinds = [("C2", "fin_hrnet_swad_v11_pool_s{s}", ".swad.tta_d4", CARD_X, GATE_X, "swad", "d4", lp),
                 ("C1", "fin_pf_v11_pool_s{s}", "", CARD_P, GATE_P, "model", "none", lp)]
        if c1d4:
            kinds.append(("C1D4", "fin_pf_v11_pool_s{s}", ".tta_d4", CARD_P, GATE_P, "model", "d4", 0))
        for _, run_t, mid, card, gate, key, tta, logp in kinds:
            for s in SEEDS:
                run = run_t.format(s=s)
                name = f"{run}{mid}.{st}"
                extra = f"--dumpof {EXP}/{run} --key {key} --tta {tta} --set {st}"
                out.append(f"{name}|{card}|{s}|{ROOT}|0|{gate}|{DGATE}|{logp}|{extra}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--c1d4", required=True, choices=("yes", "no"))
    ap.add_argument("out")
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refuse: {out} exists")
    L = lines(a.c1d4 == "yes")
    names = [l.split("|", 1)[0] for l in L]
    assert len(set(names)) == len(names) == (30 if a.c1d4 == "yes" else 20), len(names)
    for l in L:
        f = l.split("|")
        assert len(f) == 9 and f[3] == ROOT and f[4] == "0" and f[7] in ("0", "1"), l
        run = f[8].split()[1].rsplit("/", 1)[1]
        st = f[8].split()[-1]
        assert f[0].startswith(run + ".") and f[0].endswith("." + st) and st in SETS, l
        assert (f[7] == "1") == (st == "e1_106" and ".tta_d4." not in f[0].replace(".swad.tta_d4.", ".")), l
    out.write_text("".join(l + "\n" for l in L))
    print(f"wrote {out}: {len(L)} lines (C1-D4 {'in' if a.c1d4 == 'yes' else 'not in'} the opening; E1 logp lines "
          f"{sum(1 for l in L if l.split('|')[7] == '1')})")


if __name__ == "__main__":
    main()
