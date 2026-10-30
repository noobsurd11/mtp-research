#!/bin/bash
# F1 / MIM5 on gaint (only with team-lead's OK). tmux session =f1g, one window per lane, chained, never racing:
#   pre : MIM pretraining (batch 32, args reports/f1/mim_args_gaint.txt) -> experiments/f1_mim_pre_s0
#   A   : A5c-f1 s0..s4 one after another (starts with pre; the comparator does not need the encoder)
#   M1  : waits for encoder_final.md5 (md5 -c), runs gate F2 (200-step fine-tune smoke with encoder_final.pth: the
#         "Encoder initialised" md5 must equal encoder_final.md5, losses finite), writes reports/f1g/F2_PASS, then
#         MIM5 s0, s2, s4
#   M2  : waits for reports/f1g/F2_PASS, then MIM5 s1, s3
# Each run: train (--overwrite only if experiments/<run> is absent), then read-only rescore if rc = 0; rc captured
# before $(date). Logs: reports/f1g/launch.log. Memory: pre about 16 GB + 1 fine-tune 5.7 GB + finllm 5.9 GB; after
# pre, 3 fine-tunes about 17 GB. A lane waits while the GPU has < 7,000 MiB free before each run (user jobs first).
set -u
cd /home/noob/work/el_f1
S=f1g; R=reports/f1; L=reports/$S/launch.log
mkdir -p reports/$S experiments
P=/home/noob/work/el-fault-detection/.venv/bin/python
ENC=/home/noob/work/el_f1/experiments/f1_mim_pre_s0/encoder_final.pth
cat > reports/$S/run_one.sh <<'EOS'
#!/bin/bash
# run_one.sh <run name> <seed> <extra opts...>: wait for >= 7,000 MiB free, train, rescore
set -u
cd /home/noob/work/el_f1
S=f1g; L=reports/$S/launch.log; P=/home/noob/work/el-fault-detection/.venv/bin/python
name=$1; k=$2; shift 2
[ -e experiments/$name ] && { echo "[$(date)] skip $name (exists)" >> $L; exit 0; }
while :; do
  free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)
  [ "$free" -ge 7000 ] && break; sleep 60
done
echo "[$(date)] start $name (free $free MiB)" >> $L
HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --opts \
  seed=$k data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 \
  data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice \
  "$@" run_name=$name > experiments/$name.stdout 2>&1
rc=$?; echo "[$(date)] trained $name rc=$rc" >> $L
if [ $rc -eq 0 ]; then
  $P scripts/rescore_label_versions.py --runs $name --out reports/$S/$name.json > experiments/$name.rescore.log 2>&1
  rc2=$?; echo "[$(date)] rescored $name rc=$rc2" >> $L
fi
EOS
chmod +x reports/$S/run_one.sh
MIMARGS=$(grep -v '^#' $R/mim_args_gaint.txt | tr '\n' ' ')
tmux has-session -t "=$S" 2>/dev/null && { echo "session $S exists; abort"; exit 1; }
tmux new-session -d -s $S -n ctl "bash"
tmux new-window -d -t "=$S:" -n pre "cd /home/noob/work/el_f1; echo \"[\$(date)] start pretrain\" >> $L; HF_HUB_OFFLINE=1 OMP_NUM_THREADS=8 $P -u scripts/pretrain_mim.py --list $R/mim_pool_v11.txt --monitor_list $R/mim_monitor_v11.txt --data_root data --out experiments/f1_mim_pre_s0 $MIMARGS > experiments/f1_mim_pre_s0.stdout 2>&1; echo \"[\$(date)] pretrain rc=\$?\" >> $L; exec bash"
sleep 120  # pretraining loads images and allocates before the A lane checks free memory
tmux new-window -d -t "=$S:" -n A "for k in 0 1 2 3 4; do bash reports/$S/run_one.sh f1_A_5pct_s\$k \$k; done; exec bash"
WAIT="until [ -s experiments/f1_mim_pre_s0/encoder_final.md5 ]; do sleep 120; done; (cd experiments/f1_mim_pre_s0 && md5sum -c encoder_final.md5) >> $L 2>&1 || exit 1"
cat > reports/$S/f2_gate.sh <<'EOS'
#!/bin/bash
# F2: 200-step fine-tune smoke with encoder_final.pth (A5c opts, seed 0) into reports/f1g/f2; pass = md5 match + finite
set -u
cd /home/noob/work/el_f1
S=f1g; L=reports/$S/launch.log; P=/home/noob/work/el-fault-detection/.venv/bin/python
ENC=/home/noob/work/el_f1/experiments/f1_mim_pre_s0/encoder_final.pth
HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --exit_after_step 200 --config configs/supervised.yaml --opts \
  seed=0 data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 \
  data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice \
  model.encoder_init=$ENC run_name=f2_smoke logging.experiments_dir=reports/$S/f2 > reports/$S/f2_smoke.stdout 2>&1
want=$(cut -d" " -f1 experiments/f1_mim_pre_s0/encoder_final.md5)
got=$(grep -o "Encoder initialised from .*md5 [0-9a-f]*" reports/$S/f2_smoke.stdout | grep -o "[0-9a-f]\{32\}$")
nl=$(grep -c "step [0-9]*/20000  loss=" reports/$S/f2_smoke.stdout); bad=$(grep -E "step [0-9]+/20000  loss=" reports/$S/f2_smoke.stdout | grep -ciE "loss=(nan|inf)")
echo "[$(date)] F2 want $want got $got loss lines $nl nonfinite $bad" >> $L
if [ -n "$got" ] && [ "$want" = "$got" ] && [ "$nl" -ge 4 ] && [ "$bad" -eq 0 ]; then touch reports/$S/F2_PASS; echo "[$(date)] F2 PASS" >> $L; else echo "[$(date)] F2 FAIL" >> $L; exit 1; fi
EOS
chmod +x reports/$S/f2_gate.sh
tmux new-window -d -t "=$S:" -n M1 "cd /home/noob/work/el_f1; $WAIT; bash reports/$S/f2_gate.sh || exit 1; for k in 0 2 4; do bash reports/$S/run_one.sh f1_MIM_5pct_s\$k \$k model.encoder_init=$ENC; done; exec bash"
tmux new-window -d -t "=$S:" -n M2 "cd /home/noob/work/el_f1; until [ -e reports/$S/F2_PASS ]; do sleep 120; done; sleep 90; for k in 1 3; do bash reports/$S/run_one.sh f1_MIM_5pct_s\$k \$k model.encoder_init=$ENC; done; exec bash"
tmux list-windows -t "=$S"
