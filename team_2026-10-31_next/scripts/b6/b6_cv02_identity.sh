#!/bin/bash
# runner DRAFT (1 Nov 2026): B6 repeat-identity check on cv02 A6000 (protocol_B6 §6: "a 1,000-step repeat-identity check of one run
# on A6000"). Runs job line 2 of b6_jobs.txt (b6_SUPPF_f0_s5: PF arm, the one with the encoder schedule) twice for 1,000 steps
# (--exit_after_step 1000, e544133 train.py l.87 / l.321) as b6_idA / b6_idB, one after the other on one qualifying GPU (G), then
# compares the "step N/20000" lines only (grep, never the rest of the stdout; steps_per_sec stripped). PASS iff identical.
# Also prints the peak used MiB of each (1 s nvidia-smi samples) for the cv02 gate. The two run dirs are deleted afterwards by
# runner (not by this script). Usage: G=<gpu id> bash b6_cv02_identity.sh
set -u
. /tmp/noob_el/env.sh   # HF_HOME (R34 ImageNet weights cache) / TORCH_HOME / TMPDIR, as the queue
B=${B:-/tmp/noob_el/el_b6}; Q=$B/q; P=/tmp/noob_el/el-fault-detection/.venv/bin/python; G=${G:?}; O=$Q/identity; mkdir -p $O $Q/pids
line=$(sed -n 2p $Q/b6_jobs.txt); IFS='|' read -r name k arm f opts <<< "$line"; [ "$name" = b6_SUPPF_f0_s5 ] || { echo "line 2 is $name"; exit 2; }
for r in A B; do
  o=${opts% run_name=$name}; o="$o run_name=b6_id$r"
  ( cd $B && CUDA_VISIBLE_DEVICES=$G HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --exit_after_step 1000 --opts $o > experiments/b6_id$r.stdout 2>&1 &
    pp=$!; echo $pp > $Q/pids/b6_id$r.pid; pk=0
    while kill -0 $pp 2>/dev/null; do k=" $pp $(ps -o pid= --ppid $pp | tr -d ' ' | tr '\n' ' ') "  # v2: the GPU process is pp's child
      m=$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr -d ' ' | while IFS=, read -r q mm; do case "$k" in *" $q "*) echo $mm;; esac; done | sort -n | tail -n 1)
      [ -n "$m" ] && [ "$m" -gt $pk ] && pk=$m; sleep 1; done
    wait $pp; rc=$?; echo "[$(date)] identity run $r rc=$rc peak ${pk} MiB" >> $O/identity.log )
  grep -oE "step [0-9]+/20000.*" $B/experiments/b6_id$r.stdout | sed -E "s/ +steps_per_sec=[0-9.]+//" > $O/steps_$r.txt
done
nA=$(wc -l < $O/steps_A.txt); nB=$(wc -l < $O/steps_B.txt)
if [ "$nA" -gt 0 ] && cmp -s $O/steps_A.txt $O/steps_B.txt; then res=PASS; else res=FAIL; fi
echo "[$(date)] identity $res: step lines A $nA / B $nB, md5 $(md5sum < $O/steps_A.txt | cut -c1-8) / $(md5sum < $O/steps_B.txt | cut -c1-8)" >> $O/identity.log
tail -n 3 $O/identity.log
