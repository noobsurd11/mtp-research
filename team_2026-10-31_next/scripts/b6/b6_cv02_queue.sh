#!/bin/bash
# runner DRAFT (1 Nov 2026, 23:5x): B6 launch queue on cv02 (protocol_B6 v1.0.1 §3, §6, §8.3). NOT APPROVED: copied to cv02 and
# armed only after coach's APPROVED and a qualifying snapshot (>= 3 GPUs with no other user's process > 4,096 MiB).
# Layout (fixed at APPROVED): B=/tmp/noob_el/el_b6 = git archive e544133 + REVISION + CODE.md5 (md5 of every archived file);
#   B/b6_roots = builder's roots (ROOTS.md5) with labeled -> B/b6_data/labeled (only the 532 stems; DATA_MANIFEST.md5 per root);
#   Q=B/q: b6_jobs.txt (JOBS_MD5), ref_SUP.yaml / ref_SUPPF.yaml (= gaint pf2_{SUP,SUPPF}_100pct_s5/config_used.yaml, ba0b243d /
#   6aba106a), exp/<arm>_f<k>.txt (builder's expected 'Labelled' / 'CE class weights' / 'Zero-pixel classes' messages, no prefix).
# Per start: lane = a GPU from GPUS (qualifying ids at launch) with < LPG of our runs alive, no process of another user > OTHER_MAX
#   on it (any compute pid not in our pids/ counts as another user's: cv02 is one shared account), free >= GATE; >= 120 s since the
#   last start; HOLD file stops new starts. A GPU taken by another user is skipped (logged), never contested; our running jobs are
#   never stopped by this script.
# After each start: (a) config_used.yaml vs ref_<arm>.yaml (run_name, seed, experiments_dir ignored) must differ only in data.root,
#   = that run's root, and seed must be K; (b) the stdout's 'Labelled:', 'CE class weights' and 'Zero-pixel classes' lines
#   (grep -m1 of those three messages only, never the rest of the stdout) must equal exp/<arm>_f<k>.txt. Either fails -> HOLD +
#   FAIL line; that run does not count until runner + coach decide. rc captured before $(date). python PIDs in pids/.
# v2 (coach review 23:39): cfgcheck polls up to 600 s until all 3 databuild messages are in the stdout; R34 ImageNet weights in
#   cv02's HF cache md5-checked = gaint's (smp 0.5.0 loads smp-hub/resnet34.imagenet under HF_HUB_OFFLINE; env.sh sets HF_HOME);
#   nproc + loadavg in the armed line (advisory).
set -u
. /tmp/noob_el/env.sh   # HF_HOME / TORCH_HOME / TMPDIR under /tmp/noob_el (as every earlier cv02 run)
B=${B:-/tmp/noob_el/el_b6}; Q=$B/q; L=$Q/launch.log; J=$Q/b6_jobs.txt; P=/tmp/noob_el/el-fault-detection/.venv/bin/python
JOBS_MD5=${JOBS_MD5:?}; GPUS=${GPUS:?space-separated qualifying GPU ids}; GATE=${GATE:-9000}; OTHER_MAX=${OTHER_MAX:-4096}
mkdir -p $Q/pids; touch $Q/last_start
fail(){ echo "[$(date)] b6q: $1; not starting" >> $L; exit 1; }
[ "$(md5sum < $J | cut -c1-32)" = "$JOBS_MD5" ] || fail "jobs md5 FAIL"
W=$HF_HOME/hub/models--smp-hub--resnet34.imagenet/snapshots/7a57b34f723329ff020b3f8bc41771163c519d0c
[ "$(md5sum < $W/model.safetensors | cut -c1-32)" = f57b430554b18e1238c4f92eac566544 ] && [ "$(md5sum < $W/config.json | cut -c1-32)" = edb5bacf626ef9c1a84766c8945cc001 ] \
  || fail "R34 ImageNet weights md5 != gaint's (f57b4305 / edb5bacf)"
[ "$(cut -c1-7 $B/REVISION)" = e544133 ] || fail "REVISION != e544133"
(cd $B && md5sum -c --quiet CODE.md5) || fail "CODE.md5 check FAIL"
(cd $B/b6_roots && md5sum -c --quiet ROOTS.md5) || fail "ROOTS.md5 check FAIL"
for k in 0 1 2 3 4; do (cd $B/b6_roots/b6_root_$k && md5sum -c --quiet SPLITS.md5 && md5sum -c --quiet DATA_MANIFEST.md5) \
  || fail "root $k SPLITS / DATA_MANIFEST check FAIL"; done
