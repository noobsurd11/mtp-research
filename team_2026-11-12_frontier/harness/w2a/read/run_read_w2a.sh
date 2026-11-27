#!/bin/bash
# Wave 2a read on gaint CPU (builder, 17 Nov 2026; LAUNCH_REQUEST_w2a.md section 8). Modelled on harness/w1read/run_read_rows2.sh.
# NOT to be run for a result before the independent review; the lead runs it once the dumps are complete.
#   Tools: the reviewed read tree bench_wt_b at b5bf0ae (scripts/bench_read_w1.py fdb56b78), unchanged.
#   Comparator PF = W1-G seeds 5, 6 (gaint, el_bench 31c0c36). A/A margin M: W1-G + W1-G2 seeds {5,6} against {7,8}.
#     The tool takes the A/A seeds from one arm, so the same PF dump folder is given twice: arm PF (seeds 5, 6; baseline
#     and comparator of every PF pair) and arm PFAA (seeds 5 to 8; used only by --aa PFAA:5,6:7,8). M is taken at
#     argmax, so it equals what --aa PF:5,6:7,8 gives on a four-seed PF arm. PF4=1 instead makes PF itself the four-seed
#     arm with --aa PF:5,6:7,8 (as run_read_w1g4.sh); then every "X - PF" contrast is against four PF seeds. Lead's ruling
#     (17 Nov): PF seeds 5, 6 is the registered comparator; a PF4=1 read is a sensitivity read, never the verdict. It goes
#     to its own folder (bench_reads/w2a_pf4<_TAG>) and is marked in run.log and in SENSITIVITY_PF4.txt.
#   Dumps: gaint only (bench_dumps/w1g and bench_dumps/w2a); nothing is linked or copied from cv02; no symlinked run folder
#     is accepted; every manifest must name the same device and fp32.
#   One run gives the 532-cell values and the 416 clean cells (benchmark/splits/score_exclude_v3.txt).
# Variables:
#   ARMS  "auto" (default) = every arm of {rcs ema jmlhard softband swad spd} whose dumps are complete and whose gate
#         verdict is PASS (others are skipped with one line each); or a list, e.g. ARMS="rcs ema": then an incomplete arm
#         or a gate that is not PASS stops the script.
#   GATE_ACK  arms whose gate verdict (FAIL or OPEN) the lead has seen and still wants read, e.g. GATE_ACK="spd". Such an
#         arm is descriptive only, not a screen verdict: it is marked at the start and end of run.log and in the file
#         <out>/GATE_ACK.txt (arm, gate, verdict, verdict file). Gate verdicts: newest
#         /home/noob/work/bench_reads/w2a_gates/<gate>_r*/VERDICT.
#   TAG   suffix of the output folder for a later second read (e.g. TAG=softband ARMS="jmlhard softband" after the
#         retrain of w2a_softband_f1_s6): /home/noob/work/bench_reads/w2a_<TAG>.
#   DRY=1 mechanics test only: PF, PFAA and the rcs seed-5 dumps, output /home/noob/work/bench_reads/w2a_gates/dry<TAG>.
#         Its numbers are not a result and are not to be reported.
#   SHOW=1 prints the read command for ARMS (auto = all six arms) and exits: no check of dumps or gates, nothing written.
# An arm is complete when every dump job of the arm in bq/w2a2/dump/jobs.txt (all readouts, 10 per readout) has
# "trained <job> rc=0" as its last "trained" line over the dump logs (w2a2, then w2a3 for the retrained run) and its
# manifest exists and names the expected run id, fold, seed, weights key, step 20000 and commit c57508e.
# Pairs (--pair A=B is the contrast B - A; arm regexes are full matches):
#   rcs       PF=RCS
#   ema       RAWBN=EMA            (pre-declared primary: ema_9998_bn - raw_bn of the same runs; the other four ema readouts are not read here)
#   jmlhard   PF=JMLHARD           (control)
#   softband  JMLHARD=SOFTBAND     (section 8: read only as soft_band_jml - jml_hard; needs jmlhard in the same read)
#   swad      PF=SWADBN (primary), SWADRAWBN=SWADBN, PF=SWADRAW, PF=SWADRAWBN, PF=SWAD, PF=SWADEMABN, PF=SWADEMA
#   spd       PF=SPD
# The one-run control w2a_spdctrl_f0_s5 is not an arm of this read (one fold, one seed).
# Output folder must not exist (no overwrite of an earlier read). CPU only, nice 19, 8 workers.
set -u
set -f
ARMS=${ARMS:-auto}; GATE_ACK=${GATE_ACK:-}; TAG=${TAG:-}; DRY=${DRY:-0}; PF4=${PF4:-0}; SHOW=${SHOW:-0}
ME=$(readlink -f "$0")
T=/home/yugma/mtp/research/team_2026-11-12_frontier
RT=/home/noob/work/bench_wt_b
cd $RT || exit 1
[ "$(git rev-parse --short HEAD)" = b5bf0ae ] || { echo "worktree not at b5bf0ae"; exit 1; }
[ "$(git status --porcelain -uno | wc -l)" = 0 ] || { echo "tracked changes in $RT"; exit 1; }
[ "$(md5sum < scripts/bench_read_w1.py | cut -c1-8)" = fdb56b78 ] || { echo "bench_read_w1.py is not fdb56b78"; exit 1; }
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
X=$T/benchmark/splits/score_exclude_v3.txt
[ "$(md5sum < $X | cut -c1-8)" = 6d48dfbd ] || { echo "score_exclude_v3.txt is not 6d48dfbd"; exit 1; }
PFD=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11
WD=/home/noob/work/bench_dumps/w2a/elbench1
DJ=/home/noob/work/bq/w2a2/dump/jobs.txt
DLOGS="/home/noob/work/bq/w2a2/dump/launch.log /home/noob/work/bq/w2a3/dump/launch.log"
GD=/home/noob/work/bench_reads/w2a_gates
[ "$(md5sum < $DJ | cut -c1-8)" = 0bcef536 ] || { echo "dump jobs.txt is not 0bcef536"; exit 1; }
ALL="rcs ema jmlhard softband swad spd"
SEEDS="5 6"; SS='[56]'
SUF=${TAG:+_$TAG}; [ "$PF4" = 1 ] && SUF=_pf4$SUF   # a PF4 read never takes the folder name of the verdict read
if [ "$DRY" = 1 ]; then O=$GD/dry$TAG; ARMS=rcs; SEEDS="5"; SS='5'; else O=/home/noob/work/bench_reads/w2a$SUF; fi
[ -e $O ] && { echo "output folder exists: $O"; exit 1; }

