#!/bin/bash
# SKR2C opening (protocol_SKR2C §3a.2 co-primary, §6), pass 10a = s2_b5w.sh c4472057 with: settings s2c_settings.sh; BOTH arms (SKR01,
# SUPPF; seeds 10-14) through the frozen hook + the wide steps (no comparator reuse); the 'SUPPF remade from PF2 dumps' block and its
# 'ops' check vs PF2 removed; table with --old for both arms; labels. Original header follows.
# SKR2 + HC2 opening, pass 10a: B5 on the WIDER grid (protocol_SKR2_HC2 v1.0.1 §3a.2 co-primary for SKR2, §4 reported for HC2, §6).
# s2_post.sh runs it with GS set; rc -> decision_rc.txt. DRAFT (runner's helper, 2 Nov 2026) for coach's FREEZE.
# From hc_b5.sh (9167911e, frozen HC hook) + calib's frozen pf2_b5_hook.sh (e06dfc5f) / pf2_b5_pooled.sh (873591ff): the frozen hook and
# pooled script are CALLED UNCHANGED (copies in open/post_extra/calib/); the wide-grid steps repeat their records / summary / pooled
# command lines with el_metrics_w (calib_w/el_metrics_w.py = 6e73ff11 with GRID / OPGRID -8.0 .. +12.0; nothing else changed).
# Per new run (10; ONE gate per run, before the hook's only GPU process, the dump):
#   (1) pf2_b5_hook.sh $PROTO <arm worktree> post/m0/<arm> WK/b5/<arm> calib RUN: calib_dump c172717e val / test / ext (--opening,
#       DEVICE from PF2's B5_DEVICE, one setting for all runs), 6e73ff11 records with the b = 0 self-check vs this opening's m0 (written
#       only on PASS), 6e73ff11 summaries;
#   (2) el_metrics_w records from the SAME dumps (self-check vs m0, same tol profile) -> WK/b5/<arm>/rec_w;
#   (3) s2_b5w_check.py records: on -4..+12 (+0.75) the wide records equal the 6e73ff11 records exactly;
#   (4) wide per-run summaries (test, ext, test_clean) -> sum_w.
# Per arm: pf2_b5_pooled.sh unchanged (6e73ff11 pooled OP, reported) and the wide pooled summaries (the SKR2 co-primary OP).
# SUPPF (no model is run): PF2's b5_work dumps (md5 vs PF2 post/b5/dump_md5_on_gaint.txt, again) -> el_metrics_w records (--code el_f3,
#   self-check vs PF2's m0) -> sub-grid check vs PF2's frozen records (post/b5/rec) -> wide summaries + pooled -> s2_b5w_check.py ops:
#   SUPPF's wide OPs must equal PF2's frozen OPs (judge).
# Then s2_b5w_check.py table -> post/b5/b5w_table.{txt,json}. Copies (rec / rec_w / sum / sum_w JSONs + self-check txt + logs, dump md5
# lists) into post/b5/<arm>/. Work dir WK/b5 is OUTSIDE post/ (dumps stay on gaint). CPU steps: nice 19, CUDA hidden, 1 thread x 8 procs.
# exit 0 iff every step passed (each failure counted in F; later steps still run where their inputs exist).
set -u
. /home/noob/work/s2c/open/s2c_settings.sh || exit 2
. $GATE_SH
GS=${GS:?}; X=$OPEN/post_extra; CW=$OPEN/calib_w/el_metrics_w.py; CHK=$OPEN/s2_b5w_check.py; B=$WK/b5; OB=$S2_OUT/b5; F=0
m=$(settings_check) || { echo "settings: $m"; exit 2; }
[ "$(md5sum < $CW | cut -c1-32)" = 45b1df03a8fb2959272534b2ab6b237f ] || { echo "el_metrics_w md5 != 45b1df03 (draft value; coach's FROZEN.md5 is the authority)"; exit 2; }
DEVICE=$(cat $B5_DEVICE_FILE 2>/dev/null)
case "$DEVICE" in cuda) TP=exact;; cpu) TP=cpu;; *) echo "B5_DEVICE missing or invalid ('$DEVICE'): B5 not run"; exit 2;; esac
export DEVICE
CPUE=(env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 nice -n 19)
echo "[$(date)] B5 wide: DEVICE=$DEVICE (PF2's mechanical decision; tol profile $TP) for the 10 fresh runs (SKR01 + SUPPF, s10-14)"
mkdir -p $B $OB

wrec(){  # ARM CODE DUMPDIR M0DIR RUN: el_metrics_w records of val / test / ext with the b = 0 self-check (as pf2_b5_hook.sh l.65-69)
  local a=$1 code=$2 dd=$3 m0=$4 r=$5 S rc bad=0; mkdir -p $B/$a/rec_w
  for S in val test ext; do
    "${CPUE[@]}" $P $CW records --dump $dd/$r.$S.npz --set $S --code $code --out $B/$a/rec_w/$r.$S.json --m0 $m0/$r.json --m0-set $S \
      --tol-profile $TP --procs 8 >> $B/$a/b5w.log 2>&1
    rc=$?; echo "[$(date)] b5w records+selfcheck $r $S rc=$rc" >> $B/$a/b5w.log; [ $rc = 0 ] || bad=1
  done; return $bad; }
