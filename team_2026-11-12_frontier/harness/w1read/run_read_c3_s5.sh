#!/bin/bash
# First cv5v3 look on gaint CPU (lead, 16 Nov 2026): seed 5 only, PF against hrnet_w18_unetpp_pf. DESCRIPTIVE (1 seed; the
# confirmation is the 5-seed read). Command form = LAUNCH_REQUEST_c3base.md section 7 ("Beside it"): reviewed tree
# bench_wt_final 89b9ea5, --groups cv5v3_groups.tsv (every cv5v3 read needs it), --score-exclude v3 for the 416-cell columns.
# cv02 runs only (relayed, checksums equal). Refuses unless all 10 runs are relayed and unless the output folder is new.
set -u
cd /home/noob/work/bench_wt_final || exit 1
[ "$(git rev-parse --short HEAD)" = 89b9ea5 ] || { echo "worktree not at 89b9ea5"; exit 1; }
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
X=/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/score_exclude_v3.txt
G3=/home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv
O=/home/noob/work/bench_reads/c3_s5; L=$O/links/elbench1
[ -e $O ] && { echo "output folder exists: $O"; exit 1; }
[ -s $G3 ] && [ -s $X ] || { echo "groups or exclude list missing"; exit 1; }
mkdir -p $O || exit 1
n=0
for spec in "/home/noob/work/bench_relay/c3base:^c3_pf_v11_f[0-4]_s5\$" "/home/noob/work/bench_relay/c3hrnet:^c3h_hrnet_w18_unetpp_pf_f[0-4]_s5\$"; do
  RD=${spec%%:*}; RX=${spec#*:}
  for r in $(ls $RD | grep -E "$RX"); do
    grep -q "relayed $r:" $RD/relay.log || { echo "not relayed: $r"; exit 1; }
    m=$(ls $RD/$r/dumps/elbench1); [ "$(echo "$m" | wc -l)" = 1 ] || { echo "method dir count != 1: $r"; exit 1; }
    mkdir -p $L/$m; ln -sfn $RD/$r/dumps/elbench1/$m/$r $L/$m/$r; n=$((n+1))
  done
done
[ "$n" = 10 ] || { echo "expected 10 linked runs, have $n"; exit 1; }
C="--arm PF=$L/house_r34_unetpp_pf_v11:c3_pf_v11_f[0-4]_s5 --arm hrnet_w18_unetpp_pf=$L/hrnet_w18_unetpp_pf_v11:c3h_hrnet_w18_unetpp_pf_f[0-4]_s5"
echo "[$(date '+%F %T')] c3 seed 5 look start ($n runs linked; out $O)"
nice -n 19 $P scripts/bench_read_w1.py $C --labels v11 --workers 8 --cache $O/cache --baseline PF --groups $G3 --score-exclude $X --out $O/read; echo "[$(date '+%F %T')] read rc=$?"
echo "[$(date '+%F %T')] C3 S5 LOOK ALL DONE; tracked changes in worktree: $(git status --porcelain -uno | wc -l)"
