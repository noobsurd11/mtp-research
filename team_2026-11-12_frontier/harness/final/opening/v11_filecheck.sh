#!/bin/bash
# Review round 1, N9: md5 of the v1.1 mask and ignore files of a stem list, file by file, against the lines of a md5 manifest
# (default masks_v11/MANIFEST.md5, whose own md5 run_opening_read.sh checks against the registration first).
# Usage: v11_filecheck.sh <masks_v11 dir> <stem list> [manifest]. Prints 'v11 file check: OK <n> files' (rc 0) or why (rc 1).
# Reads file hashes only. Every stem must have exactly one masks/<stem>.png and one ignore/<stem>.png line.
set -u
set -f
D=${1:?masks_v11 dir}; S=${2:?stem list}; M=${3:-$1/MANIFEST.md5}
[ -s "$M" ] && [ -s "$S" ] || { echo "no manifest or stem list"; exit 1; }
n=0; L=""
for s in $(grep . "$S"); do
  for k in masks ignore; do
    l=$(grep -E "^[0-9a-f]{32}  $k/$s\.png\$" "$M")
    [ "$(printf '%s\n' "$l" | grep -c .)" = 1 ] || { echo "manifest has $(printf '%s\n' "$l" | grep -c .) lines for $k/$s.png"; exit 1; }
    L="$L$l
"; n=$((n + 1)); done
done
r=$(cd "$D" && printf '%s' "$L" | md5sum -c --quiet - 2>&1) || { echo "md5sum -c failed: $(echo "$r" | head -3 | tr '\n' ' ')"; exit 1; }
echo "v11 file check: OK $n files ($(grep -c . "$S") stems, manifest $(md5sum < "$M" | cut -c1-8))"
