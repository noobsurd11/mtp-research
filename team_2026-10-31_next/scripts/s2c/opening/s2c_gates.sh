#!/bin/bash
# SKR2C pre-opening gates (protocol_SKR2C §6 stage 2; build_s2c_stage2.md §5; rulings_s2c_stage2.md 5). New file. CPU only (CUDA hidden,
# nice 19, <= 8 threads); computes NO SKR2C test or E1 number: on the fresh runs it reads only config_used.yaml, 'grep -c' of fixed
# patterns in the stdouts / launch.log, latest.pth md5s and (gate B) each checkpoint's step and key count.
# Usage: bash s2c_gates.sh OUTDIR   (OUTDIR under /home/noob/work/s2c/open_check; refused if it exists). Run in tmux s2c_gates.
#   A  integrity = s2c_post.sh passes 0-2 (statements repeated from it, outputs to OUTDIR/pass0 instead of post/): settings, worktrees,
#      FROZEN.md5 + s2c_copies.md5, 5 reference MANIFESTs, external scorer / data md5s, launch.log conditions, no HOLD, real splits (pre),
#      'step 20000/20000' grep -c == 1 per stdout, config diff vs pf2_SUPPF_100pct_s5 == exp file, seed K
#   B  checkpoint asserts: s2c_ckpt_check.py on the 10 fresh runs (step == 20000, key count / key set / shapes == pf2_SUPPF_100pct_s5)
#   C  R self-tests on the opened s5-9 files, same arguments as s2c_post.sh: e1_coprim, guards, named boot
#   C2 s2c_realsplits.py, every mode, on the opened #5 (s2q/post, s2q/post_work) and #6 (SKR2E out) outputs
#   D  D val-only identity on the opened s5-9 members vs #6 (ruling 5): d/s2c_d_run.sh idcheck, then s2c_realsplits.py d --val-only
#   E  FROZEN.md5 md5sum -c again at the end
# One line per gate in OUTDIR/gates_rc.txt; last line 'GATES PASS' or 'GATES FAIL (<n>)'; exit 0 iff all passed.
set -u
. /home/noob/work/s2c/open/s2c_settings.sh || exit 2
H=$OPEN; G=${1:?OUTDIR}
case "$G" in $OCHK/*) ;; *) echo "refused: OUTDIR must be under $OCHK"; exit 2;; esac
[ ! -e $G ] || { echo "refused: $G exists"; exit 2; }
mkdir -p $G/pass0
CPU=(env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 nice -n 19)
ARMS="SKR01 SUPPF"
declare -A WT=([SKR01]=$SKR_WT [SUPPF]=$SUP_WT) DEP=([SKR01]=$SKR_DEP [SUPPF]=$SUP_DEP) DEPF=([SKR01]=$SKR_DEPLOY_FILE [SUPPF]=$SUP_DEPLOY_FILE)
declare -A EXP=([SKR01]=$SKR_EXP [SUPPF]=$SUP_EXP) EXPM=([SKR01]=$SKR_EXP_MD5 [SUPPF]=$SUP_EXP_MD5) RUNS=([SKR01]="$SKR_RUNS" [SUPPF]="$SUP_RUNS")
F=0
gate(){ local lab=$1 rc; shift; "$@"; rc=$?; echo "$(date '+%F %T') GATE $lab rc=$rc" >> $G/gates_rc.txt; [ $rc = 0 ] || F=$((F + 1)); }
echo "$(date '+%F %T') s2c gates start pid $$ (FROZEN.md5 $(md5sum < $H/FROZEN.md5 | cut -c1-32))" > $G/gates_rc.txt

gateA(){ (
  OUT=$G/pass0
  fail(){ echo "[$(date)] FAIL: $*"; exit 1; }
  frozen_ok(){ local f; [ -s $H/FROZEN.md5 ] || { echo "no $H/FROZEN.md5"; return 1; }
    for f in $REQ; do grep -qE "^[0-9a-f]{32}  (\./)?$f\$" $H/FROZEN.md5 || { echo "FROZEN.md5 does not list $f"; return 1; }; done
    (cd $H && md5sum -c --quiet FROZEN.md5) || { echo "FROZEN.md5 check failed"; return 1; }
    (cd $H && md5sum -c --quiet s2c_copies.md5) || { echo "s2c_copies.md5 check failed"; return 1; }; }
  man_ok(){ local d=$1 m=$2; [ "$(md5sum < $d/MANIFEST.md5 | cut -c1-32)" = $m ] || { echo "$d/MANIFEST.md5 md5 != $m"; return 1; }
    (cd $d && md5sum -c --quiet MANIFEST.md5) || { echo "$d: md5sum -c MANIFEST.md5 failed"; return 1; }; }
  m=$(settings_check) || fail "$m"
  for a in $ARMS; do
    w=${WT[$a]}; d=${DEP[$a]}
    [ "$(git -C $w rev-parse --short=7 HEAD)" = $d ] || fail "$a: $w HEAD != $d"
    [ "$(cat ${DEPF[$a]})" = $d ] || fail "$a: ${DEPF[$a]} != $d"
    [ "$(cat $w/REVISION 2>/dev/null)" = $d ] || fail "$a: $w/REVISION != $d"
    [ -z "$(git -C $w status --short --untracked-files=no)" ] || fail "$a: tracked changes in $w"
    for l in data/escdd_masks data/labeled/masks_escdd data/labeled/images; do
      [ "$(readlink -f $w/$l)" = "$(readlink -f /home/noob/work/el_f3/$l)" ] || fail "$a: $w/$l and el_f3's resolve to different targets"
    done
    echo "$a: $w HEAD = ${DEPF[$a]} = REVISION = $d; 0 tracked changes; data links = el_f3's"
  done
  frozen_ok || fail "frozen scorer files"; echo "FROZEN.md5 lists every REQ file; md5sum -c FROZEN.md5 and s2c_copies.md5 OK"
  man_ok $PF $MAN_PF2 || fail "PF2"; man_ok $HCP $MAN_HC || fail "HC"; man_ok $THP $MAN_THIN || fail "THIN"
  man_ok $S2P $MAN_S2 || fail "S2"; man_ok $SKE $MAN_SKE || fail "SKR2E"
  echo "reference MANIFESTs unchanged: PF2 $MAN_PF2, HC $MAN_HC, THIN $MAN_THIN, S2 $MAN_S2, SKR2E $MAN_SKE (md5sum -c)"
  printf '%s\n' \
    "d36f7438d0fefb0ffc926c69f6c6af2d  $F1/m0_audit.py" \
    "d77241bbe2845cabc2779adc827eb838  $F1/m0_audit_tau.py" \
    "7aa7d6d807b9eccb87360a5b9eb8eb81  $SKR_WT/scripts/b3/m0_audit_b3.py" \
    "$SKR_RESCORE_MD5  $SKR_WT/scripts/rescore_label_versions.py" \
    "$SKR_LA_MD5  $SKR_WT/scripts/rescore_logit_adjust.py" \
    "$SUP_RESCORE_MD5  $SUP_WT/scripts/rescore_label_versions.py" \
    "$SUP_LA_MD5  $SUP_WT/scripts/rescore_logit_adjust.py" \
    "d3bc7a708d3630de7322fc6dd2ff403e  $ENC" \
    "178b872d35d15689f6ab38bf57789327  $S0" \
    "00fabfddaf7d7dfd11e25008f94f744d  $GATE_SH" \
    "4e7ff5667feec6c8ca239343833c224b  $B5_DEVICE_FILE" \
    "12bd138523fccfc6be5b41df35d19147  $CTX" \
    "$EXT_MD5  $X1/stems_eval.txt" \
    "$VAL_MD5  /home/noob/work/el_f3/data/splits/val.txt" \
    "$TEST_MD5  /home/noob/work/el_f3/data/splits/test.txt" \
    "$VAL_MD5  $SKR_WT/data/splits/val.txt" \
    "$TEST_MD5  $SKR_WT/data/splits/test.txt" \
    "$SKR_EXP_MD5  $SKR_EXP" \
    "$SUP_EXP_MD5  $SUP_EXP" \
    "$ROOT_SPLITS_MD5  $ROOT_SPLITS" \
    "$LL_MD5  $LL" \
    "6aba106ae295950d99baff75cfaa407b  $REF_CFG" > $OUT/scorer_md5_expected.txt
  md5sum -c $OUT/scorer_md5_expected.txt > $OUT/scorer_md5.txt 2>&1 || fail "external scorer / data md5 (scorer_md5.txt)"
  echo "external scorer / data md5s: $(grep -c ': OK$' $OUT/scorer_md5.txt) OK of $(wc -l < $OUT/scorer_md5_expected.txt)"
  for a in $ARMS; do for r in ${RUNS[$a]}; do
    [ "$(grep -c "] config OK $r vs pf2_SUPPF_100pct_s5: " $LL)" = 1 ] || fail "launch.log: 'config OK $r' not exactly once"
    [ "$(grep -c "] trained $r rc=0\$" $LL)" = 1 ] || fail "launch.log: 'trained $r rc=0' not exactly once"
  done; done
  [ "$(grep -c '] S2C ALL TRAINED (10 rc 0 of 10; ' $LL)" = 1 ] || fail "launch.log: no 'S2C ALL TRAINED (10 rc 0 of 10' line"
  [ ! -e $S2/HOLD ] || fail "s2c/HOLD exists"
  echo "launch.log $LL_MD5: 10 x 'config OK', 10 x 'trained <run> rc=0', 'S2C ALL TRAINED (10 rc 0 of 10', no s2c/HOLD"
  "${CPU[@]}" $P $H/s2c_realsplits.py pre --wt $SUP_WT --wt $SKR_WT --ext $X1 --root-splits $ROOT_SPLITS $ROOT_SPLITS_MD5 > $OUT/realsplits_pre.txt 2>&1 \
    || fail "real splits (pre)"; echo "real splits (pre): $(tail -n 1 $OUT/realsplits_pre.txt)"
  for a in $ARMS; do for r in ${RUNS[$a]}; do
    [ "$(grep -c "step 20000/20000" ${WT[$a]}/experiments/$r.stdout)" = 1 ] || fail "INCOMPLETE $r ('step 20000/20000' count != 1)"; done; done
  echo "pass 1: 'step 20000/20000' grep -c == 1 in each of the 10 stdouts"
  for a in $ARMS; do for r in ${RUNS[$a]}; do
    c=${WT[$a]}/experiments/$r/config_used.yaml; k=${r##*_s}
    d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' $REF_CFG) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
    [ "$d" = "$(sort ${EXP[$a]})" ] || fail "config of $r: diff vs pf2_SUPPF_100pct_s5 != $(basename ${EXP[$a]})"
    grep -qx "seed: $k" $c || fail "config of $r: seed != $k"
    echo "$r ($a): config diff vs pf2_SUPPF_100pct_s5 = $(basename ${EXP[$a]}) (${EXPM[$a]:0:8}), seed $k; $(md5sum < ${WT[$a]}/experiments/$r/checkpoints/latest.pth | cut -c1-32) latest.pth"
  done; done > $OUT/init_check.txt
  echo "pass 2: config diff == exp file and seed K for all 10 (init_check.txt)"
  echo "GATE A PASS"
) > $G/A_integrity.txt 2>&1; }

gateB(){ "${CPU[@]}" $P $H/s2c_ckpt_check.py --ref /home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5 \
  $(for a in $ARMS; do for r in ${RUNS[$a]}; do echo ${WT[$a]}/experiments/$r; done; done) > $G/B_ckpt_check.txt 2>&1; }

gateC(){ local rc=0
  "${CPU[@]}" $P $H/s2c_e1_coprim.py --selftest --pf2-m0 $PF/m0 --hc-m0 $HCP/m0 --hc-json $HCP/e1_coprim.json --trackm $H/trackM \
    --thin $H/thin/thin_e1_relf1.py > $G/C_e1_coprim_selftest.txt 2>&1 || rc=1
  "${CPU[@]}" $P $H/s2c_guards.py --selftest --trackm $H/trackM --pf2-m0 $PF/m0 --hc-m0 $HCP/m0 --thin-m0 $THP/m0 > $G/C_guards_selftest.txt 2>&1 || rc=1
  "${CPU[@]}" $P $H/s2c_named_boot.py --selftest --base SUPPF $PF/m0 $CMP_RUNS --arm SKR01 $S2P/m0/SKR01 $S2SKR_RUNS \
    --ref-txt $H/selftest_ref/coach_s2_boot.txt > $G/C_named_boot_selftest.txt 2>&1 || rc=1
  return $rc; }

gateC2(){ local rc=0 W2=/home/noob/work/s2q/post_work  # every s2c_realsplits.py mode on the OPENED #5 / #6 outputs (same call forms as s2c_post.sh)
  { "${CPU[@]}" $P $H/s2c_realsplits.py m0 --wt $SKR_WT --ext $X1 $S2P/m0/SKR01 $S2SKR_RUNS || rc=1
    "${CPU[@]}" $P $H/s2c_realsplits.py rescore --wt $SKR_WT $S2P/rescore/SKR01 $S2SKR_RUNS || rc=1
    "${CPU[@]}" $P $H/s2c_realsplits.py la --wt $SKR_WT $S2P/la_SKR01.json $S2SKR_RUNS || rc=1
    "${CPU[@]}" $P $H/s2c_realsplits.py b5 --wt $SKR_WT --ext $X1 $W2/b5/SKR01/dump $W2/b5/SKR01/rec_w $S2SKR_RUNS || rc=1
    "${CPU[@]}" $P $H/s2c_realsplits.py scuffign --wt $SKR_WT --ext $X1 $S2P/m0_scuffign/SKR01 $S2SKR_RUNS || rc=1
    "${CPU[@]}" $P $H/s2c_realsplits.py d --wt /home/noob/work/el_f3 --ext $X1 $SKE || rc=1; } > $G/C2_realsplits_opened.txt 2>&1
  return $rc; }

gateD(){ local rc=0
  bash $H/d/s2c_d_run.sh idcheck || rc=1
  "${CPU[@]}" $P $H/s2c_realsplits.py d --val-only --wt /home/noob/work/el_f3 --ext $X1 $OCHK/d_val_identity > $G/D_realsplits_valonly.txt 2>&1 || rc=1
  grep -qx "IDENTITY PASS" $OCHK/d_val_identity/s2c_d_identity.txt 2>/dev/null || rc=1
  cp -p $OCHK/d_val_identity/s2c_d_identity.txt $OCHK/d_val_identity/s2c_d_gate.txt $G/ 2>/dev/null
  return $rc; }

gateE(){ (cd $H && md5sum -c --quiet FROZEN.md5) > $G/E_frozen_recheck.txt 2>&1; }

gate A_integrity gateA
gate B_ckpt_check gateB
gate C_R_selftests gateC
gate C2_realsplits_opened gateC2
gate D_val_identity gateD
gate E_frozen_recheck gateE
echo "$(date '+%F %T') $([ $F = 0 ] && echo 'GATES PASS' || echo "GATES FAIL ($F)")" >> $G/gates_rc.txt
exit $([ $F = 0 ] && echo 0 || echo 1)
