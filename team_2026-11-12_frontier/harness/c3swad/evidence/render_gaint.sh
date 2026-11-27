#!/bin/bash
# c3swad: render-only run of the PATCHED cq.sh on gaint with the REAL card code (bench.cards of the 89b9ea5 tree), split
# mode (B = unpatched tree, QC = patched tree), on the preview of the merged list. cq.sh stops at the logger check.
# Sandbox edits: the env.sh line; the python wrapper skips cvcard.py (cv02 weights paths do not exist on gaint).
set -u
S=${S:?}; R=$S/rs; P0=/home/noob/work/el-fault-detection/.venv/bin/python
[ -e $R ] && { echo "REFUSED: $R exists"; exit 1; }
mkdir -p $R/data/meta $R/q; export CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1
cp -r $S/stB $R/B; cp -r $S/stQ $R/QC
sed -i 's#^\. /tmp/noob_el/env\.sh.*#:#' $R/QC/bench/q/cv02/cq.sh
(cd $R/QC && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5)
ln -s /home/noob/work/bench_data/roots $R/data/roots; echo x > $R/data/meta/forbidden_v1.txt; (cd $R/data && md5sum meta/forbidden_v1.txt > DEPLOY.md5)
printf '#!/bin/bash\ncase "$1" in */cvcard.py) exit 0;; esac\nexec %s "$@"\n' $P0 > $R/python; chmod +x $R/python
sed 's#/tmp/noob_el/bench_data_v3b/#/home/noob/work/bench_data_v3b/#' $S/io1/preview_jobs.txt > $R/q/jobs.txt; echo 1 > $R/q/LPG
echo "[$(date '+%F %T')] render start: $(wc -l < $R/q/jobs.txt) jobs"
B=$R/B Q=$R/q QC=$R/QC JOBS_MD5=$(md5sum < $R/q/jobs.txt | cut -c1-32) DEPLOY=89b9ea5a12a37a87c16c4868cc4adf00794a7610 DATA_MD5=$(md5sum < $R/data/DEPLOY.md5 | cut -c1-32) \
  DATA=$R/data DATA_V3=/home/noob/work/bench_data_v3b P=$R/python nice -n 19 bash $R/QC/bench/q/cv02/cq.sh > $R/stdout 2>&1
echo "[$(date '+%F %T')] rc=$? last log line: $(tail -1 $R/q/launch.log | cut -c23-200)"
# map the sandbox paths to the cv02 paths
sed "s#$R/python#/tmp/noob_el/el-fault-detection/.venv/bin/python#g; s#$R/B/#/tmp/noob_el/bench_89b9ea5/#g; s#$R/data/#/tmp/noob_el/bench_data/#g; s#/home/noob/work/bench_data_v3b/#/tmp/noob_el/bench_data_v3b/#g" $R/q/jobs_rendered.txt > $R/rendered_cv02paths.txt
grep -vE '^(dump_)?c3s_swad_' $R/rendered_cv02paths.txt > $R/carried.txt
echo "rendered $(wc -l < $R/q/jobs_rendered.txt) lines; carried $(wc -l < $R/carried.txt), of them byte-equal to a line of cv02 c3all's own jobs_rendered.txt (97bb83fc): $(grep -cFxf $S/io1/preview_prev_rendered.txt $R/carried.txt); swad lines $(grep -cE '^(dump_)?c3s_swad_' $R/rendered_cv02paths.txt)"
echo "cv02 c3all jobs_rendered.txt md5 $(md5sum < $S/io1/preview_prev_rendered.txt | cut -c1-8), $(wc -l < $S/io1/preview_prev_rendered.txt) lines"
grep -E '^(dump_)?c3s_swad_v11_f0_s5' $R/rendered_cv02paths.txt
echo "ALL DONE"
