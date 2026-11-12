#!/bin/bash
# Refresh handbook/sources/: verbatim copies of the primary project documents, so the guide agent has them even when it
# only receives this folder. Re-run after new results land. The chat-derived files (sources/chat/) are static and kept.
# Usage: bash handbook/sync_sources.sh
set -e
R=~/mtp/research; S=$R/handbook/sources
mkdir -p $S/protocols $S/results $S/to_human $S/analysis $S/data_analysis $S/literature/notes $S/old_era_reports
cp $R/protocols/*.md $S/protocols/
for d in $R/results/*/; do
  n=$(basename $d)
  for f in $d*.md $d*_rules.txt $d*per_image_test.txt $d*_curve.txt $d*sensitivity*.txt $d*noise_rank*.txt $d*selection.txt; do [ -e "$f" ] && cp "$f" "$S/results/${n}__$(basename $f)"; done
done
cp $R/to_human/*.md $S/to_human/
cp $R/analysis/*.md $S/analysis/
cp $R/data_analysis/*.md $S/data_analysis/
cp $R/literature/*.md $S/literature/
cp $R/literature/notes/*.md $S/literature/notes/
cp ~/mtp/MTP_session_handoff_2026-10-07.md $S/
# Agent-team folders (21 to 30 Oct) and the session records (added 30 Oct): every markdown file, keeping the folder
# layout, plus the small text outputs the handbook cites. Not copied: scripts, raw JSONs, images, logs of runs.
mkdir -p $S/teams $S/session_records
cp $R/SESSION_RECORD_*.md $S/session_records/
for t in $R/team_2026-10-*/ $R/team_2026-11-*/; do
  n=$(basename $t)
  (cd $t && find . -name '*.md' -not -path '*/scripts/*' -not -path '*_scripts/*' | while read -r f; do
     mkdir -p "$S/teams/$n/$(dirname "$f")"; cp -f "$f" "$S/teams/$n/$f"; done)  # -f: frozen read-only copies can be refreshed (12 Nov)
done
mkdir -p $S/teams/team_2026-10-29_features/b1_audit
cp $R/team_2026-10-29_features/b1_audit/b1_coverage.txt $S/teams/team_2026-10-29_features/b1_audit/
cp $R/team_2026-10-29_features/identity_f1.txt $S/teams/team_2026-10-29_features/
# Thermal team (added 12 Nov; every .md is copied by the loop above): the small text results the handbook cites
mkdir -p $S/teams/team_2026-11-04_thermal/pick1/out $S/teams/team_2026-11-04_thermal/pick3/out
for f in G0_v1_frozen.json G0v2_primary.json G0v2_sensB.json; do cp -f $R/team_2026-11-04_thermal/pick1/out/$f $S/teams/team_2026-11-04_thermal/pick1/out/; done
for f in t15_summary.json t15_descriptive.json t37_v03_summary.json t37_v04_summary.json; do cp -f $R/team_2026-11-04_thermal/pick3/out/$f $S/teams/team_2026-11-04_thermal/pick3/out/; done
cp ~/mtp/datasets/BenchmarkELimages/README.md $S/data_analysis/BenchmarkELimages_README.md 2>/dev/null || true
# E-SCDD dataset card and class definitions (MIT), plus the masks_escdd build note (gaint, read-only)
cp ~/mtp/datasets/escdd_full/README.md $S/data_analysis/escdd_dataset_card_README.md 2>/dev/null || true
cp ~/mtp/datasets/escdd_full/class_explanation.json $S/data_analysis/escdd_class_explanation.json 2>/dev/null || true
cp ~/mtp/datasets/escdd_full/ListOfClassesAndColorCodes_20221008.csv $S/data_analysis/escdd_ListOfClassesAndColorCodes.csv 2>/dev/null || true
# Server copies (read-only scp). SKIP_SERVERS=1 skips them and keeps the copies already in sources/ (added 12 Nov:
# after the laptop OS reinstall, server access had not been re-checked).
SKIP_SERVERS=${SKIP_SERVERS:-0}
if [ "$SKIP_SERVERS" != 1 ]; then
scp -q -o BatchMode=yes noob@172.18.22.20:/home/noob/work/el-fault-detection/data/labeled/masks_escdd/README.txt $S/data_analysis/masks_escdd_README.txt 2>/dev/null || true
# Old-era (phase 1) reports from gaint and cv02, read-only copies
for f in summary.md results_consolidated.md day1.md arm_differences.md bn_recalibration.md precision_diagnostic.md \
         stats_tests.md external_pool.md fit_vs_generalise.md threshold_free.md split_class_pixel_counts.md setup_check.md; do
  scp -q -o BatchMode=yes noob@172.18.22.20:/home/noob/work/el-fault-detection/reports/$f $S/old_era_reports/gaint__$f 2>/dev/null || true
