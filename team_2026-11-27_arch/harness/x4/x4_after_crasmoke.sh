#!/bin/bash
# x4 lead 28 Nov (user: "go ahead, build it"). Runs on gaint in tmux bench_x4_after_crasmoke. Waits until cv02 x4_w1 has
# trained smoke_x4_cidee55982_f0_s5 (GPU identity, COMBO card at ee55982, 1,000 steps) and the four 200-step memory smokes
# (cra, cra_region, cra_dir, cra_rdice). Then:
#  (1) GPU identity: train.log steps 50..1,000 (loss, loss_sup, loss_con, lambda, lr) and PF encoder lines vs
#      c3x_hrnet_swad_v11_f0_s5 (bench_03375d4). Not IDENTICAL -> REFUSED, nothing appended (lead decides).
#  (2) peaks from gpumem.log (smoke rc must be 3); full-run estimate = peak + 748, gate = estimate + 2,048.
#  (3) stage P seed 5 (PATHFINDER_RULE.md 26474b34): x4_cra and x4_cra_dir with readouts swad,swad_bridge (primary read key
#      swad_bridge, fixed here before any run; the swad read is printed beside), x4_cra_region with swad. x4_cra_rdice: smoke
#      only (optional card, not in stage P). Auto reads armed.
#  (4) re-appends the placeholder-skipped jobs: x4_lowfreeze3 (card x4_lowfreeze, 0d4e431, peak 9,386) and x4_geomaux2
#      (card x4_geomaux, 0d4e431, peak 9,224), auto reads armed.
set -u
H=$(dirname "$(readlink -f "$0")"); L=$H/evidence/after_crasmoke.log; C=ee55982bf7ab114faeea7fe53d9a8e8a0e6a237c
G=0d4e43137764752970fe28fdadd1959441f8c137; P=/home/noob/work/el-fault-detection/.venv/bin/python
SC(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 "$1"; }
say(){ echo "[$(date '+%F %T')] $*" >> $L; }
J="smoke_x4_cidee55982_f0_s5 smoke_x4_cra_f0_s5 smoke_x4_cra_region_f0_s5 smoke_x4_cra_dir_f0_s5 smoke_x4_cra_rdice_f0_s5"
say "armed (script md5 $(md5sum < $0 | cut -c1-8)): waiting for $J"
for j in $J; do
  until t=$(SC "grep 'trained $j ' /tmp/noob_el/bench_q/x4_w1/launch.log | tail -1") && [ -n "$t" ]; do sleep 120; done
  say "$t"; case "$t" in *" rc=3 "*) ;; *) say "REFUSED: $j rc is not 3; nothing appended"; exit 1;; esac
done
idr=$(SC 'cd /tmp/noob_el; ext(){ grep -oE "(step [0-9]+/20000 .*lr=[0-9.e-]+|PF encoder lr=[0-9.e-]+ at step [0-9]+)" $1 | awk "/^step/{split(\$2,a,\"/\"); if (a[1]<=1000) print; next} {if (\$NF<=1000) print}"; }
  v(){ grep ^step | grep -oE "(loss|loss_sup|loss_con|lambda|lr)=[0-9.e-]+"; }
  ext bench_03375d4/experiments/c3x_hrnet_swad_v11_f0_s5/train.log > .ir; ext bench_ee55982/experiments/smoke_x4_cidee55982_f0_s5/train.log > .ic
  nv=$(v < .ic | wc -l); nd=$(diff <(v < .ic) <(v < .ir) | grep -c "^<"); pf=$(diff <(grep ^PF .ic) <(grep ^PF .ir) >/dev/null && echo identical || echo DIFFER)
  echo "$nv values, $nd differ, PF lines $pf ($(grep -c ^PF .ic) vs $(grep -c ^PF .ir))"; rm -f .ir .ic')
say "GPU identity ee55982 vs c3x f0 s5: $idr"
case "$idr" in "100 values, 0 differ, PF lines identical (20 vs 20)") say "IDENTICAL";; *) say "REFUSED: GPU identity not IDENTICAL; nothing appended"; exit 1;; esac
pk(){ SC "grep -v '^#' /tmp/noob_el/bench_q/x4_w1/gpumem.log | tr ' ' '\n' | grep -E ':smoke_x4_$1_f0_s5\$' | cut -d: -f3 | sort -n | tail -1"; }
declare -A E
for a in cra cra_region cra_dir cra_rdice; do p=$(pk $a); case "$p" in ''|*[!0-9]*) say "REFUSED: no peak for $a"; exit 1;; esac
  E[$a]=$((p + 748)); say "$a smoke peak $p MiB (E); full-run estimate ${E[$a]} (S, + 748); gate $((p + 748 + 2048))"; done
cd $H
mk(){ $P x4_make_jobs.py --commit $1 --seeds 5 --out jobs/$2.tsv "${@:3}" >> $L 2>&1 || { say "make_jobs $2 failed"; exit 1; }
      say "$(bash x4_queue.sh append w1 jobs/$2.tsv 2>&1 | tail -1 | cut -c1-220)"; }
ar(){ tmux has-session -t "=bench_x4_auto_$1" 2>/dev/null || tmux new-session -d -s bench_x4_auto_$1 "sleep ${6:-0}; bash $H/x4_auto_read.sh $1 w1 $2 $3 $4 $5 P"; }
mk $C w1_cra_p --readouts swad,swad_bridge bench/methods/x4_cra.yaml=cra@${E[cra]}
ar cra_p CRA cra x4_cra swad_bridge; ar cra_sw_p CRASW cra x4_cra swad 1800
mk $C w1_crar_p bench/methods/x4_cra_region.yaml=cra_region@${E[cra_region]}
ar cra_region_p CRAR cra_region x4_cra_region swad
mk $C w1_crad_p --readouts swad,swad_bridge bench/methods/x4_cra_dir.yaml=cra_dir@${E[cra_dir]}
ar cra_dir_p CRAD cra_dir x4_cra_dir swad_bridge; ar cra_dir_sw_p CRADSW cra_dir x4_cra_dir swad 1800
mk $G w1_lf3_p bench/methods/x4_lowfreeze.yaml=lowfreeze3@9386; ar lowfreeze3_p LOWFREEZE lowfreeze3 x4_lowfreeze swad
mk $G w1_geo2_p bench/methods/x4_geomaux.yaml=geomaux2@9224; ar geomaux2_p GEOMAUX geomaux2 x4_geomaux swad
say "AFTER CRASMOKE DONE: cra, cra_region, cra_dir stage P, lowfreeze3, geomaux2 appended; reads armed"
