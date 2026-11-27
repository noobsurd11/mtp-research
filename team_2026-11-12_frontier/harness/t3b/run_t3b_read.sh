#!/bin/bash
# The read of the T3b opening (E1 opening #9; T3B_RULE.md section 8), on gaint CPU (nice 19, at most 8 workers). Run by the
# LEAD ONCE, after the relay of t3bopen says RELAY ALL DONE: 30 of 30 (the registered read; a repeat needs TAG).
# Every check runs before the output folder is created, so a refusal leaves nothing behind. Refuses unless:
#   - REG_MD5 = md5 of IO/REGISTERED.txt = IO/REGISTERED.md5; it names opening #9 e1_open9_t3b, this T3B_RULE.md's md5, the
#     lists, jobs_dump.txt's md5, commit K, and the zs file whose md5 = IO/reg/zs.tsv; TEST MODE only with TEST_MODE=1 and back;
#   - the read worktree RT (default the K worktree /home/noob/work/bench_wt_t3b) is at K with no tracked change;
#   - the E1 image, mask and ignore files still match reg/e1_files.md5 (the registered hashes);
#   - the 30 T3b dumps are relayed in RD2 (.ok + 'relayed' line + the dump folder); the 3 zero-shot units of opening #8 in RD_OPEN
#     still match reg/zs.tsv (.ok md5) and pass md5sum -c of their RUN.md5;
#   - every manifest: T3b dumps run_id = job name, set e1t3b_f<k> sealed at e1_open9_t3b, seed, weights_key swad, step 20000,
#     fp32, tta d4, trained_on_e1 true with the root's E1 count, no ens_member, writer = K's bench_infer.py, train_code_revision
#     = K, checkpoint_md5 = the LATEST.md5 relayed from t3b (RD1) for that run, list md5 of the fold; zero-shot dumps run_id,
#     set e1_106 sealed at e1_open8_final, seed 5 / 6 / 7, swad, step 20000, fp32, d4, ens_member true, no trained_on_e1, writer
#     G's bench_infer.py, train_code_revision F2, checkpoint_md5 = fin2's relayed LATEST.md5 (RF); one GPU model over all 33.
# Then (log O/run.log): records (K's bench_score: 30 fold dumps on their e1t3b sets, the 3 zero-shot dumps on e1_106), the
# zero-shot records compared cell by cell with opening #8's records (bench_score compare; information), the 6 out-of-fold
# records (bench_t3b_oof.py), the read (bench_open_read.py --t3b ZS: ALL, HALF, ZS; pairs ZS=ALL, ZS=HALF, HALF=ALL; strata),
# the verdict (t3b_verdict.py), MD5.txt, the line 'T3B READ ALL DONE'.
# Round 1: B2 the read refuses unless its own md5 and t3b_verdict.py's are those of the registration's 'scripts' line; N4 a
#   PINS_FILE may hold only K=, F2=, W_K= and W_G= assignments (checked before it is sourced); N5 TAG must be [a-z0-9_]+ and a
#   TAG read prints 'REPEAT (TAG ...), not the registered read' in run.log and in the verdict header.
# Env: REG_MD5 (required), TAG (repeat), SHOW=1. Test-only overrides: IO, RD1, RD2, RD_OPEN, RF, READ_ROOT, RT, BENCH_EXT,
#   CELLS_TSV, OPEN8_RECORDS, PINS_FILE, DEVICE_OK. If any is set the read refuses unless TEST_MODE=1; with TEST_MODE=1 IO,
#   RD1, RD2, RD_OPEN, RF, READ_ROOT, BENCH_EXT, CELLS_TSV and OPEN8_RECORDS must be set, absolute and resolve under
#   /home/noob/work/bench_int_io (guard below, before any read, hash or mkdir).
set -u
set -f
OV=""; for v in IO RD1 RD2 RD_OPEN RF READ_ROOT RT BENCH_EXT CELLS_TSV OPEN8_RECORDS PINS_FILE DEVICE_OK; do [ -n "${!v+x}" ] && OV="$OV $v=${!v}"; done
if [ -n "$OV" ] && [ "${TEST_MODE:-0}" != 1 ]; then echo "REFUSED: test-only overrides set:$OV (unset them; TEST_MODE=1 only for dry runs)"; exit 1; fi
SCR_ROOT=/home/noob/work/bench_int_io
tm_no(){ echo "REFUSED (TEST_MODE guard): $*"; exit 1; }
tm_in(){ local r; case "$1" in /*) ;; *) tm_no "$1 is not an absolute path";; esac; r=$(readlink -m -- "$1"); case "$r/" in "$SCR_ROOT"/*/*) ;; *) tm_no "$1 resolves to $r, outside $SCR_ROOT";; esac; }
if [ "${TEST_MODE:-0}" = 1 ]; then
  for v in IO RD1 RD2 RD_OPEN RF READ_ROOT BENCH_EXT CELLS_TSV OPEN8_RECORDS; do [ -n "${!v+x}" ] && [ -n "${!v}" ] || tm_no "$v must be set explicitly to a path under $SCR_ROOT (its default is a production path)"; done
  for p in "$IO" "$RD1" "$RD2" "$RD_OPEN" "$RF" "$READ_ROOT" "$BENCH_EXT" "$BENCH_EXT/stems_eval.txt" "$BENCH_EXT/images" "$BENCH_EXT/masks" "$BENCH_EXT/ignore" "$CELLS_TSV" "$OPEN8_RECORDS"; do tm_in "$p"; done
  for d in "$IO" "$RD1" "$RD2" "$RD_OPEN" "$RF" "$BENCH_EXT" "$OPEN8_RECORDS"; do [ -d "$d" ] || continue; for l in $(find "$d" -type l 2>/dev/null); do tm_in "$l"; done; done
