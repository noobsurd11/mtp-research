#!/bin/bash
# c3swad: chain test of the patched cv02 queue script (bench/q/cv02/cq.sh + cq_setup.sh) in a sandbox on gaint.
# cq.sh is run for real to its end line ("BENCH CV02 Q ALL DONE"). Stubs stand in for everything outside the script:
#   python  (card calls, train.py, bench_infer.py, slim_ckpt.py, cvcard.py: they write small text files and log their
#            arguments), nvidia-smi (2 GPUs, 48 GB free, no other user), tmux (T6 only), and a `sleep` as gpumem logger.
# No real python, torch, GPU or nvidia-smi is used; nothing outside the work dir is written; the only signal sent is a
# kill of the test's own `sleep` logger PIDs. The one edit to each script copy is the '. /tmp/noob_el/env.sh' line.
# Tests:
#   T1 patched, QC unset: one plain job (9 fields, logp 1) and one job with the 10th field "swad" (logp 0).
#   T2 UNPATCHED, the same plain job: its rendered lines and RUN.md5 must equal T1's (no change without the field).
#   T3 patched, the further dump fails (stub exit 1): no slim, no RUN.md5, lane released, queue ends.
#   T4 patched, QC != B (queue code in its own dir): slim_ckpt.py, cvcard.py and the cv02 card variant come from QC,
#      training and dumps run in B; RUN.md5 of the swad job equals T1's.
#   T5 UNPATCHED with the 10-field line: refused at arming, nothing started (a forgotten QC fails safe).
#   T6 cq_setup.sh old against new with a stub tmux: same commands without QC; with QC the commands use QC's scripts;
#      a GPUS list is handed on to cq.sh (the dump dry test on cv02 uses it).
# Usage: OLD=<tree at 89b9ea5> NEW=<patched tree> nice -n 19 bash c3swad_chain_test.sh <new work dir>
set -u
OLD=${OLD:?unpatched tree}; NEW=${NEW:?patched tree}; W=${1:?work dir (must not exist)}
[ -e "$W" ] && { echo "REFUSED: $W exists"; exit 1; }
mkdir -p $W/bin $W/fail || exit 1
W=$(cd $W && pwd); export STUB_FAIL=$W/fail
ENVL='. /tmp/noob_el/env.sh'
for t in $OLD $NEW; do [ "$(grep -cF "$ENVL" $t/bench/q/cv02/cq.sh)" = 1 ] || { echo "env line not found once in $t"; exit 1; }; done
NP=0; NF=0
ck(){ if eval "$2"; then NP=$((NP+1)); echo "PASS $1"; else NF=$((NF+1)); echo "FAIL $1   [$2]"; fi; }

cat > $W/bin/nvidia-smi <<'EOF'
#!/bin/bash
# stub: any GPU index, 48,000 MiB free, no compute apps
i=""; p=""; for x in "$@"; do [ "$p" = -i ] && i=$x; p=$x; done
case "$*" in *--query-gpu=uuid*) echo "GPU-stub-$i";; *--query-gpu=memory.free*) echo 48000;; *--query-compute-apps=*) :;; *) exit 1;; esac
EOF
cat > $W/bin/tmux <<'EOF'
#!/bin/bash
# stub: no session exists; new-session / new-window only log their command (last argument)
case "$1" in has-session) exit 1;; new-session|new-window) echo "$1: ${@: -1}" >> "$TMUXLOG";; esac; exit 0
EOF
cat > $W/python <<'EOF'
#!/bin/bash
# stub python for the chain sandbox
log(){ echo "$*" >> "$STUBLOG"; }
if [ "$1" = -m ]; then
  case "$3" in validate) exit 0;;
    opts) shift 4; s=""; n=""; r=""; while [ $# -gt 0 ]; do case "$1" in --seed) s=$2;; --run-name) n=$2;; --data-root) r=$2;; esac; shift 2; done
          echo "seed=$s run_name=$n data.root=$r"; exit 0;;
    cfgcheck) echo "config OK (= card)"; exit 0;; esac; exit 9
elif [ "$1" = -c ]; then
  case "$4" in memory.gate_mib) echo 9000;; config) echo configs/base.yaml;; name) echo stub_method;; weights_key) echo swad_bn;;
    readouts) echo "[{'name': 'raw', 'weights_key': 'model'}, {'name': 'swad', 'weights_key': 'swad'}, {'name': 'swad_bn', 'weights_key': 'swad_bn'}]";;
    *) exit 9;; esac; exit 0
