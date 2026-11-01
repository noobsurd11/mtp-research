#!/bin/bash
# runner DRAFT (1 Nov 2026, written by a helper agent; coach reviews and FREEZES it before any screen run is scored, protocol_A8screen
# §10 launch-order ruling): scoring of the A8 screen (protocol_A8screen v1.1: §3 GO rule, §9 lock record, §10 data.root) on gaint,
# after all 4 screen runs trained rc 0 through runner's nq queue (scripts/next/nq_queue.sh).
# Device: CPU fp32 for ALL 4 runs (CUDA hidden, nice 19, <= 8 threads); no GPU gate, no GPU memory (reasons: build_a8_runner.md).
# Reads: val 54 (el_f8 data/splits/val.txt 9dcccf00 = a8_root's val), Hanifi _rf 106 (F51 51 + H36 36 + F19 19 per rf_sets.tsv
# 14771356), the 4 run dirs (config_used.yaml, checkpoints/latest.pth), the 2 backbone weights files, runner's nq launch.log.
# NO test cell, NO E1 cell: dumps --sets val rf only (no --opening, no ext); records --set val | rf only; no training .stdout read.
# Passes (a pre-check failure aborts with nothing computed):
#   0 static checks: coach's FROZEN.md5 (lists this file), md5 of every scorer / data list / weights file, the 4k dumper = calib_dump
#     c172717e + one line, el_f8 HEAD c280e8c2 = REVISION_f8 with 0 tracked changes, a8_root (SPLITS.md5, test.txt == val.txt);
#     start condition (launch.log 'trained <run> rc=0' for all 4, then 'config OK <run>' for all 4); per-run config_used.yaml
#     (data.root a8_root, seed, total_steps 4000, the arm's model keys); latest.pth + config md5s recorded
#   1 a8_screen_score --selftest (synthetic; reads no data)
#   2 per run: a8_calib_dump_4k.py (calib_dump c172717e with the step assert 4000) --sets val rf -> work/dump/<run>.{val,rf}.npz
#   3 per run x {val, rf}: el_metrics 6e73ff11 records (no m0 JSON exists for screen runs: SELFCHECK UNCHECKED) -> out/rec/
#  3b per run (coach): val records at b = 0 (el_metrics.curves) vs metrics.json val_history[-1] (step 4000), crack IoU and inactive
#     IoU |delta| <= 0.005, reads only val_history -> out/a8_dump_integrity.txt; any failure stops before pass 5 (rc 1)
#   4 per run: a8_init_dump.py (step-0 reference) -> work/init/; enc_cosine_hr.py d72f4324 per arm (--backbone = the arm's timm
#     name) -> out/enc_cosine_4k_<arm>.{json,txt}; validity: every run stage2 and stage3 cos_w >= 0.5 -> out/a8_validity.txt
#   5 a8_screen_score 8eba76e5 on seed means, --el-metrics = the frozen el_metrics 6e73ff11 copy (calib's OP grid, protocol_PF2
#     §4.1; NOT its default found/t9 46b682cc) -> out/a8_screen_score.{json,stdout}
#   6 out/a8_summary.txt (mechanical; coach recomputes), md5 lists, inputs re-checked, out/MANIFEST.md5
# Log $O/a8_score.log; exactly one end line "a8 scoring done: rc=N" (EXIT trap; rc captured before $(date); MODE=check: "a8 check done").
# rc: 0 all passes OK | 1 a scoring pass failed | 2 a pre-check failed (nothing scored) | 3 a screen run not trained rc 0, or not
#     all 4 trained within MAXH h (nothing scored) | 143 stopped by signal.
# Run it in tmux; script PID in $O/a8_score.pid, every python PID in $O/pids.txt (to stop: the python PID first, then the script).
# $O/HOLD (runner-declared CPU window) pauses before each python pass. Outputs to pull: $O/out/ (~10 MB) + $O/a8_score.log.
# Usage: bash /home/noob/work/a8_score/scripts/a8_score.sh            MODE=wait (default): polls launch.log every 60 s, MAXH 72
#        MODE=now   bash .../a8_score.sh                              one check of the start condition
#        MODE=check bash .../a8_score.sh                              static checks only (for coach's freeze); OUT default .../check
set -u
A=/home/noob/work/a8_score; S=$A/scripts; MODE=${MODE:-wait}; MAXH=${MAXH:-72}
[ "$MODE" = check ] && O=${OUT:-$A/check} || O=${OUT:-$A/v1}
LOG=$O/a8_score.log
W=/home/noob/work/el_f8; E=$W/experiments; R8=/home/noob/work/a8_root; RF=/home/noob/work/calib/data/rf
NQ=/home/noob/work/nq/launch.log; P=/home/noob/work/el-fault-detection/.venv/bin/python
CAL=/home/noob/work/el_f3/reports/pf2/post_extra/calib
WA8=/home/noob/work/weights/dinov3_convnext_tiny_lvd1689m_timm.safetensors
WA8C=/home/noob/.cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth
HEAD8=c280e8c2f5cec2fd3ed38eb4ea010da7e6966dde
RUNS="f8_A8_4k_s0 f8_A8_4k_s1 f8_A8c_4k_s0 f8_A8c_4k_s1"
case "$MODE" in wait|now|check) ;; *) echo "MODE must be wait, now or check" >&2; exit 2;; esac
[ -e "$LOG" ] && { echo "refused: $LOG exists (a rerun needs a fresh OUT=..., on coach's word)" >&2; exit 2; }
mkdir -p $O/frozen $O/work/dump $O/work/init $O/out/rec || exit 2
fin(){ rc=$?; [ "$MODE" = check ] && w=check || w=scoring; echo "[$(date)] a8 $w done: rc=$rc" >> $LOG; }
trap fin EXIT
trap 'exit 143' TERM INT HUP
echo $$ > $O/a8_score.pid
export CUDA_VISIBLE_DEVICES="" HF_HUB_OFFLINE=1 OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
F=0
log(){ echo "[$(date)] $*" >> $LOG; }
die(){ log "PRE-CHECK FAIL: $*; NOT scored"; exit 2; }
hold(){ [ -e $O/HOLD ] && log "HOLD file seen; waiting"; while [ -e $O/HOLD ]; do sleep 60; done; }
# run TAG OUTFILE CMD...: one python pass at nice 19, PID recorded, waited for; returns its exit status
run(){ local tag=$1 out=$2 pp; shift 2
  hold
  nice -n 19 "$@" >> "$out" 2>&1 &
  pp=$!; echo "$(date '+%F %T') $pp $tag" >> $O/pids.txt
  wait $pp; }
