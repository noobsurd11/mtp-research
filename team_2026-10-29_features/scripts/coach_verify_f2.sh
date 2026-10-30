#!/bin/bash
# coach (30 Oct): DDeP5 / CP5 verification vs A5c-f1 (same per-cell files verified for MIM5, results/mim5/coach_raw).
# Usage: coach_verify_f2.sh ddep5 f2_DDeP   |   coach_verify_f2.sh cp5 f2_CP
# Read-only ssh to gaint (no -A). Own pull of el_f2/reports/f2/post_<label>/ -> results/<label>/coach_raw; outputs results/<label>/coach.
set -u
cd /home/yugma/mtp/research/team_2026-10-29_features
LBL=$1; PFX=$2; G=/home/noob/work/el_f2
RAW=results/$LBL/coach_raw; OUT=results/$LBL/coach; mkdir -p $RAW $OUT
PY=/home/yugma/mtp/research/.venv/bin/python
{ [ "$LBL" != cp5 ] || ssh -o BatchMode=yes -o ConnectTimeout=15 noob@172.18.22.20 "grep -qE '^\[[^]]*\] f2 CP5 E3b decoy final rc=[0-9]+: ' $G/reports/f2g/launch.log"; } && ssh -o BatchMode=yes -o ConnectTimeout=15 noob@172.18.22.20 "test -s $G/reports/f2/post_$LBL/MANIFEST.md5 && grep -q 'POST DONE' $G/reports/f2/post_$LBL.log" || { echo "gaint post_$LBL not done: abort"; exit 1; }
rsync -a -e "ssh -o BatchMode=yes" noob@172.18.22.20:$G/reports/f2/post_$LBL/ $RAW/ || exit 1
ssh -o BatchMode=yes -o ConnectTimeout=15 noob@172.18.22.20 "cd $G
echo \"REVISION \$(cat REVISION) HEAD \$(git rev-parse --short HEAD) tracked-modified \$(git status --short --untracked-files=no | wc -l)\"
cat /home/noob/work/cv02_noob_el/el_f2/experiments/f2_ddep_pre_s0/decoder_final.md5
for k in 0 1 2 3 4; do r=${PFX}_5pct_s\$k; f=experiments/\$r.stdout
  echo \"\$r hdr=\$(grep -c 'INFO train — Run: ' \$f) last=\\\"\$(grep -oE 'step [0-9]+/20000' \$f | tail -1)\\\" enc=\$(grep -c 'Encoder initialised' \$f) dec=\$(grep -c 'Decoder initialised' \$f) decmd5=\$(grep -o 'Decoder initialised.*' \$f | grep -oE '[0-9]+ tensors, md5 [0-9a-f]{32}' | sort -u | tr '\n' ' ') cp_keys=\$(grep -c 'loss_cp=' \$f) cfg=\\\"\$(grep -E 'decoder_init|encoder_init|lambda' experiments/\$r/config_used.yaml | tr -s ' ' | tr '\n' ' ')\\\"\"
  grep -E \"(trained|rescored) \$r rc=\" reports/f2g/launch.log | sed 's/^/   /'
done
grep -E '^\[[^]]*\] f2 (DDeP5|CP5) scoring' reports/f2g/launch.log
echo \"gaint MANIFEST \$(md5sum < reports/f2/post_$LBL/MANIFEST.md5 | cut -c1-32) \$(wc -l < reports/f2/post_$LBL/MANIFEST.md5) files\"" > $OUT/gaint_integrity.txt 2>&1
echo "local MANIFEST $(md5sum < $RAW/MANIFEST.md5 | cut -c1-32) $(wc -l < $RAW/MANIFEST.md5) files" >> $OUT/gaint_integrity.txt
(cd $RAW && md5sum -c --quiet MANIFEST.md5 && echo "md5sum -c OK") >> $OUT/gaint_integrity.txt 2>&1
$PY -I scripts/coach_f2_checks.py $RAW 2751aa8 $(for k in 0 1 2 3 4; do echo ${PFX}_5pct_s$k; done) > $OUT/file_checks.txt 2>&1
AM=results/mim5/coach_raw/m0
A0=$(echo $AM/f1_A_5pct_s{0..4}.json | tr ' ' ','); A1=$(echo $AM/f1_A_5pct_s{0..4}.tau1.json | tr ' ' ',')
B0=$(for k in 0 1 2 3 4; do echo -n $RAW/m0/${PFX}_5pct_s$k.json,; done | sed 's/,$//')
B1=$(for k in 0 1 2 3 4; do echo -n $RAW/m0/${PFX}_5pct_s$k.tau1.json,; done | sed 's/,$//')
$PY -I scripts/coach_verify.py --base $A0 --arm $B0 --boot 2000 --e1ctx scripts/e1_context.tsv > $OUT/verify_tau0.txt 2>&1      # C1
$PY -I scripts/coach_verify.py --base $A1 --arm $B1 --boot 2000 --e1ctx scripts/e1_context.tsv > $OUT/verify_tau1.txt 2>&1      # C2 (LA-matched)
$PY -I scripts/coach_verify.py --base $A1 --arm $B0 --boot 2000 --e1ctx scripts/e1_context.tsv > $OUT/verify_c3.txt 2>&1        # C3 yardstick
(cd $OUT && md5sum gaint_integrity.txt file_checks.txt verify_tau0.txt verify_tau1.txt verify_c3.txt > MD5)
echo "coach verify $LBL written to $OUT"
[ "$LBL" = cp5 ] && $PY -I scripts/coach_cp5_extra.py $RAW > $OUT/cp5_extra.txt 2>&1 && (cd $OUT && md5sum cp5_extra.txt >> MD5)