elif [ "$2" = scripts/train.py ]; then
  n=""; r=""; for x in "$@"; do case "$x" in run_name=*) n=${x#run_name=};; data.root=*) r=${x#data.root=};; esac; done
  log "train cwd=$PWD gpu=$CUDA_VISIBLE_DEVICES $n"
  mkdir -p experiments/$n/checkpoints; echo "run_name: $n" > experiments/$n/config_used.yaml
  echo "Labelled: $(grep -c . $r/splits/train.txt) ($r/splits/train.txt)  unlabelled: 0 (-)  val: $(grep -c . $r/splits/val.txt)  test: $(grep -c . $r/splits/test.txt)"
  sleep 4; echo "latest of $n" > experiments/$n/checkpoints/latest.pth
  case "$n" in *swad*) echo '{"step": 20000}' > experiments/$n/enc_probe.jsonl;; esac
  echo "step 20000/20000"; exit 0
elif [ "$2" = scripts/bench_infer.py ]; then
  shift 2; wk=auto; lp=0
  while [ $# -gt 0 ]; do case "$1" in --set) set=$2;; --dumps) dumps=$2;; --method) meth=$2;; --run-id) rid=$2;; --weights-key) wk=$2;; --bench-run) br=$2;; --logp) lp=1;; esac; shift; done
  echo "BENCH_START: run=$br"; log "dump cwd=$PWD gpu=$CUDA_VISIBLE_DEVICES run-id=$rid key=$wk logp=$lp bench-run=$br"
  [ -e "$STUB_FAIL/$br" ] && { sleep 3; echo "Traceback (stub failure)"; exit 1; }
  d=$dumps/elbench1/$meth/$rid/$set; [ -e $d ] && { echo "refuse: $d exists"; exit 1; }
  mkdir -p $d; echo "cell 0 of $rid key $wk logp $lp" > $d/c0.npz; echo "cell 1 of $rid key $wk" > $d/c1.npz
  echo "{\"run_id\": \"$rid\", \"weights_key\": \"$wk\"}" > $d/manifest.json
  sleep 3; echo "dumped $rid $set: 2 cells, key $wk"; exit 0
else
  case "$1" in */cvcard.py) log "cvcard $*"; exit 0;;
    */slim_ckpt.py) log "slim cwd=$PWD $*"; r=$3; [ -e $r/checkpoints/slim.pth ] && exit 1
      echo "slim of $(cat $r/checkpoints/latest.pth) keys ${5:-all}" > $r/checkpoints/slim.pth; echo "slim $r keys ${5:-all}"; exit 0;; esac
  exit 9
fi
EOF
chmod +x $W/bin/nvidia-smi $W/bin/tmux $W/python
export PATH=$W/bin:$PATH
[ "$(command -v nvidia-smi)" = $W/bin/nvidia-smi ] || { echo "stub nvidia-smi is not first in PATH"; exit 1; }

m5(){ md5sum < "$1" | cut -c1-32; }
mroot(){ local r=$1; mkdir -p $r/splits; printf 'a\nb\nc\n' > $r/splits/train.txt; printf 'd\ne\n' > $r/splits/val.txt; cp $r/splits/val.txt $r/splits/test.txt
  (cd $r && md5sum splits/train.txt splits/val.txt splits/test.txt > SPLITS.md5 && md5sum splits/train.txt > DATA_MANIFEST.md5); }
mkdir -p $W/data/meta $W/data/roots $W/data_v3/roots; echo x > $W/data/meta/forbidden_v1.txt
(cd $W/data && md5sum meta/forbidden_v1.txt > DEPLOY.md5)
mroot $W/data/roots/cv5v2_v11_f0; mroot $W/data/roots/cv5v2_v1_f1; mroot $W/data_v3/roots/cv5v3_v11_f2
(cd $W/data/roots && md5sum cv5v2_v11_f0/SPLITS.md5 cv5v2_v1_f1/SPLITS.md5 > ROOTS_cv5v2_v11.md5 && md5sum cv5v2_v1_f1/SPLITS.md5 > ROOTS_cv5v2_v1.md5)
(cd $W/data_v3/roots && md5sum cv5v3_v11_f2/SPLITS.md5 > ROOTS_cv5v3_v11.md5)
DEP=0000000000000000000000000000000000000000
# code TREE DIR: a deploy-like dir with the queue code of TREE (env line neutralised), REVISION and CODE.md5
code(){ local t=$1 d=$2; mkdir -p $d/bench/q/cv02 $d/bench/methods_cv02; cp $t/bench/q/bench_lib.sh $d/bench/q/
  for f in cq.sh cq_setup.sh cq_gpumem.sh cvcard.py slim_ckpt.py; do cp $t/bench/q/cv02/$f $d/bench/q/cv02/; done
  sed -i "s#^$ENVL.*#:#" $d/bench/q/cv02/cq.sh
  [ -f $t/bench/methods_cv02/swad_const_pf_v11.yaml ] && cp $t/bench/methods_cv02/swad_const_pf_v11.yaml $d/bench/methods_cv02/
  echo $DEP > $d/REVISION; (cd $d && find bench -type f | sort | xargs md5sum > CODE.md5); }
