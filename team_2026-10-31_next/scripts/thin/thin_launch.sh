#!/bin/bash
# THIN-B3 arming on gaint (after coach's APPROVED in protocol_thin_b3.md). Usage: DEPLOY=<hash> JOBS_MD5=<md5> M0B3=<8-char md5> GS=<MiB> bash thin_launch.sh
# Writes el_thin/REVISION (untracked, as el_f3) if absent, then tmux session "thin": gpumem logger, queue (waits for PF2 ALL TRAINED),
# opening trigger (waits for 15 rc 0 + PF2's opening rc 0).
set -eu
cd /home/noob/work/el_thin
: "${DEPLOY:?}" "${JOBS_MD5:?}" "${M0B3:?}" "${GS:?}"
[ "$(git rev-parse --short HEAD)" = "$DEPLOY" ] && [ "$(cat reports/thin/DEPLOY)" = "$DEPLOY" ] && [ -z "$(git status --short --untracked-files=no)" ]
[ -e REVISION ] || echo "$DEPLOY" > REVISION; [ "$(cat REVISION)" = "$DEPLOY" ]
[ "$(md5sum < reports/thin/q/thin_jobs.txt | cut -c1-32)" = "$JOBS_MD5" ]
[ "$(md5sum < scripts/b3/m0_audit_b3.py | cut -c1-8)" = "$M0B3" ]
tmux has-session -t =thin 2>/dev/null && { echo "tmux session thin exists"; exit 1; }
echo "[$(date)] runner: THIN-B3 armed (coach APPROVED; DEPLOY $DEPLOY, jobs $JOBS_MD5, m0_audit_b3 $M0B3, GS $GS)" >> reports/thin/q/launch.log
tmux new-session -d -s thin -n gpumem "cd /home/noob/work/el_thin; bash reports/thin/scripts/thin_gpumem.sh; exec bash"
sleep 3; kill -0 "$(cat reports/thin/q/gpumem.pid)"
tmux new-window -d -t "=thin:" -n queue "cd /home/noob/work/el_thin; DEPLOY=$DEPLOY JOBS_MD5=$JOBS_MD5 bash reports/thin/scripts/thin_queue.sh; exec bash"
tmux new-window -d -t "=thin:" -n post "cd /home/noob/work/el_thin; GS=$GS DEPLOY=$DEPLOY M0B3=$M0B3 bash reports/thin/scripts/thin_postwatch.sh; exec bash"
sleep 3; tmux list-windows -t =thin -F '#I #W #{pane_pid}'; tail -4 reports/thin/q/launch.log