fi
SHOW=${SHOW:-0}; TAG=${TAG:-}
case "$TAG" in '') ;; *[!a-z0-9_]*) echo "REFUSED: TAG must be [a-z0-9_]+"; exit 1;; esac
ME=$(readlink -f "$0"); HERE=$(dirname "$ME")
P=/home/noob/work/el-fault-detection/.venv/bin/python
IO=${IO:-/home/noob/work/bench_t3b_io}
RD1=${RD1:-/mnt/nas/noob_el_archive/bench_relay/t3b}; RD2=${RD2:-/mnt/nas/noob_el_archive/bench_relay/t3bopen}
RD_OPEN=${RD_OPEN:-/mnt/nas/noob_el_archive/bench_relay/open}; RF=${RF:-/mnt/nas/noob_el_archive/bench_relay/fin2}
RT=${RT:-/home/noob/work/bench_wt_t3b}; RD0=${READ_ROOT:-/home/noob/work/bench_reads}
OPEN8_RECORDS=${OPEN8_RECORDS:-/home/noob/work/bench_reads/open_final/records/set}
export BENCH_EXT=${BENCH_EXT:-/home/noob/work/el_f1/reports/f1/ext117}
CELLS_TSV=${CELLS_TSV:-/home/noob/work/bench_data/meta/cells.tsv}
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
# ---- pins (the build fills them; the reviewer checks them)
K=cba7fbdf5df1579d6efb1168eb292e637bc9fad6; F2=9967d59abaab03cef83c1e3014840b2359ef45d7
W_K="bench_infer.py 149e2a633094e94343cb729dbd570557"; W_G="bench_infer.py a3268638d91937223433cd88d2d97df6"
if [ -n "${PINS_FILE:-}" ]; then   # round 1 N4: only the four pin assignments, checked before sourcing
  tm_in "$PINS_FILE"
  grep -vE '^(K|F2)=[0-9a-f]{40}$|^W_(K|G)="bench_infer\.py [0-9a-f]{32}"$' "$PINS_FILE" | grep -q . && { echo "REFUSED: PINS_FILE holds other lines than K=, F2=, W_K=, W_G="; exit 1; }
  . "$PINS_FILE"; fi