ROOT=$W/data_v3/roots/cv5v3_v11_f2; CARD=bench/methods/swad_const_pf_v11.yaml
PLAIN="c3_p_f2_s5|$CARD|5|$ROOT|2|9000|5262|1|"
SWAD="c3s_swad_f2_s5|$CARD|5|$ROOT|2|11000|5262|0||swad"
SWADF="c3s_swadfail_f2_s6|$CARD|6|$ROOT|2|11000|5262|0||swad"
# runq TAG B CQ [QC] -- job lines on stdin; runs the queue to its end (timeout 300 s)
runq(){ local tag=$1 b=$2 cq=$3 qc=${4:-} q=$W/q_$1 lp
  mkdir -p $q; cat > $q/jobs.txt; echo 1 > $q/LPG; echo 8 > $q/MAXC
  sleep 900 & lp=$!; echo $lp > $q/gpumem.pid
  ( export B=$b Q=$q JOBS_MD5=$(m5 $q/jobs.txt) DEPLOY=$DEP DATA_MD5=$(m5 $W/data/DEPLOY.md5) DATA=$W/data DATA_V3=$W/data_v3 \
      P=$W/python GPUS="0 1" GAPSEC=1 POLL=1 LIVE_WAIT=30 STUBLOG=$W/stub_$tag.log
    [ -n "$qc" ] && export QC=$qc || unset QC
    timeout 300 bash $cq > $q/stdout 2>&1; echo $? > $q/rc )
  kill $lp 2>/dev/null; wait $lp 2>/dev/null; }

code $NEW $W/B1; code $OLD $W/B2; code $NEW $W/B3; code $OLD $W/B4; code $NEW $W/QC; code $OLD $W/B5
touch $STUB_FAIL/dump_c3s_swadfail_f2_s6.swad
qcsnap(){ (cd $W/QC && find . -type f | LC_ALL=C sort | xargs md5sum | md5sum | cut -c1-32); }; QC0=$(qcsnap)
echo "[$(date '+%F %T')] start; old cq $(m5 $OLD/bench/q/cv02/cq.sh | cut -c1-8) new cq $(m5 $NEW/bench/q/cv02/cq.sh | cut -c1-8); T1..T5 run side by side"
printf '%s\n%s\n' "$PLAIN" "$SWAD" | runq t1 $W/B1 $W/B1/bench/q/cv02/cq.sh &
printf '%s\n' "$PLAIN" | runq t2 $W/B2 $W/B2/bench/q/cv02/cq.sh &
printf '%s\n' "$SWADF" | runq t3 $W/B3 $W/B3/bench/q/cv02/cq.sh &
printf '%s\n' "$SWAD" | runq t4 $W/B4 $W/QC/bench/q/cv02/cq.sh $W/QC &
printf '%s\n' "$SWAD" | runq t5 $W/B5 $W/B5/bench/q/cv02/cq.sh &
wait
echo "[$(date '+%F %T')] queues ended: rc t1 $(cat $W/q_t1/rc) t2 $(cat $W/q_t2/rc) t3 $(cat $W/q_t3/rc) t4 $(cat $W/q_t4/rc) t5 $(cat $W/q_t5/rc)"

