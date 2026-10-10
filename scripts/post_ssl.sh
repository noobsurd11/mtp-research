#!/bin/bash
# Post-process a finished SSL set (p9 | p10): pull re-score JSONs (cv02, plus gaint for p10's supervised references),
# per-image + histogram scoring of the cv02 runs on cv02, locked rules (scripts/ssl_rules.py), image bootstrap with the
# P9 source split, bars. Usage: bash scripts/post_ssl.sh p9|p10|p11|p12 <cv02 gpu> <expected cv02 JSONs>
# p12 also pulls gaint's p12_g* replication/calibration JSONs (rules only; no per-image scoring for gaint runs).
set -e
E=$1; G=$2; N=$3; R=~/mtp/research; O=$R/results/$E; PY=$R/.venv/bin/python
CV=cv02@10.8.1.106; GA=noob@172.18.22.20; CODE=/tmp/noob_el/$(case $E in p11|p12) echo el_p11;; *) echo el_p7;; esac); RP=$CODE/reports/$E
mkdir -p $O/raw
scp -q -o BatchMode=yes "$CV:$RP/${E}_*_s[0-9].json" $CV:$RP/launch.log $O/raw/
n=$(ls $O/raw/${E}_*_s[0-9].json | grep -vc "/p12_g"); echo "$E: $n cv02 re-score JSONs"; [ "$n" -eq "$N" ] || { echo "expected $N"; exit 1; }
[ $E = p12 ] && scp -q -o BatchMode=yes "$GA:/home/noob/work/el-fault-detection/reports/p12/p12_g*.json" $GA:/home/noob/work/el-fault-detection/reports/p12/launch_gaint.log $O/raw/ 2>/dev/null || true
[ $E = p10 ] && scp -q -o BatchMode=yes "$GA:/home/noob/work/el-fault-detection/reports/p10/p10_A_*.json" $GA:/home/noob/work/el-fault-detection/reports/p10/launch_gaint.log $O/raw/ 2>/dev/null || true
ssh -o BatchMode=yes $CV "source /tmp/noob_el/env.sh; cd $CODE; RUNS=\$(ls $RP/${E}_*_s[0-9].json | grep -v /p12_g | xargs -n1 basename | sed 's/.json//' | tr '\n' ' '); \
  CUDA_VISIBLE_DEVICES=$G /tmp/noob_el/el-fault-detection/.venv/bin/python scripts/per_image_scores.py --runs \$RUNS --out $RP/per_image.json > $RP/per_image.log 2>&1 && \
  CUDA_VISIBLE_DEVICES=$G /tmp/noob_el/el-fault-detection/.venv/bin/python scripts/score_histograms.py --runs \$RUNS --out $RP/hist_revised.npz > $RP/hist.log 2>&1; tail -n 1 $RP/per_image.log $RP/hist.log"
scp -q -o BatchMode=yes $CV:$RP/per_image.json $CV:$RP/hist_revised.npz $O/
cd $R
if [ $E = p9 ]; then
  $PY scripts/ssl_rules.py --dirs $O/raw results/p8/raw results/p6/raw \
    --arms p6:L3_10pct p8:D_10pct p8:B_10pct p8:C_10pct p9:Dx_10pct p9:Bx_10pct p9:Cx_10pct p6:L3_100pct \
    --pairs p9:Cx_10pct=p9:Dx_10pct p9:Bx_10pct=p9:Dx_10pct p9:Cx_10pct=p9:Bx_10pct p9:Dx_10pct=p8:D_10pct \
    --ref p6:L3_100pct --interact p9:Cx_10pct=p9:Dx_10pct,p8:C_10pct=p8:D_10pct | tee $O/${E}_rules.txt
  J="--json $O/per_image.json results/p8/per_image.json --check $O/raw"
  P="p9:Dx_10pct=p9:Cx_10pct p9:Dx_10pct=p9:Bx_10pct p9:Bx_10pct=p9:Cx_10pct p8:D_10pct=p9:Dx_10pct p8:C_10pct=p9:Cx_10pct"
  ARMS=("p6:L3_10pct=A sup. 10%" "p8:D_10pct=D (431)" "p8:B_10pct=B (431)" "p8:C_10pct=C (431)" "p9:Dx_10pct=Dx (12k)" "p9:Bx_10pct=Bx (12k)" "p9:Cx_10pct=Cx (12k)" "p6:L3_100pct=L3 100%")
  T="P9: external unlabelled pool (11,938 cells) vs in-domain (431), L3 base, 10% labels"
  H="$O/hist_revised.npz results/p8/hist_revised.npz"
elif [ $E = p11 ]; then
  $PY scripts/ssl_rules.py --dirs $O/raw results/p9/raw results/p8/raw results/p6/raw \
    --arms p6:L3_10pct p8:D_10pct p11:Dm_10pct p11:Cm_10pct p9:Dx_10pct p11:Dmx_10pct p11:Cmx_10pct p6:L3_100pct \
    --pairs p11:Dm_10pct=p6:L3_10pct p11:Cm_10pct=p11:Dm_10pct p11:Cmx_10pct=p11:Dmx_10pct p11:Cm_10pct=p6:L3_10pct p11:Cmx_10pct=p6:L3_10pct \
    --ref p6:L3_100pct | tee $O/${E}_rules.txt
  J="--json $O/per_image.json results/p6/per_image.json results/p8/per_image.json --check $O/raw"
  P="p6:L3_10pct=p11:Dm_10pct p11:Dm_10pct=p11:Cm_10pct p11:Dmx_10pct=p11:Cmx_10pct p6:L3_10pct=p11:Cm_10pct p6:L3_10pct=p11:Cmx_10pct p8:D_10pct=p11:Dm_10pct"
  ARMS=("p6:L3_10pct=A sup. 10%" "p8:D_10pct=D (P8 view)" "p11:Dm_10pct=Dm (matched)" "p11:Cm_10pct=Cm (431)" "p11:Dmx_10pct=Dmx (12k)" "p11:Cmx_10pct=Cmx (12k)" "p6:L3_100pct=L3 100%")
  T="P11: pipeline-matched Mean Teacher (supervised labelled view), L3 base, 10% labels"
  H="$O/hist_revised.npz"