MX=hrnet_w18_unetpp_swad_const_pf_v11; OPENING=e1_open9_t3b
ZS="fin_hrnet_swad_v11_pool_s5.swad.tta_d4.e1_106 fin_hrnet_swad_v11_pool_s6.swad.tta_d4.e1_106 fin_hrnet_swad_v11_pool_s7.swad.tta_d4.e1_106"
O=$RD0/t3b_open9${TAG:+_$TAG}
no(){ echo "REFUSED: $*"; exit 1; }
if [ "$SHOW" = 1 ]; then echo "SHOW=1: records (30 T3b, 3 ZS) -> compare ZS with opening #8 -> bench_t3b_oof (6) -> bench_open_read --t3b ZS -> t3b_verdict.py; out $O"; exit 0; fi
REG_MD5=${REG_MD5:?REG_MD5: the md5 of REGISTERED.txt logged in the ledger}
[ -s $IO/REGISTERED.txt ] || no "no $IO/REGISTERED.txt"
[ "$(md5sum < $IO/REGISTERED.txt | cut -c1-32)" = "$REG_MD5" ] && [ "$(cat $IO/REGISTERED.md5)" = "$REG_MD5" ] || no "REGISTERED.txt md5 != REG_MD5"
if head -1 $IO/REGISTERED.txt | grep -q '^TEST MODE'; then [ "${TEST_MODE:-0}" = 1 ] || no "the registration is a TEST MODE dry run"
else [ "${TEST_MODE:-0}" != 1 ] || no "TEST_MODE=1 against a real registration"; fi
[ "${TEST_MODE:-0}" = 1 ] && echo "TEST MODE (dry run; overrides:${OV:- none}): not the registered read"
grep -q "^opening_e1 E1 opening #9 $OPENING " $IO/REGISTERED.txt || no "the registration names another opening"
grep -q "^rule T3B_RULE.md $(md5sum < $HERE/T3B_RULE.md | cut -c1-32)\$" $IO/REGISTERED.txt || no "T3B_RULE.md is not the registered file"
grep -q "^lists LISTS.md5 $(md5sum < $IO/reg/lists/LISTS.md5 | cut -c1-32)\$" $IO/REGISTERED.txt && (cd $IO/reg/lists && md5sum -c --quiet LISTS.md5) || no "lists differ from the registration"
grep -q "^jobs_dump $(md5sum < $IO/jobs_dump.txt | cut -c1-32) 30 lines" $IO/REGISTERED.txt || no "jobs_dump.txt is not the registered list"
grep -q "^commits K $K " $IO/REGISTERED.txt || no "the registration names another K than $K"
grep -q "^zs $(md5sum < $IO/reg/zs.tsv | cut -c1-32) " $IO/REGISTERED.txt || no "reg/zs.tsv is not the registered file"
grep "^scripts " $IO/REGISTERED.txt | grep -qF " run_t3b_read.sh=$(md5sum < $ME | cut -c1-32) " || no "run_t3b_read.sh is not the registered script (REGISTERED.txt scripts line)"
grep "^scripts " $IO/REGISTERED.txt | grep -qF " t3b_verdict.py=$(md5sum < $HERE/t3b_verdict.py | cut -c1-32) " || no "t3b_verdict.py is not the registered script (REGISTERED.txt scripts line)"
cd $RT || no "no $RT"
[ "$(git rev-parse HEAD)" = "$K" ] || no "read worktree $RT is not at K"
[ "$(git status --porcelain -uno | wc -l)" = 0 ] || no "tracked changes in $RT"
[ -e $O ] && no "output folder exists: $O"
[ "$CELLS_TSV" != /home/noob/work/bench_data/meta/cells.tsv ] || [ "$(md5sum < $CELLS_TSV | cut -c1-8)" = a50521b4 ] || no "cells.tsv is not a50521b4"
(cd $BENCH_EXT && md5sum -c --quiet $IO/reg/e1_files.md5 > /dev/null 2>&1) || no "E1 image / mask / ignore files differ from the registration"
grep -q "^e1_files $(md5sum < $IO/reg/e1_files.md5 | cut -c1-32)\$" $IO/REGISTERED.txt || no "reg/e1_files.md5 is not the registered file"
# ---- relayed dumps (rows: name|set|dump dir|seed|kind|run|e1n)
ROWS=""; MISS=""
while IFS='|' read -r name card seed root fold gate dgate logp extra; do
  set -- $extra; run=$(basename $2); st=$8
  e1n=$(grep -c . $IO/reg/lists/e1t3b_f$fold.txt); case $run in t3b_all_*) e1n=$((106 - e1n));; t3b_half_*) e1n=$(grep -c . $IO/reg/lists/t3b_half_f$fold.txt);; esac
  d=$RD2/$name/dumps/elbench1/$MX/$name/$st
  if [ -e $RD2/.ok/$name ] && grep -q "relayed $name:" $RD2/relay.log 2>/dev/null && [ -f $d/manifest.json ]; then
    ROWS="$ROWS$name|$st|$d|$seed|t3b|$run|$e1n