method(){ case $1 in rcs) echo rcs_pf_v11;; ema) echo ema_wise_posthoc_pf_v11;; softband) echo soft_band_jml;; jmlhard) echo jml_hard;;
  swad) echo swad_const_pf_v11;; spd) echo encoder_spd_pf_v11;; *) return 1;; esac; }
keys(){ case $1 in ema) echo "model raw_bn ema_9998_bn ema_999_bn ema_9998 ema_999";; swad) echo "model raw_bn swad swad_bn ema_9998 ema_9998_bn";;
  *) echo model;; esac; }
gate_of(){ case $1 in ema) echo gate_ema_hash;; swad) echo gate_swad_prescreen;; spd) echo gate_spd_mech;; *) echo none;; esac; }
has(){ case " $2 " in *" $1 "*) return 0;; esac; return 1; }
# complete <arm>: 0 if every dump of the arm is there; else prints the first reason. With a second argument "list" it
# prints one line per expected dump instead (set dir, run id, fold, seed, weights key) for the manifest check.
complete(){
  local a=$1 m k s key job rid d last
  m=$(method $a) || { echo "unknown arm $a"; return 1; }
  for k in 0 1 2 3 4; do for s in $SEEDS; do for key in $(keys $a); do
    job=dump_w2a_${a}_f${k}_s${s}; rid=w2a_${a}_f${k}_s${s}
    [ $key = model ] || { job=${job}_$key; rid=$rid.$key; }
    d=$WD/$m/$rid
    [ "${2:-}" = list ] && { printf '%s\t%s\t%s\t%s\t%s\n' $d/cv5v2_f$k $rid $k $s $key; continue; }
    [ "$(grep -c "^$job|" $DJ)" = 1 ] || { echo "$a: job $job is not in $DJ"; return 1; }
    last=$(for f in $DLOGS; do [ -e $f ] && grep -h "\] trained $job rc=" $f; done | tail -1)
    case "$last" in *" trained $job rc=0") ;; "") echo "$a: $job has no 'trained' line yet"; return 1;; *) echo "$a: $job last line: ${last#*] }"; return 1;; esac
    [ -d $d ] && [ ! -L $d ] && [ ! -L $d/cv5v2_f$k ] && [ -f $d/cv5v2_f$k/manifest.json ] || { echo "$a: no dump folder with a manifest: $d/cv5v2_f$k"; return 1; }
  done; done; done
  return 0
}
gate_ok(){   # gate_ok <arm>: 0 if the arm has no gate here or its newest verdict is PASS; prints the verdict line
  local a=$1 g v f
  g=$(gate_of $a); [ $g = none ] && return 0
  set +f; f=$(ls -d $GD/${g}_r[0-9]*/VERDICT 2>/dev/null | grep -E "/${g}_r[0-9]+/VERDICT\$" | sort -V | tail -1); set -f
  [ -n "$f" ] || { echo "$a: no verdict file $GD/${g}_r*/VERDICT"; return 1; }
  v=$(cut -d' ' -f2 $f)
  [ "$(cat $f)" = "$g PASS" ] && { echo "$a: gate $g PASS ($f)"; return 0; }
  echo "$a: gate $g $v ($f)"; return 1
}

