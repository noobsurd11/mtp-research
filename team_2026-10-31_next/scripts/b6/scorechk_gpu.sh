#!/bin/bash
# builder: B6 scorer EXACT check on GPU (protocol_B6 s8.2), for runner to start behind his gate (9,900 MiB free; m0-type pass).
# b6_score.py --mode check on f3_SUPPF_100pct_s0 (latest.pth, step 20000), the 54 val stems (sorted = el_f3 val.txt),
# bf16 autocast, batch 8, TTA off: the same forward path as the opening-1 m0 pass. Then b6_valcmp.py --expect exact
# against the m0 file's VAL block only. Writes only under /home/noob/work/b6_build/check/. No test / E1 cell is scored.
set -u
B=/home/noob/work/b6_build; C=$B/check; P=/home/noob/work/el-fault-detection/.venv/bin/python
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
echo "[$(date +%T)] gpu check start pid $$" >> $C/batch.log
nice -n 19 $P $B/scripts/b6_score.py --code /home/noob/work/el_f3 --out $C/out_gpu --forbidden /home/noob/work/b6/b6_forbidden.txt \
  --mode check --device cuda --runs $C/runs/f3_SUPPF_100pct_s0 --stems $C/valroot/splits/test.txt > $C/score_gpu.log 2>&1; rc=$?
echo "[$(date +%T)] score_gpu rc=$rc" >> $C/batch.log
[ $rc -eq 0 ] || exit $rc
python3 $B/scripts/b6_valcmp.py --b6 $C/out_gpu/f3_SUPPF_100pct_s0.check.json \
  --m0 /home/noob/work/el_f3/reports/f100/post_opening1/m0/f3_SUPPF_100pct_s0.json --expect exact > $C/valcmp_gpu.txt 2>&1; rc=$?
echo "[$(date +%T)] valcmp_gpu rc=$rc (0 = EXACT PASS)" >> $C/batch.log
exit $rc
