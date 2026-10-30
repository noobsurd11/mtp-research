"""DDeP5 protocol 'free diagnostic' (descriptive): per decoder module, relative change ||theta_20k - theta_init|| / ||theta_init||
of trainable decoder parameters (BN running stats and counters excluded), A5c-f1 vs DDeP5, seeds 0-4. CPU only.
theta_init: DDeP5 = decoder_final.pth (what model.decoder_init loads); A5c-f1 = rebuilt as train.py does it
(torch.manual_seed(seed) immediately before build_model(cfg["model"]), train.py l.242-243; file loads draw no random numbers).
Check: the rebuilt encoder must equal the A5c-f1 ImageNet start (smp weights) bit for bit, i.e. the build path is the same.
Usage (gaint, cwd el_f2): python reports/f2/f2_decoder_change.py --out reports/f2/post_ddep5_decoder_change.json
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import torch

sys.path.insert(0, "/home/noob/work/el_f2")
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
a = ap.parse_args()
torch.set_num_threads(4)
DEC = "/home/noob/work/cv02_noob_el/el_f2/experiments/f2_ddep_pre_s0/decoder_final.pth"
ARMS = {"A5c-f1": "/home/noob/work/el_f1/experiments/f1_A_5pct_s{}", "DDeP5": "/home/noob/work/el_f2/experiments/f2_DDeP_5pct_s{}"}
skip = ("running_mean", "running_var", "num_batches_tracked")


def module_of(k):
    p = k.split(".")
    return ".".join(p[:3]) if p[1] == "blocks" else ".".join(p[:2])


ddep_init = torch.load(DEC, map_location="cpu", weights_only=False)["models"]["model"]
res = {}
for arm, pat in ARMS.items():
    for s in range(5):
        run = Path(pat.format(s))
        st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
        assert int(st["step"]) == 20000, (run, st["step"])
        fin = st["models"]["model"]
        cfg = load_config(run / "config_used.yaml")
        mcfg = {k: v for k, v in cfg["model"].items() if k not in ("encoder_init", "decoder_init")}
        torch.manual_seed(int(cfg["seed"]))
        m = build_model(mcfg)
        built = m.state_dict()
        src = built if arm == "A5c-f1" else ddep_init
        init = {k: v for k, v in src.items() if k.startswith("decoder.")}
        num, den = defaultdict(float), defaultdict(float)
        for k, v0 in init.items():
            if k.endswith(skip):
                continue
            d = (fin[k].float() - v0.float()).pow(2).sum().item(); n = v0.float().pow(2).sum().item()
            num[module_of(k)] += d; den[module_of(k)] += n; num["ALL"] += d; den["ALL"] += n
        res[f"{arm}_s{s}"] = {mod: (num[mod] ** 0.5) / max(den[mod] ** 0.5, 1e-12) for mod in sorted(num)}
        print(arm, s, f"ALL {res[f'{arm}_s{s}']['ALL']:.4f}", flush=True)
        del m, st, fin, built
# build-path check: the rebuilt ImageNet encoder for seed 0 equals the encoder smp builds for any seed (weights loaded, no RNG)
torch.manual_seed(0); e0 = {k: v for k, v in build_model(mcfg).state_dict().items() if k.startswith("encoder.")}
torch.manual_seed(3); e3 = {k: v for k, v in build_model(mcfg).state_dict().items() if k.startswith("encoder.")}
same_enc = all(torch.equal(e0[k], e3[k]) for k in e0)
torch.manual_seed(0); d0 = build_model(mcfg).state_dict(); torch.manual_seed(0); d0b = build_model(mcfg).state_dict()
rebuild_det = all(torch.equal(d0[k], d0b[k]) for k in d0 if k.startswith("decoder."))
mods = [m for m in res["A5c-f1_s0"] if m != "ALL"] + ["ALL"]
summ = {}
for mod in mods:
    A = [res[f"A5c-f1_s{s}"][mod] for s in range(5)]; D = [res[f"DDeP5_s{s}"][mod] for s in range(5)]
    summ[mod] = {"A5c-f1": sum(A) / 5, "DDeP5": sum(D) / 5}
    print(f"{mod:28s} A5c-f1 {sum(A) / 5:.4f}  DDeP5 {sum(D) / 5:.4f}")
print("checks: ImageNet encoder identical across seeds:", same_enc, "| decoder rebuild deterministic:", rebuild_det)
json.dump({"per_run": res, "mean": summ, "checks": {"encoder_same_across_seeds": same_enc, "rebuild_deterministic": rebuild_det},
           "theta_init": {"DDeP5": DEC, "A5c-f1": "torch.manual_seed(seed); build_model(cfg.model) (train.py l.242-243)"}},
          open(a.out, "w"), indent=1)
