#!/bin/bash
# SK1 cv02 launcher (copy of launch_set_p17.sh for /tmp/noob_el/el_sk1): one tmux window per run in session <session>
# (train, then read-only rescore only if train rc = 0). rc is captured before $(date): in launch_set_p17.sh the
# logged rc came from the $(date) substitution, so it was always 0 (found 21 Oct). Usage: [XARGS="--exit_after_step 2500"] launch_set_sk1.sh <session> <spec file>
# Spec lines: <run name> <gpu> <config yaml> <opts...>. A run whose experiments/<name> exists is skipped (never overwritten).
S=$1; SPEC=$2; XARGS=${XARGS:-}
cd /tmp/noob_el/el_sk1
PY=/tmp/noob_el/el-fault-detection/.venv/bin/python
mkdir -p reports/$S experiments
tmux has-session -t "=$S" 2>/dev/null || tmux new-session -d -s $S -n ctl "bash"
while read -r name g cfg opts; do
  [ -z "$name" ] && continue; case $name in \#*) continue;; esac
  [ -e experiments/$name ] && { echo "skip $name (exists)"; continue; }
  CMD="source /tmp/noob_el/env.sh; cd /tmp/noob_el/el_sk1; export CUDA_VISIBLE_DEVICES=$g OMP_NUM_THREADS=4; \
echo \"[\$(date)] start $name gpu $g\" >> reports/$S/launch.log; \
$PY -u scripts/train.py $XARGS --overwrite --config configs/$cfg --opts $opts run_name=$name > experiments/$name.stdout 2>&1; \
rc=\$?; echo \"[\$(date)] trained $name rc=\$rc\" >> reports/$S/launch.log; \
if [ \$rc -eq 0 ]; then $PY scripts/rescore_label_versions.py --runs $name --out reports/$S/$name.json > experiments/$name.rescore.log 2>&1; \
rc2=\$?; echo \"[\$(date)] rescored $name rc=\$rc2\" >> reports/$S/launch.log; \
else echo \"[\$(date)] not rescored $name (train rc=\$rc)\" >> reports/$S/launch.log; fi; exec bash"
  tmux new-window -d -t "=$S:" -n "$name" "bash -c '$CMD'"
  echo "launched $name on gpu $g"
  sleep 3
done < "$SPEC"
