"""judge a8_cos_check (1 Nov 2026): encoder-validity cross-check for the A8 screen (protocol_A8screen §3, stages 2-3 cos >= 0.5).
Own code (torch only; no enc_cosine_hr / a8_init_dump / el_f8 import). CPU, reads checkpoints + weight files only.
1. step 4000 in every latest.pth; per-stage weight cosine 4k vs the scorer's init.pth (stage mean of per-tensor cos, dim >= 2,
   and the cosine of the concatenated stage vector);
2. arm-swap control: cos(A8 4k, A8c init) and cos(A8c 4k, A8 init) per stage (must be ~0 if the arms started from different files);
3. init.pth vs the weight files WITHOUT el_f8's remap: A8 = safetensors by key (stem summed over RGB);
   A8c = torchvision file matched by exact flattened values (stem summed over RGB).
Usage: python -B a8_cos_check.py OUT.txt
"""
import sys
from collections import defaultdict

import torch
from safetensors.torch import load_file

V1 = "/home/noob/work/a8_score/v1"; EX = "/home/noob/work/el_f8/experiments"
RUNS = {"A8": ["f8_A8_4k_s0", "f8_A8_4k_s1"], "A8c": ["f8_A8c_4k_s0", "f8_A8c_4k_s1"]}
DINO = "/home/noob/work/weights/dinov3_convnext_tiny_lvd1689m_timm.safetensors"
TV = "/home/noob/.cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth"
out = open(sys.argv[1], "w")


def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.write(s + "\n"); out.flush()


def enc(sd):
    return {k[len("encoder."):]: v.float() for k, v in sd.items() if k.startswith("encoder.")}


def stage(k):
    if k.startswith("stem."):
        return "stem"
    if k.startswith("stages."):
        return "stage" + k.split(".")[1]
    return "other"


def cos_table(A, B):
    per, cat = defaultdict(list), defaultdict(lambda: [0.0, 0.0, 0.0])
    for k, a in A.items():
        if a.dim() < 2:
            continue
        b = B[k]; x, y = a.flatten().double(), b.flatten().double()
        per[stage(k)].append(float(x @ y / (x.norm() * y.norm())))
        c = cat[stage(k)]; c[0] += float(x @ y); c[1] += float(x @ x); c[2] += float(y @ y)
    return {s: (sum(v) / len(v), cat[s][0] / (cat[s][1] * cat[s][2]) ** 0.5, len(v)) for s, v in sorted(per.items())}


init, k4 = {}, {}
for arm, rs in RUNS.items():
    for r in rs:
        st = torch.load(f"{EX}/{r}/checkpoints/latest.pth", map_location="cpu", weights_only=False)
        say(f"{r}: latest.pth step {st.get('step')}")
        assert int(st["step"]) == 4000
        k4[r] = enc(st["models"]["model"]); del st
        init[r] = enc(torch.load(f"{V1}/work/init/{r}.init.pth", map_location="cpu", weights_only=False)["models"]["model"])
        t = cos_table(init[r], k4[r])
        say(f"  4k vs own init: " + "; ".join(f"{s} mean {m:.4f} cat {c:.4f} (n {n})" for s, (m, c, n) in t.items()))
        say(f"  validity (stage2 & stage3 mean >= 0.5): {'PASS' if t['stage2'][0] >= 0.5 and t['stage3'][0] >= 0.5 else 'FAIL'}")

say("== arm-swap control (4k of one arm vs the init of the other arm)")
for a, b in (("f8_A8_4k_s0", "f8_A8c_4k_s0"), ("f8_A8c_4k_s0", "f8_A8_4k_s0")):
    t = cos_table(init[b], k4[a])
    say(f"{a} 4k vs {b} init: " + "; ".join(f"{s} {m:.4f}" for s, (m, c, n) in t.items()))
t = cos_table(init["f8_A8_4k_s0"], init["f8_A8c_4k_s0"])
say("A8 init vs A8c init: " + "; ".join(f"{s} {m:.4f}" for s, (m, c, n) in t.items()))
same_init = all(torch.equal(init["f8_A8_4k_s0"][k], init["f8_A8_4k_s1"][k]) for k in init["f8_A8_4k_s0"]) and \
    all(torch.equal(init["f8_A8c_4k_s0"][k], init["f8_A8c_4k_s1"][k]) for k in init["f8_A8c_4k_s0"])
say(f"encoder init identical across seeds within each arm: {same_init}")

say("== init vs weight files (no el_f8 remap)")
dz = load_file(DINO); A = init["f8_A8_4k_s0"]; bad = 0; mx = 0.0
for k, v in A.items():
    r = dz[k].float()
    if k == "stem.0.weight" and r.shape[1] != v.shape[1]:
        r = r.sum(1, keepdim=True)
    d = float((r - v).abs().max()); mx = max(mx, d); bad += d > 1e-6
say(f"A8 init vs DINOv3 safetensors by key: tensors {len(A)} max|d| {mx:.2e} mismatches {bad}")
tv = torch.load(TV, map_location="cpu", weights_only=True)
pool = defaultdict(list)
for k, v in tv.items():
    f = v.float().flatten(); pool[f.numel()].append((k, f))
C = init["f8_A8c_4k_s0"]; hit = 0; miss = []
for k, v in C.items():
    f = v.flatten()
    if k == "stem.0.weight":
        src = tv["features.0.0.weight"].float()
        ok = src.shape[1] == 3 and torch.allclose(src.sum(1, keepdim=True).flatten(), f, atol=1e-6)
    else:
        ok = any(torch.equal(f, g) for _, g in pool[f.numel()])
    hit += ok
    if not ok:
        miss.append(k)
say(f"A8c init vs torchvision file by exact values: matched {hit}/{len(C)}; unmatched {miss[:6]}")
say("DONE")
