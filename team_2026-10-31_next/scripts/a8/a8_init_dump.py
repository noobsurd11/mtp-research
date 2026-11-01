"""a8_init_dump (runner DRAFT, 1 Nov 2026; protocol_A8screen §3 validity check, §9): the step-0 encoder reference that
el_f8 reports/enc_cosine_hr.py (d72f4324) needs as its A file, one per screen run. NEEDS coach's review before use.
Builds the model from the run's own config_used.yaml through el_f8's build_model (= the training init path: the
backbone_weights file is loaded; the 1-channel stem is the RGB sum), then checks that every encoder.* tensor equals the
weights file (stem: file stem summed over RGB, max|d| <= 1e-6; every other tensor exact), and saves
{"models": {"model": state_dict}, "step": 0} (the house step-0 format of pf2_rn50_cpucheck.py).
CPU only (CUDA hidden). Reads config_used.yaml and the weights file only: no image, no mask, no checkpoint.
Usage: python -B a8_init_dump.py --code /home/noob/work/el_f8 --run RUN_DIR --out INIT.pth
"""
import argparse
import hashlib
import os
import sys

import torch

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--run", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
assert os.environ.get("CUDA_VISIBLE_DEVICES") == "", "CPU only: CUDA hidden"
sys.path.insert(0, a.code)
from src.models.hrstem_unetpp import torchvision_convnext_to_timm  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

cfg = load_config(os.path.join(a.run, "config_used.yaml"))
mc = dict(cfg["model"])
assert mc["name"] == "hrstem_unetpp", mc["name"]
w, fmt = mc["backbone_weights"], mc.get("backbone_weights_format", "timm")
torch.manual_seed(int(cfg["seed"]))  # decoder / stem init only; encoder.* comes from the file
sd = build_model(mc).state_dict()
if fmt == "timm":
    from safetensors.torch import load_file
    ref = load_file(w)
elif fmt == "torchvision_convnext":
    ref = torchvision_convnext_to_timm(torch.load(w, map_location="cpu", weights_only=True))
else:
    raise SystemExit(f"unknown backbone_weights_format {fmt}")
enc = {k[len("encoder."):]: v for k, v in sd.items() if k.startswith("encoder.")}
assert enc and set(enc) <= set(ref), ("encoder keys not in the weights file", sorted(set(enc) - set(ref))[:5])
d_stem, d_other = 0.0, 0.0
for k, v in enc.items():
    r = ref[k].float()
    if k == "stem.0.weight" and r.shape[1] != v.shape[1]:
        r = r.sum(1, keepdim=True)
    assert r.shape == v.shape, (k, tuple(r.shape), tuple(v.shape))
    d = float((v.float() - r).abs().max())
    if k == "stem.0.weight":
        d_stem = d
    else:
        d_other = max(d_other, d)
assert d_stem <= 1e-6 and d_other == 0.0, ("init != weights file", d_stem, d_other)
md5 = hashlib.md5(open(w, "rb").read()).hexdigest()
torch.save({"models": {"model": sd}, "step": 0}, a.out)
print(f"init {a.run}: backbone {mc['backbone']} format {fmt} weights {w} md5 {md5}; encoder tensors {len(enc)} "
      f"(file keys unused: {len(set(ref) - set(enc))}); max|d| stem {d_stem:.2e} other {d_other:.2e} -> {a.out}", flush=True)
