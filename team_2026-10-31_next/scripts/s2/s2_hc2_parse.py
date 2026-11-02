"""runner (2 Nov 2026): summary line for one HC2 GPU check (s2_hc2_check.sh). Args: run_dir gpumem_txt pid.
Reads ONLY step lines, 'synth window' / 'synth inactive' lines, the 'synth_halfcut_ignore_inactive' startup line and the Traceback count
from the check's stdout (hard exit at step 1,000, before any TEST block); never prints anything else of it."""
import re
import sys

run, mem, pid = sys.argv[1:4]
smi = [int(m.group(1)) for line in open(mem) for m in re.finditer(rf"\b{pid}, (\d+)", line)]
fr = [int(m.group(1)) for line in open(mem) for m in re.finditer(r"free (\d+)", line)]
steps, synth, inact, key, tb = [], [], [], [], 0
for line in open(f"{run}.stdout", errors="replace"):
    if "Traceback" in line:
        tb += 1
    m = re.search(r"step (\d+)/20000 .*?loss=(\S+)", line)
    if m:
        steps.append((int(m.group(1)), m.group(2)))
    elif "synth window:" in line:
        synth.append(line.split("synth window:", 1)[1].strip())
    elif "synth inactive:" in line:
        inact.append(line.split("synth inactive:", 1)[1].strip())
    elif "synth_halfcut_ignore_inactive: on" in line:
        key.append(line.split("—", 1)[-1].strip()[:160])
fin = all(x[1] not in ("nan", "inf", "-inf") for x in steps)
out = (f"  {run.split('/')[-1]}: last step {steps[-1][0] if steps else '-'} | losses {[x[1] for x in steps][::4]} | finite {fin} | "
       f"Traceback {tb} | nvidia-smi max {max(smi) if smi else '-'} MiB | min free {min(fr) if fr else '-'} MiB | startup key line: "
       f"{key[0] if key else 'NONE'}")
m = re.search(r"total: made (\d+) eligible_not_drawn (\d+) not_eligible (\d+)", synth[-1]) if synth else None
if m:
    a, b, c = map(int, m.groups()); n = a + b + c
    out += (f" | synth lines {len(synth)}; total made {a} / eligible_not_drawn {b} / not_eligible {c} of {n}: share {a / n:.4f}, "
            f"eligible {(a + b) / n:.4f}, p_eff {a / max(a + b, 1):.4f}")
else:
    out += f" | synth lines {len(synth)}; total line not parsed"
m = re.search(r"total: excluded (\d+) .*?synthetic_inactive_px (\d+) synthetic_ignored_px (\d+) \(share of synthetic px ([0-9.]+)\)", inact[-1]) if inact else None
if m:
    out += (f" | synth inactive lines {len(inact)}; total excluded {m.group(1)}, synthetic_inactive_px {m.group(2)}, synthetic_ignored_px "
            f"{m.group(3)}, ignored share of synthetic px {m.group(4)}")
else:
    out += f" | synth inactive lines {len(inact)}; total line not parsed: {inact[-1][:200] if inact else 'NONE'}"
print(out)
