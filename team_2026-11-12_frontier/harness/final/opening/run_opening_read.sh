#!/bin/bash
# The read of the final opening (OPENING_RULE.md section 8), on gaint CPU (nice 19, at most 8 workers). Run by the LEAD
# ONCE, after the relay of the `open` queue says RELAY ALL DONE (the registered read; a repeat needs TAG).
# Every check runs before the output folder is created, so a refusal leaves nothing behind. Refuses unless:
#   - REG_MD5 (env; the md5 the lead logged in both ledgers at registration) = md5 of IO/REGISTERED.txt = IO/REGISTERED.md5;
#     the registration names opening_e1 '#8 e1_open8_final' and opening_t50 '#19 t50_open19_final', this OPENING_RULE.md's
#     md5, IO/jobs.txt's md5, commits F, G, R equal to the pins here, and the runs line naming F2 (the fin2 resume deploy);
#   - the read worktree (RT, default /home/noob/work/bench_wt_open) is at R with no tracked change;
#   - every job of IO/jobs.txt is relayed (RD/.ok/<name> and a 'relayed <name>:' log line) with its one dump folder;
#   - every manifest: run_id = the job name, set and set_kind sealed, opening = the set's, seed, weights_key, step 20000,
#     precision fp32, tta (False or mode_spec('d4')), ens_member True exactly for the logp jobs (absent otherwise), writer =
#     G's bench_infer.py, train_code_revision = F2 (9967d59; every dump is of a full-pool run, whose run dir is in F2's deploy
#     after the fin2 resume, REVIEW_FIN2 N3), checkpoint_md5 = the LATEST.md5 relayed by fin2 for that run, list_md5 of
#     the set, n_cells 106 / 50; one GPU model over all dumps;
#   - the sealed label files still match the registration (E1 masks + ignore; v0 test50; masks_v11 MANIFEST).
# Then (log O/run.log): links, per-cell records (bench_score records: E1 labels set; test50 v0 and v11), the two registered
# ensembles by bench_ens_dump --opening (C3 = mean softmax of the 5 C2 dumps; E-PF = of the 5 C1 dumps), their records, the
# three reads (bench_open_read.py), the verdict (opening_verdict.py), MD5.txt.
# Env: REG_MD5 (required), TAG (repeat), SHOW=1 (print the commands, no check), RD (the relay dir; default the NAS dir
#   /mnt/nas/noob_el_archive/bench_relay/open, the same default as opening_relay.sh and opening_queue.sh unstage).
#   Test-only overrides (review round 1, N11): IO, RF (fin relay dir), READ_ROOT, RT, BENCH_EXT / BENCH_LABELED /
#   BENCH_MASKS_V11 (label dirs), CELLS_TSV, PINS_FILE (replaces the pins below), DEVICE_OK=cpu (CPU dumps), FIN_VERDICT,
#   V11_FILECHECK_MANIFEST. If any is set the read refuses unless TEST_MODE=1; TEST_MODE=1 also needs a registration that
#   starts with its 'TEST MODE' line, and a real registration refuses TEST_MODE (a dry run never reads the real opening).
#   Round 2 (B2): with TEST_MODE=1, IO, RD, RF, READ_ROOT, BENCH_EXT, BENCH_LABELED, BENCH_MASKS_V11, CELLS_TSV, FIN_VERDICT
#   and V11_FILECHECK_MANIFEST must all be set and resolve under /home/noob/work/bench_int_io (guard below).
# Round 1 also: N3 the fin CV5 TTA verdict (FIN_VERDICT, default /home/noob/work/bench_reads/final_tta/verdict.txt; its md5
#   must be the registered one) is passed to the verdict, which quotes its decisions (a), (b), (c); N9 the test50 v1.1 mask
#   and ignore files of the 50 cells are md5-checked file by file against the lines of masks_v11/MANIFEST.md5 (whose own md5
#   is the registered one) before the output folder exists.
set -u
set -f
OV=""; for v in IO RF READ_ROOT RT BENCH_EXT BENCH_LABELED BENCH_MASKS_V11 CELLS_TSV PINS_FILE DEVICE_OK FIN_VERDICT V11_FILECHECK_MANIFEST; do
  [ -n "${!v+x}" ] && OV="$OV $v=${!v}"; done
