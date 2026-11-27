#!/bin/bash
# SKR2C scoring on gaint, verdict R of the ONE pre-registered opening of protocol_SKR2C (v1 LOCKED 91b76abd + §9; §3a, §4, §6; rulings
# rulings_s2c_stage2.md); E1 opening #7 (same 50 test and 106 E1 cells as #5 / #6, 3rd look). From s2_post.sh 039c1dc6 (S2 frozen set
# fb5becd2), minimal diff (build_s2c_stage2.md §5): structure kept (prun / dpass / spass, gate per GPU process, PIDs, core passes abort,
# decision / reported rc files, one end line); changed: arms SKR01 + SUPPF, BOTH scored fresh from their own worktrees (no comparator
# reuse); HC2 parts removed (pass 1b, SHV1 pass 11, F51 pass 12, G3; ruling 2); launch.log conditions and the real-splits assert
# (s2c_realsplits.py) added to pass 0 and after every scoring pass; pass 14 = named-claim seed-aware bootstrap (s2c_named_boot.py); no
# gpumem FAST touch (no s2c logger runs now). Lives in /home/noob/work/s2c/open/. Started ONLY by s2c_opening.sh (team-lead, ruling 4).
# Usage: GS=<MiB, >= 9900> bash s2c_post.sh
# Out: /home/noob/work/s2c/post/ (per-arm subdirs SKR01 / SUPPF where a tool writes per run). Work dirs (B5 dumps) in
# /home/noob/work/s2c/post_work/ (outside post/). Opened reference files (#5 PF2 / S2 m0, HC / THIN self-test inputs, #6 SKR2E out) are
# read unchanged, re-checked by md5sum -c of their MANIFESTs in pass 0.
# GPU passes: one shared-gate wait per GPU process (gpu_gate.sh: flock, free >= GS, >= 120 s since any start, HOLD). CPU passes: CUDA
# hidden, nice 19, <= 8 threads.
# Passes (label = S2's number; run in the order listed):
#   0  integrity (each check its own statement, '|| fail'): per arm HEAD = DEPLOY file = REVISION = deploy, 0 tracked changes, data links
#      = el_f3's; settings complete; FROZEN.md5 lists every REQ file + md5sum -c; s2c_copies.md5; MANIFESTs PF2 / HC / THIN / S2 / SKR2E
#      (md5 + -c); external scorer / data md5s (scorer_md5.txt); launch.log (md5 5d2544a7; per run 'config OK' and 'trained <run> rc=0'
#      once; 'S2C ALL TRAINED (10 rc 0 of 10'; no s2c/HOLD); training root SPLITS.md5 24568cdb; real splits (s2c_realsplits.py pre)
#   1  completeness: grep -q "step 20000/20000" on each of the 10 stdouts. Nothing else of a stdout is read
#   2  config record from config_used.yaml: diff vs pf2_SUPPF_100pct_s5 == the arm's exp file, seed K; latest.pth md5s
#   3  rescore_label_versions per run, from the arm's worktree; then real-splits (n 50 / 54)                [GPU, gate per run: 10]
#   4  m0 per-cell files, default + tau 0 / 1, val / test / ext117, --code per arm; then real-splits (cell stems)  [GPU, 3 gates per arm: 6]
#      SKR01: el_thin's scripts/b3/m0_audit_b3.py 7aa7d6d8 (as S2); SUPPF: m0_audit d36f7438 + m0_audit_tau d77241bb (as PF2's opening)
#   5  tau0 check per arm: tau0 cells == default, step 20000, code_revision = the arm's deploy, 54 / 50 / 106 cells   [CPU]
#   6  LA tau 0 / 1 per arm (the arm's rescore_logit_adjust), test + val, --check vs the rescore JSONs; then real-splits   [GPU, gate per arm: 2]
#   7  E1 co-primaries: s2c_e1_coprim.py --selftest, then the scorer (refs = #5 rows)                  [CPU; decision]
#   9  20k encoder cosines vs ImageNet R34, 10 runs (enc_cosine d3bc7a70)                             [CPU; reported]
#  10a B5 wide grid: post_extra/s2c_b5w.sh (frozen calib hook + el_metrics_w, both arms); then real-splits (dumps + records)
#                                                                         [GPU, gate per run inside the hook: 10; decision (co-primary)]
#  10b SKR + cell gate line: s2_cellgate.py on the B5 records                                          [CPU; reported]
#  10c scuff-ignored test: post_extra/s2c_scuffign.sh (pf2_scuffign.py, --code per arm); then real-splits  [GPU, gate per arm inside: 2; reported]
#   8  guards G1 / G2: s2c_guards.py --selftest, then the guards (G2 E1 bar = 1.5 x fresh SUPPF mean, ruling 1)   [CPU; decision]
#  14  named claim condition 1: s2c_named_boot.py --selftest, then seed 0 on the 10 fresh m0 files      [CPU; decision]
#  13  MANIFEST.md5 of post/
# Decision passes (7, 10a, 8, 14) are non-aborting: rc in post/decision_rc.txt, the opening continues to the MANIFEST and ends rc 1
# if any failed. Reported passes (9, 10b, 10c): rc in post/extra_rc.txt. Core passes (0-6, and every real-splits check of 3 / 4 / 6)
# abort the opening (set -e) with rc 1.
# ONE end line in /home/noob/work/s2c/post.log: "[<date>] s2c scoring done: post rc=<rc>" (rc captured before $(date)). rc 2 = refused
# before any pass (settings incomplete, GS < 9,900, post/ or post_work/ exists). Python PIDs in s2c/post_pids.txt (gate passes too); to
# stop: the python PID first, then the post subshell, then this script; the end line then carries rc != 0.
set -u
# ######## settings: ONE block, s2c_settings.sh. Nothing else to edit here. ########
. /home/noob/work/s2c/open/s2c_settings.sh || { echo "[$(date)] s2c scoring done: post rc=2" >> /home/noob/work/s2c/post.log; exit 2; }
# ##################################################################################
. $GATE_SH
H=$OPEN; OUT=$S2_OUT
GS=${GS:?set GS (scoring gate MiB, >= 9900)}
ARMS="SKR01 SUPPF"
declare -A WT=([SKR01]=$SKR_WT [SUPPF]=$SUP_WT) DEP=([SKR01]=$SKR_DEP [SUPPF]=$SUP_DEP) DEPF=([SKR01]=$SKR_DEPLOY_FILE [SUPPF]=$SUP_DEPLOY_FILE)
declare -A EXP=([SKR01]=$SKR_EXP [SUPPF]=$SUP_EXP) EXPM=([SKR01]=$SKR_EXP_MD5 [SUPPF]=$SUP_EXP_MD5) RUNS=([SKR01]="$SKR_RUNS" [SUPPF]="$SUP_RUNS")
declare -A LAM=([SKR01]=$SKR_LA_MD5 [SUPPF]=$SUP_LA_MD5) RSM=([SKR01]=$SKR_RESCORE_MD5 [SUPPF]=$SUP_RESCORE_MD5)
CPU=(env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 nice -n 19)
GPU=(env HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1)
# prun LABEL LOG CMD...: one process in the background, PID recorded (env / nice exec, so it is python's PID), waited for; returns its rc
prun(){ local lab=$1 log=$2 pp; shift 2; "$@" > "$log" 2>&1 & pp=$!; echo "$(date '+%F %T') $pp $lab" >> $PIDS; wait $pp; }
fail(){ echo "[$(date)] FAIL: $*" >&2; exit 1; }   # stderr: reaches post.log even inside a stdout-redirected loop
# rs MODE ARGS...: real-splits assert (s2c_realsplits.py; counts / md5s / booleans only) appended to post/realsplits.txt; returns its rc
rs(){ echo "== $(date '+%F %T') realsplits $*" >> $OUT/realsplits.txt; "${CPU[@]}" $P $H/s2c_realsplits.py "$@" >> $OUT/realsplits.txt 2>&1; }

