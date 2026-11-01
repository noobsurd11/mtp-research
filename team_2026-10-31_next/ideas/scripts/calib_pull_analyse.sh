#!/bin/bash
# calib: pull per-cell records from gaint (MANIFEST.md5 checked) and run the idea 1 / idea 7 analyses locally.
set -u
T=/home/yugma/mtp/research/team_2026-10-31_next/ideas
O=$T/calib_out; PY=/home/yugma/mtp/research/.venv/bin/python; CTX=/home/yugma/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv
mkdir -p $O/rec
ssh -o BatchMode=yes noob@172.18.22.20 'cd /home/noob/work/calib/out/rec && md5sum *.json > MANIFEST.md5'
rsync -a noob@172.18.22.20:/home/noob/work/calib/out/rec/ $O/rec/
(cd $O/rec && md5sum -c --quiet MANIFEST.md5) ; rc=$?; echo "manifest check rc=$rc"
A="--rec $O/rec --ctx $CTX --rfctx $O/rf_context.tsv --f51 $O/F51.txt --out $O"
$PY $T/scripts/idea1_analysis.py $A --targets FINAL SUPPF5 SUP5 --figs $T/figs > /dev/null
$PY $T/scripts/idea1_adapt.py $A --targets FINAL SUPPF5 SUP5 > /dev/null
$PY $T/scripts/idea7_backfill.py --rec $O/rec --ctx $CTX --f51 $O/F51.txt --out $O/idea7_backfill.txt --json $O/idea7_backfill.json > /dev/null
ls -la $O $T/figs