if [ -n "$OV" ] && [ "${TEST_MODE:-0}" != 1 ]; then echo "REFUSED: test-only overrides set:$OV (unset them; TEST_MODE=1 only for dry runs)"; exit 1; fi
# B2 (review round 2): under TEST_MODE every label, mask, ignore, image, relay, output and fin-verdict path must be set
#   explicitly and resolve (readlink -m, symlinks followed) under the scratch root SCR_ROOT, and no symlink inside those scratch
#   dirs may resolve outside it; checked here, before any read, hash or mkdir. A dry run can never reach the real data.
SCR_ROOT=/home/noob/work/bench_int_io
tm_no(){ echo "REFUSED (TEST_MODE guard): $*"; exit 1; }
tm_in(){ local r; case "$1" in /*) ;; *) tm_no "$1 is not an absolute path";; esac; r=$(readlink -m -- "$1"); case "$r/" in "$SCR_ROOT"/*/*) ;; *) tm_no "$1 resolves to $r, outside $SCR_ROOT";; esac; }   # B3: absolute paths only
if [ "${TEST_MODE:-0}" = 1 ]; then
  for v in IO RD RF READ_ROOT BENCH_EXT BENCH_LABELED BENCH_MASKS_V11 CELLS_TSV FIN_VERDICT V11_FILECHECK_MANIFEST; do [ -n "${!v+x}" ] && [ -n "${!v}" ] || tm_no "$v must be set explicitly to a path under $SCR_ROOT (its default is a production path)"; done
  for p in "${IO:-}" "${RD:-}" "${RF:-}" "${READ_ROOT:-}" "${BENCH_EXT:-}" "${BENCH_EXT:-}/stems_eval.txt" "${BENCH_EXT:-}/images" "${BENCH_EXT:-}/masks" "${BENCH_EXT:-}/ignore" "${BENCH_LABELED:-}" "${BENCH_LABELED:-}/images" "${BENCH_LABELED:-}/masks_coded" "${BENCH_MASKS_V11:-}" "${BENCH_MASKS_V11:-}/masks" "${BENCH_MASKS_V11:-}/ignore" "${BENCH_MASKS_V11:-}/MANIFEST.md5" "${CELLS_TSV:-}" "${FIN_VERDICT:-}" "${V11_FILECHECK_MANIFEST:-}"; do tm_in "$p"; done
  for d in "$IO" "$RD" "$RF" "$BENCH_EXT" "$BENCH_LABELED" "$BENCH_MASKS_V11"; do [ -d "$d" ] || continue
    for l in $(find "$d" -type l 2>/dev/null); do tm_in "$l"; done; done