[ "$(md5sum < $Q/ref_SUP.yaml | cut -c1-8)" = ba0b243d ] && [ "$(md5sum < $Q/ref_SUPPF.yaml | cut -c1-8)" = 6aba106a ] || fail "ref config md5 FAIL"
kill -0 "$(cat $Q/gpumem.pid 2>/dev/null)" 2>/dev/null || fail "gpumem logger (b6_cv02_gpumem.sh) not running"
mapfile -t JOBS < $J
# v3 (runner 2 Nov 13:3x, found at the identity run): a recorded pid is the launching SUBSHELL; the GPU process is its child python.
# ours() therefore lists every live recorded pid AND its children, so lane_ok matches our GPU processes; nown() counts live runs.
ours(){ local f p; for f in $Q/pids/*.pid; do [ -e "$f" ] || continue; p=$(cat $f); kill -0 "$p" 2>/dev/null || continue; echo $p; ps -o pid= --ppid $p | tr -d ' '; done; }
nown(){ local f n=0; for f in $Q/pids/*.pid; do [ -e "$f" ] && kill -0 "$(cat $f)" 2>/dev/null && n=$((n + 1)); done; echo $n; }
uuid(){ nvidia-smi --query-gpu=uuid --format=csv,noheader -i $1 | tr -d ' '; }
lane_ok(){ local g=$1 u n=0 other=0 p m o; u=$(uuid $g); o=" $(ours | tr '\n' ' ') "
  while IFS=, read -r gu p m; do gu=$(echo $gu | tr -d ' '); p=$(echo $p | tr -d ' '); m=$(echo $m | tr -d ' ')
    [ "$gu" = "$u" ] || continue
    case "$o" in *" $p "*) n=$((n+1));; *) [ "$m" -gt "$OTHER_MAX" ] && other=1;; esac
  done < <(nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits)
  [ $other = 1 ] && { echo "[$(date)] lane skip GPU $g: another user > $OTHER_MAX MiB" >> $L; return 1; }
  [ $n -ge "$(cat $Q/LPG 2>/dev/null || echo 3)" ] && return 1
  [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i $g | tr -d ' ')" -ge $GATE ]; }
cfgcheck(){ local name=$1 k=$2 arm=$3 f=$4 c=$B/experiments/$1/config_used.yaml so=$B/experiments/$1.stdout t=0 d e x
  while [ ! -s $c ] && [ $t -lt 300 ]; do sleep 5; t=$((t+5)); done
  [ -s $c ] || { echo "[$(date)] CONFIG FAIL $name: no config_used.yaml after 300 s; HOLD set" >> $L; touch $Q/HOLD; return; }
  d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' $Q/ref_$arm.yaml) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
  e=$(printf '<   root: %s\n>   root: data\n' "$B/b6_roots/b6_root_$f" | sort)
  if [ "$d" = "$e" ] && grep -qx "seed: $k" $c; then echo "[$(date)] config OK $name vs pf2_${arm}_100pct_s5: data.root b6_root_$f + seed $k only" >> $L
  else echo "[$(date)] CONFIG FAIL $name: [$(echo "$d" | tr '\n' ' ')] seed_ok $(grep -qx "seed: $k" $c && echo 1 || echo 0); HOLD set" >> $L; touch $Q/HOLD; return; fi
  t=0; while [ "$(for m in 'Labelled: ' 'CE class weights: ' 'Zero-pixel classes'; do grep -m1 -c "$m" $so 2>/dev/null; done | grep -c '^1$')" -lt 3 ] && [ $t -lt 600 ]; do sleep 5; t=$((t+5)); done
  x=$(for m in 'Labelled: ' 'CE class weights: ' 'Zero-pixel classes'; do grep -m1 -oE "$m.*" $so; done)
  if [ "$x" = "$(cat $Q/exp/${arm}_f$f.txt)" ]; then echo "[$(date)] databuild OK $name (Labelled / CE weights / zero-pixel = exp/${arm}_f$f.txt)" >> $L
  else echo "[$(date)] DATABUILD FAIL $name vs exp/${arm}_f$f.txt; HOLD set" >> $L; touch $Q/HOLD; fi; }
echo "[$(date)] b6 queue armed: ${#JOBS[@]} jobs (md5 $JOBS_MD5), GPUS '$GPUS', LPG $(cat $Q/LPG 2>/dev/null || echo 3), gate $GATE, other-user max $OTHER_MAX, pid $$; nproc $(nproc), loadavg $(cut -d' ' -f1-3 /proc/loadavg); R34 weights md5 OK" >> $L
for j in "${JOBS[@]}"; do
  IFS='|' read -r name k arm f opts <<< "$j"
  if [ -e $B/experiments/$name ]; then echo "[$(date)] skip $name (exists)" >> $L; continue; fi
  while :; do
    [ -e $Q/HOLD ] && { sleep 60; continue; }
    [ $(( $(date +%s) - $(stat -c %Y $Q/last_start) )) -lt 120 ] && { sleep 10; continue; }
    g=""; for c in $GPUS; do lane_ok $c && { g=$c; break; }; done
    [ -n "$g" ] && break; sleep 60
  done
  touch $Q/last_start
  echo "[$(date)] start $name on GPU $g (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i $g | tr -d ' ') MiB; ours alive $(nown))" >> $L
  ( cd $B && CUDA_VISIBLE_DEVICES=$g HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --opts $opts > experiments/$name.stdout 2>&1 &
    pp=$!; echo $pp > $Q/pids/$name.pid
    wait $pp; rc=$?; echo "[$(date)] trained $name rc=$rc" >> $L ) &
  echo "$name subshell $!" >> $Q/pids/subshells.txt
  sleep 3; echo "[$(date)] pid $name $(cat $Q/pids/$name.pid 2>/dev/null) GPU $g" >> $L
  cfgcheck $name $k $arm $f
done
echo "[$(date)] b6 queue: all jobs dispatched; waiting" >> $L
wait
echo "[$(date)] B6 ALL TRAINED ($(grep -c 'trained .* rc=0' $L) rc 0 of ${#JOBS[@]})" >> $L
