#!/bin/bash
# gaint (RTX PRO 4500): P13 replication lanes (protocols/P13_cutmix_separate_bn.md), worktree el_p13 at bac5264.
# Lane A starts when P12 lane 2 has finished (p12_gA_10pct_s1 rescored); lane B when P12 lane 1 has (p12_gA_10pct_s2).
# So gaint never runs more than two jobs. Each run also waits for < 20,000 MiB GPU memory used.
# Lane A: gCsM5 s3 s4 s5. Lane B: gDs5 s3 s4 s5.
cd /home/noob/work/el_p13
mkdir -p reports/p13 experiments
SSL="training.total_steps=20000 data.split_seed=0 data.labeled_fraction=0.05 training.labeled_batch_size=8 training.unlabeled_batch_size=8 data.mask_subdir=labeled/masks_escdd data.augmentation=labelsafe loss.t_pos=0.95 ssl.lambda_final=1.0 ssl.warmup_steps=2000 ssl.ramp_steps=2000 model.name=smp_unetpp loss.supervised=ce_dice ssl.labeled_aug=supervised ssl.student_forward=separate loss.consistency=tolerant_pl loss.tolerance_radius=2"
LA="p13_gCsM_5pct_s3|seed=3 $SSL ssl.cutmix_p=0.5;p13_gCsM_5pct_s4|seed=4 $SSL ssl.cutmix_p=0.5;p13_gCsM_5pct_s5|seed=5 $SSL ssl.cutmix_p=0.5"
LB="p13_gDs_5pct_s3|seed=3 $SSL ssl.lambda_final=0.0;p13_gDs_5pct_s4|seed=4 $SSL ssl.lambda_final=0.0;p13_gDs_5pct_s5|seed=5 $SSL ssl.lambda_final=0.0"
tmux has-session -t "=p13g" 2>/dev/null && { echo "session p13g exists; abort"; exit 1; }
cat > reports/p13/lane.sh <<'EOS'
#!/bin/bash
# lane.sh "<wait-for line in P12 log>" "<name|opts;...>": train + rescore each run in turn.
cd /home/noob/work/el_p13; PY=/home/noob/work/el-fault-detection/.venv/bin/python; L=reports/p13/launch_gaint.log
export CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=4
until grep -q "$1" /home/noob/work/el-fault-detection/reports/p12/launch_gaint.log; do sleep 60; done
IFS=';' read -ra RUNS <<< "$2"
for r in "${RUNS[@]}"; do
  IFS='|' read -r nm opts <<< "$r"
  [ -e experiments/$nm ] && { echo "[$(date)] skip $nm (exists)" >> $L; continue; }
  until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0)" -lt 20000 ]; do sleep 60; done
  echo "[$(date)] start $nm" >> $L
  $PY -u scripts/train.py --overwrite --config configs/ssl_mean_teacher.yaml --opts $opts run_name=$nm > experiments/$nm.stdout 2>&1
  echo "[$(date)] trained $nm rc=$?" >> $L
  $PY scripts/rescore_label_versions.py --runs $nm --out reports/p13/$nm.json > experiments/$nm.rescore.log 2>&1
  echo "[$(date)] rescored $nm rc=$?" >> $L
  sleep 30
done
EOS
tmux new-session -d -s p13g -n ctl "bash"
tmux new-window -d -t "=p13g:" -n laneA "bash reports/p13/lane.sh \"rescored p12_gA_10pct_s1\" \"$LA\"; exec bash"
tmux new-window -d -t "=p13g:" -n laneB "bash reports/p13/lane.sh \"rescored p12_gA_10pct_s2\" \"$LB\"; exec bash"
tmux list-windows -t "=p13g"
