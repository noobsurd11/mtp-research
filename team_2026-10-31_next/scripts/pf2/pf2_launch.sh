#!/bin/bash
# PF2 launch on gaint (after coach's APPROVED line in protocol_PF2.md). Usage: GRN=<RN50 peak + 2048> GS=<scoring gate> bash pf2_launch.sh
# Starts three windows in tmux session pf2 (the gpumem logger window already runs): queue, g6, post (opening trigger).
set -eu
cd /home/noob/work/el_f3
: "${GRN:?}" "${GS:?}"
J=210d0d6fcc54c3effcc36893e0d51ad5
[ "$(md5sum < reports/pf2/pf2_jobs.txt | cut -c1-32)" = $J ]
kill -0 "$(cat reports/pf2/gpumem.pid)"
[ -e reports/pf2/smoke/ALLDONE ]
tmux has-session -t =pf2
for w in queue g6 post; do tmux list-windows -t =pf2 -F '#W' | grep -qx $w && { echo "window $w exists"; exit 1; }; done
echo "[$(date)] runner: PF2 launch (coach APPROVED; GRN $GRN, GS $GS, POLICY twohead, MAXC 3, MAXRN 1, G34 9000)" >> reports/pf2/launch.log
tmux new-window -d -t "=pf2:" -n queue "cd /home/noob/work/el_f3; POLICY=twohead MAXC=3 MAXRN=1 G34=9000 GRN=$GRN JOBS_MD5=$J bash reports/pf2/scripts/pf2_queue.sh; exec bash"
tmux new-window -d -t "=pf2:" -n g6 "cd /home/noob/work/el_f3; bash reports/pf2/scripts/pf2_g6.sh; exec bash"
tmux new-window -d -t "=pf2:" -n post "cd /home/noob/work/el_f3; GS=$GS bash reports/pf2/scripts/pf2_postwatch.sh; exec bash"
sleep 5; tmux list-windows -t =pf2 -F '#I #W #{pane_pid}'; tail -5 reports/pf2/launch.log
