"""runner (2 Nov 2026): summary line for one SKR2 / HC2 smoke (s2_smoke.sh). Args: arm run_dir gpumem_txt pid.
Reads ONLY step lines, 'thin ... at step' lines (SKR01), 'synth window' lines (HC2) and the Traceback count from the smoke stdout
(the smoke hard-exits at step 1,000 before any TEST block); never prints anything else of it."""
import re
import sys

arm, run, mem, pid = sys.argv[1:5]
smi = [int(m.group(1)) for line in open(mem) for m in re.finditer(rf"\b{pid}, (\d+)", line)]
fr = [int(m.group(1)) for line in open(mem) for m in re.finditer(r"free (\d+)", line)]
steps, thin, synth, tb = [], [], [], 0
for line in open(f"{run}.stdout", errors="replace"):
    if "Traceback" in line:
        tb += 1
    m = re.search(r"step (\d+)/20000 .*?loss=(\S+).*?steps_per_sec=(\S+)", line)
    if m:
        steps.append((int(m.group(1)), m.group(2), m.group(3)))
    elif re.search(r"\bthin .* at step \d+", line):
        thin.append(line.split("INFO", 1)[-1].strip())
    elif "synth window:" in line:
        synth.append(line.split("synth window:", 1)[1].strip())
fin = all(x[1] not in ("nan", "inf", "-inf") for x in steps)
out = (f"  {run.split('/')[-1]}: last step {steps[-1][0] if steps else '-'} | losses {[x[1] for x in steps][::4]} | finite {fin} | "
       f"Traceback {tb} | steps/s cumulative {steps[-1][2] if steps else '-'} | nvidia-smi max {max(smi) if smi else '-'} MiB | "
       f"min free {min(fr) if fr else '-'} MiB")
if arm == "SKR01":
    out += f" | thin lines {len(thin)}; last: {thin[-1][:160] if thin else 'NONE'}"
if arm == "HC2":
    m = re.search(r"total: made (\d+) eligible_not_drawn (\d+) not_eligible (\d+)", synth[-1]) if synth else None
    if m:
        a, b, c = map(int, m.groups()); n = a + b + c
        out += f" | synth lines {len(synth)}; total made {a} / eligible_not_drawn {b} / not_eligible {c} of {n}: share {a / n:.4f}, eligible {(a + b) / n:.4f}"
    else:
        out += f" | synth lines {len(synth)}; total line not parsed: {synth[-1][:160] if synth else 'NONE'}"
print(out)