log "a8_score start: pid $$ MODE=$MODE OUT=$O; script md5 $(md5sum < "$0" | cut -c1-32); CPU fp32, CUDA hidden, nice 19, 8 threads"

# ---- 0. static checks (fail fast, again right before scoring) ----
static(){
  [ -s $S/FROZEN.md5 ] && grep -qE '  (\./)?a8_score\.sh$' $S/FROZEN.md5 && (cd $S && md5sum -c --quiet FROZEN.md5) >> $LOG 2>&1 \
    || die "coach's $S/FROZEN.md5 missing, without a8_score.sh, or mismatched"
  printf '%s\n' \
    "12e4818ea6e172e4332fa34f3fc3446b  $S/a8_calib_dump_4k.py" \
    "87923f8e395856cdf2eb4abe13145051  $S/a8_init_dump.py" \
    "c172717e5989edb8e0b7b312096f9180  $CAL/calib_dump.py" \
    "6e73ff11aaa6171a52b5a5404877ab46  $CAL/el_metrics.py" \
    "8eba76e5bb0783e9d4ecc432dea4a785  /home/noob/work/found/p8/a8_screen_score.py" \
    "14771356ef7c99f567c5f80dad2e48dd  /home/noob/work/found/t9/rf_sets.tsv" \
    "d72f4324cb0417a211025cf0f18b2465  $W/reports/enc_cosine_hr.py" \
    "42c3980d9ea6bdc27cda818c1f554b9d  $W/src/models/hrstem_unetpp.py" \
    "9cd345b80a1e15d371e03ea30d12b0bd  $W/src/models/model_factory.py" \
    "9dcccf00662dfca750f0b46628f8d5bb  $W/data/splits/val.txt" \
    "0880d3e0257bced258e3102f0e6b3348  $R8/SPLITS.md5" \
    "3a65c2fb0ecaf32e91377d4ad249029a  $RF/stems_eval.txt" \
    "abf904631bf1ba23642e60c46b20dc5e  $WA8" \
    "fcc1480a11e933010f4d7e0ccb7e33b1  $WA8C" > $O/expected_md5.txt
  md5sum -c $O/expected_md5.txt >> $LOG 2>&1 || die "md5 check (lines marked FAILED above)"
  [ "$(diff $CAL/calib_dump.py $S/a8_calib_dump_4k.py | grep -c '^[<>]')" = 2 ] \
    && diff $CAL/calib_dump.py $S/a8_calib_dump_4k.py | grep -q '^> .*== 4000, run' || die "a8_calib_dump_4k.py != calib_dump c172717e + the l.54 step line"
  [ "$(git -C $W rev-parse HEAD)" = $HEAD8 ] && [ "$(cat $W/REVISION_f8)" = $HEAD8 ] \
    && [ -z "$(git -C $W status --short --untracked-files=no)" ] || die "el_f8 HEAD / REVISION_f8 != c280e8c2, or tracked changes"
  (cd $R8 && md5sum -c --quiet SPLITS.md5) && cmp -s $R8/splits/test.txt $R8/splits/val.txt \
    && cmp -s $R8/splits/val.txt $W/data/splits/val.txt && [ "$(readlink -f $R8/labeled)" = "$(readlink -f $W/data/labeled)" ] \
    || die "a8_root (SPLITS.md5 / test.txt == val.txt == el_f8 val.txt / labeled link)"
  [ "$(wc -l < $RF/stems_eval.txt)" = 106 ] && [ "$(wc -l < $W/data/splits/val.txt)" = 54 ] || die "set sizes (rf 106, val 54)"
}
static
log "static checks OK (FROZEN.md5, $(wc -l < $O/expected_md5.txt) md5s, 4k dumper diff, el_f8 $HEAD8, a8_root)"
log "env: $($P -c 'import torch, timm, numpy, scipy, sys; print(sys.version.split()[0], torch.__version__, timm.__version__, numpy.__version__, scipy.__version__)' 2>&1 | tail -1)"
[ "$MODE" = check ] && exit 0

