"""Track D probe (protocol team_2026-10-24_go/trackD/protocol_probe.md): frozen-encoder linear probe per source.

P4 recipe (scripts_gaint/p4_feature_probe.py) with one change: probe trained on the seed-0 5% labelled cells (23) with
revised masks (labeled/masks_escdd), i.e. A5c's labelled set. Same inference pass scores A5c (5 seeds) at LA tau 0 and 1.
Eval sets: test (50, escdd_masks/test) and pool (seed-0 unlabelled 5% minus the 7 D7 twins = 448, labeled/masks_escdd).
Per cell: crack tp/fp/fn, relaxed@2 counts, inactive tp/fp/fn; per-cell 1000-bin pos/neg histograms (npz);
relaxed@2 recall of the 40 always-missed components at argmax and at a matched-precision threshold.

Run from /tmp/noob_el/el_trackD/probe with el_sk1 code (read-only):
  python trackD_probe.py --out out/  [--encoders ...] [--a5c ...]
"""
from __future__ import annotations

import argparse, hashlib, json, sys, time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from PIL import Image
from scipy import ndimage as ndi

CODE = Path("/tmp/noob_el/el_sk1")
sys.path.insert(0, str(CODE)); sys.path.insert(0, str(CODE / "scripts"))
from rescore_logit_adjust import log_prior  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.evaluation.threshold_free import binned_ap  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

DATA = CODE / "data"
IMG, REV, NEWT = DATA / "labeled" / "images", DATA / "labeled" / "masks_escdd", DATA / "escdd_masks" / "test"
CR, IN, C, BINS, SIZE = 14, 11, 24, 1000, 512
IMNET = (torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1), torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1))
TWINS_TRAIN = [l.strip() for l in (CODE / "d7_twin_train_cells.txt").read_text().split() if l.strip()]
A5C = ["p12_A_5pct_s0", "p12_A_5pct_s1", "p12_A_5pct_s2", "p13_A_5pct_s3", "p13_A_5pct_s4"]
ENC = ["rn50_random", "rn34_imagenet", "rn50_imagenet", "convnext_t", "dinov2_vits14", "ref_A5c_enc"]
SEEDS = [0, 1]


def src_of(stem): return stem.split("_")[0]


def load_img(stem):
    return torch.from_numpy(np.asarray(Image.open(IMG / f"{stem}.png").convert("L"), dtype=np.float32) / 255.0)


def imnet(x, dev):
    return (x.repeat(1, 3, 1, 1) - IMNET[0].to(dev)) / IMNET[1].to(dev)


def build_encoder(name, dev):
    tv = torchvision.models
    if name in ("rn50_random", "rn50_imagenet", "rn34_imagenet"):
        if name == "rn50_random":
            torch.manual_seed(0); m = tv.resnet50(weights=None)
        elif name == "rn50_imagenet":
            m = tv.resnet50(weights=tv.ResNet50_Weights.IMAGENET1K_V2)
        else:
            m = tv.resnet34(weights=tv.ResNet34_Weights.IMAGENET1K_V1)
        m = m.to(dev).eval()

        def f(x):
            x = m.maxpool(m.relu(m.bn1(m.conv1(imnet(x, dev)))))
            l1 = m.layer1(x)
            return [l1, m.layer2(l1)]
        return f
    if name == "convnext_t":
        m = tv.convnext_tiny(weights=tv.ConvNeXt_Tiny_Weights.IMAGENET1K_V1).to(dev).eval()

        def f(x):
            s0 = m.features[1](m.features[0](imnet(x, dev)))
            return [s0, m.features[3](m.features[2](s0))]
        return f
    if name == "dinov2_vits14":
        m = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14").to(dev).eval()

        def f(x):
            x = F.interpolate(imnet(x, dev), size=(518, 518), mode="bilinear", align_corners=False)
            t = m.forward_features(x)["x_norm_patchtokens"]
            return [t.transpose(1, 2).reshape(t.shape[0], -1, 37, 37)]
        return f
    if name == "ref_A5c_enc":
        run = CODE / "experiments" / A5C[0]
        m = build_model(load_config(run / "config_used.yaml")["model"]).to(dev)
        m.load_state_dict(torch.load(run / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)["models"]["model"])
        m.eval()

        def f(x):
            e = m.encoder((x - 0.5) / 0.25)
            return [e[2], e[3]]
        return f
    raise ValueError(name)


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


