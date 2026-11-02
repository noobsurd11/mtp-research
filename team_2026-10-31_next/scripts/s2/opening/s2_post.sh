#!/bin/bash
# SKR2 + HC2 scoring on gaint, the ONE pre-registered opening of protocol_SKR2_HC2 (v1.0.1 0cf1344b §3, §4, §6, §9; HC2 under v1.1);
# E1 opening #5. DRAFT (runner's helper, 2 Nov 2026; runner review: SKR01 m0 scorer = el_thin m0_audit_b3, as THIN) for coach's FREEZE. From hc_post.sh (088145323, frozen HC
# opening): structure kept (prun / dpass / spass, gate per GPU process, FAST, PIDs, core passes abort, decision / reported rc files,
# one end line); changed: two arms with --code per arm (settings in s2_settings.sh), per-arm subdirs, new decision passes (guards,
# B5 wide grid), comparator reuse checks for PF2 B5 dumps and HC's SHV1 / rf files. Lives in /home/noob/work/s2q/open/.
# Fired by s2_postwatch.sh when all 10 runs trained rc 0 with 'config OK' in s2q/launch.log.  Usage: GS=<MiB, >= 9900> bash s2_post.sh
# Out: /home/noob/work/s2q/post/ (per-arm subdirs SKR01 / HC2 where a tool writes per run). Work dirs (dumps, ~6 GB) in
# /home/noob/work/s2q/post_work/ (outside post/). Comparator SUPPF = PF2's pf2_SUPPF_100pct_s5..9: m0 / rescore / LA / B5 files from
# el_f3/reports/pf2/post (MANIFEST 3827f7c0), val / rf / SHV1 records + dumps from HC's opening (post MANIFEST d5c39e0d, syn_work);
# reused unchanged, re-checked by md5sum -c.
# GPU passes: one shared-gate wait per GPU process (gpu_gate.sh: flock, free >= GS, >= 120 s since any start, HOLD). CPU passes: CUDA
# hidden, nice 19, <= 8 threads. gpu_gate/FAST touched for the whole opening (1 s gpumem samples), removed at the end.
# Passes (label = the brief's number; run in the order listed; 8 runs after 12 because G3 reads the F51 output):
#   0  integrity (each check its own statement, '|| fail'): per arm HEAD = DEPLOY file = REVISION = deploy, 0 tracked changes, data links
#      = el_f3's; settings complete; FROZEN.md5 lists every REQ file + md5sum -c; s2_copies.md5; MANIFESTs PF2 / HC / THIN (md5 + -c);
#      external scorer / data md5s (scorer_md5.txt); SUPPF B5 dumps (PF2 list) and HC syn_work dumps (HC list) md5sum -c
#   1  completeness: grep -q "step 20000/20000" on each of the 10 stdouts; 1b HC2 only: the LAST 'synth window:' + LAST 'synth inactive:'
#      line per HC2 stdout (coach ruling 6; reported; synthetic_inactive_px != 0 -> decision flag). Nothing else of a stdout is read
#   2  config record from config_used.yaml: diff vs pf2_SUPPF_100pct_s5 == the arm's exp file, seed K; latest.pth md5s
#   3  rescore_label_versions per run, from the arm's worktree                                       [GPU, gate per run: 10]
#   4  m0 per-cell files, default + tau 0 / 1, val / test / ext117, --code per arm                 [GPU, 3 gates per arm: 6]
#      SKR01: el_thin's scripts/b3/m0_audit_b3.py 7aa7d6d8 (THIN's opening scorer on this deploy; for a 24-class run it equals
#      m0_audit_tau d77241bb, no scuff flags here, so the cell schema = m0_audit's); HC2: m0_audit d36f7438 + m0_audit_tau d77241bb (as HC)
#   5  tau0 check per arm: tau0 cells == default, step 20000, code_revision = the arm's deploy, 54 / 50 / 106 cells   [CPU]
#   6  LA tau 0 / 1 per arm (the arm's rescore_logit_adjust), test + val, --check vs the rescore JSONs   [GPU, gate per arm: 2]
#   7  E1 co-primaries: s2_e1_coprim.py --selftest, then the scorer                                   [CPU; decision]
#   9  20k encoder cosines vs ImageNet R34, 10 runs (enc_cosine d3bc7a70)                             [CPU; reported]
#  10a B5 wide grid: post_extra/s2_b5w.sh (frozen calib hook + el_metrics_w; SUPPF records remade from PF2's dumps; OP check)
#                                                                         [GPU, gate per run inside the hook: 10; decision (SKR2 co-primary)]
#  10b SKR + cell gate line (protocol §9 v1.0.1): s2_cellgate.py on the B5 records                    [CPU; reported]
#  10c scuff-ignored test: post_extra/s2_scuffign.sh (pf2_scuffign.py, --code per arm)                [GPU, gate per arm inside: 2; reported]
#  11  SHV1 / SHV1-p mechanism + val / rf / SHV1 dumps: s2_shv1.sh (CPU fp32; SUPPF + HC reused)      [CPU; decision for HC2]
#  12  F51 / H36: s2_f51.py --selftest, then the readout (G3 input for HC2; reported for SKR2)        [CPU; decision]
#   8  guards G1-G3: s2_guards.py --selftest, then the guards (G3 from pass 12's JSON)                [CPU; decision]
#  13  MANIFEST.md5 of post/
# Decision passes (7, 10a, 11, 12, 8) are non-aborting: rc in post/decision_rc.txt, the opening continues to the MANIFEST and ends rc 1
# if any failed. Reported passes (9, 10b, 10c): rc in post/extra_rc.txt. Core passes (0-6) abort the opening (set -e) with rc 1.
# ONE end line in /home/noob/work/s2q/post.log: "[<date>] s2q scoring done: post rc=<rc>" (rc captured before $(date); s2q_gpumem.sh
# stops 60 s later). rc 2 = refused before any pass (settings incomplete, GS < 9,900, post/ or post_work/ exists). Python PIDs in
# s2q/post_pids.txt (gate passes too); to stop: the python PID first, then the post subshell, then this script; the end line then
# carries rc != 0.
set -u
# ######## settings: ONE block, s2_settings.sh (SKR01 fixed; HC2 = placeholders until protocol v1.1). Nothing else to edit here. ########
. /home/noob/work/s2q/open/s2_settings.sh || { echo "[$(date)] s2q scoring done: post rc=2" >> /home/noob/work/s2q/post.log; exit 2; }
# ########################################################################################################################################
. $GATE_SH
H=$OPEN; OUT=$S2_OUT
GS=${GS:?set GS (scoring gate MiB, >= 9900)}
ARMS="SKR01 HC2"
declare -A WT=([SKR01]=$SKR_WT [HC2]=$HC2_WT) DEP=([SKR01]=$SKR_DEP [HC2]=$HC2_DEP) DEPF=([SKR01]=$SKR_DEPLOY_FILE [HC2]=$HC2_DEPLOY_FILE)
declare -A EXP=([SKR01]=$SKR_EXP [HC2]=$HC2_EXP) EXPM=([SKR01]=$SKR_EXP_MD5 [HC2]=$HC2_EXP_MD5) RUNS=([SKR01]="$SKR_RUNS" [HC2]="$HC2_RUNS")
declare -A LAM=([SKR01]=$SKR_LA_MD5 [HC2]=$HC2_LA_MD5) RSM=([SKR01]=$SKR_RESCORE_MD5 [HC2]=$HC2_RESCORE_MD5)
CPU=(env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 nice -n 19)
GPU=(env HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1)
# prun LABEL LOG CMD...: one process in the background, PID recorded (env / nice exec, so it is python's PID), waited for; returns its rc
prun(){ local lab=$1 log=$2 pp; shift 2; "$@" > "$log" 2>&1 & pp=$!; echo "$(date '+%F %T') $pp $lab" >> $PIDS; wait $pp; }
fail(){ echo "[$(date)] FAIL: $*" >&2; exit 1; }   # stderr: reaches post.log even inside a stdout-redirected loop

