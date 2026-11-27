#!/bin/bash
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
# Steps: place (cv02 WRITE: fixture files and a smoke queue dir), arm (cv02 START), look (read only).
# DRY=1 prints every write or start instead of running it.
# Expected in the smoke queue's launch.log:
#   dump_dumptest_c3s_swad_f0 startup line OK: BENCH_START: run=dump_dumptest_c3s_swad_f0
#   dumped dump_dumptest_c3s_swad_f0 rc=0 ...          (dlogs: '107 cells, 132.6 MiB, ties 0, key swad_bn, step 20000, cuda/fp32')
#   dumped dump_dumptest_c3s_swad_f0.swad rc=0 ...     (dlogs: '107 cells, 132.2 MiB, ties 0, key swad, step 20000, cuda/fp32')
#   RUN.md5 dumptest_c3s_swad_f0 rc=0: 220 files       (config, slim, LATEST.md5, enc_probe.jsonl, 2 x (107 npz + manifest))
#   BENCH CV02 Q ALL DONE (0 trained rc 0, 1 dumped rc 0, 1 RUN.md5 of 1 jobs ...)
# and in dlogs/slim_dumptest_c3s_swad_f0.log: keys ['swad', 'swad_bn']. Peak of both dumps from gpumem.log (PF: 3,212 MiB).
set -u
STEP=${1:?step: place | arm | look}; QC=${QC:?cv02 deploy dir of the patched queue code}; DRY=${DRY:-0}
echo "$QC" | grep -qE '^/tmp/noob_el/bench_[0-9a-f]{7}$' && [ "$QC" != /tmp/noob_el/bench_89b9ea5 ] || { echo "REFUSED: QC must be the new deploy dir"; exit 1; }
SRC=/home/noob/work/bench_wt_w2/experiments/w2a_swad_f0_s5; N=dumptest_c3s_swad_f0
Q=/tmp/noob_el/bench_q/c3swad_smoke; SES=bench_q_c3swad_smoke
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
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: tar stream of config_used.yaml (root line -> /tmp/noob_el/bench_data/roots/cv5v2_v11_f0), enc_probe.jsonl, checkpoints/latest.pth to $QC/experiments/$N; mkdir $Q with jobs.txt ($JOB; md5 $JMD5), LPG 1, MAXC 1"; exit 0; fi
  T=$(mktemp -d) && mkdir -p $T/$N/checkpoints && sed 's#root: /home/noob/work/bench_data/roots/cv5v2_v11_f0$#root: /tmp/noob_el/bench_data/roots/cv5v2_v11_f0#' $SRC/config_used.yaml > $T/$N/config_used.yaml \
    && cp $SRC/enc_probe.jsonl $T/$N/ && ln -s $SRC/checkpoints/latest.pth $T/$N/checkpoints/latest.pth || no "staging failed"
  [ "$(diff $SRC/config_used.yaml $T/$N/config_used.yaml | grep -c '^[<>]')" = 2 ] || no "config rewrite changed more than the root line"
  tar -C $T -chf - $N | ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $QC/experiments/$N && tar -x -C $QC/experiments && md5sum < $QC/experiments/$N/checkpoints/latest.pth | cut -c1-32" | grep -qx 1f0fdb30e87e81551e611856f8f3df75 || no "fixture stream or md5 failed"
  rm -rf $T
  echo "$JOB" | ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $Q && mkdir $Q && cat > $Q/jobs.txt && echo 1 > $Q/LPG && echo 1 > $Q/MAXC && md5sum < $Q/jobs.txt | cut -c1-32" | grep -qx $JMD5 || no "queue dir not placed"
  echo "placed fixture $QC/experiments/$N (latest.pth md5 OK) and $Q (jobs md5 $JMD5; not armed)";;
arm)
  BQ=/tmp/noob_el/bench_q
  o=$(R "open=\" \$(for f in $BQ/*/pids/*.gpu; do [ -e \${f%.gpu}.end ] || cat \$f; done | tr '\n' ' ')\"; for g in 0 1 2 3 4 5 6 7; do case \"\$open\" in *\" \$g \"*) ;; *) echo -n \"\$g \";; esac; done; echo; for f in $BQ/*/pids/*.gpu; do [ -e \${f%.gpu}.end ] || echo \"open lane: GPU \$(cat \$f) \$(basename \${f%.gpu})\"; done") || no "ssh failed"
  G=$(echo "$o" | head -1); G=$(echo $G); echo "$o" | tail -n +2
  case "$G" in ""|*[!0-7\ ]*) no "no GPU without an open lane of one of our queues (list '$G'); try later";; esac
  echo "GPUs without an open lane of our queues (the test may use only these, and only under the lane rule): $G"
  A="B=$QC Q=$Q SES=$SES GPUS='$G' DEPLOY=\$(cat $QC/REVISION) JOBS_MD5=$JMD5 DATA_MD5=$DATA_MD5 bash $QC/bench/q/cv02/cq_setup.sh"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: $A"; exit 0; fi
  R "$A";;
look)
  R "grep -E 'armed|fixture|start |startup|dumped|RUN.md5|slim|ALL DONE|HOLD|FAIL' $Q/launch.log | cut -c1-240; cat $Q/dlogs/slim_$N.log 2>/dev/null | cut -c1-200; grep -h '^dumped ' $Q/dlogs/dump_*.stdout 2>/dev/null | cut -c1-140; grep -oE ':[0-7]:[0-9]+:dump_$N(\.swad)?' $Q/gpumem.log 2>/dev/null | awk -F: '{if (\$3 > p[\$4]) p[\$4] = \$3} END {for (k in p) print \"peak\", k, p[k], \"MiB\"}'; ls $Q/HOLD 2>/dev/null";;
*) no "unknown step";;
esac
