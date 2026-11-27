#!/bin/bash
# SKR2C opening (protocol_SKR2C v1 LOCKED 91b76abd + §9; rulings_s2c_stage2.md; E1 opening #7): THE settings block. Sourced by s2c_post.sh,
# s2c_opening.sh and post_extra/s2c_*.sh, so every script sees the same arms, runs and paths. Listed in FROZEN.md5.
# From s2_settings.sh af791321 (S2 frozen set fb5becd2); minimal diff. Defines variables and helper functions only; runs nothing.
#
# ############################## SETTINGS (both arms fresh, seeds 10-14; protocol §2) ##############################
# SKR01 = SKR2 (protocol §2)
SKR_WT=/home/noob/work/el_thin
SKR_DEP=c9bbb02
SKR_DEPLOY_FILE=/home/noob/work/el_thin/reports/thin/DEPLOY
SKR_EXP=/home/noob/work/s2c/exp_SKR01.txt
SKR_EXP_MD5=1343cca2740daba87e83a5adb0bb688a
SKR_RUNS="s2c_SKR01_100pct_s10 s2c_SKR01_100pct_s11 s2c_SKR01_100pct_s12 s2c_SKR01_100pct_s13 s2c_SKR01_100pct_s14"
SKR_LA_MD5=419486b146cddbbd48c619502b6ebcad      # el_thin scripts/rescore_logit_adjust.py (THIN's LA; 24 classes when scuff_class absent)
SKR_RESCORE_MD5=1e41202b99611169030abc5d2524f72c # el_thin scripts/rescore_label_versions.py
# SUPPF = SUP100-PF, scored fresh (protocol §3: no comparator reuse; as PF2's own opening: m0_audit + m0_audit_tau, el_f3 scripts)
SUP_WT=/home/noob/work/el_f3
SUP_DEP=e544133
SUP_DEPLOY_FILE=/home/noob/work/el_f3/REVISION   # el_f3 has no DEPLOY file; REVISION = e544133 (checked against HEAD in pass 0)
SUP_EXP=/home/noob/work/s2c/exp_SUPPF.txt
SUP_EXP_MD5=dc9c344aa418ff699b85c81e430c5e57
SUP_RUNS="s2c_SUPPF_100pct_s10 s2c_SUPPF_100pct_s11 s2c_SUPPF_100pct_s12 s2c_SUPPF_100pct_s13 s2c_SUPPF_100pct_s14"
SUP_LA_MD5=ec315d2e8c3e3015cb31a1fc3675ddd5      # el_f3 scripts/rescore_logit_adjust.py (PF2's LA)
SUP_RESCORE_MD5=1e41202b99611169030abc5d2524f72c # el_f3 scripts/rescore_label_versions.py
# ############################## END SETTINGS ##############################
#
# Fixed paths (s2c queue dir; opened reference files read unchanged, re-checked by md5sum -c in pass 0)
S2=/home/noob/work/s2c; OPEN=$S2/open; S2_OUT=$S2/post; NL=$S2/post.log; LL=$S2/launch.log; WK=$S2/post_work; PIDS=$S2/post_pids.txt
DOUT=$S2/d_out; DLOG=$S2/d.log; OCHK=$S2/open_check
P=/home/noob/work/el-fault-detection/.venv/bin/python
F1=/home/noob/work/el_f1/reports/f1; X1=$F1/ext117; S0=$F1/smoke_v1/mim_step0.pth
GATE_SH=/home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh; B5_DEVICE_FILE=/home/noob/work/el_f3/reports/pf2/post_extra/B5_DEVICE
REF_CFG=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml
CTX=/home/noob/work/el_f3/reports/d/e1_context.tsv; ENC=/home/noob/work/el_f3/reports/enc_cosine.py; TMD=/home/noob/work/el_f3/reports/d
PF=/home/noob/work/el_f3/reports/pf2/post; MAN_PF2=3827f7c08e653ae5a2164093b242b3b6
HCP=/home/noob/work/el_hc/reports/hc/post; MAN_HC=d5c39e0de9145393925389c44848533a
THP=/home/noob/work/el_thin/reports/thin/post; MAN_THIN=5d3f5b314f4dc0cc52d5a4ec3793888c
S2P=/home/noob/work/s2q/post; MAN_S2=bd671e26eddd2bd92b840e5cb0c1bd93          # #5 opening (SKR2 s5-9): reference rows + self-tests
SKE=/home/noob/work/el_f3/reports/skr2e/out; MAN_SKE=9b43e6369ddc5d19fafa477039031eec  # #6 opening (SKR2E): D identity reference
TEST_MD5=a31fad14fa27ee28e2a2319b8976aba3; VAL_MD5=9dcccf00662dfca750f0b46628f8d5bb; EXT_MD5=5266806b559f74bcf9eae167bb076b95
ROOT_SPLITS=/home/noob/work/s2c_root/SPLITS.md5; ROOT_SPLITS_MD5=24568cdb4ad0764924660e448cef6a37; LL_MD5=5d2544a7417a11671708aef46c74fdd5
CMP_RUNS="pf2_SUPPF_100pct_s5 pf2_SUPPF_100pct_s6 pf2_SUPPF_100pct_s7 pf2_SUPPF_100pct_s8 pf2_SUPPF_100pct_s9"       # #5 reference row (opened)
S2SKR_RUNS="skr2_SKR01_100pct_s5 skr2_SKR01_100pct_s6 skr2_SKR01_100pct_s7 skr2_SKR01_100pct_s8 skr2_SKR01_100pct_s9"  # #5 reference row (opened)
HC_RUNS="hc_HC_100pct_s5 hc_HC_100pct_s6 hc_HC_100pct_s7 hc_HC_100pct_s8 hc_HC_100pct_s9"            # e1_coprim self-test only (opened)
THSKR_RUNS="thin_SKR_100pct_s5 thin_SKR_100pct_s6 thin_SKR_100pct_s7 thin_SKR_100pct_s8 thin_SKR_100pct_s9"  # guards self-test only (opened)
THCLD_RUNS="thin_CLD_100pct_s5 thin_CLD_100pct_s6 thin_CLD_100pct_s7 thin_CLD_100pct_s8 thin_CLD_100pct_s9"  # guards self-test only
PROTO=protocol_SKR2C
# Every file FROZEN.md5 must list (by path relative to $OPEN)
REQ="s2c_settings.sh s2c_opening.sh s2c_post.sh s2c_e1_coprim.py s2c_guards.py s2c_realsplits.py s2c_named_boot.py s2c_ckpt_check.py
     s2_b5w_check.py s2_cellgate.py s2c_copies.md5 calib_w/el_metrics_w.py trackM/m0_analyze.py thin/thin_e1_relf1.py
     post_extra/s2c_b5w.sh post_extra/s2c_scuffign.sh post_extra/pf2_scuffign.py
     post_extra/calib/calib_dump.py post_extra/calib/el_metrics.py post_extra/calib/pf2_b5_hook.sh post_extra/calib/pf2_b5_pooled.sh
     d/s2c_d_infer.py d/s2c_d_run.sh local/s2c_d_boot.py local/s2c_post_local.sh selftest_ref/coach_s2_boot.txt"

