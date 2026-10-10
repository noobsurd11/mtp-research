"""P4: frozen-feature linear probe for crack / inactive (protocol: ~/mtp/research/protocols/P4_frozen_feature_probe.md).

Frozen encoders: rn50_random, rn50_imagenet, convnext_t_imagenet, dinov2_vits14, unetpp_sl100 (reference).
Per-stage 1x1 conv heads on cached, train-standardised features; logits upsampled bilinearly to 512 and summed
(equivalent to a 1x1 conv on upsampled concatenated features). 24-class plain CE on the 47 seed-0 labeled_10pct
images (old 20211104 masks), Adam 1e-3, 2,000 steps, batch 8 with replacement, no augmentation, probe seeds 0 and 1.
Scored on val (54) / test (50) / pooled against the old masks and the revised E-SCDD masks (data/escdd_masks/).

Usage: .venv/bin/python scripts/p4_feature_probe.py [--encoders ...]
"""
from __future__ import annotations

import argparse, json, os, sys, time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
from src.data.benchmark_el import load_index_mask  # noqa: E402
from src.data.class_info import CRACK_CLASS, INACTIVE_CLASS  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.evaluation.threshold_free import binned_ap  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

DATA = ROOT / "data"
IMG, MSK, NEW = DATA / "labeled" / "images", DATA / "labeled" / "masks_coded", DATA / "escdd_masks"
C, BINS, SIZE = 24, 1000, 512
IMNET = (torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1), torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1))
ALL = ["rn50_random", "rn50_imagenet", "convnext_t_imagenet", "dinov2_vits14", "unetpp_sl100"]


def load_img(stem: str) -> torch.Tensor:
    return torch.from_numpy(np.array(Image.open(IMG / f"{stem}.png").convert("L"), dtype=np.float32) / 255.0)


