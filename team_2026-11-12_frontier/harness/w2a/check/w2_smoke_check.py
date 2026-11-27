"""w2 smoke check: raw-weight hashes of the 5-step CPU runs (models[model]) and checkpoint keys.
Prints IDENTICAL / DIFF and key names only (no metric)."""
import hashlib
import sys
from pathlib import Path

import torch

E = Path(sys.argv[1])
NAMES = ["w2s_pf_ref", "w2s_pf_new", "w2s_rcs", "w2s_sbj", "w2s_jmlh", "w2s_spd", "w2s_spd_ctrl", "w2s_ema", "w2s_swad"]


def ck(name):
    p = E / name / "checkpoints" / "latest.pth"
    return torch.load(p, map_location="cpu", weights_only=False) if p.exists() else None


def h(sd):
    m = hashlib.sha256()
    for k, v in sd.items():
        m.update(k.encode())
        m.update(v.detach().contiguous().numpy().tobytes())
    return m.hexdigest()[:16]


C = {n: ck(n) for n in NAMES}
for n, c in C.items():
    print(f"{n}: " + ("MISSING" if c is None else f"step {c['step']} models {sorted(c['models'])}"))
ref = C["w2s_pf_ref"]
for n, exp in [("w2s_pf_new", "IDENTICAL"), ("w2s_ema", "IDENTICAL"), ("w2s_spd", "IDENTICAL (encoder frozen 1k)"),
               ("w2s_spd_ctrl", "IDENTICAL (encoder frozen 1k)"), ("w2s_rcs", "DIFF (sampler)"),
               ("w2s_sbj", "DIFF (loss)"), ("w2s_jmlh", "DIFF (loss)"), ("w2s_swad", "any (constant lr)")]:
    if ref is not None and C[n] is not None:
        same = h(C[n]["models"]["model"]) == h(ref["models"]["model"])
        print(f"raw models[model] {n} vs w2s_pf_ref: {'IDENTICAL' if same else 'DIFF'} (expected {exp})")