# arm helpers: wt_of / dep_of / runs_of ARM; arm_of RUN
wt_of(){ case $1 in SKR01) echo $SKR_WT;; SUPPF) echo $SUP_WT;; *) return 1;; esac; }
dep_of(){ case $1 in SKR01) echo $SKR_DEP;; SUPPF) echo $SUP_DEP;; *) return 1;; esac; }
runs_of(){ case $1 in SKR01) echo $SKR_RUNS;; SUPPF) echo $SUP_RUNS;; *) return 1;; esac; }
arm_of(){ local r; for r in $SKR_RUNS; do [ "$r" = "$1" ] && { echo SKR01; return 0; }; done
          for r in $SUP_RUNS; do [ "$r" = "$1" ] && { echo SUPPF; return 0; }; done; return 1; }

# settings_check: prints the first problem and returns 1; returns 0 if the settings are complete and consistent
settings_check(){
  local v k r n
  for v in SUP_WT SUP_DEP SUP_DEPLOY_FILE SUP_EXP SUP_EXP_MD5 SUP_RUNS SUP_LA_MD5 SUP_RESCORE_MD5; do
    case "${!v}" in *TBD*|"") echo "settings: $v not filled ('${!v}')"; return 1;; esac; done
  echo "$SKR_DEP $SUP_DEP" | grep -qE '^[0-9a-f]{7} [0-9a-f]{7}$' || { echo "settings: deploy commits must be 7 hex chars"; return 1; }
  echo "$SKR_EXP_MD5 $SUP_EXP_MD5 $SUP_LA_MD5 $SUP_RESCORE_MD5" | grep -qE '^[0-9a-f]{32}( [0-9a-f]{32}){3}$' || { echo "settings: md5s must be 32 hex chars"; return 1; }
  for v in SKR_RUNS SUP_RUNS; do
    n=0; k=10
    for r in ${!v}; do
      echo "$r" | grep -qE "^s2c_[A-Za-z0-9]+_100pct_s$k\$" || { echo "settings: $v entry '$r' is not s2c_<arm>_100pct_s$k"; return 1; }
      n=$((n + 1)); k=$((k + 1)); done
    [ $n = 5 ] || { echo "settings: $v has $n names, need 5 (s10..s14)"; return 1; }
  done
  for r in $SUP_RUNS; do for v in $SKR_RUNS $CMP_RUNS $S2SKR_RUNS; do [ "$r" != "$v" ] || { echo "settings: $r reused"; return 1; }; done; done
  [ "$SKR_WT" != "$SUP_WT" ] || { echo "settings: the two arms share a worktree"; return 1; }
  return 0
}
