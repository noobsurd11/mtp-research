#!/bin/bash
# f2 scoring on gaint (protocol_ddep5 / protocol_cp5: scoring "as MIM5"). Read-only inference. Masks = el_f2/data/escdd_masks
# -> el_f1 per-stem links -> labeled/masks_escdd (pixel-identical to cv02), the same files and scorer copies as the MIM5 post.
# Usage: f2_post_gaint.sh <label> <run> ...   Output: el_f2/reports/f2/post_<label>/
# 1) completeness: step 20000/20000 in the log + rescore JSON; REVISION 2751aa8; 2) init check (decoder_init md5 / cp section);
# 3) m0_audit default + tau 0/1 per-cell JSONs (val, test, ext106; el_f1 copies m0_audit.py d36f7438, m0_audit_tau.py d77241bb);
#    tau 0 == default checked; 4) LA aggregate tau 0/1 with the tau-0 check against the rescore JSONs; 5) MD5 manifest.
# Every GPU pass waits at the f2g gate (6,000 MiB = own peak ~4 GB + 2 GB, flock, >= 120 s since the last f2 start).
set -eu
cd /home/noob/work/el_f2
LBL=$1; shift; RUNS="$*"
SETS=${SETS:-val test ext}; SPL=${SPL:-test val}  # overrides only for the val-only smoke of this script
P=/home/noob/work/el-fault-detection/.venv/bin/python
F1=/home/noob/work/el_f1/reports/f1
OUT=reports/f2/post_$LBL; mkdir -p $OUT/m0 $OUT/rescore
gate_wait(){  # same gate as reports/f2g/run_one.sh v4/v5
  while :; do
    ok=$(flock reports/f2g/gate.lock bash -c 'f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0); '\
'a=$(( $(date +%s) - $(stat -c %Y reports/f2g/last_start 2>/dev/null || echo 0) )); '\
'if [ "$f" -ge "$1" ] && [ "$a" -ge 120 ]; then touch reports/f2g/last_start; echo 1; else echo 0; fi' _ "$1")
    [ "$ok" = 1 ] && break; sleep 60
  done
}
[ "$(cat REVISION)" = 2751aa8 ] || { echo "REVISION is not 2751aa8"; exit 1; }
md5sum $F1/m0_audit.py $F1/m0_audit_tau.py > $OUT/scorer_md5.txt
grep -q d36f7438 $OUT/scorer_md5.txt && grep -q d77241bb $OUT/scorer_md5.txt || { echo "scorer md5"; exit 1; }
for r in $RUNS; do
  grep -q "step 20000/20000" experiments/$r.stdout || { echo "INCOMPLETE $r"; exit 1; }
  test -s reports/f2g/$r.json || { echo "NO RESCORE $r"; exit 1; }
  cp reports/f2g/$r.json $OUT/rescore/
done
for r in $RUNS; do
  echo "== $r"; grep -E "decoder_init|encoder_init" experiments/$r/config_used.yaml || true
  grep -A10 "^cp:" experiments/$r/config_used.yaml || echo "(no cp section)"
  grep -h "Decoder initialised" experiments/$r.stdout | sed -E 's/^.*\(([0-9]+) tensors, md5 ([0-9a-f]+)\).*$/decoder_init log: \1 tensors md5 \2/' || echo "(no decoder_init log line)"
done > $OUT/init_check.txt
cat /home/noob/work/cv02_noob_el/el_f2/experiments/f2_ddep_pre_s0/decoder_final.md5 >> $OUT/init_check.txt
RD=$(for r in $RUNS; do echo /home/noob/work/el_f2/experiments/$r; done)
gate_wait 6000
HF_HUB_OFFLINE=1 $P $F1/m0_audit.py --code /home/noob/work/el_f2 --out $OUT/m0 --ext $F1/ext117 --no-logits --sets $SETS --runs $RD > $OUT/m0_audit.log 2>&1
for T in 0 1; do
  gate_wait 6000
  HF_HUB_OFFLINE=1 $P $F1/m0_audit_tau.py --code /home/noob/work/el_f2 --out $OUT/m0 --ext $F1/ext117 --no-logits --sets $SETS --tau $T \
    --runs $RD > $OUT/m0_audit_tau$T.log 2>&1
done
$P - <<PY > $OUT/tau0_check.txt
import json
bad = [r for r in "$RUNS".split() if json.load(open("$OUT/m0/%s.json" % r))["cells"] != json.load(open("$OUT/m0/%s.tau0.json" % r))["cells"]]
rev = sorted({json.load(open("$OUT/m0/%s.json" % r))["code_revision"] for r in "$RUNS".split()})
print("tau0 == default cells for all runs:", not bad, bad, "| code_revision", rev)
PY
cat $OUT/tau0_check.txt
gate_wait 6000
HF_HUB_OFFLINE=1 $P scripts/rescore_logit_adjust.py --runs $RUNS --taus 0 1 --splits $SPL --out $OUT/la.json \
  --check $OUT/rescore > $OUT/la.log 2>&1
(cd $OUT && find . -type f ! -name MANIFEST.md5 -print0 | sort -z | xargs -0 md5sum > MANIFEST.md5)
echo "POST DONE $LBL $(wc -l < $OUT/MANIFEST.md5) files"