frozen_ok(){  # coach's FROZEN.md5 lists every REQ file and md5sum -c passes; the third-party copies equal their originals
  local f; [ -s $H/FROZEN.md5 ] || { echo "no $H/FROZEN.md5"; return 1; }
  for f in $REQ; do grep -qE "^[0-9a-f]{32}  (\./)?$f\$" $H/FROZEN.md5 || { echo "FROZEN.md5 does not list $f"; return 1; }; done
  (cd $H && md5sum -c --quiet FROZEN.md5) || { echo "FROZEN.md5 check failed"; return 1; }
  (cd $H && md5sum -c --quiet s2_copies.md5) || { echo "s2_copies.md5 check failed"; return 1; }
}
man_ok(){ local d=$1 m=$2; [ "$(md5sum < $d/MANIFEST.md5 | cut -c1-32)" = $m ] || { echo "$d/MANIFEST.md5 md5 != $m"; return 1; }
          (cd $d && md5sum -c --quiet MANIFEST.md5) || { echo "$d: md5sum -c MANIFEST.md5 failed"; return 1; }; }

e1pass(){  # decision pass 7 (set -e is off inside: explicit returns)
  prun e1_selftest $OUT/e1_coprim_selftest.txt "${CPU[@]}" $P $H/s2_e1_coprim.py --selftest --pf2-m0 $PF/m0 --hc-m0 $HCP/m0 \
    --hc-json $HCP/e1_coprim.json --trackm $H/trackM --thin $H/thin/thin_e1_relf1.py || return 1
  prun e1_coprim $OUT/e1_coprim.txt "${CPU[@]}" $P $H/s2_e1_coprim.py --arm SUPPF $PF/m0 $CMP_RUNS --arm SKR01 $OUT/m0/SKR01 $SKR_RUNS \
    --arm HC2 $OUT/m0/HC2 $HC2_RUNS --rev SUPPF e544133 --rev SKR01 $SKR_DEP --rev HC2 $HC2_DEP --base SUPPF \
    --contrast SKR01 relF1 anyhit --contrast HC2 relF1 inactIoU --ref HC $HCP/m0 $HC_RUNS --ref SKRw1 $THP/m0 $THSKR_RUNS \
    --trackm $H/trackM --ctx $CTX --json $OUT/e1_coprim.json
}

