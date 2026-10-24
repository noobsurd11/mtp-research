"""Track M, M0: val-only post-hoc operating points on saved val log-probs (no test, no ext).

For each run (and seed ensembles: mean of softmax over runs):
  1. plain argmax vs dihedral-8 TTA;
  2. logit adjustment z - tau*log(pi), pi = class pixel share over the 478 train cells (masks_escdd), tau grid;
  3. crack-only and inactive-only additive bias sweeps (P, R, IoU, relP@2, relR@2);
  4. 24-class bias vector fitted by coordinate ascent on val mIoU_gt, with a 2-fold module-grouped cross-fit on val
     (fit on one half of the modules, score the other) to estimate how much of the gain is val overfitting.

Usage (cv02): python m0_tune.py --m0 m0 --code /tmp/noob_el/el_p13 --runs <run names> --ens NAME=r1,r2,...
"""
from __future__ import annotations

import argparse, json
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

NC, CRACK, INACT = 24, 14, 11
DEV = torch.device("cuda")
DISK = torch.tensor([[1 if dx * dx + dy * dy <= 4 else 0 for dx in range(-2, 3)] for dy in range(-2, 3)], dtype=torch.float32, device=DEV)[None, None]


def dil(m):  # bool [N,H,W] -> within 2 px (euclidean)
    return F.conv2d(m[:, None].float(), DISK, padding=2)[:, 0] > 0


def metrics(pred, gt):
    C = torch.bincount((gt.long() * NC + pred.long()).ravel(), minlength=NC * NC).reshape(NC, NC).double().cpu().numpy()
    tp = np.diag(C); g = C.sum(1); p = C.sum(0); den = g + p - tp
    iou = np.where(den > 0, tp / np.maximum(den, 1), np.nan)
    o = {"miou24": float(np.nanmean(iou)), "miou_gt": float(np.nanmean(np.where(g > 0, iou, np.nan)))}
    for n, c in (("crack", CRACK), ("inact", INACT)):
        o[f"{n}_iou"] = float(iou[c]); o[f"{n}_P"] = float(tp[c] / max(p[c], 1)); o[f"{n}_R"] = float(tp[c] / max(g[c], 1))
    pc, gc = pred == CRACK, gt == CRACK
    rP = float((pc & dil(gc)).sum() / max(int(pc.sum()), 1)); rR = float((gc & dil(pc)).sum() / max(int(gc.sum()), 1))
    o.update(relP2=rP, relR2=rR, relF1=2 * rP * rR / max(rP + rR, 1e-9))
    o["iou"] = iou.tolist()
    return o


def mi(pred, gt, cls_mask):
    C = torch.bincount((gt.long() * NC + pred.long()).ravel(), minlength=NC * NC).reshape(NC, NC).double()
    tp = torch.diag(C); g = C.sum(1); p = C.sum(0); den = g + p - tp
    iou = tp / den.clamp(min=1)
    return float(iou[cls_mask].mean())


def argmax_b(lp, b, chunk=8):
    return torch.cat([(lp[i:i + chunk].float() + b[None, :, None, None]).argmax(1) for i in range(0, len(lp), chunk)])