L1=$W/q_t1/launch.log; R1=$W/B1/runs; S1=$W/stub_t1.log; n=c3s_swad_f2_s5; p=c3_p_f2_s5
echo "--- T1 patched, QC unset"
ck "T1 end line: 2 trained, 2 dumped (usual dumps), 2 RUN.md5 of 2 jobs" 'grep -q "BENCH CV02 Q ALL DONE (2 trained rc 0, 2 dumped rc 0, 2 RUN.md5 of 2 jobs" $L1'
ck "T1 no HOLD, no FAIL line" '[ ! -e $W/q_t1/HOLD ] && ! grep -qiE "FAIL|HOLD|MISMATCH" $L1'
ck "T1 rendered: 5 lines, one further dump line" '[ "$(wc -l < $W/q_t1/jobs_rendered.txt)" = 5 ] && [ "$(grep -c "^dump_$n\.swad|" $W/q_t1/jobs_rendered.txt)" = 1 ]'
ck "T1 further dump command = the usual one + run id, key and job name" '[ "$(grep "^dump_$n|" $W/q_t1/jobs_rendered.txt | cut -d"|" -f2- | sed "s# --run-id $n # --run-id $n.swad --weights-key swad #; s#--bench-run dump_$n\$#--bench-run dump_$n.swad#")" = "$(grep "^dump_$n\.swad|" $W/q_t1/jobs_rendered.txt | cut -d"|" -f2-)" ]'
ck "T1 dumps of the swad job: usual (key auto, no logp) then swad, same GPU as training" '[ "$(grep -E "^(train|dump) .* ?($n|run-id=$n)" $S1 | sed -E "s/cwd=[^ ]* //" | tr "\n" ";")" = "$(g=$(cat $W/q_t1/pids/$n.gpu); echo "train gpu=$g $n;dump gpu=$g run-id=$n key=auto logp=0 bench-run=dump_$n;dump gpu=$g run-id=$n.swad key=swad logp=0 bench-run=dump_$n.swad;")" ]'
ck "T1 log order: trained, usual dump, further dump, RUN.md5" '[ "$(grep -oE "(trained|start|dumped|RUN.md5) (dump_)?$n(\.swad)?( rc=0)?" $L1 | tr "\n" ";")" = "start $n;trained $n rc=0;start dump_$n;dumped dump_$n rc=0;start dump_$n.swad;dumped dump_$n.swad rc=0;RUN.md5 $n rc=0;" ]'
ck "T1 both dumps passed the BENCH_START check" '[ "$(grep -c "dump_$n\(\.swad\)\? startup line OK: BENCH_START: run=dump_$n" $L1)" = 2 ]'
ck "T1 slim of the swad job keeps swad_bn,swad; slim of the plain job has no --keys" 'grep -qx "slim cwd=$W/B1 $W/B1/bench/q/cv02/slim_ckpt.py --run experiments/$n --keys swad_bn,swad" $S1 && grep -qx "slim cwd=$W/B1 $W/B1/bench/q/cv02/slim_ckpt.py --run experiments/$p" $S1'
ck "T1 RUN.md5 of the swad job: first 4 lines config, slim, LATEST.md5, enc_probe; then the 6 files of both dump dirs (their order follows the locale)" '[ "$(awk "{print \$2}" $R1/$n/RUN.md5 | head -4 | tr "\n" " ")" = "experiments/$n/config_used.yaml experiments/$n/checkpoints/slim.pth runs/$n/LATEST.md5 experiments/$n/enc_probe.jsonl " ] && [ "$(awk "{print \$2}" $R1/$n/RUN.md5 | tail -n +5 | LC_ALL=C sort | tr "\n" " ")" = "dumps/elbench1/stub_method/$n.swad/cv5v3_f2/c0.npz dumps/elbench1/stub_method/$n.swad/cv5v3_f2/c1.npz dumps/elbench1/stub_method/$n.swad/cv5v3_f2/manifest.json dumps/elbench1/stub_method/$n/cv5v3_f2/c0.npz dumps/elbench1/stub_method/$n/cv5v3_f2/c1.npz dumps/elbench1/stub_method/$n/cv5v3_f2/manifest.json " ]'
ck "T1 RUN.md5 of both jobs checks (md5sum -c)" '(cd $W/B1 && md5sum -c --quiet runs/$n/RUN.md5 && md5sum -c --quiet runs/$p/RUN.md5)'
ck "T1 plain job: one dump (logp 1, key auto), RUN.md5 6 lines, no enc_probe line" '[ "$(grep -c "run-id=$p" $S1)" = 1 ] && grep -q "run-id=$p key=auto logp=1" $S1 && [ "$(wc -l < $R1/$p/RUN.md5)" = 6 ] && ! grep -q enc_probe $R1/$p/RUN.md5'
ck "T1 the two jobs ran on different GPUs (LPG 1)" '[ "$(cat $W/q_t1/pids/$n.gpu)" != "$(cat $W/q_t1/pids/$p.gpu)" ]'
ck "T1 only GPUs named in GPUS (0 1) were used, for training and for every dump" '[ -z "$(cat $W/q_t1/pids/*.gpu | grep -v "^[01]\$")" ] && [ -z "$(grep -oE "gpu=[0-9]+" $S1 | grep -v "gpu=[01]\$")" ]'
ck "T1 lanes released (.end for both)" '[ -e $W/q_t1/pids/$n.end ] && [ -e $W/q_t1/pids/$p.end ]'
echo "--- T2 unpatched, plain job"
ck "T2 end line: 1 trained, 1 dumped, 1 RUN.md5" 'grep -q "BENCH CV02 Q ALL DONE (1 trained rc 0, 1 dumped rc 0, 1 RUN.md5 of 1 jobs" $W/q_t2/launch.log'
ck "T2 = T1: RUN.md5 of the plain job byte-equal" 'cmp -s $W/B2/runs/$p/RUN.md5 $R1/$p/RUN.md5'
ck "T2 = T1: rendered lines of the plain job equal (deploy dir name aside)" '[ "$(sed "s#$W/B2#B#g" $W/q_t2/jobs_rendered.txt)" = "$(grep -E "^(dump_)?$p\|" $W/q_t1/jobs_rendered.txt | sed "s#$W/B1#B#g")" ]'
ck "T2 = T1: stub calls of the plain job equal (deploy dir and GPU aside)" '[ "$(grep -E "$p( |\$)" $W/stub_t2.log | sed -E "s#$W/B2#B#g; s/gpu=[0-9]/gpu=G/")" = "$(grep -E "$p( |\$)" $S1 | sed -E "s#$W/B1#B#g; s/gpu=[0-9]/gpu=G/")" ]'
ck "T2 = T1: log lines of the plain job equal (time, pids, md5 of cmdline, GPU and lane counts aside)" '[ "$(grep -E "(dump_)?$p( |:|\$)" $W/q_t2/launch.log | grep -v "waits" | sed -E "s/^\[[^]]*\] //; s#$W/B2#B#g; s/GPU [0-9]/GPU G/g; s/pid ((dump_)?$p) [0-9]+/pid \1 N/; s/parent [0-9]+/parent N/; s/\([0-9a-f]{8}\)/(M)/; s/all [0-9]+\)/all N)/; s/:  *PID .*//" )" = "$(grep -E "(dump_)?$p( |:|\$)" $L1 | grep -v "waits" | sed -E "s/^\[[^]]*\] //; s#$W/B1#B#g; s/GPU [0-9]/GPU G/g; s/pid ((dump_)?$p) [0-9]+/pid \1 N/; s/parent [0-9]+/parent N/; s/\([0-9a-f]{8}\)/(M)/; s/all [0-9]+\)/all N)/; s/:  *PID .*//")" ]'
echo "--- T3 patched, the further dump fails"
L3=$W/q_t3/launch.log; f=c3s_swadfail_f2_s6
ck "T3 usual dump rc 0, further dump rc 1" 'grep -q "dumped dump_$f rc=0:" $L3 && grep -q "dumped dump_$f.swad rc=1:" $L3'
ck "T3 no slim call, no slim.pth, no RUN.md5" '! grep -q "^slim " $W/stub_t3.log && [ ! -e $W/B3/experiments/$f/checkpoints/slim.pth ] && [ ! -e $W/B3/runs/$f ]'
ck "T3 lane released, queue ended: 1 trained, 1 dumped, 0 RUN.md5" '[ -e $W/q_t3/pids/$f.end ] && grep -q "BENCH CV02 Q ALL DONE (1 trained rc 0, 1 dumped rc 0, 0 RUN.md5 of 1 jobs" $L3'
echo "--- T4 patched, QC != B"
L4=$W/q_t4/launch.log; S4=$W/stub_t4.log
ck "T4 armed line names the queue code dir" 'grep -q "cv02 q armed: 1 jobs .*; queue code QC $W/QC (0000000, CODE.md5 OK)" $L4'
ck "T4 end line: 1 trained, 1 dumped, 1 RUN.md5" 'grep -q "BENCH CV02 Q ALL DONE (1 trained rc 0, 1 dumped rc 0, 1 RUN.md5 of 1 jobs" $L4'
ck "T4 cvcard.py and the cv02 variant from QC; card from B (relative path, cwd B)" 'grep -qx "cvcard $W/QC/bench/q/cv02/cvcard.py $CARD $W/QC/bench/methods_cv02/swad_const_pf_v11.yaml" $S4'
ck "T4 slim_ckpt.py from QC, run in B, keys swad_bn,swad" 'grep -qx "slim cwd=$W/B4 $W/QC/bench/q/cv02/slim_ckpt.py --run experiments/$n --keys swad_bn,swad" $S4'
ck "T4 training and both dumps ran in B" '[ "$(grep -cE "^(train|dump) cwd=$W/B4 " $S4)" = 3 ] && [ "$(grep -cE "^(train|dump) " $S4)" = 3 ]'
ck "T4 RUN.md5 of the swad job = T1's" 'cmp -s $W/B4/runs/$n/RUN.md5 $R1/$n/RUN.md5'
ck "T4 nothing written into QC (file list and contents as before the run)" '[ "$(qcsnap)" = "$QC0" ]'
echo "--- T5 unpatched script, 10-field line"
ck "T5 refused at arming, nothing rendered or started" '[ "$(cat $W/q_t5/rc)" = 1 ] && grep -q "extra .|swad. not allowed; not starting" $W/q_t5/launch.log && [ ! -e $W/q_t5/jobs_rendered.txt ] && [ ! -s $W/stub_t5.log -o "$(grep -cE "^(train|dump|slim)" $W/stub_t5.log)" = 0 ] && [ -z "$(ls $W/B5/experiments)" ]'
echo "--- T6 cq_setup.sh with a stub tmux"
setup(){ local tag=$1 b=$2 qc=${3:-} gp=${4:-} q=$W/qs_$1; mkdir -p $q; printf '%s\n' "$PLAIN" > $q/jobs.txt; echo 1 > $q/LPG
  ( export B=$b Q=$q SES=bench_q_t DEPLOY=$DEP JOBS_MD5=$(m5 $q/jobs.txt) DATA_MD5=x TMUXLOG=$W/tmux_$tag.log
    [ -n "$qc" ] && export QC=$qc || unset QC
    [ -n "$gp" ] && export GPUS="$gp" || unset GPUS
    bash ${qc:-$b}/bench/q/cv02/cq_setup.sh > $q/stdout 2>&1; echo $? > $q/rc ); }