fi
SHOW=${SHOW:-0}; TAG=${TAG:-}
ME=$(readlink -f "$0"); HERE=$(dirname "$ME")
P=/home/noob/work/el-fault-detection/.venv/bin/python
IO=${IO:-/home/noob/work/bench_open_io}; RD=${RD:-/mnt/nas/noob_el_archive/bench_relay/open}; RF=${RF:-/mnt/nas/noob_el_archive/bench_relay/fin2}
FIN_VERDICT=${FIN_VERDICT:-/home/noob/work/bench_reads/final_tta/verdict.txt}
RT=${RT:-/home/noob/work/bench_wt_open}; RD0=${READ_ROOT:-/home/noob/work/bench_reads}
export BENCH_EXT=${BENCH_EXT:-/home/noob/work/el_f1/reports/f1/ext117}
export BENCH_LABELED=${BENCH_LABELED:-/home/noob/work/el-fault-detection/data/labeled}
export BENCH_MASKS_V11=${BENCH_MASKS_V11:-/home/noob/work/bench_data/masks_v11}
CELLS_TSV=${CELLS_TSV:-/home/noob/work/bench_data/meta/cells.tsv}
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
# ---- pins (the build fills them; the reviewer checks them)
F=821dfadf49116cc6d5fdbd6697e263dd7cf0f834
F2=9967d59abaab03cef83c1e3014840b2359ef45d7   # the deploy of the full-pool runs (fin2 resume): their dumps' train_code_revision
G=8bd1c2761c85f4721e444a8bf7124d2e5804973a; R=0c72cf942a5cc89accfcd02e1d2b443a033549d9; W_G="bench_infer.py a3268638d91937223433cd88d2d97df6"
[ -n "${PINS_FILE:-}" ] && . "$PINS_FILE"
MX=hrnet_w18_unetpp_swad_const_pf_v11; MP=house_r34_unetpp_pf_v11
O=$RD0/open_final${TAG:+_$TAG}
no(){ echo "REFUSED: $*"; exit 1; }
if [ "$SHOW" = 1 ]; then echo "SHOW=1: records -> bench_ens_dump --opening (C3, E-PF) -> bench_open_read (e1, t50 v11, t50 v0) -> opening_verdict.py; out $O"; exit 0; fi
REG_MD5=${REG_MD5:?REG_MD5: the md5 of REGISTERED.txt logged in the ledgers}
[ -s $IO/REGISTERED.txt ] || no "no $IO/REGISTERED.txt"
[ "$(md5sum < $IO/REGISTERED.txt | cut -c1-32)" = "$REG_MD5" ] && [ "$(cat $IO/REGISTERED.md5)" = "$REG_MD5" ] || no "REGISTERED.txt md5 != REG_MD5"
if head -1 $IO/REGISTERED.txt | grep -q '^TEST MODE'; then [ "${TEST_MODE:-0}" = 1 ] || no "the registration is a TEST MODE dry run"
else [ "${TEST_MODE:-0}" != 1 ] || no "TEST_MODE=1 against a real registration"; fi
[ "${TEST_MODE:-0}" = 1 ] && echo "TEST MODE (dry run; overrides:${OV:- none}): not the registered read"
grep -q "^c1d4 [a-z]* (fin verdict $(md5sum < $FIN_VERDICT 2>/dev/null | cut -c1-32))\$" $IO/REGISTERED.txt || no "fin verdict $FIN_VERDICT is not the registered one"
grep -q "^opening_e1 E1 opening #8 e1_open8_final " $IO/REGISTERED.txt && grep -q "^opening_t50 test50 opening #19 t50_open19_final " $IO/REGISTERED.txt || no "the registration names other openings"
grep -q "^rule OPENING_RULE.md $(md5sum < $HERE/OPENING_RULE.md | cut -c1-32)\$" $IO/REGISTERED.txt || no "OPENING_RULE.md is not the registered file"
grep -q "^jobs $(md5sum < $IO/jobs.txt | cut -c1-32) " $IO/REGISTERED.txt || no "jobs.txt is not the registered list"
grep -q "^commits F $F G $G R $R\$" $IO/REGISTERED.txt || no "the registration names other commits than F $F G $G R $R"
grep -q "^runs F2 $F2 " $IO/REGISTERED.txt || no "the registration does not name F2 $F2 as the deploy of the full-pool runs"
cd $RT || no "no $RT"
[ "$(git rev-parse HEAD)" = "$R" ] || no "read worktree $RT is not at R"
[ "$(git status --porcelain -uno | wc -l)" = 0 ] || no "tracked changes in $RT"
[ -e $O ] && no "output folder exists: $O"
[ "$CELLS_TSV" != /home/noob/work/bench_data/meta/cells.tsv ] || [ "$(md5sum < $CELLS_TSV | cut -c1-8)" = a50521b4 ] || no "cells.tsv is not a50521b4"
C1D4=$(awk '/^c1d4 /{print $2}' $IO/REGISTERED.txt)
# ---- sealed label files still as registered (file hashes only)
(cd $BENCH_EXT && md5sum -c --quiet $IO/reg/e1_masks.md5 > /dev/null 2>&1) || no "E1 mask / ignore files differ from the registration"
(cd $BENCH_LABELED/masks_coded && md5sum -c --quiet $IO/reg/masks_v0_test50.md5 > /dev/null 2>&1) || no "v0 test50 masks differ from the registration"
grep -q "^lists e1 5266806b559f74bcf9eae167bb076b95 t50 a31fad14fa27ee28e2a2319b8976aba3 masks_v11 $(md5sum < $BENCH_MASKS_V11/MANIFEST.md5 | cut -c1-32)\$" $IO/REGISTERED.txt || no "masks_v11 MANIFEST.md5 differs from the registration"
V0MD5=$(awk '/^v0_test50 /{print $2}' $IO/REGISTERED.txt)
[ "$(md5sum < $IO/reg/masks_v0_test50.md5 | cut -c1-32)" = "$V0MD5" ] || no "reg/masks_v0_test50.md5 is not the registered file"
V11C=$(bash $HERE/v11_filecheck.sh $BENCH_MASKS_V11 $RT/data/splits/test.txt ${V11_FILECHECK_MANIFEST:-$BENCH_MASKS_V11/MANIFEST.md5}) || no "test50 v1.1 files: $V11C"
echo "$V11C"
# ---- relayed dumps and their manifests (rows: name|set|dump dir|seed|key|tta|logp|run)
ROWS=""; MISS=""
while IFS='|' read -r name card seed root fold gate dgate logp extra; do
  set -- $extra; run=$(basename $2); key=$4; tta=$6; st=$8
  case "$card" in *$MX.yaml) meth=$MX;; *$MP.yaml) meth=$MP;; *) no "card $card";; esac
  d=$RD/$name/dumps/elbench1/$meth/$name/$st
  if [ -e $RD/.ok/$name ] && grep -q "relayed $name:" $RD/relay.log 2>/dev/null && [ -f $d/manifest.json ]; then
    ROWS="$ROWS$name|$st|$d|$seed|$key|$tta|$logp|$run|$meth
