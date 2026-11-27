#!/bin/bash
# c3lane dump dry test (17 Nov 2026) = harness/c3swad/c3swad_dumptest.sh (24281092, reviewed after fix round 1) with these
# changes only: queue dir c3lane_smoke and session bench_q_c3lane_smoke (the waiting c3swad_smoke test of the old QC is
# stopped and cleaned first, with the c3swad script and QC = the old deploy); `place` also writes SHARE_DUMP 10240 into
# the test's queue dir, so the fixture takes its lane and both dumps run by the shared-dump rule of lane rule v2 (10,240
# MiB free; no unknown owner, no unreadable memory); ANYGPU=1 at `arm` passes all eight GPUs instead of only those without
# an open lane of our queues (rule R3 allows a dump beside our own login). The text below is the c3swad header; where it
# says "no other user above 4,096 MiB", read: the strict rule first, else the shared-dump rule.
# c3swad dump dry test on cv02 (run by the LEAD on gaint, after the deploy of the patched queue code, before the handover;
# optional but recommended, as c3base_smoke2 was): the chain 'dump swad_bn -> dump swad -> slim (2 keys) -> RUN.md5' of
# the patched cq.sh on one cv02 GPU, with NO training. Fixture = the finished gaint screen run w2a_swad_f0_s5 (20k steps,
# cv5v2 fold 0), placed in the NEW deploy dir QC (not in the live deploy): config_used.yaml with the data.root line
# rewritten to the cv02 root, latest.pth unchanged (940 MB), enc_probe.jsonl. The queue runs wholly from QC (B = QC).
# A dump holds about 3.2 GB for 2 minutes; it is not a training run (one-training-queue rule not touched).
# Lane rule for this test (lead's ruling Q10, 17 Nov): only a GPU where no other user holds more than 4,096 MiB and where
# none of our training runs sits. Where it is enforced:
#   1. `arm` below reads every queue dir of ours on cv02 and passes GPUS = only the GPUs that have NO open lane of any of
#      our queues (pids/<name>.gpu without <name>.end: a training run from its first second, or a run waiting for its
#      dump). It refuses if no GPU is left. cq_setup.sh hands GPUS to cq.sh (unchanged code).
#   2. cq.sh's lane rule (patched file: other_on l.69, lane_ok l.85), checked live at the fixture's lane pick (main loop,
#      l.219) and again before EACH of the two dump starts (chain, l.176, inside the loop over the dumps, l.171): the GPU
#      qualifies only if no other user holds more than 4,096 MiB there. Processes of our other queues are not in this
#      queue's pid files, so they count as another user: a training run of ours (5,740 MiB or more) blocks the GPU.
#   Not covered by 1 and 2: the training queue starts a run on the test's GPU after `arm`, and the dump's live check falls
#   into the first seconds of that run (memory still below 4,096 MiB). The dump would then run beside it (the case seen
#   on 16 Nov, 17:40). To exclude it fully, run the test inside the handover's freeze window (after `freeze` and `build`,
#   before `arm`), when no queue can start a training run.
# Steps: place (cv02 WRITE: fixture files and a smoke queue dir), arm (cv02 START), look (read only),
#   stop  (cv02: for a test queue that never got a lane. It sets HOLD in the test's own queue dir, waits 20 s, and only if
#          launch.log has no 'fixture <name> on GPU' line and no pids/*.gpu file it ends the test's own tmux session, by
#          exact name (tmux kill-session -t '=bench_q_c3swad_smoke'). Then it removes the HOLD it set. If the fixture did
#          take a lane it ends nothing and removes its HOLD, so the chain runs to its end by itself.)
#   clean (cv02 REMOVE, the lead runs it after the test: only the test's own folders: QC/experiments/<fixture>, its two
#          dump folders, QC/runs/<fixture> and the queue dir c3swad_smoke. It prints the list first. It refuses while the
#          test's session or queue process is alive, and if any path of QC/CODE.md5 lies in one of these folders: the
#          merged queue checks QC/CODE.md5 before every start and would HOLD on a missing file.)
# DRY=1 prints every write, start, stop or removal instead of running it.
# Expected in the smoke queue's launch.log:
#   dump_dumptest_c3s_swad_f0 startup line OK: BENCH_START: run=dump_dumptest_c3s_swad_f0
#   dumped dump_dumptest_c3s_swad_f0 rc=0 ...          (dlogs: '107 cells, 132.6 MiB, ties 0, key swad_bn, step 20000, cuda/fp32')
#   dumped dump_dumptest_c3s_swad_f0.swad rc=0 ...     (dlogs: '107 cells, 132.2 MiB, ties 0, key swad, step 20000, cuda/fp32')
#   RUN.md5 dumptest_c3s_swad_f0 rc=0: 220 files       (config, slim, LATEST.md5, enc_probe.jsonl, 2 x (107 npz + manifest))
#   BENCH CV02 Q ALL DONE (0 trained rc 0, 1 dumped rc 0, 1 RUN.md5 of 1 jobs ...)
# and in dlogs/slim_dumptest_c3s_swad_f0.log: keys ['swad', 'swad_bn']. Peak of both dumps from gpumem.log (PF: 3,212 MiB).
set -u
STEP=${1:?step: place | arm | look | stop | clean}; QC=${QC:?cv02 deploy dir of the patched queue code}; DRY=${DRY:-0}
echo "$QC" | grep -qE '^/tmp/noob_el/bench_[0-9a-f]{7}$' && [ "$QC" != /tmp/noob_el/bench_89b9ea5 ] || { echo "REFUSED: QC must be the new deploy dir"; exit 1; }
SRC=/home/noob/work/bench_wt_w2/experiments/w2a_swad_f0_s5; N=dumptest_c3s_swad_f0
Q=/tmp/noob_el/bench_q/c3lane_smoke; SES=bench_q_c3lane_smoke; SD=10240
JOB="$N|bench/methods/swad_const_pf_v11.yaml|5|/tmp/noob_el/bench_data/roots/cv5v2_v11_f0|0|11000|5262|0|--fixture|swad"
JMD5=$(echo "$JOB" | md5sum | cut -c1-32); DATA_MD5=d6063fd83d20e656612540edda702cbe
C=cv02@10.8.1.106; R(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; }
no(){ echo "REFUSED ($STEP): $*"; exit 1; }
case $STEP in
place)
  [ "$(md5sum < $SRC/checkpoints/latest.pth | cut -c1-32)" = 1f0fdb30e87e81551e611856f8f3df75 ] || no "gaint latest.pth of w2a_swad_f0_s5 is not 1f0fdb30"
  grep -q "root: /home/noob/work/bench_data/roots/cv5v2_v11_f0$" $SRC/config_used.yaml || no "config_used.yaml has no gaint root line"
  o=$(R "cd $QC && md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo CODE_OK; test ! -e experiments/$N && test ! -e $Q && echo FREE; df --output=avail -BG /tmp | tail -1 | tr -dc 0-9") || no "ssh failed"
  case "$o" in *CODE_OK*FREE*) ;; *) no "QC CODE.md5 failed, or experiments/$N or $Q exists: $o";; esac
  [ "$(echo "$o" | tail -1)" -ge 30 ] || no "cv02 free below 30 GB"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: tar stream of config_used.yaml (root line -> /tmp/noob_el/bench_data/roots/cv5v2_v11_f0), enc_probe.jsonl, checkpoints/latest.pth to $QC/experiments/$N; mkdir $Q with jobs.txt ($JOB; md5 $JMD5), LPG 1, MAXC 1, SHARE_DUMP $SD"; exit 0; fi
  T=$(mktemp -d) && mkdir -p $T/$N/checkpoints && sed 's#root: /home/noob/work/bench_data/roots/cv5v2_v11_f0$#root: /tmp/noob_el/bench_data/roots/cv5v2_v11_f0#' $SRC/config_used.yaml > $T/$N/config_used.yaml \
    && cp $SRC/enc_probe.jsonl $T/$N/ && ln -s $SRC/checkpoints/latest.pth $T/$N/checkpoints/latest.pth || no "staging failed"
  [ "$(diff $SRC/config_used.yaml $T/$N/config_used.yaml | grep -c '^[<>]')" = 2 ] || no "config rewrite changed more than the root line"
  tar -C $T -chf - $N | ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $QC/experiments/$N && tar -x -C $QC/experiments && md5sum < $QC/experiments/$N/checkpoints/latest.pth | cut -c1-32" | grep -qx 1f0fdb30e87e81551e611856f8f3df75 || no "fixture stream or md5 failed"
  rm -rf $T
  echo "$JOB" | ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $Q && mkdir $Q && cat > $Q/jobs.txt && echo 1 > $Q/LPG && echo 1 > $Q/MAXC && echo $SD > $Q/SHARE_DUMP && md5sum < $Q/jobs.txt | cut -c1-32" | grep -qx $JMD5 || no "queue dir not placed"
  echo "placed fixture $QC/experiments/$N (latest.pth md5 OK) and $Q (jobs md5 $JMD5; not armed)";;