"; else MISS="$MISS $name"; fi
done < $IO/jobs_dump.txt
[ -z "$MISS" ] || no "$(echo $MISS | wc -w) T3b dumps not relayed:$MISS"
for n in $ZS; do
  w=$(awk -v n=$n -F'\t' '$1 == n {print $2}' $IO/reg/zs.tsv); m=$(awk '{print $4}' $RD_OPEN/.ok/$n 2>/dev/null)
  [ -n "$w" ] && [ "$m" = "$w" ] && [ "$(md5sum < $RD_OPEN/$n/runs/$n/RUN.md5 | cut -c1-32)" = "$w" ] || no "zero-shot unit $n differs from the registration"
  (cd $RD_OPEN/$n && md5sum -c --quiet runs/$n/RUN.md5 > /dev/null 2>&1) || no "zero-shot unit $n: md5sum -c of its relayed files failed"
  s=${n#fin_hrnet_swad_v11_pool_s}; s=${s%%.*}
  ROWS="$ROWS$n|e1_106|$RD_OPEN/$n/dumps/elbench1/$MX/$n/e1_106|$s|zs|fin_hrnet_swad_v11_pool_s$s|0
"
done
[ "$(printf '%s' "$ROWS" | grep -c .)" = 33 ] || no "expected 33 dumps"
MC=$($P - /dev/fd/3 "$RD1" "$RF" "$W_K" "$W_G" "$K" "$F2" "${DEVICE_OK:-}" 3< <(printf '%s' "$ROWS") <<'EOF'
import json, sys
from pathlib import Path
rows = [l.rstrip("\n").split("|") for l in open(sys.argv[1]) if l.strip()]
RD1, RF, WK, WG, K, F2, devok = sys.argv[2:9]
D4 = {"mode": "d4", "scales": [1.0], "d4": True, "views": 8}
T3B = {"e1t3b_f0": ("9581b3e2bfe2eb0b784d4eb62469e2a0", 22), "e1t3b_f1": ("c1e8bcf53a38c226fe70c44c624ad713", 22),
       "e1t3b_f2": ("5067b76be191afddcbf0daeed6947d13", 20), "e1t3b_f3": ("92f8e87da504e18e8b735a2ed50290b6", 21),
       "e1t3b_f4": ("60aa7c33e0a1a173e529873ab51797d0", 21)}
bad, dev = [], set()
def latest(base, run):
    p = Path(base) / run / "runs" / run / "LATEST.md5"
    return p.read_text().split()[0] if p.exists() else "NO LATEST.md5"
for name, st, d, seed, kind, run, e1n in rows:
    m = json.loads((Path(d) / "manifest.json").read_text())
    want = {"run_id": name, "set": st, "set_kind": "sealed", "seed": int(seed), "weights_key": "swad", "step": 20000,
            "precision": "fp32", "tta": D4, "method": "hrnet_w18_unetpp_swad_const_pf_v11"}
    if kind == "t3b":
        want.update({"opening": "e1_open9_t3b", "writer": WK, "train_code_revision": K, "checkpoint_md5": latest(RD1, run),
                     "trained_on_e1": True, "e1_train_cells": int(e1n), "list_md5": T3B[st][0], "n_cells": T3B[st][1]})
        if "ens_member" in m:
            bad.append(f"{name}: ens_member present")
    else:
        want.update({"opening": "e1_open8_final", "writer": WG, "train_code_revision": F2, "checkpoint_md5": latest(RF, run),
                     "ens_member": True, "list_md5": "5266806b559f74bcf9eae167bb076b95", "n_cells": 106})
        if "trained_on_e1" in m:
            bad.append(f"{name}: a zero-shot dump carries trained_on_e1")
    bad += [f"{name}: {k} = {m.get(k)!r}, expected {v!r}" for k, v in want.items() if m.get(k) != v]
    dev.add(str(m.get("device")))
if len(dev) != 1 or (("cpu" in dev) and devok != "cpu"):
    bad.append(f"devices over the dumps: {sorted(dev)} (one GPU model expected)")
print(f"manifest check: {len(rows)} dumps (30 T3b, 3 zero-shot), device {sorted(dev)}: {'OK' if not bad else 'FAIL'}")
for b in bad[:20]:
    print("  " + b)
sys.exit(1 if bad else 0)
EOF
) || { echo "$MC"; no "manifest check failed (nothing written; $O not created)"; }
# ---- the read (everything below writes under O only)
mkdir -p $O/records/t3b $O/records/zs $O/records/oof $O/subsets || exit 1
printf '%s' "$ROWS" > $O/expected_dumps.tsv
recs(){ nice -n 19 $P scripts/bench_score.py records --dumps $3 --set $2 --opening $4 --out $O/records/$5/$1.json > /dev/null || echo "FAIL records $1"; }
{
  echo "[$(date '+%F %T')] T3b read start (out $O; 33 dumps; REGISTERED $REG_MD5; script $(md5sum < $ME | cut -c1-8); rule $(md5sum < $HERE/T3B_RULE.md | cut -c1-8); K $K; relays $RD2, $RD_OPEN)"
  [ "${TEST_MODE:-0}" = 1 ] && echo "TEST MODE (dry run; overrides:${OV:- none}): NOT the registered read"
  [ -n "$TAG" ] && echo "REPEAT (TAG $TAG), not the registered read"
  echo "$MC"
  JOBS=()
  while IFS='|' read -r name st d seed kind run e1n; do
    if [ $kind = t3b ]; then JOBS+=("$name $st $d $OPENING t3b"); else JOBS+=("$name e1_106 $d e1_open8_final zs"); fi
  done < $O/expected_dumps.tsv
  export -f recs; export O P
  printf '%s\n' "${JOBS[@]}" | xargs -P 8 -L 1 bash -c 'recs "$@"' _ | tee $O/records_fail.txt
  [ -s $O/records_fail.txt ] && { echo "records failed"; exit 1; }
  echo "[$(date '+%F %T')] records: $(ls $O/records/t3b | wc -l) T3b fold records, $(ls $O/records/zs | wc -l) zero-shot records"
  for n in $ZS; do   # information: the zero-shot comparator re-scored by K = opening #8's records (R), cell by cell
    if [ -s $OPEN8_RECORDS/$n.json ]; then echo "zero-shot re-score vs opening #8 $n: $(nice -n 19 $P scripts/bench_score.py compare --a $OPEN8_RECORDS/$n.json --b $O/records/zs/$n.json | cut -c1-120)"
    else echo "zero-shot re-score vs opening #8 $n: opening #8 record not found (not compared)"; fi
  done
  for arm in all half; do for s in 5 6 7; do
    L=$(for k in 0 1 2 3 4; do printf '%s,' $O/records/t3b/t3b_${arm}_f${k}_s$s.swad.tta_d4.e1t3b_f$k.json; done)
    nice -n 19 $P scripts/bench_t3b_oof.py --arm $arm --seed $s --records ${L%,} --out $O/records/oof/t3b_${arm}_s$s.oof.json || { echo "oof $arm $s failed"; exit 1; }
  done; done
  awk -F'\t' 'NR > 1 && $2 == "halfcut+scuff" {print $1}' $IO/reg/lists/t3b_strata.tsv > $O/subsets/hard.txt
  awk -F'\t' 'NR > 1 && $2 == "halfcut" {print $1}' $IO/reg/lists/t3b_strata.tsv > $O/subsets/halfcut_noscuff.txt
  awk -F'\t' 'NR > 1 && $2 ~ /^full/ {print $1}' $IO/reg/lists/t3b_strata.tsv > $O/subsets/full.txt
  awk -F'\t' 'NR > 1 && $2 ~ /^halfcut/ {print $1}' $IO/reg/lists/t3b_strata.tsv > $O/subsets/halfcut.txt
  echo "strata (lists/t3b_strata.tsv): full $(grep -c . $O/subsets/full.txt), half-cut $(grep -c . $O/subsets/halfcut.txt) (of which hard = half-cut + scuff $(grep -c . $O/subsets/hard.txt), half-cut without scuff $(grep -c . $O/subsets/halfcut_noscuff.txt))"
  set +f
  A=$(ls $O/records/oof/t3b_all_s*.oof.json | LC_ALL=C sort | paste -sd,); H=$(ls $O/records/oof/t3b_half_s*.oof.json | LC_ALL=C sort | paste -sd,)
  Z=$(ls $O/records/zs/*.json | LC_ALL=C sort | paste -sd,)
  set -f
  nice -n 19 $P scripts/bench_open_read.py --set e1_106 --arm "ALL=$A" --arm "HALF=$H" --arm "ZS=$Z" --pair ZS=ALL --pair ZS=HALF --pair HALF=ALL \
    --t3b ZS --celltypes $CELLS_TSV --subset strat_full=$O/subsets/full.txt --subset strat_halfcut=$O/subsets/halfcut.txt \
    --subset strat_hard=$O/subsets/hard.txt --subset strat_halfcut_noscuff=$O/subsets/halfcut_noscuff.txt --boot 2000 --out $O/read_t3b || { echo "T3b read failed"; exit 1; }
  nice -n 19 $P $HERE/t3b_verdict.py --read $O/read_t3b/read.json --reg $IO/REGISTERED.txt ${TAG:+--repeat $TAG} --out $O/verdict.txt; rc=$?
  set +f; ( cd $O && md5sum read_t3b/read.json read_t3b/read.txt verdict.txt verdict.json records/oof/*.json 2>/dev/null > MD5.txt ); set -f
  md5sum $ME $HERE/t3b_verdict.py $HERE/T3B_RULE.md $RT/scripts/bench_open_read.py $RT/scripts/bench_score.py $RT/scripts/bench_t3b_oof.py $IO/REGISTERED.txt | sed 's/  /  input: /' >> $O/MD5.txt
  echo "[$(date '+%F %T')] T3B READ ALL DONE (verdict rc $rc); tracked changes in $RT: $(git status --porcelain -uno | wc -l)"
  exit $rc
} 2>&1 | tee $O/run.log
exit ${PIPESTATUS[0]}
