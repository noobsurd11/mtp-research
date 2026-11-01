#!/bin/bash
# HC scoring on gaint (el_hc, deploy c2e6973), the ONE pre-registered opening of protocol_HC v1.1 (§4-6, §9.3); E1 opening #3.
# DRAFT (runner's helper, 1 Nov 2026) for coach's review and FREEZE; lives in /home/noob/work/nq/hc/ (listed in coach's FROZEN.md5).
# Fired by hc_postwatch.sh when hc_HC_100pct_s5..9 all trained rc 0 with 'config OK' (nq launch.log). Usage: GS=<MiB, >= 9900> bash hc_post.sh
# Out: el_hc/reports/hc/post/ (absolute paths throughout). Comparator: PF2's pf2_SUPPF_100pct_s5..9 opening files, reused unchanged
# (el_f3/reports/pf2/post, MANIFEST re-checked); PF2's SUPPF B5 per-run / pooled OPs reused from the same files.
# GPU passes: one shared-gate wait per GPU process (gpu_gate.sh: flock, free >= GS, >= 120 s since any start, HOLD), GS from env (>= 9,900);
# gpu_gate/FAST touched for the whole opening (1 s gpumem samples), removed at the end. CPU passes: CUDA hidden, nice 19, <= 8 threads.
# Passes:
#   0  integrity (each check fails the opening; no bash '&&'-list under set -e): HEAD = reports/hc/DEPLOY = REVISION = c2e6973, 0 tracked
#      changes; coach's FROZEN.md5 lists every scorer file and md5sum -c passes; third-party copies (hc_copies.md5); PF2 comparator
#      MANIFEST (md5sum -c); external scorer / data md5s (scorer_md5.txt)
#   1  completeness: grep -q "step 20000/20000" on each HC stdout (the ONE stdout grep; nothing else of a stdout is read)
#   2  config record from config_used.yaml only: diff vs pf2_SUPPF_100pct_s5 == nq exp_HC.txt (01008fdf), seed K; latest.pth md5s
#   3  rescore_label_versions (1e41202b) per run                                  [GPU, gate per run]
#   4  m0_audit d36f7438 default + m0_audit_tau d77241bb tau 0 / 1, val / test / ext117, --code el_hc      [GPU, 3 gates]
#   5  tau0 check: tau0 cells == default cells, step 20000, code_revision c2e6973, cell counts 54 / 50 / 106   [CPU]
#   6  LA tau 0 / 1 (rescore_logit_adjust ec315d2e = PF2's), test + val, --check vs the rescore JSONs       [GPU, gate]
#   7  E1 co-primaries: hc_e1_coprim.py --selftest, then the scorer (relF1@2 + inactive IoU, rule 1 vs SUPPF)   [CPU; decision pass]
#   8  20k encoder cosines vs ImageNet R34 (enc_cosine d3bc7a70)                   [CPU; reported, non-fatal]
#   9  frozen extra passes: FROZEN.md5 entries post_extra/*.sh (hc_b5.sh: B5 + cell-level via calib's frozen hook, as thin_b5.sh;
#      hc_scuffign.sh: scuff-ignored test, PF2's pf2_scuffign.py with --code el_hc)   [GPU, gate per hook; reported, non-fatal]
#  10  SHV1 / SHV1-p mechanism + shared val / rf dumps: hc_shv1.sh (CPU fp32)       [CPU; decision pass]
#  11  F51 harm guard: hc_f51.py --selftest, then the guard (a8_screen_score AP + module bootstrap)   [CPU; decision pass]
#  12  MANIFEST.md5 of post/
# Decision passes (7, 10, 11) are non-aborting: rc in post/decision_rc.txt, the opening continues to the MANIFEST and ends rc 1 if any
# failed. Reported passes: rc in post/extra_rc.txt. Core passes (0-6) abort the opening (set -e) with rc 1.
# ONE end line in /home/noob/work/nq/post.log: "[<date>] nq scoring done: post rc=<rc>" (rc captured before $(date); nq_gpumem.sh stops
# 60 s later). rc 2 = refused before any pass (GS < 9,900 or post/ exists). Python PIDs in el_hc/reports/hc/post_pids.txt (gate passes
# are recorded too); to stop: the python PID first, then the post subshell, then this script; the end line then carries rc != 0.
set -u
cd /home/noob/work/el_hc || exit 1
. /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
H=/home/noob/work/nq/hc; NL=/home/noob/work/nq/post.log; DEPLOY=c2e6973
OUT=/home/noob/work/el_hc/reports/hc/post; PIDS=/home/noob/work/el_hc/reports/hc/post_pids.txt; W=/home/noob/work/el_hc/reports/hc/syn_work
GS=${GS:?set GS (scoring gate MiB, >= 9900)}
P=/home/noob/work/el-fault-detection/.venv/bin/python; F1=/home/noob/work/el_f1/reports/f1; X1=$F1/ext117; S0=$F1/smoke_v1/mim_step0.pth
PF=/home/noob/work/el_f3/reports/pf2/post; CTX=/home/noob/work/el_f3/reports/d/e1_context.tsv; ENC=/home/noob/work/el_f3/reports/enc_cosine.py
REF=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml; EXP=/home/noob/work/nq/exp_HC.txt
RUNS=$(for k in 5 6 7 8 9; do echo hc_HC_100pct_s$k; done); CMP=$(for k in 5 6 7 8 9; do echo pf2_SUPPF_100pct_s$k; done)
REQ="hc_postwatch.sh hc_post.sh hc_e1_coprim.py hc_shv1.sh hc_shv1_read.py hc_f51.py hc_copies.md5 calib_syn/calib_dump.py calib_syn/el_metrics.py
     found/a8_screen_score.py trackM/m0_analyze.py thin/thin_e1_relf1.py post_extra/hc_b5.sh post_extra/hc_scuffign.sh post_extra/pf2_scuffign.py
     post_extra/calib/calib_dump.py post_extra/calib/el_metrics.py post_extra/calib/pf2_b5_hook.sh post_extra/calib/pf2_b5_pooled.sh"
