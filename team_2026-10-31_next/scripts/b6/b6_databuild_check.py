"""B6 per-root CPU data-build check at e544133 (protocol_B6 v1.0.1 s3 'Asserts per run', s8.2). CPU only, no training.

For each fold root and each arm (house = pf2_SUP_100pct_s5 opts, PF = pf2_SUPPF_100pct_s5 opts, from pf2_jobs.txt, plus
data.root=<root>), with --code's own scripts/train.py functions (apply_opts, build_benchmark_data) and loss factory:
  - the exact 'Labelled: ...' line train.py logs (captured from logger 'train' inside build_benchmark_data);
  - the exact 'CE class weights: ...' and 'Zero-pixel classes ...' lines (format strings of train.py main l.277-281,
    applied to build_losses on the fold list's class counts, as main does);
  - the class pixel counts of the labelled (4-fold) list, checked against b6_folds.tsv: inactive / crack px of the
    train list = pool total - fold k's;
  - the config diff vs the PF2 run's config_used.yaml of the same arm (expected: data.root and run_name only).
Control: the same harness on the real root (data.root=data) must print the PF2 train.log lines exactly.
Writes <out>/databuild.json and <out>/databuild.txt (the per-run assert table for runner).

Usage: python b6_databuild_check.py --code <el_f3> --roots /home/noob/work/b6 --folds b6_folds.tsv --out <dir>
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import os
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--roots", required=True)
ap.add_argument("--folds", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--threads", type=int, default=2)
a = ap.parse_args()
ROOT = Path(a.code).resolve()
OUT = Path(a.out).resolve()
ROOTS = Path(a.roots).resolve()
FOLDS = Path(a.folds).resolve()
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

import torch  # noqa: E402
import yaml  # noqa: E402

torch.set_num_threads(a.threads)
spec = importlib.util.spec_from_file_location("train_under_test", ROOT / "scripts" / "train.py")
train = importlib.util.module_from_spec(spec); spec.loader.exec_module(train)
from src.losses.loss_factory import build_losses  # noqa: E402
from src.utils.config import load_config  # noqa: E402

FOLDS_MD5 = "e2cafce1509bb0f2b95ce6d5db397caf"
JOBS = ROOT / "reports" / "pf2" / "pf2_jobs.txt"
ARMS = {"house": "pf2_SUP_100pct_s5", "PF": "pf2_SUPPF_100pct_s5"}
NC, CRACK, INACT = 24, 14, 11
PF2_LINES = {  # E: el_f3 experiments/pf2_{SUP,SUPPF}_100pct_s5/train.log (grep of these three lines only)
    "labelled": "Labelled: 478 (data/splits/train.txt)  unlabelled: 0 (-)  val: 54  test: 50",
    "ce": "CE class weights: none (plain CE)",
    "zero": "Zero-pixel classes in labelled subset (weight 0): none"}


class Grab(logging.Handler):
    def __init__(self):
        super().__init__(logging.INFO); self.msgs = []

    def emit(self, r):
        self.msgs.append(r.getMessage())


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def flat(d, pre=""):
    o = {}
    for k, v in d.items():
        if isinstance(v, dict):
            o.update(flat(v, f"{pre}{k}."))
        else:
            o[f"{pre}{k}"] = v
    return o


def build(opts: list[str]) -> dict:
    cfg = train.apply_opts(load_config("configs/supervised.yaml"), opts)
    seed, frac = int(cfg["seed"]), float(cfg["data"]["labeled_fraction"])
    lg = logging.getLogger("train"); h = Grab(); lg.addHandler(h); lg.setLevel(logging.INFO)
    try:
        data = train.build_benchmark_data(cfg, cfg.get("method", "supervised"), seed, frac, False, torch.device("cpu"), 0)
    finally:
        lg.removeHandler(h)
    lab = [m for m in h.msgs if m.startswith("Labelled:")]
    assert len(lab) == 1, h.msgs
    # train.py main l.274-281 (e544133), format strings copied verbatim
    class_counts = data.pop("class_counts")
    losses = build_losses(cfg["loss"], class_counts)
    w = losses["supervised"].criterion.weight
    weights = w.tolist() if w is not None else None
    ce = "CE class weights: %s" % ([round(x, 3) for x in weights] if weights else "none (plain CE)")
    zero = None
    if data["info"].get("zero_pixel_classes") is not None:
        zero = "Zero-pixel classes in labelled subset (weight 0): %s" % (data["info"]["zero_pixel_classes"] or "none")
    return {"cfg": cfg, "labelled": lab[0], "ce": ce, "zero": zero, "counts": [int(c) for c in class_counts],
            "loss_class": type(losses["supervised"]).__name__, "n_labeled": data["info"]["n_labeled"],
            "n_val": len(data["val_loader"].dataset), "n_test": len(data["test_loader"].dataset)}


def main() -> None:
    assert md5(FOLDS) == FOLDS_MD5, "folds md5"
    rows = [l.rstrip("\n").split("\t") for l in open(FOLDS) if l.strip()]
    hdr, rows = rows[0], [dict(zip(rows[0], r)) for r in rows[1:]]
    tot_in = sum(int(r["inactive_px"]) for r in rows); tot_cr = sum(int(r["crack_px"]) for r in rows)
    jobs = {l.split("|")[0]: l.rstrip("\n").split("|")[3].split() for l in open(JOBS) if l.strip()}
    res = {"code": str(ROOT), "jobs_md5": md5(JOBS), "folds_md5": FOLDS_MD5, "control": {}, "roots": {}}
    # control: real root, both arms, must reproduce the PF2 train.log lines
    for arm, run in ARMS.items():
        b = build(jobs[run])
        for k in ("labelled", "ce", "zero"):
            assert b[k] == PF2_LINES[k], (arm, k, b[k])
        ref = flat(load_config(ROOT / "experiments" / run / "config_used.yaml"))
        got = flat(b["cfg"])
        assert got == ref, sorted(set(got.items()) ^ set(ref.items()))
        res["control"][arm] = {k: b[k] for k in ("labelled", "ce", "zero", "loss_class")}
    lines = []
    for k in range(5):
        r = ROOTS / f"b6_root_{k}"
        held = [x["stem"] for x in rows if int(x["fold"]) == k]
        exp_in = tot_in - sum(int(x["inactive_px"]) for x in rows if int(x["fold"]) == k)
        exp_cr = tot_cr - sum(int(x["crack_px"]) for x in rows if int(x["fold"]) == k)
        out = {}
        for arm, run in ARMS.items():
            opts = jobs[run] + [f"data.root={r}"]
            b = build(opts)
            ref = flat(load_config(ROOT / "experiments" / run / "config_used.yaml"))
            got = flat(b["cfg"])
            diff = sorted(x for x in set(ref) | set(got) if ref.get(x) != got.get(x))
            assert diff == ["data.root"], diff  # run_name stays the PF2 one here: only data.root differs
            n_tr = 532 - len(held)
            assert b["labelled"] == (f"Labelled: {n_tr} ({r}/splits/train.txt)  unlabelled: 0 (-)  "
                                     f"val: {len(held)}  test: {len(held)}"), b["labelled"]
            assert (b["n_labeled"], b["n_val"], b["n_test"]) == (n_tr, len(held), len(held))
            assert b["counts"][INACT] == exp_in and b["counts"][CRACK] == exp_cr, (k, b["counts"][INACT], exp_in)
            out[arm] = {x: b[x] for x in ("labelled", "ce", "zero", "counts", "loss_class")}
        assert {x: out["house"][x] for x in out["house"]} == out["PF"], "arms differ in data build"
        res["roots"][k] = {"root": str(r), "n_train": 532 - len(held), "n_heldout": len(held), **out["PF"],
                           "counts_sha": hashlib.sha256(str(out["PF"]["counts"]).encode()).hexdigest()[:16],
                           "config_diff_vs_pf2_s5": ["data.root"]}
        lines.append(f"fold {k}\t{out['PF']['labelled']}\t{out['PF']['ce']}\t{out['PF']['zero']}\t"
                     f"inactive px {out['PF']['counts'][INACT]}\tcrack px {out['PF']['counts'][CRACK]}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "databuild.json").write_text(json.dumps(res, indent=1))
    txt = ("control (data.root=data): " + " | ".join(res["control"]["PF"][x] for x in ("labelled", "ce", "zero")) +
           " = PF2 train.log; config = pf2 s5 config_used.yaml exactly, both arms\n" + "\n".join(lines) + "\n")
    (OUT / "databuild.txt").write_text(txt)
    print(txt, end="")
    print("class counts per fold (24 classes, labelled 4-fold list):")
    for k in range(5):
        print(k, res["roots"][k]["counts"])


if __name__ == "__main__":
    main()
