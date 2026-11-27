#!/bin/bash
# c3x read on gaint CPU (LAUNCH_REQUEST_c3x.md section 6, fixed before any c3x run exists) = harness/c3swad/run_read_c3swad.sh
# (10ed79a6) with the arms, pairs, relays and manifest expectations of the c3x read. NOT to be run before the independent
# review; the lead runs it ONCE, when all 25 c3x runs and the full PF, HRNet and swad arms are relayed (ruling C1: one
# registered read of all 5 seeds, no earlier look).
#   Tools: the reviewed read tree bench_wt_final at 89b9ea5 (scripts/bench_read_w1.py fdb56b78), unchanged.
#   Arms (cv02 runs only, relayed, checksums equal; seeds 5 to 9, folds 0 to 4, cv5v3):
#     PF          c3_pf_v11_f[0-4]_s[5-9]                (relay c3base; comparator, baseline, A/A)
#     HRNET       c3h_hrnet_w18_unetpp_pf_f[0-4]_s[5-9]  (relay c3hrnet; readout model)
#     SWADBN      c3s_swad_v11_f[0-4]_s[5-9]             (relay c3swad; readout swad_bn)
#     COMBO       c3x_hrnet_swad_v11_f[0-4]_s[5-9]       (relay c3x; readout swad_bn = the card's weights_key; primary)
#     COMBO_SWAD  c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad (relay c3x; readout swad = COMBO.swad; declared secondary)
#   Pairs: PF=COMBO (primary), PF=COMBO_SWAD (carry), HRNET=COMBO, HRNET=COMBO_SWAD, SWADBN=COMBO, SWADBN=COMBO_SWAD (the four
#     pre-declared secondary contrasts). No other contrast is read.
#   Margin M: --aa PF:5,6:7,8 on the same PF dumps in the same read (seed 9 not in the A/A); M = max(0.01, 2 x SE) at argmax,
#     computed by the tool for the 532 cells and again for the 416 clean cells.
#   Cells: all 532 and the 416 clean cells (--score-exclude benchmark/splits/score_exclude_v3.txt) in one run.
#   Groups: --groups bench_data_v3b/meta/cv5v3_groups.tsv.
# Every check below runs before the output folder is created, so a refusal leaves no folder behind.
# Refuses unless: the worktree is at 89b9ea5 with no tracked change and the read tool is fdb56b78; C3X (env, the full c3x
#   commit) is the c3x commit on 852ed5c with the pinned tree and its diff to 89b9ea5 is the 9 paths of the code proof; the
#   output folder is new; all 100 runs are relayed (.ok file and 'relayed' log line) with their dump folders (c3x 2) and,
#   for c3x, enc_probe.jsonl; every manifest names the expected run id, fold, seed, weights key, step 20000, set, fp32, open
#   set, the train code revision (89b9ea5 for PF, HRNET, SWADBN; C3X for COMBO and COMBO_SWAD), and over all 125 dumps one
#   single device and one single writer (bench_infer.py md5: the dump code is byte-equal in both deploys).
# After the read: per-class table (c3x_class_guard.py = c3swad_class_guard.py unchanged) and the registered rule applied by
#   c3x_verdict.py (verdict.txt: primary, carry, the four secondary contrasts, the final-model rule, per-seed differences,
#   encoder cosine at 20k).
# Variables: SHOW=1 prints the read command and exits (no check, nothing written). TAG = suffix of the output folder for a
#   repeat (bench_reads/c3x_<TAG>); the first read without TAG is the registered one.
#   Tests only: RELAY_ROOT, READ_ROOT, C3X_REPO, STUB (a command run instead of the read tool, the class guard and the verdict).
# CPU only, nice 19, 8 workers.
set -u
set -f
SHOW=${SHOW:-0}; TAG=${TAG:-}
ME=$(readlink -f "$0"); HERE=$(dirname "$ME")
T=/home/yugma/mtp/research/team_2026-11-12_frontier
RT=/home/noob/work/bench_wt_final
OLD=89b9ea5a12a37a87c16c4868cc4adf00794a7610; BASE=852ed5c411b967d7ea758ef2cd5dbe70ae4e50a1; TREE=c860f1bc243ff5262f8c23ffb1e551cfaea5ea79
RR=${RELAY_ROOT:-/home/noob/work/bench_relay}; RD0=${READ_ROOT:-/home/noob/work/bench_reads}
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
XCL=$T/benchmark/splits/score_exclude_v3.txt
G3=/home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv
RDP=$RR/c3base; RDH=$RR/c3hrnet; RDS=$RR/c3swad; RDX=$RR/c3x
MP=house_r34_unetpp_pf_v11; MH=hrnet_w18_unetpp_pf_v11; MS=swad_const_pf_v11; MX=hrnet_w18_unetpp_swad_const_pf_v11
O=$RD0/c3x${TAG:+_$TAG}; L=$O/links/elbench1
A=(--arm "PF=$L/$MP:c3_pf_v11_f[0-4]_s[5-9]" --arm "HRNET=$L/$MH:c3h_hrnet_w18_unetpp_pf_f[0-4]_s[5-9]"
   --arm "SWADBN=$L/$MS:c3s_swad_v11_f[0-4]_s[5-9]" --arm "COMBO=$L/$MX:c3x_hrnet_swad_v11_f[0-4]_s[5-9]"
   --arm "COMBO_SWAD=$L/$MX:c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad")
