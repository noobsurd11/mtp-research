#!/bin/bash
# AMENDMENT_1 audit: every T3b comparison that reads real cv02 or NAS files, run as a standalone READ-ONLY snippet against the
# real files where they exist now (KB, F2B, bench_data on cv02; finished queue / relay dirs of fin2 and fin as format samples).
# cv02: only `ssh -n -a -o BatchMode=yes` with read-only commands (cat, md5sum, md5sum -c, diff, ls, test, grep, df, nvidia-smi,
# tmux has-session); nothing is written there. gaint: reads the NAS fin2 relay and the gaint fin relay (open-set cv5v3 dumps,
# RUN.md5 / .ok / relay.log only); never reads IO, an E1 label or any E1 / test50 prediction; writes only OUT and a scratch dir.
# Usage: bash t3b_realinput_audit.sh <out file>
set -u
OUT=${1:?out}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); P=/home/noob/work/el-fault-detection/.venv/bin/python
C=cv02@10.8.1.106; R(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; }
S=/home/noob/work/bench_int_io/t3b/audit_$$; [ -e $S ] && exit 1; mkdir -p $S
NEWQ=$HERE/t3b_queue.sh; OLDQ=$HERE/evidence/amend1/t3b_queue.sh.reg1_cad952c0
KC=$(grep -m1 '^KC=' $NEWQ | cut -d= -f2 | cut -d';' -f1); KB=/tmp/noob_el/bench_${KC:0:7}; F2B=/tmp/noob_el/bench_9967d59; BQ=/tmp/noob_el/bench_q
res(){ echo "$1	$2	$3" | tee -a $OUT; }
: > $OUT; echo "t3b real-input audit $(date '+%F %T %Z') (script $(md5sum < $0 | cut -c1-8); queue $(md5sum < $NEWQ | cut -c1-8), old $(md5sum < $OLDQ | cut -c1-8))" | tee -a $OUT
echo "check	result	evidence" | tee -a $OUT
# kb_check, exactly as written in each script (function, PINS, DW, KB lines extracted), with the real read-only R()
kbx(){ # script -> prints the kb_check result line
  { echo 'set -u'; grep -m1 '^KC=' $1; grep -m1 '^KB=' $1; sed -n '/^PINS="/,/"$/p' $1; grep -m1 '^DW=' $1
    echo 'C=cv02@10.8.1.106; STEP=check; R(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; }; no(){ echo "REFUSED ($STEP): $*"; exit 1; }'
    sed -n '/^kb_check(){/,/echo "KB \$KB: REVISION K/p' $1; echo 'kb_check'; } > $S/kbx.sh
  bash $S/kbx.sh 2>&1 | tail -1; }
