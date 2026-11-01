"""p8_probe (found, 31 Oct 2026): idea 8 step 1, the frozen-encoder probe of protocol_A8screen.md §2 (descriptive; it only
picks which hierarchical candidates enter the PF screen and never closes the direction).

D1 recipe (scripts_cv02/trackD_probe.py) with these changes, all fixed in the protocol:
  - probe trained on all 478 train cells (masks_escdd), not the 23 5% cells;
  - eval sets: val (54) and Hanifi _rf (106; F51 / H36 / F19 from rf_sets.tsv md5 14771356; ignore px removed); NO test, NO E1;
  - encoders: cached IN R34 (smp-hub, house init), IN R50 (torchvision V2), IN ConvNeXt-T (torchvision V1), DINOv2-S/14;
    sanity rows SUP100-PF s0 / SUP100-g s0 encoders (house input normalisation); candidates from files: DINOv3 ConvNeXt-T,
    SAM2 Hiera-T, DINOv3 ViT-S/16 at 512 and 1024 px (an encoder whose file is absent is skipped and reported);
  - CNN / Hiera features: the stride-4 and stride-8 stages; ViT: blocks 2, 5, 8, 11 (one head each), stride 16 tokens.
Probe: one 1x1 conv head per feature map (bias on the first), bilinear to 512, summed; channel standardisation from the
train features; 24 classes, plain CE; Adam 1e-3, 2,000 steps, batch 8 with replacement, no augmentation; seeds 0 and 1.
Per cell: 1,000-bin p(crack) and p(inactive) histograms on GT-pos / GT-neg keep px; argmax crack / inactive tp, fp, fn;
max p(crack); crack px at argmax. Summary: crack AP per set, cell AUROC (max p vs >= 20 GT px), recall at matched
precision (P* = calib's SUPPF5 ensemble dump, argmax precision on that set), H36 crack-free false-alarm px, inactive AP,
and the pick rule (F51 crack AP, 2-seed mean >= best cached CNN reference - 0.02; if none, DINOv3 ConvNeXt-T enters).
CPU by default (CUDA_VISIBLE_DEVICES=""); --device cuda only when runner starts it behind its gate.
Usage: python p8_probe.py --code EL_F3 --out DIR [--encoders ...] [--steps 2000] [--smoke]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--code", default="/home/noob/work/el_f3")
ap.add_argument("--out", required=True)
ap.add_argument("--rf", default="/home/noob/work/calib/data/rf")
ap.add_argument("--rf-sets", default="/home/noob/work/found/t9/rf_sets.tsv")
ap.add_argument("--calib-dump", default="/home/noob/work/calib/out/dump", help="SUPPF5.{val,rf}.npz for the matched precision P*")
ap.add_argument("--weights", default="/home/noob/work/weights")
ap.add_argument("--encoders", nargs="+", default=["rn34_imagenet", "rn50_imagenet", "convnext_t_in1k", "dinov2_vits14",
                                                  "suppf_s0_enc", "sup_s0_enc", "dinov3_cnx_t", "sam2_hiera_t",
                                                  "dinov3_vits16_512", "dinov3_vits16_1024"])
ap.add_argument("--steps", type=int, default=2000)
ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1])
ap.add_argument("--device", default="cpu")
ap.add_argument("--threads", type=int, default=8)
ap.add_argument("--smoke", action="store_true", help="4 train cells, 20 steps, evaluated on 4 TRAIN cells only (no val / rf)")
a = ap.parse_args()
if a.device == "cpu":
    import os
    assert os.environ.get("CUDA_VISIBLE_DEVICES") == "", "CPU runs keep CUDA hidden"
torch.set_num_threads(a.threads)
DEV = torch.device(a.device)
CODE = Path(a.code); DATA = CODE / "data"; W = Path(a.weights); RF = Path(a.rf)
sys.path.insert(0, str(CODE))
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

CR, IN, C, BINS, SIZE = 14, 11, 24, 1000, 512
IMNET = (torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1), torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1))
FILES = {"dinov3_cnx_t": ["dinov3_convnext_tiny_lvd1689m_timm.safetensors", "dinov3_convnext_tiny_lvd1689m_meta.safetensors"],
         "dinov3_vits16": ["dinov3_vits16_lvd1689m_timm.safetensors", "dinov3_vits16_lvd1689m_meta.safetensors"],
         "sam2_hiera_t": ["timm_sam2_hiera_tiny_fb_r896.safetensors"]}
CNN_REFS = ("rn34_imagenet", "rn50_imagenet", "convnext_t_in1k")


def imnet(x):
    return (x.repeat(1, 3, 1, 1) - IMNET[0].to(x.device)) / IMNET[1].to(x.device)


def find(key):
    for f in FILES[key]:
        if (W / f).exists():
            return W / f
    return None


def build_encoder(name):
    """Returns (fn: x01 [B,1,512,512] -> list of feature maps, info dict) or (None, reason)."""
    import timm
    import torchvision
    tv = torchvision.models
    if name == "rn34_imagenet":  # the house init (smp-hub resnet34 imagenet, offline HF cache)
        import segmentation_models_pytorch as smp
        e = smp.encoders.get_encoder("resnet34", in_channels=3, depth=5, weights="imagenet").to(DEV).eval()
        return (lambda x: (lambda f: [f[2], f[3]])(e(imnet(x)))), {"src": "smp-hub resnet34.imagenet"}
    if name == "rn50_imagenet":
        m = tv.resnet50(weights=None); m.load_state_dict(torch.load(Path.home() / ".cache/torch/hub/checkpoints/resnet50-11ad3fa6.pth", map_location="cpu")); m = m.to(DEV).eval()

        def f(x):
            h = m.maxpool(m.relu(m.bn1(m.conv1(imnet(x))))); l1 = m.layer1(h)
            return [l1, m.layer2(l1)]
        return f, {"src": "torchvision resnet50-11ad3fa6 (IMAGENET1K_V2)"}
    if name == "convnext_t_in1k":
        m = tv.convnext_tiny(weights=None); m.load_state_dict(torch.load(Path.home() / ".cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth", map_location="cpu")); m = m.to(DEV).eval()

        def f(x):
            s0 = m.features[1](m.features[0](imnet(x)))
            return [s0, m.features[3](m.features[2](s0))]
        return f, {"src": "torchvision convnext_tiny-983f1562 (IMAGENET1K_V1)"}
    if name == "dinov2_vits14":
        hub = Path.home() / ".cache/torch/hub/facebookresearch_dinov2_main"
        m = torch.hub.load(str(hub), "dinov2_vits14", source="local").to(DEV).eval()

        def f(x):
            t = m.forward_features(F.interpolate(imnet(x), size=(518, 518), mode="bilinear", align_corners=False))["x_norm_patchtokens"]
            return [t.transpose(1, 2).reshape(t.shape[0], -1, 37, 37)]
        return f, {"src": "torch.hub dinov2_vits14 (cached)"}
    if name in ("suppf_s0_enc", "sup_s0_enc"):
        run = CODE / "experiments" / ("f3_SUPPF_100pct_s0" if name == "suppf_s0_enc" else "f3_SUP_100pct_s0")
        st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
        assert int(st.get("step", -1)) == 20000, run
        mc = {k: v for k, v in load_config(run / "config_used.yaml")["model"].items() if k not in ("encoder_init", "decoder_init")}; mc["encoder_weights"] = None
        m = build_model(mc); m.load_state_dict(st["models"]["model"]); m = m.to(DEV).eval()
        return (lambda x: (lambda e: [e[2], e[3]])(m.encoder((x - 0.5) / 0.25))), {"src": str(run), "step": 20000}
    if name in ("dinov3_cnx_t", "sam2_hiera_t"):
        p = find(name)
        if p is None:
            return None, "weights file absent"
        tname = "convnext_tiny.dinov3_lvd1689m" if name == "dinov3_cnx_t" else "sam2_hiera_tiny"
        m = timm.create_model(tname, pretrained=True, pretrained_cfg_overlay=dict(file=str(p)), num_classes=0).to(DEV).eval()
        return (lambda x: list(m.forward_intermediates(imnet(x), indices=(0, 1), intermediates_only=True))), {"src": str(p)}
    if name.startswith("dinov3_vits16_"):
        p = find("dinov3_vits16")
        if p is None:
            return None, "weights file absent"
        res = int(name.rsplit("_", 1)[1])
        m = timm.create_model("vit_small_patch16_dinov3.lvd1689m", pretrained=True, pretrained_cfg_overlay=dict(file=str(p)),
                              num_classes=0, dynamic_img_size=True).to(DEV).eval()

        def f(x):
            xi = imnet(x) if res == 512 else F.interpolate(imnet(x), size=(res, res), mode="bilinear", align_corners=False)
            return list(m.forward_intermediates(xi, indices=(2, 5, 8, 11), intermediates_only=True))
        return f, {"src": str(p), "input_px": res}
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


def binned_ap(pos, neg):
    tp, fp = np.cumsum(pos[::-1]).astype(float), np.cumsum(neg[::-1]).astype(float)
    P = np.where(tp + fp > 0, tp / np.maximum(tp + fp, 1), 0.0); R = tp / max(pos.sum(), 1)
    return float(np.sum(P * np.diff(np.concatenate([[0.0], R]))))


def auroc(pos, neg):
    if not pos or not neg:
        return float("nan")
    v = np.array(pos + neg); r = v.argsort().argsort() + 1.0
    _, inv, cnt = np.unique(v, return_inverse=True, return_counts=True); r = (np.bincount(inv, r) / cnt)[inv]
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def load_x(path):
    return torch.from_numpy(np.asarray(Image.open(path).convert("L"), dtype=np.float32) / 255.0)


# ---------------------------------------------------------------- cells
tr = sorted(l.strip() for l in open(DATA / "splits" / "train.txt") if l.strip())
val = sorted(l.strip() for l in open(DATA / "splits" / "val.txt") if l.strip())
assert len(tr) == 478 and len(val) == 54
rfrows = [l.rstrip("\n").split("\t") for l in open(a.rf_sets) if l.strip()][1:]
rfset = {r[0]: r[1] for r in rfrows}
assert len(rfset) == 106 and sorted(set(rfset.values())) == ["F19", "F51", "H36"]
MASK = DATA / "labeled" / "masks_escdd"
cells = {"val": [(s, DATA / "labeled" / "images" / f"{s}.png", np.array(Image.open(MASK / f"{s}.png")), None) for s in val],
         "rf": [(s, RF / "images" / f"{s}.png", np.array(Image.open(RF / "masks" / f"{s}.png")),
                 ~(np.array(Image.open(RF / "ignore" / f"{s}.png")) > 0)) for s in sorted(rfset)]}
if a.smoke:
    tr = tr[:4]; a.steps = 20; a.seeds = [0]
    cells = {"train_smoke": [(s, DATA / "labeled" / "images" / f"{s}.png", np.array(Image.open(MASK / f"{s}.png")), None) for s in tr]}
Ytr = torch.from_numpy(np.stack([np.array(Image.open(MASK / f"{s}.png")).astype(np.int64) for s in tr]))
Xtr = [load_x(DATA / "labeled" / "images" / f"{s}.png") for s in tr]
OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)


def p_star():
    """Matched-precision target per set: calib's SUPPF5 5-seed ensemble dump, argmax (margin > 0) pixel crack precision."""
    out = {}
    for sp, key in (("val", "val"), ("rf", "rf")):
        f = Path(a.calib_dump) / f"SUPPF5.{key}.npz"
        if not f.exists():
            continue
        z = np.load(f); st = [str(s) for s in z["stems"]]
        groups = {"val": [s for s in st]} if sp == "val" else {g: [s for s in st if rfset.get(s) == g] for g in ("F51", "H36", "F19")}
        cd = {c[0]: c for c in cells.get(sp, [])}
        for g, ss in groups.items():
            tp = pp = 0
            for s in ss:
                i = st.index(s); pred = z["margin"][i].astype(np.float32) > 0; gt = cd[s][2] == CR
                keep = cd[s][3] if cd[s][3] is not None else np.ones_like(gt)
                tp += int((pred & gt & keep).sum()); pp += int((pred & keep).sum())
            out[g] = tp / max(pp, 1)
    return out


