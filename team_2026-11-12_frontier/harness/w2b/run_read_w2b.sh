#!/bin/bash
# Wave 2b screen read on gaint CPU (w2b builder, 17 Nov 2026; harness/w2b/READ_PLAN_w2b.md; lead's rulings log.md
# "17 Nov 17:33" and the K0 to K4 / Q6 rulings received between 19:10 and 19:16). Modelled on harness/w2a/read/run_read_w2a.sh (5aac565d).
# NOT to be run for a result before the independent review; the lead runs it once an arm's dumps are complete.
#   ARM=lace : la_ce  (queue bq/w2b_lace, card la_ce_pf_v11, 10 dumps, readout = the card's argmax24)
#   ARM=lci  : layered_ci (queue bq/w2b_lci, card layered_ci_pf_v11, 30 dumps: the card's layered_ci_replace,
#              <run>.argmax24, <run>.layered_ci_union)
#   PF4=1    : sensitivity read (PF and PFC at seeds 5 to 8, A/A on PF itself), own folder w2b_pf4_<arm>, marked in run.log
#              and SENSITIVITY_PF4.txt; never the verdict (D Q5).
#   SHOW=1   : prints the commands and exits (no check, nothing written).
#   STOP=checks : stops after the completeness, manifest and pin checks (tests; nothing written but run.log).
#   OUTROOT, QROOT, DUMPROOT: output, queue and arm-dump roots (defaults below; changed only by the test script).
# Steps: (1) pins: read tree bench_wt_b at b5bf0ae, clean, bench_read_w1.py fdb56b78, score_exclude_v3.txt 6d48dfbd,
#   the arm's dump jobs.txt, w2b_counts.py and w2b_verdict.py md5s; (2) completeness: every expected dump job has
#   'trained <job> rc=0' as its last trained line in <Q>/dump/launch.log, a real (not symlinked) folder and a manifest;
#   (3) manifests: run id, fold, seed, weights key model, step 20000, set cv5v2_f<k>, fp32, open set, code commit
#   f678381, decision rule (and t_I 0.5 for the layered readouts); PF: fp32, 31c0c36; PF at OP-C: derivation
#   classbias_xfit, fit_folds without the own fold; one device over all; (4) bench_read_w1 (arms and pairs of READ_PLAN,
#   --score-exclude: 532 and 416 cells in one run); (5) w2b_counts.py on 532 and on 416 cells; (6) w2b_verdict.py.
# Output folder must not exist. CPU only, nice 19, 8 workers.
set -u
set -f
ARM=${ARM:-}; PF4=${PF4:-0}; SHOW=${SHOW:-0}; STOP=${STOP:-}
OUTROOT=${OUTROOT:-/home/noob/work/bench_reads}; QROOT=${QROOT:-/home/noob/work/bq}; DUMPROOT=${DUMPROOT:-/home/noob/work/bench_dumps/w2b}
ME=$(readlink -f "$0"); HW=$(dirname "$ME")
T=/home/yugma/mtp/research/team_2026-11-12_frontier
RT=/home/noob/work/bench_wt_b
DEPLOY=f678381
P=/home/noob/work/el-fault-detection/.venv/bin/python
X=$T/benchmark/splits/score_exclude_v3.txt
PFD=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11
PCD=/home/noob/work/bench_udev/opc/dumps_gaint/elbench1/pf_v11_opc
WD=$DUMPROOT/elbench1
COUNTS_MD5=a23dd544d2f83d2905397b27dd2b887b
VERDICT_MD5=1ace40f781cfcae1a3a7ab97d9aebfe6
R13=0,1,2,4,5,7,11,13,14,15,16,20,21
case "$ARM" in
  lace) Q=$QROOT/w2b_lace; CARD=la_ce_pf_v11; PRE=w2b_lace; DECS="card"; DJ_MD5=3759e8249fa4a112493f0258e11e9adb;;
  lci)  Q=$QROOT/w2b_lci;  CARD=layered_ci_pf_v11; PRE=w2b_lci; DECS="card argmax24 layered_ci_union"; DJ_MD5=135778ff7c09635d98cf6de59cf16b10;;
  *) echo "REFUSED: ARM must be lace or lci (got '$ARM')"; exit 1;;
esac
DJ=$Q/dump/jobs.txt; DLOG=$Q/dump/launch.log
if [ "$PF4" = 1 ]; then PS='[5-8]'; SUF=_pf4; else PS='[56]'; SUF=; fi
O=$OUTROOT/w2b${SUF}_$ARM
A=(--arm "PF=$PFD:w1g_pf_v11_f[0-4]_s$PS" --arm "PFC=$PCD:w1g_pf_v11_f[0-4]_s$PS")
if [ "$PF4" = 1 ]; then AA=PF:5,6:7,8; else A+=(--arm "PFAA=$PFD:w1g_pf_v11_f[0-4]_s[5-8]"); AA=PFAA:5,6:7,8; fi
r="${PRE}_f[0-4]_s[56]"
if [ $ARM = lace ]; then
  A+=(--arm "LACE=$WD/$CARD:$r"); PR=(--pair PFC=LACE --pair PF=LACE)
  CP=(--pair PFC=LACE --pair PF=LACE)
