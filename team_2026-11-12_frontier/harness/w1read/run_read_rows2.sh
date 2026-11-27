#!/bin/bash
# Rows tranche 2, read on gaint CPU (lead, 16 Nov 2026; ruling in log.md 16 Nov 16:00): the read does not wait for the dump of
# r2_segformer_mitb2_pf_f4_s6 (cv02 GPU 2 is held by another user's job since 16 Nov 05:05 IST).
#   hrnet_w18_unetpp_pf seeds 5, 6; skr01_pf_v11 seeds 5, 6; segformer_mitb2_pf seed 5 ONLY (open at 2 seeds, one dump missing;
#   redo that arm with run_read_rows2.sh SEG6=1 once the dump is relayed).
# Same tools, comparators and options as run_read_rows2_prelim.sh: bench_wt_b b5bf0ae; 532-cell values and the 416 clean cells
# (benchmark/splits/score_exclude_v3.txt) in one run. cv02 dumps only (relayed, checksums equal). CPU only.
# Refuses unless every run it names is relayed. Output folder must not exist (no overwrite of an earlier read).
set -u
SEG6=${SEG6:-0}
cd /home/noob/work/bench_wt_b || exit 1
[ "$(git rev-parse --short HEAD)" = b5bf0ae ] || { echo "worktree not at b5bf0ae"; exit 1; }
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
X=/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/score_exclude_v3.txt
RD=/home/noob/work/bench_relay/rows2
if [ "$SEG6" = 1 ]; then O=/home/noob/work/bench_reads/rows2_full; SS='[56]'; WANT=30; else O=/home/noob/work/bench_reads/rows2; SS='5'; WANT=25; fi
W=/home/noob/work/bench_reads/w1c/links/elbench1; L=$O/links/elbench1
[ -e $O ] && { echo "output folder exists: $O"; exit 1; }
mkdir -p $O || exit 1
n=0
for r in $(ls $RD | grep -E "^r2_(hrnet_w18_unetpp_pf_f[0-4]_s[56]|skr01_pf_v11_f[0-4]_s[56]|segformer_mitb2_pf_f[0-4]_s$SS)\$"); do
  grep -q "relayed $r:" $RD/relay.log || { echo "not relayed: $r"; exit 1; }
  m=$(ls $RD/$r/dumps/elbench1); [ "$(echo "$m" | wc -l)" = 1 ] || { echo "method dir count != 1: $r"; exit 1; }
  mkdir -p $L/$m; ln -sfn $RD/$r/dumps/elbench1/$m/$r $L/$m/$r; n=$((n+1))
done
[ "$n" = "$WANT" ] || { echo "expected $WANT linked runs, have $n"; exit 1; }
# cache: start from a copy of the preliminary read's cache (PF, HOUSE and the 20 runs read on 16 Nov 14:00); never write into that one
cp -r /home/noob/work/bench_reads/rows2_prelim/cache_c $O/cache_c || exit 1
C="--arm PF=$W/house_r34_unetpp_pf_v11:w1c1_pf_v11_f[0-4]_s[5-9] --arm HOUSE=$W/house_r34_unetpp_v11:w1c2_house_v11_f[0-4]_s[56]"
C="$C --arm hrnet_w18_unetpp_pf=$L/hrnet_w18_unetpp_pf_v11:r2_hrnet_w18_unetpp_pf_f[0-4]_s[56]"
C="$C --arm segformer_mitb2_pf=$L/segformer_mitb2_pf_v11:r2_segformer_mitb2_pf_f[0-4]_s$SS"
C="$C --arm skr01_pf_v11=$L/skr01_pf_v11:r2_skr01_pf_v11_f[0-4]_s[56]"
echo "[$(date '+%F %T')] rows2 read start ($n rows 2 runs linked; SEG6=$SEG6; out $O)"
nice -n 19 $P scripts/bench_read_w1.py $C --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa PF:5,6:7,8 --score-exclude $X --out $O/read; echo "[$(date '+%F %T')] read rc=$?"
echo "[$(date '+%F %T')] ROWS2 READ ALL DONE; tracked changes in worktree: $(git status --porcelain -uno | wc -l)"
