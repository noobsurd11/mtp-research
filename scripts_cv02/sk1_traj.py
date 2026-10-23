"""SK1 diagnostics (CPU only): per-arm trajectories over training of confident share, confident background /
padding / crack / inactive share of unlabelled px (pseudo_labels.csv, 500-step windows) and of the mechanism-log
fields (stdout, averaged over the 50-step lines inside each 2,000-step block). Mean over 5 seeds, min-max in brackets."""
import csv, glob, re
import numpy as np
STEPS = [2500, 3000, 4000, 6000, 8000, 10000, 12000, 14000, 16000, 18000, 20000]
ARMS = ["sk1_BsD", "sk1_BsDB", "sk1_BsDBn"]
print("## Confident pseudo-labels of the main (teacher) head, share of unlabelled px, 500-step window ending at step\n")
print("| arm | field | " + " | ".join(str(s) for s in STEPS) + " |\n|---|---|" + "---|" * len(STEPS))
for a in ARMS:
    runs = sorted(glob.glob(f"{a}_5pct_s[0-9]"))
    R = [{int(x["step"]): x for x in csv.DictReader(open(r + "/pseudo_labels.csv"))} for r in runs]
    for lab, f in (("confident", lambda x: float(x["confident_frac"])), ("bg", lambda x: float(x["unl_share_0"])),
                   ("padding", lambda x: float(x["unl_share_7"])), ("crack", lambda x: float(x["unl_share_14"])),
                   ("inactive", lambda x: float(x["unl_share_11"]))):
        cells = []
        for s in STEPS:
            v = np.array([f(r[s]) for r in R if s in r])
            cells.append(f"{v.mean():.4f} [{v.min():.4f}–{v.max():.4f}]" if len(v) else "-")
        print(f"| {a} | {lab} | " + " | ".join(cells) + " |")
K = ["conf_frac", "aux_keep_l", "aux_keep_u", "aux_pl_crack", "aux_pl_inactive", "head_drift", "main_pred_crack",
     "aux_pred_crack", "gt_crack", "main_pred_inactive", "aux_pred_inactive", "gt_inactive", "loss_sup", "loss_con", "loss_aux_sup", "loss_aux_con"]
B = [(0, 2000), (2000, 4000), (4000, 6000), (6000, 10000), (10000, 14000), (14000, 18000), (18000, 20000)]
print("\n## Mechanism log (stdout 50-step lines), mean over the block and over 5 seeds\n")
for a in ARMS + ["sk1_AB"]:
    runs = sorted(glob.glob(f"{a}_5pct_s[0-9]"))
    L = []
    for r in runs:
        d = {}
        for ln in open(r + ".stdout"):
            m = re.search(r"step (\d+)/20000\s+(.*)", ln)
            if m:
                d[int(m.group(1))] = {k: float(v) for k, v in (kv.split("=", 1) for kv in m.group(2).split() if "=" in kv)}
        L.append(d)
    keys = [k for k in K if k in L[0][20000]]
    print(f"### {a}\n\n| field | " + " | ".join(f"{lo}-{hi}" for lo, hi in B) + " |\n|---|" + "---|" * len(B))
    for k in keys:
        row = []
        for lo, hi in B:
            v = [np.mean([d[s][k] for s in d if lo < s <= hi]) for d in L]
            row.append(f"{np.mean(v):.4g}")
        print(f"| {k} | " + " | ".join(row) + " |")
    print()
