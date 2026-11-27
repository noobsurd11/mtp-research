#!/bin/bash
# c3x smokes on gaint (rulings C5 / Q4; run by the LEAD after the commit, before the deploy; GPU work only through the gaint
# queue tools: bench_setup.sh with the shared gate, the outside-process wait, the 1 s memory log and the auto-stop guard,
# as the wave 2a smoke). One queue dir Q = /home/noob/work/bq/c3x_smoke, session bench_q_c3x_smoke, from the worktree
# /home/noob/work/bench_wt_c3s at the c3x commit X. finllm (PID 6206) is protected by bench_lib.sh (PROTECT default 6206).
#   training queue (MAXC 1, one run at a time; gate 11000 each; cv5v3 fold 0, seed 5):
#     smoke_c3x_mem_hrnet   card hrnet_w18_unetpp_pf_v11 (plain HRNet), --exit_after_step 300 (rc 3 by design)  (a) MEMORY
#     smoke_c3x_mem_combo   card hrnet_w18_unetpp_swad_const_pf_v11 (c3x), --exit_after_step 300 (rc 3)         (a) MEMORY
#     smoke_c3x_path        smoke card smoke/smoke_c3x_hrnet_swad_path.yaml (the c3x card with total_steps 600,
#                           enc_probe_every 200, swad window 300 to 600, encoder_pf freeze 100 and ramp 100: the
#                           order of events of the real run), full run to step 600                              (b) PATH
#   dump queue (after the training queue's end line; MAXC 1, gate 6200), the two dumps cq.sh makes on cv02, same arguments
#   except the gaint paths and bench_infer's default forbidden list (as every gaint dump):
#     dump_smoke_c3x_path        --run-id smoke_c3x_path       (key auto = the card's weights_key swad_bn)
#     dump_smoke_c3x_path.swad   --run-id smoke_c3x_path.swad --weights-key swad
#   then by hand (step slim, CPU): bench/q/cv02/slim_ckpt.py --run experiments/smoke_c3x_path --keys swad_bn,swad (as cq.sh).
# Steps (one per call):
#   place   writes Q (jobs.txt, MAXC 1, dump/jobs.txt, dump/MAXC 1); refuses if Q exists. Prints both md5s.
#   arm     pre-checks (worktree at X = one commit on 852ed5c with the expected tree, no tracked change; smoke card md5; Q as
#           placed and unused; no experiments/<job> or dump folder yet; session free), then bench_setup.sh. Other gaint
#           queues are not touched: the shared gate (free >= gate, 120 s since any start) and the outside wait (any other
#           GPU process > 1,024 MiB except finllm) make the smoke wait for them, and them for it.
#   check   read only, after 'chain done' in Q/chain.log: every proving line (request section 3), the peaks, the gate
#           max(11000, P + 2,048) with P = the highest peak of the c3x card over the memory and the path smoke, and the
#           pass criterion P - (plain HRNet peak) <= 1,024 MiB (lead's Q1 ruling; above it the lead looks before arming).
#           Output also in Q/smoke_check.out (its RULE line is what c3x_queue.sh build requires as GATE); returns its rc.
#   slim    CPU: the slim step with --keys (refuses before 'chain done' or if slim.pth exists); returns slim_ckpt.py's own rc
#           (review B1); log Q/slim_smoke_c3x_path.log. Then run check again: a missing slim.pth is a FAIL there.
#   clean   removes the smoke's experiments dirs and stdout files in the worktree and the smoke dump folder (prints the
#           list first; DRY=1 prints only; refuses while the session lives). Q (logs) is kept.
# Env: X (full c3x commit; arm, check), DRY.
set -u
STEP=${1:?step: place | arm | check | slim | clean}
Q=${Q_TEST:-/home/noob/work/bq/c3x_smoke}; SES=bench_q_c3x_smoke; R=${R_TEST:-/home/noob/work/bench_wt_c3s}   # *_TEST: tests only
D=${D_TEST:-/home/noob/work/bench_dumps/c3x_smoke}
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); SC=$HERE/smoke_c3x_hrnet_swad_path.yaml; SC_MD5=7e74f6687ec760474d38730334ff1fb2
BASE=852ed5c411b967d7ea758ef2cd5dbe70ae4e50a1; TREE=c860f1bc243ff5262f8c23ffb1e551cfaea5ea79
P=/home/noob/work/el-fault-detection/.venv/bin/python; RT=/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f0
HC=bench/methods/hrnet_w18_unetpp_pf_v11.yaml; XC=bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml
N1=smoke_c3x_mem_hrnet; N2=smoke_c3x_mem_combo; N3=smoke_c3x_path; DRY=${DRY:-0}
no(){ echo "REFUSED ($STEP): $*"; exit 1; }
DC="$P -u scripts/bench_infer.py --run $R/experiments/$N3 --set cv5v3_f0 --dumps $D --method smoke_c3x_hrnet_swad_path --card $SC --run-id $N3 --device cuda --precision fp32 --threads 4 --workers 4 --batch 8 --bench-run dump_$N3"
DC2="$P -u scripts/bench_infer.py --run $R/experiments/$N3 --set cv5v3_f0 --dumps $D --method smoke_c3x_hrnet_swad_path --card $SC --run-id $N3.swad --weights-key swad --device cuda --precision fp32 --threads 4 --workers 4 --batch 8 --bench-run dump_$N3.swad"
case $STEP in
place)
  [ -e $Q ] && no "$Q exists"
  [ "$(md5sum < $SC | cut -c1-32)" = $SC_MD5 ] || no "smoke card md5 is not $SC_MD5"
  mkdir -p $Q/dump || exit 1
  printf '%s\n' "$N1|$HC|5|$RT|11000||--exit_after_step 300" "$N2|$XC|5|$RT|11000||--exit_after_step 300" "$N3|$SC|5|$RT|11000||" > $Q/jobs.txt
  printf '%s\n' "dump_$N3|-|5|$RT|6200|$DC|" "dump_$N3.swad|-|5|$RT|6200|$DC2|" > $Q/dump/jobs.txt
  echo 1 > $Q/MAXC; echo 1 > $Q/dump/MAXC; chmod a-w $Q/jobs.txt $Q/dump/jobs.txt
  echo "placed $Q: jobs.txt md5 $(md5sum < $Q/jobs.txt | cut -c1-32) (3 lines), dump/jobs.txt md5 $(md5sum < $Q/dump/jobs.txt | cut -c1-32) (2 lines), MAXC 1 / 1";;