USE=""; NOTES=""; ACKED=""
if [ "$ARMS" = auto ]; then CAND=$ALL; MODE=auto; else CAND=$ARMS; MODE=list; fi
for a in $CAND; do
  has $a "$ALL" || { echo "unknown arm: $a (arms: $ALL)"; exit 1; }
  [ "$SHOW" = 1 ] && { USE="$USE $a"; continue; }
  why=$(complete $a) || { [ $MODE = list ] && { echo "REFUSED, incomplete: $why"; exit 1; }; NOTES="$NOTES
skipped (incomplete): $why"; continue; }
  if [ "$DRY" != 1 ]; then
    gv=$(gate_ok $a); grc=$?
    if [ $grc != 0 ]; then
      if has $a "$GATE_ACK"; then ACKED="$ACKED
$gv"; NOTES="$NOTES
GATE NOT PASSED BUT ACKNOWLEDGED (GATE_ACK): $gv"
      elif [ $MODE = list ]; then echo "REFUSED, gate not passed: $gv (name the arm in GATE_ACK to read it anyway)"; exit 1
      else NOTES="$NOTES
skipped (gate not passed; GATE_ACK=\"$a\" reads it anyway): $gv"; continue; fi
    elif [ -n "$gv" ]; then NOTES="$NOTES
$gv"; fi
  fi
  USE="$USE $a"
done
if has softband "$USE" && ! has jmlhard "$USE"; then
  [ $MODE = list ] && { echo "REFUSED: softband is read only against jmlhard; jmlhard is not in this read"; exit 1; }
  USE=$(echo " $USE " | sed 's/ softband / /'); NOTES="$NOTES
skipped: softband (jmlhard is not in this read)"
fi
USE=$(echo $USE)
[ -n "$USE" ] || { echo "no arm to read.$NOTES"; exit 1; }
for k in 0 1 2 3 4; do for s in 5 6 7 8; do d=$PFD/w1g_pf_v11_f${k}_s$s
  [ -d $d ] && [ ! -L $d ] && [ -f $d/cv5v2_f$k/manifest.json ] || { echo "PF dump missing: $d"; exit 1; }
done; done

if [ "$PF4" = 1 ]; then A=(--arm "PF=$PFD:w1g_pf_v11_f[0-4]_s[5-8]"); AA=PF:5,6:7,8
else A=(--arm "PF=$PFD:w1g_pf_v11_f[0-4]_s[56]" --arm "PFAA=$PFD:w1g_pf_v11_f[0-4]_s[5-8]"); AA=PFAA:5,6:7,8; fi
PR=()
for a in $USE; do m=$WD/$(method $a); r="w2a_${a}_f[0-4]_s$SS"
  case $a in
    rcs) A+=(--arm "RCS=$m:$r"); PR+=(--pair PF=RCS);;
    ema) A+=(--arm "RAWBN=$m:$r\.raw_bn" --arm "EMA=$m:$r\.ema_9998_bn"); PR+=(--pair RAWBN=EMA);;
    jmlhard) A+=(--arm "JMLHARD=$m:$r"); PR+=(--pair PF=JMLHARD);;
    softband) A+=(--arm "SOFTBAND=$m:$r"); PR+=(--pair JMLHARD=SOFTBAND);;
    swad) A+=(--arm "SWADBN=$m:$r\.swad_bn" --arm "SWADRAWBN=$m:$r\.raw_bn" --arm "SWADRAW=$m:$r" --arm "SWAD=$m:$r\.swad"
              --arm "SWADEMABN=$m:$r\.ema_9998_bn" --arm "SWADEMA=$m:$r\.ema_9998")
          PR+=(--pair PF=SWADBN --pair SWADRAWBN=SWADBN --pair PF=SWADRAW --pair PF=SWADRAWBN --pair PF=SWAD --pair PF=SWADEMABN --pair PF=SWADEMA);;
    spd) A+=(--arm "SPD=$m:$r"); PR+=(--pair PF=SPD);;
  esac
done

