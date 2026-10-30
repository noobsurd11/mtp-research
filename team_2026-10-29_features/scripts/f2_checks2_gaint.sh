#!/bin/bash
# f2 checks, part 2 (replaces the tail of f2_checks_gaint.sh, whose bash was stopped at 18:4x IST while its I1-f2
# python child kept running): finish I1-f2's comparison, run the cp lambda-0 identity, release the A-lane hold, then
# defer the CP smoke, decoy go/no-go, DDeP smoke and decoder_init smoke until all 10 MIM5-experiment runs are rescored
# (they do not gate anything before that). Gates: own peak + 2 GB free. Status: reports/f2/checks/status.txt.
set -u
cd /home/noob/work/el_f2
P=/home/noob/work/el-fault-detection/.venv/bin/python
OUT=/home/noob/work/el_f2/reports/f2/checks; S=$OUT/status.txt
L=/home/noob/work/el_f1/reports/f1g/launch.log
I1PID=${I1PID:?}
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
trap 'rm -f /home/noob/work/el_f1/reports/f1g/HOLD_A' EXIT   # never leave the A lane held
wfree(){ while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)" -lt "$1" ]; do sleep 30; done; }
OPTS="seed=0 data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
CP="cp.batch=4 cp.bg_pool_list=/home/noob/work/el_f1/reports/f1/mim_pool_v11.txt cp.heldout_list=/home/noob/work/el_f1/reports/f1/mim_monitor_v11.txt cp.bg_train_exclude=data/splits/d7_twin_train_cells.txt"
ext(){ grep -E "src.trainers.trainer — (step|val @)" $1 | sed -E "s/^[0-9-]+ [0-9:,]+ //; s/ +steps_per_sec=[0-9.]+//; s/  loss_cp=.*\$//"; }
idchk(){
  ext $1 > $OUT/$2.lines; n=$(wc -l < $OUT/$2.lines)
  ext /home/noob/work/el_f1/experiments/f1_A_5pct_s0.stdout | head -n $n > $OUT/$2.ref
  cmp -s $OUT/$2.lines $OUT/$2.ref && echo "[$(date)] $2 IDENTICAL ($n lines)" >> $S || echo "[$(date)] $2 DIFFER ($n lines)" >> $S; }
TR="$P scripts/train.py --config configs/supervised.yaml --overwrite"
echo "[$(date)] part 2 start (part 1 bash stopped; waiting for I1-f2 pid $I1PID)" >> $S
while kill -0 $I1PID 2>/dev/null; do sleep 20; done
grep -q "exit_after_step=2000 reached" $OUT/i1f2_A_s0.stdout && idchk $OUT/i1f2_A_s0.stdout I1f2_2000 || echo "[$(date)] I1-f2 did not reach step 2000" >> $S
wfree 9000; $TR --exit_after_step 1000 --opts $OPTS $CP cp.lambda=0 run_name=cp0_s0 logging.experiments_dir=$OUT > $OUT/cp0_s0.stdout 2>&1
idchk $OUT/cp0_s0.stdout CP_lambda0_1000
grep -h "CP: lambda" $OUT/cp0_s0.stdout | cut -c1-300 >> $S
rm -f /home/noob/work/el_f1/reports/f1g/HOLD_A; echo "[$(date)] HOLD_A released by f2 checks part 2" >> $L
echo "[$(date)] identity part done; deferring smokes until 10 MIM5-experiment runs are rescored" >> $S
until [ "$(grep -cE 'rescored f1_(A|MIM)_5pct_s[0-4] rc=0' $L)" -ge 10 ]; do sleep 120; done
wfree 12000; $TR --exit_after_step 2000 --opts $OPTS $CP cp.lambda=1 run_name=cpsmoke_s0 logging.experiments_dir=$OUT > $OUT/cpsmoke_s0.stdout 2>&1
echo "[$(date)] cp smoke: $(grep -c 'step [0-9]*/20000' $OUT/cpsmoke_s0.stdout) log lines, last: $(grep 'step [0-9]*/20000' $OUT/cpsmoke_s0.stdout | tail -1 | cut -c1-400)" >> $S
wfree 5000; $P scripts/cp_decoy.py --runs $OUT/i1f2_A_s0 $OUT/cpsmoke_s0 --out $OUT/decoy_2k.json > $OUT/decoy_2k.log 2>&1
tail -3 $OUT/decoy_2k.log >> $S
wfree 10000; $P scripts/pretrain_ddep.py --list /home/noob/work/el_f1/reports/f1/mim_pool_v11.txt \
  --monitor_list /home/noob/work/el_f1/reports/f1/mim_monitor_v11.txt --data_root data --out $OUT/ddep_smoke \
  --steps 40000 --batch 32 --crop 256 --gamma 0.95 --lr 1e-4 --warmup_steps 500 --clip 1.0 --max_steps 500 \
  --log_every 50 --monitor_every 250 > $OUT/ddep_smoke.stdout 2>&1
grep -E "step (50|250|500)/40000 ep|monitor|DDeP:" $OUT/ddep_smoke.stdout | cut -c40-260 >> $S
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
echo "[$(date)] ALLDONE" >> $S
