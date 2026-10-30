#!/bin/bash
# MIM5 scoring on gaint (read-only inference; masks = el_f1/data/escdd_masks, pixel-identical to cv02).
# 1) completeness: every run has step 20000 in its log and a rescore JSON; 2) m0_audit per-cell (val, test, ext106);
# 3) per-cell JSONs at tau 0 and 1 (m0_audit_tau.py, coach request; tau 0 must equal the default cells); 4) logit
# adjustment tau 0/1 aggregate with the tau-0 check against the rescore JSONs; 5) md5 manifest of all outputs.
set -eu
cd /home/noob/work/el_f1
P=/home/noob/work/el-fault-detection/.venv/bin/python
OUT=reports/f1/post; mkdir -p $OUT/m0 $OUT/rescore
RUNS="f1_A_5pct_s0 f1_A_5pct_s1 f1_A_5pct_s2 f1_A_5pct_s3 f1_A_5pct_s4 f1_MIM_5pct_s0 f1_MIM_5pct_s1 f1_MIM_5pct_s2 f1_MIM_5pct_s3 f1_MIM_5pct_s4"
for r in $RUNS; do
  grep -q "step 20000/20000" experiments/$r.stdout || { echo "INCOMPLETE $r"; exit 1; }
  test -s reports/f1g/$r.json || { echo "NO RESCORE $r"; exit 1; }
  cp reports/f1g/$r.json $OUT/rescore/
done
grep "encoder_init" experiments/f1_MIM_5pct_s*/config_used.yaml > $OUT/encoder_init_check.txt
grep -h "Encoder initialised" experiments/f1_MIM_5pct_s*.stdout | sed -E 's/^.*md5 //' | sort | uniq -c >> $OUT/encoder_init_check.txt
cat experiments/f1_mim_pre_s0/encoder_final.md5 >> $OUT/encoder_init_check.txt
HF_HUB_OFFLINE=1 $P reports/f1/m0_audit.py --code /home/noob/work/el_f1 --out $OUT/m0 --ext reports/f1/ext117 --no-logits \
  --runs $(for r in $RUNS; do echo experiments/$r; done) > $OUT/m0_audit.log 2>&1
for T in 0 1; do  # coach request: per-cell JSONs under logit adjustment (m0_audit_tau.py, F1 copy of m0_audit.py)
  HF_HUB_OFFLINE=1 $P reports/f1/m0_audit_tau.py --code /home/noob/work/el_f1 --out $OUT/m0 --ext reports/f1/ext117 \
    --no-logits --tau $T --runs $(for r in $RUNS; do echo experiments/$r; done) > $OUT/m0_audit_tau$T.log 2>&1
done
$P - <<PY > $OUT/tau0_check.txt
import json
bad = [r for r in "$RUNS".split() if json.load(open("$OUT/m0/%s.json" % r))["cells"] != json.load(open("$OUT/m0/%s.tau0.json" % r))["cells"]]
print("tau0 == default cells for all runs:", not bad, bad)
PY
cat $OUT/tau0_check.txt
HF_HUB_OFFLINE=1 $P scripts/rescore_logit_adjust.py --runs $RUNS --taus 0 1 --splits test val --out $OUT/la.json \
  --check $OUT/rescore > $OUT/la.log 2>&1
(cd $OUT && find . -type f ! -name MANIFEST.md5 -print0 | sort -z | xargs -0 md5sum > MANIFEST.md5)
echo "POST DONE $(wc -l < $OUT/MANIFEST.md5) files"