o=$(kbx $OLDQ); n=$(echo "$o" | grep -o '<[^ ]*\|>[^ ]*' | wc -l); res "kb_check, registration-1 script (cad952c0)" "$(case "$o" in REFUSED*) echo refuses;; *) echo passes;; esac)" "${o:0:110}... ($n path entries)"
o=$(kbx $NEWQ); res "kb_check, amended script (sorted by path)" "$(case "$o" in REFUSED*) echo "REFUSES (not OK)";; *) echo "real-input OK";; esac)" "$o"
o=$(R "cd $KB && grep -v '  REVISION\$' CODE.md5 | wc -l; cd $F2B && grep -v '  REVISION\$' CODE.md5 | wc -l; head -2 $F2B/CODE.md5 | awk '{print \$2}' | tr '\n' ' '; head -2 $KB/CODE.md5 | awk '{print \$2}' | tr '\n' ' '") || o="ssh failed"
res "  CODE.md5 line orders" "info" "$(echo $o)"
# data_check
o=$(R "md5sum < /tmp/noob_el/bench_data/DEPLOY.md5 | cut -c1-32"); w=$(grep -m1 '^DT=' $NEWQ | grep -o 'DATA_MD5=[0-9a-f]*' | cut -d= -f2)
res "data_check (bench_data DEPLOY.md5)" "$([ "$o" = "$w" ] && echo "real-input OK" || echo FAIL)" "cv02 $o, pinned $w"
# names_check (the logic, names from t3b_make_jobs.py for K into scratch; IO not read)
$P $HERE/t3b_make_jobs.py --k $KC --train $S/jt.txt --dump $S/jd.txt > /dev/null; NM=$(cut -d'|' -f1 $S/jt.txt $S/jd.txt | tr '\n' ' ')
hit=$(R "for n in $NM; do ls -d /tmp/noob_el/bench_*/experiments/\$n /tmp/noob_el/bench_*/experiments/\$n.stdout /tmp/noob_el/bench_*/dumps/elbench1/*/\$n /tmp/noob_el/bench_*/runs/\$n $BQ/*/pids/\$n.gpu 2>/dev/null; done; true")
rh=$(for n in $NM; do ls -d /home/noob/work/bench_relay/*/$n /mnt/nas/noob_el_archive/bench_relay/*/$n 2>/dev/null; done)
res "names_check (63 names)" "$([ -z "$hit$rh" ] && echo "real-input OK" || echo FAIL)" "cv02 hits $(echo -n "$hit" | grep -c .), relay hits $(echo -n "$rh" | grep -c .); jobs md5 $(md5sum < $S/jt.txt | cut -c1-8) / $(md5sum < $S/jd.txt | cut -c1-8)"
# stage precondition, dt_check, ds_check
o=$(R "test ! -e /tmp/noob_el/bench_data_sealed && test ! -e /tmp/noob_el/bench_data_t3b && echo FREE")
res "stage precondition (DT, DS absent)" "$([ "$o" = FREE ] && echo "real-input OK" || echo "FAIL: $o")" "$o"
res "dt_check" "not testable before stage" "DT does not exist yet; same commands passed on the chain smoke's staged copy (stub ssh); both sides now LC_ALL=C sorted"
res "ds_check" "not testable before stage" "DS does not exist yet; compares md5 of the same MANIFEST.md5 bytes (tar copy) and md5sum -c (order-free)"
# render_q / rendercmp, place / arm
res "render_q + t3b_rendercmp.py" "not testable before stage" "cq.sh arming checks DT's ROOTS_t3b.md5 / MANIFEST.md5 and render writes a scratch queue dir on cv02; rendercmp compares sets of lines (order-free); K's real cq.sh rendered 65 lines in the render smoke"
o=$(R "cd $BQ/fin2 && echo \"jobs \$(md5sum < jobs.txt | cut -c1-32) LPG \$(cat LPG) share \$(cat SHARE_TRAIN 2>/dev/null || echo -) \$(ls SHARE_DUMP 2>/dev/null | wc -l) sealed \$(ls SEALED 2>/dev/null | wc -l) used \$(ls -d queue.pid gpumem.pid pids HOLD 2>/dev/null | wc -l)\$(test -s launch.log && echo +log) ses \$(tmux has-session -t '=bench_q_t3b' 2>/dev/null && echo yes || echo no)\"")
res "arm_q queue-dir string (format, on the ended queue fin2)" "$(echo "$o" | grep -qE '^jobs [0-9a-f]{32} LPG [12] share [-0-9]+ [0-9]+ sealed [0-9]+ used [0-9]+(\+log)? ses (yes|no)$' && echo "real-input OK (format)" || echo FAIL)" "$o"
o=$(R "nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits" | awk '$1 < 4096' | wc -l); a=$(R "df --output=avail -BG /tmp | tail -1 | tr -dc 0-9")
res "free_gpus / free disk (arm)" "real-input OK" "GPUs < 4096 MiB now: $o; cv02 /tmp free $a GB (arm needs 55)"
o=$(R "tmux has-session -t '=bench_diskguard8' 2>/dev/null && echo RUNNING; test -e $BQ/diskguard8.sh && echo PRESENT; true")
res "guard preconditions" "$([ -z "$o" ] && echo "real-input OK" || echo "note: $o")" "bench_diskguard8 session and $BQ/diskguard8.sh absent: 'guard' will place and start it"
res "place / arm / place2 / arm2 / render_r / place_r / arm_r" "not testable now" "they write or start on cv02 (forbidden here); the cq_setup.sh line they grep is the one fin2 / open printed"
# q1_done's remote part and parser, on fin2 (launch.log with 10 'trained <run> rc=0', F2B/runs/<run>/RUN.md5)
FN="fin_hrnet_swad_v11_pool_s5 fin_hrnet_swad_v11_pool_s6 fin_hrnet_swad_v11_pool_s7 fin_hrnet_swad_v11_pool_s8 fin_hrnet_swad_v11_pool_s9 fin_pf_v11_pool_s5 fin_pf_v11_pool_s6 fin_pf_v11_pool_s7 fin_pf_v11_pool_s8 fin_pf_v11_pool_s9"
Q1=$BQ/fin2; QL=$Q1; RL=""
o=$(R "for q in $QL; do echo \"Q \$q \$(cat \$q/launch.log 2>/dev/null | grep -c 'BENCH CV02 Q ALL DONE') \$(kill -0 \$(cat \$q/queue.pid 2>/dev/null) 2>/dev/null && echo alive || echo ended)\"; done
    for n in $FN; do echo \"N \$n \$(cat $Q1/launch.log 2>/dev/null | grep -c \"trained \$n rc=0 \") \$(cat $RL /dev/null 2>/dev/null | grep -c \"trained \$n rc=0 \") \$(test -s $F2B/runs/\$n/RUN.md5 && echo R || echo -)\"; done
    echo \"D \$(cd $BQ 2>/dev/null && ls -d t3brep[1-9] 2>/dev/null | tr '\n' ' ')\"")