CMD="scripts/bench_read_w1.py ${A[*]} ${PR[*]} --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa $AA --score-exclude $X --out $O/read"
[ "$SHOW" = 1 ] && { echo "SHOW=1 (no check of dumps or gates, nothing run, nothing written); arms: $USE"; echo "$CMD"; exit 0; }
mkdir -p $O || exit 1
EXP=$O/expected_dumps.tsv
for a in $USE; do complete $a list; done > $EXP
ACKMSG="DESCRIPTIVE ONLY, NOT A SCREEN VERDICT: the arms below are read under GATE_ACK although their gate (LAUNCH_REQUEST_w2a.md section 8) did not pass."
PF4MSG="SENSITIVITY READ (PF4=1), NEVER THE VERDICT: PF is the four-seed arm (W1-G + W1-G2 seeds 5 to 8). The registered comparator is PF seeds 5, 6 (the read without PF4)."
[ -n "$ACKED" ] && printf '%s\narm: gate verdict (verdict file)%s\n' "$ACKMSG" "$ACKED" > $O/GATE_ACK.txt
[ "$PF4" = 1 ] && echo "$PF4MSG" > $O/SENSITIVITY_PF4.txt
{
  echo "[$(date '+%F %T')] w2a read start (out $O; DRY=$DRY; ARMS=$ARMS -> $USE; GATE_ACK='$GATE_ACK'; PF4=$PF4; script $(md5sum < $ME | cut -c1-8))"
  [ "$PF4" = 1 ] && echo "$PF4MSG"
  [ -n "$ACKED" ] && echo "$ACKMSG$ACKED"
  [ -n "$NOTES" ] && echo "notes:$NOTES"
  # manifests of the arms in use: run id, fold, seed, weights key, step, commit; one device and precision over PF and arms
  $P - $EXP $PFD <<'EOF' || { echo "REFUSED: manifest check failed"; exit 1; }
import json, sys
from pathlib import Path
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if l.strip()]
dev, bad = set(), []
for d, rid, k, s, key in rows:
    m = json.loads((Path(d) / "manifest.json").read_text())
    want = {"run_id": rid, "fold": int(k), "seed": int(s), "weights_key": key, "step": 20000, "set": f"cv5v2_f{k}",
            "precision": "fp32", "set_kind": "open"}
    bad += [f"{d}: {x} = {m.get(x)!r}, expected {v!r}" for x, v in want.items() if m.get(x) != v]
    if not str(m.get("code_commit", "")).startswith("c57508e"):
        bad.append(f"{d}: code_commit {m.get('code_commit')}")
    dev.add(m["device"])
for p in sorted(Path(sys.argv[2]).glob("w1g_pf_v11_f[0-4]_s[5-8]/cv5v2_f[0-4]/manifest.json")):
    m = json.loads(p.read_text())
    dev.add(m["device"])
    if m["precision"] != "fp32" or not str(m["code_commit"]).startswith("31c0c36"):
        bad.append(f"{p}: precision {m['precision']}, commit {m['code_commit']}")
if len(dev) != 1:
    bad.append(f"more than one device over PF and the arms: {sorted(dev)}")
print(f"manifest check: {len(rows)} wave 2a dumps, device {sorted(dev)}: {'OK' if not bad else 'FAIL'}")
for b in bad[:20]:
    print("  " + b)
sys.exit(1 if bad else 0)
EOF
  echo "command (cwd $RT, nice -n 19): $CMD"
  nice -n 19 $P scripts/bench_read_w1.py "${A[@]}" "${PR[@]}" --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa $AA \
    --score-exclude $X --out $O/read; rc=$?
  echo "[$(date '+%F %T')] read rc=$rc"
  set +f; ( cd $O/read 2>/dev/null && md5sum read*.txt read.json > $O/MD5.txt ); set -f
  { md5sum $ME $RT/scripts/bench_read_w1.py $X $DJ | sed 's/  /  input: /'; } >> $O/MD5.txt
  echo "[$(date '+%F %T')] W2A READ ALL DONE (rc $rc); tracked changes: bench_wt_b $(git status --porcelain -uno | wc -l), bench_wt_w2 $(git -C /home/noob/work/bench_wt_w2 status --porcelain -uno | wc -l)"
  [ "$DRY" = 1 ] && echo "DRY RUN: a mechanics test (rcs seed 5 only). Its numbers are not a result."
  [ "$PF4" = 1 ] && echo "$PF4MSG (file $O/SENSITIVITY_PF4.txt)"
  [ -n "$ACKED" ] && echo "$ACKMSG$ACKED
(file $O/GATE_ACK.txt)"
  exit $rc
} 2>&1 | tee $O/run.log
exit ${PIPESTATUS[0]}
