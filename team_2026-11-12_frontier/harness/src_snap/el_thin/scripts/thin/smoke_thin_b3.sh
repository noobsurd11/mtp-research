#!/bin/bash
# builder -> runner: GPU smokes for the thin worktree (el_thin, branch thin), one job at a time, every start through runner's
# shared gate (el_f3/reports/pf2/scripts/gpu_gate.sh: one flock for all GPU starts, free >= peak + 2,048 MiB, >= 120 s
# since the last start by anyone, HOLD honoured). rc is captured before $(date). Outputs: reports/thin/smoke/.
#
#   S0  GPU identity: flags off, SUP100-PF opts s0, 2,000 steps, val off; step + "PF encoder lr=" lines up to step 2,000
#       vs el_f3/experiments/f3_SUPPF_100pct_s0.stdout (protocol_PF2 s7: >= 2,000 steps for the shared baseline)
#   S1  Skeleton Recall (w 1):        SUP100-PF s0, 2,000 steps
#   S2  clDice (w 1, k 10):           SUP100-PF s0, 2,000 steps
#   S3  B3 scuff class:               SUP100-PF s0, 2,000 steps, val at 1,000 / 2,000 (exercises scuff -> bg), then
#                                     scripts/b3/scuff_train_iou.py on the 2k checkpoint (12 train scuff cells)
#   S4  scoring only: m0_audit_b3.py (no B3 flags) on f3_SUPPF_100pct_s0 vs the opening-1 m0 JSON (m0_audit.py at e544133):
#       cells must be identical; then --ext-scuff / --test-scuff on f3_SUPPF_100pct_s0 (E1 crack-on-scuff, descriptive)
#       and on cv02_noob_el p6_L3_100pct_s0 (cross-check vs the 27 Oct figure: results/e1/raw_v2 crack_pred_on_ignored
#       total 8,812 for that run, cv02 scorer)
# S1-S3 report: peak max_memory_reserved (latest.pth at step 2,000, trainer state), per-process nvidia-smi every 5 s,
# steps/s from the step lines, loss finite, the "thin" term lines (S1, S2), val lines (S3).
# Runs use --exit_after_step 2000 (latest.pth is written at 2,000 first): rc 3 on the "trained" line is the planned exit.
# Usage: bash scripts/thin/smoke_thin_b3.sh S0 S1 S2 S3 S4   (env: GATE_TRAIN default 9000, GATE_THIN default 10000,
#        GATE_SCORE default 7154; runner may override)
set -u
cd /home/noob/work/el_thin
export CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1
source /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
P=/home/noob/work/el-fault-detection/.venv/bin/python
O=reports/thin/smoke; mkdir -p $O; L=$O/smoke.log
GATE_TRAIN=${GATE_TRAIN:-9000}; GATE_THIN=${GATE_THIN:-10000}; GATE_SCORE=${GATE_SCORE:-7154}
[ "$(git rev-parse --short HEAD)" = "$(cat reports/thin/DEPLOY 2>/dev/null)" ] && [ -z "$(git status --short --untracked-files=no)" ] \
  || { echo "[$(date)] deploy check FAIL (HEAD != reports/thin/DEPLOY or tracked changes)" >> $L; exit 1; }
B="seed=0 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
VAL="training.val_every=20000"
F1=/home/noob/work/el_f1/reports/f1
memlog(){ while kill -0 "$1" 2>/dev/null; do
  echo "$(date +%T) $(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr '\n' ' ')" >> "$2"; sleep 5; done; }
train(){ # name gate opts...
  local n=$1 g=$2 pid rc; shift 2
  gate_wait "$g" "thin-smoke $n"
  echo "[$(date)] start $n (gate $g)" >> $L
  $P scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 2000 --opts "$@" run_name=$n \
    > experiments/$n.stdout 2>&1 &
  pid=$!; echo "$pid $n $(date +%T)" >> $O/pids.txt
  memlog $pid $O/$n.gpumem.txt
  wait $pid; rc=$?
  echo "[$(date)] trained $n rc=$rc" >> $L
  $P - experiments/$n $O/$n.gpumem.txt $pid >> $L 2>&1 <<'PY'
import re, sys, torch
run, mem, pid = sys.argv[1:4]
st = torch.load(f"{run}/checkpoints/latest.pth", map_location="cpu", weights_only=False)
tr = st.get("trainer", st)
peak = {k: tr.get(k) for k in ("peak_alloc", "peak_reserved")} if isinstance(tr, dict) else {}
smi = [int(m.group(1)) for l in open(mem) for m in re.finditer(rf"\b{pid}, (\d+)", l)]
log = open(f"{run}.stdout").read()
sps = re.findall(r"step (\d+)/20000 .*?loss=(\S+).*?steps_per_sec=(\S+)", log)
thin = re.findall(r"thin (.*) at step (\d+)", log)
print(f"  {run.split('/')[-1]}: step {st.get('step')} | peak GiB {peak} | nvidia-smi max {max(smi) if smi else 'n/a'} MiB"
      f" | steps/s at {sps[-1][0] if sps else '-'}: {sps[-1][2] if sps else '-'} | last loss {sps[-1][1] if sps else '-'}"
      f" | finite {all(x[1] not in ('nan', 'inf') for x in sps)} | thin lines {len(thin)} last {thin[-1] if thin else '-'}")
PY
}
for s in "$@"; do case $s in
  S0) train thin_s0_idchk "$GATE_TRAIN" $B $PF $VAL
      $P - /home/noob/work/el_f3/experiments/f3_SUPPF_100pct_s0.stdout experiments/thin_s0_idchk.stdout $O >> $L 2>&1 <<'PY'