def fit_bias(lp, gt, cls_mask, grid=np.arange(-3, 3.01, 0.5), rounds=2):
    b = torch.zeros(NC, device=DEV)
    best = mi(argmax_b(lp, b), gt, cls_mask)
    for _ in range(rounds):
        for c in range(NC):
            if c == 0:
                continue  # background is the reference
            for v in grid:
                bb = b.clone(); bb[c] = float(v)
                s = mi(argmax_b(lp, bb), gt, cls_mask)
                if s > best + 1e-6:
                    best, b = s, bb
    return b, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m0", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--ens", nargs="*", default=[])
    ap.add_argument("--out", default="m0_tune.json")
    a = ap.parse_args()
    m0 = Path(a.m0)
    gt = torch.from_numpy(np.load(m0 / "val_gt.npy")).to(DEV)
    stems = [l for l in (m0 / "val_stems.txt").read_text().split("\n") if l]
    # group key: module ID, except CFVS (a time series of the same modules) grouped by source + cell position
    gk = lambda s: ("CFVS_" + "_".join(s.split("_")[2:])) if s.startswith("CFVS") else "_".join(s.split("_")[:2])
    mods = sorted({gk(s) for s in stems})
    rng = np.random.default_rng(0); perm = rng.permutation(len(mods))
    fold_of_mod = {mods[i]: int(k % 2) for k, i in enumerate(perm)}
    fold = torch.tensor([fold_of_mod[gk(s)] for s in stems], device=DEV)
    # train prior
    data = Path(a.code) / "data"
    tr = [l.strip() for l in open(data / "splits" / "train.txt") if l.strip()]
    cnt = np.zeros(NC)
    for s in tr:
        cnt += np.bincount(np.array(Image.open(data / "labeled" / "masks_escdd" / f"{s}.png")).ravel(), minlength=NC)[:NC]
    pi = torch.tensor(np.maximum(cnt / cnt.sum(), 1e-8), dtype=torch.float32, device=DEV)
    logpi = torch.log(pi)
    present = torch.bincount(gt.long().ravel(), minlength=NC)[:NC] > 0
    items = [(r, [r]) for r in a.runs] + [(e.split("=")[0], e.split("=")[1].split(",")) for e in a.ens]
    res = {"prior": pi.tolist(), "folds": {m: f for m, f in fold_of_mod.items()}}
    for name, members in items:
        out = {}
        for var in ("val_logp", "val_tta_logp"):
            if len(members) == 1:
                lp = torch.from_numpy(np.load(m0 / f"{members[0]}.{var}.npy")).to(DEV)
            else:
                acc = None
                for r in members:
                    p = torch.from_numpy(np.load(m0 / f"{r}.{var}.npy")).to(DEV).float().exp()
                    acc = p if acc is None else acc + p
                lp = torch.log(acc / len(members) + 1e-12).half(); del acc
            tag = "plain" if var == "val_logp" else "tta"
            z = torch.zeros(NC, device=DEV)
            out[tag] = metrics(argmax_b(lp, z), gt)
            if tag == "plain" or len(members) > 1 or True:
                out[f"{tag}_la"] = {str(t): metrics(argmax_b(lp, -t * logpi), gt) for t in (0.25, 0.5, 0.75, 1.0, 1.5, 2.0)}
                sw = {}
                for c, n in ((CRACK, "crack"), (INACT, "inact")):
                    for v in (-1, -0.5, 0.5, 1, 1.5, 2, 3, 4):
                        b = z.clone(); b[c] = v
                        m = metrics(argmax_b(lp, b), gt); m.pop("iou")
                        sw[f"{n}{v:+}"] = m
                out[f"{tag}_sweep"] = sw
                # full bias, in-sample and 2-fold cross-fit
                bfull, s_in = fit_bias(lp, gt, present)
                cf_pred = torch.empty_like(gt)
                biases = []
                for f in (0, 1):
                    tr_i, te_i = (fold != f).nonzero().ravel(), (fold == f).nonzero().ravel()
                    pm = torch.bincount(gt[tr_i].long().ravel(), minlength=NC)[:NC] > 0
                    bf, _ = fit_bias(lp[tr_i], gt[tr_i], pm)
                    biases.append(bf.tolist())
                    cf_pred[te_i] = argmax_b(lp[te_i], bf).to(cf_pred.dtype)
                out[f"{tag}_bias_in"] = {"b": bfull.tolist(), **metrics(argmax_b(lp, bfull), gt)}
                out[f"{tag}_bias_cv"] = {"b_folds": biases, **metrics(cf_pred, gt)}
            del lp; torch.cuda.empty_cache()
        res[name] = out
        p, t = out["plain"], out["tta"]
        print(f"{name:22s} plain crack {p['crack_iou']:.3f} relF1 {p['relF1']:.3f} inact {p['inact_iou']:.3f} mIoU_gt {p['miou_gt']:.3f} | "
              f"tta {t['crack_iou']:.3f} {t['relF1']:.3f} {t['inact_iou']:.3f} {t['miou_gt']:.3f} | "
              f"bias_in mIoU_gt {out['plain_bias_in']['miou_gt']:.3f} cv {out['plain_bias_cv']['miou_gt']:.3f}", flush=True)
        Path(a.out).write_text(json.dumps(res))


if __name__ == "__main__":
    main()