PR=(--pair PF=COMBO --pair PF=COMBO_SWAD --pair HRNET=COMBO --pair HRNET=COMBO_SWAD --pair SWADBN=COMBO --pair SWADBN=COMBO_SWAD)
CMD="scripts/bench_read_w1.py ${A[*]} ${PR[*]} --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa PF:5,6:7,8 --groups $G3 --score-exclude $XCL --out $O/read"
[ "$SHOW" = 1 ] && { echo "SHOW=1 (no check of relays, nothing run, nothing written)"; echo "$CMD"; exit 0; }
cd $RT || exit 1
[ "$(git rev-parse --short HEAD)" = 89b9ea5 ] || { echo "worktree not at 89b9ea5"; exit 1; }
[ "$(git status --porcelain -uno | wc -l)" = 0 ] || { echo "tracked changes in $RT"; exit 1; }
[ "$(md5sum < scripts/bench_read_w1.py | cut -c1-8)" = fdb56b78 ] || { echo "bench_read_w1.py is not fdb56b78"; exit 1; }
[ "$(md5sum < $XCL | cut -c1-8)" = 6d48dfbd ] || { echo "score_exclude_v3.txt is not 6d48dfbd"; exit 1; }
[ "$(md5sum < $G3 | cut -c1-8)" = d880a769 ] || { echo "cv5v3_groups.tsv is not d880a769"; exit 1; }
C3X=${C3X:?full c3x commit}
GX=${C3X_REPO:-$RT}     # C3X_REPO: tests only (a scratch clone that holds the commit)
[ "$(git -C $GX rev-parse $C3X^ 2>/dev/null)" = $BASE ] && [ "$(git -C $GX rev-parse $C3X^{tree} 2>/dev/null)" = $TREE ] || { echo "C3X is not the c3x commit on 852ed5c with tree $TREE"; exit 1; }
[ "$(git -C $GX diff --name-only $OLD $C3X | tr '\n' ' ')" = "bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml bench/methods_cv02/swad_const_pf_v11.yaml bench/q/cv02/cq.sh bench/q/cv02/cq_rescue.sh bench/q/cv02/cq_setup.sh bench/q/cv02/slim_ckpt.py tests/test_bench_c3x_card.py tests/test_bench_cq_readouts.py " ] || { echo "89b9ea5 -> C3X differs in other paths than the 9 of the code proof"; exit 1; }
[ -e $O ] && { echo "output folder exists: $O"; exit 1; }

# ---- all 100 runs relayed, with their dump folders; rows: link name|relayed dump dir|run id|fold|seed|weights key|revision
ROWS=""; MISS=""
okrun(){ [ -e $1/.ok/$2 ] && grep -q "relayed $2:" $1/relay.log 2>/dev/null; }
for s in 5 6 7 8 9; do for k in 0 1 2 3 4; do
  r=c3_pf_v11_f${k}_s$s; d=$RDP/$r/dumps/elbench1/$MP/$r
  if okrun $RDP $r && [ -f $d/cv5v3_f$k/manifest.json ]; then ROWS="$ROWS$MP/$r|$d|$r|$k|$s|model|$OLD
"; else MISS="$MISS $r"; fi
  r=c3h_hrnet_w18_unetpp_pf_f${k}_s$s; d=$RDH/$r/dumps/elbench1/$MH/$r
  if okrun $RDH $r && [ -f $d/cv5v3_f$k/manifest.json ]; then ROWS="$ROWS$MH/$r|$d|$r|$k|$s|model|$OLD
"; else MISS="$MISS $r"; fi
  r=c3s_swad_v11_f${k}_s$s; d=$RDS/$r/dumps/elbench1/$MS/$r
  if okrun $RDS $r && [ -f $d/cv5v3_f$k/manifest.json ]; then ROWS="$ROWS$MS/$r|$d|$r|$k|$s|swad_bn|$OLD