code $OLD $W/B6; code $NEW $W/B7; code $OLD $W/B8
setup s_old $W/B6 & setup s_new $W/B7 & setup s_qc $W/B8 $W/QC & wait
ck "T6 without QC: old and new cq_setup.sh give the same tmux commands" '[ "$(sed "s#$W/B6#B#g; s#$W/qs_s_old#Q#g" $W/tmux_s_old.log)" = "$(sed "s#$W/B7#B#g; s#$W/qs_s_new#Q#g" $W/tmux_s_new.log)" ] && [ "$(wc -l < $W/tmux_s_new.log)" = 2 ]'
ck "T6 with QC: logger and queue script from QC, QC passed on, B unchanged" 'grep -qx "new-session: Q=$W/qs_s_qc nice -n 19 bash $W/QC/bench/q/cv02/cq_gpumem.sh" $W/tmux_s_qc.log && grep -qx "new-window: B=$W/B8 Q=$W/qs_s_qc JOBS_MD5=$(m5 $W/qs_s_qc/jobs.txt) DEPLOY=$DEP DATA_MD5=x QC=$W/QC bash $W/QC/bench/q/cv02/cq.sh" $W/tmux_s_qc.log'
code $NEW $W/B10; setup s_gpus $W/B10 "" "1 3"
ck "T6 a GPUS list is handed on to cq.sh" 'grep -q "^new-window: B=$W/B10 .* GPUS=.1 3. bash $W/B10/bench/q/cv02/cq.sh\$" $W/tmux_s_gpus.log'
echo x >> $W/QC/bench/q/bench_lib.sh; code $OLD $W/B9; setup s_bad $W/B9 $W/QC
ck "T6 with a changed file in QC: cq_setup.sh refuses, no tmux command" 'grep -q "cq_setup: REFUSED: QC $W/QC CODE.md5 check failed" $W/qs_s_bad/stdout && [ ! -e $W/tmux_s_bad.log ]'
echo "[$(date '+%F %T')] CHAIN TEST: $((NP+NF)) checks, $NP passed, $NF failed"
[ $NF = 0 ]
