#!/bin/bash
# Builder's smoke of the T3b repair path (review round 1 N1) and of the training relay with failed runs, gaint CPU only,
# SYNTHETIC files (no model, no image): a stub ssh runs every cv02 command locally with /tmp/noob_el/ mapped into the scratch dir;
# the relay is the real t3b_relay.sh / relay_w1c.sh in the foreground.
#   t3b ends with 31 'trained rc=0' and 2 failures (t3b_half_f2_s6 -> fresh repair 1; t3b_deploy_s7 -> resume repair 2)
#   -> relay train ends 'RELAY DONE ... 31 of 33' -> gate refused -> repair_register 1 (fresh) -> repair_aside refused while the
#   ledger lacks the repair line -> a repair of a run that succeeded refused -> repair_register 2 (resume) -> ledger lines ->
#   an unregistered repair queue dir makes the gate refuse -> repair_aside 1 and 2 -> place_r 1 and 2 -> the repair runs end
#   (synthetic) -> gate refused (relay not 33 of 33) -> relay trainrep 1 -> 'RELAY ALL DONE: 33 of 33' -> relay deploy (3 of 3)
#   -> gate passes with both registered repairs.
# Usage: bash t3b_repair_smoke.sh <out dir>   (about 1 CPU-min)
set -u
OUT=${1:?out}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); P=/home/noob/work/el-fault-detection/.venv/bin/python
KC=$(grep -m1 '^KC=' $HERE/t3b_queue.sh | cut -d= -f2 | cut -d';' -f1); K7=${KC:0:7}
S=/home/noob/work/bench_int_io/t3b/repair_$$; [ -e $S ] && exit 1; mkdir -p $S/bin $S/noob_el $OUT || exit 1
say(){ echo "$*" | tee -a $OUT/repair_smoke.out; }
say "[$(date '+%F %T')] T3b repair smoke in $S (K $KC; script $(md5sum < $0 | cut -c1-8))"
cat > $S/bin/ssh <<EOF
#!/bin/bash
c="\${@: -1}"; c=\${c//\/tmp\/noob_el\//$S/noob_el/}
exec bash -c "\$c"
EOF
chmod +x $S/bin/ssh
nice -n 19 $P $HERE/t3b_smoke_synth.py ext $S/ext117 > /dev/null
RO=$S/relay_open; mkdir -p $RO/.ok; : > $RO/relay.log
for n in fin_hrnet_swad_v11_pool_s{5,6,7}.swad.tta_d4.e1_106; do mkdir -p $RO/$n/runs/$n; echo "x  dumps/$n" > $RO/$n/runs/$n/RUN.md5
  echo "2026-11-21 12:00:00 RUN.md5 $(md5sum < $RO/$n/runs/$n/RUN.md5 | cut -c1-32) files 1" > $RO/.ok/$n; echo "[x] relayed $n: smoke" >> $RO/relay.log; done
mkdir -p $S/open_reg && cp /home/noob/work/bench_open_io/REGISTERED.txt $S/open_reg/REGISTERED.txt
TEST_MODE=1 IO=$S/io EXT_DIR=$S/ext117 RD_OPEN=$RO OPEN_REG=$S/open_reg/REGISTERED.txt bash $HERE/t3b_register.sh > $OUT/register.out 2>&1 || { say "register failed"; exit 1; }
REG=$(cat $S/io/REGISTERED.md5); LED=$S/e1_openings.md
{ grep -m1 -F "| # | protocol | models |" /home/yugma/mtp/research/team_2026-10-31_next/e1_openings.md; grep '^| 9 |' $OUT/register.out; } > $LED
QE="TEST_MODE=1 REG_MD5=$REG IO=$S/io EXT_DIR=$S/ext117 RD1=$S/relay_t3b RD2=$S/relay_t3bopen READ_OUT=$S/reads/t3b_open9 LEDGER=$LED K=$KC PATH=$S/bin:$PATH"
RLE="TEST_MODE=1 REG_MD5=$REG IO=$S/io RD1=$S/relay_t3b RD2=$S/relay_t3bopen POLL=1 FG=1 PATH=$S/bin:$PATH"
q(){ env $QE "$@"; }
KB=$S/noob_el/bench_$K7; Q1=$S/noob_el/bench_q/t3b; mkdir -p $KB/experiments $Q1
TN=$(cut -d'|' -f1 $S/io/jobs_train.txt | tr '\n' ' '); F1=t3b_half_f2_s6; F2N=t3b_deploy_s7
mkrun(){ mkdir -p $KB/experiments/$1/checkpoints; echo "run_name: $1" > $KB/experiments/$1/config_used.yaml; head -c 2048 /dev/urandom > $KB/experiments/$1/checkpoints/latest.pth; echo "stdout of $1" > $KB/experiments/$1.stdout; }
for n in $TN; do mkrun $n; done
nice -n 19 $P $HERE/t3b_smoke_synth.py units $KB $(for n in $TN; do [ $n = $F1 ] || [ $n = $F2N ] || echo $n; done) > /dev/null
{ for n in $TN; do [ $n = $F1 ] || [ $n = $F2N ] && echo "[x] trained $n rc=1 (GPU 0)" || echo "[x] trained $n rc=0 (GPU 0)"; done; echo "[x] BENCH CV02 Q ALL DONE (31 trained rc 0)"; } > $Q1/launch.log
env $RLE bash $HERE/t3b_relay.sh train > $OUT/relay_train.out 2>&1; say "relay train with 2 failed runs: rc $? ($(tail -1 $S/relay_t3b/relay.log | cut -c22-110))"
q bash $HERE/t3b_queue.sh gate > $OUT/gate1.out 2>&1; say "gate with 2 failed runs: rc $? ($(tail -1 $OUT/gate1.out | cut -c1-170))"
RN=1 NAMES_R=$F1 KIND=fresh q bash $HERE/t3b_queue.sh repair_register > $OUT/reg1.out 2>&1; say "repair_register 1 ($F1, fresh): rc $? ($(grep -m1 '^jobs ' $OUT/reg1.out))"
RN=1 q bash $HERE/t3b_queue.sh repair_aside > $OUT/neg_aside_unreg.out 2>&1; say "negative repair_aside 1 before its ledger line: rc $? ($(tail -1 $OUT/neg_aside_unreg.out | cut -c1-130))"
grep -h '^- \*\*#9 amendment' $OUT/reg1.out >> $LED
RN=3 NAMES_R=t3b_all_f0_s5 KIND=fresh q bash $HERE/t3b_queue.sh repair_register > $OUT/neg_reg_ok.out 2>&1; say "negative repair of a run that succeeded: rc $? ($(tail -1 $OUT/neg_reg_ok.out | cut -c1-110)); repair3 dir: $([ -e $S/io/repair3 ] && echo yes || echo no)"
RN=2 NAMES_R=$F2N KIND=resume q bash $HERE/t3b_queue.sh repair_register > $OUT/reg2.out 2>&1; say "repair_register 2 ($F2N, resume): rc $? ($(grep -m1 '^jobs ' $OUT/reg2.out)); its line ends '$(tail -c 22 $S/io/repair2/jobs.txt | tr -d '\n')'"
grep -h '^- \*\*#9 amendment' $OUT/reg2.out >> $LED
mkdir -p $S/noob_el/bench_q/t3brep4
q bash $HERE/t3b_queue.sh gate > $OUT/neg_gate_unreg.out 2>&1; say "negative gate with an unregistered repair queue dir t3brep4: rc $? ($(tail -1 $OUT/neg_gate_unreg.out | grep -o 'unregistered repair queue [^;]*'))"
rmdir $S/noob_el/bench_q/t3brep4
RN=1 q bash $HERE/t3b_queue.sh repair_aside > $OUT/aside1.out 2>&1; say "repair_aside 1 (fresh): rc $? ($(grep -c '^moved' $OUT/aside1.out) moved: $(ls -d $KB/experiments/$F1* | xargs -n1 basename | tr '\n' ' '))"
RN=2 q bash $HERE/t3b_queue.sh repair_aside > $OUT/aside2.out 2>&1; say "repair_aside 2 (resume): rc $? ($(grep -c '^moved' $OUT/aside2.out) moved: $(ls -d $KB/experiments/$F2N* | xargs -n1 basename | tr '\n' ' '))"
for r in 1 2; do RN=$r q bash $HERE/t3b_queue.sh place_r > $OUT/place_r$r.out 2>&1; say "place_r $r: rc $? ($(tail -1 $OUT/place_r$r.out | cut -c22-130))"; done
mkrun $F1; nice -n 19 $P $HERE/t3b_smoke_synth.py units $KB $F1 > /dev/null
head -c 2048 /dev/urandom > $KB/experiments/$F2N/checkpoints/latest.pth; nice -n 19 $P $HERE/t3b_smoke_synth.py units $KB $F2N > /dev/null
echo "[x] trained $F1 rc=0 (GPU 1)
[x] BENCH CV02 Q ALL DONE (1 trained rc 0)" > $S/noob_el/bench_q/t3brep1/launch.log
echo "[x] trained $F2N rc=0 (GPU 2)
[x] BENCH CV02 Q ALL DONE (1 trained rc 0)" > $S/noob_el/bench_q/t3brep2/launch.log
q bash $HERE/t3b_queue.sh gate > $OUT/gate2.out 2>&1; say "gate after the repairs, before the relay: rc $? ($(tail -1 $OUT/gate2.out | cut -c1-150))"
env $RLE bash $HERE/t3b_relay.sh trainrep 1 > $OUT/relay_rep.out 2>&1; say "relay trainrep 1: rc $? ($(tail -1 $S/relay_t3b/relay.log | cut -c22-90)); units in RD1 $(ls $S/relay_t3b/.ok | wc -l)"
env $RLE bash $HERE/t3b_relay.sh deploy > $OUT/relay_deploy.out 2>&1; say "relay deploy: rc $? ($(tail -1 $OUT/relay_deploy.out | cut -c22-80))"
q bash $HERE/t3b_queue.sh gate > $OUT/gate3.out 2>&1; rc=$?; say "gate after the repairs and the relay: rc $rc ($(tail -1 $OUT/gate3.out | cut -c1-200))"
say "[$(date '+%F %T')] repair smoke done (final gate rc $rc); scratch removed"
chmod -R u+w $S; rm -rf $S
exit $rc