elif [ $E = p12 ]; then
  $PY scripts/ssl_rules.py --dirs $O/raw results/p11/raw results/p10/raw results/p6/raw \
    --arms p12:A_5pct p10:D_5pct p12:Dm_5pct p12:Cm_5pct p12:Dmx_5pct p12:Cmx_5pct p10:A_5pct p12:gDm_5pct p12:gCm_5pct p6:L3_10pct p12:gA_10pct p6:L3_100pct \
    --pairs p12:Dm_5pct=p12:A_5pct p12:Dm_5pct=p10:D_5pct p12:Cm_5pct=p12:Dm_5pct p12:Cmx_5pct=p12:Dmx_5pct p12:Cm_5pct=p12:A_5pct p12:Cmx_5pct=p12:A_5pct \
      p12:gCm_5pct=p12:gDm_5pct p12:gCm_5pct=p10:A_5pct p12:gA_10pct=p6:L3_10pct \
    --ref p6:L3_100pct --interact p12:Cm_5pct=p12:Dm_5pct,p11:Cm_10pct=p11:Dm_10pct p12:Cmx_5pct=p12:Dmx_5pct,p11:Cmx_10pct=p11:Dmx_10pct | tee $O/${E}_rules.txt
  J="--json $O/per_image.json results/p10/per_image.json --check $O/raw"
  P="p12:A_5pct=p12:Dm_5pct p10:D_5pct=p12:Dm_5pct p12:Dm_5pct=p12:Cm_5pct p12:Dmx_5pct=p12:Cmx_5pct p12:A_5pct=p12:Cm_5pct p12:A_5pct=p12:Cmx_5pct"
  ARMS=("p12:A_5pct=A5 sup. (cv02)" "p10:D_5pct=D5 (P10 view)" "p12:Dm_5pct=Dm5 (455)" "p12:Cm_5pct=Cm5 (455)" "p12:Dmx_5pct=Dmx5 (12k)" "p12:Cmx_5pct=Cmx5 (12k)" "p10:A_5pct=A5 (gaint)" "p12:gDm_5pct=gDm5 (gaint s3-5)" "p12:gCm_5pct=gCm5 (gaint s3-5)" "p6:L3_100pct=L3 100%")
  T="P12: pipeline-matched Mean Teacher at 5% labels (23 cells), L3 base; gaint replication"
  H="$O/hist_revised.npz"
else
  $PY scripts/ssl_rules.py --dirs $O/raw results/p9/raw results/p8/raw results/p6/raw \
    --arms p10:A_5pct p10:D_5pct p10:B_5pct p10:C_5pct p10:Dx_5pct p10:Cx_5pct p6:L3_10pct p6:L3_20pct p10:A_50pct p6:L3_100pct \
    --pairs p10:C_5pct=p10:D_5pct p10:B_5pct=p10:D_5pct p10:C_5pct=p10:B_5pct p10:Cx_5pct=p10:Dx_5pct \
    --ref p6:L3_100pct --interact p10:C_5pct=p10:D_5pct,p8:C_10pct=p8:D_10pct p10:Cx_5pct=p10:Dx_5pct,p9:Cx_10pct=p9:Dx_10pct | tee $O/${E}_rules.txt
  J="--json $O/per_image.json --check $O/raw"
  P="p10:D_5pct=p10:C_5pct p10:D_5pct=p10:B_5pct p10:B_5pct=p10:C_5pct p10:Dx_5pct=p10:Cx_5pct p10:D_5pct=p10:Dx_5pct"
  ARMS=("p10:A_5pct=A sup. 5% (gaint)" "p10:D_5pct=D5 (455)" "p10:B_5pct=B5 (455)" "p10:C_5pct=C5 (455)" "p10:Dx_5pct=Dx5 (12k)" "p10:Cx_5pct=Cx5 (12k)" "p6:L3_10pct=L3 10%" "p10:A_50pct=L3 50% (gaint)" "p6:L3_100pct=L3 100%")
  T="P10: SSL at 5% labels (23 cells), L3 base, in-domain (455) vs external (11,938) pool"
  H="$O/hist_revised.npz"
fi
$PY scripts/per_image_analysis.py $J --pairs $P | tee $O/per_image_test.txt
for k in '^(CSIR|ARTS)_' '^(CFVS|BMRK|SDLE)_'; do
  echo -e "\nSource split, cells matching $k:" | tee -a $O/per_image_test.txt
  $PY scripts/per_image_analysis.py $J --pairs $P --keep "$k" | tee -a $O/per_image_test.txt
done
$PY scripts/ssl_figure.py --dirs $O/raw results/p9/raw results/p8/raw results/p6/raw results/p10/raw results/p11/raw --out $O/fig_${E}_bars.png --title "$T" --arms "${ARMS[@]}" --hist $H | tee -a $O/${E}_rules.txt
