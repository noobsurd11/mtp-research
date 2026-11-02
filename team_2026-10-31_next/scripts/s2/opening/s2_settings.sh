#!/bin/bash
# SKR2 + HC2 opening (protocol_SKR2_HC2 v1.0.1, 0cf1344b; HC2 under v1.1): THE settings block. Sourced by s2_postwatch.sh, s2_post.sh,
# s2_shv1.sh and post_extra/s2_*.sh, so every script sees the same arms, runs and paths. Listed in coach's FROZEN.md5.
# DRAFT (runner's helper, 2 Nov 2026) for runner's review and coach's FREEZE. Defines variables and two functions only; runs nothing.
#
# ############################## SETTINGS: FILL THE HC2 PLACEHOLDERS BEFORE COACH FREEZES ##############################
# SKR01 = SKR2 (fixed; protocol §2 v1)
SKR_WT=/home/noob/work/el_thin
SKR_DEP=c9bbb02
SKR_DEPLOY_FILE=/home/noob/work/el_thin/reports/thin/DEPLOY
SKR_EXP=/home/noob/work/s2q/exp_SKR01.txt
SKR_EXP_MD5=3fa67569be40c0da4ab48fa538378416
SKR_RUNS="skr2_SKR01_100pct_s5 skr2_SKR01_100pct_s6 skr2_SKR01_100pct_s7 skr2_SKR01_100pct_s8 skr2_SKR01_100pct_s9"
SKR_LA_MD5=419486b146cddbbd48c619502b6ebcad      # el_thin scripts/rescore_logit_adjust.py (THIN's LA; 24 classes when scuff_class absent)
SKR_RESCORE_MD5=1e41202b99611169030abc5d2524f72c # el_thin scripts/rescore_label_versions.py
# HC2 (PLACEHOLDERS: builder's new deploy, recorded in protocol v1.1). Any 'TBD' left -> every s2 script refuses.
HC2_WT=TBD             # expected /home/noob/work/el_hc2 (builder, log 2 Nov 11:30: worktree on branch hc2 from c2e6973)
HC2_DEP=TBD            # 7-char commit = HEAD of HC2_WT at v1.1
HC2_DEPLOY_FILE=TBD    # file holding "<HC2_DEP>\n" (as el_hc/reports/hc/DEPLOY)
HC2_EXP=TBD            # expected /home/noob/work/s2q/exp_HC2.txt, regenerated for the v1.1 variant (450c0c7c is VOID)
HC2_EXP_MD5=TBD        # its full md5
HC2_RUNS="TBD"         # 5 names, seeds 5..9 in this order; expected hc2_HCni_100pct_s5 .. hc2_HCni_100pct_s9 (protocol §2)
HC2_LA_MD5=ec315d2e8c3e3015cb31a1fc3675ddd5      # expected = c2e6973's (= el_f3's); confirm at v1.1 (builder may not touch scripts/)
HC2_RESCORE_MD5=1e41202b99611169030abc5d2524f72c # expected = c2e6973's; confirm at v1.1
# ############################## END SETTINGS ##############################
#
# Fixed paths (s2q queue dir; comparator and reference files reused unchanged, re-checked by md5sum -c in pass 0)
S2=/home/noob/work/s2q; OPEN=$S2/open; S2_OUT=$S2/post; NL=$S2/post.log; LL=$S2/launch.log; WK=$S2/post_work; PIDS=$S2/post_pids.txt
P=/home/noob/work/el-fault-detection/.venv/bin/python
F1=/home/noob/work/el_f1/reports/f1; X1=$F1/ext117; S0=$F1/smoke_v1/mim_step0.pth
GATE_SH=/home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh; B5_DEVICE_FILE=/home/noob/work/el_f3/reports/pf2/post_extra/B5_DEVICE
REF_CFG=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml
CTX=/home/noob/work/el_f3/reports/d/e1_context.tsv; ENC=/home/noob/work/el_f3/reports/enc_cosine.py
PF=/home/noob/work/el_f3/reports/pf2/post; PF2B5=/home/noob/work/el_f3/reports/pf2/b5_work; MAN_PF2=3827f7c08e653ae5a2164093b242b3b6
HCP=/home/noob/work/el_hc/reports/hc/post; HCSYN=/home/noob/work/el_hc/reports/hc/syn_work; MAN_HC=d5c39e0de9145393925389c44848533a
THP=/home/noob/work/el_thin/reports/thin/post; MAN_THIN=5d3f5b314f4dc0cc52d5a4ec3793888c
CMP_RUNS="pf2_SUPPF_100pct_s5 pf2_SUPPF_100pct_s6 pf2_SUPPF_100pct_s7 pf2_SUPPF_100pct_s8 pf2_SUPPF_100pct_s9"
HC_RUNS="hc_HC_100pct_s5 hc_HC_100pct_s6 hc_HC_100pct_s7 hc_HC_100pct_s8 hc_HC_100pct_s9"            # reference row (opened)
THSKR_RUNS="thin_SKR_100pct_s5 thin_SKR_100pct_s6 thin_SKR_100pct_s7 thin_SKR_100pct_s8 thin_SKR_100pct_s9"  # reference row (opened)
THCLD_RUNS="thin_CLD_100pct_s5 thin_CLD_100pct_s6 thin_CLD_100pct_s7 thin_CLD_100pct_s8 thin_CLD_100pct_s9"  # guards self-test only
PROTO=protocol_SKR2_HC2
# Every file coach's FROZEN.md5 must list (by path relative to $OPEN)
REQ="s2_settings.sh s2_postwatch.sh s2_post.sh s2_e1_coprim.py s2_guards.py s2_shv1.sh s2_shv1_read.py s2_f51.py s2_b5w_check.py
     s2_cellgate.py s2_copies.md5 calib_w/el_metrics_w.py calib_syn/calib_dump.py calib_syn/el_metrics.py found/a8_screen_score.py
     trackM/m0_analyze.py thin/thin_e1_relf1.py post_extra/s2_b5w.sh post_extra/s2_scuffign.sh post_extra/pf2_scuffign.py
     post_extra/calib/calib_dump.py post_extra/calib/el_metrics.py post_extra/calib/pf2_b5_hook.sh post_extra/calib/pf2_b5_pooled.sh"