else
  A+=(--arm "LCI=$WD/$CARD:$r" --arm "LCIARG=$WD/$CARD:$r\.argmax24" --arm "LCIUNI=$WD/$CARD:$r\.layered_ci_union")
  PR=(--pair PFC=LCI --pair PF=LCI --pair LCIARG=LCI --pair LCIARG=LCIUNI --pair PF=LCIARG)
  CP=(--pair PFC=LCI --pair LCIARG=LCI:paired --pair LCIARG=LCIUNI:paired --pair PF=LCI)
fi
CMD="scripts/bench_read_w1.py ${A[*]} ${PR[*]} --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa $AA --score-exclude $X --out $O/read"
C5="$HW/w2b_counts.py --read $O ${CP[*]} --classes $R13 --out $O/counts_532.txt"
C4="$HW/w2b_counts.py --read $O ${CP[*]} --classes $R13 --exclude $X --out $O/counts_416.txt"
VC="$HW/w2b_verdict.py --arm $ARM --read $O --c532 $O/counts_532.txt.json --c416 $O/counts_416.txt.json --out $O/verdict.txt"
if [ "$SHOW" = 1 ]; then
  echo "SHOW=1 (nothing checked, nothing written); ARM=$ARM PF4=$PF4 out $O"
  echo "read (cwd $RT): $CMD"; echo "counts 532: $C5"; echo "counts 416: $C4"; echo "verdict: $VC"; exit 0
fi
[ -e $O ] && { echo "REFUSED: output folder exists: $O"; exit 1; }
# (1) pins
fail(){ echo "REFUSED: $*"; exit 1; }
[ "$(git -C $RT rev-parse --short HEAD)" = b5bf0ae ] || fail "$RT not at b5bf0ae"
[ "$(git -C $RT status --porcelain -uno | wc -l)" = 0 ] || fail "tracked changes in $RT"
[ "$(md5sum < $RT/scripts/bench_read_w1.py | cut -c1-8)" = fdb56b78 ] || fail "bench_read_w1.py is not fdb56b78"
[ "$(md5sum < $X | cut -c1-8)" = 6d48dfbd ] || fail "score_exclude_v3.txt is not 6d48dfbd"
[ "$(md5sum < $HW/w2b_counts.py | cut -c1-32)" = "$COUNTS_MD5" ] || fail "w2b_counts.py md5 is not the pinned $COUNTS_MD5"
[ "$(md5sum < $HW/w2b_verdict.py | cut -c1-32)" = "$VERDICT_MD5" ] || fail "w2b_verdict.py md5 is not the pinned $VERDICT_MD5"
[ -s $DJ ] && [ "$(md5sum < $DJ | cut -c1-32)" = "$DJ_MD5" ] || fail "$DJ missing or md5 != $DJ_MD5"
# (2) completeness
EXP=""
for k in 0 1 2 3 4; do for s in 5 6; do for dec in $DECS; do
  job=dump_${PRE}_f${k}_s${s}; rid=${PRE}_f${k}_s${s}; want=$dec
  [ $dec = card ] && { [ $ARM = lace ] && want=argmax24 || want=layered_ci_replace; } || { job=${job}_$dec; rid=$rid.$dec; }
  [ "$(grep -c "^$job|" $DJ)" = 1 ] || fail "job $job is not once in $DJ"
  last=$( [ -e $DLOG ] && grep -h "\] trained $job rc=" $DLOG | tail -1)
  case "$last" in *" trained $job rc=0") ;; "") fail "incomplete: $job has no 'trained' line in $DLOG";; *) fail "$job last line: ${last#*] }";; esac
  d=$WD/$CARD/$rid
  [ -d $d ] && [ ! -L $d ] && [ ! -L $d/cv5v2_f$k ] && [ -f $d/cv5v2_f$k/manifest.json ] || fail "no real dump folder with a manifest: $d/cv5v2_f$k"
  EXP="$EXP$d/cv5v2_f$k	$rid	$k	$s	$want
"
done; done; done
# (3) manifests
mkdir -p $(dirname $O) && TMPE=$(mktemp) && printf '%s' "$EXP" > $TMPE
$P - $TMPE $PFD $PCD "$PS" $DEPLOY <<'EOF' || { rm -f $TMPE; fail "manifest check failed"; }
import json, re, sys
from pathlib import Path
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if l.strip()]
pfd, pcd, ps, deploy = Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4], sys.argv[5]
seeds = [int(x) for x in re.findall(r"\d", ps)] if "-" not in ps else list(range(int(ps[1]), int(ps[3]) + 1))
dev, bad = set(), []
for d, rid, k, s, rule in rows:
    m = json.loads((Path(d) / "manifest.json").read_text())
    want = {"run_id": rid, "fold": int(k), "seed": int(s), "weights_key": "model", "step": 20000, "set": f"cv5v2_f{k}",
            "precision": "fp32", "set_kind": "open", "decision_rule": rule}
    if rule.startswith("layered_ci"):
        want["decision_t_I"] = 0.5
    bad += [f"{d}: {x} = {m.get(x)!r}, expected {v!r}" for x, v in want.items() if m.get(x) != v]
    if not str(m.get("code_commit", "")).startswith(deploy):
        bad.append(f"{d}: code_commit {m.get('code_commit')}")
    dev.add(m["device"])