# ---- 0b. start condition: all 4 screen runs trained rc 0 and config OK (runner's nq launch.log) ----
st(){ grep -E "trained $1 rc=[0-9]+$" $NQ 2>/dev/null | tail -1 | sed -E 's/.* rc=([0-9]+)$/\1/'; }
t0=$(date +%s)
while :; do
  n=0; bad=""
  for r in $RUNS; do v=$(st $r); [ -n "$v" ] && n=$((n + 1)); [ -n "$v" ] && [ "$v" != 0 ] && bad="$bad $r:rc=$v"; done
  [ -n "$bad" ] && { log "start condition FAIL:$bad; NOT scored (decision needed)"; exit 3; }
  [ $n = 4 ] && break
  [ "$MODE" = now ] && { log "start condition not met ($n/4 trained); NOT scored"; exit 3; }
  [ $(( $(date +%s) - t0 )) -ge $(( MAXH * 3600 )) ] && { log "start condition not met within ${MAXH} h ($n/4 trained); NOT scored"; exit 3; }
  sleep 60
done
for r in $RUNS; do grep -q "config OK $r vs " $NQ || die "no 'config OK $r' line in $NQ"; done
log "start condition met: 4/4 'trained rc=0', 4/4 'config OK' in $NQ"
static
# per-run config_used.yaml (config file, not a log): value of KEY in top-level SECTION (block-style YAML, as nq cfgcheck assumes)
yv(){ awk -v s="$1:" -v k="  $2: " '$0 == s {f = 1; next} /^[^ ]/ {f = 0} f && index($0, k) == 1 {print $2; exit}' "$3"; }
for r in $RUNS; do
  c=$E/$r/config_used.yaml; ck=$E/$r/checkpoints/latest.pth
  [ -s $c ] && [ -s $ck ] || die "$r: config_used.yaml or checkpoints/latest.pth missing"
  case $r in f8_A8_4k_*) bb=convnext_tiny.dinov3_lvd1689m; bw=$WA8; bf=timm;; f8_A8c_4k_*) bb=convnext_tiny; bw=$WA8C; bf=torchvision_convnext;; esac
  got="$(yv data root $c) $(awk '/^seed: / {print $2; exit}' $c) $(yv training total_steps $c) $(yv model name $c) $(yv model backbone $c) $(yv model backbone_weights $c) $(yv model backbone_weights_format $c) $(yv model backbone_drop_path $c)"
  exp="$R8 ${r##*_s} 4000 hrstem_unetpp $bb $bw $bf 0.0"
  [ "$got" = "$exp" ] || die "$r config_used.yaml: got [$got], expected [$exp]"
