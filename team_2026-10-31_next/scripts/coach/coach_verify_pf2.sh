#!/bin/bash
# coach (1 Nov): protocol_PF2 opening verification. Read-only ssh (no -A). Own pull of gaint el_f3/reports/pf2/post -> results/pf2/coach_raw;
# outputs results/pf2/coach_v. Test verdicts with the predecessor's independent coach_verify.py; E1 co-primaries + width checks with coach_e1_pf2.py.
set -u
cd /home/yugma/mtp/research/team_2026-10-31_next
G=/home/noob/work/el_f3; RAW=results/pf2/coach_raw; OUT=results/pf2/coach_v; mkdir -p $RAW $OUT
PY=/home/yugma/mtp/research/.venv/bin/python; V=/home/yugma/mtp/research/team_2026-10-29_features/scripts
CTX=$V/e1_context.tsv
ssh -o BatchMode=yes -o ConnectTimeout=15 noob@172.18.22.20 "grep -qE '^\[[^]]*\] pf2 scoring done: post rc=0$' $G/reports/pf2/launch.log && test -s $G/reports/pf2/post/MANIFEST.md5" || { echo "PF2 opening not done (rc=0): abort"; exit 1; }
rsync -a -e "ssh -o BatchMode=yes" noob@172.18.22.20:$G/reports/pf2/post/ $RAW/ || exit 1
(cd $RAW && md5sum -c --quiet MANIFEST.md5 && echo "local md5sum -c OK $(md5sum < MANIFEST.md5 | cut -c1-8) $(wc -l < MANIFEST.md5) files") > $OUT/integrity.txt 2>&1
ssh -o BatchMode=yes -o ConnectTimeout=15 noob@172.18.22.20 "cd $G
echo \"REVISION \$(cat REVISION) HEAD \$(git rev-parse --short HEAD) tracked-modified \$(git status --short --untracked-files=no | wc -l)\"
echo \"gaint MANIFEST \$(md5sum < reports/pf2/post/MANIFEST.md5 | cut -c1-8)\"
for a in SUP SUPPF RN50PF; do for k in 5 6 7 8 9; do r=pf2_\${a}_100pct_s\$k; f=experiments/\$r.stdout
  echo \"\$r hdr=\$(grep -c 'INFO train — Run: ' \$f) last=\\\"\$(grep -oE 'step [0-9]+/20000' \$f | tail -1)\\\" tb=\$(grep -c Traceback \$f) pf=\$(grep -c 'PF encoder lr' \$f) cfg=\\\"\$(grep -E 'encoder_pf|freeze|lr_mult|val_every|encoder_name|^seed' experiments/\$r/config_used.yaml | tr -s ' ' | tr '\n' ' ')\\\"\"
  grep -E \"(trained|config OK|CONFIG FAIL).*\$r\" reports/pf2/launch.log | sed 's/^/   /'
done; done
grep -E 'G6|PF2 ALL TRAINED|pf2 scoring' reports/pf2/launch.log
echo \"gpumem min free over the PF2 run: \$(grep -v '^#' reports/pf2/gpumem.log | awk '{print \$2}' | sort -n | head -1) MiB\"" >> $OUT/integrity.txt 2>&1
M=$RAW/m0
L(){ for k in 5 6 7 8 9; do echo -n $M/pf2_$1_100pct_s$k${2:-}.json,; done | sed 's/,$//'; }
for c in "PF2 SUP SUPPF" "RN SUPPF RN50PF" "bottom SUP RN50PF"; do set -- $c
  $PY -I $V/coach_verify.py --base $(L $2) --arm $(L $3) --boot 2000 --e1ctx $CTX > $OUT/verify_$1_tau0.txt 2>&1
  $PY -I $V/coach_verify.py --base $(L $2 .tau1) --arm $(L $3 .tau1) --boot 2000 > $OUT/verify_$1_tau1.txt 2>&1
done
$PY -I scripts/coach/coach_e1_pf2.py $M $CTX > $OUT/e1_pf2.txt 2>&1
(cd $OUT && md5sum *.txt > MD5)
echo "coach verify PF2 written to $OUT"
