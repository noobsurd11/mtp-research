#!/bin/bash
# Track M cv02 lanes: fixed (gpu, lane) workers that pop runs from one flock-locked queue file, so later rungs can be
# appended to the same queue without touching running lanes. Training is deterministic per machine: packing changes speed only.
# Usage: lanes_m.sh <session> <queue file> <lanes per gpu> <gpu ...>
#   queue lines: <run name> <config yaml> <opts...>      (no gpu field; the lane's gpu is used)
#   append later with:  flock <queue>.lock -c 'cat more.spec >> <queue>'
# Per run: train (XARGS env passed through, e.g. "--exit_after_step 300" for smokes), rc captured before $(date), then the
# P-series rescorer only if rc = 0. A run whose experiments/<name> exists is skipped, never overwritten.
S=$1; Q=$(readlink -f "$2"); K=$3; shift 3; GPUS=("$@")
CODE=${CODE:-/tmp/noob_el/el_mt}
cd $CODE; mkdir -p reports/$S experiments
cat > reports/$S/worker.sh <<'EOF'
#!/bin/bash
S=$1; Q=$2; G=$3; L=$4; CODE=$5; PY=/tmp/noob_el/el-fault-detection/.venv/bin/python
source /tmp/noob_el/env.sh; cd $CODE
while true; do
  line=$(flock "$Q.lock" -c "l=\$(grep -v '^\s*#' '$Q' | grep -v '^\s*\$' | head -1); [ -n \"\$l\" ] && { grep -vxF -- \"\$l\" '$Q' > '$Q.tmp'; mv '$Q.tmp' '$Q'; echo \"\$l\" >> '$Q.popped'; }; echo \"\$l\"")
  [ -z "$line" ] && break
  read -r name cfg opts <<< "$line"
  if [ -e experiments/$name ]; then echo "[$(date)] skip $name (exists)" >> reports/$S/launch.log; continue; fi
  export CUDA_VISIBLE_DEVICES=$G OMP_NUM_THREADS=4
  echo "[$(date)] start $name gpu $G lane $L" >> reports/$S/launch.log
  $PY -u scripts/train.py ${XARGS:-} --overwrite --config configs/$cfg --opts $opts run_name=$name > experiments/$name.stdout 2>&1
  rc=$?; echo "[$(date)] trained $name rc=$rc" >> reports/$S/launch.log
  if [ $rc -eq 0 ] && [ -z "${XARGS:-}" ]; then
    $PY scripts/rescore_label_versions.py --runs $name --out reports/$S/$name.json > experiments/$name.rescore.log 2>&1
    rc2=$?; echo "[$(date)] rescored $name rc=$rc2" >> reports/$S/launch.log
  else
    echo "[$(date)] not rescored $name (rc=$rc, XARGS='${XARGS:-}')" >> reports/$S/launch.log
  fi
done
echo "[$(date)] lane $L gpu $G done (queue empty)" >> reports/$S/launch.log
EOF
touch "$Q.lock"
tmux has-session -t "=$S" 2>/dev/null || tmux new-session -d -s $S -n ctl "bash"
for g in "${GPUS[@]}"; do for ((l=0; l<K; l++)); do
  tmux new-window -d -t "=$S:" -n "g${g}l$l" "XARGS='${XARGS:-}' bash reports/$S/worker.sh $S $Q $g g${g}l$l $CODE; exec bash"
  echo "lane g${g}l$l started"; sleep 5
done; done
