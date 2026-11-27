#!/bin/bash
# Negatives (and controls) for the TEST_MODE guards of t3b_register.sh, t3b_queue.sh and run_t3b_read.sh (pattern of
# opening_testmode_guard_test.sh, review rounds 2 and 3 of the final opening). Synthetic scratch dirs only; the IO dirs are
# empty or fake, so even a failed guard would refuse at the next check; the "real tree" paths used here do NOT exist
# (.../__no_such__), so no real file can be read whatever happens. Every negative must print 'REFUSED (TEST_MODE guard)' (or
# the named refusal) and create nothing. Usage: bash t3b_testmode_guard_test.sh <out file>
set -u
OUT=${1:?out file}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
S=/home/noob/work/bench_int_io/t3b/tmguard_$$; [ -e $S ] && exit 1
mkdir -p $S/ext/images $S/ext/masks $S/ext/ignore $S/relay $S/r1 $S/r2 $S/rf $S/reads $S/o8 $S/ro $S/bin $S/io_read $S/io_rel
echo l > $S/ledger.md
echo s > $S/ext/stems_eval.txt; echo r > $S/open_reg.txt; printf 'stem\tcell_type\n' > $S/cells.tsv
printf '#!/bin/bash\necho stub-ssh "$@"\n' > $S/bin/ssh; chmod +x $S/bin/ssh
mkdir -p $S/io_real; printf 'registered real\n' > $S/io_real/REGISTERED.txt; md5sum < $S/io_real/REGISTERED.txt | cut -c1-32 > $S/io_real/REGISTERED.md5
RM=$(cat $S/io_real/REGISTERED.md5)
chk(){ local o; o=$(cat); if echo "$o" | grep -qF "$2"; then echo "PASS  $1: $(echo "$o" | tail -1 | cut -c1-160)"; else echo "FAIL  $1: $(echo "$o" | tail -1 | cut -c1-160)"; fi; }
REGB="TEST_MODE=1 IO=$S/io_reg EXT_DIR=$S/ext RD_OPEN=$S/relay OPEN_REG=$S/open_reg.txt"
reg(){ env -u IO -u EXT_DIR -u RD_OPEN -u OPEN_REG "$@" bash $HERE/t3b_register.sh 2>&1; }
QB="TEST_MODE=1 REG_MD5=0 IO=$S/io_q EXT_DIR=$S/ext RD1=$S/r1 RD2=$S/r2 READ_OUT=$S/ro LEDGER=$S/ledger.md"
qu(){ local st=$1; shift; env -u IO -u EXT_DIR -u RD1 -u RD2 -u READ_OUT -u LEDGER "$@" bash $HERE/t3b_queue.sh $st 2>&1; }
LB="TEST_MODE=1 REG_MD5=0 IO=$S/io_rel RD1=$S/r1 RD2=$S/r2"
rl(){ env -u IO -u RD1 -u RD2 "$@" bash $HERE/t3b_relay.sh deploy 2>&1; }
RB="TEST_MODE=1 REG_MD5=0 IO=$S/io_read RD1=$S/r1 RD2=$S/r2 RD_OPEN=$S/relay RF=$S/rf READ_ROOT=$S/reads BENCH_EXT=$S/ext CELLS_TSV=$S/cells.tsv OPEN8_RECORDS=$S/o8"
rd(){ env -u IO -u RD1 -u RD2 -u RD_OPEN -u RF -u READ_ROOT -u BENCH_EXT -u CELLS_TSV -u OPEN8_RECORDS "$@" bash $HERE/run_t3b_read.sh 2>&1; }
{
echo "== t3b_register.sh"
reg $(echo $REGB | sed "s# OPEN_REG=$S/open_reg.txt##") | chk "R1 OPEN_REG left at its default" "REFUSED (TEST_MODE guard): OPEN_REG must be set explicitly"
reg $(echo $REGB | sed "s#EXT_DIR=$S/ext#EXT_DIR=/home/noob/work/ext117/__no_such__#") | chk "R2 EXT_DIR inside the real tree" "REFUSED (TEST_MODE guard): /home/noob/work/ext117/__no_such__ resolves to"
mkdir -p $S/ext2/images $S/ext2/ignore; echo s > $S/ext2/stems_eval.txt; ln -s /home/noob/work/ext117/__no_such__ $S/ext2/masks
reg $(echo $REGB | sed "s#EXT_DIR=$S/ext#EXT_DIR=$S/ext2#") | chk "R3 scratch EXT_DIR whose masks dir links into the real tree" "REFUSED (TEST_MODE guard): $S/ext2/masks resolves to /home/noob/work/ext117/__no_such__"
reg $(echo $REGB | sed "s#RD_OPEN=$S/relay#RD_OPEN=/mnt/nas/noob_el_archive/bench_relay/__no_such__#") | chk "R4 RD_OPEN on the real relay tree" "REFUSED (TEST_MODE guard): /mnt/nas/noob_el_archive/bench_relay/__no_such__ resolves to"
(cd $S && reg $(echo $REGB | sed "s#EXT_DIR=$S/ext#EXT_DIR=ext#")) | chk "R5 a relative EXT_DIR (run from the scratch dir)" "REFUSED (TEST_MODE guard): ext is not an absolute path"
reg $(echo $REGB | sed 's/TEST_MODE=1 //') | chk "R6 overrides without TEST_MODE" "REFUSED (register): test-only overrides set"
reg $REGB | chk "R7 control: all paths scratch -> the guard passes, a later check refuses" "REFUSED (register): E1 stems_eval.txt is not 5266806b"
echo "   IO made by any register case: $([ -e $S/io_reg ] && echo YES || echo no)"
echo "== t3b_queue.sh"
qu build $(echo $QB | sed "s# READ_OUT=$S/ro##") | chk "Q1 READ_OUT left at its default" "REFUSED (TEST_MODE guard): READ_OUT must be set explicitly"
qu build $(echo $QB | sed "s#RD2=$S/r2#RD2=/mnt/nas/noob_el_archive/bench_relay/__no_such__#") | chk "Q2 RD2 on the real relay tree" "REFUSED (TEST_MODE guard): /mnt/nas/noob_el_archive/bench_relay/__no_such__ resolves to"
qu check $QB | chk "Q3 a cv02 step with the real ssh in PATH" "REFUSED (TEST_MODE guard): $(command -v ssh) resolves to"
(cd $S && qu build $(echo $QB | sed "s#IO=$S/io_q#IO=io_q#")) | chk "Q4 a relative IO" "REFUSED (TEST_MODE guard): io_q is not an absolute path"
qu build $(echo $QB | sed 's/TEST_MODE=1 //') | chk "Q5 overrides without TEST_MODE" "REFUSED (build): test-only overrides set"
qu build $(echo $QB | sed "s#IO=$S/io_q#IO=$S/io_real#; s#REG_MD5=0#REG_MD5=$RM#") | chk "Q6 TEST_MODE against a real (non TEST MODE) registration" "TEST_MODE=1 against a real registration"
qu build $QB | chk "Q7 control build: the guard passes, a later check refuses" "REFUSED (build): no registration in $S/io_q"
PATH=$S/bin:$PATH qu check $QB | chk "Q8 control check with the stub ssh: the guard passes, a later check refuses" "REFUSED (check): no registration in $S/io_q"
qu build $(echo $QB | sed "s# LEDGER=$S/ledger.md##") | chk "Q9 LEDGER left at its default (round 1 N6)" "REFUSED (TEST_MODE guard): LEDGER must be set explicitly"
echo "== t3b_relay.sh (round 1 B1 / B2)"
PATH=$S/bin:$PATH rl $(echo $LB | sed "s# IO=$S/io_rel##") | chk "L1 IO left at its default" "REFUSED (TEST_MODE guard): IO must be set explicitly"
PATH=$S/bin:$PATH rl $(echo $LB | sed "s#RD2=$S/r2#RD2=/mnt/nas/noob_el_archive/bench_relay/__no_such__#") | chk "L2 RD2 on the real relay tree" "REFUSED (TEST_MODE guard): /mnt/nas/noob_el_archive/bench_relay/__no_such__ resolves to"
rl $LB | chk "L3 the real ssh in PATH" "REFUSED (TEST_MODE guard): $(command -v ssh) resolves to"
PATH=$S/bin:$PATH rl $(echo $LB | sed 's/TEST_MODE=1 //') | chk "L4 overrides without TEST_MODE" "REFUSED: test-only overrides set"
PATH=$S/bin:$PATH rl $(echo $LB | sed "s#IO=$S/io_rel#IO=$S/io_real#; s#REG_MD5=0#REG_MD5=$RM#") | chk "L5 TEST_MODE against a real (non TEST MODE) registration" "REFUSED: TEST_MODE=1 against a real registration"
PATH=$S/bin:$PATH rl $LB | chk "L6 control: the guard passes, a later check refuses" "REFUSED: no registration 0 in $S/io_rel"
echo "== run_t3b_read.sh"
rd $(echo $RB | sed "s# READ_ROOT=$S/reads##") | chk "D1 READ_ROOT left at its default" "REFUSED (TEST_MODE guard): READ_ROOT must be set explicitly"
rd $(echo $RB | sed "s# OPEN8_RECORDS=$S/o8##") | chk "D2 OPEN8_RECORDS left at its default" "REFUSED (TEST_MODE guard): OPEN8_RECORDS must be set explicitly"
rd $(echo $RB | sed "s#BENCH_EXT=$S/ext#BENCH_EXT=/home/noob/work/el_f1/reports/f1/__no_such__#") | chk "D3 BENCH_EXT inside the real tree" "REFUSED (TEST_MODE guard): /home/noob/work/el_f1/reports/f1/__no_such__ resolves to"
rd $(echo $RB | sed "s#RD_OPEN=$S/relay#RD_OPEN=/mnt/nas/noob_el_archive/bench_relay/__no_such__#") | chk "D4 RD_OPEN on the real relay tree" "REFUSED (TEST_MODE guard): /mnt/nas/noob_el_archive/bench_relay/__no_such__ resolves to"
mkdir -p $S/r2b; ln -s /mnt/nas/noob_el_archive/bench_relay/__no_such__ $S/r2b/unit
rd $(echo $RB | sed "s#RD2=$S/r2#RD2=$S/r2b#") | chk "D5 a scratch RD2 holding a link into the real relay tree" "REFUSED (TEST_MODE guard): $S/r2b/unit resolves to /mnt/nas/noob_el_archive/bench_relay/__no_such__"
(cd $S && rd $(echo $RB | sed "s#READ_ROOT=$S/reads#READ_ROOT=reads#")) | chk "D6 a relative READ_ROOT" "REFUSED (TEST_MODE guard): reads is not an absolute path"
rd $(echo $RB | sed 's/TEST_MODE=1 //') | chk "D7 overrides without TEST_MODE" "REFUSED: test-only overrides set"
rd $(echo $RB | sed "s#IO=$S/io_read#IO=$S/io_real#; s#REG_MD5=0#REG_MD5=$RM#") | chk "D8 TEST_MODE against a real (non TEST MODE) registration" "REFUSED: TEST_MODE=1 against a real registration"
echo 'BENCH_EXT=/home/noob/work/el_f1/reports/f1/__no_such__' > $S/pins_bad.sh; printf 'K=%s\n' 0000000000000000000000000000000000000000 > $S/pins_ok.sh
rd $RB PINS_FILE=$S/pins_bad.sh | chk "D10 a PINS_FILE that sets BENCH_EXT (round 1 N4)" "REFUSED: PINS_FILE holds other lines than K=, F2=, W_K=, W_G="
rd $RB PINS_FILE=/home/noob/work/__no_such__/pins.sh | chk "D11 a PINS_FILE outside the scratch root" "REFUSED (TEST_MODE guard): /home/noob/work/__no_such__/pins.sh resolves to"
rd $RB TAG=../../tmp_x | chk "D12 TAG with a path (round 1 N5)" "REFUSED: TAG must be [a-z0-9_]+"
rd $RB PINS_FILE=$S/pins_ok.sh | chk "D13 control: a PINS_FILE with a K= line only passes, a later check refuses" "REFUSED: no $S/io_read/REGISTERED.txt"
rd $RB | chk "D9 control: all paths scratch -> the guard passes, a later check refuses" "REFUSED: no $S/io_read/REGISTERED.txt"
echo "   output folder made by any read case: $([ -n "$(ls -A $S/reads)" ] && echo YES || echo no)"
} | tee $OUT
echo "guard test: $(grep -c '^FAIL' $OUT) FAIL" | tee -a $OUT
rm -rf $S
grep -q "^guard test: 0 FAIL" $OUT
