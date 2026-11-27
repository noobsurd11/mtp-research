#!/bin/bash
# Pre-registered leakage read (harness/LAUNCH_REQUEST_c3base.md section 7, written 16 Nov before any cv5v3 run existed).
# Commands copied from that section; run by the lead on 17 Nov on gaint CPU. PF: 5 common seeds; HOUSE: seeds 5, 6.
set -u
W=/home/noob/work/bench_wt_final; P=/home/noob/work/el-fault-detection/.venv/bin/python
[ "$(git -C $W rev-parse --short HEAD)" = 89b9ea5 ] && [ "$(git -C $W status --porcelain -uno | wc -l)" = 0 ] || { echo "bench_wt_final not clean at 89b9ea5"; exit 1; }
L=/home/noob/work/bench_reads/c3base/links/elbench1; mkdir -p $L/house_r34_unetpp_pf_v11 $L/house_r34_unetpp_v11
for d in /home/noob/work/bench_relay/c3base/c3_*; do n=${d##*/}; for m in house_r34_unetpp_pf_v11 house_r34_unetpp_v11; do [ -d $d/dumps/elbench1/$m/$n ] && [ ! -e $L/$m/$n ] && ln -s $d/dumps/elbench1/$m/$n $L/$m/$n; done; done
echo "links: PF $(ls $L/house_r34_unetpp_pf_v11 | grep -c '^c3_pf_v11_f[0-4]_s[5-9]$'), HOUSE s5-6 $(ls $L/house_r34_unetpp_v11 | grep -c '^c3_house_v11_f[0-4]_s[56]$')"
G3=/home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv; C=/home/noob/work/bench_reads/w1c/links/elbench1
export OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
echo "[$(date '+%F %T')] leak PF start"
cd $W && CUDA_VISIBLE_DEVICES= nice -n 19 $P scripts/bench_leak_did.py --v3 PF=$L/house_r34_unetpp_pf_v11:'c3_pf_v11_f[0-4]_s[5-9]' --v2 PF=$C/house_r34_unetpp_pf_v11:'w1c1_pf_v11_f[0-4]_s[5-9]' --groups $G3 --out /home/noob/work/bench_reads/c3base/leak_pf --workers 8; echo "[$(date '+%F %T')] leak PF rc=$?"
cd $W && CUDA_VISIBLE_DEVICES= nice -n 19 $P scripts/bench_leak_did.py --v3 HOUSE=$L/house_r34_unetpp_v11:'c3_house_v11_f[0-4]_s[56]' --v2 HOUSE=$C/house_r34_unetpp_v11:'w1c2_house_v11_f[0-4]_s[56]' --groups $G3 --out /home/noob/work/bench_reads/c3base/leak_house --workers 8; echo "[$(date '+%F %T')] leak HOUSE rc=$?"
echo "[$(date '+%F %T')] LEAK READ ALL DONE; tracked changes in bench_wt_final: $(git -C $W status --porcelain -uno | wc -l)"