done
(for r in $RUNS; do md5sum $E/$r/checkpoints/latest.pth $E/$r/config_used.yaml; done) > $O/out/inputs_md5.txt || die "input md5s"
log "per-run configs OK (data.root $R8, seed, total_steps 4000, arm model keys, drop_path 0.0); latest.pth / config md5s in out/inputs_md5.txt"

# ---- copies of the frozen third-party scorer files (md5 re-checked on the copies) ----
cp -p $CAL/el_metrics.py $CAL/calib_dump.py /home/noob/work/found/p8/a8_screen_score.py /home/noob/work/found/t9/rf_sets.tsv $O/frozen/ || die "frozen copies"
(cd $O/frozen && printf '%s\n' "6e73ff11aaa6171a52b5a5404877ab46  el_metrics.py" "c172717e5989edb8e0b7b312096f9180  calib_dump.py" \
  "8eba76e5bb0783e9d4ecc432dea4a785  a8_screen_score.py" "14771356ef7c99f567c5f80dad2e48dd  rf_sets.tsv" | md5sum -c --quiet) >> $LOG 2>&1 || die "frozen copy md5"
diff $O/frozen/calib_dump.py $S/a8_calib_dump_4k.py > $O/out/a8_calib_dump_4k.diff

# ---- 1. scorer self-test (synthetic) ----
run selftest $LOG $P -B $O/frozen/a8_screen_score.py --selftest
rc=$?; log "pass 1 a8_screen_score --selftest rc=$rc"; [ $rc = 0 ] || exit 1

# ---- 2. calib dumps, CPU fp32, val + rf only ----
OK2=""
for r in $RUNS; do
  run dump_$r $LOG $P -B $S/a8_calib_dump_4k.py --code $W --out $O/work/dump --group $r $E/$r --sets val rf --rf $RF --device cpu --threads 8
  rc=$?; log "pass 2 dump $r (val 54 + rf 106, CPU fp32, step 4000 asserted) rc=$rc"
  if [ $rc = 0 ] && [ -s $O/work/dump/$r.val.npz ] && [ -s $O/work/dump/$r.rf.npz ]; then OK2="$OK2 $r"; else F=$((F + 1)); fi
done

# ---- 3. el_metrics records (8 procs x 1 thread) ----
NREC=0
for r in $OK2; do for s in val rf; do
  run rec_${r}_$s $LOG env OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 $P -B $O/frozen/el_metrics.py records \
    --dump $O/work/dump/$r.$s.npz --set $s --code $W --rf $RF --out $O/out/rec/$r.$s.json --procs 8
  rc=$?; log "pass 3 records $r $s (el_metrics 6e73ff11, no m0: UNCHECKED) rc=$rc"
  if [ $rc = 0 ] && [ -s $O/out/rec/$r.$s.json ]; then NREC=$((NREC + 1)); else F=$((F + 1)); fi
done; done

# ---- 3b. dump-integrity gate (coach ruling): val records at b = 0 vs the trainer's own pooled val at step 4000 ----
# per run: crack IoU and inactive IoU from el_metrics.curves (frozen 6e73ff11) at the grid point b = 0 vs metrics.json
# val_history[-1] (step 4000 asserted), |delta| <= 0.005 (trainer GPU bf16 vs dump CPU fp32). Reads ONLY val_history; never
# test_final / test_best. Any failure (or a missing record): stop before pass 5 (rc 1, no GO-rule output).
G3B=0
for r in $RUNS; do
  [ -s $O/out/rec/$r.val.json ] && [ -s $E/$r/metrics.json ] || { log "pass 3b $r: val record or metrics.json missing"; G3B=1; continue; }
  nice -n 19 $P -B - $O/frozen $O/out/rec/$r.val.json $E/$r/metrics.json >> $O/out/a8_dump_integrity.txt 2>> $LOG <<'EOF'