frozen_ok(){  # FROZEN.md5 lists every REQ file and md5sum -c passes; the third-party copies equal their originals
  local f; [ -s $H/FROZEN.md5 ] || { echo "no $H/FROZEN.md5"; return 1; }
  for f in $REQ; do grep -qE "^[0-9a-f]{32}  (\./)?$f\$" $H/FROZEN.md5 || { echo "FROZEN.md5 does not list $f"; return 1; }; done
  (cd $H && md5sum -c --quiet FROZEN.md5) || { echo "FROZEN.md5 check failed"; return 1; }
  (cd $H && md5sum -c --quiet s2c_copies.md5) || { echo "s2c_copies.md5 check failed"; return 1; }
}
man_ok(){ local d=$1 m=$2; [ "$(md5sum < $d/MANIFEST.md5 | cut -c1-32)" = $m ] || { echo "$d/MANIFEST.md5 md5 != $m"; return 1; }
          (cd $d && md5sum -c --quiet MANIFEST.md5) || { echo "$d: md5sum -c MANIFEST.md5 failed"; return 1; }; }

e1pass(){  # decision pass 7 (set -e is off inside: explicit returns)
  prun e1_selftest $OUT/e1_coprim_selftest.txt "${CPU[@]}" $P $H/s2c_e1_coprim.py --selftest --pf2-m0 $PF/m0 --hc-m0 $HCP/m0 \
    --hc-json $HCP/e1_coprim.json --trackm $H/trackM --thin $H/thin/thin_e1_relf1.py || return 1
  prun e1_coprim $OUT/e1_coprim.txt "${CPU[@]}" $P $H/s2c_e1_coprim.py --arm SUPPF $OUT/m0/SUPPF $SUP_RUNS --arm SKR01 $OUT/m0/SKR01 $SKR_RUNS \
    --rev SUPPF $SUP_DEP --rev SKR01 $SKR_DEP --base SUPPF --contrast SKR01 relF1 anyhit \
    --ref SUPPF_s5-9 $PF/m0 $CMP_RUNS --ref SKR01_s5-9 $S2P/m0/SKR01 $S2SKR_RUNS \
    --trackm $H/trackM --ctx $CTX --json $OUT/e1_coprim.json
}

