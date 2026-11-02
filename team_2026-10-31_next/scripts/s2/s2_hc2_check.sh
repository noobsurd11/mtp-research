#!/bin/bash
# runner DRAFT (2 Nov 2026; coach: HC2 build acbe4352 ACCEPTED): the two HC2 GPU checks at el_hc2 0405151 (protocol_SKR2_HC2 §6, v1.1),
# one at a time, seed 0, each start through the shared gate (gpu_gate.sh) at 9,000 (HC's measured peak 6,826 + 2,048).
# Lanes are SHARED with the running SKR2 queue: each check's python PID is written to /home/noob/work/s2q/pids/<name>.pid, so the
# queue's alive() (MAXC 3) counts it, and the check also waits while 3 s2q processes are alive (same rule as the queue).
#   H0  hc2_h0_p0_s0:     pf2_SUPPF_100pct_s5 opts with seed=0 + data.synth_halfcut.p=0 + pool + data.synth_halfcut_ignore_inactive=true,
#                         --exit_after_step 1000. PASS = its 20 step lines + 20 'PF encoder lr' lines (steps 50..1000; timestamps and
#                         steps_per_sec stripped) are byte-identical (cmp) to the same lines of el_f3/experiments/f3_SUPPF_100pct_s0.stdout
#                         (grep of those lines only, as HC's H0 8645b979).
#   SMK hc2_smk_HCig_s0:  the HC2 arm opts (pf2 SUPPF + p 0.35 + pool + ignore_inactive=true), seed 0, --exit_after_step 1000. Reported by
#                         s2_hc2_parse.py (step / 'synth window' / 'synth inactive' / startup-key lines + Traceback count only): finite
#                         losses, 0 Tracebacks, synth share / eligible / p_eff (exp ~0.2585 / 0.7385 / 0.35), synthetic_inactive_px total
#                         (must be 0), ignored share of synthetic px (~0.002), nvidia-smi peak of its own pid, min free.
# Both: config_used.yaml diff vs pf2_SUPPF_100pct_s5 (run_name / seed / experiments_dir ignored) written to the log (H0: p 0 + pool + key;
# SMK: p 0.35 + pool + key = the exp_HC2 lines). el_hc2/REVISION is written (= 0405151) if absent, as hc_postwatch did for el_hc.
# Memory guard as smoke_a8.sh (free < 2,200 on 2 consecutive 1 s samples stops ONLY the check's own python PID, command printed first).
# rc captured before $(date). Usage: bash s2_hc2_check.sh H0 SMK
set -u
source /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
export CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1
P=/home/noob/work/el-fault-detection/.venv/bin/python; Q=/home/noob/work/s2q; O=/home/noob/work/runner_smk/s2; mkdir -p $O $Q/pids; L=$O/hc2_check.log
W=/home/noob/work/el_hc2; DEP=0405151; GATE=9000; J=/home/noob/work/el_f3/reports/pf2/pf2_jobs.txt
REF=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml; F3S=/home/noob/work/el_f3/experiments/f3_SUPPF_100pct_s0.stdout
POOL="data.synth_halfcut.pool=data/splits/synth_halfcut_pool_ap.tsv"; KEY="data.synth_halfcut_ignore_inactive=true"
cd $W || exit 1
[ "$(git rev-parse --short=7 HEAD)" = $DEP ] || { echo "[$(date)] deploy check FAIL: HEAD != $DEP" >> $L; exit 1; }
[ "$(cut -c1-7 reports/hc2/DEPLOY)" = $DEP ] || { echo "[$(date)] deploy check FAIL: reports/hc2/DEPLOY (first 7) != $DEP" >> $L; exit 1; }
[ -z "$(git status --short --untracked-files=no)" ] || { echo "[$(date)] deploy check FAIL: tracked changes" >> $L; exit 1; }
[ "$(md5sum < $J | cut -c1-32)" = 210d0d6fcc54c3effcc36893e0d51ad5 ] || { echo "[$(date)] pf2_jobs md5 FAIL" >> $L; exit 1; }
[ -e REVISION ] || echo $DEP > REVISION
[ "$(cat REVISION)" = $DEP ] || { echo "[$(date)] REVISION != $DEP" >> $L; exit 1; }
base=$(grep "^pf2_SUPPF_100pct_s5|" $J | cut -d'|' -f4 | sed -e "s/^seed=5 /seed=0 /" -e "s/ run_name=pf2_SUPPF_100pct_s5\$//")
case "$base" in "seed=0 "*) ;; *) echo "[$(date)] opts derivation FAIL" >> $L; exit 1;; esac
s2alive(){ local n=0 f; for f in $Q/pids/*.pid; do [ -e "$f" ] || continue; kill -0 "$(cat $f)" 2>/dev/null && n=$((n + 1)); done; echo $n; }
guard(){ local pid=$1 mem=$2 low=0 f
  while kill -0 "$pid" 2>/dev/null; do
    f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)
    echo "$(date +%T) free $f | $(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr '\n' ' ')" >> "$mem"
    if [ "$f" -lt 2200 ]; then low=$((low+1)); else low=0; fi
    if [ $low -ge 2 ]; then
      echo "[$(date)] GUARD: free $f < 2200 twice; stopping own check PID $pid: $(ps -o args= -p "$pid" | cut -c1-200)" >> $L
      kill "$pid"; low=0; fi
    sleep 1; done; }
lines(){ grep -oE "step [0-9]+/20000 .*|PF encoder lr=[^ ]+ at step [0-9]+" "$1" | sed -E 's/ +steps_per_sec=[0-9.]+//' \
         | awk '{n=($1=="step") ? $2+0 : $NF+0; if (n <= 1000) print}'; }
run(){ local n=$1 pid rc c d; shift
  [ ! -e experiments/$n ] || { echo "[$(date)] $n exists; refusing" >> $L; return 1; }
  while [ "$(s2alive)" -ge 3 ]; do sleep 30; done
  gate_wait $GATE "s2-hc2 $n"
  echo "[$(date)] start $n (gate $GATE; s2q alive $(s2alive))" >> $L
  $P scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 1000 --opts "$@" run_name=$n > experiments/$n.stdout 2>&1 &
  pid=$!; echo $pid > $Q/pids/$n.pid; echo "$pid $n $(date +%T)" >> $O/pids.txt
  guard $pid $O/$n.gpumem.txt
  wait $pid; rc=$?
  echo "[$(date)] trained $n rc=$rc (3 = planned exit at 1000)" >> $L
  c=experiments/$n/config_used.yaml
  d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' $REF) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
  echo "  config diff vs pf2_SUPPF_100pct_s5 ($n; seed $(grep -m1 '^seed:' $c)): [$(echo "$d" | tr '\n' ';')]" >> $L
  echo "$d" > $O/$n.cfgdiff.txt
  return 0; }
for s in "$@"; do case $s in
  H0) run hc2_h0_p0_s0 $base data.synth_halfcut.p=0 $POOL $KEY || continue
      lines experiments/hc2_h0_p0_s0.stdout > $O/H0_hc2.lines; lines $F3S > $O/H0_ref_1000.lines
      nh=$(wc -l < $O/H0_hc2.lines); nr=$(wc -l < $O/H0_ref_1000.lines)
      if [ "$nr" = 40 ] && cmp -s $O/H0_hc2.lines $O/H0_ref_1000.lines; then res=IDENTICAL; else res=DIFFERENT; fi
      echo "H0 p=0 + ignore_inactive identity to step 1,000: $res ($nr ref lines, $nh hc2 lines; md5 $(md5sum < $O/H0_ref_1000.lines | cut -c1-8) / $(md5sum < $O/H0_hc2.lines | cut -c1-8))" >> $L
      $P -I /home/noob/work/runner_smk/s2_hc2_parse.py experiments/hc2_h0_p0_s0 $O/hc2_h0_p0_s0.gpumem.txt "$(cat $Q/pids/hc2_h0_p0_s0.pid)" >> $L 2>&1;;
  SMK) run hc2_smk_HCig_s0 $base data.synth_halfcut.p=0.35 $POOL $KEY || continue
      $P -I /home/noob/work/runner_smk/s2_hc2_parse.py experiments/hc2_smk_HCig_s0 $O/hc2_smk_HCig_s0.gpumem.txt "$(cat $Q/pids/hc2_smk_HCig_s0.pid)" >> $L 2>&1;;
  *) echo "[$(date)] unknown check $s" >> $L;;
esac; done
echo "[$(date)] hc2 checks done: $*" >> $L
