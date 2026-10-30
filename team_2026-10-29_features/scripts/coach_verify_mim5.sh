#!/bin/bash
# coach (29 Oct, respawn): MIM5 verification. Read-only ssh to gaint (no -A). Outputs in results/mim5/coach/.
# 1) gaint integrity: rc 0, one header per stdout, step 20000, encoder_init only in MIM runs (md5 = encoder_final), REVISION
# 2) local raw (runner's pull): md5sum -c, MANIFEST.md5 equal to gaint's; 3) file checks + tau0 == default + m0-vs-rescore
# 4) coach_verify.py: tau 0 (default) incl. E1 split, and tau 1 (LA-matched contrast)
set -u
cd /home/yugma/mtp/research/team_2026-10-29_features
RAW=${RAW:-results/mim5/raw}; OUT=results/mim5/coach; mkdir -p $OUT
ssh -o BatchMode=yes -o ConnectTimeout=15 noob@172.18.22.20 "grep -q 'POST DONE' /home/noob/work/el_f1/reports/f1/post.log && test -s /home/noob/work/el_f1/reports/f1/post/MANIFEST.md5" || { echo "gaint post not done: abort"; exit 1; }
test -s $RAW/MANIFEST.md5 || { echo "no local raw manifest: abort"; exit 1; }
PY=/home/yugma/mtp/research/.venv/bin/python
ssh -o BatchMode=yes -o ConnectTimeout=15 noob@172.18.22.20 'cd /home/noob/work/el_f1
echo "REVISION $(cat REVISION)"; cat experiments/f1_mim_pre_s0/encoder_final.md5
for r in f1_A_5pct_s{0..4} f1_MIM_5pct_s{0..4}; do f=experiments/$r.stdout
  echo "$r hdr=$(grep -c "INFO train — Run: " $f) last=\"$(grep -oE "step [0-9]+/20000" $f | tail -1)\" enc=$(grep -c "Encoder initialised" $f) encmd5=$(grep -o "Encoder initialised.*md5 [0-9a-f]*" $f | grep -oE "[0-9a-f]{32}$" | sort -u | tr "\n" " ") cfg=\"$(grep -E "encoder_init" experiments/$r/config_used.yaml | tr -s " " | tr "\n" " ")\" ckpt=$(ls experiments/$r/checkpoints | tr "\n" " ")"
  grep -E "(trained|rescored) $r rc=" reports/f1g/launch.log | sed "s/^/   /"
done
grep -E "MIM5 post rc|AM rc|AFTER-RUNS" reports/f1g/launch.log
echo "gaint MANIFEST $(md5sum < reports/f1/post/MANIFEST.md5 | cut -c1-32) $(wc -l < reports/f1/post/MANIFEST.md5) files"' > $OUT/gaint_integrity.txt 2>&1
echo "local MANIFEST $(md5sum < $RAW/MANIFEST.md5 | cut -c1-32) $(wc -l < $RAW/MANIFEST.md5) files" >> $OUT/gaint_integrity.txt
(cd $RAW && md5sum -c --quiet MANIFEST.md5 && echo "md5sum -c OK") >> $OUT/gaint_integrity.txt 2>&1
$PY -I scripts/coach_mim5_checks.py $RAW > $OUT/file_checks.txt 2>&1
M=$RAW/m0; A=$(echo $M/f1_A_5pct_s{0..4}.json | tr ' ' ','); B=$(echo $M/f1_MIM_5pct_s{0..4}.json | tr ' ' ',')
$PY -I scripts/coach_verify.py --base $A --arm $B --boot 2000 --e1ctx scripts/e1_context.tsv > $OUT/verify_tau0.txt 2>&1
A1=$(echo $M/f1_A_5pct_s{0..4}.tau1.json | tr ' ' ','); B1=$(echo $M/f1_MIM_5pct_s{0..4}.tau1.json | tr ' ' ',')
$PY -I scripts/coach_verify.py --base $A1 --arm $B1 --boot 2000 --e1ctx scripts/e1_context.tsv > $OUT/verify_tau1.txt 2>&1
(cd $OUT && md5sum gaint_integrity.txt file_checks.txt verify_tau0.txt verify_tau1.txt > MD5)
echo "coach verify written to $OUT"
