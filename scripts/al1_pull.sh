#!/bin/bash
# Pull AL1 outputs from cv02 into results/al1 (after al1_post.sh): re-score JSONs, launch.log, per-image, histograms,
# E1 JSONs (results/e1/raw_v2), regions.csv per run, training-log watch (shares.py, steps 4,000-20,000) and gshare series.
set -euo pipefail
cd /home/yugma/mtp/research; O=results/al1; mkdir -p $O/raw $O/regions results/e1/raw_v2
CV="ssh -o BatchMode=yes cv02@10.8.1.106"; R=/tmp/noob_el/el_alhvr
$CV "cd $R && tar cf - reports/al1/al1_*_s[0-4].json reports/al1/launch.log reports/al1post experiments/al1_*_s[0-4]/regions.csv" | tar xf - -C $O --transform 's#^reports/al1/al1_#raw/al1_#' --transform 's#^reports/al1/launch.log#launch.log#' --transform 's#^reports/al1post/#post/#' --transform 's#^experiments/\(al1_[^/]*\)/regions.csv#regions/\1.csv#'
cp $O/post/per_image.json $O/post/hist_revised.npz $O/
$CV "cd /tmp/noob_el/diag/e1v2 && tar cf - al1_*_s[0-4].json" | tar xf - -C results/e1/raw_v2
$CV "cd $R && /tmp/noob_el/el-fault-detection/.venv/bin/python reports/al1/shares.py experiments 4000 20000 $(for a in AL5 ALd5 ALdh5 CPS5 CPSm5 BsM5; do for s in 0 1 2 3 4; do printf "al1_${a}_s$s "; done; done)" > $O/watch_4k_20k.txt
$CV "cd $R && for f in experiments/al1_*_s[0-4].stdout; do echo \"\$(basename \$f .stdout) \$(grep -o 'grad share @ step [0-9]*  .*gshare_a=[0-9.e+-]*' \$f | awk '{print \$5\":\"\$NF}' | sed 's/gshare_a=//' | tr '\n' ' ')\"; done" > $O/gshare_series.txt
ls $O/raw | wc -l; ls results/e1/raw_v2/al1_* | wc -l; ls $O/regions | wc -l