def build_encoder(name: str, dev: torch.device):
    """Returns (callable x01[B,1,512,512] -> list of feature maps, description)."""
    tv = torchvision.models
    if name.startswith("rn50"):
        if name == "rn50_random":
            torch.manual_seed(0)
            m = tv.resnet50(weights=None)
        else:
            m = tv.resnet50(weights=tv.ResNet50_Weights.IMAGENET1K_V2)
        m = m.to(dev).eval()

        def f(x):
            x = ((x.repeat(1, 3, 1, 1) - IMNET[0].to(dev)) / IMNET[1].to(dev))
            x = m.maxpool(m.relu(m.bn1(m.conv1(x))))
            l1 = m.layer1(x)
            return [l1, m.layer2(l1)]
        return f, "layer1 (s4, 256) + layer2 (s8, 512)"
    if name == "convnext_t_imagenet":
        m = tv.convnext_tiny(weights=tv.ConvNeXt_Tiny_Weights.IMAGENET1K_V1).to(dev).eval()

        def f(x):
            x = ((x.repeat(1, 3, 1, 1) - IMNET[0].to(dev)) / IMNET[1].to(dev))
            s0 = m.features[1](m.features[0](x))
            return [s0, m.features[3](m.features[2](s0))]
        return f, "stage0 (s4, 96) + stage1 (s8, 192)"
    if name == "dinov2_vits14":
        m = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14").to(dev).eval()

        def f(x):
            x = ((x.repeat(1, 3, 1, 1) - IMNET[0].to(dev)) / IMNET[1].to(dev))
            x = F.interpolate(x, size=(518, 518), mode="bilinear", align_corners=False)
            t = m.forward_features(x)["x_norm_patchtokens"]            # (B, 37*37, 384)
            return [t.transpose(1, 2).reshape(t.shape[0], -1, 37, 37)]
        return f, "patch tokens 37x37 (s14, 384) at 518 px"
    if name == "unetpp_sl100":
        run = ROOT / "experiments" / "sl_100pct_b8_s0"
        cfg = load_config(run / "config_used.yaml")
        m = build_model(cfg["model"]).to(dev)
        st = torch.load(run / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
        m.load_state_dict(st["models"]["model"])
        m.eval()

        def f(x):
            e = m.encode((x - 0.5) / 0.25)
            return [e[2], e[3]]
        return f, "encode e2 (s4, 128) + e3 (s8, 256); supervised on all train labels (reference)"
    raise ValueError(name)


@torch.no_grad()
def extract(fn, stems, dev, bs=4):
    out = None
    for i in range(0, len(stems), bs):
        x = torch.stack([load_img(s) for s in stems[i:i + bs]])[:, None].to(dev)
        fs = [t.float().half() for t in fn(x)]
        out = [[t] for t in fs] if out is None else [o + [t] for o, t in zip(out, fs)]
    return [torch.cat(o) for o in out]


class Probe(nn.Module):
    def __init__(self, dims, mus, sds):
        super().__init__()
        self.heads = nn.ModuleList([nn.Conv2d(d, C, 1, bias=(k == 0)) for k, d in enumerate(dims)])
        self.mus, self.sds = mus, sds

    def forward(self, feats):
        out = 0
        for h, f, mu, sd in zip(self.heads, feats, self.mus, self.sds):
            out = out + F.interpolate(h((f.float() - mu) / sd), size=(SIZE, SIZE), mode="bilinear", align_corners=False)
        return out


def relaxed(pred, gt, r):
    d_gt = ndi.distance_transform_edt(~gt) if gt.any() else np.full(gt.shape, np.inf)
    d_pr = ndi.distance_transform_edt(~pred) if pred.any() else np.full(gt.shape, np.inf)
    return np.array([(d_gt[pred] <= r).sum(), pred.sum(), (d_pr[gt] <= r).sum(), gt.sum()], np.int64)


def per_image_stats(prob, pred, gt, c):
    p, t = pred == c, gt == c
    b = np.clip((prob.astype(np.float32) * BINS).astype(int), 0, BINS - 1)
    return {"tp": int((p & t).sum()), "fp": int((p & ~t).sum()), "fn": int((~p & t).sum()),
            "pos": np.bincount(b[t], minlength=BINS), "neg": np.bincount(b[~t], minlength=BINS), "rel2": relaxed(p, t, 2)}


def aggregate(rows):
    tp, fp, fn = (sum(r[k] for r in rows) for k in ("tp", "fp", "fn"))
    pos, neg = sum(r["pos"] for r in rows), sum(r["neg"] for r in rows)
    v = sum(r["rel2"] for r in rows)
    P, R = v[0] / max(v[1], 1), v[2] / max(v[3], 1)
    return {"ap": float(binned_ap(pos, neg)), "iou": tp / max(tp + fp + fn, 1), "precision": tp / max(tp + fp, 1),
            "recall": tp / max(tp + fn, 1), "rel_f1_2": float(2 * P * R / max(P + R, 1e-9)), "rel_p2": float(P), "rel_r2": float(R)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--encoders", nargs="+", default=ALL)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1])
    ap.add_argument("--out", default="reports/probes/p4_feature_probe.json")
    a = ap.parse_args()
    dev = torch.device("cuda")
    train = sorted(load_split(DATA / "splits" / "seed0" / "labeled_10pct.txt"))
    evals = {s: sorted(load_split(DATA / "splits" / f"{s}.txt")) for s in ("val", "test")}
    Y = torch.from_numpy(np.stack([load_index_mask(MSK / f"{s}.png") for s in train])).to(dev)
    gts = {s: {"old": [load_index_mask(MSK / f"{t}.png") for t in st],
               "revised": [np.array(Image.open(NEW / s / f"{t}.png")) for t in st]} for s, st in evals.items()}
    res = {"train_images": len(train), "eval_images": {s: len(v) for s, v in evals.items()}, "encoders": {}}
    outp = Path(a.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    for name in a.encoders:
        t0 = time.time()
        fn, desc = build_encoder(name, dev)
        feats = extract(fn, train, dev)
        dims = [f.shape[1] for f in feats]
        mus = [f.float().mean((0, 2, 3), keepdim=True) for f in feats]
        sds = [f.float().std((0, 2, 3), keepdim=True).clamp(min=1e-6) for f in feats]
        probes = {}
        for seed in a.seeds:
            torch.manual_seed(seed)
            pr = Probe(dims, mus, sds).to(dev)
            opt = torch.optim.Adam(pr.parameters(), lr=1e-3)
            g = torch.Generator().manual_seed(seed)
            for step in range(a.steps):
                idx = torch.randint(0, len(train), (8,), generator=g).to(dev)
                loss = F.cross_entropy(pr([f[idx] for f in feats]), Y[idx])
                opt.zero_grad(set_to_none=True)
                loss.backward()
                opt.step()
            probes[seed] = (pr.eval(), float(loss))
        del feats
        stats = {seed: {s: {lab: {"crack": [], "inactive": []} for lab in ("old", "revised")} for s in evals} for seed in a.seeds}
        with torch.no_grad():
            for s, st in evals.items():
                for i in range(0, len(st), 4):
                    x = torch.stack([load_img(t) for t in st[i:i + 4]])[:, None].to(dev)
                    fb = fn(x)
                    for seed, (pr, _) in probes.items():
                        lg = pr(fb)
                        sm = torch.softmax(lg, 1)
                        pc, pi, pd = sm[:, CRACK_CLASS].cpu().numpy(), sm[:, INACTIVE_CLASS].cpu().numpy(), lg.argmax(1).cpu().numpy()
                        for j in range(x.shape[0]):
                            for lab in ("old", "revised"):
                                gt = gts[s][lab][i + j]
                                stats[seed][s][lab]["crack"].append(per_image_stats(pc[j], pd[j], gt, CRACK_CLASS))
                                stats[seed][s][lab]["inactive"].append(per_image_stats(pi[j], pd[j], gt, INACTIVE_CLASS))
        enc = {"features": desc, "dims": dims, "final_train_loss": {str(k): v[1] for k, v in probes.items()}, "seeds": {}}
        for seed in a.seeds:
            enc["seeds"][str(seed)] = {}
            for split in ("val", "test", "pooled"):
                enc["seeds"][str(seed)][split] = {}
                for lab in ("old", "revised"):
                    enc["seeds"][str(seed)][split][lab] = {}
                    for cl in ("crack", "inactive"):
                        rows = (stats[seed]["val"][lab][cl] + stats[seed]["test"][lab][cl]) if split == "pooled" else stats[seed][split][lab][cl]
                        enc["seeds"][str(seed)][split][lab][cl] = aggregate(rows)
        mean = {}
        for split in ("val", "test", "pooled"):
            mean[split] = {lab: {cl: {k: float(np.mean([enc["seeds"][str(sd)][split][lab][cl][k] for sd in a.seeds]))
                                      for k in enc["seeds"][str(a.seeds[0])][split][lab][cl]} for cl in ("crack", "inactive")}
                           for lab in ("old", "revised")}
        enc["mean"] = mean
        enc["seconds"] = round(time.time() - t0)
        res["encoders"][name] = enc
        m = mean["pooled"]["revised"]
        print(f"{name:20s} pooled/revised crack AP {m['crack']['ap']:.3f} IoU {m['crack']['iou']:.3f} relF1@2 {m['crack']['rel_f1_2']:.3f} | "
              f"inactive AP {m['inactive']['ap']:.3f} IoU {m['inactive']['iou']:.3f} | test/old crack AP {mean['test']['old']['crack']['ap']:.3f} "
              f"| {enc['seconds']}s", flush=True)
        outp.write_text(json.dumps(res, indent=1))
        del fn
        torch.cuda.empty_cache()
    print("wrote", outp)


if __name__ == "__main__":
    main()
