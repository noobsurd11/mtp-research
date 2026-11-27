#!/bin/bash
# c3swad read on gaint CPU (builder, 17 Nov 2026; LAUNCH_REQUEST_c3swad.md section 7, fixed before any cv5v3 swad number).
# Modelled on harness/w1read/run_read_c3_s5.sh (links, refusals) and harness/w2a/read/run_read_w2a.sh (manifest check).
# NOT to be run before the independent review; the lead runs it once, when all 50 runs are relayed.
#   Tools: the reviewed read tree bench_wt_final at 89b9ea5 (scripts/bench_read_w1.py fdb56b78), unchanged.
#   Arms (cv02 runs only, relayed, checksums equal):
#     PF      c3_pf_v11_f[0-4]_s[5-9]            (relay c3base; comparator and baseline)
#     SWADBN  c3s_swad_v11_f[0-4]_s[5-9]         (relay c3swad; readout swad_bn = the card's weights_key; declared primary)
#     SWAD    c3s_swad_v11_f[0-4]_s[5-9]\.swad   (relay c3swad; readout swad; declared secondary)
#   Pairs: PF=SWADBN (primary), PF=SWAD (declared secondary). No other swad contrast is read.
#   Margin M: --aa PF:5,6:7,8 on the same PF dumps in the same read (seed 9 is not in the A/A); M = max(0.01, 2 x SE)
#     at argmax, computed by the tool for the 532 cells and again for the 416 clean cells.
#   Cells: all 532 and the 416 clean cells (--score-exclude benchmark/splits/score_exclude_v3.txt) in one run.
#   Groups: --groups bench_data_v3b/meta/cv5v3_groups.tsv (every cv5v3 read needs it).
# Every check below runs before the output folder is created, so a refusal leaves no folder behind.
# Refuses unless: the worktree is at 89b9ea5 with no tracked change and the read tool is fdb56b78; the output folder is
#   new; all 25 PF and all 25 swad runs are relayed (.ok file and 'relayed' log line) with their dump folders (PF 1, swad 2)
#   and enc_probe.jsonl; every manifest names the expected run id, fold, seed, weights key, step 20000, set, fp32, the
#   train code revision 89b9ea5 and one single device over all 75 dumps.
# After the read: per-class table (c3swad_class_guard.py) and the registered rule applied by c3swad_verdict.py
#   (verdict.txt: every criterion with its value, per-seed differences, layer3 / layer4 cosine at 20k).
# Variables: SHOW=1 prints the read command and exits (no check of relays, nothing written). TAG = suffix of the output
#   folder for a repeat (bench_reads/c3swad_<TAG>); the first read without TAG is the registered one.
# CPU only, nice 19, 8 workers.
set -u
set -f
SHOW=${SHOW:-0}; TAG=${TAG:-}
ME=$(readlink -f "$0"); HERE=$(dirname "$ME")
T=/home/yugma/mtp/research/team_2026-11-12_frontier
RT=/home/noob/work/bench_wt_final
cd $RT || exit 1
[ "$(git rev-parse --short HEAD)" = 89b9ea5 ] || { echo "worktree not at 89b9ea5"; exit 1; }
[ "$(git status --porcelain -uno | wc -l)" = 0 ] || { echo "tracked changes in $RT"; exit 1; }
[ "$(md5sum < scripts/bench_read_w1.py | cut -c1-8)" = fdb56b78 ] || { echo "bench_read_w1.py is not fdb56b78"; exit 1; }
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
X=$T/benchmark/splits/score_exclude_v3.txt
G3=/home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv
[ "$(md5sum < $X | cut -c1-8)" = 6d48dfbd ] || { echo "score_exclude_v3.txt is not 6d48dfbd"; exit 1; }
[ "$(md5sum < $G3 | cut -c1-8)" = d880a769 ] || { echo "cv5v3_groups.tsv is not d880a769"; exit 1; }
RDP=/home/noob/work/bench_relay/c3base; RDS=/home/noob/work/bench_relay/c3swad
MP=house_r34_unetpp_pf_v11; MS=swad_const_pf_v11
O=/home/noob/work/bench_reads/c3swad${TAG:+_$TAG}; L=$O/links/elbench1
A=(--arm "PF=$L/$MP:c3_pf_v11_f[0-4]_s[5-9]" --arm "SWADBN=$L/$MS:c3s_swad_v11_f[0-4]_s[5-9]" --arm "SWAD=$L/$MS:c3s_swad_v11_f[0-4]_s[5-9]\.swad")
PR=(--pair PF=SWADBN --pair PF=SWAD)
CMD="scripts/bench_read_w1.py ${A[*]} ${PR[*]} --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa PF:5,6:7,8 --groups $G3 --score-exclude $X --out $O/read"
[ "$SHOW" = 1 ] && { echo "SHOW=1 (no check of relays, nothing run, nothing written)"; echo "$CMD"; exit 0; }
[ -e $O ] && { echo "output folder exists: $O"; exit 1; }