guardspass(){  # decision pass 8
  prun guards_selftest $OUT/guards_selftest.txt "${CPU[@]}" $P $H/s2c_guards.py --selftest --trackm $H/trackM --pf2-m0 $PF/m0 \
    --hc-m0 $HCP/m0 --thin-m0 $THP/m0 || return 1
  prun guards $OUT/guards.txt "${CPU[@]}" $P $H/s2c_guards.py --trackm $H/trackM --arm SUPPF $OUT/m0/SUPPF $SUP_RUNS \
    --arm SKR01 $OUT/m0/SKR01 $SKR_RUNS --base SUPPF --g1 SKR01 --g2 SKR01 --json $OUT/guards.json
}

namedpass(){  # decision pass 14 (protocol §3a named claim, condition 1; §6 stage 2)
  prun named_selftest $OUT/named_boot_selftest.txt "${CPU[@]}" $P $H/s2c_named_boot.py --selftest --base SUPPF $PF/m0 $CMP_RUNS \
    --arm SKR01 $S2P/m0/SKR01 $S2SKR_RUNS --ref-txt $H/selftest_ref/coach_s2_boot.txt || return 1
  prun named_boot $OUT/named_boot.txt "${CPU[@]}" $P $H/s2c_named_boot.py --base SUPPF $OUT/m0/SUPPF $SUP_RUNS \
    --arm SKR01 $OUT/m0/SKR01 $SKR_RUNS --seed 0 --json $OUT/named_boot.json
}

cellgatepass(){  # reported pass 10b: wide B5 records of the 10 runs
  mkdir -p $OUT/cellgate || return 2
  prun cellgate $OUT/cellgate/s2_cellgate.txt "${CPU[@]}" $P $H/s2_cellgate.py --arm SUPPF $WK/b5/SUPPF/rec_w $SUP_RUNS \
    --arm SKR01 $WK/b5/SKR01/rec_w $SKR_RUNS --base SUPPF --json $OUT/cellgate/s2_cellgate.json
}

