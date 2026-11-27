#!/bin/bash
# Final package CV5 TTA read on gaint CPU (rule: harness/final/FINAL_RULE.md, written 21 Nov 2026 before any D4 dump of a
# cv5v3 run existed) = harness/c3x/run_read_c3x.sh (060e24a2) with the arms, pairs, relays and manifest expectations of the
# final package. NOT to be run before the independent review; the lead runs it ONCE, when all 75 dump-only jobs of the fin
# queue are relayed (the registered read; no earlier look).
#   Tools: the reviewed read tree bench_wt_final at 89b9ea5 (scripts/bench_read_w1.py fdb56b78), unchanged.
#   Arms (cv02 dumps of cv5v3 held-out folds, relayed, checksums equal; seeds 5 to 9, folds 0 to 4):
#     PF     c3_pf_v11_f[0-4]_s[5-9]                         (relay c3base; plain; baseline; A/A)
#     PF_D4  c3_pf_v11_f[0-4]_s[5-9]\.tta_d4                 (relay fin; the same checkpoints, --tta d4)
#     CS     c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad          (relay c3x; readout swad, plain = COMBO_SWAD)
#     CS_D4  c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad\.tta_d4  (relay fin; swad, --tta d4)
#     CB     c3x_hrnet_swad_v11_f[0-4]_s[5-9]                (relay c3x; readout swad_bn, plain = COMBO; information)
#     CB_D4  c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad_bn\.tta_d4 (relay fin; swad_bn, --tta d4; information)
#   Pairs: PF=PF_D4 (a), CS=CS_D4 (b), PF=CS_D4 (c, selection-biased); descriptive CB=CB_D4, PF=CB_D4, PF=CS, PF_D4=CS_D4.
#   Margin M: --aa PF:5,6:7,8 on the plain PF dumps in the same read; M = max(0.01, 2 x SE) at argmax, per cell set.
#   Cells: all 532 and the 416 clean cells (--score-exclude benchmark/splits/score_exclude_v3.txt) in one run.
#   Groups: --groups bench_data_v3b/meta/cv5v3_groups.tsv.
# Every check below runs before the output folder is created, so a refusal leaves no folder behind.
# Refuses unless: the read worktree is at 89b9ea5 with no tracked change and the read tool is fdb56b78; F (env, default the
#   pinned final-package commit) is 821dfad with tree 114d5469 in F_REPO (default bench_wt_fin), its bench_infer.py is the
#   D4 writer 32e0b67c, and 03375d4 -> F touches exactly the 10 paths of the code proof; the output folder is new; all 150
#   dump folders are relayed (.ok file and 'relayed' log line); every manifest names the expected run id, fold, seed,
#   weights key (model / swad / swad_bn), step 20000, set, fp32, open set, train code revision (89b9ea5 for PF and PF_D4,
#   03375d4 for the four c3x arms), tta (false for the three plain arms; mode_spec('d4') for the three D4 arms) and writer
#   (bench_infer.py afd91642 for the plain arms, 32e0b67c for the D4 arms); over all 150 one single GPU device.
#   Review N1 (fix round 1): each D4 dump's checkpoint_md5 equals that of the plain dump of the same run and key (a 32-hex
#   value on both), so the D4 arms read the very checkpoints of the plain arms.
# After the read: per-class table (final_class_guard.py = c3x_class_guard.py byte-equal) and the registered rule applied by
#   final_verdict.py (verdict.txt: (a), (b), (c), the D4 and opening decisions, descriptive lines).
# Variables: SHOW=1 prints the read command and exits (no check, nothing written). TAG = suffix of the output folder for a
#   repeat (bench_reads/final_tta_<TAG>); the first read without TAG is the registered one.
#   RELAY_FIN (not a test variable): the fin relay dir, default <RELAY_ROOT>/fin = /home/noob/work/bench_relay/fin; the lead
#   may put the fin relay on the NAS (/mnt/nas/noob_el_archive/bench_relay/fin) if gaint has less than 25 GB free at relay
#   start. Same checks there (.ok file, 'relayed' log line, manifests); c3base and c3x stay under RELAY_ROOT.
#   Tests only: RELAY_ROOT, READ_ROOT, F_REPO, STUB (a command run instead of the read tool, the class guard and the verdict).
# CPU only, nice 19, 8 workers.
set -u
set -f
SHOW=${SHOW:-0}; TAG=${TAG:-}
ME=$(readlink -f "$0"); HERE=$(dirname "$ME")
T=/home/yugma/mtp/research/team_2026-11-12_frontier
RT=/home/noob/work/bench_wt_final
OLD=89b9ea5a12a37a87c16c4868cc4adf00794a7610; C3X=03375d4c5e9ddde040603230eaca2b1c1139e14c
F_PIN=821dfadf49116cc6d5fdbd6697e263dd7cf0f834; F_TREE=114d5469340e7bfd496f290c18dccb7d4f13bdd3
W_OLD="bench_infer.py afd9164264de4d91e43e258e6f8b1836"; W_F="bench_infer.py 32e0b67c2ad8073c33440b8347d77f57"
F10="bench/q/cv02/cq.sh bench/q/cv02/cq_setup.sh bench/tta.py scripts/bench_infer.py scripts/bench_make_pool_root.py tests/test_bench_cards_cv02.py tests/test_bench_cq_cv5v3.py tests/test_bench_cq_final.py tests/test_bench_pool_root.py tests/test_bench_tta_pred.py "
RR=${RELAY_ROOT:-/home/noob/work/bench_relay}; RD0=${READ_ROOT:-/home/noob/work/bench_reads}
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
XCL=$T/benchmark/splits/score_exclude_v3.txt
G3=/home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv
RDP=$RR/c3base; RDX=$RR/c3x; RDF=${RELAY_FIN:-$RR/fin}
MP=house_r34_unetpp_pf_v11; MX=hrnet_w18_unetpp_swad_const_pf_v11
O=$RD0/final_tta${TAG:+_$TAG}; L=$O/links/elbench1
A=(--arm "PF=$L/$MP:c3_pf_v11_f[0-4]_s[5-9]" --arm "PF_D4=$L/$MP:c3_pf_v11_f[0-4]_s[5-9]\.tta_d4"
   --arm "CS=$L/$MX:c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad" --arm "CS_D4=$L/$MX:c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad\.tta_d4"
   --arm "CB=$L/$MX:c3x_hrnet_swad_v11_f[0-4]_s[5-9]" --arm "CB_D4=$L/$MX:c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad_bn\.tta_d4")
