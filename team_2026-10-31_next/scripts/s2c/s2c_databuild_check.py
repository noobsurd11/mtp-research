"""SKR2C data-root CPU data-build check (runner, 3 Nov 2026), adapted from b6_databuild_check.py 061a3964. CPU only, no training.

One arm per call (one code root per process): SUPPF = el_f3 e544133 with the pf2_SUPPF_100pct_s5 opts (pf2_jobs.txt), SKR01 =
el_thin c9bbb02 with the skr2_SKR01_100pct_s5 opts (s2q_jobs.txt). With --code's own scripts/train.py functions (apply_opts,
build_benchmark_data) and loss factory:
  - control (opts as run, data.root=data): the 'Labelled:' / 'CE class weights:' / 'Zero-pixel classes' lines must equal the
    run's own train.log lines, the flat config must equal its config_used.yaml, and yaml.safe_dump(cfg, sort_keys=False) (train.py's
    own writer) must equal the config_used.yaml file byte for byte;
  - root (opts + data.root=<root>): 'Labelled: 478 (<root>/splits/train.txt)  unlabelled: 0 (-)  val: 54  test: 54'; CE / zero lines
    = control's; labelled class counts = control's; val and test datasets hold the same stems in the same order = the real val list;
    flat config diff vs control = ['data.root'] only.
Writes <out>/<arm>_databuild.json and <out>/<arm>_root_config.yaml (the config this arm's runs will write, seed 5 / s5 run_name).
Usage: python s2c_databuild_check.py --arm SUPPF|SKR01 --root /home/noob/work/s2c_root --out <dir>
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import logging
import os
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--arm", required=True, choices=["SUPPF", "SKR01"])
ap.add_argument("--root", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--threads", type=int, default=2)
a = ap.parse_args()
W = "/home/noob/work"
ARM = {"SUPPF": (f"{W}/el_f3", f"{W}/el_f3/reports/pf2/pf2_jobs.txt", "210d0d6fcc54c3effcc36893e0d51ad5", "pf2_SUPPF_100pct_s5"),
       "SKR01": (f"{W}/el_thin", f"{W}/s2q/s2q_jobs.txt", "d6efb9af81e5bc98101cbf674c20d5f2", "skr2_SKR01_100pct_s5")}[a.arm]
ROOT = Path(ARM[0]); JOBS = Path(ARM[1]); RUN = ARM[3]; DR = str(Path(a.root).resolve()); OUT = Path(a.out).resolve()
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

import torch  # noqa: E402
import yaml  # noqa: E402

torch.set_num_threads(a.threads)
spec = importlib.util.spec_from_file_location("train_under_test", ROOT / "scripts" / "train.py")
train = importlib.util.module_from_spec(spec); spec.loader.exec_module(train)
from src.losses.loss_factory import build_losses  # noqa: E402
from src.utils.config import load_config  # noqa: E402


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
    method = cfg.get("method", "supervised")
    train.__dict__.get("check_thin_b3", lambda c, m: None)(cfg, method)  # thin worktree only (as identity_cpu.py)
    lg = logging.getLogger("train"); h = Grab(); lg.addHandler(h); lg.setLevel(logging.INFO)
    try:
        data = train.build_benchmark_data(cfg, method, seed, frac, False, torch.device("cpu"), 0)
    finally:
        lg.removeHandler(h)
    lab = [m for m in h.msgs if m.startswith("Labelled:")]
    assert len(lab) == 1, h.msgs
    class_counts = data.pop("class_counts")
    losses = build_losses(cfg["loss"], class_counts)
    crit = getattr(losses["supervised"], "criterion", None)
    w = getattr(crit, "weight", None) if crit is not None else None
    weights = w.tolist() if w is not None else None
    ce = "CE class weights: %s" % ([round(x, 3) for x in weights] if weights else "none (plain CE)")
    zero = None
    if data["info"].get("zero_pixel_classes") is not None:
        zero = "Zero-pixel classes in labelled subset (weight 0): %s" % (data["info"]["zero_pixel_classes"] or "none")
    s = io.StringIO(); yaml.safe_dump(cfg, s, sort_keys=False)
    return {"cfg": cfg, "yaml": s.getvalue(), "labelled": lab[0], "ce": ce, "zero": zero,
            "counts": [int(c) for c in class_counts], "loss_class": type(losses["supervised"]).__name__,
            "n_labeled": data["info"]["n_labeled"], "val_stems": list(data["val_loader"].dataset.stems),
            "test_stems": list(data["test_loader"].dataset.stems)}


def main() -> None:
    assert md5(JOBS) == ARM[2], "jobs md5"
    opts = [l.rstrip("\n").split("|")[3].split() for l in open(JOBS) if l.startswith(RUN + "|")]
    assert len(opts) == 1; opts = opts[0]
    run_dir = ROOT / "experiments" / RUN
    want = {}
    for l in (run_dir / "train.log").read_text().splitlines():
        for k, pre in (("labelled", "Labelled:"), ("ce", "CE class weights:"), ("zero", "Zero-pixel classes")):
            if " — " + pre in l and k not in want:
                want[k] = l.split(" — ", 1)[1]
    real_val = Path("data/splits/val.txt").read_text().split()
    c = build(opts)
    for k in ("labelled", "ce", "zero"):
        assert c[k] == want[k], (k, c[k], want[k])
    ref_txt = (run_dir / "config_used.yaml").read_text()
    assert flat(c["cfg"]) == flat(load_config(run_dir / "config_used.yaml")), "control flat config"
    assert c["yaml"] == ref_txt, "control yaml text differs from config_used.yaml"
    assert c["val_stems"] == real_val
    r = build(opts + [f"data.root={DR}"])
    exp_lab = f"Labelled: 478 ({DR}/splits/train.txt)  unlabelled: 0 (-)  val: 54  test: 54"
    assert r["labelled"] == exp_lab, r["labelled"]
    assert (r["ce"], r["zero"], r["counts"], r["n_labeled"]) == (c["ce"], c["zero"], c["counts"], c["n_labeled"])
    assert r["val_stems"] == real_val and r["test_stems"] == real_val, "root val / test stems"
    fc, fr = flat(c["cfg"]), flat(r["cfg"])
    diff = sorted(x for x in set(fc) | set(fr) if fc.get(x) != fr.get(x))
    assert diff == ["data.root"], diff
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{a.arm}_root_config.yaml").write_text(r["yaml"])
    res = {"arm": a.arm, "code": str(ROOT), "run": RUN, "jobs_md5": ARM[2], "root": DR,
           "control": {k: c[k] for k in ("labelled", "ce", "zero", "loss_class")}, "control_yaml_md5": hashlib.md5(c["yaml"].encode()).hexdigest(),
           "root_lines": {k: r[k] for k in ("labelled", "ce", "zero", "loss_class")}, "root_yaml_md5": hashlib.md5(r["yaml"].encode()).hexdigest(),
           "counts_sha": hashlib.sha256(str(r["counts"]).encode()).hexdigest()[:16], "n_val": len(r["val_stems"]),
           "n_test": len(r["test_stems"]), "test_eq_val": r["test_stems"] == r["val_stems"], "config_diff_vs_control": diff}
    (OUT / f"{a.arm}_databuild.json").write_text(json.dumps(res, indent=1))
    print(f"{a.arm} PASS: control = {RUN} train.log lines + config_used.yaml (text identical); root: {r['labelled']} | {r['ce']} | "
          f"{r['zero']}; counts = control ({res['counts_sha']}); test stems = val stems ({len(r['test_stems'])}); config diff = data.root only")


if __name__ == "__main__":
    main()