q=$(echo "$o" | awk '$1 == "Q" {print $3, $4}'); k=$(echo "$o" | awk '$1 == "N" && $3 == 1 && $4 == 0 && $5 == "R"' | wc -l); d=$(echo "$o" | awk '$1 == "D" {$1=""; print}')
res "q1_done remote part + parser (fin2 sample)" "$([ "$q" = "1 ended" ] && [ $k = 10 ] && [ -z "$(echo $d)" ] && echo "real-input OK (format)" || echo FAIL)" "ALL DONE / state '$q'; names with 'trained <n> rc=0 ' and RUN.md5: $k of 10; t3brep dirs: '${d# }'"
RF=/mnt/nas/noob_el_archive/bench_relay/fin2; u=fin_hrnet_swad_v11_pool_s5
g=$(grep -c "RELAY ALL DONE: 10 of 10" $RF/relay.log); m=$(awk '{print $4}' $RF/.ok/$u); m2=$(md5sum < $RF/$u/runs/$u/RUN.md5 | cut -c1-32)
c=$( (cd $RF/$u && md5sum -c --quiet runs/$u/RUN.md5 > /dev/null 2>&1) && echo OK || echo FAIL); l=$(awk '{print $2}' $RF/$u/runs/$u/LATEST.md5)
res "relay.log / .ok / md5sum -c / LATEST.md5 formats (NAS fin2)" "$([ $g = 1 ] && [ "$m" = "$m2" ] && [ $c = OK ] && [ "$l" = "experiments/$u/checkpoints/latest.pth" ] && echo "real-input OK (format)" || echo FAIL)" "'RELAY ALL DONE: 10 of 10' lines $g; .ok field 4 = md5(RUN.md5) $([ "$m" = "$m2" ] && echo yes || echo no); md5sum -c $c; LATEST.md5 path $l (q1_done / relay deploy use these)"
RW=/home/noob/work/bench_relay/fin; v=$(ls $RW/.ok | grep -m1 'tta_d4$')
m=$(awk '{print $4}' $RW/.ok/$v); m2=$(md5sum < $RW/$v/runs/$v/RUN.md5 | cut -c1-32); c=$( (cd $RW/$v && md5sum -c --quiet runs/$v/RUN.md5 > /dev/null 2>&1) && echo OK || echo FAIL)
kk=$(grep -cE "  dumps/elbench1/[A-Za-z0-9_]+/$v/" $RW/$v/runs/$v/RUN.md5); ll=$(grep -c . $RW/$v/runs/$v/RUN.md5)
res "unstage gaint-side checks (an open-set dump unit of fin)" "$([ "$m" = "$m2" ] && [ $c = OK ] && [ "$kk" = "$ll" ] && [ $kk -gt 0 ] && echo "real-input OK (format)" || echo FAIL)" "unit $v: .ok field 4 = md5(RUN.md5) $([ "$m" = "$m2" ] && echo yes || echo no); md5sum -c $c; dump-dir lines $kk of $ll"
res "unstage cv02 part, relay deploy, the read" "not testable before the runs / dumps" "need KB/runs and KB/dumps of T3b (absent); same commands passed through the stub ssh in the chain smoke"
ST=/home/noob/work/bench_c3_io/stage/bench_89b9ea5; c=$( (cd $ST && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) && echo OK || echo FAIL); r=$(md5sum < $ST/bench/q/cv02/relay_w1c.sh | cut -c1-32)
a=$(df --output=avail -BG /mnt/nas/noob_el_archive | tail -1 | tr -dc 0-9); e=$(ls -d /mnt/nas/noob_el_archive/bench_relay/t3b /mnt/nas/noob_el_archive/bench_relay/t3bopen 2>/dev/null | wc -l)
res "relay preconditions (stage copy, relay_w1c.sh, NAS)" "$([ $c = OK ] && [ $r = 74a2ec3d48ad3cd989aa0c9b5ae69942 ] && [ $e = 0 ] && [ $a -ge 25 ] && echo "real-input OK" || echo FAIL)" "stage CODE.md5 $c; relay_w1c $r; RD1 / RD2 existing $e; NAS free $a GB"
echo "audit end $(date '+%F %T'); nothing written on cv02; IO not read" | tee -a $OUT
rm -rf $S
