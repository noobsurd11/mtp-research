#!/bin/bash
# coach (1 Nov, successor): protocol_thin_b3 opening verification. Read-only ssh (no -A). Own pull of gaint el_thin/reports/thin/post
# -> results/thin/coach_raw; outputs results/thin/coach_v. Test primaries (two-set, tau 0 / tau 1, scuff-ignored test) by coach_verify.py
# (coach's, 29 Oct); E1 relF1@2 co-primary, B5 co-primaries (own recompute from calib's raw per-cell records), B3 readouts by
# scripts/coach/coach_thin.py (self-tested on PF2: B5 36/36 lines = coach_v/b5_pf2.txt; E1 relF1 PF2 +0.0365). Comparator = PF2's
# SUPPF s5-9 from my own PF2 pull (results/pf2/coach_raw, MANIFEST 3827f7c0).
set -u
cd /home/yugma/mtp/research/team_2026-10-31_next
G=/home/noob/work/el_thin; RAW=results/thin/coach_raw; OUT=results/thin/coach_v; P2=results/pf2/coach_raw; mkdir -p $RAW $OUT
PY=/home/yugma/mtp/research/.venv/bin/python; V=/home/yugma/mtp/research/team_2026-10-29_features/scripts
CTX=$V/e1_context.tsv; DEP=c9bbb02
ssh -o BatchMode=yes -o ConnectTimeout=15 noob@172.18.22.20 "grep -qE '^\[[^]]*\] thin scoring done: post rc=0$' $G/reports/thin/q/launch.log && test -s $G/reports/thin/post/MANIFEST.md5" || { echo "THIN opening not done (rc=0): abort"; exit 1; }
rsync -a -e "ssh -o BatchMode=yes" noob@172.18.22.20:$G/reports/thin/post/ $RAW/ || exit 1
(cd $RAW && md5sum -c --quiet MANIFEST.md5 && echo "local md5sum -c OK $(md5sum < MANIFEST.md5 | cut -c1-8) $(wc -l < MANIFEST.md5) files") > $OUT/integrity.txt 2>&1
(cd $P2 && md5sum -c --quiet MANIFEST.md5 && echo "PF2 comparator pull md5sum -c OK $(md5sum < MANIFEST.md5 | cut -c1-8)") >> $OUT/integrity.txt 2>&1
ssh -o BatchMode=yes -o ConnectTimeout=15 noob@172.18.22.20 "cd $G
echo \"REVISION \$(cat REVISION) HEAD \$(git rev-parse --short HEAD) tracked-modified \$(git status --short --untracked-files=no | wc -l)\"
echo \"gaint MANIFEST \$(md5sum < reports/thin/post/MANIFEST.md5 | cut -c1-8)\"
for a in SKR CLD B3; do for k in 5 6 7 8 9; do r=thin_\${a}_100pct_s\$k; f=experiments/\$r.stdout
  echo \"\$r hdr=\$(grep -c 'INFO train — Run: ' \$f) last=\\\"\$(grep -oE 'step [0-9]+/20000' \$f | tail -1)\\\" tb=\$(grep -c Traceback \$f) pf=\$(grep -c 'PF encoder lr' \$f) thin=\$(grep -c ' thin ' \$f) nan=\$(grep -ciE 'nan|inf ' \$f) cfg=\\\"\$(grep -E 'encoder_pf|freeze|lr_mult|val_every|^seed|num_classes|scuff_class|mask_subdir|skel_recall|cldice|weight:|iters:' experiments/\$r/config_used.yaml | tr -s ' ' | tr '\n' ' ')\\\"\"
  grep -E \"(trained|config OK|CONFIG FAIL).*\$r( |\$)\" reports/thin/q/launch.log | sed 's/^/   /'
done; done
grep -E 'HOLD|FAIL|thin scoring|all jobs dispatched' reports/thin/q/launch.log
echo \"gpumem min free over the THIN queue + opening: \$(grep -v '^#' reports/thin/q/gpumem.log | awk '{print \$2}' | sort -n | head -1) MiB\"
echo '# thin-term magnitudes (mean of logged values per 5k-step block, per run)'
for a in SKR CLD; do for k in 5 6 7 8 9; do r=thin_\${a}_100pct_s\$k
  grep ' thin ' experiments/\$r.stdout | sed -E 's/.*=([0-9.eE+-]+) at step ([0-9]+).*/\2 \1/' | awk -v r=\$r '{b=int((\$1-1)/5000); s[b]+=\$2; n[b]++} END{printf \"%s\", r; for(i=0;i<4;i++) printf \" %d-%dk %.4f\", i*5, (i+1)*5, s[i]/n[i]; printf \"\\n\"}'
done; done" >> $OUT/integrity.txt 2>&1
M=$RAW/m0; MB=$P2/m0
L(){ for k in 5 6 7 8 9; do echo -n $1/$2_100pct_s$k${3:-}.json,; done | sed 's/,$//'; }
for a in SKR CLD B3; do
  $PY -I $V/coach_verify.py --base $(L $MB pf2_SUPPF) --arm $(L $M thin_$a) --boot 2000 --e1ctx $CTX > $OUT/verify_${a}_tau0.txt 2>&1
  $PY -I $V/coach_verify.py --base $(L $MB pf2_SUPPF .tau1) --arm $(L $M thin_$a .tau1) --boot 2000 > $OUT/verify_${a}_tau1.txt 2>&1
done
# scuff-ignored test (descriptive): THIN test_noscuff cells as 'test' vs PF2's m0_scuffign SUPPF (same 236 px)
SI=$OUT/scuffign_in; mkdir -p $SI
$PY -I - $M $SI <<'PY'
import json, sys
m, o = sys.argv[1:3]
for a in ('SKR', 'CLD', 'B3'):
    for k in range(5, 10):
        d = json.load(open(f'{m}/thin_{a}_100pct_s{k}.json'))
        d['cells'] = {'test': d['cells']['test_noscuff']}
        json.dump(d, open(f'{o}/thin_{a}_100pct_s{k}.json', 'w'))
PY
for a in SKR CLD B3; do
  $PY -I $V/coach_verify.py --base $(L $P2/m0_scuffign pf2_SUPPF .scuffign) --arm $(L $SI thin_$a) --boot 2000 > $OUT/verify_${a}_scuffign.txt 2>&1
done
rm -rf $SI
$PY -I scripts/coach/coach_thin.py run $RAW $P2 $CTX $DEP > $OUT/thin_e1_b5_b3.txt 2>&1
(cd $OUT && md5sum *.txt > MD5)
echo "coach verify THIN written to $OUT"