f51pass(){  # decision pass 12
  [ -e $WK/syn/DUMPS_OK ] || { echo "no complete val / rf dumps + records (s2_shv1 passes 1-2)"; return 2; }
  mkdir -p $OUT/f51 || return 2
  prun f51_selftest $OUT/f51/s2_f51_selftest.txt "${CPU[@]}" $P $H/s2_f51.py --selftest --a8 $H/found/a8_screen_score.py --el-metrics $H/calib_syn || return 1
  prun f51 $OUT/f51/s2_f51.txt "${CPU[@]}" $P $H/s2_f51.py --a8 $H/found/a8_screen_score.py --el-metrics $H/calib_syn \
    --arm SUPPF $HCSYN/dump $HCP/shv1/rec $CMP_RUNS --arm SKR01 $WK/syn/dump $WK/syn/rec $SKR_RUNS --arm HC2 $WK/syn/dump $WK/syn/rec $HC2_RUNS \
    --arm HC $HCSYN/dump $HCP/shv1/rec $HC_RUNS --base SUPPF --test HC2 SKR01 --decide HC2 --ref HC \
    --check-ref HC $HCP/f51/hc_f51.json 349c3d90e6873281c472828da549b1ab \
    --code /home/noob/work/el_f3 --rf /home/noob/work/calib/data/rf --rf-sets /home/noob/work/found/t9/rf_sets.tsv --boot 2000 --out $OUT/f51/s2_f51.json
}

guardspass(){  # decision pass 8 (after 12)
  prun guards_selftest $OUT/guards_selftest.txt "${CPU[@]}" $P $H/s2_guards.py --selftest --trackm $H/trackM --pf2-m0 $PF/m0 \
    --hc-m0 $HCP/m0 --thin-m0 $THP/m0 || return 1
  prun guards $OUT/guards.txt "${CPU[@]}" $P $H/s2_guards.py --trackm $H/trackM --arm SUPPF $PF/m0 $CMP_RUNS \
    --arm SKR01 $OUT/m0/SKR01 $SKR_RUNS --arm HC2 $OUT/m0/HC2 $HC2_RUNS --base SUPPF --g1 SKR01 HC2 --g2 SKR01 \
    --g3 HC2 $OUT/f51/s2_f51.json --json $OUT/guards.json
}