CPU=(env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 nice -n 19)
GPU=(env HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1)
# prun LABEL LOG CMD...: one process in the background, PID recorded (env / nice exec, so it is python's PID), waited for; returns its rc
prun(){ local lab=$1 log=$2 pp; shift 2; "$@" > "$log" 2>&1 & pp=$!; echo "$(date '+%F %T') $pp $lab" >> $PIDS; wait $pp; }
fail(){ echo "[$(date)] FAIL: $*" >&2; exit 1; }   # stderr: reaches post.log even inside a stdout-redirected loop

frozen_ok(){  # coach's FROZEN.md5 lists every REQ file and md5sum -c passes; the third-party copies equal their originals
  local f; [ -s $H/FROZEN.md5 ] || { echo "no $H/FROZEN.md5"; return 1; }
  for f in $REQ; do grep -qE "^[0-9a-f]{32}  (\./)?$f\$" $H/FROZEN.md5 || { echo "FROZEN.md5 does not list $f"; return 1; }; done
  (cd $H && md5sum -c --quiet FROZEN.md5) || { echo "FROZEN.md5 check failed"; return 1; }
  (cd $H && md5sum -c --quiet hc_copies.md5) || { echo "hc_copies.md5 check failed"; return 1; }
}

e1pass(){  # decision pass 7 (set -e is off inside: explicit returns)
  local f=() k
  for k in 5 6 7 8 9; do f+=($PF/m0/pf2_SUPPF_100pct_s$k.json $OUT/m0/hc_HC_100pct_s$k.json); done
  prun e1_selftest $OUT/e1_coprim_selftest.txt "${CPU[@]}" $P $H/hc_e1_coprim.py --selftest "${f[@]}" --trackm $H/trackM --thin $H/thin/thin_e1_relf1.py || return 1
  prun e1_coprim $OUT/e1_coprim.txt "${CPU[@]}" $P $H/hc_e1_coprim.py --arm SUPPF $PF/m0 pf2 --arm HC $OUT/m0 hc --rev SUPPF e544133 \
    --rev HC $DEPLOY --base SUPPF --trackm $H/trackM --ctx $CTX --json $OUT/e1_coprim.json
}

f51pass(){  # decision pass 11
  [ -e $W/DUMPS_OK ] || { echo "no complete val / rf dumps + records (hc_shv1 passes 1-2)"; return 2; }
  mkdir -p $OUT/f51 || return 2
  prun f51_selftest $OUT/f51/hc_f51_selftest.txt "${CPU[@]}" $P $H/hc_f51.py --selftest --a8 $H/found/a8_screen_score.py --el-metrics $H/calib_syn || return 1
  prun f51 $OUT/f51/hc_f51.txt "${CPU[@]}" $P $H/hc_f51.py --a8 $H/found/a8_screen_score.py --el-metrics $H/calib_syn --dump $W/dump --rec $W/rec \
    --hc $RUNS --base $CMP --code /home/noob/work/el_hc --rf /home/noob/work/calib/data/rf --rf-sets /home/noob/work/found/t9/rf_sets.tsv \
    --boot 2000 --out $OUT/f51/hc_f51.json
}

