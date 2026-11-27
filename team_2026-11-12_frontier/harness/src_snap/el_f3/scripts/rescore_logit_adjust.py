"""SK1 prior-shift control (descriptive): re-score final checkpoints with logit adjustment z_c - tau * log(pi_c).

Read-only inference, same data path and conventions as rescore_label_versions.py (weak view, bf16, final
``latest.pth``, EMA teacher for Mean Teacher runs, revised masks ``data/escdd_masks/<split>``). pi_c is the class
pixel frequency in the run's own labelled cells (``data.labeled_fraction``, ``data.split_seed``, ``data.mask_subdir``),
the same counts the absh keep probabilities use. Classes with no labelled pixel get pi = the smallest non-zero pi
(fixed in SK1 protocol v2; otherwise log 0 would force them everywhere). tau = 1 is the pre-fixed value; other taus
are for a val-only grid. tau = 0 reproduces rescore_label_versions.py's new_escdd numbers (checked on every run).

Output per (split, run, tau): crack / inactive IoU, P, R, AP, relaxed scores, bin-0 share; plus per-cell
[crack tp, fp, fn, inactive tp, fp, fn] for the with/without-cell checks.

Usage: python scripts/rescore_logit_adjust.py --runs <run> ... --taus 0 1 [0.25 0.5 ...] --splits test val --out f.json
"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from rescore_label_versions import BINS, DATA, IMG, MSK, NEW, relaxed  # noqa: E402
from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.class_info import CRACK_CLASS, INACTIVE_CLASS  # noqa: E402
from src.data.class_stats import count_class_pixels  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.evaluation.threshold_free import binned_ap  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402


def log_prior(cfg: dict) -> tuple[torch.Tensor, torch.Tensor]:
    d = cfg["data"]
    frac, ss = float(d.get("labeled_fraction", 1.0)), int(d.get("split_seed", cfg.get("seed", 0)))
    tag = f"{round(frac * 100)}pct"
    f = DATA / "splits" / ("train.txt" if frac >= 1 else f"seed{ss}/labeled_{tag}.txt")
    if d.get("labeled_list"):  # Track D: explicit labelled list (data.labeled_list)
        f = Path(d["labeled_list"])
    counts = count_class_pixels(DATA / d.get("mask_subdir", "labeled/masks_coded"), load_split(f)).astype(np.float64)
    pi = counts / counts.sum()
    absent = torch.tensor(pi == 0)
    pi[pi == 0] = pi[pi > 0].min()
    return torch.tensor(np.log(pi), dtype=torch.float32), absent


def score(probs, preds, gts, c):
    tp = fp = fn = 0
    pos, neg = np.zeros(BINS, np.int64), np.zeros(BINS, np.int64)
    rel = {1: np.zeros(4, np.int64), 2: np.zeros(4, np.int64)}
    per = []
    for pr, pd, g in zip(probs, preds, gts):
        p, t = pd == c, g == c
        a, b_, e = int((p & t).sum()), int((p & ~t).sum()), int((~p & t).sum())
        tp += a; fp += b_; fn += e; per.append([a, b_, e])
        b = np.clip((pr * BINS).astype(int), 0, BINS - 1)
        pos += np.bincount(b[t], minlength=BINS); neg += np.bincount(b[~t], minlength=BINS)
        for r in rel: rel[r] += relaxed(p, t, r)
    out = {"iou": tp / max(tp + fp + fn, 1), "precision": tp / max(tp + fp, 1), "recall": tp / max(tp + fn, 1),
           "ap": float(binned_ap(pos, neg)), "gt_px": tp + fn, "bin0_share": pos[0] / max(pos.sum(), 1)}
    for r, v in rel.items():
        P, R = v[0] / max(v[1], 1), v[2] / max(v[3], 1)
        out[f"rel_f1_{r}"] = 2 * P * R / max(P + R, 1e-9); out[f"rel_p{r}"] = P; out[f"rel_r{r}"] = R
    return {k: float(v) for k, v in out.items()}, per


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--taus", nargs="+", type=float, default=[0.0, 1.0])
    ap.add_argument("--splits", nargs="+", default=["test", "val"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", default=None, help="dir of rescore_label_versions JSONs: tau 0 must match them")
    a = ap.parse_args()
    dev = torch.device("cuda")
    res = {}
    for split in a.splits:
        stems = sorted(load_split(DATA / "splits" / f"{split}.txt"))
        stems = [s for s in stems if (NEW / split / f"{s}.png").exists()]
        gts = [np.array(Image.open(NEW / split / f"{s}.png")) for s in stems]
        for run in a.runs:
            cfg = load_config(ROOT / "experiments" / run / "config_used.yaml")
            d = cfg["data"]
            ds = BenchmarkELDataset(IMG, MSK, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
            dl = DataLoader(ds, batch_size=8, shuffle=False, num_workers=2)
            st = torch.load(ROOT / "experiments" / run / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
            key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
            m = build_model(cfg["model"]).to(dev); m.load_state_dict(st["models"][key]); m.eval()
            lp, absent = log_prior(cfg)
            lp, absent = lp.to(dev).view(1, -1, 1, 1), absent.to(dev)
            logits, got = [], []
            for b in dl:
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    logits.append(m(b["image"].to(dev)).float())
                got += list(b["stem"])
            assert got == stems
            # review_v2: share of pixels predicted as a class absent from the labelled cells, at each tau; the
            # "_maskabsent" variant (absent-class logits set to -inf) is always written too and is reported when
            # that share exceeds 0.1% at tau = 1.
            for tau, mask_absent in [(t, m) for t in a.taus for m in (False, True)]:
                probs = {CRACK_CLASS: [], INACTIVE_CLASS: []}; preds = []; n_abs = n_px = 0
                for lg in logits:
                    z = lg - tau * lp
                    if mask_absent:
                        z = z.masked_fill(absent.view(1, -1, 1, 1), float("-inf"))
                    sm = torch.softmax(z, 1)
                    for c in probs: probs[c] += list(sm[:, c].cpu().numpy())
                    am = z.argmax(1)
                    n_abs += int(absent[am].sum()); n_px += am.numel()
                    preds += list(am.cpu().numpy())
                r, per = {}, {}
                for name, c in (("crack", CRACK_CLASS), ("inactive", INACTIVE_CLASS)):
                    r[name], per[name] = score(probs[c], preds, gts, c)
                cells = {s: per["crack"][i] + per["inactive"][i] for i, s in enumerate(stems)}
                tag = f"{split}/{run}/tau{tau:g}" + ("_maskabsent" if mask_absent else "")
                res[tag] = {"n": len(stems), "weights": key, "step": int(st.get("step", -1)), "tau": tau,
                            "mask_absent": mask_absent, "absent_pred_share": n_abs / max(n_px, 1),
                            "new_escdd": r, "per_cell": cells}
                print(f"{split:5s} {run:24s} tau {tau:<5g}{' mask' if mask_absent else '     '} absent {n_abs / max(n_px, 1):.5f} crack IoU {r['crack']['iou']:.4f} P {r['crack']['precision']:.3f} "
                      f"R {r['crack']['recall']:.3f} AP {r['crack']['ap']:.3f} bin0 {r['crack']['bin0_share']:.3f} | "
                      f"inactive IoU {r['inactive']['iou']:.4f} | relF1@2 {r['crack']['rel_f1_2']:.4f}", flush=True)
                if tau == 0 and not mask_absent and a.check:
                    ref = json.loads(Path(a.check, f"{run}.json").read_text())[f"{split}/{run}"]["new_escdd"]
                    dmax = max(abs(ref[name][k] - r[name][k]) for name in ("crack", "inactive") for k in ("iou", "ap", "rel_f1_2"))
                    res[tag]["check_max_abs_diff"] = dmax
                    print(f"  check vs re-score JSON: max |diff| = {dmax:.2e}", flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
