"""P16 descriptive curve (cv02 only): supervised vs SSL (separate BN, tolerant PL, P16's CutMix setting) against label fraction.

Test, revised labels, final weights, mean ± sd over seeds. The 5% point is P13 (Cs5 if P16 runs CutMix off, CsM5 if on);
10% has no separate-BN SSL arm (P11 Cm is joint BN, a different recipe) so it is supervised only. 100% SSL uses the external
pool (the in-domain pool is empty). Usage: python scripts/p16_curve.py --out results/p16/fig_p16_curve.png
"""
import argparse, glob, json, os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--selection", default="results/p16/selection.txt")
a = ap.parse_args()

R = {}
for d in ("results/p6/raw", "results/p12/raw", "results/p13/raw", "results/p16/raw"):
    for f in glob.glob(os.path.join(d, "p*_s[0-9].json")):
        for key, v in json.load(open(f)).items():
            split, run = key.split("/", 1)
            m = re.match(r"^(p\d+_.+)_s(\d+)$", run)
            if split == "test" and m:
                R.setdefault(m.group(1), {})[int(m.group(2))] = v["new_escdd"]

cm = re.search(r"CUTMIX=(\S+)", open(a.selection).read()).group(1)
ssl5 = "p13_CsM_5pct" if cm == "0.5" else "p13_Cs_5pct"
SUP = {5: ["p12_A_5pct", "p13_A_5pct"], 10: ["p6_L3_10pct"], 20: ["p6_L3_20pct", "p16_A_20pct"], 50: ["p16_A_50pct"],
       100: ["p6_L3_100pct", "p16_A_100pct"]}
SSL = {5: [ssl5], 20: ["p16_S_20pct"], 50: ["p16_S_50pct"], 100: ["p16_Sx_100pct"]}
MET = [("crack", "iou", "crack IoU"), ("inactive", "iou", "inactive IoU"), ("crack", "rel_f1_2", "crack relF1@2")]


def vals(arms, c, m):
    v = [R[x][s][c][m] for x in arms if x in R for s in sorted(R[x])]
    return np.array(v)


print(f"P16 curve; CutMix {cm}; 5% SSL point = {ssl5}; test, revised labels, mean ± sd (n seeds)")
print("| labels | metric | supervised | SSL | Δ |")
print("|---|---|---|---|---|")
fig, axs = plt.subplots(1, 3, figsize=(13, 3.8))
for ax, (c, m, name) in zip(axs, MET):
    for lab, D, col, mk in (("supervised", SUP, "tab:green", "o"), ("SSL (sep. BN, tolerant PL)", SSL, "tab:red", "s")):
        fr = [f for f in sorted(D) if len(vals(D[f], c, m))]
        mu = [vals(D[f], c, m).mean() for f in fr]; sd = [vals(D[f], c, m).std(ddof=1) for f in fr]
        ax.errorbar(fr, mu, yerr=sd, color=col, marker=mk, capsize=3, label=lab)
        for f in fr:
            v = vals(D[f], c, m)
            ax.scatter([f] * len(v), v, color=col, s=8, alpha=0.5)
    ax.set_xscale("log"); ax.set_xticks([5, 10, 20, 50, 100]); ax.set_xticklabels(["5%", "10%", "20%", "50%", "100%\n(SSL: ext. pool)"])
    ax.set_title(name, fontsize=10); ax.grid(alpha=0.3)
    for f in sorted(SSL):
        s, b = vals(SUP[f], c, m), vals(SSL[f], c, m)
        if len(s) and len(b):
            print(f"| {f}% | {name} | {s.mean():.3f}±{s.std(ddof=1):.3f} ({len(s)}) | {b.mean():.3f}±{b.std(ddof=1):.3f} ({len(b)}) | {b.mean() - s.mean():+.3f} |")
axs[0].legend(fontsize=8)
fig.suptitle(f"P16: SSL vs supervised by label fraction (cv02, test, revised labels; CutMix {cm}; 5% = P13 {ssl5[4:]})", fontsize=10)
fig.tight_layout(); fig.savefig(a.out, dpi=160)
print("wrote", a.out)