"; else MISS="$MISS $name"; fi
done < $IO/jobs.txt
[ -z "$MISS" ] || no "$(echo $MISS | wc -w) dumps not relayed:$MISS"
NJ=$(grep -c . $IO/jobs.txt); [ "$(printf '%s' "$ROWS" | grep -c .)" = "$NJ" ] || no "expected $NJ dumps"
MC=$($P - /dev/fd/3 "$RF" "$W_G" "$F2" "${DEVICE_OK:-}" 3< <(printf '%s' "$ROWS") <<'EOF'
import json, sys
from pathlib import Path
rows = [l.rstrip("\n").split("|") for l in open(sys.argv[1]) if l.strip()]
RF, WG, F2, devok = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]   # F2: train_code_revision of the full-pool runs
D4 = {"mode": "d4", "scales": [1.0], "d4": True, "views": 8}
OPEN = {"e1_106": "e1_open8_final", "test50": "t50_open19_final"}
LIST = {"e1_106": ("5266806b559f74bcf9eae167bb076b95", 106), "test50": ("a31fad14fa27ee28e2a2319b8976aba3", 50)}
bad, dev = [], set()
for name, st, d, seed, key, tta, logp, run, meth in rows:
    m = json.loads((Path(d) / "manifest.json").read_text())
    lm = (Path(RF) / run / "runs" / run / "LATEST.md5")
    latest = lm.read_text().split()[0] if lm.exists() else "NO LATEST.md5"
    want = {"run_id": name, "set": st, "set_kind": "sealed", "opening": OPEN[st], "seed": int(seed), "weights_key": key,
            "step": 20000, "precision": "fp32", "tta": D4 if tta == "d4" else False, "writer": WG,
            "train_code_revision": F2, "checkpoint_md5": latest, "list_md5": LIST[st][0], "n_cells": LIST[st][1],
            "method": meth}
    bad += [f"{name}: {k} = {m.get(k)!r}, expected {v!r}" for k, v in want.items()
            if m.get(k) != v or (k == "tta" and tta != "d4" and m.get(k) is not False)]
    if (logp == "1") != (m.get("ens_member") is True) or (logp != "1" and "ens_member" in m):
        bad.append(f"{name}: ens_member {m.get('ens_member')!r} with logp {logp}")
    dev.add(str(m.get("device")))
if len(dev) != 1 or (("cpu" in dev) and devok != "cpu"):
    bad.append(f"devices over the dumps: {sorted(dev)} (one GPU model expected)")
print(f"manifest check: {len(rows)} dumps, device {sorted(dev)}: {'OK' if not bad else 'FAIL'}")
for b in bad[:20]:
    print("  " + b)
