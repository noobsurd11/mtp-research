#!/bin/bash
# Wave 2a follow-up (lead, 16 Nov 2026): w2a_softband_f1_s6 was stopped by the auto-stop guard on 16 Nov 04:40:42 at about
# step 12,500 of 20,000 (another GPU job squeezed free memory under 2,048 MiB; bq/w2a2/autostop.log). The queue never
# restarts a stopped run, and its dump job in the w2a2 chain fails on bench_infer's step assert. This queue trains that one
# run again from step 0 and dumps it: the two reviewed job lines, unchanged (taken from bq/w2a2/jobs.txt dde618e0 and
# bq/w2a2/dump/jobs.txt 0bcef536), same code c57508e, same card, root, gate and dump command.
# Runs once, after the LOSO-2 chain (waiter harness/udev/wait_then_arm.sh). Before arming it moves the stopped folder aside
# (kept). Every check that fails stops with one line and starts nothing.
set -u
E=/home/noob/work/bench_wt_w2/experiments; R=w2a_softband_f1_s6; S=stopped_20261116_0440
no(){ echo "w2a3 launch: REFUSED: $*"; exit 1; }
grep -q "chain done" /home/noob/work/bq/w2a2/chain.log || no "the w2a2 chain has not written 'chain done'"
[ -z "$(ps -eo comm,args | awk '$1 ~ /^python/ && /run_name=w2a_/')" ] || no "a w2a training process is alive"
[ ! -e /home/noob/work/bench_dumps/w2a/elbench1/soft_band_jml/$R ] || no "a dump folder of $R exists"
if [ -e $E/$R ] || [ -e $E/$R.stdout ]; then
  [ "$(grep -c 'step 20000/20000' $E/$R.stdout)" = 0 ] || no "$R has a final-step line (not the stopped run)"
  [ ! -e $E/$R.$S ] && [ ! -e $E/$R.$S.stdout ] || no "$E/$R.$S exists"
  mv $E/$R $E/$R.$S && mv $E/$R.stdout $E/$R.$S.stdout || no "move aside failed"
  echo "w2a3 launch: moved aside $R -> $R.$S (kept)"
fi
export Q=/home/noob/work/bq/w2a3 SES=bench_q_w2a3 DEPLOY=c57508ec458b54d935a8c3ffcfe722ff2acadb38 \
  JOBS_MD5=7829c813af7164aa7194ea3be6f17f99 DJOBS_MD5=65e22b458dfe04d334c48c723a3286cc REPO=/home/noob/work/bench_wt_w2 MAXH=120
exec bash $REPO/bench/q/bench_setup.sh
