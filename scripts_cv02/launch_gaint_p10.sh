#!/bin/bash
# gaint (RTX PRO 4500): P10 supervised references A5 (L3, 5% labels) then A50 (L3, 50% labels), seeds 0-2, one tmux
# window per seed, chained. Reference-only (different hardware from cv02); P6 L3 options verbatim.
cd /home/noob/work/el-fault-detection
PY=/home/noob/work/el-fault-detection/.venv/bin/python
mkdir -p reports/p10 experiments
COMMON="training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd"
L3="model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
tmux has-session -t p10g 2>/dev/null && { echo "session p10g exists; abort"; exit 1; }
tmux new-session -d -s p10g -n ctl "bash"
for s in 0 1 2; do
  CMD="cd /home/noob/work/el-fault-detection; export CUDA_VISIBLE_DEVICES=0; for f in 0.05:5pct 0.5:50pct; do fr=\${f%%:*}; nm=p10_A_\${f##*:}_s$s; \
[ -e experiments/\$nm ] && continue; echo \"[\$(date)] start \$nm\" >> reports/p10/launch_gaint.log; \
$PY -u scripts/train.py --overwrite --config configs/supervised.yaml --opts seed=$s data.labeled_fraction=\$fr $COMMON $L3 run_name=\$nm > experiments/\$nm.stdout 2>&1; \
echo \"[\$(date)] trained \$nm rc=\$?\" >> reports/p10/launch_gaint.log; \
$PY scripts/rescore_label_versions.py --runs \$nm --out reports/p10/\$nm.json > experiments/\$nm.rescore.log 2>&1; \
echo \"[\$(date)] rescored \$nm rc=\$?\" >> reports/p10/launch_gaint.log; done; exec bash"
  tmux new-window -d -t p10g: -n "A_s$s" "bash -c '$CMD'"
  sleep 90
done
tmux list-windows -t p10g | wc -l
