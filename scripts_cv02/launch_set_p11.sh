#!/bin/bash
# Generic cv02 launcher: one tmux window per run in session <session> (train, then read-only rescore), same pattern as
# launch_p7.sh / launch_p8.sh. Usage: launch_set.sh <session> <spec file>
# Spec lines: <run name> <gpu> <config yaml> <opts...>. A run whose experiments/<name> exists is skipped (never overwritten).
S=$1; SPEC=$2
cd /tmp/noob_el/el_p11
PY=/tmp/noob_el/el-fault-detection/.venv/bin/python
mkdir -p reports/$S experiments
tmux has-session -t $S 2>/dev/null || tmux new-session -d -s $S -n ctl "bash"
while read -r name g cfg opts; do
  [ -z "$name" ] && continue; case $name in \#*) continue;; esac
  [ -e experiments/$name ] && { echo "skip $name (exists)"; continue; }
  CMD="source /tmp/noob_el/env.sh; cd /tmp/noob_el/el_p11; export CUDA_VISIBLE_DEVICES=$g OMP_NUM_THREADS=4; \
echo \"[\$(date)] start $name gpu $g\" >> reports/$S/launch.log; \
$PY -u scripts/train.py --overwrite --config configs/$cfg --opts $opts run_name=$name > experiments/$name.stdout 2>&1; \
echo \"[\$(date)] trained $name rc=\$?\" >> reports/$S/launch.log; \
$PY scripts/rescore_label_versions.py --runs $name --out reports/$S/$name.json > experiments/$name.rescore.log 2>&1; \
echo \"[\$(date)] rescored $name rc=\$?\" >> reports/$S/launch.log; exec bash"
  tmux new-window -d -t $S: -n "$name" "bash -c '$CMD'"
  echo "launched $name on gpu $g"
  sleep 3
done < "$SPEC"
