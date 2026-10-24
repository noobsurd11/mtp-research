"""Track D inactive-edge re-score (protocol team_2026-10-24_go/trackD/protocol_edge.md). Read-only inference.

Per run (final latest.pth; EMA teacher for Mean Teacher runs, as rescore_label_versions.py), test 50 cells, revised
masks, weak view, bf16, LA tau 0 and 1 (log prior of the run's own labelled cells, rescore_logit_adjust.log_prior).
Band = GT inactive dilated by 2 px (Euclidean, EDT <= 2). Banded crack scoring ignores band pixels in both GT and
prediction (gt' = gt & ~band, pred' = pred & ~band), then the same counts as standard.
Per cell: crack std / band [tp, fp, fn, relTP_pred@2, pred_px, relTP_gt@2, gt_px], inactive [tp, fp, fn],
band_px, crack GT px in band, crack pred px in band.

Usage (from /tmp/noob_el/el_trackD/edge): python trackD_edge_rescore.py --out edge.json --runs <exp dir> ...
"""
from __future__ import annotations

import argparse, json, sys, time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from scipy import ndimage as ndi

CODE = Path("/tmp/noob_el/el_sk1")
sys.path.insert(0, str(CODE)); sys.path.insert(0, str(CODE / "scripts"))
from rescore_logit_adjust import log_prior  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

DATA = CODE / "data"
IMG, NEWT = DATA / "labeled" / "images", DATA / "escdd_masks" / "test"
CR, IN = 14, 11


def counts(p, t):
    d_gt = ndi.distance_transform_edt(~t) if t.any() else np.full(t.shape, np.inf)
    d_pr = ndi.distance_transform_edt(~p) if p.any() else np.full(t.shape, np.inf)
    return [int((p & t).sum()), int((p & ~t).sum()), int((~p & t).sum()),
            int((d_gt[p] <= 2).sum()), int(p.sum()), int((d_pr[t] <= 2).sum()), int(t.sum())]


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True, help="experiment dirs (absolute)")
    ap.add_argument("--taus", nargs="+", type=float, default=[0.0, 1.0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dev = torch.device("cuda")
    stems = sorted(load_split(DATA / "splits" / "test.txt"))
    assert len(stems) == 50
    gts = {s: np.array(Image.open(NEWT / f"{s}.png")) for s in stems}
    bands = {s: ndi.distance_transform_edt(gts[s] != IN) <= 2 if (gts[s] == IN).any() else np.zeros(gts[s].shape, bool)
             for s in stems}
    x_all = torch.stack([torch.from_numpy(np.asarray(Image.open(IMG / f"{s}.png").convert("L"), dtype=np.float32) / 255.0)
                         for s in stems])[:, None]
    res, t0 = {}, time.time()
    for rd in a.runs:
        d = Path(rd); run = d.name
        cfg = load_config(d / "config_used.yaml")
        st = torch.load(d / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
        key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
        m = build_model(cfg["model"]).to(dev); m.load_state_dict(st["models"][key]); m.eval()
        lp, _ = log_prior(cfg); lp = lp.to(dev).view(1, -1, 1, 1)
        logits = []
        for i in range(0, 50, 8):
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits.append(m(((x_all[i:i + 8] - 0.5) / 0.25).to(dev)).float())
        for tau in a.taus:
            per = {}
            for lg_i, lg in enumerate(logits):
                pd = (lg - tau * lp).argmax(1).cpu().numpy()
                for j in range(pd.shape[0]):
                    s = stems[lg_i * 8 + j]; g, b = gts[s], bands[s]
                    p, t = pd[j] == CR, g == CR
                    pi, ti = pd[j] == IN, g == IN
                    per[s] = {"crack_std": counts(p, t), "crack_band": counts(p & ~b, t & ~b),
                              "inactive": [int((pi & ti).sum()), int((pi & ~ti).sum()), int((~pi & ti).sum())],
                              "band_px": int(b.sum()), "gt_crack_in_band": int((t & b).sum()), "pred_crack_in_band": int((p & b).sum())}
            tag = f"{run}/tau{tau:g}"
            res[tag] = {"run_dir": str(d), "weights": key, "step": int(st.get("step", -1)), "tau": tau, "per_cell": per}
            tp, fp, fn = (sum(v["crack_std"][k] for v in per.values()) for k in range(3))
            tb, fb, nb = (sum(v["crack_band"][k] for v in per.values()) for k in range(3))
            print(f"{tag:32s} step {res[tag]['step']} crack IoU std {tp / max(tp + fp + fn, 1):.4f} band {tb / max(tb + fb + nb, 1):.4f} "
                  f"| {time.time() - t0:.0f}s", flush=True)
        del m, logits; torch.cuda.empty_cache()
    Path(a.out).write_text(json.dumps(res))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
