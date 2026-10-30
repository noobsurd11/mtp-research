"""Encoder conv-weight comparison per ResNet-34 stage (runner's independent re-derivation of coach_100.md §0; also the PF
smoke gate). For each pair (A, B): per conv weight tensor (4-D, encoder.*), cosine(A, B) flattened; per stage the mean
of the tensor cosines; plus the stage norm ratio ||B|| / ||A|| over the stage's concatenated conv weights.
Inputs are files holding {"models": {"model": state_dict}} (checkpoints/latest.pth, encoder_final.pth, mim_step0.pth).
Usage: python enc_cosine.py --pair LABEL A.pth B.pth [--pair ...] [--out f.json]
"""
import argparse
import json
from collections import defaultdict

import torch

ap = argparse.ArgumentParser()
ap.add_argument("--pair", nargs=3, action="append", required=True, metavar=("LABEL", "A", "B"))
ap.add_argument("--out")
a = ap.parse_args()
STAGES = ("conv1", "layer1", "layer2", "layer3", "layer4")
cache = {}


def load(p):
    if p not in cache:
        st = torch.load(p, map_location="cpu", weights_only=False)
        sd = st["models"]["model"]
        cache[p] = ({k: v.float() for k, v in sd.items() if k.startswith("encoder.") and v.dim() == 4}, st.get("step"))
    return cache[p]


res = {}
for lab, pa, pb in a.pair:
    (A, sa), (B, sb) = load(pa), load(pb)
    ks = sorted(set(A) & set(B))
    assert ks and len(ks) == len(A) == len(B), (lab, len(A), len(B), len(ks))
    cos, na, nb = defaultdict(list), defaultdict(float), defaultdict(float)
    for k in ks:
        st = k.split(".")[1]
        st = "conv1" if st == "conv1" else st
        if st not in STAGES:
            continue
        x, y = A[k].flatten(), B[k].flatten()
        cos[st].append(float(torch.nn.functional.cosine_similarity(x, y, 0)))
        na[st] += float(x.pow(2).sum()); nb[st] += float(y.pow(2).sum())
    res[lab] = {s: {"cos": sum(cos[s]) / len(cos[s]), "n_tensors": len(cos[s]), "norm_ratio": (nb[s] / na[s]) ** 0.5}
                for s in STAGES}
    res[lab]["steps"] = [sa, sb]
    print(f"{lab:44s} " + "  ".join(f"{s} {res[lab][s]['cos']:+.3f}/{res[lab][s]['norm_ratio']:.2f}" for s in STAGES)
          + f"  (steps {sa}, {sb})")
if a.out:
    json.dump(res, open(a.out, "w"), indent=1)
