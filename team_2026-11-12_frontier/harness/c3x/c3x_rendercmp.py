"""c3x: compare the rendered c3x lines (cq.sh jobs_rendered.txt, cv02 paths) with cv02 c3all3's own jobs_rendered.txt.
  - 75 lines: per job one train line, dump_<name> and dump_<name>.swad; no line has --logp;
  - every train line holds the 8 swad opts directly before data.root=;
  - train line of c3x f<k> s<s> minus the 8 opts, with the name c3h_hrnet_w18_unetpp_pf_f<k>_s<s>, equals c3all3's HRNet line
    of the same fold and seed (where c3all3 has one: f3, f4 s7 and s8, s9 = 12 jobs);
  - both dump lines of c3x f<k> s<s>, with the deploy dir, method, card and name of c3s_swad_v11_f<k>_s<s>, equal c3all3's two
    swad dump lines (all 25 jobs).
Usage: python c3x_rendercmp.py --rendered R --c3all3 C --xb /tmp/noob_el/bench_<7 hex>   (exit 0 only if everything holds)
"""
import argparse
import sys

OPTS8 = (" training.lr_scheduler=constant training.weight_avg.swad.mode=uniform training.weight_avg.swad.start=10000 "
         "training.weight_avg.swad.end=20000 training.weight_avg.ema_9998.mode=ema training.weight_avg.ema_9998.decay=0.9998 "
         "training.bn_recal=true training.enc_probe_every=2000")
B89 = "/tmp/noob_el/bench_89b9ea5/"


def load(p):
    d = {}
    for line in open(p):
        line = line.rstrip("\n")
        if line:
            k, _, v = line.partition("|")
            assert k not in d, f"{p}: {k} twice"
            d[k] = line
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rendered", required=True)
    ap.add_argument("--c3all3", required=True)
    ap.add_argument("--xb", required=True)
    a = ap.parse_args()
    R, C = load(a.rendered), load(a.c3all3)
    xb = a.xb.rstrip("/") + "/"
    bad, nt, et, ed = [], 0, 0, 0
    names = [f"c3x_hrnet_swad_v11_f{k}_s{s}" for s in range(5, 10) for k in range(5)]
    want = {x for n in names for x in (n, f"dump_{n}", f"dump_{n}.swad")}
    if set(R) != want:
        bad.append(f"rendered keys differ: {len(R)} lines; missing {sorted(want - set(R))[:3]}; extra {sorted(set(R) - want)[:3]}")
    if any(" --logp" in v for v in R.values()):
        bad.append("a rendered line has --logp")
    for n in names:
        k, s = n[-4], n[-1]
        h, w = f"c3h_hrnet_w18_unetpp_pf_f{k}_s{s}", f"c3s_swad_v11_f{k}_s{s}"
        t = R.get(n, "")
        if OPTS8 + " data.root=" not in t:
            bad.append(f"{n}: train line lacks the 8 opts before data.root")
        if h in C:
            nt += 1
            m = t.replace(OPTS8, "").replace(n, h)
            et += m == C[h]
            if m != C[h]:
                bad.append(f"{n}: train line differs from {h}'s after removing the 8 opts")
        for sfx in ("", ".swad"):
            d, ref = R.get(f"dump_{n}{sfx}", ""), C.get(f"dump_{w}{sfx}")
            m = (d.replace(xb, B89).replace("--method hrnet_w18_unetpp_swad_const_pf_v11", "--method swad_const_pf_v11")
                 .replace("bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml", "bench/methods/swad_const_pf_v11.yaml").replace(n, w))
            ed += ref is not None and m == ref
            if ref is None or m != ref:
                bad.append(f"dump_{n}{sfx}: differs from dump_{w}{sfx} after mapping")
    print(f"rendered {len(R)} lines (75 expected), --logp in {sum(' --logp' in v for v in R.values())}; "
          f"train: {et} of {nt} lines with an HRNet twin in c3all3 equal it without the 8 opts; "
          f"dumps: {ed} of 50 equal c3all3's swad dump line after mapping deploy dir, method, card and name")
    for b in bad[:10]:
        print("FAIL " + b)
    print(f"render compare: {len(bad)} FAIL")
    return 1 if bad or nt == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
