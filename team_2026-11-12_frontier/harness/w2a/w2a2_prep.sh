#!/bin/bash
# Wave 2a restart (lead, 15 Nov 2026): the reviewed queue bq/w2a (jobs d8be4f16, c57508e) was stopped by a signal on 15 Nov 09:49
# after 25 of 61 training runs (no dumps yet). This prepares bq/w2a2 = the 36 reviewed job lines that have no "trained ... rc=0"
# line, in the reviewed order, plus the unchanged reviewed dump list (161 lines, 0bcef536). Same code, cards, roots and gates.
# The two runs that were killed mid-training are moved aside (kept), so they train again from step 0.
set -eu
O=/home/noob/work/bq/w2a; N=/home/noob/work/bq/w2a2; R=/home/noob/work/bench_wt_w2; E=$R/experiments
[ ! -e $N ] || { echo "$N exists"; exit 1; }
[ "$(md5sum < $O/jobs.txt | cut -c1-32)" = d8be4f16c79a499ebff2d822068f4870 ] && [ "$(md5sum < $O/dump/jobs.txt | cut -c1-32)" = 0bcef5368e50b5df75326359edcb6da3 ] || { echo "reviewed lists changed"; exit 1; }
! kill -0 "$(cat $O/queue.pid)" 2>/dev/null || { echo "old queue still alive"; exit 1; }
[ -z "$(ps -eo comm,args | awk '$1 ~ /^python/ && /run_name=w2a_/' || true)" ] || { echo "a w2a training process is alive"; exit 1; }
mkdir -p $N/dump
grep -oE '\] trained [^ ]+ rc=0' $O/launch.log | awk '{print $3}' | sort > $N/done_names.txt
awk -F'|' 'NR==FNR {d[$1]=1; next} !($1 in d)' $N/done_names.txt $O/jobs.txt > $N/jobs.txt
cp $O/dump/jobs.txt $N/dump/jobs.txt; echo 2 > $N/MAXC; echo 1 > $N/dump/MAXC
[ "$(wc -l < $N/done_names.txt)" = 25 ] && [ "$(wc -l < $N/jobs.txt)" = 36 ] || { echo "counts differ"; exit 1; }
[ "$(tail -n 36 $O/jobs.txt | md5sum)" = "$(md5sum < $N/jobs.txt)" ] || { echo "remaining lines are not the last 36 reviewed lines"; exit 1; }
for n in $(cut -d'|' -f1 $N/done_names.txt); do [ -s $E/$n/checkpoints/latest.pth ] || { echo "done run $n lacks latest.pth"; exit 1; }; done
for n in $(cut -d'|' -f1 $N/jobs.txt); do
  if [ -e $E/$n ] || [ -e $E/$n.stdout ]; then
    case $n in w2a_spd_f0_s5|w2a_spd_f1_s5) mv $E/$n $E/$n.killed_20261115_0949; mv $E/$n.stdout $E/$n.killed_20261115_0949.stdout; echo "moved aside $n";;
      *) echo "unexpected existing output $n"; exit 1;; esac; fi; done
chmod a-w $N/jobs.txt $N/dump/jobs.txt
echo "jobs $(md5sum < $N/jobs.txt | cut -c1-32) ($(wc -l < $N/jobs.txt) lines); dump jobs $(md5sum < $N/dump/jobs.txt | cut -c1-32) ($(wc -l < $N/dump/jobs.txt) lines); MAXC $(cat $N/MAXC)"
