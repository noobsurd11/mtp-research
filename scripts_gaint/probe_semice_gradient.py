"""P2 probe: does the SemiCE consistency term change the student's class decisions?

Protocol: ~/mtp/research/protocols/P2_semice_gradient_probe.md (locked before running).

Read-only. Loads ``experiments/<run>/checkpoints/latest.pth`` (student ``model`` and EMA ``teacher``), draws
training batches exactly as the run did (labelled ``labeled_view`` + unlabelled strong / weak views, same
streams and seed), and does forward + backward only (no optimizer step, nothing saved but the report).

Per batch it measures:
  * loss values: loss_sup, lambda * loss_con;
  * parameter-gradient norms of loss_sup, lambda * loss_con and a reference pseudo-label CE
    (teacher argmax where teacher max-prob >= 0.95, weight 1), and their cosines with the supervised gradient;
  * the logit-gradient of loss_con split into the per-pixel class-mean component (adding the same value to all
    24 logits of a pixel leaves softmax unchanged, so this part cannot change any decision) and the rest;
  * the positive / negative sets: per-class share of unlabelled pixels flagged positive, share of pixels with
    0 / 1 / >= 2 positive classes, share of active (pixel, class) pairs that are negative, mean raw logit level;
  * student / teacher argmax disagreement on the unlabelled pixels.
Also parses ``train.log`` for lambda * loss_con / loss_sup over training.

Usage::

    .venv/bin/python scripts/probe_semice_gradient.py --run experiments/mt_20pct_s0 --batches 40
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
os.chdir(ROOT)

import train as T  # noqa: E402  (build_benchmark_data)
from src.data.class_info import CLASS_INFO, CRACK_CLASS, INACTIVE_CLASS, PADDING_CLASS  # noqa: E402
from src.losses.loss_factory import build_losses  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

NAMES = [c["name"] for c in CLASS_INFO]
REPORT_CLASSES = {"background": 0, "padding": PADDING_CLASS, "crack": CRACK_CLASS, "inactive": INACTIVE_CLASS}


def flat_grad(model: torch.nn.Module, loss: torch.Tensor) -> torch.Tensor:
    params = [p for p in model.parameters() if p.requires_grad]
    grads = torch.autograd.grad(loss, params, retain_graph=True, allow_unused=True)
    return torch.cat([(g if g is not None else torch.zeros_like(p)).flatten() for g, p in zip(grads, params)])


def cos(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(F.cosine_similarity(a[None], b[None]).item())


def parse_log(path: Path) -> list[dict]:
    pat = re.compile(r"step (\d+)/\d+\s+loss=\S+\s+loss_sup=(\S+)\s+loss_con=(\S+)\s+lambda=(\S+)\s+lr=(\S+)")
    rows = []
    for line in path.read_text().splitlines():
        m = pat.search(line)
        if m:
            s, ls, lc, lam, lr = m.groups()
            rows.append({"step": int(s), "loss_sup": float(ls), "loss_con": float(lc), "lambda": float(lam), "lr": float(lr)})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="experiments/mt_20pct_s0")
    ap.add_argument("--batches", type=int, default=40)
    ap.add_argument("--pl_threshold", type=float, default=0.95)
    ap.add_argument("--out", default="reports/probes")
    a = ap.parse_args()

    run = ROOT / a.run
    cfg = load_config(run / "config_used.yaml")
    assert cfg["method"] == "mean_teacher", cfg["method"]
    dev = torch.device("cuda")
    seed, frac = int(cfg["seed"]), float(cfg["data"]["labeled_fraction"])
    torch.manual_seed(seed)

    data = T.build_benchmark_data(cfg, "mean_teacher", seed, frac, True, dev, 4)
    losses = build_losses(cfg["loss"], data["class_counts"])
    sup, con = losses["supervised"].to(dev), losses["consistency"].to(dev)
    t_pos, t_neg = con.t_pos.float().cpu(), con.t_neg.float().cpu()

    st = torch.load(run / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
    student, teacher = build_model(cfg["model"]).to(dev), build_model(cfg["model"]).to(dev)
    student.load_state_dict(st["models"]["model"])
    teacher.load_state_dict(st["models"]["teacher"])
    student.train()   # as in training: dropout on, BN batch statistics
    teacher.eval()
    for p in teacher.parameters():
        p.requires_grad_(False)

    lam = float(cfg["ssl"]["lambda_final"])
    labeled_view = cfg["ssl"].get("labeled_view", "strong")
    amp_dtype = torch.bfloat16 if cfg["training"].get("amp_dtype", "bfloat16") == "bfloat16" else torch.float16
    lab_it, unl_it = data["labeled_loader"].iterate(0), data["unlabeled_loader"].iterate(0)

    C = len(NAMES)
    acc = {k: [] for k in ("loss_sup", "lam_loss_con", "loss_pl", "g_sup", "g_con", "g_pl", "cos_con_sup", "cos_pl_sup",
                           "offset_share", "neg_pair_share", "pix_pos0", "pix_pos1", "pix_pos2plus", "argmax_in_pos",
                           "disagree", "pl_mask_frac", "logit_level")}
    pos_share = torch.zeros(C, dtype=torch.float64)
    neg_share = torch.zeros(C, dtype=torch.float64)
    pl_comp = torch.zeros(C, dtype=torch.float64)
    n_pix_total = 0
    for b in range(a.batches):
        batch, ubatch = next(lab_it), next(unl_it)
        n_l = batch["image_strong"].shape[0]
        lab_view = batch["image_weak"] if labeled_view == "weak" else batch["image_strong"]
        strong = torch.cat([lab_view, ubatch["image_strong"]]).to(dev)
        masks = batch["mask"].to(dev)
        with torch.autocast("cuda", dtype=amp_dtype):
            s_logits = student(strong)
            with torch.no_grad():
                t_logits = teacher(ubatch["image_weak"].to(dev))
        s_u = s_logits[n_l:].float()
        t_u = t_logits.float()
        loss_sup = sup(s_logits[:n_l], masks)
        loss_con = con(s_u, t_u)
        # reference: standard confidence-thresholded pseudo-label CE
        t_prob = torch.softmax(t_u, 1)
        conf, pl = t_prob.max(1)
        m = (conf >= a.pl_threshold).float()
        loss_pl = (F.cross_entropy(s_u, pl, reduction="none") * m).sum() / m.sum().clamp(min=1.0)

        g_sup = flat_grad(student, loss_sup)
        g_con = flat_grad(student, lam * loss_con)
        g_pl = flat_grad(student, loss_pl)
        # logit-gradient of loss_con: share in the per-pixel class-mean (softmax-invariant) direction
        g_logit = torch.autograd.grad(loss_con, s_u, retain_graph=False)[0]
        mean_c = g_logit.mean(1, keepdim=True)
        offset_energy = float((mean_c.pow(2) * C).sum())
        total_energy = float(g_logit.pow(2).sum())

        tp, tn = t_pos.to(dev).view(1, C, 1, 1), t_neg.to(dev).view(1, C, 1, 1)
        pos, neg = t_u > tp, t_u < -tn
        npos = pos.sum(1)
        n_pix = npos.numel()
        n_pix_total += n_pix
        pos_share += pos.sum((0, 2, 3)).double().cpu()
        neg_share += neg.sum((0, 2, 3)).double().cpu()
        pl_comp += torch.bincount(pl[m.bool()].flatten(), minlength=C).double().cpu()
        t_arg = t_u.argmax(1)

        acc["loss_sup"].append(float(loss_sup))
        acc["lam_loss_con"].append(float(lam * loss_con))
        acc["loss_pl"].append(float(loss_pl))
        acc["g_sup"].append(float(g_sup.norm()))
        acc["g_con"].append(float(g_con.norm()))
        acc["g_pl"].append(float(g_pl.norm()))
        acc["cos_con_sup"].append(cos(g_con, g_sup))
        acc["cos_pl_sup"].append(cos(g_pl, g_sup))
        acc["offset_share"].append(offset_energy / max(total_energy, 1e-30))
        acc["neg_pair_share"].append(float(neg.sum()) / max(float((pos | neg).sum()), 1.0))
        acc["pix_pos0"].append(float((npos == 0).sum()) / n_pix)
        acc["pix_pos1"].append(float((npos == 1).sum()) / n_pix)
        acc["pix_pos2plus"].append(float((npos >= 2).sum()) / n_pix)
        acc["argmax_in_pos"].append(float(pos.gather(1, t_arg[:, None]).float().mean()))
        acc["disagree"].append(float((s_u.argmax(1) != t_arg).float().mean()))
        acc["pl_mask_frac"].append(float(m.mean()))
        acc["logit_level"].append(float(t_u.mean()))
        if b % 10 == 0:
            print(f"batch {b}: lam*con/sup {acc['lam_loss_con'][-1] / acc['loss_sup'][-1]:.3f}  |g_con|/|g_sup| "
                  f"{acc['g_con'][-1] / acc['g_sup'][-1]:.4f}  offset share {acc['offset_share'][-1]:.3f}  "
                  f"pix>=2pos {acc['pix_pos2plus'][-1]:.3f}  |g_pl|/|g_sup| {acc['g_pl'][-1] / acc['g_sup'][-1]:.4f}", flush=True)

    def ms(v: list[float]) -> dict:
        x = np.asarray(v, np.float64)
        return {"mean": float(x.mean()), "sd": float(x.std(ddof=1)) if len(x) > 1 else 0.0}

    summary = {k: ms(v) for k, v in acc.items()}
    ratio = lambda num, den: ms([n / d for n, d in zip(acc[num], acc[den])])  # noqa: E731
    summary["ratio_g_con_over_g_sup"] = ratio("g_con", "g_sup")
    summary["ratio_g_pl_over_g_sup"] = ratio("g_pl", "g_sup")
    summary["ratio_lam_con_over_sup_value"] = ratio("lam_loss_con", "loss_sup")
    per_class = {n: {"pos_pixel_share": float(pos_share[c] / n_pix_total), "neg_pixel_share": float(neg_share[c] / n_pix_total),
                     "t_pos": float(t_pos[c]), "t_neg": float(t_neg[c]),
                     "pl_conf_share": float(pl_comp[c] / max(pl_comp.sum(), 1))}
                 for n, c in REPORT_CLASSES.items()}
    log_rows = parse_log(run / "train.log")
    traj = [{"step": r["step"], "lam_con_over_sup": r["lambda"] * r["loss_con"] / r["loss_sup"] if r["loss_sup"] else None,
             "lr": r["lr"]} for r in log_rows if r["step"] % 1000 == 0]
    out = {"run": a.run, "step": int(st["step"]), "batches": a.batches, "lambda": lam, "labeled_view": labeled_view,
           "pl_threshold": a.pl_threshold, "summary": summary, "per_class": per_class,
           "t_pos_all": t_pos.tolist(), "t_neg_all": t_neg.tolist(), "log_trajectory": traj}
    od = ROOT / a.out
    od.mkdir(parents=True, exist_ok=True)
    path = od / f"p2_semice_{run.name}.json"
    path.write_text(json.dumps(out, indent=1))
    print(json.dumps({"summary": {k: round(v["mean"], 5) for k, v in summary.items()}, "per_class": per_class}, indent=1))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
