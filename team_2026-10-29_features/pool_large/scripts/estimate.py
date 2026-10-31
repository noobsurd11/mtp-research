"""Summaries and extrapolation from the random sample (targeted rows reported separately).

Rates: Wilson 95% CI on the random rows (2 per shard, stratified; Wilson ignores the stratification, which is
conservative when strata differ), extrapolated to N = 159,332.
Usage: python -I estimate.py <out_dir>   (reads targets.tsv, sample_profile.tsv, sample_matches.tsv, ref_stats.tsv,
manifest_profile.json, gaint_raw_ls.txt, sample_log.jsonl[.walked]; writes estimates.json and prints a summary)
"""
import collections
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

out = Path(sys.argv[1])
N = 159332
tg = {int(r["global_row"]): r for r in csv.DictReader(open(out / "targets.tsv"), delimiter="\t")}
prof = {int(r["global_row"]): r for r in csv.DictReader(open(out / "sample_profile.tsv"), delimiter="\t")}
mat = {int(r["global_row"]): r for r in csv.DictReader(open(out / "sample_matches.tsv"), delimiter="\t")}
log = [json.loads(x) for x in open(out / "sample_log.jsonl") if x.strip()]
refs = json.load(open(out / "refs.json"))
rnd = [g for g in prof if tg[g]["part"] == "random"]
tgt = [g for g in prof if tg[g]["part"] == "targeted"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def rate(pred, rows=None):
    rows = rnd if rows is None else rows
    k = sum(1 for g in rows if pred(g))
    p, lo, hi = wilson(k, len(rows))
    return dict(k=k, n=len(rows), p=round(p, 4), ci=[round(lo, 4), round(hi, 4)],
                N_est=round(p * N), N_ci=[round(lo * N), round(hi * N)])


def f(g, k):
    v = prof[g].get(k, "")
    return float(v) if v not in ("", None) else float("nan")


E = {}
E["fetch"] = dict(attempted=len(log), ok=sum(r.get("ok", False) for r in log),
                  failed=[(r["global_row"], r.get("err")) for r in log if not r.get("ok")][:20],
                  random_ok=len(rnd), targeted_ok=len(tgt))
E["decode_fail"] = rate(lambda g: prof[g]["decode_ok"] != "1")
E["size"] = {s: rate(lambda g, s=s: f"{prof[g]['w']}x{prof[g]['h']}" == s)
             for s in sorted({f"{prof[g]['w']}x{prof[g]['h']}" for g in rnd})}
E["mode"] = {m: rate(lambda g, m=m: prof[g]["mode"] == m) for m in sorted({prof[g]["mode"] for g in rnd})}
E["bit_depth_colour_type"] = {b: rate(lambda g, b=b: f"{prof[g]['bit_depth']}/{prof[g]['colour_type']}" == b)
                              for b in sorted({f"{prof[g]['bit_depth']}/{prof[g]['colour_type']}" for g in rnd})}
E["chan_diff_gt16_share_gt_1pct"] = rate(lambda g: f(g, "chan_diff_gt16") > 0.01)
E["chan_maxdiff_median"] = float(np.nanmedian([f(g, "chan_maxdiff") for g in rnd]))
E["near_blank_sd_lt_5"] = rate(lambda g: f(g, "sd") < 5)
E["near_blank_sd_lt_10"] = rate(lambda g: f(g, "sd") < 10)
E["dark_mean_lt_40"] = rate(lambda g: f(g, "mean") < 40)
E["saturated_share255_gt_0.3"] = rate(lambda g: f(g, "share255") > 0.3)
E["border_dark_gt_0.5"] = rate(lambda g: f(g, "border_dark") > 0.5)
# size by folder
by = collections.defaultdict(collections.Counter)
for g in rnd:
    by[prof[g]["label"]][f"{prof[g]['w']}"] += 1
E["native_width_by_folder"] = {k: dict(v) for k, v in by.items()}
# intensity stats (512 L) by folder vs labelled sources
keys = ["mean", "sd", "p1", "lap", "border_dark"]


def med(vals):
    v = [x for x in vals if not math.isnan(x)]
    return [round(float(np.percentile(v, q)), 2) for q in (25, 50, 75)] if v else None


st = {}
for lab in sorted({prof[g]["label"] for g in rnd}):
    for w in ("1200", "512"):
        gs = [g for g in rnd if prof[g]["label"] == lab and prof[g]["w"] == w]
        if gs:
            st[f"{lab} {w}px (n={len(gs)})"] = {k: med([f(g, k) for g in gs]) for k in keys}
for src in ("ARTS", "CSIR"):
    for w in ("1200", "512"):
        gs = [g for g in rnd if prof[g]["stem"].startswith(src) and prof[g]["w"] == w]
        if gs:
            st[f"HF {src} {w}px (n={len(gs)})"] = {k: med([f(g, k) for g in gs]) for k in keys}
ref = list(csv.DictReader(open(out / "ref_stats.tsv"), delimiter="\t"))
for setn in ("train", "val", "test", "e1"):
    for src in ("ARTS", "CSIR", "BMRK", "CFVS", "SDLE"):
        rs = [r for r in ref if r["set"] == setn and r["source"] == src]
        if rs and (setn != "val" and setn != "test"):
            st[f"ours {setn} {src} (n={len(rs)})"] = {k: med([float(r[k]) for r in rs]) for k in keys}
E["intensity_quartiles"] = st
# overlap (random rows)
SETS = ["train", "val", "test", "e1", "rf17", "ext117_inpool", "rf_inpool"]
ov = {}
for k in SETS:
    for thr in (0.95, 0.98):
        ov[f"{k}>={thr}"] = rate(lambda g, k=k, thr=thr: float(mat[g][f"{k}_best_r"]) >= thr)
ov["any_labelled>=0.95"] = rate(lambda g: max(float(mat[g][f"{k}_best_r"]) for k in ("train", "val", "test")) >= 0.95)
ov["any_heldout(val,test,e1,rf17)>=0.95"] = rate(
    lambda g: max(float(mat[g][f"{k}_best_r"]) for k in ("val", "test", "e1", "rf17")) >= 0.95)
ov["exact_512L_md5_any_ref"] = rate(lambda g: mat[g]["exact_512"] != "")
ov["best_r_quantiles_by_set"] = {k: [round(float(np.percentile([float(mat[g][f"{k}_best_r"]) for g in rnd], q)), 4)
                                     for q in (50, 90, 99, 100)] for k in SETS}
E["overlap_random"] = ov
E["overlap_random_rows_ge_0.95"] = sorted(
    [(g, prof[g]["stem"], k, mat[g][f"{k}_best_stem"], float(mat[g][f"{k}_best_r"])) for g in rnd for k in SETS
     if float(mat[g][f"{k}_best_r"]) >= 0.95], key=lambda x: -x[4])
# in-pool share of random rows by ID
pool = set(refs["pool11938"])
E["random_rows_in_pool11938_by_id"] = rate(lambda g: prof[g]["stem"] in pool)
# targeted: same-ID r
E["targeted"] = [dict(global_row=g, set=tg[g]["set"], stem=prof[g]["stem"], label=prof[g]["label"],
                      w=prof[g]["w"], same_id=mat.get(g, {}).get("same_id", ""), best=mat.get(g, {}).get("best_stem", ""),
                      best_set=mat.get(g, {}).get("best_set", ""), best_r=mat.get(g, {}).get("r_hp", ""),
                      exact_512=mat.get(g, {}).get("exact_512", ""), md5_png=prof[g]["md5_png"],
                      md5_512L=prof[g].get("md5_512L", "")) for g in sorted(tgt)]
# byte-length agreement with our gaint raw download (same file => same length)
gs = {}
for line in open(out / "gaint_raw_ls.txt"):
    p = line.split()
    if len(p) >= 7 and p[-1].endswith(".png"):
        gs[p[-1].split("__")[-1][:-4]] = (int(p[4]), p[-1])
man = {}
for r in csv.DictReader(open(out / "manifest.tsv"), delimiter="\t"):
    man[int(r["global_row"])] = r
walked = {}
wp = out / "sample_log.jsonl.walked"
if wp.exists():
    for x in open(wp):
        if x.strip():
            w = json.loads(x)
            walked[w["global_row"]] = w["png_len"]
for g in prof:
    walked[g] = int(prof[g]["png_bytes"])
cmp_ = [(g, walked[g], gs[Path(man[g]["file_path"]).stem][0]) for g in walked
        if Path(man[g]["file_path"]).stem in gs]
E["bytes_vs_gaint_raw"] = dict(rows_compared=len(cmp_), equal=sum(a == b for _, a, b in cmp_),
                               unequal_examples=[x for x in cmp_ if x[1] != x[2]][:10], walked_rows=len(walked))
json.dump(E, open(out / "estimates.json", "w"), indent=1)
print(json.dumps({k: v for k, v in E.items() if k not in ("overlap_random_rows_ge_0.95",)}, indent=1)[:12000])
print("rows >=0.95:", E["overlap_random_rows_ge_0.95"][:30])
