#!/bin/bash
# Track D (d1) queue on cv02 (copy of lanes_sk1.sh, dir el_d1): fixed per-GPU lanes, no GPU polling (agreed split with the ALHVR track: SK1 owns the listed
# GPUs). Runs are dealt round-robin over (gpu, lane) pairs; each lane runs its runs one after another in one tmux window
# of session <session>. Same train / rc / rescore commands as launch_set_sk1.sh. Training is deterministic per
# machine, so lane packing changes speed only.
# Usage: lanes_sk1.sh <session> <spec> <lanes per gpu> <gpu ...>
S=$1; SPEC=$2; K=$3; shift 3; GPUS=($@)
cd /tmp/noob_el/el_d1
PY=/tmp/noob_el/el-fault-detection/.venv/bin/python
mkdir -p reports/$S/lanes experiments
mapfile -t Q < <(grep -v '^\s*#' "$SPEC" | grep -v '^\s*$')
NL=$(( ${#GPUS[@]} * K ))
for ((l=0; l<NL; l++)); do : > reports/$S/lanes/lane$l.spec; done
for ((i=0; i<${#Q[@]}; i++)); do
  l=$(( i % NL )); g=${GPUS[$(( l % ${#GPUS[@]} ))]}
  echo "${Q[$i]}" | awk -v g=$g '{$2=g; print}' >> reports/$S/lanes/lane$l.spec
done
cat > reports/$S/lanes/run_lane.sh <<'EOF'
#!/bin/bash
S=$1; LANE=$2; PY=/tmp/noob_el/el-fault-detection/.venv/bin/python
source /tmp/noob_el/env.sh; cd /tmp/noob_el/el_d1
while read -r name g cfg opts; do
  [ -z "$name" ] && continue
  if [ -e experiments/$name ]; then echo "[$(date)] skip $name (exists)" >> reports/$S/launch.log; continue; fi
  export CUDA_VISIBLE_DEVICES=$g OMP_NUM_THREADS=4
  echo "[$(date)] start $name gpu $g lane $(basename $LANE .spec)" >> reports/$S/launch.log
  $PY -u scripts/train.py --overwrite --config configs/$cfg --opts $opts run_name=$name > experiments/$name.stdout 2>&1
  rc=$?; echo "[$(date)] trained $name rc=$rc" >> reports/$S/launch.log
  if [ $rc -eq 0 ]; then
    $PY scripts/rescore_label_versions.py --runs $name --out reports/$S/$name.json > experiments/$name.rescore.log 2>&1
    rc2=$?; echo "[$(date)] rescored $name rc=$rc2" >> reports/$S/launch.log
  else
    echo "[$(date)] not rescored $name (train rc=$rc)" >> reports/$S/launch.log
  fi
done < "$LANE"
echo "[$(date)] lane $(basename $LANE .spec) done" >> reports/$S/launch.log
EOF
tmux has-session -t "=$S" 2>/dev/null || tmux new-session -d -s $S -n ctl "bash"
for ((l=0; l<NL; l++)); do
  [ -s reports/$S/lanes/lane$l.spec ] || continue
  tmux new-window -d -t "=$S:" -n "lane$l" "bash reports/$S/lanes/run_lane.sh $S reports/$S/lanes/lane$l.spec; exec bash"
  echo "lane$l: $(cut -d' ' -f1,2 reports/$S/lanes/lane$l.spec | tr '\n' ' ')"
  sleep 3
done
