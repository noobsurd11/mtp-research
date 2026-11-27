"""c3x: writes bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml and its cv02 variant from the HRNet card text (run in a
tree of 852ed5c). Every change is one literal line replacement; the test file proves the equalities."""
import sys
from pathlib import Path
R = Path(sys.argv[1])
hr = (R / "bench/methods/hrnet_w18_unetpp_pf_v11.yaml").read_text().splitlines()
assert hr[17] == "name: hrnet_w18_unetpp_pf_v11" and all(l.startswith("#") for l in hr[:17])
head = """# c3x (lead's rulings C1 to C6, 17 Nov 2026): HRNet-W18 U-Net++ with swad_const = the rows2 row hrnet_w18_unetpp_pf_v11 plus
# exactly the changes that swad_const_pf_v11 makes to house_r34_unetpp_pf_v11: the 8 opts after training.encoder_pf.wd=0
# (constant lr after warm-up, a uniform average of every iterate of steps 10,000 to 20,000, an EMA 0.9998 averager, BN
# re-estimate on the training fold at the end, the encoder probe every 2,000 steps), weights_key swad_bn and the 6 readouts.
# Primary readout swad_bn (the weights_key); declared secondary readout swad (cv02 queue: 10th job field 'swad').
# The encoder probe logs one stage, 'model' (timm tensor names encoder.model.*), not layer1 to layer4; it is a log only.
# Proof (tests/test_bench_c3x_card.py): the non-comment diff of this card against hrnet_w18_unetpp_pf_v11 equals that of
# swad_const_pf_v11 against house_r34_unetpp_pf_v11 (the descriptive keys name, papers, memory, diff_ref, notes are checked
# one by one), and the rendered config differs from an HRNet run's only in the 8 keys.
# The header of hrnet_w18_unetpp_pf_v11 follows unchanged ('Card =' and 'deviations' there describe the HRNet row itself).""".splitlines()
EIGHT = ["  - training.lr_scheduler=constant", "  - training.weight_avg.swad.mode=uniform",
         "  - training.weight_avg.swad.start=10000", "  - training.weight_avg.swad.end=20000",
         "  - training.weight_avg.ema_9998.mode=ema", "  - training.weight_avg.ema_9998.decay=0.9998",
         "  - training.bn_recal=true", "  - training.enc_probe_every=2000"]
RO = ["weights_key: swad_bn", "readouts:", "  - {name: raw, weights_key: model}", "  - {name: raw_bn, weights_key: raw_bn}",
      "  - {name: swad, weights_key: swad}", "  - {name: swad_bn, weights_key: swad_bn}",
      "  - {name: ema_9998, weights_key: ema_9998}", "  - {name: ema_9998_bn, weights_key: ema_9998_bn}"]
SRC = ('  source: "peak not measured on a GPU when the card was written. Gate 11,000 = the gate of swad_const_pf_v11 (the lowest '
       'job gate the queues accept for this card; basis: HRNet PF peak on cv02 8,432 MiB, cv02 gpumem logs, card smoke 8,430; '
       'swad_const added 294 MiB to the PF peak on cv02, 5,736 -> 6,030, and 324 on gaint, 6,830 -> 7,154; expected cv02 '
       'peak about 8,760, + 2,048 = 10,808 <= 11,000). Job gate of the c3x lines (lead\'s ruling of 17 Nov 2026 17:35): '
       'max(11,000, P + 2,048), P = the highest gaint peak of this card over the memory smoke and the path smoke; smoke pass '
       'criterion: P minus the gaint peak of hrnet_w18_unetpp_pf_v11 at most 1,024 MiB, else nothing is armed before the '
       'lead has looked"')
NOTES = ('notes: "c3x: hrnet_w18_unetpp_pf_v11 plus the changes of swad_const_pf_v11 (constant lr, swad 10k to 20k, ema_9998, '
         'bn_recal, encoder probe). readouts: model (constant-lr raw), raw_bn, swad, swad_bn (primary), ema_9998, ema_9998_bn. '
         'Encoder drift: train.log ENC probe lines and enc_probe.jsonl (one stage, model)."')
REPL = {"name: hrnet_w18_unetpp_pf_v11": ["name: hrnet_w18_unetpp_swad_const_pf_v11"],
        "papers: [arXiv:1908.07919]": ['papers: [arXiv:1908.07919, "arXiv:2102.08604", "arXiv:2411.18704"]'],
        "  - training.encoder_pf.wd=0": ["  - training.encoder_pf.wd=0"] + EIGHT,
        "weights_key: model": RO, "  peak_mib: 8430": ["  peak_mib: null"], "  gate_mib: 10478": ["  gate_mib: 11000"],
        "diff_ref: house_r34_unetpp_pf_v11": ["diff_ref: hrnet_w18_unetpp_pf_v11"]}
out, used = head + hr[:17], set()
for l in hr[17:]:
    if l in REPL:
        out += REPL[l]; used.add(l)
    elif l.startswith("  source: "):
        out.append(SRC); used.add("source")
    elif l.startswith("notes: "):
        out.append(NOTES); used.add("notes")
    else:
        out.append(l)
assert len(used) == len(REPL) + 2, used
t = "\n".join(out) + "\n"
(R / "bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml").write_text(t)
a, b = "  - path: /home/noob/.cache/huggingface/hub/", "  - path: /tmp/noob_el/cache/hf/hub/"
assert t.count(a) == 1
(R / "bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml").write_text(t.replace(a, b))
print("written", len(out), "lines")