arm)
  BQ=/tmp/noob_el/bench_q
  o=$(R "open=\" \$(for f in $BQ/*/pids/*.gpu; do [ -e \${f%.gpu}.end ] || cat \$f; done | tr '\n' ' ')\"; for g in 0 1 2 3 4 5 6 7; do case \"\$open\" in *\" \$g \"*) ;; *) echo -n \"\$g \";; esac; done; echo; for f in $BQ/*/pids/*.gpu; do [ -e \${f%.gpu}.end ] || echo \"open lane: GPU \$(cat \$f) \$(basename \${f%.gpu})\"; done") || no "ssh failed"
  G=$(echo "$o" | head -1); G=$(echo $G); echo "$o" | tail -n +2
  case "$G" in ""|*[!0-7\ ]*) no "no GPU without an open lane of one of our queues (list '$G'); try later";; esac
  [ "${ANYGPU:-0}" = 1 ] && G="0 1 2 3 4 5 6 7"
  echo "GPUs the test may use (ANYGPU=${ANYGPU:-0}; default: only those without an open lane of our queues), under lane rule v2: $G"
  A="B=$QC Q=$Q SES=$SES GPUS='$G' DEPLOY=\$(cat $QC/REVISION) JOBS_MD5=$JMD5 DATA_MD5=$DATA_MD5 bash $QC/bench/q/cv02/cq_setup.sh"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: $A"; exit 0; fi
  R "$A";;