# ---- all 50 runs relayed, with their dump folders; rows: link name, relayed dump dir, run id, fold, seed, weights key
ROWS=""; MISS=""
for s in 5 6 7 8 9; do for k in 0 1 2 3 4; do
  r=c3_pf_v11_f${k}_s$s; d=$RDP/$r/dumps/elbench1/$MP/$r
  if [ -e $RDP/.ok/$r ] && grep -q "relayed $r:" $RDP/relay.log && [ -f $d/cv5v3_f$k/manifest.json ]; then ROWS="$ROWS$MP/$r|$d|$r|$k|$s|model
"; else MISS="$MISS $r"; fi
  r=c3s_swad_v11_f${k}_s$s; d=$RDS/$r/dumps/elbench1/$MS
  if [ -e $RDS/.ok/$r ] && grep -q "relayed $r:" $RDS/relay.log 2>/dev/null && [ -f $d/$r/cv5v3_f$k/manifest.json ] \
     && [ -f $d/$r.swad/cv5v3_f$k/manifest.json ] && [ -s $RDS/$r/experiments/$r/enc_probe.jsonl ]; then
    ROWS="$ROWS$MS/$r|$d/$r|$r|$k|$s|swad_bn
$MS/$r.swad|$d/$r.swad|$r.swad|$k|$s|swad
"; else MISS="$MISS $r"; fi
done; done
[ -z "$MISS" ] || { echo "REFUSED: $(echo $MISS | wc -w) of 50 runs not relayed (or a dump folder or enc_probe.jsonl is missing):$MISS"; exit 1; }
[ "$(printf '%s' "$ROWS" | grep -c .)" = 75 ] || { echo "REFUSED: expected 75 dump folders (25 PF, 25 swad_bn, 25 swad)"; exit 1; }

# ---- manifests of all 75 dumps, BEFORE anything is written: a refused read must not use up the registered output folder
MC=$($P - /dev/fd/3 3< <(printf '%s' "$ROWS") <<'EOF'
import json, sys
from pathlib import Path
rows = [l.rstrip("\n").split("|") for l in open(sys.argv[1]) if l.strip()]
dev, bad = set(), []
for ln, d, rid, k, s, key in rows:
    m = json.loads((Path(d) / f"cv5v3_f{k}" / "manifest.json").read_text())
    want = {"run_id": rid, "fold": int(k), "seed": int(s), "weights_key": key, "step": 20000, "set": f"cv5v3_f{k}",
            "precision": "fp32", "set_kind": "open"}
    bad += [f"{d}: {x} = {m.get(x)!r}, expected {v!r}" for x, v in want.items() if m.get(x) != v]
    if not str(m.get("train_code_revision", "")).startswith("89b9ea5"):
        bad.append(f"{d}: train_code_revision {m.get('train_code_revision')}")
    dev.add(m["device"])
if len(dev) != 1 or "cpu" in dev:
    bad.append(f"devices over PF and swad dumps: {sorted(dev)} (one GPU model expected)")
print(f"manifest check: {len(rows)} dumps, device {sorted(dev)}: {'OK' if not bad else 'FAIL'}")
for b in bad[:20]:
    print("  " + b)
sys.exit(1 if bad else 0)
EOF
) || { echo "$MC"; echo "REFUSED: manifest check failed (nothing written, $O not created)"; exit 1; }
mkdir -p $L/$MP $L/$MS || exit 1
printf '%s' "$ROWS" > $O/expected_dumps.tsv
while IFS='|' read -r ln d rid k s key; do ln -s $d $L/$ln || { echo "link failed: $ln"; exit 1; }; done < $O/expected_dumps.tsv
{
  echo "[$(date '+%F %T')] c3swad read start (out $O; 50 runs, 75 dump folders linked; script $(md5sum < $ME | cut -c1-8))"
  echo "$MC"
  echo "command (cwd $RT, nice -n 19): $CMD"
  nice -n 19 $P scripts/bench_read_w1.py "${A[@]}" "${PR[@]}" --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa PF:5,6:7,8 \
    --groups $G3 --score-exclude $X --out $O/read; rc=$?
  echo "[$(date '+%F %T')] read rc=$rc"
  if [ $rc = 0 ]; then
    nice -n 19 $P $HERE/c3swad_class_guard.py --read $O --out $O/class_guard.txt --classes 13,16,20,11 --baseline PF; echo "class guard rc=$?"
    nice -n 19 $P $HERE/c3swad_verdict.py --read $O --probes $RDS --out $O/verdict.txt; echo "verdict rc=$?"
  fi
  set +f; ( cd $O/read 2>/dev/null && md5sum read*.txt read.json > $O/MD5.txt ); ( cd $O && md5sum class_guard.txt verdict.txt >> $O/MD5.txt 2>/dev/null ); set -f
  { md5sum $ME $HERE/c3swad_class_guard.py $HERE/c3swad_verdict.py $RT/scripts/bench_read_w1.py $X $G3 | sed 's/  /  input: /'; } >> $O/MD5.txt
  echo "[$(date '+%F %T')] C3SWAD READ ALL DONE (rc $rc); tracked changes: bench_wt_final $(git status --porcelain -uno | wc -l)"
  exit $rc
} 2>&1 | tee $O/run.log
exit ${PIPESTATUS[0]}
