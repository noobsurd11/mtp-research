"""SK1 prior-shift control (protocol_v2 §8 item 6, descriptive): BsD5+LA(τ=1) and A5c+LA(τ=1) next to the ABSH arms.
Inputs: results/sk1/la_test.json (rescore_logit_adjust.py), re-score JSONs, results/sk1/hist_revised.npz (bin-0 share).
Usage: .venv/bin/python scripts/sk1_la_compare.py | tee results/sk1/sk1_la.md
"""
import glob, json, os
import numpy as np

LA = json.load(open("results/sk1/la_test.json"))
LAV = json.load(open("results/sk1/la_val.json"))
RS = {}
for d in ("results/p12/raw", "results/p13/raw", "results/sk1/raw"):
    for f in glob.glob(os.path.join(d, "*_s[0-9].json")):
        for k, v in json.load(open(f)).items():
            if k.startswith("test/"):
                RS[k[5:]] = v["new_escdd"]
H = {k: v for f in ("results/sk1/hist_revised.npz", "results/p12/hist_revised.npz", "results/p13/hist_revised.npz") for k, v in np.load(f).items()}
A5 = ["p12_A_5pct_s0", "p12_A_5pct_s1", "p12_A_5pct_s2", "p13_A_5pct_s3", "p13_A_5pct_s4"]
arm = lambda p: [f"sk1_{p}_5pct_s{i}" for i in range(5)]
M = [("crack", "iou"), ("inactive", "iou"), ("crack", "rel_f1_2"), ("crack", "precision"), ("crack", "recall"),
     ("crack", "ap"), ("crack", "bin0_share"), ("inactive", "ap"), ("inactive", "bin0_share")]


def bin0(run, cls):
    a = H[f"test/{run}"]  # (2 classes [crack, inactive], pos/neg, bins)
    j = 0 if cls == "crack" else 1
    return a[j, 0, 0] / a[j, 0].sum()


def plain(runs):
    return np.array([[RS[r][c][m] if m != "bin0_share" else bin0(r, c) for c, m in M] for r in runs])


def la(runs, tau=1, split="test", src=LA):
    return np.array([[src[f"{split}/{r}/tau{tau:g}"]["new_escdd"][c][m] for c, m in M] for r in runs])


print("Absent-class predicted share at tau 1 (test), max over runs: %.5f (masked variant not needed below 0.001)" %
      max(v["absent_pred_share"] for k, v in LA.items() if k.endswith("tau1")))
print("tau 0 check vs re-score JSONs, max |diff|: %.1e" % max(v.get("check_max_abs_diff", 0) for v in LA.values()))
ROWS = {"A5c": plain(A5), "A5c+LA τ=1": la(A5), "AB5": plain(arm("AB")),
        "BsD5": plain(arm("BsD")), "BsD5+LA τ=1": la(arm("BsD")), "BsDB5": plain(arm("BsDB")), "BsDBn5": plain(arm("BsDBn"))}
hdr = ["crack IoU", "inactive IoU", "crack relF1@2", "crack P", "crack R", "crack AP", "crack bin-0", "inactive AP", "inactive bin-0"]
print("\n| arm (test, final step, 5 seeds) | " + " | ".join(hdr) + " |\n|---|" + "---|" * len(hdr))
for k, v in ROWS.items():
    print(f"| {k} | " + " | ".join(f"{v[:, j].mean():.3f}±{v[:, j].std(ddof=1):.3f}" for j in range(len(hdr))) + " |")
print("\nRule-1 arithmetic (descriptive): Δ (threshold) on crack IoU / inactive IoU / crack relF1@2")
for a, b in (("BsDB5", "BsD5+LA τ=1"), ("BsDBn5", "BsD5+LA τ=1"), ("AB5", "A5c+LA τ=1"), ("BsD5+LA τ=1", "BsD5"), ("A5c+LA τ=1", "A5c")):
    out = []
    for j in range(3):
        xa, xb = ROWS[a][:, j], ROWS[b][:, j]
        thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
        dl = xa.mean() - xb.mean()
        out.append(f"{dl:+.4f} ({thr:.4f}){' >' if dl > thr else ' <' if dl < -thr else ''}")
    print(f"- {a} − {b}: " + " / ".join(out))
print("\nVal τ grid (val only, descriptive; mean over 5 seeds of crack IoU / inactive IoU):")
for name, runs in (("BsD5", arm("BsD")), ("A5c", A5)):
    print(f"- {name}: " + ", ".join(f"τ={t:g} {la(runs, t, 'val', LAV)[:, 0].mean():.3f}/{la(runs, t, 'val', LAV)[:, 1].mean():.3f}"
                                    for t in (0, 0.25, 0.5, 0.75, 1, 1.5, 2)))
