#!/bin/bash
# f2 identity runs and smokes on gaint (protocol_cp5 v1 checks 1-3, protocol_ddep5 v1 I1-f2 and smoke), deploy commit
# 2751aa8, in the gap after f1_A_5pct_s0 while the f1g A lane is held (reports/f1g/HOLD); releases HOLD at the end.
# Each step waits for its own peak + 2 GB free (team-lead rule: >= 2 GB free on gaint at all times). Results in reports/f2/checks/status.txt.
set -u
cd /home/noob/work/el_f2
P=/home/noob/work/el-fault-detection/.venv/bin/python
OUT=/home/noob/work/el_f2/reports/f2/checks; mkdir -p $OUT; S=$OUT/status.txt
L=/home/noob/work/el_f1/reports/f1g/launch.log
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
trap 'rm -f /home/noob/work/el_f1/reports/f1g/HOLD' EXIT   # never leave the A lane held
echo "[$(date)] start; commit $(git rev-parse --short HEAD); waiting for rescored f1_A_5pct_s0" >> $S
until grep -qE "rescored f1_A_5pct_s0|trained f1_A_5pct_s0 rc=[1-9]" $L; do sleep 60; done
wfree(){ while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)" -lt "$1" ]; do sleep 30; done; }
OPTS="seed=0 data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
CP="cp.batch=4 cp.bg_pool_list=/home/noob/work/el_f1/reports/f1/mim_pool_v11.txt cp.heldout_list=/home/noob/work/el_f1/reports/f1/mim_monitor_v11.txt cp.bg_train_exclude=data/splits/d7_twin_train_cells.txt"
ext(){ grep -E "src.trainers.trainer — (step|val @)" $1 | sed -E "s/^[0-9-]+ [0-9:,]+ //; s/ +steps_per_sec=[0-9.]+//; s/  loss_cp=.*\$//"; }
idchk(){ # $1 run stdout, $2 label: compare its step/val lines with the head of f1_A_5pct_s0's
  ext $1 > $OUT/$2.lines; n=$(wc -l < $OUT/$2.lines)
  ext /home/noob/work/el_f1/experiments/f1_A_5pct_s0.stdout | head -n $n > $OUT/$2.ref
  cmp -s $OUT/$2.lines $OUT/$2.ref && echo "[$(date)] $2 IDENTICAL ($n lines)" >> $S || echo "[$(date)] $2 DIFFER ($n lines)" >> $S; }
TR="$P scripts/train.py --config configs/supervised.yaml --overwrite"
# 1. I1-f2: no switch, 2,000 steps (also the A5c step-2k checkpoint for the decoy go/no-go)
wfree 9000; $TR --exit_after_step 2000 --opts $OPTS run_name=i1f2_A_s0 logging.experiments_dir=$OUT > $OUT/i1f2_A_s0.stdout 2>&1
idchk $OUT/i1f2_A_s0.stdout I1f2_2000
# 2. cp section at lambda 0, 1,000 steps
wfree 9000; $TR --exit_after_step 1000 --opts $OPTS $CP cp.lambda=0 run_name=cp0_s0 logging.experiments_dir=$OUT > $OUT/cp0_s0.stdout 2>&1
idchk $OUT/cp0_s0.stdout CP_lambda0_1000
grep -h "CP: lambda" $OUT/cp0_s0.stdout | cut -c1-300 >> $S
# 3. CP smoke at lambda 1, 2,000 steps
wfree 12000; $TR --exit_after_step 2000 --opts $OPTS $CP cp.lambda=1 run_name=cpsmoke_s0 logging.experiments_dir=$OUT > $OUT/cpsmoke_s0.stdout 2>&1
grep -h "peak" $OUT/cpsmoke_s0/metrics.json >/dev/null 2>&1; echo "[$(date)] cp smoke: $(grep -c 'step [0-9]*/20000' $OUT/cpsmoke_s0.stdout) log lines, last: $(grep 'step [0-9]*/20000' $OUT/cpsmoke_s0.stdout | tail -1 | cut -c1-400)" >> $S
# 4. decoy go/no-go at 2k: CP smoke vs A5c (I1-f2) step-2k checkpoints
wfree 5000; $P scripts/cp_decoy.py --runs $OUT/i1f2_A_s0 $OUT/cpsmoke_s0 --out $OUT/decoy_2k.json > $OUT/decoy_2k.log 2>&1
tail -3 $OUT/decoy_2k.log >> $S
# 5. DDeP pretraining smoke (real args, 500 steps) and a 200-step fine-tune with its decoder
wfree 10000; $P scripts/pretrain_ddep.py --list /home/noob/work/el_f1/reports/f1/mim_pool_v11.txt \
  --monitor_list /home/noob/work/el_f1/reports/f1/mim_monitor_v11.txt --data_root data --out $OUT/ddep_smoke \
  --steps 40000 --batch 32 --crop 256 --gamma 0.95 --lr 1e-4 --warmup_steps 500 --clip 1.0 --max_steps 500 \
  --log_every 50 --monitor_every 250 > $OUT/ddep_smoke.stdout 2>&1
grep -E "step (50|250|500)/|monitor|DDeP:" $OUT/ddep_smoke.stdout | cut -c40-260 >> $S
$P - <<'PY' >> $S 2>&1
import torch
st = torch.load("/home/noob/work/el_f2/reports/f2/checks/ddep_smoke/ckpt_latest.pth", map_location="cpu", weights_only=False)
sd = {"decoder." + k[len("net.decoder."):]: v for k, v in st["model"].items() if k.startswith("net.decoder.")}
torch.save({"models": {"model": sd}}, "/home/noob/work/el_f2/reports/f2/checks/ddep_smoke_dec500.pth")
print("ddep smoke decoder tensors", len(sd), "step", st["step"])
PY
wfree 9000; $TR --exit_after_step 200 --opts $OPTS model.decoder_init=$OUT/ddep_smoke_dec500.pth run_name=ddinit_s0 logging.experiments_dir=$OUT > $OUT/ddinit_s0.stdout 2>&1
grep -h "Decoder initialised" $OUT/ddinit_s0.stdout | cut -c1-250 >> $S
md5sum $OUT/ddep_smoke_dec500.pth >> $S
grep -E "step (50|200)/20000" $OUT/ddinit_s0.stdout | cut -c1-200 >> $S
echo "[$(date)] ALLDONE; releasing HOLD" >> $S
rm -f /home/noob/work/el_f1/reports/f1g/HOLD