post(){
  set -e
  DF=0
  dpass(){ local lab=$1 xrc=0; shift; "$@" || xrc=$?; echo "$lab rc=$xrc" >> $OUT/decision_rc.txt; [ $xrc = 0 ] || DF=$((DF + 1)); }
  spass(){ local lab=$1 xrc=0; shift; "$@" || xrc=$?; echo "$lab rc=$xrc" >> $OUT/extra_rc.txt; }
  # ---- 0. integrity ----
  [ "$(git rev-parse --short=7 HEAD)" = $DEPLOY ] || fail "HEAD != $DEPLOY"
  [ "$(cat reports/hc/DEPLOY)" = $DEPLOY ] || fail "reports/hc/DEPLOY != $DEPLOY"
  [ "$(cat REVISION 2>/dev/null)" = $DEPLOY ] || fail "el_hc/REVISION != $DEPLOY (hc_postwatch writes it at arming)"
  [ -z "$(git status --short --untracked-files=no)" ] || fail "tracked changes in el_hc"
  frozen_ok || fail "frozen scorer files"
  cp -p $H/FROZEN.md5 $OUT/FROZEN_hc.md5
  (cd $PF && md5sum -c --quiet MANIFEST.md5) || fail "PF2 comparator files changed (MANIFEST)"
  echo "PF2 comparator files unchanged (MANIFEST $(md5sum < $PF/MANIFEST.md5 | cut -c1-8), $(wc -l < $PF/MANIFEST.md5) files)" > $OUT/comparator_check.txt
  printf '%s\n' \
    "d36f7438d0fefb0ffc926c69f6c6af2d  $F1/m0_audit.py" \
    "d77241bbe2845cabc2779adc827eb838  $F1/m0_audit_tau.py" \
    "1e41202b99611169030abc5d2524f72c  /home/noob/work/el_hc/scripts/rescore_label_versions.py" \
    "ec315d2e8c3e3015cb31a1fc3675ddd5  /home/noob/work/el_hc/scripts/rescore_logit_adjust.py" \
    "d3bc7a708d3630de7322fc6dd2ff403e  $ENC" \
    "178b872d35d15689f6ab38bf57789327  $S0" \
    "00fabfddaf7d7dfd11e25008f94f744d  /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh" \
    "4e7ff5667feec6c8ca239343833c224b  /home/noob/work/el_f3/reports/pf2/post_extra/B5_DEVICE" \
    "3827f7c08e653ae5a2164093b242b3b6  $PF/MANIFEST.md5" \
    "12bd138523fccfc6be5b41df35d19147  $CTX" \
    "5266806b559f74bcf9eae167bb076b95  $X1/stems_eval.txt" \
    "14771356ef7c99f567c5f80dad2e48dd  /home/noob/work/found/t9/rf_sets.tsv" \
    "3a65c2fb0ecaf32e91377d4ad249029a  /home/noob/work/calib/data/rf/stems_eval.txt" \
    "9dcccf00662dfca750f0b46628f8d5bb  /home/noob/work/el_hc/data/splits/val.txt" \
    "a31fad14fa27ee28e2a2319b8976aba3  /home/noob/work/el_hc/data/splits/test.txt" \
    "01008fdfd25c3e0a70b0102d2f72b2bc  $EXP" > $OUT/scorer_md5_expected.txt
  md5sum -c $OUT/scorer_md5_expected.txt > $OUT/scorer_md5.txt 2>&1 || fail "external scorer / data md5 (scorer_md5.txt)"
  [ "$(readlink -f data/escdd_masks)" = "$(readlink -f /home/noob/work/el_f3/data/escdd_masks)" ] \
    || fail "el_hc and el_f3 score against different escdd_masks"
  echo "protocol_HC v1.1 opening = E1 opening #3; deploy $DEPLOY; GS $GS; runs $(echo $RUNS); comparator $(echo $CMP) (PF2 opening files)" > $OUT/post_settings.txt
  # ---- 1. completeness (the one stdout grep) ----
  for r in $RUNS; do grep -q "step 20000/20000" experiments/$r.stdout || fail "INCOMPLETE $r"; done
  # ---- 2. config record (config_used.yaml only; as nq cfgcheck) ----
  for r in $RUNS; do
    c=experiments/$r/config_used.yaml; k=${r##*_s}
    d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' $REF) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
    [ "$d" = "$(sort $EXP)" ] && grep -qx "seed: $k" $c || fail "config of $r differs from pf2_SUPPF_100pct_s5 + exp_HC.txt"
    echo "$r: config diff vs pf2_SUPPF_100pct_s5 = exp_HC.txt (01008fdf), seed $k; $(md5sum < experiments/$r/checkpoints/latest.pth | cut -c1-32) latest.pth"
  done > $OUT/init_check.txt
  # ---- 3. rescore_label_versions per run [GPU] ----
  for r in $RUNS; do
    gate_wait $GS "hc post rescore $r"
    prun rescore_$r $OUT/rescore/$r.log "${GPU[@]}" $P scripts/rescore_label_versions.py --runs $r --out $OUT/rescore/$r.json; done
  # ---- 4. m0_audit default + tau 0 / 1 [GPU] ----
  RD=$(for r in $RUNS; do echo /home/noob/work/el_hc/experiments/$r; done)
  gate_wait $GS "hc post m0"
  prun m0 $OUT/m0_audit.log "${GPU[@]}" $P $F1/m0_audit.py --code /home/noob/work/el_hc --out $OUT/m0 --ext $X1 --no-logits --runs $RD
  for T in 0 1; do
    gate_wait $GS "hc post m0 tau$T"
    prun m0_tau$T $OUT/m0_audit_tau$T.log "${GPU[@]}" $P $F1/m0_audit_tau.py --code /home/noob/work/el_hc --out $OUT/m0 --ext $X1 --no-logits --tau $T --runs $RD
  done
  # ---- 5. tau0 check [CPU] ----
  "${CPU[@]}" $P - "$OUT" "$DEPLOY" $RUNS > $OUT/tau0_check.txt <<'PY'
import json, sys
o, dep, runs = sys.argv[1], sys.argv[2], sys.argv[3:]
J = {r: json.load(open(f"{o}/m0/{r}.json")) for r in runs}
bad = [r for r in runs if J[r]["cells"] != json.load(open(f"{o}/m0/{r}.tau0.json"))["cells"]]
assert all(J[r]["step"] == 20000 and J[r]["code_revision"] == dep for r in runs), {r: (J[r]["step"], J[r]["code_revision"]) for r in runs}
n = {r: {k: len(v) for k, v in J[r]["cells"].items()} for r in runs}
assert all(n[r]["val"] == 54 and n[r]["test"] == 50 and n[r]["ext"] == 106 for r in runs), n
assert not bad, bad
print("tau0 == default cells for all runs: True | step 20000 and code_revision", dep, "for all", len(runs), "| cells per set", n[runs[0]])
PY
  # ---- 6. LA tau 0 / 1 [GPU] ----
  gate_wait $GS "hc post LA"
  prun la $OUT/la.log "${GPU[@]}" $P scripts/rescore_logit_adjust.py --runs $RUNS --taus 0 1 --splits test val --out $OUT/la.json --check $OUT/rescore
  # ---- 7. E1 co-primaries [CPU; decision] ----
  dpass e1_coprim e1pass
  # ---- 8. 20k encoder cosines [CPU; reported] ----
  PAIRS=(); for r in $RUNS; do PAIRS+=(--pair "$r vs ImageNet" $S0 experiments/$r/checkpoints/latest.pth); done
  spass enc_cosine prun enc_cosine $OUT/enc_cosine_20k.txt env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1 nice -n 19 \
    $P $ENC --out $OUT/enc_cosine_20k.json "${PAIRS[@]}"
  # ---- 9. frozen extra passes [GPU; reported] ----
  for s in $(awk '{print $2}' $H/FROZEN.md5 | sed 's#^\./##' | grep -E '^post_extra/[^/]+\.sh$'); do
    gate_wait $GS "hc post extra $s"
    xrc=0; OUT=$OUT RUNS="$RUNS" GS=$GS bash $H/$s > $OUT/extra_$(basename $s .sh).log 2>&1 || xrc=$?
    echo "extra $s rc=$xrc" >> $OUT/extra_rc.txt
  done
  # ---- 10. SHV1 mechanism + shared dumps [CPU; decision] ----
  dpass shv1 prun hc_shv1 $OUT/hc_shv1.stdout env OUT=$OUT bash $H/hc_shv1.sh
  # ---- 11. F51 harm guard [CPU; decision] ----
  dpass f51 f51pass
  # ---- 12. MANIFEST ----
  (cd $OUT && find . -type f ! -name MANIFEST.md5 -print0 | sort -z | xargs -0 md5sum > MANIFEST.md5)
  echo "[$(date)] decision passes failed: $DF (decision_rc.txt)"
  [ $DF = 0 ]
}

pre(){ [ "$GS" -ge 9900 ] 2>/dev/null || { echo "refused: GS '$GS' < 9900"; return 2; }
       [ ! -e $OUT ] || { echo "refused: $OUT exists (a rerun needs coach's word and a fresh dir)"; return 2; }
       mkdir -p $OUT/m0 $OUT/rescore; }
touch $GG/FAST   # 1 s gpumem samples for the whole opening
if pre >> /home/noob/work/el_hc/reports/hc/post_pre.log 2>&1; then
  ( post ) > $OUT.log 2>&1
  rc=$?
else
  rc=2
fi
rm -f $GG/FAST
echo "[$(date)] nq scoring done: post rc=$rc" >> $NL
