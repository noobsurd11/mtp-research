#!/bin/bash
# Clean-cell re-read (lead, 16 Nov 2026): PF, HOUSE, PFV1 and the tranche 1 rows on the 416 clean cells of cv5v2
# (benchmark/splits/score_exclude_v3.txt: 116 cells excluded), 532-cell values beside. Tools: bench_wt_b b5bf0ae (reviewed
# read tools with --score-exclude; no queue uses this tree; reads write nothing into it). CPU only.
set -u
cd /home/noob/work/bench_wt_b || exit 1
[ "$(git rev-parse --short HEAD)" = b5bf0ae ] || { echo "worktree not at b5bf0ae"; exit 1; }
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
X=/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/score_exclude_v3.txt
O=/home/noob/work/bench_reads/clean416
W=/home/noob/work/bench_reads/w1c/links/elbench1; L=/home/noob/work/bench_reads/rows1/links/elbench1
echo "[$(date '+%F %T')] gaint PF 4 seeds"
nice -n 19 $P scripts/bench_read_w1.py --arm PF=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11:'w1g_pf_v11_f[0-4]_s[5-8]' --labels v11 --workers 8 --cache $O/cache_g --baseline PF --aa PF:5,6:7,8 --score-exclude $X --out $O/w1g4; echo "[$(date '+%F %T')] gaint rc=$?"
C="--arm PF=$W/house_r34_unetpp_pf_v11:w1c1_pf_v11_f[0-4]_s[5-9] --arm HOUSE=$W/house_r34_unetpp_v11:w1c2_house_v11_f[0-4]_s[56] --arm PFV1=$W/house_r34_unetpp_pf:w1c3_pf_v1_f[0-4]_s[56]"
for r in dlv3p_r34_pf unet_r34_pf pratt_dlv3p_wcec hanifi_vgg16_unet_pf ucf_dlv3_r50_pf; do C="$C --arm $r=$L/${r}_v11:r1_${r}_f[0-4]_s[56]"; done
echo "[$(date '+%F %T')] cv02 arms"
nice -n 19 $P scripts/bench_read_w1.py $C --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa PF:5,6:7,8 --score-exclude $X --out $O/cv02; echo "[$(date '+%F %T')] cv02 rc=$?"
echo "[$(date '+%F %T')] CLEAN416 READ ALL DONE; tracked changes in worktree: $(git status --porcelain -uno | wc -l)"
