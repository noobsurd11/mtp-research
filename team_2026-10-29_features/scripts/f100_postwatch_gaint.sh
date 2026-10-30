#!/bin/bash
# Fires the two protocol_100 openings (f100_post_gaint.sh). Opening 1 when all 15 fine-tunes (SUP / SUPPF / MIMPF s0-4)
# trained rc 0; opening 2 when all 5 CP100 trained rc 0 and opening 1 ended rc 0. Any rc != 0 of a needed run: log and stop
# (decision needed). No per-seed scoring.
set -u
cd /home/noob/work/el_f3
L=reports/f100/launch.log
cnt(){ grep -oE "trained f3_($1)_100pct_s[0-4] rc=0" $L | sort -u | wc -l; }
bad(){ grep -E "trained f3_($1)_100pct_s[0-4] rc=[1-9]" $L | head -1; }
until [ "$(cnt 'SUP|SUPPF|MIMPF')" -ge 15 ]; do
  b=$(bad 'SUP|SUPPF|MIMPF'); [ -n "$b" ] && { echo "[$(date)] f3 opening1 NOT scored (FAIL): $b" >> $L; exit 1; }; sleep 120; done
echo "[$(date)] f3 opening1 scoring start (15 fine-tunes trained rc 0)" >> $L
bash reports/f100_post.sh opening1
until [ "$(cnt CP)" -ge 5 ]; do
  b=$(bad CP); [ -n "$b" ] && { echo "[$(date)] f3 opening2 NOT scored (FAIL): $b" >> $L; exit 1; }; sleep 120; done
grep -q "f3 opening1 scoring done: post rc=0" $L || { echo "[$(date)] f3 opening2 NOT scored (FAIL): opening1 not rc 0" >> $L; exit 1; }
echo "[$(date)] f3 opening2 scoring start (5 CP100 trained rc 0)" >> $L
bash reports/f100_post.sh opening2
