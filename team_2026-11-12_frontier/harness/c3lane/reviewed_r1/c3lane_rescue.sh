#!/bin/bash
# c3lane rescue (run by the LEAD on gaint, after the deploy of the new queue code QC): starts bench/q/cv02/cq_rescue.sh of
# QC on cv02 for waiting dumps of an older queue. One rescue at a time (the tool holds a lock in the rescue dir).
#   prep                    cv02 WRITE: rescue dir /tmp/noob_el/bench_q/c3rescue with SHARE_DUMP 10240 (the user's floor)
#   list                    cv02 READ ONLY: open lanes of c3all, c3all2, rows2 (run, GPU, training rc, chain pid alive), free
#                           memory per GPU, and the tool's file-list check (DRYLIST) on one finished run of each queue
#   run <queue> <run> [..]  cv02 START: tmux session bench_rescue_<queue> that runs the tool for these runs, in this order;
#                           output /tmp/noob_el/bench_q/c3rescue/<queue>.out, log .../rescue.log
#   look                    cv02 READ ONLY: outputs, log tail, HOLD
#   hold | unhold           cv02 WRITE: touch / remove c3rescue/HOLD (with HOLD no dump is started; a running dump goes on)
# Stop path: `hold`. A tool that waits for a lane may also be ended with its session (tmux kill-session -t '=bench_rescue_<queue>')
# while it waits: the stopped chain is recorded in <queue>/pids/<run>.rescued and a later `run` goes on from there.
# Switch sharing off at once: remove c3rescue/SHARE_DUMP (then the tool waits for a strict lane, as the old chain did).
# DRY=1 prints every cv02 write or start instead of running it.
set -u
STEP=${1:?step: prep | list | run <queue> <run> [...] | look | hold | unhold}; QC=${QC:?cv02 deploy dir of the new queue code}; DRY=${DRY:-0}
echo "$QC" | grep -qE '^/tmp/noob_el/bench_[0-9a-f]{7}$' || { echo "REFUSED: QC must be /tmp/noob_el/bench_<7 hex>"; exit 1; }
BQ=/tmp/noob_el/bench_q; RQ=$BQ/c3rescue; SD=10240; TOOL=$QC/bench/q/cv02/cq_rescue.sh
C=cv02@10.8.1.106; R(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; }
Wr(){ if [ $DRY = 1 ]; then echo "DRY, not run on cv02: $1"; else ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; fi; }
no(){ echo "REFUSED ($STEP): $*"; exit 1; }
case $STEP in
prep) R "test ! -e $RQ && echo FREE" | grep -qx FREE || no "$RQ exists"
  Wr "mkdir $RQ && echo $SD > $RQ/SHARE_DUMP && echo \"placed $RQ, SHARE_DUMP \$(cat $RQ/SHARE_DUMP)\"";;
list) R "nvidia-smi --query-gpu=index,name,memory.free --format=csv,noheader,nounits | tr '\n' ';'; echo; for q in c3all c3all2 rows2; do Q=$BQ/\$q; m=\$(cat \$Q/queue.pid 2>/dev/null); for f in \$Q/pids/*.gpu; do n=\$(basename \$f .gpu); [ -e \$Q/pids/\$n.end ] && continue; c=\$(grep \"^\$n chain \" \$Q/pids/subshells.txt | tail -1 | cut -d' ' -f3); echo \"\$q \$n GPU \$(cat \$f) training rc '\$(cat \$Q/pids/\$n.rc 2>/dev/null)' chain \$c \$(kill -0 \$c 2>/dev/null && [ \"\$(ps -o ppid= -p \$c | tr -d ' ')\" = \"\$m\" ] && echo alive-child-of-main || echo NOT-VERIFIED) dump started \$(ls \$Q/pids/dump_\$n.pid 2>/dev/null | wc -l)\"; done; s=\$(for n in \$(cut -d'|' -f1 \$Q/jobs.txt); do grep -q \"^dump_\$n|\" \$Q/jobs_rendered.txt && b=\$(grep \"^dump_\$n|\" \$Q/jobs_rendered.txt | sed -n \"s#.* --run \\([^ ]*\\)/experiments/\$n .*#\\1#p\") && [ -s \$b/runs/\$n/RUN.md5 ] && { echo \$n; break; }; done); [ -s $TOOL ] && [ -n \"\$s\" ] && DRYLIST=1 OQ=\$Q bash $TOOL \$s || echo \"\$q: no file-list check (tool not deployed at $TOOL, or no finished run)\"; done; echo \"rescue dir: \$(ls $RQ 2>/dev/null | tr '\n' ' ') SHARE_DUMP \$(cat $RQ/SHARE_DUMP 2>/dev/null)\"";;
run) q=${2:?queue}; shift 2; [ $# -ge 1 ] || no "no run name"; case "$q$*" in *[!A-Za-z0-9_\ ]*) no "bad queue or run name";; esac
  o=$(R "cd $QC && md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo CODE_OK; echo \"\$(md5sum < bench/q/cv02/cq_rescue.sh | cut -c1-32) \$(md5sum < bench/q/cv02/cq.sh | cut -c1-32) share \$(cat $RQ/SHARE_DUMP 2>/dev/null) ses \$(tmux has-session -t '=bench_rescue_$q' 2>/dev/null && echo yes || echo no) lock \$(flock -n $RQ/rescue.lock true 2>/dev/null && echo free || echo held) hold \$(ls $RQ/HOLD $BQ/$q/HOLD 2>/dev/null | wc -l)\"") || no "ssh failed"
  echo "$o"
  [ "$(echo $o)" = "CODE_OK 8710a7321e060a68e49823f94f3a2b06 4fc8d2c0f87c77b099e06164e6b513ea share $SD ses no lock free hold 0" ] || no "QC does not check or is not the reviewed queue code, or the rescue dir is not prepared (SHARE_DUMP $SD), or a rescue runs, or a HOLD is set"
  Wr "tmux new-session -d -s bench_rescue_$q 'OQ=$BQ/$q RQ=$RQ bash $TOOL $* > $RQ/$q.out 2>&1' && echo started bench_rescue_$q: $*";;
look) R "for f in $RQ/*.out; do [ -e \$f ] && { echo \"== \$f\"; cat \$f; }; done; echo '== rescue.log (tail)'; tail -15 $RQ/rescue.log 2>/dev/null; echo \"HOLD: \$(ls $RQ/HOLD 2>/dev/null | wc -l); sessions: \$(tmux ls 2>/dev/null | grep -o '^bench_rescue_[a-z0-9_]*' | tr '\n' ' ')\"";;
hold) Wr "touch $RQ/HOLD && echo HOLD set in $RQ";;
unhold) Wr "rm -f $RQ/HOLD && echo HOLD removed from $RQ";;
*) no "unknown step";;
esac
