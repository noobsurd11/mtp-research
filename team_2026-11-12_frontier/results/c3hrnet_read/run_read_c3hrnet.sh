#!/bin/bash
# HRNet-W18 U-Net++ 5-seed confirmation on cv5v3 (rule pre-registered by the lead in log.md, 18 Nov 2026 00:22, before
# seeds 8 and 9 existed). Lead's script, 18 Nov. One read, all 75 runs (PF, HOUSE, HRNET), cv02 only, relayed copies.
set -u
W=/home/noob/work/bench_wt_final; P=/home/noob/work/el-fault-detection/.venv/bin/python
T=/home/yugma/mtp/research/team_2026-11-12_frontier; X=$T/benchmark/splits/score_exclude_v3.txt
G3=/home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv; O=/home/noob/work/bench_reads/c3hrnet_read; L=$O/links/elbench1
[ "$(git -C $W rev-parse --short HEAD)" = 89b9ea5 ] && [ "$(git -C $W status --porcelain -uno | wc -l)" = 0 ] || { echo "bench_wt_final not clean at 89b9ea5"; exit 1; }
[ "$(md5sum < $W/scripts/bench_read_w1.py | cut -c1-8)" = fdb56b78 ] || { echo "read tool is not fdb56b78"; exit 1; }
[ "$(md5sum < $X | cut -c1-8)" = 6d48dfbd ] || { echo "score_exclude is not 6d48dfbd"; exit 1; }
[ -e $O/read ] && { echo "read folder exists"; exit 1; }
mkdir -p $L/house_r34_unetpp_pf_v11 $L/house_r34_unetpp_v11 $L/hrnet_w18_unetpp_pf_v11
n=0; bad=0
for spec in "c3base c3_pf_v11 house_r34_unetpp_pf_v11" "c3base c3_house_v11 house_r34_unetpp_v11" "c3hrnet c3h_hrnet_w18_unetpp_pf hrnet_w18_unetpp_pf_v11"; do
  set -- $spec; R=/home/noob/work/bench_relay/$1
  for f in 0 1 2 3 4; do for s in 5 6 7 8 9; do r=${2}_f${f}_s${s}; d=$R/$r/dumps/elbench1/$3/$r
    grep -q "relayed $r:" $R/relay.log && [ -d $d ] || { echo "MISSING $r"; bad=$((bad+1)); continue; }
    m=$(ls $d/*/manifest.json 2>/dev/null | head -n 1)
    $P -c 'import json,sys; m=json.load(open(sys.argv[1])); s=json.dumps(m); ok=("RTX A6000" in s) and ("20000" in s); sys.exit(0 if ok else 1)' $m || { echo "MANIFEST $r"; bad=$((bad+1)); }
    [ -e $L/$3/$r ] || ln -s $d $L/$3/$r; n=$((n+1)); done; done; done
echo "linked $n runs, problems $bad"; [ $n = 75 ] && [ $bad = 0 ] || exit 1
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
echo "[$(date '+%F %T')] c3hrnet read start"
cd $W && nice -n 19 $P scripts/bench_read_w1.py --arm PF=$L/house_r34_unetpp_pf_v11:'c3_pf_v11_f[0-4]_s[5-9]' --arm HOUSE=$L/house_r34_unetpp_v11:'c3_house_v11_f[0-4]_s[5-9]' --arm HRNET=$L/hrnet_w18_unetpp_pf_v11:'c3h_hrnet_w18_unetpp_pf_f[0-4]_s[5-9]' --pair PF=HRNET --pair HOUSE=HRNET --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa PF:5,6:7,8 --groups $G3 --score-exclude $X --out $O/read; echo "[$(date '+%F %T')] read rc=$?"
echo "[$(date '+%F %T')] C3HRNET READ ALL DONE; tracked changes in bench_wt_final: $(git -C $W status --porcelain -uno | wc -l)"
