#!/bin/bash
# runner DRAFT (1 Nov 2026): B6 cv02 deploy, step "stage on gaint" (called by b6_deploy.sh; CPU only, nice 19). Builds ST, the exact
# tree that lands at cv02 /tmp/noob_el/el_b6:
#   ./ (+ CODE.md5)       git archive of e5441339 (el_f3) + REVISION (full hash)
#   b6_roots/             builder's 5 roots: splits/{train,val,test}.txt + SPLITS.md5 + DATA_MANIFEST.md5, ROOTS.md5, b6_forbidden.txt
#                         (no labeled symlink; cv02 links labeled -> b6_data/labeled)
#   b6_data/labeled/      ONLY the 532 B6 stems' images + masks_escdd (DATA_MANIFEST 2630f630, 1,064 files; cp -L from el-fault-detection)
#   frozen/               the 13 FROZEN_B6.md5 files at their laptop-relative paths + exp/*.txt + b6_valcmp.py (from the laptop)
#   b6s/ q/ bin/          copies from frozen/: b6_score.py, b6_valcmp.py, forbidden, folds | b6_jobs.txt, exp/, ref_SUP/SUPPF.yaml
#                         (gaint pf2 s5 config_used.yaml ba0b243d / 6aba106a) | queue, gpumem, identity, b6_verify_cv02.sh
#   experiments/          empty; DEPLOY.md5 over every file
# Prints "OK <n files> <DEPLOY.md5 md5>" on success; any failed check exits non-zero (set -e) before printing OK.
set -euo pipefail
R=${R:-/home/noob/work/runner_b6deploy}; ST=$R/el_b6; FI=$R/frozen_in; E=/home/noob/work/el_f3; RT=/home/noob/work/b6
LAB=/home/noob/work/el-fault-detection/data/labeled; H=e5441339768b9e7ec54fd4de0b50b2a819bfbeab
chk(){ [ "$(md5sum < "$1" | cut -c1-8)" = "$2" ] || { echo "md5 FAIL $1 (want $2)" >&2; exit 1; }; }
[ ! -e $ST ] || { echo "$ST exists" >&2; exit 1; }
chk $FI/results/b6/FROZEN_B6.md5 807d4d03
(cd $FI && md5sum -c --quiet results/b6/FROZEN_B6.md5)
(cd $FI/results/b6/jobs && md5sum -c --quiet exp/EXP.md5)
chk $FI/scripts/b6/b6_valcmp.py 1ad95d68
chk $RT/ROOTS.md5 e4100381; chk $RT/b6_root_0/DATA_MANIFEST.md5 2630f630
chk $E/experiments/pf2_SUP_100pct_s5/config_used.yaml ba0b243d; chk $E/experiments/pf2_SUPPF_100pct_s5/config_used.yaml 6aba106a
mkdir -p $ST
git -C $E archive --format=tar $H | tar xf - -C $ST
# guard: no image under data/ and no weight file anywhere (the archive's 7 reports/ figure PNGs are plots, shipped as in earlier deploys)
[ -z "$(find $ST/data -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.tif*' \))" ] || { echo "archive holds images under data/" >&2; exit 1; }
[ -z "$(find $ST -type f \( -iname '*.pth' -o -iname '*.pt' -o -iname '*.safetensors' -o -iname '*.ckpt' \))" ] || { echo "archive holds weight files" >&2; exit 1; }
echo $H > $ST/REVISION
(cd $ST && find . -type f ! -name REVISION | sort | xargs -d '\n' md5sum > $R/CODE.md5.tmp) && mv $R/CODE.md5.tmp $ST/CODE.md5
for k in 0 1 2 3 4; do mkdir -p $ST/b6_roots/b6_root_$k/splits
  cp $RT/b6_root_$k/splits/{train,val,test}.txt $ST/b6_roots/b6_root_$k/splits/
  cp $RT/b6_root_$k/SPLITS.md5 $RT/b6_root_$k/DATA_MANIFEST.md5 $ST/b6_roots/b6_root_$k/; done
cp $RT/ROOTS.md5 $RT/b6_forbidden.txt $ST/b6_roots/
(cd $ST/b6_roots && md5sum -c --quiet ROOTS.md5)
mkdir -p $ST/b6_data/labeled/images $ST/b6_data/labeled/masks_escdd
awk '{print $2}' $RT/b6_root_0/DATA_MANIFEST.md5 | while read -r p; do cp -L "$LAB/${p#labeled/}" "$ST/b6_data/$p"; done
(cd $ST/b6_data && md5sum -c --quiet $RT/b6_root_0/DATA_MANIFEST.md5)
[ "$(find $ST/b6_data -type f | wc -l)" = 1064 ]
n=$(find $ST/b6_data/labeled/images -name '*.png' -printf '%f\n' | sed 's/\.png$//' | sort | comm -12 - <(sort $RT/b6_forbidden.txt) | wc -l); [ "$n" = 0 ]
mkdir -p $ST/frozen $ST/b6s $ST/q $ST/bin $ST/experiments
cp -a $FI/. $ST/frozen/
cp $ST/frozen/scripts/b6/b6_score.py $ST/frozen/scripts/b6/b6_valcmp.py $ST/frozen/results/b6/b6_forbidden.txt $ST/frozen/results/b6/b6_folds.tsv $ST/b6s/
cp $ST/frozen/results/b6/jobs/b6_jobs.txt $ST/q/; cp -r $ST/frozen/results/b6/jobs/exp $ST/q/exp
cp $E/experiments/pf2_SUP_100pct_s5/config_used.yaml $ST/q/ref_SUP.yaml; cp $E/experiments/pf2_SUPPF_100pct_s5/config_used.yaml $ST/q/ref_SUPPF.yaml
cp $ST/frozen/scripts/b6/b6_cv02_queue.sh $ST/frozen/scripts/b6/b6_cv02_gpumem.sh $ST/frozen/scripts/b6/b6_cv02_identity.sh $R/b6_verify_cv02.sh $ST/bin/
(cd $ST && find . -type f ! -name DEPLOY.md5 | sort | xargs -d '\n' md5sum > DEPLOY.md5)
echo "OK $(wc -l < $ST/DEPLOY.md5) $(md5sum < $ST/DEPLOY.md5 | cut -c1-32)"