import re, sys
def lines(f):  # step and PF lines up to step 2,000, timestamps and steps_per_sec stripped
    out = []
    for l in open(f):
        m = re.search(r"(step (\d+)/20000 .*)$", l) or re.search(r"(PF encoder lr=\S+ at step (\d+))$", l.rstrip())
        if m and int(m.group(2)) <= 2000:
            out.append(re.sub(r"\s+steps_per_sec=\S+", "", m.group(1)).rstrip())
    return out
a, b = lines(sys.argv[1]), lines(sys.argv[2])
open(sys.argv[3] + "/S0_ref.lines", "w").write("\n".join(a) + "\n"); open(sys.argv[3] + "/S0_thin.lines", "w").write("\n".join(b) + "\n")
print("S0 identity to step 2,000:", "IDENTICAL" if a == b and len(a) == 80 else "DIFFER", f"({len(a)} ref lines, {len(b)} thin lines)")
PY
      ;;
  S1) train thin_s1_srec "$GATE_THIN" $B $PF $VAL loss.skel_recall.weight=1.0;;
  S2) train thin_s2_cldice "$GATE_THIN" $B $PF $VAL loss.cldice.weight=1.0 loss.cldice.iters=10;;
  S3) train thin_s3_b3 "$GATE_TRAIN" $B $PF training.val_every=1000 data.scuff_class=24 model.num_classes=25 \
        data.mask_subdir=labeled/masks_escdd_s
      grep -E "val @ step" experiments/thin_s3_b3.stdout | sed -E 's/^[0-9-]+ [0-9:,]+ //' >> $L
      gate_wait "$GATE_SCORE" "thin-smoke S3 scuff_train_iou"
      $P scripts/b3/scuff_train_iou.py --run experiments/thin_s3_b3 --out $O/S3_scuff_train_iou.json > $O/S3_scuff_train_iou.log 2>&1
      rc=$?; echo "[$(date)] S3 scuff_train_iou rc=$rc: $(tail -1 $O/S3_scuff_train_iou.log | cut -c1-300)" >> $L;;
  S4) R=/home/noob/work/el_f3/experiments/f3_SUPPF_100pct_s0; R6=/home/noob/work/cv02_noob_el/el_p6/experiments/p6_L3_100pct_s0
      gate_wait "$GATE_SCORE" "thin-smoke S4 m0 identity"
      $P scripts/b3/m0_audit_b3.py --code /home/noob/work/el_thin --out $O/S4_m0 --ext $F1/ext117 --no-logits --runs $R > $O/S4_m0.log 2>&1
      rc=$?; echo "[$(date)] S4 m0_audit_b3 (no B3 flags) rc=$rc" >> $L
      $P - $O/S4_m0/f3_SUPPF_100pct_s0.json /home/noob/work/el_f3/reports/f100/post_opening1/m0/f3_SUPPF_100pct_s0.json >> $L 2>&1 <<'PY'
import json, sys
a, b = (json.load(open(f)) for f in sys.argv[1:3])
print("S4 m0 cells identical to opening-1 m0_audit.py:", a["cells"] == b["cells"], "| sets", sorted(a["cells"]), "| step", a["step"], b["step"])
PY
      gate_wait "$GATE_SCORE" "thin-smoke S4 m0 scuff"
      $P scripts/b3/m0_audit_b3.py --code /home/noob/work/el_thin --out $O/S4_m0_scuff --ext $F1/ext117 --no-logits \
        --ext-scuff data/ext_scuff --test-scuff data/test_scuff --runs $R $R6 > $O/S4_m0_scuff.log 2>&1
      rc=$?; echo "[$(date)] S4 m0_audit_b3 (--ext-scuff, --test-scuff) rc=$rc" >> $L
      $P - $O/S4_m0_scuff >> $L 2>&1 <<'PY'
import json, sys
for run, ref in (("f3_SUPPF_100pct_s0", None), ("p6_L3_100pct_s0", 8812)):
    r = json.load(open(f"{sys.argv[1]}/{run}.json"))
    sc = [c["scuff"] for c in r["cells"]["ext"].values()]
    tot = {k: sum(x[k] for x in sc) for k in sc[0]}
    print(f"S4 {run}: E1 (n {len(sc)})", tot, "| 27 Oct cv02 crack_pred_on_ignored", ref, "| test_noscuff cells",
          len(r["cells"].get("test_noscuff", {})))
PY
      ;;
  *) echo "unknown smoke $s" >> $L;;
esac; done
echo "[$(date)] smokes done: $*" >> $L