PSTAR = {} if a.smoke else p_star()
results, meta = {}, {"encoders": {}, "p_star": PSTAR, "argv": sys.argv}
t0 = time.time()
for name in a.encoders:
    fn, info = build_encoder(name)
    if fn is None:
        meta["encoders"][name] = {"skipped": info}; print(f"{name}: SKIPPED ({info})", flush=True); continue
    t1 = time.time()
    with torch.no_grad():
        feats = None
        for i in range(0, len(tr), 4):
            fs = [t.float().half().cpu() for t in fn(torch.stack(Xtr[i:i + 4])[:, None].to(DEV))]
            feats = [[t] for t in fs] if feats is None else [o + [t] for o, t in zip(feats, fs)]
        feats = [torch.cat(o) for o in feats]
    dims = [f.shape[1] for f in feats]
    mus = [f.float().mean((0, 2, 3), keepdim=True).to(DEV) for f in feats]
    sds = [f.float().std((0, 2, 3), keepdim=True).clamp(min=1e-6).to(DEV) for f in feats]
    meta["encoders"][name] = {**info, "dims": dims, "feat_shapes": [list(f.shape[1:]) for f in feats], "seeds": {}}
    for seed in a.seeds:
        torch.manual_seed(seed)
        pr = Probe(dims, mus, sds).to(DEV); opt = torch.optim.Adam(pr.parameters(), lr=1e-3)
        g = torch.Generator().manual_seed(seed)
        for step in range(a.steps):
            idx = torch.randint(0, len(tr), (8,), generator=g)
            loss = F.cross_entropy(pr([f[idx].to(DEV) for f in feats]), Ytr[idx].to(DEV))
            opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        pr.eval(); tag = f"{name}/seed{seed}"; results[tag] = {}
        for sp, cs in cells.items():
            for s, ip, gt, keep in cs:
                with torch.no_grad():
                    sm = torch.softmax(pr(fn(load_x(ip)[None, None].to(DEV))).float(), 1)[0].cpu().numpy()
                k = np.ones(gt.shape, bool) if keep is None else keep
                pc, pi, pd = sm[CR], sm[IN], sm.argmax(0)
                rec = {"set": rfset.get(s, sp), "n_gt_crack": int(((gt == CR) & k).sum()), "max_pc": float(pc[k].max())}
                for cname, c, prob in (("crack", CR, pc), ("inactive", IN, pi)):
                    t, p = (gt == c) & k, (pd == c) & k
                    b = np.clip((prob * BINS).astype(int), 0, BINS - 1)
                    rec[cname] = {"tp": int((p & t).sum()), "fp": int((p & ~t).sum()), "fn": int((~p & t).sum()),
                                  "pos": np.bincount(b[t], minlength=BINS).tolist(), "neg": np.bincount(b[k & ~t], minlength=BINS).tolist()}
                results[tag][s] = rec
        meta["encoders"][name]["seeds"][seed] = {"final_train_loss": float(loss)}
        print(f"{tag} loss {float(loss):.4f} {time.time() - t1:.0f}s", flush=True)
    del feats


