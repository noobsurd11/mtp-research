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
  for f in $d*.md $d*_rules.txt $d*per_image_test.txt; do [ -e "$f" ] && cp "$f" "$S/results/${n}__$(basename $f)"; done
done
cp $R/to_human/*.md $S/to_human/
cp $R/analysis/*.md $S/analysis/
cp $R/data_analysis/*.md $S/data_analysis/
cp $R/literature/*.md $S/literature/
cp $R/literature/notes/*.md $S/literature/notes/
cp ~/mtp/MTP_session_handoff_2026-10-07.md $S/
cp ~/mtp/datasets/BenchmarkELimages/README.md $S/data_analysis/BenchmarkELimages_README.md 2>/dev/null || true
# E-SCDD dataset card and class definitions (MIT), plus the masks_escdd build note (gaint, read-only)
cp ~/mtp/datasets/escdd_full/README.md $S/data_analysis/escdd_dataset_card_README.md 2>/dev/null || true
cp ~/mtp/datasets/escdd_full/class_explanation.json $S/data_analysis/escdd_class_explanation.json 2>/dev/null || true
cp ~/mtp/datasets/escdd_full/ListOfClassesAndColorCodes_20221008.csv $S/data_analysis/escdd_ListOfClassesAndColorCodes.csv 2>/dev/null || true
scp -q -o BatchMode=yes noob@172.18.22.20:/home/noob/work/el-fault-detection/data/labeled/masks_escdd/README.txt $S/data_analysis/masks_escdd_README.txt 2>/dev/null || true
# Old-era (phase 1) reports from gaint and cv02, read-only copies
for f in summary.md results_consolidated.md day1.md arm_differences.md bn_recalibration.md precision_diagnostic.md \
         stats_tests.md external_pool.md fit_vs_generalise.md threshold_free.md split_class_pixel_counts.md setup_check.md; do
  scp -q -o BatchMode=yes noob@172.18.22.20:/home/noob/work/el-fault-detection/reports/$f $S/old_era_reports/gaint__$f 2>/dev/null || true
done
scp -q -o BatchMode=yes noob@172.18.22.20:/home/noob/work/el-fault-detection/docs/alhvr_port_notes.md $S/old_era_reports/gaint__alhvr_port_notes.md 2>/dev/null || true
scp -q -o BatchMode=yes noob@172.18.22.20:/home/noob/work/el-fault-detection/README.md $S/old_era_reports/gaint__repo_README.md 2>/dev/null || true
scp -q -o BatchMode=yes cv02@10.8.1.106:noob/el_results/cv02.md $S/old_era_reports/cv02__el_results_cv02.md 2>/dev/null || true
echo "sources: $(find $S -type f | wc -l) files, $(du -sh $S | cut -f1)"