look)
  R "grep -E 'armed|fixture|start |startup|dumped|RUN.md5|slim|ALL DONE|HOLD|FAIL' $Q/launch.log | cut -c1-240; cat $Q/dlogs/slim_$N.log 2>/dev/null | cut -c1-200; grep -h '^dumped ' $Q/dlogs/dump_*.stdout 2>/dev/null | cut -c1-140; grep -oE ':[0-7]:[0-9]+:dump_$N(\.swad)?' $Q/gpumem.log 2>/dev/null | awk -F: '{if (\$3 > p[\$4]) p[\$4] = \$3} END {for (k in p) print \"peak\", k, p[k], \"MiB\"}'; ls $Q/HOLD 2>/dev/null";;
stop)
  o=$(R "tmux has-session -t '=$SES' 2>/dev/null && echo SES_ALIVE || echo SES_GONE; echo \"lane \$(grep -c 'fixture $N on GPU' $Q/launch.log 2>/dev/null) gpu \$(ls $Q/pids/*.gpu 2>/dev/null | wc -l) hold \$(ls $Q/HOLD 2>/dev/null | wc -l)\"") || no "ssh failed"
  echo "$o"
  case "$o" in *SES_ALIVE*) ;; *) no "tmux session $SES is not alive on cv02 (nothing to stop)";; esac
  echo "$o" | grep -qx "lane 0 gpu 0 hold 0" || no "the fixture took a lane, or a HOLD is set in $Q: nothing is stopped (a running chain ends by itself)"
  K="touch $Q/HOLD; sleep 20; if [ \"\$(grep -c 'fixture $N on GPU' $Q/launch.log)\" = 0 ] && [ \"\$(ls $Q/pids/*.gpu 2>/dev/null | wc -l)\" = 0 ]; then tmux kill-session -t '=$SES'; sleep 2; rm -f $Q/HOLD; tmux has-session -t '=$SES' 2>/dev/null && echo STILL_ALIVE || echo STOPPED; else rm -f $Q/HOLD; echo TOOK_LANE; fi"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: $K"; exit 0; fi
  o=$(R "$K"); echo "$o"
  case "$o" in STOPPED) echo "stopped: tmux session $SES ended (its queue and logger with it); no dump had started; the fixture files stay (step clean)";;
    TOOK_LANE) no "the fixture took a lane in the last seconds: nothing was stopped, the HOLD is removed, the chain runs to its end";;
    *) no "stop not confirmed ('$o'); look at tmux session $SES on cv02";; esac;;
clean)
  M=dumps/elbench1/swad_const_pf_v11; LIST="$QC/experiments/$N $QC/$M/$N $QC/$M/$N.swad $QC/runs/$N $Q"
  [ "$Q" = /tmp/noob_el/bench_q/c3lane_smoke ] || no "queue dir is not the test's"
  o=$(R "tmux has-session -t '=$SES' 2>/dev/null && echo SES_ALIVE; p=\$(cat $Q/queue.pid 2>/dev/null); [ -n \"\$p\" ] && kill -0 \$p 2>/dev/null && echo QUEUE_ALIVE; echo \"listed \$(grep -cE '  (experiments/$N|$M/$N(\\.swad)?|runs/$N)(/|\$)' $QC/CODE.md5)\"; for d in $LIST; do [ -e \$d ] && echo \"have \$d: \$(find \$d -type f | wc -l) files, \$(du -sm \$d | cut -f1) MB\"; done; true") || no "ssh failed"
  echo "$o"
  case "$o" in *SES_ALIVE*|*QUEUE_ALIVE*) no "the test's tmux session or queue process is alive (wait for its end line, or use step stop)";; esac
  echo "$o" | grep -qx "listed 0" || no "a path of $QC/CODE.md5 lies inside a folder of the list (or CODE.md5 is unreadable): nothing is removed"
  echo "$o" | grep -q "^have " || { echo "nothing of the test exists on cv02; nothing to remove"; exit 0; }
  K="for d in $LIST; do [ -e \$d ] && rm -rf -- \$d && echo \"removed \$d\"; done; cd $QC && md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo CODE_OK"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: $K"; exit 0; fi
  o=$(R "$K"); echo "$o"
  case "$o" in *CODE_OK*) echo "clean done; $QC/CODE.md5 still checks";; *) no "after the removal $QC/CODE.md5 does NOT check: do not arm with this QC";; esac;;
*) no "unknown step";;
esac
