"""integrator c3base: config of the 50 c3base tuples (PF / HOUSE v1.1 cards, folds 0-4, seeds 5-9) on the cv5v3 root
against the same card, seed and name on the cv5v2 root of the same fold (bench.cards expected_config at the deploy tree).
Also two config_used.yaml files (5-step runs) given with --pair A B. Prints the flattened keys that differ (no values
except data.root). Usage: c3_rdiff.py <repo> [--pair A.yaml B.yaml]"""
import sys
from pathlib import Path

import yaml

repo = Path(sys.argv[1])
sys.path.insert(0, str(repo))
from bench import cards  # noqa: E402


def flat(d, p=""):
    out = {}
    for k, v in d.items():
        key = f"{p}{k}"
        if isinstance(v, dict):
            out.update(flat(v, key + "."))
        else:
            out[key] = v
    return out


def diff(a, b):
    fa, fb = flat(a), flat(b)
    return sorted(k for k in set(fa) | set(fb) if fa.get(k) != fb.get(k))


if len(sys.argv) > 2 and sys.argv[2] == "--pair":
    a, b = (yaml.safe_load(open(x)) for x in sys.argv[3:5])
    print(f"config_used diff keys: {diff(a, b)}")
    sys.exit(0)

V2 = "/home/noob/work/bench_data/roots/cv5v2_v11_f{k}"
V3 = "/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f{k}"
seen, bad, n = {}, 0, 0
for tag, card in (("pf", "house_r34_unetpp_pf_v11"), ("house", "house_r34_unetpp_v11")):
    c = cards.load_card(repo / f"bench/methods/{card}.yaml")
    for s in (5, 6, 7, 8, 9):
        for k in range(5):
            name = f"c3_{tag}_v11_f{k}_s{s}"
            a = cards.expected_config(c, s, name, V2.format(k=k))
            b = cards.expected_config(c, s, name, V3.format(k=k))
            d = diff(a, b)
            n += 1
            ok = d == ["data.root"] and flat(b)["data.root"] == V3.format(k=k)
            bad += not ok
            seen[tuple(d)] = seen.get(tuple(d), 0) + 1
print(f"c3base tuples: {n}; differing keys cv5v2 root -> cv5v3 root: {dict(seen)}; tuples with any other difference: {bad}")
sys.exit(1 if bad else 0)
