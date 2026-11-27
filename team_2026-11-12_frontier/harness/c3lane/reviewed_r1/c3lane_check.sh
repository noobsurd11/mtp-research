#!/bin/bash
# c3lane: checks before the launch steps (run by the LEAD on gaint). READ ONLY on both machines. Lines start with OK, FAIL,
# SKIP or INFO; the last line counts them. QC=<cv02 deploy dir of the new queue code> after the deploy; NEWQ (c3all3).
set -u
QC=${QC:-}; NEWQ=${NEWQ:-c3all3}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
WT=/home/noob/work/bench_wt_c3s; R=/home/noob/work/el_bench; BQ=/tmp/noob_el/bench_q; OQC=/tmp/noob_el/bench_5437778
C(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 "$1"; }
NO=0; NFL=0; NS=0
ok(){ NO=$((NO+1)); echo "OK   $*"; }; bad(){ NFL=$((NFL+1)); echo "FAIL $*"; }; skip(){ NS=$((NS+1)); echo "SKIP $*"; }
ck(){ if eval "$2"; then ok "$1"; else bad "$1"; fi; }
echo "[$(date '+%F %T')] c3lane check (QC '${QC:-none}', NEWQ $NEWQ)"
echo "--- 1 code"
ck "worktree $WT on bench_c3s at 5437778 or at its child with the c3lane commit, no tracked change" '[ "$(git -C $WT rev-parse --abbrev-ref HEAD)" = bench_c3s ] && [ "$(git -C $WT status --porcelain -uno | wc -l)" = 0 ] && { [ "$(git -C $WT rev-parse --short HEAD)" = 5437778 ] || [ "$(git -C $WT rev-parse --short HEAD^)" = 5437778 ]; }'
ck "c3lane.patch applies to a fresh archive of 5437778 and gives cq.sh 4fc8d2c0 and cq_rescue.sh 8710a732; only these two files differ" 'x=$(mktemp -d) && git -C $R archive 5437778 | tar -x -C $x && (cd $x && git apply $HERE/c3lane.patch && echo "4fc8d2c0f87c77b099e06164e6b513ea  bench/q/cv02/cq.sh
8710a7321e060a68e49823f94f3a2b06  bench/q/cv02/cq_rescue.sh" | md5sum -c --quiet -); rc=$?; rm -rf $x; [ $rc = 0 ]'
ck "strict lane code untouched: from '# ---- lanes' to the line of logger_ok the patched cq.sh equals 5437778 (5222150b)" 'x=$(mktemp -d) && git -C $R archive 5437778 bench/q/cv02/cq.sh | tar -x -C $x && cp $x/bench/q/cv02/cq.sh $x/old && (cd $x && git apply $HERE/c3lane.patch) && cmp -s <(sed -n "/^# ---- lanes/,/^logger_ok()/p" $x/old) <(sed -n "/^# ---- lanes/,/^logger_ok()/p" $x/bench/q/cv02/cq.sh); rc=$?; rm -rf $x; [ $rc = 0 ]'
if [ -z "$QC" ]; then skip "no QC given: the new queue code is not deployed yet"
else q=$(C "cd $QC && md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo CODE_OK; md5sum < bench/q/cv02/cq.sh | cut -c1-32; md5sum < bench/q/cv02/cq_rescue.sh | cut -c1-32; diff <(grep -v '  REVISION\$' $OQC/CODE.md5) <(grep -v '  REVISION\$' CODE.md5) | grep '^[<>]' | awk '{print \$1 \$3}' | LC_ALL=C sort | tr '\n' ' '") || q=""
  ck "QC $QC: CODE.md5 OK, cq.sh 4fc8d2c0, cq_rescue.sh 8710a732; against the running QC (5437778) only cq.sh changed and cq_rescue.sh added" '[ "$(echo $q)" = "CODE_OK 4fc8d2c0f87c77b099e06164e6b513ea 8710a7321e060a68e49823f94f3a2b06 <bench/q/cv02/cq.sh >bench/q/cv02/cq.sh >bench/q/cv02/cq_rescue.sh" ]'; fi
