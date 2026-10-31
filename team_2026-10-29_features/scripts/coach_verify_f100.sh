#!/bin/bash
# coach (30 Oct): protocol_100 opening 1 verification (SUP100-g, SUP100-PF, MIM100-PF). Read-only ssh (no -A).
# Own pull of gaint el_f3/reports/f100/post_opening1 -> results/f100/coach_raw_o1; outputs results/f100/coach_o1.
set -u
cd /home/yugma/mtp/research/team_2026-10-29_features
G=/home/noob/work/el_f3; RAW=results/f100/coach_raw_o1; OUT=results/f100/coach_o1; mkdir -p $RAW $OUT
PY=/home/yugma/mtp/research/.venv/bin/python
ssh -o BatchMode=yes -o ConnectTimeout=15 noob@172.18.22.20 "grep -qE '^\[[^]]*\] f3 opening1 scoring done: post rc=0$' $G/reports/f100/launch.log && test -s $G/reports/f100/post_opening1/MANIFEST.md5" || { echo "opening 1 not done: abort"; exit 1; }
rsync -a -e "ssh -o BatchMode=yes" noob@172.18.22.20:$G/reports/f100/post_opening1/ $RAW/ || exit 1
ssh -o BatchMode=yes -o ConnectTimeout=15 noob@172.18.22.20 "cd $G
echo \"REVISION \$(cat REVISION) HEAD \$(git rev-parse --short HEAD) tracked-modified \$(git status --short --untracked-files=no | wc -l)\"
for a in SUP SUPPF MIMPF; do for k in 0 1 2 3 4; do r=f3_\${a}_100pct_s\$k; f=experiments/\$r.stdout
  echo \"\$r hdr=\$(grep -c 'INFO train — Run: ' \$f) last=\\\"\$(grep -oE 'step [0-9]+/20000' \$f | tail -1)\\\" tb=\$(grep -c Traceback \$f) resumed=\$(grep -c RESUMED \$f) val=\$(grep -cE 'val ' \$f) pf=\$(grep -c 'PF encoder lr' \$f) enc=\$(grep -o 'Encoder initialised.*' \$f | grep -oE '[0-9]+ tensors, md5 [0-9a-f]{32}' | sort -u | tr '\n' ' ') cfg=\\\"\$(grep -E 'encoder_pf|encoder_init|freeze|lr_mult|val_every' experiments/\$r/config_used.yaml | tr -s ' ' | tr '\n' ' ')\\\"\"
  grep -E \"(trained|rescored) \$r rc=\" reports/f100/launch.log | sed 's/^/   /'
done; done
grep -E 'gate 6b|opening1' reports/f100/launch.log
echo \"gaint MANIFEST \$(md5sum < reports/f100/post_opening1/MANIFEST.md5 | cut -c1-32) \$(wc -l < reports/f100/post_opening1/MANIFEST.md5) files\"" > $OUT/gaint_integrity.txt 2>&1
echo "local MANIFEST $(md5sum < $RAW/MANIFEST.md5 | cut -c1-32) $(wc -l < $RAW/MANIFEST.md5) files" >> $OUT/gaint_integrity.txt
(cd $RAW && md5sum -c --quiet MANIFEST.md5 && echo "md5sum -c OK") >> $OUT/gaint_integrity.txt 2>&1
M=$RAW/m0; [ -d $M ] || M=$(dirname $(find $RAW -name 'f3_SUP_100pct_s0.json' | head -1))
echo "m0 dir: $M" >> $OUT/gaint_integrity.txt
RUNS=$(for a in SUP SUPPF MIMPF; do for k in 0 1 2 3 4; do echo f3_${a}_100pct_s$k; done; done)
$PY -I scripts/coach_f2_checks.py $(dirname $M) e544133 $RUNS > $OUT/file_checks.txt 2>&1
L(){ for k in 0 1 2 3 4; do echo -n $M/f3_$1_100pct_s$k${2:-}.json,; done | sed 's/,$//'; }
for c in "pool SUPPF MIMPF" "recipe SUP SUPPF" "bottom SUP MIMPF"; do set -- $c
  $PY -I scripts/coach_verify.py --base $(L $2) --arm $(L $3) --boot 2000 --e1ctx scripts/e1_context.tsv > $OUT/verify_$1_tau0.txt 2>&1
  $PY -I scripts/coach_verify.py --base $(L $2 .tau1) --arm $(L $3 .tau1) --boot 2000 --e1ctx scripts/e1_context.tsv > $OUT/verify_$1_tau1.txt 2>&1
done
(cd $OUT && md5sum *.txt > MD5)
echo "coach verify f100 opening 1 written to $OUT"
