#!/bin/bash
# Rows tranche 2, PRELIMINARY read on gaint CPU (lead, 16 Nov 2026): only the arms whose five folds are relayed.
#   hrnet_w18_unetpp_pf seeds 5, 6; segformer_mitb2_pf seed 5; skr01_pf_v11 seed 5. (Missing on 16 Nov 14:00: segformer f4 s6
#   (dump waits for cv02 GPU 2), skr01 f3 s6 (training), skr01 f4 s6 (waits for a lane).) The full read replaces this one.
# Tools: bench_wt_b b5bf0ae (reviewed read tools with --score-exclude); 532-cell values and the 416 clean cells
# (benchmark/splits/score_exclude_v3.txt) in one run. cv02 dumps only (relayed, checksums equal). CPU only.
set -u
cd /home/noob/work/bench_wt_b || exit 1
[ "$(git rev-parse --short HEAD)" = b5bf0ae ] || { echo "worktree not at b5bf0ae"; exit 1; }
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
X=/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/score_exclude_v3.txt
RD=/home/noob/work/bench_relay/rows2; O=/home/noob/work/bench_reads/rows2_prelim
W=/home/noob/work/bench_reads/w1c/links/elbench1; L=$O/links/elbench1
mkdir -p $O || exit 1
# links: only runs the relay marked complete (.ok) and listed below
n=0
for r in $(ls $RD | grep -E '^r2_(hrnet_w18_unetpp_pf_f[0-4]_s[56]|segformer_mitb2_pf_f[0-4]_s5|skr01_pf_v11_f[0-4]_s5)$'); do
  grep -q "relayed $r:" $RD/relay.log || { echo "not relayed: $r"; exit 1; }
  m=$(ls $RD/$r/dumps/elbench1); [ "$(echo "$m" | wc -l)" = 1 ] || { echo "method dir count != 1: $r"; exit 1; }
  mkdir -p $L/$m; ln -sfn $RD/$r/dumps/elbench1/$m/$r $L/$m/$r; n=$((n+1))
done
[ "$n" = 20 ] || { echo "expected 20 linked runs, have $n"; exit 1; }
# cache: start from a copy of the clean416 cache (PF and HOUSE records), never write into that one
[ -e $O/cache_c ] || cp -r /home/noob/work/bench_reads/clean416/cache_c $O/cache_c
C="--arm PF=$W/house_r34_unetpp_pf_v11:w1c1_pf_v11_f[0-4]_s[5-9] --arm HOUSE=$W/house_r34_unetpp_v11:w1c2_house_v11_f[0-4]_s[56]"
C="$C --arm hrnet_w18_unetpp_pf=$L/hrnet_w18_unetpp_pf_v11:r2_hrnet_w18_unetpp_pf_f[0-4]_s[56]"
C="$C --arm segformer_mitb2_pf=$L/segformer_mitb2_pf_v11:r2_segformer_mitb2_pf_f[0-4]_s5"
C="$C --arm skr01_pf_v11=$L/skr01_pf_v11:r2_skr01_pf_v11_f[0-4]_s5"
echo "[$(date '+%F %T')] rows2 prelim read start ($n rows 2 runs linked)"
nice -n 19 $P scripts/bench_read_w1.py $C --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa PF:5,6:7,8 --score-exclude $X --out $O/read; echo "[$(date '+%F %T')] read rc=$?"
echo "[$(date '+%F %T')] ROWS2 PRELIM READ ALL DONE; tracked changes in worktree: $(git status --porcelain -uno | wc -l)"