import json, sys
import numpy as np
sys.path.insert(0, sys.argv[1]); import el_metrics as M  # the frozen 6e73ff11 copy
rec = json.load(open(sys.argv[2])); vh = json.load(open(sys.argv[3]))["val_history"]; e = vh[-1]
assert int(e["step"]) == 4000, ("val_history[-1] step", e["step"])
cv = M.curves(rec["cells"]); j = int(np.argmin(np.abs(M.GRID - 0.0)))
mine = {"crack_iou": float(cv["IoU"][j]), "inactive_iou": float(cv["inactIoU"][j])}
d = {k: mine[k] - float(e[k]) for k in mine}; ok = all(abs(v) <= 0.005 for v in d.values())
print(sys.argv[2].split("/")[-1], "| n cells", len(rec["cells"]), "| " + " | ".join(f"{k}: records {mine[k]:.4f} trainer {float(e[k]):.4f} "
      f"delta {d[k]:+.5f}" for k in mine), "| tol 0.005 |", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
EOF
  rc=$?; log "pass 3b dump integrity $r (val b 0 vs metrics.json val_history[-1], tol 0.005) rc=$rc"; [ $rc = 0 ] || G3B=1
done
[ $G3B = 0 ] || { log "pass 3b FAILED: stopping before pass 5 (no GO-rule output)"; exit 1; }

# ---- 4. PF validity: 4k encoder cosine to init, per run ----
OK4=""
for r in $OK2; do
  run init_$r $LOG $P -B $S/a8_init_dump.py --code $W --run $E/$r --out $O/work/init/$r.init.pth
  rc=$?; log "pass 4a init reference $r rc=$rc"; if [ $rc = 0 ]; then OK4="$OK4 $r"; else F=$((F + 1)); fi
done
for arm in A8 A8c; do
  case $arm in A8) bb=convnext_tiny.dinov3_lvd1689m;; A8c) bb=convnext_tiny;; esac
  PAIRS=()
  for k in 0 1; do r=f8_${arm}_4k_s$k
    case " $OK4 " in *" $r "*) PAIRS+=(--pair "$r 4k vs init" $O/work/init/$r.init.pth $E/$r/checkpoints/latest.pth);; esac; done
  [ ${#PAIRS[@]} = 8 ] || { log "pass 4b cosine $arm skipped (a dump or init reference missing)"; F=$((F + 1)); continue; }
  run cos_$arm $O/out/enc_cosine_4k_$arm.txt $P -B $W/reports/enc_cosine_hr.py --backbone $bb "${PAIRS[@]}" --out $O/out/enc_cosine_4k_$arm.json
  rc=$?; log "pass 4b enc_cosine_hr $arm (--backbone $bb) rc=$rc"; [ $rc = 0 ] || F=$((F + 1))
done
if [ -s $O/out/enc_cosine_4k_A8.json ] && [ -s $O/out/enc_cosine_4k_A8c.json ]; then
  nice -n 19 $P -B - $O/out/enc_cosine_4k_A8.json $O/out/enc_cosine_4k_A8c.json > $O/out/a8_validity.txt 2>> $LOG <<'EOF'
import json, sys
# protocol_A8screen §3 validity: ConvNeXt stages 2-3 (timm encoder.stages.2 / .3) weight cosine to init >= 0.5; operationalised
# per run, an arm VALID only if both of its runs pass. cos_ln, cos_gamma and norm_ratio are reported, not in the rule.
for arm, f in zip(("A8", "A8c"), sys.argv[1:]):
    res = json.load(open(f)); ok = len(res) == 2
    for lab, v in res.items():
        st = v["stages"]
        good = all(st.get(s, {}).get("cos_w") is not None and st[s]["cos_w"] >= 0.5 for s in ("stage2", "stage3")); ok = ok and good
        print(arm, "|", lab, "|", " ".join(f"{s}: cos_w {st[s]['cos_w']} norm_ratio {st[s]['norm_ratio']} cos_ln {st[s]['cos_ln']} "
                                           f"cos_gamma {st[s]['cos_gamma']};" for s in sorted(st)), "|", "PASS" if good else "FAIL")
    print(f"ARM {arm} {'VALID' if ok else 'INVALID'}")
EOF
  rc=$?; log "pass 4c validity table rc=$rc ($(grep '^ARM' $O/out/a8_validity.txt | tr '\n' ' '))"; [ $rc = 0 ] || F=$((F + 1))
else log "pass 4c validity skipped (cosine JSON missing)"; F=$((F + 1)); fi

# ---- 5. GO rule (a8_screen_score 8eba76e5, seed means) ----
if [ "$(echo $OK2 | wc -w)" = 4 ] && [ $NREC = 8 ]; then
  run screen $O/out/a8_screen_score.stdout $P -B $O/frozen/a8_screen_score.py --dump $O/work/dump --rec $O/out/rec \
    --arm A8=f8_A8_4k_s0,f8_A8_4k_s1 --arm A8c=f8_A8c_4k_s0,f8_A8c_4k_s1 --code $W --rf $RF --rf-sets $O/frozen/rf_sets.tsv \
    --el-metrics $O/frozen --boot 2000 --out $O/out/a8_screen_score.json
  rc=$?; log "pass 5 a8_screen_score (8eba76e5; el_metrics 6e73ff11 imported from $O/frozen; 2,000 module resamples, seed 0) rc=$rc"
  [ $rc = 0 ] || F=$((F + 1))
else log "pass 5 skipped: dumps $(echo $OK2 | wc -w)/4, records $NREC/8"; F=$((F + 1)); fi

# ---- 6. mechanical summary, md5 lists, MANIFEST ----
if [ -s $O/out/a8_screen_score.json ] && [ -s $O/out/a8_validity.txt ]; then
  $P -B - $O/out/a8_screen_score.json $O/out/a8_validity.txt > $O/out/a8_summary.txt 2>> $LOG <<'EOF'
import json, sys
r = json.load(open(sys.argv[1]))
valid = {l.split()[1]: l.split()[2] == "VALID" for l in open(sys.argv[2]) if l.startswith("ARM ")}
print("A8 screen: MECHANICAL output of a8_score.sh (protocol_A8screen v1.1 §3); not a verdict until coach's recompute")
print("validity (4k cosine to init, stages 2-3 cos_w >= 0.5, every run):", json.dumps(valid))
print("GO rule terms (seed means):", json.dumps(r["terms"]))
print("GO (all five terms):", r["GO"], "| F51 modules:", r["F51_modules"], "| F51 sign up:", r["F51_sign_up"], "| boot hi:", round(r["boot_hi"], 4))
print("b_rel per run (val, relR@2 s.t. relP@2 >= 0.90, el_metrics 6e73ff11 OP grid):", json.dumps(r["b_rel"]))
ok = all(valid.get(a, False) for a in ("A8", "A8c"))
print("screen outcome by the rule:", ("GO" if r["GO"] else "KILL") if ok else "NO VERDICT (an arm is invalid: fix PF for LayerNorm first, §3)")
EOF
  rc=$?; log "pass 6 summary rc=$rc: $(tail -1 $O/out/a8_summary.txt)"; [ $rc = 0 ] || F=$((F + 1))
fi
md5sum -c --quiet $O/out/inputs_md5.txt >> $LOG 2>&1 || { log "inputs changed during scoring (latest.pth / config md5)"; F=$((F + 1)); }
(cd $O/work/dump && md5sum *.npz) > $O/out/dump_md5_on_gaint.txt 2>> $LOG
(cd $O/work/init && md5sum *.pth) > $O/out/init_md5_on_gaint.txt 2>> $LOG
md5sum "$0" $S/FROZEN.md5 $S/a8_calib_dump_4k.py $S/a8_init_dump.py $O/frozen/* $W/reports/enc_cosine_hr.py $O/expected_md5.txt > $O/out/scripts_md5.txt
cp -p $O/pids.txt $O/out/ 2>/dev/null
(cd $O/out && find . -type f ! -name MANIFEST.md5 | sort | xargs md5sum > MANIFEST.md5)
log "MANIFEST written ($(wc -l < $O/out/MANIFEST.md5) files); scoring fails $F"
[ $F = 0 ] || exit 1
exit 0
