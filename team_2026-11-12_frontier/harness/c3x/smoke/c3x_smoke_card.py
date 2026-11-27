"""c3x PATH smoke (rulings C5 b, Q4 and the lead's Q2 ruling of 17 Nov): writes the smoke card = the c3x card with six values
changed in place, so that one 600-step run has the order of events of the real run: encoder unfrozen (step 100) and ramped
(to step 200) before the first encoder-probe call (step 200) and before the averaging window starts (step 300), then the BN
re-estimate and the final save with all readouts (step 600). Nothing else changes (bench.cards diff: exactly these 6 keys).
  training.total_steps 20000 -> 600, training.enc_probe_every 2000 -> 200,
  training.weight_avg.swad.start 10000 -> 300, training.weight_avg.swad.end 20000 -> 600 (window = the second half, as in the card),
  training.encoder_pf.freeze 1000 -> 100, training.encoder_pf.ramp 1000 -> 100 (lead's Q2 ruling: the probe sees a moving encoder)
  name -> smoke_c3x_hrnet_swad_path (= file stem; the card lives outside the repo and is passed to bench_q.sh by path)
  memory.source (the 17:35 gate rule) and notes say what it is; gate 11000 as the card.
Usage: python c3x_smoke_card.py <c3x card yaml> <out yaml>   (refuses an existing output)
"""
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
if out.exists():
    sys.exit(f"REFUSED: {out} exists")
t = src.read_text().splitlines()
REPL = {"name: hrnet_w18_unetpp_swad_const_pf_v11": "name: smoke_c3x_hrnet_swad_path",
        "  - training.total_steps=20000": "  - training.total_steps=600",
        "  - training.enc_probe_every=2000": "  - training.enc_probe_every=200",
        "  - training.weight_avg.swad.start=10000": "  - training.weight_avg.swad.start=300",
        "  - training.weight_avg.swad.end=20000": "  - training.weight_avg.swad.end=600",
        "  - training.encoder_pf.freeze=1000": "  - training.encoder_pf.freeze=100",
        "  - training.encoder_pf.ramp=1000": "  - training.encoder_pf.ramp=100"}
o, used = ["# c3x PATH smoke card (not in the repo): the c3x card with total_steps 600, enc_probe_every 200, swad window 300 to "
           "600, encoder_pf freeze 100 and ramp 100; written by c3x_smoke_card.py."], set()
for l in t:
    if l in REPL:
        o.append(REPL[l]); used.add(l)
    elif l.startswith("  source: "):
        o.append('  source: "smoke card: gate as the c3x card (11000). Its gaint peak enters P of the job gate rule (lead\'s ruling of 17 Nov '
                 '2026 17:35: job gate = max(11,000, P + 2,048), P = the highest peak of the c3x card over the memory and the path smoke)"'); used.add("s")
    elif l.startswith("notes: "):
        o.append('notes: "c3x PATH smoke only (ruling C5 b): 600 steps, probe every 200, swad 300 to 600, PF freeze 100 ramp 100; never a result."'); used.add("n")
    else:
        o.append(l)
assert len(used) == len(REPL) + 2, used
out.write_text("\n".join(o) + "\n")
print(f"wrote {out}")