# arm helpers: wt_of / dep_of / runs_of ARM; arm_of RUN
wt_of(){ case $1 in SKR01) echo $SKR_WT;; HC2) echo $HC2_WT;; SUPPF) echo /home/noob/work/el_f3;; *) return 1;; esac; }
dep_of(){ case $1 in SKR01) echo $SKR_DEP;; HC2) echo $HC2_DEP;; SUPPF) echo e544133;; *) return 1;; esac; }
runs_of(){ case $1 in SKR01) echo $SKR_RUNS;; HC2) echo $HC2_RUNS;; SUPPF) echo $CMP_RUNS;; *) return 1;; esac; }
arm_of(){ local r; for r in $SKR_RUNS; do [ "$r" = "$1" ] && { echo SKR01; return 0; }; done
          for r in $HC2_RUNS; do [ "$r" = "$1" ] && { echo HC2; return 0; }; done
          for r in $CMP_RUNS; do [ "$r" = "$1" ] && { echo SUPPF; return 0; }; done; return 1; }

# settings_check: prints the first problem and returns 1; returns 0 if the settings are complete and consistent
settings_check(){
  local v k r n
  for v in HC2_WT HC2_DEP HC2_DEPLOY_FILE HC2_EXP HC2_EXP_MD5 HC2_RUNS HC2_LA_MD5 HC2_RESCORE_MD5; do
    case "${!v}" in *TBD*|"") echo "settings: $v not filled ('${!v}')"; return 1;; esac; done
  echo "$SKR_DEP $HC2_DEP" | grep -qE '^[0-9a-f]{7} [0-9a-f]{7}$' || { echo "settings: deploy commits must be 7 hex chars"; return 1; }
  echo "$SKR_EXP_MD5 $HC2_EXP_MD5 $HC2_LA_MD5 $HC2_RESCORE_MD5" | grep -qE '^[0-9a-f]{32}( [0-9a-f]{32}){3}$' || { echo "settings: md5s must be 32 hex chars"; return 1; }
  for v in SKR_RUNS HC2_RUNS; do
    n=0; k=5
    for r in ${!v}; do
      echo "$r" | grep -qE "^[A-Za-z0-9]+_[A-Za-z0-9]+_100pct_s$k\$" || { echo "settings: $v entry '$r' is not <x>_<y>_100pct_s$k"; return 1; }
      n=$((n + 1)); k=$((k + 1)); done
    [ $n = 5 ] || { echo "settings: $v has $n names, need 5 (s5..s9)"; return 1; }
  done
  for r in $HC2_RUNS; do for v in $SKR_RUNS $CMP_RUNS $HC_RUNS; do [ "$r" != "$v" ] || { echo "settings: $r reused"; return 1; }; done; done
  [ "$SKR_WT" != "$HC2_WT" ] || { echo "settings: the two arms share a worktree"; return 1; }
  return 0
}