cellgatepass(){  # reported pass 10b (protocol §9 v1.0.1): wide B5 records of the 15 runs
  mkdir -p $OUT/cellgate || return 2
  prun cellgate $OUT/cellgate/s2_cellgate.txt "${CPU[@]}" $P $H/s2_cellgate.py --arm SUPPF $WK/b5/SUPPF/rec_w $CMP_RUNS \
    --arm SKR01 $WK/b5/SKR01/rec_w $SKR_RUNS --arm HC2 $WK/b5/HC2/rec_w $HC2_RUNS --base SUPPF --json $OUT/cellgate/s2_cellgate.json
}

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
    [ "$(cat $w/REVISION 2>/dev/null)" = $d ] || fail "$a: $w/REVISION != $d (s2_postwatch writes it at arming if absent)"
    [ -z "$(git -C $w status --short --untracked-files=no)" ] || fail "$a: tracked changes in $w"
    for l in data/escdd_masks data/labeled/masks_escdd data/labeled/images; do
      [ "$(readlink -f $w/$l)" = "$(readlink -f /home/noob/work/el_f3/$l)" ] || fail "$a: $w/$l and el_f3's resolve to different targets"
    done
  done
  frozen_ok || fail "frozen scorer files"
  cp -p $H/FROZEN.md5 $OUT/FROZEN_s2.md5
  cp -p $H/s2_settings.sh $OUT/s2_settings_used.sh
  man_ok $PF $MAN_PF2 || fail "PF2 comparator files changed (MANIFEST)"
  man_ok $HCP $MAN_HC || fail "HC opening files changed (MANIFEST)"
  man_ok $THP $MAN_THIN || fail "THIN opening files changed (MANIFEST)"
  echo "comparator / reference files unchanged: PF2 post MANIFEST $MAN_PF2, HC post MANIFEST $MAN_HC, THIN post MANIFEST $MAN_THIN (md5sum -c)" > $OUT/comparator_check.txt
  printf '%s\n' \
    "d36f7438d0fefb0ffc926c69f6c6af2d  $F1/m0_audit.py" \
    "d77241bbe2845cabc2779adc827eb838  $F1/m0_audit_tau.py" \
    "7aa7d6d807b9eccb87360a5b9eb8eb81  $SKR_WT/scripts/b3/m0_audit_b3.py" \
    "$SKR_RESCORE_MD5  $SKR_WT/scripts/rescore_label_versions.py" \
    "$SKR_LA_MD5  $SKR_WT/scripts/rescore_logit_adjust.py" \
    "$HC2_RESCORE_MD5  $HC2_WT/scripts/rescore_label_versions.py" \
    "$HC2_LA_MD5  $HC2_WT/scripts/rescore_logit_adjust.py" \
    "d3bc7a708d3630de7322fc6dd2ff403e  $ENC" \
    "178b872d35d15689f6ab38bf57789327  $S0" \
    "00fabfddaf7d7dfd11e25008f94f744d  $GATE_SH" \
    "4e7ff5667feec6c8ca239343833c224b  $B5_DEVICE_FILE" \
    "12bd138523fccfc6be5b41df35d19147  $CTX" \
    "5266806b559f74bcf9eae167bb076b95  $X1/stems_eval.txt" \
    "14771356ef7c99f567c5f80dad2e48dd  /home/noob/work/found/t9/rf_sets.tsv" \
    "3a65c2fb0ecaf32e91377d4ad249029a  /home/noob/work/calib/data/rf/stems_eval.txt" \
    "9dcccf00662dfca750f0b46628f8d5bb  /home/noob/work/el_f3/data/splits/val.txt" \
    "a31fad14fa27ee28e2a2319b8976aba3  /home/noob/work/el_f3/data/splits/test.txt" \
    "9dcccf00662dfca750f0b46628f8d5bb  $SKR_WT/data/splits/val.txt" \
    "a31fad14fa27ee28e2a2319b8976aba3  $SKR_WT/data/splits/test.txt" \
    "9dcccf00662dfca750f0b46628f8d5bb  $HC2_WT/data/splits/val.txt" \
    "a31fad14fa27ee28e2a2319b8976aba3  $HC2_WT/data/splits/test.txt" \
    "$SKR_EXP_MD5  $SKR_EXP" \
    "$HC2_EXP_MD5  $HC2_EXP" \
    "6aba106ae295950d99baff75cfaa407b  $REF_CFG" > $OUT/scorer_md5_expected.txt
  md5sum -c $OUT/scorer_md5_expected.txt > $OUT/scorer_md5.txt 2>&1 || fail "external scorer / data md5 (scorer_md5.txt)"
  grep -E '  pf2_SUPPF_100pct_s[5-9]\.(val|test|ext)\.npz$' $PF/b5/dump_md5_on_gaint.txt > $OUT/suppf_b5_dump_md5.txt || fail "PF2 b5 dump md5 list"
  [ "$(wc -l < $OUT/suppf_b5_dump_md5.txt)" = 15 ] || fail "PF2 b5 dump md5 list: SUPPF s5-9 val / test / ext != 15 lines"
  (cd $PF2B5/dump && md5sum -c --quiet $OUT/suppf_b5_dump_md5.txt) || fail "PF2 b5_work SUPPF dumps missing or changed"
  [ "$(wc -l < $HCP/shv1/dump_md5_on_gaint.txt)" = 30 ] || fail "HC syn_work dump md5 list != 30 lines"
  (cd $HCSYN/dump && md5sum -c --quiet $HCP/shv1/dump_md5_on_gaint.txt) || fail "HC syn_work dumps (SUPPF + HC val / rf / SHV1) missing or changed"
  echo "SUPPF B5 dumps (15, PF2 list) and HC syn_work dumps (30, HC list) present and unchanged" >> $OUT/comparator_check.txt
  { echo "protocol_SKR2_HC2 v1.0.1 (0cf1344b; HC2 v1.1) opening = E1 opening #5; GS $GS"
    for a in $ARMS; do echo "$a: ${WT[$a]} deploy ${DEP[$a]}; exp ${EXP[$a]} (${EXPM[$a]}); runs $(echo ${RUNS[$a]})"; done
    echo "comparator SUPPF: $(echo $CMP_RUNS) (PF2 opening files; HC opening SHV1 / rf files); settings md5 $(md5sum < $H/s2_settings.sh | cut -c1-32)"; } > $OUT/post_settings.txt
  # ---- 1. completeness (the one stdout grep) ----
  for a in $ARMS; do for r in ${RUNS[$a]}; do grep -q "step 20000/20000" ${WT[$a]}/experiments/$r.stdout || fail "INCOMPLETE $r"; done; done
  # ---- 1b. HC2 live synthetic readouts (coach ruling 6, 2 Nov): per HC2 stdout ONLY the LAST 'synth window:' and the LAST
  #      'synth inactive:' line, by line prefix; reported (post/hc2_synth_readout.txt); total synthetic_inactive_px != 0 (or no
  #      parsable total) -> decision flag hc2_synth_inactive rc=1 (no abort). '|| true' keeps an empty grep from tripping set -e.
  SI=0
  for r in $HC2_RUNS; do
    sw=$(grep -F "synth window:" $HC2_WT/experiments/$r.stdout | tail -n 1 | sed 's/^.*synth window:/synth window:/' || true)
    si=$(grep -F "synth inactive:" $HC2_WT/experiments/$r.stdout | tail -n 1 | sed 's/^.*synth inactive:/synth inactive:/' || true)
    t=$(echo "$si" | grep -oE "total: excluded [0-9]+ \(share [0-9.]+\) synthetic_inactive_px [0-9]+" | grep -oE "[0-9]+\$" || true)
    echo "$r | $sw | $si | total synthetic_inactive_px ${t:-UNPARSED}"
    [ "${t:-x}" = 0 ] || SI=$((SI + 1))
  done > $OUT/hc2_synth_readout.txt
  echo "hc2_synth_inactive rc=$([ $SI = 0 ] && echo 0 || echo 1)" >> $OUT/decision_rc.txt
  [ $SI = 0 ] || DF=$((DF + 1))
  # ---- 2. config record (config_used.yaml only; as the s2q queue's cfgcheck) ----
  for a in $ARMS; do for r in ${RUNS[$a]}; do
    c=${WT[$a]}/experiments/$r/config_used.yaml; k=${r##*_s}
    d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' $REF_CFG) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
    [ "$d" = "$(sort ${EXP[$a]})" ] || fail "config of $r: diff vs pf2_SUPPF_100pct_s5 != $(basename ${EXP[$a]})"
    grep -qx "seed: $k" $c || fail "config of $r: seed != $k"
    echo "$r ($a): config diff vs pf2_SUPPF_100pct_s5 = $(basename ${EXP[$a]}) (${EXPM[$a]:0:8}), seed $k; $(md5sum < ${WT[$a]}/experiments/$r/checkpoints/latest.pth | cut -c1-32) latest.pth"
  done; done > $OUT/init_check.txt
  # ---- 3. rescore_label_versions per run, from the arm's worktree [GPU] ----
  for a in $ARMS; do mkdir -p $OUT/rescore/$a; for r in ${RUNS[$a]}; do
    gate_wait $GS "s2 post rescore $r"
    prun rescore_$r $OUT/rescore/$a/$r.log "${GPU[@]}" $P ${WT[$a]}/scripts/rescore_label_versions.py --runs $r --out $OUT/rescore/$a/$r.json
  done; done
  # ---- 4. m0_audit default + tau 0 / 1 per arm, --code = the arm's worktree [GPU] ----
  declare -A M0D=([SKR01]=$SKR_WT/scripts/b3/m0_audit_b3.py [HC2]=$F1/m0_audit.py) M0T=([SKR01]=$SKR_WT/scripts/b3/m0_audit_b3.py [HC2]=$F1/m0_audit_tau.py)
  for a in $ARMS; do
    RD=$(for r in ${RUNS[$a]}; do echo ${WT[$a]}/experiments/$r; done)
    gate_wait $GS "s2 post m0 $a"
    prun m0_$a $OUT/m0_audit_$a.log "${GPU[@]}" $P ${M0D[$a]} --code ${WT[$a]} --out $OUT/m0/$a --ext $X1 --no-logits --runs $RD
    for T in 0 1; do
      gate_wait $GS "s2 post m0 $a tau$T"
      prun m0_${a}_tau$T $OUT/m0_audit_${a}_tau$T.log "${GPU[@]}" $P ${M0T[$a]} --code ${WT[$a]} --out $OUT/m0/$a --ext $X1 --no-logits --tau $T --runs $RD
    done
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
    gate_wait $GS "s2 post LA $a"
    prun la_$a $OUT/la_$a.log "${GPU[@]}" $P ${WT[$a]}/scripts/rescore_logit_adjust.py --runs ${RUNS[$a]} --taus 0 1 --splits test val \
      --out $OUT/la_$a.json --check $OUT/rescore/$a
  done
  # ---- 7. E1 co-primaries [CPU; decision] ----
  dpass e1_coprim e1pass
  # ---- 9. 20k encoder cosines, 10 runs [CPU; reported] ----
  PAIRS=(); for a in $ARMS; do for r in ${RUNS[$a]}; do PAIRS+=(--pair "$r vs ImageNet" $S0 ${WT[$a]}/experiments/$r/checkpoints/latest.pth); done; done
  spass enc_cosine prun enc_cosine $OUT/enc_cosine_20k.txt env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1 nice -n 19 \
    $P $ENC --out $OUT/enc_cosine_20k.json "${PAIRS[@]}"
  # ---- 10a. B5 wide grid [GPU inside the hook, gate per run; decision: SKR2 co-primary input] ----
  dpass b5w prun s2_b5w $OUT/extra_s2_b5w.log env GS=$GS bash $H/post_extra/s2_b5w.sh
  # ---- 10b. SKR + cell gate line [CPU; reported; protocol §9 v1.0.1] ----
  spass cellgate cellgatepass
  # ---- 10c. scuff-ignored test [GPU inside the hook, gate per arm; reported] ----
  spass scuffign prun s2_scuffign $OUT/extra_s2_scuffign.log env GS=$GS bash $H/post_extra/s2_scuffign.sh
  # ---- 11. SHV1 mechanism + shared val / rf dumps [CPU; decision] ----
  dpass shv1 prun s2_shv1 $OUT/s2_shv1.stdout bash $H/s2_shv1.sh
  # ---- 12. F51 / H36 [CPU; decision: G3 input] ----
  dpass f51 f51pass
  # ---- 8. guards G1-G3 [CPU; decision; after 12] ----
  dpass guards guardspass
  # ---- 13. MANIFEST ----
  (cd $OUT && find . -type f ! -name MANIFEST.md5 -print0 | sort -z | xargs -0 md5sum > MANIFEST.md5)
  echo "[$(date)] decision passes failed: $DF (decision_rc.txt)"
  [ $DF = 0 ]
}

pre(){ m=$(settings_check) || { echo "refused: $m"; return 2; }
       [ "$GS" -ge 9900 ] 2>/dev/null || { echo "refused: GS '$GS' < 9900"; return 2; }
       [ ! -e $OUT ] || { echo "refused: $OUT exists (a rerun needs coach's word and a fresh dir)"; return 2; }
       [ ! -e $WK ] || { echo "refused: $WK exists (a rerun needs coach's word and a fresh dir)"; return 2; }
       mkdir -p $OUT/m0/SKR01 $OUT/m0/HC2 $WK; }
touch $GG/FAST   # 1 s gpumem samples for the whole opening
if pre >> $S2/post_pre.log 2>&1; then
  ( post ) > $OUT.log 2>&1
  rc=$?
else
  rc=2
fi
rm -f $GG/FAST
echo "[$(date)] s2q scoring done: post rc=$rc" >> $NL