sys.exit(1 if bad else 0)
EOF
) || { echo "$MC"; no "manifest check failed (nothing written; $O not created)"; }
# ---- the read (everything below writes under O only)
mkdir -p $O/links/elbench1/$MX $O/links/elbench1/$MP $O/records/set $O/records/v0 $O/records/v11 $O/ens || exit 1
printf '%s' "$ROWS" > $O/expected_dumps.tsv
while IFS='|' read -r name st d seed key tta logp run meth; do ln -s $(dirname $d) $O/links/elbench1/$meth/$name || exit 1; done < $O/expected_dumps.tsv
grep -vx CSIR_00070_r8_c4 $RT/data/splits/test.txt | grep . | sort > $O/t50_clean49.txt
export BENCH_MASKS_V0_SEALED=$IO/reg/masks_v0_test50.md5 BENCH_MASKS_V0_SEALED_MD5=$V0MD5
recs(){ # labels out-dir name set dumpdir opening
  nice -n 19 $P scripts/bench_score.py records --dumps $5 --set $4 --opening $6 --labels $1 --out $O/records/$2/$3.json > /dev/null || echo "FAIL records $1 $3"; }
{
  echo "[$(date '+%F %T')] final opening read start (out $O; $NJ dumps; REGISTERED $REG_MD5; script $(md5sum < $ME | cut -c1-8); rule $(md5sum < $HERE/OPENING_RULE.md | cut -c1-8); R $R; C1-D4 $C1D4; relay $RD)"
  [ "${TEST_MODE:-0}" = 1 ] && echo "TEST MODE (dry run; overrides:${OV:- none}): NOT the registered read"
  echo "$V11C"
  echo "$MC"
  declare -A OPN=([e1_106]=e1_open8_final [test50]=t50_open19_final)
  JOBS=()
  while IFS='|' read -r name st d seed key tta logp run meth; do
    if [ $st = e1_106 ]; then JOBS+=("set set $name e1_106 $O/links/elbench1/$meth/$name/e1_106 e1_open8_final")
    else JOBS+=("v0 v0 $name test50 $O/links/elbench1/$meth/$name/test50 t50_open19_final" "v11 v11 $name test50 $O/links/elbench1/$meth/$name/test50 t50_open19_final"); fi
  done < $O/expected_dumps.tsv
  export -f recs; export O P
  printf '%s\n' "${JOBS[@]}" | xargs -P 8 -L 1 bash -c 'recs "$@"' _ | tee $O/records_fail.txt
  [ -s $O/records_fail.txt ] && { echo "records failed"; exit 1; }
  echo "[$(date '+%F %T')] records: $(ls $O/records/set | wc -l) E1, $(ls $O/records/v0 | wc -l) test50 v0, $(ls $O/records/v11 | wc -l) test50 v11"
  nice -n 19 $P scripts/bench_ens_dump.py --arm "C3=$O/links/elbench1/$MX:fin_hrnet_swad_v11_pool_s[5-9]\.swad\.tta_d4\.e1_106" --seeds 5,6,7,8,9 --seed-id 56789 --method $MX --run-prefix C3_fin_hrnet_swad_v11_pool_s56789.swad.tta_d4.e1_106 --dumps $O/ens --workers 8 --opening e1_open8_final || { echo "C3 ensemble failed"; exit 1; }
  nice -n 19 $P scripts/bench_ens_dump.py --arm "EPF=$O/links/elbench1/$MP:fin_pf_v11_pool_s[5-9]\.e1_106" --seeds 5,6,7,8,9 --seed-id 56789 --method $MP --run-prefix EPF_fin_pf_v11_pool_s56789.e1_106 --dumps $O/ens --workers 8 --opening e1_open8_final || { echo "E-PF ensemble failed"; exit 1; }
  recs set set C3 e1_106 $O/ens/elbench1/$MX/C3_fin_hrnet_swad_v11_pool_s56789.swad.tta_d4.e1_106/e1_106 e1_open8_final
  recs set set EPF e1_106 $O/ens/elbench1/$MP/EPF_fin_pf_v11_pool_s56789.e1_106/e1_106 e1_open8_final
  [ -s $O/records/set/C3.json ] && [ -s $O/records/set/EPF.json ] || { echo "ensemble records missing"; exit 1; }
  set +f
  fl(){ ls $O/records/$1/$2 2>/dev/null | LC_ALL=C sort | paste -sd, ; }   # comma list of absolute record paths
  C1E=$(fl set 'fin_pf_v11_pool_s[5-9].e1_106.json'); C2E=$(fl set 'fin_hrnet_swad_v11_pool_s[5-9].swad.tta_d4.e1_106.json')
  C1DE=$(fl set 'fin_pf_v11_pool_s[5-9].tta_d4.e1_106.json')
  for lb in v11 v0; do
    eval "C1T_$lb=\$(fl $lb 'fin_pf_v11_pool_s[5-9].test50.json'); C2T_$lb=\$(fl $lb 'fin_hrnet_swad_v11_pool_s[5-9].swad.tta_d4.test50.json'); C1DT_$lb=\$(fl $lb 'fin_pf_v11_pool_s[5-9].tta_d4.test50.json')"
  done
  set -f
  A_E1=(--arm "C1=$C1E" --arm "C2=$C2E" --arm "C3=$O/records/set/C3.json" --arm "EPF=$O/records/set/EPF.json" --arm "C2S5=$O/records/set/fin_hrnet_swad_v11_pool_s5.swad.tta_d4.e1_106.json")
  P_E1=(--pair C1=C2 --pair C1=C3 --pair EPF=C3 --pair C2=C3 --pair C1=C2S5 --pair C1=EPF)
  [ $C1D4 = yes ] && { A_E1+=(--arm "C1D4=$C1DE"); P_E1+=(--pair C1=C1D4 --pair C1D4=C2); }
  A_T=(); for lb in v11 v0; do eval "a1=\$C1T_$lb; a2=\$C2T_$lb; a3=\$C1DT_$lb"
    A_T+=("$lb|--arm C1=$a1 --arm C2=$a2 --arm C2S5=$O/records/$lb/fin_hrnet_swad_v11_pool_s5.swad.tta_d4.test50.json$([ $C1D4 = yes ] && echo " --arm C1D4=$a3")"); done
  echo "arms: E1 C1 $(echo $C1E | tr ',' '\n' | grep -c .) C2 $(echo $C2E | tr ',' '\n' | grep -c .) C1-D4 $(echo $C1DE | tr ',' '\n' | grep -c .); test50 v11 C1 $(echo $C1T_v11 | tr ',' '\n' | grep -c .) C2 $(echo $C2T_v11 | tr ',' '\n' | grep -c .)"
  nice -n 19 $P scripts/bench_open_read.py --set e1_106 "${A_E1[@]}" "${P_E1[@]}" --aa C1:5,6:7,8 --celltypes $CELLS_TSV --boot 2000 --out $O/read_e1 || { echo "E1 read failed"; exit 1; }
  P_T=(--pair C1=C2 --pair C1=C2S5); [ $C1D4 = yes ] && P_T+=(--pair C1=C1D4 --pair C1D4=C2)
  for x in "${A_T[@]}"; do lb=${x%%|*}; args=${x#*|}
    if [ $lb = v11 ]; then nice -n 19 $P scripts/bench_open_read.py --set test50 $args "${P_T[@]}" --celltypes $CELLS_TSV --subset clean49=$O/t50_clean49.txt --subset nolink16=$IO/reg/t50_nolink.txt --boot 2000 --out $O/read_t50_v11 || { echo "t50 v11 read failed"; exit 1; }
    else nice -n 19 $P scripts/bench_open_read.py --set test50 $args --pair C1=C2 --public --boot 2000 --out $O/read_t50_v0 || { echo "t50 v0 read failed"; exit 1; }; fi
  done
  nice -n 19 $P $HERE/opening_verdict.py --e1 $O/read_e1/read.json --t50 $O/read_t50_v11/read.json --t50v0 $O/read_t50_v0/read.json --reg $IO/REGISTERED.txt --fin-verdict $FIN_VERDICT --out $O/verdict.txt; rc=$?
  set +f; ( cd $O && md5sum read_*/read.json read_*/read.txt verdict.txt verdict.json 2>/dev/null > MD5.txt; md5sum ens/elbench1/*/*/e1_106/manifest.json >> MD5.txt ); set -f
  md5sum $ME $HERE/opening_verdict.py $HERE/OPENING_RULE.md $RT/scripts/bench_open_read.py $RT/scripts/bench_score.py $RT/scripts/bench_ens_dump.py $RT/bench/public_metrics.py $IO/REGISTERED.txt $FIN_VERDICT $HERE/v11_filecheck.sh | sed 's/  /  input: /' >> $O/MD5.txt
  echo "[$(date '+%F %T')] FINAL OPENING READ ALL DONE (verdict rc $rc); tracked changes in $RT: $(git status --porcelain -uno | wc -l)"
  exit $rc
} 2>&1 | tee $O/run.log
exit ${PIPESTATUS[0]}
