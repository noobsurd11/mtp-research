#!/bin/bash
# w2b builder: mechanics test of the layered_ci dump path on a TRAINED core (CPU only, nice 19, 8 threads; numbers are
# not results). Why: a 5-step checkpoint fails the writer check of c57508e itself (E 18:55: the c57508e bench_infer on a
# 5-step PF smoke model: "pred disagrees ... at 1 px"; cause found: classes 7 and 5 with logits 6e-8 apart and equal
# float32 softmax, so pred = argmax(logits) = 7 but oth = argmax(log p) = 5 while m_crack = -0.80; the check's tie
# tolerance looks at |m_crack| only). Trained models do not hit it (W1-G / wave 2a GPU dumps, the CPU dump identity).
# Shim run (in IO only): config = the layered_ci card rendered on cv5v2_v11_f0, checkpoints/latest.pth = {step 20000,
# models: {model: W1-G w1g_pf_v11_f0_s5's weights + the aux head as AuxHeadModel initialises it at seed 5}}.
# Checks: (1) the shim's argmax24 dump equals the plain PF dump of the same W1-G checkpoint array for array (the aux head
# changes nothing on the softmax path); (2) layered_ci_replace and layered_ci_union dumps pass the writer check on read,
# carry p_inact_softmax (= the plain dump's p_inact) and p_inact = sigmoid(layer), and keep every cell's crack px equal
# to the argmax dump's; manifest decision_rule / decision_t_I. Everything written under IO/shim is removed at the end.
# Usage: bash layered_dump_shim_test.sh <new code archive dir> <out log>
set -u
NEW=${1:?code dir}; LOG=${2:?log}
IO=/home/noob/work/bench_w2b_io/shim; [ -e $IO ] && { echo "refuse: $IO exists"; exit 1; }
P=/home/noob/work/el-fault-detection/.venv/bin/python
W1=/home/noob/work/el_bench/experiments/w1g_pf_v11_f0_s5; R0=/home/noob/work/bench_data/roots/cv5v2_v11_f0
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
lg(){ echo "[$(date '+%F %T')] $*" | tee -a $LOG; }
mkdir -p $IO/run/shim_lci_f0_s5/checkpoints
cd $NEW || exit 1
$P -m bench.cards render bench/methods/layered_ci_pf_v11.yaml --seed 5 --run-name shim_lci_f0_s5 --data-root $R0 > $IO/run/shim_lci_f0_s5/config_used.yaml
nice -n 19 $P - $W1/checkpoints/latest.pth $IO/run/shim_lci_f0_s5 <<'PYEOF' 2>&1 | tee -a $LOG
import sys, torch, yaml
from src.models.model_factory import build_model
src, out = sys.argv[1], sys.argv[2]
cfg = yaml.safe_load(open(f"{out}/config_used.yaml"))
mc = dict(cfg["model"]); mc["encoder_weights"] = None
torch.manual_seed(5)
m = build_model(mc)
st = torch.load(src, map_location="cpu", weights_only=False)
assert int(st["step"]) == 20000
sd = m.state_dict()
miss = m.load_state_dict({**st["models"]["model"], **{k: v for k, v in sd.items() if k.startswith("aux_heads.")}})
torch.save({"step": 20000, "models": {"model": m.state_dict()}}, f"{out}/checkpoints/latest.pth")
print(f"shim checkpoint: PF core keys {len(st['models']['model'])} + aux keys {sum(k.startswith('aux_heads.') for k in sd)}; load {miss}")
PYEOF
for dec in argmax24 card layered_ci_union; do
  nice -n 19 $P scripts/bench_infer.py --run $IO/run/shim_lci_f0_s5 --set cv5v2_f0 --dumps $IO/d --method layered_ci_pf_v11 --card bench/methods/layered_ci_pf_v11.yaml --decision $dec --device cpu --precision fp32 --threads 8 --workers 2 > $IO/dump_$dec.log 2>&1
  lg "shim dump $dec rc=$?: $(grep -o 'dumped .*cells.*s ->' $IO/dump_$dec.log | head -1) tracebacks $(grep -c Traceback $IO/dump_$dec.log)"
done
nice -n 19 $P scripts/bench_infer.py --run $W1 --set cv5v2_f0 --dumps $IO/pf --method house_r34_unetpp_pf_v11 --card bench/methods/house_r34_unetpp_pf_v11.yaml --device cpu --precision fp32 --threads 8 --workers 2 > $IO/dump_pf.log 2>&1
lg "plain PF dump of the same W1-G checkpoint rc=$?: $(grep -o 'dumped .*cells' $IO/dump_pf.log | head -1)"
D=$IO/d/elbench1/layered_ci_pf_v11
ARRAYS_ONLY=1 $P /home/noob/work/bench_w2b_io/dump_compare.py $D/shim_lci_f0_s5.argmax24/cv5v2_f0 $IO/pf/elbench1/house_r34_unetpp_pf_v11/w1g_pf_v11_f0_s5/cv5v2_f0 $NEW > $IO/cmp.txt 2>&1
lg "(1) shim argmax24 dump vs plain PF dump rc=$?: $(cat $IO/cmp.txt)"
nice -n 19 $P - $D $IO/pf/elbench1/house_r34_unetpp_pf_v11/w1g_pf_v11_f0_s5/cv5v2_f0 <<'PYEOF' 2>&1 | tee -a $LOG
import json, sys
from pathlib import Path
import numpy as np, torch
from bench import dumpfmt
D, PF = Path(sys.argv[1]), Path(sys.argv[2])
base = D / "shim_lci_f0_s5.argmax24" / "cv5v2_f0"
out = []
for rid, rule in (("shim_lci_f0_s5", "layered_ci_replace"), ("shim_lci_f0_s5.layered_ci_union", "layered_ci_union")):
    d = D / rid / "cv5v2_f0"
    man = json.loads((d / "manifest.json").read_text())
    assert man["decision_rule"] == rule and man["decision_t_I"] == 0.5, man["decision_rule"]
    n = crack_eq = sm_eq = moved = layer_px = 0
    for f in sorted(d.glob("*.npz")):
        c = dumpfmt.read_cell(f)                                   # writer check on read
        a = dumpfmt.read_cell(base / f.name); p = dumpfmt.read_cell(PF / f.name)
        n += 1
        crack_eq += int(np.array_equal(c["pred"] == 14, a["pred"] == 14))
        sm_eq += int(np.array_equal(c["p_inact_softmax"], p["p_inact"]))
        moved += int((c["pred"] != a["pred"]).sum()); layer_px += int((c["p_inact"].astype(np.float32) > 0.5).sum())
    out.append(f"(2) {rule}: {n} cells pass the writer check; crack px equal to argmax24 in {crack_eq}/{n}; "
               f"p_inact_softmax = plain p_inact in {sm_eq}/{n}; px changed by the rule {moved}; layer px {layer_px}")
print("\n".join(out))
PYEOF
lg "shim test done; removing $IO"
rm -rf $IO