PR=(--pair PF=PF_D4 --pair CS=CS_D4 --pair PF=CS_D4 --pair CB=CB_D4 --pair PF=CB_D4 --pair PF=CS --pair PF_D4=CS_D4)
CMD="scripts/bench_read_w1.py ${A[*]} ${PR[*]} --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa PF:5,6:7,8 --groups $G3 --score-exclude $XCL --out $O/read"
[ "$SHOW" = 1 ] && { echo "SHOW=1 (no check of relays, nothing run, nothing written)"; echo "$CMD"; exit 0; }
cd $RT || exit 1
[ "$(git rev-parse --short HEAD)" = 89b9ea5 ] || { echo "worktree not at 89b9ea5"; exit 1; }
[ "$(git status --porcelain -uno | wc -l)" = 0 ] || { echo "tracked changes in $RT"; exit 1; }
[ "$(md5sum < scripts/bench_read_w1.py | cut -c1-8)" = fdb56b78 ] || { echo "bench_read_w1.py is not fdb56b78"; exit 1; }
[ "$(md5sum < $XCL | cut -c1-8)" = 6d48dfbd ] || { echo "score_exclude_v3.txt is not 6d48dfbd"; exit 1; }
[ "$(md5sum < $G3 | cut -c1-8)" = d880a769 ] || { echo "cv5v3_groups.tsv is not d880a769"; exit 1; }
F=${F:-$F_PIN}; GF=${F_REPO:-/home/noob/work/bench_wt_fin}
[ "$F" = "$F_PIN" ] && [ "$(git -C $GF rev-parse $F^{commit} 2>/dev/null)" = $F_PIN ] && [ "$(git -C $GF rev-parse $F^{tree} 2>/dev/null)" = $F_TREE ] \
  || { echo "F is not the final-package commit $F_PIN with tree $F_TREE in $GF"; exit 1; }