echo "--- 2 queues on cv02"
s=$(C "for q in $BQ/*/; do n=\$(basename \$q); p=\$(cat \$q/queue.pid 2>/dev/null); [ -n \"\$p\" ] && kill -0 \$p 2>/dev/null || continue; m=\$(cat \$q/MAXC 2>/dev/null); echo \"\$n MAXC \${m:-16} dispatched \$(grep -c 'cv02 q: all jobs dispatched' \$q/launch.log) fixture_only \$([ -s \$q/jobs.txt ] && [ \"\$(cut -d'|' -f9 \$q/jobs.txt | sort -u)\" = --fixture ] && echo 1 || echo 0) share \$(cat \$q/SHARE_TRAIN 2>/dev/null)/\$(cat \$q/SHARE_DUMP 2>/dev/null) started \$(ls \$q/pids/*.gpu 2>/dev/null | wc -l) of \$(grep -c . \$q/jobs.txt)\"; done; echo ---; for q in c3all c3all2 rows2 $NEWQ; do Q=$BQ/\$q; [ -d \$Q/pids ] || continue; m=\$(cat \$Q/queue.pid 2>/dev/null); for f in \$Q/pids/*.gpu; do [ -e \$f ] || continue; n=\$(basename \$f .gpu); [ -e \$Q/pids/\$n.end ] && continue; c=\$(grep \"^\$n chain \" \$Q/pids/subshells.txt | tail -1 | cut -d' ' -f3); echo \"open \$q \$n GPU \$(cat \$f) rc '\$(cat \$Q/pids/\$n.rc 2>/dev/null)' chain \$(kill -0 \$c 2>/dev/null && [ \"\$(ps -o ppid= -p \$c | tr -d ' ')\" = \"\$m\" ] && echo ok || echo NOT-VERIFIED) rescued \$(ls \$Q/pids/\$n.rescued 2>/dev/null | wc -l)\"; done; done; echo ---; nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits | tr '\n' ';'; echo; df --output=avail -BG /tmp | tail -1 | tr -dc 0-9; echo; for g in bench_diskguard bench_diskguard2 bench_diskguard3; do tmux has-session -t \"=\$g\" 2>/dev/null && echo \"\$g up\" || echo \"\$g down\"; done; grep -c 'for q in c3all2 c3all3;' $BQ/diskguard3.sh; ls $BQ/*/HOLD 2>/dev/null | wc -l") || s=""
echo "$s" | sed 's/^/     /'
live=$(echo "$s" | sed '/^---$/,$d'); can=$(echo "$live" | awk '$3 != 0 && $5 == 0 && $7 == 0 {print $1}' | tr '\n' ' ')
ck "live queues that can still start training: '$can' (at most one)" '[ "$(echo $can | wc -w)" -le 1 ]'
ck "c3all, c3base, c3hrnet frozen (MAXC 0)" '[ "$(echo "$live" | awk "(\$1 == \"c3all\" || \$1 == \"c3base\" || \$1 == \"c3hrnet\") && \$3 == 0" | wc -l)" = 3 ]'
ck "no sharing in any live queue other than $NEWQ (older queue code ignores the files; they must not be there)" '[ -z "$(echo "$live" | awk -v n=$NEWQ "\$1 != n && \$1 !~ /smoke/ && \$9 != \"/\"")" ]'
if echo "$live" | grep -q "^$NEWQ "; then ck "$NEWQ runs with SHARE_TRAIN 20480 and SHARE_DUMP 10240" 'echo "$live" | grep -q "^$NEWQ .* share 20480/10240 "'; else skip "$NEWQ is not armed yet"; fi
ck "every open lane of an older queue has a verified chain (candidates for the rescue tool), or was stopped by the tool" '! echo "$s" | grep "^open " | grep -v " rescued 1" | grep -q NOT-VERIFIED'
t=$(echo "$s" | tail -6); cf=$(echo "$t" | sed -n 1p)
ck "cv02 /tmp free >= 45 GB (now ${cf:-?})" '[ "${cf:-0}" -ge 45 ]'
ck "cv02 disk guards up; guard 3 names c3all2 and c3all3; no HOLD file" 'echo "$t" | grep -qx "bench_diskguard3 up" && echo "$t" | grep -qx "bench_diskguard2 up" && [ "$(echo "$t" | sed -n 5p)" = 1 ] && [ "$(echo "$t" | sed -n 6p)" = 0 ]'
echo "--- 3 gaint"
gf=$(df --output=avail -BG /home/noob/work | tail -1 | tr -dc 0-9)
ck "gaint free >= 15 GB (now $gf)" '[ "$gf" -ge 15 ]'
for r in c3base c3hrnet c3swad; do p=$(cat /home/noob/work/bench_relay/$r/relay.pid 2>/dev/null); if kill -0 "$p" 2>/dev/null; then ok "relay $r alive ($(ls /home/noob/work/bench_relay/$r/.ok | wc -l) runs relayed)"; else skip "relay $r is not running"; fi; done
(cd $HERE && md5sum c3lane.patch c3lane_commit.sh c3lane_handover.sh c3lane_rescue.sh c3lane_dumptest.sh c3lane_check.sh c3lane_test.sh c3lane_handover_test.sh | sed 's/^/     /')
echo "[$(date '+%F %T')] C3LANE CHECK: $NO OK, $NFL FAIL, $NS SKIP"
[ $NFL = 0 ]
