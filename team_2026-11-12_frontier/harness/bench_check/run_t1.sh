#!/bin/bash
# tranche-1 unit tests on el_bench (CPU only, nice 19, 8 threads).
set -u
O=/home/noob/work/bench_check/t1; mkdir -p $O; L=$O/run.log
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 BENCH_MODEL_REPORT=$O/models_report.txt
cd /home/noob/work/el_bench
nice -n 19 $P -m pytest -q -p no:cacheprovider tests/test_bench_dumpfmt.py tests/test_bench_m0core_ast.py tests/test_bench_score_ext.py tests/test_bench_cards.py tests/test_bench_models.py -rs > $O/pytest_bench.log 2>&1
rc=$?; echo "[$(date '+%F %T')] pytest bench tests rc=$rc: $(tail -1 $O/pytest_bench.log)" >> $L
nice -n 19 $P scripts/bench_score.py ast-check > $O/ast.txt 2>&1; rc=$?; echo "[$(date '+%F %T')] ast-check rc=$rc: $(cat $O/ast.txt)" >> $L
nice -n 19 $P -m bench.cards validate bench/methods/*.yaml > $O/cards.txt 2>&1; rc=$?; echo "[$(date '+%F %T')] cards validate rc=$rc: $(tr '\n' ' ' < $O/cards.txt)" >> $L
nice -n 19 $P -m pytest -q -p no:cacheprovider tests > $O/pytest_all.log 2>&1; rc=$?; echo "[$(date '+%F %T')] pytest all rc=$rc: $(tail -1 $O/pytest_all.log)" >> $L
echo "[$(date '+%F %T')] t1 done" >> $L
