#!/bin/bash
# AL1 launcher (cv02), from el_p17/launch_set_p17.sh: one tmux window per run in session <session>, train then
# read-only rescore (latest.pth = final step), per-image scores and histograms. Usage: launch_set_al1.sh <session> <spec>
# Spec: <run> <gpu> <config> <opts...> [EXIT=<step>]. A run whose experiments/<run> exists is skipped, never overwritten.
S=$1; SPEC=$2
cd /tmp/noob_el/el_alhvr
PY=/tmp/noob_el/el-fault-detection/.venv/bin/python
mkdir -p reports/$S experiments
tmux has-session -t "=$S" 2>/dev/null || tmux new-session -d -s "$S" -n ctl "bash"
while read -r name g cfg opts; do
  [ -z "$name" ] && continue; case $name in \#*) continue;; esac
  [ -e experiments/$name ] && { echo "skip $name (exists)"; continue; }
  EXIT=""; case "$opts" in *EXIT=*) EXIT="--exit_after_step ${opts##*EXIT=}"; opts="${opts% EXIT=*}";; esac
  RESCORE="$PY scripts/rescore_label_versions.py --runs $name --out reports/$S/$name.json > experiments/$name.rescore.log 2>&1; rc=\$?; echo \"[\$(date)] rescored $name rc=\$rc\" >> reports/$S/launch.log;"
  [ -n "$EXIT" ] && RESCORE=""
  CMD="source /tmp/noob_el/env.sh; cd /tmp/noob_el/el_alhvr; export CUDA_VISIBLE_DEVICES=$g OMP_NUM_THREADS=4 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True; \
echo \"[\$(date)] start $name gpu $g\" >> reports/$S/launch.log; \
$PY -u scripts/train.py --overwrite $EXIT --config configs/$cfg --opts $opts run_name=$name > experiments/$name.stdout 2>&1; rc=\$?; \
echo \"[\$(date)] trained $name rc=\$rc\" >> reports/$S/launch.log; $RESCORE exec bash"
  tmux new-window -d -t "=$S:" -n "$name" "bash -c '$CMD'"
  echo "launched $name on gpu $g"
  sleep 3
done < "$SPEC"
