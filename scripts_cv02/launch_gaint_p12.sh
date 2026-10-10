#!/bin/bash
# gaint (RTX PRO 4500): P12 replication lanes (protocols/P12_matched_5pct.md). Two sequential lanes in tmux session p12g;
# they start once all six P10 gaint references are rescored, and each run waits for < 20,000 MiB GPU memory used.
# Lane 1: gDm5 s3 s4 s5, gA10 s0 s2. Lane 2: gCm5 s3 s4 s5, gA10 s1. Code: repo HEAD 24590fb.
cd /home/noob/work/el-fault-detection
PY=/home/noob/work/el-fault-detection/.venv/bin/python
mkdir -p reports/p12 experiments
SSL="training.total_steps=20000 data.split_seed=0 data.labeled_fraction=0.05 training.labeled_batch_size=8 training.unlabeled_batch_size=8 data.mask_subdir=labeled/masks_escdd data.augmentation=labelsafe loss.t_pos=0.95 ssl.lambda_final=1.0 ssl.warmup_steps=2000 ssl.ramp_steps=2000 model.name=smp_unetpp loss.supervised=ce_dice loss.consistency=tolerant_pl loss.tolerance_radius=2"
SUP="data.labeled_fraction=0.1 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
L1="p12_gDm_5pct_s3|ssl_mean_teacher.yaml|seed=3 $SSL ssl.lambda_final=0.0 ssl.labeled_aug=supervised;p12_gDm_5pct_s4|ssl_mean_teacher.yaml|seed=4 $SSL ssl.lambda_final=0.0 ssl.labeled_aug=supervised;p12_gDm_5pct_s5|ssl_mean_teacher.yaml|seed=5 $SSL ssl.lambda_final=0.0 ssl.labeled_aug=supervised;p12_gA_10pct_s0|supervised.yaml|seed=0 $SUP;p12_gA_10pct_s2|supervised.yaml|seed=2 $SUP"
L2="p12_gCm_5pct_s3|ssl_mean_teacher.yaml|seed=3 $SSL ssl.labeled_aug=supervised;p12_gCm_5pct_s4|ssl_mean_teacher.yaml|seed=4 $SSL ssl.labeled_aug=supervised;p12_gCm_5pct_s5|ssl_mean_teacher.yaml|seed=5 $SSL ssl.labeled_aug=supervised;p12_gA_10pct_s1|supervised.yaml|seed=1 $SUP"
tmux has-session -t p12g 2>/dev/null && { echo "session p12g exists; abort"; exit 1; }
tmux new-session -d -s p12g -n ctl "bash"
cat > reports/p12/lane.sh <<'EOF'
#!/bin/bash
# lane.sh "<name|config|opts;...>": wait for the P10 references, then train + rescore each run in turn.
cd /home/noob/work/el-fault-detection; PY=.venv/bin/python; L=reports/p12/launch_gaint.log
export CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=4
until [ "$(grep -c rescored reports/p10/launch_gaint.log)" -ge 6 ]; do sleep 60; done
IFS=';' read -ra RUNS <<< "$1"
for r in "${RUNS[@]}"; do
  IFS='|' read -r nm cfg opts <<< "$r"
  [ -e experiments/$nm ] && { echo "[$(date)] skip $nm (exists)" >> $L; continue; }
  until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0)" -lt 20000 ]; do sleep 60; done
  echo "[$(date)] start $nm" >> $L
  $PY -u scripts/train.py --overwrite --config configs/$cfg --opts $opts run_name=$nm > experiments/$nm.stdout 2>&1
  echo "[$(date)] trained $nm rc=$?" >> $L
  $PY scripts/rescore_label_versions.py --runs $nm --out reports/p12/$nm.json > experiments/$nm.rescore.log 2>&1
  echo "[$(date)] rescored $nm rc=$?" >> $L
  sleep 30
done
EOF
tmux new-window -d -t p12g: -n lane1 "bash reports/p12/lane.sh \"$L1\"; exec bash"
sleep 120
tmux new-window -d -t p12g: -n lane2 "bash reports/p12/lane.sh \"$L2\"; exec bash"
tmux list-windows -t p12g