[ "bench_infer.py $(git -C $GF show $F:scripts/bench_infer.py | md5sum | cut -c1-32)" = "$W_F" ] || { echo "bench_infer.py at F is not the D4 writer ${W_F#* }"; exit 1; }
[ "$(git -C $GF diff --name-only $C3X $F | tr '\n' ' ')" = "$F10" ] || { echo "03375d4 -> F differs in other paths than the 10 of the code proof"; exit 1; }
[ -e $O ] && { echo "output folder exists: $O"; exit 1; }

# ---- all 150 dump folders relayed; rows: link name|relayed dump dir|run id|fold|seed|weights key|revision|tta|writer
ROWS=""; MISS=""
okrun(){ [ -e $1/.ok/$2 ] && grep -q "relayed $2:" $1/relay.log 2>/dev/null; }
row(){ # relay dir, unit name, method, dump dir name, fold, seed, key, revision, tta (0/1), writer
  local d=$1/$2/dumps/elbench1/$3/$4
  if okrun $1 $2 && [ -f $d/cv5v3_f$5/manifest.json ]; then ROWS="$ROWS$3/$4|$d|$4|$5|$6|$7|$8|$9|${10}
"; else MISS="$MISS $4"; fi; }
for s in 5 6 7 8 9; do for k in 0 1 2 3 4; do
  r=c3_pf_v11_f${k}_s$s
  row $RDP $r $MP $r $k $s model $OLD 0 "$W_OLD"
  row $RDF $r.tta_d4 $MP $r.tta_d4 $k $s model $OLD 1 "$W_F"
  r=c3x_hrnet_swad_v11_f${k}_s$s
  row $RDX $r $MX $r.swad $k $s swad $C3X 0 "$W_OLD"
  row $RDF $r.swad.tta_d4 $MX $r.swad.tta_d4 $k $s swad $C3X 1 "$W_F"
  row $RDX $r $MX $r $k $s swad_bn $C3X 0 "$W_OLD"
  row $RDF $r.swad_bn.tta_d4 $MX $r.swad_bn.tta_d4 $k $s swad_bn $C3X 1 "$W_F"
done; done
[ -z "$MISS" ] || { echo "REFUSED: $(echo $MISS | wc -w) of 150 dump folders not relayed (or the manifest is missing):$MISS"; exit 1; }
[ "$(printf '%s' "$ROWS" | grep -c .)" = 150 ] || { echo "REFUSED: expected 150 dump folders (25 per arm: PF, PF_D4, CS, CS_D4, CB, CB_D4)"; exit 1; }

# ---- manifests of all 150 dumps, BEFORE anything is written: a refused read must not use up the registered output folder
MC=$($P - /dev/fd/3 3< <(printf '%s' "$ROWS") <<'EOF'
import json, sys
from pathlib import Path
D4 = {"mode": "d4", "scales": [1.0], "d4": True, "views": 8}   # bench/tta.py mode_spec("d4") at F
rows = [l.rstrip("\n").split("|") for l in open(sys.argv[1]) if l.strip()]
dev, wr, bad, ck = set(), {}, [], {}
for ln, d, rid, k, s, key, rev, tta, writer in rows:
    m = json.loads((Path(d) / f"cv5v3_f{k}" / "manifest.json").read_text())
    want = {"run_id": rid, "fold": int(k), "seed": int(s), "weights_key": key, "step": 20000, "set": f"cv5v3_f{k}",
            "precision": "fp32", "set_kind": "open", "train_code_revision": rev, "tta": D4 if tta == "1" else False,
            "writer": writer}
    bad += [f"{d}: {x} = {m.get(x)!r}, expected {v!r}" for x, v in want.items()
            if m.get(x) != v or (x == "tta" and tta == "0" and m.get(x) is not False)]
    dev.add(m.get("device")); wr.setdefault(str(m.get("writer")), 0); wr[str(m.get("writer"))] += 1
    ck.setdefault((rid.split(".")[0], key), {})["d4" if tta == "1" else "plain"] = m.get("checkpoint_md5")
for (src, key), v in sorted(ck.items()):   # review N1: each D4 dump reads the very checkpoint its plain dump read
    p0, p4 = v.get("plain"), v.get("d4")
    if not (isinstance(p0, str) and len(p0) == 32 and p0 == p4):
        bad.append(f"{src} key {key}: checkpoint_md5 of the D4 dump {p4!r} != the plain dump's {p0!r} (the D4 arm must read the same checkpoint)")
if len(dev) != 1 or "cpu" in dev:
    bad.append(f"devices over the 150 dumps: {sorted(map(str, dev))} (one GPU model expected)")
if len(wr) != 2:
    bad.append(f"writers over the 150 dumps: {sorted(wr.items())} (two expected: afd91642 for the plain arms, 32e0b67c for D4)")
print(f"manifest check: {len(rows)} dumps, device {sorted(map(str, dev))}, writers {sorted(wr.items())}: {'OK' if not bad else 'FAIL'}")
for b in bad[:20]:
    print("  " + b)
sys.exit(1 if bad else 0)
EOF
) || { echo "$MC"; echo "REFUSED: manifest check failed (nothing written, $O not created)"; exit 1; }
mkdir -p $L/$MP $L/$MX || exit 1
printf '%s' "$ROWS" > $O/expected_dumps.tsv
while IFS='|' read -r ln d rid k s key rev tta w; do ln -s $d $L/$ln || { echo "link failed: $ln"; exit 1; }; done < $O/expected_dumps.tsv
{
  echo "[$(date '+%F %T')] final TTA read start (out $O; 150 dump folders linked; relays $RDP, $RDX, $RDF; script $(md5sum < $ME | cut -c1-8); F $F; rule FINAL_RULE.md $(md5sum < $HERE/FINAL_RULE.md | cut -c1-8))"
  echo "$MC"
  echo "command (cwd $RT, nice -n 19): $CMD"
  if [ -n "${STUB:-}" ]; then $STUB "${A[@]}" "${PR[@]}"; rc=$?; else
  nice -n 19 $P scripts/bench_read_w1.py "${A[@]}" "${PR[@]}" --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa PF:5,6:7,8 \
    --groups $G3 --score-exclude $XCL --out $O/read; rc=$?; fi
  echo "[$(date '+%F %T')] read rc=$rc"
  if [ $rc = 0 ] && [ -z "${STUB:-}" ]; then
    nice -n 19 $P $HERE/final_class_guard.py --read $O --out $O/class_guard.txt --classes 13,16,20,11 --baseline PF; echo "class guard rc=$?"
    nice -n 19 $P $HERE/final_verdict.py --read $O --out $O/verdict.txt; echo "verdict rc=$?"
  fi
  set +f; ( cd $O/read 2>/dev/null && md5sum read*.txt read.json > $O/MD5.txt ); ( cd $O && md5sum class_guard.txt verdict.txt >> $O/MD5.txt 2>/dev/null ); set -f
  { md5sum $ME $HERE/final_class_guard.py $HERE/final_verdict.py $HERE/FINAL_RULE.md $RT/scripts/bench_read_w1.py $XCL $G3 | sed 's/  /  input: /'; } >> $O/MD5.txt
  echo "[$(date '+%F %T')] FINAL TTA READ ALL DONE (rc $rc); tracked changes: bench_wt_final $(git status --porcelain -uno | wc -l)"
  exit $rc
} 2>&1 | tee $O/run.log
exit ${PIPESTATUS[0]}