done
scp -q -o BatchMode=yes noob@172.18.22.20:/home/noob/work/el-fault-detection/docs/alhvr_port_notes.md $S/old_era_reports/gaint__alhvr_port_notes.md 2>/dev/null || true
scp -q -o BatchMode=yes noob@172.18.22.20:/home/noob/work/el-fault-detection/README.md $S/old_era_reports/gaint__repo_README.md 2>/dev/null || true
scp -q -o BatchMode=yes cv02@10.8.1.106:noob/el_results/cv02.md $S/old_era_reports/cv02__el_results_cv02.md 2>/dev/null || true
fi
# B2 blinding (coach fix 5, accepted by Om 31 Oct): the 3 Hanifi cells among the 100 B2 panels stay unnamed in these
# copies until the user has marked B2. Stems and panel numbers are read at run time from b2v2_hanifi_panels.txt (that
# file is never copied here, and this script does not contain them). Every copied file that names one is redacted, then
# the copies are checked and the sync fails if a name survives. Set B2_MARKED=1 once the user has marked every panel.
B2_MARKED=${B2_MARKED:-0}
HP=$R/team_2026-10-29_features/b2_mining/v2/b2v2_hanifi_panels.txt
if [ "$B2_MARKED" != 1 ]; then
  [ -e "$HP" ] || { echo "sync_sources: $HP missing, cannot apply the B2 redaction" >&2; exit 1; }
  python3 -I - "$HP" "$S" <<'PYEOF'
import os, re, sys
hp, src = sys.argv[1], sys.argv[2]
rows = [l.rstrip('\n').split('\t') for l in open(hp) if l.strip() and not l.startswith('#')]
rows = [r for r in rows if r[0].isdigit()]
stems = [r[1] for r in rows]; panels = [r[0] for r in rows]
assert len(stems) == 3, 'expected 3 Hanifi panel rows'
stem_re = re.compile('|'.join(re.escape(s) for s in stems))
pan_re = re.compile(r'panels ' + r',? (?:and )?'.join(panels))
TAG = '[redacted until the user marks B2: Hanifi B2 panel cell]'
n = 0
for dp, _, fs in os.walk(src):
    for f in fs:
        p = os.path.join(dp, f)
        try: txt = open(p, encoding='utf-8').read()
        except (UnicodeDecodeError, OSError): continue
        out = []
        for line in txt.split('\n'):
            if stem_re.search(line):   # drop the whole line: it may also carry the cell's label px
                ind = line[:len(line) - len(line.lstrip())]
                line = ind + ('- ' if line.lstrip().startswith('- ') else '') + TAG
            line = pan_re.sub('panels [redacted until the user marks B2]', line)
            out.append(line)
        new = '\n'.join(out)
        if new != txt:
            open(p, 'w', encoding='utf-8').write(new); n += 1
for dp, _, fs in os.walk(src):
    for f in fs:
        p = os.path.join(dp, f)
        try: txt = open(p, encoding='utf-8').read()
        except (UnicodeDecodeError, OSError): continue
        if stem_re.search(txt) or pan_re.search(txt):
            sys.exit('sync_sources: B2 redaction failed in ' + p)
print('B2 redaction: %d file(s) redacted, 0 names left' % n)
PYEOF
fi
echo "sources: $(find $S -type f | wc -l) files, $(du -sh $S | cut -f1)"
