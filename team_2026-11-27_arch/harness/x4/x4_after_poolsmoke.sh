#!/bin/bash
# x4 (lead order 28 Nov: stage P vfmctx f4, fullres_skip, POOLST, lowfreeze, geomaux). Runs on gaint in tmux
# bench_x4_after_poolsmoke. Waits for "trained smoke_x4_poolst_f0_s5" in cv02 x4_w1; then:
#  (1) peak P = max MiB of smoke_x4_poolst_f0_s5 in x4_w1/gpumem.log (the smoke is inside the PF freeze); full-run estimate
#      P + 748 (COMBO smoke-to-run, E), gate = estimate + 2,048; refuses (no append) if the smoke rc is not 3 or P is empty;
#  (2) appends x4_poolst_f0..f4_s5 (seed 5, commit 8da53f6) and arms its stage-P auto read;
#  (3) appends x4_lowfreeze2_f0..f4_s5 (same card and commit as the skipped x4_lowfreeze jobs, gate 11,434) and arms its read.
set -u
H=$(dirname "$(readlink -f "$0")"); L=$H/evidence/after_poolsmoke.log; X=8da53f67cfe2cb9162aa785da5c513b97ceff572; LX=0d4e43137764752970fe28fdadd1959441f8c137
P=/home/noob/work/el-fault-detection/.venv/bin/python
SC(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 "$1"; }
say(){ echo "[$(date '+%F %T')] $*" >> $L; }
say "armed: waiting for trained smoke_x4_poolst_f0_s5"
until t=$(SC "grep 'trained smoke_x4_poolst_f0_s5' /tmp/noob_el/bench_q/x4_w1/launch.log") && [ -n "$t" ]; do sleep 120; done
say "$t"
case "$t" in *" rc=3 "*) ;; *) say "REFUSED: smoke rc is not 3; nothing appended (lead decides)"; exit 1;; esac
pk=$(SC "grep -v '^#' /tmp/noob_el/bench_q/x4_w1/gpumem.log | tr ' ' '\n' | grep -E ':smoke_x4_poolst_f0_s5\$' | cut -d: -f3 | sort -n | tail -1")
case "$pk" in ''|*[!0-9]*) say "REFUSED: no peak for smoke_x4_poolst_f0_s5 in gpumem.log"; exit 1;; esac
est=$((pk + 748)); say "poolst smoke peak $pk MiB (E); full-run estimate $est (S, + 748); gate $((est + 2048))"
cd $H
$P x4_make_jobs.py --out jobs/w1_pool_p.tsv --seeds 5 --commit $X bench/methods/x4_poolst.yaml=poolst@$est >> $L 2>&1 || { say "make_jobs poolst failed"; exit 1; }
say "$(bash x4_queue.sh append w1 jobs/w1_pool_p.tsv 2>&1 | tail -1 | cut -c1-200)"
tmux has-session -t "=bench_x4_auto_poolst_p" 2>/dev/null || tmux new-session -d -s bench_x4_auto_poolst_p "bash $H/x4_auto_read.sh poolst_p w1 POOLST poolst x4_poolst swad P"
$P x4_make_jobs.py --out jobs/w1_lf2_p.tsv --seeds 5 --commit $LX bench/methods/x4_lowfreeze.yaml=lowfreeze2@9386 >> $L 2>&1 || { say "make_jobs lowfreeze2 failed"; exit 1; }
say "$(bash x4_queue.sh append w1 jobs/w1_lf2_p.tsv 2>&1 | tail -1 | cut -c1-200)"
tmux has-session -t "=bench_x4_auto_lowfreeze2_p" 2>/dev/null || tmux new-session -d -s bench_x4_auto_lowfreeze2_p "bash $H/x4_auto_read.sh lowfreeze2_p w1 LOWFREEZE lowfreeze2 x4_lowfreeze swad P"
say "AFTER POOLSMOKE DONE: poolst stage P and lowfreeze2 appended, auto reads armed"
