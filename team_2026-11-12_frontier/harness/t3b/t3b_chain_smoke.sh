#!/bin/bash
# Builder's dry run of the whole T3b chain on gaint CPU with SYNTHETIC data (no sealed image, mask or prediction is read; the
# E1 stem LIST is real; opening #8's REGISTERED.txt is copied as a text record of hashes, so its pinned md5 holds). A stub ssh
# first in PATH runs every cv02 command locally with /tmp/noob_el/ mapped into the scratch dir; the relays are the REAL
# t3b_relay.sh / relay_w1c.sh (74a2ec3d) in the foreground (review round 1 B1c).
#   zero-shot stand-ins: 3 tiny runs in a fake F2 deploy dumped by G's bench_infer as opening #8 rendered its C2 E1 lines,
#     relayed layout; their records by R's scorer (the read compares them)
#   -> t3b_register.sh (TEST_MODE) -> build refused without the ledger row (N6) -> a scratch ledger gets row #9 -> build
#      (label precheck in memory, then K's builder) -> stage (DT, DS)
#   -> 33 tiny training runs in a fake K deploy + their cv02-side units (slim, LATEST.md5, RUN.md5) + t3b's launch.log ->
#      gate refused (no relay yet) -> t3b_relay.sh train (33 of 33, no dump unit) -> deploy (latest.pth x 3) -> gate passes
#   -> the 30 lines of jobs_dump.txt by K's bench_infer as cq.sh renders them (cpu; images from the staged DS), RUN.md5 as cq.sh
#      writes them -> t3b_relay.sh dump with the 33 training RUN.md5 present (30 of 30, no training unit)
#   -> read negatives -> run_t3b_read.sh -> swapped ALL / HALF read refused by the verdict (B2) -> tampered copies of the queue,
#      relay, read and verdict refused (B2) -> TAG checks and a repeat read (N5) -> unstage (30 dump dirs, DS, DT removed).
# Usage: bash t3b_chain_smoke.sh <out dir>   (about 15 to 25 CPU-min, nice 19)
set -u
OUT=${1:?out}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
P=/home/noob/work/el-fault-detection/.venv/bin/python; KT=/home/noob/work/bench_wt_t3b; GT=/home/noob/work/bench_wt_openg; RT0=/home/noob/work/bench_wt_open
KC=$(grep -m1 '^KC=' $HERE/t3b_queue.sh | cut -d= -f2 | cut -d';' -f1); K7=${KC:0:7}
F2=9967d59abaab03cef83c1e3014840b2359ef45d7; G=8bd1c2761c85f4721e444a8bf7124d2e5804973a; R=0c72cf942a5cc89accfcd02e1d2b443a033549d9
S=/home/noob/work/bench_int_io/t3b/chain_$$; [ -e $S ] && exit 1; mkdir -p $S/bin $S/noob_el $OUT || exit 1
export CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1
[ "$(git -C $KT rev-parse HEAD)" = "$KC" ] && [ "$(git -C $GT rev-parse HEAD)" = "$G" ] && [ "$(git -C $RT0 rev-parse HEAD)" = "$R" ] || { echo "worktrees not at K / G / R"; exit 1; }
say(){ echo "$*" | tee -a $OUT/chain_smoke.out; }
say "[$(date '+%F %T')] T3b chain smoke in $S (K $KC; script $(md5sum < $0 | cut -c1-8))"
cat > $S/bin/ssh <<EOF
#!/bin/bash
c="\${@: -1}"; c=\${c//\/tmp\/noob_el\//$S/noob_el/}
exec bash -c "\$c"
EOF
chmod +x $S/bin/ssh
nice -n 19 $P $HERE/t3b_smoke_synth.py ext $S/ext117 | tee -a $OUT/chain_smoke.out
mkdir -p $S/open_reg && cp /home/noob/work/bench_open_io/REGISTERED.txt $S/open_reg/REGISTERED.txt
# ---- the zero-shot comparator stand-ins
POOLR=$S/noob_el/bench_data_fin/roots/pool532_v11; mkdir -p $POOLR/splits; echo ARTS_pool_only_r1_c1 > $POOLR/splits/train.txt
ZSN="fin_hrnet_swad_v11_pool_s5 fin_hrnet_swad_v11_pool_s6 fin_hrnet_swad_v11_pool_s7"
nice -n 19 $P $HERE/t3b_smoke_synth.py runs $S/noob_el/bench_9967d59 $F2 "fin_=$POOLR" $S/relay_fin2 $ZSN | tee -a $OUT/chain_smoke.out
RO=$S/relay_open; mkdir -p $RO/.ok $S/open8_records; : > $RO/relay.log
CARD=bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml; MX=hrnet_w18_unetpp_swad_const_pf_v11
for r in $ZSN; do n=$r.swad.tta_d4.e1_106
  (cd $GT && BENCH_EXT=$S/ext117 OMP_NUM_THREADS=4 nice -n 19 $P -u scripts/bench_infer.py --run $S/noob_el/bench_9967d59/experiments/$r --set e1_106 \
    --opening e1_open8_final --dumps $RO/$n/dumps --method $MX --card $CARD --run-id $n --weights-key swad --tta d4 --device cpu --precision fp32 \
    --threads 4 --workers 0 --batch 8 --logp --ens-member --forbidden /nonexistent --bench-run dump_$n > $S/zslog_$n.txt 2>&1) || { say "ZS DUMP FAILED $n"; exit 1; }
  mkdir -p $RO/$n/runs/$n; (cd $RO/$n && find dumps -type f | sort | xargs md5sum > runs/$n/RUN.md5)
  echo "$(date '+%F %T') RUN.md5 $(md5sum < $RO/$n/runs/$n/RUN.md5 | cut -c1-32) files $(grep -c . $RO/$n/runs/$n/RUN.md5)" > $RO/.ok/$n
  echo "[$(date '+%F %T')] relayed $n: smoke" >> $RO/relay.log
  (cd $RT0 && BENCH_EXT=$S/ext117 nice -n 19 $P scripts/bench_score.py records --dumps $RO/$n/dumps/elbench1/$MX/$n/e1_106 --set e1_106 --opening e1_open8_final --out $S/open8_records/$n.json > /dev/null) || { say "R records failed $n"; exit 1; }
done
say "zero-shot stand-ins: 3 relayed units in $RO (G's bench_infer), 3 records by R's scorer"
# ---- registration, ledger, build, stage
REGE="TEST_MODE=1 IO=$S/io EXT_DIR=$S/ext117 RD_OPEN=$RO OPEN_REG=$S/open_reg/REGISTERED.txt"
env $REGE bash $HERE/t3b_register.sh > $OUT/register.out 2>&1; rc=$?; say "register rc $rc ($(grep -m1 'REGISTERED.txt md5' $OUT/register.out | cut -c1-80); $(grep -c '^scripts ' $S/io/REGISTERED.txt) scripts line)"; [ $rc = 0 ] || exit 1
REG=$(cat $S/io/REGISTERED.md5) || exit 1
LED=$S/ledger/e1_openings.md; mkdir -p $S/ledger; grep -m1 -F "| # | protocol | models |" /home/yugma/mtp/research/team_2026-10-31_next/e1_openings.md > $LED
QE="TEST_MODE=1 REG_MD5=$REG IO=$S/io EXT_DIR=$S/ext117 RD1=$S/relay_t3b RD2=$S/relay_t3bopen READ_OUT=$S/reads/t3b_open9 LEDGER=$LED K=$KC"
env $QE bash $HERE/t3b_queue.sh build > $OUT/neg_build_noledger.out 2>&1; say "negative build without ledger row #9: rc $? ($(tail -1 $OUT/neg_build_noledger.out | cut -c1-110)); IO/data made: $([ -e $S/io/data ] && echo yes || echo no)"
grep '^| 9 |' $OUT/register.out >> $LED
env $QE bash $HERE/t3b_queue.sh build > $OUT/build.out 2>&1; rc=$?; say "build rc $rc ($(grep -m1 '^label precheck' $OUT/build.out | cut -c1-90); $(grep -m1 '^ROOTS_t3b' $OUT/build.out | cut -c1-60); $(grep '^t3b_' $OUT/build.out | sort -u | wc -l) roots; $(grep -m1 '^CHECK OK' $OUT/build.out | cut -c1-40))"; [ $rc = 0 ] || exit 1
env $QE PATH=$S/bin:$PATH bash $HERE/t3b_queue.sh stage > $OUT/stage.out 2>&1; rc=$?; say "stage rc $rc ($(grep -E '^DT |^DS ' $OUT/stage.out | cut -c1-80 | tr '\n' ' '))"; [ $rc = 0 ] || exit 1
env $QE PATH=$S/bin:$PATH bash $HERE/t3b_queue.sh stage > $OUT/stage_again.out 2>&1; say "negative stage twice: rc $? ($(tail -1 $OUT/stage_again.out | cut -c1-100))"
# ---- the 33 trainings (tiny runs) as t3b leaves them, the gate, the training relay, the deploy latest.pth
KB=$S/noob_el/bench_$K7; DTR=$S/noob_el/bench_data_t3b/roots
TN=$(cut -d'|' -f1 $S/io/jobs_train.txt | tr '\n' ' ')
nice -n 19 $P $HERE/t3b_smoke_synth.py runs $KB $KC "$(for a in all half; do for k in 0 1 2 3 4; do printf 't3b_%s_f%s_=%s/t3b_%s_f%s,' $a $k $DTR $a $k; done; done)t3b_deploy_=$DTR/t3b_deploy" $S/synth_unused $TN | tee -a $OUT/chain_smoke.out
nice -n 19 $P $HERE/t3b_smoke_synth.py units $KB $TN | tee -a $OUT/chain_smoke.out
Q1=$S/noob_el/bench_q/t3b; mkdir -p $Q1; { for n in $TN; do echo "[x] trained $n rc=0 (GPU 0)"; done; echo "[x] BENCH CV02 Q ALL DONE (33 trained rc 0)"; } > $Q1/launch.log
env $QE PATH=$S/bin:$PATH bash $HERE/t3b_queue.sh gate > $OUT/neg_gate_norelay.out 2>&1; say "negative gate before the training relay: rc $? ($(tail -1 $OUT/neg_gate_norelay.out | cut -c1-140))"
RLE="TEST_MODE=1 REG_MD5=$REG IO=$S/io RD1=$S/relay_t3b RD2=$S/relay_t3bopen POLL=1 FG=1 PATH=$S/bin:$PATH"
env $RLE bash $HERE/t3b_relay.sh train > $OUT/relay_train.out 2>&1; say "relay train rc $? ($(tail -1 $OUT/relay_train.out | cut -c1-90)); units in RD1 $(ls $S/relay_t3b/.ok | wc -l), of which dump units $(ls $S/relay_t3b/.ok | grep -c 'e1t3b')"
env $RLE bash $HERE/t3b_relay.sh deploy > $OUT/relay_deploy.out 2>&1; say "relay deploy rc $? ($(tail -1 $OUT/relay_deploy.out | cut -c22-80)); latest.pth in RD1: $(ls $S/relay_t3b/t3b_deploy_s*/experiments/*/checkpoints/latest.pth 2>/dev/null | wc -l)"
env $QE PATH=$S/bin:$PATH bash $HERE/t3b_queue.sh gate > $OUT/gate.out 2>&1; say "gate after the training relay: rc $? ($(tail -1 $OUT/gate.out | cut -c1-150))"
# ---- the 30 dumps as cq.sh renders them (cpu; images from the staged DS), RUN.md5 as cq.sh writes them; the dump relay
run_job(){ IFS='|' read -r name card seed root fold gate dgate logp extra <<< "$1"; set -- $extra
  local run=${2/\/tmp\/noob_el\//$S/noob_el/} st=$8 m=$MX
  (cd $KT && BENCH_EXT=$S/noob_el/bench_data_sealed/e1_106 OMP_NUM_THREADS=2 nice -n 19 $P -u scripts/bench_infer.py --run $run --set $st --opening e1_open9_t3b \
    --dumps $KB/dumps --method $m --card $card --run-id $name --weights-key $4 --tta $6 --device cpu --precision fp32 --threads 2 --workers 0 \
    --batch 8 --forbidden /nonexistent --bench-run dump_$name > $S/dlog_$name.txt 2>&1) || { echo "DUMP FAILED $name"; return 1; }
  mkdir -p $KB/runs/$name; (cd $KB && find dumps -path "dumps/*/$m/$name/*" -type f | sort | xargs -d '\n' md5sum > runs/$name/RUN.md5.tmp && mv runs/$name/RUN.md5.tmp runs/$name/RUN.md5); }
export -f run_job; export S KT P KB MX
t0=$(date +%s)
grep . $S/io/jobs_dump.txt | xargs -P ${PAR:-4} -d '\n' -I{} bash -c 'run_job "$@"' _ {} | tee -a $OUT/chain_smoke.out
Q2=$S/noob_el/bench_q/t3bopen; mkdir -p $Q2; echo "[x] BENCH CV02 Q ALL DONE (0 trained rc 0, 30 dumped rc 0)" > $Q2/launch.log
say "T3b dumps: $(ls -d $KB/dumps/elbench1/$MX/* | wc -l) of 30 in $(( $(date +%s) - t0 )) s; marked trained_on_e1: $(grep -l '"trained_on_e1": true' $KB/dumps/elbench1/$MX/*/*/manifest.json | wc -l); RUN.md5 in KB/runs: $(ls $KB/runs/*/RUN.md5 | wc -l) (33 training + 30 dump)"
env $RLE bash $HERE/t3b_relay.sh dump > $OUT/relay_dump.out 2>&1; say "relay dump rc $? ($(tail -1 $OUT/relay_dump.out | cut -c1-90)); units in RD2 $(ls $S/relay_t3bopen/.ok | wc -l), of which training units $(ls $S/relay_t3bopen/.ok | grep -vc 'e1t3b'); RD1 still $(ls $S/relay_t3b/.ok | wc -l)"
# ---- the read: negatives first (each must refuse and leave no output folder), then the read, then an existing output
types=(halfcut_multi multi mono halfcut_mono); printf 'stem\tsource\tcell_type\n' > $S/cells.tsv
i=0; for s in $(grep . $S/ext117/stems_eval.txt); do printf '%s\t%s\t%s\n' $s ${s%%_*} ${types[$((i % 4))]} >> $S/cells.tsv; i=$((i+1)); done
RE="TEST_MODE=1 IO=$S/io RD1=$S/relay_t3b RD2=$S/relay_t3bopen RD_OPEN=$RO RF=$S/relay_fin2 READ_ROOT=$S/reads BENCH_EXT=$S/ext117 CELLS_TSV=$S/cells.tsv OPEN8_RECORDS=$S/open8_records DEVICE_OK=cpu"
neg(){ local t=$1; shift; env $RE "$@" bash $HERE/run_t3b_read.sh > $OUT/neg_$t.out 2>&1; say "negative $t: rc $? ($(grep -m1 -E 'REFUSED|FAIL' $OUT/neg_$t.out | cut -c1-110)); out dir created: $([ -e $S/reads/t3b_open9 ] && echo yes || echo no)"; }
neg regmd5 REG_MD5=0000
m=$(ls $S/relay_t3bopen/t3b_half_f3_s6.swad.tta_d4.e1t3b_f3/dumps/elbench1/$MX/*/e1t3b_f3/manifest.json); cp $m $S/m.bak; chmod u+w $m
sed -i 's/"e1_train_cells": [0-9]*/"e1_train_cells": 85/' $m; neg manifest_e1count REG_MD5=$REG; cp $S/m.bak $m
z=$(ls $RO/fin_hrnet_swad_v11_pool_s6.swad.tta_d4.e1_106/dumps/elbench1/$MX/*/e1_106/*.npz | head -1); cp $z $S/z.bak; chmod u+w $z; printf x >> $z
neg zs_changed REG_MD5=$REG; cp $S/z.bak $z
e=$S/ext117/masks/$(head -1 $S/ext117/stems_eval.txt).png; cp $e $S/e.bak; chmod u+w $e; printf x >> $e
neg e1_mask_changed REG_MD5=$REG; cp $S/e.bak $e
neg tag_path REG_MD5=$REG TAG=../x
env $(echo $RE | sed 's/TEST_MODE=1 //') REG_MD5=$REG bash $HERE/run_t3b_read.sh > $OUT/neg_notest.out 2>&1; say "negative overrides without TEST_MODE: rc $? ($(tail -1 $OUT/neg_notest.out | cut -c1-90)); out dir created: $([ -e $S/reads/t3b_open9 ] && echo yes || echo no)"
env $QE PATH=$S/bin:$PATH bash $HERE/t3b_queue.sh unstage > $OUT/neg_unstage_before_read.out 2>&1; say "negative unstage before the read: rc $? ($(tail -1 $OUT/neg_unstage_before_read.out | cut -c1-100)); DT $([ -d $S/noob_el/bench_data_t3b ] && echo kept || echo removed)"
# tampered copies of the registered scripts (B2): a copy of H3 with one comment line appended to one script each time
for f in run_t3b_read.sh t3b_verdict.py t3b_queue.sh t3b_relay.sh; do
  C=$S/h3copy_${f%%.*}; mkdir -p $C && cp -r $HERE/lists $C/ && cp $HERE/*.sh $HERE/*.py $HERE/T3B_RULE.md $C/ && echo "# tampered" >> $C/$f
  case $f in run_t3b_read.sh|t3b_verdict.py) o=$(env $RE REG_MD5=$REG bash $C/run_t3b_read.sh 2>&1 | grep -m1 REFUSED);;
    t3b_queue.sh) o=$(env $QE PATH=$S/bin:$PATH bash $C/t3b_queue.sh gate 2>&1 | grep -m1 REFUSED);;
    t3b_relay.sh) o=$(env $RLE bash $C/t3b_relay.sh deploy 2>&1 | grep -m1 REFUSED);; esac
  say "negative tampered $f: ${o:-NOT REFUSED}"; done
say "  out dir created by any negative: $([ -e $S/reads/t3b_open9 ] && echo yes || echo no)"
env $RE REG_MD5=$REG bash $HERE/run_t3b_read.sh > $OUT/read.out 2>&1; rc=$?
say "read rc $rc"
grep -E "manifest check|records:|zero-shot re-score|strata|T3B VERDICT|ALL DONE" $OUT/read.out | cut -c1-200 | tee -a $OUT/chain_smoke.out
cp $S/reads/t3b_open9/verdict.txt $OUT/verdict_synthetic.txt 2>/dev/null; cp $S/reads/t3b_open9/read_t3b/read.txt $OUT/read_t3b_synthetic.txt 2>/dev/null
cp $S/reads/t3b_open9/MD5.txt $OUT/MD5_synthetic.txt 2>/dev/null
env $RE REG_MD5=$REG bash $HERE/run_t3b_read.sh > $OUT/neg_exists.out 2>&1; say "negative existing output: rc $? ($(tail -1 $OUT/neg_exists.out | cut -c1-80))"
# the reviewer's swapped read (B2): ALL and HALF record lists exchanged -> the verdict refuses
O=$S/reads/t3b_open9
(cd $KT && nice -n 19 $P scripts/bench_open_read.py --set e1_106 --arm "ALL=$(ls $O/records/oof/t3b_half_s*.oof.json | paste -sd,)" --arm "HALF=$(ls $O/records/oof/t3b_all_s*.oof.json | paste -sd,)" \
  --arm "ZS=$(ls $O/records/zs/*.json | paste -sd,)" --pair ZS=ALL --pair ZS=HALF --pair HALF=ALL --t3b ZS --celltypes $S/cells.tsv --boot 2000 --out $S/swapped > /dev/null 2>&1)
o=$($P $HERE/t3b_verdict.py --read $S/swapped/read.json --reg $S/io/REGISTERED.txt --out $S/swapped/verdict.txt 2>&1 | tail -1); say "negative swapped ALL / HALF read: verdict $(echo "$o" | cut -c1-170); verdict written: $([ -e $S/swapped/verdict.txt ] && echo yes || echo no)"
env $RE REG_MD5=$REG TAG=rep1 bash $HERE/run_t3b_read.sh > $OUT/read_repeat.out 2>&1; say "repeat read TAG=rep1: rc $? ($(grep -m1 '^REPEAT' $OUT/read_repeat.out)); verdict header: $(sed -n 3p $S/reads/t3b_open9_rep1/verdict.txt 2>/dev/null | cut -c1-60)"
# ---- unstage through the stub
env $QE PATH=$S/bin:$PATH bash $HERE/t3b_queue.sh unstage > $OUT/unstage.out 2>&1; say "unstage rc $? ($(grep -E 'REMOVED|removed|REFUSED' $OUT/unstage.out | cut -c1-120 | tr '\n' ' '))"
say "  after unstage: dump dirs left $(ls -d $KB/dumps/elbench1/$MX/* 2>/dev/null | wc -l); runs/*/RUN.md5 kept $(ls $KB/runs/*/RUN.md5 2>/dev/null | wc -l); DS $([ -d $S/noob_el/bench_data_sealed ] && echo kept || echo removed); DT $([ -d $S/noob_el/bench_data_t3b ] && echo kept || echo removed); removal log lines $(grep -c removed $S/noob_el/removed_relayed_dumps_t3b.log 2>/dev/null)"
say "[$(date '+%F %T')] chain smoke done (read rc $rc); scratch removed"
chmod -R u+w $S; rm -rf $S
exit $rc