b5rs(){ local a; for a in $ARMS; do rs b5 --wt ${WT[$a]} --ext $X1 $WK/b5/$a/dump $WK/b5/$a/rec_w ${RUNS[$a]} || return 1; done; }
scrs(){ local a; for a in $ARMS; do rs scuffign --wt ${WT[$a]} --ext $X1 $OUT/m0_scuffign/$a ${RUNS[$a]} || return 1; done; }

post(){
  set -e
  DF=0
  dpass(){ local lab=$1 xrc=0; shift; "$@" || xrc=$?; echo "$lab rc=$xrc" >> $OUT/decision_rc.txt; [ $xrc = 0 ] || DF=$((DF + 1)); }
  spass(){ local lab=$1 xrc=0; shift; "$@" || xrc=$?; echo "$lab rc=$xrc" >> $OUT/extra_rc.txt; }
  # ---- 0. integrity ----
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
  done
  frozen_ok || fail "frozen scorer files"
  cp -p $H/FROZEN.md5 $OUT/FROZEN_s2c.md5
  cp -p $H/s2c_settings.sh $OUT/s2c_settings_used.sh
  man_ok $PF $MAN_PF2 || fail "PF2 opening files changed (MANIFEST)"
  man_ok $HCP $MAN_HC || fail "HC opening files changed (MANIFEST)"
  man_ok $THP $MAN_THIN || fail "THIN opening files changed (MANIFEST)"
  man_ok $S2P $MAN_S2 || fail "S2 (#5) opening files changed (MANIFEST)"
  man_ok $SKE $MAN_SKE || fail "SKR2E (#6) opening files changed (MANIFEST)"
  echo "reference files unchanged: PF2 post MANIFEST $MAN_PF2, HC post MANIFEST $MAN_HC, THIN post MANIFEST $MAN_THIN, S2 post MANIFEST $MAN_S2, SKR2E out MANIFEST $MAN_SKE (md5sum -c)" > $OUT/comparator_check.txt
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
  # launch.log conditions (queue log; holds no metric): per run 'config OK <run>' and 'trained <run> rc=0' exactly once, the end line, no HOLD
  for a in $ARMS; do for r in ${RUNS[$a]}; do
    [ "$(grep -c "] config OK $r vs pf2_SUPPF_100pct_s5: " $LL)" = 1 ] || fail "launch.log: 'config OK $r' not exactly once"
    [ "$(grep -c "] trained $r rc=0\$" $LL)" = 1 ] || fail "launch.log: 'trained $r rc=0' not exactly once"
  done; done
  [ "$(grep -c '] S2C ALL TRAINED (10 rc 0 of 10; ' $LL)" = 1 ] || fail "launch.log: no 'S2C ALL TRAINED (10 rc 0 of 10' line"
  [ ! -e $S2/HOLD ] || fail "s2c/HOLD exists"
  echo "launch.log $LL_MD5: 10 x 'config OK', 10 x 'trained <run> rc=0', 'S2C ALL TRAINED (10 rc 0 of 10', no s2c/HOLD" >> $OUT/comparator_check.txt
  rs pre --wt $SUP_WT --wt $SKR_WT --ext $X1 --root-splits $ROOT_SPLITS $ROOT_SPLITS_MD5 || fail "real splits (pre)"
  { echo "protocol_SKR2C v1 (91b76abd + §9; rulings_s2c_stage2.md) opening = E1 opening #7 (same 50 test and 106 E1 cells, 3rd look); GS $GS"
    for a in $ARMS; do echo "$a: ${WT[$a]} deploy ${DEP[$a]}; exp ${EXP[$a]} (${EXPM[$a]}); runs $(echo ${RUNS[$a]})"; done
    echo "reference rows (#5, opened): $(echo $CMP_RUNS) / $(echo $S2SKR_RUNS); settings md5 $(md5sum < $H/s2c_settings.sh | cut -c1-32)"; } > $OUT/post_settings.txt
  # ---- 1. completeness (the one stdout grep) ----
  for a in $ARMS; do for r in ${RUNS[$a]}; do grep -q "step 20000/20000" ${WT[$a]}/experiments/$r.stdout || fail "INCOMPLETE $r"; done; done
  # ---- 2. config record (config_used.yaml only; as the s2c queue's cfgcheck) ----
  for a in $ARMS; do for r in ${RUNS[$a]}; do
    c=${WT[$a]}/experiments/$r/config_used.yaml; k=${r##*_s}
    d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' $REF_CFG) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
    [ "$d" = "$(sort ${EXP[$a]})" ] || fail "config of $r: diff vs pf2_SUPPF_100pct_s5 != $(basename ${EXP[$a]})"
    grep -qx "seed: $k" $c || fail "config of $r: seed != $k"
    echo "$r ($a): config diff vs pf2_SUPPF_100pct_s5 = $(basename ${EXP[$a]}) (${EXPM[$a]:0:8}), seed $k; $(md5sum < ${WT[$a]}/experiments/$r/checkpoints/latest.pth | cut -c1-32) latest.pth"
  done; done > $OUT/init_check.txt
  # ---- 3. rescore_label_versions per run, from the arm's worktree [GPU] ----
  for a in $ARMS; do mkdir -p $OUT/rescore/$a; for r in ${RUNS[$a]}; do
    gate_wait $GS "s2c post rescore $r"
    prun rescore_$r $OUT/rescore/$a/$r.log "${GPU[@]}" $P ${WT[$a]}/scripts/rescore_label_versions.py --runs $r --out $OUT/rescore/$a/$r.json
  done; rs rescore --wt ${WT[$a]} $OUT/rescore/$a ${RUNS[$a]} || fail "real splits (rescore $a)"; done
  # ---- 4. m0_audit default + tau 0 / 1 per arm, --code = the arm's worktree [GPU] ----
  declare -A M0D=([SKR01]=$SKR_WT/scripts/b3/m0_audit_b3.py [SUPPF]=$F1/m0_audit.py) M0T=([SKR01]=$SKR_WT/scripts/b3/m0_audit_b3.py [SUPPF]=$F1/m0_audit_tau.py)
  for a in $ARMS; do
    RD=$(for r in ${RUNS[$a]}; do echo ${WT[$a]}/experiments/$r; done)
    gate_wait $GS "s2c post m0 $a"
    prun m0_$a $OUT/m0_audit_$a.log "${GPU[@]}" $P ${M0D[$a]} --code ${WT[$a]} --out $OUT/m0/$a --ext $X1 --no-logits --runs $RD
    for T in 0 1; do
      gate_wait $GS "s2c post m0 $a tau$T"
      prun m0_${a}_tau$T $OUT/m0_audit_${a}_tau$T.log "${GPU[@]}" $P ${M0T[$a]} --code ${WT[$a]} --out $OUT/m0/$a --ext $X1 --no-logits --tau $T --runs $RD
    done
    rs m0 --wt ${WT[$a]} --ext $X1 $OUT/m0/$a ${RUNS[$a]} || fail "real splits (m0 $a)"
  done
  # ---- 5. tau0 check per arm [CPU] ----
  for a in $ARMS; do
    "${CPU[@]}" $P - "$OUT/m0/$a" "${DEP[$a]}" ${RUNS[$a]} > $OUT/tau0_check_$a.txt <<'PY'
import json, sys
o, dep, runs = sys.argv[1], sys.argv[2], sys.argv[3:]
J = {r: json.load(open(f"{o}/{r}.json")) for r in runs}
bad = [r for r in runs if J[r]["cells"] != json.load(open(f"{o}/{r}.tau0.json"))["cells"]]
assert all(J[r]["step"] == 20000 and J[r]["code_revision"] == dep for r in runs), {r: (J[r]["step"], J[r]["code_revision"]) for r in runs}
n = {r: {k: len(v) for k, v in J[r]["cells"].items()} for r in runs}
assert all(n[r]["val"] == 54 and n[r]["test"] == 50 and n[r]["ext"] == 106 for r in runs), n
assert all(len(c["conf"]) == 576 for r in runs for k in ("val", "test", "ext") for c in J[r]["cells"][k].values()), "conf not 24x24"
assert not bad, bad
print("tau0 == default cells for all runs: True | step 20000 and code_revision", dep, "for all", len(runs), "| cells per set", n[runs[0]], "| conf 24x24")
PY
  done
  # ---- 6. LA tau 0 / 1 per arm [GPU] ----
  for a in $ARMS; do
    gate_wait $GS "s2c post LA $a"
    prun la_$a $OUT/la_$a.log "${GPU[@]}" $P ${WT[$a]}/scripts/rescore_logit_adjust.py --runs ${RUNS[$a]} --taus 0 1 --splits test val \
      --out $OUT/la_$a.json --check $OUT/rescore/$a
    rs la --wt ${WT[$a]} $OUT/la_$a.json ${RUNS[$a]} || fail "real splits (LA $a)"
  done
  # ---- 7. E1 co-primaries [CPU; decision] ----
  dpass e1_coprim e1pass
  # ---- 9. 20k encoder cosines, 10 runs [CPU; reported] ----
  PAIRS=(); for a in $ARMS; do for r in ${RUNS[$a]}; do PAIRS+=(--pair "$r vs ImageNet" $S0 ${WT[$a]}/experiments/$r/checkpoints/latest.pth); done; done
  spass enc_cosine prun enc_cosine $OUT/enc_cosine_20k.txt env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1 nice -n 19 \
    $P $ENC --out $OUT/enc_cosine_20k.json "${PAIRS[@]}"
  # ---- 10a. B5 wide grid [GPU inside the hook, gate per run; decision: co-primary input] ----
  dpass b5w prun s2c_b5w $OUT/extra_s2c_b5w.log env GS=$GS bash $H/post_extra/s2c_b5w.sh
  dpass realsplits_b5 b5rs
  # ---- 10b. SKR + cell gate line [CPU; reported] ----
  spass cellgate cellgatepass
  # ---- 10c. scuff-ignored test [GPU inside the hook, gate per arm; reported] ----
  spass scuffign prun s2c_scuffign $OUT/extra_s2c_scuffign.log env GS=$GS bash $H/post_extra/s2c_scuffign.sh
  spass realsplits_scuffign scrs
  # ---- 8. guards G1 / G2 [CPU; decision] ----
  dpass guards guardspass
  # ---- 14. named claim condition 1 [CPU; decision] ----
  dpass named_boot namedpass
  # ---- 13. MANIFEST ----
  (cd $OUT && find . -type f ! -name MANIFEST.md5 -print0 | sort -z | xargs -0 md5sum > MANIFEST.md5)
  echo "[$(date)] decision passes failed: $DF (decision_rc.txt)"
  [ $DF = 0 ]
}

pre(){ m=$(settings_check) || { echo "refused: $m"; return 2; }
       [ "$GS" -ge 9900 ] 2>/dev/null || { echo "refused: GS '$GS' < 9900"; return 2; }
       [ ! -e $OUT ] || { echo "refused: $OUT exists (a rerun needs coach's word and a fresh dir)"; return 2; }
       [ ! -e $WK ] || { echo "refused: $WK exists (a rerun needs coach's word and a fresh dir)"; return 2; }
       mkdir -p $OUT/m0/SKR01 $OUT/m0/SUPPF $WK; }
if pre >> $S2/post_pre.log 2>&1; then
  ( post ) > $OUT.log 2>&1
  rc=$?
else
  rc=2
fi
echo "[$(date)] s2c scoring done: post rc=$rc" >> $NL
exit $rc   # SKR2C: the driver (s2c_opening.sh) starts D only if this is 0