wchk(){  # ARM OLDRECDIR RUN: sub-grid equality, the 3 sets
  local a=$1 od=$2 r=$3
  "${CPUE[@]}" $P $CHK records --pair $B/$a/rec_w/$r.val.json $od/$r.val.json --pair $B/$a/rec_w/$r.test.json $od/$r.test.json \
    --pair $B/$a/rec_w/$r.ext.json $od/$r.ext.json >> $B/$a/subgrid_check.txt 2>&1; }
wsum(){  # ARM RUN: per-run wide summaries (as pf2_b5_hook.sh l.71-78)
  local a=$1 r=$2 S rc bad=0; mkdir -p $B/$a/sum_w
  for S in test ext; do
    "${CPUE[@]}" $P $CW summary --val $B/$a/rec_w/$r.val.json --target $B/$a/rec_w/$r.$S.json --deployed-b 0 --out $B/$a/sum_w/$r.$S.json >> $B/$a/b5w.log 2>&1
    rc=$?; echo "[$(date)] b5w summary $r $S rc=$rc" >> $B/$a/b5w.log; [ $rc = 0 ] || bad=1
  done
  "${CPUE[@]}" $P $CW summary --val $B/$a/rec_w/$r.val.json --target $B/$a/rec_w/$r.test.json --deployed-b 0 --exclude CSIR_00070_r8_c4 \
    --out $B/$a/sum_w/$r.test_clean.json >> $B/$a/b5w.log 2>&1
  rc=$?; echo "[$(date)] b5w summary $r test_clean rc=$rc" >> $B/$a/b5w.log; [ $rc = 0 ] || bad=1
  return $bad; }
wpool(){  # ARM RUN x5: wide arm-pooled summaries (as pf2_b5_pooled.sh l.13-23)
  local a=$1 S N rc bad=0 PV=(); shift
  for N in "$@"; do PV+=("$B/$a/rec_w/$N.val.json"); done
  for N in "$@"; do
    for S in test ext; do
      "${CPUE[@]}" $P $CW summary --val $B/$a/rec_w/$N.val.json --pooled-val "${PV[@]}" --target $B/$a/rec_w/$N.$S.json --deployed-b 0 \
        --out $B/$a/sum_w/$N.$S.pooled.json >> $B/$a/b5w.log 2>&1
      rc=$?; echo "[$(date)] b5w pooled summary $N $S rc=$rc" >> $B/$a/b5w.log; [ $rc = 0 ] || bad=1
    done
    "${CPUE[@]}" $P $CW summary --val $B/$a/rec_w/$N.val.json --pooled-val "${PV[@]}" --target $B/$a/rec_w/$N.test.json --deployed-b 0 \
      --exclude CSIR_00070_r8_c4 --out $B/$a/sum_w/$N.test_clean.pooled.json >> $B/$a/b5w.log 2>&1
    rc=$?; echo "[$(date)] b5w pooled summary $N test_clean rc=$rc" >> $B/$a/b5w.log; [ $rc = 0 ] || bad=1
  done; return $bad; }

# ---- new runs: frozen hook (dump + 6e73ff11) then the wide steps ----
for a in SKR01 SUPPF; do
  w=$(wt_of $a); mkdir -p $B/$a
  for r in $(runs_of $a); do
    gate_wait $GS "s2c post b5 $r"
    bash $X/calib/pf2_b5_hook.sh $PROTO $w $S2_OUT/m0/$a $B/$a $X/calib $w/experiments/$r || F=$((F + 1))
    echo "[$(date)] b5 frozen hook $r done (fails so far $F)"
    ok=1; for S in val test ext; do [ -s $B/$a/dump/$r.$S.npz ] || ok=0; done
    if [ $ok = 1 ]; then
      wrec $a $w $B/$a/dump $S2_OUT/m0/$a $r || F=$((F + 1))
      wchk $a $B/$a/rec $r || F=$((F + 1))
      wsum $a $r || F=$((F + 1))
    else F=$((F + 1)); echo "[$(date)] b5 $r: dump missing, wide steps skipped"; fi
    echo "[$(date)] b5w $r done (fails so far $F)"
  done
  bash $X/calib/pf2_b5_pooled.sh $B/$a $X/calib $(runs_of $a) || F=$((F + 1))
  wpool $a $(runs_of $a) || F=$((F + 1))
  echo "[$(date)] b5 pooled $a (6e73ff11 + wide) done (fails so far $F)"
done

# ---- table + copies ----
"${CPUE[@]}" $P $CHK table --arm SUPPF $B/SUPPF/sum_w $SUP_RUNS --arm SKR01 $B/SKR01/sum_w $SKR_RUNS \
  --base SUPPF --coprim SKR01 --old SKR01 $B/SKR01/sum --old SUPPF $B/SUPPF/sum --json $OB/b5w_table.json > $OB/b5w_table.txt 2>&1 || F=$((F + 1))
for a in SKR01 SUPPF; do
  mkdir -p $OB/$a
  for d in rec rec_w sum sum_w; do
    [ -d $B/$a/$d ] || continue; mkdir -p $OB/$a/$d
    cp -p $B/$a/$d/*.json $OB/$a/$d/ 2>/dev/null; cp -p $B/$a/$d/*.selfcheck.txt $OB/$a/$d/ 2>/dev/null
  done
  cp -p $B/$a/*.log $B/$a/*.txt $OB/$a/ 2>/dev/null
  [ -d $B/$a/dump ] && (cd $B/$a/dump && md5sum *.npz) > $OB/$a/dump_md5_on_gaint.txt
done
echo "[$(date)] s2c_b5w done: fails $F"
[ $F = 0 ]
