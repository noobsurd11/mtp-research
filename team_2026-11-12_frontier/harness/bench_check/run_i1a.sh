#!/bin/bash
# I1a: CPU fp32 dump of f3_SUPPF_100pct_s0 on val54 through bench_infer + bench_score == b6's CPU check record (54 cells);
# I3 round trip; GT-only reference rows on val54 and cv5v1_f0; one summary (smoke of the summary path). CPU only, nice 19.
# Settings as b6 scorechk.sh 0be80a2c: 4 threads, 4 loader workers, batch 8.
set -u
O=/home/noob/work/bench_check/i1a; mkdir -p $O; L=$O/run.log; DU=/home/noob/work/bench_dumps/t1
P=/home/noob/work/el-fault-detection/.venv/bin/python; R=/home/noob/work/el_bench
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
RUN=/home/noob/work/b6_build/check/runs/f3_SUPPF_100pct_s0; REF=/home/noob/work/b6_build/check/out_cpu/f3_SUPPF_100pct_s0.check.json
cd $R
nice -n 19 $P scripts/bench_infer.py --run $RUN --set val54 --dumps $DU --method house_r34_unetpp_pf --card bench/methods/house_r34_unetpp_pf.yaml --device cpu --precision fp32 --threads 4 --workers 4 --batch 8 > $O/infer.log 2>&1
rc=$?; echo "[$(date '+%F %T')] infer rc=$rc: $(tail -1 $O/infer.log)" >> $L
SD=$DU/elbench1/house_r34_unetpp_pf/f3_SUPPF_100pct_s0/val54
nice -n 19 $P scripts/bench_score.py records --dumps $SD --set val54 --out $O/rec_val54.json > $O/records.log 2>&1
rc=$?; echo "[$(date '+%F %T')] records rc=$rc: $(tail -1 $O/records.log)" >> $L
$P scripts/bench_score.py compare --a $O/rec_val54.json --b $REF --b-cells cells/heldout > $O/i1a_compare.txt 2>&1
rc=$?; echo "[$(date '+%F %T')] I1a compare rc=$rc: $(cat $O/i1a_compare.txt)" >> $L
nice -n 19 $P /home/noob/work/bench_check/i3_roundtrip.py $SD val54 > $O/i3.txt 2>&1
rc=$?; echo "[$(date '+%F %T')] I3 rc=$rc: $(cat $O/i3.txt)" >> $L
for s in val54 cv5v1_f0; do nice -n 19 $P scripts/bench_score.py refrows --set $s --out $O/ref_$s.json > $O/ref_$s.log 2>&1
  rc=$?; echo "[$(date '+%F %T')] refrows $s rc=$rc: $(tail -1 $O/ref_$s.log)" >> $L; done
nice -n 19 $P scripts/bench_score.py summary --records $O/rec_val54.json --arms PF='f3_SUPPF.*' --ref $O/ref_val54.json --celltypes bench/sets/celltypes.tsv --out $O/sum_val54.json > $O/summary.log 2>&1
rc=$?; echo "[$(date '+%F %T')] summary rc=$rc: $(tail -1 $O/summary.log)" >> $L
du -sb $SD | awk '{printf "dump dir bytes %d (%.2f MiB per cell over 54)\n", $1, $1/54/1048576}' >> $L
echo "[$(date '+%F %T')] i1a done" >> $L
