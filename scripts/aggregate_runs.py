"""Aggregate re-score JSONs (scripts_gaint/rescore_label_versions.py output) into per-arm tables and a ladder figure.

Usage: python aggregate_runs.py <dir with p6_*.json / p7_*.json> <out_prefix> [--arms L0_10pct L1_10pct ...]
Run names are <prefix>_<arm>_s<seed>; the arm key is everything between the experiment prefix and _s<seed>.
"""
from __future__ import annotations

import argparse, glob, json, os, re
from collections import defaultdict

import numpy as np


def load(dir_):
    rows = defaultdict(dict)  # arm -> seed -> {split/label/class/metric: value}
    for f in sorted(glob.glob(os.path.join(dir_, "*.json"))):
        d = json.load(open(f))
        for key, v in d.items():
            split, run = key.split("/", 1)
            m = re.match(r"^(p\d+)_(.+)_s(\d+)$", run)
            if not m:
                continue
            arm, seed = m.group(2), int(m.group(3))
            for lab in ("new_escdd", "old_20211104"):
                for cls, mets in v[lab].items():
                    for k, x in mets.items():
                        rows[arm].setdefault(seed, {})[f"{split}/{lab}/{cls}/{k}"] = x
    return rows


def stat(rows, arm, key):
    xs = [s[key] for s in rows[arm].values() if key in s]
    if not xs:
        return float("nan"), float("nan"), 0
    return float(np.mean(xs)), float(np.std(xs, ddof=1)) if len(xs) > 1 else 0.0, len(xs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir"); ap.add_argument("out")
    ap.add_argument("--arms", nargs="*")
    a = ap.parse_args()
    rows = load(a.dir)
    arms = a.arms or sorted(rows)
    keys = [("test", "new_escdd", "crack", "ap"), ("test", "new_escdd", "inactive", "ap"),
            ("test", "new_escdd", "crack", "iou"), ("test", "new_escdd", "inactive", "iou"),
            ("test", "new_escdd", "crack", "rel_f1_2"), ("test", "new_escdd", "crack", "rel_p2"),
            ("val", "new_escdd", "crack", "ap"), ("val", "new_escdd", "inactive", "ap"),
            ("test", "old_20211104", "crack", "ap"), ("test", "old_20211104", "crack", "iou")]
    hdr = "| arm | n | " + " | ".join(f"{s} {c} {m} ({'rev' if l == 'new_escdd' else 'old'})" for s, l, c, m in keys) + " |"
    lines = [hdr, "|" + "---|" * (len(keys) + 2)]
    summary = {}
    for arm in arms:
        cells, n = [], 0
        for s, l, c, m in keys:
            mu, sd, n = stat(rows, arm, f"{s}/{l}/{c}/{m}")
            cells.append(f"{mu:.3f}±{sd:.3f}")
            summary.setdefault(arm, {})[f"{s}/{l}/{c}/{m}"] = (mu, sd, n)
        lines.append(f"| {arm} | {n} | " + " | ".join(cells) + " |")
    open(a.out + ".md", "w").write("\n".join(lines) + "\n")
    json.dump(summary, open(a.out + ".json", "w"), indent=1)
    print("\n".join(lines))
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
        for ax, cls in zip(axs, ("crack", "inactive")):
            for split, mk in (("test", "o"), ("val", "s")):
                mu = [summary[x][f"{split}/new_escdd/{cls}/ap"][0] for x in arms]
                sd = [summary[x][f"{split}/new_escdd/{cls}/ap"][1] for x in arms]
                ax.errorbar(range(len(arms)), mu, yerr=sd, marker=mk, capsize=3, label=split)
            ax.set_xticks(range(len(arms))); ax.set_xticklabels(arms, rotation=30, ha="right", fontsize=8)
            ax.set_title(f"{cls} pixel AP (revised labels), mean ± sd over seeds"); ax.grid(alpha=0.3); ax.legend()
        fig.tight_layout(); fig.savefig(a.out + ".png", dpi=150)
        print("wrote", a.out + ".png")
    except Exception as e:  # plotting is optional
        print("plot skipped:", e)


if __name__ == "__main__":
    main()