"; else MISS="$MISS $r"; fi
  r=c3x_hrnet_swad_v11_f${k}_s$s; d=$RDX/$r/dumps/elbench1/$MX
  if okrun $RDX $r && [ -f $d/$r/cv5v3_f$k/manifest.json ] && [ -f $d/$r.swad/cv5v3_f$k/manifest.json ] && [ -s $RDX/$r/experiments/$r/enc_probe.jsonl ]; then
    ROWS="$ROWS$MX/$r|$d/$r|$r|$k|$s|swad_bn|$C3X
$MX/$r.swad|$d/$r.swad|$r.swad|$k|$s|swad|$C3X
"; else MISS="$MISS $r"; fi
done; done
[ -z "$MISS" ] || { echo "REFUSED: $(echo $MISS | wc -w) of 100 runs not relayed (or a dump folder or enc_probe.jsonl is missing):$MISS"; exit 1; }
[ "$(printf '%s' "$ROWS" | grep -c .)" = 125 ] || { echo "REFUSED: expected 125 dump folders (25 PF, 25 HRNET, 25 SWADBN, 25 COMBO, 25 COMBO_SWAD)"; exit 1; }

# ---- manifests of all 125 dumps, BEFORE anything is written: a refused read must not use up the registered output folder
MC=$($P - /dev/fd/3 3< <(printf '%s' "$ROWS") <<'EOF'
import json, sys
from pathlib import Path
rows = [l.rstrip("\n").split("|") for l in open(sys.argv[1]) if l.strip()]
dev, wr, bad = set(), set(), []
for ln, d, rid, k, s, key, rev in rows:
    m = json.loads((Path(d) / f"cv5v3_f{k}" / "manifest.json").read_text())
    want = {"run_id": rid, "fold": int(k), "seed": int(s), "weights_key": key, "step": 20000, "set": f"cv5v3_f{k}",
            "precision": "fp32", "set_kind": "open", "train_code_revision": rev}
    bad += [f"{d}: {x} = {m.get(x)!r}, expected {v!r}" for x, v in want.items() if m.get(x) != v]
    dev.add(m.get("device")); wr.add(m.get("writer"))
if len(dev) != 1 or "cpu" in dev:
    bad.append(f"devices over the 125 dumps: {sorted(map(str, dev))} (one GPU model expected)")
if len(wr) != 1:
    bad.append(f"writers over the 125 dumps: {sorted(map(str, wr))} (one bench_infer.py expected)")
print(f"manifest check: {len(rows)} dumps, device {sorted(map(str, dev))}, writer {sorted(map(str, wr))}: {'OK' if not bad else 'FAIL'}")
for b in bad[:20]:
    print("  " + b)
sys.exit(1 if bad else 0)
EOF
) || { echo "$MC"; echo "REFUSED: manifest check failed (nothing written, $O not created)"; exit 1; }
mkdir -p $L/$MP $L/$MH $L/$MS $L/$MX || exit 1
printf '%s' "$ROWS" > $O/expected_dumps.tsv
while IFS='|' read -r ln d rid k s key rev; do ln -s $d $L/$ln || { echo "link failed: $ln"; exit 1; }; done < $O/expected_dumps.tsv
{
  echo "[$(date '+%F %T')] c3x read start (out $O; 100 runs, 125 dump folders linked; script $(md5sum < $ME | cut -c1-8); C3X $C3X)"
  echo "$MC"
  echo "command (cwd $RT, nice -n 19): $CMD"
  if [ -n "${STUB:-}" ]; then $STUB "${A[@]}" "${PR[@]}"; rc=$?; else
  nice -n 19 $P scripts/bench_read_w1.py "${A[@]}" "${PR[@]}" --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa PF:5,6:7,8 \
    --groups $G3 --score-exclude $XCL --out $O/read; rc=$?; fi
  echo "[$(date '+%F %T')] read rc=$rc"
  if [ $rc = 0 ] && [ -z "${STUB:-}" ]; then
    nice -n 19 $P $HERE/c3x_class_guard.py --read $O --out $O/class_guard.txt --classes 13,16,20,11 --baseline PF; echo "class guard rc=$?"
    nice -n 19 $P $HERE/c3x_verdict.py --read $O --probes $RDX --out $O/verdict.txt; echo "verdict rc=$?"
  fi
  set +f; ( cd $O/read 2>/dev/null && md5sum read*.txt read.json > $O/MD5.txt ); ( cd $O && md5sum class_guard.txt verdict.txt >> $O/MD5.txt 2>/dev/null ); set -f
  { md5sum $ME $HERE/c3x_class_guard.py $HERE/c3x_verdict.py $RT/scripts/bench_read_w1.py $XCL $G3 | sed 's/  /  input: /'; } >> $O/MD5.txt
  echo "[$(date '+%F %T')] C3X READ ALL DONE (rc $rc); tracked changes: bench_wt_final $(git status --porcelain -uno | wc -l)"
  exit $rc
} 2>&1 | tee $O/run.log
exit ${PIPESTATUS[0]}
