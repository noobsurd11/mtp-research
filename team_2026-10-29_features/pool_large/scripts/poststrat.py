"""Folder post-stratified rates for the random sample (folder sizes known exactly from the manifest).
Estimate = sum_F (N_F/N) p_F; 95% CI by stratified bootstrap (2,000 draws, resampling within folder).
Usage: python -I poststrat.py <out_dir>   (writes poststrat.json)
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

out = Path(sys.argv[1])
prof = json.load(open(out / "manifest_profile.json"))
NF = prof["labels"]
N = sum(NF.values())
tg = {r["global_row"]: r for r in csv.DictReader(open(out / "targets.tsv"), delimiter="\t")}
P = [r for r in csv.DictReader(open(out / "sample_profile.tsv"), delimiter="\t") if tg[r["global_row"]]["part"] == "random"]
M = {r["global_row"]: r for r in csv.DictReader(open(out / "sample_matches.tsv"), delimiter="\t")}
pool = set(json.load(open(out / "refs.json"))["pool11938"])
lab = lambda g: max(float(M[g][f"{k}_best_r"]) for k in ("train", "val", "test"))  # noqa: E731
held = lambda g: max(float(M[g][f"{k}_best_r"]) for k in ("val", "test", "e1", "rf17"))  # noqa: E731
preds = {
    "native_1200px": lambda r: r["w"] == "1200",
    "colour_chan_diff_gt16_over_1pct": lambda r: float(r["chan_diff_gt16"]) > 0.01,
    "low_contrast_sd_lt_10": lambda r: float(r["sd"]) < 10,
    "near_blank_sd_lt_5": lambda r: float(r["sd"]) < 5,
    "white_pad_share255_gt_0.3": lambda r: float(r["share255"]) > 0.3,
    "in_pool11938_by_id": lambda r: r["stem"] in pool,
    "r_hp_ge_0.95_any_labelled": lambda r: lab(r["global_row"]) >= 0.95,
    "r_hp_ge_0.98_any_labelled": lambda r: lab(r["global_row"]) >= 0.98,
    "r_hp_ge_0.95_val_test_e1_rf17": lambda r: held(r["global_row"]) >= 0.95,
    "exact_512L_md5_any_ref": lambda r: M[r["global_row"]]["exact_512"] != "",
}
by = {}
for r in P:
    by.setdefault(r["label"], []).append(r)
rng = np.random.default_rng(0)
res = {"n_by_folder": {k: len(v) for k, v in by.items()}, "N_by_folder": NF}
for name, f in preds.items():
    x = {k: np.array([1.0 if f(r) else 0.0 for r in v]) for k, v in by.items()}
    est = sum(NF[k] / N * x[k].mean() for k in x)
    boots = []
    for _ in range(2000):
        boots.append(sum(NF[k] / N * rng.choice(x[k], len(x[k])).mean() for k in x))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    res[name] = dict(p=round(est, 4), ci=[round(lo, 4), round(hi, 4)], N_est=round(est * N),
                     N_ci=[round(lo * N), round(hi * N)], k=int(sum(v.sum() for v in x.values())), n=len(P))
json.dump(res, open(out / "poststrat.json", "w"), indent=1)
for k, v in res.items():
    print(k, v)
