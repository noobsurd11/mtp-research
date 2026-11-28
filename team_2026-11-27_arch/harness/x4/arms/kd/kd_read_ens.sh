#!/bin/bash
# kd builder: read of the out-of-fold 5-seed COMBO ensemble (x4_ens_inference) against COMBO single models (gaint CPU,
# nice 19; run in tmux bench_x4_read_kdens). Driver: harness/x4/arms/kd/read_x4_ens.py (= read_x4.py + writer allowlist).
# Arms: COMBO = c3x swad readout seeds 5..9 (all 5 members); COMBO_D4 = the same runs with D4 TTA (queue fin);
#   ENS = mean softmax of the 5 swad members, no TTA, one record per fold (seed id 56789); ENS_D4 = the same with D4 per
#   member; PFAA = c3_pf_v11 seeds 5..8 for the margin M (A/A {5,6} v {7,8}).
# Pairs: COMBO=ENS (ensemble effect, no TTA), COMBO_D4=ENS_D4 (ensemble effect under D4), COMBO=ENS_D4 (C2-style
#   deployment vs the x4 comparator; TTA and ensemble together).
set -u
H=/home/yugma/mtp/research/team_2026-11-27_arch/harness/x4; . $H/x4_arms.sh
P=/home/noob/work/el-fault-detection/.venv/bin/python; TAG=${1:?tag}
D4_T="$RLY/fin/c3x_hrnet_swad_v11_f{k}_s{s}.swad.tta_d4/dumps/elbench1/hrnet_w18_unetpp_swad_const_pf_v11/c3x_hrnet_swad_v11_f{k}_s{s}.swad.tta_d4"
E_T(){ echo "$RLY/x4_ens/x4ens_mean_$1_f{k}_s{s}/dumps/elbench1/x4_ens_mean/x4ens_mean_$1_f{k}_s{s}"; }
exec nice -n 19 $P $H/arms/kd/read_x4_ens.py --out /home/noob/work/bench_reads/x4_$TAG --base COMBO \
  --cache /home/noob/work/bench_reads/x4_kd_cache \
  --arm "COMBO=$COMBO_T:5,6,7,8,9:swad" --arm "COMBO_D4=$D4_T:5,6,7,8,9:swad" \
  --arm "ENS=$(E_T none):56789:swad" --arm "ENS_D4=$(E_T d4):56789:swad" --arm "PFAA=$PF_T:5,6,7,8:model" \
  --pair COMBO=ENS --pair COMBO_D4=ENS_D4 --pair COMBO=ENS_D4 --aa PFAA:5,6:7,8 --verdict ENS,ENS_D4 \
  --writers "bench_infer.py afd9164264de4d91e43e258e6f8b1836" --writers "bench_infer.py 32e0b67c2ad8073c33440b8347d77f57" \
  --writers "bench_ens_infer.py 410912bd3210ae1649747df0d0ec6a9d"