def summarize(tag, ss):
    R = [results[tag][s] for s in ss]
    if not R:
        return {}
    pos = np.sum([r["crack"]["pos"] for r in R], 0); neg = np.sum([r["crack"]["neg"] for r in R], 0)
    ipos = np.sum([r["inactive"]["pos"] for r in R], 0); ineg = np.sum([r["inactive"]["neg"] for r in R], 0)
    cp = [r["max_pc"] for r in R if r["n_gt_crack"] >= 20]; cn = [r["max_pc"] for r in R if r["n_gt_crack"] == 0]
    o = {"n": len(R), "crack_ap": binned_ap(pos, neg), "inactive_ap": binned_ap(ipos, ineg) if ipos.sum() else None,
         "cell_auroc": auroc(cp, cn), "fa_px_crackfree_argmax": int(sum(r["crack"]["tp"] + r["crack"]["fp"] for r in R if r["n_gt_crack"] == 0))}
    return o


def matched_recall(tag, ss, target):
    R = [results[tag][s] for s in ss]
    pos = np.sum([r["crack"]["pos"] for r in R], 0); neg = np.sum([r["crack"]["neg"] for r in R], 0)
    tp, fp = np.cumsum(pos[::-1])[::-1], np.cumsum(neg[::-1])[::-1]
    prec = np.where(tp + fp > 0, tp / np.maximum(tp + fp, 1), 0.0); ok = np.where(prec >= target)[0]
    return float(tp[ok.min()] / max(pos.sum(), 1)) if len(ok) else 0.0