def cell_stats(prob_c, prob_i, pred, gt):
    """Per cell: crack [tp, fp, fn, relTP_pred, pred_px, relTP_gt, gt_px], inactive [tp, fp, fn], hists (2, 2, BINS)."""
    out, hist = {}, np.zeros((2, 2, BINS), np.int32)
    for k, (c, pr) in enumerate(((CR, prob_c), (IN, prob_i))):
        p, t = pred == c, gt == c
        row = [int((p & t).sum()), int((p & ~t).sum()), int((~p & t).sum())]
        b = np.clip((pr * BINS).astype(int), 0, BINS - 1)
        hist[k, 0] = np.bincount(b[t], minlength=BINS); hist[k, 1] = np.bincount(b[~t], minlength=BINS)
        if c == CR:
            d_gt = ndi.distance_transform_edt(~t) if t.any() else np.full(t.shape, np.inf)
            d_pr = ndi.distance_transform_edt(~p) if p.any() else np.full(t.shape, np.inf)
            row += [int((d_gt[p] <= 2).sum()), int(p.sum()), int((d_pr[t] <= 2).sum()), int(t.sum())]
        out["crack" if c == CR else "inactive"] = row
    return out, hist


def matched_bin(pos, neg, target):
    """Lowest bin k (highest recall) with precision of p >= k/BINS at least target; returns (k, recall, precision)."""
    tp, fp = np.cumsum(pos[::-1])[::-1], np.cumsum(neg[::-1])[::-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        prec = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
    ok = np.where(prec >= target)[0]
    if len(ok) == 0:
        return None, 0.0, float("nan")
    k = int(ok.min())
    return k, float(tp[k] / max(pos.sum(), 1)), float(prec[k])


def comp_recall(prob_c, pred_mask, gt, comps):
    d_pr = ndi.distance_transform_edt(~pred_mask) if pred_mask.any() else np.full(gt.shape, np.inf)
    lab, _ = ndi.label(gt == CR, structure=np.ones((3, 3), bool))
    return {cid: [int((d_pr[lab == k] <= 2).sum()), int((lab == k).sum())] for cid, k in comps}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--encoders", nargs="+", default=ENC)
    ap.add_argument("--a5c", nargs="+", default=A5C)
    ap.add_argument("--steps", type=int, default=2000)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    dev = torch.device("cuda")
    train = sorted(load_split(DATA / "splits" / "seed0" / "labeled_5pct.txt"))
    test = sorted(load_split(DATA / "splits" / "test.txt"))
    val = set(load_split(DATA / "splits" / "val.txt"))
    pool_all = sorted(load_split(DATA / "splits" / "seed0" / "unlabeled_5pct.txt"))
    assert len(train) == 23 and len(test) == 50 and len(pool_all) == 455 and len(TWINS_TRAIN) == 7
    assert all(t in pool_all for t in TWINS_TRAIN)
    pool = [s for s in pool_all if s not in TWINS_TRAIN]
    assert len(pool) == 448 and not (set(pool) & (set(test) | val | set(train)))
    sets = {"test": (test, {s: np.array(Image.open(NEWT / f"{s}.png")) for s in test}),
            "pool": (pool, {s: np.array(Image.open(REV / f"{s}.png")) for s in pool})}
    m40 = json.loads((CODE / "missed40.json").read_text())
    comps_by_stem = {}
    for r in m40:
        comps_by_stem.setdefault(r["stem"], []).append((r["id"], r["comp"]))
    assert len(m40) == 40
    percell, hists, meta = {}, {}, {"train": train, "pool_n": len(pool), "twins_excluded": TWINS_TRAIN, "models": {}}

    def evaluate(tag, predict):
        """predict(x01 batch [B,1,512,512]) -> logits [B,24,512,512] (float)."""
        percell[tag] = {}
        for sname, (stems, gts) in sets.items():
            H = np.zeros((len(stems), 2, 2, BINS), np.int32)
            probs40 = {}
            for i in range(0, len(stems), 4):
                chunk = stems[i:i + 4]
                x = torch.stack([load_img(s) for s in chunk])[:, None].to(dev)
                with torch.no_grad():
                    lg = predict(x)
                    sm = torch.softmax(lg, 1)
                pc, pi, pd = sm[:, CR].cpu().numpy(), sm[:, IN].cpu().numpy(), lg.argmax(1).cpu().numpy()
                for j, s in enumerate(chunk):
                    row, h = cell_stats(pc[j], pi[j], pd[j], gts[s])
                    H[i + j] = h
                    if sname == "test" and s in comps_by_stem:
                        row["comp40_argmax"] = comp_recall(pc[j], pd[j] == CR, gts[s], comps_by_stem[s])
                        probs40[s] = pc[j].astype(np.float32)
                    percell[tag][f"{sname}/{s}"] = row
            hists[f"{tag}|{sname}"] = H
            if sname == "test":
                hists[f"{tag}|probs40"] = probs40
        # free logits

    t0 = time.time()
    # ---- A5c at tau 0 / 1
    for run in a.a5c:
        d = CODE / "experiments" / run
        cfg = load_config(d / "config_used.yaml")
        st = torch.load(d / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
        m = build_model(cfg["model"]).to(dev); m.load_state_dict(st["models"]["model"]); m.eval()
        lp, _ = log_prior(cfg); lp = lp.to(dev).view(1, -1, 1, 1)
        for tau in (0.0, 1.0):
            def pred(x, m=m, tau=tau):
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    z = m((x - 0.5) / 0.25).float()
                return z - tau * lp
            tag = f"A5c/{run}/tau{tau:g}"
            evaluate(tag, pred)
            meta["models"][tag] = {"step": int(st.get("step", -1))}
            print(f"{tag} done {time.time() - t0:.0f}s", flush=True)
        del m; torch.cuda.empty_cache()
    # ---- probes
    Ytr = torch.from_numpy(np.stack([np.array(Image.open(REV / f"{s}.png")).astype(np.int64) for s in train])).to(dev)
    for name in a.encoders:
        t1 = time.time()
        fn = build_encoder(name, dev)
        with torch.no_grad():
            feats = None
            for i in range(0, len(train), 4):
                fs = [t.float().half() for t in fn(torch.stack([load_img(s) for s in train[i:i + 4]])[:, None].to(dev))]
                feats = [[t] for t in fs] if feats is None else [o + [t] for o, t in zip(feats, fs)]
            feats = [torch.cat(o) for o in feats]
        dims = [f.shape[1] for f in feats]
        mus = [f.float().mean((0, 2, 3), keepdim=True) for f in feats]
        sds = [f.float().std((0, 2, 3), keepdim=True).clamp(min=1e-6) for f in feats]
        for seed in SEEDS:
            torch.manual_seed(seed)
            pr = Probe(dims, mus, sds).to(dev)
            opt = torch.optim.Adam(pr.parameters(), lr=1e-3)
            g = torch.Generator().manual_seed(seed)
            for step in range(a.steps):
                idx = torch.randint(0, len(train), (8,), generator=g).to(dev)
                loss = F.cross_entropy(pr([f[idx] for f in feats]), Ytr[idx])
                opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
            pr.eval()
            tag = f"probe/{name}/seed{seed}"
            evaluate(tag, lambda x, pr=pr: pr(fn(x)))
            meta["models"][tag] = {"final_train_loss": float(loss), "dims": dims}
            print(f"{tag} loss {float(loss):.4f} done {time.time() - t1:.0f}s", flush=True)
        del feats, fn; torch.cuda.empty_cache()
    # ---- matched-precision component recall (all-source test, target = A5c+LA mean pixel precision)
    def agg_prec(tag):
        tp = sum(v["crack"][0] for k, v in percell[tag].items() if k.startswith("test/"))
        fp = sum(v["crack"][1] for k, v in percell[tag].items() if k.startswith("test/"))
        return tp / max(tp + fp, 1)
    target = float(np.mean([agg_prec(f"A5c/{r}/tau1") for r in a.a5c]))
    meta["comp40_target_precision_test_all"] = target
    for tag in list(percell):
        H = hists[f"{tag}|test"]
        k, rec, prec = matched_bin(H[:, 0, 0].sum(0), H[:, 0, 1].sum(0), target)
        meta["models"][tag]["comp40_matched"] = {"bin": k, "recall": rec, "precision": prec}
        for s, cl in comps_by_stem.items():
            pc = hists[f"{tag}|probs40"][s]
            thr_mask = (np.clip((pc * BINS).astype(int), 0, BINS - 1) >= k) if k is not None else np.zeros_like(pc, bool)
            percell[tag][f"test/{s}"]["comp40_matched"] = comp_recall(pc, thr_mask, sets["test"][1][s], cl)
    # ---- outputs
    np.savez_compressed(out / "hists.npz", **{k: v for k, v in hists.items() if not k.endswith("|probs40")},
                        stems_test=np.array(test), stems_pool=np.array(pool))
    (out / "percell.json").write_text(json.dumps(percell))
    ck = Path(torch.hub.get_dir()) / "checkpoints"
    meta["weights_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ck.glob("*.pth"))}
    meta["seconds"] = round(time.time() - t0)
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    # ---- quick summary: crack AP / IoU per source (test, pool)
    for tag in percell:
        line = []
        for sname, (stems, _) in sets.items():
            H = hists[f"{tag}|{sname}"]
            for src in ("BMRK", "ARTS", "CFVS", "CSIR", "all"):
                ix = [i for i, s in enumerate(stems) if src == "all" or src_of(s) == src]
                line.append(f"{sname}/{src} AP {binned_ap(H[ix, 0, 0].sum(0), H[ix, 0, 1].sum(0)):.3f}")
        print(tag, " | ".join(line), flush=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
