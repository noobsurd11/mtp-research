"""arch A6 addendum (descriptive): ORACLE cell gate = remove every predicted crack px on cells with n_gt == 0
(label-aware upper bound on what any cell gate can do), at each run's ungated val b_rel. Same records as a6_gate.py;
reads its json for b_rel; val + _rf only."""
import json, sys
from pathlib import Path
T = Path(__file__).resolve().parents[2]
A = json.load(open(T / "ideas/arch_out/a6_gate_s1.json"))
RFSET = {l.split("\t")[0]: l.split("\t")[1] for l in open(T / "ideas/found_scripts/t9_rf_sets.tsv") if l.strip()}
out = []
for arm, runs in A.items():
    acc = {}
    for r in runs:
        for key, setnames in (("val_path", ["val"]), ("rf_path", ["F51", "H36"])):
            if not r[key]:
                continue
            d = json.load(open(T / r[key])); g = d["grid"]; i = min(range(len(g)), key=lambda k: abs(g[k] - r["b_rel"][0]))
            for sn in setnames:
                st = [s for s in d["cells"] if sn == "val" or RFSET.get(s) == sn]
                C = d["cells"]; ngt = sum(C[s]["n_gt"] for s in st)
                pred = sum(C[s]["pred"][i] for s in st); rp = sum(C[s]["relp_tp"][i] for s in st); rr = sum(C[s]["relr_tp"][i] for s in st)
                fa = sum(C[s]["pred"][i] for s in st if C[s]["n_gt"] == 0)
                P0 = rp / pred if pred else float("nan"); P1 = rp / (pred - fa) if pred - fa else float("nan"); R = rr / ngt
                f = lambda P: 2 * P * R / (P + R) if (P + R) else 0.0
                acc.setdefault(sn, []).append((P0, P1, f(P0), f(P1), fa, pred))
    for sn, v in acc.items():
        m = lambda j: sum(x[j] for x in v) / len(v)
        out.append(f"{arm:42s} [{sn}] at val b_rel: relP {m(0):.4f} -> oracle gate {m(1):.4f} (d {m(1)-m(0):+.4f}); relF1 {m(2):.4f} -> {m(3):.4f} (d {m(3)-m(2):+.4f}); FA px {m(4):.1f} of pred {m(5):.0f} ({100*m(4)/m(5):.1f}%)")
open(T / "ideas/arch_out/a6_gate_oracle.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