for k in range(5):
    for s in seeds:
        mp = pfd / f"w1g_pf_v11_f{k}_s{s}" / f"cv5v2_f{k}" / "manifest.json"
        mc = pcd / f"w1g_pf_v11_f{k}_s{s}" / f"cv5v2_f{k}" / "manifest.json"
        for p in (mp, mc):
            if not p.exists() or p.parent.is_symlink() or p.parent.parent.is_symlink():
                bad.append(f"missing or symlinked: {p}"); continue
        if bad and bad[-1].startswith("missing"):
            continue
        a, c = json.loads(mp.read_text()), json.loads(mc.read_text())
        if a["precision"] != "fp32" or not str(a["code_commit"]).startswith("31c0c36") or a["seed"] != s or a["fold"] != k:
            bad.append(f"{mp}: precision {a['precision']}, commit {a['code_commit']}, seed {a['seed']}, fold {a['fold']}")
        if c.get("derivation") != "classbias_xfit" or k in c.get("fit_folds", [k]) or c.get("seed") != s \
                or c.get("decision_rule") != "argmax24_logp_plus_classbias_xfit" or c.get("fold") != k:
            bad.append(f"{mc}: derivation {c.get('derivation')}, fit_folds {c.get('fit_folds')}, rule {c.get('decision_rule')}")
        dev |= {a["device"], c["device"]}
if len(dev) != 1:
    bad.append(f"more than one device: {sorted(dev)}")
print(f"manifest check: {len(rows)} arm dumps, PF and PF at OP-C seeds {seeds}, device {sorted(dev)}: {'OK' if not bad else 'FAIL'}")
for b in bad[:20]:
    print("  " + b)
sys.exit(1 if bad else 0)
EOF
rm -f $TMPE
[ "$STOP" = checks ] && { echo "STOP=checks: pins, completeness and manifests OK; nothing run"; exit 0; }
mkdir -p $O || exit 1
printf '%s' "$EXP" > $O/expected_dumps.tsv
PF4MSG="SENSITIVITY READ (PF4=1), NEVER THE VERDICT: PF and PF at OP-C are seeds 5 to 8. The registered comparator is seeds 5, 6."
[ "$PF4" = 1 ] && echo "$PF4MSG" > $O/SENSITIVITY_PF4.txt
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
{
  echo "[$(date '+%F %T')] w2b read start (ARM=$ARM PF4=$PF4 out $O; script $(md5sum < $ME | cut -c1-8); counts $(md5sum < $HW/w2b_counts.py | cut -c1-8); verdict $(md5sum < $HW/w2b_verdict.py | cut -c1-8))"
  [ "$PF4" = 1 ] && echo "$PF4MSG"
  echo "read (cwd $RT, nice -n 19): $CMD"
  (cd $RT && nice -n 19 $P scripts/bench_read_w1.py "${A[@]}" "${PR[@]}" --labels v11 --workers 8 --cache $O/cache_c \
    --baseline PF --aa $AA --score-exclude $X --out $O/read); rc=$?
  echo "[$(date '+%F %T')] read rc=$rc"
  if [ $rc = 0 ]; then
    nice -n 19 $P $C5; r5=$?; nice -n 19 $P $C4; r4=$?
    echo "[$(date '+%F %T')] counts rc 532 $r5, 416 $r4"
    [ $r5 = 0 ] && [ $r4 = 0 ] && { $P $VC; rc=$?; echo "[$(date '+%F %T')] verdict rc=$rc"; } || rc=1
  fi
  set +f; ( cd $O && md5sum read/read*.txt read/read.json counts_*.txt counts_*.json verdict.txt 2>/dev/null > MD5.txt ); set -f
  { md5sum $ME $RT/scripts/bench_read_w1.py $X $DJ $HW/w2b_counts.py $HW/w2b_verdict.py | sed 's/  /  input: /'; } >> $O/MD5.txt
  echo "[$(date '+%F %T')] W2B READ ALL DONE (rc $rc); tracked changes: bench_wt_b $(git -C $RT status --porcelain -uno | wc -l), bench_wt_w2b $(git -C /home/noob/work/bench_wt_w2b status --porcelain -uno | wc -l)"
  [ "$PF4" = 1 ] && echo "$PF4MSG"
  exit $rc
} 2>&1 | tee $O/run.log
exit ${PIPESTATUS[0]}
