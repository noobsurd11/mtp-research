#!/bin/bash
# Lead, 13 Nov 2026. Prepares queue dir bq/w1g2 = W1-G with seeds 7 and 8 (10 runs house_r34_unetpp_pf_v11, cv5v2 folds 0-4,
# label set v1.1) plus the 10 held-out dumps. Same code (el_bench 31c0c36), cards, roots and gates as the reviewed W1-G;
# only the seed and the run names change. Nothing is started here.
set -eu
S=/home/noob/work/bq/w1g; Q=/home/noob/work/bq/w1g2; R=/home/noob/work/el_bench
[ -e $Q/jobs.txt ] && { echo "REFUSE: $Q/jobs.txt exists"; exit 1; }
[ "$(md5sum < $S/jobs.txt | cut -c1-32)" = 4f5a55350ea253cea794cf465fa11aa5 ] || { echo "REFUSE: W1-G jobs md5"; exit 1; }
[ "$(md5sum < $S/dump/jobs.txt | cut -c1-32)" = 240890b5ee3150c62f8c3102b23bda44 ] || { echo "REFUSE: W1-G dump jobs md5"; exit 1; }
mkdir -p $Q/dump
sed -e 's/_s5|/_s7|/; s/\.yaml|5|/.yaml|7|/; s/_s6|/_s8|/; s/\.yaml|6|/.yaml|8|/' $S/jobs.txt > $Q/jobs.txt
sed -e 's/_s5\([| ]\)/_s7\1/g; s/^\([^|]*\)|-|5|/\1|-|7|/; s/_s6\([| ]\)/_s8\1/g; s/^\([^|]*\)|-|6|/\1|-|8|/' $S/dump/jobs.txt > $Q/dump/jobs.txt
echo 3 > $Q/MAXC; echo 1 > $Q/dump/MAXC
# checks: same lines as W1-G once seeds are masked; seeds 7, 8 only; 10 + 10 lines; unique names; nothing exists yet
norm(){ sed -e 's/_s[5-8]\([| ]\)/_sX\1/g; s/\.yaml|[5-8]|/.yaml|X|/; s/^\([^|]*\)|-|[5-8]|/\1|-|X|/' "$1"; }
diff <(norm $S/jobs.txt) <(norm $Q/jobs.txt) > /dev/null && echo "jobs: equal to W1-G with seeds masked" || { echo "FAIL jobs differ"; exit 1; }
diff <(norm $S/dump/jobs.txt) <(norm $Q/dump/jobs.txt) > /dev/null && echo "dump jobs: equal to W1-G with seeds masked" || { echo "FAIL dump jobs differ"; exit 1; }
echo "train lines $(wc -l < $Q/jobs.txt), seeds $(cut -d'|' -f3 $Q/jobs.txt | sort | uniq -c | tr '\n' ' '), dup names $(cut -d'|' -f1 $Q/jobs.txt | sort | uniq -d | wc -l)"
echo "dump lines $(wc -l < $Q/dump/jobs.txt), seeds $(cut -d'|' -f3 $Q/dump/jobs.txt | sort | uniq -c | tr '\n' ' '), s5/s6 tokens left $(grep -cE '_s[56]([| ]|$)' $Q/jobs.txt $Q/dump/jobs.txt | tr '\n' ' ')"
ex=0; for n in $(cut -d'|' -f1 $Q/jobs.txt); do { [ -e $R/experiments/$n ] || [ -e $R/experiments/$n.stdout ] || [ -e /home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11/$n ]; } && { echo "EXISTS $n"; ex=1; }; done; echo "existing outputs: $ex"
JM=$(md5sum < $Q/jobs.txt | cut -c1-32); DM=$(md5sum < $Q/dump/jobs.txt | cut -c1-32)
cat > $Q/launch_w1g2.sh <<L
#!/bin/bash
# W1-G2 launch (lead, 13 Nov): W1-G with seeds 7 and 8. Arms $Q in tmux bench_q_w1g2 (10 training jobs, MAXC 3, gate 9,000,
# then 10 held-out dumps). bench_setup.sh refuses if the session exists, an md5 or HEAD differs, or any experiments/<job> exists.
export Q=$Q SES=bench_q_w1g2 DEPLOY=31c0c368ee65742893a36523bcf48e366ea948ed \\
  JOBS_MD5=$JM DJOBS_MD5=$DM REPO=$R
exec bash \$REPO/bench/q/bench_setup.sh
L
cat > $Q/wait_then_launch.sh <<'W'
#!/bin/bash
# Starts W1-G2 only after the W1-G chain (training, then dumps) has ended, because two queues block each other
# through the "outside process" rule. Stop the wait: touch /home/noob/work/bq/w1g2/NOSTART
Q=/home/noob/work/bq/w1g2; L=$Q/wait.log
lg(){ echo "[$(date '+%F %T')] $*" >> $L; }
lg "wait start pid $$"
while :; do
  [ -e $Q/NOSTART ] && { lg "NOSTART file; exit"; exit 0; }
  grep -qE "chain done|dumps not started" /home/noob/work/bq/w1g/chain.log 2>/dev/null && break
  sleep 60
done
lg "W1-G chain ended: $(tail -1 /home/noob/work/bq/w1g/chain.log | cut -c1-160)"
tmux has-session -t "=bench_q_w1g" 2>/dev/null && lg "note: session bench_q_w1g still exists"
sleep 150
bash $Q/launch_w1g2.sh >> $L 2>&1; rc=$?
lg "launch rc=$rc"
W
echo "jobs md5 $JM; dump jobs md5 $DM"; head -1 $Q/jobs.txt; head -1 $Q/dump/jobs.txt | cut -c1-330; cat $Q/launch_w1g2.sh | tail -4
git -C $R rev-parse --short HEAD; git -C $R status --porcelain --untracked-files=no | wc -l
