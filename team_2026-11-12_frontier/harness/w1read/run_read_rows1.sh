#!/bin/bash
# Rows tranche 1 read on gaint CPU (lead, 15 Nov 2026): reviewed tools at bench_wt_w2 c57508e; cv02 dumps only (relayed).
# Arms: PF (W1-C1, 5 seeds, baseline), HOUSE (W1-C2), and the five rows of tranche 1 (seeds 5, 6). A/A = PF {5,6} v {7,8}.
set -u
cd /home/noob/work/bench_wt_w2 || exit 1
[ "$(git rev-parse --short HEAD)" = c57508e ] || { echo "worktree not at c57508e"; exit 1; }
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
W=/home/noob/work/bench_reads/w1c/links/elbench1; L=/home/noob/work/bench_reads/rows1/links/elbench1; O=/home/noob/work/bench_reads/rows1
C="--arm PF=$W/house_r34_unetpp_pf_v11:w1c1_pf_v11_f[0-4]_s[5-9] --arm HOUSE=$W/house_r34_unetpp_v11:w1c2_house_v11_f[0-4]_s[56]"
for r in dlv3p_r34_pf unet_r34_pf pratt_dlv3p_wcec hanifi_vgg16_unet_pf ucf_dlv3_r50_pf; do C="$C --arm $r=$L/${r}_v11:r1_${r}_f[0-4]_s[56]"; done
C="$C --labels v11 --workers 8 --cache $O"
echo "[$(date '+%F %T')] rows1 read start"
nice -n 19 $P scripts/bench_read_w1.py $C --baseline PF --aa PF:5,6:7,8 --out $O/read; echo "[$(date '+%F %T')] read rc=$?"
echo "[$(date '+%F %T')] ROWS1 READ ALL DONE; tracked changes in worktree: $(git status --porcelain -uno | wc -l)"
