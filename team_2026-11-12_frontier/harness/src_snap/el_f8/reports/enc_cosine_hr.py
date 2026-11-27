"""F8: encoder weight cosine per backbone stage for hrstem_unetpp checkpoints (ConvNeXt or SAM2 Hiera), the PF validity
check of protocol_A8screen.md §3 (stages 2-3 cosine to init >= 0.5). Like reports/enc_cosine.py (ResNet stages), per weight
tensor with dim >= 2 under encoder.*: cosine(A, B) flattened, stage mean; plus the stage norm ratio ||B|| / ||A||.
1-D tensors are classified by their OWNING MODULE TYPE (builder review of 063f74f0), not by name: every LayerNorm /
LayerNorm2d weight (incl. ConvNeXt's stem.1 and stages.{1,2,3}.downsample.0, which have no "norm" in the name) is reported
per stage as cos_ln; ConvNeXt layer-scale gammas (a parameter of the block itself) as cos_gamma; with counts.
The module map comes from building the timm backbone (--backbone, no weights) and pruning it exactly as hrstem_unetpp does.
Inputs: files holding {"models": {"model": state_dict}} (latest.pth) or a plain state dict (the step-0 init dump).
Usage: python enc_cosine_hr.py --backbone convnext_tiny --pair LABEL A.pth B.pth [--pair ...] [--hiera-stage-ends 0 2 9 11] [--out f.json]
"""
import argparse
import json
import re
from collections import defaultdict

import torch

ap = argparse.ArgumentParser()
ap.add_argument("--backbone", required=True, help="timm name, e.g. convnext_tiny or sam2_hiera_tiny")
ap.add_argument("--pair", nargs=3, action="append", required=True, metavar=("LABEL", "A", "B"))
ap.add_argument("--hiera-stage-ends", nargs=4, type=int, default=[0, 2, 9, 11])
ap.add_argument("--out")
a = ap.parse_args()


def module_kinds(backbone):
    """param name (encoder.*) -> 'ln' | 'gamma' | 'other1d' for 1-D tensors, from the owning module's type."""
    import timm
    m = timm.create_model(backbone, pretrained=False, num_classes=0, in_chans=1)
    m.prune_intermediate_layers(indices=(0, 1, 2, 3), prune_norm=True, prune_head=True)
    if hasattr(m, "head"):
        m.head = torch.nn.Identity()
    kinds = {}
    for mname, mod in m.named_modules():
        for pname, p in mod.named_parameters(recurse=False):
            if p.dim() != 1:
                continue
            full = f"encoder.{mname}.{pname}" if mname else f"encoder.{pname}"
            if "LayerNorm" in type(mod).__name__ or isinstance(mod, torch.nn.LayerNorm):
                kinds[full] = "ln" if pname == "weight" else "ln_bias"
            elif pname == "gamma":
                kinds[full] = "gamma"
            else:
                kinds[full] = "other1d"
    return kinds


KIND = module_kinds(a.backbone)


def sd_of(p):
    st = torch.load(p, map_location="cpu", weights_only=False)
    sd = st["models"]["model"] if isinstance(st, dict) and "models" in st else st
    return {k: v.float() for k, v in sd.items() if k.startswith("encoder.") and v.is_floating_point()}


def stage(k):
    m = re.match(r"encoder\.stages\.(\d+)\.", k)
    if m:
        return f"stage{m.group(1)}"
    if k.startswith("encoder.stem.") or k.startswith("encoder.patch_embed.") or k.startswith("encoder.pos_embed"):
        return "stem"
    m = re.match(r"encoder\.blocks\.(\d+)\.", k)
    if m:
        b = int(m.group(1)); ends = a.hiera_stage_ends
        return f"stage{next(i for i, e in enumerate(ends) if b <= e)}"
    return "other"


res = {}
for lab, pa, pb in a.pair:
    A, B = sd_of(pa), sd_of(pb)
    ks = sorted(set(A) & set(B)); assert ks and len(ks) == len(A) == len(B), (lab, len(A), len(B))
    cw, cl, cg, na, nb, n1 = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(float), defaultdict(float), defaultdict(int)
    for k in ks:
        x, y = A[k].flatten(), B[k].flatten(); s = stage(k)
        c = float(torch.nn.functional.cosine_similarity(x, y, dim=0))
        if A[k].dim() >= 2:
            cw[s].append(c); na[s] += float(x.pow(2).sum()); nb[s] += float(y.pow(2).sum())
        else:
            kind = KIND.get(k, "unknown"); n1[kind] += 1
            if kind == "ln":
                cl[s].append(c)
            elif kind == "gamma":
                cg[s].append(c)
    mean = lambda v: round(sum(v) / len(v), 4) if v else None
    res[lab] = {"stages": {s: {"cos_w": mean(v), "n_w": len(v), "norm_ratio": round((nb[s] / na[s]) ** 0.5, 4),
                               "cos_ln": mean(cl[s]), "n_ln": len(cl[s]), "cos_gamma": mean(cg[s]), "n_gamma": len(cg[s])}
                           for s, v in sorted(cw.items())},
                "n_1d_by_kind": dict(n1)}
    assert n1.get("unknown", 0) == 0, ("1-D encoder tensors without a module map entry", n1)
    print(lab, json.dumps(res[lab]))
if a.out:
    json.dump(res, open(a.out, "w"), indent=1)
