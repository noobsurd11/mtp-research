#!/bin/bash
# x4 read of one or more screening arms against COMBO (HRNet-W18 U-Net++ PF + SWAD, swad readout, seeds 5, 6; c3x runs),
# with PFAA (c3_pf_v11 seeds 5 to 8) only for the margin M (PF A/A {5,6} v {7,8}, PROTOCOL v1.0 s5.4). gaint CPU, nice 19.
# Usage: bash x4_read.sh <tag> <ARM>=<QN>:<SHORT>:<METHOD>:<KEY> [...]
#   KEY = the readout read for the arm: 'swad' / 'swad_bridge' read the <run>.swad / <run>.swad_bridge dump, any other key
#   the run's own dump.
#   Stage P (PATHFINDER_RULE.md): SEEDS=5 STAGE=P (COMBO seeds follow SEEDS unless CSEEDS is set).
#   Out: /home/noob/work/bench_reads/x4_<tag> (refuses if it exists); verdict.txt there. Seeds: SEEDS (default 5,6).
set -u
H=$(dirname "$(readlink -f "$0")"); . $H/x4_arms.sh
P=/home/noob/work/el-fault-detection/.venv/bin/python; SEEDS=${SEEDS:-5,6}; CSEEDS=${CSEEDS:-$SEEDS}; STAGE=${STAGE:-}; FOLDS=${FOLDS:-0,1,2,3,4}; HEADER=${HEADER:-}
TAG=${1:?tag}; shift; [ $# -ge 1 ] || { sed -n 2,7p "$0"; exit 1; }
AR=(); PR=(); VS=""
for spec in "$@"; do n=${spec%%=*}; IFS=: read -r qn sh me key <<< "${spec#*=}"
  case "$key" in swad|swad_bridge) suf=.$key;; *) suf="";; esac
  AR+=(--arm "$n=$(X4_T $qn $sh $me $suf):$SEEDS:$key"); PR+=(--pair "COMBO=$n"); VS="$VS${VS:+,}$n"; done
tmux_note="run me inside tmux (bench_x4_read_<tag>)"
exec $P $H/read_x4.py --out /home/noob/work/bench_reads/x4_$TAG --base COMBO --cache /home/noob/work/bench_reads/x4_cache \
  --arm "COMBO=$COMBO_T:$CSEEDS:swad" "${AR[@]}" --arm "PFAA=$PF_T:5,6,7,8:model" "${PR[@]}" --aa PFAA:5,6:7,8 --verdict "$VS" ${STAGE:+--stage $STAGE} --folds $FOLDS ${HEADER:+--header "$HEADER"}