summary = {}
for tag in results:
    groups = {}
    for s, r in results[tag].items():
        groups.setdefault(r["set"], []).append(s)
    summary[tag] = {g: summarize(tag, ss) for g, ss in groups.items()}
    for g, ss in groups.items():
        if g in PSTAR:
            summary[tag][g]["recall_at_pstar"] = matched_recall(tag, ss, PSTAR[g])
# pick rule (fixed in protocol_A8screen §2): F51 crack AP, 2-seed mean, >= best cached CNN reference - 0.02
mean_f51 = {}
for name in a.encoders:
    v = [summary[t]["F51"]["crack_ap"] for t in summary if t.startswith(name + "/") and "F51" in summary[t]]
    if v:
        mean_f51[name] = float(np.mean(v))
ref = max((mean_f51[n] for n in CNN_REFS if n in mean_f51), default=None)
cands = [n for n in ("dinov3_cnx_t", "sam2_hiera_t") if n in mean_f51]
pick = [n for n in cands if ref is not None and mean_f51[n] >= ref - 0.02]
if not pick:
    pick = ["dinov3_cnx_t"]  # Om's named encoder enters anyway (protocol §2)
meta.update({"f51_crack_ap_mean": mean_f51, "best_cached_cnn_ref": ref, "pick": pick, "seconds": round(time.time() - t0)})
np.savez_compressed(OUT / "percell_hists.npz", data=np.array(json.dumps(results)))
json.dump({"summary": summary, "meta": meta}, open(OUT / "p8_summary.json", "w"), indent=1)
print(json.dumps({"pick": pick, "f51_crack_ap_mean": mean_f51, "ref": ref}, indent=1))
