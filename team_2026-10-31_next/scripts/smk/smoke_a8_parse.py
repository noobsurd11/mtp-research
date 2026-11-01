"""runner: summary line for one A8 / A8c smoke (smoke_a8.sh). Args: run_dir gpumem_txt pid."""
import re
import sys

import torch

run, mem, pid = sys.argv[1:4]
try:
    st = torch.load(f"{run}/checkpoints/latest.pth", map_location="cpu", weights_only=False)
    tr = st["trainer"]
    step, pr, pa = st.get("step"), tr.get("peak_reserved"), tr.get("peak_alloc")
except Exception as e:  # noqa: BLE001
    step = pr = pa = f"n/a ({e.__class__.__name__})"
smi = [int(m.group(1)) for line in open(mem) for m in re.finditer(rf"\b{pid}, (\d+)", line)]
fr = [int(m.group(1)) for line in open(mem) for m in re.finditer(r"free (\d+)", line)]
log = open(f"{run}.stdout").read()
sps = re.findall(r"(\d\d:\d\d:\d\d) INFO .*?step (\d+)/4000 .*?loss=(\S+).*?steps_per_sec=(\S+)", log)
inst = "-"
if len(sps) >= 3:  # steady rate from the last two log windows (timestamps), after the frozen-encoder phase
    t = [int(h) * 3600 + int(m) * 60 + int(s) for h, m, s in (x[0].split(":") for x in sps[-3:])]
    inst = f"{(int(sps[-1][1]) - int(sps[-3][1])) / max(t[2] - t[0], 1):.2f}"
print(f"  {run.split('/')[-1]}: step {step} | peak_reserved GiB {pr} | peak_alloc GiB {pa} | nvidia-smi max "
      f"{max(smi) if smi else '-'} MiB | min free {min(fr) if fr else '-'} MiB | steps/s cumulative at "
      f"{sps[-1][1] if sps else '-'}: {sps[-1][3] if sps else '-'}, last 100 steps {inst} | losses "
      f"{[x[2] for x in sps]} | finite {all(x[2] not in ('nan', 'inf') for x in sps)} | Traceback {log.count('Traceback')}")
