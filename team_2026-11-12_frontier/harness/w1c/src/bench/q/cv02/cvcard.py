"""cv02 card variant check (PyYAML only). bench/methods_cv02/<m>.yaml must equal bench/methods/<m>.yaml in every key except
weights[i].path (the cv02 HF cache path of the same file; same md5). Prints one line per weights file: "<md5> <cv02 path>".
Exit 1 with a reason if anything else differs.
Usage: python bench/q/cv02/cvcard.py bench/methods/<m>.yaml bench/methods_cv02/<m>.yaml
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from bench.cards import load_card  # noqa: E402


def main(a: str, b: str) -> int:
    ca, cb = load_card(a), load_card(b)
    if len(ca["weights"] or []) != len(cb["weights"] or []):
        print(f"FAIL weights count differs: {a} vs {b}")
        return 1
    xa, xb = copy.deepcopy(ca), copy.deepcopy(cb)
    for w in (xa["weights"] or []) + (xb["weights"] or []):
        w["path"] = "<path>"
    if xa != xb:
        keys = sorted(k for k in set(xa) | set(xb) if xa.get(k) != xb.get(k))
        print(f"FAIL {b} differs from {a} beyond weights paths: {keys}")
        return 1
    for wa, wb in zip(ca["weights"] or [], cb["weights"] or []):
        print(wb["md5"], wb["path"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