arm)
  X=${X:?full c3x commit}
  [ "$(git -C $R rev-parse HEAD)" = "$X" ] || no "$R HEAD $(git -C $R rev-parse HEAD) != X $X"
  [ "$(git -C $R rev-parse HEAD^)" = $BASE ] && [ "$(git -C $R rev-parse HEAD^{tree})" = $TREE ] || no "X is not the c3x commit on 852ed5c with tree $TREE"
  [ -z "$(git -C $R status --short --untracked-files=no)" ] || no "$R has tracked changes"
  [ "$(md5sum < $SC | cut -c1-32)" = $SC_MD5 ] || no "smoke card md5 is not $SC_MD5"
  [ -s $Q/jobs.txt ] && [ -s $Q/dump/jobs.txt ] || no "run 'place' first"
  for f in queue.pid gpumem.pid guard.pid HOLD pids launch.log chain.log; do [ -e $Q/$f ] || [ -e $Q/dump/$f ] && no "$Q is armed or used ($f)"; done
  for n in $N1 $N2 $N3 dump_$N3 dump_$N3.swad; do [ -e $R/experiments/$n ] || [ -e $R/experiments/$n.stdout ] && no "$R/experiments/$n exists"; done
  [ -e $D ] && no "$D exists"
  tmux has-session -t "=$SES" 2>/dev/null && no "tmux session $SES exists"
  o=$(tmux ls 2>/dev/null | grep -oE '^bench_q_[a-z0-9_]+' | tr '\n' ' '); [ -z "$o" ] || echo "note: other gaint queue sessions alive: $o(the gate and the outside wait serialise them with the smoke)"
  A="Q=$Q SES=$SES DEPLOY=$X JOBS_MD5=$(md5sum < $Q/jobs.txt | cut -c1-32) DJOBS_MD5=$(md5sum < $Q/dump/jobs.txt | cut -c1-32) REPO=$R MAXH=6 bash $R/bench/q/bench_setup.sh"
  [ $DRY = 1 ] && { echo "DRY, pre-checks passed; not run: $A"; exit 0; }
  eval "$A";;
check)
  X=${X:?full c3x commit}
  grep -q "chain done" $Q/chain.log 2>/dev/null || no "no 'chain done' in $Q/chain.log yet"
  cd $R || exit 1
  CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 nice -n 19 $P $HERE/c3x_smoke_check.py --q $Q --repo $R --dumps $D --card $SC 2>&1 | tee $Q/smoke_check.out
  rc=${PIPESTATUS[0]}; echo "check rc $rc; output kept in $Q/smoke_check.out (c3x_queue.sh build reads its RULE line)"; exit $rc;;
slim)
  grep -q "chain done" $Q/chain.log 2>/dev/null || no "no 'chain done' in $Q/chain.log yet"
  [ -e $R/experiments/$N3/checkpoints/slim.pth ] && no "slim.pth exists"
  (cd $R && CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 nice -n 19 $P bench/q/cv02/slim_ckpt.py --run experiments/$N3 --keys swad_bn,swad) 2>&1 | tee $Q/slim_$N3.log
  rc=${PIPESTATUS[0]}; [ $rc = 0 ] || echo "SLIM FAILED (slim_ckpt.py rc $rc; $Q/slim_$N3.log)"; exit $rc;;
clean)
  tmux has-session -t "=$SES" 2>/dev/null && no "session $SES still alive"
  L=$(for n in $N1 $N2 $N3 dump_$N3 dump_$N3.swad; do for p in $R/experiments/$n $R/experiments/$n.stdout; do [ -e $p ] && echo $p; done; done; [ -e $D ] && echo $D)
  echo "to remove:"; echo "$L"; [ $DRY = 1 ] && exit 0
  for p in $L; do case "$p" in $R/experiments/smoke_c3x_*|$R/experiments/dump_smoke_c3x_*|$D) rm -rf "$p";; *) no "unexpected path $p";; esac; done
  echo "removed; $Q kept";;
*) no "unknown step";;
esac
